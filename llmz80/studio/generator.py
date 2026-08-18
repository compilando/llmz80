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
from .llm import structured
from .models import GameProject
from .reference import GameReference, reference_prompt
from .retrieval import examples_prompt

#: Sources a program may contribute. Anything else is refused rather than
#: silently dropped, so a writer cannot smuggle a Makefile past the scaffold.
SOURCE_NAME = re.compile(r"^[a-z][a-z0-9_]{0,30}\.(c|h)$")

#: The interface every target implements. Handed to the writer verbatim: telling
#: it the library exists without showing the header invites invented functions.
PLATFORM_HEADER = (
    Path(__file__).resolve().parents[2] / "resources" / "studio_lib" / "common" / "platform.h"
)

#: Read once at import: the header is
#: invariant across every writer attempt in the repair loop, and a missing or
#: unreadable file should fail loudly at startup rather than surface deep
#: inside write_program's blanket except as an indistinguishable "writer
#: failed" result.
PLATFORM_INTERFACE = (
    "PLATFORM LIBRARY INTERFACE\n\nThis header is beside your sources:\n\n"
    + PLATFORM_HEADER.read_text(encoding="utf-8")
)


def library_interface() -> str:
    """The platform header, as a prompt block."""
    return PLATFORM_INTERFACE


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
    def write(self, project: GameProject, feedback: str | None = None) -> ProgramSources: ...


def writing_prompt(
    project: GameProject,
    *,
    with_examples: bool = True,
    reference: GameReference | None = None,
) -> str:
    """Everything the writer is told before its first attempt."""
    parts = [
        reference_prompt(reference),
        generation_prompt(project),
        platform_notes(project.target.platform.value),
        library_interface(),
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
is rejected: the emulated screen is captured while the program runs, it must
not be blank, and two captures taken as the game advances must differ. Draw
what this design declares -- its terrain, its entities, whatever its
observables say a player can see -- and redraw only what changed.

Write no build files, no Makefile and no prose outside code comments.
"""


def repair_prompt(
    build: dict[str, Any] | None,
    acceptance: dict[str, Any] | None,
    probes: dict[str, Any] | None,
    animation: dict[str, Any] | None = None,
    pacing: dict[str, Any] | None = None,
    attributes: dict[str, Any] | None = None,
) -> str:
    """Turn gate output into the most specific instruction the evidence allows."""
    sections: list[str] = []
    if build and not build.get("quality_pass"):
        # Each stream gets its own budget. Slicing the concatenation instead
        # kept the tail of stdout and threw away all of stderr whenever the
        # two together cleared the ceiling -- and stderr is where both the
        # compiler's errors and `compiler.build_project`'s own contract
        # diagnostic live. A CPCtelera build spamming SDCC warning 283 clears
        # 3000 characters on its own, so the refusal the writer most needed to
        # read was exactly the one a noisy toolchain buried.
        diagnostics = (
            str(build.get("stderr") or "")[-1500:] + str(build.get("stdout") or "")[-1500:]
        )
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
    # Said in its own section rather than folded into the one above: these are
    # not the contract's symbols but this design's own, game_state.h declares
    # them `extern` from game.yml, and a writer told only "contract symbols are
    # missing" would go looking for them in `contract_prompt`, where they are
    # not.
    if probes and probes.get("missing_observables"):
        sections.append(
            "THIS DESIGN'S OWN OBSERVABLES ARE MISSING\n\ngame_state.h declares these "
            "extern because game.yml declares them, and they are absent from the "
            "linker map. Define each one exactly once at file scope -- not static, "
            "not inside a function -- and update it where the rule it names "
            "happens:\n  " + ", ".join(probes["missing_observables"])
        )
    if acceptance and acceptance.get("quality_pass") is False:
        lines = ["THE PROGRAM BUILT AND RAN BUT BEHAVED WRONGLY", ""]
        for scenario in acceptance.get("scenarios", []):
            if scenario.get("passed"):
                continue
            lines.append(f"  After holding {scenario['hold']} for {scenario['frames']} frames:")
            for mismatch in scenario["mismatches"] or ["no reading arrived"]:
                lines.append(f"    {mismatch}")
        lines.append("")
        lines.append("Memory was read directly, so these are facts about your program.")
        sections.append("\n".join(lines))
    if animation and animation.get("quality_pass") is False:
        lines = ["THE ANIMATION FRAME DID NOT BEHAVE AS DECLARED", ""]
        for reason in animation.get("failures") or []:
            lines.append(f"  {reason}")
        lines.append("")
        lines.append(
            "g_anim_frame must change between two consecutive readings taken while "
            "the player is moving, and stay the same between two readings taken "
            "while it is not. Update it whenever you redraw a moving actor, and "
            "leave it untouched on a step where no direction is held. Memory was "
            "read directly, so these are facts about your program."
        )
        sections.append("\n".join(lines))
    if pacing and pacing.get("quality_pass") is False:
        lines = ["THE GAME LOOP DID NOT FIT INSIDE ITS DISPLAY FRAME", ""]
        for reason in pacing.get("failures") or []:
            lines.append(f"  {reason}")
        lines.append("")
        lines.append(
            "plat_wait_frame returns how many whole frames the previous iteration "
            "overran by; keep the worst you ever see in g_worst_frame_cost. The cost "
            "is measured between consecutive calls, so a loop that never waits -- a "
            "menu polling tightly for a key, which the platform notes require -- "
            "charges its whole duration to whoever calls next: call plat_wait_frame "
            "once as you leave such a loop and discard the result. Memory was read "
            "directly, so these are facts about your program."
        )
        sections.append("\n".join(lines))
    if attributes and attributes.get("quality_pass") is False:
        lines = ["YOU DREW PIXELS WHERE NO PLAYER CAN SEE THEM", ""]
        for reason in attributes.get("failures") or []:
            lines.append(f"  {reason}")
        lines.append("")
        lines.append(
            "A cell whose ink is the same colour as its paper shows nothing, however "
            "carefully the pixels in it were drawn. Set the attribute of every cell "
            "you draw into before you draw, and pick an ink that differs from that "
            "cell's paper -- BRIGHT lifts both halves and FLASH swaps them, so "
            "neither can separate a colour from itself. The display file was read "
            "directly out of the machine, so these are facts about your program."
        )
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


class ResponsesProgramWriter:
    """Writes the program with the model."""

    def __init__(
        self,
        client: Any,
        model: str = "claude-opus-5",
        reference: GameReference | None = None,
    ) -> None:
        self.client = client
        self.model = model
        self.reference = reference

    def write(self, project: GameProject, feedback: str | None = None) -> ProgramSources:
        content = writing_prompt(project, reference=self.reference)
        if feedback:
            content += "\n\nYOUR PREVIOUS ATTEMPT WAS REJECTED\n\n" + feedback
        return structured(
            self.client,
            self.model,
            system=(
                "You write complete, small C programs for 8-bit Z80 home computers. "
                "You honour the stated contract exactly and you never invent build files."
            ),
            user=content,
            schema=ProgramSources,
            missing="the model did not return program sources",
        )


@dataclass
class Attempt:
    number: int
    summary: str
    files: list[str]
    build_passed: bool | None = None
    acceptance_passed: bool | None = None
    #: Whether the toolchain itself accepted the sources, as opposed to
    #: whether the build passed policy. A compile that succeeds and is then
    #: refused over its warnings is a different thing to fix from one that
    #: never compiled, and the progress line used to call both "did not compile".
    build_compiled: bool | None = None
    #: `None` means the animation gate abstained (no adapter, or the design
    #: never declared g_anim_frame) -- exactly as unobserved as `acceptance`'s
    #: own abstention, and just as non-fatal. See `write_program`.
    animation_passed: bool | None = None
    #: `None` means the pacing gate abstained -- no adapter, no reading of
    #: g_worst_frame_cost, or a target whose plat_wait_frame never counts a
    #: frame at all (the CPC returns a literal zero). Non-fatal for the same
    #: reason as the two above: a number nobody measured is not a pass.
    pacing_passed: bool | None = None
    #: `None` means the attribute gate abstained -- the run kept no display
    #: file, because the target has no way to read emulated memory (the CPC
    #: harness dumps no screen at all) or the screen read came back short.
    #: Non-fatal for the same reason as the three above: a screen nobody read
    #: is not a screen anybody approved.
    attributes_passed: bool | None = None
    #: The *runtime* state-probe gate -- `services.probe_report`, which reads
    #: the contract back out of the running machine -- and not the build-time
    #: symbol map, which the writer still gets as `evidence["probes"]`. It
    #: abstains at every run today (no examiner has derived what a design
    #: should read), and it is wired anyway: `runtime_test` has always folded
    #: it into its verdict, so the day the phase 2 examiner makes it return
    #: `False` this loop would have accepted the very program `release`
    #: refused -- one program with two verdicts, which is the defect this
    #: floor exists to remove. Until that examiner also gives the refusal a
    #: sentence, a run failed by this gate alone ends the loop with "rejected
    #: without any diagnostic to act on" rather than with a repair, which is
    #: the honest order of those two problems.
    state_probe_passed: bool | None = None
    feedback: str = ""


#: Told what is happening while it happens -- see `services.Progress` for the
#: same alias and the reason it exists. Defined again here, rather than
#: imported, because `services.py` imports *this* module; importing back the
#: other way would be a cycle.
Progress = Callable[[str], None] | None


def _say(on_progress: Progress, text: str) -> None:
    """Report `text` if anyone is listening, so callers stay free of the check."""
    if on_progress is not None:
        on_progress(text)


def _gate_verdict(passed: bool | None) -> str:
    """`True`/`False`/`None` (a gate that abstained -- no adapter, or nothing
    to judge) read out the way a person, not a parser, would ask for them."""
    if passed is None:
        return "not observed"
    return "passed" if passed else "refused"


def _attempt_line(attempt: Attempt) -> str:
    """One attempt, as `Attempt` already recorded it: its number, whether the
    build compiled, and each gate's verdict."""
    if attempt.build_passed:
        build = "compiled"
    elif attempt.build_compiled:
        build = "compiled but was refused"
    else:
        build = "did not compile"
    acceptance = _gate_verdict(attempt.acceptance_passed)
    animation = _gate_verdict(attempt.animation_passed)
    pacing = _gate_verdict(attempt.pacing_passed)
    attributes = _gate_verdict(attempt.attributes_passed)
    state_probe = _gate_verdict(attempt.state_probe_passed)
    return (
        f"attempt {attempt.number}: build {build}, "
        f"acceptance {acceptance}, animation {animation}, pacing {pacing}, "
        f"attributes {attributes}, state {state_probe}"
    )


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
    attempts: int = 5,
    on_progress: Progress = None,
) -> WriteResult:
    """Ask for a program, verify it, and feed what failed back in.

    Verification is injected because the loop's logic and the emulator's cost
    are separate concerns: the same loop is exercised in tests without a
    toolchain and in anger with both.

    `on_progress`, when given, is told twice per attempt: once before
    `writer.write` -- the long wait, an LLM call -- and once its verdict is
    known, after `verify` has judged it. Both happen inside this loop, so a
    caller listening hears the first line well before this function itself
    returns -- unlike a report handed back only once every attempt is spent.
    """
    result = WriteResult(accepted=False)
    feedback: str | None = None
    for number in range(1, max(1, attempts) + 1):
        _say(on_progress, f"attempt {number}: writing...")
        try:
            sources = writer.write(project, feedback)
        except Exception as exc:  # a writer failing is an outcome, not a crash
            result.last_error = str(exc)
            return result
        program_dir = store_program(project, directory, sources)
        result.program_dir = program_dir
        attempt = Attempt(number=number, summary=sources.summary, files=sorted(sources.sources))
        result.attempts.append(attempt)

        evidence = verify(project, directory)
        build = evidence.get("build")
        acceptance = evidence.get("acceptance")
        probes = evidence.get("probes")
        animation = evidence.get("animation")
        pacing = evidence.get("pacing")
        attributes = evidence.get("attributes")
        # The runtime gate, under its own key. `probes` above is the build-time
        # symbol map, which `repair_prompt` legitimately wants for its missing
        # contract symbols; reading the verdict off that map is what let the
        # runtime one reach `runtime_test` and never reach this loop.
        state_probe = evidence.get("state_probe")
        attempt.build_passed = bool(build and build.get("quality_pass"))
        attempt.build_compiled = bool(build and build.get("compile_succeeded"))
        attempt.acceptance_passed = (acceptance or {}).get("quality_pass")
        attempt.animation_passed = (animation or {}).get("quality_pass")
        attempt.pacing_passed = (pacing or {}).get("quality_pass")
        attempt.attributes_passed = (attributes or {}).get("quality_pass")
        attempt.state_probe_passed = (state_probe or {}).get("quality_pass")
        _say(on_progress, _attempt_line(attempt))

        # An unobservable target cannot confirm behaviour, so a clean build is
        # as far as the evidence goes; it is recorded as such, not as a pass.
        # `is not False` treats an abstaining gate (`quality_pass: None`) as
        # neither: not a pass earned, but not a refusal either. Only a definite
        # `False` -- a gate that actually watched and found something wrong --
        # blocks acceptance.
        #
        # Which gates abstain is a property of the target, and on the CPC it is
        # two of the five rather than all of them. That was not always true and
        # this comment said so for longer than it was: the CPC used to be driven
        # by Caprice32, which reads no memory, so every behaviour gate abstained.
        # ZEsarUX drives it now over the same ZRCP as the Spectrum
        # (`emulator_smoke._ZESARUX_PROFILES`), so acceptance, animation and the
        # state probe all really watch a CPC game. The two that still abstain do
        # so for reasons that are about the machine rather than the harness:
        # `pacing` because a CPC with the firmware disabled has no free-running
        # frame counter, so `plat_wait_frame` returns zero without measuring
        # anything (`codegen.has_frame_clock`), and `attributes` because a CPC
        # screen has no attribute area to judge -- its colour lives in the pixel
        # bytes (`attributes.attribute_report`). The first is a gap somebody
        # could close with `cpct_count2VSYNC`; the second wants a different gate,
        # not this one aimed somewhere new.
        # All five gates `services.runtime_test` folds into its own verdict
        # are read here, and the same way: a gate that fails the run and not
        # the attempt gives one program two verdicts, with `release` refusing
        # what this loop accepted and never asked to have repaired.
        if (
            attempt.build_passed
            and attempt.acceptance_passed is not False
            and attempt.animation_passed is not False
            and attempt.pacing_passed is not False
            and attempt.attributes_passed is not False
            and attempt.state_probe_passed is not False
        ):
            result.accepted = True
            return result
        feedback = repair_prompt(build, acceptance, probes, animation, pacing, attributes)
        attempt.feedback = feedback
        if not feedback:
            result.last_error = "the program was rejected without any diagnostic to act on"
            return result
    return result
