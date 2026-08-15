import json
import subprocess
from pathlib import Path

from llmz80.core.state_contract import REQUIRED_SYMBOLS
from llmz80.studio import compiler as compiler_module
from llmz80.studio.compiler import BuildResult, build_project
from llmz80.studio.generator import repair_prompt
from llmz80.studio.models import TargetPlatform
from llmz80.studio.samples import blank_project
from llmz80.studio.probes import (
    PROBE_SYMBOLS,
    contract_failures,
    parse_sdcc_noi,
    parse_z88dk_map,
    write_probe_report,
)
from llmz80.studio.services import StudioService
from llmz80.studio.store import ProjectStore

Z88DK_MAP = """
CHAR_BELL                       = $0007 ; const, local, , console_01, , config.inc:150
_g_level                        = $9EFF ; addr, public, , engine, , src/engine.c:20
_g_lives                        = $9F00 ; addr, public, , engine, , src/engine.c:21
_g_remaining                    = $9F01 ; addr, public, , engine, , src/engine.c:22
_g_score                        = $9F02 ; addr, public, , engine, , src/engine.c:23
_g_worst_frame_cost             = $9F04 ; addr, public, , engine, , src/engine.c:26
_g_private                      = $9F06 ; addr, local, , engine, , src/engine.c:27
"""

SDCC_NOI = """
DEF _g_level_width 0x4BEA
DEF _g_level 0x5102
DEF _g_lives 0x5103
DEF _g_remaining 0x5104
DEF _g_score 0x5105
DEF _g_worst_frame_cost 0x5107
DEF _g_hiscore 0x5108
DEF _g_state 0x510a
DEF _g_anim_frame 0x510b
"""


def test_z88dk_map_yields_public_probe_addresses():
    found = parse_z88dk_map(Z88DK_MAP)

    assert found == {
        "g_level": 0x9EFF,
        "g_lives": 0x9F00,
        "g_remaining": 0x9F01,
        "g_score": 0x9F02,
        "g_worst_frame_cost": 0x9F04,
    }


def test_sdcc_noi_yields_probe_addresses_and_ignores_other_globals():
    found = parse_sdcc_noi(SDCC_NOI)

    assert set(found) == set(PROBE_SYMBOLS)
    assert found["g_score"] == 0x5105


def test_a_designs_own_observable_is_located_and_read_at_its_declared_width(tmp_path: Path):
    """The link the whole chain was broken at. A design declares `g_dug`,
    `codegen.render_state_header` declares it extern, the writer defines it --
    and this report only ever searched the state contract, so the symbol was
    never located, never read out of memory and never reached a gate."""
    (tmp_path / "output.map").write_text(
        "_g_score = $9F02 ; addr, public, , engine\n"
        "_g_state = $9F04 ; addr, public, , engine\n"
        "_g_worst_frame_cost = $9F05 ; addr, public, , engine\n"
        "_g_dug = $9F06 ; addr, public, , engine\n"
    )

    report = write_probe_report(tmp_path, "spectrum", {"g_dug": 2})

    assert report["addresses"]["g_dug"] == 0x9F06
    # Read as two bytes because the design said two, not because the contract
    # has an opinion: `emulator_smoke._read_probes` reads `widths[name]`.
    assert report["widths"]["g_dug"] == 2
    assert report["observables"] == ["g_dug"]
    assert report["missing_observables"] == []
    assert contract_failures(report) == []


def test_an_observable_the_design_declared_and_the_program_never_defined_fails_the_build():
    """The design promised a window onto one of its own rules and the program
    did not open it. Treated exactly like a missing required contract symbol,
    since the alternative -- reporting it and building anyway -- is how a
    recorded absence went on being accepted before `contract_failures` was
    consulted at all."""
    failures = contract_failures({"missing_required": [], "missing_observables": ["g_dug"]})

    assert len(failures) == 1
    assert "g_dug" in failures[0]
    assert "game.yml" in failures[0]


def test_probe_report_records_what_could_not_be_located(tmp_path: Path):
    (tmp_path / "output.map").write_text("_g_score = $9F02 ; addr, public, , engine\n")

    report = write_probe_report(tmp_path, "spectrum")

    assert report["complete"] is False
    assert "g_lives" in report["missing"]
    assert json.loads((tmp_path / "probes.json").read_text())["addresses"] == {"g_score": 0x9F02}


# --- StudioService.probe_report: records what memory read, never judges it --
#
# v3's probe_report compared a reading against `expected_state`, which
# predicted exact `g_score`/`g_remaining`/`g_hiscore` values from the
# pellet-sweep script `services.scenario_script` used to drive. Both are
# gone (see `services.py`'s own history): deriving a real expectation from a
# design is the examiner's job, and until it exists there is nothing honest
# for this gate to judge a reading against. It now only records what memory
# said and abstains -- `quality_pass` is always `None`, whether or not a
# reading arrived.


def test_a_reading_is_recorded_but_never_judged(tmp_path: Path):
    service = StudioService.at(tmp_path)
    project = blank_project("Probe", TargetPlatform.SPECTRUM)
    reading = {"g_level": 1, "g_score": 0}

    report = service.probe_report(project, {"probe_after": reading})

    assert report["observed"] is True
    assert report["read"] == reading
    assert report["checks"] == {}
    assert report["mismatches"] == []
    assert report["quality_pass"] is None


def test_a_target_without_probes_abstains_instead_of_passing(tmp_path: Path):
    service = StudioService.at(tmp_path)
    project = blank_project("Probe", TargetPlatform.AMSTRAD_CPC)

    report = service.probe_report(project, {"probe_after": {}})

    assert report["observed"] is False
    assert report["quality_pass"] is None
    assert report["checks"] == {}


def _stub_runtime_test(monkeypatch, service: StudioService, tmp_path: Path, fake_report: dict):
    """Make `runtime_test` run its own merging logic against `fake_report`
    without a build toolchain or emulator: `build` is stubbed to a
    already-succeeded result rooted at `tmp_path`, and the module-level
    `smoke_test` -- the only thing `runtime_test` calls to get a runtime --
    is stubbed to hand back `fake_report` verbatim, the same way `probe_report`
    and `acceptance_report` are exercised elsewhere by handing them a runtime
    dict directly rather than one an emulator produced.
    """
    monkeypatch.setattr(
        service,
        "build",
        lambda project, directory: BuildResult(
            output_dir=tmp_path, success=True, artifact=None, report={"quality_pass": True}
        ),
    )
    monkeypatch.setattr(
        "llmz80.studio.services.smoke_test",
        lambda *args, **kwargs: dict(fake_report),
    )


def _degenerate_animation_readings():
    """Two moving readings and one idle reading, hand-built rather than
    derived from `acceptance.runtime_script` -- which no examiner has
    populated yet, so it always returns `[]` (see `acceptance.py`'s own
    docstring). `feel.animation_report` reads `step_readings` directly and
    does not care where they came from, so this threads `hold` the same way
    `_run_zesarux` does. `g_anim_frame` is held constant at 0 throughout on
    purpose: the animation gate must still reach a definite (failing)
    verdict on evidence this degenerate -- the same shape of bug a real
    failing run showed, where `g_anim_frame` read 0 at every scripted step.

    The two moving steps hold *different* directions, and must: a still frame
    across two holds of the same direction is what a correct program reports
    once the arena has clamped the player, so `feel.animation_report` abstains
    there rather than blaming it. Straddling a direction change is what makes
    this evidence definite instead of ambiguous.
    """
    return [
        {"id": "move_1", "hold": "right", "read": {"g_anim_frame": 0}},
        {"id": "move_2", "hold": "left", "read": {"g_anim_frame": 0}},
        {"id": "idle_1", "hold": "none", "read": {"g_anim_frame": 0}},
    ]


def test_runtime_tests_report_carries_the_animation_verdict(tmp_path, monkeypatch):
    service = StudioService.at(tmp_path)
    project = blank_project("Anim", TargetPlatform.SPECTRUM)
    fake_report = {
        "quality_pass": True,
        "probe_after": {},
        "step_readings": _degenerate_animation_readings(),
    }
    _stub_runtime_test(monkeypatch, service, tmp_path, fake_report)

    report = service.runtime_test(project, tmp_path)

    assert report["animation"]["schema_version"] == 1
    assert report["animation"]["observed"] is True
    assert (tmp_path / "emulator_report.json").is_file()
    assert json.loads((tmp_path / "emulator_report.json").read_text())["animation"] == (
        report["animation"]
    )


def test_a_definite_animation_failure_lowers_the_overall_verdict(tmp_path, monkeypatch):
    service = StudioService.at(tmp_path)
    project = blank_project("Anim", TargetPlatform.SPECTRUM)
    fake_report = {
        "quality_pass": True,
        "probe_after": {},
        "step_readings": _degenerate_animation_readings(),
    }
    _stub_runtime_test(monkeypatch, service, tmp_path, fake_report)

    report = service.runtime_test(project, tmp_path)

    # Acceptance abstains too -- no examiner has derived a script yet -- so
    # the animation gate is the only thing that can lower this verdict here.
    assert report["acceptance"]["quality_pass"] is None
    assert report["animation"]["quality_pass"] is False
    assert report["quality_pass"] is False


def test_an_animation_abstention_does_not_lower_the_overall_verdict(tmp_path, monkeypatch):
    service = StudioService.at(tmp_path)
    project = blank_project("Anim", TargetPlatform.SPECTRUM)
    # No `step_readings` at all -- what the CPC produces, since it has no
    # memory probe adapter -- so the gate abstains rather than judging.
    fake_report = {"quality_pass": True, "probe_after": {}}
    _stub_runtime_test(monkeypatch, service, tmp_path, fake_report)

    report = service.runtime_test(project, tmp_path)

    assert report["animation"]["quality_pass"] is None
    assert report["animation"]["observed"] is False
    assert report["quality_pass"] is True


def _invisible_screen(directory: Path) -> Path:
    """A display file whose first cell holds drawn pixels on ink the same
    colour as its paper -- what `attributes.invisible_cells` refuses, written
    out at the exact length `emulator_smoke._read_screen` would have dumped.
    """
    from llmz80.studio.attributes import ATTRIBUTE_ORIGIN, SCREEN_BYTES, cell_offset

    screen = bytearray(SCREEN_BYTES)
    for line in range(8):
        screen[cell_offset(0, 0) + (line << 8)] = 0xFF
    # PAPER_BLUE | INK_BLUE: pixels were drawn, and nothing in that cell reaches
    # the player.
    screen[ATTRIBUTE_ORIGIN] = 0b00_001_001
    path = directory / "screen.bin"
    path.write_bytes(bytes(screen))
    return path


def test_the_runtime_report_carries_the_pacing_verdict_and_a_refusal_lowers_it(
    tmp_path, monkeypatch
):
    """`runtime_test` folds five gates into its verdict, and the pacing gate's
    place in that fold had no test: replacing `pacing_report(report)` with a
    literal abstention left the suite green, so a loop that overran its display
    frame would have passed the run that measured it. The key has to be in the
    report -- `release.py` and `verification_level` read it by name -- and a
    definite `False` has to lower `quality_pass`.
    """
    service = StudioService.at(tmp_path)
    project = blank_project("Paced", TargetPlatform.SPECTRUM)
    fake_report = {
        "quality_pass": True,
        "platform": "spectrum",
        "probe_after": {},
        # No `g_anim_frame` anywhere, so the animation gate abstains and the
        # pacing gate is the only thing that can lower this verdict.
        "step_readings": [
            {"id": "hold_left_a", "hold": "left", "read": {"g_worst_frame_cost": 4}},
        ],
    }
    _stub_runtime_test(monkeypatch, service, tmp_path, fake_report)

    report = service.runtime_test(project, tmp_path)

    assert report["animation"]["quality_pass"] is None
    assert report["pacing"]["observed"] is True
    assert report["pacing"]["worst"] == 4
    assert report["pacing"]["quality_pass"] is False
    assert report["quality_pass"] is False
    assert json.loads((tmp_path / "emulator_report.json").read_text())["pacing"] == (
        report["pacing"]
    )


def test_the_runtime_report_carries_the_attribute_verdict_and_a_refusal_lowers_it(
    tmp_path, monkeypatch
):
    """The same untested fold as the pacing gate's: with `attribute_report`
    replaced by a literal abstention the suite stayed green, so a screen whose
    drawn pixels no player could see passed the run that read it.
    """
    service = StudioService.at(tmp_path)
    project = blank_project("Drawn", TargetPlatform.SPECTRUM)
    fake_report = {
        "quality_pass": True,
        "platform": "amstrad_cpc",  # the pacing gate abstains, leaving this gate alone
        "probe_after": {},
        "screen_dump": str(_invisible_screen(tmp_path)),
    }
    _stub_runtime_test(monkeypatch, service, tmp_path, fake_report)

    report = service.runtime_test(project, tmp_path)

    assert report["pacing"]["quality_pass"] is None
    assert report["attributes"]["observed"] is True
    assert report["attributes"]["invisible_cells"] == [(0, 0)]
    assert report["attributes"]["quality_pass"] is False
    assert report["quality_pass"] is False
    # Round-tripped through JSON, where the cell tuples come back as lists.
    written = json.loads((tmp_path / "emulator_report.json").read_text())
    assert written["attributes"]["quality_pass"] is False
    assert written["attributes"]["invisible_cells"] == [[0, 0]]


def test_a_missing_required_symbol_is_a_diagnostic_the_writer_can_act_on():
    failures = contract_failures({"missing_required": ["g_score", "g_state"]})

    assert len(failures) == 1
    assert "g_score" in failures[0]
    assert "g_state" in failures[0]
    assert "static" in failures[0]


def test_nothing_missing_is_no_diagnostic():
    assert contract_failures({"missing_required": []}) == []
    assert contract_failures({}) == []


def test_the_frame_cost_is_part_of_the_contract_every_program_must_honour():
    """A game that cannot report how badly it missed its frame cannot be judged
    on pacing, and pacing is the one performance claim the machine can make for
    any design whatsoever."""
    assert "g_worst_frame_cost" in REQUIRED_SYMBOLS


# --- The gate itself: the build must refuse, not merely report ---------------
#
# `contract_failures` being right is not the fix. The defect was that nothing
# consulted it: `write_probe_report` recorded `missing_required`, and
# `build.quality_pass` -- the only thing `generator.write_program` reads to set
# `attempt.build_passed` -- never looked. A program declaring `g_score` static
# compiled, was unprobeable, and was accepted. These two drive the real
# `build_project` with the toolchain faked out, so a future edit that deletes
# the wiring while keeping the helper fails here.


#: Chatter a real toolchain prints on the way to a successful link, long
#: enough to overrun `generator.repair_prompt`'s diagnostics budget on its
#: own. A silent toolchain is not the case that matters: a CPCtelera build
#: prints several kilobytes of this before it says anything about the
#: program, and the whole point of the contract diagnostic is that it must
#: still reach the writer through that. Deliberately free of the word
#: "warning", which `build_quality.classify_build_warnings` would count and
#: fail the build over -- a different refusal than the one under test.
TOOLCHAIN_NOISE = "".join(f"compiling obj/module_{index:03d}.rel\n" for index in range(300))


def _fake_toolchain(monkeypatch, symbols: list[str]):
    """Stand in for zcc: succeed instantly, writing the artifact and a map
    that carries exactly `symbols` as public addresses, over a realistic
    quantity of build chatter.

    Which symbols land in the map is the entire variable under test here, so
    the fake takes them as an argument rather than compiling a C program that
    would have to be believed to produce them.
    """

    def fake_run(command, cwd, capture_output, text, check):
        (Path(cwd) / "output.tap").write_bytes(b"\x00" * 64)
        (Path(cwd) / "output.map").write_text(
            "".join(
                f"_{name}{' ' * 8}= ${0x9F00 + index:04X} ; addr, public, , main\n"
                for index, name in enumerate(symbols)
            ),
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(
            command, 0, stdout=TOOLCHAIN_NOISE, stderr=TOOLCHAIN_NOISE
        )

    monkeypatch.setattr(compiler_module.subprocess, "run", fake_run)


def _built_with_symbols(tmp_path: Path, monkeypatch, symbols: list[str]):
    _fake_toolchain(monkeypatch, symbols)
    project = blank_project("Gate", TargetPlatform.SPECTRUM)
    directory = ProjectStore(tmp_path).create(project)
    program_dir = directory / project.program_dir
    program_dir.mkdir(parents=True, exist_ok=True)
    (program_dir / "main.c").write_text(
        '#include "platform.h"\n\nvoid main(void) { plat_init(); while (1) { } }\n',
        encoding="utf-8",
    )
    return build_project(project, directory / "build")


def test_a_build_whose_state_cannot_be_read_is_refused(tmp_path: Path, monkeypatch):
    build = _built_with_symbols(tmp_path, monkeypatch, ["g_state", "g_worst_frame_cost"])

    assert build.success is False
    assert build.report["quality_pass"] is False
    assert "g_score" in build.report["contract_errors"][0]
    assert "g_score" in build.report["stderr"]


def test_the_refusal_survives_a_toolchain_noisy_enough_to_bury_it(tmp_path: Path, monkeypatch):
    """Refusing is worthless if the writer never reads why.

    `repair_prompt` used to slice the *concatenation* of stderr and stdout to
    its last 3000 characters, so a build that printed more than that dropped
    all of stderr -- where both the compiler's errors and this diagnostic
    live -- and handed the writer nothing but the tail of stdout. Asserting
    the diagnostic is in `report["stderr"]` does not catch that; only reading
    it back out of the prompt the writer is actually given does.

    `probes` is passed as None deliberately. `repair_prompt` has its own
    "CONTRACT SYMBOLS ARE MISSING" section fed straight from the probe
    report, and it names the same symbol -- so handing it the real probes
    would let these assertions pass through that section while the build
    section stayed truncated, proving nothing about the path under test.
    """
    build = _built_with_symbols(tmp_path, monkeypatch, ["g_state", "g_worst_frame_cost"])
    assert len(build.report["stdout"]) > 3000  # the fake really is noisy

    prompt = repair_prompt(build.report, None, None, None)

    assert "absent from the linker map" in prompt
    assert "g_score" in prompt


def test_a_build_that_carries_every_required_symbol_still_passes(tmp_path: Path, monkeypatch):
    build = _built_with_symbols(tmp_path, monkeypatch, list(REQUIRED_SYMBOLS))

    assert build.success is True, build.report.get("stderr")
    assert "contract_errors" not in build.report
    assert build.report["probes"]["contract_honoured"] is True
