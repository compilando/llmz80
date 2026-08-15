"""StudioService, judged on what survives a real trip through the filesystem.

`draw_sprites` is the one place a drawn sheet is written to disk as a PNG and
later re-read (`compiler.render_project` reopens the very file this method
saves). That round trip is exactly where an implicit decision -- transparency
that lives only in an in-memory PIL image, never written into the pixels
themselves -- would be silently dropped one step after `sprite_artist.py`
gets it right: a PNG that loses its alpha on save is the same "solid block"
defect one step later, and no in-memory-only test could ever catch it.

No API call is made anywhere in this file: `draw_sprites` takes its artist as
a parameter, so a fake artist stands in for `SpriteArtist`, exactly the
pattern `test_studio_tui.py`'s `_FakeArtist` already uses for the same method.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from llmz80.studio.models import TargetPlatform
from llmz80.studio.samples import blank_project
from llmz80.studio.services import StudioService
from llmz80.studio.sprite_artist import FRAMES_PER_SHEET, MAX_DRAW_ATTEMPTS, SpriteArtist
from llmz80.studio.sprite_sheet import split_frames
from llmz80.studio.spriting import SPRITE_SIZE, pack_spectrum

_FIXTURE_SHEET = Path(__file__).parent / "fixtures" / "sprite_sheet_running_figure.png"


def _create_sprited_project(service: StudioService, title: str, platform=TargetPlatform.SPECTRUM):
    """`create_project` -> `blank_project`'s one entity ("actor") has no
    `sprite` id at all -- v4 has no fixed roster of roles to default one
    from -- but `draw_sprites` groups entities by `entity.sprite`, so a
    project actually worth drawing art for needs one. Gives the entity a
    sprite id of "hero" and re-saves, the way a designer using the map/
    entities panel would before ever pressing ctrl+d.
    """
    project, directory = service.create_project(title, platform)
    project = project.model_copy(
        update={"entities": [project.entities[0].model_copy(update={"sprite": "hero"})]}
    )
    service.save_project(project, directory)
    return project, directory


class _FakeGenerator:
    """Returns one fixed image; see `test_sprite_artist.py`'s twin."""

    def __init__(self, image: Image.Image) -> None:
        self.image = image

    def generate_image(self, prompt: str) -> Image.Image:
        return self.image


class _FixtureArtist:
    """A fake artist -- `draw_sprites`' collaborator parameter, not a mock of
    the filesystem -- whose `draw_frames` returns real, already-keyed RGBA
    frames drawn from the real `gpt-image-1` fixture (via the real
    `SpriteArtist`, computed once in `__init__`). This is what lets this
    test exercise `draw_sprites`' own tiling/save/reload path with a
    silhouette worth losing, without a network call and without patching
    `Path`, `Image.open` or anything else in `services.py`.
    """

    def __init__(self) -> None:
        project = blank_project("Fixture", TargetPlatform.SPECTRUM)
        entity = project.entities[0]
        with Image.open(_FIXTURE_SHEET) as sheet:
            real_artist = SpriteArtist(_FakeGenerator(sheet.copy()))
            self.frames = real_artist.draw_frames(project, entity)
        self.calls: list[str] = []

    def draw_frames(self, project, entity, dossier=None, *, on_progress=None):
        self.calls.append(entity.sprite)
        return self.frames


class _StubArtist:
    """A minimal fake artist: one solid frame, no raw sheet, no attempt
    history -- the same bare `list[Image.Image]` several fakes across the
    test suite return from `draw_frames` (only the real `SpriteArtist`
    carries `.sheet`/`.sheets`/`.attempts`/`.repairs`). Used wherever a test
    needs *an* artist but not a particular drawing.
    """

    def draw_frames(self, project, entity, dossier=None, *, on_progress=None):
        return [Image.new("RGBA", (SPRITE_SIZE, SPRITE_SIZE), (200, 40, 40, 255))]


def test_draw_sprites_round_trip_through_disk_keeps_a_recognisable_silhouette(tmp_path: Path):
    """`draw_sprites` tiles `_FixtureArtist`'s real frames into one sheet,
    saves it as a PNG under the project's `assets/`, and registers it. Then,
    exactly as `compiler.render_project` does for a real build, this test
    reopens that PNG from disk, splits it back into frames, and packs it --
    checking that what comes out the far end of the round trip is still a
    running figure, not a solid block (256 set pixels -- the original defect,
    reappearing one step later if the sheet PNG lost its alpha on save) and
    not a blank frame (0 set pixels -- the same defect's mirror image).
    """
    service = StudioService.at(tmp_path)
    project, directory = _create_sprited_project(service, "Round Trip")
    artist = _FixtureArtist()

    drawn = service.draw_sprites(project, directory, artist)

    assert len(drawn) >= 1
    assert artist.calls
    asset = drawn[0]
    assert asset.frames == FRAMES_PER_SHEET
    sheet_path = directory / asset.source
    assert sheet_path.is_file()

    with Image.open(sheet_path) as reloaded:
        assert reloaded.mode == "RGBA"
        frames = split_frames(reloaded.convert("RGBA"), asset.frames)

    packed = pack_spectrum(frames)
    set_bits_per_frame = [
        sum(
            bin(byte).count("1")
            for byte in packed.data[
                index * packed.bytes_per_frame : (index + 1) * packed.bytes_per_frame
            ]
        )
        for index in range(packed.frames)
    ]

    assert len(set_bits_per_frame) == FRAMES_PER_SHEET
    for index, count in enumerate(set_bits_per_frame):
        assert count not in (
            0,
            256,
        ), f"frame {index} packed to {count}/256 set pixels after the disk round trip"


# --- Keeping the evidence: the raw sheet, saved beside the asset it produced --
#
# Nothing used to save what the model actually returned -- only the cleaned,
# packed 16x16-per-frame sheet ever reached disk, so a run like the one
# against *Abu Simbel Profanation* (two of three sprites coming back as dark
# art on a near-black background) left nothing to look at afterwards except
# the ruined result. `SpriteArtist.draw_frames` now returns a `DrawnFrames`
# carrying the winning attempt's raw, unprocessed response as `.sheet`; these
# tests check `draw_sprites` writes it to `assets/<sprite id>.raw.png`.


def test_draw_sprites_saves_the_raw_sheet_beside_the_registered_asset(tmp_path: Path):
    service = StudioService.at(tmp_path)
    project, directory = _create_sprited_project(service, "Raw Sheet")
    artist = _FixtureArtist()

    drawn = service.draw_sprites(project, directory, artist)

    asset = drawn[0]
    asset_path = directory / asset.source
    raw_path = asset_path.with_name(f"{asset_path.stem}.raw.png")
    assert raw_path.is_file(), "the raw response must be saved beside the registered asset"
    assert raw_path.parent == asset_path.parent

    with Image.open(raw_path) as raw, Image.open(_FIXTURE_SHEET) as original:
        assert raw.size == original.size
        assert (
            raw.convert("RGB").tobytes() == original.convert("RGB").tobytes()
        ), "the saved file must be the model's raw response, not a cleaned/packed frame"

    # The real fixture passes judgement on the first attempt, so the numbered
    # attempt history (see the failure-path test below) is exactly one entry
    # long, and it must match the unsuffixed "winner" file byte for byte.
    attempt_one = asset_path.with_name(f"{asset_path.stem}.raw.attempt-1.png")
    assert attempt_one.is_file()
    assert attempt_one.read_bytes() == raw_path.read_bytes()
    assert not asset_path.with_name(f"{asset_path.stem}.raw.attempt-2.png").exists()


def test_draw_sprites_saves_every_attempts_raw_sheet_after_a_failure(tmp_path: Path):
    """A sprite that exhausts every attempt without a judged-valid sheet
    never reaches `add_asset` -- no `AssetSpec` is ever registered for it --
    which is exactly the run whose evidence matters most: it is the one a
    person most needs to see what the model actually drew, and until now it
    was also the one for which nothing at all was kept. `SpriteDrawFailure`
    (see `sprite_artist.py`) carries every attempt's raw sheet even though
    none of them worked; `draw_sprites` must save all of them, not silently
    lose them because the loop ended in a raise instead of a return.
    """
    service = StudioService.at(tmp_path)
    project, directory = _create_sprited_project(service, "Persistent Failure")
    # Filled edge to edge, no white margin at all -- `_clean_image`'s tight
    # bounding-box crop leaves nothing but figure, so every attempt is judged
    # a solid block and none of the three ever wins.
    blank = Image.new("RGBA", (512, 128), (10, 20, 30, 255))
    artist = SpriteArtist(_FakeGenerator(blank))

    with pytest.raises(ValueError):
        service.draw_sprites(project, directory, artist)

    assets_dir = directory / "assets"
    attempts = sorted(assets_dir.glob("hero.raw.attempt-*.png"))
    assert [path.name for path in attempts] == [
        f"hero.raw.attempt-{n}.png" for n in range(1, MAX_DRAW_ATTEMPTS + 1)
    ], "every attempt must be saved, numbered so their order is obvious"
    assert not (
        assets_dir / "hero.raw.png"
    ).is_file(), "no attempt won, so the unsuffixed 'the winner' file must not exist"
    assert not (assets_dir / "hero.png").is_file(), "a failed draw must never register an asset"


def test_draw_sprites_tolerates_an_artist_that_carries_no_raw_sheet(tmp_path: Path):
    """A caller's own fake artist -- several exist across the test suite --
    can return a bare `list[Image.Image]` from `draw_frames`, carrying no
    raw sheet at all (only the real `SpriteArtist` carries one). Registering
    the asset must not depend on it being there.
    """

    service = StudioService.at(tmp_path)
    project, directory = _create_sprited_project(service, "Bare Artist")

    drawn = service.draw_sprites(project, directory, _StubArtist())

    asset = drawn[0]
    asset_path = directory / asset.source
    assert asset_path.is_file()
    raw_path = asset_path.with_name(f"{asset_path.stem}.raw.png")
    assert not raw_path.is_file()


def test_a_v3_document_is_refused_with_a_message_that_says_what_to_do(tmp_path):
    from llmz80.studio.store import ProjectStore

    path = tmp_path / "old" / "game.yml"
    path.parent.mkdir(parents=True)
    path.write_text("schema_version: 3\nmetadata: {}\n", encoding="utf-8")
    with pytest.raises(ValueError) as error:
        ProjectStore(tmp_path).load(path)
    message = str(error.value)
    assert "schema version 3" in message
    assert "v4" in message


def test_draw_sprites_narrates_each_sheet_it_packs(tmp_path):
    """Without this the screen can say nothing for the eighty seconds the
    artist takes, because the report only exists once it is over."""
    from llmz80.studio.services import StudioService

    service = StudioService.at(tmp_path)
    project, directory = service.create_project("Narrated", TargetPlatform.SPECTRUM)
    said: list[str] = []
    service.draw_sprites(project, directory, _StubArtist(), on_progress=said.append)
    assert said, "the artist packed a sheet and said nothing about it"
    assert any("actor" in line for line in said), said


def test_on_progress_is_optional(tmp_path):
    """Every existing caller passes nothing and must keep working."""
    from llmz80.studio.services import StudioService

    service = StudioService.at(tmp_path)
    project, directory = service.create_project("Quiet", TargetPlatform.SPECTRUM)
    service.draw_sprites(project, directory, _StubArtist())


def test_write_program_lets_runtime_test_narrate_from_inside_the_repair_loop(tmp_path):
    """`verify_program`, called once per attempt from inside
    `generator.write_program`'s repair loop, used to call `runtime_test`
    with no `on_progress` at all -- `runtime_test`'s two long-wait lines
    (compiling, then starting the emulator) never reached a listener when
    `write_program` was the caller, even though `write_program` itself
    narrated every attempt. `StudioService.write_program` now hands
    `verify_program` a closure that carries `on_progress` through
    `generator.write_program`'s fixed two-argument `verify` contract, so the
    lines must arrive interleaved with the per-attempt narration, not be
    missing from it.

    `build` and `runtime_test` are replaced with instance-level fakes rather
    than exercised for real: this test is about whether `on_progress`
    reaches `runtime_test` from this call path, which needs no compiler or
    emulator to demonstrate.
    """
    from llmz80.studio.compiler import BuildResult
    from llmz80.studio.generator import ProgramFile, ProgramSources

    service = StudioService.at(tmp_path)
    project, directory = service.create_project("Loop", TargetPlatform.SPECTRUM)

    def fake_build(project, directory):
        return BuildResult(
            success=True,
            artifact=None,
            report={"quality_pass": True},
            output_dir=directory / "build",
        )

    def fake_runtime_test(project, directory, *, seconds=3, on_progress=None):
        if on_progress is not None:
            on_progress("compilando el programa")
            on_progress("arrancando el emulador")
        return {"acceptance": {"quality_pass": True}, "animation": {"quality_pass": True}}

    service.build = fake_build
    service.runtime_test = fake_runtime_test

    class _Writer:
        def write(self, project, feedback=None):
            return ProgramSources(
                summary="ok", files=[ProgramFile(name="main.c", body="void main(void) { }")]
            )

    messages: list[str] = []
    service.write_program(project, directory, _Writer(), attempts=1, on_progress=messages.append)

    assert messages == [
        "intento 1: escribiendo...",
        "compilando el programa",
        "arrancando el emulador",
        "intento 1: build compiló, aceptación aprobada, animación aprobada, "
        "ritmo sin observar, atributos sin observar, estado sin observar",
    ], messages


def test_the_runtime_test_drives_the_observation_script(tmp_path, monkeypatch):
    """`runtime_test` passed `script=[]`, so `step_readings` came back empty and
    every gate that reads it abstained. The pipeline was built and disconnected
    by a literal."""
    from llmz80.studio.compiler import BuildResult
    from llmz80.studio.models import TargetPlatform
    from llmz80.studio.observation import observation_script
    from llmz80.studio.samples import blank_project
    from llmz80.studio.services import StudioService

    project = blank_project("Driven", TargetPlatform.SPECTRUM)
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    monkeypatch.setattr(
        StudioService,
        "build",
        lambda self, p, d: BuildResult(
            output_dir=build_dir, success=True, artifact=None, report={"quality_pass": True}
        ),
    )
    captured: dict = {}

    def fake_smoke(output_dir, platform, full=False, seconds=3, probes=None, script=None):
        captured["script"] = script
        return {"quality_pass": True, "step_readings": []}

    monkeypatch.setattr("llmz80.studio.services.smoke_test", fake_smoke)

    StudioService.at(tmp_path).runtime_test(project, tmp_path)

    # Whole steps, not just their ids: the field `feel.animation_report` reads
    # is `hold`, and both modules carry a docstring about the run where `hold`
    # never reached it. An id-only assertion would have passed through that.
    assert captured["script"] == observation_script(project)
