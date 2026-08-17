"""Real-toolchain proof that terrain artwork reaches the screen.

The sibling of `test_sprite_blitter_toolchain.py`, aimed at the two calls tile
art added: `plat_tile`, which puts a design's own 8x8 block into a character
cell, and `plat_ink`, which decides the colour the character-drawn cells and
text are written in. Both claims are checked the strong way the Spectrum
affords -- the bytes are read back out of the emulated machine's screen and
attribute files -- because a compile is not a drawing and a colour that
compiles can still be invisible.

One cell, at a boundary that matters: row 7 is the last row of the Spectrum
screen's first third, so a tile drawn there proves the blitter converted its
address rather than assuming the screen file is linear. (A tile is one cell
tall, so unlike the two-cell sprite it never spans the boundary itself; what
row 7 catches here is arithmetic that only happens to work in the first
third.)
"""

from __future__ import annotations

import shutil
import socket
import subprocess
import time
from pathlib import Path

import pytest
from PIL import Image

from llmz80.core.state_contract import REQUIRED_SYMBOLS, SYMBOLS_BY_NAME, required_declarations
from llmz80.studio.models import TargetPlatform
from llmz80.studio.services import StudioService
from llmz80.studio.spriting import pack_spectrum_tile
from tests.test_sprite_blitter_toolchain import (
    _connect_zrcp,
    _free_local_port,
    _screen_address,
    _zrcp_query,
)

zcc_missing = pytest.mark.skipif(shutil.which("zcc") is None, reason="z88dk is not installed")
zesarux_missing = pytest.mark.skipif(
    shutil.which("zesarux") is None, reason="ZEsarUX is not installed"
)

TILE_COL = 9
TILE_ROW = 7

#: The ink plat_ink is switched to before the character cell is drawn:
#: PAPER_BLACK | INK_MAGENTA | BRIGHT. Deliberately not white, which is what
#: the library used to hardcode, and not black, which would be invisible.
INK_UNDER_TEST = 0x43

CONTRACT_STATE = required_declarations()
CONTRACT_INIT = "".join(
    f"    {name} = 0;\n"
    for name in REQUIRED_SYMBOLS
    if not SYMBOLS_BY_NAME[name].provided_by_library
)


def _tile_image() -> Image.Image:
    """An 8x8 tile that is neither blank nor solid, in a dim non-white colour
    so the attribute the packer derives is distinguishable from the old
    hardcoded PAPER_BLACK | INK_WHITE."""
    image = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    pixels = image.load()
    for y in range(8):
        for x in range(8):
            if (x + y) % 3 != 0:
                pixels[x, y] = (0, 205, 205, 255)  # dim cyan
    return image


def _build_tile_project(tmp_path: Path):
    """Render and build a Spectrum project whose program draws one tile."""
    workspace = tmp_path / "projects"
    service = StudioService.at(workspace)
    project, directory = service.create_project("TileProbe", TargetPlatform.SPECTRUM)

    tile_path = tmp_path / "ladrillo.png"
    _tile_image().save(tile_path)
    asset = service.add_asset(project, directory, tile_path, kind="tileset")
    project.tiles[0].art = asset.id
    service.save_project(project, directory)

    program_dir = directory / project.program_dir
    program_dir.mkdir(parents=True, exist_ok=True)
    (program_dir / "main.c").write_text(
        f"""#include <arch/zx.h>
#include "platform.h"
#include "tiles.h"

{CONTRACT_STATE}
void main(void) {{
    plat_init();
{CONTRACT_INIT}
    plat_tile({TILE_COL}, {TILE_ROW}, TILE_{project.tiles[0].id.upper()});
    plat_ink(0x{INK_UNDER_TEST:02X});
    plat_cell({TILE_COL + 1}, {TILE_ROW}, 'X');
    while (1) {{ }}
}}
""",
        encoding="utf-8",
    )

    return service.build(project, directory)


@zcc_missing
def test_a_project_with_tile_art_compiles_and_links(tmp_path: Path):
    build = _build_tile_project(tmp_path)

    assert build.success, build.report.get("stderr") or build.report.get("stdout")
    assert build.artifact is not None and build.artifact.is_file()
    tiles_h = (build.output_dir / "src" / "tiles.h").read_text(encoding="utf-8")
    assert "#define TILE_COUNT 1" in tiles_h


def _attribute_address(col: int, row: int) -> int:
    """The attribute file is linear, one byte per cell, unlike the bitmap."""
    return 0x5800 + row * 32 + col


def _read_byte(connection: socket.socket, address: int) -> int:
    answer = _zrcp_query(connection, f"read-memory {address} 1")
    digits = "".join(
        ch for ch in answer.split("command@")[0] if ch in "0123456789abcdefABCDEF"
    )[:2]
    assert len(digits) == 2, f"no memory read back for {address:#06x}: {answer!r}"
    return int(digits, 16)


@zcc_missing
@zesarux_missing
def test_the_tile_blitter_draws_the_exact_packed_bytes_and_its_own_colour(tmp_path: Path):
    build = _build_tile_project(tmp_path)
    assert build.success, build.report.get("stderr") or build.report.get("stdout")
    artifact = build.artifact
    assert artifact is not None and artifact.is_file()

    packed = pack_spectrum_tile(_tile_image())
    assert len(packed.data) == 8

    port = _free_local_port()
    command = [
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
    ]
    process = subprocess.Popen(
        command,
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

            drawn = bytes(
                _read_byte(connection, _screen_address(TILE_COL, TILE_ROW, line))
                for line in range(8)
            )
            tile_attribute = _read_byte(connection, _attribute_address(TILE_COL, TILE_ROW))
            cell_attribute = _read_byte(connection, _attribute_address(TILE_COL + 1, TILE_ROW))
    finally:
        process.terminate()
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate(timeout=5)

    assert drawn == packed.data
    assert tile_attribute == packed.attribute
    # plat_ink decides what a character cell is written in; before it existed
    # every cell was PAPER_BLACK | INK_WHITE whatever the design said.
    assert cell_attribute == INK_UNDER_TEST
