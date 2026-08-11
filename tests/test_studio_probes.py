import json
from pathlib import Path

from llmz80.studio.models import GenreId, TargetPlatform
from llmz80.studio.packs import create_default_project
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
    project = create_default_project("Probe", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)

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
    project = create_default_project("Probe", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    reading = dict(service.expected_state(project))
    reading["g_remaining"] = 5

    report = service.probe_report(project, {"probe_after": reading})

    assert report["quality_pass"] is False
    assert report["mismatches"] == ["g_remaining: expected 8, read 5"]


def test_a_missed_frame_fails_the_probe(tmp_path: Path):
    service = StudioService.at(tmp_path)
    project = create_default_project("Probe", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    reading = dict(service.expected_state(project))
    reading["g_worst_frame_cost"] = 2

    report = service.probe_report(project, {"probe_after": reading})

    assert report["quality_pass"] is False
    assert "g_worst_frame_cost: expected 0, read 2" in report["mismatches"]


def test_a_target_without_probes_abstains_instead_of_passing(tmp_path: Path):
    service = StudioService.at(tmp_path)
    project = create_default_project("Probe", TargetPlatform.AMSTRAD_CPC, GenreId.MAZE_CHASE)

    report = service.probe_report(project, {"probe_after": {}})

    assert report["observed"] is False
    assert report["quality_pass"] is None
    assert report["checks"] == {}


def test_sweep_plan_picks_a_direction_that_collects(tmp_path: Path):
    project = create_default_project("Sweep", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)

    plan = sweep_plan(project, 0)

    assert plan["direction"] in {"left", "right", "up", "down"}
    assert plan["collected"] >= 1


def test_sweep_stops_at_a_wall_and_counts_only_what_it_passes():
    project = create_default_project("Sweep", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
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
    project = create_default_project("Keys", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)

    steps = service.scenario_script(project)

    assert project.controls.scheme == "qaop_space"
    keys = {"left": "o", "right": "p", "up": "q", "down": "a", "action": "space"}
    assert [step["id"] for step in steps] == ["start_game", "collect_scores"]
    for step in steps:
        assert step["key"] == keys[step["hold"]]


def test_expected_state_predicts_the_score_a_sweep_must_produce(tmp_path: Path):
    service = StudioService.at(tmp_path)
    project = create_default_project("Predict", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)

    expected = service.expected_state(project, collected=3)

    assert expected["g_score"] == 3 * project.gameplay.score_per_collectible
    assert expected["g_remaining"] == 8 - 3


def test_a_sweep_that_scores_nothing_fails_the_probe(tmp_path: Path):
    service = StudioService.at(tmp_path)
    project = create_default_project("Silent", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    # The engine never awarded the point the design says the sweep must earn.
    reading = dict(service.expected_state(project, collected=0))

    report = service.probe_report(project, {"probe_after": reading}, collected=1)

    assert report["quality_pass"] is False
    assert "g_score: expected 10, read 0" in report["mismatches"]
    assert "g_remaining: expected 7, read 8" in report["mismatches"]


def test_high_score_is_expected_to_track_the_run(tmp_path: Path):
    service = StudioService.at(tmp_path)
    project = create_default_project("Hi", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)

    expected = service.expected_state(project, collected=2)

    assert expected["g_hiscore"] == expected["g_score"] == 20


def test_a_high_score_that_ignores_the_run_fails_the_probe(tmp_path: Path):
    service = StudioService.at(tmp_path)
    project = create_default_project("Hi", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    reading = dict(service.expected_state(project, collected=1))
    reading["g_hiscore"] = 0

    report = service.probe_report(project, {"probe_after": reading}, collected=1)

    assert report["quality_pass"] is False
    assert "g_hiscore: expected 10, read 0" in report["mismatches"]
