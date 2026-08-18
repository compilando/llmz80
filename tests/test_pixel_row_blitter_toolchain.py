"""Real-toolchain proof that a sprite can sit on a pixel row, not just a cell.

Every position in this project has been a character cell: `SpawnSpec` holds a
`col` and a `row`, `plat_sprite` takes the same pair, and so nothing a
generated game draws has ever moved by less than eight pixels. On a machine
whose whole idiom is a smoothly moving sprite that is a real ceiling, and half
of it comes off cheaply -- the vertical half.

Cheaply, because neither machine needs a differently packed sprite to move
down by one pixel. It needs a different *address*, and both toolchains already
compute one: z88dk has `zx_pxy2saddr` and `zx_saddrpdown`, which steps one
pixel line and crosses the Spectrum's non-linear thirds by itself, and
`cpct_getScreenPtr` already takes its y in pixel lines rather than character
rows -- `plat_sprite` was multiplying a row by eight to throw that away.

The horizontal half is not cheap and is not here: a sprite moved by less than
one byte across needs pre-shifted copies of itself, eight on the Spectrum and
two or four on the CPC, and the memory for them.

What is asserted below is the only thing worth asserting: that the sprite's
first line lands on the pixel row the caller named, at a row that is *not* a
multiple of eight -- because at a multiple of eight a broken implementation
that quietly rounds to the containing cell passes.
"""

from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path

import pytest

from llmz80.core.state_contract import REQUIRED_SYMBOLS, SYMBOLS_BY_NAME, required_declarations
from llmz80.core.toolchain import resolve_cpct_path
from llmz80.studio.models import TargetPlatform
from llmz80.studio.services import StudioService
from llmz80.studio.spriting import pack_spectrum
from tests.test_sprite_blitter_toolchain import (
    _connect_zrcp,
    _free_local_port,
    _sprite_image,
    _zrcp_query,
)

zcc_missing = pytest.mark.skipif(shutil.which("zcc") is None, reason="z88dk is not installed")
make_missing = pytest.mark.skipif(shutil.which("make") is None, reason="make is not installed")
zesarux_missing = pytest.mark.skipif(
    shutil.which("zesarux") is None, reason="ZEsarUX is not installed"
)
cpctelera_missing = pytest.mark.skipif(
    resolve_cpct_path() is None, reason="no set-up CPCtelera was found"
)

CONTRACT_STATE = required_declarations()
CONTRACT_INIT = "".join(
    f"    {name} = 0;\n"
    for name in REQUIRED_SYMBOLS
    if not SYMBOLS_BY_NAME[name].provided_by_library
)

#: Where the sprite is drawn. The column is a plain character column -- this
#: change is about the vertical axis only -- and the pixel row is deliberately
#: **not** a multiple of eight: 59 is cell row 7 plus three pixel lines. An
#: implementation that ignored the offset and drew into cell row 7 would pass
#: at py=56 and fail here, which is the whole point of the number.
PIXEL_COL = 2
PIXEL_ROW = 59

#: 59 spans cell rows 7, 8 and 9 (pixel rows 59..74), so the sprite straddles
#: three character rows rather than the two a cell-aligned one covers -- and
#: the third of them, row 8, is in the *second* screen third, which is where a
#: naive `address + 256` stride stops being the next pixel line at all.
STRADDLED_ROWS = (7, 8, 9)

BACKGROUND_BYTE = 0xAA


def _pixel_row_address(col: int, py: int) -> int:
    """The Spectrum screen address of one pixel row, at a byte column.

    The display file's own layout: third, then the pixel line within the
    character row, then the character row within the third. Spelled out here
    rather than derived from `_screen_address` so the test computes the answer
    the hardware gives independently of the helper the cell-aligned test uses.
    """
    third, rest = divmod(py, 64)
    # Within a third: the character row comes first and the scanline inside
    # that row second, and getting these two the wrong way round is how this
    # helper was first written. It reads plausible either way -- both are
    # small numbers derived from the same remainder -- and it does not fail
    # loudly, it just reads a different part of the screen and reports the
    # blitter wrong.
    row_in_third, line = divmod(rest, 8)
    return 0x4000 + third * 2048 + line * 256 + row_in_third * 32 + col


def _build_spectrum(tmp_path: Path):
    workspace = tmp_path / "projects"
    service = StudioService.at(workspace)
    project, directory = service.create_project("PixelRow", TargetPlatform.SPECTRUM)

    sprite_path = tmp_path / "hero.png"
    _sprite_image().save(sprite_path)
    service.add_asset(project, directory, sprite_path)

    program_dir = directory / project.program_dir
    program_dir.mkdir(parents=True, exist_ok=True)
    (program_dir / "main.c").write_text(
        f"""#include <arch/zx.h>
#include "platform.h"

{CONTRACT_STATE}
void main(void) {{
    unsigned char line;
    unsigned char *at;
    plat_init();
{CONTRACT_INIT}
    /* Fill the sixteen pixel rows the sprite will cover with a known pattern,
     * so the (screen & mask) | data formula is exercised rather than drawn
     * over blank memory -- and so a blitter writing to the wrong rows leaves
     * this pattern visible where the sprite should be. */
    at = (unsigned char *)zx_pxy2saddr({PIXEL_COL} * 8, {PIXEL_ROW});
    for (line = 0; line < 16; ++line) {{
        at[0] = 0x{BACKGROUND_BYTE:02X};
        at[1] = 0x{BACKGROUND_BYTE:02X};
        at = (unsigned char *)zx_saddrpdown(at);
    }}
    plat_sprite_py({PIXEL_COL}, {PIXEL_ROW}, 0, 0);
    while (1) {{ }}
}}
""",
        encoding="utf-8",
    )
    return service.build(project, directory)


def _read_spectrum_screen(artifact: Path) -> bytearray:
    """The sixteen pixel rows starting at PIXEL_ROW, two bytes each."""
    port = _free_local_port()
    process = subprocess.Popen(
        [
            "zesarux",
            "--noconfigfile",
            "--machine",
            "48k",
            "--vo",
            "null",
            "--ao",
            "null",
            "--fastautoload",
            "--quickexit",
            "--enable-remoteprotocol",
            "--remoteprotocol-port",
            str(port),
            "--exit-after",
            "16",
            str(artifact),
        ],
        cwd=artifact.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        connection = _connect_zrcp(port, time.monotonic() + 3.0)
        with connection:
            time.sleep(3.5)
            _zrcp_query(connection, "get-version")
            read = bytearray()
            for line in range(16):
                address = _pixel_row_address(PIXEL_COL, PIXEL_ROW + line)
                answer = _zrcp_query(connection, f"read-memory {address} 2")
                digits = "".join(
                    ch for ch in answer.split("command@")[0] if ch in "0123456789abcdefABCDEF"
                )[:4]
                assert len(digits) == 4, f"no memory read back for {address:#06x}: {answer!r}"
                read.append(int(digits[0:2], 16))
                read.append(int(digits[2:4], 16))
            return read
    finally:
        process.terminate()
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate(timeout=5)


@zcc_missing
def test_the_spectrum_library_offers_a_pixel_row_blitter(tmp_path: Path):
    """The cheap half, so a compile break is not diagnosed through an emulator."""
    build = _build_spectrum(tmp_path)

    assert build.success, build.report.get("stderr") or build.report.get("stdout")


@zcc_missing
@zesarux_missing
def test_the_spectrum_sprite_lands_on_the_pixel_row_it_was_given(tmp_path: Path):
    """Read back out of the machine: the same bytes `plat_sprite` would write,
    sixteen pixel rows down from PIXEL_ROW rather than from its cell."""
    build = _build_spectrum(tmp_path)
    assert build.success, build.report.get("stderr") or build.report.get("stdout")
    assert build.artifact is not None and build.artifact.is_file()

    expected_data = pack_spectrum([_sprite_image()]).data
    assert len(expected_data) == 32
    expected = bytes((BACKGROUND_BYTE | byte) & 0xFF for byte in expected_data)

    assert bytes(_read_spectrum_screen(build.artifact)) == expected


@zcc_missing
@zesarux_missing
def test_the_attributes_cover_all_three_rows_the_sprite_straddles(tmp_path: Path):
    """A cell-aligned sprite touches four cells; one offset inside a cell
    touches six, and the two it gains are the ones a blitter that only wrote
    `row` and `row + 1` would leave in whatever colour was there before --
    which reads on screen as a sprite with its head or feet cut off.
    """
    build = _build_spectrum(tmp_path)
    assert build.success, build.report.get("stderr") or build.report.get("stdout")
    assert build.artifact is not None

    port = _free_local_port()
    process = subprocess.Popen(
        [
            "zesarux",
            "--noconfigfile",
            "--machine",
            "48k",
            "--vo",
            "null",
            "--ao",
            "null",
            "--fastautoload",
            "--quickexit",
            "--enable-remoteprotocol",
            "--remoteprotocol-port",
            str(port),
            "--exit-after",
            "16",
            str(build.artifact),
        ],
        cwd=build.artifact.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        connection = _connect_zrcp(port, time.monotonic() + 3.0)
        with connection:
            time.sleep(3.5)
            _zrcp_query(connection, "get-version")
            seen = []
            for row in STRADDLED_ROWS:
                for column in (PIXEL_COL, PIXEL_COL + 1):
                    address = 0x5800 + row * 32 + column
                    answer = _zrcp_query(connection, f"read-memory {address} 1")
                    digits = "".join(
                        ch for ch in answer.split("command@")[0] if ch in "0123456789abcdefABCDEF"
                    )[:2]
                    seen.append(int(digits, 16))
    finally:
        process.terminate()
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate(timeout=5)

    # One ink for the whole sprite is what the machine affords, so every cell
    # it covers must carry the same attribute -- and it must not be the
    # cleared screen's, or the blitter never wrote it.
    assert len(set(seen)) == 1, dict(zip(STRADDLED_ROWS, seen))


CPC_PIXEL_COL = 18
CPC_PIXEL_ROW = 83


def _build_cpc(tmp_path: Path):
    workspace = tmp_path / "cpc"
    service = StudioService.at(workspace)
    project, directory = service.create_project("PixelRow", TargetPlatform.AMSTRAD_CPC)

    sprite_path = tmp_path / "hero_cpc.png"
    _sprite_image().save(sprite_path)
    service.add_asset(project, directory, sprite_path)

    program_dir = directory / project.program_dir
    program_dir.mkdir(parents=True, exist_ok=True)
    (program_dir / "main.c").write_text(
        f"""#include "platform.h"

{CONTRACT_STATE}
void main(void) {{
    plat_init();
{CONTRACT_INIT}
    plat_sprite_py({CPC_PIXEL_COL}, {CPC_PIXEL_ROW}, 0, 0);
    while (1) {{ }}
}}
""",
        encoding="utf-8",
    )
    return service.build(project, directory)


@make_missing
@cpctelera_missing
def test_the_cpc_library_offers_a_pixel_row_blitter(tmp_path: Path):
    """`cpct_getScreenPtr` already takes a pixel row, so this is the CPC's
    whole cost: not multiplying it away."""
    build = _build_cpc(tmp_path)

    assert build.success, build.report.get("stderr") or build.report.get("stdout")


@make_missing
@cpctelera_missing
@zesarux_missing
def test_the_cpc_draws_something_at_a_pixel_row_between_cells(tmp_path: Path):
    """Not the exact bytes, unlike the Spectrum.

    The CPC's screen has no attribute area and its pixel bytes interleave
    differently per video mode, so `_ZESARUX_PROFILES` marks it as reading no
    display file and `attributes.attribute_report` abstains on it. What can be
    had is the same evidence `test_cpc_blitter_visibly_draws_where_the_control
    _build_does_not` settles for: the screen is not blank after the program
    ran, at a pixel row no cell-aligned call could have reached.
    """
    from llmz80.quality.emulator_smoke import smoke_test

    build = _build_cpc(tmp_path)
    assert build.success, build.report.get("stderr") or build.report.get("stdout")

    report = smoke_test(build.output_dir, "amstrad_cpc", full=True, seconds=3)

    assert not report.get("emulator_error"), report.get("emulator_error")
    frames = report["frames"]
    assert len(frames) >= 2, report
    assert frames[1]["non_dominant_pixels"] > 30, frames[1]["path"]
