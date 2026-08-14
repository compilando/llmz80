"""Guided terminal front end for designing, writing and proving a game.

The screen walks one pipeline step at a time. `wizard` decides which step
that is and what doing it would mean; this names the key -- `Enter` does the
step, `→` leaves it behind, `Esc` goes back, `R` repeats a finished one --
and shows the diary underneath, always. There are no per-stage shortcuts any
more: knowing that `ctrl+f` had to be pressed before `ctrl+a`, and that
`ctrl+t` rather than `ctrl+b` was what produced the quality report, was
knowledge the screen demanded and never offered.

Editing (title, brief, style; the map; the entity roster; sprites; a pending
diff) still lives in a panel that opens over the resting screen, one at a
time, so the screen a person leaves running never grows past what they need
to glance at.

The work is done by `StudioService`, `editing`, `screen` and `wizard`;
nothing here decides anything about a design, a project's status or what
comes next, which is what keeps the same operations usable from a script.
"""

from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import Callable, Sequence

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

from . import editing, wizard
from .journal import Journal
from .models import GameProject, TargetPlatform
from .screen import Stage
from .services import StudioService

#: Cell glyphs used by the map editor, keyed by what occupies the cell.
GLYPH_WALL = "▓"
GLYPH_FLOOR = "·"


def _entity_glyph(kind: str) -> str:
    """The map-editor glyph for an occupant of a cell, from its entity's `kind`.

    v4 has no fixed roster of entity roles -- `kind` is free text a design
    coins for itself -- so there is no table to key a glyph off of the way
    `GLYPH_BY_ROLE` (player/enemy/collectible/...) used to. The first letter
    of `kind`, uppercased, is legible enough on the grid and distinguishes
    entities that name themselves differently without Studio needing to know
    what any of them mean; an entity with no `kind` at all (never valid on a
    saved project, but cheap to guard) falls back to "?".
    """
    return kind[0].upper() if kind else "?"


#: One character per `screen.StageState`, plus the one state only the
#: wizard knows about (`skipped`: walked past on purpose, and not coming
#: back). Drawn plain for `status_text`, which tests and scripts read as a
#: string, and wrapped in colour markup only for the widget a person looks at.
STAGE_ICON = {"done": "✓", "pending": "—", "failed": "✗", "skipped": "»"}
STAGE_COLOR = {"done": "green", "pending": "dim", "failed": "red", "skipped": "yellow"}

#: The characters left of the brief preview's one line, before it is cut off
#: with an ellipsis. Chosen to comfortably fit a typical terminal width
#: without depending on the actual rendered width of the box: a fixed budget
#: keeps the preview exactly one line regardless of window size or how long
#: the brief itself is, which is the property that keeps the resting screen
#: from growing.
BRIEF_PREVIEW_LIMIT = 78

#: Every key that opens a panel over the resting screen, and the id of the
#: container each shows. The log is no longer among them: it is the diary,
#: it is half of what this screen says, and a diary you have to press a key
#: to see is a diary nobody reads. It sits below the wizard, always.
PANEL_KEYS = {
    "g": "design",
    "m": "map",
    "e": "entities",
    "s": "sprites",
    "d": "diff",
}
#: Every panel this screen can show, keyed and toggled the same way,
#: including the two the wizard's own first step opens rather than a letter:
#: `create` and `open`.
PANEL_IDS = {
    "design": "panel-design",
    "map": "panel-map",
    "entities": "panel-entities",
    "sprites": "panel-sprites",
    "diff": "panel-diff",
    "create": "panel-create",
    "open": "panel-open",
}

#: Rich markup tags, stripped when a screen message is written to the diary:
#: the file is read in a pager, where `[green]` is noise rather than colour.
_MARKUP = re.compile(r"\[/?[a-z ]+\]")


def _plain(text: str) -> str:
    return _MARKUP.sub("", text).strip()


def render_map(project: GameProject, screen_index: int, cursor: tuple[int, int]) -> str:
    """Draw one screen as markup: terrain, spawns and the edit cursor.

    A module-level function over plain data, so it can be read and tested
    without a running application.
    """
    screen = project.screens[screen_index]
    kinds = {entity.id: entity.kind for entity in project.entities}
    occupants = {
        (spawn.col, spawn.row): _entity_glyph(kinds.get(spawn.entity, ""))
        for spawn in screen.spawns
    }
    solid = editing.solid_char(project)
    lines = []
    for row in range(screen.height):
        cells = []
        for col in range(screen.width):
            glyph = occupants.get(
                (col, row),
                GLYPH_WALL if screen.tiles[row][col] == solid else GLYPH_FLOOR,
            )
            if (col, row) == cursor:
                glyph = f"[reverse]{glyph}[/reverse]"
            cells.append(glyph)
        lines.append("".join(cells))
    return "\n".join(lines)


def render_stage_marks(stages: Sequence[Stage | wizard.Step], *, colour: bool) -> str:
    """One line: every stage's name and its state as a single character.

    `colour` picks Rich markup (for the widget a person reads) or plain text
    (for `status_text`, so a test can search it without stripping markup).
    A pure function over `screen.stage_line`'s own output -- or over
    `wizard.steps`'s, which carries the same two fields plus the `skipped`
    state -- kept separate from the widget for the same reason `render_map`
    is: it can be read and tested without a running application.
    """
    parts = []
    for stage in stages:
        icon = STAGE_ICON[stage.state]
        if colour:
            icon = f"[{STAGE_COLOR[stage.state]}]{icon}[/{STAGE_COLOR[stage.state]}]"
        parts.append(f"{stage.name} {icon}")
    return "  ".join(parts)


def pick_stage_detail(stages: Sequence[Stage | wizard.Step]) -> str:
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


def render_step_head(step: wizard.Step) -> str:
    """The one line that says where in the pipeline the person is standing.

    Counted "de 6" rather than "de 7": the six pipeline stages are the work,
    and step zero -- having a project open at all -- is the precondition for
    any of them, so numbering it 0 keeps the six named steps at the numbers
    `wizard` and the diary already give them.
    """
    return f"Paso {step.number} de 6: {step.name}"


def render_step_summary(step: wizard.Step, *, can_adapt: bool = False) -> str:
    """What this step is for, and which key does it -- the sentence that
    replaces having to know that `ctrl+f` came before `ctrl+a`.

    A step still to do names `Enter` and its own verb, warns when pressing it
    will spend money at an API, and offers `→` only where
    `wizard.can_leave_behind` would actually allow it, so the screen never
    suggests a key that will answer with a refusal. A step already resolved
    names `→` to move on and `R` to do it over, which is the honest pair:
    `Enter` on a done step is `R`'s job, after a confirmation.

    `can_adapt` adds the one key that is not any step's own: `A`, offered
    inside `diseño` and only where research archived a dossier, because
    adapting the design to the researched game is a way of changing the
    design rather than a step after it (see `StudioApp._adapt_step`). It is
    named in both branches on purpose -- `diseño` is normally `done` from
    the moment a project exists (`screen._design_stage` never says
    `pending`), so a key offered only to unresolved steps would be a key
    this step never offered at all.
    """
    parts = [step.summary]
    if can_adapt:
        parts.append("[A] adaptar el diseño a la ficha")
    if step.state in {"done", "skipped"}:
        parts.append("[→] siguiente paso")
        if step.state == "done":
            parts.append("[R] repetir")
        return " · ".join(parts)
    parts.append(f"[Enter] {step.action_label}")
    if step.costs_api:
        parts.append("gasta dinero (API)")
    if wizard.can_leave_behind(step):
        parts.append("[→] omitir")
    return " · ".join(parts)


def _can_adapt(walked: Sequence[wizard.Step], step: wizard.Step) -> bool:
    """Whether adapting the design to the researched game is available now.

    Two conditions, both read off `wizard.steps`'s own single reading of the
    project rather than loading `reference.yml` a second time: the person is
    standing on `diseño` -- adapting *is* changing the design -- and
    `referencia` is `done`, which (see `screen._reference_stage`) means
    exactly that a dossier exists and identified a game. That is precisely
    what `propose_from_reference` needs to have something to propose from;
    an absent dossier, or one that found nothing, leaves it nothing to say.
    """
    if step.name != "diseño":
        return False
    reference = next((walk for walk in walked if walk.name == "referencia"), None)
    return reference is not None and reference.state == "done"


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
    #: Nothing is focused at rest. Textual's default would hand focus to the
    #: first focusable widget it finds -- a field inside a panel that is not
    #: even on screen -- which then swallows the wizard's own keys: `Enter`
    #: submits the hidden Input instead of doing the step. The wizard keys
    #: belong to the screen, so the screen keeps them until a person opens a
    #: panel and deliberately puts the cursor in something.
    AUTO_FOCUS = None
    CSS = """
    #brief { height: auto; }
    #brief-box { height: 3; border: round $primary; margin: 0 1; padding: 0 1; }
    .row { height: 3; }
    .row Label { width: 10; padding: 1 0 0 0; }
    .row Input, .row Select { width: 1fr; }
    #brief-edit-box { height: 8; border: round $primary; margin: 0 0 1 0; }
    #brief-edit-box TextArea { height: 1fr; }
    #create-brief-box { height: 8; border: round $primary; margin: 0 0 1 0; }
    #create-brief-box TextArea { height: 1fr; }
    #wizard-head { height: 1; padding: 0 1; }
    #stage-line { height: 1; padding: 0 1; }
    #wizard-summary { height: 1; padding: 0 1; }
    #stage-detail { height: 1; padding: 0 1; }
    #shortcuts { height: 1; padding: 0 1; background: $boost; }
    .panel { display: none; height: 1fr; padding: 0 1; }
    .panel.open { display: block; }
    #map-grid { height: auto; }
    DataTable { height: auto; max-height: 12; }
    RichLog { height: 1fr; border: round $primary; }
    #workspace-list { height: 1fr; }
    """
    #: One key per thing a person can decide, not one per pipeline stage.
    #: Which stage `Enter` runs is the wizard's answer, not the keyboard's.
    BINDINGS = [
        ("enter", "do", "Hacer"),
        ("right", "advance", "Siguiente paso"),
        ("escape", "back", "Volver"),
        ("r", "repeat", "Repetir"),
        ("q", "quit", "Salir"),
    ]

    def __init__(self, workspace: Path) -> None:
        super().__init__()
        self.workspace = workspace.expanduser().resolve()
        self.service = StudioService.at(self.workspace)
        self.project: GameProject | None = None
        self.project_dir: Path | None = None
        self.screen_index = 0
        self.cursor: tuple[int, int] = (0, 0)
        #: `None` at rest; otherwise one of `PANEL_IDS`'s keys, the single
        #: panel currently shown over the resting screen.
        self.active_panel: str | None = None
        #: Steps the person has already left behind -- done, moved past, or
        #: skipped. Session state on purpose: the diary records the decision,
        #: but having walked past a step is not evidence of work done, and must
        #: not be read back as if it were.
        self.passed: set[str] = set()
        self.journal: Journal | None = None
        self._workspace_paths: dict[str, Path] = {}
        #: `None` until a test sets one directly, which is the injection
        #: point `research_reference`, `propose_from_reference` and
        #: `draw_sprites` are built around: the service takes a
        #: researcher/designer/artist as a parameter rather than building
        #: its own, precisely so a caller -- this screen, a script, or a
        #: test -- can hand it a fake instead of the OpenAI-backed default
        #: each step's method below builds when this stays `None`.
        self.researcher = None
        self.designer = None
        self.artist = None
        #: Set by `_research`/`_draw_sprites` on their first press when
        #: there is something an overwrite would destroy, naming which of
        #: them is waiting; a second press of the *same* action confirms it.
        #: `action_repeat` asks the same way before doing a finished step
        #: over again.
        self._pending_confirm: str | None = None
        #: `(diff, updated_project, refusals)` once `_adapt`'s job
        #: returns, read by `_show_pending_proposal` and consumed by
        #: `_decide_proposal` -- nothing here is saved until a person
        #: presses [y] in the diff panel.
        self._pending_proposal: tuple[str, GameProject, list[str]] | None = None
        #: Assets `_draw_sprites`'s job just registered, read by
        #: `_show_drawn_sprites` once the job finishes.
        self._drawn_sprites: list = []
        #: Whether the design has changed since the diary last recorded a
        #: save. `_apply` is the one path that changes it, so `_apply` is
        #: what sets this; `_save_and_log` clears it. Asked before saving
        #: rather than after, because `store.save` stamps `updated_at` on
        #: every write: once a save has happened the file always differs
        #: from the one before it, and "did anything actually change?" can
        #: no longer be answered by comparing the two.
        self._edited = False
        #: Whether [A] -- adapting the design to the researched game -- is on
        #: offer right now. Decided in `_refresh_wizard`, off the same
        #: reading of the project's evidence that draws the summary naming
        #: the key, so what the screen offers and what the key does cannot
        #: disagree.
        self._adaptable = False

    # --- layout ---------------------------------------------------------

    def _field(self, label: str, widget) -> ComposeResult:
        with Horizontal(classes="row"):
            yield Label(label)
            yield widget

    def compose(self) -> ComposeResult:
        yield Header()
        # The resting screen: identity (Header's title/sub_title), a one-line
        # reminder of the brief, where in the pipeline the person is standing
        # and what doing this step would mean, the seven-step progress line,
        # and -- underneath all of it, never hidden -- the diary.
        with Vertical(id="brief"):
            brief_box = Vertical(
                Static("no project loaded", id="brief-preview", markup=False),
                id="brief-box",
            )
            brief_box.border_title = "Brief"
            yield brief_box
        yield Static("", id="wizard-head")
        yield Static("no project loaded", id="stage-line")
        yield Static("", id="wizard-summary", markup=False)
        yield Static("", id="stage-detail")
        # Only the panels: the five wizard keys are on the Footer, which
        # Textual draws from BINDINGS itself and therefore cannot fall out of
        # step with them the way a second hand-written copy would.
        yield Static(
            "[g] diseño  [m] mapa  [e] entidades  [s] sprites  [d] diff",
            id="shortcuts",
            markup=False,
        )

        # Panels: one at a time, opened by a letter key (design/map/entities/
        # sprites/diff) or by the wizard's own first step (open/create),
        # hidden until then.
        with Vertical(id="panel-design", classes="panel"):
            yield from self._field("Title", Input(value="My Retro Game", id="f-title"))
            brief_edit_box = Vertical(TextArea(id="f-brief"), id="brief-edit-box")
            brief_edit_box.border_title = "Brief"
            yield brief_edit_box
            yield from self._field("Style", Input(id="f-style"))
        with Vertical(id="panel-create", classes="panel"):
            yield Static(
                "New project -- target is fixed once it exists. The brief is "
                "what research reads to identify the game and what the "
                "program writer is told to build; worth writing now."
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
            create_brief_box = Vertical(TextArea(id="f-create-brief"), id="create-brief-box")
            create_brief_box.border_title = "Brief (optional, editable later)"
            yield create_brief_box
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
                    yield Select([("screen 1", 0)], value=0, allow_blank=False, id="f-screen")
                    yield Select([("none", -1)], value=-1, allow_blank=False, id="f-spawn")
        with Vertical(id="panel-entities", classes="panel"):
            yield DataTable(id="entity-table", cursor_type="row")
        with Vertical(id="panel-sprites", classes="panel"):
            # Where art the sprites step generated is looked at before
            # it is compiled -- filled in by `_show_drawn_sprites`.
            yield Static(
                "No sprites drawn yet -- the sprites step draws the art this "
                "project is missing.",
                id="sprites-view",
            )
        with Vertical(id="panel-diff", classes="panel"):
            # Where `_adapt`'s proposal is reviewed and accepted or
            # rejected -- filled in by `_show_pending_proposal`. `markup`
            # off: this shows a model-written diff verbatim, the same reason
            # `#shortcuts` (also literal bracketed text) turns it off.
            yield Static(
                "No proposal yet -- adapting the design to the researched game "
                "is part of the diseño step.",
                id="diff-view",
                markup=False,
            )
        # The diary, below everything and never hidden: what Studio did, when,
        # and how long it took, the same lines `journal` wrote to studio.log.
        # Not focusable, so its own scroll bindings never swallow the arrow
        # key the wizard advances with.
        diary = RichLog(id="log-view", wrap=True, markup=True)
        diary.can_focus = False
        diary.border_title = "Diario"
        yield diary
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#entity-table", DataTable)
        table.add_columns("entity", "kind", "count")
        self.query_one("#map-hint", Static).update(
            "wasd move · space wall · m move spawn · +/- count"
        )
        self._set_panel(None)
        found = len(self.service.store.list_projects())
        self._log(f"Workspace {self.workspace} · {found} projects")
        self._refresh_wizard()

    # --- panels -----------------------------------------------------------

    def _set_panel(self, name: str | None) -> None:
        """Show `name`'s panel over the resting screen, or return to rest.

        Exactly one panel is visible at a time; opening one implicitly closes
        whichever was open, and `None` closes the open panel (if any) back to
        the resting screen -- header, brief, wizard, stage line, shortcuts.
        The diary is not one of these: it stays on screen underneath whatever
        panel is open, so a long job can be watched while its result is read.
        """
        # Leaving the design panel commits what was typed in it. `ctrl+s` was
        # one of the ten keys this change removes, and the design step that
        # will own saving is not built yet; without this, a brief typed here
        # would be lost the moment the panel closed, which is worse than
        # having no key at all.
        if self.active_panel == "design" and name != "design" and self.project is not None:
            self.action_save()
        self.active_panel = name
        self.query_one("#brief", Vertical).display = name is None
        self.query_one("#wizard-head", Static).display = name is None
        self.query_one("#stage-line", Static).display = name is None
        self.query_one("#wizard-summary", Static).display = name is None
        self.query_one("#stage-detail", Static).display = name is None
        self.query_one("#shortcuts", Static).display = name is None
        for key, widget_id in PANEL_IDS.items():
            self.query_one(f"#{widget_id}", Vertical).set_class(key == name, "open")
        # Focus follows the panel, and only where a widget is what a person
        # would be aiming at: the workspace picker is a list to move through
        # and choose from. Everywhere else the screen keeps its own keys --
        # a focused field would eat the letter that closes the panel again.
        if name == "open":
            self._refresh_workspace_list()
            self.query_one("#workspace-list", OptionList).focus()
        else:
            self.set_focus(None)

    def _toggle_panel(self, name: str) -> None:
        self._set_panel(None if self.active_panel == name else name)

    # --- rendering ------------------------------------------------------

    def _log(self, message: str) -> None:
        self.query_one("#log-view", RichLog).write(message)

    #: Last status text, plain (no Rich markup) so it can be read back and
    #: searched by a test or a script without scraping a widget.
    status_text: str = "no project loaded"

    def _ensure_journal(self) -> None:
        """Point the diary at whatever project is open.

        The diary belongs to the project directory, not to the session: open
        another project and the lines must land in *its* studio.log. Adopting
        it here rather than only in `action_open`/`action_create` means any
        caller that sets `project_dir` -- including a test -- gets a diary
        without having to know to ask for one.
        """
        if self.project_dir is None:
            return
        if self.journal is None or self.journal.path.parent != self.project_dir:
            self.journal = Journal.for_project(self.project_dir)

    def _refresh_wizard(self) -> None:
        """Redraw the three things the wizard says, and the detail under them.

        The head names where the person is standing (`Paso 3 de 6: sprites`),
        the strip shows every step's state at a glance, and the summary says
        what this one is for and which key does it -- including its warning
        when pressing that key spends money. `#stage-detail` keeps its old
        job underneath: the one detail worth attention, which is the earliest
        failure's reason, or else the dossier's title.

        `wizard.steps` reads the project's evidence off disk exactly once and
        every line here is drawn from that one reading, so the strip and the
        summary can never disagree about what is done.
        """
        self._ensure_journal()
        walked = wizard.steps(self.project, self.project_dir, self.passed)
        step = wizard.current(self.project, self.project_dir, self.passed)
        self._adaptable = _can_adapt(walked, step)
        head = render_step_head(step)
        strip = render_stage_marks(walked, colour=False)
        summary = render_step_summary(step, can_adapt=self._adaptable)
        detail = pick_stage_detail(walked)
        self.query_one("#wizard-head", Static).update(f"[b]{head}[/b]")
        self.query_one("#stage-line", Static).update(render_stage_marks(walked, colour=True))
        self.query_one("#wizard-summary", Static).update(summary)
        self.query_one("#stage-detail", Static).update(detail)
        self.status_text = "\n".join(part for part in (head, strip, summary, detail) if part)
        if self.project is None:
            self.sub_title = ""
            self.query_one("#brief-preview", Static).update("no project loaded")
            return
        self.sub_title = (
            f"{self.project.metadata.slug} · {self.project.target.platform.value} · "
            f"{len(self.project.screens)} screens"
        )
        self.query_one("#brief-preview", Static).update(brief_preview(self.project.metadata.brief))

    def _refresh(self) -> None:
        if self.project is None:
            return
        project = self.project
        self.query_one("#f-title", Input).value = project.metadata.title
        self.query_one("#f-style", Input).value = project.presentation.style
        brief = self.query_one("#f-brief", TextArea)
        if brief.text != project.metadata.brief:
            brief.text = project.metadata.brief

        screen = project.screens[self.screen_index]
        self.cursor = (
            min(self.cursor[0], screen.width - 1),
            min(self.cursor[1], screen.height - 1),
        )
        self.query_one("#map-grid", Static).update(
            render_map(project, self.screen_index, self.cursor)
        )
        screens = self.query_one("#f-screen", Select)
        screens.set_options([(item.name, index) for index, item in enumerate(project.screens)])
        screens.value = self.screen_index
        kinds = {entity.id: entity.kind for entity in project.entities}
        spawns = self.query_one("#f-spawn", Select)
        spawns.set_options(
            [
                (f"{index}: {spawn.entity} ({kinds.get(spawn.entity, '?')})", index)
                for index, spawn in enumerate(screen.spawns)
            ]
            or [("none", -1)]
        )
        table = self.query_one("#entity-table", DataTable)
        table.clear()
        for entity in project.entities:
            table.add_row(
                entity.id,
                entity.kind,
                str(entity.count),
                key=entity.id,
            )
        self._refresh_wizard()

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
            self._edited = True
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
        wait for the same key to confirm it.
        """
        if self._pending_confirm == action:
            self._pending_confirm = None
            return True
        self._pending_confirm = action
        return False

    def _show_pending_proposal(self) -> None:
        """After `_adapt`'s job returns, show its diff for review.

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
            self.query_one("#diff-view", Static).update("Applied.")
            self._log("[green]Adaptation applied[/green]")
        else:
            self.query_one("#diff-view", Static).update("Left unchanged.")
            self._log("Left unchanged")

    def _show_drawn_sprites(self) -> None:
        """After `_draw_sprites`'s job returns, look at what it drew.

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
        if event.select.id == "f-screen" and isinstance(event.value, int):
            self.screen_index = event.value
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
        # `Esc` is deliberately absent from here: it is bound to
        # `action_back`, and `event.stop()` does not keep this screen's own
        # bindings from firing afterwards -- handling it here as well made
        # one press do the action twice, closing the editor *and* stepping
        # the wizard back a step. Bound once, it happens once, whether a
        # field has focus or not.
        if isinstance(self.focused, self._TEXT_ENTRY):
            return
        if self.active_panel == "map" and self.project is not None:
            screen = self.project.screens[self.screen_index]
            col, row = self.cursor
            moves = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}
            if key in moves:
                step = moves[key]
                self.cursor = (
                    min(max(col + step[0], 0), screen.width - 1),
                    min(max(row + step[1], 0), screen.height - 1),
                )
                self._refresh()
                event.stop()
                return
            if key == "space":
                self._apply(lambda: editing.toggle_tile(self.project, self.screen_index, col, row))
                event.stop()
                return
            if key == "m":
                index = self.query_one("#f-spawn", Select).value
                if isinstance(index, int) and index >= 0:
                    self._apply(
                        lambda: editing.move_spawn(self.project, self.screen_index, index, col, row)
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
        # After the map editor's own keys, which own `a` as "move left"
        # while it is open, and before the panel letters: adapting the
        # design belongs to the `diseño` step, and `_adapt_step` is what
        # decides whether this is the place to ask for it.
        if key == "a":
            self._adapt_step()
            event.stop()
            return
        if key in PANEL_KEYS:
            self._toggle_panel(PANEL_KEYS[key])
            event.stop()

    # --- actions --------------------------------------------------------

    def action_do(self) -> None:
        """Do whatever the current step is for. Leaving it is `action_advance`."""
        step = wizard.current(self.project, self.project_dir, self.passed)
        self._actions()[step.name]()

    def action_advance(self) -> None:
        """Leave the current step behind.

        On a resolved step this is simply moving on, and there is nothing to
        write down: no decision was made. On a pending one it is skipping, the
        diary says so, and `wizard.can_leave_behind` decides whether the
        pipeline can spare it.
        """
        step = wizard.current(self.project, self.project_dir, self.passed)
        if not wizard.can_leave_behind(step):
            self.notify(f"El paso {step.name} no se puede omitir", severity="warning")
            return
        if step.state == "pending" and self.journal is not None:
            self._log(self.journal.write("OMITIR", f"{step.number} {step.name}"))
        # Whatever this step changed is committed before it is left behind:
        # walking on must never be the thing that loses an edit, and the
        # diary says so where there was anything to say.
        self._save_and_log()
        self.passed.add(step.name)
        self._refresh_wizard()

    def action_back(self) -> None:
        """Leave the editor, saving; or step back to look at an earlier step."""
        if self.active_panel is not None:
            self._save_and_log()
            self._set_panel(None)
            self._refresh_wizard()
            return
        self._step_back()

    def _save_and_log(self) -> None:
        """Commit what the open project holds, and write it down if it changed.

        `store.save` archives the previous revision only where the text
        changed, and the diary follows the same rule: a save that saved
        nothing is not an event, and a diary that recorded one every time a
        panel closed would bury the ones that matter.

        The question is asked of `_edited` -- set by `_apply`, the one path
        that changes a design -- rather than by comparing the file with what
        is in memory, because `store.save` stamps `metadata.updated_at` on
        every write: after any save the two agree, and before it they differ
        by a timestamp nobody edited. `_edited` is also what keeps an
        untouched project from being rewritten (and a revision of identical
        content archived) each time a step is left behind.
        """
        if self.project is None or self.project_dir is None or not self._edited:
            return
        self._ensure_journal()
        self.service.save_project(self.project, self.project_dir)
        self._edited = False
        if self.journal is not None:
            self._log(self.journal.write("GUARDAR", f"{self.project.metadata.slug}/game.yml"))

    def _step_back(self) -> None:
        """Move the wizard's cursor back onto the step before this one.

        Going back is removing that step from `passed` rather than undoing
        anything: the work it did is on disk and stays there, and
        `wizard.steps` will read it again and still call it done. What comes
        back is the chance to look at it, and to press `R` to do it over.
        """
        walked = wizard.steps(self.project, self.project_dir, self.passed)
        here = wizard.current(self.project, self.project_dir, self.passed)
        behind = [step for step in walked[: here.number] if step.name in self.passed]
        if not behind:
            self.notify("Ya estás en el primer paso", severity="warning")
            return
        self.passed.discard(behind[-1].name)
        self._refresh_wizard()

    def action_repeat(self) -> None:
        """Do a finished step again, after asking.

        `Enter` on a done step does it again only through here: without this,
        stepping back with `Esc` would leave the person looking at a finished
        step unable to touch it. The confirmation is the one
        `research_reference` and `draw_sprites` already ask before overwriting.
        """
        step = wizard.current(self.project, self.project_dir, self.passed)
        if step.state != "done":
            self.notify("Ese paso no está hecho todavía", severity="warning")
            return
        if not self._confirmed(f"repeat:{step.name}"):
            self.notify(f"Pulsa R otra vez para rehacer {step.name}", severity="warning")
            return
        # The step's own guard asks the same question before overwriting what
        # is already there, and this was the answer: arm it, so one decision
        # costs one confirmation rather than two.
        self._pending_confirm = step.name
        self._actions()[step.name]()

    def _actions(self) -> dict[str, Callable[[], None]]:
        """One entry per step, holding the methods that used to be reachable by
        a ctrl-binding. The wizard decides which one runs; no key names any of
        them any more."""
        return {
            "proyecto": self._open_project_step,
            "referencia": self._research,
            "diseño": self._edit_design,
            "sprites": self._draw_sprites,
            "programa": self._write,
            "gates": self._test,
            "release": self._release,
        }

    def _open_project_step(self) -> None:
        """Step 0: pick a project out of the workspace, or start one.

        A workspace with projects in it shows the picker; an empty one shows
        the creation panel straight away, because an empty list is no answer
        to "choose a project" and making someone press one more key to be
        told so wastes the time of exactly the person who has least idea
        what to press.

        Both paths end in `action_open`/`action_create`, which point the
        diary at the project's own directory, write `ABRIR` in it, and put
        `proyecto` in `passed`. That last part is what actually lets the
        wizard move: `wizard.current` returns the first step *not left
        behind*, so a project that is open but whose step nobody marked
        would leave the wizard standing on step 0 forever.
        """
        self._set_panel("open" if self.service.store.list_projects() else "create")

    def _edit_design(self) -> None:
        """Step 2: review and adjust the design, in the map editor.

        The map is the largest part of what reviewing a design means by
        hand, and it is the panel `Esc` now saves out of (`action_back`), so
        a wall painted here is on disk before the wizard moves on. The two
        smaller parts have their own letters on the shortcuts line -- `e`
        for the entity roster, `g` for title/brief/style -- and `A`, offered
        by this step's own summary once a dossier exists, adapts the whole
        design to the researched game in one reviewable diff.
        """
        self._set_panel("map")
        if self.project is not None:
            self._refresh()

    def _adapt_step(self) -> None:
        """`A`: propose the adaptation of the design to the researched game.

        Part of the `diseño` step rather than a step of its own. Adapting is
        one of the ways a design changes, and a step of its own would need
        evidence on disk of "I already adapted" for `wizard.steps` to read --
        which nothing writes, and which `reference.yml`'s presence certainly
        is not: it says a game was researched, not that its design was ever
        taken up.

        Outside that step, or with no dossier to adapt to, this says so
        rather than doing nothing silently: `A` is a key the summary only
        offers where it works, so pressing it elsewhere is a question worth
        an answer.
        """
        if self._pending_proposal is not None:
            # A proposal is already on the table and costs nothing more to
            # decide; asking for another would spend money at the API to
            # replace an answer nobody has read yet.
            self.notify(
                "Hay una propuesta sin decidir: [y] aplicarla, [n] descartarla",
                severity="warning",
            )
            return
        if not self._adaptable:
            self.notify(
                "Adaptar el diseño a la ficha sólo se puede en el paso diseño, "
                "y con una ficha que haya identificado un juego",
                severity="warning",
            )
            return
        self._adapt()

    def action_create(self) -> None:
        """Create the project, then -- like
        `llmz80 project new`'s own trailing BRIEF argument -- apply
        whatever brief was written in the creation panel through the same
        `editing.rename_project` `action_save` uses, so this screen is at
        least as capable as the command line at asking for the one field
        that matters most and is easiest to forget.
        """
        try:
            title = self.query_one("#f-title", Input).value.strip()
            self.project, self.project_dir = self.service.create_project(
                title,
                TargetPlatform(str(self.query_one("#f-target", Select).value)),
            )
            brief = self.query_one("#f-create-brief", TextArea).text.strip()
            if brief:
                self.project = editing.rename_project(self.project, title, brief=brief)
                self.service.save_project(self.project, self.project_dir)
            self.screen_index, self.cursor = 0, (0, 0)
            # Step 0 is behind us the moment a project exists: `current` is
            # the first step *not left behind*, so without this the wizard
            # would go on offering "choose a project" to someone who just
            # made one.
            self.passed = {"proyecto"}
            self.journal = Journal.for_project(self.project_dir)
            self._edited = False
            self._refresh()
            self._log(self.journal.write("ABRIR", f"creado {self.project_dir}"))
            self._log(f"[green]Created[/green] {self.project_dir / 'game.yml'}")
        except Exception as exc:
            self.notify(str(exc), severity="error")

    def action_open(self, path: str) -> None:
        try:
            location = Path(path).expanduser().resolve()
            self.project = self.service.open_project(location)
            self.project_dir = location.parent if location.name == "game.yml" else location
            self.screen_index, self.cursor = 0, (0, 0)
            #: Same as `action_create`: having a project *is* step 0, and the
            #: diary belongs to the project just opened, not to the one
            #: before it.
            self.passed = {"proyecto"}
            self.journal = Journal.for_project(self.project_dir)
            self._edited = False
            self._refresh()
            self._log(self.journal.write("ABRIR", f"abierto {self.project_dir}"))
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
                style=self.query_one("#f-style", Input).value.strip(),
                brief=self.query_one("#f-brief", TextArea).text.strip(),
            )
        )
        self._log("[green]Saved[/green]")

    def _research(self) -> None:
        """The `referencia` step: research the real game the brief names,
        archiving reference.yml.

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
        step = wizard.current(self.project, self.project_dir, self.passed)
        try:
            existing = self.service.reference(self.project_dir)
        except ValueError as exc:
            self.notify(str(exc), severity="error")
            self.notify(
                "Fix or remove reference.yml before researching again.",
                severity="warning",
            )
            return
        if existing is not None and not self._confirmed(step.name):
            self.notify(
                "An archived dossier already exists: "
                f"{existing.title or '(unidentified)'}. Press Enter again to replace it.",
                severity="warning",
            )
            return

        project, directory = self.project, self.project_dir

        def job() -> tuple[bool, str]:
            researcher = self.researcher
            if researcher is None:
                from ..cli import _openai_client_and_model
                from .reference import ResponsesReferenceResearcher

                client, model = _openai_client_and_model()
                researcher = ResponsesReferenceResearcher(client, model=model)
            dossier = self.service.research_reference(project, directory, researcher)
            if not dossier.identified:
                # Not a failure: an archived "nothing was found" is a real
                # answer, and the step is done -- the design keeps its typology.
                return True, "No game was identified. The design keeps its typology."
            known = [part for part in (dossier.publisher, str(dossier.year or "")) if part]
            on_publisher = f" ({', '.join(known)})" if known else ""
            return True, (
                f"[green]{dossier.title}{on_publisher}[/green] · "
                f"{len(dossier.sources)} source(s). See the stage line for referencia."
            )

        self._run("Researching with the OpenAI API; this searches the web", job)

    def _adapt(self) -> None:
        """Propose an adaptation to the researched game, and open the diff
        panel to review it.

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

        def job() -> tuple[bool, str]:
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
            return True, "\n".join(lines)

        self._run(
            "Proposing an adaptation with the OpenAI API",
            job,
            on_finished=self._show_pending_proposal,
            # A proposal is not the design step finished: nothing is applied
            # until [y], and the person may well go on editing afterwards.
            leaves_behind=False,
        )

    def _draw_sprites(self) -> None:
        """The `sprites` step: draw the art this project is missing, and
        register each result as an asset.

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
        needed = sorted({entity.sprite or entity.id for entity in self.project.entities})
        existing = [sprite_id for sprite_id in needed if sprite_id in have]
        if existing and not self._confirmed("sprites"):
            self.notify(
                "Sprite art already exists for: "
                + ", ".join(existing)
                + ". Press Enter again to redraw it, overwriting the existing art.",
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
            # `model_copy`, not `model_validate` or a plain assignment,
            # deliberately skips the structural check tying an entity's
            # sprite to a declared asset: for the instant between evicting
            # the old art here and `draw_sprites` registering its
            # replacement below, no asset declares this id at all, which
            # the full validator would refuse. That gap lives only in
            # memory and is never saved -- `draw_sprites`'s own `add_asset`
            # call is what next writes to disk, once a fresh asset closes it.
            self.project = self.project.model_copy(update={"assets": remaining})

        self._drawn_sprites = []
        project, directory = self.project, self.project_dir
        progress = self._progress()

        def job() -> tuple[bool, str]:
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
            drawn = self.service.draw_sprites(project, directory, artist, on_progress=progress)
            self._drawn_sprites = drawn
            if not drawn:
                return True, "Every entity already has sprite art."
            return True, "[green]Drawn[/green] " + ", ".join(asset.id for asset in drawn)

        self._run(
            "Drawing sprites with OpenAI's image API",
            job,
            on_finished=self._show_drawn_sprites,
        )

    def _write(self) -> None:
        """The `programa` step: have the program written and repaired against
        the compiler. This spends money, so it says so first."""
        progress = self._progress()

        def job() -> tuple[bool, str]:
            from ..cli import _openai_client_and_model
            from .generator import ResponsesProgramWriter

            client, model = _openai_client_and_model()
            writer = ResponsesProgramWriter(client, model=model)
            report = self.service.write_program(
                self.project, self.project_dir, writer, on_progress=progress
            )
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
            return bool(report["accepted"]), "\n".join(lines)

        self._run("Writing the program with the OpenAI API", job)

    def _progress(self) -> Callable[[str], None] | None:
        """The callback the slow services narrate themselves through.

        Every line goes through `Journal.note`, which writes it to studio.log
        and hands back the very string that is then put on screen: what a
        person watches a long job say and what the file remembers it saying
        are the same characters, not two renderings of one event.

        The job runs on a thread, so the screen half is handed back to the UI
        task rather than touched from there -- the same rule `_background`
        follows for the result.
        """
        journal = self.journal
        if journal is None:
            return None

        def say(text: str) -> None:
            line = journal.note(text)
            try:
                self.call_from_thread(self._log, line)
            except Exception:
                self._log(line)

        return say

    def _run(self, label: str, job, *, on_finished=None, leaves_behind: bool = True) -> None:
        """Run a slow job off the UI thread and report it as it finishes.

        Building takes seconds and a runtime test takes tens of them. Run on the
        UI thread they freeze the app so completely that even the "working"
        line never appears, which reads as the command doing nothing at all.

        `job` returns `(ok, message)`: the message is what goes on screen, and
        `ok` is what the wizard acts on -- a step that failed is not added to
        `passed`, so the screen stays standing on the problem instead of
        walking past it. The diary is opened here with `Journal.start` and
        closed in `_background` with `Journal.finish`, which is what gives
        every piece of work a duration.

        `on_finished`, when given, runs after the job's message has already
        been logged and the wizard redrawn -- adapt and draw-sprites use it to
        open the panel their result belongs in (diff, sprites respectively)
        without teaching this generic runner anything about either.

        `leaves_behind` is what tells a step's own work apart from work done
        *within* a step: `_adapt` runs inside `diseño` and only produces a
        diff for someone to accept or discard, so finishing it must not walk
        the wizard past the very step whose result is still on the table.
        """
        if self.project is None or self.project_dir is None:
            self.notify("Create or open a project first", severity="warning")
            return
        self._ensure_journal()
        step = wizard.current(self.project, self.project_dir, self.passed)
        assert self.journal is not None
        token = self.journal.start(f"{step.number} {step.name} — {label}")
        self._log(token.line)
        self._busy(label)
        self._background(job, label, step.name, token, on_finished, leaves_behind)

    @work(exclusive=True)
    async def _background(
        self, job, label: str, step: str, token, on_finished=None, leaves_behind: bool = True
    ) -> None:
        """Await the job on a thread, then update from the UI task itself.

        Handing the result back through the event loop rather than across
        threads keeps every widget touched from the task that owns it.

        A job that raised, or that reported a failure of its own, closes the
        diary entry as failed, writes down why, and leaves the step where it
        is: the wizard goes on pointing at it, which is the difference between
        stopping where the problem is and carrying on past it.
        """
        try:
            ok, message = await asyncio.to_thread(job)
            reason = "" if ok else _plain(message)
        except Exception as exc:
            ok, message, reason = False, f"[red]{exc}[/red]", str(exc)
            self.notify(str(exc), severity="error")
        self._log(message)
        if self.journal is not None:
            self._log(self.journal.finish(token, ok=ok))
            if not ok:
                self._log(self.journal.write("ERROR", f"{step}: {reason}"))
        if ok and leaves_behind:
            self.passed.add(step)
        self._finished(label)
        if on_finished is not None:
            on_finished()

    def _busy(self, label: str) -> None:
        text = f"{label}... (the interface stays usable)"
        self.status_text = text
        self.query_one("#stage-detail", Static).update(f"[yellow]{text}[/yellow]")

    def _finished(self, label: str) -> None:
        self._refresh_wizard()

    def _test(self) -> None:
        """The `gates` step: build, run in the emulator, and report the gates.

        There is no build-only step: `runtime_test` compiles before it runs,
        and it is the only thing that writes studio_quality_report.json --
        building alone was a shortcut, never a stage of the pipeline.
        """
        progress = self._progress()

        def work() -> tuple[bool, str]:
            report = self.service.runtime_test(self.project, self.project_dir, on_progress=progress)
            acceptance = report.get("acceptance") or {}
            lines = [
                (
                    "[green]Runtime passed[/green]"
                    if report["quality_pass"]
                    else "[red]Runtime rejected[/red]"
                )
            ]
            for scenario in acceptance.get("scenarios") or []:
                if isinstance(scenario, dict):
                    mark = "ok" if scenario["passed"] else "FAILED"
                    lines.append(f"  {scenario['id']}: {mark} {scenario['mismatches'] or ''}")
            return bool(report["quality_pass"]), "\n".join(lines)

        self._run("Building and running", work)

    def _release(self) -> None:
        def work() -> tuple[bool, str]:
            archive = self.service.release(self.project, self.project_dir)
            return True, f"[green]Released[/green] {archive}"

        self._run("Exporting", work)


def run_studio(workspace: Path = Path("studio-projects")) -> None:
    StudioApp(workspace).run()
