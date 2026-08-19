"""Real-toolchain proof that building a screen is not a slow game loop.

The defect, measured: `plat_wait_frame` records the worst gap it ever sees in
`g_worst_frame_cost`, and the gap between "the title screen is waiting for a
key" (or "two hundred cells of terrain artwork are being drawn") and the first
iteration of the game loop is not an iteration of anything. `platform.h` has
always told a program to "call plat_wait_frame once as you leave such a loop
and ignore what it returns" -- but ignoring the *return value* does not undo
the write to `g_worst_frame_cost`, so the gesture the contract asks for cannot
work, and the number stays high for the rest of the session because it is a
maximum.

Ten consecutive program attempts across two runs failed the pacing gate this
way, every one of them reading its worst cost at the step where the title
screen handed over to the game and never at any later step. This is the call
that gives the contract's own advice an effect: `plat_frame_baseline` starts
the measurement afresh without charging anybody for the gap it closes.

Read back out of the machine rather than argued about: two programs, one that
draws a deliberately slow screen and calls the baseline before its loop, one
that draws the same screen and does not.
"""

from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path

import pytest

from llmz80.core.state_contract import REQUIRED_SYMBOLS, SYMBOLS_BY_NAME, required_declarations
from llmz80.studio.models import TargetPlatform
from llmz80.studio.services import StudioService
from tests.test_sprite_blitter_toolchain import _connect_zrcp, _free_local_port, _zrcp_query

zcc_missing = pytest.mark.skipif(shutil.which("zcc") is None, reason="z88dk is not installed")
zesarux_missing = pytest.mark.skipif(
    shutil.which("zesarux") is None, reason="ZEsarUX is not installed"
)

CONTRACT_STATE = required_declarations()
CONTRACT_INIT = "".join(
    f"    {name} = 0;\n"
    for name in REQUIRED_SYMBOLS
    if not SYMBOLS_BY_NAME[name].provided_by_library
)

#: Iterations of an empty loop that add up to a gap inside the band the library
#: really reports. `plat_wait_frame` forgives a gap wider than RESYNC_FRAMES (8)
#: as a resynchronisation and reports one of 2 to 8 verbatim, so a fixture has to
#: land inside that band to exercise the defect at all -- the first version of
#: this test painted 960 character cells, which cost less than one frame, and
#: measured 0 without the fix. Calibrated against the real machine (see the
#: assertion in the first test, which pins the gap to the band rather than to a
#: particular number, since the exact figure is an emulator timing detail).
STARTUP_SPIN = 12000


def _main_c(*, with_baseline: bool, spin: int = STARTUP_SPIN) -> str:
    """A program that pays a real startup cost and then keeps perfect time.

    The loop after it does nothing but wait, so every frame it is charged for is
    a frame the *startup* work cost -- which is the whole question here.
    """
    baseline = "    plat_frame_baseline();\n" if with_baseline else ""
    return f"""#include "platform.h"

{CONTRACT_STATE}
void main(void) {{
    unsigned int spin;
    plat_init();
{CONTRACT_INIT}
    /* Stands in for the work between plat_init and the first iteration of the
     * game loop: painting a screen, waiting for a key on a title screen,
     * building a level. Whatever it is, it is not an iteration of the loop that
     * follows, and the gap it leaves is what plat_wait_frame charges to
     * whoever calls next. */
    for (spin = 0; spin < {spin}; ++spin) {{
    }}
{baseline}    while (1) {{
        plat_wait_frame();
    }}
}}
"""


def _build(tmp_path: Path, *, with_baseline: bool, spin: int = STARTUP_SPIN):
    workspace = tmp_path / "projects"
    service = StudioService.at(workspace)
    name = "Baselined" if with_baseline else "Charged"
    project, directory = service.create_project(name, TargetPlatform.SPECTRUM)
    program_dir = directory / project.program_dir
    program_dir.mkdir(parents=True, exist_ok=True)
    (program_dir / "main.c").write_text(
        _main_c(with_baseline=with_baseline, spin=spin), encoding="utf-8"
    )
    return service.build(project, directory)


def _worst_frame_cost(artifact: Path, output_dir: Path) -> int:
    """`g_worst_frame_cost`, read out of the running machine's memory."""
    address = None
    for line in (
        (output_dir / "output.map").read_text(encoding="utf-8", errors="ignore").splitlines()
    ):
        if "_g_worst_frame_cost" in line:
            for token in line.split():
                if token.startswith("$"):
                    address = int(token[1:].split(";")[0], 16)
                    break
            if address is not None:
                break
    assert address is not None, "the linker map does not carry g_worst_frame_cost"

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
            "20",
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
            time.sleep(5.0)
            _zrcp_query(connection, "get-version")
            answer = _zrcp_query(connection, f"read-memory {address} 1")
            digits = "".join(
                ch for ch in answer.split("command@")[0] if ch in "0123456789abcdefABCDEF"
            )[:2]
            assert len(digits) == 2, f"no memory read back for {address:#06x}: {answer!r}"
            return int(digits, 16)
    finally:
        process.terminate()
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate(timeout=5)


@zcc_missing
@zesarux_missing
def test_a_screen_drawn_before_the_loop_is_charged_to_the_loop_without_a_baseline(
    tmp_path: Path,
):
    """The defect itself, so the fix below is measured against a real number
    rather than against an assumption about one."""
    build = _build(tmp_path, with_baseline=False)
    assert build.success, build.report.get("stderr") or build.report.get("stdout")

    charged = _worst_frame_cost(build.artifact, build.output_dir)
    # Inside the band the library reports verbatim: above 1 (which is what the
    # pacing gate accepts) and no wider than RESYNC_FRAMES, past which a gap is
    # forgiven as a resynchronisation instead. Pinned as a band rather than a
    # number because the exact figure is an emulator timing detail.
    assert 1 < charged <= 8, charged


@zcc_missing
@zesarux_missing
def test_the_same_program_keeps_a_clean_frame_cost_after_a_baseline(tmp_path: Path):
    """One call, and the loop is judged on what the loop actually costs. The
    loop here does nothing but wait, so anything above zero is startup work
    being charged to it."""
    build = _build(tmp_path, with_baseline=True)
    assert build.success, build.report.get("stderr") or build.report.get("stdout")

    assert _worst_frame_cost(build.artifact, build.output_dir) == 0
