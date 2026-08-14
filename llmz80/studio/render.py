"""Everything the Studio screen draws, as functions over plain data.

Nothing here imports Textual, touches a widget or reads a file: each of these
takes a `GameProject`, a `wizard.Step` or a plain string and returns the text
(Rich markup, or plain) that the screen puts in front of a person. That is
why they live apart from `tui.py` -- they can be read, and tested, without
starting an application: `render_map` against a project built in three lines,
`render_step_summary` against a step, `brief_preview` against a string.

It is the same principle `screen.stage_line` and `wizard.steps` already
follow, one layer further out. Those two decide *what is true* about a
project without drawing anything; this decides *what that looks like*
without drawing anything either. What is left in `tui.py` is the part that
genuinely needs a running terminal: the widget tree, the keys, and the jobs.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Sequence

from . import editing, wizard
from .journal import parse
from .models import GameProject
from .screen import Stage

#: The one glyph the map editor does not take from the design itself: the
#: filled block it has always drawn a wall with.
GLYPH_WALL = "▓"

#: What the legend puts in front of the tile `space` is about to paint.
TILE_CURSOR = "▸"


def tile_glyphs(project: GameProject) -> dict[str, str]:
    """Which glyph draws each tile character this design declared.

    The rule, and it is a legibility decision rather than a forced one:

    * the design's *solid* tile -- the one `editing.solid_char` picks, the
      first carrying the `solid` trait -- is drawn as `▓`. A filled block
      reads as a wall from across the room, which a `#` does not, and it is
      the glyph this editor has always used for it;
    * every other declared tile is drawn as the very character the design
      declared for it. Nothing else Studio could invent would be as easy to
      check against `game.yml`: the grid on screen and the rows in the file
      are then the same characters, and the legend needs no second table
      mapping invented glyphs back onto tiles.

    That every tile ends up distinguishable is not luck. `structure.py`
    refuses a design where two tiles share a character, and `▓` can never
    collide with a declared one because `TileSpec.char` is printable ASCII
    only -- so the map draws exactly as many different glyphs as the design
    declares tiles.

    What this replaces: a two-way test (`is this the solid character?`) that
    drew every other tile as the same floor dot, so a design declaring three
    tiles showed two, and a ladder could be neither seen nor painted.
    """
    solid = editing.solid_char(project)
    return {tile.char: (GLYPH_WALL if tile.char == solid else tile.char) for tile in project.tiles}


def render_tile_legend(project: GameProject, selected: str = "") -> str:
    """The map's own key: which glyph is which tile, named by its `id`.

    A glyph a person can see but not name is only half the fix -- the point
    is to edit the map, and editing means knowing that `H` is the ladder this
    design calls `escalera` before painting with it. `selected` marks the tile
    `space` paints, so the legend answers "what will this key do" as well as
    "what am I looking at", which is why it is one line and not two.
    """
    glyphs = tile_glyphs(project)
    parts = []
    for tile in project.tiles:
        chosen = tile.char == selected
        # Marked twice, on purpose: reverse video is what a person sees on a
        # terminal, and `▸` is what survives being read as plain text -- by a
        # test, by a screen reader, or by a terminal that renders reverse
        # video as nothing much.
        entry = f"{TILE_CURSOR if chosen else ' '}{glyphs[tile.char]} {tile.id}"
        if chosen:
            entry = f"[reverse]{entry}[/reverse]"
        parts.append(entry)
    return " ".join(parts)


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
#: Rich markup tags, stripped when a screen message is written to the diary:
#: the file is read in a pager, where `[green]` is noise rather than colour.
_MARKUP = re.compile(r"\[/?[a-z ]+\]")


def _plain(text: str) -> str:
    return _MARKUP.sub("", text).strip()


def _summary(message: str) -> str:
    """A job's result as the one line a diary can hold.

    Screen messages run to several lines -- one per write attempt, one per
    acceptance scenario -- and a diary is read by scanning the left margin,
    which a multi-line entry ruins. Joined with the same separator the wizard
    already uses between the parts of a sentence.
    """
    return " · ".join(part for part in _plain(message).splitlines() if part.strip())


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
    glyphs = tile_glyphs(project)
    lines = []
    for row in range(screen.height):
        cells = []
        for col in range(screen.width):
            char = screen.tiles[row][col]
            # `glyphs.get(char, char)` rather than `glyphs[char]`: a saved
            # design cannot hold a character it never declared (`structure.py`
            # refuses one), and drawing it as itself is a cheaper answer than
            # a KeyError for a project someone hand-edited badly.
            glyph = occupants.get((col, row), glyphs.get(char, char))
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


def render_step_head(step: wizard.Step) -> str:
    """The one line that says where in the pipeline the person is standing.

    Counted "of 6" rather than "of 7": the six pipeline stages are the work,
    and step zero -- having a project open at all -- is the precondition for
    any of them, so numbering it 0 keeps the six named steps at the numbers
    `wizard` and the diary already give them.

    `title`, not `name`: `name` is the stage's id -- what `passed` holds and
    what the diary records -- and printing it here is what left an otherwise
    English screen saying `Step 2 of 6: diseño`.
    """
    return f"Step {step.number} of 6: {step.title}"


def render_step_summary(step: wizard.Step, *, can_adapt: bool = False) -> str:
    """What this step is for, and which key does it -- the sentence that
    replaces having to know that `ctrl+f` came before `ctrl+a`.

    A step still to do names `Enter` and its own verb, warns when pressing it
    will spend money at an API, and offers `→` only where
    `wizard.can_leave_behind` would actually allow it, so the screen never
    suggests a key that will answer with a refusal. A step already resolved
    names `→` to move on and `R` to do it over.

    An *editable* step names `Enter` in both cases, and that is what
    `Step.editable` is for. `diseño` is the one step whose purpose is to be
    edited and the one step that arrives already `done` -- a `GameProject`
    cannot exist without screens, tiles and entities, so
    `screen._design_stage` never says `pending`. Collapsing those into one
    "resolved" branch meant the only step that exists in order to be worked
    on was the only one that never named its own verb: `Enter` opened the
    editor and the screen did not say so. `done` on an editable step means
    "the design is valid", not "there is nothing left to do here", and
    those are different things.

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
    resolved = step.state in {"done", "skipped"}
    if not resolved or step.editable:
        parts.append(f"[Enter] {step.action_label}")
        if step.costs_api:
            parts.append("spends money (API)")
    if can_adapt:
        parts.append("[A] adapt the design to the dossier")
    if resolved:
        parts.append("[→] next step")
        if step.state == "done":
            parts.append("[R] repeat")
        return " · ".join(parts)
    if wizard.can_leave_behind(step):
        parts.append("[→] skip")
    return " · ".join(parts)


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
