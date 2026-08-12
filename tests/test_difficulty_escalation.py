"""Every built-in genre, on every target, actually gets harder.

`difficulty.py` is the gate; this is the proof that `layout.py`'s generators
clear it -- not for a sample, but for the whole catalogue in
`resources/genres.yml`, on both targets, at the same time as the two gates it
must not break to get there: `solvability.py` (every collectible reachable)
and `terrain_structure.py` (terrain still carries its typology's shape). A
generator that hardens levels by sealing a pellet behind a wall, or by
flattening a maze into an empty room, is not a fix; this test is what would
have caught either.

Regenerating `layout.py` does not touch the five saved designs under
`studio-projects/` -- those stay as evidence of what the old generator
produced. This test is about what the generator produces *now*.
"""

import pytest

from llmz80.studio.difficulty import difficulty_report
from llmz80.studio.models import TargetPlatform
from llmz80.studio.packs import BUILTIN_PACKS, create_default_project
from llmz80.studio.solvability import solvability_report
from llmz80.studio.terrain_structure import structure_report

GENRE_IDS = [pack.id for pack in BUILTIN_PACKS]


def _neighbours(cell: tuple[int, int]) -> list[tuple[int, int]]:
    col, row = cell
    return [(col + 1, row), (col - 1, row), (col, row + 1), (col, row - 1)]


@pytest.mark.parametrize("genre", GENRE_IDS)
@pytest.mark.parametrize("platform", list(TargetPlatform))
def test_every_genre_honours_its_declared_difficulty_curve_on_every_target(genre, platform):
    """The gate this whole module exists for: route length never shrinks
    level to level, and grows somewhere. Every built-in pack declares
    `linear` (the model's default), so this is the same check for all of
    them, but each genre reaches it through a different terrain kind and a
    different collectible/enemy count -- exactly the variation that hid the
    old generator's flatness."""
    project = create_default_project("Difficulty", platform, genre)

    report = difficulty_report(project)

    assert report.honored, f"{genre} on {platform.value}: {report.failures}"


@pytest.mark.parametrize("genre", GENRE_IDS)
@pytest.mark.parametrize("platform", list(TargetPlatform))
def test_every_genre_stays_solvable_while_it_escalates(genre, platform):
    """Pushing collectibles further from the player is worthless if one of
    them ends up outside the reachable region. `default_spawns` only chooses
    from cells `_distances` already proved reachable, but the choice of
    *which* reachable cell is new code with its own way to be wrong -- this
    is the check that it isn't, for every genre and level index the pack
    actually authors."""
    project = create_default_project("Solvable", platform, genre)

    report = solvability_report(project)

    assert report.solvable, f"{genre} on {platform.value}: {report.failures}"


@pytest.mark.parametrize("genre", GENRE_IDS)
@pytest.mark.parametrize("platform", list(TargetPlatform))
def test_every_genre_keeps_its_terrain_shape_while_it_escalates(genre, platform):
    """`default_tiles` (and its `PILLAR_PATTERNS`) is unchanged by the
    difficulty work -- escalation here is entirely a spawn-placement lever --
    so this is really a check that it stayed that way: every shaped terrain
    kind still clears `terrain_structure.py`'s calibrated thresholds with
    margin, genre by genre."""
    project = create_default_project("Structured", platform, genre)

    report = structure_report(project)

    assert report.structured, f"{genre} on {platform.value}: {report.failures}"


@pytest.mark.parametrize("genre", GENRE_IDS)
@pytest.mark.parametrize("platform", list(TargetPlatform))
def test_all_three_gates_pass_together_for_every_genre_and_target(genre, platform):
    """The three gates constrain each other -- a fix tuned against one alone
    can quietly break another. This is the combined check the task actually
    asked for: not three separate green ticks, but all three green on the
    same generated project, for the whole catalogue."""
    project = create_default_project("Combined", platform, genre)

    difficulty = difficulty_report(project)
    solvability = solvability_report(project)
    structure = structure_report(project)

    assert difficulty.honored, f"{genre} on {platform.value}: {difficulty.failures}"
    assert solvability.solvable, f"{genre} on {platform.value}: {solvability.failures}"
    assert structure.structured, f"{genre} on {platform.value}: {structure.failures}"


@pytest.mark.parametrize("genre", GENRE_IDS)
def test_route_length_strictly_grows_somewhere_across_every_designs_levels(genre):
    """`honored` alone would pass a design whose levels are all equally
    long -- `flat` allows that, and a single-level design passes vacuously.
    Every built-in pack declares `linear`, which additionally requires at
    least one real increase; this pins that down as an explicit number
    rather than trusting `honored` to have caught it."""
    project = create_default_project("Grows", TargetPlatform.SPECTRUM, genre)

    report = difficulty_report(project)
    steps = [level.estimated_steps for level in report.levels]

    assert max(steps) > min(steps), f"{genre}: route length never varies -- {steps}"
    assert all(b >= a for a, b in zip(steps, steps[1:])), f"{genre}: {steps}"


@pytest.mark.parametrize("genre", GENRE_IDS)
def test_level_one_is_not_a_single_clump_of_collectibles(genre):
    """A regression this exact change could reintroduce: pulling every
    collectible's target radius in tight on level 1 (the easiest level, by
    design) can leave them all mutually adjacent -- solvable, structured,
    and even honouring the curve, but reading as one blob rather than a
    level. At least one collectible must have room around it."""
    project = create_default_project("Uncrowded", TargetPlatform.SPECTRUM, genre)
    level = project.levels[0]
    occupied = {(spawn.col, spawn.row) for spawn in level.spawns}
    roles = {entity.id: entity.role for entity in project.entities}

    collectibles = [
        (spawn.col, spawn.row) for spawn in level.spawns if roles.get(spawn.entity) == "collectible"
    ]

    assert any(
        not any(neighbour in occupied for neighbour in _neighbours(cell)) for cell in collectibles
    ), f"{genre}: every collectible on level 1 is boxed in by another spawn"
