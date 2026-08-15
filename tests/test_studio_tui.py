"""The screen, judged as a window: it shows a run and it changes nothing.

Every test here drives the viewer against a project directory somebody else
wrote -- a `studio.log` appended to, a `reference.yml` archived, an artifact
published -- because that is exactly the situation the screen exists for:
`llmz80 make` runs in one terminal and this watches from another, with
nothing between them but the files.

`poll()` is called by hand rather than waited for. The interval is Textual's
and its timing is not this suite's business; what is worth proving is that a
poll reads what is on disk at that moment and draws it.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from llmz80.studio.journal import Journal
from llmz80.studio.models import TargetPlatform
from llmz80.studio.reference import GameReference, ReferenceSource, save_reference
from llmz80.studio.play import NotPlayable
from llmz80.studio.render import (
    brief_preview,
    pick_stage_detail,
    render_play_offer,
    render_stage_marks,
    render_verdict,
)
from llmz80.studio.screen import Stage
from llmz80.studio.services import StudioService
from llmz80.studio.tui import StudioViewer


def _project(workspace: Path, title: str = "Watched", brief: str = "") -> Path:
    """A real project on disk, the way `make` would leave one: the viewer is
    given nothing else to go on."""
    service = StudioService.at(workspace)
    project, directory = service.create_project(title, TargetPlatform.SPECTRUM)
    if brief:
        from llmz80.studio.editing import rename_project

        service.save_project(
            rename_project(project, project.metadata.title, brief=brief), directory
        )
    return directory


def _built(directory: Path) -> Path:
    """The tape a finished run publishes. Playing is offered off this file
    being on disk and nothing else."""
    artifact = directory / "build" / "output.tap"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_bytes(b"TAP")
    return artifact


def _dossier(title: str = "Manic Miner") -> GameReference:
    return GameReference(
        identified=True,
        confidence="high",
        title=title,
        sources=[
            ReferenceSource(
                url="https://example.com/game",
                title="a source",
                retrieved_at=datetime.now(timezone.utc),
            )
        ],
    )


def _log_view(app: StudioViewer) -> str:
    """What the diary panel is actually showing, as text.

    One string per rendered row, which is not one per diary line: the panel
    wraps, so a long line arrives here in pieces. Tests that care about a
    whole line read `app.lines` instead -- that is the list the verdict is
    read off, and the one that must hold what the file holds.
    """
    return "\n".join(strip.text for strip in app.query_one("#log-view").lines)


# --- what the screen says --------------------------------------------------


@pytest.mark.asyncio
async def test_the_strip_advances_by_reading_what_the_run_left_on_disk(tmp_path: Path):
    """Nothing tells this screen anything: the stage marks are read off the
    same evidence `screen.stage_line` reads, so a run happening in another
    process moves them."""
    directory = _project(tmp_path)
    app = StudioViewer(tmp_path)
    async with app.run_test(size=(80, 24)):
        assert "Reference —" in app.status_text

        save_reference(_dossier("Manic Miner"), directory)
        app.poll()

        assert "Reference ✓" in app.status_text
        assert "Manic Miner" in app.status_text
        # Six steps: the five the order runs, and having a project at all.
        assert "Project ✓" in app.status_text
        assert "Gates —" in app.status_text
        assert "Release" not in app.status_text


@pytest.mark.asyncio
async def test_the_diary_reaches_the_screen_as_it_is_written(tmp_path: Path):
    directory = _project(tmp_path)
    diary = Journal.for_project(directory)
    app = StudioViewer(tmp_path)
    async with app.run_test(size=(80, 24)):
        diary.write("OPEN", "made game.yml · spectrum")
        app.poll()
        assert "made game.yml · spectrum" in _log_view(app)

        token = diary.start("4 programa — writing the program against the compiler")
        diary.note("attempt 1: asking the model")
        app.poll()

        panel = _log_view(app)
        assert token.line in app.lines
        assert "attempt 1: asking the model" in panel
        # Nothing is shown twice: the second poll took only what was appended.
        assert panel.count("made game.yml") == 1


@pytest.mark.asyncio
async def test_half_a_line_waits_for_the_rest_of_itself(tmp_path: Path):
    """The writer is another process, so the tail of the file can be a line
    that is still being written. Half a line on screen is a line the diary
    never held."""
    directory = _project(tmp_path)
    app = StudioViewer(tmp_path)
    async with app.run_test(size=(80, 24)):
        log = directory / "studio.log"
        log.write_text("2026-08-13 10:00:00  START   4 programa — writ", encoding="utf-8")
        app.poll()
        assert app.lines == []

        log.write_text("2026-08-13 10:00:00  START   4 programa — writing it\n", encoding="utf-8")
        app.poll()

        assert app.lines == ["2026-08-13 10:00:00  START   4 programa — writing it"]


@pytest.mark.asyncio
async def test_the_verdict_names_where_the_game_landed(tmp_path: Path):
    directory = _project(tmp_path)
    Journal.for_project(directory).write("END", "5 gates — ok in 84 s. gates passed")
    artifact = directory / "build" / "output.tap"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_bytes(b"TAP")

    app = StudioViewer(tmp_path)
    async with app.run_test(size=(80, 24)):
        assert f"Done · the game is at {artifact}" in app.status_text


@pytest.mark.asyncio
async def test_the_verdict_names_what_stopped_the_run(tmp_path: Path):
    directory = _project(tmp_path)
    diary = Journal.for_project(directory)
    diary.write("END", "4 programa — FAILED in 61 s.")
    diary.write("ERROR", "programa: the compiler said no")

    app = StudioViewer(tmp_path)
    async with app.run_test(size=(80, 24)):
        assert "Stopped · programa: the compiler said no" in app.status_text


@pytest.mark.asyncio
async def test_the_verdict_says_what_the_run_is_busy_with(tmp_path: Path):
    directory = _project(tmp_path)
    Journal.for_project(directory).start("4 programa — writing the program")

    app = StudioViewer(tmp_path)
    async with app.run_test(size=(80, 24)):
        assert "Working · 4 programa — writing the program" in app.status_text


@pytest.mark.asyncio
async def test_the_header_names_the_project_and_the_brief_is_one_line(tmp_path: Path):
    _project(tmp_path, "Ghosts", brief="Four ghosts chase you.\nA big dot makes them edible.")

    app = StudioViewer(tmp_path)
    async with app.run_test(size=(80, 24)):
        assert "ghosts · spectrum" in app.sub_title
        assert (
            str(app.query_one("#brief-preview").content)
            == "Four ghosts chase you. A big dot makes them edible."
        )


# --- which project ---------------------------------------------------------


@pytest.mark.asyncio
async def test_the_run_started_afterwards_is_the_one_followed(tmp_path: Path):
    """Open the screen, then type `llmz80 make` next door: the project being
    watched did not exist when the watching began."""
    first = _project(tmp_path, "First")
    Journal.for_project(first).write("OPEN", "the older run")

    app = StudioViewer(tmp_path)
    async with app.run_test(size=(80, 24)):
        assert app.project_dir == first

        second = _project(tmp_path, "Second")
        Journal.for_project(second).write("OPEN", "the newer run")
        app.poll()

        assert app.project_dir == second
        # The older run's lines went with it, rather than being read as this
        # one's history.
        assert "the older run" not in _log_view(app)
        assert "the newer run" in _log_view(app)


@pytest.mark.asyncio
async def test_a_project_directory_is_watched_on_its_own(tmp_path: Path):
    """Pointed at one project, it follows that one and no other -- which is
    how yesterday's run is looked at while today's is running."""
    older = _project(tmp_path, "Older")
    Journal.for_project(older).write("OPEN", "yesterday")
    newer = _project(tmp_path, "Newer")
    Journal.for_project(newer).write("OPEN", "today")

    app = StudioViewer(older)
    async with app.run_test(size=(80, 24)):
        assert app.project_dir == older
        assert "yesterday" in _log_view(app)


@pytest.mark.asyncio
async def test_an_empty_workspace_says_so_rather_than_crashing(tmp_path: Path):
    app = StudioViewer(tmp_path)
    async with app.run_test(size=(80, 24)):
        app.poll()

        assert app.project_dir is None
        # The strip is still drawn, with nothing done in it: an empty
        # workspace is a run that has not started, not a broken screen.
        assert app.status_text == (
            "Project —  Reference —  Drafting —  Design —  Sprites —  Program —  Gates —"
        )
        assert str(app.query_one("#brief-preview").content) == "no project yet"


# --- two keys, and nothing written -----------------------------------------


def test_the_only_keys_are_playing_the_game_and_leaving():
    """A screen that shows a run has two things left to decide: play what it
    produced, or stop watching. Anything else is work, and work belongs in the
    order that does it."""
    assert [binding[0] for binding in StudioViewer.BINDINGS] == ["p", "q"]
    # And Textual's own palette is off, so the Footer names every key that
    # answers: `p`, `q`, and `ctrl+c`, which the framework reserves for itself.
    assert StudioViewer.ENABLE_COMMAND_PALETTE is False
    # No `on_key` either: every key the old wizard answered lived there, and
    # a screen with a handler is a screen that can grow one back without
    # anybody noticing the Footer never mentioned it.
    assert not hasattr(StudioViewer, "on_key")


@pytest.mark.asyncio
async def test_no_key_changes_anything_it_is_watching(tmp_path: Path):
    directory = _project(tmp_path)
    Journal.for_project(directory).write("OPEN", "made game.yml")
    before = {path.name: path.read_bytes() for path in directory.iterdir() if path.is_file()}

    app = StudioViewer(tmp_path)
    async with app.run_test(size=(80, 24)) as pilot:
        for key in ("enter", "right", "escape", "r", "g", "m", "e", "s", "d", "a", "y", "n"):
            await pilot.press(key)
        app.poll()

        assert app.is_running
        assert {
            path.name: path.read_bytes() for path in directory.iterdir() if path.is_file()
        } == before


@pytest.mark.asyncio
async def test_a_poll_that_lands_while_the_screen_is_coming_down_draws_nothing(
    tmp_path: Path,
):
    """The interval outlives the widgets it draws into.

    Shutting down -- `q`, Ctrl-C, or a test leaving `run_test` -- clears
    `is_running` first and takes the screen's children away afterwards, and a
    tick in between used to reach `query_one("#stage-line")` and raise
    `NoMatches` out of the timer. That is the app stopping on an error rather
    than on somebody's say-so, and the reason `test_no_key_changes_anything_it
    _is_watching` above can lose `assert app.is_running` in a loaded suite and
    win it on its own: at half a second the window is only as wide as the
    shutdown, and it takes a busy machine to land in it.

    A thousandth of a second is the same window opened wide enough to hit
    every time -- without the guard this failed 25 runs out of 25 -- and the
    poll interval is injectable for exactly this sort of reason.
    """
    directory = _project(tmp_path)
    Journal.for_project(directory).write("OPEN", "made game.yml")

    app = StudioViewer(tmp_path, poll_seconds=0.001)
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.press("enter")
        assert app.is_running

    # Leaving the context is the shutdown, and it must come back quietly:
    # `run_test` re-raises whatever the timer raised while it was closing.
    assert not app.is_running


# --- playing what the run produced -----------------------------------------


@pytest.mark.asyncio
async def test_the_key_that_plays_is_offered_only_once_the_game_is_on_disk(tmp_path: Path):
    """A footer advertising a key that would answer with an error is worse
    than a footer that never mentioned it -- and the screen says it beside the
    verdict, which is the line somebody actually reads when a run ends."""
    directory = _project(tmp_path)
    Journal.for_project(directory).write("END", "5 gates — ok in 84 s. gates passed")

    app = StudioViewer(tmp_path, launcher=lambda _artifact: None)
    async with app.run_test(size=(80, 24)):
        assert "[p] play" not in app.status_text
        assert app.check_action("play", ()) is False

        artifact = _built(directory)
        app.poll()

        assert "[p] play" in app.status_text
        assert f"Done · the game is at {artifact}" in app.status_text
        assert app.check_action("play", ()) is True


@pytest.mark.asyncio
async def test_pressing_it_starts_the_game_this_run_built(tmp_path: Path):
    """What the whole change exists for: a person watching a finished run can
    play it from where they are watching."""
    directory = _project(tmp_path)
    artifact = _built(directory)
    started: list[Path] = []

    app = StudioViewer(tmp_path, launcher=started.append)
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.press("p")

        assert started == [artifact]
        # And it changed nothing it is watching.
        assert app.play_notice == ""


@pytest.mark.asyncio
async def test_pressing_it_with_nothing_built_starts_nothing(tmp_path: Path):
    _project(tmp_path)
    started: list[Path] = []

    app = StudioViewer(tmp_path, launcher=started.append)
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.press("p")

        assert started == []


@pytest.mark.asyncio
async def test_a_missing_emulator_is_said_on_screen_rather_than_swallowed(tmp_path: Path):
    """`play` reports by printing, and a screen has no terminal to print on.
    Its refusal arrives as an exception and is put where a person can read
    it."""
    directory = _project(tmp_path)
    _built(directory)

    def refuse(_artifact: Path) -> None:
        raise NotPlayable("zesarux is not on PATH.", "Install ZEsarUX and run this again.")

    app = StudioViewer(tmp_path, launcher=refuse)
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.press("p")

        assert "zesarux is not on PATH." in app.play_notice
        assert "Install ZEsarUX" in app.status_text
        assert app.is_running


@pytest.mark.asyncio
@pytest.mark.parametrize("size", [(80, 24), (96, 37), (120, 40)])
async def test_the_footer_names_the_keys_on_the_last_row_at_any_size(
    tmp_path: Path, size: tuple[int, int]
):
    """Three terminals, one question: is the footer there. It was reported
    missing at around 96x37 with a long diary, and it is not -- the diary
    panel gives up its last row to the footer at every size, because the
    Footer is docked and the panel is what `1fr` divides up.

    The pause is not decoration: Textual's Footer composes nothing until the
    screen publishes its bindings, and it does that after the mount that this
    test would otherwise measure.
    """
    directory = _project(tmp_path, "Watched", brief="x" * 400)
    _built(directory)
    diary = Journal.for_project(directory)
    for number in range(60):
        diary.note(f"line {number} of a diary that is longer than the panel")

    app = StudioViewer(tmp_path, launcher=lambda _artifact: None)
    async with app.run_test(size=size) as pilot:
        app.poll()
        await pilot.pause()
        drawn = [strip.text.rstrip() for strip in app.screen._compositor.render_strips()]

        assert len(drawn) == size[1]
        assert "Quit" in drawn[-1]
        assert "Play" in drawn[-1]


@pytest.mark.asyncio
async def test_the_whole_path_of_the_game_is_readable_at_eighty_columns(tmp_path: Path):
    """The verdict of a finished run is where the game is, and a path is as
    long as somebody's directories are deep. Cut at the width of the terminal
    it read "Done · the game is at" and nothing after it."""
    deep = tmp_path / "a-workspace-with-a-long-name" / "and-another-directory-inside-it"
    directory = _project(deep, "Deeply Nested Game")
    Journal.for_project(directory).write("END", "5 gates — ok in 84 s. gates passed")
    artifact = directory / "build" / "output.tap"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_bytes(b"TAP")

    app = StudioViewer(deep)
    async with app.run_test(size=(80, 24)):
        drawn = [strip.text.rstrip() for strip in app.screen._compositor.render_strips()]

        assert all(len(line) <= 80 for line in drawn)
        shown = "".join(line.strip() for line in drawn)
        assert str(artifact) in shown


@pytest.mark.asyncio
async def test_the_screen_fits_an_eighty_by_twentyfour_terminal(tmp_path: Path):
    """The narrowest terminal anybody still uses, with a run at its noisiest:
    six steps, a detail, a verdict and a diary."""
    directory = _project(tmp_path, "Cornered", brief="x" * 400)
    save_reference(_dossier("A Game With A Long Enough Name"), directory)
    diary = Journal.for_project(directory)
    for number in range(40):
        diary.note(f"line {number} of a diary that is longer than the panel")

    app = StudioViewer(tmp_path)
    async with app.run_test(size=(80, 24)):
        drawn = [strip.text.rstrip() for strip in app.screen._compositor.render_strips()]

        assert len(drawn) <= 24
        assert all(len(line) <= 80 for line in drawn)
        # The three lines that carry the news are all on it.
        assert any("Reference ✓" in line for line in drawn)
        assert any("A Game With A Long Enough Name" in line for line in drawn)
        assert any("Working" in line for line in drawn)


# --- the pure functions the screen draws with ------------------------------


def test_render_stage_marks_shows_one_icon_per_stage():
    stages = [
        Stage("referencia", "done", "Zampa Bolas (System 4, 1990) · 8 sources"),
        Stage("diseño", "done"),
        Stage("sprites", "failed", "0/2 accepted by the blitter"),
        Stage("programa", "pending"),
    ]

    plain = render_stage_marks(stages, colour=False)

    assert plain == "referencia ✓  diseño ✓  sprites ✗  programa —"
    assert "[red]" not in plain


def test_render_stage_marks_colours_each_state():
    stages = [Stage("gates", "done"), Stage("programa", "pending")]

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


def test_the_play_offer_is_drawn_only_for_a_game_that_is_really_there():
    assert render_play_offer(None) == ""
    assert render_play_offer(Path("build/output.tap")) == "[p] play"


def test_the_play_offer_escapes_its_brackets_where_a_person_reads_it():
    """Rich would read `[p]` as a style it does not have and refuse to draw
    the line at all."""
    assert render_play_offer(Path("build/output.tap"), colour=True) == "[dim]\\[p] play[/dim]"


def test_the_newest_line_decides_the_verdict():
    """A stopped run that is started again is running, not stopped, and a
    stale artifact from the run before never speaks for the one going on."""
    stopped = ["2026-08-13 10:00:00  ERROR   programa: the compiler said no"]
    working = stopped + ["2026-08-13 10:05:00  START   4 programa — writing it again"]

    assert render_verdict(stopped) == "Stopped · programa: the compiler said no"
    assert render_verdict(stopped, Path("build/output.tap")) == (
        "Stopped · programa: the compiler said no"
    )
    assert render_verdict(working, Path("build/output.tap")) == (
        "Working · 4 programa — writing it again"
    )


def test_a_diary_that_says_nothing_yet_gets_no_verdict():
    assert render_verdict([]) == ""
    assert render_verdict(["2026-08-13 10:00:00  END     5 gates — ok in 2 s."]) == ""


def test_the_verdict_is_coloured_only_where_a_person_reads_it():
    lines = ["2026-08-13 10:00:00  ERROR   gates: the game ran but the gates refused it"]

    assert "[red]" in render_verdict(lines, colour=True)
    assert "[" not in render_verdict(lines)
