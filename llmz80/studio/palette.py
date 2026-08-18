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
from dataclasses import dataclass

from .models import GameProject, TargetPlatform, VideoMode


def cpc_mode(project: GameProject) -> int:
    """Which CPC video mode this project targets, as the packers number them.

    Here rather than repeated at each call site: `compiler`, `codegen`,
    `sprite_grid` and this module all need it, and four copies of
    `0 if ... is VideoMode.CPC_MODE_0 else 1` is four places for a third mode
    to be forgotten.
    """
    return 0 if project.target.video_mode is VideoMode.CPC_MODE_0 else 1


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


# ---------------------------------------------------------------------------
# The Amstrad CPC's hardware colours.
#
# One table, two consumers, and that is the whole point of it being here. The
# packers need RGB, to quantise a drawn pixel against what the machine will
# show; `codegen.render_config_header` needs the gate-array byte, to write the
# pens `platform.c` programs at run time. Those two facts used to live apart --
# RGB in `compiler.CPC_DEFAULT_PALETTE`, hardware names hard-coded in
# `apply_palette` -- in two files in two languages, and they had drifted:
# HW_BLUE was written down as (0, 0, 255), which is HW_BRIGHT_BLUE, and
# HW_WHITE as (255, 255, 255), which is HW_BRIGHT_WHITE. The CPC's "white" is
# grey. So half the four-pen palette quantised sprites against colours the
# machine was never asked to show, and no test could see it, because neither
# half of the pair knew the other existed.
#
# The values are CPCtelera's `CPCT_HW_Colour` (video/colours.h), and the RGB is
# the CPC's own 3x3x3 space: every channel off, half or full.


@dataclass(frozen=True)
class HardwareColour:
    """One of the CPC's 27 colours, under both the names it answers to."""

    #: CPCtelera's constant, so a reader can check a row against colours.h.
    name: str
    #: What `cpct_setPalette` is given.
    hardware: int
    rgb: tuple[int, int, int]


HARDWARE_COLOURS: tuple[HardwareColour, ...] = (
    HardwareColour("HW_BLACK", 0x14, (0, 0, 0)),
    HardwareColour("HW_BLUE", 0x04, (0, 0, 128)),
    HardwareColour("HW_BRIGHT_BLUE", 0x15, (0, 0, 255)),
    HardwareColour("HW_RED", 0x1C, (128, 0, 0)),
    HardwareColour("HW_MAGENTA", 0x18, (128, 0, 128)),
    HardwareColour("HW_MAUVE", 0x1D, (128, 0, 255)),
    HardwareColour("HW_BRIGHT_RED", 0x0C, (255, 0, 0)),
    HardwareColour("HW_PURPLE", 0x05, (255, 0, 128)),
    HardwareColour("HW_BRIGHT_MAGENTA", 0x0D, (255, 0, 255)),
    HardwareColour("HW_GREEN", 0x16, (0, 128, 0)),
    HardwareColour("HW_CYAN", 0x06, (0, 128, 128)),
    HardwareColour("HW_SKY_BLUE", 0x17, (0, 128, 255)),
    HardwareColour("HW_YELLOW", 0x1E, (128, 128, 0)),
    HardwareColour("HW_WHITE", 0x00, (128, 128, 128)),
    HardwareColour("HW_PASTEL_BLUE", 0x1F, (128, 128, 255)),
    HardwareColour("HW_ORANGE", 0x0E, (255, 128, 0)),
    HardwareColour("HW_PINK", 0x07, (255, 128, 128)),
    HardwareColour("HW_PASTEL_MAGENTA", 0x0F, (255, 128, 255)),
    HardwareColour("HW_BRIGHT_GREEN", 0x12, (0, 255, 0)),
    HardwareColour("HW_SEA_GREEN", 0x02, (0, 255, 128)),
    HardwareColour("HW_BRIGHT_CYAN", 0x13, (0, 255, 255)),
    HardwareColour("HW_LIME", 0x1A, (128, 255, 0)),
    HardwareColour("HW_PASTEL_GREEN", 0x19, (128, 255, 128)),
    HardwareColour("HW_PASTEL_CYAN", 0x1B, (128, 255, 255)),
    HardwareColour("HW_BRIGHT_YELLOW", 0x0A, (255, 255, 0)),
    HardwareColour("HW_PASTEL_YELLOW", 0x03, (255, 255, 128)),
    HardwareColour("HW_BRIGHT_WHITE", 0x0B, (255, 255, 255)),
)

_BY_NAME = {colour.name: colour for colour in HARDWARE_COLOURS}


def _pens(*names: str) -> tuple[HardwareColour, ...]:
    return tuple(_BY_NAME[name] for name in names)


#: Mode 1's four pens. The same four this project has always programmed, with
#: two of them now carrying the colour the hardware actually produces rather
#: than the one somebody assumed.
_MODE_1_PENS = _pens("HW_BLACK", "HW_BLUE", "HW_BRIGHT_YELLOW", "HW_BRIGHT_WHITE")

#: Mode 0's sixteen. Chosen to span the machine's colour space rather than to
#: extend mode 1's four: the point of mode 0 is that a design can name green,
#: orange or pink at all, and a palette that spent twelve of its pens on
#: neighbours of the original four would give a drafter nothing new to say.
#: Mode 1's four are all present, so a design moved between modes keeps every
#: colour it had.
#:
#: Pen 0 is black in both, and that is load-bearing rather than aesthetic:
#: `cpc_pen` will only hand pen 0 to prose that asked for black, because pen 0
#: is the paper and painting brickwork in it draws the void behind the wall.
_MODE_0_PENS = _pens(
    "HW_BLACK",
    "HW_BLUE",
    "HW_BRIGHT_BLUE",
    "HW_RED",
    "HW_BRIGHT_RED",
    "HW_BRIGHT_MAGENTA",
    "HW_GREEN",
    "HW_BRIGHT_GREEN",
    "HW_CYAN",
    "HW_BRIGHT_CYAN",
    "HW_YELLOW",
    "HW_BRIGHT_YELLOW",
    "HW_ORANGE",
    "HW_PINK",
    "HW_WHITE",
    "HW_BRIGHT_WHITE",
)


def cpc_palette(mode: int) -> tuple[HardwareColour, ...]:
    """The pens this video mode really shows, in index order.

    Sixteen in mode 0 and four in mode 1, which is what the pen's bit width
    allows: `spriting.pack_cpc` encodes 4 bits per pen in mode 0 and 2 in mode
    1, and a longer palette than that would alias two colours onto one pen.
    """
    if mode == 0:
        return _MODE_0_PENS
    if mode == 1:
        return _MODE_1_PENS
    raise ValueError(f"the CPC has no video mode {mode} this project supports; expected 0 or 1")


def cpc_rgb(mode: int) -> list[tuple[int, int, int]]:
    """`cpc_palette` as the plain RGB list the packers take."""
    return [colour.rgb for colour in cpc_palette(mode)]


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


def cpc_pen(prose: str, *, mode: int) -> int | None:
    """`prose` as an index into the palette this video mode really shows.

    The mode is required rather than defaulted. It used to take an optional
    palette that no caller ever passed, so every colour on this machine
    resolved against four pens whatever mode the design had chosen -- which is
    what made mode 0's sixteen unreachable from a design's own vocabulary.
    A default here would have let that come back silently.
    """
    attribute = spectrum_attribute(prose)
    if attribute is None:
        return None
    palette = cpc_rgb(mode)
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
    # Pen 0 is the paper (every mode's palette starts at HW_BLACK), so it is
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
    return cpc_pen(entry.colour, mode=cpc_mode(project))
