import json
from pathlib import Path

from llmz80.studio.compiler import BuildResult
from llmz80.studio.models import TargetPlatform
from llmz80.studio.samples import blank_project
from llmz80.studio.probes import (
    PROBE_SYMBOLS,
    parse_sdcc_noi,
    parse_z88dk_map,
    write_probe_report,
)
from llmz80.studio.services import StudioService

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
