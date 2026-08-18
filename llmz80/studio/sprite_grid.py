"""A sprite as a grid of palette indices, rather than as a picture of one.

The pipeline this replaces asked an image model for a 1024x1024 canvas and
then spent most of `sprite_artist.py` trying to recover a 16x16 sprite from
it: reading each frame's real background off its own border because the
model would not honour the one it was asked for, discounting an
anti-aliased halo with a tolerance derived from a per-column histogram,
cropping to the drawn pose, and rescaling by a factor that kept proportions.
Every one of those exists to repair damage the *output format* caused, not
the drawing.

A sprite for these machines is not a picture. On the Spectrum it is 256 bits;
on the CPC it is 256 pens out of a palette of four. That fits in a grid of
characters, which a model can write directly and `output_format` can shape.
Two whole classes of failure stop being possible rather than being detected:
there is no character for "40% grey", so there is no anti-aliasing, and there
is no character outside the target's own alphabet, so there is no colour the
machine cannot show.

What is deliberately *not* enforced by the pydantic schema is the shape:
`SpriteFrameGrid.rows` is a plain list of plain strings. A schema that
demanded exactly sixteen sixteen-character rows would turn a model's
near-miss into a `ValidationError` raised inside the SDK's own parse step,
which no retry loop can turn into feedback. `grid_errors` checks the same
things afterwards and returns a sentence naming the frame and row at fault,
so a near-miss becomes the next attempt's instructions -- the way
`sprite_artist._judge_frames` already works, and for the same reason.
"""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image
from pydantic import BaseModel

from .models import GameProject, TargetPlatform
from .spriting import SPRITE_SIZE

#: The one character that is not a pen. Chosen over a space because trailing
#: spaces do not survive being read back out of YAML, a diff or a terminal,
#: and a sprite's transparent right-hand column is exactly what would be lost.
TRANSPARENT = "."

#: What the Spectrum's single pen is drawn as. `spriting.pack_spectrum` reads
#: the colour off the frames only to derive the attribute byte -- the bitmap
#: itself records set or not set -- so any one opaque colour would do, and
#: black is the one an author looking at a raw frame would expect.
SPECTRUM_INK = (0, 0, 0)


@dataclass(frozen=True)
class GridPalette:
    """The pens a target really has, and the characters that name them.

    "Really" is doing work here: this carries the palette the art is actually
    packed against, not the one the hardware could be set up for. The two used
    to differ -- the CPC in mode 0 can address sixteen pens and `compiler.py`
    packed every CPC sprite with four whatever the mode, so a sheet naming pen
    9 named a colour nothing downstream could resolve. They agree now, and
    `palette.cpc_palette` is the one place that decides.
    """

    pens: tuple[tuple[int, int, int], ...]

    #: Pen characters past 9, so mode 0's sixteen pens each get one. Hex
    #: digits rather than letters chosen freely: a reader already reads "a" as
    #: ten after "9", and a grid is easier to check by eye when every pen is
    #: one column wide -- which is also what `grid_errors` measures a row
    #: against. Upper case is deliberately not accepted; one spelling per pen
    #: keeps a model from mixing them inside a frame.
    EXTRA_PENS = "abcdef"

    @property
    def alphabet(self) -> str:
        """The legal pen characters, in index order: "0", "0123", "0123456789abcdef"."""
        digits = "0123456789" + self.EXTRA_PENS
        return digits[: len(self.pens)]


def palette_for(project: GameProject) -> GridPalette:
    """The pens `project`'s target can show, as the packers will read them."""
    if project.target.platform is TargetPlatform.SPECTRUM:
        return GridPalette(pens=(SPECTRUM_INK,))

    from .palette import cpc_mode, cpc_rgb

    return GridPalette(pens=tuple(cpc_rgb(cpc_mode(project))))


class SpriteFrameGrid(BaseModel):
    """One pose: `SPRITE_SIZE` rows of `SPRITE_SIZE` characters.

    Unconstrained on purpose -- see the module docstring. `grid_errors` is
    what holds the shape.
    """

    rows: list[str]


class SpriteSheetGrid(BaseModel):
    """A whole cycle of poses, one `SpriteFrameGrid` per frame."""

    frames: list[SpriteFrameGrid]


def grid_errors(
    sheet: SpriteSheetGrid,
    palette: GridPalette,
    *,
    frames_expected: int,
    size: int = SPRITE_SIZE,
    solid_allowed: bool = False,
) -> str | None:
    """What is wrong with `sheet`, in words the next attempt can act on.

    `None` means nothing is. Everything else is a sentence naming the frame
    (and where it helps, the row) at fault, because this string is handed
    straight back to the model as the reason its previous sheet was rejected.
    Frames and rows are counted from 1 in that sentence: it is read by
    whoever wrote the grid, not by the code that indexes it.

    The checks are ordered cheapest and most structural first, and only the
    first failure is reported -- a sheet with the wrong number of frames has
    nothing useful to say about row lengths inside them.

    `size` is the square each frame must be, defaulting to a sprite's 16.
    Terrain artwork asks for 8 (`spriting.TILE_SIZE`): a tile fills one
    character cell, and the same grid vocabulary describes it.

    `solid_allowed` lifts the no-solid-frames rule, and only terrain lifts it.
    A solid *sprite* is a 16x16 brick where a figure should be, which is why
    that rule exists; a solid *tile* is what a wall looks like. Blank is
    refused either way -- artwork that draws nothing is not artwork.
    """
    if len(sheet.frames) != frames_expected:
        return (
            f"the sheet must hold exactly {frames_expected} "
            f"frame{'s' if frames_expected != 1 else ''}, "
            f"and this one holds {len(sheet.frames)}"
        )

    allowed = set(palette.alphabet) | {TRANSPARENT}
    for number, frame in enumerate(sheet.frames, start=1):
        if len(frame.rows) != size:
            return f"frame {number} must have exactly {size} rows, " f"and it has {len(frame.rows)}"
        for row_number, row in enumerate(frame.rows, start=1):
            if len(row) != size:
                return (
                    f"frame {number}, row {row_number} must be exactly "
                    f"{size} characters long, and it is {len(row)}"
                )
            for character in row:
                if character not in allowed:
                    return (
                        f"frame {number}, row {row_number} uses '{character}', which is "
                        f"not a pen this machine has. Use '{TRANSPARENT}' for transparent "
                        f"and one of '{palette.alphabet}' for a colour."
                    )

    # Blank and solid are the two answers that pack into something that is
    # demonstrably not a sprite -- an invisible one and a 16x16 block. They
    # are caught again downstream on the pixels themselves
    # (`sprite_artist._judge_frames`), but catching them here lets the reason
    # be phrased in the grid's own terms rather than in opaque-pixel counts.
    for number, frame in enumerate(sheet.frames, start=1):
        drawn = sum(character != TRANSPARENT for row in frame.rows for character in row)
        if drawn == 0:
            return f"frame {number} is entirely transparent, so it draws nothing"
        if drawn == size * size and not solid_allowed:
            return (
                f"frame {number} has no transparent pixel at all, so it is a solid "
                f"{size}x{size} block rather than a shape"
            )
    return None


#: How much to magnify a grid when rendering it for a human to look at. A
#: 16px frame is unreadable at native size on any modern screen, and a whole
#: sheet at this factor is 512x128 -- large enough to see a pose in, small
#: enough to keep beside every attempt of every failed run.
PREVIEW_SCALE = 8


def render_grid(
    sheet: SpriteSheetGrid,
    palette: GridPalette,
    *,
    scale: int = PREVIEW_SCALE,
    size: int = SPRITE_SIZE,
) -> Image.Image:
    """The sheet as one magnified picture, for somebody to look at.

    Deliberately tolerant where `frames_from_grid` is strict, because this is
    what gets saved for the attempts that *failed*: a sheet with a short row,
    a missing row or a pen the machine does not have is exactly the sheet
    worth seeing, and a renderer that raised on those would leave nothing on
    disk for the only run that needs evidence. Anything it cannot read is
    left transparent rather than guessed at.

    Magnified by whole-pixel nearest neighbour, so what is on screen is the
    grid and not a smoothed version of it.
    """
    frames = max(len(sheet.frames), 1)
    image = Image.new("RGBA", (frames * size * scale, size * scale), (0, 0, 0, 0))
    pixels = image.load()
    for index, frame in enumerate(sheet.frames):
        origin = index * size
        for y, row in enumerate(frame.rows[:size]):
            for x, character in enumerate(row[:size]):
                if character == TRANSPARENT or not character.isdigit():
                    continue
                pen = int(character)
                if pen >= len(palette.pens):
                    continue
                red, green, blue = palette.pens[pen]
                for dy in range(scale):
                    for dx in range(scale):
                        pixels[(origin + x) * scale + dx, y * scale + dy] = (
                            red,
                            green,
                            blue,
                            255,
                        )
    return image


def frames_from_grid(
    sheet: SpriteSheetGrid, palette: GridPalette, *, size: int = SPRITE_SIZE
) -> list[Image.Image]:
    """`sheet` as the RGBA frames `spriting.py`'s packers take.

    Every pixel comes out fully opaque or fully transparent. That is not a
    threshold applied here, it is the only thing the input can express --
    which is why nothing downstream of this needs to key a background out.

    Assumes `grid_errors` has already passed; an out-of-range character
    raises rather than being silently drawn as something else.
    """
    frames: list[Image.Image] = []
    for frame in sheet.frames:
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        pixels = image.load()
        for y, row in enumerate(frame.rows):
            for x, character in enumerate(row):
                if character == TRANSPARENT:
                    continue
                red, green, blue = palette.pens[int(character)]
                pixels[x, y] = (red, green, blue, 255)
        frames.append(image)
    return frames
