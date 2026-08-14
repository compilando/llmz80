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

The work is done by `StudioService`, `editing`, `screen` and `wizard`, and
the lines this screen shows are composed by `render`, which is pure text over
plain data; nothing here decides anything about a design, a project's status
or what comes next, which is what keeps the same operations usable from a
script.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Callable, Sequence

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
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
from .render import (
    _plain,
    _summary,
    brief_preview,
    pick_stage_detail,
    render_map,
    render_stage_marks,
    render_step_head,
    render_step_summary,
    render_tile_legend,
)
from .services import StudioService


#: Every key that opens a panel over the resting screen, and the id of the
#: container each shows. The log is no longer among them: it is the diary,
#: it is half of what this screen says, and a diary you have to press a key
#: to see is a diary nobody reads. It sits below the wizard, always, and
#: everything written into it after mount goes through `Journal`, so the
#: panel and `studio.log` cannot drift into telling different stories.
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

#: The workspace picker's own first entry, and the id it answers to.
#: Creating a project used to hang off `ctrl+n`, and when the ten shortcuts
#: went it survived only as the panel `_open_project_step` opens *instead of*
#: the picker when the workspace is empty -- which meant that from the second
#: project onwards there was no way to start one at all without leaving for
#: the command line. A lost feature, not a lost key. It lives here now, where
#: choosing a project already lives.
NEW_PROJECT_ID = "new"
NEW_PROJECT_LABEL = "＋ new project…"

#: The steps whose own action asks before overwriting what is already on
#: disk (`reference.yml`, existing sprite art). `action_repeat` pre-answers
#: that question, and only these can hear the answer.
_CONFIRMING_STEPS = frozenset({"referencia", "sprites"})


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
    /* The creation panel is the one panel that must fit a whole form on the
       smallest terminal anybody still uses. `1fr` split it with the diary and
       pushed its Create button off the bottom of an 80x24 screen: the only
       control that starts a project was invisible on the only screen a person
       new to Studio is likely to be looking at. `auto` gives it exactly the
       rows its four fields need and leaves the rest to the diary. */
    #panel-create { height: auto; }
    #create-help { height: auto; padding: 0 0 1 0; }
    /* Same reason as the creation panel: an equal split with the diary is
       fine for a list, and wrong for anything a person has to read all of.
       The design panel's Style field and the map editor's grid both sat
       below the fold of an 80x24 terminal. */
    #panel-design { height: auto; }
    #panel-map { height: auto; }
    #panel-map Horizontal { height: auto; }
    #panel-map Vertical { height: auto; }
    #design-help { height: auto; padding: 0 0 1 0; }
    #map-hint { height: auto; padding: 0 0 1 0; }
    /* Wraps rather than growing the panel sideways: a design may declare up
       to 32 tiles, and the legend is the one line here whose length is the
       design's business rather than Studio's. */
    #tile-legend { height: auto; }
    /* The grid and its legend get the room; the two selects need a fixed,
       small column and were taking half the panel -- which on an 80-column
       terminal wrapped the legend of a three-tile design onto three rows. */
    #panel-map #map-column { width: 1fr; }
    #panel-map #map-side { width: 24; }
    #wizard-head { height: 1; padding: 0 1; }
    #stage-line { height: 1; padding: 0 1; }
    /* The one line that must never be cut: it is where the keys are named.
       Fixed at `height: 1` it fitted 120 columns and silently dropped
       `[→] skip` and the `spends money (API)` warning off the right-hand
       edge of an 80-column terminal -- hiding the key that walks past a step
       that spends money, on the narrowest screen. `auto` lets it take a
       second row where it needs one; it still cannot grow with a project,
       because every word in it comes from `wizard`'s own fixed vocabulary. */
    #wizard-summary { height: auto; padding: 0 1; }
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
    #:
    #: These are the *resting screen's* keys, and `check_action` is what keeps
    #: them there: with a panel open they are switched off, so `→` cannot walk
    #: the wizard past steps nobody has seen while the editor covers them.
    #: Textual reads the same `check_action` when it draws the Footer, so the
    #: bar and the keyboard cannot disagree about what is live -- which is the
    #: whole point of gating them there rather than with a guard inside each
    #: action.
    #:
    #: `R` is bound twice on purpose. Textual delivers Shift+R as the key
    #: `"R"`, which the `"r"` binding does not match, so the screen offered
    #: `[R] repeat` and answered only the lowercase one, silently. The second
    #: binding is hidden: one row in the Footer, two keys that reach it.
    BINDINGS = [
        ("enter", "do", "Do it"),
        ("right", "advance", "Next step"),
        ("escape", "back", "Back"),
        ("r", "repeat", "Repeat"),
        Binding("R", "repeat", "Repeat", show=False),
        ("q", "quit", "Quit"),
    ]

    #: The actions this screen's own bindings name. `check_action` is asked
    #: about *every* action Textual can reach, including its own `focus_next`,
    #: `focus_previous` and `command_palette`, so it has to know which ones are
    #: its business: answering for all of them switched `Tab` off inside the
    #: creation panel, which is the one place `Tab` is the way between fields.
    WIZARD_ACTIONS = frozenset({"do", "advance", "back", "repeat", "quit"})

    #: The wizard actions that survive a panel being open. `back` is how a
    #: panel is left at all, and quitting must never need a panel closed first.
    PANEL_SAFE_ACTIONS = frozenset({"back", "quit"})

    def __init__(self, workspace: Path) -> None:
        super().__init__()
        self.workspace = workspace.expanduser().resolve()
        self.service = StudioService.at(self.workspace)
        self.project: GameProject | None = None
        self.project_dir: Path | None = None
        self.screen_index = 0
        self.cursor: tuple[int, int] = (0, 0)
        #: The character `space` paints with, one of the tiles the open design
        #: declares. Empty until a project is loaded; `_refresh` picks the
        #: design's solid tile then, and puts it back if a project is opened
        #: (or adapted) whose alphabet no longer contains what was selected.
        self.tile_char = ""
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
        #: The step `_pending_confirm` was armed on. A confirmation is an
        #: answer to a question this step asked, and walking to another step
        #: abandons the question; without this, arming `sprites` and coming
        #: back to it later ("Enter, →, Esc, Enter") spent money and destroyed
        #: existing art on a single press, because the second press was read
        #: as confirming the first.
        self._confirm_step: str | None = None
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
        #: The design as it was when the diary last recorded it -- what a
        #: `SAVE` line is compared against to say what the save actually
        #: saved. A deep copy, because `store.save` stamps `updated_at` on
        #: the very object it is handed and a shared reference would be
        #: quietly rewritten under this one.
        self._saved: GameProject | None = None
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
            "[g] design  [m] map  [e] entities  [s] sprites  [d] diff",
            id="shortcuts",
            markup=False,
        )

        # Panels: one at a time, opened by a letter key (design/map/entities/
        # sprites/diff) or by the wizard's own first step (open/create),
        # hidden until then.
        with Vertical(id="panel-design", classes="panel"):
            # Third panel to need this, and for the third time the same
            # reason: with nothing focused and no key named, typing here
            # closed panels instead of writing -- `g` shut this one, `s`
            # opened sprites -- so the brief could not be edited without
            # guessing `Tab`.
            yield Static("", id="design-help", markup=False)
            yield from self._field("Title", Input(value="My Retro Game", id="f-title"))
            brief_edit_box = Vertical(TextArea(id="f-brief"), id="brief-edit-box")
            brief_edit_box.border_title = "Brief"
            yield brief_edit_box
            yield from self._field("Style", Input(id="f-style"))
        with Vertical(id="panel-create", classes="panel"):
            # This help names the way *in*, not only the way out. It used to
            # describe the brief and then say only that Esc closes the panel,
            # which left the one question a newcomer actually has -- "how do I
            # create it?" -- answered nowhere on the screen.
            yield Static(
                "New project. The brief is what research reads to identify the "
                "game and what the program writer is told to build; the target "
                "is fixed once the project exists. [Enter] creates it · [Tab] "
                "moves between fields · [Esc] closes without creating anything.",
                id="create-help",
                markup=False,
            )
            yield from self._field("Title", Input(value="My Retro Game", id="f-create-title"))
            yield from self._field(
                "Target",
                Select(
                    [("ZX Spectrum", "spectrum"), ("Amstrad CPC", "amstrad_cpc")],
                    value="spectrum",
                    allow_blank=False,
                    id="f-target",
                ),
            )
            # An `Input`, not the `TextArea` this was: `Enter` inside a text
            # area inserts a newline, so the one key the wizard teaches did
            # nothing here and the only way on was a `Tab` nothing named. A
            # single line is enough to say what a game is at the moment of
            # creating it, and the design panel keeps the full text area for
            # writing the brief properly afterwards.
            yield from self._field("Brief", Input(id="f-create-brief"))
            yield Button("Create", id="create-confirm", variant="primary")
        with Vertical(id="panel-open", classes="panel"):
            yield Static(
                "Open a project from the workspace, or start a new one. " "Esc closes this panel.",
                id="open-help",
            )
            yield OptionList(id="workspace-list")
        with Vertical(id="panel-map", classes="panel"):
            with Horizontal():
                with Vertical(id="map-column"):
                    # Above the grid, not below it. Under a 14-row map the
                    # hint fell off the bottom of an 80x24 screen and the
                    # editor opened saying nothing at all about how to work
                    # it or how to get out of it.
                    yield Static("", id="map-hint", markup=False)
                    # The legend, between the keys and the grid: a glyph is
                    # only editable if you can name the tile it stands for.
                    yield Static("", id="tile-legend", markup=True)
                    yield Static("No project loaded.", id="map-grid", markup=True)
                with Vertical(id="map-side"):
                    yield Select([("screen 1", 0)], value=0, allow_blank=False, id="f-screen")
                    yield Select([("none", -1)], value=-1, allow_blank=False, id="f-spawn")
        with Vertical(id="panel-entities", classes="panel"):
            yield DataTable(id="entity-table", cursor_type="row")
        with Vertical(id="panel-sprites", classes="panel"):
            # Where art the sprites step generated is looked at before
            # it is compiled -- filled in by `_show_drawn_sprites`.
            yield Static(
                "No sprites drawn yet -- the Sprites step draws the art this "
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
                "is part of the Design step.",
                id="diff-view",
                markup=False,
            )
        # The diary, below everything and never hidden: what Studio did, when,
        # and how long it took, the same lines `journal` wrote to studio.log.
        # Not focusable, so its own scroll bindings never swallow the arrow
        # key the wizard advances with.
        diary = RichLog(id="log-view", wrap=True, markup=True)
        diary.can_focus = False
        diary.border_title = "Diary"
        yield diary
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#entity-table", DataTable)
        table.add_columns("entity", "kind", "count")
        # `esc` is named alongside the editing keys because it is the one
        # that now does something worth knowing about: it saves what was
        # drawn here and returns to the wizard.
        self.query_one("#map-hint", Static).update(
            "arrows or wasd move · [t] picks the tile · space paints · "
            "m moves the spawn · +/- count · [Esc] saves and returns"
        )
        self.query_one("#design-help", Static).update(
            "Title, brief and style. The brief is the first thing research "
            "and whoever writes the program read. "
            "[Tab] changes field · [Esc] saves and returns"
        )
        self._set_panel(None)
        # The one line in this panel that is not a diary line, and the only
        # one that cannot be: a diary belongs to a project directory, and at
        # mount there is no project to own it. Everything the screen says from
        # here on goes through `Journal`, so what is read in the panel and what
        # `studio.log` keeps are the same lines -- with this single, stated
        # exception, which is about the workspace rather than about any project
        # in it.
        found = len(self.service.store.list_projects())
        self._log(f"Workspace {self.workspace} · {found} projects")
        self._refresh_wizard()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Whether a wizard key is live right now. Textual asks before firing
        it *and* before drawing it in the Footer, which is what collapses two
        of the three places a key used to be described into one.

        A panel is a mode, and in a mode its own keys rule. `→` stayed bound
        while the map editor covered the screen, so a press meant for the
        cursor walked the wizard past steps the person could not even see and
        wrote `SKIP` for a decision nobody made. Returning `False` (rather
        than `None`) also takes the key out of the Footer, so the bar stops
        promising what the keyboard will not do.
        """
        if action not in self.WIZARD_ACTIONS:
            return True
        if self.active_panel is None:
            return True
        return action in self.PANEL_SAFE_ACTIONS

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
        # The cursor starts where the work starts. Left unfocused, a panel
        # could only be worked by first guessing `Tab`, a key the wizard never
        # names -- and worse than useless in the meantime, since the letters a
        # person typed were read as panel keys and closed the panel under them.
        # Everywhere a widget is what someone would be aiming at, it gets the
        # focus; `map`, `sprites` and `diff` keep the screen's own keys,
        # because what a person aims at there is the screen itself.
        focus_first = {
            "open": "#workspace-list",
            "create": "#f-create-title",
            "design": "#f-title",
            "entities": "#entity-table",
        }
        if name == "open":
            self._refresh_workspace_list()
        target = focus_first.get(name or "")
        if target is not None:
            self.query_one(target).focus()
        else:
            self.set_focus(None)
        # `check_action` answers off `active_panel`, and Textual caches what
        # it answered: without this the Footer goes on offering the keys a
        # panel has just switched off.
        self.refresh_bindings()

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

        The head names where the person is standing (`Step 3 of 6: sprites`),
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
        # A pending confirmation belongs to the step that asked for it. This
        # is the one place every move between steps passes through, which is
        # why the rule lives here rather than in each of `action_advance`,
        # `_step_back` and `_background`.
        if self._confirm_step != step.name:
            self._pending_confirm = None
            self._confirm_step = step.name
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
        # The paint selection belongs to the design that declared it: a
        # project opened (or adapted) into a different alphabet must not leave
        # `space` painting a character this design does not have, which
        # `editing.set_tile` would refuse on every press.
        if self.tile_char not in {tile.char for tile in project.tiles}:
            self.tile_char = editing.solid_char(project)
        self.query_one("#map-grid", Static).update(
            render_map(project, self.screen_index, self.cursor)
        )
        self.query_one("#tile-legend", Static).update(render_tile_legend(project, self.tile_char))
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
        """Everything step 0 can do, in one list: start a project, or open one.

        `＋ nuevo proyecto…` comes first and is always there, so an empty
        workspace is the same list with one entry rather than a rule of its
        own, and a workspace with projects in it can still start another.
        The highlight starts on the first *project* where there is one --
        opening what already exists is the likelier answer, and creating is
        one key away either way.
        """
        listing = self.query_one("#workspace-list", OptionList)
        listing.clear_options()
        projects = self.service.store.list_projects()
        self._workspace_paths = {str(index): path for index, path in enumerate(projects)}
        listing.add_option(Option(NEW_PROJECT_LABEL, id=NEW_PROJECT_ID))
        if not projects:
            listing.add_option(Option("(no projects in this workspace yet)", id="none"))
            return
        for index, path in enumerate(projects):
            listing.add_option(Option(path.name, id=str(index)))
        listing.highlighted = 1

    def _apply(self, operation) -> None:
        """Run an editing operation, reporting refusals instead of crashing."""
        # The design as it stands before this edit, where nothing has recorded
        # one yet. `action_create`/`action_open` set it for anybody arriving
        # through the screen; this covers the caller -- a script, a test --
        # that put a project here itself, the same courtesy `_ensure_journal`
        # does for the diary, and it is what lets the `SAVE` line say what
        # the edit changed rather than only which file it went to.
        if self._saved is None and self.project is not None:
            self._saved = self.project.model_copy(deep=True)
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
        self._confirm_step = wizard.current(self.project, self.project_dir, self.passed).name
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
        self._ensure_journal()
        if accept:
            self._apply(lambda: updated)
            self.query_one("#diff-view", Static).update("Applied.")
            # Taking up a researched game's design, or refusing to, is a
            # decision about the game -- as much as skipping a step is -- and
            # it used to be said on screen and to no file at all. `_apply` has
            # already marked the project edited, so `_note_saved` writes the
            # `SAVE` that follows this.
            if self.journal is not None:
                self._log(self.journal.note("adaptation applied"))
            self._note_saved()
        else:
            self.query_one("#diff-view", Static).update("Left unchanged.")
            if self.journal is not None:
                self._log(self.journal.note("adaptation discarded"))

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

    def _cycle_tile(self) -> None:
        """`t`: select the next tile the design declares, wrapping round.

        In declaration order, which is the order the legend prints and the
        order `game.yml` holds -- so the key and the line above the grid agree
        about what "next" means.
        """
        if self.project is None:
            return
        chars = [tile.char for tile in self.project.tiles]
        here = chars.index(self.tile_char) if self.tile_char in chars else -1
        self.tile_char = chars[(here + 1) % len(chars)]
        self._refresh()

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

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """`Enter` in any field of the creation panel creates the project.

        The button stays -- it is what a mouse aims at, and what says the panel
        can be finished at all -- but it is no longer the only way through.
        `Enter` is the key the wizard teaches on every other step, and the one
        step where it did nothing was the first one anybody meets.

        Guarded on the panel because the design panel's own fields
        (`#f-title`, `#f-style`) submit the same message, and creating a
        second project out of a rename would be a surprising thing for a
        title field to do.
        """
        if self.active_panel != "create":
            return
        self.action_create()
        self._set_panel(None)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if event.option_list.id != "workspace-list":
            return
        if event.option_id == NEW_PROJECT_ID:
            self._set_panel("create")
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
            # The arrows do here what the spec promises they do: move the
            # cursor. They used to reach the wizard's own bindings instead --
            # `→` from inside the editor left a step behind -- and a person
            # following the documentation hit that on the first press.
            moves = {
                "w": (0, -1),
                "s": (0, 1),
                "a": (-1, 0),
                "d": (1, 0),
                "up": (0, -1),
                "down": (0, 1),
                "left": (-1, 0),
                "right": (1, 0),
            }
            if key in moves:
                step = moves[key]
                self.cursor = (
                    min(max(col + step[0], 0), screen.width - 1),
                    min(max(row + step[1], 0), screen.height - 1),
                )
                self._refresh()
                event.stop()
                return
            if key == "t":
                self._cycle_tile()
                event.stop()
                return
            if key == "space":
                # Paints the selected tile, rather than flipping the cell
                # between solid and open as it used to: a design declares its
                # own tiles, and a key that could only reach two of them left
                # every other one unpaintable. Which one is selected is on the
                # legend above the grid, and `t` walks through them.
                self._apply(
                    lambda: editing.set_tile(
                        self.project, self.screen_index, col, row, self.tile_char
                    )
                )
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
        # Both cases: the summary offers `[A]`, and Textual delivers Shift+A
        # as `"A"`, so answering only `"a"` meant the screen named a key it
        # did not have. `"a"` alone reaches here anyway -- the map editor's
        # branch above owns it as "move left" while that panel is open.
        if key in {"a", "A"}:
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
            # `name`, not `title`: the screen translates and the file does
            # not. A diary line is a record, and a record that is written in
            # whatever language the interface happens to speak can neither be
            # searched nor read back beside the lines written before it.
            refusal = f"{step.number} {step.name}: cannot be skipped"
            self.notify(f"The {step.title} step cannot be skipped", severity="warning")
            # A toast lives five seconds. Wanting to walk past this step was a
            # decision the person made and the pipeline denied, and reading the
            # diary the next morning without it would leave the gap between
            # "skipped sprites" and "wrote the program" unexplained.
            self._ensure_journal()
            if self.journal is not None:
                self._log(self.journal.write("WARN", refusal))
            return
        if step.state == "pending" and self.journal is not None:
            self._log(self.journal.write("SKIP", f"{step.number} {step.name}"))
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

    def _note_saved(self) -> None:
        """Write down that the design was committed -- once, only if it was,
        and saying what changed.

        Split out of `_save_and_log` so `action_save`, which saves through
        `_apply` and therefore has nothing left to write to disk, can still
        put the same `SAVE` line in the diary. It used to answer with a
        screen-only "Saved" that the file never heard about, which is how the
        panel and `studio.log` came to be telling different stories.

        The line used to name the file and nothing else, which told the person
        reading it the next morning the one thing they already knew. What
        changed is answered by `editing.describe_changes` against the design
        as the diary last recorded it -- kept in memory rather than read back
        off disk, because the file has already been overwritten by the time
        this runs, and its previous revision is only archived when the text
        differs.
        """
        if self.project is None or not self._edited:
            return
        self._ensure_journal()
        if self.journal is not None:
            detail = f"{self.project.metadata.slug}/game.yml"
            changed = (
                editing.describe_changes(self._saved, self.project)
                if self._saved is not None
                else ""
            )
            if changed:
                detail = f"{detail} — {changed}"
            self._log(self.journal.write("SAVE", detail))
        self._saved = self.project.model_copy(deep=True)
        self._edited = False

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
        self.service.save_project(self.project, self.project_dir)
        self._note_saved()

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
            self.notify("You are already on the first step", severity="warning")
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
            self.notify("That step is not done yet", severity="warning")
            return
        if not self._confirmed(f"repeat:{step.name}"):
            self.notify(f"Press R again to redo {step.title}", severity="warning")
            return
        # The step's own guard asks the same question before overwriting what
        # is already there, and this was the answer: arm it, so one decision
        # costs one confirmation rather than two. Only for the two steps whose
        # action actually asks -- arming one that never consumes it left a
        # live confirmation lying around for whatever asked next.
        if step.name in _CONFIRMING_STEPS:
            self._pending_confirm = step.name
            self._confirm_step = step.name
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

        A workspace with projects in it shows the picker, whose first entry
        starts a new project; an empty one shows the creation panel straight
        away, because there is only one sensible thing to do in an empty
        workspace and making someone press one more key to be told so wastes
        the time of exactly the person who has least idea what to press.
        That shortcut is a courtesy and not the only road: the picker offers
        creating too, or the second project would be unreachable from here.

        Both paths end in `action_open`/`action_create`, which point the
        diary at the project's own directory, write `OPEN` in it, and put
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
                "There is a proposal still undecided: [y] applies it, [n] discards it",
                severity="warning",
            )
            return
        if not self._adaptable:
            self.notify(
                "The design can only be adapted to the dossier on the Design "
                "step, and only with a dossier that identified a game",
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
            title = self.query_one("#f-create-title", Input).value.strip()
            self.project, self.project_dir = self.service.create_project(
                title,
                TargetPlatform(str(self.query_one("#f-target", Select).value)),
            )
            brief = self.query_one("#f-create-brief", Input).value.strip()
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
            # What the next `SAVE` is measured against: a project starts
            # as whatever it was created (or opened) as, so the first save
            # after that reports the edits, not the whole document.
            self._saved = self.project.model_copy(deep=True)
            self._refresh()
            self._log(
                self.journal.write(
                    "OPEN",
                    f"created {self.project_dir / 'game.yml'} · "
                    f"{self.project.target.platform.value}",
                )
            )
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
            self._saved = self.project.model_copy(deep=True)
            self._refresh()
            self._log(
                self.journal.write(
                    "OPEN",
                    f"opened {self.project_dir} · {self.project.target.platform.value}",
                )
            )
        except Exception as exc:
            self.notify(str(exc), severity="error")

    def action_save(self) -> None:
        """Commit the design panel's three fields, if any of them changed.

        Asked before applying, not after. `_apply` marks the project edited
        whatever it was handed, so opening the design panel and closing it
        again without typing anything wrote a second `SAVE` for a save that
        saved nothing -- the very thing `_save_and_log` refuses to do, arrived
        at by another road. `rename_project` applies all three together
        because a rename can be valid only once all three are in place, which
        is also why they are compared together here.
        """
        if self.project is None or self.project_dir is None:
            return
        typed = (
            self.query_one("#f-title", Input).value.strip(),
            self.query_one("#f-style", Input).value.strip(),
            self.query_one("#f-brief", TextArea).text.strip(),
        )
        held = (
            self.project.metadata.title,
            self.project.presentation.style,
            self.project.metadata.brief,
        )
        if typed == held:
            return
        self._apply(
            lambda: editing.rename_project(self.project, typed[0], style=typed[1], brief=typed[2])
        )
        self._note_saved()

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
                f"{len(dossier.sources)} source(s). See the stage line for Reference."
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
        # The id again, for the reason `action_advance` states: this line is
        # the record of a piece of work, and `FIN 3 sprites` has to go on
        # meaning the same thing next year.
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
            # The result goes into the `FIN` line, which is what `finish`'s
            # `text` was always for (`END 3 sprites — ok in 84 s. Drawn ...`).
            # Without it the diary kept every failure -- the `ERROR` line
            # below -- and threw away every success: which game research
            # identified, which sprites were drawn, where the release landed.
            # A diary that only remembers the bad days is not a record.
            self._log(self.journal.finish(token, ok=ok, text=_summary(message)))
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
