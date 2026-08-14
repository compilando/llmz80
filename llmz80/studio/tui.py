"""A window onto a run: where `llmz80 make` has got to, and how it ended.

This screen does no work and decides nothing. The pipeline is one order --
`llmz80 make "an idea"` -- and it runs in whatever terminal it was typed in;
this is the other terminal, the one somebody leaves open to watch. It shows
four things and offers one key:

* the project's identity, in the header;
* the seven-stage strip, read off the evidence the pipeline leaves on disk
  (`wizard.steps`, over `screen.stage_line`), so it advances by itself as the
  run advances -- nothing here is told anything;
* the diary, followed line by line out of `<project>/studio.log` as it is
  written;
* the verdict: what stopped the run, or where the game landed.

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

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, RichLog, Static

from . import wizard
from .journal import FILENAME as JOURNAL_FILENAME
from .make import artifact_path
from .models import GameProject
from .render import brief_preview, pick_stage_detail, render_stage_marks, render_verdict
from .store import ProjectStore

#: How often the diary and the evidence on disk are re-read. Half a second is
#: below the threshold at which a person watching a build would call the
#: screen stale, and far above the cost of stat-ing two files and reading the
#: tail of one.
POLL_SECONDS = 0.5


class StudioViewer(App[None]):
    """The whole screen. One key -- `q` -- and nothing that writes."""

    TITLE = "LLMZ80 Studio"
    #: Nothing here is focusable and nothing is typed into, so nothing is
    #: focused: Textual would otherwise hand focus to the first widget it
    #: finds and give its scroll keys precedence over the one key this has.
    AUTO_FOCUS = None
    #: One key. Not "one key per thing you can do" -- there is nothing to do
    #: here -- but the only decision a person looking at a screen still has.
    BINDINGS = [("q", "quit", "Quit")]
    #: Off, so that one key is really one: Textual's palette is a way of
    #: reaching commands, and a screen with no commands offering a way to
    #: search them would be advertising something it does not have.
    ENABLE_COMMAND_PALETTE = False
    CSS = """
    #brief-box { height: 3; border: round $primary; margin: 0 1; padding: 0 1; }
    /* Auto rather than a fixed row: seven stages fit one line on 80 columns
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

    def __init__(self, workspace: Path, *, poll_seconds: float = POLL_SECONDS) -> None:
        super().__init__()
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
        verdict = render_verdict(self.lines, artifact)
        self.query_one("#stage-line", Static).update(render_stage_marks(walked, colour=True))
        self.query_one("#stage-detail", Static).update(detail)
        self.query_one("#verdict", Static).update(render_verdict(self.lines, artifact, colour=True))
        self.status_text = "\n".join(part for part in (strip, detail, verdict) if part)
        if self.project is None:
            self.sub_title = str(self.root)
            self.query_one("#brief-preview", Static).update("no project yet")
            return
        self.sub_title = (
            f"{self.project.metadata.slug} · {self.project.target.platform.value} · "
            f"{len(self.project.screens)} screens"
        )
        self.query_one("#brief-preview", Static).update(brief_preview(self.project.metadata.brief))

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
