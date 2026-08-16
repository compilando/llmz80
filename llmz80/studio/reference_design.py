"""Rebuild a design from what was researched about the real game.

Kept apart from `reference.py` because the two change for different reasons: one
follows where the facts come from, this one follows the design schema. It emits
the same `ProjectProposal` the AI assistant already emits, so it inherits the
diff, the protected paths and the playability refusal for free.
"""

from __future__ import annotations

from typing import Any, Protocol

from .design_exam import DesignExaminer, coverage_errors
from .models import GameProject
from .planner import AppliedProposal, ProjectProposal, propose_apply_repair
from .reference import GameReference
from .typologies import typology_hints

#: Everything the designer is told. It is pointed at the fields that carry a
#: game's presentation, and warned off both the ones that carry the design's
#: own identity and the ones that carry Studio's guarantees: a proposal
#: touching a protected path is refused on apply anyway, and one that
#: outgrows the target's playable grid is refused by `GameProject`'s own
#: validation, so spending changes there only wastes the twenty a proposal
#: is allowed.
DESIGN_SYSTEM_PROMPT = """\
You dress a game design in the look, pacing and feel of a real 1980s game
that has been researched for you. The design already decided what this game
is -- each entity's kind, the mechanics it declares, and how its screens
connect are settled and not yours to change. The dossier does not get a
vote on any of that. A comecocos named after the real game stays a
comecocos, wearing that game's clothes.

Read the dossier against the design before proposing anything. Where the
dossier is a different kind of game -- a different cast of actors,
structure or progression the design does not have -- that is a sign the
two are not the same kind of game under the same name, not licence to
rebuild one into the other. The right response there is a small proposal,
or none at all, never a reinterpretation.

Propose JSON-pointer changes to the supplied GameProject. You get at most 20
changes in total, so spend them on whole arrays and whole objects -- a
screen's entire `tiles` list, an entity's whole spawn list -- rather than one
row, cell or spawn at a time. Aim them at how the game presents itself, never
at what it is:
  /screens/N/tiles          the screen layout, as rows of the design's own
                             tile characters                             -> {"rows": [...]}
  /screens/N/spawns         where each actor starts                      -> {"spawns": [...]}
  /mechanics                what the game does, one sentence each        -> {"rows": [...]}
  /entities/N/notes         what this actor does                         -> {"text": ...}
  /presentation/style       how it should look, in a short phrase, at most 80
                             characters -- the dossier's own visual_style can
                             run to 600; do not paste it in whole         -> {"text": ...}

/entities/N/count is deliberately not on this list. It looks like
presentation but it is how many of each actor there is -- exactly the kind
of thing a dossier describing a different game will disagree with the
design about, and that disagreement is not the reference's to settle by
changing it.

Each change carries its value in `value`, as one object of the shape shown
above -- never a mixture of two shapes, and null for a remove.

Rules:
  * A screen's terrain rows must all match its declared width and height
    exactly, and use only tile characters the design itself declares under
    `/tiles` -- anything else is rejected outright. Start from the screen's
    existing `tiles` and edit it, rather than authoring a new layout from a
    blank grid, so whatever does not need to change survives untouched.
  * Never propose changes to /schema_version, /metadata/slug, /target/platform,
    /acceptance or /budgets. They are refused.
  * There is no field value that means "none of this": to drop a whole
    element the design has -- a mechanic, a menu option, an asset -- propose
    removing it, not writing an empty string in its place.
  * Only propose what the dossier supports. Where it says nothing, leave the
    design alone.
  * Give each change a reason that cites what in the dossier motivates it.
"""


class ReferenceDesigner(Protocol):
    def propose(
        self, project: GameProject, dossier: GameReference, feedback: str | None = None
    ) -> ProjectProposal: ...


class ResponsesReferenceDesigner:
    """Proposes a design adaptation through the OpenAI Responses API."""

    def __init__(self, client: Any, model: str = "gpt-5") -> None:
        self.client = client
        self.model = model

    def propose(
        self, project: GameProject, dossier: GameReference, feedback: str | None = None
    ) -> ProjectProposal:
        if not dossier.identified:
            raise ValueError(
                "this game was not identified, so there is nothing to adapt the design to"
            )
        content = "\n\n".join(
            [
                typology_hints(),
                f"RESEARCHED GAME:\n{dossier.model_dump_json(indent=2)}",
                f"CURRENT DESIGN:\n{project.model_dump_json(indent=2)}",
            ]
        )
        if feedback:
            content += "\n\nYOUR PREVIOUS PROPOSAL WAS REJECTED\n\n" + feedback
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": DESIGN_SYSTEM_PROMPT},
                {"role": "user", "content": content},
            ],
            text_format=ProjectProposal,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("the model did not return a structured project proposal")
        return parsed


def coverage_feedback(errors: list[str]) -> str:
    """Turn the examiner's gaps into an instruction the designer can act on.

    Pointed at the two fields where a missed brief is actually fixable from
    here. The designer's allowed targets are the ones `DESIGN_SYSTEM_PROMPT`
    lists, and the entity roster is not among them -- a design with no enemy
    entity cannot grow one through a proposal, and a designer that tries burns
    an attempt on a path `apply_proposal` refuses. So this says where to state
    the missing thing, and says plainly what it must not try instead.
    """
    return "\n".join(
        [
            "THE PROPOSAL APPLIED BUT THE DESIGN STILL DOES NOT ANSWER ITS BRIEF",
            "",
            *(f"  {gap}" for gap in errors),
            "",
            "State each of these in the design. `/mechanics` is where what the "
            "game does belongs -- one sentence per rule, in the design's own "
            "words -- and `/entities/N/notes` is where what a particular actor "
            "does belongs. Both are yours to propose.",
            "",
            "Do not try to add, remove or renumber entities, screens or scenes to "
            "close a gap: those paths are refused, and the attempt is lost. Where "
            "the design has no actor for something the brief asks for, say what "
            "the actor it does have must do about it.",
        ]
    )


def _coverage_gaps(project: GameProject, examiner: DesignExaminer | None) -> list[str]:
    """What the examiner says this design fails to state, or nothing.

    Nothing, and no model call, when there is no examiner (every offline
    caller, and every test that injects only a designer) or when the project
    carries no brief -- a design with nothing asked of it cannot fall short of
    it, and asking a model to judge coverage of an empty brief spends a call
    to be told something obvious.
    """
    if examiner is None or not project.metadata.brief.strip():
        return []
    return coverage_errors(examiner.examine(project))


def propose_and_apply(
    project: GameProject,
    dossier: GameReference,
    designer: ReferenceDesigner,
    *,
    attempts: int = 3,
    allow_budget_changes: bool = False,
    allow_unplayable: bool = False,
    examiner: DesignExaminer | None = None,
) -> AppliedProposal:
    """Propose a design adaptation and validate it through `apply_proposal`,
    repairing a mechanically refused proposal instead of discarding the whole
    thing.

    The loop itself is `planner.propose_apply_repair`, shared with `drafting`
    since that stage grew one of the same shape. What is this stage's own is
    the two things below: the designer is handed the dossier, and a proposal
    is only accepted once the design answers its brief.

    An `examiner` adds a second reason to try again, and the one that matters
    most: a proposal can apply cleanly and still leave a design that says
    nothing about what its brief asked for. `studio-projects/zampabolas` and
    `studio-projects/my-retro-game` both reached the writer with
    `mechanics: []` -- the second of them from a dossier that had correctly
    identified Harrier Attack! -- so the stage that is supposed to turn
    research into a design had never once produced a design with mechanics. A refusal alone would only have closed a door in
    front of that; feeding the gaps back as feedback is what gives the
    designer the chance to state them.

    Raises `ValueError` carrying the last refusal reason once attempts run
    out, so a user who burned several model calls learns what finally went
    wrong rather than getting a generic failure.
    """

    def review(updated: GameProject) -> tuple[str, str] | None:
        gaps = _coverage_gaps(updated, examiner)
        if not gaps:
            return None
        return (
            "the design still does not state what the brief asks for: " + "; ".join(gaps),
            coverage_feedback(gaps),
        )

    return propose_apply_repair(
        project,
        lambda feedback: designer.propose(project, dossier, feedback),
        review,
        attempts=attempts,
        allow_budget_changes=allow_budget_changes,
        allow_unplayable=allow_unplayable,
    )
