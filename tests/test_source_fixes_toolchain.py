"""Real-toolchain proof that the build's own rewrites do not break the build.

Added after they did. `compiler.prepare_program_source` applies SDCC's
byte-constant cast to the program before compiling it, and the CPC branch cast
to `u8` -- a CPCtelera typedef. A generated program includes `platform.h` and
`game_config.h`, not `<cpctelera.h>`, so `#define PXMAX 128` became
`#define PXMAX ((u8)128)` naming a type that was not in scope, and the very
next basketball attempt died on

    src/main.c:326: syntax error: token -> '128' ; column 50

A rewrite the compiler never sees is a rewrite nobody tested. The unit tests
for it passed: they called the function and read the string back, and no build
ran. This one builds.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from llmz80.core.state_contract import REQUIRED_SYMBOLS, SYMBOLS_BY_NAME, required_declarations
from llmz80.core.toolchain import resolve_cpct_path
from llmz80.studio.models import TargetPlatform
from llmz80.studio.services import StudioService

zcc_missing = pytest.mark.skipif(shutil.which("zcc") is None, reason="z88dk is not installed")
make_missing = pytest.mark.skipif(shutil.which("make") is None, reason="make is not installed")
cpctelera_missing = pytest.mark.skipif(
    resolve_cpct_path() is None, reason="no set-up CPCtelera was found"
)

CONTRACT_STATE = required_declarations()
CONTRACT_INIT = "".join(
    f"    {name} = 0;\n"
    for name in REQUIRED_SYMBOLS
    if not SYMBOLS_BY_NAME[name].provided_by_library
)

#: A program shaped like the ones Studio really gets: it includes the headers
#: Studio writes and nothing of the toolchain's own, and it defines a byte
#: constant above 127 -- which is the thing the rewrite reaches for.
PROGRAM = f"""#include "platform.h"
#include "game_config.h"

#define PXMAX 128
#define PXMIN 8

{CONTRACT_STATE}
void main(void) {{
    unsigned char rx = 64;
    unsigned char step = 1;
    plat_init();
{CONTRACT_INIT}
    while (1) {{
        rx += step;
        if (rx >= PXMAX) step = 0;
        if (rx <= PXMIN) step = 1;
        plat_wait_frame();
    }}
}}
"""


def _build(tmp_path: Path, platform: TargetPlatform):
    service = StudioService.at(tmp_path / platform.value)
    project, directory = service.create_project("Fixes", platform)
    program_dir = directory / project.program_dir
    program_dir.mkdir(parents=True, exist_ok=True)
    (program_dir / "main.c").write_text(PROGRAM, encoding="utf-8")
    return service.build(project, directory)


@make_missing
@cpctelera_missing
def test_a_cpc_program_survives_the_cast_the_build_adds(tmp_path: Path):
    """The regression itself. `u8` is CPCtelera's; a Studio program has no
    reason to have it in scope."""
    build = _build(tmp_path, TargetPlatform.AMSTRAD_CPC)

    assert build.success, build.report.get("stderr") or build.report.get("stdout")


@zcc_missing
def test_a_spectrum_program_does_too(tmp_path: Path):
    """`uint8_t` is <stdint.h>'s, which a program need not have included
    either."""
    build = _build(tmp_path, TargetPlatform.SPECTRUM)

    assert build.success, build.report.get("stderr") or build.report.get("stdout")


@make_missing
@cpctelera_missing
def test_the_rewrite_is_recorded_in_the_build_report(tmp_path: Path):
    """`prepare_program_source` returns what it changed, and until now nothing
    carried it anywhere: the report read `source_fixes: None` while the build
    was quietly editing the program. A build that rewrites what it was handed
    and does not say so is one whose diagnostics point at lines nobody wrote.
    """
    build = _build(tmp_path, TargetPlatform.AMSTRAD_CPC)

    recorded = build.report.get("source_fixes") or []

    assert any("cast" in note for note in recorded), recorded
    assert any("main.c" in note for note in recorded), recorded


@make_missing
@cpctelera_missing
def test_a_program_needing_nothing_records_nothing(tmp_path: Path):
    service = StudioService.at(tmp_path / "clean")
    project, directory = service.create_project("Clean", TargetPlatform.AMSTRAD_CPC)
    program_dir = directory / project.program_dir
    program_dir.mkdir(parents=True, exist_ok=True)
    (program_dir / "main.c").write_text(
        f"""#include "platform.h"

{CONTRACT_STATE}
void main(void) {{
    plat_init();
{CONTRACT_INIT}
    while (1) {{ plat_wait_frame(); }}
}}
""",
        encoding="utf-8",
    )

    build = service.build(project, directory)

    assert build.success, build.report.get("stderr") or build.report.get("stdout")
    assert not (build.report.get("source_fixes") or [])
