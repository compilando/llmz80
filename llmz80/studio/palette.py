"""The colour a design names, read back as something a machine can show.

A design's colour vocabulary is two layers deep on purpose. `TileSpec.colour`
and `EntitySpec.colour` hold a palette entry *id* -- the design's own word,
`ladrillo` or `brick_red` -- and `PaletteEntry.colour` holds the prose that
says what that word looks like, "bright cyan" or "azul brillante". Both
layers existed before this module and neither was ever read: every terrain
cell was drawn in `PAPER_BLACK | INK_WHITE` (see the Spectrum `plat_cell`)
and every sprite took whatever ink its own pixels resolved to
(`spriting._spectrum_attribute`). A design could name a colour; nothing
listened.

This module is the listener, and it is deliberately the only one: the
translation from prose to a machine colour is a single table read from one
place, rather than a guess repeated in the packer, the header writer and the
prompt.

**Prose, not an enumeration.** `PaletteEntry.colour` is `Prose` -- free text
the drafter writes, in the language the brief was written in. So this parses
rather than looks up: it scans the words for a colour name it knows in either
English or Spanish and for a brightness modifier, and answers `None` when it
finds no colour at all. `None` is load-bearing and not the same as white: a
caller that could not tell "the design named nothing" from "the design named
white" would have to overwrite the ink a sprite's own pixels resolved to on
every project that never mentioned colour.

**Why the Spectrum gets an attribute and the CPC gets a pen.** They are not
the same kind of thing. The Spectrum's colour lives outside the bitmap, one
attribute byte per character cell, so a colour a design declares can be
applied to art that was packed without knowing it. The CPC's colour lives
*in* the pixels -- `spriting.pack_cpc` encodes a pen index per pixel -- so a
declared colour there is a pen the art should have been drawn in, and the
only honest thing to hand back is that pen index. `compiler.CPC_DEFAULT_PALETTE`
is what the packers really use, so a named colour resolves to the nearest of
those four rather than to one of the sixteen the hardware could be set up for
but no design ever sets (see `sprite_grid.palette_for`, which draws the same
distinction for the drawing side).
"""

from __future__ import annotations

import re

from .models import GameProject, TargetPlatform

#: Ink bits per colour name, in both languages a design is written in. The
#: values are the Spectrum's own bit layout, quoted in full in `spriting.py`:
#: bit 0 is blue, bit 1 red, bit 2 green, and every remaining colour is the OR
#: of those (magenta = red|blue, cyan = green|blue, yellow = red|green, white =
#: all three). Written out rather than computed so a reader can check a name
#: against `<arch/zx.h>` by eye.
_INK_BY_NAME: dict[str, int] = {
    "black": 0x00,
    "negro": 0x00,
    "blue": 0x01,
    "azul": 0x01,
    "red": 0x02,
    "rojo": 0x02,
    "magenta": 0x03,
    "purple": 0x03,
    "morado": 0x03,
    "green": 0x04,
    "verde": 0x04,
    "cyan": 0x05,
    "cian": 0x05,
    "turquesa": 0x05,
    "yellow": 0x06,
    "amarillo": 0x06,
    "white": 0x07,
    "blanco": 0x07,
}

#: Words that mean "the bright half of the palette". The Spectrum has two
#: intensities of every ink and BRIGHT is the bit that picks between them, so a
#: design saying "bright red" is asking for something the machine really has.
_BRIGHT_WORDS = frozenset({"bright", "brillante", "intenso", "vivo", "luminoso"})

#: BRIGHT, from `<arch/zx.h>`. Named here rather than imported from
#: `spriting.py`: that module's copy is private to its pixel-derived
#: attribute, and one constant defined twice against the same quoted header is
#: cheaper than a dependency between two modules that share nothing else.
_BRIGHT_BIT = 0x40

#: PAPER_BLACK. Every design Studio ships draws on black paper (the same
#: commitment `spriting._PAPER_BLACK` records), so a declared colour is an ink
#: on that paper and not a paper of its own.
_PAPER_BLACK = 0x00

#: Splits prose into words, so "cyan, bright" and "bright cyan" read alike and
#: punctuation never becomes part of a name.
_WORDS = re.compile(r"[^\W\d_]+", re.UNICODE)


def _words(prose: str) -> list[str]:
    return [word.lower() for word in _WORDS.findall(prose)]


def spectrum_attribute(prose: str) -> int | None:
    """`prose` as a Spectrum attribute byte, or `None` if it names no colour.

    The first colour word wins. Prose that mentions two ("red bricks on a
    blue wall") is describing a scene rather than naming a colour, and taking
    the first is both predictable and what a reader would guess; refusing
    would turn an over-descriptive palette entry into a failed build.
    """
    words = _words(prose)
    ink = next((_INK_BY_NAME[word] for word in words if word in _INK_BY_NAME), None)
    if ink is None:
        return None
    bright = _BRIGHT_BIT if any(word in _BRIGHT_WORDS for word in words) else 0
    return _PAPER_BLACK | ink | bright


def cpc_pen(prose: str, palette: list[tuple[int, int, int]] | None = None) -> int | None:
    """`prose` as an index into the palette the CPC packers really use.

    `palette` defaults to `compiler.CPC_DEFAULT_PALETTE`, imported inside the
    call the way `sprite_grid.palette_for` does it: `compiler` imports this
    module's neighbours, and a module-level import here would close that loop.
    """
    attribute = spectrum_attribute(prose)
    if attribute is None:
        return None
    if palette is None:
        from .compiler import CPC_DEFAULT_PALETTE

        palette = CPC_DEFAULT_PALETTE
    # The named colour as RGB, at whichever of the machine's two intensities
    # the prose asked for, and then the nearest pen actually packed. Going
    # through RGB rather than matching pen names means a palette that changes
    # its four colours keeps resolving names correctly with no table to edit.
    level = 0xFF if attribute & _BRIGHT_BIT else 0xCD
    ink = attribute & 0x07
    wanted = (
        level if ink & 0x02 else 0,
        level if ink & 0x04 else 0,
        level if ink & 0x01 else 0,
    )
    # Pen 0 is the paper (`CPC_DEFAULT_PALETTE` starts at HW_BLACK), so it is
    # only a candidate for a colour that actually asked to be black. Without
    # this, a design's "bright red" -- a colour those four pens cannot show at
    # all -- ties black against yellow on Euclidean distance and the tie hands
    # back the background: brickwork painted in the colour of the void behind
    # it. The same reasoning `spriting._MONOCHROME_FALLBACK_INK` records for
    # the Spectrum, one machine over.
    candidates = range(len(palette)) if ink == 0 else range(1, len(palette))
    return min(
        candidates,
        key=lambda index: sum((a - b) ** 2 for a, b in zip(wanted, palette[index])),
    )


def declared_attribute(project: GameProject, colour_id: str | None) -> int | None:
    """What `colour_id` means on `project`'s target, or `None`.

    Three different silences all answer `None`, and none of them is an error:
    a tile or entity with no `colour` at all, an id the design's palette never
    declared (the drafter is free to write one and forget the entry), and an
    entry whose prose names no colour this module knows. In every case the
    caller keeps whatever colour it would have used without a design saying
    anything -- the pixel-derived ink for a sprite, white for a character
    cell -- which is why the answer is `None` rather than a default.
    """
    if colour_id is None:
        return None
    entry = next((item for item in project.presentation.palette if item.id == colour_id), None)
    if entry is None:
        return None
    if project.target.platform is TargetPlatform.SPECTRUM:
        return spectrum_attribute(entry.colour)
    return cpc_pen(entry.colour)
