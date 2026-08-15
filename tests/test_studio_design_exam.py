"""Does the design state what its own brief asked for."""

import pytest

from llmz80.studio.design_exam import (
    BriefCoverage,
    coverage_errors,
    design_summary,
    examination_prompt,
)
from llmz80.studio.editing import rename_project
from llmz80.studio.models import TargetPlatform
from llmz80.studio.planner import ProjectChange, ProjectProposal
from llmz80.studio.reference import GameReference, save_reference
from llmz80.studio.reference_design import coverage_feedback, propose_and_apply
from llmz80.studio.samples import blank_project
from llmz80.studio.services import StudioService


@pytest.fixture
def flying_project():
    return rename_project(
        blank_project("My Retro Game", TargetPlatform.SPECTRUM),
        "My Retro Game",
        brief="un avión de combate que vuela hacia la derecha. hay scroll y van "
        "apareciendo otros cazas, y se disparan entre ambos.",
    )


def test_the_prompt_carries_the_brief_and_what_the_design_actually_states(flying_project):
    prompt = examination_prompt(flying_project)

    assert "avión de combate" in prompt
    assert "20x14" in prompt


def test_an_uncovered_brief_becomes_an_error_naming_what_is_missing():
    coverage = BriefCoverage(
        covered=False,
        missing=["el brief pide scroll y el diseño declara una sola pantalla fija"],
        quoted="hay scroll",
    )

    errors = coverage_errors(coverage)

    assert len(errors) == 1
    assert "scroll" in errors[0]
    assert "hay scroll" in errors[0]


def test_a_covered_brief_is_no_error():
    assert coverage_errors(BriefCoverage(covered=True, missing=[], quoted="")) == []


def test_a_covered_verdict_that_still_lists_gaps_is_read_as_uncovered():
    """A model that says yes and then lists what is missing has contradicted
    itself, and the safe reading of a contradiction is the one that does not
    let a design through."""
    coverage = BriefCoverage(covered=True, missing=["no hay enemigos"], quoted="otros cazas")

    assert coverage_errors(coverage) != []


# --- the examiner inside the repair loop -----------------------------------
#
# The finding this task exists for: the adapt stage had never once produced a
# design with mechanics in this repository -- not even for `my-retro-game`,
# whose dossier correctly identified Harrier Attack!. A refusal alone would
# have closed a door in front of that stage. These tests prove the gaps go
# back to the designer as feedback first, and that a refusal is what is left
# once the attempts are spent.


def _dossier() -> GameReference:
    return GameReference.model_validate(
        {
            "identified": True,
            "confidence": "high",
            "title": "Harrier Attack!",
            "publisher": "Durell Software",
            "year": 1983,
            "platforms": ["spectrum"],
            "mechanics": ["fly right", "enemy fighters appear", "both sides shoot"],
            "sources": [
                {
                    "url": "https://example.org/harrier",
                    "title": "Harrier Attack!",
                    "retrieved_at": "2026-08-14T09:00:00Z",
                }
            ],
        }
    )


class ScriptedDesigner:
    """A designer whose attempts are decided in advance. Mirrors the one in
    `tests/test_studio_reference_design.py`, kept here rather than shared so
    each test file still reads on its own."""

    def __init__(self, *attempts: ProjectProposal) -> None:
        self.attempts = list(attempts)
        self.feedback_seen: list[str | None] = []

    def propose(self, project, dossier, feedback=None):
        self.feedback_seen.append(feedback)
        return self.attempts[min(len(self.feedback_seen), len(self.attempts)) - 1]


class ScriptedExaminer:
    """An examiner whose verdicts are decided in advance, so the loop is
    testable without spending a model call. The last verdict repeats, the way
    a model that keeps seeing the same gap would."""

    def __init__(self, *verdicts: BriefCoverage) -> None:
        self.verdicts = list(verdicts)
        self.seen = []

    def examine(self, project):
        self.seen.append(project)
        return self.verdicts[min(len(self.seen), len(self.verdicts)) - 1]


def _mechanics_proposal(*sentences: str) -> ProjectProposal:
    return ProjectProposal(
        summary="say what the game does",
        changes=[
            ProjectChange(
                path="/mechanics",
                operation="replace",
                value_rows=list(sentences),
                reason="the dossier describes these",
            )
        ],
    )


def _uncovered() -> BriefCoverage:
    return BriefCoverage(
        covered=False,
        missing=["the brief asks for enemy fighters and the design states no mechanics"],
        quoted="van apareciendo otros cazas",
    )


def _covered() -> BriefCoverage:
    return BriefCoverage(covered=True, missing=[], quoted="")


def test_a_design_that_misses_its_brief_is_repaired_rather_than_refused(flying_project):
    """The whole point of feeding the examiner into the loop: the first
    attempt states nothing, and the second one -- told what was missing --
    is the design that gets returned."""
    designer = ScriptedDesigner(
        _mechanics_proposal("the plane moves"),
        _mechanics_proposal("the plane flies right", "enemy fighters appear and shoot back"),
    )
    examiner = ScriptedExaminer(_uncovered(), _covered())

    result = propose_and_apply(flying_project, _dossier(), designer, examiner=examiner)

    assert result.proposal is designer.attempts[1]
    assert "enemy fighters appear and shoot back" in result.project.mechanics
    assert len(result.refusals) == 1
    assert "otros cazas" in result.refusals[0]


def test_the_second_attempt_is_told_which_words_of_the_brief_went_unanswered(flying_project):
    designer = ScriptedDesigner(
        _mechanics_proposal("the plane moves"),
        _mechanics_proposal("the plane flies right", "enemy fighters appear and shoot back"),
    )

    propose_and_apply(
        flying_project, _dossier(), designer, examiner=ScriptedExaminer(_uncovered(), _covered())
    )

    feedback = designer.feedback_seen[1]
    assert feedback is not None
    assert "van apareciendo otros cazas" in feedback
    assert "/mechanics" in feedback


def test_the_feedback_warns_off_the_paths_a_proposal_may_not_touch():
    """A gap like "there is no enemy actor" is not closable by adding an
    entity -- `apply_proposal` refuses that path -- so a designer that tries
    loses an attempt for nothing."""
    feedback = coverage_feedback(["the brief asks for enemy fighters and there are none"])

    assert "/mechanics" in feedback
    assert "/entities/N/notes" in feedback
    assert "entities" in feedback and "refused" in feedback


def test_a_design_that_still_misses_after_its_attempts_is_refused(flying_project):
    designer = ScriptedDesigner(_mechanics_proposal("the plane moves"))
    examiner = ScriptedExaminer(_uncovered())

    with pytest.raises(ValueError, match="otros cazas"):
        propose_and_apply(flying_project, _dossier(), designer, attempts=3, examiner=examiner)

    assert len(designer.feedback_seen) == 3
    assert len(examiner.seen) == 3


def test_a_covered_design_is_examined_once_and_returned(flying_project):
    designer = ScriptedDesigner(_mechanics_proposal("the plane flies right"))
    examiner = ScriptedExaminer(_covered())

    result = propose_and_apply(flying_project, _dossier(), designer, examiner=examiner)

    assert designer.feedback_seen == [None]
    assert result.refusals == []
    assert len(examiner.seen) == 1


def test_without_an_examiner_nothing_is_examined_and_nothing_changes(flying_project):
    """Every offline caller and every existing test injects a designer alone;
    none of them may start making a second API call."""
    designer = ScriptedDesigner(_mechanics_proposal("the plane flies right"))

    result = propose_and_apply(flying_project, _dossier(), designer)

    assert result.refusals == []


def test_a_project_with_no_brief_is_never_sent_to_the_examiner():
    """There is nothing to fall short of, and a model asked to judge coverage
    of an empty brief is being paid to state the obvious."""
    project = blank_project("Zampa", TargetPlatform.SPECTRUM)
    designer = ScriptedDesigner(_mechanics_proposal("eat every dot"))
    examiner = ScriptedExaminer(_uncovered())

    result = propose_and_apply(project, _dossier(), designer, examiner=examiner)

    assert examiner.seen == []
    assert result.refusals == []


def test_the_examiner_judges_the_design_the_proposal_produced_not_the_one_it_started_from(
    flying_project,
):
    """A verdict on the design before the changes would refuse work the
    proposal had already done."""
    designer = ScriptedDesigner(_mechanics_proposal("the plane flies right"))
    examiner = ScriptedExaminer(_covered())

    propose_and_apply(flying_project, _dossier(), designer, examiner=examiner)

    assert examiner.seen[0].mechanics == ["the plane flies right"]


def test_the_service_carries_the_examiner_into_the_loop(tmp_path):
    """Proves the examiner is reachable through the layer both front ends
    call, not only through the module-level function."""
    service = StudioService.at(tmp_path)
    project, directory = service.create_project("My Retro Game", TargetPlatform.SPECTRUM)
    project = rename_project(project, "My Retro Game", brief="hay scroll y van apareciendo cazas")
    save_reference(_dossier(), directory)
    designer = ScriptedDesigner(
        _mechanics_proposal("the plane moves"),
        _mechanics_proposal("the plane flies right", "enemy fighters appear and shoot back"),
    )

    _proposal, _diff, updated, refusals = service.propose_from_reference(
        project, directory, designer, examiner=ScriptedExaminer(_uncovered(), _covered())
    )

    assert "enemy fighters appear and shoot back" in updated.mechanics
    assert len(refusals) == 1
    assert "does not state what the brief asks for" in refusals[0]


def test_the_summary_shows_what_an_entity_notes_field_already_states(flying_project):
    """`my-retro-game`'s single actor carries a paragraph about fuel, missiles
    and landing on a carrier. A summary that hid it would have the examiner
    report gaps the design does state, in a field the writer genuinely reads."""
    document = flying_project.model_dump(mode="json")
    document["entities"][0]["notes"] = "Combustible limitado; debe aterrizar en el portaaviones."
    with_notes = type(flying_project).model_validate(document)

    summary = design_summary(with_notes)

    assert "portaaviones" in summary
    assert "x1" in summary


def test_the_summary_says_out_loud_that_a_design_states_no_mechanics(flying_project):
    """`studio-projects/zampabolas` and `studio-projects/my-retro-game` both
    reached the writer with `mechanics: []`. An empty heading reads as a list
    that was cut off."""
    assert "Mechanics: none stated" in design_summary(flying_project)


def test_the_summary_carries_presentation_and_audio_but_not_the_machine_budgets(flying_project):
    """A brief can ask for music or a look; nobody ever wrote a brief asking
    for 24576 bytes of binary, and showing budgets invites a verdict about a
    field the machine imposed."""
    summary = design_summary(flying_project)

    assert "classic arcade" in summary
    assert "no music" in summary
    assert str(flying_project.budgets.binary_bytes) not in summary
