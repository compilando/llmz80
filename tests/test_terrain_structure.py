"""The empty-room gate: does a level's terrain carry its genre's shape?

Solvability proves a level can be finished; it says nothing about whether it
is the kind of level its typology promises. An empty bordered room is
trivially solvable -- everything reaches everything -- but a `maze_chase`
with no interior walls is not a maze. `every_level_has_genre_shaped_terrain`
in `design_quality_report` is the gate that notices.
"""

from types import SimpleNamespace

from llmz80.studio.layout import TERRAIN_SHAPERS, default_tiles
from llmz80.studio.models import GenreId, TargetPlatform
from llmz80.studio.packs import BUILTIN_PACKS, create_default_project
from llmz80.studio.quality import design_quality_report
from llmz80.studio.terrain_structure import (
    TERRAIN_THRESHOLDS,
    analyse_level_structure,
    structure_report,
)

TERRAIN_GENRES = {
    pack.id: pack.terrain for pack in BUILTIN_PACKS if pack.terrain in TERRAIN_SHAPERS
}


def _blank_interior(project, level_index):
    """Return a copy whose level has its interior walls stripped to floor."""
    document = project.model_dump(mode="json")
    level = document["levels"][level_index]
    width, height = level["width"], level["height"]
    rows = [list(row) for row in level["tiles"]]
    for row in range(1, height - 1):
        for column in range(1, width - 1):
            rows[row][column] = "."
    level["tiles"] = ["".join(row) for row in rows]
    return type(project).model_validate(document)


def _place_solid_block(project, level_index, size=6):
    """Return a copy whose level's only interior structure is one solid block.

    Existing interior walls are stripped first, so the block is the level's
    entire wall content -- otherwise it would just add one more shape to the
    genuine maze pillars already there and prove nothing.
    """
    document = project.model_dump(mode="json")
    level = document["levels"][level_index]
    width, height = level["width"], level["height"]
    occupied = {(spawn["col"], spawn["row"]) for spawn in level["spawns"]}
    rows = [list(row) for row in level["tiles"]]
    for row in range(1, height - 1):
        for column in range(1, width - 1):
            rows[row][column] = "."
    block = None
    for top in range(1, height - 1 - size):
        for left in range(1, width - 1 - size):
            cells = [(c, r) for r in range(top, top + size) for c in range(left, left + size)]
            if not any(cell in occupied for cell in cells):
                block = cells
                break
        if block:
            break
    if block is None:
        raise AssertionError(f"no {size}x{size} block fits without covering a spawn")
    for column, row in block:
        rows[row][column] = "#"
    level["tiles"] = ["".join(row) for row in rows]
    return type(project).model_validate(document)


def test_an_empty_room_fails_the_terrain_structure_gate():
    project = create_default_project("Empty", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    empty = _blank_interior(project, 0)

    report = structure_report(empty)

    assert report.structured is False
    assert not report.levels[0].structured
    assert report.levels[0].wall_ratio == 0.0
    assert report.levels[0].wall_components == 0
    assert any("level_1" in reason for reason in report.failures)


def test_an_empty_room_fails_the_design_quality_gate_with_an_actionable_reason():
    project = create_default_project("Empty", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    empty = _blank_interior(project, 0)

    result = design_quality_report(empty)

    assert result["checks"]["every_level_has_genre_shaped_terrain"] is False
    assert "every_level_has_genre_shaped_terrain" in result["failures"]
    assert result["quality_pass"] is False
    # The gate stays solvable throughout -- this is a different question from
    # reachability, and must not be confused with it in the report.
    assert result["checks"]["every_level_is_solvable"] is True
    assert any("level_1" in reason for reason in result["terrain_structure_failures"])
    # Only the edited level should be implicated; levels 2 and 3 still carry a
    # real maze and must not be swept up in a whole-project failure.
    assert not any("level_2" in reason for reason in result["terrain_structure_failures"])
    assert not any("level_3" in reason for reason in result["terrain_structure_failures"])


def test_a_single_solid_wall_block_fails_the_gate_even_though_ratio_alone_would_pass():
    project = create_default_project("Blocky", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    blocky = _place_solid_block(project, 0, size=6)

    report = structure_report(blocky)
    level = report.levels[0]

    # The block alone clears the ratio floor a real maze needs...
    assert level.wall_ratio >= TERRAIN_THRESHOLDS["maze"][0]
    # ...but it is one shape, not the many separate obstacles a maze needs,
    # so the gate still refuses it.
    assert level.wall_components == 1
    assert level.structured is False
    assert report.structured is False

    result = design_quality_report(blocky)
    assert result["checks"]["every_level_has_genre_shaped_terrain"] is False
    assert result["checks"]["every_level_is_solvable"] is True


def test_every_shaped_terrain_kind_authored_by_studio_passes_the_gate():
    """Every genre pack whose terrain isn't `open`, on every level it authors."""
    assert TERRAIN_GENRES, "expected at least one genre with structured terrain"
    for genre, terrain in TERRAIN_GENRES.items():
        for platform in TargetPlatform:
            project = create_default_project("Structured", platform, genre)

            report = structure_report(project)

            assert report.structured, f"{genre}/{terrain} on {platform.value}: {report.failures}"
            for level in report.levels:
                assert not level.exempt
                assert level.terrain == terrain


def test_open_terrain_genres_are_exempt_from_the_gate():
    open_genres = {pack.id for pack in BUILTIN_PACKS if pack.terrain == "open"}
    assert open_genres
    for genre in open_genres:
        project = create_default_project("Open", TargetPlatform.SPECTRUM, genre)

        report = structure_report(project)

        assert report.structured
        assert all(level.exempt for level in report.levels)


def test_layout_generates_structure_with_margin_over_the_threshold_for_every_level_index():
    """`layout.py`'s own generators, at the size Studio actually authors,
    must clear the gate with room to spare -- for every terrain kind and
    every level index its pattern cycles through, not just level 0."""
    width, height = 20, 16
    for terrain in TERRAIN_SHAPERS:
        if terrain not in TERRAIN_THRESHOLDS:
            continue
        for level_index in range(6):
            tiles = default_tiles("x", width, height, level_index, terrain)
            level = SimpleNamespace(
                id=f"level_{level_index}", width=width, height=height, tiles=tiles
            )
            structure = analyse_level_structure(terrain, level)

            assert structure.structured, (
                f"{terrain} level index {level_index}: ratio={structure.wall_ratio:.3f} "
                f"components={structure.wall_components}"
            )


def test_the_terrain_structure_check_is_reported_in_design_quality_report():
    project = create_default_project("Reported", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)

    result = design_quality_report(project)

    assert "every_level_has_genre_shaped_terrain" in result["checks"]
    assert result["checks"]["every_level_has_genre_shaped_terrain"] is True
    assert "terrain_structure_failures" in result
    assert "terrain_structure" in result
    assert result["terrain_structure"]["structured"] is True
