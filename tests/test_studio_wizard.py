"""The wizard walks the pipeline in order and never guesses what is done."""

from llmz80.studio.models import GameProject, TargetPlatform
from llmz80.studio.samples import blank_project
from llmz80.studio.wizard import can_leave_behind, current, steps


def test_without_a_project_the_first_step_is_choosing_one():
    step = current(None, None)
    assert step.number == 0
    assert step.name == "proyecto"


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
        "release",
    ]


def test_a_fresh_project_is_pointed_at_research(tmp_path):
    project = blank_project("Fresh", TargetPlatform.SPECTRUM)
    assert current(project, tmp_path, passed={"proyecto"}).name == "referencia"


def test_the_wizard_stands_on_the_first_step_not_left_behind(tmp_path):
    project = blank_project("Skip", TargetPlatform.SPECTRUM)
    assert current(project, tmp_path, passed={"proyecto", "referencia"}).name == "diseño"


def test_a_valid_design_is_still_a_stop_not_a_step_to_skip_over(tmp_path):
    """The design stage is never `pending` -- it validates or it fails -- so a
    wizard that advanced on "done" would never stop where the editing happens."""
    project = blank_project("Stop", TargetPlatform.SPECTRUM)
    step = current(project, tmp_path, passed={"proyecto", "referencia"})
    assert step.name == "diseño"
    assert step.state == "done"


def test_only_research_and_sprites_may_be_skipped(tmp_path):
    project = blank_project("Optional", TargetPlatform.SPECTRUM)
    skippable = {step.name for step in steps(project, tmp_path) if step.skippable}
    assert skippable == {"referencia", "sprites"}


def test_only_the_design_step_is_editable(tmp_path):
    project = blank_project("Editable", TargetPlatform.SPECTRUM)
    editable = {step.name for step in steps(project, tmp_path) if step.editable}
    assert editable == {"diseño"}


def test_the_steps_that_spend_money_say_so(tmp_path):
    project = blank_project("Money", TargetPlatform.SPECTRUM)
    paid = {step.name for step in steps(project, tmp_path) if step.costs_api}
    assert paid == {"referencia", "sprites", "programa"}


def test_a_failure_wins_over_a_later_pending_step(tmp_path):
    """Nothing is gained by pointing at "draw sprites" while the design is broken."""
    project = blank_project("Broken", TargetPlatform.SPECTRUM)
    wide = project.screens[0].model_copy(
        update={"width": 40, "tiles": [row.ljust(40, row[-1]) for row in project.screens[0].tiles]}
    )
    broken = project.model_copy(update={"screens": [wide]})
    step = current(broken, tmp_path, passed={"proyecto", "referencia"})
    assert step.name == "diseño"
    assert step.state == "failed"
    assert step.detail


def test_every_step_carries_words_a_person_can_read(tmp_path):
    project = blank_project("Words", TargetPlatform.SPECTRUM)
    for step in steps(project, tmp_path):
        assert step.summary
        assert step.action_label
        assert step.title


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
        "release",
    ]
    assert [step.title for step in walked] == [
        "Project",
        "Reference",
        "Design",
        "Sprites",
        "Program",
        "Gates",
        "Release",
    ]


# --- who may be left behind ------------------------------------------------


def test_a_resolved_step_is_behind_you_once_you_say_so(tmp_path):
    """`diseño` is not skippable, but a design that validates is *done*: there
    is nothing left to make it wait for."""
    project = blank_project("Resolved", TargetPlatform.SPECTRUM)
    step = current(project, tmp_path, passed={"proyecto", "referencia"})
    assert step.name == "diseño"
    assert step.state == "done"
    assert can_leave_behind(step)


def test_a_pending_step_the_pipeline_can_spare_may_be_left_behind(tmp_path):
    project = blank_project("Optional", TargetPlatform.SPECTRUM)
    step = current(project, tmp_path, passed={"proyecto"})
    assert step.name == "referencia"
    assert step.state == "pending"
    assert can_leave_behind(step)


def test_a_pending_step_the_pipeline_needs_may_not(tmp_path):
    """Without a program there is nothing to gate and nothing to release."""
    project = blank_project("Required", TargetPlatform.SPECTRUM)
    step = current(project, tmp_path, passed={"proyecto", "referencia", "diseño", "sprites"})
    assert step.name == "programa"
    assert step.state == "pending"
    assert not can_leave_behind(step)


def test_a_step_already_skipped_stays_behind_you(tmp_path):
    project = blank_project("Skipped", TargetPlatform.SPECTRUM)
    step = next(
        s
        for s in steps(project, tmp_path, passed={"proyecto", "referencia"})
        if s.name == "referencia"
    )
    assert step.state == "skipped"
    assert can_leave_behind(step)


def test_a_failed_step_may_not_be_walked_past(tmp_path):
    """A broken design is the one thing worth being dragged back to."""
    project = blank_project("Broken", TargetPlatform.SPECTRUM)
    wide = project.screens[0].model_copy(
        update={"width": 40, "tiles": [row.ljust(40, row[-1]) for row in project.screens[0].tiles]}
    )
    broken = project.model_copy(update={"screens": [wide]})
    step = current(broken, tmp_path, passed={"proyecto", "referencia"})
    assert step.state == "failed"
    assert not can_leave_behind(step)
