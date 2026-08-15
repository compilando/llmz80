"""Judging the display file the machine actually held.

What this gate looks for is one thing and it is not colour clash. Clash --
two colours wanted inside one 8x8 cell -- is not visible in the display file
at all: seeing it would mean knowing which sprite overlapped which
background, and that is a claim about the program, not about its output.
What *is* visible there, costs one memory read, and is a defect in every
design without exception, is a cell carrying drawn pixels whose ink is the
same colour as its paper. The player sees nothing in that cell. That is the
whole of what `invisible_cells` reports.

`spriting.py` already fights this failure from the other side:
`_MONOCHROME_FALLBACK_INK` exists because a correctly shaped sprite packed
with INK_BLACK on PAPER_BLACK draws a silhouette nobody can see. That was
caught by reading a fixture before the program was ever built. This catches
it on the real machine, in whatever the program actually put on screen --
which is the only place a paper chosen by the program itself, rather than by
the packer, can be checked against the ink drawn over it.

The address arithmetic is the hardware's, not a stride: the screen is three
thirds of eight character rows each, and inside a third the eight pixel
lines of a character row are 256 bytes apart. This is exactly why
`resources/studio_lib/spectrum/platform.c` writes `address[line << 8]`
instead of adding a row width -- the same fact, told to Python instead of
to the C.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

#: The bitmap: 192 pixel rows of 32 bytes, addressed in thirds.
BITMAP_BYTES = 6144

#: One attribute byte per character cell, laid out plainly row by row --
#: the thirds apply to the bitmap only.
ATTRIBUTE_ORIGIN = BITMAP_BYTES

#: Bitmap plus attributes: the whole display file, and the exact length
#: `quality.emulator_smoke._read_screen` writes or nothing.
SCREEN_BYTES = 6912

COLUMNS = 32
ROWS = 24

#: How many cells a failure may name before it stops being a diagnostic. A
#: black-on-black screen has 768 of them, and a failure listing all 768 is
#: not something a repair prompt or a person can read.
_MAX_NAMED_CELLS = 12


def cell_offset(col: int, row: int) -> int:
    """Where a character cell's first pixel line lives in the bitmap.

    `third, row_in_third = divmod(row, 8)` and the result is
    `(third << 11) | (row_in_third << 5) | col`. Row 8 therefore starts 2048
    bytes in, not 8*32 = 256: the second third begins there. Getting this
    wrong does not crash anything, it silently judges the wrong cell, which
    is why it has a test of its own.
    """
    third, row_in_third = divmod(row, 8)
    return (third << 11) | (row_in_third << 5) | col


def invisible_cells(screen: bytes) -> list[tuple[int, int]]:
    """Cells carrying drawn pixels whose ink cannot be told from their paper.

    BRIGHT is ignored on purpose: it applies to ink and paper together, so it
    can never separate a colour from itself. FLASH is ignored for the same
    reason -- it swaps the two, and swapping a colour with itself changes
    nothing.

    A cell with no set pixels is never reported however its attribute reads:
    black ink on black paper with nothing drawn in it is just background, and
    a screen is mostly that. Only pixels the program actually set and then
    made unreadable are a defect.

    A screen of the wrong length yields no cells. Judging a truncated dump
    would read the missing half as unset pixels and quietly approve it.
    """
    if len(screen) != SCREEN_BYTES:
        return []
    cells: list[tuple[int, int]] = []
    for row in range(ROWS):
        for col in range(COLUMNS):
            attribute = screen[ATTRIBUTE_ORIGIN + row * COLUMNS + col]
            if attribute & 0x07 != (attribute >> 3) & 0x07:
                continue
            base = cell_offset(col, row)
            if any(screen[base + (line << 8)] for line in range(8)):
                cells.append((col, row))
    return cells


def _named(cells: list[tuple[int, int]]) -> str:
    shown = ", ".join(f"({col},{row})" for col, row in cells[:_MAX_NAMED_CELLS])
    remaining = len(cells) - _MAX_NAMED_CELLS
    return f"{shown} and {remaining} more" if remaining > 0 else shown


def attribute_report(runtime: dict[str, Any]) -> dict[str, Any]:
    """Judge the display file for content no player could have seen.

    Abstaining is not passing, exactly as in `feel.animation_report` and
    `pacing.pacing_report`: with no dump to read there is nothing to judge,
    and `quality_pass` is `None` rather than `True`. There are three ways to
    have nothing: a target whose harness never dumps a screen (the CPC path,
    `emulator_smoke._run_caprice32`, has no remote protocol to read memory
    through and writes no such key), a run whose ZRCP answer arrived short so
    `_read_screen` wrote no file at all, and a file that cannot be read back.

    A dump of the wrong length abstains for the same reason `invisible_cells`
    refuses it: half a display file judged as though the missing half were
    blank is a pass nobody earned.
    """
    dump = runtime.get("screen_dump")
    if not dump:
        return {
            "schema_version": 1,
            "observed": False,
            "reason": "this run kept no display file; the target has no way to read "
            "emulated memory, or the screen read came back short",
            "invisible_cells": [],
            "failures": [],
            "quality_pass": None,
        }
    try:
        screen = Path(dump).read_bytes()
    except OSError as exc:
        return {
            "schema_version": 1,
            "observed": False,
            "reason": f"the display file at {dump} could not be read: {exc}",
            "invisible_cells": [],
            "failures": [],
            "quality_pass": None,
        }
    if len(screen) != SCREEN_BYTES:
        return {
            "schema_version": 1,
            "observed": False,
            "reason": f"the display file at {dump} is {len(screen)} bytes, not "
            f"{SCREEN_BYTES}; a partial screen says nothing about the cells it is "
            "missing",
            "invisible_cells": [],
            "failures": [],
            "quality_pass": None,
        }
    cells = invisible_cells(screen)
    failures: list[str] = []
    if cells:
        failures.append(
            f"{len(cells)} character cell(s) hold drawn pixels whose ink is the same "
            f"colour as their paper, so nothing in them reaches the player: "
            f"{_named(cells)}. Give what is drawn there an ink that differs from the "
            "paper of the cell it lands in -- BRIGHT does not help, it lifts both."
        )
    return {
        "schema_version": 1,
        "observed": True,
        "invisible_cells": cells,
        "failures": failures,
        "quality_pass": not failures,
    }
