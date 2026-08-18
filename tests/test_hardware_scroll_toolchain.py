"""Real-toolchain proof that `plat_scroll_to` moves a real CPC's picture.

The unit tests above it pin the numbers; this pins that the numbers are the
machine's. A bar exactly one byte wide is drawn and the display start is moved,
so the bar's own width in captured pixels is the unit being measured -- which
makes the reading independent of whatever scale ZEsarUX captured at.

Both figures came out of this harness in the first place. CPCtelera's own
examples disagree about the horizontal one (`advanced/hwscroll` comments
"4-by-4 bytes"; `advanced/tilemap_hwscroll` advances its pointer by two), and
this is the tie-break, kept as a test so the answer is not something somebody
has to measure again.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from PIL import Image

from llmz80.core.state_contract import REQUIRED_SYMBOLS, SYMBOLS_BY_NAME, required_declarations
from llmz80.core.toolchain import resolve_cpct_path
from llmz80.quality.emulator_smoke import smoke_test
from llmz80.studio.codegen import SCROLL_ROW_BYTES, SCROLL_STEP_BYTES
from llmz80.studio.models import TargetPlatform
from llmz80.studio.services import StudioService

make_missing = pytest.mark.skipif(shutil.which("make") is None, reason="make is not installed")
zcc_missing = pytest.mark.skipif(shutil.which("zcc") is None, reason="z88dk is not installed")
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

#: Byte column of the vertical bar: away from both edges so a shift either way
#: stays on screen. `cpct_drawSolidBox` refuses a width outside [1, 64], which
#: is why the horizontal bar below is 64 and not the full 80 -- a wider one
#: does not fail, it hangs the machine.
BAR_BYTE = 40
BAR_LINE = 96


def _program(*, vertical_bar: bool, origin: int) -> str:
    draw = (
        f"    at = cpct_getScreenPtr(CPCT_VMEM_START, {BAR_BYTE}, 0);\n"
        "    cpct_drawSolidBox(at, 0xFF, 1, 200);\n"
        if vertical_bar
        else f"    at = cpct_getScreenPtr(CPCT_VMEM_START, 0, {BAR_LINE});\n"
        "    cpct_drawSolidBox(at, 0xFF, 64, 8);\n"
    )
    return f"""#include <cpctelera.h>
#include "platform.h"

{CONTRACT_STATE}
void main(void) {{
    u8 *at;
    plat_init();
{CONTRACT_INIT}
{draw}    plat_scroll_to({origin});
    while (1) {{ }}
}}
"""


def _capture(tmp_path: Path, name: str, source: str) -> Path:
    service = StudioService.at(tmp_path / name)
    project, directory = service.create_project(name, TargetPlatform.AMSTRAD_CPC)
    project.presentation.scrolling = True
    service.save_project(project, directory)
    program_dir = directory / project.program_dir
    program_dir.mkdir(parents=True, exist_ok=True)
    (program_dir / "main.c").write_text(source, encoding="utf-8")

    build = service.build(project, directory)
    assert build.success, build.report.get("stderr") or build.report.get("stdout")

    report = smoke_test(build.output_dir, "amstrad_cpc", full=True, seconds=3)
    assert not report.get("emulator_error"), report.get("emulator_error")
    frames = report["frames"]
    assert len(frames) >= 2, report
    return Path(frames[1]["path"])


def _bar_columns(path: Path) -> tuple[int, int]:
    """First and last x of the vertical bar, sampled across the middle row."""
    image = Image.open(path).convert("L")
    width, height = image.size
    pixels = image.load()
    lit = [x for x in range(width) if pixels[x, height // 2] > 128]
    assert lit, f"no bar in {path}"
    return lit[0], lit[-1]


def _bar_rows(path: Path) -> list[int]:
    """Scanlines the full-width bar occupies, ignoring anything narrow."""
    image = Image.open(path).convert("L")
    width, height = image.size
    pixels = image.load()
    return [
        y
        for y in range(height)
        if sum(1 for x in range(0, width, 4) if pixels[x, y] > 128) > width // 16
    ]


@make_missing
@cpctelera_missing
def test_the_cpc_library_compiles_with_the_scroll_call(tmp_path: Path):
    build_source = _program(vertical_bar=True, origin=0)
    service = StudioService.at(tmp_path / "compile")
    project, directory = service.create_project("Compile", TargetPlatform.AMSTRAD_CPC)
    project.presentation.scrolling = True
    service.save_project(project, directory)
    program_dir = directory / project.program_dir
    program_dir.mkdir(parents=True, exist_ok=True)
    (program_dir / "main.c").write_text(build_source, encoding="utf-8")

    build = service.build(project, directory)

    assert build.success, build.report.get("stderr") or build.report.get("stdout")


@zcc_missing
def test_the_spectrum_library_compiles_with_it_too(tmp_path: Path):
    """A no-op there, but one source has to build for both machines."""
    service = StudioService.at(tmp_path / "zx")
    project, directory = service.create_project("Compile", TargetPlatform.SPECTRUM)
    program_dir = directory / project.program_dir
    program_dir.mkdir(parents=True, exist_ok=True)
    (program_dir / "main.c").write_text(
        f"""#include "platform.h"

{CONTRACT_STATE}
void main(void) {{
    plat_init();
{CONTRACT_INIT}
    plat_scroll_to(80);
    while (1) {{ }}
}}
""",
        encoding="utf-8",
    )

    build = service.build(project, directory)

    assert build.success, build.report.get("stderr") or build.report.get("stdout")


@make_missing
@cpctelera_missing
@zesarux_missing
def test_one_step_moves_the_picture_two_bytes(tmp_path: Path):
    """The tie-break against CPCtelera's own contradictory comments.

    Self-calibrating: the bar is one byte wide, so its width in captured
    pixels *is* one byte and the displacement reads in bytes with no
    assumption about the emulator's framebuffer scale.
    """
    step = SCROLL_STEP_BYTES[TargetPlatform.AMSTRAD_CPC]
    at_rest = _bar_columns(_capture(tmp_path, "rest", _program(vertical_bar=True, origin=0)))
    moved = _bar_columns(_capture(tmp_path, "moved", _program(vertical_bar=True, origin=step)))

    byte_width = at_rest[1] - at_rest[0] + 1
    assert byte_width > 0
    assert (at_rest[0] - moved[0]) == byte_width * step


@make_missing
@cpctelera_missing
@zesarux_missing
def test_one_screen_row_of_origin_moves_the_picture_up_one_character_row(tmp_path: Path):
    """The vertical half, and the reason the API takes a byte origin rather
    than an (x, y): it is one register, and a row of it is a row up."""
    row = SCROLL_ROW_BYTES[TargetPlatform.AMSTRAD_CPC]
    at_rest = _bar_rows(_capture(tmp_path, "vrest", _program(vertical_bar=False, origin=0)))
    moved = _bar_rows(_capture(tmp_path, "vmoved", _program(vertical_bar=False, origin=row)))

    assert at_rest and moved
    character_row = len(at_rest)
    assert (at_rest[0] - moved[0]) == character_row


@make_missing
@cpctelera_missing
@zesarux_missing
def test_an_origin_past_the_register_is_ignored_rather_than_wrapped(tmp_path: Path):
    """R13 holds eight bits. Letting an out-of-range origin through would make
    a scroller jump back to the start of the screen instead of stopping, which
    is the harder thing to diagnose from a screenshot."""
    at_rest = _bar_columns(_capture(tmp_path, "guard0", _program(vertical_bar=True, origin=0)))
    past = _bar_columns(_capture(tmp_path, "guard1", _program(vertical_bar=True, origin=512)))

    assert past == at_rest
