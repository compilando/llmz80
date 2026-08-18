"""Real-toolchain proof that a sprite can be rubbed out without a trace.

The claim `plat_save_under`/`plat_restore_under` make is exact and therefore
checkable: after saving, drawing a sprite and restoring, the screen must hold
the bytes it held before -- every pixel and, on the Spectrum, every attribute
of every character row the sprite covered.

Checked against a background that is *not* terrain, on purpose. Repainting the
tile map is the alternative this replaces, and it would pass a test whose
background was tiles while failing the case the mechanism exists for: text, a
second sprite, anything a design draws that its tile map does not describe.
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
from tests.test_pixel_row_blitter_toolchain import _pixel_row_address
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

#: Where the sprite is drawn and rubbed out. `PY` is deliberately not a
#: multiple of eight: at a cell boundary a sprite covers two character rows and
#: an implementation that saved only two rows of attributes would pass.
PX = 24
PY = 59

#: The background the sprite is drawn over: a pattern written straight into the
#: bitmap, which no tile map describes and no terrain repaint could restore.
PATTERN = 0x5A


def _program(*, restore: bool) -> str:
    """Paint a background, draw a sprite over it, and put the background back.

    `restore=False` is the control: the same program that does not restore, so
    the assertion below is comparing against a screen the sprite really changed
    rather than one it never reached.
    """
    put_back = (
        f"    plat_restore_under({PX}, {PY}, under);\n"
        if restore
        else "    /* control: the sprite stays */\n"
    )
    return f"""#include <arch/zx.h>
#include "platform.h"
#include "game_config.h"\n#include "sprites.h"

{CONTRACT_STATE}
static unsigned char under[SPRITE_UNDER_BYTES];

void main(void) {{
    unsigned char line;
    unsigned char byte;
    unsigned char row;
    unsigned char *at;
    plat_init();
{CONTRACT_INIT}
    /* A background no tile map describes: written into the bitmap directly,
     * with an attribute per covered cell that is not the sprite's. */
    at = (unsigned char *)zx_pxy2saddr({PX}, {PY});
    for (line = 0; line < 16; ++line) {{
        for (byte = 0; byte < SPRITE_BYTES_WIDE; ++byte) at[byte] = 0x{PATTERN:02X};
        at = (unsigned char *)zx_saddrpdown(at);
    }}
    for (row = 0; row < 3; ++row) {{
        for (byte = 0; byte < SPRITE_BYTES_WIDE; ++byte) {{
            *(unsigned char *)zx_cxy2aaddr(({PX} >> 3) + byte, ({PY} >> 3) + row) = 0x26;
        }}
    }}

    plat_save_under({PX}, {PY}, under);
    plat_sprite_px({PX}, {PY}, 0, 0);
{put_back}    while (1) {{ }}
}}
"""


def _build(tmp_path: Path, *, restore: bool):
    name = "restored" if restore else "control"
    service = StudioService.at(tmp_path / name)
    project, directory = service.create_project(name, TargetPlatform.SPECTRUM)

    sprite_path = tmp_path / f"hero_{name}.png"
    _sprite_image().save(sprite_path)
    service.add_asset(project, directory, sprite_path)

    program_dir = directory / project.program_dir
    program_dir.mkdir(parents=True, exist_ok=True)
    (program_dir / "main.c").write_text(_program(restore=restore), encoding="utf-8")
    return service.build(project, directory)


def _read(artifact: Path, width: int) -> tuple[bytearray, bytearray]:
    """The sixteen bitmap rows the sprite covered, and the three cell rows."""
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

    def read_bytes(address: int, count: int) -> list[int]:
        answer = _zrcp_query(connection, f"read-memory {address} {count}")
        digits = "".join(
            ch for ch in answer.split("command@")[0] if ch in "0123456789abcdefABCDEF"
        )[: count * 2]
        assert len(digits) == count * 2, f"{address:#06x}: {answer!r}"
        return [int(digits[i * 2 : i * 2 + 2], 16) for i in range(count)]

    try:
        connection = _connect_zrcp(port, time.monotonic() + 3.0)
        with connection:
            time.sleep(3.5)
            _zrcp_query(connection, "get-version")
            pixels = bytearray()
            for line in range(16):
                pixels += bytes(read_bytes(_pixel_row_address(PX >> 3, PY + line), width))
            attributes = bytearray()
            for row in range(3):
                address = 0x5800 + ((PY >> 3) + row) * 32 + (PX >> 3)
                attributes += bytes(read_bytes(address, width))
            return pixels, attributes
    finally:
        process.terminate()
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate(timeout=5)


@zcc_missing
def test_the_spectrum_library_offers_the_pair(tmp_path: Path):
    build = _build(tmp_path, restore=True)

    assert build.success, build.report.get("stderr") or build.report.get("stdout")


@make_missing
@cpctelera_missing
def test_the_cpc_library_offers_it_too(tmp_path: Path):
    """A CPC program compiles against the same two calls, with no attribute
    half to save."""
    service = StudioService.at(tmp_path / "cpc")
    project, directory = service.create_project("Under", TargetPlatform.AMSTRAD_CPC)
    sprite_path = tmp_path / "hero_cpc.png"
    _sprite_image().save(sprite_path)
    service.add_asset(project, directory, sprite_path)
    program_dir = directory / project.program_dir
    program_dir.mkdir(parents=True, exist_ok=True)
    (program_dir / "main.c").write_text(
        f"""#include "platform.h"
#include "game_config.h"\n#include "sprites.h"

{CONTRACT_STATE}
static unsigned char under[SPRITE_UNDER_BYTES];

void main(void) {{
    plat_init();
{CONTRACT_INIT}
    plat_save_under({PX}, {PY}, under);
    plat_sprite_px({PX}, {PY}, 0, 0);
    plat_restore_under({PX}, {PY}, under);
    while (1) {{ }}
}}
""",
        encoding="utf-8",
    )

    build = service.build(project, directory)

    assert build.success, build.report.get("stderr") or build.report.get("stdout")


@zcc_missing
@zesarux_missing
def test_the_sprite_leaves_the_screen_exactly_as_it_found_it(tmp_path: Path):
    """The whole claim, read out of a running 48K."""
    build = _build(tmp_path, restore=True)
    assert build.success, build.report.get("stderr") or build.report.get("stdout")
    assert build.artifact is not None

    # Two bytes: SPRITE_BYTES_WIDE for an unshifted Spectrum sprite, which is
    # what this project is -- it never asked for smooth_horizontal.
    pixels, attributes = _read(build.artifact, 2)

    assert set(pixels) == {PATTERN}, pixels
    assert set(attributes) == {0x26}, attributes


@zcc_missing
@zesarux_missing
def test_the_control_shows_the_sprite_really_covered_it(tmp_path: Path):
    """Without this the test above passes on a program whose sprite never
    reached the screen: an implementation that drew nothing would leave the
    background untouched and look like a perfect restore."""
    build = _build(tmp_path, restore=False)
    assert build.success, build.report.get("stderr") or build.report.get("stdout")
    assert build.artifact is not None

    pixels, attributes = _read(build.artifact, 2)

    assert set(pixels) != {PATTERN}
    assert set(attributes) != {0x26}
