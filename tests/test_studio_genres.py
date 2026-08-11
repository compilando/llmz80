import pytest

from llmz80.studio.compiler import validate_design_fits_target
from llmz80.studio.layout import TERRAIN_SHAPERS, default_tiles
from llmz80.studio.models import TargetPlatform
from llmz80.studio.packs import BUILTIN_PACKS, PACKS_BY_ID, create_default_project
from llmz80.studio.quality import design_quality_report
from llmz80.studio.retrieval import retrieval_query
from llmz80.studio.solvability import solvability_report

TYPOLOGY_IDS = [pack.id for pack in BUILTIN_PACKS]


def test_the_catalogue_covers_the_common_typologies():
    assert len(BUILTIN_PACKS) >= 15
    for expected in ("maze_chase", "platform_single_screen", "shooter_vertical", "breakout"):
        assert expected in PACKS_BY_ID


def test_every_typology_names_a_terrain_that_exists():
    for pack in BUILTIN_PACKS:
        assert pack.terrain == "open" or pack.terrain in TERRAIN_SHAPERS


@pytest.mark.parametrize("genre", TYPOLOGY_IDS)
@pytest.mark.parametrize("platform", list(TargetPlatform))
def test_every_typology_starts_from_a_design_that_passes_its_gates(genre, platform):
    project = create_default_project("Typology", platform, genre)

    report = design_quality_report(project)

    assert report["quality_pass"], f"{genre} on {platform.value}: {report['failures']}"
    validate_design_fits_target(project)


@pytest.mark.parametrize("genre", TYPOLOGY_IDS)
def test_every_typology_is_solvable_on_every_level(genre):
    project = create_default_project("Solvable", TargetPlatform.SPECTRUM, genre)

    report = solvability_report(project)

    assert report.solvable, f"{genre}: {report.failures}"


@pytest.mark.parametrize("genre", TYPOLOGY_IDS)
def test_every_typology_has_a_runnable_acceptance_step(genre):
    project = create_default_project("Runnable", TargetPlatform.SPECTRUM, genre)

    executable = [s for s in project.acceptance if s.executable]

    assert any(s.id == "start_game" for s in executable)


def test_terrain_shapes_differ_between_typologies():
    maze = default_tiles("x", 20, 16, 0, "maze")
    ledges = default_tiles("x", 20, 16, 0, "ledges")
    open_field = default_tiles("x", 20, 16, 0, "open")

    assert maze != ledges != open_field
    assert "#" not in "".join(row[1:-1] for row in open_field[1:-1])


def test_chambers_leave_every_quadrant_reachable():
    # A single doorway per wall seals a quadrant; this caught that in review.
    for index in range(3):
        tiles = default_tiles("x", 20, 16, index, "chambers")
        floor = {
            (c, r)
            for r, line in enumerate(tiles)
            for c, tile in enumerate(line)
            if tile == "."
        }
        start = min(floor)
        seen, queue = {start}, [start]
        while queue:
            col, row = queue.pop()
            for cell in ((col+1, row), (col-1, row), (col, row+1), (col, row-1)):
                if cell in floor and cell not in seen:
                    seen.add(cell)
                    queue.append(cell)
        assert seen == floor, f"chambers level {index} seals off {len(floor - seen)} cells"


def test_the_typology_shapes_its_entities():
    shooter = create_default_project("S", TargetPlatform.SPECTRUM, "shooter_vertical")
    maze = create_default_project("M", TargetPlatform.SPECTRUM, "maze_chase")

    shooter_enemy = next(e for e in shooter.entities if e.role == "enemy")
    maze_enemy = next(e for e in maze.entities if e.role == "enemy")

    assert shooter_enemy.count == 4 and shooter_enemy.behaviour == "patrol_v"
    assert maze_enemy.behaviour == "chase"
    assert shooter.presentation.style != maze.presentation.style


def test_the_retrieval_query_uses_the_typologys_vocabulary():
    project = create_default_project("B", TargetPlatform.SPECTRUM, "breakout")

    query = retrieval_query(project)

    assert "ball" in query and "bricks" in query
