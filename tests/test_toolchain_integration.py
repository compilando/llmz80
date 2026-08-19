"""Small real-toolchain contract tests (skipped when SDKs are unavailable)."""

import shutil
import subprocess

import pytest

from llmz80.core.build_quality import classify_build_warnings
from llmz80.core.toolchain import prepare_amstrad_cpc_build_project, resolve_cpct_path


@pytest.mark.skipif(shutil.which("zcc") is None, reason="Z88DK is not installed")
def test_minimal_spectrum_contract_builds_tap(tmp_path):
    source = tmp_path / "main.c"
    source.write_text(
        """#include <arch/zx.h>
#include <stdio.h>
void main(void) {
    zx_cls(PAPER_BLACK | INK_WHITE);
    printf("OK\\n");
    while (1) { }
}
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "zcc",
            "+zx",
            "-vn",
            "-O3",
            "-clib=sdcc_iy",
            "main.c",
            "-o",
            "output",
            "-create-app",
            "-subtype=default",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "output.tap").stat().st_size > 0
    warnings = classify_build_warnings(result.stdout + "\n" + result.stderr)
    assert warnings["structural"] == []


@pytest.mark.skipif(shutil.which("make") is None, reason="make is not installed")
def test_minimal_cpc_contract_builds_dsk(tmp_path):
    cpct_path = resolve_cpct_path()
    if cpct_path is None:
        pytest.skip("CPCtelera is not installed")

    (tmp_path / "main.c").write_text(
        """#include <cpctelera.h>
void main(void) {
    cpct_disableFirmware();
    cpct_setVideoMode(1);
    cpct_clearScreen(0x00);
    while (1) { }
}
""",
        encoding="utf-8",
    )
    assert prepare_amstrad_cpc_build_project(tmp_path, cpct_path)

    result = subprocess.run(
        ["make", f"CPCT_PATH={cpct_path}/"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert any(path.stat().st_size > 0 for path in tmp_path.glob("*.dsk"))
    build_config = (tmp_path / "cfg" / "build_config.mk").read_text(encoding="utf-8")
    assert "Z80CCFLAGS    := --sdcccall 0" in build_config
    assembly = (tmp_path / "obj" / "main.asm").read_text(encoding="utf-8")
    clear_screen_call = assembly.index("call\t_cpct_memset")
    # ABI 0 must push the 0xC000 video-memory pointer before CPCtelera pops it.
    assert "push\thl" in assembly[max(0, clear_screen_call - 250) : clear_screen_call]
