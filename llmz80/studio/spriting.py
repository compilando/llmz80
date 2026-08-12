"""Turn frames into the bytes each machine's blitter expects.

This module knows about pixels and about two machines, and about nothing else:
not where the image came from, not which entity wears it, not how the C that
draws it is written. That is what lets the same packer serve an imported PNG, a
model-generated sheet and a fixture in a test.

Mask convention, fixed here and honoured by every blitter: a set bit in the mask
keeps the background. A blit is `screen = (screen & mask) | data`.
"""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image

#: Every sprite is one 16x16 block, two character cells square. Fixing the size
#: keeps the blitter branchless and the budget arithmetic honest; a design that
#: needs something else needs a second sprite kind, not a variable-size one.
SPRITE_SIZE = 16

#: A pixel counts as drawn when it is this opaque. Generated art carries soft
#: edges no matter how firmly the prompt forbids them, and a threshold is a
#: decision made once here rather than differently in each caller.
ALPHA_THRESHOLD = 128


@dataclass(frozen=True)
class PackedSprite:
    """One sprite's frames, ready to be written into a header."""

    data: bytes
    mask: bytes
    width_bytes: int
    height: int
    frames: int

    @property
    def bytes_per_frame(self) -> int:
        return self.width_bytes * self.height


def _checked(frames: list[Image.Image]) -> list[Image.Image]:
    if not frames:
        raise ValueError("a sprite needs at least one frame")
    bad = [frame.size for frame in frames if frame.size != (SPRITE_SIZE, SPRITE_SIZE)]
    if bad:
        raise ValueError(f"every frame must be 16x16; found {bad}")
    return [frame.convert("RGBA") for frame in frames]


def pack_spectrum(frames: list[Image.Image]) -> PackedSprite:
    """Pack frames as one bit per pixel, two bytes to a row."""
    data = bytearray()
    mask = bytearray()
    for frame in _checked(frames):
        pixels = frame.load()
        for y in range(SPRITE_SIZE):
            for byte in range(2):
                bits = 0
                holes = 0
                for bit in range(8):
                    x = byte * 8 + bit
                    drawn = pixels[x, y][3] >= ALPHA_THRESHOLD
                    if drawn:
                        bits |= 0x80 >> bit
                    else:
                        holes |= 0x80 >> bit
                data.append(bits)
                mask.append(holes)
    return PackedSprite(bytes(data), bytes(mask), 2, SPRITE_SIZE, len(frames))
