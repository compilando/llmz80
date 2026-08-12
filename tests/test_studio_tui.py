from pathlib import Path

import pytest

from llmz80.studio import editing
from llmz80.studio.models import GenreId, TargetPlatform
from llmz80.studio.packs import BUILTIN_PACKS, create_default_project
from llmz80.studio.screen import Stage
from llmz80.studio.tui import (
    StudioApp,
    pick_stage_detail,
    render_map,
    render_stage_marks,
)


def _neighbours(cell):
    col, row = cell
    return [(col + 1, row), (col - 1, row), (col, row + 1), (col, row - 1)]


def _isolated_collectible(project):
    """A collectible whose neighbours hold no other spawn.

    Walling a cell that holds a spawn is refused by the model, so a test that
    seals a collectible in has to pick one with room around it.
    """
    occupied = {(s.col, s.row) for s in project.levels[0].spawns}
    roles = {e.id: e.role for e in project.entities}
    for spawn in project.levels[0].spawns:
        if roles.get(spawn.entity) != "collectible":
            continue
        cell = (spawn.col, spawn.row)
        if not any(n in occupied for n in _neighbours(cell)):
            return cell
    raise AssertionError("every collectible has a neighbour that is occupied")


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
        # A freshly created default project is a solvable, structured design,
        # which is the six-stage line's "diseño" (design) stage reading done
        # -- the direct replacement for the old one-line "ready" verdict.
        assert "diseño ✓" in app.status_text


@pytest.mark.asyncio
async def test_saving_applies_every_scalar_field_at_once(tmp_path: Path):
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Pilot Game"
        app.action_create()
        await pilot.pause()

        # `win_score` is no longer a field this screen edits at all -- it is
        # derived, per `quality.py`, and no widget offers it any more -- so
        # this test now only covers the fields that remain: lives and style.
        app.query_one("#f-lives").value = "5"
        app.query_one("#f-style").value = "neon"
        app.action_save()
        await pilot.pause()

        assert app.project.gameplay.lives == 5
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
async def test_the_stage_line_reports_an_unsolvable_design(tmp_path: Path):
    """Formerly `test_the_status_line_reports_an_unsolvable_design`: the
    one-line "ready"/"not releasable" verdict this asserted on is gone, but
    the underlying fact -- an unsolvable design is refused, and says why --
    still holds, now carried by the "diseño" stage of the new stage line
    (`screen._design_stage` folds the same solvability failures in)."""
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Sealed"
        app.action_create()
        await pilot.pause()

        target = _isolated_collectible(app.project)
        sealed = app.project
        for col, row in _neighbours(target):
            sealed = editing.set_tile(sealed, 0, col, row, "#")
        app.project = sealed
        app._refresh_stage()
        await pilot.pause()

        status = app.status_text
        assert "diseño ✗" in status
        assert "seal off" in status


@pytest.mark.asyncio
async def test_every_typology_can_be_chosen(tmp_path: Path):
    """The genre `Select` now lives inside the creation panel rather than a
    "Project" tab -- opened by ctrl+n -- but it is still queryable whether or
    not the panel is open (hidden widgets stay in the tree), and it still
    has to offer every built-in typology."""
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.action_new_dialog()
        await pilot.pause()
        assert app.active_panel == "create"

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


@pytest.mark.asyncio
async def test_a_slow_operation_leaves_the_interface_usable(tmp_path: Path):
    """The whole point of the worker: the app answers while work is running."""
    import threading

    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Slow"
        app.action_create()
        await pilot.pause()

        started, release = threading.Event(), threading.Event()

        def slow() -> str:
            started.set()
            release.wait(5)
            return "done"

        app._run("Working", slow)
        # Wait by yielding to the loop: blocking here would stop the very
        # event loop the worker needs in order to start.
        for _ in range(100):
            await pilot.pause()
            if started.is_set():
                break
        assert started.is_set(), "the job never started"

        # While it runs the app still redraws and accepts input.
        await pilot.pause()
        assert "Working" in app.status_text
        app.query_one("#f-lives").value = "7"
        await pilot.pause()
        assert app.query_one("#f-lives").value == "7"

        release.set()
        for _ in range(50):
            await pilot.pause()
            if "Working" not in app.status_text:
                break
        assert "Working" not in app.status_text


@pytest.mark.asyncio
async def test_the_brief_is_saved_and_reaches_the_prompt(tmp_path: Path):
    from llmz80.studio.acceptance import design_prompt

    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Zampabolas"
        app.action_create()
        await pilot.pause()

        app.query_one("#f-brief").text = "Four ghosts. A big dot makes them edible."
        app.action_save()
        await pilot.pause()

        assert "ghosts" in app.project.metadata.brief
        assert "ghosts" in design_prompt(app.project)
        assert "ghosts" in app.service.open_project(tmp_path / "zampabolas").metadata.brief


# --- new behaviour: the panelled screen this task builds -------------------


def test_render_stage_marks_shows_one_icon_per_stage():
    stages = [
        Stage("referencia", "done", "Zampa Bolas (System 4, 1990) · 8 fuentes"),
        Stage("diseño", "done"),
        Stage("sprites", "failed", "0/2 accepted by the blitter"),
        Stage("programa", "pending"),
    ]

    plain = render_stage_marks(stages, colour=False)

    assert plain == "referencia ✓  diseño ✓  sprites ✗  programa —"
    assert "[red]" not in plain


def test_render_stage_marks_colours_each_state():
    stages = [Stage("gates", "done"), Stage("release", "pending")]

    coloured = render_stage_marks(stages, colour=True)

    assert "[green]✓[/green]" in coloured
    assert "[dim]—[/dim]" in coloured


def test_pick_stage_detail_prefers_the_first_failure():
    stages = [
        Stage("referencia", "done", "found it"),
        Stage("diseño", "failed", "walls seal off 1 collectible"),
        Stage("sprites", "failed", "0/2 accepted"),
    ]

    assert pick_stage_detail(stages) == "walls seal off 1 collectible"


def test_pick_stage_detail_falls_back_to_a_done_stage_with_no_failure():
    stages = [Stage("referencia", "done", "found it"), Stage("diseño", "done")]

    assert pick_stage_detail(stages) == "found it"


def test_pick_stage_detail_is_empty_with_nothing_to_report():
    assert pick_stage_detail([Stage("referencia", "pending")]) == ""


@pytest.mark.asyncio
async def test_a_panel_key_opens_its_panel_and_hides_the_resting_screen(tmp_path: Path):
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Panels"
        app.action_create()
        await pilot.pause()
        # Focus somewhere that does not own letter keys, the way a person
        # would after tabbing off the title field.
        app.query_one("#entity-table").focus()
        await pilot.pause()

        await pilot.press("e")
        await pilot.pause()

        assert app.active_panel == "entities"
        assert app.query_one("#design").display is False
        assert app.query_one("#panel-entities").has_class("open")

        # Pressing the same key again closes it, back to the resting screen.
        await pilot.press("e")
        await pilot.pause()

        assert app.active_panel is None
        assert app.query_one("#design").display is True
        assert not app.query_one("#panel-entities").has_class("open")


@pytest.mark.asyncio
async def test_typing_in_the_title_field_never_opens_a_panel(tmp_path: Path):
    """Panel-toggle keys share letters with ordinary text (m, e, s, d, l);
    while a text field owns focus, Textual's own `Input` consumes those
    keystrokes as characters before `on_key` ever sees them, so typing a
    project title can never be mistaken for "open the map/entities/sprites/
    diff/log panel". This is the property that made this task's map-editing
    keys (wasd, space, +/-) safe in the original screen too."""
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        title = app.query_one("#f-title")
        title.value = ""
        title.focus()
        await pilot.pause()

        await pilot.press("m", "e", "l", "d", "s")
        await pilot.pause()

        assert title.value == "melds"
        assert app.active_panel is None


@pytest.mark.asyncio
async def test_map_editing_keys_still_toggle_a_wall(tmp_path: Path):
    """The map editor is carried into its own panel rather than rewritten:
    `render_map` is unchanged, and wasd/space/m/+/- still drive `editing`
    exactly as before -- only reachable through the map panel now."""
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Editable"
        app.action_create()
        await pilot.pause()
        app.query_one("#entity-table").focus()
        await pilot.pause()
        await pilot.press("m")
        await pilot.pause()
        assert app.active_panel == "map"

        level = app.project.levels[0]
        app.query_one("#map-grid").focus()
        await pilot.pause()
        # Walk the cursor to a floor cell with no spawn, then toggle it.
        occupied = {(s.col, s.row) for s in level.spawns}
        col = col_row = None
        for row in range(level.height):
            for col in range(level.width):
                if (col, row) not in occupied and level.tiles[row][col] != "#":
                    col_row = (col, row)
                    break
            if col_row:
                break
        assert col_row is not None
        while app.cursor[0] != col_row[0]:
            await pilot.press("d" if app.cursor[0] < col_row[0] else "a")
            await pilot.pause()
        while app.cursor[1] != col_row[1]:
            await pilot.press("s" if app.cursor[1] < col_row[1] else "w")
            await pilot.pause()

        await pilot.press("space")
        await pilot.pause()

        assert app.project.levels[0].tiles[col_row[1]][col_row[0]] == "#"


@pytest.mark.asyncio
async def test_the_resting_screen_has_a_fixed_height(tmp_path: Path):
    """The complaint this task answers: the screen used to grow with every
    field it carried. At rest -- no project, and with one loaded -- the
    header/brief/stage-line/shortcuts group occupies the same number of
    rows; only an opened panel adds height, and it replaces that group
    rather than stacking on top of it."""
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        empty_height = app.query_one("#design").size.height

        app.query_one("#f-title").value = "Sized"
        app.action_create()
        await pilot.pause()
        loaded_height = app.query_one("#design").size.height

        assert empty_height == loaded_height

        app.query_one("#entity-table").focus()
        await pilot.pause()
        await pilot.press("l")
        await pilot.pause()
        assert app.query_one("#design").display is False


@pytest.mark.asyncio
async def test_the_workspace_picker_lists_and_opens_a_project(tmp_path: Path):
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Findable"
        app.action_create()
        await pilot.pause()
        created_dir = app.project_dir
        app.project = None
        app.project_dir = None
        app._refresh_stage()

        app.action_open_dialog()
        await pilot.pause()

        assert app.active_panel == "open"
        listing = app.query_one("#workspace-list")
        assert listing.option_count == 1

        listing.focus()
        listing.highlighted = 0
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        assert app.project is not None
        assert app.project_dir == created_dir
        assert app.active_panel is None
