"""Does a design's authored levels back up the difficulty curve it declares?

`GameplaySpec.difficulty_curve` is a word nothing checked before this gate.
These tests build every fixture from `create_default_project` plus real
edits -- the same discipline `tests/test_terrain_structure.py` uses -- rather
than hand-writing whole `game.yml` documents, so a fixture stays valid
against every other invariant `GameProject` enforces along the way.
"""

from llmz80.studio.difficulty import difficulty_report
from llmz80.studio.editing import move_spawn, set_entity_count, set_time_limit
from llmz80.studio.models import GameProject, GenreId, TargetPlatform
from llmz80.studio.packs import create_default_project


def _with_curve(project: GameProject, curve: str) -> GameProject:
    document = project.model_dump(mode="json")
    document["gameplay"]["difficulty_curve"] = curve
    return type(project).model_validate(document)


def _single_level(project: GameProject) -> GameProject:
    document = project.model_dump(mode="json")
    document["levels"] = document["levels"][:1]
    document["gameplay"]["level_count"] = 1
    return type(project).model_validate(document)


def _spawn_indices(project: GameProject, level_index: int, entity_id: str) -> list[int]:
    return [
        index
        for index, spawn in enumerate(project.levels[level_index].spawns)
        if spawn.entity == entity_id
    ]


def _route(title: str, distances: list[int], curve: str = "linear") -> GameProject:
    """A single-screen-collect project (open terrain, so BFS distance is exact
    Manhattan distance) with one collectible per level, placed `distances[i]`
    cells from the player on level `i`. This controls `estimated_steps`
    directly rather than hoping a generated maze produces the number wanted.

    Enemies are parked in a corner out of the player/collectible row so they
    never collide with the cells this helper places things on.
    """
    project = create_default_project(title, TargetPlatform.SPECTRUM, GenreId.SINGLE_SCREEN_COLLECT)
    project = set_entity_count(project, "collectible", 1)
    for level_index, distance in enumerate(distances):
        for slot, enemy_spawn in enumerate(_spawn_indices(project, level_index, "enemy")):
            project = move_spawn(project, level_index, enemy_spawn, 17, 13 - slot)
        player_spawn = _spawn_indices(project, level_index, "player")[0]
        project = move_spawn(project, level_index, player_spawn, 1, 1)
        collectible_spawn = _spawn_indices(project, level_index, "collectible")[0]
        project = move_spawn(project, level_index, collectible_spawn, 1 + distance, 1)
    return _with_curve(project, curve)


def test_a_linear_design_that_does_not_harden_fails_and_names_the_levels():
    # level_2 has the longest route, level_3 backslides to a shorter one.
    project = _route("Backslide", [1, 9, 4], curve="linear")

    report = difficulty_report(project)

    assert report.honored is False
    assert report.regressions
    failure = next(f for f in report.failures if "level_3" in f and "level_2" in f)
    assert "level_3 is easier than level_2" in failure
    assert "9" in failure and "4" in failure


def test_a_linear_design_that_hardens_passes():
    project = _route("Hardens", [1, 4, 9], curve="linear")

    report = difficulty_report(project)

    assert report.honored is True
    assert report.failures == []
    assert report.regressions == []
    assert report.advances


def test_a_flat_design_that_softens_fails():
    # Getting easier is not flat either.
    project = _route("Softens", [9, 4, 4], curve="flat")

    report = difficulty_report(project)

    assert report.honored is False
    failure = next(f for f in report.failures if "level_2" in f)
    assert "level_2 is easier than level_1" in failure
    assert "9" in failure and "4" in failure


def test_a_flat_design_that_never_gets_easier_passes_even_if_it_hardens():
    # Flat forbids getting easier; it does not forbid getting harder.
    project = _route("Steady-or-up", [4, 4, 9], curve="flat")

    report = difficulty_report(project)

    assert report.honored is True
    assert report.failures == []


def test_a_single_level_design_passes_vacuously_for_every_curve():
    base = create_default_project("Solo", TargetPlatform.SPECTRUM, GenreId.SINGLE_SCREEN_COLLECT)
    solo = _single_level(base)

    for curve in ("flat", "linear", "stepped"):
        report = difficulty_report(_with_curve(solo, curve))

        assert report.honored is True, curve
        assert report.failures == []
        assert report.deltas == []


def test_identical_levels_declared_linear_fail_with_a_did_not_increase_message_not_a_decrease_one():
    project = _route("Flatline", [4, 4, 4], curve="linear")

    report = difficulty_report(project)

    assert report.honored is False
    assert report.regressions == []
    assert len(report.failures) == 1
    failure = report.failures[0]
    assert "no level is ever harder" in failure
    assert "is easier than" not in failure


def test_stepped_is_held_to_the_same_rule_as_linear():
    hardens = difficulty_report(_route("Stepped-up", [1, 4, 9], curve="stepped"))
    flatline = difficulty_report(_route("Stepped-flat", [4, 4, 4], curve="stepped"))

    assert hardens.honored is True
    assert flatline.honored is False
    assert "no level is ever harder" in flatline.failures[0]


def test_a_shrinking_time_limit_alone_satisfies_linear_even_with_a_constant_route():
    project = _route("Clock-tightens", [4, 4, 4], curve="linear")
    project = set_time_limit(project, 0, 60)
    project = set_time_limit(project, 1, 50)
    project = set_time_limit(project, 2, 40)

    report = difficulty_report(project)

    assert report.honored is True
    assert all(delta.harder for delta in report.deltas)


def test_a_loosening_time_limit_makes_a_flat_design_fail_even_with_a_constant_route():
    project = _route("Clock-loosens", [4, 4, 4], curve="flat")
    project = set_time_limit(project, 0, 40)
    project = set_time_limit(project, 1, 60)
    project = set_time_limit(project, 2, 60)

    report = difficulty_report(project)

    assert report.honored is False
    failure = next(f for f in report.failures if "level_2" in f)
    assert "time limit loosens from 40s to 60s" in failure


def test_a_time_limit_only_appearing_on_one_side_of_a_pair_is_not_compared():
    # Setting or dropping a limit is a design choice, not a measured direction.
    project = _route("Clock-appears", [4, 4, 4], curve="flat")
    project = set_time_limit(project, 1, 30)

    report = difficulty_report(project)

    assert report.honored is True
    assert all(not delta.time_limit_comparable for delta in report.deltas)


def test_route_shortening_fails_even_when_the_time_limit_simultaneously_tightens():
    # A regression on one dimension is not cancelled out by an advance on the
    # other -- a shorter, more time-pressured level is still a shorter level.
    project = _route("Mixed-signal", [4, 9, 4], curve="linear")
    project = set_time_limit(project, 1, 60)
    project = set_time_limit(project, 2, 40)

    report = difficulty_report(project)

    assert report.honored is False
    failure = next(f for f in report.failures if "level_3" in f and "level_2" in f)
    assert "route shortens from 9 to 4 steps" in failure
    assert "time limit" not in failure


def test_the_reported_curve_matches_the_projects_declared_curve():
    project = _route("Reported", [1, 4, 9], curve="stepped")

    report = difficulty_report(project)

    assert report.curve == "stepped"


def test_as_dict_carries_per_level_and_per_pair_detail():
    project = _route("Shape", [1, 4, 9], curve="linear")

    document = difficulty_report(project).as_dict()

    assert document["schema_version"] == 1
    assert document["curve"] == "linear"
    assert document["honored"] is True
    assert document["failures"] == []
    assert [level["estimated_steps"] for level in document["levels"]] == [1, 4, 9]
    assert len(document["deltas"]) == 2
    assert document["deltas"][0]["harder"] is True
