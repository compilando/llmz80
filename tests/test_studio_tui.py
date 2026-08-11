from pathlib import Path

import pytest

from llmz80.studio import editing
from llmz80.studio.models import GenreId, TargetPlatform
from llmz80.studio.packs import BUILTIN_PACKS, create_default_project
from llmz80.studio.tui import StudioApp, render_map


@pytest.mark.asyncio
async def test_creating_a_project_fills_the_editor(tmp_path: Path):
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Pilot Game"
        app.action_create()
        await pilot.pause()

        assert (tmp_path / "pilot-game" / "game.yml").is_file()
        assert app.project is not None
        assert app.query_one("#f-lives").value == str(app.project.gameplay.lives)
        assert app.query_one("#entity-table").row_count == len(app.project.entities)
        assert "ready" in app.status_text


@pytest.mark.asyncio
async def test_saving_applies_every_scalar_field_at_once(tmp_path: Path):
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Pilot Game"
        app.action_create()
        await pilot.pause()

        app.query_one("#f-lives").value = "5"
        app.query_one("#f-score").value = "120"
        app.query_one("#f-style").value = "neon"
        app.action_save()
        await pilot.pause()

        assert app.project.gameplay.lives == 5
        assert app.project.gameplay.win_score == 120
        assert app.project.presentation.style == "neon"
        assert app.service.open_project(tmp_path / "pilot-game").gameplay.lives == 5


@pytest.mark.asyncio
async def test_a_refused_edit_warns_instead_of_crashing(tmp_path: Path):
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Refused"
        app.action_create()
        await pilot.pause()
        before = app.project.gameplay.lives

        # Lives outside the model's range must be refused, not stored.
        app.query_one("#f-lives").value = "99"
        app.action_save()
        await pilot.pause()

        assert app.project.gameplay.lives == before


@pytest.mark.asyncio
async def test_the_status_line_reports_an_unsolvable_design(tmp_path: Path):
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Sealed"
        app.action_create()
        await pilot.pause()

        target = next(
            (s.col, s.row) for s in app.project.levels[0].spawns if s.entity == "collectible"
        )
        sealed = app.project
        for col, row in (
            (target[0] + 1, target[1]),
            (target[0] - 1, target[1]),
            (target[0], target[1] + 1),
            (target[0], target[1] - 1),
        ):
            sealed = editing.set_tile(sealed, 0, col, row, "#")
        app.project = sealed
        app._status()
        await pilot.pause()

        status = app.status_text
        assert "not releasable" in status
        assert "seal off" in status


@pytest.mark.asyncio
async def test_every_typology_can_be_chosen(tmp_path: Path):
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()

        offered = {str(value) for _label, value in app.query_one("#f-genre")._options}

        assert offered == {pack.id for pack in BUILTIN_PACKS}


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


def test_render_map_marks_the_cursor_wherever_it_sits():
    project = create_default_project("Cursor", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)

    drawn = render_map(project, 0, (3, 2)).splitlines()

    assert drawn[2].count("[reverse]") == 1
    assert sum(line.count("[reverse]") for line in drawn) == 1
