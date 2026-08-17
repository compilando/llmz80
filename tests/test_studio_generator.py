from pathlib import Path

import pytest

from llmz80.core.platform_notes import platform_notes
from llmz80.studio.generator import (
    ProgramFile,
    ProgramSources,
    ResponsesProgramWriter,
    repair_prompt,
    store_program,
    write_program,
    writing_prompt,
)
from llmz80.studio.models import TargetPlatform
from llmz80.studio.samples import blank_project
from llmz80.studio.reference import GameReference, ReferenceSource
from tests.conftest import FakeMessageStream


@pytest.fixture
def project():
    return blank_project("Written", TargetPlatform.SPECTRUM)


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
    store_program(
        project,
        tmp_path,
        ProgramSources(
            summary="a",
            files=[
                ProgramFile(name="main.c", body="void main(void){}"),
                ProgramFile(name="old.c", body="void old(void){}"),
            ],
        ),
    )

    store_program(project, tmp_path, _sources("second"))

    program = tmp_path / project.program_dir
    assert sorted(path.name for path in program.iterdir()) == ["main.c"]
    assert "second" in (program / "main.c").read_text()


def test_the_writing_prompt_carries_contract_design_and_hazards(project):
    prompt = writing_prompt(project)

    assert "OBSERVABLE STATE CONTRACT" in prompt
    assert "DESIGN" in prompt
    # No acceptance section: task 10 removed the derivation that wrote one.
    assert "Terrain characters" in prompt
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


def test_repair_prompt_names_a_failing_animation_gate():
    prompt = repair_prompt(
        {"quality_pass": True},
        {"quality_pass": True},
        None,
        {
            "quality_pass": False,
            "failures": [
                "g_anim_frame never advanced across the moving steps " "(anim_probe_move)"
            ],
        },
    )

    assert "ANIMATION" in prompt
    assert "g_anim_frame never advanced across the moving steps (anim_probe_move)" in prompt
    assert "Memory was read directly" in prompt


def test_repair_prompt_says_nothing_about_animation_when_the_gate_abstained():
    # `quality_pass: None` is abstention (no adapter, or the symbol was never
    # declared) -- not evidence of a bug, so it must not be reported as one.
    prompt = repair_prompt(
        {"quality_pass": True}, {"quality_pass": True}, None, {"quality_pass": None}
    )

    assert "ANIMATION" not in prompt


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


def test_write_program_narrates_before_a_slow_attempt_returns(tmp_path: Path, project):
    """`write_program`'s own `WriteResult` only exists once the whole repair
    loop is over -- a caller assembling progress lines from it after the
    fact would still watch the screen say nothing for as long as an attempt
    takes, then dump every line at once. `on_progress` must not have that
    shape: the first line has to arrive before even the first attempt's
    (possibly slow) writer call finishes, not merely before `write_program`
    itself returns -- the two are different claims, and only a genuinely
    slow fake tells them apart.
    """
    import time

    class SlowWriter:
        def __init__(self, sources: ProgramSources) -> None:
            self.sources = sources
            self.finished_at: float | None = None

        def write(self, project, feedback=None):
            time.sleep(0.05)
            self.finished_at = time.monotonic()
            return self.sources

    writer = SlowWriter(_sources("good"))
    progress_times: list[float] = []
    messages: list[str] = []

    def on_progress(text: str) -> None:
        progress_times.append(time.monotonic())
        messages.append(text)

    result = write_program(
        project,
        tmp_path,
        writer,
        lambda p, d: {"build": {"quality_pass": True}, "acceptance": {"quality_pass": True}},
        on_progress=on_progress,
    )

    assert result.accepted is True
    assert progress_times, "no progress was reported at all"
    assert writer.finished_at is not None
    assert progress_times[0] < writer.finished_at, (
        "the first progress line must arrive before the slow writer call it "
        "precedes finishes, not only before write_program returns"
    )
    assert messages[0] == "intento 1: escribiendo..."
    assert messages[1] == (
        "intento 1: build compiló, aceptación aprobada, animación sin observar, "
        "ritmo sin observar, atributos sin observar, estado sin observar"
    )


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


def test_a_failing_animation_gate_is_fed_back_and_the_repair_accepted(tmp_path: Path, project):
    """The defect a real run exposed: `runtime_test` already lowered its own
    `quality_pass` when the animation gate failed, but `write_program` only
    ever looked at `evidence["acceptance"]`, so the failing verdict never
    reached the writer and a program that failed a runtime gate was accepted
    on attempt one. This is the fix -- a failing animation verdict must now
    reject the attempt and its reason must reach the next one's feedback.
    """
    writer = ScriptedWriter(_sources("frozen"), _sources("animating"))
    calls = {"n": 0}

    def verify(_project, _directory):
        calls["n"] += 1
        if calls["n"] == 1:
            return {
                "build": {"quality_pass": True},
                "acceptance": {"quality_pass": True},
                "animation": {
                    "quality_pass": False,
                    "observed": True,
                    "failures": [
                        "g_anim_frame never advanced across the moving steps " "(anim_probe_move)"
                    ],
                },
            }
        return {
            "build": {"quality_pass": True},
            "acceptance": {"quality_pass": True},
            "animation": {"quality_pass": True, "observed": True, "failures": []},
        }

    result = write_program(project, tmp_path, writer, verify)

    assert result.accepted is True
    assert result.attempts[0].animation_passed is False
    assert result.attempts[0].acceptance_passed is True
    assert "g_anim_frame never advanced" in writer.feedback_seen[1]
    assert "animating" in (tmp_path / project.program_dir / "main.c").read_text()


def test_an_abstaining_animation_gate_does_not_block_acceptance(tmp_path: Path, project):
    """A CPC run (no memory probe adapter) or a design that never declared
    g_anim_frame both make the gate abstain (`quality_pass: None`), exactly
    like `acceptance` already does for an unobservable target -- that must
    stay non-fatal, the same way a plain build-only pass already was.
    """
    writer = ScriptedWriter(_sources("cpc"))

    result = write_program(
        project,
        tmp_path,
        writer,
        lambda p, d: {
            "build": {"quality_pass": True},
            "acceptance": {"quality_pass": None},
            "animation": {"quality_pass": None, "observed": False},
        },
    )

    assert result.accepted is True
    assert result.attempts[0].animation_passed is None


def test_a_definite_pacing_refusal_blocks_the_attempt_and_reaches_the_next_writer(
    tmp_path: Path, project
):
    """The pacing gate was wired into `write_program`'s acceptance condition
    with no test on the wiring: deleting `and attempt.pacing_passed is not
    False` left the whole suite green, so a program whose loop overran its
    display frame would have been accepted on attempt one while
    `runtime_test` failed the very same run. A definite `False` must reject
    the attempt, and its reason must reach the writer that repairs it.
    """
    writer = ScriptedWriter(_sources("juddering"), _sources("paced"))
    calls = {"n": 0}

    def verify(_project, _directory):
        calls["n"] += 1
        if calls["n"] == 1:
            return {
                "build": {"quality_pass": True},
                "acceptance": {"quality_pass": None},
                "pacing": {
                    "quality_pass": False,
                    "observed": True,
                    "failures": ["g_worst_frame_cost reached 4 at step hold_left_a"],
                },
            }
        return {
            "build": {"quality_pass": True},
            "acceptance": {"quality_pass": None},
            "pacing": {"quality_pass": True, "observed": True, "failures": []},
        }

    result = write_program(project, tmp_path, writer, verify)

    assert result.accepted is True
    assert [attempt.pacing_passed for attempt in result.attempts] == [False, True]
    assert "g_worst_frame_cost reached 4" in writer.feedback_seen[1]
    assert "paced" in (tmp_path / project.program_dir / "main.c").read_text()


def test_a_definite_attribute_refusal_blocks_the_attempt_and_reaches_the_next_writer(
    tmp_path: Path, project
):
    """The same untested wiring as the pacing gate's: deleting `and
    attempt.attributes_passed is not False` from the acceptance condition
    left the suite green, so a program drawing pixels into cells whose ink
    matches their paper -- a screen no player can read -- was accepted while
    `runtime_test` refused it.
    """
    writer = ScriptedWriter(_sources("invisible"), _sources("legible"))
    calls = {"n": 0}

    def verify(_project, _directory):
        calls["n"] += 1
        if calls["n"] == 1:
            return {
                "build": {"quality_pass": True},
                "acceptance": {"quality_pass": None},
                "attributes": {
                    "quality_pass": False,
                    "observed": True,
                    "failures": ["3 character cell(s) hold drawn pixels: (0,0), (1,0), (2,0)"],
                },
            }
        return {
            "build": {"quality_pass": True},
            "acceptance": {"quality_pass": None},
            "attributes": {"quality_pass": True, "observed": True, "failures": []},
        }

    result = write_program(project, tmp_path, writer, verify)

    assert result.accepted is True
    assert [attempt.attributes_passed for attempt in result.attempts] == [False, True]
    assert "3 character cell(s) hold drawn pixels" in writer.feedback_seen[1]
    assert "legible" in (tmp_path / project.program_dir / "main.c").read_text()


def test_a_definite_state_probe_refusal_blocks_the_attempt(tmp_path: Path, project):
    """`runtime_test` has always folded the runtime state-probe verdict into
    its own, but this loop read only `evidence["probes"]` -- the build-time
    symbol map -- so the runtime gate reached one verdict path and not the
    other. Harmless only while `probe_report` hardcodes `quality_pass: None`:
    the day the phase 2 examiner makes it refuse, `runtime_test` would fail
    the run and `release` would refuse the artifact while this loop accepted
    the attempt and never asked for a repair. One program, two verdicts.

    The refusal carries no sentence for `repair_prompt` yet -- that is the
    examiner's to write with the expectation it derives -- so a run failed by
    this gate alone stops the loop saying there was no diagnostic to act on.
    That is the honest order: a program nobody can tell how to fix is not a
    program to accept.
    """
    writer = ScriptedWriter(_sources("wrong_state"))

    result = write_program(
        project,
        tmp_path,
        writer,
        lambda p, d: {
            "build": {"quality_pass": True},
            "acceptance": {"quality_pass": None},
            # The build-time symbol map: every required symbol is in the
            # linker map, which says nothing about what memory read back.
            "probes": {"missing_required": []},
            "state_probe": {
                "quality_pass": False,
                "observed": True,
                "mismatches": ["g_lives: expected 3, read 0"],
            },
        },
        attempts=1,
    )

    assert result.accepted is False
    assert result.attempts[0].state_probe_passed is False
    assert result.attempts[0].build_passed is True


def test_a_design_with_no_animation_evidence_is_accepted_exactly_as_before(tmp_path: Path, project):
    """A design with no sprites and no g_anim_frame gives `verify_program` no
    "animation" key at all (its evidence dict predates this gate, or the
    caller simply never populated it) -- `evidence.get("animation")` is then
    `None`, and acceptance must not regress relative to the behaviour before
    the animation verdict was wired in at all.
    """
    writer = ScriptedWriter(_sources("plain"))

    result = write_program(
        project,
        tmp_path,
        writer,
        lambda p, d: {"build": {"quality_pass": True}, "acceptance": {"quality_pass": True}},
    )

    assert result.accepted is True
    assert result.attempts[0].animation_passed is None


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
    project = blank_project("Iface", TargetPlatform.SPECTRUM)

    prompt = writing_prompt(project, with_examples=False)

    assert "unsigned char plat_wait_frame(void);" in prompt
    assert "void plat_cell(unsigned char col, unsigned char row, char glyph);" in prompt
    assert "PLATFORM LIBRARY INTERFACE" in prompt


def test_the_writing_prompt_carries_the_dossier_when_the_project_has_one():
    project = blank_project("Ref", TargetPlatform.SPECTRUM)
    dossier = GameReference(
        identified=True,
        confidence="high",
        title="Zampa Bolas",
        publisher="Iber Soft",
        mechanics=["eat every dot"],
        sources=[
            ReferenceSource(
                url="https://example.org/z",
                title="Zampa Bolas",
                retrieved_at="1985-01-01T00:00:00Z",
            )
        ],
    )

    prompt = writing_prompt(project, with_examples=False, reference=dossier)

    assert "REFERENCE GAME" in prompt
    assert "Zampa Bolas" in prompt


def test_the_writing_prompt_is_unchanged_without_a_dossier():
    project = blank_project("Ref", TargetPlatform.SPECTRUM)

    assert "REFERENCE GAME" not in writing_prompt(project, with_examples=False)


class _FakeMessages:
    """Stands in for client.messages, recording how it was called."""

    def __init__(self, parsed):
        self.parsed = parsed
        self.calls = []

    def stream(self, **kwargs):
        self.calls.append(kwargs)
        return FakeMessageStream(type("Response", (), {"parsed_output": self.parsed})())


class _FakeClient:
    def __init__(self, parsed):
        self.messages = _FakeMessages(parsed)


def test_the_writer_actually_sends_the_dossier_to_the_model():
    """Every other dossier test calls writing_prompt or reference_prompt
    directly, so none of them would notice write() forgetting to pass the
    reference through. This one inspects what actually reached
    client.messages.parse."""
    project = blank_project("Ref", TargetPlatform.SPECTRUM)
    dossier = GameReference(
        identified=True,
        confidence="high",
        title="Zampa Bolas",
        publisher="Iber Soft",
        mechanics=["eat every dot"],
        sources=[
            ReferenceSource(
                url="https://example.org/z",
                title="Zampa Bolas",
                retrieved_at="1985-01-01T00:00:00Z",
            )
        ],
    )
    client = _FakeClient(_sources("with reference"))

    ResponsesProgramWriter(client, reference=dossier).write(project)

    content = client.messages.calls[0]["messages"][0]["content"]
    assert "REFERENCE GAME" in content
    assert "Zampa Bolas" in content


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


def test_repair_prompt_names_a_failing_pacing_gate():
    prompt = repair_prompt(
        {"quality_pass": True},
        {"quality_pass": True},
        None,
        {"quality_pass": True},
        {
            "quality_pass": False,
            "failures": ["g_worst_frame_cost reached 7 at step hold_right_b"],
        },
    )

    assert "DID NOT FIT INSIDE ITS DISPLAY FRAME" in prompt
    assert "g_worst_frame_cost reached 7 at step hold_right_b" in prompt
    assert "plat_wait_frame returns how many whole frames" in prompt


def test_repair_prompt_names_a_failing_attributes_gate():
    prompt = repair_prompt(
        {"quality_pass": True},
        {"quality_pass": True},
        None,
        {"quality_pass": True},
        {"quality_pass": True},
        {
            "quality_pass": False,
            "failures": [
                "3 character cell(s) hold drawn pixels whose ink is the same colour "
                "as their paper, so nothing in them reaches the player: (4,9), "
                "(5,9), (6,9)."
            ],
        },
    )

    assert "WHERE NO PLAYER CAN SEE THEM" in prompt
    assert "(4,9), (5,9), (6,9)" in prompt
    assert "BRIGHT lifts both halves" in prompt


def test_repair_prompt_says_nothing_about_attributes_when_the_gate_abstained():
    # The CPC harness reads no memory and so dumps no display file at all, and
    # a Spectrum run whose screen read came back short keeps none either. Both
    # abstain, and an abstention leaking a section here would spend a whole
    # repair attempt on a screen nobody ever looked at.
    prompt = repair_prompt(
        {"quality_pass": True},
        {"quality_pass": True},
        None,
        {"quality_pass": True},
        {"quality_pass": True},
        {"quality_pass": None, "invisible_cells": [], "failures": []},
    )

    assert prompt == ""


def test_repair_prompt_says_nothing_about_pacing_when_the_gate_abstained():
    # The CPC's plat_wait_frame returns zero without counting anything, so the
    # gate abstains there however good the number looks; abstention is not a
    # bug to report back to the writer.
    prompt = repair_prompt(
        {"quality_pass": True},
        {"quality_pass": True},
        None,
        {"quality_pass": True},
        {"quality_pass": None},
    )

    assert prompt == ""
