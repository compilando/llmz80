"""A window onto a run: where `llmz80 make` has got to, and how it ended.

This screen does no work and decides nothing. The pipeline is one order --
`llmz80 make "an idea"` -- and it runs in whatever terminal it was typed in;
this is the other terminal, the one somebody leaves open to watch. It shows
four things and offers two keys -- `p`, once there is a game, and `q`:

* the project's identity, in the header;
* the six-step strip, read off the evidence the pipeline leaves on disk
  (`wizard.steps`, over `screen.stage_line`), so it advances by itself as the
  run advances -- nothing here is told anything;
* the diary, followed line by line out of `<project>/studio.log` as it is
  written;
* the verdict: what stopped the run, or where the game landed -- and, when
  the game is really on disk, `[p] play`, which starts it in the emulator.

Why follow a file rather than run the work behind the screen, which is what
this module used to do: the file is already the record. `Journal` writes every
line of it and hands the very same string back to whoever asked, so there is
no second rendering of an event to keep in step -- there is one story, and
this reads it. It also decouples the two completely: the run survives the
screen being closed, the screen survives the run crashing, and yesterday's
run can be looked at this morning with the same command. A screen that owned
the jobs could offer none of that, and the wizard that did own them is what
`make` replaced.

Which project: the argument may be a project directory, and then that is the
one; a workspace, and it follows whichever project in it was written to last,
re-asked on every tick, so `llmz80 make` started afterwards in another
terminal is picked up without anything being typed here.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, RichLog, Static

from . import wizard
from .journal import FILENAME as JOURNAL_FILENAME
from .make import artifact_path
from .models import GameProject
from .play import NotPlayable, plan, start
from .render import (
    brief_preview,
    pick_stage_detail,
    render_play_offer,
    render_stage_marks,
    render_verdict,
)
from .store import ProjectStore

#: How often the diary and the evidence on disk are re-read. Half a second is
#: below the threshold at which a person watching a build would call the
#: screen stale, and far above the cost of stat-ing two files and reading the
#: tail of one.
POLL_SECONDS = 0.5


def _launch(artifact: Path) -> None:
    """Start the game, and do not wait for it.

    The screen has to keep reading the diary and answering its own keys while
    somebody plays; waiting here would freeze the viewer behind the emulator
    window, which reads as a crash. `plan` and `start` rather than `play`,
    because `play` reports by printing and there is no terminal to print on:
    what can go wrong arrives as `NotPlayable` instead, and the screen says
    it in its own way.
    """
    start(plan(artifact), wait=False)


class StudioViewer(App[None]):
    """The whole screen. Two keys -- `p` and `q` -- and nothing that writes."""

    TITLE = "LLMZ80 Studio"
    #: Nothing here is focusable and nothing is typed into, so nothing is
    #: focused: Textual would otherwise hand focus to the first widget it
    #: finds and give its scroll keys precedence over the two keys this has.
    AUTO_FOCUS = None
    #: Two keys, and both are decisions rather than work: play the game this
    #: run produced, or stop watching. `p` is offered only while there is an
    #: artifact on disk (`check_action`), because a key that answers with an
    #: error is worse than a key that is not there.
    BINDINGS = [("p", "play", "Play"), ("q", "quit", "Quit")]
    #: Off, so those two keys are really the only two: Textual's palette is a
    #: way of reaching commands, and a screen with no commands offering a way
    #: to search them would be advertising something it does not have.
    ENABLE_COMMAND_PALETTE = False
    CSS = """
    #brief-box { height: 3; border: round $primary; margin: 0 1; padding: 0 1; }
    /* Auto rather than a fixed row: six steps fit one line on 80 columns
       and take two on a narrower terminal, and the strip is the one line that
       must never be cut. It cannot grow with a project either -- every word
       in it comes from `wizard`'s own fixed vocabulary. */
    #stage-line { height: auto; padding: 0 1; }
    #stage-detail { height: 1; padding: 0 1; }
    /* Auto, and the one line here that had to be: the verdict of a finished
       run is the path of the game, and a path is as long as somebody's
       directories are deep. Fixed at one row it was cut at the width of the
       terminal -- "Done · the game is at" and nothing after it, which is the
       one thing this screen exists to say. */
    #verdict { height: auto; padding: 0 1; }
    RichLog { height: 1fr; border: round $primary; }
    """

    def __init__(
        self,
        workspace: Path,
        *,
        poll_seconds: float = POLL_SECONDS,
        launcher: Callable[[Path], None] = _launch,
    ) -> None:
        super().__init__()
        #: How `p` starts the game. Injected for the same reason `make_game`
        #: takes its stages: a test must be able to press the key and read
        #: back what would have been run, without a window opening in front
        #: of whoever is running the suite.
        self.launcher = launcher
        self.root = workspace.expanduser().resolve()
        watching_one = (self.root / ProjectStore.filename).is_file()
        self.store = ProjectStore(self.root.parent if watching_one else self.root)
        #: `None` until the first poll finds a project to follow.
        self.project_dir: Path | None = None
        self.project: GameProject | None = None
        self.poll_seconds = poll_seconds
        #: Every diary line already on screen, in order. Kept as well as
        #: written into the panel because the verdict is read off the last of
        #: them, and a widget is not a place to read anything back from.
        self.lines: list[str] = []
        #: How much of `studio.log` has been consumed, in bytes. Bytes and
        #: not lines: this file is appended to by another process while it is
        #: being read, and a byte offset is the only cursor into it that
        #: cannot drift.
        self._read = 0
        #: `game.yml`'s mtime when it was last loaded, so a design is parsed
        #: again when the run adapts it and not twice a second forever.
        self._loaded = 0.0
        #: Last status, plain (no Rich markup), so a test or a script can read
        #: back what the screen says without scraping a widget.
        self.status_text = "no project yet"
        #: What `p` last had to report, or "". Only ever a refusal -- a
        #: launch that works says nothing, because the window says it.
        self.play_notice = ""
        #: Whether there was an artifact at the last redraw, so the footer is
        #: asked to re-read its bindings when that changes and not twice a
        #: second forever.
        self._playable = False

    # --- layout ---------------------------------------------------------

    def compose(self) -> ComposeResult:
        yield Header()
        brief_box = Vertical(
            Static("no project yet", id="brief-preview", markup=False),
            id="brief-box",
        )
        brief_box.border_title = "Brief"
        yield brief_box
        yield Static("", id="stage-line")
        yield Static("", id="stage-detail")
        yield Static("", id="verdict")
        # The diary, and it is most of the screen: the strip says which stage,
        # and only this says what the stage is doing.
        diary = RichLog(id="log-view", wrap=True, markup=False)
        diary.can_focus = False
        diary.border_title = "Diary"
        yield diary
        yield Footer()

    def on_mount(self) -> None:
        self.poll()
        self.set_interval(self.poll_seconds, self.poll)

    # --- following ------------------------------------------------------

    def poll(self) -> None:
        """Re-read everything that can have changed, and redraw.

        Cheap enough to run twice a second: two `stat` calls, the tail of one
        file, and a YAML parse only when `game.yml` has actually been written.
        """
        directory = self._watched()
        if directory != self.project_dir:
            self._follow(directory)
        self._read_diary()
        self._reload_project()
        self._redraw()

    def _projects(self) -> list[Path]:
        """Every project this screen could be watching.

        A directory holding a `game.yml` is itself the answer -- somebody
        pointed this at one project on purpose -- and anything else is read as
        a workspace.
        """
        if (self.root / ProjectStore.filename).is_file():
            return [self.root]
        return self.store.list_projects()

    def _watched(self) -> Path | None:
        """The project to follow: whichever was written to most recently.

        Asked again on every tick rather than once at startup, because the
        likeliest way this screen is used is to open it and *then* type
        `llmz80 make` next door: the project being watched does not exist yet
        when the watching begins. The diary is what is compared, since it is
        the file a run touches constantly; a project that has never been run
        is ranked by its `game.yml` instead, so a fresh workspace still shows
        something.
        """

        def touched(directory: Path) -> float:
            diary = directory / JOURNAL_FILENAME
            watched = diary if diary.is_file() else directory / ProjectStore.filename
            try:
                return watched.stat().st_mtime
            except OSError:
                return 0.0

        return max(self._projects(), key=touched, default=None)

    def _follow(self, directory: Path | None) -> None:
        """Start again on another project: its diary from the top, its design
        re-read, and nothing of the last one left on screen."""
        self.project_dir = directory
        self.project = None
        self.lines = []
        self._read = 0
        self._loaded = 0.0
        self.query_one("#log-view", RichLog).clear()

    def _read_diary(self) -> None:
        """Take whatever has been appended to `studio.log` since the last look.

        Read as bytes and stopped at the last newline, because the writer is
        another process: the tail of the file can be half a line at the moment
        this reads it, and half a line put on screen would be a line the
        diary never held. What is left of it arrives on the next tick.
        """
        if self.project_dir is None:
            return
        diary = self.project_dir / JOURNAL_FILENAME
        try:
            with diary.open("rb") as handle:
                handle.seek(self._read)
                fresh = handle.read()
        except OSError:
            return
        cut = fresh.rfind(b"\n")
        if cut < 0:
            return
        self._read += cut + 1
        panel = self.query_one("#log-view", RichLog)
        for line in fresh[:cut].decode("utf-8", errors="replace").splitlines():
            self.lines.append(line)
            panel.write(line)

    def _reload_project(self) -> None:
        """Re-read `game.yml` when it has been written since the last read.

        A design that will not parse is kept, not reported: the writer is
        another process, and a document caught mid-save is a moment rather
        than a fault -- the next tick reads the whole of it.
        """
        if self.project_dir is None:
            return
        document = self.project_dir / ProjectStore.filename
        try:
            stamp = document.stat().st_mtime
        except OSError:
            return
        if stamp == self._loaded and self.project is not None:
            return
        try:
            self.project = self.store.load(document)
        except (OSError, ValueError):
            return
        self._loaded = stamp

    # --- drawing --------------------------------------------------------

    def _redraw(self) -> None:
        walked = wizard.steps(self.project, self.project_dir)
        detail = pick_stage_detail(walked)
        artifact = self._artifact()
        strip = render_stage_marks(walked, colour=False)
        # The verdict and the offer share a line: what the run came to, and
        # the one thing left to do about it.
        verdict = "   ".join(
            part
            for part in (render_verdict(self.lines, artifact), render_play_offer(artifact))
            if part
        )
        coloured = "   ".join(
            part
            for part in (
                render_verdict(self.lines, artifact, colour=True),
                render_play_offer(artifact, colour=True),
            )
            if part
        )
        self.query_one("#stage-line", Static).update(render_stage_marks(walked, colour=True))
        self.query_one("#stage-detail", Static).update(detail)
        self.query_one("#verdict", Static).update(coloured)
        if (artifact is not None) != self._playable:
            # The footer caches which keys answer. Asked again only when the
            # answer has actually changed, not twice a second forever.
            self._playable = artifact is not None
            self.refresh_bindings()
        self.status_text = "\n".join(
            part for part in (strip, detail, verdict, self.play_notice) if part
        )
        if self.project is None:
            self.sub_title = str(self.root)
            self.query_one("#brief-preview", Static).update("no project yet")
            return
        self.sub_title = (
            f"{self.project.metadata.slug} · {self.project.target.platform.value} · "
            f"{len(self.project.screens)} screens"
        )
        self.query_one("#brief-preview", Static).update(brief_preview(self.project.metadata.brief))

    # --- the one thing that can be done ---------------------------------

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool:
        """Whether `p` is offered at all: only with a game really on disk.

        `False` rather than `None`, which are not the same answer to Textual:
        `None` greys the key out in the Footer and leaves it there, `False`
        takes it away. Until a run has published an artifact there is no game,
        and a footer advertising a key that would answer with an error is
        worse than a footer that never mentioned it.
        """
        if action == "play":
            return self._artifact() is not None
        return True

    def action_play(self) -> None:
        """Start the game in the emulator, or say why it cannot be.

        Nothing on this screen is written to and nothing on disk is touched:
        this hands the artifact to another process and goes back to watching.
        """
        artifact = self._artifact()
        if artifact is None:
            return
        self.play_notice = ""
        try:
            self.launcher(artifact)
        except NotPlayable as refusal:
            # The one thing this screen ever says on its own account. It goes
            # into `status_text` as well as a toast, so a test -- and a person
            # who missed the toast -- can still read it.
            self.play_notice = " ".join(refusal.lines)
            self.notify(self.play_notice, title="Cannot play", severity="error")
        except OSError as exc:
            self.play_notice = f"The emulator would not start: {exc}"
            self.notify(self.play_notice, title="Cannot play", severity="error")
        self._redraw()

    def _artifact(self) -> Path | None:
        """The tape or disk image this run published, if it is really there.

        `make.artifact_path` names it, so the screen and the order that builds
        it cannot disagree about which file a finished game is.
        """
        if self.project is None or self.project_dir is None:
            return None
        artifact = artifact_path(self.project, self.project_dir)
        return artifact if artifact.is_file() else None


def run_studio(workspace: Path = Path("studio-projects")) -> None:
    StudioViewer(workspace).run()
