"""Splitting a frame sheet, by arithmetic rather than by detection."""

import pytest
from PIL import Image

from llmz80.studio.sprite_sheet import split_frames


def _sheet(frames: int, size: int = 16) -> Image.Image:
    """One sheet whose frames are solid grey levels, so order is checkable."""
    sheet = Image.new("RGBA", (size * frames, size), (0, 0, 0, 0))
    for index in range(frames):
        block = Image.new("RGBA", (size, size), (index * 40, index * 40, index * 40, 255))
        sheet.paste(block, (index * size, 0))
    return sheet


def test_a_sheet_splits_left_to_right():
    frames = split_frames(_sheet(4), 4)

    assert len(frames) == 4
    assert [frame.size for frame in frames] == [(16, 16)] * 4
    assert [frame.getpixel((0, 0))[0] for frame in frames] == [0, 40, 80, 120]


def test_a_sheet_that_does_not_divide_is_refused():
    # `_sheet(frames, size)` always yields a width of `size * frames`, which is
    # divisible by `frames` by construction -- that can never exercise the
    # remainder check. Crop one column off so the width genuinely doesn't divide.
    lopsided = _sheet(4, size=15).crop((0, 0, 4 * 15 - 1, 15))

    with pytest.raises(ValueError, match="divide"):
        split_frames(lopsided, 4)


def test_one_frame_returns_the_image_itself():
    frames = split_frames(_sheet(1), 1)

    assert len(frames) == 1
    assert frames[0].size == (16, 16)
