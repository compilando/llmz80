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
    pick_stage_detail,
    render_map,
    render_stage_marks,
    render_step_head,
    render_step_summary,
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

        def slow() -> tuple[bool, str]:
            started.set()
            release.wait(5)
            return True, "done"

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


def test_render_step_head_says_where_in_the_pipeline_you_are():
    from llmz80.studio.wizard import current

    project = blank_project("Placed", TargetPlatform.SPECTRUM)
    step = current(project, None, passed={"proyecto"})

    assert render_step_head(step) == "Paso 1 de 6: referencia"


def test_render_step_summary_names_the_key_and_warns_about_the_bill():
    from llmz80.studio.wizard import current

    project = blank_project("Costly", TargetPlatform.SPECTRUM)
    summary = render_step_summary(current(project, None, passed={"proyecto"}))

    assert "[Enter] investigar" in summary
    assert "gasta dinero" in summary
    # Research is optional to the pipeline, so the key that walks past it is
    # offered too -- and only where it would actually be allowed.
    assert "[→] omitir" in summary


def test_render_step_summary_never_offers_to_skip_what_cannot_be_skipped():
    from llmz80.studio.wizard import current

    project = blank_project("Needed", TargetPlatform.SPECTRUM)
    step = current(project, None, passed={"proyecto", "referencia", "diseño", "sprites"})

    assert step.name == "programa"
    assert "[→] omitir" not in render_step_summary(step)


def test_render_step_summary_of_a_finished_step_offers_to_repeat_it():
    from llmz80.studio.wizard import current

    project = blank_project("Done", TargetPlatform.SPECTRUM)
    step = current(project, None, passed={"proyecto", "referencia"})

    assert step.name == "diseño" and step.state == "done"
    summary = render_step_summary(step)
    assert "[R] repetir" in summary
    assert "[Enter]" not in summary


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
    """Panel-toggle keys share letters with ordinary text (g, m, e, s, d), and
    so do the wizard's own `r` and `q`; while a text field owns focus,
    Textual's own `Input` consumes those keystrokes as characters before
    `on_key` or any binding ever sees them, so typing a project title can
    never be mistaken for "open the map/entities/sprites/diff panel" -- or for
    quitting. This is the property that makes the map-editing keys (wasd,
    space, +/-) safe on this screen too."""
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        title = app.query_one("#f-title")
        title.value = ""
        title.focus()
        await pilot.pause()

        await pilot.press("g", "m", "e", "d", "s", "r", "q")
        await pilot.pause()

        assert title.value == "gmedsrq"
        assert app.active_panel is None
        assert app.is_running


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
    """Header + brief-box + the wizard's three lines + detail + shortcuts.

    Everything the resting screen shows above the diary, excluding the docked
    `Footer` (which Textual pins to the last row regardless of how little
    content sits above it, so it says nothing about whether the resting
    screen itself grew) and the diary itself, which fills whatever is left.
    """
    return (
        app.query_one("Header").size.height
        + app.query_one("#brief").size.height
        + app.query_one("#wizard-head").size.height
        + app.query_one("#stage-line").size.height
        + app.query_one("#wizard-summary").size.height
        + app.query_one("#stage-detail").size.height
        + app.query_one("#shortcuts").size.height
    )


#: header(1) + brief-box(3, with its border) + wizard-head(1) + stage-line(1)
#: + wizard-summary(1) + stage-detail(1) + shortcuts(1) -- nine lines,
#: measured with `run_test(size=(120, 40))` via `Widget.size.height` on each.
#: Two more than before this screen became a wizard, and both of them are the
#: guidance that replaced ten shortcuts nobody could remember; everything
#: else (title, style, the brief itself) still lives in a panel precisely so
#: it adds no row here.
RESTING_CONTENT_HEIGHT = 9


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

        # A panel opens over the resting screen -- and the diary stays
        # visible underneath it, since it is no longer a panel of its own.
        app.query_one("#entity-table").focus()
        await pilot.pause()
        await pilot.press("e")
        await pilot.pause()
        assert app.query_one("#brief").display is False
        assert app.query_one("#log-view").display is True


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
        app._refresh_wizard()
        await pilot.pause()

        assert _resting_content_height(app) == RESTING_CONTENT_HEIGHT
        assert app.query_one("#brief").size.height == 3


@pytest.mark.asyncio
async def test_the_wizard_names_the_step_and_moves_on_once_it_is_done(tmp_path: Path):
    """What replaced "press ctrl+f": the screen says which step it is standing
    on and what Enter would do there, and moves on to the next one by itself
    once the step succeeds -- checked at two distinct points, not just the
    first."""
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Guided"
        app.action_create()
        await pilot.pause()

        # A brand new project: research is where the wizard stands, and the
        # screen says so in words rather than naming a key to memorise.
        assert "Paso 1 de 6: referencia" in app.query_one("#wizard-head").content
        summary = app.query_one("#wizard-summary").content
        assert "[Enter] investigar" in summary
        assert "gasta dinero" in summary

        fake = _FakeResearcher(title="Real Game")
        app.researcher = fake
        app.action_do()
        for _ in range(100):
            await pilot.pause()
            if "Real Game" in app.status_text:
                break

        # Researched: the step it just did is behind it, and the wizard has
        # moved on to the next one on its own.
        assert "referencia" in app.passed
        assert "Paso 2 de 6: diseño" in app.query_one("#wizard-head").content
        # The dossier it found still names itself on the detail line.
        assert "Real Game" in app.query_one("#stage-detail").content


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

        app._refresh_wizard()
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

        # Closing it saves what was typed: `ctrl+s` is gone, and an edit that
        # vanished when the panel closed would be worse than no key at all.
        app.query_one("#f-brief").text = "Four ghosts. A big dot makes them edible."
        await pilot.press("g")
        await pilot.pause()
        assert app.active_panel is None
        assert "ghosts" in app.project.metadata.brief
        assert "ghosts" in app.service.open_project(app.project_dir).metadata.brief


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
        app.passed = set()
        app._refresh_wizard()

        # No project open, so the wizard stands on step 0, and doing it is
        # what opens the picker -- there is no ctrl+o any more.
        assert "Paso 0 de 6: proyecto" in app.status_text
        app.action_do()
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
# hand them something other than the OpenAI-backed default `_research`/
# `_adapt`/`_draw_sprites` build. These fakes are that something: no test in
# this section makes a network call or generates an image.


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
        # A freshly created project stands on step 1; Enter does it.
        app.action_do()

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
        app.action_do()
        for _ in range(100):
            await pilot.pause()
            if "First Game" in app.status_text:
                break
        assert first.calls == 1
        archived = (app.project_dir / "reference.yml").read_text()

        # The wizard moved on once it succeeded; Esc steps back onto the
        # step that already has a dossier.
        app.action_back()
        await pilot.pause()
        assert "referencia" not in app.passed

        # Declining (only pressing once) changes nothing on disk.
        second = _FakeResearcher(title="Second Game")
        app.researcher = second
        app.action_do()
        await pilot.pause()

        assert second.calls == 0
        assert (app.project_dir / "reference.yml").read_text() == archived

        # Confirming (the same step again) replaces it.
        app.action_do()
        for _ in range(100):
            await pilot.pause()
            if "Second Game" in app.status_text:
                break

        assert second.calls == 1
        assert (app.project_dir / "reference.yml").read_text() != archived


@pytest.mark.asyncio
async def test_a_finished_step_is_redone_only_after_asking(tmp_path: Path):
    """`R` on a step that is already done: once to ask, once to mean it. The
    second press is also the answer to the step's own "this would overwrite
    the archived dossier" question -- one decision, one confirmation, not
    two."""
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Redone"
        app.action_create()
        await pilot.pause()

        first = _FakeResearcher(title="First Game")
        app.researcher = first
        app.action_do()
        for _ in range(100):
            await pilot.pause()
            if "First Game" in app.status_text:
                break
        assert first.calls == 1

        # Step back onto it: done, and standing on it again.
        app.action_back()
        await pilot.pause()
        second = _FakeResearcher(title="Second Game")
        app.researcher = second

        # Asking once only warns.
        app.action_repeat()
        await pilot.pause()
        assert second.calls == 0

        # Meaning it does the step over, without a third press.
        app.action_repeat()
        for _ in range(100):
            await pilot.pause()
            if "Second Game" in app.status_text:
                break
        assert second.calls == 1


@pytest.mark.asyncio
async def test_a_step_that_is_not_done_cannot_be_repeated(tmp_path: Path):
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Unfinished"
        app.action_create()
        await pilot.pause()

        app.researcher = _FakeResearcher()
        app.action_repeat()
        await pilot.pause()

        assert app.researcher.calls == 0
        assert any(n.severity == "warning" for n in app._notifications)


@pytest.mark.asyncio
async def test_a_step_that_failed_leaves_the_wizard_standing_on_it(tmp_path: Path):
    """The difference between stopping where the problem is and walking past
    it: a job that raised does not put its step behind you."""
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Stuck"
        app.action_create()
        await pilot.pause()

        # `propose_from_reference` raises with no dossier archived, which is
        # the same failure path every step's job shares.
        app.designer = _FakeDesigner()
        app._adapt()
        for _ in range(100):
            await pilot.pause()
            if any(n.severity == "error" for n in app._notifications):
                break

        assert "referencia" not in app.passed
        diary = (app.project_dir / "studio.log").read_text(encoding="utf-8")
        assert "FALLÓ" in diary
        assert "ERROR" in diary


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
        app.action_do()
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
        app.action_do()
        for _ in range(100):
            await pilot.pause()
            if "Real Game" in app.status_text:
                break

        designer = _FakeDesigner()
        app.designer = designer
        original_style = app.project.presentation.style
        app._adapt()
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
        app.action_do()
        for _ in range(100):
            await pilot.pause()
            if "Real Game" in app.status_text:
                break

        app.designer = _FakeDesigner()
        original_style = app.project.presentation.style
        app._adapt()
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
        app._adapt()

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
        # Research and the design review are behind this project; the wizard
        # is standing on sprites, and Enter draws them.
        app.passed = {"proyecto", "referencia", "diseño"}
        app._refresh_wizard()
        app.action_do()

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
        app.passed = {"proyecto", "referencia", "diseño"}
        app._refresh_wizard()
        app.action_do()
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

        # Drawing succeeded, so the wizard moved on. Esc closes the panel
        # showing what was drawn; Esc again steps back onto the sprites step,
        # which now has art a redraw would overwrite.
        app.action_back()
        app.action_back()
        await pilot.pause()
        assert "sprites" not in app.passed

        # Declining (only pressing once) changes nothing on disk.
        second_artist = _FakeArtist()
        app.artist = second_artist
        app.action_do()
        await pilot.pause()

        assert second_artist.calls == []
        for asset_id, data in before.items():
            asset = next(a for a in app.project.assets if a.id == asset_id)
            assert (app.project_dir / asset.source).read_bytes() == data

        # Confirming (the same step again) redraws it.
        app.action_do()
        for _ in range(100):
            await pilot.pause()
            if second_artist.calls:
                break

        assert sorted(second_artist.calls) == sorted(before.keys())


# --- the wizard replaces the ten shortcuts ---------------------------------


def test_none_of_the_ten_shortcuts_survive():
    """The decision this whole change exists to make, written as a test."""
    from llmz80.studio.tui import StudioApp

    bound = {binding[0] for binding in StudioApp.BINDINGS}
    for gone in (
        "ctrl+n",
        "ctrl+o",
        "ctrl+s",
        "ctrl+f",
        "ctrl+a",
        "ctrl+d",
        "ctrl+w",
        "ctrl+b",
        "ctrl+t",
        "ctrl+r",
    ):
        assert gone not in bound, f"{gone} survives"


@pytest.mark.asyncio
async def test_enter_does_the_current_step(tmp_path):
    from llmz80.studio.tui import StudioApp

    app = StudioApp(tmp_path)
    async with app.run_test() as pilot:
        app.project, app.project_dir = app.service.create_project("Wizard", TargetPlatform.SPECTRUM)
        app.passed = {"proyecto", "referencia"}
        app._refresh_wizard()
        await pilot.press("enter")
        await pilot.pause()
        assert app.active_panel == "map"  # el paso 2 abre el editor


@pytest.mark.asyncio
async def test_the_right_arrow_leaves_a_step_behind(tmp_path):
    from llmz80.studio.tui import StudioApp

    app = StudioApp(tmp_path)
    async with app.run_test() as pilot:
        app.project, app.project_dir = app.service.create_project("Onward", TargetPlatform.SPECTRUM)
        app.passed = {"proyecto"}
        app._refresh_wizard()
        await pilot.press("right")
        await pilot.pause()
        assert "referencia" in app.passed
        diary = (app.project_dir / "studio.log").read_text(encoding="utf-8")
        assert "OMITIR" in diary


@pytest.mark.asyncio
async def test_a_step_the_pipeline_needs_cannot_be_left_behind(tmp_path):
    """Skipping research is fine -- a game need not be based on a real one.
    Skipping the program is not: there would be nothing to release."""
    from llmz80.studio.tui import StudioApp

    app = StudioApp(tmp_path)
    async with app.run_test() as pilot:
        app.project, app.project_dir = app.service.create_project(
            "Required", TargetPlatform.SPECTRUM
        )
        app.passed = {"proyecto", "referencia", "diseño", "sprites"}
        app._refresh_wizard()
        await pilot.press("right")
        await pilot.pause()
        assert "programa" not in app.passed


@pytest.mark.asyncio
async def test_without_a_project_the_wizard_offers_the_chooser(tmp_path):
    from llmz80.studio.tui import StudioApp

    app = StudioApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.press("enter")
        await pilot.pause()
        assert app.active_panel in {"open", "create"}


@pytest.mark.asyncio
async def test_an_empty_workspace_opens_the_creation_panel_directly(tmp_path):
    """There is nothing to choose from in an empty workspace, and making a
    person press one more key to be told so wastes the time of exactly the
    person who has least idea what to press."""
    from llmz80.studio.tui import StudioApp

    app = StudioApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.press("enter")
        await pilot.pause()
        assert app.active_panel == "create"


@pytest.mark.asyncio
async def test_a_populated_workspace_offers_the_picker(tmp_path):
    from llmz80.studio.tui import StudioApp

    app = StudioApp(tmp_path)
    async with app.run_test() as pilot:
        app.service.create_project("Already There", TargetPlatform.SPECTRUM)
        await pilot.press("enter")
        await pilot.pause()
        assert app.active_panel == "open"


@pytest.mark.asyncio
async def test_opening_a_project_leaves_step_zero_behind(tmp_path):
    """`current` is the first step not left behind, so step 0 must be marked
    as soon as there is a project -- otherwise the wizard never moves off it."""
    from llmz80.studio.tui import StudioApp

    app = StudioApp(tmp_path)
    async with app.run_test() as pilot:
        project, directory = app.service.create_project("Opened", TargetPlatform.SPECTRUM)
        app.action_open(str(directory))
        await pilot.pause()
        assert "proyecto" in app.passed


@pytest.mark.asyncio
async def test_opening_a_project_points_the_diary_at_it(tmp_path):
    from llmz80.studio.tui import StudioApp

    app = StudioApp(tmp_path)
    async with app.run_test() as pilot:
        _project, directory = app.service.create_project("Diaried", TargetPlatform.SPECTRUM)
        app.action_open(str(directory))
        await pilot.pause()
        assert app.journal is not None and app.journal.path.parent == directory
        assert "ABRIR" in (directory / "studio.log").read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_leaving_the_editor_saves_and_says_so(tmp_path):
    from llmz80.studio.tui import StudioApp

    app = StudioApp(tmp_path)
    async with app.run_test() as pilot:
        app.project, app.project_dir = app.service.create_project("Saved", TargetPlatform.SPECTRUM)
        app.passed = {"proyecto", "referencia"}
        app._refresh_wizard()
        await pilot.press("enter")  # entra al editor
        await pilot.press("space")  # pinta una celda
        await pilot.press("escape")  # sale, y al salir guarda
        await pilot.pause()
        assert app.active_panel is None
        diary = (app.project_dir / "studio.log").read_text(encoding="utf-8")
        assert "GUARDAR" in diary


@pytest.mark.asyncio
async def test_leaving_the_editor_untouched_writes_no_save_down(tmp_path):
    """`store.save` archives the previous revision only where the text
    changed; the diary follows the same rule rather than filling up with
    saves that saved nothing."""
    from llmz80.studio.tui import StudioApp

    app = StudioApp(tmp_path)
    async with app.run_test() as pilot:
        app.project, app.project_dir = app.service.create_project(
            "Untouched", TargetPlatform.SPECTRUM
        )
        app.passed = {"proyecto", "referencia"}
        app._refresh_wizard()
        await pilot.press("enter")
        await pilot.press("escape")
        await pilot.pause()
        assert app.active_panel is None
        log = app.project_dir / "studio.log"
        diary = log.read_text(encoding="utf-8") if log.is_file() else ""
        assert "GUARDAR" not in diary


@pytest.mark.asyncio
async def test_leaving_a_step_behind_saves_what_was_edited(tmp_path):
    """The other half of "there is no unsaved state to lose": walking on
    with `→` commits whatever the step changed, and says so once."""
    from llmz80.studio.tui import StudioApp

    app = StudioApp(tmp_path)
    async with app.run_test() as pilot:
        app.project, app.project_dir = app.service.create_project(
            "Committed", TargetPlatform.SPECTRUM
        )
        app.passed = {"proyecto", "referencia"}
        app._refresh_wizard()
        await pilot.press("enter")  # el editor del paso diseño
        await pilot.press("space")  # una celda pintada
        app._set_panel(None)  # cerrado sin pasar por Esc
        await pilot.press("right")  # deja atrás el paso
        await pilot.pause()

        assert "diseño" in app.passed
        diary = (app.project_dir / "studio.log").read_text(encoding="utf-8")
        assert "GUARDAR" in diary


@pytest.mark.asyncio
async def test_stepping_back_from_the_first_step_lands_on_the_project_step(tmp_path):
    from llmz80.studio.tui import StudioApp
    from llmz80.studio import wizard

    app = StudioApp(tmp_path)
    async with app.run_test() as pilot:
        app.project, app.project_dir = app.service.create_project(
            "Backwards", TargetPlatform.SPECTRUM
        )
        app.passed = {"proyecto"}
        app._refresh_wizard()
        await pilot.press("escape")
        await pilot.pause()

        step = wizard.current(app.project, app.project_dir, app.passed)
        assert step.name == "proyecto" and step.state == "done"
        # And no further back than that: there is no step before the first.
        await pilot.press("escape")
        await pilot.pause()
        assert wizard.current(app.project, app.project_dir, app.passed).name == "proyecto"


# --- adapting the design: not a step, a key within the design step ---------


def _archive_dossier(directory: Path, title: str = "Real Game") -> None:
    from llmz80.studio.reference import save_reference

    save_reference(
        GameReference(
            identified=True,
            confidence="high",
            title=title,
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


def test_the_design_step_names_the_adapt_key_only_where_it_works():
    """A pure check of the sentence itself: the key is offered inside
    `diseño` and nowhere else, whatever state the step is in."""
    from llmz80.studio.wizard import current

    project = blank_project("Adapting", TargetPlatform.SPECTRUM)
    design = current(project, None, passed={"proyecto", "referencia"})
    assert design.name == "diseño"

    assert "[A] adaptar el diseño a la ficha" in render_step_summary(design, can_adapt=True)
    assert "[A]" not in render_step_summary(design)


@pytest.mark.asyncio
async def test_the_design_step_offers_adapting_once_a_dossier_exists(tmp_path: Path):
    """`_adapt` is reachable again: research → adapt → design lost its middle
    when the ten shortcuts went, and the middle is where the dossier becomes
    a design."""
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Adapting"
        app.action_create()
        await pilot.pause()
        _focus_away_from_text_entry(app)
        app.passed = {"proyecto", "referencia"}
        app._refresh_wizard()
        await pilot.pause()

        reached: list[bool] = []
        app._adapt = lambda: reached.append(True)

        # No dossier archived: the key is not offered, and pressing it does
        # not start a proposal there is nothing to base on.
        assert "[A] adaptar" not in app.status_text
        await pilot.press("a")
        await pilot.pause()
        assert reached == []
        assert any(n.severity == "warning" for n in app._notifications)

        _archive_dossier(app.project_dir)
        app._refresh_wizard()
        await pilot.pause()

        assert "[A] adaptar el diseño a la ficha" in app.status_text
        await pilot.press("a")
        await pilot.pause()
        assert reached == [True]


@pytest.mark.asyncio
async def test_adapting_is_offered_in_no_other_step(tmp_path: Path):
    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#f-title").value = "Elsewhere"
        app.action_create()
        await pilot.pause()
        _focus_away_from_text_entry(app)
        _archive_dossier(app.project_dir)
        # Past the design step, standing on sprites.
        app.passed = {"proyecto", "referencia", "diseño"}
        app._refresh_wizard()
        await pilot.pause()

        reached: list[bool] = []
        app._adapt = lambda: reached.append(True)

        assert "[A] adaptar" not in app.status_text
        await pilot.press("a")
        await pilot.pause()
        assert reached == []


@pytest.mark.asyncio
async def test_escaping_out_of_the_editor_does_not_also_step_back(tmp_path: Path):
    """One press, one action. `Esc` is bound to `action_back`, and
    `event.stop()` in `on_key` does not keep this screen's own bindings from
    firing afterwards -- so handling it in both places made a single press
    close the editor *and* step the wizard back onto the step before it, as
    if the work just done had come undone."""
    from llmz80.studio.tui import StudioApp

    app = StudioApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        app.project, app.project_dir = app.service.create_project(
            "OneStep", TargetPlatform.SPECTRUM
        )
        app.passed = {"proyecto", "referencia"}
        app._refresh_wizard()
        await pilot.press("enter")
        await pilot.pause()
        assert app.active_panel == "map"

        await pilot.press("escape")
        await pilot.pause()

        assert app.active_panel is None
        assert app.passed == {"proyecto", "referencia"}

        # And with a field focused -- the case `on_key`'s text-entry branch
        # was written for -- it is still exactly one action.
        app._set_panel("design")
        app.query_one("#f-title").focus()
        await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()

        assert app.active_panel is None
        assert app.passed == {"proyecto", "referencia"}

        # At rest, the same key steps back, once.
        await pilot.press("escape")
        await pilot.pause()

        assert app.passed == {"proyecto"}
