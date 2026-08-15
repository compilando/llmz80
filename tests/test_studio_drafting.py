"""Turning a brief into a design that states something."""

import pytest

from llmz80.studio.drafting import (
    DraftRefused,
    draft_and_apply,
    drafting_prompt,
    needs_drafting,
)
from llmz80.studio.editing import rename_project
from llmz80.studio.models import TargetPlatform
from llmz80.studio.planner import EntityValue, ProjectChange, ProjectProposal
from llmz80.studio.samples import blank_project


@pytest.fixture
def blank():
    return rename_project(
        blank_project("Harrier", TargetPlatform.SPECTRUM),
        "Harrier",
        brief="un avión de combate que vuela hacia la derecha; hay scroll y van "
        "apareciendo otros cazas, y se disparan entre ambos",
    )


class ScriptedDrafter:
    """A drafter whose proposals are decided in advance, so the loop is
    testable without an API call -- the same shape `tests/test_studio_
    reference_design.py` uses for the designer."""

    def __init__(self, *proposals: ProjectProposal) -> None:
        self.proposals = list(proposals)
        self.feedback_seen: list[str | None] = []

    def draft(self, project, dossier=None, feedback=None):
        self.feedback_seen.append(feedback)
        return self.proposals[min(len(self.feedback_seen), len(self.proposals)) - 1]


def _mechanics(*sentences: str) -> ProjectProposal:
    return ProjectProposal(
        summary="state what the game does",
        changes=[
            ProjectChange(
                path="/mechanics",
                operation="replace",
                reason="the brief says what this game is and the design said nothing",
                value_rows=list(sentences),
            )
        ],
        risks=[],
    )


def test_a_design_that_states_nothing_wants_drafting(blank):
    assert needs_drafting(blank) is True


def test_a_design_that_already_states_its_rules_is_left_alone(blank):
    """A design with mechanics is somebody's. Redrafting it would be the
    reinterpretation `adapt`'s own prompt exists to refuse."""
    stated = blank.model_copy(update={"mechanics": ["el avión dispara misiles"]})

    assert needs_drafting(stated) is False


def test_a_design_with_no_brief_is_not_drafted_either(blank):
    """Nobody has said what this game should be, so there is nothing to draft
    from and inventing one is exactly what this pipeline must not do."""
    briefless = blank.model_copy(
        update={"metadata": blank.metadata.model_copy(update={"brief": ""})}
    )

    assert needs_drafting(briefless) is False


def test_the_prompt_carries_the_brief_and_what_the_design_has_so_far(blank):
    prompt = drafting_prompt(blank, None)

    assert "avión de combate" in prompt
    assert "actor" in prompt
    assert "20x14" in prompt


def test_the_prompt_carries_the_dossier_when_one_was_researched(blank):
    from llmz80.studio.reference import GameReference, ReferenceSource

    dossier = GameReference(
        identified=True,
        confidence="high",
        title="Harrier Attack!",
        mechanics=["el avión despega del portaaviones", "el combustible se agota"],
        sources=[
            ReferenceSource(
                url="https://example.test/x", title="x", retrieved_at="2026-08-15T09:00:00Z"
            )
        ],
    )

    prompt = drafting_prompt(blank, dossier)

    assert "Harrier Attack!" in prompt
    assert "el combustible se agota" in prompt


def test_a_draft_that_states_the_rules_is_applied(blank):
    drafter = ScriptedDrafter(_mechanics("el avión dispara misiles hacia delante"))

    result = draft_and_apply(blank, drafter)

    assert result.project.mechanics == ["el avión dispara misiles hacia delante"]
    assert result.refusals == []


def test_a_draft_that_still_says_nothing_is_tried_again_with_the_reason(blank):
    """The design gate is the drafter's own acceptance test, so failing it is
    feedback rather than the end -- the same repair loop `propose_and_apply`
    runs behind the adaptation stage."""
    drafter = ScriptedDrafter(
        ProjectProposal(summary="nothing", changes=[], risks=[]),
        _mechanics("el avión aterriza en el portaaviones para repostar"),
    )

    result = draft_and_apply(blank, drafter, attempts=2)

    assert result.project.mechanics == ["el avión aterriza en el portaaviones para repostar"]
    assert len(result.refusals) == 1
    assert "mechanics" in result.refusals[0]
    assert drafter.feedback_seen[1] is not None


def test_a_drafter_that_never_states_anything_is_refused_with_what_it_kept_missing(blank):
    drafter = ScriptedDrafter(ProjectProposal(summary="nothing", changes=[], risks=[]))

    with pytest.raises(DraftRefused, match="mechanics"):
        draft_and_apply(blank, drafter, attempts=2)


def test_a_draft_that_adds_the_cast_the_brief_asks_for_is_applied(blank):
    """The stage exists to grow a design, not only to annotate one: the brief
    names enemy fighters and the blank project has a single `actor`. This is
    the path `/entities/-` was added for, end to end through the loop."""
    drafter = ScriptedDrafter(
        ProjectProposal(
            summary="give the design its cast and its rules",
            changes=[
                ProjectChange(
                    path="/entities/-",
                    operation="add",
                    reason="the brief asks for other fighters and the design has none",
                    value_entity=EntityValue(
                        id="caza", kind="enemigo", count=3, notes="dispara al jugador"
                    ),
                ),
                ProjectChange(
                    path="/mechanics",
                    operation="replace",
                    reason="the brief says the two sides shoot at each other",
                    value_rows=["los cazas y el jugador se disparan entre ellos"],
                ),
            ],
            risks=[],
        )
    )

    result = draft_and_apply(blank, drafter)

    assert [entity.id for entity in result.project.entities] == ["actor", "caza"]
    assert result.project.entities[1].notes == "dispara al jugador"


def test_a_draft_the_document_refuses_is_repaired_rather_than_abandoned(blank):
    """A drafter proposing an entity id the schema refuses gets the refusal
    back as feedback, the same way a refused adaptation does -- the drafter's
    reach is wider than the designer's, so it has more ways to be wrong."""
    refused = ProjectProposal(
        summary="add an entity the schema will not have",
        changes=[
            ProjectChange(
                path="/entities/-",
                operation="add",
                reason="the brief asks for other fighters",
                value_entity=EntityValue(id="Caza Enemigo", kind="enemigo"),
            )
        ],
        risks=[],
    )
    drafter = ScriptedDrafter(refused, _mechanics("los cazas persiguen al jugador"))

    result = draft_and_apply(blank, drafter, attempts=2)

    assert result.project.mechanics == ["los cazas persiguen al jugador"]
    assert len(result.refusals) == 1
    assert "entities" in result.refusals[0]
    assert "REFUSED" in (drafter.feedback_seen[1] or "")
