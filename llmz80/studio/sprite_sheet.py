"""Cut a sheet of animation frames into single images.

A sheet exists because a model asked for one pose at a time draws a different
character each time. Cutting it is arithmetic on purpose: anything that inferred
frame boundaries from the pixels would drift the moment a pose reached the edge
of its cell.
"""

from __future__ import annotations

from PIL import Image


def split_frames(sheet: Image.Image, frames: int) -> list[Image.Image]:
    """Split a sheet into `frames` equal images, left to right."""
    if frames < 1:
        raise ValueError("a sheet holds at least one frame")
    if sheet.width % frames:
        raise ValueError(
            f"a sheet {sheet.width} wide does not divide into {frames} whole frames"
        )
    width = sheet.width // frames
    return [
        sheet.crop((index * width, 0, (index + 1) * width, sheet.height))
        for index in range(frames)
    ]
