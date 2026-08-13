import pytest

from llmz80.studio.editing import (
    EditError,
    add_entity,
    editing_status,
    fill_screen,
    move_spawn,
    open_char,
    remove_entity,
    rename_screen,
    resize_screen,
    set_entity_count,
    set_scene_next,
    set_screen_time_limit,
    set_tile,
    solid_char,
    toggle_tile,
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


def test_painting_uses_a_character_the_design_declared():
    project = blank_project("Paint", TargetPlatform.SPECTRUM)
    painted = set_tile(project, 0, 2, 2, "#")
    assert painted.screens[0].tiles[2][2] == "#"
    with pytest.raises(EditError):
        set_tile(project, 0, 2, 2, "Z")


def test_painting_uses_a_character_a_third_tile_declared():
    """A design with a ladder can paint ladders, without Studio knowing what
    a ladder is."""
    document = blank_project("Ladders", TargetPlatform.SPECTRUM).model_dump(mode="json")
    document["tiles"].append({"id": "ladder", "char": "H", "traits": ["climbable"]})
    project = GameProject.model_validate(document)
    assert set_tile(project, 0, 3, 3, "H").screens[0].tiles[3][3] == "H"


def test_editing_status_reports_only_what_it_can_know():
    status = editing_status(blank_project("Status", TargetPlatform.SPECTRUM))
    assert set(status) == {"buildable", "backend_error", "ready"}
    assert status["ready"] is True


def test_painting_a_wall_updates_only_that_cell(project):
    col, row = _free_cell(project)

    edited = set_tile(project, 0, col, row, "#")

    assert edited.screens[0].tiles[row][col] == "#"
    unchanged = sum(
        1
        for index, line in enumerate(edited.screens[0].tiles)
        if line == project.screens[0].tiles[index]
    )
    assert unchanged == project.screens[0].height - 1


def test_toggle_returns_terrain_to_its_previous_state(project):
    col, row = _free_cell(project)

    once = toggle_tile(project, 0, col, row)
    twice = toggle_tile(once, 0, col, row)

    assert once.screens[0].tiles[row][col] == solid_char(project)
    assert twice.screens[0].tiles == project.screens[0].tiles


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


def test_adding_and_removing_an_entity_keeps_every_screen_consistent(project):
    added = add_entity(project, "guard", "enemy", count=2)

    assert any(entity.id == "guard" for entity in added.entities)
    for screen in added.screens:
        assert len([spawn for spawn in screen.spawns if spawn.entity == "guard"]) == 2

    removed = remove_entity(added, "guard")

    assert not any(entity.id == "guard" for entity in removed.entities)
    for screen in removed.screens:
        assert not any(spawn.entity == "guard" for spawn in screen.spawns)


def test_removing_an_unknown_entity_is_refused(project):
    with pytest.raises(EditError, match="no entity"):
        remove_entity(project, "ghost")


def test_resizing_keeps_surviving_terrain_and_rehomes_displaced_spawns(project):
    painted = set_tile(project, 0, 3, 3, "#")

    edited = resize_screen(painted, 0, 12, 10)

    assert edited.screens[0].width == 12
    assert edited.screens[0].height == 10
    assert all(len(row) == 12 for row in edited.screens[0].tiles)
    assert edited.screens[0].tiles[3][3] == "#"
    for spawn in edited.screens[0].spawns:
        assert spawn.col < 12 and spawn.row < 10
        assert edited.screens[0].tiles[spawn.row][spawn.col] == open_char(edited)
    placed = {(spawn.col, spawn.row) for spawn in edited.screens[0].spawns}
    assert len(placed) == len(edited.screens[0].spawns)


def test_resizing_below_the_space_the_entities_need_is_refused(project):
    document = project.model_dump(mode="json")
    document["budgets"]["max_entities"] = 64
    roomy = GameProject.model_validate(document)
    crowded = add_entity(roomy, "guard", "enemy", count=60)

    with pytest.raises(EditError, match="free floor cells"):
        resize_screen(crowded, 0, 8, 8)


def test_filling_a_screen_with_open_floor_keeps_spawns_valid(project):
    edited = fill_screen(project, 0, ".")

    assert set("".join(edited.screens[0].tiles)) == {"."}
    assert len(edited.screens[0].spawns) == len(project.screens[0].spawns)


def test_filling_a_screen_with_an_undeclared_tile_is_refused(project):
    with pytest.raises(EditError):
        fill_screen(project, 0, "Z")


def test_renaming_and_time_limit_round_trip(project):
    edited = set_screen_time_limit(rename_screen(project, 0, "CAVERN"), 0, 120)

    assert edited.screens[0].name == "CAVERN"
    assert edited.screens[0].time_limit_seconds == 120


def test_scene_link_to_an_unknown_scene_is_refused(project):
    with pytest.raises(EditError, match="unknown scene"):
        set_scene_next(project, 1, "nowhere")


def test_every_edit_leaves_a_project_the_backend_still_accepts(project):
    edited = set_entity_count(project, "actor", 3)
    edited = resize_screen(edited, 0, 18, 12)
    edited = rename_screen(edited, 0, "FIRST")
    col, row = _free_cell(edited)
    edited = set_tile(edited, 0, col, row, "#")

    status = editing_status(edited)

    assert status["ready"] is True, status


def test_setting_the_count_an_entity_already_has_is_a_no_op(project):
    """Asking for the current count divided by zero before this was fixed."""
    current = next(e.count for e in project.entities if e.id == "actor")

    result = set_entity_count(project, "actor", current)

    assert next(e.count for e in result.entities if e.id == "actor") == current
    for screen in result.screens:
        assert len([s for s in screen.spawns if s.entity == "actor"]) == current
