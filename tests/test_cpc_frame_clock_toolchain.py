"""Real-toolchain proof that the Amstrad CPC now counts frames.

The pacing gate abstained on this machine for as long as it existed, and
honestly: `cpct_disableFirmware()` removes the firmware's interrupt handling
and the CPC has no ROM counter to read the way the Spectrum reads 23672, so
`plat_wait_frame` returned a literal zero. `pacing.pacing_report` said so --
"writing a frame counter for the CPC is real work; until it exists, silence is
the honest reading" -- and refused to read that zero as a game keeping perfect
time, which would have cleared the entire platform on a number nobody computed.

`cpct_setInterruptHandler` is the work. The CPC raises an interrupt 300 times a
second, six per 50 Hz display frame, and counting the sixths is the same
free-running counter the other machine gets for free.

A unit test cannot tell whether that number is a measurement or a constant --
`has_frame_clock` returning True and `game_config.h` saying `HAS_FRAME_CLOCK 1`
would both be equally green if the handler never fired. So this reads the
number back out of a running CPC, from two programs that differ only in whether
they pay a startup cost the loop should not be charged for. If the counter is
dead, both read zero and the first assertion fails.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from llmz80.core.state_contract import REQUIRED_SYMBOLS, SYMBOLS_BY_NAME, required_declarations
from llmz80.core.toolchain import resolve_cpct_path
from llmz80.quality.emulator_smoke import smoke_test
from llmz80.studio.models import TargetPlatform
from llmz80.studio.probes import write_probe_report
from llmz80.studio.services import StudioService

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

#: Iterations of an empty loop that cost more than one display frame and fewer
#: than RESYNC_FRAMES (8), which is the band `plat_wait_frame` reports verbatim.
#: A gap wider than that is forgiven as a resynchronisation and reports 0 until
#: it has repeated SLOW_RUN times, so a fixture outside the band would measure
#: nothing whether the counter worked or not. The exact figure is a timing
#: detail of the emulated machine; the assertion pins the band, not the number.
STARTUP_SPIN = 9000


def _main_c(*, with_baseline: bool) -> str:
    """A program that pays a real startup cost and then keeps perfect time.

    The loop does nothing but wait, so every frame it is charged for is a frame
    the *startup* cost -- which is the whole question the baseline exists for,
    and here doubles as the only way to make the counter say something other
    than zero on purpose.
    """
    baseline = "    plat_frame_baseline();\n" if with_baseline else ""
    return f"""#include "platform.h"

{CONTRACT_STATE}
void main(void) {{
    unsigned int spin;
    plat_init();
{CONTRACT_INIT}
    for (spin = 0; spin < {STARTUP_SPIN}; ++spin) {{
    }}
{baseline}    while (1) {{
        plat_wait_frame();
    }}
}}
"""


def _build(tmp_path: Path, *, with_baseline: bool):
    workspace = tmp_path / ("baselined" if with_baseline else "charged")
    service = StudioService.at(workspace)
    name = "Baselined" if with_baseline else "Charged"
    project, directory = service.create_project(name, TargetPlatform.AMSTRAD_CPC)
    program_dir = directory / project.program_dir
    program_dir.mkdir(parents=True, exist_ok=True)
    (program_dir / "main.c").write_text(_main_c(with_baseline=with_baseline), encoding="utf-8")
    return service.build(project, directory)


def _worst_frame_cost(output_dir: Path) -> int:
    """`g_worst_frame_cost`, read out of the running machine's memory.

    Through `smoke_test` rather than a ZEsarUX invocation of its own: booting a
    CPC is not a one-liner -- a .dsk is not a tape, so the harness waits for a
    BASIC prompt and types `run"program.bin"` at it -- and a second copy of that
    sequence here would drift from the one the runtime gate actually uses.
    """
    probes = write_probe_report(output_dir, "amstrad_cpc")
    assert "g_worst_frame_cost" in probes["addresses"], (
        "the SDCC symbol file does not carry g_worst_frame_cost, so nothing "
        f"below is reading the counter: {probes}"
    )
    report = smoke_test(output_dir, "amstrad_cpc", full=True, seconds=6, probes=probes)
    assert not report.get("emulator_error"), report.get("emulator_error")
    # `probe_before` and `probe_after`, not `step_readings`: the latter is
    # filled per step of an observation script, and this fixture has no
    # bindings to script. The number wanted is a maximum kept for the whole
    # session anyway, so the last read of it is the answer.
    readings = [
        (report.get(key) or {}).get("g_worst_frame_cost") for key in ("probe_before", "probe_after")
    ]
    measured = [value for value in readings if value is not None]
    assert measured, f"the emulator read no g_worst_frame_cost at all: {report}"
    return max(measured)


@make_missing
@cpctelera_missing
def test_the_cpc_platform_library_still_compiles_and_links(tmp_path: Path):
    """The cheap half, so a compile break is not diagnosed through an emulator.

    `cpct_setInterruptHandler` takes a function pointer and CPCtelera's
    prebuilt bindings use the classic stack ABI (`--sdcccall 0`), which is the
    kind of thing that links or does not.
    """
    build = _build(tmp_path, with_baseline=False)

    assert build.success, build.report.get("stderr") or build.report.get("stdout")


@make_missing
@cpctelera_missing
@zesarux_missing
def test_the_counter_charges_a_startup_gap_to_whoever_waits_next(tmp_path: Path):
    """The one that cannot pass with a dead counter.

    A CPC that is not counting reports 0 here however long the spin took, which
    is exactly what it did before `count_frame` existed.
    """
    build = _build(tmp_path, with_baseline=False)
    assert build.success, build.report.get("stderr") or build.report.get("stdout")

    charged = _worst_frame_cost(build.output_dir)

    assert 1 < charged <= 8, (
        f"g_worst_frame_cost read {charged}: the startup spin cost more than one "
        "frame, so a working counter reports it inside the band plat_wait_frame "
        "reports verbatim. Zero means the interrupt handler never fired."
    )


@make_missing
@cpctelera_missing
@zesarux_missing
def test_one_baseline_call_stops_the_loop_being_charged_for_it(tmp_path: Path):
    """And the other direction, so the number above is a measurement of the gap
    rather than of anything that happens to be nonzero."""
    build = _build(tmp_path, with_baseline=True)
    assert build.success, build.report.get("stderr") or build.report.get("stdout")

    assert _worst_frame_cost(build.output_dir) == 0
