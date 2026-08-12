"""Packing an image into the bytes a Z80 can blit."""

import pytest
from PIL import Image

from llmz80.studio.spriting import PackedSprite, pack_spectrum


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

    assert packed.data[0] == 0xFF   # first row, left byte: eight opaque pixels
    assert packed.mask[0] == 0x00   # nothing of the background survives there
    assert packed.data[1] == 0x00   # right byte is transparent
    assert packed.mask[1] == 0xFF   # so the background is kept whole


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
    assert packed.data[2 * 16] == 0x00   # second frame starts fully transparent


def test_a_frame_that_is_not_sixteen_by_sixteen_is_refused():
    with pytest.raises(ValueError, match="16x16"):
        pack_spectrum([Image.new("RGBA", (8, 8), (0, 0, 0, 0))])
