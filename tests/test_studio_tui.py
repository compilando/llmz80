from pathlib import Path

import pytest

from llmz80.studio.models import GenreId, TargetPlatform
from llmz80.studio.packs import create_default_project
from llmz80.studio.tui import StudioApp, render_map


@pytest.mark.asyncio
async def test_tui_creates_and_generates_project(tmp_path: Path):
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#new-title").value = "Pilot Game"
        await pilot.click("#create")
        await pilot.pause()

        assert (tmp_path / "pilot-game" / "game.yml").is_file()
        assert app.project is not None
        assert app.query_one("#save").disabled is False

        app.query_one("#edit-lives").value = "5"
        app.query_one("#edit-win-score").value = "120"
        app.query_one("#edit-enemy-speed").value = "2"
        app.action_save()
        assert app.project.gameplay.lives == 5
        assert app.project.gameplay.win_score == 120
        assert next(entity for entity in app.project.entities if entity.role == "enemy").speed == 2

        app.action_generate()
        await pilot.pause()
        assert (tmp_path / "pilot-game" / "build" / "main.c").is_file()


def test_render_map_draws_terrain_spawns_and_cursor():
    project = create_default_project("Map", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    level = project.levels[0]
    player = next(
        spawn for spawn in level.spawns
        if next(e for e in project.entities if e.id == spawn.entity).role == "player"
    )

    drawn = render_map(project, 0, (0, 0))
    lines = drawn.splitlines()

    assert len(lines) == level.height
    assert lines[0].startswith("[reverse]▓[/reverse]")
    plain = [line.replace("[reverse]", "").replace("[/reverse]", "") for line in lines]
    assert all(len(line) == level.width for line in plain)
    assert plain[player.row][player.col] == "@"
    for row in range(level.height):
        for col in range(level.width):
            if (col, row) in {(s.col, s.row) for s in level.spawns}:
                continue
            expected = "▓" if level.tiles[row][col] == "#" else "·"
            assert plain[row][col] == expected, (col, row)


def test_render_map_marks_the_cursor_wherever_it_sits():
    project = create_default_project("Cursor", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)

    drawn = render_map(project, 0, (3, 2)).splitlines()

    assert drawn[2].count("[reverse]") == 1
    assert sum(line.count("[reverse]") for line in drawn) == 1
