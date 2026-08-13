import pytest

from llmz80.studio.models import TargetPlatform
from llmz80.studio.planner import ProjectChange, ProjectProposal, apply_proposal
from llmz80.studio.samples import blank_project


@pytest.fixture
def project():
    return blank_project("Planner", TargetPlatform.SPECTRUM)


def test_a_proposal_that_outgrows_the_target_grid_is_refused(project):
    """`GameProject.model_validate` refuses a screen wider than its target's
    playable grid (see `structure._fit_errors`) unconditionally -- this is a
    fact about the hardware, not a rule `allow_unplayable` can waive, so a
    proposal that outgrows it never even reaches `apply_proposal`'s own
    playability gate.
    """
    screen = project.screens[0]
    wide = ["." * 40 for _ in range(screen.height)]
    proposal = ProjectProposal(
        summary="widen the first screen",
        changes=[
            ProjectChange(
                path="/screens/0/width",
                operation="replace",
                value_number=40,
                reason="more room to run",
            ),
            ProjectChange(
                path="/screens/0/tiles",
                operation="replace",
                value_rows=wide,
                reason="more room to run",
            ),
        ],
    )

    with pytest.raises(ValueError, match="playable cells"):
        apply_proposal(project, proposal)


def test_a_playable_proposal_still_applies(project):
    proposal = ProjectProposal(
        summary="tune the presentation",
        changes=[
            ProjectChange(
                path="/presentation/style",
                operation="replace",
                value_text="moody pixel-art dungeon",
                reason="match the new mechanics",
            )
        ],
    )

    applied = apply_proposal(project, proposal)

    assert applied.presentation.style == "moody pixel-art dungeon"


def test_a_proposal_can_change_mechanics_and_a_screens_tiles(project):
    """`/mechanics` and a screen's `tiles` are proposable in v4 -- neither
    existed as a field a v3 proposal could touch at all: `/gameplay` had no
    prose slot for what the game does, and terrain lived under `/levels`, not
    `/screens`.
    """
    screen = project.screens[0]
    rows = [list(row) for row in screen.tiles]
    rows[1][5] = "#"  # a single interior cell, away from the entity's spawn
    edited_tiles = ["".join(row) for row in rows]
    proposal = ProjectProposal(
        summary="declare a mechanic and add a pillar",
        changes=[
            ProjectChange(
                path="/mechanics",
                operation="replace",
                value_rows=["the player explores the screen and avoids obstacles"],
                reason="the design had no stated mechanics yet",
            ),
            ProjectChange(
                path="/screens/0/tiles",
                operation="replace",
                value_rows=edited_tiles,
                reason="break up the empty room with a single pillar",
            ),
        ],
    )

    applied = apply_proposal(project, proposal)

    assert applied.mechanics == ["the player explores the screen and avoids obstacles"]
    assert applied.screens[0].tiles == edited_tiles
