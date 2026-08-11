"""Turning a dossier into a reviewable design proposal."""

import pytest

from llmz80.studio.editing import rename_project
from llmz80.studio.models import GenreId, TargetPlatform
from llmz80.studio.packs import create_default_project
from llmz80.studio.planner import ProjectChange, ProjectProposal, apply_proposal
from llmz80.studio.reference import GameReference, load_reference, save_reference
from llmz80.studio.reference_design import ResponsesReferenceDesigner
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
    return create_default_project("Zampa", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)


def test_the_dossier_and_the_project_both_reach_the_model(project):
    proposal = ProjectProposal(
        summary="match the original",
        changes=[
            ProjectChange(
                path="/presentation/style",
                operation="replace",
                value="bright maze on black",
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
                value="bright maze on black",
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
                value="bright maze on black",
                reason="the original drew a bright maze on black",
            )
        ],
    )

    class _Designer:
        def propose(self, project, dossier):
            return proposal

    returned, diff = service.propose_from_reference(project, directory, _Designer(), _dossier())

    assert returned is proposal
    assert "presentation/style" in diff


def test_proposing_without_a_dossier_says_so(tmp_path):
    service = StudioService.at(tmp_path)
    project, directory = service.create_project(
        "Zampa", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE
    )

    class _Designer:
        def propose(self, project, dossier):
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
        def propose(self, project, dossier):
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
        def propose(self, project, dossier):
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
