import pytest

from llmz80.studio.models import TargetPlatform
from llmz80.studio.planner import ProjectChange, ProjectProposal, apply_proposal
from llmz80.studio.samples import blank_project


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
                value_rows=["".join(row) for row in rows],
                reason="frame the pellet with masonry",
            )
        ],
    )


@pytest.fixture
def project():
    return blank_project("Planner", TargetPlatform.SPECTRUM)


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


def _empty_room_tiles(level):
    """Blank a level's interior to open floor, keeping its border ring solid --
    the same shape `tests/test_terrain_structure.py` uses to build the gate's
    own motivating failure."""
    rows = [list(row) for row in level.tiles]
    for row in range(1, level.height - 1):
        for column in range(1, level.width - 1):
            rows[row][column] = "."
    return ["".join(row) for row in rows]


def _empty_room_proposal(project):
    """The motivating case the terrain-structure gate exists for: a bulk
    proposal that guts every maze level into a trivially solvable, structurally
    empty room."""
    return ProjectProposal(
        summary="open up the level layouts",
        changes=[
            ProjectChange(
                path=f"/levels/{index}/tiles",
                operation="replace",
                value_rows=_empty_room_tiles(level),
                reason="simplify the maze",
            )
            for index, level in enumerate(project.levels)
        ],
    )


def test_a_proposal_that_guts_every_level_into_an_empty_room_is_refused(project):
    proposal = _empty_room_proposal(project)

    with pytest.raises(ValueError, match="would leave the game unplayable"):
        apply_proposal(project, proposal)


def test_the_refusal_names_the_terrain_structure_problem(project):
    proposal = _empty_room_proposal(project)

    with pytest.raises(ValueError, match="not enough interior structure"):
        apply_proposal(project, proposal)


def test_a_proposal_that_outgrows_the_target_grid_is_refused(project):
    level = project.levels[0]
    wide = ["." * 40 for _ in range(level.height)]
    proposal = ProjectProposal(
        summary="widen the first level",
        changes=[
            ProjectChange(
                path="/levels/0/width",
                operation="replace",
                value_number=40,
                reason="more room to run",
            ),
            ProjectChange(
                path="/levels/0/tiles",
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
        summary="tune the difficulty",
        changes=[
            ProjectChange(
                path="/gameplay/lives",
                operation="replace",
                value_number=5,
                reason="the maze is unforgiving",
            )
        ],
    )

    applied = apply_proposal(project, proposal)

    assert applied.gameplay.lives == 5
