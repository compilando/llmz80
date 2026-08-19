"""A drawn sprite sheet, as something you can look at in a terminal.

One truecolour ANSI cell per pixel, painted with the pixel's own colour.

**Why there is no palette lookup here.** The preview this replaces lived in
`cli.py` as `_sprite_preview_array` and went through `image_utils.display_sprite`,
which quantised every pixel against `config.get_palette_for_platform` -- a
table that is not the one the sprite is packed with. `cli.py`'s own docstring
recorded the mismatch and called the result "a preview to judge the art by,
not a byte-for-byte look at what gets packed", which was true and was also
avoidable: the sheet on disk was already drawn from `sprite_grid.palette_for`,
i.e. from `compiler.CPC_DEFAULT_PALETTE` on the CPC and the Spectrum ink on
the Spectrum. Its pixels *are* what the machine will show. Re-quantising them
against a second, different table could only move them away from that, so
this paints them as they are and the preview becomes exact.

Transparency is a mask rather than a colour, at the same `ALPHA_THRESHOLD`
the packers use, so no pixel is solid here and clear there.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from .spriting import ALPHA_THRESHOLD

if TYPE_CHECKING:  # pragma: no cover - import cost, not behaviour
    from PIL.Image import Image

#: End the line's colouring. Without it the last cell's background bleeds
#: across the rest of the terminal row and into whatever is printed next.
RESET = "\033[0m"


def sprite_lines(sheet: Image) -> list[str]:
    """`sheet` as one string per pixel row, ready to print.

    Returned rather than printed so the caller decides where they go and a
    test can read them without capturing stdout.
    """
    if sheet.mode != "RGBA":
        sheet = sheet.convert("RGBA")
    width, height = sheet.size
    pixels = sheet.load()
    lines = []
    for y in range(height):
        cells = []
        for x in range(width):
            red, green, blue, alpha = pixels[x, y]
            if alpha < ALPHA_THRESHOLD:
                # Reset first: an unpainted cell must show the terminal's own
                # background, not the colour the pixel to its left set.
                cells.append(f"{RESET} ")
            else:
                cells.append(f"\033[48;2;{red};{green};{blue}m ")
        lines.append("".join(cells) + RESET)
    return lines


def print_sprite(sheet: Image, say: Callable[[str], object] = print) -> None:
    """Draw `sheet` through `say`, one line at a time."""
    for line in sprite_lines(sheet):
        say(line)
