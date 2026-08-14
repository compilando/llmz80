"""Which step the person is on, and what pressing Enter would do.

A pure state machine over `screen.stage_line`. That module already decides
what has been done, from the design in memory and the evidence the pipeline
left on disk; this one adds the three things it does not have: the order, the
words to put on screen, and the rule for what comes next. It deliberately does
not re-derive any of the "is this done" logic -- two answers to that question
would drift apart within a week.

Nothing here draws, calls an API or touches disk, which is what lets the whole
flow be tested without starting Textual, exactly as `render_map` and
`stage_line` already are.
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
    number: int
    name: str
    summary: str
    action_label: str
    costs_api: bool
    state: StepState
    detail: str = ""
    editable: bool = False
    skippable: bool = False


#: name, summary, action label, costs API, editable, skippable.
#:
#: `referencia` and `sprites` are skippable because they are optional in the
#: pipeline itself, not as a convenience: a game need not be based on a real
#: one, and a game without sprite art is drawn with characters. Demanding
#: "done" from them would invent a requirement the pipeline does not have.
_PIPELINE: tuple[tuple[str, str, str, bool, bool, bool], ...] = (
    (
        "referencia",
        "Buscar el juego real en la web y archivar su ficha citada",
        "investigar",
        True,
        False,
        True,
    ),
    ("diseño", "Revisar y ajustar el diseño", "editar", False, True, False),
    ("sprites", "Dibujar el arte que le falte a alguna entidad", "dibujar", True, False, True),
    (
        "programa",
        "Escribir el juego en C y repararlo contra el compilador",
        "escribir",
        True,
        False,
        False,
    ),
    (
        "gates",
        "Compilar, ejecutar en el emulador y pasar las puertas",
        "probar",
        False,
        False,
        False,
    ),
    ("release", "Empaquetar el zip con su evidencia", "publicar", False, False, False),
)

#: Step zero is the wizard's own: `stage_line` knows the six pipeline stages
#: and nothing about whether a project is open, because "I have a project
#: open" is not evidence anybody leaves on disk. It is the one step whose
#: state this module decides rather than reads.
_PROJECT_STEP = Step(
    number=0,
    name="proyecto",
    summary="Elegir un proyecto del workspace, o crear uno nuevo",
    action_label="abrir",
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
    for number, (name, summary, label, costs, editable, skippable) in enumerate(_PIPELINE, start=1):
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
