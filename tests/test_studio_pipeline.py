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

from llmz80 import cli
from llmz80.studio import pipeline
from llmz80.studio.models import TargetPlatform
from llmz80.studio.planner import NumberValue, ProjectChange, ProjectProposal, RowsValue, TextValue
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
                        value=NumberValue(number=99),
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
                    value=TextValue(text="arcade neon"),
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


# --- draft -----------------------------------------------------------------


class _FakeDrafter:
    """States the rules its brief asks for, recording what it was handed."""

    def __init__(self) -> None:
        self.calls = 0
        self.dossiers: list[GameReference | None] = []

    def draft(self, project, dossier=None, feedback=None):
        self.calls += 1
        self.dossiers.append(dossier)
        return ProjectProposal(
            summary="state the rules",
            changes=[
                ProjectChange(
                    path="/mechanics",
                    operation="replace",
                    reason="the brief says what this is",
                    value=RowsValue(
                        rows=[
                            "el minero cava hacia abajo",
                            "un murcielago le quita una vida",
                        ]
                    ),
                )
            ],
            # The note every real draft carries now: `draft_and_apply` sends a
            # draft that declares no observables and says nothing about why
            # back for one more attempt, so a fake that stayed silent would
            # make every stage test here cost two drafts instead of one.
            observability="none: nothing this design does leaves a count behind",
        )


def test_drafting_saves_what_it_came_to(tmp_path: Path):
    service = StudioService.at(tmp_path)
    project, directory = pipeline.create(
        service, "Drafted", TargetPlatform.SPECTRUM, "un minero cava y esquiva murcielagos"
    )

    updated = pipeline.draft(service, project, directory, _FakeDrafter())

    assert updated.mechanics[0] == "el minero cava hacia abajo"
    assert service.open_project(directory).mechanics == updated.mechanics


def test_drafting_hands_the_drafter_the_dossier_that_was_archived(tmp_path: Path):
    """The stage runs after research precisely so a draft can read one. The
    dossier is optional here where `adapt` requires it -- drafting from the
    brief alone is the case that unblocks a game nobody recognised -- so both
    are proved."""
    service = StudioService.at(tmp_path)
    project, directory = pipeline.create(
        service, "Researched", TargetPlatform.SPECTRUM, "un minero cava y esquiva murcielagos"
    )
    save_reference(_dossier("Manic Miner"), directory)
    drafter = _FakeDrafter()

    pipeline.draft(service, project, directory, drafter)

    assert drafter.dossiers[0] is not None
    assert drafter.dossiers[0].title == "Manic Miner"

    unresearched, elsewhere = pipeline.create(
        service, "Alone", TargetPlatform.SPECTRUM, "un minero cava y esquiva murcielagos"
    )
    alone = _FakeDrafter()

    pipeline.draft(service, unresearched, elsewhere, alone)

    assert alone.dossiers == [None]


def test_drafting_a_design_that_already_states_its_rules_changes_nothing(tmp_path: Path):
    """`needs_drafting` is asked before the drafter is used, so a design that
    is already somebody's costs nothing and is left exactly as it was."""
    service = StudioService.at(tmp_path)
    project, directory = pipeline.create(
        service, "Stated", TargetPlatform.SPECTRUM, "un minero cava y esquiva murcielagos"
    )
    project = project.model_copy(update={"mechanics": ["ya lo dice"]})
    service.save_project(project, directory)
    said: list[str] = []

    class NeverCalled:
        def draft(self, project, dossier=None, feedback=None):
            raise AssertionError("the drafter must not be asked")

    updated = pipeline.draft(service, project, directory, NeverCalled(), say=said.append)

    assert updated.mechanics == ["ya lo dice"]
    assert any("already states" in line for line in said)


def test_drafting_shows_the_diff_before_saving_anything(tmp_path: Path):
    service = StudioService.at(tmp_path)
    project, directory = pipeline.create(
        service, "Reviewed", TargetPlatform.SPECTRUM, "un minero cava y esquiva murcielagos"
    )
    before = (directory / "game.yml").read_text(encoding="utf-8")
    shown: list[str] = []

    def refuse(diff: str) -> bool:
        shown.append(diff)
        return False

    with pytest.raises(pipeline.Declined):
        pipeline.draft(service, project, directory, _FakeDrafter(), confirm=refuse)

    assert shown and "mechanics" in shown[0]
    assert (directory / "game.yml").read_text(encoding="utf-8") == before


def test_drafting_settles_whether_it_is_wanted_before_it_spends_anything(
    tmp_path: Path, monkeypatch
):
    """The same order `research` and `adapt` both keep, and for the same
    reason: this stage says "this calls the OpenAI API" out loud, so a design
    that does not want drafting must never hear it. Proved by making the
    client's own constructor an error -- if the guard ever moves below it, the
    test fails rather than quietly costing somebody a call.

    Both halves of `needs_drafting` are checked, because either one arriving
    late would spend the same money: a design that already states its rules,
    and one nobody wrote a brief for.
    """
    service = StudioService.at(tmp_path)
    stated, stated_directory = pipeline.create(
        service, "Stated", TargetPlatform.SPECTRUM, "un minero cava y esquiva murcielagos"
    )
    stated = stated.model_copy(update={"mechanics": ["ya lo dice"]})
    service.save_project(stated, stated_directory)
    briefless, briefless_directory = pipeline.create(service, "Briefless", TargetPlatform.SPECTRUM)

    def _refuse_to_be_built():
        raise AssertionError("the OpenAI client was built before the guard fired")

    monkeypatch.setattr(cli, "_llm_client_and_model", _refuse_to_be_built)

    for project, directory, state in (
        (stated, stated_directory, "stated"),
        (briefless, briefless_directory, "briefless"),
    ):
        said: list[str] = []

        assert pipeline.draft(service, project, directory, say=said.append) is project, state
        assert not any("OpenAI" in line for line in said), state


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


def test_adapt_refuses_before_it_announces_that_it_is_about_to_spend_money(opened, monkeypatch):
    """`adapt` says "this calls the OpenAI API" and builds the client, and it
    used to do both before finding out there was nothing to adapt to. No call
    was ever made -- the guard was one line further down -- but a user who is
    told money is about to go out and is then handed an error has no way to
    know that, and reads it as a charge that failed.

    `research` already gets this order right and its docstring says why, so
    the fix is to match it: settle the question first, build the client after.
    Both refusals are checked, because both used to come too late.
    """
    service, project, directory = opened
    unidentified = GameReference(identified=False, confidence="low")

    for state, archive in (("absent", False), ("unidentified", True)):
        if archive:
            save_reference(unidentified, directory)
        built: list[str] = []
        said: list[str] = []

        def _refuse_to_be_built():
            built.append("client")
            raise AssertionError("the OpenAI client was built before the guard fired")

        monkeypatch.setattr(cli, "_llm_client_and_model", _refuse_to_be_built)

        with pytest.raises(ValueError, match="no researched game"):
            pipeline.adapt(service, project, directory, say=said.append)

        assert built == [], state
        assert said == [], state


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

    def _write_program(project, directory, writer, *, on_progress=None, examiner=None):
        on_progress("attempt 1: asking the model")
        return {"accepted": True, "attempts": [{"number": 1}]}

    service.write_program = _write_program  # type: ignore[method-assign]
    report = pipeline.write(service, project, directory, _Writer(), say=said.append)

    assert report["accepted"] is True
    assert said == ["attempt 1: asking the model"]


def test_test_forwards_its_commentary_to_whoever_is_listening(opened):
    service, project, directory = opened
    said: list[str] = []

    def _runtime_test(project, directory, *, on_progress=None, examiner=None):
        on_progress("building")
        return {"quality_pass": True}

    service.runtime_test = _runtime_test  # type: ignore[method-assign]
    report = pipeline.test(service, project, directory, say=said.append)

    assert report["quality_pass"] is True
    assert said == ["building"]


def test_writing_refuses_a_design_that_does_not_pass_its_own_gate(tmp_path):
    """The writer is not asked for a program the design gate already refused:
    an API call costs money and ninety seconds, and the answer is known."""
    from llmz80.studio.editing import rename_project

    service = StudioService.at(tmp_path)
    project, directory = service.create_project("Refused", TargetPlatform.SPECTRUM)
    project = rename_project(project, "Refused", brief="un juego como la abadía del crimen")
    service.save_project(project, directory)

    class NeverCalled:
        def write(self, project, feedback=None):
            raise AssertionError("the writer must not be asked")

    with pytest.raises(ValueError, match="not ready to be written"):
        pipeline.write(service, project, directory, NeverCalled())


class _FakeTerrainArtist(_FakeArtist):
    """Also draws terrain, recording which tile it drew, so one fake can stand
    in for the whole graphics stage the way the real artist pair does."""

    def __init__(self) -> None:
        super().__init__()
        self.tiles: list[str] = []

    def draw_tile(self, project, tile, dossier=None, *, on_progress=None):
        from PIL import Image

        from llmz80.studio.spriting import TILE_SIZE

        self.tiles.append(tile.id)
        image = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
        pixels = image.load()
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                if (x + y) % 2 == 0:
                    pixels[x, y] = (200, 40, 40, 255)
        return [image]


def test_the_graphics_stage_draws_the_terrain_the_design_asked_for(opened):
    """The stage is "the art this project is missing", and terrain is art. A
    design whose tiles asked to be drawn and whose stage only drew actors is
    how a finished game came out looking like text."""
    service, project, directory = opened
    project.tiles[0].art_note = "brickwork, mortar lines between courses"
    service.save_project(project, directory)
    artist = _FakeTerrainArtist()

    pipeline.sprites(service, project, directory, artist)

    assert artist.tiles == [project.tiles[0].id]
    on_disk = service.open_project(directory)
    tile = next(tile for tile in on_disk.tiles if tile.id == project.tiles[0].id)
    assert tile.art == tile.id
    assert any(asset.kind == "tileset" for asset in on_disk.assets)


def test_a_design_that_asked_for_no_terrain_art_draws_none(opened):
    service, project, directory = opened
    assert all(not tile.wants_art for tile in project.tiles)
    artist = _FakeTerrainArtist()

    pipeline.sprites(service, project, directory, artist)

    assert artist.tiles == []
    assert artist.calls  # the actors were still drawn
