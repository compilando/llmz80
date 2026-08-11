"""Compact terminal front end for designing, writing and proving a game.

Three panes, one status line, and the actions on keys rather than buttons. The
work is done by `StudioService` and `editing`; nothing here decides anything
about a design, which is what keeps the same operations usable from a script.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    RichLog,
    Select,
    TextArea,
    Static,
    TabbedContent,
    TabPane,
)

from . import editing
from .models import TILE_WALL, GameProject, TargetPlatform
from .packs import BUILTIN_PACKS
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


class StudioApp(App[None]):
    """A deliberately thin UI: domain rules remain in StudioService."""

    TITLE = "LLMZ80 Studio"
    CSS = """
    #status { height: 1; padding: 0 1; background: $boost; }
    #map-grid { height: auto; }
    .row { height: 3; }
    .row Label { width: 14; padding: 1 0 0 0; }
    .row Input, .row Select { width: 1fr; }
    RichLog { height: 1fr; border: round $primary; }
    TabPane { padding: 0 1; }
    DataTable { height: auto; max-height: 12; }
    TextArea { height: 6; }
    """
    BINDINGS = [
        ("ctrl+s", "save", "Save"),
        ("ctrl+n", "create", "New"),
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

    # --- layout ---------------------------------------------------------

    def _field(self, label: str, widget) -> ComposeResult:
        with Horizontal(classes="row"):
            yield Label(label)
            yield widget

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("No project loaded", id="status")
        with TabbedContent(initial="project"):
            with TabPane("Project", id="project"):
                with VerticalScroll():
                    yield from self._field("Title", Input(value="My Retro Game", id="f-title"))
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
                    yield from self._field("Open", Input(placeholder="path", id="f-open"))
                    yield Static(
                        "ctrl+n new · enter in Open loads · ctrl+w write · "
                        "ctrl+b build · ctrl+t test · ctrl+r release",
                        id="hint",
                    )
                    yield from self._field("Lives", Input(id="f-lives", type="integer"))
                    yield from self._field("Win score", Input(id="f-score", type="integer"))
                    yield from self._field("Style", Input(id="f-style"))
                    yield Label("What this game should be (free text)")
                    yield TextArea(id="f-brief")
            with TabPane("Map", id="map"):
                with Horizontal():
                    with Vertical():
                        yield Static("No project loaded.", id="map-grid", markup=True)
                        yield Static("", id="map-hint")
                    with Vertical():
                        yield Select([("level 1", 0)], value=0, allow_blank=False, id="f-level")
                        yield Select([("none", -1)], value=-1, allow_blank=False, id="f-spawn")
                        yield DataTable(id="entity-table", cursor_type="row")
            with TabPane("Log", id="log"):
                yield RichLog(id="log-view", wrap=True, markup=True)
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#entity-table", DataTable)
        table.add_columns("entity", "role", "count", "speed", "behaviour")
        self.query_one("#map-hint", Static).update(
            "wasd move · space wall · m move spawn · +/- count"
        )
        found = len(self.service.store.list_projects())
        self._log(f"Workspace {self.workspace} · {found} projects")

    # --- rendering ------------------------------------------------------

    def _log(self, message: str) -> None:
        self.query_one("#log-view", RichLog).write(message)

    #: Last status text, kept so it can be read back without scraping a widget.
    status_text: str = "No project loaded"

    def _set_status(self, text: str) -> None:
        self.status_text = text
        self.query_one("#status", Static).update(text)

    def _status(self, message: str | None = None) -> None:
        if message:
            self._set_status(message)
            return
        if self.project is None:
            self._set_status("No project loaded")
            return
        state = editing.editing_status(self.project)
        mark = "[green]ready[/green]" if state["ready"] else "[yellow]not releasable[/yellow]"
        reasons = list(state["solvability_failures"])
        if state["backend_error"]:
            reasons.append(state["backend_error"])
        detail = (" · " + "; ".join(reasons)) if reasons else ""
        self._set_status(
            f"{self.project.metadata.title} · {self.project.target.platform.value} · "
            f"{self.project.genre} · {mark}{detail}"
        )

    def _refresh(self) -> None:
        if self.project is None:
            return
        project = self.project
        self.query_one("#f-title", Input).value = project.metadata.title
        self.query_one("#f-lives", Input).value = str(project.gameplay.lives)
        self.query_one("#f-score", Input).value = str(project.gameplay.win_score)
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
        self._status()

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

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "f-open":
            self.action_open(event.value)

    def on_key(self, event) -> None:
        if self.project is None or self.query_one(TabbedContent).active != "map":
            return
        if isinstance(self.focused, (Input, Select)):
            return
        level = self.project.levels[self.level_index]
        col, row = self.cursor
        moves = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}
        if event.key in moves:
            step = moves[event.key]
            self.cursor = (
                min(max(col + step[0], 0), level.width - 1),
                min(max(row + step[1], 0), level.height - 1),
            )
            self._refresh()
        elif event.key == "space":
            self._apply(lambda: editing.toggle_tile(self.project, self.level_index, col, row))
        elif event.key == "m":
            index = self.query_one("#f-spawn", Select).value
            if isinstance(index, int) and index >= 0:
                self._apply(
                    lambda: editing.move_spawn(self.project, self.level_index, index, col, row)
                )
        elif event.key in {"plus", "equals_sign", "minus"}:
            entity_id = self._selected_entity()
            if entity_id:
                current = next(e.count for e in self.project.entities if e.id == entity_id)
                delta = -1 if event.key == "minus" else 1
                self._apply(
                    lambda: editing.set_entity_count(self.project, entity_id, current + delta)
                )
        else:
            return
        event.stop()

    # --- actions --------------------------------------------------------

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
                win_score=int(self.query_one("#f-score", Input).value or 100),
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
        self.query_one(TabbedContent).active = "log"
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
        self._set_status(f"[yellow]{label}...[/yellow] (the interface stays usable)")

    def _finished(self, label: str) -> None:
        self._status()

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
