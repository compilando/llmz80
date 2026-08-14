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

A `Step` carries five things and no more: `number` and `name` for the diary,
`title` and `state` for the strip, `detail` for the one line under it. It
used to carry a summary, the label of the verb its key performed, whether
that key spent money, and whether a person could edit or skip the step --
`can_leave_behind` decided the last of those. All of it was a wizard naming
its keys, and there is no wizard: `llmz80 make` runs the whole order and the
screen watches it.

For the same reason there is no `skipped` state and no `passed` argument to
carry one. A step was skipped when a person decided to walk past it, and
nothing writes that decision anywhere -- it lived in the session that made
it. So every state here is `screen.StageState`, read off evidence and
nothing else. If a human decision ever re-enters the pipeline it will be a
different decision with a shape of its own, and keeping this one's empty
socket would not help it fit.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from .models import GameProject
from .screen import StageState, stage_line


@dataclass(frozen=True)
class Step:
    #: The stage's id, and never a label: `screen.stage_line` produces it and
    #: the diary records it. Two fields rather than one because a single one
    #: had to be both, and lost: the interface reads English and showed
    #: `diseño`.
    name: str
    #: What a person reads where this step is named, on the progress strip.
    #: Translating this translates the screen; translating `name` would
    #: rename the stage.
    title: str
    number: int
    state: StageState
    detail: str = ""


#: name, title -- the id and the label, which is every field a step still has
#: that is not read off the stage itself.
#:
#: The title is what a person reads, and it is English like the rest of the
#: interface. The *name* is not prose: it is the id `screen.stage_line`
#: writes and the diary records, and renaming it would be renaming the stage
#: rather than translating a label. That is why every entry carries both --
#: and why the diary goes on writing the name: a log that translates is a log
#: that cannot be searched, and a `studio.log` begun in one language and
#: continued in another is a log nobody can read.
_PIPELINE: tuple[tuple[str, str], ...] = (
    ("referencia", "Reference"),
    ("diseño", "Design"),
    ("sprites", "Sprites"),
    ("programa", "Program"),
    ("gates", "Gates"),
    ("release", "Release"),
)

#: Step zero is this module's own: `stage_line` knows the six pipeline stages
#: and nothing about whether a project is open, because "I have a project
#: open" is not evidence anybody leaves on disk. It is the one step whose
#: state this module decides rather than reads.
_PROJECT_STEP = Step(number=0, name="proyecto", title="Project", state="pending")


def steps(project: GameProject | None, directory: Path | None) -> list[Step]:
    """The seven steps, in order, with the state each one is in right now.

    Every state is evidence: what `stage_line` found on disk, plus the one
    thing it does not look for, which is whether there is a project at all.
    Nothing is remembered between calls, so two readers of the same project
    -- the order doing the work and the screen watching it -- cannot disagree
    about where it stands.
    """
    stages = {stage.name: stage for stage in stage_line(project, directory)}
    walked = [replace(_PROJECT_STEP, state="done" if project is not None else "pending")]
    for number, (name, title) in enumerate(_PIPELINE, start=1):
        stage = stages.get(name)
        state: StageState = stage.state if stage is not None else "pending"
        walked.append(
            Step(
                number=number,
                name=name,
                title=title,
                state=state,
                detail=stage.detail if stage is not None else "",
            )
        )
    return walked
