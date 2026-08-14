"""The stages themselves, with nobody watching them.

These used to be tested twice: once through `llmz80 project ...` (with
`builtins.input` monkeypatched) and once through the terminal wizard (by
driving a Textual app and pressing keys twice). Both were testing the same
rules -- an archived dossier is not replaced without a yes, existing art is
not overwritten without one, a proposal is not saved until somebody has seen
the diff -- and now there is one place those rules live, so there is one
place they are proved.

Not one OpenAI call is made here. Every stage takes its collaborator as a
parameter for exactly this reason, and the fakes below are what a caller --
this suite, a script, `llmz80 make` under test -- hands it instead.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from llmz80.studio import pipeline
from llmz80.studio.models import TargetPlatform
from llmz80.studio.planner import ProjectChange, ProjectProposal
from llmz80.studio.reference import GameReference, ReferenceSource, save_reference
from llmz80.studio.services import StudioService
from llmz80.studio.spriting import SPRITE_SIZE


class _FakeResearcher:
    """Records how many times it was asked, and for what."""

    def __init__(self, title: str = "Zampa Bolas", identified: bool = True) -> None:
        self.title, self.identified = title, identified
        self.calls = 0

    def research(self, brief, target):
        self.calls += 1
        sources = (
            [
                ReferenceSource(
                    url="https://example.com/review",
                    title="A review",
                    retrieved_at=datetime.now(timezone.utc),
                )
            ]
            if self.identified
            else []
        )
        return GameReference(
            identified=self.identified,
            confidence="high",
            title=self.title if self.identified else "",
            sources=sources,
        )


class _FakeDesigner:
    """Refuses its first proposal (a protected path), then succeeds, so the
    repair loop's refusal has somewhere to be seen."""

    def __init__(self) -> None:
        self.calls = 0

    def propose(self, project, dossier, feedback=None):
        self.calls += 1
        if self.calls == 1:
            return ProjectProposal(
                summary="touch what is not mine to touch",
                changes=[
                    ProjectChange(
                        path="/schema_version",
                        operation="replace",
                        reason="bogus",
                        value_number=99,
                    )
                ],
            )
        return ProjectProposal(
            summary="dress it up like the real game",
            changes=[
                ProjectChange(
                    path="/presentation/style",
                    operation="replace",
                    reason="matches the dossier's visual style",
                    value_text="arcade neon",
                )
            ],
        )


class _FakeArtist:
    """Draws one flat frame per call, recording which sprite id it drew."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def draw_frames(self, project, entity, dossier=None, *, on_progress=None):
        from PIL import Image

        self.calls.append(entity.sprite or entity.id)
        return [Image.new("RGBA", (SPRITE_SIZE, SPRITE_SIZE), (200, 40, 40, 255))]


@pytest.fixture
def opened(tmp_path: Path):
    """A saved project and the service that owns it -- what every stage takes."""
    service = StudioService.at(tmp_path)
    project, directory = pipeline.create(service, "Staged", TargetPlatform.SPECTRUM)
    return service, project, directory


def _dossier(title: str = "Real Game") -> GameReference:
    return GameReference(
        identified=True,
        confidence="high",
        title=title,
        sources=[
            ReferenceSource(
                url="https://example.com/game",
                title="a source",
                retrieved_at=datetime.now(timezone.utc),
            )
        ],
    )


def _yes(_detail: str) -> bool:
    return True


def _no(_detail: str) -> bool:
    return False


# --- create ----------------------------------------------------------------


def test_create_puts_the_brief_in_the_project_it_makes(tmp_path: Path):
    service = StudioService.at(tmp_path)

    project, directory = pipeline.create(
        service, "Briefed", TargetPlatform.SPECTRUM, "four ghosts chase you"
    )

    assert project.metadata.brief == "four ghosts chase you"
    assert service.open_project(directory).metadata.brief == "four ghosts chase you"


def test_create_refuses_a_name_already_taken(tmp_path: Path):
    """Whether that is the end of it or an invitation to count up is the
    caller's business: `llmz80 project new` stops, `llmz80 make` tries "… 2"."""
    service = StudioService.at(tmp_path)
    pipeline.create(service, "Twice", TargetPlatform.SPECTRUM)

    with pytest.raises(FileExistsError):
        pipeline.create(service, "Twice", TargetPlatform.SPECTRUM)


# --- research --------------------------------------------------------------


def test_research_archives_what_it_found(opened):
    service, project, directory = opened
    researcher = _FakeResearcher(title="Zampa Bolas")

    dossier = pipeline.research(service, project, directory, researcher)

    assert researcher.calls == 1
    assert dossier.title == "Zampa Bolas"
    assert (directory / "reference.yml").is_file()


def test_research_asks_before_replacing_an_archived_dossier(opened):
    service, project, directory = opened
    pipeline.research(service, project, directory, _FakeResearcher(title="First Game"))
    archived = (directory / "reference.yml").read_text(encoding="utf-8")

    second = _FakeResearcher(title="Second Game")
    with pytest.raises(pipeline.Declined):
        pipeline.research(service, project, directory, second, confirm=_no)

    assert second.calls == 0, "declining must cost nothing at the API"
    assert (directory / "reference.yml").read_text(encoding="utf-8") == archived

    pipeline.research(service, project, directory, second, confirm=_yes)

    assert second.calls == 1
    assert "Second Game" in (directory / "reference.yml").read_text(encoding="utf-8")


def test_research_asked_of_nobody_replaces_what_is_there(opened):
    """`llmz80 make` passes no `confirm` and researches a project it created a
    moment ago: there is nothing of anybody's to protect, and stopping to ask
    a question with nobody to answer it would hang the order."""
    service, project, directory = opened
    pipeline.research(service, project, directory, _FakeResearcher(title="First Game"))

    pipeline.research(service, project, directory, _FakeResearcher(title="Second Game"))

    assert "Second Game" in (directory / "reference.yml").read_text(encoding="utf-8")


def test_an_unreadable_archive_is_told_apart_from_an_absent_one(opened):
    """Reading a malformed dossier as "no dossier" would overwrite a
    hand-corrected file without ever asking."""
    service, project, directory = opened
    (directory / "reference.yml").write_text("not: [valid", encoding="utf-8")
    researcher = _FakeResearcher()

    with pytest.raises(pipeline.Unreadable):
        pipeline.research(service, project, directory, researcher, confirm=_yes)

    assert researcher.calls == 0


# --- adapt -----------------------------------------------------------------


def test_adapt_repairs_a_refused_proposal_and_says_it_did(opened):
    service, project, directory = opened
    save_reference(_dossier(), directory)
    designer = _FakeDesigner()
    said: list[str] = []

    updated = pipeline.adapt(service, project, directory, designer, say=said.append)

    assert designer.calls == 2
    assert any("Attempt 1 was refused, repairing:" in line for line in said)
    assert updated.presentation.style == "arcade neon"
    assert service.open_project(directory).presentation.style == "arcade neon"


def test_adapt_shows_the_diff_before_saving_anything(opened):
    service, project, directory = opened
    save_reference(_dossier(), directory)
    before = (directory / "game.yml").read_text(encoding="utf-8")
    shown: list[str] = []

    def refuse(diff: str) -> bool:
        shown.append(diff)
        return False

    with pytest.raises(pipeline.Declined):
        pipeline.adapt(service, project, directory, _FakeDesigner(), confirm=refuse)

    assert shown and "style" in shown[0]
    assert (directory / "game.yml").read_text(encoding="utf-8") == before


def test_adapt_without_a_dossier_says_so(opened):
    service, project, directory = opened

    with pytest.raises(ValueError, match="no researched game"):
        pipeline.adapt(service, project, directory, _FakeDesigner())


# --- sprites ---------------------------------------------------------------


def test_sprites_draws_what_is_missing_and_registers_it(opened):
    service, project, directory = opened
    artist = _FakeArtist()

    drawn = pipeline.sprites(service, project, directory, artist)

    assert artist.calls == [asset.id for asset in drawn]
    on_disk = service.open_project(directory)
    registered = {asset.id for asset in on_disk.assets if asset.kind == "sprite"}
    assert registered == set(artist.calls)
    assert all((directory / asset.source).is_file() for asset in drawn)


def test_sprites_asked_of_nobody_keeps_the_art_it_finds(opened):
    """`llmz80 make` passes no `confirm`, and a caller with nobody to ask must
    not destroy artwork on its own authority: it fills the gaps and stops."""
    service, project, directory = opened
    pipeline.sprites(service, project, directory, _FakeArtist())
    project = service.open_project(directory)
    before = {
        asset.id: (directory / asset.source).read_bytes()
        for asset in project.assets
        if asset.kind == "sprite"
    }
    assert before

    second = _FakeArtist()
    drawn = pipeline.sprites(service, project, directory, second)

    assert second.calls == [] and drawn == []
    project = service.open_project(directory)
    for asset in project.assets:
        if asset.kind == "sprite":
            assert (directory / asset.source).read_bytes() == before[asset.id]


def test_sprites_asks_before_overwriting_existing_art(opened):
    service, project, directory = opened
    pipeline.sprites(service, project, directory, _FakeArtist())
    project = service.open_project(directory)
    existing = pipeline._drawn_already(project)
    assert existing

    declined = _FakeArtist()
    with pytest.raises(pipeline.Declined):
        pipeline.sprites(service, project, directory, declined, confirm=_no)
    assert declined.calls == []
    assert service.open_project(directory).assets == project.assets

    redrawing = _FakeArtist()
    drawn = pipeline.sprites(service, project, directory, redrawing, confirm=_yes)

    assert sorted(redrawing.calls) == existing
    assert sorted(asset.id for asset in drawn) == existing


def test_what_counts_as_already_drawn_is_what_draw_sprites_would_draw(opened):
    """`entity.sprite or entity.id` -- an entity carrying no sprite id yet
    wants its own, which is the id the art is registered under. Asking the
    question any other way lets the guard miss art that is really there."""
    service, project, directory = opened
    assert pipeline._drawn_already(project) == []

    pipeline.sprites(service, project, directory, _FakeArtist())
    project = service.open_project(directory)

    assert pipeline._drawn_already(project) == [
        entity.sprite or entity.id for entity in project.entities
    ]


# --- write and test --------------------------------------------------------


def test_write_hands_back_the_report_and_narrates_the_attempts(opened):
    service, project, directory = opened
    said: list[str] = []

    class _Writer:
        def write(self, *args, **kwargs):  # pragma: no cover - never reached
            raise AssertionError("the fake service below is what answers")

    def _write_program(project, directory, writer, *, on_progress=None):
        on_progress("attempt 1: asking the model")
        return {"accepted": True, "attempts": [{"number": 1}]}

    service.write_program = _write_program  # type: ignore[method-assign]
    report = pipeline.write(service, project, directory, _Writer(), say=said.append)

    assert report["accepted"] is True
    assert said == ["attempt 1: asking the model"]


def test_test_forwards_its_commentary_to_whoever_is_listening(opened):
    service, project, directory = opened
    said: list[str] = []

    def _runtime_test(project, directory, *, on_progress=None):
        on_progress("building")
        return {"quality_pass": True}

    service.runtime_test = _runtime_test  # type: ignore[method-assign]
    report = pipeline.test(service, project, directory, say=said.append)

    assert report["quality_pass"] is True
    assert said == ["building"]
