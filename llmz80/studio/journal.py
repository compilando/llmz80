"""The project's diary: what Studio did, when, and how long it took.

Every line is written to `<project>/studio.log` *and returned*, so whatever
draws it on screen shows the same string the file keeps. Composing the screen
version separately is how the two start telling different stories about the
same event.

The diary is append-only and survives the session: a pipeline step can take
minutes and spend money, and "what happened last night" is a question worth
being able to answer the next morning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Literal, get_args

#: The kinds of line a diary carries. Few and fixed-width on purpose: a reader
#: scanning the left margin sees the shape of a session -- what started, what
#: it said along the way, what it ended as -- before reading any of it.
#:
#: English, like everything else a person reads in Studio; `..` is not a word
#: and stays as it is. The column keeps the eight characters it always had
#: even though the longest word is now five, so the lines a diary already
#: holds and the ones written after this go on lining up in the same file.
Kind = Literal["OPEN", "STAGE", "START", "..", "END", "WARN", "ERROR", "SAVE", "SKIP"]

#: `Kind` read back as plain strings, for `parse` below: a line is only a
#: diary line if its margin holds one of these, and there is no second list of
#: them to keep in step with the first.
KINDS = get_args(Kind)

FILENAME = "studio.log"

_STAMP = "%Y-%m-%d %H:%M:%S"


@dataclass(frozen=True)
class Token:
    """What `start` hands back: enough to price the work when it finishes, and
    the line it already wrote, so the caller can put that same line on screen
    without composing a second version of it."""

    text: str
    began: datetime
    line: str


@dataclass
class Journal:
    path: Path
    #: Injected so a test can wind time forward and assert a duration instead
    #: of timing one. The default is the local clock rather than UTC: this file
    #: is read by the person sitting at the machine, and local time is what
    #: matches their memory of what they were doing.
    clock: Callable[[], datetime] = field(default=datetime.now)

    @classmethod
    def for_project(cls, directory: Path) -> "Journal":
        return cls(directory / FILENAME)

    def write(self, kind: Kind, text: str) -> str:
        line = f"{self.clock().strftime(_STAMP)}  {kind:<8}{text}"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as diary:
            diary.write(line + "\n")
        return line

    def start(self, text: str) -> Token:
        """Open a piece of work. The token remembers when, so `finish` can say."""
        began = self.clock()
        return Token(text=text, began=began, line=self.write("START", text))

    def note(self, text: str) -> str:
        """One line of running commentary from inside a piece of work."""
        return self.write("..", text)

    def finish(self, token: Token, *, ok: bool, text: str = "") -> str:
        seconds = int((self.clock() - token.began).total_seconds())
        verdict = "ok" if ok else "FAILED"
        tail = f" {text}" if text else ""
        return self.write("END", f"{token.text} — {verdict} in {seconds} s.{tail}")


def parse(line: str) -> tuple[str, str]:
    """A written line read back as `(kind, text)`.

    The inverse of `write`, and the reason the format is fixed-width: the
    stamp is 19 characters, two spaces separate it from an eight-character
    kind, and the rest is what was said. A line that does not hold one of
    `KINDS` in that column is not one of ours -- a stack trace someone pasted
    in, a line from an older format -- and is handed back whole under an empty
    kind rather than guessed at.

    Reading a diary back is how a screen that did not do the work can still
    show it: `llmz80 make` writes this file from one terminal and `llmz80
    studio` follows it from another, with nothing between them but the file.
    """
    kind = line[21:29].strip()
    if line[19:21] == "  " and kind in KINDS:
        return kind, line[29:]
    return "", line
