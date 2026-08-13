"""SpriteArtist, judged on the prompt it writes and the frames it returns.

No API call is made anywhere in this file: every generator is a fake that
returns a fixed, in-memory image, exactly like `test_studio_generator.py` does
for `ResponsesProgramWriter`'s client.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from llmz80.studio.models import GameProject, GenreId, TargetPlatform, VideoMode
from llmz80.studio.packs import create_default_project
from llmz80.studio.reference import GameReference, ReferenceSource
from llmz80.studio.sprite_artist import (
    FRAMES_PER_SHEET,
    REQUEST_HEIGHT,
    REQUEST_WIDTH,
    SHEET_HEIGHT,
    SHEET_WIDTH,
    TECHNICAL_REQUIREMENTS_HEADING,
    SpriteArtist,
    compose_prompt,
)
from llmz80.studio.spriting import SPRITE_SIZE, pack_cpc, pack_spectrum

#: A real sheet captured from `gpt-image-1`: four running-figure poses, black
#: on a pure white background, no alpha channel, no anti-aliasing -- exactly
#: the shape that exposed the "every packed sprite is a solid block" defect
#: (see `sprite_artist._key_out_background`'s docstring for the mechanism).
#: Every other fixture in this file is synthetic RGBA built with
#: `ImageDraw`, which could never have caught that bug: it is already the
#: RGBA `spriting.py`'s packers expect, so it was never exposed to the
#: "opaque RGB with no alpha at all" shape a real model response actually
#: has. This one is real output, kept as a file rather than reconstructed in
#: code, because the noise a real model leaves behind (compression artefacts,
#: near-white and near-black outliers) is part of what the fix has to survive.
_FIXTURE_SHEET = Path(__file__).parent / "fixtures" / "sprite_sheet_running_figure.png"


class _FakeGenerator:
    """Returns one fixed image and remembers every prompt it was asked for."""

    def __init__(self, image: Image.Image) -> None:
        self.image = image
        self.prompts: list[str] = []

    def generate_image(self, prompt: str) -> Image.Image:
        self.prompts.append(prompt)
        return self.image


def _project(platform: TargetPlatform = TargetPlatform.SPECTRUM) -> GameProject:
    return create_default_project("Test Game", platform, GenreId.MAZE_CHASE)


def _cpc_mode0_project() -> GameProject:
    """`create_default_project` always builds CPC projects in mode 1; mode 0
    is reached the same way `test_studio_models.py` reaches an alternate
    video mode -- dump, edit, revalidate -- since nothing else in Studio
    constructs one directly.
    """
    data = _project(TargetPlatform.AMSTRAD_CPC).model_dump()
    data["target"]["video_mode"] = VideoMode.CPC_MODE_0
    return GameProject.model_validate(data)


def _dossier(**overrides: object) -> GameReference:
    fields = dict(
        identified=True,
        confidence="high",
        title="Jet Set Willy",
        publisher="Software Projects",
        year=1984,
        platforms=["ZX Spectrum"],
        visual_style="Flat colour rooms, black outlines, one attribute clash per room.",
        sources=[
            ReferenceSource(
                url="https://example.com/jsw",
                title="MobyGames",
                retrieved_at=datetime.now(timezone.utc),
            )
        ],
    )
    fields.update(overrides)
    return GameReference(**fields)


def _solid_image(size: tuple[int, int], colour: tuple[int, int, int, int]) -> Image.Image:
    return Image.new("RGBA", size, colour)


#: One colour per column of `_four_pose_sheet`, chosen to be unmistakably
#: different from each other and from the white background.
_POSE_COLOURS = [
    (255, 0, 0, 255),  # red
    (0, 128, 0, 255),  # green
    (0, 0, 255, 255),  # blue
    (255, 165, 0, 255),  # orange
]


def _four_pose_sheet() -> Image.Image:
    """A raw sheet with one solid, differently sized and positioned, non-
    touching blob per column -- a stand-in for four genuinely different
    animation poses side by side, which is exactly what the composed prompt
    asks a real model to draw.

    This is the shape the old clean-the-whole-sheet-then-split order got
    wrong: `_clean_image` keeps only the single largest connected component,
    so run across the whole sheet it would keep one pose and blank the other
    three. Run per column, after splitting (`SpriteArtist.draw_frames`), it
    keeps all four -- see `test_draw_frames_keeps_all_four_distinct_poses`.
    """
    column_width = 200
    height = 200
    width = column_width * FRAMES_PER_SHEET
    sheet = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    # A different size and position per column, so no single bounding-box
    # crop could coincidentally cover more than one of them.
    boxes = [
        (20, 20, 60, 60),  # small, top-left of its column
        (30, 120, 170, 180),  # wide, low in its column
        (20, 20, 180, 180),  # large, fills most of its column
        (80, 80, 120, 120),  # small, centred
    ]
    for index, (x0, y0, x1, y1) in enumerate(boxes):
        offset = index * column_width
        draw.rectangle((offset + x0, y0, offset + x1, y1), fill=_POSE_COLOURS[index])
    return sheet


# --- The composed prompt ----------------------------------------------------


def test_prompt_carries_the_dossiers_visual_style_and_publisher():
    project = _project()
    entity = next(e for e in project.entities if e.role == "enemy")
    dossier = _dossier()

    prompt = compose_prompt(project, entity, dossier)

    assert dossier.publisher in prompt
    assert dossier.visual_style in prompt


def test_prompt_states_the_spectrums_monochrome_constraint():
    project = _project(TargetPlatform.SPECTRUM)
    entity = next(e for e in project.entities if e.role == "player")

    prompt = compose_prompt(project, entity, None)

    assert "monochrome" in prompt.lower()


def test_prompt_states_cpc_mode0s_sixteen_pens():
    project = _cpc_mode0_project()
    entity = next(e for e in project.entities if e.role == "player")

    prompt = compose_prompt(project, entity, None)

    assert "16-color" in prompt


def test_prompt_states_cpc_mode1s_four_pens():
    project = _project(TargetPlatform.AMSTRAD_CPC)  # create_default_project builds mode 1
    assert project.target.video_mode is VideoMode.CPC_MODE_1
    entity = next(e for e in project.entities if e.role == "player")

    prompt = compose_prompt(project, entity, None)

    assert "4-color" in prompt


def test_prompt_asks_for_a_four_frame_sheet_at_the_requested_size():
    project = _project()
    entity = next(e for e in project.entities if e.role == "player")

    prompt = compose_prompt(project, entity, None)

    assert str(FRAMES_PER_SHEET) in prompt
    assert f"{REQUEST_WIDTH}x{REQUEST_HEIGHT}" in prompt


def test_prompt_without_a_dossier_falls_back_to_role_and_presentation_style():
    project = _project()
    entity = next(e for e in project.entities if e.role == "enemy")

    prompt = compose_prompt(project, entity, dossier=None)

    assert entity.role in prompt
    assert project.presentation.style in prompt


def test_technical_requirements_come_after_the_style_block_and_close_the_prompt():
    """The fix for the real defect a run for *Abu Simbel Profanation*
    exposed: the dossier's own style block used to sit last in the prompt,
    so an image model read that game's palette description as the final,
    most heavily weighted word and drew a dark sheet on a dark background.
    The pipeline's technical constraints -- pure white background, no
    anti-aliasing, exact frame layout -- must come after the style block and
    must be the last thing the prompt says, not the other way round.

    Written to fail if someone reorders `compose_prompt`'s parts: swapping
    style and technical constraints back would either put
    `TECHNICAL_REQUIREMENTS_HEADING` before "REFERENCE GAME" (failing the
    first assertion) or leave the style block's own closing sentence as the
    prompt's last text instead of the technical block's (failing the
    second).
    """
    project = _project()
    entity = next(e for e in project.entities if e.role == "player")
    dossier = _dossier()

    prompt = compose_prompt(project, entity, dossier)

    style_index = prompt.index("REFERENCE GAME")
    technical_index = prompt.index(TECHNICAL_REQUIREMENTS_HEADING)
    assert style_index < technical_index, (
        "the style block must be read before the technical requirements"
    )
    assert prompt.rstrip().endswith("Studio colours the sprite itself afterwards."), (
        "the technical requirements must be the last thing the prompt says"
    )


def test_source_urls_do_not_reach_the_image_prompt():
    """A dossier's source URLs (see `reference.reference_prompt`) are for a
    person auditing the dossier, not for an image model -- to a model they
    are noise sitting at the prompt's most heavily weighted position.
    `compose_prompt` composes its own, shorter style block instead of
    reusing `reference_prompt` wholesale, precisely so those URLs never
    reach the model at all.
    """
    project = _project()
    entity = next(e for e in project.entities if e.role == "player")
    dossier = _dossier()
    assert dossier.sources, "the fixture dossier must actually carry sources to be a real check"

    prompt = compose_prompt(project, entity, dossier)

    for source in dossier.sources:
        assert source.url not in prompt
    assert "Researched from" not in prompt


def test_prompt_with_an_unidentified_dossier_also_falls_back():
    """An unidentified dossier's `visual_style`/`publisher` are blank by
    construction (see `reference.RESEARCH_SYSTEM_PROMPT`), so it carries
    nothing to quote -- the fallback used for no dossier at all applies here
    too.
    """
    project = _project()
    entity = next(e for e in project.entities if e.role == "enemy")
    unidentified = GameReference(identified=False, confidence="low")

    prompt = compose_prompt(project, entity, unidentified)

    assert entity.role in prompt
    assert project.presentation.style in prompt


# --- Frames returned by SpriteArtist ----------------------------------------


def test_draw_frames_returns_four_sprite_sized_frames():
    project = _project()
    entity = next(e for e in project.entities if e.role == "player")
    image = _solid_image((900, 900), (255, 255, 255, 255))
    pixels = image.load()
    for y in range(300, 600):
        for x in range(200, 700):
            pixels[x, y] = (255, 0, 0, 255)
    artist = SpriteArtist(_FakeGenerator(image))

    frames = artist.draw_frames(project, entity)

    assert len(frames) == FRAMES_PER_SHEET
    assert all(frame.size == (SPRITE_SIZE, SPRITE_SIZE) for frame in frames)


def test_draw_frames_asks_the_generator_for_the_composed_prompt():
    project = _project()
    entity = next(e for e in project.entities if e.role == "player")
    generator = _FakeGenerator(_solid_image((512, 128), (0, 0, 0, 255)))
    artist = SpriteArtist(generator)

    artist.draw_frames(project, entity)

    assert generator.prompts == [compose_prompt(project, entity, None)]


@pytest.mark.parametrize(
    "size,colour",
    [
        ((1, 1), (10, 20, 30, 255)),
        ((37, 501), (10, 20, 30, 255)),
        ((2000, 2000), (10, 20, 30, 255)),
        ((500, 500), (255, 255, 255, 255)),  # entirely background: no object at all
    ],
)
def test_a_wrongly_sized_image_still_yields_valid_frames(
    size: tuple[int, int], colour: tuple[int, int, int, int]
):
    """Neither a tiny image, an oddly-proportioned one, an oversized one, nor
    one with nothing drawn on it (all background) should ever reach
    `split_frames` in a shape it cannot cut cleanly -- `draw_frames` forces the
    sheet to its real, final size before splitting, precisely so a
    badly-sized response cannot silently produce broken frames.
    """
    project = _project()
    entity = next(e for e in project.entities if e.role == "player")
    artist = SpriteArtist(_FakeGenerator(_solid_image(size, colour)))

    frames = artist.draw_frames(project, entity)

    assert len(frames) == FRAMES_PER_SHEET
    assert all(frame.size == (SPRITE_SIZE, SPRITE_SIZE) for frame in frames)


def test_draw_frames_keeps_all_four_distinct_poses():
    """The regression this guards against: cleaning the whole sheet before
    splitting it keeps only the single largest connected pose and silently
    blanks the other three, so every generated sprite would animate as one
    real frame plus three empty ones. A fake generator returning a single
    fixed blob cannot catch that -- every "frame" it produced would trivially
    look the same either way -- so this one returns four distinct,
    non-touching poses instead (`_four_pose_sheet`) and checks that all four
    survive, and that they are not all the same frame repeated.
    """
    project = _project()
    entity = next(e for e in project.entities if e.role == "player")
    artist = SpriteArtist(_FakeGenerator(_four_pose_sheet()))

    frames = artist.draw_frames(project, entity)

    assert len(frames) == FRAMES_PER_SHEET
    non_background_pixel_counts = [
        sum(1 for pixel in frame.convert("RGB").getdata() if pixel != (255, 255, 255))
        for frame in frames
    ]
    assert all(count > 0 for count in non_background_pixel_counts), (
        f"every frame must carry drawn pixels of its own pose; got {non_background_pixel_counts}"
    )
    assert len({frame.tobytes() for frame in frames}) == FRAMES_PER_SHEET, (
        "the four frames must differ from each other -- four distinct poses went in"
    )


def test_the_sheet_and_request_sizes_are_consistent_with_the_packer():
    assert SHEET_WIDTH == FRAMES_PER_SHEET * SPRITE_SIZE
    assert SHEET_HEIGHT == SPRITE_SIZE
    assert REQUEST_WIDTH % FRAMES_PER_SHEET == 0


# --- The real defect: a genuine model response, packed all the way to bytes ---
#
# Every test above builds its own RGBA fixtures. That is exactly why none of
# them could have caught the defect this module was fixed for: `gpt-image-1`
# returns opaque RGB with no alpha channel whatsoever, and `_clean_image` /
# `_scale_image` (image_utils.py) preserve that -- they never introduce
# transparency. `spriting.pack_spectrum` and `pack_cpc` both decide "is this
# pixel drawn" from alpha, so an RGB frame handed to `spriting._checked`'s
# blanket `.convert("RGBA")` reads as opaque everywhere, and every sprite
# packs as a solid rectangle. Only a real, no-alpha fixture run through the
# real chain -- `SpriteArtist.draw_frames` to `spriting.pack_spectrum`/
# `pack_cpc` -- can catch that; see `_FIXTURE_SHEET` above.


def _spectrum_set_bits_per_frame(packed) -> list[int]:
    return [
        sum(
            bin(byte).count("1")
            for byte in packed.data[index * packed.bytes_per_frame : (index + 1) * packed.bytes_per_frame]
        )
        for index in range(packed.frames)
    ]


def _cpc_mode1_opaque_pixels_per_frame(packed) -> list[int]:
    """How many of a mode-1 CPC frame's 256 pixels are opaque (pen != 3, the
    all-set "keep the background" pen `pack_cpc` gives every transparent
    pixel).

    Inverts `spriting._pack_byte_m1`'s `g(pen) = (pen&1)<<4 | (pen&2)>>1` /
    `byte = g(a)<<3 | g(b)<<2 | g(c)<<1 | g(d)` bit for bit: pen `pos`'s low
    bit lands at byte bit `7 - pos`, its high bit at byte bit `3 - pos`. This
    mirrors `pack_cpc` itself rather than re-deriving the layout by guessing,
    and was checked, while writing this test, against this exact fixture's
    known per-pixel alpha (`frame.getdata()`) before being trusted here.
    """
    counts = []
    for index in range(packed.frames):
        frame_bytes = packed.data[index * packed.bytes_per_frame : (index + 1) * packed.bytes_per_frame]
        opaque = 0
        for mask_byte in frame_bytes[0::2]:  # every other byte is the mask; see pack_cpc's docstring
            for pos in range(4):
                low_bit = (mask_byte >> (7 - pos)) & 1
                high_bit = (mask_byte >> (3 - pos)) & 1
                pen = low_bit | (high_bit << 1)
                if pen != 3:
                    opaque += 1
        counts.append(opaque)
    return counts


def test_a_real_black_on_white_sheet_packs_as_a_recognisable_silhouette_not_a_solid_block():
    """The regression test for the defect itself: a real `gpt-image-1`
    response, run through `SpriteArtist.draw_frames` and
    `spriting.pack_spectrum` exactly as `compiler.render_project` does,
    must come out as a running figure -- not a solid rectangle (256 set
    pixels, the bug) and not a blank frame (0 set pixels, the same bug's
    mirror image: a fix that keyed out the figure along with the background
    would be just as broken and just as invisible to a test that only
    checked "not 256").
    """
    project = _project(TargetPlatform.SPECTRUM)
    entity = next(e for e in project.entities if e.role == "player")
    with Image.open(_FIXTURE_SHEET) as sheet:
        artist = SpriteArtist(_FakeGenerator(sheet.copy()))
        frames = artist.draw_frames(project, entity)

    packed = pack_spectrum(frames)
    set_bits = _spectrum_set_bits_per_frame(packed)

    assert len(set_bits) == FRAMES_PER_SHEET
    for index, count in enumerate(set_bits):
        assert count not in (0, 256), f"frame {index} packed to {count}/256 set pixels"


def test_the_same_real_sheet_does_not_pack_as_a_solid_block_for_the_cpc_either():
    """`pack_cpc` makes the same alpha-threshold decision `pack_spectrum`
    does (see `spriting.ALPHA_THRESHOLD` and both packers' `a >=
    ALPHA_THRESHOLD` checks), on the same frames -- so it was checked for the
    same defect on the same input, and the same fix (`_key_out_background`)
    covers it without any change to `pack_cpc` itself.
    """
    project = _project(TargetPlatform.AMSTRAD_CPC)
    entity = next(e for e in project.entities if e.role == "player")
    with Image.open(_FIXTURE_SHEET) as sheet:
        artist = SpriteArtist(_FakeGenerator(sheet.copy()))
        frames = artist.draw_frames(project, entity)

    packed = pack_cpc(frames, mode=1, palette=[(0, 0, 0), (255, 255, 255)])
    opaque_counts = _cpc_mode1_opaque_pixels_per_frame(packed)

    assert len(opaque_counts) == FRAMES_PER_SHEET
    for index, count in enumerate(opaque_counts):
        assert count not in (0, 256), f"frame {index} packed to {count}/256 opaque pixels"


def test_the_real_black_on_white_fixture_yields_a_visible_attribute():
    """The second half of the same real-run defect: `pack_spectrum` derives
    the Spectrum attribute from the frames' dominant *opaque* colour (see
    `spriting._dominant_opaque_rgb`). Once `_key_out_background` keys this
    fixture's white away, that dominant colour is the black figure itself,
    which used to pack to PAPER_BLACK | INK_BLACK (0x00) -- a correctly
    shaped sprite nobody could ever see, on this exact fixture.

    "attribute != 0" would not actually prove the sprite is visible (a lone
    FLASH bit is nonzero and still invisible, for instance), so this
    decomposes the byte into paper, ink and bright and checks that ink and
    paper genuinely differ -- see `spriting._MONOCHROME_FALLBACK_INK`.
    """
    project = _project(TargetPlatform.SPECTRUM)
    entity = next(e for e in project.entities if e.role == "player")
    with Image.open(_FIXTURE_SHEET) as sheet:
        artist = SpriteArtist(_FakeGenerator(sheet.copy()))
        frames = artist.draw_frames(project, entity)

    packed = pack_spectrum(frames)
    ink = packed.attribute & 0x07
    paper = (packed.attribute >> 3) & 0x07
    bright = bool(packed.attribute & 0x40)

    assert paper == 0x00  # PAPER_BLACK, as every current typology draws on
    assert ink != paper, f"ink ({ink}) must differ from paper ({paper}) to be visible at all"
    assert ink == 0x07  # INK_WHITE: max contrast, since this fixture's figure is black
    assert bright is True


def test_coloured_art_still_yields_its_own_colour_not_the_monochrome_fallback():
    """The monochrome fallback (`spriting._MONOCHROME_FALLBACK_INK`) must
    trigger only for art whose dominant opaque colour is genuinely black --
    real colour, the kind CPC mode 0 art is meant to carry, must still win
    exactly as it did before this fix.
    """
    project = _project(TargetPlatform.SPECTRUM)
    entity = next(e for e in project.entities if e.role == "player")
    cyan = _solid_image((512, 128), (0, 255, 255, 255))
    artist = SpriteArtist(_FakeGenerator(cyan))

    frames = artist.draw_frames(project, entity)
    packed = pack_spectrum(frames)

    assert packed.attribute == 0x45  # INK_CYAN | BRIGHT, unchanged by the fallback
