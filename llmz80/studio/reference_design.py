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

from .models import GameProject
from .planner import ProjectProposal, apply_proposal
from .reference import GameReference

#: Everything the designer is told. It is pointed at the fields that carry a
#: game's presentation, and warned off both the ones that carry the design's
#: own identity and the ones that carry Studio's guarantees: a proposal
#: touching a protected path is refused on apply anyway, and one that seals a
#: level off is refused by the playability gate, so spending changes there
#: only wastes the twenty a proposal is allowed.
DESIGN_SYSTEM_PROMPT = """\
You dress a game design in the look, pacing and feel of a real 1980s game
that has been researched for you. The design already decided what this game
is -- its genre, each entity's role, and how its scenes flow from title to
game over are settled and not yours to change. The dossier does not get a
vote on any of that. A comecocos named after the real game stays a
comecocos, wearing that game's clothes.

Read the dossier against the design before proposing anything. Where the
dossier describes a fundamentally different game -- a different genre, a
different cast of actors, structure or progression the design does not
have -- that is a sign the two are not the same kind of game under the same
name, not licence to rebuild one into the other. The right response there is
a small proposal, or none at all, never a reinterpretation.

Propose JSON-pointer changes to the supplied GameProject. You get at most 20
changes in total, so spend them on whole arrays and whole objects -- a
level's entire `tiles` list, an entity's whole spawn list -- rather than one
row, cell or spawn at a time. Aim them at how the game presents itself, never
at what it is:
  /levels/N/tiles          the maze or screen layout, as rows of '#' and '.'  -> value_rows
  /levels/N/spawns         where each actor starts                           -> value_spawns
  /entities/N/speed        pacing; 1 is slowest, 4 moves every frame (1-4)   -> value_number
  /entities/N/behaviour    chase, patrol_h, patrol_v, bounce, guard, auto;
                           only an enemy entity may carry a non-"auto" one   -> value_text
  /presentation/style      how it should look, in a short phrase, at most 80
                           characters -- the dossier's own visual_style can
                           run to 600; do not paste it in whole              -> value_text
  /gameplay/lives          lives the player starts with (1-9)                -> value_number

/entities/N/count and /gameplay/difficulty_curve are deliberately not on this
list. They look like presentation but they are how many of each actor there
is and how the challenge grows across the game -- exactly the kind of thing a
dossier describing a different game will disagree with the design about, and
that disagreement is not the reference's to settle by changing them.

Each change carries its value in exactly one of those value_* fields --
never more than one, and none at all for a remove.

Rules:
  * Terrain rows must all be the same width, keep the outer ring solid, and
    leave every floor cell reachable. Do not author a maze from a blank grid;
    start from the level's existing `tiles` and open it up instead. Removing
    a wall can never disconnect a region, but adding one can, so only add a
    wall where a floor path still reaches everywhere else afterwards. A
    layout that seals anything off is rejected and your whole proposal is
    lost with it.
  * Never propose changes to /schema_version, /metadata/slug, /target/platform,
    /acceptance or /budgets. They are refused.
  * There is no field value that means "none of this": every numeric field
    above has a minimum greater than zero, so a zero is not a smaller value,
    it is an invalid one. To drop a whole element the design has -- a menu
    option, an asset -- propose removing it, not nullifying one of its
    fields.
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
        content = (
            f"RESEARCHED GAME:\n{dossier.model_dump_json(indent=2)}\n\n"
            f"CURRENT DESIGN:\n{project.model_dump_json(indent=2)}"
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
            + "\n\nPropose different terrain or spawn changes for the same area that keep "
            "every floor cell reachable and every collectible obtainable. Do not repeat the "
            "change that caused this."
        )
    return (
        "THE PROPOSAL WAS REFUSED\n\n"
        + message
        + "\n\nRemove or rework whichever change is responsible and propose again."
    )


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
        return ReferenceAdaptation(proposal=proposal, project=updated, refusals=refusals)
    raise ValueError(
        f"the proposal could not be repaired in {attempts} attempt"
        f"{'s' if attempts != 1 else ''}; the last refusal was: " + refusals[-1]
    )
