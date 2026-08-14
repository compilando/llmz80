"""The pipeline's steps, in order, and never a guess about what is done."""

from llmz80.studio.models import TargetPlatform
from llmz80.studio.samples import blank_project
from llmz80.studio.wizard import steps


def test_without_a_project_nothing_is_done_yet():
    walked = steps(None, None)
    assert walked[0].number == 0
    assert walked[0].name == "proyecto"
    assert {step.state for step in walked} == {"pending"}


def test_with_a_project_step_zero_is_done_and_the_walk_begins():
    project = blank_project("Walk", TargetPlatform.SPECTRUM)
    walked = steps(project, None)
    assert walked[0].number == 0
    assert walked[0].state == "done"
    assert [step.name for step in walked[1:]] == [
        "referencia",
        "diseño",
        "sprites",
        "programa",
        "gates",
    ]


def test_a_valid_design_reads_as_done_rather_than_pending(tmp_path):
    """The design stage is never `pending` -- it validates or it fails."""
    project = blank_project("Stop", TargetPlatform.SPECTRUM)
    step = next(s for s in steps(project, tmp_path) if s.name == "diseño")
    assert step.state == "done"


def test_a_broken_design_reads_as_failed_and_says_why(tmp_path):
    project = blank_project("Broken", TargetPlatform.SPECTRUM)
    wide = project.screens[0].model_copy(
        update={"width": 40, "tiles": [row.ljust(40, row[-1]) for row in project.screens[0].tiles]}
    )
    broken = project.model_copy(update={"screens": [wide]})

    step = next(s for s in steps(broken, tmp_path) if s.name == "diseño")

    assert step.state == "failed"
    assert step.detail


def test_every_state_is_evidence_and_nothing_is_remembered(tmp_path):
    """There is no state a caller can assert into a step. `skipped` was the
    one -- a person walking past a step on purpose -- and nothing decides
    that any more, so two readers of one project cannot disagree."""
    project = blank_project("Evidence", TargetPlatform.SPECTRUM)

    assert [step.state for step in steps(project, tmp_path)] == [
        step.state for step in steps(project, tmp_path)
    ]
    assert {step.state for step in steps(project, tmp_path)} <= {"done", "pending", "failed"}


def test_a_step_keeps_its_id_and_carries_a_label_of_its_own(tmp_path):
    """The two jobs one field used to do, and lost at: `name` is the id
    `screen.stage_line` produces, `passed` holds and the diary records, and it
    stays exactly as it was; `title` is what the screen prints, and it is
    English like the rest of the interface."""
    project = blank_project("Labelled", TargetPlatform.SPECTRUM)
    walked = steps(project, tmp_path)

    assert [step.name for step in walked] == [
        "proyecto",
        "referencia",
        "diseño",
        "sprites",
        "programa",
        "gates",
    ]
    assert [step.title for step in walked] == [
        "Project",
        "Reference",
        "Design",
        "Sprites",
        "Program",
        "Gates",
    ]


def test_a_step_carries_nothing_a_wizard_would_have_needed():
    """What each key did, what it cost and whether a person could walk past
    it went with the wizard that named them."""
    fields = set(steps(None, None)[0].__dataclass_fields__)

    assert fields == {"name", "title", "number", "state", "detail"}
