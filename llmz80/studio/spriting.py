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
        """How many bytes of `data` one frame really occupies.

        On the Spectrum (`pack_spectrum`), `mask` is a separate, equal-sized
        array, so a frame is exactly `width_bytes * height` bytes of `data`.

        On the CPC (`pack_cpc`), `mask` is always empty -- the mask does not
        travel separately, it is interleaved one byte ahead of every colour
        byte inside `data` (see `pack_cpc`'s docstring). A frame therefore
        occupies twice `width_bytes * height` bytes of `data`. Reading that off
        `mask` being empty, rather than a target flag, keeps this in step with
        the same distinction `pack_cpc` and `pack_spectrum` already draw.

        This is what makes `len(data) == frames * bytes_per_frame` true for
        both packers -- the property answers "how far to the next frame",
        not just "how big is one row block".
        """
        stride = self.width_bytes * self.height
        return stride if self.mask else stride * 2


def _nearest_pen(rgb: tuple[int, int, int], palette: list[tuple[int, int, int]]) -> int:
    """The palette index closest to `rgb` in Euclidean RGB distance.

    This mirrors what `image_utils._process_image` gets from PIL's palette
    quantizer (nearest-colour matching against a fixed palette); we do it by hand
    here because the CPC path works pixel-by-pixel rather than through PIL's
    image-wide quantize().
    """
    best_index = 0
    best_distance = None
    for index, colour in enumerate(palette):
        distance = sum((a - b) ** 2 for a, b in zip(rgb, colour))
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_index = index
    return best_index


def _pixel_pattern_m0(pen: int) -> int:
    """One CPC mode-0 pen's bit pattern, exactly `CPCTM_PEN2PIXELPATTERN_M0` /
    the per-pixel half of `cpctm_px2byteM0` in
    ~/cpctelera/cpctelera/src/sprites/pixel_macros.h (line 335):

        f(P) = (P&1)<<6 | (P&2)<<1 | (P&4)<<2 | (P&8)>>3

    The pen's four bits do not end up as a tidy nibble; they are spread across
    bits 6, 4, 2 and 0 (or 7, 5, 3, 1 once shifted for the left pixel below).
    """
    return ((pen & 0x01) << 6) | ((pen & 0x02) << 1) | ((pen & 0x04) << 2) | ((pen & 0x08) >> 3)


def _pack_byte_m0(left: int, right: int) -> int:
    """cpctm_px2byteM0(X, Y): a mode-0 screen byte holding two pens.

    `pixel_macros.h` lines 335-336: `byte = (f(X) << 1) | f(Y)`. The left pixel's
    bits land on the odd bit positions (7, 5, 3, 1), the right pixel's on the
    even ones (6, 4, 2, 0) -- interleaved bit by bit, not packed as two nibbles.
    """
    return ((_pixel_pattern_m0(left) << 1) | _pixel_pattern_m0(right)) & 0xFF


def _pack_byte_m1(a: int, b: int, c: int, d: int) -> int:
    """cpctm_px2byteM1(A, B, C, D): a mode-1 screen byte holding four pens.

    `pixel_macros.h` lines 380-383: each pen contributes
    `g(P) = (P&1)<<4 | (P&2)>>1`, and `byte = g(A)<<3 | g(B)<<2 | g(C)<<1 | g(D)`.
    Bit 0 of every pen (A..D, left to right) ends up in the high nibble; bit 1
    of every pen ends up in the low nibble.
    """

    def g(pen: int) -> int:
        return ((pen & 0x01) << 4) | ((pen & 0x02) >> 1)

    return ((g(a) << 3) | (g(b) << 2) | (g(c) << 1) | g(d)) & 0xFF


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


def pack_cpc(
    frames: list[Image.Image], *, mode: int, palette: list[tuple[int, int, int]]
) -> PackedSprite:
    """Pack frames for CPCtelera's `cpct_drawSpriteMasked`.

    Two things here come from the CPCtelera source rather than from general
    reasoning about the CPC, and each is worth citing precisely because getting
    either wrong still produces something that compiles and passes a size check:

    Mask convention: `cpct_drawSpriteMasked.asm` (lines 154-158) computes
    `screen = (background AND mask) OR colour`. A set mask bit ANDs the
    background bit through unchanged and is then OR'd with a colour bit that
    must be 0 there, so a set bit *keeps* the background -- the same convention
    `pack_spectrum` uses. The doc comment above it (lines 41-43) confirms this in
    words: "enabled bits [are] those that should be picked from the background
    (transparent)", and that "each mask data byte must precede its associated
    colour data byte" -- mask first, then colour, is CPCtelera's ordering.

    Pixel encoding: mode 0 packs two pens per byte and mode 1 packs four, but
    neither packs them as tidy nibbles. `cpctm_px2byteM0` and `cpctm_px2byteM1`
    in ~/cpctelera/cpctelera/src/sprites/pixel_macros.h (lines 335-336 and
    380-383) interleave the pens' individual bits across the byte; see
    `_pack_byte_m0` and `_pack_byte_m1` above, which implement those macros bit
    for bit. The mask for a byte is built with the same interleaving, using the
    all-ones pen (15 in mode 0, 3 in mode 1) for a transparent pixel and pen 0
    for an opaque one -- that is what makes a transparent pixel's bits come out
    all-set (keep the background there) and an opaque pixel's bits come out
    all-clear (erase the background there so the colour byte's OR can show
    through).

    Unlike `pack_spectrum`, the returned `PackedSprite.mask` is always empty:
    on this target the mask does not travel separately, it is interleaved into
    `data` one mask byte ahead of each colour byte, because that is the layout
    `cpct_drawSpriteMasked` expects its single sprite pointer to hold. A caller
    that assumes mask and data are separate, as they are for the Spectrum, would
    silently drop the CPC mask if it looked at `.mask` here.
    """
    if mode not in (0, 1):
        raise ValueError(f"the CPC packer only supports modes 0 and 1; got mode {mode}")

    pixels_per_byte = 2 if mode == 0 else 4
    width_bytes = SPRITE_SIZE // pixels_per_byte
    bits_per_pen = 4 if mode == 0 else 2
    max_pens = 1 << bits_per_pen  # 16 in mode 0, 4 in mode 1: what fits in the pen's bit width
    if len(palette) > max_pens:
        raise ValueError(
            f"mode {mode} pens are {bits_per_pen} bits wide, so a palette can have at most "
            f"{max_pens} entries; got {len(palette)}. A longer palette would silently alias "
            "two colours onto the same pen, since only the low bits of the index are encoded."
        )
    transparent_pen = (1 << bits_per_pen) - 1  # all bits set -> "keep the background" per pixel
    pack_byte = _pack_byte_m0 if mode == 0 else _pack_byte_m1

    data = bytearray()
    for frame in _checked(frames):
        pixels = frame.load()
        for y in range(SPRITE_SIZE):
            for byte in range(width_bytes):
                colour_pens = []
                mask_pens = []
                for i in range(pixels_per_byte):
                    x = byte * pixels_per_byte + i
                    r, g, b, a = pixels[x, y]
                    if a >= ALPHA_THRESHOLD:
                        colour_pens.append(_nearest_pen((r, g, b), palette))
                        mask_pens.append(0)
                    else:
                        # Colour must be 0 here too: the mask's OR step only leaves
                        # the background untouched if the colour bits it is OR'd
                        # with are themselves 0.
                        colour_pens.append(0)
                        mask_pens.append(transparent_pen)
                data.append(pack_byte(*mask_pens))
                data.append(pack_byte(*colour_pens))
    return PackedSprite(bytes(data), b"", width_bytes, SPRITE_SIZE, len(frames))
