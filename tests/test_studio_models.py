from collections import Counter
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from llmz80.studio.models import AssetSpec, GenreId, TargetPlatform, VideoMode
from llmz80.studio.packs import create_default_project
from llmz80.studio.store import ProjectStore


@pytest.mark.parametrize("platform", list(TargetPlatform))
@pytest.mark.parametrize("genre", list(GenreId))
def test_every_builtin_project_is_complete(platform, genre):
    project = create_default_project("Test Game", platform, genre)

    assert project.schema_version == 3
    assert project.gameplay.level_count == len(project.levels) == 3
    assert {entity.role for entity in project.entities} >= {"player", "enemy", "collectible"}
    assert len(project.acceptance) >= 3


def test_platform_and_video_mode_must_match():
    project = create_default_project("Invalid Mode", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    data = project.model_dump()
    data["target"]["video_mode"] = VideoMode.CPC_MODE_0

    with pytest.raises(ValidationError, match="Spectrum projects require"):
        type(project).model_validate(data)


def test_entity_budget_is_enforced():
    project = create_default_project("Too Many", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    data = project.model_dump()
    data["budgets"]["max_entities"] = 2

    with pytest.raises(ValidationError, match="entity count exceeds"):
        type(project).model_validate(data)


def test_yaml_roundtrip_and_revision_history(tmp_path: Path):
    store = ProjectStore(tmp_path)
    project = create_default_project("Saved Game", TargetPlatform.AMSTRAD_CPC, GenreId.MAZE_CHASE)
    directory = store.create(project)

    loaded = store.load(directory)
    assert loaded == project
    loaded.gameplay.lives = 5
    store.save(loaded, directory)

    revisions = list((directory / ".llmz80" / "revisions").glob("*.yml"))
    assert len(revisions) == 1
    assert ProjectStore(tmp_path).load(directory).gameplay.lives == 5


def test_levels_carry_terrain_and_one_spawn_per_entity_instance():
    project = create_default_project("Mapped", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)

    for level in project.levels:
        assert len(level.tiles) == level.height
        assert all(len(row) == level.width for row in level.tiles)
        assert set("".join(level.tiles)) <= {".", "#"}
        placed = Counter(spawn.entity for spawn in level.spawns)
        for entity in project.entities:
            assert placed[entity.id] == entity.count
        assert all(level.tiles[s.row][s.col] == "." for s in level.spawns)


def test_terrain_leaves_every_floor_cell_reachable():
    project = create_default_project("Reachable", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)

    for level in project.levels:
        floor = {
            (col, row)
            for row, line in enumerate(level.tiles)
            for col, tile in enumerate(line)
            if tile == "."
        }
        start = next(iter(sorted(floor)))
        seen = {start}
        queue = [start]
        while queue:
            col, row = queue.pop()
            for step in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                cell = (col + step[0], row + step[1])
                if cell in floor and cell not in seen:
                    seen.add(cell)
                    queue.append(cell)
        assert seen == floor, f"{level.id} has floor cells sealed off by generated walls"


def test_spawn_inside_a_wall_is_rejected():
    project = create_default_project("Walled", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    data = project.model_dump()
    data["levels"][0]["spawns"][0]["col"] = 0
    data["levels"][0]["spawns"][0]["row"] = 0

    with pytest.raises(ValidationError, match="inside a wall"):
        type(project).model_validate(data)


def test_spawn_count_must_match_entity_count():
    project = create_default_project("Missing", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    data = project.model_dump()
    data["levels"][0]["spawns"] = [
        spawn for spawn in data["levels"][0]["spawns"] if spawn["entity"] != "collectible"
    ]

    with pytest.raises(ValidationError, match="collectible placed 0 times, expected 8"):
        type(project).model_validate(data)


def test_v2_documents_migrate_to_v3_on_load(tmp_path: Path):
    project = create_default_project("Legacy", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    document = project.model_dump(mode="json")
    document["schema_version"] = 2
    for level in document["levels"]:
        del level["tiles"]
        del level["spawns"]
    directory = tmp_path / "legacy"
    directory.mkdir()
    (directory / "game.yml").write_text(yaml.safe_dump(document), encoding="utf-8")

    loaded = ProjectStore(tmp_path).load(directory)

    assert loaded.schema_version == 3
    assert loaded.levels[0].tiles == project.levels[0].tiles
    assert loaded.levels[0].spawns == project.levels[0].spawns


def test_an_asset_declares_its_frames():
    asset = AssetSpec(id="hero", source="assets/hero.png", width=64, height=16, frames=4)

    assert asset.frames == 4
    assert asset.frame_width == 16


def test_an_asset_sheet_must_divide_into_whole_frames():
    """A sheet 65 wide cannot hold 4 frames; the split would silently lose a column."""
    with pytest.raises(ValidationError, match="frames"):
        AssetSpec(id="hero", source="assets/hero.png", width=65, height=16, frames=4)


def test_an_entity_may_name_a_sprite_that_no_asset_provides():
    """Designs predating any artwork must keep loading; the library falls back to shapes."""
    project = create_default_project("Fallback", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)

    assert project.assets == []
    assert any(entity.sprite for entity in project.entities)
