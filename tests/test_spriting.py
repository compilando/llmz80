"""Packing an image into the bytes a Z80 can blit."""

import pytest
from PIL import Image

from llmz80.studio.spriting import PackedSprite, pack_cpc, pack_spectrum


def _square(size: int = 16) -> Image.Image:
    """An opaque 8x8 block in the top-left quarter of a transparent 16x16 frame."""
    frame = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    for y in range(8):
        for x in range(8):
            frame.putpixel((x, y), (255, 255, 255, 255))
    return frame


def test_a_spectrum_frame_packs_two_bytes_per_row():
    packed = pack_spectrum([_square()])

    assert isinstance(packed, PackedSprite)
    assert packed.width_bytes == 2
    assert packed.height == 16
    assert len(packed.data) == 2 * 16
    assert len(packed.mask) == 2 * 16


def test_opaque_pixels_become_set_bits_and_a_clear_mask():
    packed = pack_spectrum([_square()])

    assert packed.data[0] == 0xFF  # first row, left byte: eight opaque pixels
    assert packed.mask[0] == 0x00  # nothing of the background survives there
    assert packed.data[1] == 0x00  # right byte is transparent
    assert packed.mask[1] == 0xFF  # so the background is kept whole


def test_transparent_rows_keep_the_background_everywhere():
    packed = pack_spectrum([_square()])
    row_nine = 9 * 2

    assert packed.data[row_nine] == 0x00
    assert packed.mask[row_nine] == 0xFF


def test_frames_are_concatenated_in_order():
    packed = pack_spectrum([_square(), Image.new("RGBA", (16, 16), (0, 0, 0, 0))])

    assert packed.frames == 2
    assert len(packed.data) == 2 * 16 * 2
    assert packed.data[0] == 0xFF
    assert packed.data[2 * 16] == 0x00  # second frame starts fully transparent


def test_a_frame_that_is_not_sixteen_by_sixteen_is_refused():
    with pytest.raises(ValueError, match="16x16"):
        pack_spectrum([Image.new("RGBA", (8, 8), (0, 0, 0, 0))])


def test_bytes_per_frame_tells_the_truth_about_the_spectrum_layout():
    packed = pack_spectrum([_square(), _square()])

    assert len(packed.data) == packed.frames * packed.bytes_per_frame


# --- Mirror-proof fixtures --------------------------------------------------
#
# The fixtures above (an 8x8 opaque block in the top-left of a 16x16 frame)
# are symmetric enough that flipping bit order within a byte, or reversing row
# order, still satisfies every assertion above. These fixtures single out one
# pixel at a time so that kind of mirroring is caught. The expected bytes are
# derived independently from the machine convention `0x80 >> bit` (leftmost
# pixel is the high bit) and row-major, top-to-bottom order -- not read off
# the implementation.


def _dot(x: int, y: int) -> Image.Image:
    """A transparent 16x16 frame with exactly one opaque pixel at `(x, y)`."""
    frame = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    frame.putpixel((x, y), (255, 255, 255, 255))
    return frame


def test_spectrum_pixel_at_origin_sets_the_high_bit_of_the_left_byte():
    packed = pack_spectrum([_dot(0, 0)])

    assert packed.data[0] == 0x80
    assert packed.data[1] == 0x00


def test_spectrum_pixel_at_x_seven_sets_the_low_bit_of_the_left_byte():
    """x=7 is the rightmost pixel still inside the left byte -- pins bit order
    within a byte in a way (0, 0) alone cannot: reversing `0x80 >> bit` to
    `0x01 << bit` would put this pixel's bit in the same place as x=0's."""
    packed = pack_spectrum([_dot(7, 0)])

    assert packed.data[0] == 0x01
    assert packed.data[1] == 0x00


def test_spectrum_pixel_at_x_eight_sets_the_high_bit_of_the_right_byte():
    """x=8 is the leftmost pixel of the right byte -- pins byte order within a
    row: swapping the left/right bytes would move this pixel into byte 0."""
    packed = pack_spectrum([_dot(8, 0)])

    assert packed.data[0] == 0x00
    assert packed.data[1] == 0x80


def test_spectrum_pixel_on_row_one_lands_two_bytes_in_and_no_other_row_lights_up():
    """Pins row order: a fixture where only row 1 is lit distinguishes
    top-to-bottom from any other row ordering, which a uniformly-opaque
    top-half fixture cannot."""
    packed = pack_spectrum([_dot(0, 1)])

    assert packed.data[0] == 0x00  # row 0, left byte: untouched
    assert packed.data[2] == 0x80  # row 1, left byte: the one lit pixel
    assert packed.data[4] == 0x00  # row 2, left byte: untouched


# --- Amstrad CPC -----------------------------------------------------------
#
# The values below are derived by hand from the two macros CPCtelera actually
# ships, `cpctm_px2byteM0` and `cpctm_px2byteM1` in
# ~/cpctelera/cpctelera/src/sprites/pixel_macros.h (lines 335-336 and
# 380-383), not from any general theory of how the CPC packs pixels. See
# `llmz80/studio/spriting.py` for the same derivation spelled out per bit.


def _pixels(*dots: tuple[int, int, tuple[int, int, int]]) -> Image.Image:
    """A transparent 16x16 frame with each `(x, y, rgb)` painted in fully opaque."""
    frame = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for x, y, rgb in dots:
        frame.putpixel((x, y), (*rgb, 255))
    return frame


def test_a_mode_zero_frame_is_eight_bytes_wide_with_the_mask_interleaved():
    packed = pack_cpc([_square()], mode=0, palette=[(255, 255, 255)])

    assert packed.width_bytes == 8
    # Interleaved: one mask byte and one colour byte per screen byte.
    assert len(packed.data) == 2 * 8 * 16


def test_a_mode_one_frame_is_four_bytes_wide():
    packed = pack_cpc([_square()], mode=1, palette=[(255, 255, 255)])

    assert packed.width_bytes == 4
    assert len(packed.data) == 2 * 4 * 16


def test_an_unsupported_mode_is_refused():
    with pytest.raises(ValueError, match="mode"):
        pack_cpc([_square()], mode=2, palette=[(255, 255, 255)])


def test_cpc_mask_travels_inside_data_and_the_separate_mask_field_is_empty():
    packed = pack_cpc([_square()], mode=0, palette=[(255, 255, 255)])

    assert packed.mask == b""


def test_mode_zero_a_single_opaque_pixel_lands_in_the_left_pixel_bit_positions():
    """Pen 1 at x=0 (left pixel of the byte), everything else in the byte transparent.

    cpctm_px2byteM0(X, Y) with X=left pixel's pen, Y=right pixel's pen:
        f(P) = (P&1)<<6 | (P&2)<<1 | (P&4)<<2 | (P&8)>>3
        byte = (f(X) << 1) | f(Y)
    Colour: X=pen 1 -> f(1) = 1<<6 = 0x40; Y=pen 0 (transparent) -> f(0) = 0.
        colour = (0x40 << 1) | 0 = 0x80.
    Mask: opaque pixel -> mask pen 0 (erase); transparent pixel -> mask pen 15,
    i.e. all four bits of the pen set, which is how "keep the background" is
    spelled per-pixel in this bit-interleaved format.
        f(0) = 0; f(15) = (1<<6)|(1<<1)|(1<<2)|(1) = 0x55.
        mask = (f(0) << 1) | f(15) = 0x55.
    """
    palette = [(0, 0, 0), (255, 255, 255)]
    packed = pack_cpc([_pixels((0, 0, (255, 255, 255)))], mode=0, palette=palette)

    assert packed.data[0] == 0x55  # mask byte for row 0, screen byte 0
    assert packed.data[1] == 0x80  # colour byte for row 0, screen byte 0


def test_mode_zero_two_adjacent_pens_interleave_their_bits_not_their_nibbles():
    """Left pixel pen 2, right pixel pen 3, both opaque.

    f(2) = (2&2)<<1 = 0x04. f(3) = (3&1)<<6 | (3&2)<<1 = 0x40 | 0x04 = 0x44.
    colour = (f(2) << 1) | f(3) = 0x08 | 0x44 = 0x4C.

    This is not the tidy "0x23" a naive two-nibbles-per-byte scheme would give;
    the CPC interleaves the pens' bits across the byte, which is the whole
    reason this encoding cannot be derived from first principles.
    """
    palette = [(0, 0, 0), (255, 255, 255), (0, 0, 255), (255, 0, 0)]
    packed = pack_cpc([_pixels((0, 0, (0, 0, 255)), (1, 0, (255, 0, 0)))], mode=0, palette=palette)

    assert packed.data[0] == 0x00  # both pixels opaque: nothing of the background kept
    assert packed.data[1] == 0x4C


def test_mode_zero_a_fully_transparent_frame_keeps_the_whole_background():
    packed = pack_cpc([Image.new("RGBA", (16, 16), (0, 0, 0, 0))], mode=0, palette=[(0, 0, 0)])

    assert packed.data[0] == 0xFF  # mask: every bit says "keep the background here"
    assert packed.data[1] == 0x00  # colour: irrelevant under an all-keeping mask, but tidy


def test_mode_one_four_adjacent_pens_pack_bit_zero_then_bit_one_of_each():
    """Pens 0, 1, 2, 3 at x=0..3, all opaque.

    cpctm_px2byteM1(A, B, C, D) with g(P) = (P&1)<<4 | (P&2)>>1:
        byte = (g(A)<<3) | (g(B)<<2) | (g(C)<<1) | g(D)
    g(0)=0x00, g(1)=0x10, g(2)=0x01, g(3)=0x11.
    byte = (0x00<<3) | (0x10<<2) | (0x01<<1) | 0x11 = 0x00 | 0x40 | 0x02 | 0x11 = 0x53.
    """
    palette = [(0, 0, 0), (85, 85, 85), (170, 170, 170), (255, 255, 255)]
    packed = pack_cpc(
        [_pixels((0, 0, palette[0]), (1, 0, palette[1]), (2, 0, palette[2]), (3, 0, palette[3]))],
        mode=1,
        palette=palette,
    )

    assert packed.data[0] == 0x00  # all four pixels opaque
    assert packed.data[1] == 0x53


def test_mode_one_a_fully_transparent_frame_keeps_the_whole_background():
    packed = pack_cpc([Image.new("RGBA", (16, 16), (0, 0, 0, 0))], mode=1, palette=[(0, 0, 0)])

    assert packed.data[0] == 0xFF
    assert packed.data[1] == 0x00


def test_bytes_per_frame_tells_the_truth_about_the_cpc_interleaved_layout():
    """Two mode-0 frames give len(data) == 512 while width_bytes * height == 128:
    the interleaved mask doubles the real stride, and bytes_per_frame must say
    so, not just report the width/height figure."""
    packed = pack_cpc([_square(), _square()], mode=0, palette=[(255, 255, 255)])

    assert len(packed.data) == 512
    assert packed.bytes_per_frame == 256
    assert len(packed.data) == packed.frames * packed.bytes_per_frame


def test_mode_zero_palette_over_sixteen_entries_is_refused():
    palette = [(i, i, i) for i in range(17)]
    with pytest.raises(ValueError, match="mode 0.*16.*17"):
        pack_cpc([_square()], mode=0, palette=palette)


def test_mode_one_palette_over_four_entries_is_refused():
    palette = [(i, i, i) for i in range(5)]
    with pytest.raises(ValueError, match="mode 1.*4.*5"):
        pack_cpc([_square()], mode=1, palette=palette)


# --- Spectrum attribute (ink) -----------------------------------------------
#
# One ink for the whole sprite is what the Spectrum affords: attributes are
# per character cell, not per pixel. `_spectrum_ink` derives the 3-bit ink
# index and the BRIGHT bit from the dominant opaque colour's RGB using the
# real z88dk <arch/zx.h> bit layout (see spriting.py); these values are
# checked by hand against that layout, not read off the implementation.
#
# INK_RED=0x02, INK_CYAN=0x05, INK_YELLOW=0x06, INK_WHITE=0x07, BRIGHT=0x40,
# PAPER_BLACK=0x00 (llmz80/studio/spriting.py cites the exact header and
# lines). The RGB fixtures below are the Spectrum's own canonical bright and
# dim colour values (bright: 0/255 per channel; dim: 0/0xCD per channel).


def _solid(rgb: tuple[int, int, int]) -> Image.Image:
    """A fully opaque 16x16 frame, one solid RGB colour."""
    return Image.new("RGBA", (16, 16), (*rgb, 255))


def test_a_mostly_red_frame_gets_bright_red_ink_on_black_paper():
    packed = pack_spectrum([_solid((255, 0, 0))])

    # 0x00 (PAPER_BLACK) | 0x02 (INK_RED) | 0x40 (BRIGHT) = 0x42.
    assert packed.attribute == 0x42


def test_a_mostly_white_frame_gets_bright_white_ink():
    packed = pack_spectrum([_solid((255, 255, 255))])

    # INK_WHITE=0x07 | BRIGHT=0x40 = 0x47.
    assert packed.attribute == 0x47


def test_a_mostly_cyan_frame_gets_bright_cyan_ink():
    packed = pack_spectrum([_solid((0, 255, 255))])

    # INK_CYAN=0x05 | BRIGHT=0x40 = 0x45.
    assert packed.attribute == 0x45


def test_a_mostly_yellow_frame_gets_bright_yellow_ink():
    packed = pack_spectrum([_solid((255, 255, 0))])

    # INK_YELLOW=0x06 | BRIGHT=0x40 = 0x46.
    assert packed.attribute == 0x46


def test_the_dominant_colour_across_frames_wins_not_the_first_frame():
    """A sprite whose first frame is a small red dot but whose second frame
    (and most pixels overall) is solid cyan should read as cyan -- "most
    common opaque colour", not "first frame's colour"."""
    packed = pack_spectrum([_dot(0, 0), _solid((0, 255, 255))])

    assert packed.attribute == 0x45  # INK_CYAN | BRIGHT


def test_bright_and_dim_red_do_not_collapse_to_the_same_attribute():
    """(255, 0, 0) is the Spectrum's own bright red; (205, 0, 0) -- 0xCD, the
    conventional dim intensity -- is its non-bright counterpart. Both are
    "red" to a human, but the hardware distinguishes them with one bit, and
    this packer must not throw that bit away."""
    bright = pack_spectrum([_solid((255, 0, 0))])
    dim = pack_spectrum([_solid((205, 0, 0))])

    assert bright.attribute == 0x42  # INK_RED | BRIGHT
    assert dim.attribute == 0x02  # INK_RED, not bright
    assert bright.attribute != dim.attribute


def test_a_fully_transparent_frame_does_not_crash_and_gets_plain_black():
    packed = pack_spectrum([Image.new("RGBA", (16, 16), (0, 0, 0, 0))])

    # No opaque pixels to take an ink from: PAPER_BLACK | INK_BLACK, i.e. 0.
    # Harmless, since a fully transparent sprite draws nothing to be seen.
    assert packed.attribute == 0x00


def test_a_solid_black_frame_does_not_pack_to_an_invisible_ink():
    """A frame whose only opaque colour is black is not the same case as the
    fully transparent frame above: it drew real pixels, just dark ones.
    `resources/sprite_prompt_spectrum.txt` asks for exactly this -- "strictly
    monochrome, black figure on white" -- so once the white background is
    keyed to transparency (see `sprite_artist._key_out_background`), the
    dominant opaque colour left in the frame is black. PAPER_BLACK |
    INK_BLACK would be a correctly shaped sprite nobody can see, because ink
    and paper are the same colour; `_MONOCHROME_FALLBACK_INK` must stop that
    from ever being the result. Checked by decomposing the attribute byte
    into paper, ink and bright rather than only asserting it is nonzero,
    since a nonzero byte (e.g. FLASH alone) need not actually be visible.
    """
    packed = pack_spectrum([_solid((0, 0, 0))])

    ink = packed.attribute & 0x07
    paper = (packed.attribute >> 3) & 0x07
    bright = bool(packed.attribute & 0x40)

    assert paper == 0x00  # PAPER_BLACK, as every current typology draws on
    assert ink != paper, f"ink ({ink}) must differ from paper ({paper}) to be visible at all"
    assert ink == 0x07  # INK_WHITE: maximum contrast against black paper
    assert bright is True


def test_cpc_packing_leaves_the_attribute_at_its_unused_default():
    """The CPC has no attribute byte -- colour lives in the pixel data via
    `palette` -- so `pack_cpc` must not invent one."""
    packed = pack_cpc([_solid((255, 0, 0))], mode=0, palette=[(255, 0, 0)])

    assert packed.attribute == 0


def test_cpc_nearest_pen_uses_euclidean_distance_in_rgb():
    """A pixel closer to palette[1] than palette[0], but not an exact match,
    must still resolve to pen 1 -- the packer does its own nearest-colour
    matching rather than requiring exact palette hits."""
    palette = [(0, 0, 0), (255, 255, 255)]
    packed = pack_cpc([_pixels((0, 0, (200, 200, 200)))], mode=0, palette=palette)

    # Same derivation as the single-opaque-pixel test above, with pen 1 for the
    # opaque pixel: colour = 0x80, mask = 0x55.
    assert packed.data[0] == 0x55
    assert packed.data[1] == 0x80
