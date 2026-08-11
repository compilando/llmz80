import pytest

from llmz80.studio.editing import (
    EditError,
    add_entity,
    editing_status,
    fill_level,
    move_spawn,
    remove_entity,
    rename_level,
    resize_level,
    set_entity_behaviour,
    set_entity_count,
    set_entity_speed,
    set_scene_next,
    set_tile,
    set_time_limit,
    toggle_tile,
)
from llmz80.studio.models import GameProject, GenreId, TargetPlatform
from llmz80.studio.packs import create_default_project


@pytest.fixture
def project():
    return create_default_project("Editing", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)


def _free_cell(project, level_index=0):
    taken = {(spawn.col, spawn.row) for spawn in project.levels[level_index].spawns}
    level = project.levels[level_index]
    return next(
        (col, row)
        for row, line in enumerate(level.tiles)
        for col, tile in enumerate(line)
        if tile == "." and (col, row) not in taken
    )


def test_painting_a_wall_updates_only_that_cell(project):
    col, row = _free_cell(project)

    edited = set_tile(project, 0, col, row, "#")

    assert edited.levels[0].tiles[row][col] == "#"
    assert edited.levels[1].tiles == project.levels[1].tiles
    unchanged = sum(
        1
        for index, line in enumerate(edited.levels[0].tiles)
        if line == project.levels[0].tiles[index]
    )
    assert unchanged == project.levels[0].height - 1


def test_toggle_returns_terrain_to_its_previous_state(project):
    col, row = _free_cell(project)

    once = toggle_tile(project, 0, col, row)
    twice = toggle_tile(once, 0, col, row)

    assert once.levels[0].tiles[row][col] == "#"
    assert twice.levels[0].tiles == project.levels[0].tiles


def test_walling_a_cell_that_holds_a_spawn_is_refused(project):
    spawn = project.levels[0].spawns[0]

    with pytest.raises(EditError, match=f"move {spawn.entity} before walling"):
        set_tile(project, 0, spawn.col, spawn.row, "#")


def test_painting_outside_the_grid_is_refused(project):
    with pytest.raises(EditError, match="outside the 20x16 grid"):
        set_tile(project, 0, 99, 0, "#")


def test_moving_a_spawn_into_a_wall_is_refused(project):
    wall = next(
        (col, row)
        for row, line in enumerate(project.levels[0].tiles)
        for col, tile in enumerate(line)
        if tile == "#"
    )

    with pytest.raises(EditError, match="inside a wall"):
        move_spawn(project, 0, 0, wall[0], wall[1])


def test_moving_a_spawn_onto_another_is_refused(project):
    other = project.levels[0].spawns[1]

    with pytest.raises(EditError, match="two spawns on cell"):
        move_spawn(project, 0, 0, other.col, other.row)


def test_moving_a_spawn_to_free_floor_succeeds(project):
    col, row = _free_cell(project)

    edited = move_spawn(project, 0, 0, col, row)

    assert (edited.levels[0].spawns[0].col, edited.levels[0].spawns[0].row) == (col, row)


def test_increasing_an_entity_count_places_new_spawns_on_every_level(project):
    edited = set_entity_count(project, "enemy", 4)

    assert next(e for e in edited.entities if e.id == "enemy").count == 4
    for level in edited.levels:
        placed = [spawn for spawn in level.spawns if spawn.entity == "enemy"]
        assert len(placed) == 4
        assert len({(spawn.col, spawn.row) for spawn in placed}) == 4
        assert all(level.tiles[spawn.row][spawn.col] == "." for spawn in placed)


def test_decreasing_an_entity_count_drops_spawns_on_every_level(project):
    edited = set_entity_count(project, "collectible", 3)

    for level in edited.levels:
        assert len([s for s in level.spawns if s.entity == "collectible"]) == 3


def test_entity_count_beyond_the_budget_is_refused(project):
    with pytest.raises(EditError, match="entity count exceeds"):
        set_entity_count(project, "collectible", 20)


def test_adding_and_removing_an_entity_keeps_every_level_consistent(project):
    added = add_entity(project, "guard", "enemy", count=2, speed=2)

    assert any(entity.id == "guard" for entity in added.entities)
    for level in added.levels:
        assert len([spawn for spawn in level.spawns if spawn.entity == "guard"]) == 2

    removed = remove_entity(added, "guard")

    assert not any(entity.id == "guard" for entity in removed.entities)
    for level in removed.levels:
        assert not any(spawn.entity == "guard" for spawn in level.spawns)


def test_the_player_entity_cannot_be_removed(project):
    with pytest.raises(EditError, match="player entity cannot be removed"):
        remove_entity(project, "player")


def test_speed_outside_the_supported_range_is_refused(project):
    assert set_entity_speed(project, "enemy", 4).entities[1].speed == 4

    with pytest.raises(EditError):
        set_entity_speed(project, "enemy", 9)


def test_resizing_keeps_surviving_terrain_and_rehomes_displaced_spawns(project):
    painted = set_tile(project, 0, 3, 3, "#")

    edited = resize_level(painted, 0, 12, 10)

    assert edited.levels[0].width == 12
    assert edited.levels[0].height == 10
    assert all(len(row) == 12 for row in edited.levels[0].tiles)
    assert edited.levels[0].tiles[3][3] == "#"
    for spawn in edited.levels[0].spawns:
        assert spawn.col < 12 and spawn.row < 10
        assert edited.levels[0].tiles[spawn.row][spawn.col] == "."
    placed = {(spawn.col, spawn.row) for spawn in edited.levels[0].spawns}
    assert len(placed) == len(edited.levels[0].spawns)


def test_resizing_below_the_space_the_entities_need_is_refused(project):
    document = project.model_dump()
    document["budgets"]["max_entities"] = 64
    roomy = GameProject.model_validate(document)
    crowded = set_entity_count(set_entity_count(roomy, "collectible", 32), "enemy", 31)

    with pytest.raises(EditError, match="free floor cells"):
        resize_level(crowded, 0, 8, 8)


def test_filling_a_level_with_open_floor_keeps_spawns_valid(project):
    edited = fill_level(project, 0, ".")

    assert set("".join(edited.levels[0].tiles)) == {"."}
    assert len(edited.levels[0].spawns) == len(project.levels[0].spawns)


def test_renaming_and_time_limit_round_trip(project):
    edited = set_time_limit(rename_level(project, 0, "CAVERN"), 0, 120)

    assert edited.levels[0].name == "CAVERN"
    assert edited.levels[0].time_limit_seconds == 120


def test_scene_link_to_an_unknown_scene_is_refused(project):
    with pytest.raises(EditError, match="unknown scene references"):
        set_scene_next(project, 1, "nowhere")


def test_status_reports_solvability_and_buildability_live(project):
    assert editing_status(project)["ready"] is True

    target = next(
        (spawn.col, spawn.row) for spawn in project.levels[0].spawns
        if spawn.entity == "collectible"
    )
    sealed = project
    for col, row in (
        (target[0] + 1, target[1]),
        (target[0] - 1, target[1]),
        (target[0], target[1] + 1),
        (target[0], target[1] - 1),
    ):
        sealed = set_tile(sealed, 0, col, row, "#")

    status = editing_status(sealed)

    assert status["solvable"] is False
    assert status["buildable"] is True
    assert status["ready"] is False
    assert any("seal off" in reason for reason in status["solvability_failures"])


def test_every_edit_leaves_a_project_the_backend_still_accepts(project):
    edited = set_entity_count(project, "enemy", 3)
    edited = set_entity_speed(edited, "enemy", 2)
    edited = resize_level(edited, 0, 18, 14)
    edited = rename_level(edited, 0, "FIRST")
    col, row = _free_cell(edited)
    edited = set_tile(edited, 0, col, row, "#")

    status = editing_status(edited)

    assert status["ready"] is True, status


@pytest.mark.parametrize("behaviour", ["patrol_h", "patrol_v", "bounce", "chase", "guard"])
def test_enemy_behaviour_is_a_design_choice(project, behaviour):
    edited = set_entity_behaviour(project, "enemy", behaviour)

    assert next(e for e in edited.entities if e.id == "enemy").behaviour == behaviour


def test_only_enemies_may_declare_a_behaviour(project):
    with pytest.raises(EditError, match="cannot declare a movement behaviour"):
        set_entity_behaviour(project, "collectible", "chase")


def test_an_unknown_behaviour_is_refused(project):
    with pytest.raises(EditError):
        set_entity_behaviour(project, "enemy", "teleport")
