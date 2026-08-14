"""What is left of the editor: three edits, and the sentence that reports one.

The other ten operations went with the map panel that was the only thing
calling them, and their tests went with them. The edits below that build an
"after" project by hand -- painting a cell, adding an entity -- do it through
the document rather than through an operation, because the operation that did
it was one of the ten: `describe_changes` has to go on recognising a painted
cell whoever painted it.
"""

import pytest

from llmz80.studio.editing import (
    EditError,
    describe_changes,
    editing_status,
    move_spawn,
    open_char,
    set_entity_count,
)
from llmz80.studio.models import GameProject, TargetPlatform
from llmz80.studio.samples import blank_project


@pytest.fixture
def project():
    return blank_project("Editing", TargetPlatform.SPECTRUM)


def _free_cell(project, screen_index=0):
    screen = project.screens[screen_index]
    taken = {(spawn.col, spawn.row) for spawn in screen.spawns}
    free = open_char(project)
    return next(
        (col, row)
        for row, line in enumerate(screen.tiles)
        for col, tile in enumerate(line)
        if tile == free and (col, row) not in taken
    )


def _painted(project, cells, char="#"):
    """The same design with `cells` repainted, built through the document."""
    document = project.model_dump(mode="json")
    rows = list(document["screens"][0]["tiles"])
    for col, row in cells:
        rows[row] = rows[row][:col] + char + rows[row][col + 1 :]
    document["screens"][0]["tiles"] = rows
    return GameProject.model_validate(document)


def _with_a_ghost(project, count=2):
    """A new entity, placed on free floor on every screen."""
    document = project.model_dump(mode="json")
    document["entities"].append({"id": "ghost", "kind": "enemy", "sprite": None, "count": count})
    free = open_char(project)
    for screen in document["screens"]:
        taken = {(spawn["col"], spawn["row"]) for spawn in screen["spawns"]}
        cells = [
            (col, row)
            for row, line in enumerate(screen["tiles"])
            for col, tile in enumerate(line)
            if tile == free and (col, row) not in taken
        ]
        for col, row in cells[:count]:
            screen["spawns"].append({"entity": "ghost", "col": col, "row": row})
    return GameProject.model_validate(document)


def test_editing_status_reports_only_what_it_can_know():
    status = editing_status(blank_project("Status", TargetPlatform.SPECTRUM))
    assert set(status) == {"buildable", "backend_error", "ready"}
    assert status["ready"] is True


def test_moving_a_spawn_to_free_floor_succeeds(project):
    col, row = _free_cell(project)

    edited = move_spawn(project, 0, 0, col, row)

    assert (edited.screens[0].spawns[0].col, edited.screens[0].spawns[0].row) == (col, row)


def test_moving_a_spawn_outside_the_grid_is_refused(project):
    with pytest.raises(EditError, match="outside the 20x14 grid"):
        move_spawn(project, 0, 0, 99, 0)


def test_increasing_an_entity_count_places_a_spawn_on_every_screen(project):
    edited = set_entity_count(project, "actor", 3)

    assert next(e for e in edited.entities if e.id == "actor").count == 3
    for screen in edited.screens:
        placed = [spawn for spawn in screen.spawns if spawn.entity == "actor"]
        assert len(placed) == 3
        assert len({(spawn.col, spawn.row) for spawn in placed}) == 3
        assert all(screen.tiles[spawn.row][spawn.col] == open_char(edited) for spawn in placed)


def test_decreasing_an_entity_count_drops_spawns_on_every_screen(project):
    grown = set_entity_count(project, "actor", 4)

    edited = set_entity_count(grown, "actor", 2)

    for screen in edited.screens:
        assert len([s for s in screen.spawns if s.entity == "actor"]) == 2


def test_entity_count_beyond_the_budget_is_refused(project):
    with pytest.raises(EditError, match="exceeds the max_entities budget"):
        set_entity_count(project, "actor", 20)


def test_setting_the_count_an_entity_already_has_is_a_no_op(project):
    """Asking for the current count divided by zero before this was fixed."""
    current = next(e.count for e in project.entities if e.id == "actor")

    result = set_entity_count(project, "actor", current)

    assert next(e.count for e in result.entities if e.id == "actor") == current
    for screen in result.screens:
        assert len([s for s in screen.spawns if s.entity == "actor"]) == current


def test_an_edit_leaves_a_project_the_backend_still_accepts(project):
    edited = set_entity_count(project, "actor", 3)
    col, row = _free_cell(edited)
    edited = move_spawn(edited, 0, 0, col, row)

    status = editing_status(edited)

    assert status["ready"] is True, status


# --- what a save actually saved ---------------------------------------------


def test_a_design_that_did_not_change_is_described_as_nothing(project):
    """`store.save` stamps `updated_at` on every write, so a version that
    differs only there is the same design and must read as no change at all."""
    from datetime import datetime, timezone

    same = project.model_copy(deep=True)
    same.metadata.updated_at = datetime(2030, 1, 1, tzinfo=timezone.utc)

    assert describe_changes(project, same) == ""


def test_painted_cells_are_counted(project):
    assert describe_changes(project, _painted(project, [(2, 2), (3, 3)])) == "2 cells painted"
    assert describe_changes(project, _painted(project, [(2, 2)])) == "1 cell painted"


def test_a_moved_spawn_reads_as_moved_rather_than_as_two(project):
    """One spawn of an entity gone and one arrived is that entity moved, which
    is what the person who moved it will recognise."""
    spawn = project.screens[0].spawns[0]
    cell = _free_cell(project)

    moved = move_spawn(project, 0, 0, *cell)

    assert (spawn.col, spawn.row) != cell
    assert describe_changes(project, moved) == "1 spawn moved"


def test_the_roster_names_what_was_added_and_recounted(project):
    described = describe_changes(project, _with_a_ghost(project, count=2))
    assert "1 entity added: ghost" in described
    # An entity placed on every screen is worth saying too.
    assert "2 spawns placed" in described

    recounted = describe_changes(project, set_entity_count(project, "actor", 3))
    assert "actor count 1->3" in recounted


def test_the_scalar_fields_a_form_edits_are_named_not_quoted(project):
    """A brief runs to paragraphs; a diary line is one line."""
    from llmz80.studio.editing import rename_project

    described = describe_changes(
        project, rename_project(project, "Another Name", brief="Four ghosts.")
    )

    assert described == "title changed, brief changed"
    assert "Four ghosts." not in described


def test_a_field_this_summary_does_not_read_is_still_named(project):
    """An adaptation rewrites tiles, mechanics and scenes at once, and a
    sprite run adds assets: a line that only knew how to look at terrain
    would report that nothing had happened."""
    document = project.model_dump(mode="json")
    document["mechanics"] = ["the player jumps"]
    document["tiles"].append({"id": "ladder", "char": "H", "traits": ["climbable"]})

    described = describe_changes(project, GameProject.model_validate(document))

    assert described == "mechanics, tiles changed"


def test_a_resized_screen_says_so_instead_of_counting_its_new_rows(project):
    document = project.model_dump(mode="json")
    screen = document["screens"][0]
    free = open_char(project)
    screen["width"] = 24
    screen["tiles"] = [row + free * 4 for row in screen["tiles"]]

    described = describe_changes(project, GameProject.model_validate(document))

    assert "screen_1 is now 24x14" in described
