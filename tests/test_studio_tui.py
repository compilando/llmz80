from datetime import datetime, timezone
from pathlib import Path

import pytest

from llmz80.studio import editing
from llmz80.studio.models import TargetPlatform
from llmz80.studio.planner import ProjectChange, ProjectProposal
from llmz80.studio.reference import GameReference, ReferenceSource
from llmz80.studio.samples import blank_project
from llmz80.studio.screen import Stage
from llmz80.studio.spriting import SPRITE_SIZE
from llmz80.studio.tui import (
    StudioApp,
    brief_preview,
    next_step_hint,
    pick_stage_detail,
    render_map,
    render_stage_marks,
)


@pytest.mark.asyncio
async def test_creating_a_project_fills_the_editor(tmp_path: Path):
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Pilot Game"
        app.action_create()
        await pilot.pause()

        assert (tmp_path / "pilot-game" / "game.yml").is_file()
        assert app.project is not None
        assert app.query_one("#entity-table").row_count == len(app.project.entities)
        # A freshly created default project fits its target machine, which
        # is the six-stage line's "diseño" (design) stage reading done --
        # the direct replacement for the old one-line "ready" verdict.
        assert "diseño ✓" in app.status_text


@pytest.mark.asyncio
async def test_saving_applies_every_scalar_field_at_once(tmp_path: Path):
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Pilot Game"
        app.action_create()
        await pilot.pause()

        # `rename_project` applies title, style and brief together in one
        # validated step -- the fields this screen still edits.
        app.query_one("#f-title").value = "Renamed Game"
        app.query_one("#f-style").value = "neon"
        app.query_one("#f-brief").text = "Four ghosts."
        app.action_save()
        await pilot.pause()

        assert app.project.metadata.title == "Renamed Game"
        assert app.project.presentation.style == "neon"
        assert app.project.metadata.brief == "Four ghosts."
        reopened = app.service.open_project(tmp_path / "pilot-game")
        assert reopened.metadata.title == "Renamed Game"
        assert reopened.presentation.style == "neon"
        assert reopened.metadata.brief == "Four ghosts."


@pytest.mark.asyncio
async def test_a_refused_edit_warns_instead_of_crashing(tmp_path: Path):
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Refused"
        app.action_create()
        await pilot.pause()
        before = app.project.metadata.title

        # A title beyond Metadata's max_length=32 must be refused, not stored.
        app.query_one("#f-title").value = "x" * 40
        app.action_save()
        await pilot.pause()

        assert app.project.metadata.title == before


def test_render_map_draws_terrain_spawns_and_cursor():
    project = blank_project("Map", TargetPlatform.SPECTRUM)
    screen = project.screens[0]
    entity = project.entities[0]
    actor = next(spawn for spawn in screen.spawns if spawn.entity == entity.id)

    drawn = render_map(project, 0, (0, 0))
    lines = drawn.splitlines()

    assert len(lines) == screen.height
    assert lines[0].startswith("[reverse]▓[/reverse]")
    plain = [line.replace("[reverse]", "").replace("[/reverse]", "") for line in lines]
    assert all(len(line) == screen.width for line in plain)
    # The map editor has no fixed roster of entity roles in v4 -- the glyph
    # is the first letter of the entity's own `kind`, uppercased; the blank
    # project's one entity has kind="actor".
    assert plain[actor.row][actor.col] == "A"


def test_render_map_marks_the_cursor_wherever_it_sits():
    project = blank_project("Cursor", TargetPlatform.SPECTRUM)

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
        app.query_one("#f-style").value = "neon"
        await pilot.pause()
        assert app.query_one("#f-style").value == "neon"

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


def test_next_step_hint_names_the_key_of_the_first_pending_stage():
    stages = [
        Stage("referencia", "done", "found it"),
        Stage("diseño", "done"),
        Stage("sprites", "pending"),
    ]

    hint = next_step_hint(stages)

    assert "ctrl+d" in hint
    assert "sprite" in hint


def test_next_step_hint_is_empty_once_every_stage_is_done():
    stages = [Stage("referencia", "done", "found it"), Stage("release", "done", "game.zip")]

    assert next_step_hint(stages) == ""


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
        assert app.query_one("#brief").display is False
        assert app.query_one("#panel-entities").has_class("open")

        # Pressing the same key again closes it, back to the resting screen.
        await pilot.press("e")
        await pilot.pause()

        assert app.active_panel is None
        assert app.query_one("#brief").display is True
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

        screen = app.project.screens[0]
        app.query_one("#map-grid").focus()
        await pilot.pause()
        # Walk the cursor to a floor cell with no spawn, then toggle it.
        occupied = {(s.col, s.row) for s in screen.spawns}
        col = col_row = None
        for row in range(screen.height):
            for col in range(screen.width):
                if (col, row) not in occupied and screen.tiles[row][col] != "#":
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

        assert app.project.screens[0].tiles[col_row[1]][col_row[0]] == "#"


def _resting_content_height(app: StudioApp) -> int:
    """Header + brief-box + stage-line + stage-detail + shortcuts, in rows.

    Everything the resting screen shows, excluding the docked `Footer` (which
    Textual pins to the last row regardless of how little content sits above
    it, so it says nothing about whether the resting screen itself grew).
    """
    return (
        app.query_one("Header").size.height
        + app.query_one("#brief").size.height
        + app.query_one("#stage-line").size.height
        + app.query_one("#stage-detail").size.height
        + app.query_one("#shortcuts").size.height
    )


#: header(1) + brief-box(3, with its border) + stage-line(1) + stage-detail(1)
#: + shortcuts(1) -- the mock's own seven lines, measured with
#: `run_test(size=(120, 40))` via `Widget.size.height` on each. Editing
#: (title, style, and the brief itself) moved into its own panel precisely so
#: none of it adds a row here.
RESTING_CONTENT_HEIGHT = 7


@pytest.mark.asyncio
async def test_the_resting_screen_has_a_fixed_height(tmp_path: Path):
    """The complaint this task answers: the screen used to grow with every
    field it carried. At rest -- no project, and with one loaded -- the
    header/brief/stage-line/stage-detail/shortcuts group occupies the same,
    small number of rows; only an opened panel adds height, and it replaces
    that group rather than stacking on top of it."""
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        assert _resting_content_height(app) == RESTING_CONTENT_HEIGHT

        app.query_one("#f-title").value = "Sized"
        app.action_create()
        await pilot.pause()
        assert _resting_content_height(app) == RESTING_CONTENT_HEIGHT

        app.query_one("#entity-table").focus()
        await pilot.pause()
        await pilot.press("l")
        await pilot.pause()
        assert app.query_one("#brief").display is False


@pytest.mark.asyncio
async def test_a_long_brief_does_not_make_the_resting_screen_taller(tmp_path: Path):
    """The brief box shows one truncated line, not an editor: however long
    the brief a person wrote, the box the resting screen shows it in stays
    exactly as tall."""
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Verbose"
        app.action_create()
        await pilot.pause()

        app.project.metadata.brief = "A very long brief. " * 40
        app._refresh_stage()
        await pilot.pause()

        assert _resting_content_height(app) == RESTING_CONTENT_HEIGHT
        assert app.query_one("#brief").size.height == 3


@pytest.mark.asyncio
async def test_the_stage_detail_line_names_the_key_that_advances_the_pipeline(tmp_path: Path):
    """`#stage-detail` doubles as a "what to press next" line: it names the
    key for whichever stage `screen.next_step` judges most worth doing, and
    that key changes as the project moves through the pipeline -- checked
    at two distinct points, not just the first."""
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Guided"
        app.action_create()
        await pilot.pause()

        # A brand new project: nothing has been researched yet.
        assert "ctrl+f" in app.query_one("#stage-detail").content

        fake = _FakeResearcher(title="Real Game")
        app.researcher = fake
        app.action_research()
        for _ in range(100):
            await pilot.pause()
            if "Real Game" in app.status_text:
                break

        # Researched, and diseño already reads done for a fresh default
        # project -- the existing detail (the game found) survives, and the
        # hint has moved on to the next stage, sprites.
        detail = app.query_one("#stage-detail").content
        assert "Real Game" in detail
        assert "ctrl+d" in detail


@pytest.mark.asyncio
async def test_a_fully_done_project_shows_no_dangling_hint(tmp_path: Path):
    """Once every stage is done there is nothing left to press; the detail
    line falls back to whatever `pick_stage_detail` already shows rather
    than leaving a stray separator or an instruction with nothing to name."""
    import json

    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Finished"
        app.action_create()
        await pilot.pause()

        directory = app.project_dir
        from datetime import datetime, timezone

        from llmz80.studio.reference import GameReference, ReferenceSource, save_reference

        save_reference(
            GameReference(
                identified=True,
                confidence="high",
                title="Finished Game",
                sources=[
                    ReferenceSource(
                        url="https://example.com/review",
                        title="A review",
                        retrieved_at=datetime.now(timezone.utc),
                    )
                ],
            ),
            directory,
        )
        program_dir = directory / app.project.program_dir
        program_dir.mkdir(parents=True, exist_ok=True)
        (program_dir / "main.c").write_text("int main(void) { return 0; }\n")
        build_dir = directory / "build"
        build_dir.mkdir(parents=True, exist_ok=True)
        (build_dir / "studio_quality_report.json").write_text(
            json.dumps({"gates": {"design": True}, "quality_pass": True})
        )
        releases = directory / "releases"
        releases.mkdir()
        name = f"{app.project.metadata.slug}-{app.project.target.platform.value}.zip"
        (releases / name).write_bytes(b"PK\x03\x04")
        # `blank_project`'s one entity has no sprite id yet -- give it one so
        # there is something to register an asset for, then give every such
        # id an asset, so sprites reaches "done" instead of staying pending.
        from llmz80.studio.models import AssetSpec

        app.project = app.project.model_copy(
            update={"entities": [app.project.entities[0].model_copy(update={"sprite": "actor"})]}
        )
        sprites = [
            AssetSpec(
                id=sprite_id,
                kind="sprite",
                source=f"assets/{sprite_id}.png",
                width=16,
                height=16,
                frames=1,
            )
            for sprite_id in sorted({e.sprite for e in app.project.entities})
        ]
        app.project.assets = sprites

        app._refresh_stage()
        await pilot.pause()

        detail = app.query_one("#stage-detail").content
        assert "press" not in detail
        assert detail  # not empty: the existing detail (the game found) remains
        assert not detail.endswith(" · ")
        assert not detail.startswith(" · ")


@pytest.mark.asyncio
async def test_creating_a_project_from_the_screen_applies_the_brief(tmp_path: Path):
    """The least discoverable step in the old flow -- create with ctrl+n,
    then separately open the design panel to type the brief and save -- is
    now one step: the creation panel itself has a Brief field, and creating
    applies it the same way `llmz80 project new`'s trailing BRIEF argument
    does, through `editing.rename_project`."""
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Briefed"
        app.query_one("#f-create-brief").text = "Four ghosts. A big dot makes them edible."
        app.action_create()
        await pilot.pause()

        assert "ghosts" in app.project.metadata.brief
        assert "ghosts" in app.service.open_project(tmp_path / "briefed").metadata.brief


@pytest.mark.asyncio
async def test_creating_a_project_from_the_screen_without_a_brief_still_works(tmp_path: Path):
    """The brief field is optional -- leaving it blank must not break
    creation, the same as `llmz80 project new` without a trailing BRIEF."""
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Unbriefed"
        app.action_create()
        await pilot.pause()

        assert app.project is not None
        assert app.project.metadata.brief == ""


def test_brief_preview_passes_a_short_brief_through_unchanged():
    assert brief_preview("Four ghosts chase you.") == "Four ghosts chase you."


def test_brief_preview_truncates_a_long_brief_with_an_ellipsis():
    long_brief = "x" * 500

    preview = brief_preview(long_brief, limit=78)

    assert len(preview) == 78
    assert preview.endswith("…")
    assert preview[:-1] == "x" * 77


def test_brief_preview_collapses_whitespace_so_it_stays_one_line():
    assert brief_preview("Four ghosts.\nA big dot\tmakes them edible.") == (
        "Four ghosts. A big dot makes them edible."
    )


@pytest.mark.asyncio
async def test_the_design_panel_holds_title_style_and_the_editable_brief(tmp_path: Path):
    """Title, Style and the editable Brief moved off the resting screen and
    into their own panel, opened by `g` (`diseño`) -- a key that does not
    collide with map/entities/sprites/diff/log."""
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Panelled"
        app.action_create()
        await pilot.pause()
        app.query_one("#entity-table").focus()
        await pilot.pause()

        await pilot.press("g")
        await pilot.pause()

        assert app.active_panel == "design"
        assert app.query_one("#panel-design").has_class("open")
        assert app.query_one("#brief").display is False
        # The fields themselves are unchanged -- still #f-title/#f-style/
        # #f-brief -- just relocated into the panel.
        assert app.query_one("#f-title", type(app.query_one("#f-title"))) is not None
        assert app.query_one("#f-style") is not None
        assert app.query_one("#f-brief") is not None

        await pilot.press("g")
        await pilot.pause()
        assert app.active_panel is None


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


# --- research, adapt and draw-sprites: fakes injected instead of the API ---
#
# `research_reference`, `propose_from_reference` and `draw_sprites` all take
# their researcher/designer/artist as a parameter -- exactly so a caller can
# hand them something other than the OpenAI-backed default `action_research`/
# `action_adapt`/`action_draw_sprites` build. These fakes are that something:
# no test in this section makes a network call or generates an image.


class _FakeResearcher:
    """Records how many times it was asked, and what it was asked for."""

    def __init__(self, title="Zampa Bolas", publisher="System 4", year=1988, identified=True):
        self.title, self.publisher, self.year, self.identified = title, publisher, year, identified
        self.calls = 0

    def research(self, brief, target):
        self.calls += 1
        sources = (
            [
                ReferenceSource(
                    url="https://example.com/review",
                    title="A review",
                    retrieved_at=datetime.now(timezone.utc),
                )
            ]
            if self.identified
            else []
        )
        return GameReference(
            identified=self.identified,
            confidence="high",
            title=self.title if self.identified else "",
            publisher=self.publisher,
            year=self.year,
            sources=sources,
        )


class _FakeDesigner:
    """Refuses its first proposal (a protected path), then succeeds -- so a
    test can see the repair loop's refusal reach the screen."""

    def __init__(self):
        self.calls = 0

    def propose(self, project, dossier, feedback=None):
        self.calls += 1
        if self.calls == 1:
            return ProjectProposal(
                summary="touch what is not mine to touch",
                changes=[
                    ProjectChange(
                        path="/schema_version",
                        operation="replace",
                        reason="bogus",
                        value_number=99,
                    )
                ],
            )
        return ProjectProposal(
            summary="dress it up like the real game",
            changes=[
                ProjectChange(
                    path="/presentation/style",
                    operation="replace",
                    reason="matches the dossier's visual style",
                    value_text="arcade neon",
                )
            ],
        )


class _FakeArtist:
    """Draws one flat-coloured frame per call, recording which sprite id it
    was asked for (`draw_sprites` calls once per distinct sprite id, handing
    it one representative entity that wears it -- see its docstring)."""

    def __init__(self):
        self.calls: list[str] = []

    def draw_frames(self, project, entity, dossier=None, *, on_progress=None):
        from PIL import Image

        self.calls.append(entity.sprite)
        return [Image.new("RGBA", (SPRITE_SIZE, SPRITE_SIZE), (200, 40, 40, 255))]


def _focus_away_from_text_entry(app: StudioApp) -> None:
    app.query_one("#entity-table").focus()


def _give_entity_a_sprite(app: StudioApp, sprite_id: str = "actor") -> None:
    """`blank_project`'s one entity wears no sprite id (`entity.sprite is
    None`) -- `draw_sprites` needs a valid asset identifier to draw and
    register, so tests that exercise it give the entity one first."""
    app.project = app.project.model_copy(
        update={"entities": [app.project.entities[0].model_copy(update={"sprite": sprite_id})]}
    )
    app.service.save_project(app.project, app.project_dir)


@pytest.mark.asyncio
async def test_research_reaches_the_service_and_the_stage_line_shows_it(tmp_path: Path):
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Researched"
        app.action_create()
        await pilot.pause()

        fake = _FakeResearcher(title="Zampa Bolas", publisher="System 4", year=1988)
        app.researcher = fake
        app.action_research()

        for _ in range(100):
            await pilot.pause()
            if "Zampa Bolas" in app.status_text:
                break

        assert fake.calls == 1
        assert (app.project_dir / "reference.yml").is_file()
        # No panel of its own: the result surfaces on the stage line's
        # "referencia" detail, the same place `screen.stage_line` already
        # names a dossier's title and source count for any project.
        assert "referencia ✓" in app.status_text
        assert "Zampa Bolas" in app.status_text
        assert app.active_panel != "diff" and app.active_panel != "sprites"


@pytest.mark.asyncio
async def test_research_asks_before_overwriting_an_existing_dossier(tmp_path: Path):
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Guarded"
        app.action_create()
        await pilot.pause()

        first = _FakeResearcher(title="First Game")
        app.researcher = first
        app.action_research()
        for _ in range(100):
            await pilot.pause()
            if "First Game" in app.status_text:
                break
        assert first.calls == 1
        archived = (app.project_dir / "reference.yml").read_text()

        # Declining (only pressing once) changes nothing on disk.
        second = _FakeResearcher(title="Second Game")
        app.researcher = second
        app.action_research()
        await pilot.pause()

        assert second.calls == 0
        assert (app.project_dir / "reference.yml").read_text() == archived

        # Confirming (the same action again) replaces it.
        app.action_research()
        for _ in range(100):
            await pilot.pause()
            if "Second Game" in app.status_text:
                break

        assert second.calls == 1
        assert (app.project_dir / "reference.yml").read_text() != archived


@pytest.mark.asyncio
async def test_a_malformed_dossier_is_reported_not_crashed_on(tmp_path: Path):
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Broken"
        app.action_create()
        await pilot.pause()

        (app.project_dir / "reference.yml").write_text("not: [valid", encoding="utf-8")

        fake = _FakeResearcher()
        app.researcher = fake
        app.action_research()
        await pilot.pause()

        # Reported, not crashed: no API call was ever made, and a warning
        # reached the user instead of an unhandled exception.
        assert fake.calls == 0
        assert any(n.severity == "error" for n in app._notifications)


@pytest.mark.asyncio
async def test_adapt_shows_the_diff_and_its_refusals_before_applying_anything(tmp_path: Path):
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Adaptable"
        app.action_create()
        await pilot.pause()
        _focus_away_from_text_entry(app)
        await pilot.pause()

        app.researcher = _FakeResearcher(title="Real Game")
        app.action_research()
        for _ in range(100):
            await pilot.pause()
            if "Real Game" in app.status_text:
                break

        designer = _FakeDesigner()
        app.designer = designer
        original_style = app.project.presentation.style
        app.action_adapt()
        for _ in range(100):
            await pilot.pause()
            if app.active_panel == "diff":
                break

        # The repair loop's first attempt touched a protected path and was
        # refused; its second succeeded. Both calls happened...
        assert designer.calls == 2
        # ...and the refusal is visible, not just repaired silently.
        diff_text = app.query_one("#diff-view").content
        assert "Attempt 1 was refused, repairing:" in diff_text
        assert "protected path" in diff_text
        assert "arcade neon" in diff_text
        # Nothing is applied yet -- the diff is shown, not acted on.
        assert app.service.open_project(app.project_dir).presentation.style == original_style

        await pilot.press("y")
        await pilot.pause()

        assert app.project.presentation.style == "arcade neon"
        assert app.service.open_project(app.project_dir).presentation.style == "arcade neon"


@pytest.mark.asyncio
async def test_declining_the_proposal_leaves_the_project_unchanged(tmp_path: Path):
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Declinable"
        app.action_create()
        await pilot.pause()
        _focus_away_from_text_entry(app)
        await pilot.pause()

        app.researcher = _FakeResearcher(title="Real Game")
        app.action_research()
        for _ in range(100):
            await pilot.pause()
            if "Real Game" in app.status_text:
                break

        app.designer = _FakeDesigner()
        original_style = app.project.presentation.style
        app.action_adapt()
        for _ in range(100):
            await pilot.pause()
            if app.active_panel == "diff":
                break

        await pilot.press("n")
        await pilot.pause()

        assert app.project.presentation.style == original_style
        assert app.service.open_project(app.project_dir).presentation.style == original_style


@pytest.mark.asyncio
async def test_a_failing_adapt_notifies_instead_of_crashing(tmp_path: Path):
    """No dossier exists yet, so `propose_from_reference` raises. That
    surfaces through the same `_run`/`_background` machinery every slow
    operation uses -- a notification, not a crash, and the diff panel never
    opens over a proposal that does not exist."""
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "NoDossier"
        app.action_create()
        await pilot.pause()

        app.designer = _FakeDesigner()
        app.action_adapt()

        for _ in range(100):
            await pilot.pause()
            if any(n.severity == "error" for n in app._notifications):
                break

        assert any(n.severity == "error" for n in app._notifications)
        assert app.active_panel != "diff"
        assert app.project is not None  # the app is still usable

        # Still responsive: an ordinary field edit still works.
        app.query_one("#f-style").value = "neon"
        await pilot.pause()
        assert app.query_one("#f-style").value == "neon"


@pytest.mark.asyncio
async def test_draw_sprites_reaches_the_service_and_registers_assets(tmp_path: Path):
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Sprited"
        app.action_create()
        await pilot.pause()
        _give_entity_a_sprite(app)
        needed = sorted({entity.sprite for entity in app.project.entities})

        artist = _FakeArtist()
        app.artist = artist
        app.action_draw_sprites()

        for _ in range(100):
            await pilot.pause()
            if app.active_panel == "sprites":
                break

        assert app.active_panel == "sprites"
        assert sorted(artist.calls) == needed
        registered = {a.id for a in app.project.assets if a.kind == "sprite"}
        assert registered == set(needed)
        reopened = app.service.open_project(app.project_dir)
        on_disk = {a.id for a in reopened.assets if a.kind == "sprite"}
        assert on_disk == set(needed)


@pytest.mark.asyncio
async def test_draw_sprites_asks_before_overwriting_existing_art(tmp_path: Path):
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Redraw"
        app.action_create()
        await pilot.pause()
        _give_entity_a_sprite(app)

        first_artist = _FakeArtist()
        app.artist = first_artist
        app.action_draw_sprites()
        for _ in range(100):
            await pilot.pause()
            if app.active_panel == "sprites":
                break
        before = {
            a.id: (app.project_dir / a.source).read_bytes()
            for a in app.project.assets
            if a.kind == "sprite"
        }
        assert before

        # Declining (only pressing once) changes nothing on disk.
        second_artist = _FakeArtist()
        app.artist = second_artist
        app.action_draw_sprites()
        await pilot.pause()

        assert second_artist.calls == []
        for asset_id, data in before.items():
            asset = next(a for a in app.project.assets if a.id == asset_id)
            assert (app.project_dir / asset.source).read_bytes() == data

        # Confirming (the same action again) redraws it.
        app.action_draw_sprites()
        for _ in range(100):
            await pilot.pause()
            if second_artist.calls:
                break

        assert sorted(second_artist.calls) == sorted(before.keys())
