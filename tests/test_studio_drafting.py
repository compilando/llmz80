"""Turning a brief into a design that states something."""

import pytest

from llmz80.studio.design_exam import DesignCoherence
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
    """A draft that states its rules and has answered the observability
    question, which is what every accepted draft looks like: one that declares
    no observables and says nothing about why is sent back once, so a helper
    that left the note empty would put a repair into every test that uses
    it."""
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
        observability="none: these rules are about where things are on screen, "
        "and none of them leaves a count behind",
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


def _mechanics_without_the_observability_note(*sentences: str) -> ProjectProposal:
    """The draft this nudge exists for: rules stated, observables none, and
    nothing recorded about whether any rule could be watched from outside."""
    proposal = _mechanics(*sentences)
    return proposal.model_copy(update={"observability": ""})


def test_a_draft_that_never_considered_whether_this_game_can_be_watched_is_asked_once(blank):
    """Declaring no observables is a legitimate answer, so the second draft is
    accepted with none -- what the nudge buys is that the question was asked.
    Demanding a symbol instead would be answered with one invented to satisfy
    the gate, which is why `minero-observable`'s two useful observables and
    `una-rana-que-cruza-una`'s missing car are different problems."""
    drafter = ScriptedDrafter(
        _mechanics_without_the_observability_note("el avión dispara misiles hacia delante"),
        _mechanics("el avión dispara misiles hacia delante"),
    )

    result = draft_and_apply(blank, drafter, attempts=3)

    assert result.project.observables == []
    assert len(result.refusals) == 1
    assert "watched from outside" in result.refusals[0]
    assert "/observables/-" in (drafter.feedback_seen[1] or "")


def test_the_observability_nudge_never_spends_the_last_attempt_a_draft_has(blank):
    """A drafter that keeps leaving the note empty has still written a design
    the two real gates accept, and losing it over a missing sentence would
    cost a correct game its draft -- the false failure this stage is built to
    avoid. With one attempt the question is not even asked."""
    drafter = ScriptedDrafter(
        _mechanics_without_the_observability_note("el avión dispara misiles hacia delante")
    )

    result = draft_and_apply(blank, drafter, attempts=1)

    assert result.project.mechanics == ["el avión dispara misiles hacia delante"]
    assert result.refusals == []


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


class _FakeResponses:
    def __init__(self, parsed):
        self.parsed = parsed
        self.calls = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        return type("Response", (), {"output_parsed": self.parsed})()


class _FakeClient:
    def __init__(self, parsed):
        self.responses = _FakeResponses(parsed)


def test_the_request_carries_the_brief_the_design_and_what_kinds_of_game_exist(blank):
    from llmz80.studio.drafting import DRAFT_SYSTEM_PROMPT, ResponsesDesignDrafter

    client = _FakeClient(_mechanics("el avión dispara misiles"))

    ResponsesDesignDrafter(client).draft(blank)

    sent = client.responses.calls[0]["input"]
    assert sent[0]["content"] == DRAFT_SYSTEM_PROMPT
    assert "avión de combate" in sent[1]["content"]
    assert "Mechanics: none stated" in sent[1]["content"]
    assert "KINDS OF GAME THAT EXIST" in sent[1]["content"]


def test_a_rejected_draft_is_sent_back_with_what_rejected_it(blank):
    """Without this the repair loop would ask the same question three times
    and pay for the same answer three times."""
    from llmz80.studio.drafting import ResponsesDesignDrafter

    client = _FakeClient(_mechanics("el avión dispara misiles"))

    ResponsesDesignDrafter(client).draft(blank, None, "THE DRAFT APPLIED BUT ...")

    assert "THE DRAFT APPLIED BUT ..." in client.responses.calls[0]["input"][1]["content"]


def test_a_project_with_no_brief_is_not_drafted_from_even_here(blank):
    """`needs_drafting` already keeps the stage from calling this, so reaching
    it means a caller went round the stage -- and inventing the brief is the
    one thing this pipeline must not do, whichever door it is asked through."""
    from llmz80.studio.drafting import ResponsesDesignDrafter

    briefless = blank.model_copy(
        update={"metadata": blank.metadata.model_copy(update={"brief": ""})}
    )
    client = _FakeClient(_mechanics("lo que sea"))

    with pytest.raises(ValueError, match="no brief"):
        ResponsesDesignDrafter(client).draft(briefless)

    assert client.responses.calls == []


def test_a_call_that_returns_nothing_parsed_is_not_silently_accepted(blank):
    """The API contract allows a response with no structured output; a draft
    must not hand that back as if it were a design."""
    from llmz80.studio.drafting import ResponsesDesignDrafter

    client = _FakeClient(None)

    with pytest.raises(ValueError, match="did not return a structured project proposal"):
        ResponsesDesignDrafter(client).draft(blank)

    assert len(client.responses.calls) == 1


# --- the design that assumes a car it never declares ------------------------
#
# The incident this gate exists for. Run on "una rana que cruza una carretera
# esquivando coches", drafting produced the five mechanics reconstructed
# below -- three of them naming coches -- and left `/entities` at the blank
# project's single default `actor` and `/tiles` at wall and floor. The design
# gate passed it, because `mechanics` is not empty; `design_exam`'s brief
# examiner passed it too, because it reads those same mechanics as the
# evidence the brief is served, and the drafter had written them. The design
# on disk is `studio-projects/una-rana-que-cruza-una/game.yml`.


class ScriptedCoherenceExaminer:
    """A coherence examiner whose verdicts are decided in advance. The last
    verdict repeats, the way a model that keeps seeing the same gap would."""

    def __init__(self, *verdicts: DesignCoherence) -> None:
        self.verdicts = list(verdicts)
        self.seen = []

    def examine(self, project):
        self.seen.append(project)
        return self.verdicts[min(len(self.seen), len(self.verdicts)) - 1]


@pytest.fixture
def frog():
    return rename_project(
        blank_project("Una Rana Que Cruza Una", TargetPlatform.SPECTRUM),
        "una rana que cruza una",
        brief="una rana que cruza una carretera esquivando coches",
    )


def _the_frog_draft_that_shipped() -> ProjectProposal:
    """The draft that reached the writer: mechanics that talk about coches and
    an entity roster nobody touched."""
    return _mechanics(
        "El jugador controla una rana que se mueve una casilla por pulsación en "
        "las direcciones arriba, abajo, izquierda y derecha.",
        "La rana comienza en el borde inferior de la pantalla, frente a una "
        "carretera compuesta por carriles con coches en movimiento.",
        "Los coches se desplazan horizontalmente por sus carriles; si la rana "
        "toca un coche en cualquier momento, es atropellada.",
        "Si la rana es atropellada por un coche, la partida se pierde de inmediato.",
        "El objetivo es cruzar la carretera y alcanzar la zona segura en el borde "
        "superior de la pantalla sin ser atropellada.",
    )


def _no_car_declared() -> DesignCoherence:
    return DesignCoherence(
        coherent=False,
        missing_entities=["coche"],
        missing_tiles=[],
        quoted="Los coches se desplazan horizontalmente por sus carriles; si la "
        "rana toca un coche en cualquier momento, es atropellada.",
    )


def test_a_draft_whose_mechanics_assume_a_car_it_never_declares_is_tried_again(frog):
    drafter = ScriptedDrafter(
        _the_frog_draft_that_shipped(),
        ProjectProposal(
            summary="declare the car the mechanics already talk about",
            changes=[
                ProjectChange(
                    path="/entities/-",
                    operation="add",
                    reason="three mechanics name coches and the design declared none",
                    value_entity=EntityValue(
                        id="coche", kind="enemigo", count=4, notes="recorre su carril"
                    ),
                ),
                ProjectChange(
                    path="/mechanics",
                    operation="replace",
                    reason="the rules are unchanged; the cast is what was missing",
                    value_rows=["Los coches recorren sus carriles y atropellan a la rana."],
                ),
            ],
            risks=[],
        ),
    )
    examiner = ScriptedCoherenceExaminer(
        _no_car_declared(),
        DesignCoherence(coherent=True, missing_entities=[], missing_tiles=[], quoted=""),
    )

    result = draft_and_apply(frog, drafter, attempts=2, examiner=examiner)

    assert [entity.id for entity in result.project.entities] == ["actor", "coche"]
    assert len(result.refusals) == 1
    assert "coche" in result.refusals[0]
    feedback = drafter.feedback_seen[1]
    assert feedback is not None
    assert "coche" in feedback
    assert "/entities/-" in feedback and "/tiles/-" in feedback


def test_the_coherence_gate_never_spends_the_last_attempt_a_draft_has(frog):
    """A drafter that keeps assuming the car is sent back while attempts
    remain and then let through on its last one, examiner unasked.

    This is the trade the gate is worth making. Its verdict is a model's
    judgement about prose, and it was measured getting that judgement wrong on
    designs that are correct: over eight runs it refused
    `studio-projects/minero-observable` seven times for "no tile is declared
    for earth" against a tile declared `dirt`. Ending the stage on such a
    verdict costs a working design its whole draft and hundreds of seconds of
    API; letting a real gap through on the last attempt costs coverage only,
    and the gap was still named twice on the way. `design_exam`'s prompt is
    what makes the verdict better; this is what stops any verdict being fatal.
    """
    drafter = ScriptedDrafter(_the_frog_draft_that_shipped())
    examiner = ScriptedCoherenceExaminer(_no_car_declared())

    result = draft_and_apply(frog, drafter, attempts=3, examiner=examiner)

    assert len(examiner.seen) == 2
    assert len(result.refusals) == 2
    assert all("coche" in refusal for refusal in result.refusals)
    assert result.project.mechanics == _the_frog_draft_that_shipped().changes[0].value_rows


def test_a_draft_that_states_no_mechanics_is_never_sent_to_the_coherence_examiner(frog):
    """The design gate has already sent it back in words the drafter can act
    on, and a design with no mechanics has nothing that could assume
    anything -- so the call would be paid for to say the obvious."""
    drafter = ScriptedDrafter(ProjectProposal(summary="nothing", changes=[], risks=[]))
    examiner = ScriptedCoherenceExaminer(_no_car_declared())

    with pytest.raises(DraftRefused, match="mechanics"):
        draft_and_apply(frog, drafter, attempts=2, examiner=examiner)

    assert examiner.seen == []


def test_without_an_examiner_no_second_question_is_asked(frog):
    """Every offline caller and every existing test injects a drafter alone;
    none of them may start making a call they did not ask for."""
    drafter = ScriptedDrafter(_the_frog_draft_that_shipped())

    result = draft_and_apply(frog, drafter)

    assert result.refusals == []
