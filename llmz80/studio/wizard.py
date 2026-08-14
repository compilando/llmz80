"""The pipeline's steps, in order, each with the state it is in.

A pure state machine over `screen.stage_line`. That module already decides
what has been done, from the design in memory and the evidence the pipeline
left on disk; this one adds what it does not have: the order, the number and
the name a person reads. It deliberately does not re-derive any of the "is
this done" logic -- two answers to that question would drift apart within a
week.

Two things read this. `make.py` takes each stage's number and id, so the
diary it writes says `4 programa` and goes on meaning that a year later; the
screen takes the whole list and draws the strip. Nothing here draws, calls an
API or touches disk, which is what lets both be tested without starting
Textual, exactly as `stage_line` already is.

`summary`, `action_label`, `costs_api`, `editable`, `skippable` and
`can_leave_behind` are what a wizard needed to name the key that did each
step and to decide whether a person could walk past it. There is no wizard
any more -- `llmz80 make` runs the whole order -- so nothing but their own
tests reads them today.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable, Literal

from .models import GameProject
from .screen import stage_line

#: `screen.StageState` plus the one state a stage cannot know about itself:
#: that the person decided to go past it.
StepState = Literal["done", "pending", "failed", "skipped"]


@dataclass(frozen=True)
class Step:
    #: The stage's id, and never a label: `screen.stage_line` produces it,
    #: `passed` holds it and the diary records it. Two fields rather than one
    #: because a single one had to be both, and lost: the interface reads
    #: English and showed `diseño`.
    name: str
    #: What a person reads where this step is named -- the wizard's head and
    #: its progress strip. Translating this translates the screen; translating
    #: `name` would rename the stage.
    title: str
    number: int
    summary: str
    action_label: str
    costs_api: bool
    state: StepState
    detail: str = ""
    editable: bool = False
    skippable: bool = False


#: name, title, summary, action label, costs API, editable, skippable.
#:
#: The title, the summary and the action label are what a person reads, and
#: they are English like the rest of the interface. The *name* is not prose:
#: it is the id `screen.stage_line` writes, `passed` holds and the diary
#: records, and renaming it would be renaming the stage rather than
#: translating a label. That is why every entry carries
#: both -- and why the diary goes on writing the name: a log that translates
#: is a log that cannot be searched, and a `studio.log` begun in one language
#: and continued in another is a log nobody can read.
#:
#: `referencia` and `sprites` are skippable because they are optional in the
#: pipeline itself, not as a convenience: a game need not be based on a real
#: one, and a game without sprite art is drawn with characters. Demanding
#: "done" from them would invent a requirement the pipeline does not have.
_PIPELINE: tuple[tuple[str, str, str, str, bool, bool, bool], ...] = (
    (
        "referencia",
        "Reference",
        "Search the web for the real game and archive its cited dossier",
        "research",
        True,
        False,
        True,
    ),
    ("diseño", "Design", "Review and adjust the design", "edit", False, True, False),
    ("sprites", "Sprites", "Draw the art any entity is missing", "draw", True, False, True),
    (
        "programa",
        "Program",
        "Write the game in C and repair it against the compiler",
        "write",
        True,
        False,
        False,
    ),
    (
        "gates",
        "Gates",
        "Build it, run it in the emulator and pass the gates",
        "test",
        False,
        False,
        False,
    ),
    ("release", "Release", "Package the zip with its evidence", "publish", False, False, False),
)

#: Step zero is the wizard's own: `stage_line` knows the six pipeline stages
#: and nothing about whether a project is open, because "I have a project
#: open" is not evidence anybody leaves on disk. It is the one step whose
#: state this module decides rather than reads.
_PROJECT_STEP = Step(
    number=0,
    name="proyecto",
    title="Project",
    summary="Choose a project from the workspace, or start a new one",
    action_label="open",
    costs_api=False,
    state="pending",
)


def steps(
    project: GameProject | None,
    directory: Path | None,
    passed: Iterable[str] = (),
) -> list[Step]:
    """The seven steps, in order, with the state each one is in right now."""
    left_behind = set(passed)
    stages = {stage.name: stage for stage in stage_line(project, directory)}
    walked = [replace(_PROJECT_STEP, state="done" if project is not None else "pending")]
    for number, (name, title, summary, label, costs, editable, skippable) in enumerate(
        _PIPELINE, start=1
    ):
        stage = stages.get(name)
        state: StepState = stage.state if stage is not None else "pending"
        #: Left behind without being done is what "skipped" means; left behind
        #: after being done is just having moved on, and says nothing extra.
        if name in left_behind and state == "pending":
            state = "skipped"
        walked.append(
            Step(
                number=number,
                name=name,
                title=title,
                summary=summary,
                action_label=label,
                costs_api=costs,
                state=state,
                detail=stage.detail if stage is not None else "",
                editable=editable,
                skippable=skippable,
            )
        )
    return walked


def current(
    project: GameProject | None,
    directory: Path | None,
    passed: Iterable[str] = (),
) -> Step:
    """The step the wizard is standing on: the first not yet left behind.

    Not "the first that is not done", which was the first attempt and was
    wrong: `screen._design_stage` never returns `pending` -- a design is either
    `done` or `failed` -- so that rule walked straight past step 2 the moment
    the design validated, and the one step that exists in order to be edited
    would have been the only one never reached.

    A failure still wins over any later step, and for the plainest of
    reasons: there is nothing to gain from pointing at "draw the sprites"
    while the design itself is broken. It wins even over a step already left
    behind, because a design that breaks after being passed is exactly the
    case worth dragging someone back to. `screen.next_step` used to apply the
    same rule over the stages alone; it had no notion of a step being walked
    past, nothing called it, and two answers to "what next" is the drift this
    module's own docstring warns about, so it was deleted rather than kept in
    reserve.

    Once every step has been left behind the last one is returned rather than
    `None`: the wizard always has something to show, and "release, done" is the
    truthful thing to be showing at that point.
    """
    walked = steps(project, directory, passed)
    failed = next((step for step in walked if step.state == "failed"), None)
    if failed is not None:
        return failed
    left_behind = set(passed)
    ahead = next((step for step in walked if step.name not in left_behind), None)
    return ahead if ahead is not None else walked[-1]


def can_leave_behind(step: Step) -> bool:
    """Whether the person may walk past this step right now.

    A resolved step is always behind you once you say so. A pending one is
    only skippable where the pipeline can spare it: it does not need
    `referencia` or `sprites` -- a game need not be based on a real one, and
    one without sprite art is drawn with characters -- but without `programa`
    or `gates` there is nothing to release.
    """
    if step.state in {"done", "skipped"}:
        return True
    return step.skippable
