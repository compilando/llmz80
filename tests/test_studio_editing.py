"""The two edits that survived, and what each one refuses.

The other sixteen -- paint a cell, fill a screen, resize one, move a spawn,
recount an entity, say what a save changed -- went with the map editor that
was the only thing calling them, and their tests went with them.
"""

import pytest

from llmz80.studio.editing import EditError, editing_status, rename_project
from llmz80.studio.models import TargetPlatform
from llmz80.studio.samples import blank_project


@pytest.fixture
def project():
    return blank_project("Editing", TargetPlatform.SPECTRUM)


def test_editing_status_reports_only_what_it_can_know(project):
    status = editing_status(project)

    assert set(status) == {"buildable", "backend_error", "ready"}
    assert status["ready"] is True


def test_a_design_too_wide_for_its_machine_is_not_buildable(project):
    wide = project.screens[0].model_copy(
        update={"width": 40, "tiles": [row.ljust(40, row[-1]) for row in project.screens[0].tiles]}
    )

    status = editing_status(project.model_copy(update={"screens": [wide]}))

    assert status["ready"] is False
    assert status["backend_error"]


def test_the_scalar_fields_are_applied_together_in_one_validated_step(project):
    edited = rename_project(project, "Another Name", style="neon arcade", brief="Four ghosts.")

    assert edited.metadata.title == "Another Name"
    assert edited.presentation.style == "neon arcade"
    assert edited.metadata.brief == "Four ghosts."


def test_a_rename_the_design_cannot_accept_is_refused_not_crashed_on(project):
    with pytest.raises(EditError):
        rename_project(project, "x" * 200)
