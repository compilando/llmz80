import pytest

from llmz80.studio.models import GenreId, TargetPlatform
from llmz80.studio.packs import create_default_project
from llmz80.studio.planner import ProjectChange, ProjectProposal, apply_proposal


def _sealing_proposal(project):
    """A proposal whose terrain walls a collectible in on every side."""
    occupied = {(s.col, s.row) for s in project.levels[0].spawns}
    roles = {e.id: e.role for e in project.entities}
    neighbours = lambda c: [(c[0]+1, c[1]), (c[0]-1, c[1]), (c[0], c[1]+1), (c[0], c[1]-1)]
    target = next(
        (s.col, s.row)
        for s in project.levels[0].spawns
        if roles.get(s.entity) == "collectible"
        and not any(n in occupied for n in neighbours((s.col, s.row)))
    )
    rows = [list(row) for row in project.levels[0].tiles]
    for col, row in neighbours(target):
        rows[row][col] = "#"
    return ProjectProposal(
        summary="add decorative walls",
        changes=[
            ProjectChange(
                path="/levels/0/tiles",
                operation="replace",
                value=["".join(row) for row in rows],
                reason="frame the pellet with masonry",
            )
        ],
    )


@pytest.fixture
def project():
    return create_default_project("Planner", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)


def test_a_proposal_that_seals_a_collectible_is_refused(project):
    proposal = _sealing_proposal(project)

    with pytest.raises(ValueError, match="would leave the game unplayable"):
        apply_proposal(project, proposal)


def test_the_refusal_names_the_cells_it_sealed(project):
    proposal = _sealing_proposal(project)

    with pytest.raises(ValueError, match="seal off 1 collectible"):
        apply_proposal(project, proposal)


def test_an_unplayable_proposal_can_be_applied_deliberately(project):
    proposal = _sealing_proposal(project)

    applied = apply_proposal(project, proposal, allow_unplayable=True)

    assert applied.levels[0].tiles != project.levels[0].tiles


def test_a_proposal_that_outgrows_the_target_grid_is_refused(project):
    level = project.levels[0]
    wide = ["." * 40 for _ in range(level.height)]
    spawns = [
        {"entity": spawn.entity, "col": spawn.col, "row": spawn.row} for spawn in level.spawns
    ]
    proposal = ProjectProposal(
        summary="widen the first level",
        changes=[
            ProjectChange(
                path="/levels/0",
                operation="replace",
                value={
                    "id": level.id,
                    "name": level.name,
                    "width": 40,
                    "height": level.height,
                    "time_limit_seconds": None,
                    "tiles": wide,
                    "spawns": spawns,
                },
                reason="more room to run",
            )
        ],
    )

    with pytest.raises(ValueError, match="playable cells"):
        apply_proposal(project, proposal)


def test_a_playable_proposal_still_applies(project):
    proposal = ProjectProposal(
        summary="tune the difficulty",
        changes=[
            ProjectChange(
                path="/gameplay/lives",
                operation="replace",
                value=5,
                reason="the maze is unforgiving",
            )
        ],
    )

    applied = apply_proposal(project, proposal)

    assert applied.gameplay.lives == 5
