"""The diary writes what it returns, so screen and file cannot diverge."""

from datetime import datetime

import pytest

from llmz80.studio.journal import FILENAME, Journal


class _Clock:
    """A clock a test can wind forward, so durations are asserted, not timed."""

    def __init__(self) -> None:
        self.now = datetime(2026, 8, 14, 9, 14, 2)

    def __call__(self) -> datetime:
        return self.now

    def advance(self, seconds: int) -> None:
        from datetime import timedelta

        self.now += timedelta(seconds=seconds)


@pytest.fixture()
def journal(tmp_path) -> Journal:
    return Journal(tmp_path / FILENAME, clock=_Clock())


def test_a_line_carries_its_stamp_and_kind(journal):
    line = journal.write("OPEN", "project fase-uno (spectrum, v4)")
    assert line.startswith("2026-08-14 09:14:02  OPEN")
    assert line.endswith("project fase-uno (spectrum, v4)")


def test_what_it_returns_is_what_it_wrote(journal):
    line = journal.write("WARN", "the design declares no mechanics")
    assert journal.path.read_text(encoding="utf-8").splitlines() == [line]


def test_lines_accumulate_across_sessions(journal):
    first = journal.write("OPEN", "project one")
    second = Journal(journal.path, clock=journal.clock).write("OPEN", "project one again")
    assert journal.path.read_text(encoding="utf-8").splitlines() == [first, second]


def test_a_start_hands_back_the_line_it_wrote(journal):
    token = journal.start("3 sprites — 2 entities with no art (API)")
    assert token.line == journal.path.read_text(encoding="utf-8").splitlines()[-1]


def test_finish_prices_the_work_from_its_own_start(journal):
    token = journal.start("3 sprites — 2 entities with no art (API)")
    journal.clock.advance(84)
    line = journal.finish(token, ok=True, text="2 sheets, 1024 B")
    assert "END" in line
    assert "in 84 s" in line
    assert "2 sheets, 1024 B" in line


def test_a_failed_finish_says_so(journal):
    token = journal.start("4 programa")
    journal.clock.advance(3)
    assert "FAILED" in journal.finish(token, ok=False, text="no diagnosis")


def test_notes_are_the_running_commentary(journal):
    assert journal.note("hero: 4 poses packed, 512 B").startswith("2026-08-14 09:14:02  ..      ")


def test_the_diary_creates_its_directory(tmp_path):
    path = tmp_path / "nuevo" / FILENAME
    Journal(path).write("OPEN", "new project")
    assert path.is_file()


def test_every_kind_keeps_the_same_left_margin(journal):
    """The margin is what makes a diary scannable, and the file is
    append-only: a column that changed width would misalign the lines written
    after this against the ones a project already holds. Checked over every
    kind there is, including `..`, which is not a word and is not translated.
    """
    from typing import get_args

    from llmz80.studio.journal import Kind

    columns = {journal.write(kind, "text").index("text") for kind in get_args(Kind)}

    assert len(columns) == 1, columns
    # And the vocabulary is the interface's one language.
    assert all(kind == ".." or kind.isascii() and kind.isupper() for kind in get_args(Kind))
    assert "ABRIR" not in get_args(Kind)
