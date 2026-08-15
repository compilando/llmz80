"""Rebuild a design from what was researched about the real game.

Kept apart from `reference.py` because the two change for different reasons: one
follows where the facts come from, this one follows the design schema. It emits
the same `ProjectProposal` the AI assistant already emits, so it inherits the
diff, the protected paths and the playability refusal for free.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from pydantic import ValidationError

from .design_exam import DesignExaminer, coverage_errors
from .models import GameProject
from .planner import ProjectProposal, apply_proposal
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
                             tile characters                             -> value_rows
  /screens/N/spawns         where each actor starts                      -> value_spawns
  /mechanics                what the game does, one sentence each        -> value_rows
  /entities/N/notes         what this actor does                         -> value_text
  /presentation/style       how it should look, in a short phrase, at most 80
                             characters -- the dossier's own visual_style can
                             run to 600; do not paste it in whole         -> value_text

/entities/N/count is deliberately not on this list. It looks like
presentation but it is how many of each actor there is -- exactly the kind
of thing a dossier describing a different game will disagree with the
design about, and that disagreement is not the reference's to settle by
changing it.

Each change carries its value in exactly one of those value_* fields --
never more than one, and none at all for a remove.

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


def repair_feedback(error: ValueError) -> str:
    """Turn a refusal from `apply_proposal` into an instruction the model can
    act on, the way `generator.repair_prompt` turns a failed build or a wrong
    reading into one.

    The two shapes `apply_proposal` raises deserve different handling. A
    `pydantic.ValidationError` names the exact fields that ended up outside
    their bounds once the changes were applied -- `presentation.style` too
    long, `entities.1.count` below its minimum -- so it is unpacked field by
    field rather than passed through as one opaque message. Everything else
    -- a protected path, a bad JSON pointer, the playability gate's refusal --
    already reads as a sentence a person wrote, so it is quoted whole and
    paired with what to do about it.
    """
    if isinstance(error, ValidationError):
        lines = [
            "THE PROPOSAL WAS REFUSED: THESE FIELDS ENDED UP OUTSIDE THEIR BOUNDS",
            "",
        ]
        for item in error.errors():
            path = "/" + "/".join(str(part) for part in item["loc"])
            lines.append(f"  {path}: {item['msg']}")
        lines.append("")
        lines.append(
            "Rewrite only the changes that set these fields so the result stays inside "
            "each bound. Leave every other change exactly as it was."
        )
        return "\n".join(lines)
    message = str(error)
    if message.startswith("this proposal would leave the game unplayable"):
        return (
            "THE PROPOSAL WAS REFUSED: IT WOULD LEAVE THE GAME UNPLAYABLE\n\n"
            + message
            + "\n\nPropose a screen that fits the target's playable grid instead -- a "
            "smaller width or height, or terrain that still fits the one already "
            "declared. Do not repeat the change that caused this."
        )
    return (
        "THE PROPOSAL WAS REFUSED\n\n"
        + message
        + "\n\nRemove or rework whichever change is responsible and propose again."
    )


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


@dataclass
class ReferenceAdaptation:
    """What the repair loop produced: the proposal that finally applied, the
    project `apply_proposal` already built while checking it, and the refusal
    each earlier attempt drew, oldest first."""

    proposal: ProjectProposal
    project: GameProject
    refusals: list[str] = field(default_factory=list)


def propose_and_apply(
    project: GameProject,
    dossier: GameReference,
    designer: ReferenceDesigner,
    *,
    attempts: int = 3,
    allow_budget_changes: bool = False,
    allow_unplayable: bool = False,
    examiner: DesignExaminer | None = None,
) -> ReferenceAdaptation:
    """Propose a design adaptation and validate it through `apply_proposal`,
    repairing a mechanically refused proposal instead of discarding the whole
    thing -- the way `generator.write_program` repairs a program that failed
    to build rather than giving up on the first rejection.

    `apply_proposal` never mutates `project` or touches disk; it only builds
    and validates a candidate `GameProject` in memory. That means the loop can
    run to a validated result before anyone has agreed to anything, and the
    project this returns is exactly the one a caller would get by calling
    `apply_proposal` again with the same inputs -- so a caller who wants
    consent first can show the diff, ask, and on "yes" use the project already
    computed here instead of redoing the work.

    An `examiner` adds a second reason to try again, and the one that matters
    most: a proposal can apply cleanly and still leave a design that says
    nothing about what its brief asked for. Both v4 projects in this
    repository reached the writer with `mechanics: []` -- one of them from a
    dossier that had correctly identified Harrier Attack! -- so the stage that
    is supposed to turn research into a design had never once produced a
    design with mechanics. A refusal alone would only have closed a door in
    front of that; feeding the gaps back as feedback is what gives the
    designer the chance to state them.

    Raises `ValueError` carrying the last refusal reason once attempts run
    out, so a user who burned several model calls learns what finally went
    wrong rather than getting a generic failure.
    """
    refusals: list[str] = []
    feedback: str | None = None
    for _ in range(max(1, attempts)):
        proposal = designer.propose(project, dossier, feedback)
        try:
            updated = apply_proposal(
                project,
                proposal,
                allow_budget_changes=allow_budget_changes,
                allow_unplayable=allow_unplayable,
            )
        except ValueError as exc:
            refusals.append(str(exc))
            feedback = repair_feedback(exc)
            continue
        gaps = _coverage_gaps(updated, examiner)
        if gaps:
            refusals.append(
                "the design still does not state what the brief asks for: " + "; ".join(gaps)
            )
            feedback = coverage_feedback(gaps)
            continue
        return ReferenceAdaptation(proposal=proposal, project=updated, refusals=refusals)
    raise ValueError(
        f"the proposal could not be repaired in {attempts} attempt"
        f"{'s' if attempts != 1 else ''}; the last refusal was: " + refusals[-1]
    )
