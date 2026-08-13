"""Compact terminal front end for designing, writing and proving a game.

The resting screen is deliberately small: an identity line, a one-line
reminder of the brief, the project's six-stage progress, and the keys that
open everything else. Everything else -- editing the title, brief and style;
the map; the entity roster; sprites; a pending diff; the log -- lives in a
panel that opens over that resting screen, one at a time, so the screen a
person leaves running never grows past what they need to glance at.

The work is done by `StudioService`, `editing` and `screen`; nothing here
decides anything about a design or a project's status, which is what keeps
the same operations usable from a script.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    OptionList,
    RichLog,
    Select,
    TextArea,
    Static,
)
from textual.widgets.option_list import Option

from . import editing
from .models import TILE_WALL, GameProject, TargetPlatform
from .packs import BUILTIN_PACKS
from .screen import Stage, stage_line
from .services import StudioService

#: Cell glyphs used by the map editor, keyed by what occupies the cell.
GLYPH_WALL = "▓"
GLYPH_FLOOR = "·"
GLYPH_BY_ROLE = {
    "player": "@",
    "enemy": "&",
    "collectible": "*",
    "hazard": "^",
    "exit": ">",
}

#: One character per `screen.StageState`, drawn plain (for `status_text`,
#: which tests and scripts read as a string) and wrapped in colour markup
#: only for the widget that a person actually looks at.
STAGE_ICON = {"done": "✓", "pending": "—", "failed": "✗"}
STAGE_COLOR = {"done": "green", "pending": "dim", "failed": "red"}

#: The characters left of the brief preview's one line, before it is cut off
#: with an ellipsis. Chosen to comfortably fit a typical terminal width
#: without depending on the actual rendered width of the box: a fixed budget
#: keeps the preview exactly one line regardless of window size or how long
#: the brief itself is, which is the property that keeps the resting screen
#: from growing.
BRIEF_PREVIEW_LIMIT = 78

#: Every key that opens a panel over the resting screen, and the id of the
#: container each shows. `g` (diseño) is the odd one out: it is not one of
#: the five panels named in the brief -- map/entities/sprites/diff/log -- but
#: it is where Title, Style and the editable Brief live, since none of those
#: belong at rest either.
PANEL_KEYS = {
    "g": "design",
    "m": "map",
    "e": "entities",
    "s": "sprites",
    "d": "diff",
    "l": "log",
}
#: Every panel this screen can show, keyed and toggled the same way,
#: including the two that stand in for a create/open dialog: `create` and
#: `open` are not in `PANEL_KEYS` since a letter key never opens them (they
#: have their own ctrl-bindings), but they use the same single-panel-at-a-time
#: machinery as the ones that do.
PANEL_IDS = {
    "design": "panel-design",
    "map": "panel-map",
    "entities": "panel-entities",
    "sprites": "panel-sprites",
    "diff": "panel-diff",
    "log": "panel-log",
    "create": "panel-create",
    "open": "panel-open",
}


def render_map(project: GameProject, level_index: int, cursor: tuple[int, int]) -> str:
    """Draw one level as markup: terrain, spawns and the edit cursor.

    A module-level function over plain data, so it can be read and tested
    without a running application.
    """
    level = project.levels[level_index]
    roles = {entity.id: entity.role for entity in project.entities}
    occupants = {
        (spawn.col, spawn.row): GLYPH_BY_ROLE.get(roles.get(spawn.entity, ""), "?")
        for spawn in level.spawns
    }
    lines = []
    for row in range(level.height):
        cells = []
        for col in range(level.width):
            glyph = occupants.get(
                (col, row),
                GLYPH_WALL if level.tiles[row][col] == TILE_WALL else GLYPH_FLOOR,
            )
            if (col, row) == cursor:
                glyph = f"[reverse]{glyph}[/reverse]"
            cells.append(glyph)
        lines.append("".join(cells))
    return "\n".join(lines)


def render_stage_marks(stages: list[Stage], *, colour: bool) -> str:
    """One line: every stage's name and its state as a single character.

    `colour` picks Rich markup (for the widget a person reads) or plain text
    (for `status_text`, so a test can search it without stripping markup).
    A pure function over `screen.stage_line`'s own output, kept separate from
    the widget for the same reason `render_map` is: it can be read and tested
    without a running application.
    """
    parts = []
    for stage in stages:
        icon = STAGE_ICON[stage.state]
        if colour:
            icon = f"[{STAGE_COLOR[stage.state]}]{icon}[/{STAGE_COLOR[stage.state]}]"
        parts.append(f"{stage.name} {icon}")
    return "  ".join(parts)


def pick_stage_detail(stages: list[Stage]) -> str:
    """The one detail worth a person's attention, of the six a stage carries.

    A failed stage explains what to fix, and the earliest failure in the
    pipeline is usually the one blocking everything after it, so the first
    failed stage with a detail wins. Absent any failure, the first *done*
    stage's detail is shown instead -- typically `referencia`'s, naming the
    game that was found -- so a healthy project is not left silent. Neither
    exists (a brand new, unresearched, still-being-drawn project) and the
    line is simply empty.
    """
    failed = next((stage for stage in stages if stage.state == "failed" and stage.detail), None)
    if failed is not None:
        return failed.detail
    done = next((stage for stage in stages if stage.state == "done" and stage.detail), None)
    return done.detail if done is not None else ""


def brief_preview(brief: str, limit: int = BRIEF_PREVIEW_LIMIT) -> str:
    """One line: `brief`, whitespace-collapsed and cut to `limit` characters.

    This is what the resting screen shows -- a reminder of what the game is,
    not an editor; editing the brief lives in the design panel. Truncating by
    a fixed character budget rather than wrapping is deliberate: a preview
    that wrapped would grow the resting screen taller for every project with
    more to say, exactly the complaint this screen exists to answer, and a
    fixed budget keeps it one line regardless of the brief's length or the
    terminal's width.
    """
    text = " ".join(brief.split())
    if len(text) <= limit:
        return text
    return text[: max(limit - 1, 0)].rstrip() + "…"


class StudioApp(App[None]):
    """A deliberately thin UI: domain rules remain in StudioService."""

    TITLE = "LLMZ80 Studio"
    CSS = """
    #brief { height: auto; }
    #brief-box { height: 3; border: round $primary; margin: 0 1; padding: 0 1; }
    .row { height: 3; }
    .row Label { width: 10; padding: 1 0 0 0; }
    .row Input, .row Select { width: 1fr; }
    #brief-edit-box { height: 8; border: round $primary; margin: 0 0 1 0; }
    #brief-edit-box TextArea { height: 1fr; }
    #stage-line { height: 1; padding: 0 1; }
    #stage-detail { height: 1; padding: 0 1; }
    #shortcuts { height: 1; padding: 0 1; background: $boost; }
    .panel { display: none; height: 1fr; padding: 0 1; }
    .panel.open { display: block; }
    #map-grid { height: auto; }
    DataTable { height: auto; max-height: 12; }
    RichLog { height: 1fr; border: round $primary; }
    #workspace-list { height: 1fr; }
    """
    BINDINGS = [
        ("ctrl+s", "save", "Save"),
        ("ctrl+n", "new_dialog", "New"),
        ("ctrl+o", "open_dialog", "Open"),
        ("ctrl+f", "research", "Research"),
        ("ctrl+a", "adapt", "Adapt"),
        ("ctrl+d", "draw_sprites", "Draw sprites"),
        ("ctrl+w", "write", "Write program"),
        ("ctrl+b", "build", "Build"),
        ("ctrl+t", "test", "Test"),
        ("ctrl+r", "release", "Release"),
        ("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self, workspace: Path) -> None:
        super().__init__()
        self.workspace = workspace.expanduser().resolve()
        self.service = StudioService.at(self.workspace)
        self.project: GameProject | None = None
        self.project_dir: Path | None = None
        self.level_index = 0
        self.cursor: tuple[int, int] = (0, 0)
        #: `None` at rest; otherwise one of `PANEL_IDS`'s keys, the single
        #: panel currently shown over the resting screen.
        self.active_panel: str | None = None
        self._workspace_paths: dict[str, Path] = {}
        #: `None` until a test sets one directly, which is the injection
        #: point `research_reference`, `propose_from_reference` and
        #: `draw_sprites` are built around: the service takes a
        #: researcher/designer/artist as a parameter rather than building
        #: its own, precisely so a caller -- this screen, a script, or a
        #: test -- can hand it a fake instead of the OpenAI-backed default
        #: each `action_*` below builds when this stays `None`.
        self.researcher = None
        self.designer = None
        self.artist = None
        #: Set by `action_research`/`action_draw_sprites` on their first
        #: press when there is something an overwrite would destroy, naming
        #: which of them is waiting; a second press of the *same* action
        #: confirms it. The same two-press idiom `action_new_dialog` already
        #: uses for creating a project, just generalised past one action.
        self._pending_confirm: str | None = None
        #: `(diff, updated_project, refusals)` once `action_adapt`'s job
        #: returns, read by `_show_pending_proposal` and consumed by
        #: `_decide_proposal` -- nothing here is saved until a person
        #: presses [y] in the diff panel.
        self._pending_proposal: tuple[str, GameProject, list[str]] | None = None
        #: Assets `action_draw_sprites`'s job just registered, read by
        #: `_show_drawn_sprites` once the job finishes.
        self._drawn_sprites: list = []

    # --- layout ---------------------------------------------------------

    def _field(self, label: str, widget) -> ComposeResult:
        with Horizontal(classes="row"):
            yield Label(label)
            yield widget

    def compose(self) -> ComposeResult:
        yield Header()
        # The resting screen: identity (Header's title/sub_title), a one-line
        # reminder of the brief, the six-stage progress line, and the keys
        # that open everything else -- including editing the brief itself.
        with Vertical(id="brief"):
            brief_box = Vertical(
                Static("no project loaded", id="brief-preview", markup=False),
                id="brief-box",
            )
            brief_box.border_title = "Brief"
            yield brief_box
        yield Static("no project loaded", id="stage-line")
        yield Static("", id="stage-detail")
        yield Static(
            "[g] diseño  [m] mapa  [e] entidades  [s] sprites  [d] diff  [l] log",
            id="shortcuts",
            markup=False,
        )

        # Panels: one at a time, opened by a key (design/map/entities/
        # sprites/diff/log) or a ctrl-binding (create/open), hidden until then.
        with Vertical(id="panel-design", classes="panel"):
            yield from self._field("Title", Input(value="My Retro Game", id="f-title"))
            brief_edit_box = Vertical(TextArea(id="f-brief"), id="brief-edit-box")
            brief_edit_box.border_title = "Brief"
            yield brief_edit_box
            yield from self._field("Style", Input(id="f-style"))
        with Vertical(id="panel-create", classes="panel"):
            yield Static(
                "New project -- target and type are fixed once it exists."
            )
            yield from self._field(
                "Target",
                Select(
                    [("ZX Spectrum", "spectrum"), ("Amstrad CPC", "amstrad_cpc")],
                    value="spectrum",
                    allow_blank=False,
                    id="f-target",
                ),
            )
            yield from self._field(
                "Type",
                Select(
                    [(pack.name, pack.id) for pack in BUILTIN_PACKS],
                    value=BUILTIN_PACKS[0].id,
                    allow_blank=False,
                    id="f-genre",
                ),
            )
            yield Button("Create", id="create-confirm", variant="primary")
        with Vertical(id="panel-open", classes="panel"):
            yield Static("Open a project from the workspace.")
            yield OptionList(id="workspace-list")
        with Vertical(id="panel-map", classes="panel"):
            with Horizontal():
                with Vertical():
                    yield Static("No project loaded.", id="map-grid", markup=True)
                    yield Static("", id="map-hint")
                with Vertical():
                    yield Select([("level 1", 0)], value=0, allow_blank=False, id="f-level")
                    yield Select([("none", -1)], value=-1, allow_blank=False, id="f-spawn")
        with Vertical(id="panel-entities", classes="panel"):
            yield from self._field("Lives", Input(id="f-lives", type="integer"))
            yield DataTable(id="entity-table", cursor_type="row")
        with Vertical(id="panel-sprites", classes="panel"):
            # Where art `action_draw_sprites` generated is looked at before
            # it is compiled -- filled in by `_show_drawn_sprites`.
            yield Static(
                "No sprites drawn yet. Press ctrl+d to draw the art this "
                "project is missing.",
                id="sprites-view",
            )
        with Vertical(id="panel-diff", classes="panel"):
            # Where `action_adapt`'s proposal is reviewed and accepted or
            # rejected -- filled in by `_show_pending_proposal`. `markup`
            # off: this shows a model-written diff verbatim, the same reason
            # `#shortcuts` (also literal bracketed text) turns it off.
            yield Static(
                "No proposal yet. Press ctrl+a to adapt the design to the "
                "researched game.",
                id="diff-view",
                markup=False,
            )
        with Vertical(id="panel-log", classes="panel"):
            yield RichLog(id="log-view", wrap=True, markup=True)
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#entity-table", DataTable)
        table.add_columns("entity", "role", "count", "speed", "behaviour")
        self.query_one("#map-hint", Static).update(
            "wasd move · space wall · m move spawn · +/- count"
        )
        self._set_panel(None)
        found = len(self.service.store.list_projects())
        self._log(f"Workspace {self.workspace} · {found} projects")

    # --- panels -----------------------------------------------------------

    def _set_panel(self, name: str | None) -> None:
        """Show `name`'s panel over the resting screen, or return to rest.

        Exactly one panel is visible at a time; opening one implicitly closes
        whichever was open, and `None` closes the open panel (if any) back to
        the resting screen -- header, brief, stage line, shortcuts.
        """
        self.active_panel = name
        self.query_one("#brief", Vertical).display = name is None
        self.query_one("#stage-line", Static).display = name is None
        self.query_one("#stage-detail", Static).display = name is None
        self.query_one("#shortcuts", Static).display = name is None
        for key, widget_id in PANEL_IDS.items():
            self.query_one(f"#{widget_id}", Vertical).set_class(key == name, "open")
        if name == "open":
            self._refresh_workspace_list()

    def _toggle_panel(self, name: str) -> None:
        self._set_panel(None if self.active_panel == name else name)

    # --- rendering ------------------------------------------------------

    def _log(self, message: str) -> None:
        self.query_one("#log-view", RichLog).write(message)

    #: Last status text, plain (no Rich markup) so it can be read back and
    #: searched by a test or a script without scraping a widget.
    status_text: str = "no project loaded"

    def _refresh_stage(self) -> None:
        """Redraw the brief preview, the stage line and its detail.

        This is the whole of what used to be `_status`: the six-stage line
        replaces the old one-line "ready"/"not releasable" verdict, and the
        identity that used to sit in a `#status` Static now sits in the
        Header's own `sub_title`.
        """
        if self.project is None:
            self.sub_title = ""
            self.status_text = "no project loaded"
            self.query_one("#brief-preview", Static).update(self.status_text)
            self.query_one("#stage-line", Static).update(self.status_text)
            self.query_one("#stage-detail", Static).update("")
            return
        self.sub_title = (
            f"{self.project.metadata.slug} · {self.project.target.platform.value} · "
            f"{self.project.genre}"
        )
        self.query_one("#brief-preview", Static).update(
            brief_preview(self.project.metadata.brief)
        )
        stages = stage_line(self.project, self.project_dir)
        detail = pick_stage_detail(stages)
        self.status_text = render_stage_marks(stages, colour=False)
        if detail:
            self.status_text += f"\n{detail}"
        self.query_one("#stage-line", Static).update(render_stage_marks(stages, colour=True))
        self.query_one("#stage-detail", Static).update(detail)

    def _refresh(self) -> None:
        if self.project is None:
            return
        project = self.project
        self.query_one("#f-title", Input).value = project.metadata.title
        self.query_one("#f-lives", Input).value = str(project.gameplay.lives)
        self.query_one("#f-style", Input).value = project.presentation.style
        brief = self.query_one("#f-brief", TextArea)
        if brief.text != project.metadata.brief:
            brief.text = project.metadata.brief

        level = project.levels[self.level_index]
        self.cursor = (
            min(self.cursor[0], level.width - 1),
            min(self.cursor[1], level.height - 1),
        )
        self.query_one("#map-grid", Static).update(
            render_map(project, self.level_index, self.cursor)
        )
        levels = self.query_one("#f-level", Select)
        levels.set_options([(item.name, index) for index, item in enumerate(project.levels)])
        levels.value = self.level_index
        roles = {entity.id: entity.role for entity in project.entities}
        spawns = self.query_one("#f-spawn", Select)
        spawns.set_options(
            [
                (f"{index}: {spawn.entity} ({roles.get(spawn.entity, '?')})", index)
                for index, spawn in enumerate(level.spawns)
            ]
            or [("none", -1)]
        )
        table = self.query_one("#entity-table", DataTable)
        table.clear()
        for entity in project.entities:
            table.add_row(
                entity.id,
                entity.role,
                str(entity.count),
                str(entity.speed),
                entity.behaviour,
                key=entity.id,
            )
        self._refresh_stage()

    def _refresh_workspace_list(self) -> None:
        listing = self.query_one("#workspace-list", OptionList)
        listing.clear_options()
        projects = self.service.store.list_projects()
        self._workspace_paths = {str(index): path for index, path in enumerate(projects)}
        if not projects:
            listing.add_option(Option("(no projects in this workspace yet)", id="none"))
            return
        for index, path in enumerate(projects):
            listing.add_option(Option(path.name, id=str(index)))

    def _apply(self, operation) -> None:
        """Run an editing operation, reporting refusals instead of crashing."""
        try:
            self.project = operation()
            if self.project_dir is not None:
                self.service.save_project(self.project, self.project_dir)
            self._refresh()
        except editing.EditError as exc:
            self.notify(str(exc), severity="warning")
        except Exception as exc:
            self.notify(str(exc), severity="error")

    def _confirmed(self, action: str) -> bool:
        """True on the second call in a row naming the same `action`.

        The first call remembers `action` and returns `False`, so a caller
        can warn about what a redraw or a fresh search would overwrite and
        wait for the same key to confirm it -- `action_new_dialog`'s
        press-again-to-confirm, generalised past creating a project.
        """
        if self._pending_confirm == action:
            self._pending_confirm = None
            return True
        self._pending_confirm = action
        return False

    def _show_pending_proposal(self) -> None:
        """After `action_adapt`'s job returns, show its diff for review.

        Runs as `_run`'s `on_finished`, once the job's own summary line is
        already in the log -- this is what actually opens the diff panel,
        with the refusals the repair loop overcame (if any) ahead of the
        diff itself, so a person watching several model calls go by sees
        what each repair was for. Nothing here saves anything: [y] and [n],
        handled in `on_key`, are the only paths into `_decide_proposal`.
        """
        if self._pending_proposal is None:
            return
        diff, _updated, refusals = self._pending_proposal
        lines = [
            f"Attempt {number} was refused, repairing: {reason}"
            for number, reason in enumerate(refusals, start=1)
        ]
        if lines:
            lines.append("")
        lines.append(diff)
        lines.append("")
        lines.append("[y] apply   [n] discard")
        self.query_one("#diff-view", Static).update("\n".join(lines))
        self._set_panel("diff")

    def _decide_proposal(self, accept: bool) -> None:
        """[y]/[n] in the diff panel: apply the already-validated project
        `propose_from_reference` built, or leave the project untouched."""
        if self._pending_proposal is None:
            return
        _diff, updated, _refusals = self._pending_proposal
        self._pending_proposal = None
        if accept:
            self._apply(lambda: updated)
            self.query_one("#diff-view", Static).update(
                "Applied. Press ctrl+a to propose another adaptation."
            )
            self._log("[green]Adaptation applied[/green]")
        else:
            self.query_one("#diff-view", Static).update(
                "Left unchanged. Press ctrl+a to propose another adaptation."
            )
            self._log("Left unchanged")

    def _show_drawn_sprites(self) -> None:
        """After `action_draw_sprites`'s job returns, look at what it drew.

        Runs as `_run`'s `on_finished`. `image_utils.display_sprite` is the
        terminal pixel-art renderer `llmz80 project sprites` already uses,
        and `llmz80.cli._sprite_preview_array` is the array it renders --
        both reused rather than re-derived. `display_sprite` writes its
        ANSI-coloured rows straight to stdout, which would corrupt this
        screen if it ran while Textual owns the terminal, so its output is
        captured and read back through `rich.text.Text.from_ansi`, Rich's
        own conversion from raw ANSI text into a renderable a `Static` can
        display.
        """
        drawn = self._drawn_sprites
        if not drawn or self.project is None or self.project_dir is None:
            return
        import contextlib
        import io
        from types import SimpleNamespace

        from PIL import Image
        from rich.console import Group
        from rich.text import Text

        from image_utils import display_sprite
        from llmz80.cli import _sprite_preview_array

        mode = None
        if self.project.target.platform.value == "amstrad_cpc":
            mode = "mode0" if self.project.target.video_mode.value == "cpc_mode_0" else "mode1"
        args = SimpleNamespace(platform=self.project.target.platform.value, mode=mode)

        blocks: list[Text] = []
        for asset in drawn:
            sheet = Image.open(self.project_dir / asset.source).convert("RGBA")
            array = _sprite_preview_array(sheet, args)
            captured = io.StringIO()
            with contextlib.redirect_stdout(captured):
                display_sprite(array, args)
            blocks.append(Text.from_markup(f"[b]{asset.id}[/b]  {asset.source}"))
            blocks.append(Text.from_ansi(captured.getvalue()))
        self.query_one("#sprites-view", Static).update(Group(*blocks))
        self._set_panel("sprites")

    def _selected_entity(self) -> str | None:
        table = self.query_one("#entity-table", DataTable)
        if not table.row_count:
            return None
        try:
            return str(table.get_row_at(table.cursor_row)[0])
        except Exception:
            return None

    # --- events ---------------------------------------------------------

    def on_select_changed(self, event: Select.Changed) -> None:
        if self.project is None:
            return
        if event.select.id == "f-level" and isinstance(event.value, int):
            self.level_index = event.value
            self.cursor = (0, 0)
            self._refresh()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create-confirm":
            self.action_create()
            self._set_panel(None)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if event.option_list.id != "workspace-list":
            return
        path = self._workspace_paths.get(event.option_id or "")
        if path is None:
            return
        self.action_open(str(path))
        self._set_panel(None)

    #: Widgets that own the letter keys they're typed while focused -- a
    #: panel-toggle key or a map-editing key must never fire while someone is
    #: naming a project or writing a brief.
    _TEXT_ENTRY = (Input, Select, TextArea, Button, OptionList)

    def on_key(self, event) -> None:
        key = event.key
        if isinstance(self.focused, self._TEXT_ENTRY):
            if key == "escape" and self.active_panel is not None:
                self._set_panel(None)
                event.stop()
            return
        if key == "escape":
            if self.active_panel is not None:
                self._set_panel(None)
                event.stop()
            return
        if self.active_panel == "map" and self.project is not None:
            level = self.project.levels[self.level_index]
            col, row = self.cursor
            moves = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}
            if key in moves:
                step = moves[key]
                self.cursor = (
                    min(max(col + step[0], 0), level.width - 1),
                    min(max(row + step[1], 0), level.height - 1),
                )
                self._refresh()
                event.stop()
                return
            if key == "space":
                self._apply(lambda: editing.toggle_tile(self.project, self.level_index, col, row))
                event.stop()
                return
            if key == "m":
                index = self.query_one("#f-spawn", Select).value
                if isinstance(index, int) and index >= 0:
                    self._apply(
                        lambda: editing.move_spawn(
                            self.project, self.level_index, index, col, row
                        )
                    )
                event.stop()
                return
        if self.active_panel == "diff" and self._pending_proposal is not None:
            if key == "y":
                self._decide_proposal(True)
                event.stop()
                return
            if key == "n":
                self._decide_proposal(False)
                event.stop()
                return
        if self.active_panel == "entities" and key in {"plus", "equals_sign", "minus"}:
            entity_id = self._selected_entity()
            if entity_id and self.project is not None:
                current = next(e.count for e in self.project.entities if e.id == entity_id)
                delta = -1 if key == "minus" else 1
                self._apply(
                    lambda: editing.set_entity_count(self.project, entity_id, current + delta)
                )
            event.stop()
            return
        if key in PANEL_KEYS:
            self._toggle_panel(PANEL_KEYS[key])
            event.stop()

    # --- actions --------------------------------------------------------

    def action_new_dialog(self) -> None:
        """ctrl+n: open the creation panel (target and type -- fixed once a
        project exists); pressed again while it is open, confirm and create.

        Two presses stand in for a dialog's open-then-confirm without a
        second modal screen: the panel holds exactly the fields a script
        would also need (title lives in the design panel, always editable
        the same way whether or not a project exists yet), so `action_create`
        below is unchanged either way.
        """
        if self.active_panel == "create":
            self.action_create()
            self._set_panel(None)
        else:
            self._set_panel("create")

    def action_open_dialog(self) -> None:
        """ctrl+o: the workspace picker, replacing a free-text path field
        with the same list `store.list_projects()` already knows."""
        self._toggle_panel("open")

    def action_create(self) -> None:
        try:
            self.project, self.project_dir = self.service.create_project(
                self.query_one("#f-title", Input).value.strip(),
                TargetPlatform(str(self.query_one("#f-target", Select).value)),
                str(self.query_one("#f-genre", Select).value),
            )
            self.level_index, self.cursor = 0, (0, 0)
            self._refresh()
            self._log(f"[green]Created[/green] {self.project_dir / 'game.yml'}")
        except Exception as exc:
            self.notify(str(exc), severity="error")

    def action_open(self, path: str) -> None:
        try:
            location = Path(path).expanduser().resolve()
            self.project = self.service.open_project(location)
            self.project_dir = location.parent if location.name == "game.yml" else location
            self.level_index, self.cursor = 0, (0, 0)
            self._refresh()
            self._log(f"[green]Opened[/green] {self.project_dir}")
        except Exception as exc:
            self.notify(str(exc), severity="error")

    def action_save(self) -> None:
        if self.project is None or self.project_dir is None:
            return
        self._apply(
            lambda: editing.rename_project(
                self.project,
                self.query_one("#f-title", Input).value.strip(),
                lives=int(self.query_one("#f-lives", Input).value or 3),
                style=self.query_one("#f-style", Input).value.strip(),
                brief=self.query_one("#f-brief", TextArea).text.strip(),
            )
        )
        self._log("[green]Saved[/green]")

    def action_research(self) -> None:
        """ctrl+f: research the real game the brief names, archiving
        reference.yml.

        This searches the web and calls the OpenAI API, so it says so
        before doing either -- the check for an existing dossier happens
        first and costs nothing. Like `llmz80 project reference`, it asks
        before replacing a dossier that already exists, since that file is
        meant to be corrected by hand, not silently overwritten; and a
        dossier that exists but cannot be read (malformed YAML) is reported
        the same way, not crashed on.
        """
        if self.project is None or self.project_dir is None:
            self.notify("Create or open a project first", severity="warning")
            return
        try:
            existing = self.service.reference(self.project_dir)
        except ValueError as exc:
            self.notify(str(exc), severity="error")
            self.notify(
                "Fix or remove reference.yml before researching again.",
                severity="warning",
            )
            return
        if existing is not None and not self._confirmed("research"):
            self.notify(
                "An archived dossier already exists: "
                f"{existing.title or '(unidentified)'}. Press ctrl+f again to replace it.",
                severity="warning",
            )
            return

        project, directory = self.project, self.project_dir

        def job() -> str:
            researcher = self.researcher
            if researcher is None:
                from ..cli import _openai_client_and_model
                from .reference import ResponsesReferenceResearcher

                client, model = _openai_client_and_model()
                researcher = ResponsesReferenceResearcher(client, model=model)
            dossier = self.service.research_reference(project, directory, researcher)
            if not dossier.identified:
                return "No game was identified. The design keeps its typology."
            known = [part for part in (dossier.publisher, str(dossier.year or "")) if part]
            on_publisher = f" ({', '.join(known)})" if known else ""
            return (
                f"[green]{dossier.title}{on_publisher}[/green] · "
                f"{len(dossier.sources)} source(s). See the stage line for referencia."
            )

        self._run("Researching with the OpenAI API; this searches the web", job)

    def action_adapt(self) -> None:
        """ctrl+a: propose an adaptation to the researched game, and open
        the diff panel to review it.

        Nothing is applied here -- `propose_from_reference` only returns an
        already-validated candidate project, and `_show_pending_proposal`
        shows its diff (and whatever the repair loop had to overcome to
        reach it) for a person to accept with [y] or discard with [n] in
        the diff panel, the same restraint `llmz80 project adapt` applies
        before it ever calls `save_project`.
        """
        if self.project is None or self.project_dir is None:
            self.notify("Create or open a project first", severity="warning")
            return
        self._pending_proposal = None
        project, directory = self.project, self.project_dir

        def job() -> str:
            designer = self.designer
            if designer is None:
                from ..cli import _openai_client_and_model
                from .reference_design import ResponsesReferenceDesigner

                client, model = _openai_client_and_model()
                designer = ResponsesReferenceDesigner(client, model=model)
            proposal, diff, updated, refusals = self.service.propose_from_reference(
                project, directory, designer
            )
            self._pending_proposal = (diff, updated, refusals)
            lines = [
                f"Attempt {number} was refused, repairing: {reason}"
                for number, reason in enumerate(refusals, start=1)
            ]
            lines.append("[green]Proposal ready[/green] -- review it in the diff panel.")
            return "\n".join(lines)

        self._run(
            "Proposing an adaptation with the OpenAI API",
            job,
            on_finished=self._show_pending_proposal,
        )

    def action_draw_sprites(self) -> None:
        """ctrl+d: draw the art this project is missing, and register each
        result as an asset.

        `draw_sprites` only ever fills a gap -- it never touches an entity
        that already wears a sprite-kind asset -- so the one place this can
        overwrite existing art is here, by evicting it first; like
        `llmz80 project sprites`, that only happens after asking, and this
        calls OpenAI's image API, so it says so before doing that too.
        """
        if self.project is None or self.project_dir is None:
            self.notify("Create or open a project first", severity="warning")
            return

        have = {asset.id for asset in self.project.assets if asset.kind == "sprite"}
        needed = sorted({entity.sprite for entity in self.project.entities})
        existing = [sprite_id for sprite_id in needed if sprite_id in have]
        if existing and not self._confirmed("sprites"):
            self.notify(
                "Sprite art already exists for: "
                + ", ".join(existing)
                + ". Press ctrl+d again to redraw it, overwriting the existing art.",
                severity="warning",
            )
            return
        if existing:
            for sprite_id in existing:
                asset = next(
                    a for a in self.project.assets if a.kind == "sprite" and a.id == sprite_id
                )
                (self.project_dir / asset.source).unlink(missing_ok=True)
            remaining = [
                a for a in self.project.assets if not (a.kind == "sprite" and a.id in existing)
            ]
            candidate = GameProject.model_validate(
                {
                    **self.project.model_dump(mode="json"),
                    "assets": [a.model_dump(mode="json") for a in remaining],
                }
            )
            self.project.assets = candidate.assets
            self.service.save_project(self.project, self.project_dir)

        self._drawn_sprites = []
        project, directory = self.project, self.project_dir

        def job() -> str:
            artist = self.artist
            if artist is None:
                from generators.openai_generator import OpenAIImageGenerator

                from ..cli import _openai_client_and_model, _openai_image_model
                from .sprite_artist import SpriteArtist

                # `OpenAIImageGenerator` takes an API key, not a client --
                # `llmz80 project sprites` reads it off the client
                # `_openai_client_and_model` already built rather than
                # loading it a second time, and this does the same; the
                # image model comes from `_openai_image_model` for the same
                # reason `llmz80 project sprites` does.
                client, _model = _openai_client_and_model()
                artist = SpriteArtist(
                    OpenAIImageGenerator(api_key=client.api_key, model=_openai_image_model())
                )
            drawn = self.service.draw_sprites(project, directory, artist)
            self._drawn_sprites = drawn
            if not drawn:
                return "Every entity already has sprite art."
            return "[green]Drawn[/green] " + ", ".join(asset.id for asset in drawn)

        self._run(
            "Drawing sprites with OpenAI's image API",
            job,
            on_finished=self._show_drawn_sprites,
        )

    def action_write(self) -> None:
        """Have the program written. This spends money, so it says so first."""

        def job() -> str:
            from ..cli import _openai_client_and_model
            from .generator import ResponsesProgramWriter

            client, model = _openai_client_and_model()
            writer = ResponsesProgramWriter(client, model=model)
            report = self.service.write_program(self.project, self.project_dir, writer)
            lines = [
                f"  attempt {attempt['number']}: build={attempt['build_passed']} "
                f"acceptance={attempt['acceptance_passed']}"
                for attempt in report["attempts"]
            ]
            lines.append(
                "[green]Program accepted[/green]"
                if report["accepted"]
                else "[red]Not accepted[/red] " + report["last_error"]
            )
            return "\n".join(lines)

        self._run("Writing the program with the OpenAI API", job)

    def _run(self, label: str, job, *, on_finished=None) -> None:
        """Run a slow job off the UI thread and report it as it finishes.

        Building takes seconds and a runtime test takes tens of them. Run on the
        UI thread they freeze the app so completely that even the "working"
        line never appears, which reads as the command doing nothing at all.

        `on_finished`, when given, runs after the job's message has already
        been logged and the stage line redrawn -- research, adapt and
        draw-sprites use it to open the panel their result belongs in
        (stage line, diff, sprites respectively) without teaching this
        generic runner anything about any one of them.
        """
        if self.project is None or self.project_dir is None:
            self.notify("Create or open a project first", severity="warning")
            return
        self._set_panel("log")
        self._log(f"[yellow]{label}...[/yellow]")
        self._busy(label)
        self._background(job, label, on_finished)

    @work(exclusive=True)
    async def _background(self, job, label: str, on_finished=None) -> None:
        """Await the job on a thread, then update from the UI task itself.

        Handing the result back through the event loop rather than across
        threads keeps every widget touched from the task that owns it.
        """
        try:
            message = await asyncio.to_thread(job)
        except Exception as exc:
            message = f"[red]{exc}[/red]"
            self.notify(str(exc), severity="error")
        self._log(message)
        self._finished(label)
        if on_finished is not None:
            on_finished()

    def _busy(self, label: str) -> None:
        text = f"{label}... (the interface stays usable)"
        self.status_text = text
        self.query_one("#stage-detail", Static).update(f"[yellow]{text}[/yellow]")

    def _finished(self, label: str) -> None:
        self._refresh_stage()

    def action_build(self) -> None:
        def work() -> str:
            result = self.service.build(self.project, self.project_dir)
            return (
                f"[green]Build passed[/green] {result.artifact}"
                if result.success
                else "[red]Build rejected[/red] see build/build_report.json"
            )

        self._run("Building", work)

    def action_test(self) -> None:
        def work() -> str:
            report = self.service.runtime_test(self.project, self.project_dir)
            acceptance = report.get("acceptance") or {}
            lines = [
                "[green]Runtime passed[/green]"
                if report["quality_pass"]
                else "[red]Runtime rejected[/red]"
            ]
            for scenario in acceptance.get("scenarios") or []:
                if isinstance(scenario, dict):
                    mark = "ok" if scenario["passed"] else "FAILED"
                    lines.append(f"  {scenario['id']}: {mark} {scenario['mismatches'] or ''}")
            return "\n".join(lines)

        self._run("Building and running", work)

    def action_release(self) -> None:
        def work() -> str:
            archive = self.service.release(self.project, self.project_dir)
            return f"[green]Released[/green] {archive}"

        self._run("Exporting", work)


def run_studio(workspace: Path = Path("studio-projects")) -> None:
    StudioApp(workspace).run()
