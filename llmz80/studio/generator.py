"""Write a project's program, then keep repairing it until the gates agree.

Studio judges programs; this is where one comes from. The writer is injected so
the loop can be exercised end to end without an API call, and so a different
writer -- another model, a template, a person pasting sources -- drops in
without touching the loop.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Protocol

from pydantic import BaseModel, ConfigDict, model_validator

from llmz80.core.platform_notes import platform_notes

from .acceptance import generation_prompt
from .models import GameProject
from .retrieval import examples_prompt

#: Sources a program may contribute. Anything else is refused rather than
#: silently dropped, so a writer cannot smuggle a Makefile past the scaffold.
SOURCE_NAME = re.compile(r"^[a-z][a-z0-9_]{0,30}\.(c|h)$")


class ProgramFile(BaseModel):
    """One source file. A flat object, because structured outputs reject the
    keyword a constrained mapping would generate."""

    model_config = ConfigDict(extra="forbid")

    name: str
    body: str


class ProgramSources(BaseModel):
    """The C sources of one program.

    Shape is kept plain for the schema's sake; the rules live in the validator
    below, where a violation can be explained rather than merely rejected.
    """

    model_config = ConfigDict(extra="forbid")

    summary: str
    files: list[ProgramFile]

    @model_validator(mode="after")
    def validate_files(self) -> "ProgramSources":
        names = [item.name for item in self.files]
        if not names:
            raise ValueError("a program must contain at least main.c")
        bad = sorted(name for name in names if not SOURCE_NAME.match(name))
        if bad:
            raise ValueError("only .c and .h source names are accepted: " + ", ".join(bad))
        duplicated = sorted({name for name in names if names.count(name) > 1})
        if duplicated:
            raise ValueError("these sources are given twice: " + ", ".join(duplicated))
        if "main.c" not in names:
            raise ValueError("a program must contain main.c")
        empty = sorted(item.name for item in self.files if not item.body.strip())
        if empty:
            raise ValueError("these sources are empty: " + ", ".join(empty))
        return self

    @property
    def sources(self) -> dict[str, str]:
        return {item.name: item.body for item in self.files}


class ProgramWriter(Protocol):
    def write(
        self, project: GameProject, feedback: str | None = None
    ) -> ProgramSources: ...


def writing_prompt(project: GameProject, *, with_examples: bool = True) -> str:
    """Everything the writer is told before its first attempt."""
    parts = [
        generation_prompt(project),
        platform_notes(project.target.platform.value),
    ]
    if with_examples:
        examples = examples_prompt(project)
        if examples:
            parts.append(examples)
    parts.append(_instructions(project))
    return "\n\n".join(part for part in parts if part)


def _instructions(project: GameProject) -> str:
    return f"""TASK

Write the complete program in C for this design. Return one file per source,
named like main.c. main.c is required. Studio places your sources beside
game_config.h, game_state.h and the platform library, all includable by name.

Define every required contract symbol exactly once, across all your files.
Do not redefine anything game_config.h already provides.

Keep the binary under {project.budgets.binary_bytes} bytes and static data
under {project.budgets.static_data_bytes} bytes.

Draw the game. The state contract is read from memory, but a program that
updates its variables without putting anything on screen is not a game and
is rejected: the screen after the scripted inputs is compared against the
screen before them, and it must differ. Draw the playfield, the actors and
the score, and redraw only what changed.

Write no build files, no Makefile and no prose outside code comments.
"""


def repair_prompt(
    build: dict[str, Any] | None, acceptance: dict[str, Any] | None, probes: dict[str, Any] | None
) -> str:
    """Turn gate output into the most specific instruction the evidence allows."""
    sections: list[str] = []
    if build and not build.get("quality_pass"):
        diagnostics = (str(build.get("stderr") or "") + str(build.get("stdout") or ""))[-3000:]
        sections.append(
            "THE BUILD FAILED\n\nFix these diagnostics. Do not change the design.\n\n"
            + diagnostics.strip()
        )
    if probes and probes.get("missing_required"):
        sections.append(
            "CONTRACT SYMBOLS ARE MISSING\n\nThese are absent from the linker map, "
            "which usually means they were declared static or optimised away:\n  "
            + ", ".join(probes["missing_required"])
        )
    if acceptance and acceptance.get("quality_pass") is False:
        lines = ["THE PROGRAM BUILT AND RAN BUT BEHAVED WRONGLY", ""]
        for scenario in acceptance.get("scenarios", []):
            if scenario.get("passed"):
                continue
            lines.append(
                f"  After holding {scenario['hold']} for {scenario['frames']} frames:"
            )
            for mismatch in scenario["mismatches"] or ["no reading arrived"]:
                lines.append(f"    {mismatch}")
        lines.append("")
        lines.append("Memory was read directly, so these are facts about your program.")
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


class ResponsesProgramWriter:
    """Writes the program with the OpenAI Responses API."""

    def __init__(self, client: Any, model: str = "gpt-5") -> None:
        self.client = client
        self.model = model

    def write(self, project: GameProject, feedback: str | None = None) -> ProgramSources:
        content = writing_prompt(project)
        if feedback:
            content += "\n\nYOUR PREVIOUS ATTEMPT WAS REJECTED\n\n" + feedback
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You write complete, small C programs for 8-bit Z80 home computers. "
                        "You honour the stated contract exactly and you never invent build files."
                    ),
                },
                {"role": "user", "content": content},
            ],
            text_format=ProgramSources,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("the model did not return program sources")
        return parsed


@dataclass
class Attempt:
    number: int
    summary: str
    files: list[str]
    build_passed: bool | None = None
    acceptance_passed: bool | None = None
    feedback: str = ""


@dataclass
class WriteResult:
    accepted: bool
    attempts: list[Attempt] = field(default_factory=list)
    program_dir: Path | None = None
    last_error: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "accepted": self.accepted,
            "attempts": [attempt.__dict__ for attempt in self.attempts],
            "program_dir": str(self.program_dir) if self.program_dir else None,
            "last_error": self.last_error,
        }


def store_program(project: GameProject, directory: Path, sources: ProgramSources) -> Path:
    """Write the program into the project, replacing whatever was there.

    Sources removed by a later attempt must not linger, or a stale file keeps
    compiling and the failure being repaired never goes away.
    """
    program_dir = directory / project.program_dir
    program_dir.mkdir(parents=True, exist_ok=True)
    for stale in program_dir.iterdir():
        if stale.is_file() and stale.suffix in {".c", ".h"}:
            stale.unlink()
    for name, body in sorted(sources.sources.items()):
        (program_dir / name).write_text(body.rstrip() + "\n", encoding="utf-8")
    return program_dir


def write_program(
    project: GameProject,
    directory: Path,
    writer: ProgramWriter,
    verify: Callable[[GameProject, Path], dict[str, Any]],
    *,
    attempts: int = 3,
) -> WriteResult:
    """Ask for a program, verify it, and feed what failed back in.

    Verification is injected because the loop's logic and the emulator's cost
    are separate concerns: the same loop is exercised in tests without a
    toolchain and in anger with both.
    """
    result = WriteResult(accepted=False)
    feedback: str | None = None
    for number in range(1, max(1, attempts) + 1):
        try:
            sources = writer.write(project, feedback)
        except Exception as exc:  # a writer failing is an outcome, not a crash
            result.last_error = str(exc)
            return result
        program_dir = store_program(project, directory, sources)
        result.program_dir = program_dir
        attempt = Attempt(
            number=number, summary=sources.summary, files=sorted(sources.sources)
        )
        result.attempts.append(attempt)

        evidence = verify(project, directory)
        build = evidence.get("build")
        acceptance = evidence.get("acceptance")
        probes = evidence.get("probes")
        attempt.build_passed = bool(build and build.get("quality_pass"))
        attempt.acceptance_passed = (acceptance or {}).get("quality_pass")

        # An unobservable target cannot confirm behaviour, so a clean build is
        # as far as the evidence goes; it is recorded as such, not as a pass.
        if attempt.build_passed and attempt.acceptance_passed is not False:
            result.accepted = True
            return result
        feedback = repair_prompt(build, acceptance, probes)
        attempt.feedback = feedback
        if not feedback:
            result.last_error = "the program was rejected without any diagnostic to act on"
            return result
    return result
