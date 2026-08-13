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

from image_utils import _clean_image
from llmz80.studio.models import GameProject, TargetPlatform, VideoMode
from llmz80.studio.reference import GameReference, ReferenceSource
from llmz80.studio.samples import blank_project
from llmz80.studio.sprite_artist import (
    BACKGROUND_TOLERANCE,
    FRAMES_PER_SHEET,
    HALO_TOLERANCE,
    MAX_DRAW_ATTEMPTS,
    REQUEST_HEIGHT,
    REQUEST_WIDTH,
    SHEET_HEIGHT,
    SHEET_WIDTH,
    TECHNICAL_REQUIREMENTS_HEADING,
    SpriteArtist,
    _binarize_against_background,
    _detect_background,
    _fit_to_frame,
    _frame_from_column,
    _key_out_background,
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

#: One real column, cropped straight out of the `hero.raw.png` sheet a real
#: run against *Abu Simbel Profanation* produced -- the actual response that
#: exposed the halo defect `_binarize_against_background` fixes (see its
#: docstring and `HALO_TOLERANCE`'s), not a hand-drawn stand-in for one. The
#: detected background here is (70, 70, 71) -- the model drew on grey, not
#: the pure white the prompt asked for, a separate, already-fixed defect
#: (`_detect_background`) -- and the figure fades into it through a broad,
#: soft vignette rather than a hard edge: exactly the "no anti-aliasing"
#: violation this fixture exists to prove the fix survives.
_HALOED_HERO_COLUMN = Path(__file__).parent / "fixtures" / "sprite_sheet_haloed_hero_column.png"

#: One real column, cropped out of the same run's `enemy.raw.png` sheet --
#: the sprite the module docstring already calls out as "genuinely good",
#: whose thin limbs are the real risk `HALO_TOLERANCE` has to respect: a
#: threshold generous enough to discount `hero`'s halo but careless with a
#: thin, low-contrast limb edge would trade one bad sprite for another.
_ENEMY_THIN_LIMB_COLUMN = (
    Path(__file__).parent / "fixtures" / "sprite_sheet_enemy_thin_limb_column.png"
)


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
    to that box comes back with every pixel opaque. A stand-in for a badly
    botched generation (the model drew a flat shape instead of a figure),
    used as the *first*, failing attempt in the retry tests below.

    The rectangle is inset from its column by only 3 pixels a side (not the
    generous gap `_four_pose_sheet`'s poses leave) so that, once
    `_fit_to_frame` scales it down without distortion (see its docstring),
    it still rounds up to fill the full 16x16 frame -- 256 of 256, a literal
    solid block -- rather than landing a pixel or two short of it the way a
    wider margin would. This is deliberately fragile in the same way the
    real defect was: a real "the model drew a rectangle, not a character"
    response leaves little to no gap either, which is exactly why
    `_judge_frames` must still catch it.
    """
    column_width = 200
    height = 200
    width = column_width * FRAMES_PER_SHEET
    margin = 3
    sheet = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    for index, colour in enumerate(_POSE_COLOURS):
        offset = index * column_width
        draw.rectangle(
            (offset + margin, margin, offset + column_width - margin, height - margin),
            fill=colour,
        )
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
    return blank_project("Test Game", platform)


def _cpc_mode0_project() -> GameProject:
    """`blank_project` always builds CPC projects in mode 1; mode 0
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


def _column_with_object(
    size: tuple[int, int],
    box: tuple[int, int, int, int],
    colour: tuple[int, int, int, int] = (0, 0, 0, 255),
) -> Image.Image:
    """A raw column, `size` pixels, pure white background, with one solid
    rectangle drawn at `box` -- the minimal shape `_fit_to_frame`'s tests
    below need: a real bounding box of a known width and height, with real
    background left inside it (so `_clean_image` does not read it as a
    solid block) is not required here since these tests check geometry, not
    `_judge_frames`'s pass/fail line.
    """
    image = Image.new("RGBA", size, (255, 255, 255, 255))
    ImageDraw.Draw(image).rectangle(box, fill=colour)
    return image


def _old_frame_from_column(column: Image.Image) -> Image.Image:
    """`_frame_from_column` exactly as it read before `_binarize_against_background`
    existed: `_clean_image` runs straight on the raw column, with no halo
    discounted first. Kept here, reconstructed rather than imported, only so
    the halo tests below can show the defect the fix replaced is still
    reachable to compare against -- not as a second implementation anything
    else depends on.
    """
    background = _detect_background(column, BACKGROUND_TOLERANCE)
    cleaned = _clean_image(column, background_color=background, tolerance=BACKGROUND_TOLERANCE)
    fitted = _fit_to_frame(cleaned, SPRITE_SIZE, background, reference_width=column.width)
    return _key_out_background(fitted, background, BACKGROUND_TOLERANCE)


def _opaque_bbox(frame: Image.Image) -> tuple[int, int] | None:
    """The (width, height) of `frame`'s opaque region, or `None` if `frame`
    carries no opaque pixels at all -- used by the tests below to check the
    *shape* `_fit_to_frame` produced, not just how many pixels ended up set.
    """
    alpha = np.asarray(frame)[..., 3]
    ys, xs = np.where(alpha >= 128)
    if len(xs) == 0:
        return None
    return int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)


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
    project = _project(TargetPlatform.AMSTRAD_CPC)  # blank_project builds mode 1
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


def test_a_statically_repeated_pose_is_accepted_without_retrying():
    """A collectible like a `pellet` does not animate -- a model drawing it
    identically in all four frames drew it *correctly*, not wrongly. An
    earlier version of `_judge_frames` refused a sheet whose frames were all
    pixel-identical on principle, which cost three wasted image generations
    on exactly this response before raising (see `_judge_frames`'s
    docstring for why that check was dropped rather than made to depend on
    `EntitySpec.role`). Only the 0/256 pixel-count check remains, and a
    real, non-degenerate silhouette repeated four times does not trip it.
    """
    project = _project(TargetPlatform.SPECTRUM)
    entity = next(e for e in project.entities if e.role == "collectible")
    static = _solid_image((512, 128), (255, 255, 255, 255))
    draw = ImageDraw.Draw(static)
    for index in range(FRAMES_PER_SHEET):
        offset = index * (static.width // FRAMES_PER_SHEET)
        draw.ellipse((offset + 20, 20, offset + 108, 108), fill=(0, 0, 0, 255))
    generator = _FakeGenerator(static)
    artist = SpriteArtist(generator)

    frames = artist.draw_frames(project, entity)

    assert len(frames) == FRAMES_PER_SHEET
    assert len(generator.prompts) == 1, "a correctly-static sprite must not be retried"
    assert frames.attempts == 1
    assert len({frame.tobytes() for frame in frames}) == 1, (
        "the four frames should indeed come back identical -- that is the point"
    )


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


# --- Discounting an anti-aliased halo before `_clean_image` sees it --------
#
# A real run against *Abu Simbel Profanation* left `hero`'s sheet with a
# soft, out-of-spec halo around the drawn figure -- a vignette fading
# gradually from the detected background toward the figure, in violation of
# `_technical_constraints`'s explicit "no anti-aliasing" line. `_clean_image`
# (see `image_utils.py`) counts every pixel that differs from the detected
# background by more than `BACKGROUND_TOLERANCE` as figure, and keeps the
# *bounding box* of whatever connected region that produces -- so a halo
# wide enough to keep differing from background past that tolerance, all the
# way to a frame's edge, drags the bounding box out to the full column width
# even though the actually-drawn pose is far narrower. Fitting a box that
# wide into `SPRITE_SIZE` leaves a bar, not a figure.
# `_binarize_against_background` is the fix: snap everything within
# `HALO_TOLERANCE` of the background to that exact colour before
# `_clean_image` ever runs, so a halo that would have dragged the bounding
# box out no longer can -- while a threshold `HALO_TOLERANCE` genuinely
# comfortably clears (a limb drawn, like the rest of a compliant sheet, at
# full contrast) survives untouched.


def test_binarizing_a_haloed_column_tightens_the_bounding_box_the_old_path_left_wide():
    """The core regression test for the `hero` defect: run the same real,
    haloed column through the pre-fix path (`_clean_image` straight on the
    raw column, exactly what `_frame_from_column` did before this fix) and
    through the new one (`_binarize_against_background` first), and compare
    the bounding boxes `_clean_image` crops to.

    The old path is reconstructed here, not imported, because it no longer
    exists as its own function -- `_frame_from_column` *is* the fix now (see
    its docstring). Rebuilding the two calls it used to make is what lets
    this test show the old behaviour is still there to compare against, not
    just assert a number against the current code's own output.
    """
    column = Image.open(_HALOED_HERO_COLUMN).convert("RGB")
    background = _detect_background(column, BACKGROUND_TOLERANCE)

    old_cleaned = _clean_image(column, background_color=background, tolerance=BACKGROUND_TOLERANCE)
    binarized = _binarize_against_background(column, background, HALO_TOLERANCE)
    new_cleaned = _clean_image(binarized, background_color=background, tolerance=BACKGROUND_TOLERANCE)

    assert old_cleaned.width == column.width, (
        "sanity check on the fixture itself: the old path must still reproduce the "
        f"known defect (a bounding box as wide as the column, {column.width}px) -- got "
        f"{old_cleaned.width}px; the fixture may no longer carry a real halo"
    )
    assert new_cleaned.width < old_cleaned.width, (
        f"binarizing first should tighten the bounding box the old path left at "
        f"{old_cleaned.size}; got {new_cleaned.size}, no narrower"
    )
    assert new_cleaned.width * new_cleaned.height < old_cleaned.width * old_cleaned.height


def test_a_thin_limb_survives_the_halo_threshold():
    """`HALO_TOLERANCE`'s other side: a real sprite with genuine thin limbs
    (the module docstring's `enemy` -- "four recognisable humanoid creature
    silhouettes with posture and limbs") must come through
    `_binarize_against_background` essentially unchanged, not eroded the way
    a too-aggressive threshold would erode exactly this kind of thin,
    lower-contrast detail.

    Compares the same real column's old- and new-path opaque counts, both
    carried all the way through fitting and keying (`_old_frame_from_column`
    vs `_frame_from_column`) so the two are measured on equal footing. The
    bound is tight -- within 2 pixels, not just "still nonzero" -- because a
    threshold that quietly ate half a limb would still pass a weaker check;
    on the real fixture the two paths in fact differ by exactly one pixel.
    """
    column = Image.open(_ENEMY_THIN_LIMB_COLUMN).convert("RGB")

    old_count = int((np.asarray(_old_frame_from_column(column))[..., 3] >= 128).sum())
    new_count = int((np.asarray(_frame_from_column(column))[..., 3] >= 128).sum())

    assert new_count > 0, "the limb-bearing figure must survive as a real silhouette"
    assert abs(new_count - old_count) <= 2, (
        f"a thin limb must not be eaten by the halo threshold: old path kept "
        f"{old_count} opaque pixels once fitted and keyed, new path kept {new_count}"
    )


# --- Fitting a cleaned pose into its 16x16 frame without distorting it ------
#
# The real defect a run against *Abu Simbel Profanation* exposed: `_clean_image`
# crops tightly to the drawn pose's own bounding box, and the code this
# replaced then handed that crop straight to `_scale_image(cleaned,
# SPRITE_SIZE, SPRITE_SIZE)`, which stretches width and height independently
# to fill the target exactly -- whatever the crop's real proportions were. A
# `hero` standing figure came out squashed into a near-solid blob; a `pellet`
# collectible came out inflated to fill the frame edge to edge. `_fit_to_frame`
# is the fix: scale by one factor, derived from both the crop's own aspect
# ratio and the column it was cut from (see its docstring for why both), and
# centre the result, leaving genuine background margin instead of distortion.


def test_a_narrower_than_tall_object_keeps_its_proportions():
    """A standing figure, cropped narrower than it is tall, must come out
    narrower than tall in its 16x16 frame too -- not stretched into a
    square. Here the crop (40x200, inside a 120-wide column) is far taller
    than the column is wide, so `_fit_to_frame`'s "contain" factor -- map
    the crop's own longer side onto the frame -- is the one that ends up
    governing (see its docstring for why the smaller of two factors wins):
    the result's height should reach the full frame while its width stays
    well short of it, in roughly the crop's own 40:200 ratio.
    """
    column = _column_with_object((120, 400), (50, 40, 89, 239))  # 40 wide, 200 tall

    frame = _frame_from_column(column)

    bbox = _opaque_bbox(frame)
    assert bbox is not None, "the drawn rectangle must survive as real opaque pixels"
    width, height = bbox
    assert width < height, f"a 40x200 source crop must not come out square-ish; got {bbox}"
    assert height >= SPRITE_SIZE - 2, f"the longer axis should reach close to the frame; got {bbox}"
    original_ratio = 40 / 200
    fitted_ratio = width / height
    assert abs(fitted_ratio - original_ratio) < 0.15, (
        f"the 40:200 aspect ratio should survive scaling; got {width}:{height}"
    )


def test_a_small_object_does_not_fill_the_frame():
    """The case the module docstring calls out by name: a `pellet`-like
    small dot, drawn small inside a large column, must not be blown up to
    fill 16x16 just because its own crop happens to be roughly square (the
    "contain" factor alone would do exactly that -- a 20x20 crop's longer
    side maps straight onto the frame, the same failure this module was
    fixed for). Here the drawn square is 20x20 inside a 200x200 column, ten
    times narrower than the column itself, so `_fit_to_frame`'s reference
    factor -- how much the column itself would shrink to fit the frame --
    must be the one that wins, keeping the object small in its frame too.
    """
    column = _column_with_object((200, 200), (90, 90, 109, 109))  # 20x20, in a 200x200 column

    frame = _frame_from_column(column)

    bbox = _opaque_bbox(frame)
    assert bbox is not None, "the drawn square must survive as real opaque pixels"
    width, height = bbox
    assert width <= 4 and height <= 4, (
        f"a source object ten times narrower than its column must stay small "
        f"in a {SPRITE_SIZE}x{SPRITE_SIZE} frame, not fill it; got {bbox}"
    )
    total = SPRITE_SIZE * SPRITE_SIZE
    count = int((np.asarray(frame)[..., 3] >= 128).sum())
    assert count < total // 4, f"a genuinely small object must leave most of the frame as background; got {count}/{total}"


def test_an_entirely_background_column_does_not_crash():
    """A column with no drawn pose at all -- `_clean_image` finds no
    non-background component and returns the column unchanged (see its own
    "No object found on background" branch) -- must still reduce to a real
    16x16 frame, not raise. `_fit_to_frame` receives a `cleaned` the same
    size as the original column in this case; nothing about that should be
    special-cased away, but it must not divide by zero or produce a
    mis-sized result either.
    """
    column = Image.new("RGBA", (100, 100), (255, 255, 255, 255))

    frame = _frame_from_column(column)

    assert frame.size == (SPRITE_SIZE, SPRITE_SIZE)
    count = int((np.asarray(frame)[..., 3] >= 128).sum())
    assert count == 0, "an all-background column must key out to an entirely transparent frame"


def test_the_real_fixture_still_yields_sane_non_degenerate_counts():
    """The real captured sheet (`_FIXTURE_SHEET`) run through the fitting
    fix must still come out as a real, judgeable silhouette in every frame
    -- not 0, not 256, and not so small a sliver that the packed sprite
    would be nearly invisible either. This is the same real fixture
    `test_a_real_black_on_white_sheet_packs_as_a_recognisable_silhouette_not_a_solid_block`
    already checks end to end through the packer; this test instead checks
    the frames `_frame_from_column` itself produces, and additionally that
    fitting actually left a visible background margin -- proof the fix is
    doing something, not just failing to break anything.
    """
    with Image.open(_FIXTURE_SHEET) as sheet:
        sheet = sheet.copy()
    columns = _sheet_columns(sheet, FRAMES_PER_SHEET)
    frames = [_frame_from_column(column) for column in columns]

    total = SPRITE_SIZE * SPRITE_SIZE
    for index, frame in enumerate(frames):
        count = int((np.asarray(frame)[..., 3] >= 128).sum())
        assert 20 <= count <= 200, (
            f"frame {index}: {count}/{total} opaque -- not a sane silhouette count"
        )
        bbox = _opaque_bbox(frame)
        assert bbox is not None
        width, height = bbox
        assert width < SPRITE_SIZE, (
            f"frame {index}: opaque region spans the full frame width ({width}) -- "
            "no background margin left, as if the old stretch-to-fill bug were still there"
        )
