"""Rebuild a design from what was researched about the real game.

Kept apart from `reference.py` because the two change for different reasons: one
follows where the facts come from, this one follows the design schema. It emits
the same `ProjectProposal` the AI assistant already emits, so it inherits the
diff, the protected paths and the playability refusal for free.
"""

from __future__ import annotations

from typing import Any, Protocol

from .models import GameProject
from .planner import ProjectProposal
from .reference import GameReference

#: Everything the designer is told. It is pointed at the fields that carry a
#: game's identity, and warned off the ones that carry Studio's guarantees:
#: a proposal touching a protected path is refused on apply anyway, and one that
#: seals a level off is refused by the playability gate, so spending changes
#: there only wastes the twenty a proposal is allowed.
DESIGN_SYSTEM_PROMPT = """\
You adapt a game design so it resembles a real 1980s game that has been
researched for you.

Propose JSON-pointer changes to the supplied GameProject. You get at most 20
changes in total, so spend them on whole arrays and whole objects -- a
level's entire `tiles` list, an entity's whole spawn list -- rather than one
row, cell or spawn at a time. Aim them at what makes the game recognisable:
  /levels/N/tiles          the maze or screen layout, as rows of '#' and '.'
  /levels/N/spawns         where each actor starts
  /entities/N/count        how many of each actor
  /entities/N/speed        pacing, 1 is slowest and 4 moves every frame
  /entities/N/behaviour    chase, patrol_h, patrol_v, bounce, guard
  /presentation/style      how it should look, in a short phrase
  /gameplay/lives          lives the player starts with
  /gameplay/difficulty_curve

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
  * Only propose what the dossier supports. Where it says nothing, leave the
    design alone.
  * Give each change a reason that cites what in the dossier motivates it.
"""


class ReferenceDesigner(Protocol):
    def propose(
        self, project: GameProject, dossier: GameReference
    ) -> ProjectProposal: ...


class ResponsesReferenceDesigner:
    """Proposes a design adaptation through the OpenAI Responses API."""

    def __init__(self, client: Any, model: str = "gpt-5") -> None:
        self.client = client
        self.model = model

    def propose(self, project: GameProject, dossier: GameReference) -> ProjectProposal:
        if not dossier.identified:
            raise ValueError(
                "this game was not identified, so there is nothing to adapt the design to"
            )
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": DESIGN_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"RESEARCHED GAME:\n{dossier.model_dump_json(indent=2)}\n\n"
                        f"CURRENT DESIGN:\n{project.model_dump_json(indent=2)}"
                    ),
                },
            ],
            text_format=ProjectProposal,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("the model did not return a structured project proposal")
        return parsed
