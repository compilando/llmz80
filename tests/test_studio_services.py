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

from PIL import Image

from llmz80.studio.models import GenreId, TargetPlatform
from llmz80.studio.packs import create_default_project
from llmz80.studio.services import StudioService
from llmz80.studio.sprite_artist import FRAMES_PER_SHEET, SpriteArtist
from llmz80.studio.sprite_sheet import split_frames
from llmz80.studio.spriting import SPRITE_SIZE, pack_spectrum

_FIXTURE_SHEET = Path(__file__).parent / "fixtures" / "sprite_sheet_running_figure.png"


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
        project = create_default_project("Fixture", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
        entity = next(e for e in project.entities if e.role == "player")
        with Image.open(_FIXTURE_SHEET) as sheet:
            real_artist = SpriteArtist(_FakeGenerator(sheet.copy()))
            self.frames = real_artist.draw_frames(project, entity)
        self.calls: list[str] = []

    def draw_frames(self, project, entity, dossier=None):
        self.calls.append(entity.sprite)
        return self.frames


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
    project, directory = service.create_project("Round Trip", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
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
            for byte in packed.data[index * packed.bytes_per_frame : (index + 1) * packed.bytes_per_frame]
        )
        for index in range(packed.frames)
    ]

    assert len(set_bits_per_frame) == FRAMES_PER_SHEET
    for index, count in enumerate(set_bits_per_frame):
        assert count not in (0, 256), (
            f"frame {index} packed to {count}/256 set pixels after the disk round trip"
        )


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
    project, directory = service.create_project(
        "Raw Sheet", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE
    )
    artist = _FixtureArtist()

    drawn = service.draw_sprites(project, directory, artist)

    asset = drawn[0]
    asset_path = directory / asset.source
    raw_path = asset_path.with_name(f"{asset_path.stem}.raw.png")
    assert raw_path.is_file(), "the raw response must be saved beside the registered asset"
    assert raw_path.parent == asset_path.parent

    with Image.open(raw_path) as raw, Image.open(_FIXTURE_SHEET) as original:
        assert raw.size == original.size
        assert raw.convert("RGB").tobytes() == original.convert("RGB").tobytes(), (
            "the saved file must be the model's raw response, not a cleaned/packed frame"
        )


def test_draw_sprites_tolerates_an_artist_that_carries_no_raw_sheet(tmp_path: Path):
    """A caller's own fake artist -- several exist across the test suite --
    can return a bare `list[Image.Image]` from `draw_frames`, carrying no
    raw sheet at all (only the real `SpriteArtist` carries one). Registering
    the asset must not depend on it being there.
    """

    class _BareArtist:
        def draw_frames(self, project, entity, dossier=None):
            return [Image.new("RGBA", (SPRITE_SIZE, SPRITE_SIZE), (200, 40, 40, 255))]

    service = StudioService.at(tmp_path)
    project, directory = service.create_project(
        "Bare Artist", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE
    )

    drawn = service.draw_sprites(project, directory, _BareArtist())

    asset = drawn[0]
    asset_path = directory / asset.source
    assert asset_path.is_file()
    raw_path = asset_path.with_name(f"{asset_path.stem}.raw.png")
    assert not raw_path.is_file()
