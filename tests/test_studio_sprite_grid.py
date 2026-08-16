"""Sprites as a grid of palette indices, rather than as a picture.

Nothing here calls a model. These are the pure halves of the new sprite
path: which pens a target really has, whether an answer is a usable sheet,
and what frames it becomes.
"""

import pytest

from llmz80.studio.models import TargetPlatform, VideoMode
from llmz80.studio.samples import blank_project
from llmz80.studio.sprite_grid import (
    TRANSPARENT,
    SpriteFrameGrid,
    SpriteSheetGrid,
    frames_from_grid,
    grid_errors,
    palette_for,
)
from llmz80.studio.spriting import ALPHA_THRESHOLD, SPRITE_SIZE, pack_cpc, pack_spectrum


def _project(platform: TargetPlatform, mode: VideoMode | None = None):
    return blank_project("Grid", platform, mode)


def _rows(fill: str = "0") -> list[str]:
    """A frame that is neither blank nor solid: a filled left half."""
    half = fill * (SPRITE_SIZE // 2) + TRANSPARENT * (SPRITE_SIZE // 2)
    return [half] * SPRITE_SIZE


def _sheet(fill: str = "0", frames: int = 4) -> SpriteSheetGrid:
    return SpriteSheetGrid(frames=[SpriteFrameGrid(rows=_rows(fill)) for _ in range(frames)])


# --- which pens a target actually has ---------------------------------------


def test_the_spectrum_gets_exactly_one_pen():
    """It is a monochrome machine: a pixel is drawn or it is not, and the
    colour comes from the attribute `pack_spectrum` derives afterwards. A
    second pen would be a colour the packer has nowhere to put."""
    palette = palette_for(_project(TargetPlatform.SPECTRUM))

    assert palette.alphabet == "0"
    assert len(palette.pens) == 1


@pytest.mark.parametrize("mode", [VideoMode.CPC_MODE_0, VideoMode.CPC_MODE_1])
def test_the_cpc_gets_four_pens_in_both_modes(mode):
    """Mode 0 addresses sixteen pens and mode 1 four -- but `compiler.py`
    packs *both* with `CPC_DEFAULT_PALETTE`, which has four entries. Offering
    the model sixteen would let it pick a pen the packer cannot resolve to a
    colour, so the alphabet follows the palette that is really used rather
    than the one the hardware could address.
    """
    palette = palette_for(_project(TargetPlatform.AMSTRAD_CPC, mode))

    assert palette.alphabet == "0123"
    assert len(palette.pens) == 4


def test_the_cpc_palette_is_the_one_the_compiler_packs_with():
    from llmz80.studio.compiler import CPC_DEFAULT_PALETTE

    palette = palette_for(_project(TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_0))

    assert list(palette.pens) == CPC_DEFAULT_PALETTE


# --- is this answer a usable sheet ------------------------------------------


def test_a_well_formed_sheet_has_nothing_wrong_with_it():
    palette = palette_for(_project(TargetPlatform.SPECTRUM))

    assert grid_errors(_sheet(), palette, frames_expected=4) is None


def test_the_wrong_number_of_frames_is_reported_rather_than_padded():
    palette = palette_for(_project(TargetPlatform.SPECTRUM))

    reason = grid_errors(_sheet(frames=3), palette, frames_expected=4)

    assert reason is not None
    assert "4" in reason and "3" in reason


def test_a_short_row_is_reported_with_where_it_is():
    """The reason becomes the feedback the next attempt is given, so it has
    to name the frame and the row rather than only the fact of a bad size."""
    palette = palette_for(_project(TargetPlatform.SPECTRUM))
    sheet = _sheet()
    sheet.frames[1].rows[5] = "0" * (SPRITE_SIZE - 1)

    reason = grid_errors(sheet, palette, frames_expected=4)

    assert reason is not None
    assert "frame 2" in reason
    assert "row 6" in reason


def test_the_wrong_number_of_rows_is_reported():
    palette = palette_for(_project(TargetPlatform.SPECTRUM))
    sheet = _sheet()
    sheet.frames[0].rows = sheet.frames[0].rows[:-1]

    reason = grid_errors(sheet, palette, frames_expected=4)

    assert reason is not None
    assert "frame 1" in reason


def test_a_pen_the_target_does_not_have_is_refused():
    """This is the whole point of drawing the sprite as indices: an illegal
    colour is not something to quantize afterwards, it is an answer the
    machine could not show, caught before anything is packed."""
    palette = palette_for(_project(TargetPlatform.SPECTRUM))
    sheet = _sheet()
    sheet.frames[0].rows[0] = "3" + sheet.frames[0].rows[0][1:]

    reason = grid_errors(sheet, palette, frames_expected=4)

    assert reason is not None
    assert "3" in reason
    assert "0" in reason  # names the alphabet that was allowed


def test_pen_three_is_fine_on_the_cpc():
    palette = palette_for(_project(TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_0))

    assert grid_errors(_sheet("3"), palette, frames_expected=4) is None


def test_an_entirely_transparent_frame_is_refused():
    """`_judge_frames` catches this downstream on pixels; catching it here
    lets the reason say which frame was empty, in the model's own terms."""
    palette = palette_for(_project(TargetPlatform.SPECTRUM))
    sheet = _sheet()
    sheet.frames[2].rows = [TRANSPARENT * SPRITE_SIZE] * SPRITE_SIZE

    reason = grid_errors(sheet, palette, frames_expected=4)

    assert reason is not None
    assert "frame 3" in reason


def test_a_completely_filled_frame_is_refused():
    palette = palette_for(_project(TargetPlatform.SPECTRUM))
    sheet = _sheet()
    sheet.frames[0].rows = ["0" * SPRITE_SIZE] * SPRITE_SIZE

    reason = grid_errors(sheet, palette, frames_expected=4)

    assert reason is not None
    assert "frame 1" in reason


# --- what the grid becomes --------------------------------------------------


def test_the_frames_come_out_at_the_size_the_packers_demand():
    palette = palette_for(_project(TargetPlatform.SPECTRUM))

    frames = frames_from_grid(_sheet(), palette)

    assert len(frames) == 4
    assert all(frame.size == (SPRITE_SIZE, SPRITE_SIZE) for frame in frames)
    assert all(frame.mode == "RGBA" for frame in frames)


def test_a_dot_is_transparent_and_a_digit_is_that_pen_opaque():
    palette = palette_for(_project(TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_0))
    sheet = _sheet()
    sheet.frames[0].rows[0] = "2" + TRANSPARENT + sheet.frames[0].rows[0][2:]

    frame = frames_from_grid(sheet, palette)[0]

    r, g, b, a = frame.getpixel((0, 0))
    assert a >= ALPHA_THRESHOLD
    assert (r, g, b) == palette.pens[2]
    assert frame.getpixel((1, 0))[3] < ALPHA_THRESHOLD


def test_no_pixel_is_ever_half_transparent():
    """The anti-aliased halo that the previous, image-model path spent
    `_detect_background`, `HALO_TOLERANCE` and `_key_out_background` fighting
    cannot be expressed here at all: there is no character for it."""
    palette = palette_for(_project(TargetPlatform.SPECTRUM))

    for frame in frames_from_grid(_sheet(), palette):
        for y in range(SPRITE_SIZE):
            for x in range(SPRITE_SIZE):
                assert frame.getpixel((x, y))[3] in (0, 255)


def test_the_spectrum_packer_accepts_what_comes_out():
    palette = palette_for(_project(TargetPlatform.SPECTRUM))

    packed = pack_spectrum(frames_from_grid(_sheet(), palette))

    assert packed.frames == 4
    assert packed.height == SPRITE_SIZE


@pytest.mark.parametrize("mode,cpc_mode", [(VideoMode.CPC_MODE_0, 0), (VideoMode.CPC_MODE_1, 1)])
def test_the_cpc_packer_accepts_what_comes_out(mode, cpc_mode):
    from llmz80.studio.compiler import CPC_DEFAULT_PALETTE

    palette = palette_for(_project(TargetPlatform.AMSTRAD_CPC, mode))

    packed = pack_cpc(
        frames_from_grid(_sheet("1"), palette), mode=cpc_mode, palette=CPC_DEFAULT_PALETTE
    )

    assert packed.frames == 4
    assert packed.height == SPRITE_SIZE


# --- what a person sees of a failed attempt ---------------------------------


def test_the_preview_is_the_whole_sheet_magnified():
    from llmz80.studio.sprite_grid import PREVIEW_SCALE, render_grid

    palette = palette_for(_project(TargetPlatform.SPECTRUM))

    image = render_grid(_sheet(), palette)

    assert image.size == (4 * SPRITE_SIZE * PREVIEW_SCALE, SPRITE_SIZE * PREVIEW_SCALE)


def test_the_preview_renders_a_sheet_that_frames_from_grid_would_refuse():
    """The failed attempts are the ones worth looking at, so a renderer that
    raised on a malformed grid would leave nothing on disk for exactly the
    run that needs it. Bad rows, missing rows and illegal pens all render as
    far as they can and leave the rest transparent."""
    from llmz80.studio.sprite_grid import render_grid

    palette = palette_for(_project(TargetPlatform.SPECTRUM))
    sheet = _sheet()
    sheet.frames[0].rows[0] = "0Z" + TRANSPARENT * 3      # illegal character
    sheet.frames[1].rows[1] = "0"                          # far too short
    sheet.frames[2].rows = sheet.frames[2].rows[:4]        # far too few rows
    sheet.frames[3].rows[0] = "9" * SPRITE_SIZE            # pen this target lacks

    image = render_grid(sheet, palette)

    assert image.size[0] > 0
    assert grid_errors(sheet, palette, frames_expected=4) is not None
