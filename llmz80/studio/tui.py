"""Compact terminal front end for designing, writing and proving a game.

The resting screen is deliberately small: an identity line, the brief a
person actually wrote, the project's six-stage progress, and the keys that
open everything else. Everything structural -- the map, the entity roster,
sprites, a pending diff, the log -- lives in a panel that opens over that
resting screen, one at a time, so the screen a person leaves running never
grows past what they need to glance at.

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

#: The five panels a key opens, and the id of the container each shows.
PANEL_KEYS = {"m": "map", "e": "entities", "s": "sprites", "d": "diff", "l": "log"}
#: Every panel this screen can show, keyed and toggled the same way,
#: including the two that stand in for a create/open dialog: `create` and
#: `open` are not in `PANEL_KEYS` since a letter key never opens them (they
#: have their own ctrl-bindings), but they use the same single-panel-at-a-time
#: machinery as the five that do.
PANEL_IDS = {
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


class StudioApp(App[None]):
    """A deliberately thin UI: domain rules remain in StudioService."""

    TITLE = "LLMZ80 Studio"
    CSS = """
    #design { height: auto; padding: 0 1; }
    .row { height: 3; }
    .row Label { width: 10; padding: 1 0 0 0; }
    .row Input, .row Select { width: 1fr; }
    #brief-box { height: 8; border: round $primary; margin: 0 0 1 0; }
    #brief-box TextArea { height: 1fr; }
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

    # --- layout ---------------------------------------------------------

    def _field(self, label: str, widget) -> ComposeResult:
        with Horizontal(classes="row"):
            yield Label(label)
            yield widget

    def compose(self) -> ComposeResult:
        yield Header()
        # The resting screen: identity (Header's title/sub_title), the brief
        # a person wrote (plus the style that only ever feeds a prompt,
        # nested in the same group since neither is a structural panel), the
        # six-stage progress line, and the keys that open everything else.
        with Vertical(id="design"):
            yield from self._field("Title", Input(value="My Retro Game", id="f-title"))
            brief_box = Vertical(TextArea(id="f-brief"), id="brief-box")
            brief_box.border_title = "Brief"
            yield brief_box
            yield from self._field("Style", Input(id="f-style"))
        yield Static("no project loaded", id="stage-line")
        yield Static("", id="stage-detail")
        yield Static(
            "[m] mapa  [e] entidades  [s] sprites  [d] diff  [l] log",
            id="shortcuts",
            markup=False,
        )

        # Panels: one at a time, opened by a key (map/entities/sprites/
        # diff/log) or a ctrl-binding (create/open), hidden until then.
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
            # Stub: drawing and reviewing sprites lands in the next task.
            yield Static(
                "Sprites -- nothing to review here yet; this panel is a stub "
                "until the next task wires up draw-sprites.",
                id="sprites-stub",
            )
        with Vertical(id="panel-diff", classes="panel"):
            # Stub: the adapt proposal's diff lands in the next task.
            yield Static(
                "Diff -- nothing to review here yet; this panel is a stub "
                "until the next task wires up research/adapt.",
                id="diff-stub",
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
        self.query_one("#design", Vertical).display = name is None
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
        """Redraw the stage line and its detail from `screen.stage_line`.

        This is the whole of what used to be `_status`: the six-stage line
        replaces the old one-line "ready"/"not releasable" verdict, and the
        identity that used to sit in a `#status` Static now sits in the
        Header's own `sub_title`.
        """
        if self.project is None:
            self.sub_title = ""
            self.status_text = "no project loaded"
            self.query_one("#stage-line", Static).update(self.status_text)
            self.query_one("#stage-detail", Static).update("")
            return
        self.sub_title = (
            f"{self.project.metadata.slug} · {self.project.target.platform.value} · "
            f"{self.project.genre}"
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
        would also need (title stays on the resting screen, always
        editable), so `action_create` below is unchanged either way.
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

    def action_write(self) -> None:
        """Have the program written. This spends money, so it says so first."""

        def job() -> str:
            from openai import OpenAI

            from llmz80.utils.config import load_api_key, load_config

            from .generator import ResponsesProgramWriter

            model = load_config("config.yml").get("openai", {}).get("model", "gpt-5")
            writer = ResponsesProgramWriter(OpenAI(api_key=load_api_key()), model=model)
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

    def _run(self, label: str, job) -> None:
        """Run a slow job off the UI thread and report it as it finishes.

        Building takes seconds and a runtime test takes tens of them. Run on the
        UI thread they freeze the app so completely that even the "working"
        line never appears, which reads as the command doing nothing at all.
        """
        if self.project is None or self.project_dir is None:
            self.notify("Create or open a project first", severity="warning")
            return
        self._set_panel("log")
        self._log(f"[yellow]{label}...[/yellow]")
        self._busy(label)
        self._background(job, label)

    @work(exclusive=True)
    async def _background(self, job, label: str) -> None:
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
