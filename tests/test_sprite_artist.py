"""SpriteArtist, judged on the prompt it writes and the frames it returns.

No API call is made anywhere in this file: every generator is a fake that
returns a fixed, in-memory image, exactly like `test_studio_generator.py` does
for `ResponsesProgramWriter`'s client.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageDraw

from llmz80.studio.models import GameProject, GenreId, TargetPlatform, VideoMode
from llmz80.studio.packs import create_default_project
from llmz80.studio.reference import GameReference, ReferenceSource
from llmz80.studio.sprite_artist import (
    BACKGROUND_TOLERANCE,
    FRAMES_PER_SHEET,
    MAX_DRAW_ATTEMPTS,
    REQUEST_HEIGHT,
    REQUEST_WIDTH,
    SHEET_HEIGHT,
    SHEET_WIDTH,
    TECHNICAL_REQUIREMENTS_HEADING,
    SpriteArtist,
    _frame_from_column,
    _sheet_columns,
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


def _dark_background_sheet() -> Image.Image:
    """The real fixture (`_FIXTURE_SHEET`), recoloured so the same running
    figure sits on a near-black background instead of white -- built from
    the real fixture rather than hand-drawn, so this reproduces the actual
    failure a real run against *Abu Simbel Profanation* showed: two of three
    sprites came back as dark grey art on a near-black background, and
    `_key_out_background`'s old fixed-white assumption packed the entire
    frame as one solid opaque block because nothing in it was close enough
    to white to key out.

    The fixture's own background is near-white (some JPEG-ish noise sits a
    few levels below 255); every pixel at least that bright is recoloured to
    a near-black "Egyptian" background, and everything else -- the drawn
    figure -- to a dark grey a few shades lighter, so the two stay
    distinguishable from each other exactly the way the real broken
    responses were (a *dark grey smear*, not a black one, *on* near-black --
    not indistinguishable from it).
    """
    with Image.open(_FIXTURE_SHEET) as original:
        rgb = np.asarray(original.convert("RGB")).astype(np.int16)
    is_background = rgb.mean(axis=2) > 200
    dark = np.empty_like(rgb)
    dark[is_background] = (12, 12, 16)
    dark[~is_background] = (90, 90, 96)
    return Image.fromarray(dark.astype(np.uint8), mode="RGB")


def _solid_block_sheet() -> Image.Image:
    """A raw sheet with one *filled* rectangle per column, on white --
    unlike `_four_pose_sheet`'s ellipses, a filled rectangle leaves no
    background inside its own bounding box, so `_clean_image`'s tight crop
    to that box comes back with every pixel opaque: 256 of 256, a solid
    block. A stand-in for a badly botched generation (the model drew a flat
    shape instead of a figure), used as the *first*, failing attempt in the
    retry tests below.
    """
    column_width = 200
    height = 200
    width = column_width * FRAMES_PER_SHEET
    sheet = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    for index, colour in enumerate(_POSE_COLOURS):
        offset = index * column_width
        draw.rectangle((offset + 10, 10, offset + column_width - 10, height - 10), fill=colour)
    return sheet


class _FakeGenerator:
    """Returns one fixed image and remembers every prompt it was asked for."""

    def __init__(self, image: Image.Image) -> None:
        self.image = image
        self.prompts: list[str] = []

    def generate_image(self, prompt: str) -> Image.Image:
        self.prompts.append(prompt)
        return self.image


class _SequenceGenerator:
    """Returns one image per call, in order -- the fake this file's retry
    tests need, since `SpriteArtist.draw_frames` must ask again after a
    judged failure and the second ask has to actually get something
    different back. Remembers every prompt too, so a test can read the
    feedback appended to the second one.
    """

    def __init__(self, images: list[Image.Image]) -> None:
        self.images = list(images)
        self.prompts: list[str] = []

    def generate_image(self, prompt: str) -> Image.Image:
        self.prompts.append(prompt)
        return self.images[len(self.prompts) - 1]


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


def _four_pose_sheet(colours: list[tuple[int, int, int, int]] = _POSE_COLOURS) -> Image.Image:
    """A raw sheet with one solid, differently sized and positioned, non-
    touching blob per column -- a stand-in for four genuinely different
    animation poses side by side, which is exactly what the composed prompt
    asks a real model to draw.

    This is the shape the old clean-the-whole-sheet-then-split order got
    wrong: `_clean_image` keeps only the single largest connected component,
    so run across the whole sheet it would keep one pose and blank the other
    three. Run per column, after splitting (`SpriteArtist.draw_frames`), it
    keeps all four -- see `test_draw_frames_keeps_all_four_distinct_poses`.

    Each blob is an *ellipse*, not a filled rectangle -- an earlier version
    of this fixture used rectangles, and `_judge_frames` (added for the same
    real run that added `_detect_background`) correctly refused every frame
    they produced: `_clean_image` crops tightly to a shape's own bounding
    box, and a solid rectangle has no background left inside that box once
    cropped -- it reads as a 256-of-256 solid block, indistinguishable from
    the real defect this module now catches. An ellipse leaves its own
    bounding box's corners as genuine background, the way a real character's
    silhouette (limbs apart, gaps around the body) always does.
    """
    column_width = 200
    height = 200
    width = column_width * FRAMES_PER_SHEET
    sheet = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    # A different size and position per column, so no single bounding-box
    # crop could coincidentally cover more than one of them, and so frames
    # cannot come out pixel-identical even where two columns share a colour.
    boxes = [
        (20, 20, 60, 60),  # small, top-left of its column
        (30, 120, 170, 180),  # wide, low in its column
        (20, 20, 180, 180),  # large, fills most of its column
        (80, 80, 120, 120),  # small, centred
    ]
    for index, (x0, y0, x1, y1) in enumerate(boxes):
        offset = index * column_width
        draw.ellipse((offset + x0, y0, offset + x1, y1), fill=colours[index % len(colours)])
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
    artist = SpriteArtist(_FakeGenerator(_four_pose_sheet()))

    frames = artist.draw_frames(project, entity)

    assert len(frames) == FRAMES_PER_SHEET
    assert all(frame.size == (SPRITE_SIZE, SPRITE_SIZE) for frame in frames)


def test_draw_frames_asks_the_generator_for_the_composed_prompt():
    project = _project()
    entity = next(e for e in project.entities if e.role == "player")
    generator = _FakeGenerator(_four_pose_sheet())
    artist = SpriteArtist(generator)

    artist.draw_frames(project, entity)

    assert generator.prompts == [compose_prompt(project, entity, None)]


# --- Pathological sheet sizes -------------------------------------------------
#
# `_sheet_columns`'s own contract -- always return `FRAMES_PER_SHEET` equal
# columns, however oddly the raw response is sized -- is a different concern
# from whether the *content* those columns hold is a sprite (`_judge_frames`'s
# job). A tiny (1x1) or entirely-flat response has no content to judge as a
# sprite at all -- `_judge_frames` correctly refuses it, retries, and (with a
# generator that always returns the same flat image) eventually raises; see
# `test_a_persistently_bad_response_raises_with_the_last_reason`. What is
# tested here is narrower and does not go through `draw_frames`/the judge at
# all: that `_sheet_columns` itself never raises and always returns the right
# number of columns, regardless of how the model sized its response.


@pytest.mark.parametrize(
    "size",
    [(1, 1), (37, 501), (2000, 2000), (500, 500)],
)
def test_sheet_columns_handles_pathological_sizes(size: tuple[int, int]):
    sheet = _solid_image(size, (10, 20, 30, 255))

    columns = _sheet_columns(sheet, FRAMES_PER_SHEET)

    assert len(columns) == FRAMES_PER_SHEET


def test_draw_frames_survives_an_oddly_sized_but_real_response():
    """A real model response is under no obligation to honour
    `REQUEST_WIDTH`/`REQUEST_HEIGHT` -- an oddly-proportioned or oversized
    reply is routine, not pathological, and unlike the sizes above it still
    carries real, judgeable content. `draw_frames` must reduce it to
    `FRAMES_PER_SHEET` real frames without needing a retry.
    """
    project = _project()
    entity = next(e for e in project.entities if e.role == "player")
    odd = _four_pose_sheet().resize((999, 333), Image.Resampling.NEAREST)
    generator = _FakeGenerator(odd)
    artist = SpriteArtist(generator)

    frames = artist.draw_frames(project, entity)

    assert len(frames) == FRAMES_PER_SHEET
    assert all(frame.size == (SPRITE_SIZE, SPRITE_SIZE) for frame in frames)
    assert len(generator.prompts) == 1, "real, judgeable content should not need a retry"


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
    cyan = (0, 255, 255, 255)
    artist = SpriteArtist(_FakeGenerator(_four_pose_sheet([cyan, cyan, cyan, cyan])))

    frames = artist.draw_frames(project, entity)
    packed = pack_spectrum(frames)

    assert packed.attribute == 0x45  # INK_CYAN | BRIGHT, unchanged by the fallback


# --- Judging a generated sheet, and retrying a bad one ------------------------
#
# The real run against *Abu Simbel Profanation* returned two sprites -- out
# of three -- as dark grey art on a near-black background, and the pipeline
# as it stood then had no way to notice: it keyed a fixed white out of every
# frame regardless of what the frame actually showed, so a dark frame packed
# as a solid 16x16 block. `_detect_background` (read the real background off
# each frame's own border) and `_judge_frames` (catch a solid, blank, or
# all-identical sheet and retry with feedback) exist because of that run.


def test_a_dark_background_response_still_yields_usable_frames():
    """The exact failure the real run showed: art drawn on a near-black
    background instead of the requested pure white. The old, fixed-white
    `_key_out_background` packed a frame like this as one solid opaque
    block, because nothing in it was close enough to white to key out.
    `_detect_background` reads the frame's own border instead of assuming
    white, so this must come back as a real silhouette -- and, since
    detection gets it right immediately, with no retry needed.
    """
    project = _project(TargetPlatform.SPECTRUM)
    entity = next(e for e in project.entities if e.role == "player")
    generator = _FakeGenerator(_dark_background_sheet())
    artist = SpriteArtist(generator)

    frames = artist.draw_frames(project, entity)

    assert len(frames) == FRAMES_PER_SHEET
    total = SPRITE_SIZE * SPRITE_SIZE
    for index, frame in enumerate(frames):
        opaque = int((np.asarray(frame)[..., 3] >= 128).sum())
        assert 0 < opaque < total, (
            f"frame {index} packed to {opaque}/{total} -- still a solid block or blank"
        )
    assert len(generator.prompts) == 1, "a correctly detected background needs no retry"


def test_a_solid_block_is_retried_and_the_feedback_names_the_problem():
    """A first attempt that comes back as a solid block (`_solid_block_sheet`)
    must be retried, not packed as-is -- and the second request must carry
    feedback that names exactly what was wrong, the way
    `reference_design.repair_feedback` names a refused proposal's specific
    fields rather than just saying "try again".
    """
    project = _project(TargetPlatform.SPECTRUM)
    entity = next(e for e in project.entities if e.role == "player")
    good = _four_pose_sheet()
    generator = _SequenceGenerator([_solid_block_sheet(), good])
    artist = SpriteArtist(generator)

    frames = artist.draw_frames(project, entity)

    assert len(frames) == FRAMES_PER_SHEET
    assert len(generator.prompts) == 2, "the solid-block first attempt must be retried once"
    assert generator.prompts[0] == compose_prompt(project, entity, None)
    feedback = generator.prompts[1]
    assert "THE SHEET WAS REJECTED" in feedback
    assert "solid block" in feedback
    assert "256 of 256" in feedback
    assert frames.attempts == 2
    assert frames.sheet is good
    assert len(frames.repairs) == 1
    assert "solid block" in frames.repairs[0]


def test_a_persistently_bad_response_raises_with_the_last_reason():
    """Once `MAX_DRAW_ATTEMPTS` are exhausted without a judged-valid sheet,
    `draw_frames` must raise rather than pack the last bad attempt anyway --
    the same shape `reference_design.propose_and_apply` raises in when a
    proposal cannot be repaired in its own attempt budget, carrying the last
    refusal reason forward instead of a generic failure.
    """
    project = _project(TargetPlatform.SPECTRUM)
    entity = next(e for e in project.entities if e.role == "player")
    generator = _FakeGenerator(_solid_block_sheet())
    artist = SpriteArtist(generator)

    with pytest.raises(ValueError) as excinfo:
        artist.draw_frames(project, entity)

    assert len(generator.prompts) == MAX_DRAW_ATTEMPTS
    message = str(excinfo.value)
    assert f"{MAX_DRAW_ATTEMPTS} attempts" in message
    assert "solid block" in message
    assert "256 of 256" in message


def test_a_sheet_of_four_identical_frames_is_judged_and_named_as_such():
    """A sheet that draws one pose and repeats it four times is just as much
    "not a sprite" as a solid block or a blank frame -- no animation was
    actually drawn. This is checked independently of the pixel-count check:
    a repeated pose need not pack to 0 or 256 to still be a single frame
    wearing four different filenames.
    """
    project = _project(TargetPlatform.SPECTRUM)
    entity = next(e for e in project.entities if e.role == "player")
    repeated = _solid_image((512, 128), (255, 255, 255, 255))
    draw = ImageDraw.Draw(repeated)
    for index in range(FRAMES_PER_SHEET):
        offset = index * (repeated.width // FRAMES_PER_SHEET)
        draw.ellipse((offset + 20, 20, offset + 108, 108), fill=(0, 0, 0, 255))
    generator = _FakeGenerator(repeated)
    artist = SpriteArtist(generator)

    with pytest.raises(ValueError) as excinfo:
        artist.draw_frames(project, entity)

    assert len(generator.prompts) == MAX_DRAW_ATTEMPTS
    assert "EVERY FRAME IS THE SAME IMAGE" in str(excinfo.value)


def test_a_sprite_touching_its_frame_edge_is_not_destroyed_by_background_detection():
    """`_detect_background` reads the majority colour of a frame's border,
    which is only correct while the figure does not dominate that border --
    true of every current sprite prompt, which centres a figure well inside
    its frame, but worth pinning down explicitly: a figure whose feet touch
    the very edge of its frame must still come out as a real silhouette, not
    be wiped out as "it must all be background" nor kept whole as "it must
    all be figure".

    Built from the real fixture (`_FIXTURE_SHEET`) rather than hand-drawn:
    each of its four real poses is cropped to remove its own bottom margin,
    so the figure's lowest real pixels sit exactly on the new bottom edge --
    a genuine silhouette that touches an edge, not a stand-in shape that
    only resembles one.
    """
    with Image.open(_FIXTURE_SHEET) as sheet:
        sheet = sheet.convert("RGB")
    width = sheet.width // FRAMES_PER_SHEET
    total = SPRITE_SIZE * SPRITE_SIZE
    for index in range(FRAMES_PER_SHEET):
        column = sheet.crop((index * width, 0, (index + 1) * width, sheet.height))
        arr = np.asarray(column).astype(np.int16)
        is_figure = ~np.all(np.abs(arr - 255) <= BACKGROUND_TOLERANCE, axis=2)
        figure_rows, _ = np.where(is_figure)
        edge_column = column.crop((0, 0, column.width, int(figure_rows.max()) + 1))

        frame = _frame_from_column(edge_column)

        alpha = np.asarray(frame)[..., 3]
        opaque = int((alpha >= 128).sum())
        assert 0 < opaque < total, (
            f"frame {index}: {opaque}/{total} opaque -- the figure must survive as a "
            "real silhouette, neither wiped out nor kept whole as background"
        )
        assert (alpha[-1, :] >= 128).any(), (
            f"frame {index}: the pixels touching the frame's own bottom edge must "
            "remain part of the figure, not be keyed away as background"
        )
