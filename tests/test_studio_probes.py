import json
from pathlib import Path

from llmz80.studio.acceptance import runtime_script
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
from llmz80.studio.solvability import sweep_plan

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


def test_expected_state_mirrors_the_design(tmp_path: Path):
    service = StudioService.at(tmp_path)
    project = blank_project("Probe", TargetPlatform.SPECTRUM)

    expected = service.expected_state(project)

    assert expected["g_lives"] == project.gameplay.lives
    assert expected["g_remaining"] == 8
    assert expected == {
        "g_level": 1,
        "g_state": 1,
        "g_lives": 3,
        "g_score": 0,
        "g_remaining": 8,
        "g_worst_frame_cost": 0,
        "g_hiscore": 0,
    }


def test_a_reading_that_contradicts_the_design_fails_the_probe(tmp_path: Path):
    service = StudioService.at(tmp_path)
    project = blank_project("Probe", TargetPlatform.SPECTRUM)
    reading = dict(service.expected_state(project))
    reading["g_remaining"] = 5

    report = service.probe_report(project, {"probe_after": reading})

    assert report["quality_pass"] is False
    assert report["mismatches"] == ["g_remaining: expected 8, read 5"]


def test_a_missed_frame_fails_the_probe(tmp_path: Path):
    service = StudioService.at(tmp_path)
    project = blank_project("Probe", TargetPlatform.SPECTRUM)
    reading = dict(service.expected_state(project))
    reading["g_worst_frame_cost"] = 2

    report = service.probe_report(project, {"probe_after": reading})

    assert report["quality_pass"] is False
    assert "g_worst_frame_cost: expected 0, read 2" in report["mismatches"]


def test_a_target_without_probes_abstains_instead_of_passing(tmp_path: Path):
    service = StudioService.at(tmp_path)
    project = blank_project("Probe", TargetPlatform.AMSTRAD_CPC)

    report = service.probe_report(project, {"probe_after": {}})

    assert report["observed"] is False
    assert report["quality_pass"] is None
    assert report["checks"] == {}


def test_sweep_plan_picks_a_direction_that_collects(tmp_path: Path):
    project = blank_project("Sweep", TargetPlatform.SPECTRUM)

    plan = sweep_plan(project, 0)

    assert plan["direction"] in {"left", "right", "up", "down"}
    assert plan["collected"] >= 1


def test_sweep_stops_at_a_wall_and_counts_only_what_it_passes():
    project = blank_project("Sweep", TargetPlatform.SPECTRUM)
    roles = {entity.id: entity.role for entity in project.entities}
    level = project.levels[0]
    player = next(
        (s.col, s.row) for s in level.spawns if roles[s.entity] == "player"
    )
    collectibles = {
        (s.col, s.row) for s in level.spawns if roles[s.entity] == "collectible"
    }

    plan = sweep_plan(project, 0)
    steps = {"right": (1, 0), "left": (-1, 0), "down": (0, 1), "up": (0, -1)}
    step_col, step_row = steps[plan["direction"]]
    col, row = player
    counted = 0
    while True:
        col += step_col
        row += step_row
        if not (0 <= col < level.width and 0 <= row < level.height):
            break
        if level.tiles[row][col] == "#":
            break
        if (col, row) in collectibles:
            counted += 1

    assert counted == plan["collected"]


def test_the_script_resolves_every_hold_through_the_control_scheme(tmp_path: Path):
    service = StudioService.at(tmp_path)
    project = blank_project("Keys", TargetPlatform.SPECTRUM)

    steps = service.scenario_script(project)

    assert project.controls.scheme == "qaop_space"
    keys = {"left": "o", "right": "p", "up": "q", "down": "a", "action": "space"}
    # The default maze_chase pack's enemy chases, so all three core criteria
    # are executable (see test_default_projects_ship_runnable_acceptance in
    # test_studio_acceptance.py); two more steps probe g_anim_frame alone
    # (see acceptance._animation_probe_steps).
    assert [step["id"] for step in steps] == [
        "start_game",
        "collect_scores",
        "enemy_costs_life",
        "anim_probe_move",
        "anim_probe_idle",
    ]
    for step in steps:
        if step["hold"] == "none":
            assert "key" not in step
        else:
            assert step["key"] == keys[step["hold"]]


def test_a_direction_resolves_to_its_key_under_both_control_schemes(tmp_path: Path):
    service = StudioService.at(tmp_path)
    spectrum = blank_project("Cursors", TargetPlatform.SPECTRUM)
    spectrum.controls.scheme = "cursor_space"

    steps = service.scenario_script(spectrum)

    directions = {"left": "5", "right": "8", "up": "7", "down": "6"}
    collect = next(step for step in steps if step["id"] == "collect_scores")
    assert collect["key"] == directions[collect["hold"]]


def test_a_none_hold_survives_as_a_waiting_step_rather_than_being_dropped(tmp_path: Path):
    service = StudioService.at(tmp_path)
    project = blank_project("Chase", TargetPlatform.SPECTRUM)

    steps = service.scenario_script(project)

    enemy = next(step for step in steps if step["id"] == "enemy_costs_life")
    assert enemy["hold"] == "none"
    # No key field at all: `_run_zesarux` reads `step.get("key")`, and a
    # missing key presses nothing but still holds and reads memory -- exactly
    # what "waits without touching the keyboard" means.
    assert "key" not in enemy


def test_an_unresolvable_hold_is_dropped_but_logged(tmp_path: Path, caplog):
    service = StudioService.at(tmp_path)
    project = blank_project("Stick", TargetPlatform.SPECTRUM)
    project.controls.scheme = "joystick"

    with caplog.at_level("WARNING"):
        steps = service.scenario_script(project)

    assert "collect_scores" not in [step["id"] for step in steps]
    assert any("collect_scores" in record.message for record in caplog.records)
    assert any("joystick" in record.message for record in caplog.records)


def test_expected_state_predicts_the_score_a_sweep_must_produce(tmp_path: Path):
    service = StudioService.at(tmp_path)
    project = blank_project("Predict", TargetPlatform.SPECTRUM)

    expected = service.expected_state(project, collected=3)

    assert expected["g_score"] == 3 * project.gameplay.score_per_collectible
    assert expected["g_remaining"] == 8 - 3


def test_a_sweep_that_scores_nothing_fails_the_probe(tmp_path: Path):
    service = StudioService.at(tmp_path)
    project = blank_project("Silent", TargetPlatform.SPECTRUM)
    # The engine never awarded the point the design says the sweep must earn.
    reading = dict(service.expected_state(project, collected=0))

    report = service.probe_report(project, {"probe_after": reading}, collected=1)

    assert report["quality_pass"] is False
    assert "g_score: expected 10, read 0" in report["mismatches"]
    assert "g_remaining: expected 7, read 8" in report["mismatches"]


def test_high_score_is_expected_to_track_the_run(tmp_path: Path):
    service = StudioService.at(tmp_path)
    project = blank_project("Hi", TargetPlatform.SPECTRUM)

    expected = service.expected_state(project, collected=2)

    assert expected["g_hiscore"] == expected["g_score"] == 20


def test_a_high_score_that_ignores_the_run_fails_the_probe(tmp_path: Path):
    service = StudioService.at(tmp_path)
    project = blank_project("Hi", TargetPlatform.SPECTRUM)
    reading = dict(service.expected_state(project, collected=1))
    reading["g_hiscore"] = 0

    report = service.probe_report(project, {"probe_after": reading}, collected=1)

    assert report["quality_pass"] is False
    assert "g_hiscore: expected 10, read 0" in report["mismatches"]


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


def _readings_that_satisfy_acceptance(project):
    """`step_readings` whose `read` matches every step's own `expect` exactly,
    so `acceptance_report` passes regardless -- plus a uniform `g_anim_frame`
    reading on every step, the way a real emulator read actually behaves: it
    returns the whole known state at each step, not a subset tailored to that
    step's own `expect` (see `_read_probes` in `emulator_smoke.py`), so the
    two animation-probe steps (`acceptance.ANIM_PROBE_MOVE_ID`, `..._IDLE_ID`)
    get a reading too even though they assert nothing of their own.

    Held constant at 0 throughout: the animation gate must still reach a
    definite failure on that evidence -- the same shape of bug the real
    failing run showed, where `g_anim_frame` read 0 at every scripted step.
    """
    return [
        {"id": step["id"], "hold": step["hold"], "read": {**step["expect"], "g_anim_frame": 0}}
        for step in runtime_script(project)
    ]


def test_runtime_tests_report_carries_the_animation_verdict(tmp_path, monkeypatch):
    service = StudioService.at(tmp_path)
    project = blank_project("Anim", TargetPlatform.SPECTRUM)
    # `g_anim_frame` never differs across the one moving reading available,
    # so the gate reaches a definite (failing) verdict rather than abstaining.
    fake_report = {
        "quality_pass": True,
        "probe_after": {},
        "step_readings": _readings_that_satisfy_acceptance(project),
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
        "step_readings": _readings_that_satisfy_acceptance(project),
    }
    _stub_runtime_test(monkeypatch, service, tmp_path, fake_report)

    report = service.runtime_test(project, tmp_path)

    assert report["acceptance"]["quality_pass"] is True
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
