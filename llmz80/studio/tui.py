"""Textual front end for guided project creation and iteration."""

from __future__ import annotations

from pathlib import Path

from openai import OpenAI
from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    RichLog,
    Select,
    Static,
    TabbedContent,
    TabPane,
)

from . import editing
from .models import TILE_WALL, GameProject, GenreId, ProjectScope, TargetPlatform
from .planner import ProjectProposal, ResponsesProjectPlanner, apply_proposal, proposal_diff
from .services import StudioService
from llmz80.utils.config import load_api_key, load_config

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

    Kept a module-level function of plain data so it can be read and tested
    without a running Textual application.
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
    SUB_TITLE = "Commercial-quality games for ZX Spectrum and Amstrad CPC"
    CSS = """
    Screen { background: $surface; }
    #summary { height: auto; padding: 1 2; background: $boost; margin-bottom: 1; }
    .form { padding: 1 2; }
    .field { margin-bottom: 1; }
    Button { margin-right: 1; }
    RichLog { height: 1fr; border: round $primary; }
    TabPane { padding: 1 2; }
    #budget { color: $text-muted; margin: 1 0; }
    """
    BINDINGS = [
        ("ctrl+s", "save", "Save"),
        ("ctrl+g", "generate", "Generate"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, workspace: Path) -> None:
        super().__init__()
        self.workspace = workspace.expanduser().resolve()
        self.service = StudioService.at(self.workspace)
        self.project: GameProject | None = None
        self.project_dir: Path | None = None
        self.pending_proposal: ProjectProposal | None = None
        self.level_index = 0
        self.cursor: tuple[int, int] = (0, 0)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(self._summary_text(), id="summary")
        with TabbedContent(initial="new"):
            with TabPane("New / Open", id="new"):
                with VerticalScroll(classes="form"):
                    yield Label("Project title")
                    yield Input(value="My Retro Game", id="new-title", classes="field")
                    yield Label("Target system")
                    yield Select(
                        [("ZX Spectrum 48K", "spectrum"), ("Amstrad CPC", "amstrad_cpc")],
                        value="spectrum",
                        allow_blank=False,
                        id="new-platform",
                        classes="field",
                    )
                    yield Label("Game type")
                    yield Select(
                        [
                            ("Single-screen collect", "single_screen_collect"),
                            ("Maze chase", "maze_chase"),
                        ],
                        value="single_screen_collect",
                        allow_blank=False,
                        id="new-genre",
                        classes="field",
                    )
                    yield Label("Production scope")
                    yield Select(
                        [
                            ("Complete game", "complete"),
                            ("Commercial release", "commercial"),
                            ("Prototype", "prototype"),
                        ],
                        value="complete",
                        allow_blank=False,
                        id="new-scope",
                        classes="field",
                    )
                    with Horizontal():
                        yield Button("Create project", id="create", variant="primary")
                    yield Label("Open existing project (directory or game.yml)")
                    yield Input(placeholder="/path/to/project", id="open-path", classes="field")
                    yield Button("Open", id="open")
            with TabPane("Design", id="design"):
                yield Label("Title")
                yield Input(id="edit-title", disabled=True)
                yield Label("Lives")
                yield Input(id="edit-lives", type="integer", disabled=True)
                yield Label("Win score")
                yield Input(id="edit-win-score", type="integer", disabled=True)
                yield Label("Visual style")
                yield Input(id="edit-style", disabled=True)
                yield Label("Enemy speed (1-4)")
                yield Input(id="edit-enemy-speed", type="integer", disabled=True)
                yield Label("Level names (comma separated)")
                yield Input(id="edit-level-names", disabled=True)
                yield Static("Scene flow unavailable.", id="scene-flow")
                yield Static("No project loaded.", id="budget")
                with Horizontal():
                    yield Button("Save", id="save", disabled=True, variant="success")
                    yield Button(
                        "Generate sources", id="generate", disabled=True, variant="primary"
                    )
                    yield Button("Build", id="compile", disabled=True, variant="warning")
                    yield Button("Runtime test", id="runtime", disabled=True)
                    yield Button("Export release", id="release", disabled=True, variant="success")
            with TabPane("Map", id="map"):
                yield Label("Level")
                yield Select([("level 1", 0)], value=0, allow_blank=False, id="map-level")
                yield Static(
                    "W A S D move the cursor · SPACE toggles wall · "
                    "M moves the selected spawn here",
                    classes="field",
                )
                yield Static("No project loaded.", id="map-grid", markup=True)
                yield Static("", id="map-status")
                yield Label("Spawn to move")
                yield Select([("none", -1)], value=-1, allow_blank=False, id="map-spawn")
                with Horizontal():
                    yield Button("Reset terrain", id="map-pattern", disabled=True)
                    yield Button("Clear terrain", id="map-clear", disabled=True)
                yield Label("Resize (width x height)")
                with Horizontal():
                    yield Input(id="map-width", type="integer", classes="field")
                    yield Input(id="map-height", type="integer", classes="field")
                    yield Button("Resize", id="map-resize", disabled=True)
                yield Label("Level name")
                with Horizontal():
                    yield Input(id="map-name", classes="field")
                    yield Button("Rename", id="map-rename", disabled=True)
            with TabPane("Entities", id="entities"):
                yield Static("No project loaded.", id="entity-list")
                yield Label("Entity")
                yield Select([("none", "")], value="", allow_blank=False, id="entity-id")
                yield Label("Count")
                yield Input(id="entity-count", type="integer", classes="field")
                yield Label("Speed (1-4)")
                yield Input(id="entity-speed", type="integer", classes="field")
                with Horizontal():
                    yield Button("Apply", id="entity-apply", disabled=True, variant="primary")
                    yield Button("Remove", id="entity-remove", disabled=True, variant="error")
                yield Label("Add entity (id and role)")
                with Horizontal():
                    yield Input(placeholder="guard", id="entity-new-id", classes="field")
                    yield Select(
                        [
                            ("enemy", "enemy"),
                            ("collectible", "collectible"),
                        ],
                        value="enemy",
                        allow_blank=False,
                        id="entity-new-role",
                    )
                    yield Button("Add", id="entity-add", disabled=True)
            with TabPane("Build & Test", id="build"):
                yield RichLog(id="log", wrap=True, markup=True)
            with TabPane("Graphics", id="graphics"):
                yield Label("Import sprite image (PNG, BMP or GIF)")
                yield Input(placeholder="/path/to/sprite.png", id="asset-path")
                yield Button("Import and convert", id="add-asset", disabled=True, variant="primary")
                yield Static("No assets.", id="asset-list")
            with TabPane("AI Assistant", id="assistant"):
                yield Label("Describe a design change")
                yield Input(
                    placeholder="Add a faster enemy from level 2",
                    id="ai-request",
                )
                yield Static(
                    "The API returns a typed proposal. Nothing changes until you review and apply it.",
                    classes="field",
                )
                with Horizontal():
                    yield Button("Request proposal (uses API)", id="propose", disabled=True)
                    yield Button(
                        "Apply reviewed proposal",
                        id="apply-proposal",
                        disabled=True,
                        variant="success",
                    )
                yield RichLog(id="ai-preview", wrap=True, markup=False)
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#log", RichLog).write(
            f"[bold]Workspace:[/bold] {self.workspace}\n"
            f"Projects found: {len(self.service.store.list_projects())}"
        )

    def _summary_text(self) -> str:
        if self.project is None:
            return "No project loaded · Create or open a project to begin"
        return (
            f"{self.project.metadata.title} · {self.project.target.platform.value} · "
            f"{self.project.genre} · {len(self.project.levels)} levels"
        )

    def _load_into_editor(self) -> None:
        assert self.project is not None
        self.query_one("#summary", Static).update(self._summary_text())
        title = self.query_one("#edit-title", Input)
        lives = self.query_one("#edit-lives", Input)
        win_score = self.query_one("#edit-win-score", Input)
        style = self.query_one("#edit-style", Input)
        speed = self.query_one("#edit-enemy-speed", Input)
        level_names = self.query_one("#edit-level-names", Input)
        for field in (title, lives, win_score, style, speed, level_names):
            field.disabled = False
        title.value = self.project.metadata.title
        lives.value = str(self.project.gameplay.lives)
        win_score.value = str(self.project.gameplay.win_score)
        style.value = self.project.presentation.style
        enemy = next(entity for entity in self.project.entities if entity.role == "enemy")
        speed.value = str(enemy.speed)
        level_names.value = ", ".join(level.name for level in self.project.levels)
        self.query_one("#scene-flow", Static).update(
            "Scene flow: "
            + " → ".join(f"{scene.id} ({scene.kind.value})" for scene in self.project.scenes)
        )
        self.query_one("#save", Button).disabled = False
        self.query_one("#generate", Button).disabled = False
        self.query_one("#compile", Button).disabled = False
        self.query_one("#runtime", Button).disabled = False
        self.query_one("#release", Button).disabled = not (
            self.project_dir
            and (self.project_dir / "build" / "studio_quality_report.json").is_file()
        )
        self.query_one("#propose", Button).disabled = False
        self.query_one("#add-asset", Button).disabled = False
        self.query_one("#asset-list", Static).update(
            "\n".join(
                f"{asset.id}: {asset.width}x{asset.height} · {asset.source}"
                for asset in self.project.assets
            )
            or "No assets."
        )
        self._refresh_map()
        self._refresh_entities()
        budget = self.project.budgets
        self.query_one("#budget", Static).update(
            f"Budgets: binary {budget.binary_bytes} B · data {budget.static_data_bytes} B · "
            f"entities {sum(item.count for item in self.project.entities)}/{budget.max_entities} · 50 Hz"
        )

    def _refresh_map(self) -> None:
        if self.project is None:
            return
        level = self.project.levels[self.level_index]
        self.cursor = (
            min(self.cursor[0], level.width - 1),
            min(self.cursor[1], level.height - 1),
        )
        self.query_one("#map-grid", Static).update(
            render_map(self.project, self.level_index, self.cursor)
        )
        status = editing.editing_status(self.project)
        if status["ready"]:
            text = "[green]Design ready:[/green] every level is solvable and the engine accepts it"
        else:
            reasons = list(status["solvability_failures"])
            if status["backend_error"]:
                reasons.append(status["backend_error"])
            text = "[yellow]Not releasable:[/yellow] " + " · ".join(reasons)
        self.query_one("#map-status", Static).update(text)
        self.query_one("#map-name", Input).value = level.name
        self.query_one("#map-width", Input).value = str(level.width)
        self.query_one("#map-height", Input).value = str(level.height)
        level_select = self.query_one("#map-level", Select)
        level_select.set_options(
            [(item.name, index) for index, item in enumerate(self.project.levels)]
        )
        level_select.value = self.level_index
        roles = {entity.id: entity.role for entity in self.project.entities}
        spawn_select = self.query_one("#map-spawn", Select)
        spawn_select.set_options(
            [
                (f"{index}: {spawn.entity} ({roles.get(spawn.entity, '?')})", index)
                for index, spawn in enumerate(level.spawns)
            ]
            or [("none", -1)]
        )
        for identifier in ("map-pattern", "map-clear", "map-resize", "map-rename"):
            self.query_one(f"#{identifier}", Button).disabled = False

    def _refresh_entities(self) -> None:
        if self.project is None:
            return
        self.query_one("#entity-list", Static).update(
            "\n".join(
                f"{entity.id}: {entity.role} x{entity.count} speed {entity.speed}"
                for entity in self.project.entities
            )
        )
        select = self.query_one("#entity-id", Select)
        select.set_options([(entity.id, entity.id) for entity in self.project.entities])
        if select.value not in {entity.id for entity in self.project.entities}:
            select.value = self.project.entities[0].id
        chosen = next(
            entity for entity in self.project.entities if entity.id == select.value
        )
        self.query_one("#entity-count", Input).value = str(chosen.count)
        self.query_one("#entity-speed", Input).value = str(chosen.speed)
        for identifier in ("entity-apply", "entity-remove", "entity-add"):
            self.query_one(f"#{identifier}", Button).disabled = False

    def _apply_edit(self, edited: GameProject, message: str) -> None:
        """Adopt an edited design, persist it and refresh every view."""
        self.project = edited
        if self.project_dir is not None:
            self.service.save_project(self.project, self.project_dir)
        self._load_into_editor()
        self._write(message)

    def _write(self, message: str) -> None:
        self.query_one("#log", RichLog).write(message)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        actions = {
            "create": self.action_create,
            "open": self.action_open,
            "save": self.action_save,
            "generate": self.action_generate,
            "compile": self.action_compile,
            "runtime": self.action_runtime,
            "propose": self.action_propose,
            "apply-proposal": self.action_apply_proposal,
            "add-asset": self.action_add_asset,
            "release": self.action_release,
            "map-pattern": lambda: self.action_fill("pattern"),
            "map-clear": lambda: self.action_fill("."),
            "map-resize": self.action_resize,
            "map-rename": self.action_rename,
            "entity-apply": self.action_apply_entity,
            "entity-remove": self.action_remove_entity,
            "entity-add": self.action_add_entity,
        }
        action = actions.get(event.button.id or "")
        if action:
            action()

    def on_select_changed(self, event: Select.Changed) -> None:
        if self.project is None:
            return
        if event.select.id == "map-level" and isinstance(event.value, int):
            self.level_index = event.value
            self.cursor = (0, 0)
            self._refresh_map()
        elif event.select.id == "entity-id":
            self._refresh_entities()

    def on_key(self, event) -> None:
        """Map editing keys, active only while the Map tab is showing."""
        if self.project is None:
            return
        if self.query_one(TabbedContent).active != "map":
            return
        if isinstance(self.focused, Input):
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
            self._refresh_map()
            event.stop()
        elif event.key == "space":
            self._edit(lambda: editing.toggle_tile(self.project, self.level_index, col, row))
            event.stop()
        elif event.key == "m":
            self.action_move_spawn()
            event.stop()

    def _edit(self, operation) -> None:
        """Run an editing operation, reporting refusals instead of crashing."""
        try:
            self._apply_edit(operation(), "[green]Design updated[/green]")
        except editing.EditError as exc:
            self.notify(str(exc), severity="warning")
        except Exception as exc:
            self.notify(str(exc), severity="error")

    def action_fill(self, tile: str) -> None:
        self._edit(lambda: editing.fill_level(self.project, self.level_index, tile))

    def action_resize(self) -> None:
        width = int(self.query_one("#map-width", Input).value or 0)
        height = int(self.query_one("#map-height", Input).value or 0)
        self._edit(lambda: editing.resize_level(self.project, self.level_index, width, height))

    def action_rename(self) -> None:
        name = self.query_one("#map-name", Input).value
        self._edit(lambda: editing.rename_level(self.project, self.level_index, name))

    def action_move_spawn(self) -> None:
        index = self.query_one("#map-spawn", Select).value
        if not isinstance(index, int) or index < 0:
            self.notify("Choose a spawn to move", severity="warning")
            return
        col, row = self.cursor
        self._edit(
            lambda: editing.move_spawn(self.project, self.level_index, index, col, row)
        )

    def action_apply_entity(self) -> None:
        entity_id = str(self.query_one("#entity-id", Select).value)
        count = int(self.query_one("#entity-count", Input).value or 1)
        speed = int(self.query_one("#entity-speed", Input).value or 1)

        def apply() -> GameProject:
            edited = editing.set_entity_count(self.project, entity_id, count)
            return editing.set_entity_speed(edited, entity_id, speed)

        self._edit(apply)

    def action_remove_entity(self) -> None:
        entity_id = str(self.query_one("#entity-id", Select).value)
        self._edit(lambda: editing.remove_entity(self.project, entity_id))

    def action_add_entity(self) -> None:
        entity_id = self.query_one("#entity-new-id", Input).value.strip()
        role = str(self.query_one("#entity-new-role", Select).value)
        self._edit(lambda: editing.add_entity(self.project, entity_id, role))

    def action_create(self) -> None:
        try:
            title = self.query_one("#new-title", Input).value.strip()
            platform = TargetPlatform(str(self.query_one("#new-platform", Select).value))
            genre = GenreId(str(self.query_one("#new-genre", Select).value))
            scope = ProjectScope(str(self.query_one("#new-scope", Select).value))
            self.project, self.project_dir = self.service.create_project(
                title, platform, genre, scope
            )
            self._load_into_editor()
            self._write(f"[green]Created[/green] {self.project_dir / 'game.yml'}")
            self.notify("Project created")
        except Exception as exc:
            self.notify(str(exc), severity="error")

    def action_open(self) -> None:
        try:
            location = Path(self.query_one("#open-path", Input).value).expanduser().resolve()
            self.project = self.service.open_project(location)
            self.project_dir = location.parent if location.name == "game.yml" else location
            self._load_into_editor()
            self._write(f"[green]Opened[/green] {self.project_dir / 'game.yml'}")
        except Exception as exc:
            self.notify(str(exc), severity="error")

    def action_save(self) -> bool:
        if self.project is None or self.project_dir is None:
            return False
        try:
            document = self.project.model_dump(mode="json")
            document["metadata"]["title"] = self.query_one("#edit-title", Input).value.strip()
            document["gameplay"]["lives"] = int(self.query_one("#edit-lives", Input).value)
            document["gameplay"]["win_score"] = int(self.query_one("#edit-win-score", Input).value)
            document["presentation"]["style"] = self.query_one("#edit-style", Input).value.strip()
            enemy_speed = int(self.query_one("#edit-enemy-speed", Input).value)
            for entity in document["entities"]:
                if entity["role"] == "enemy":
                    entity["speed"] = enemy_speed
            names = [
                name.strip()
                for name in self.query_one("#edit-level-names", Input).value.split(",")
                if name.strip()
            ]
            if len(names) != len(document["levels"]):
                raise ValueError(f"enter exactly {len(document['levels'])} level names")
            for level, name in zip(document["levels"], names):
                level["name"] = name
            candidate = GameProject.model_validate(document)
            path = self.service.save_project(candidate, self.project_dir)
            self.project = candidate
            self._load_into_editor()
            self._write(f"[green]Saved[/green] {path}")
            return True
        except Exception as exc:
            self.notify(str(exc), severity="error")
            return False

    def action_generate(self) -> None:
        if self.project is None or self.project_dir is None:
            return
        try:
            if not self.action_save():
                return
            result = self.service.generate_sources(self.project, self.project_dir)
            self._write(
                f"[green]Generated[/green] {len(result.files)} files in {result.output_dir}"
            )
            self.notify("Sources generated")
        except Exception as exc:
            self.notify(str(exc), severity="error")

    def action_compile(self) -> None:
        if self.project is None or self.project_dir is None:
            return
        try:
            self._write("[yellow]Building with the real target toolchain...[/yellow]")
            result = self.service.build(self.project, self.project_dir)
            if result.success:
                self._write(f"[green]Quality build passed[/green] {result.artifact}")
                self.notify("Build passed")
            else:
                count = result.report.get("unexpected_warning_count", 0)
                self._write(f"[red]Build rejected[/red] unexpected warnings: {count}")
                self.notify("Build rejected; inspect build_report.json", severity="error")
        except Exception as exc:
            self.notify(str(exc), severity="error")

    def action_runtime(self) -> None:
        if self.project is None or self.project_dir is None:
            return
        try:
            self._write("[yellow]Building and running a bounded emulator playtest...[/yellow]")
            report = self.service.runtime_test(self.project, self.project_dir)
            if report["quality_pass"]:
                self._write(
                    f"[green]Runtime passed[/green] {report['adapter']['name']} · "
                    f"boot={report['boot']} · visible={report['non_blank_output']} · "
                    f"transition={report['visual_change']}"
                )
                self.notify("Runtime test passed")
                self.query_one("#release", Button).disabled = False
            else:
                self._write("[red]Runtime rejected[/red] Inspect build/emulator_report.json")
                self.notify("Runtime test rejected", severity="error")
        except Exception as exc:
            self.notify(str(exc), severity="error")

    def action_propose(self) -> None:
        if self.project is None:
            return
        request = self.query_one("#ai-request", Input).value.strip()
        if not request:
            self.notify("Describe the requested design change", severity="warning")
            return
        try:
            config = load_config("config.yml")
            model = config.get("openai", {}).get("model", "gpt-5")
            self.notify("Requesting a structured proposal; this uses the OpenAI API")
            planner = ResponsesProjectPlanner(OpenAI(api_key=load_api_key()), model=model)
            self.pending_proposal = planner.propose(self.project, request)
            preview = self.query_one("#ai-preview", RichLog)
            preview.clear()
            preview.write(proposal_diff(self.pending_proposal))
            self.query_one("#apply-proposal", Button).disabled = False
        except Exception as exc:
            self.pending_proposal = None
            self.query_one("#apply-proposal", Button).disabled = True
            self.notify(str(exc), severity="error")

    def action_apply_proposal(self) -> None:
        if self.project is None or self.project_dir is None or self.pending_proposal is None:
            return
        try:
            self.project = apply_proposal(self.project, self.pending_proposal)
            self.service.save_project(self.project, self.project_dir)
            self.pending_proposal = None
            self.query_one("#apply-proposal", Button).disabled = True
            self._load_into_editor()
            self._write("[green]Reviewed AI proposal applied to game.yml[/green]")
            self.notify("Proposal applied")
        except Exception as exc:
            self.notify(str(exc), severity="error")

    def action_add_asset(self) -> None:
        if self.project is None or self.project_dir is None:
            return
        try:
            source = Path(self.query_one("#asset-path", Input).value)
            asset = self.service.add_asset(self.project, self.project_dir, source)
            self._load_into_editor()
            self._write(f"[green]Imported asset[/green] {asset.id} ({asset.width}x{asset.height})")
            self.notify("Asset imported; target conversion runs during source generation")
        except Exception as exc:
            self.notify(str(exc), severity="error")

    def action_release(self) -> None:
        if self.project is None or self.project_dir is None:
            return
        try:
            archive = self.service.release(self.project, self.project_dir)
            self._write(f"[green]Release exported[/green] {archive}")
            self.notify("Release archive created")
        except Exception as exc:
            self.notify(str(exc), severity="error")


def run_studio(workspace: Path = Path("studio-projects")) -> None:
    StudioApp(workspace).run()
