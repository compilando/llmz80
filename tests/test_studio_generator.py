from pathlib import Path

import pytest

from llmz80.core.platform_notes import platform_notes
from llmz80.studio.generator import (
    ProgramFile,
    ProgramSources,
    repair_prompt,
    store_program,
    write_program,
    writing_prompt,
)
from llmz80.studio.models import GenreId, TargetPlatform
from llmz80.studio.packs import create_default_project


@pytest.fixture
def project():
    return create_default_project("Written", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)


class ScriptedWriter:
    """A writer whose attempts are decided in advance, so the loop is testable."""

    def __init__(self, *attempts: ProgramSources) -> None:
        self.attempts = list(attempts)
        self.feedback_seen: list[str | None] = []

    def write(self, project, feedback=None):
        self.feedback_seen.append(feedback)
        return self.attempts[min(len(self.feedback_seen), len(self.attempts)) - 1]


def _sources(marker: str) -> ProgramSources:
    return ProgramSources(
        summary=f"attempt {marker}",
        files=[ProgramFile(name="main.c", body=f"/* {marker} */\nvoid main(void) {{ }}\n")],
    )


def test_program_sources_reject_anything_that_is_not_a_source():
    with pytest.raises(ValueError, match="only .c and .h source names"):
        ProgramSources(summary="s", files=[ProgramFile(name="Makefile", body="all:")])

    with pytest.raises(ValueError, match="must contain main.c"):
        ProgramSources(summary="s", files=[ProgramFile(name="engine.c", body="void f(void){}")])

    with pytest.raises(ValueError, match="empty"):
        ProgramSources(summary="s", files=[ProgramFile(name="main.c", body="   ")])


def test_storing_a_program_replaces_what_was_there(tmp_path: Path, project):
    store_program(project, tmp_path, ProgramSources(summary="a", files=[
        ProgramFile(name="main.c", body="void main(void){}"),
        ProgramFile(name="old.c", body="void old(void){}"),
    ]))

    store_program(project, tmp_path, _sources("second"))

    program = tmp_path / project.program_dir
    assert sorted(path.name for path in program.iterdir()) == ["main.c"]
    assert "second" in (program / "main.c").read_text()


def test_the_writing_prompt_carries_contract_design_acceptance_and_hazards(project):
    prompt = writing_prompt(project)

    assert "OBSERVABLE STATE CONTRACT" in prompt
    assert "DESIGN" in prompt
    assert "RUNTIME ACCEPTANCE" in prompt
    assert "PLATFORM NOTES" in prompt
    assert "ROM frame counter" in prompt
    assert str(project.budgets.binary_bytes) in prompt


def test_platform_notes_differ_per_machine():
    assert "sdcccall(1)" in platform_notes("amstrad_cpc")
    assert "sdcccall(1)" not in platform_notes("spectrum")
    assert "bit_beep" in platform_notes("spectrum")


def test_repair_prompt_prefers_the_most_specific_evidence():
    build_only = repair_prompt({"quality_pass": False, "stderr": "error 101: too many"}, None, None)
    assert "THE BUILD FAILED" in build_only
    assert "error 101" in build_only

    missing = repair_prompt(None, None, {"missing_required": ["g_score"]})
    assert "CONTRACT SYMBOLS ARE MISSING" in missing
    assert "g_score" in missing

    behaved = repair_prompt(
        {"quality_pass": True},
        {
            "quality_pass": False,
            "scenarios": [
                {
                    "id": "collect_scores",
                    "hold": "down",
                    "frames": 60,
                    "passed": False,
                    "mismatches": ["g_score: expected 10, read 0"],
                }
            ],
        },
        None,
    )
    assert "BEHAVED WRONGLY" in behaved
    assert "g_score: expected 10, read 0" in behaved
    assert "holding down for 60 frames" in behaved


def test_a_first_attempt_that_passes_stops_the_loop(tmp_path: Path, project):
    writer = ScriptedWriter(_sources("good"))

    result = write_program(
        project,
        tmp_path,
        writer,
        lambda p, d: {"build": {"quality_pass": True}, "acceptance": {"quality_pass": True}},
    )

    assert result.accepted is True
    assert len(result.attempts) == 1
    assert writer.feedback_seen == [None]


def test_a_build_failure_is_fed_back_and_the_repair_accepted(tmp_path: Path, project):
    writer = ScriptedWriter(_sources("broken"), _sources("fixed"))
    calls = {"n": 0}

    def verify(_project, _directory):
        calls["n"] += 1
        if calls["n"] == 1:
            return {"build": {"quality_pass": False, "stderr": "error 101: too many parameters"}}
        return {"build": {"quality_pass": True}, "acceptance": {"quality_pass": True}}

    result = write_program(project, tmp_path, writer, verify)

    assert result.accepted is True
    assert [attempt.build_passed for attempt in result.attempts] == [False, True]
    assert "error 101" in writer.feedback_seen[1]
    assert "fixed" in (tmp_path / project.program_dir / "main.c").read_text()


def test_a_program_that_builds_but_misbehaves_is_repaired_from_memory_reads(
    tmp_path: Path, project
):
    writer = ScriptedWriter(_sources("silent"), _sources("scoring"))
    calls = {"n": 0}

    def verify(_project, _directory):
        calls["n"] += 1
        if calls["n"] == 1:
            return {
                "build": {"quality_pass": True},
                "acceptance": {
                    "quality_pass": False,
                    "scenarios": [
                        {
                            "id": "collect_scores",
                            "hold": "down",
                            "frames": 60,
                            "passed": False,
                            "mismatches": ["g_score: expected 10, read 0"],
                        }
                    ],
                },
            }
        return {"build": {"quality_pass": True}, "acceptance": {"quality_pass": True}}

    result = write_program(project, tmp_path, writer, verify)

    assert result.accepted is True
    assert result.attempts[0].acceptance_passed is False
    assert "g_score: expected 10, read 0" in writer.feedback_seen[1]


def test_the_loop_gives_up_after_the_agreed_number_of_attempts(tmp_path: Path, project):
    writer = ScriptedWriter(_sources("bad"))

    result = write_program(
        project,
        tmp_path,
        writer,
        lambda p, d: {"build": {"quality_pass": False, "stderr": "boom"}},
        attempts=2,
    )

    assert result.accepted is False
    assert len(result.attempts) == 2


def test_an_unobservable_target_accepts_on_the_build_alone(tmp_path: Path, project):
    writer = ScriptedWriter(_sources("cpc"))

    result = write_program(
        project,
        tmp_path,
        writer,
        # A CPC run abstains from the acceptance verdict rather than failing it.
        lambda p, d: {"build": {"quality_pass": True}, "acceptance": {"quality_pass": None}},
    )

    assert result.accepted is True
    assert result.attempts[0].acceptance_passed is None


def test_a_writer_that_fails_ends_the_loop_with_its_reason(tmp_path: Path, project):
    class Broken:
        def write(self, project, feedback=None):
            raise RuntimeError("the model did not return program sources")

    result = write_program(project, tmp_path, Broken(), lambda p, d: {})

    assert result.accepted is False
    assert result.attempts == []
    assert "did not return program sources" in result.last_error


def test_the_writing_prompt_shows_the_platform_interface():
    """A writer told to include platform.h must be shown what is in it."""
    project = create_default_project("Iface", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)

    prompt = writing_prompt(project, with_examples=False)

    assert "unsigned char plat_wait_frame(void);" in prompt
    assert "void plat_cell(unsigned char col, unsigned char row, unsigned char kind);" in prompt
    assert "PLATFORM LIBRARY INTERFACE" in prompt


def test_a_missing_platform_header_is_not_silently_survivable():
    """The header is now read once at import (mirroring BUILTIN_PACKS in
    packs.py), specifically so a missing file fails loudly there instead of
    surfacing, mid-loop, as an indistinguishable "writer failed" result under
    write_program's blanket except. Reproducing that means re-running the
    module's import-time load with the real header briefly out of the way."""
    import importlib

    import llmz80.studio.generator as generator_module

    header = generator_module.PLATFORM_HEADER
    missing = header.with_name(header.name + ".missing-for-test")
    header.rename(missing)
    try:
        with pytest.raises(FileNotFoundError):
            importlib.reload(generator_module)
    finally:
        missing.rename(header)
        importlib.reload(generator_module)
