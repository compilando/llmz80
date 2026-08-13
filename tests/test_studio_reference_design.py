"""Turning a dossier into a reviewable design proposal."""

import pytest

from llmz80.studio.editing import rename_project
from llmz80.studio.models import GenreId, PresentationSpec, TargetPlatform
from llmz80.studio.planner import ProjectChange, ProjectProposal, apply_proposal
from llmz80.studio.reference import GameReference, load_reference, save_reference
from llmz80.studio.reference_design import (
    DESIGN_SYSTEM_PROMPT,
    ResponsesReferenceDesigner,
    propose_and_apply,
    repair_feedback,
)
from llmz80.studio.samples import blank_project
from llmz80.studio.services import StudioService


def _dossier(**overrides) -> GameReference:
    document = {
        "identified": True,
        "confidence": "high",
        "title": "Zampa Bolas",
        "publisher": "Iber Soft",
        "year": 1985,
        "platforms": ["spectrum"],
        "mechanics": ["eat every dot", "two ghosts chase the player"],
        "screen_layout": "score on the top row",
        "pacing": "ghosts are slower than the player",
        "visual_style": "bright maze on black",
        "level_structure": "three mazes of rising density",
        "sources": [
            {
                "url": "https://example.org/z",
                "title": "Zampa Bolas",
                "retrieved_at": "2026-08-11T09:00:00Z",
            }
        ],
    }
    document.update(overrides)
    return GameReference.model_validate(document)


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


@pytest.fixture
def project():
    return blank_project("Zampa", TargetPlatform.SPECTRUM)


def test_the_prompt_puts_the_design_in_charge_of_what_the_game_is():
    """The Zampabolas live run: the real 1990 game the brief named is an
    entirely different genre (a 4-player grab-the-balls game, no enemies, no
    progression) from the maze-chase the designer actually described. The
    model proposed rewriting the design to match the real game anyway. The
    prompt must place the design's genre, entity roles and scene flow beyond
    the reference's reach, not merely suggest restraint."""
    lowered = DESIGN_SYSTEM_PROMPT.lower()

    assert "genre" in lowered
    assert "role" in lowered
    assert "scene" in lowered
    # Not just mentioned -- explicitly withheld from the reference's authority.
    assert "settled" in lowered or "not yours to change" in lowered or "not to change" in lowered


def test_the_prompt_tells_the_model_to_hold_back_on_a_different_game():
    """Where the dossier describes a different game from the design, the
    prompt must call for a small or empty proposal, not a rewrite."""
    lowered = DESIGN_SYSTEM_PROMPT.lower()

    assert "different game" in lowered
    assert "small" in lowered or "none at all" in lowered


def test_the_prompt_states_the_true_presentation_style_bound():
    """The live run copied the dossier's 600-character visual_style straight
    into presentation.style, which pydantic capped at 80 and refused. Read
    the real bound from the model instead of hard-coding it, so this test
    fails the moment the prompt and the schema disagree, in either
    direction."""
    style_field = PresentationSpec.model_fields["style"]
    max_length = next(
        constraint.max_length
        for constraint in style_field.metadata
        if hasattr(constraint, "max_length")
    )

    assert str(max_length) in DESIGN_SYSTEM_PROMPT
    assert "/presentation/style" in DESIGN_SYSTEM_PROMPT


def test_the_prompt_no_longer_offers_count_or_difficulty_curve_as_targets():
    """Both fields were among the ten changes the live run proposed to turn a
    maze-chase into a 4-player ball-grabbing game: zeroing entity counts to
    remove the enemies, and flattening the difficulty curve because the real
    game has no progression. Neither is a presentation knob."""
    # Bulleted targets are indented two spaces; the explanatory sentence about
    # what was deliberately left off is not, so this tells the two apart.
    assert "\n  /entities/N/count" not in DESIGN_SYSTEM_PROMPT
    assert "\n  /gameplay/difficulty_curve" not in DESIGN_SYSTEM_PROMPT
    assert "/entities/N/count" in DESIGN_SYSTEM_PROMPT
    assert "/gameplay/difficulty_curve" in DESIGN_SYSTEM_PROMPT


def test_the_dossier_and_the_project_both_reach_the_model(project):
    proposal = ProjectProposal(
        summary="match the original",
        changes=[
            ProjectChange(
                path="/presentation/style",
                operation="replace",
                value_text="bright maze on black",
                reason="the original drew a bright maze on black",
            )
        ],
    )
    client = _FakeClient(proposal)

    ResponsesReferenceDesigner(client).propose(project, _dossier())

    sent = client.responses.calls[0]["input"][1]["content"]
    assert "Zampa Bolas" in sent
    assert "maze_chase" in sent


def test_a_proposal_from_a_dossier_applies_like_any_other(project):
    proposal = ProjectProposal(
        summary="match the original",
        changes=[
            ProjectChange(
                path="/presentation/style",
                operation="replace",
                value_text="bright maze on black",
                reason="the original drew a bright maze on black",
            )
        ],
    )

    updated = apply_proposal(project, proposal)

    assert updated.presentation.style == "bright maze on black"
    assert project.presentation.style != "bright maze on black"


def test_an_unidentified_dossier_yields_no_proposal(project):
    """Nothing was found, so there is nothing to rebuild the design from."""
    client = _FakeClient(None)

    with pytest.raises(ValueError, match="not identified"):
        ResponsesReferenceDesigner(client).propose(
            project, _dossier(identified=False, sources=[], title="")
        )

    assert client.responses.calls == []


def test_a_call_that_returns_nothing_parsed_is_not_silently_accepted(project):
    """The API contract allows a response with no structured output; propose
    must not hand that back to a caller as if it were a real proposal."""
    client = _FakeClient(None)

    with pytest.raises(ValueError, match="did not return a structured project proposal"):
        ResponsesReferenceDesigner(client).propose(project, _dossier())

    assert len(client.responses.calls) == 1


def test_researching_archives_the_dossier_in_the_project(tmp_path):
    service = StudioService.at(tmp_path)
    project, directory = service.create_project(
        "Zampa", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE
    )

    class _Researcher:
        def research(self, brief, target):
            return _dossier()

    dossier = service.research_reference(project, directory, _Researcher())

    assert dossier.title == "Zampa Bolas"
    assert load_reference(directory).title == "Zampa Bolas"


def test_researching_archives_an_unidentified_dossier_too(tmp_path):
    """A recorded empty search is worth as much as a dossier: it stops every
    later action re-running the same search, so it is archived just the same."""
    service = StudioService.at(tmp_path)
    project, directory = service.create_project(
        "Zampa", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE
    )

    class _Researcher:
        def research(self, brief, target):
            return GameReference(identified=False, confidence="low")

    dossier = service.research_reference(project, directory, _Researcher())

    assert dossier.identified is False
    archived = load_reference(directory)
    assert archived is not None
    assert archived.identified is False


def test_a_reference_proposal_is_returned_with_its_diff(tmp_path):
    service = StudioService.at(tmp_path)
    project, directory = service.create_project(
        "Zampa", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE
    )
    proposal = ProjectProposal(
        summary="match the original",
        changes=[
            ProjectChange(
                path="/presentation/style",
                operation="replace",
                value_text="bright maze on black",
                reason="the original drew a bright maze on black",
            )
        ],
    )

    class _Designer:
        def propose(self, project, dossier, feedback=None):
            return proposal

    returned, diff, updated, refusals = service.propose_from_reference(
        project, directory, _Designer(), _dossier()
    )

    assert returned is proposal
    assert "presentation/style" in diff
    assert updated.presentation.style == "bright maze on black"
    assert refusals == []


def test_proposing_without_a_dossier_says_so(tmp_path):
    service = StudioService.at(tmp_path)
    project, directory = service.create_project(
        "Zampa", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE
    )

    class _Designer:
        def propose(self, project, dossier, feedback=None):
            raise AssertionError("must not be called")

    with pytest.raises(ValueError, match="no researched game"):
        service.propose_from_reference(project, directory, _Designer(), None)


def test_proposing_without_a_dossier_argument_falls_back_to_the_archived_one(tmp_path):
    """The only real caller, `project adapt`, never passes a dossier: it always
    relies on `load_reference(directory)` picking up what was researched
    earlier. Prove that fallback itself works, not just the explicit-None case."""
    service = StudioService.at(tmp_path)
    project, directory = service.create_project(
        "Zampa", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE
    )
    save_reference(_dossier(), directory)

    received = []

    class _Designer:
        def propose(self, project, dossier, feedback=None):
            received.append(dossier)
            return ProjectProposal(summary="match the original", changes=[])

    service.propose_from_reference(project, directory, _Designer())

    assert len(received) == 1
    assert received[0].title == "Zampa Bolas"


def test_proposing_from_an_unidentified_archived_dossier_says_so(tmp_path):
    """The service's own guard, distinct from the designer's equivalent one:
    it must refuse before the designer is ever invoked."""
    service = StudioService.at(tmp_path)
    project, directory = service.create_project(
        "Zampa", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE
    )

    class _Designer:
        def propose(self, project, dossier, feedback=None):
            raise AssertionError("must not be called")

    with pytest.raises(ValueError, match="no researched game was identified"):
        service.propose_from_reference(
            project, directory, _Designer(), _dossier(identified=False, sources=[], title="")
        )


def test_researching_sends_the_brief_and_the_platform_value(tmp_path):
    """A wrong field, or the enum instead of its `.value`, must fail a test
    here rather than surface only against a live API call."""
    service = StudioService.at(tmp_path)
    project, directory = service.create_project(
        "Zampa", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE
    )
    project = rename_project(project, project.metadata.title, brief="a maze full of ghosts")

    received = []

    class _Researcher:
        def research(self, brief, target):
            received.append((brief, target))
            return _dossier()

    service.research_reference(project, directory, _Researcher())

    assert received == [("a maze full of ghosts", "spectrum")]
    # TargetPlatform is a str Enum, so it compares equal to its own .value;
    # only checking the type catches passing the enum member itself.
    assert type(received[0][1]) is str


# --- the repair loop -------------------------------------------------------
#
# The live run's ten-change proposal was thrown away whole over two
# mechanically fixable errors: a `presentation.style` written past its
# 80-character bound, and an `entities.1.count` of 0 against a `ge=1` floor.
# These tests prove `propose_and_apply` turns that kind of refusal into
# another attempt with real, actionable feedback instead of a dead end.


class ScriptedDesigner:
    """A designer whose attempts are decided in advance -- some refusable,
    some not -- so the repair loop is testable without a model. Mirrors
    `generator.ScriptedWriter`."""

    def __init__(self, *attempts: ProjectProposal) -> None:
        self.attempts = list(attempts)
        self.feedback_seen: list[str | None] = []

    def propose(self, project, dossier, feedback=None):
        self.feedback_seen.append(feedback)
        return self.attempts[min(len(self.feedback_seen), len(self.attempts)) - 1]


def _oversized_style_proposal() -> ProjectProposal:
    """The live-run shape: a `presentation.style` written past its 80-char
    bound. `ProjectChange.value_text` carries no length limit of its own, so
    this parses cleanly and is only refused once `apply_proposal` revalidates
    the whole `GameProject`."""
    return ProjectProposal(
        summary="paint the maze from the dossier",
        changes=[
            ProjectChange(
                path="/presentation/style",
                operation="replace",
                value_text="x" * 100,
                reason="the dossier's visual_style ran long",
            )
        ],
    )


def _fixed_style_proposal() -> ProjectProposal:
    return ProjectProposal(
        summary="paint the maze from the dossier",
        changes=[
            ProjectChange(
                path="/presentation/style",
                operation="replace",
                value_text="bright maze on black",
                reason="the dossier's visual_style, trimmed to fit",
            )
        ],
    )


def _sealing_proposal(project) -> ProjectProposal:
    """Borrowed from tests/test_studio_planner_gate.py: a proposal that
    `apply_proposal` refuses because it walls a collectible in on every
    side -- a solvability failure, not a schema violation, so it exercises
    `repair_feedback`'s other branch."""
    occupied = {(s.col, s.row) for s in project.levels[0].spawns}
    roles = {e.id: e.role for e in project.entities}
    neighbours = lambda c: [(c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)]
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


def test_repair_feedback_names_every_field_that_ended_up_out_of_bounds(project):
    """The exact live-run case: a style written past 80 characters and an
    entity count zeroed below its ge=1 floor, both in one proposal. Both
    fields must be named, with their actual bound, not a generic message."""
    proposal = ProjectProposal(
        summary="import the dossier wholesale",
        changes=[
            ProjectChange(
                path="/presentation/style",
                operation="replace",
                value_text="x" * 100,
                reason="paste the dossier's visual style",
            ),
            ProjectChange(
                path="/entities/1/count",
                operation="replace",
                value_number=0,
                reason="remove the enemies",
            ),
        ],
    )

    with pytest.raises(ValueError) as excinfo:
        apply_proposal(project, proposal)

    feedback = repair_feedback(excinfo.value)

    assert "/presentation/style" in feedback
    assert "80 characters" in feedback
    assert "/entities/1/count" in feedback
    assert "greater than or equal to 1" in feedback


def test_repair_feedback_on_an_unplayable_result_names_solvability_not_fields(project):
    """The other shape `apply_proposal` raises: a plain sentence about
    solvability, not a field-by-field pydantic error. It must be quoted, not
    misread as a validation failure."""
    with pytest.raises(ValueError) as excinfo:
        apply_proposal(project, _sealing_proposal(project))

    feedback = repair_feedback(excinfo.value)

    assert "unplayable" in feedback.lower()
    assert "reachable" in feedback.lower()


def test_a_refused_proposal_is_repaired_on_the_second_attempt(project):
    designer = ScriptedDesigner(_oversized_style_proposal(), _fixed_style_proposal())

    result = propose_and_apply(project, _dossier(), designer)

    assert len(designer.feedback_seen) == 2
    assert result.proposal is designer.attempts[1]
    assert result.project.presentation.style == "bright maze on black"
    assert len(result.refusals) == 1
    assert "80 characters" in result.refusals[0]


def test_the_feedback_handed_to_the_second_attempt_names_the_real_problem(project):
    designer = ScriptedDesigner(_oversized_style_proposal(), _fixed_style_proposal())

    propose_and_apply(project, _dossier(), designer)

    feedback = designer.feedback_seen[1]
    assert feedback is not None
    assert "/presentation/style" in feedback
    assert "80 characters" in feedback


def test_an_unplayable_proposal_is_also_repaired(project):
    designer = ScriptedDesigner(_sealing_proposal(project), _fixed_style_proposal())

    result = propose_and_apply(project, _dossier(), designer)

    assert "unplayable" in designer.feedback_seen[1].lower()
    assert result.project.presentation.style == "bright maze on black"


def _empty_room_tiles(level):
    """Blank a level's interior to open floor, keeping its border ring solid --
    the shape `terrain_structure.py` exists to catch."""
    rows = [list(row) for row in level.tiles]
    for row in range(1, level.height - 1):
        for column in range(1, level.width - 1):
            rows[row][column] = "."
    return ["".join(row) for row in rows]


def _empty_room_proposal(project) -> ProjectProposal:
    """The motivating case for the whole gap this file closes: an AI proposal
    that rewrites every maze level into a completely empty room. It is
    trivially solvable and fits the target machine, so neither of
    `editing_status`'s other two checks caught it before the terrain-structure
    gate joined them."""
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


def _structured_maze_proposal(project) -> ProjectProposal:
    """What a repaired attempt should look like: the same levels, still
    carrying their generated maze's corridors rather than an open room."""
    return ProjectProposal(
        summary="restore proper maze corridors",
        changes=[
            ProjectChange(
                path=f"/levels/{index}/tiles",
                operation="replace",
                value_rows=list(level.tiles),
                reason="corridors and dead ends, not an open room",
            )
            for index, level in enumerate(project.levels)
        ],
    )


def test_the_repair_loop_engages_when_a_proposal_guts_the_terrain(project):
    """The gate built in `terrain_structure.py` and the repair loop built in
    `propose_and_apply` were wired up separately and never met: this is the
    end-to-end proof that they now do. The first attempt is exactly the
    empty-room case the gate exists for; the second is a properly structured
    maze, and it is the one that ends up applied."""
    designer = ScriptedDesigner(_empty_room_proposal(project), _structured_maze_proposal(project))

    result = propose_and_apply(project, _dossier(), designer)

    assert len(designer.feedback_seen) == 2
    assert result.proposal is designer.attempts[1]
    assert result.project.levels[0].tiles == project.levels[0].tiles
    assert len(result.refusals) == 1
    assert "not enough interior structure" in result.refusals[0]


def test_the_feedback_after_a_gutted_proposal_names_the_terrain_failure(project):
    """Not just "unplayable" -- the specific reason, so the model has
    something to act on other than guessing."""
    designer = ScriptedDesigner(_empty_room_proposal(project), _structured_maze_proposal(project))

    propose_and_apply(project, _dossier(), designer)

    feedback = designer.feedback_seen[1]
    assert feedback is not None
    assert "maze terrain has wall ratio" in feedback
    assert "not enough interior structure for a maze level" in feedback


def test_exhausting_attempts_raises_carrying_the_last_refusal(project):
    designer = ScriptedDesigner(
        _oversized_style_proposal(), _oversized_style_proposal(), _oversized_style_proposal()
    )

    with pytest.raises(ValueError, match="80 characters"):
        propose_and_apply(project, _dossier(), designer, attempts=3)

    assert len(designer.feedback_seen) == 3


def test_a_proposal_that_applies_first_time_makes_exactly_one_model_call(project):
    designer = ScriptedDesigner(_fixed_style_proposal())

    result = propose_and_apply(project, _dossier(), designer)

    assert designer.feedback_seen == [None]
    assert result.refusals == []


def test_the_service_repairs_a_refused_proposal_before_returning_it(tmp_path):
    """Proves the loop is actually reachable through the service both front
    ends call, not just the module-level function directly."""
    service = StudioService.at(tmp_path)
    project, directory = service.create_project(
        "Zampa", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE
    )
    save_reference(_dossier(), directory)
    designer = ScriptedDesigner(_oversized_style_proposal(), _fixed_style_proposal())

    proposal, diff, updated, refusals = service.propose_from_reference(
        project, directory, designer
    )

    assert proposal is designer.attempts[1]
    assert updated.presentation.style == "bright maze on black"
    assert len(refusals) == 1
    assert "presentation/style" in diff
