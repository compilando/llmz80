"""Everything the Studio screen draws, as functions over plain data.

Nothing here imports Textual, touches a widget or reads a file: each of these
takes a stage, a diary line or a plain string and returns the text (Rich
markup, or plain) that the screen puts in front of a person. That is why they
live apart from `tui.py` -- they can be read, and tested, without starting an
application: `render_stage_marks` against four stages built in one line,
`render_verdict` against a diary that is a list of strings.

It is the same principle `screen.stage_line` and `wizard.steps` already
follow, one layer further out. Those two decide *what is true* about a
project without drawing anything; this decides *what that looks like*
without drawing anything either. What is left in `tui.py` is the part that
genuinely needs a running terminal: the widget tree, the one key, and the
timer that re-reads the files.

What went with the wizard: the map, its tile legend and the two lines that
named which key did this step. A screen that watches a run has no keys to
name, and the map was a fixed-width grid of characters -- it could not draw
connected rooms, or scroll, or anything else a design might invent, and
keeping it would have kept the assumption that every game has the same shape.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from . import wizard
from .journal import parse
from .screen import Stage

#: One character per `screen.StageState`, and no more: those three are every
#: state a stage can be in, because every one of them is read off evidence.
#: (There was a fourth, `skipped`, for a step a person walked past on purpose;
#: nothing decides that any more.) Drawn plain for `status_text`, which tests
#: and scripts read as a string, and wrapped in colour markup only for the
#: widget a person looks at.
STAGE_ICON = {"done": "✓", "pending": "—", "failed": "✗"}
STAGE_COLOR = {"done": "green", "pending": "dim", "failed": "red"}

#: The characters left of the brief preview's one line, before it is cut off
#: with an ellipsis. Chosen to comfortably fit a typical terminal width
#: without depending on the actual rendered width of the box: a fixed budget
#: keeps the preview exactly one line regardless of window size or how long
#: the brief itself is, which is the property that keeps the resting screen
#: from growing.
BRIEF_PREVIEW_LIMIT = 78


def render_stage_marks(stages: Sequence[Stage | wizard.Step], *, colour: bool) -> str:
    """One line: every stage's name and its state as a single character.

    `colour` picks Rich markup (for the widget a person reads) or plain text
    (for `status_text`, so a test can search it without stripping markup).
    A pure function over `screen.stage_line`'s own output -- or over
    `wizard.steps`'s, which carries the same two fields under a title --
    kept apart from the widget so it can be read, and tested, without a
    running application.
    """
    parts = []
    for stage in stages:
        icon = STAGE_ICON[stage.state]
        if colour:
            icon = f"[{STAGE_COLOR[stage.state]}]{icon}[/{STAGE_COLOR[stage.state]}]"
        # `wizard.Step` carries a title to show; `screen.Stage` is the
        # evidence layer and knows only the stage's id, which is exactly what
        # it should know. Whatever this is handed, it prints the most
        # human-readable name that thing has.
        parts.append(f"{getattr(stage, 'title', '') or stage.name} {icon}")
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


#: What the verdict line says, and the colour it says it in. Three states and
#: no more, because a diary answers exactly three questions about the run that
#: wrote it: is it still going, did it stop, and where did the game land.
VERDICT_COLOR = {"stopped": "red", "working": "yellow", "done": "green"}


def render_verdict(
    lines: Sequence[str], artifact: Path | None = None, *, colour: bool = False
) -> str:
    """What the run this diary belongs to has come to, from its own last line.

    A run that stopped ends its diary with `ERROR` naming the stage and what
    it said; a run still going ends with the work it opened (`START`) or with
    something that work said along the way (`..`), and naming that line is how
    a screen says "it is on the program, writing it against the compiler"
    without asking anybody. Anything else is a run that ended without
    stopping, and the only thing worth saying then is where the game is:
    `artifact` is that path, and the caller passes it only where the file is
    really on disk -- printing a path to a file that is not there is the one
    lie a screen watching a build must not tell.

    The order matters and is the order above: an `ERROR` beats a stale
    artifact from an earlier run, and a `START` after that `ERROR` beats the
    error, because the newest line is the truest thing the file knows.

    `colour` picks Rich markup or plain text, the same choice
    `render_stage_marks` offers and for the same reason: the widget wants
    colour, and `status_text` -- which a test or a script reads back -- wants
    the characters and nothing else.
    """
    kind, text = "", ""
    for line in reversed(list(lines)):
        if line.strip():
            kind, text = parse(line)
            break
    if kind == "ERROR":
        state, said = "stopped", f"Stopped · {text}"
    elif kind in {"START", ".."}:
        state, said = "working", f"Working · {text}"
    elif artifact is not None:
        state, said = "done", f"Done · the game is at {artifact}"
    else:
        return ""
    if not colour:
        return said
    return f"[{VERDICT_COLOR[state]}]{said}[/{VERDICT_COLOR[state]}]"


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
