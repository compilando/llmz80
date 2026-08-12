from pathlib import Path
import shutil
import subprocess

import pytest

from llm_z80 import prepare_amstrad_cpc_build_project, resolve_cpct_path
from llmz80.core.runtime_contracts import archetype_contract, runtime_contract
from llmz80.core.state_contract import PROBE_WIDTHS, SYMBOLS_BY_NAME, contract_prompt
from llmz80.utils.helpers import apply_deterministic_cpc_fixes


def test_all_generation_archetypes_have_loop_and_primitives():
    for name in (
        "static_display", "animation", "collect_game", "maze_collect_game", "platform_movement",
        "board_game", "scrolling_scene", "arcade",
    ):
        contract = archetype_contract(name)
        assert contract["loop"]
        assert contract["required_primitives"]


def test_the_contract_carries_an_animation_frame():
    assert "g_anim_frame" in SYMBOLS_BY_NAME
    assert SYMBOLS_BY_NAME["g_anim_frame"].required is False
    assert PROBE_WIDTHS["g_anim_frame"] == 1


def test_the_prompt_explains_when_the_animation_frame_must_change():
    text = contract_prompt()

    assert "g_anim_frame" in text
    assert "moves" in text


@pytest.mark.skipif(shutil.which("zcc") is None, reason="Z88DK is not installed")
def test_spectrum_runtime_compiles(tmp_path):
    header = runtime_contract("spectrum")
    (tmp_path / "main.c").write_text(
        header + "\nstatic const unsigned char dot[8]={24,60,126,255,126,60,24,0};\n"
        "void main(void){zx_cls(PAPER_BLACK|INK_WHITE);llmz80_draw_sprite8(8,8,dot);"
        "llmz80_wait_frame();while(1){}}\n", encoding="utf-8")
    result = subprocess.run([
        "zcc", "+zx", "-vn", "-O3", "-clib=sdcc_iy", "main.c", "-o", "output",
        "-create-app", "-subtype=default",
    ], cwd=tmp_path, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "output.tap").stat().st_size > 0


@pytest.mark.skipif(shutil.which("make") is None, reason="make is not installed")
def test_cpc_runtime_compiles(tmp_path):
    cpct_path = resolve_cpct_path()
    if cpct_path is None:
        pytest.skip("CPCtelera is not installed")
    header = runtime_contract("amstrad_cpc")
    (tmp_path / "main.c").write_text(
        header + "\nstatic const u8 dot[2]={0xFF,0xFF};\n"
        "void main(void){cpct_disableFirmware();cpct_setVideoMode(1);"
        "llmz80_scan_input();llmz80_draw_sprite(1,1,dot,1,2);llmz80_wait_frame();"
        "while(1){}}\n", encoding="utf-8")
    assert prepare_amstrad_cpc_build_project(tmp_path, cpct_path)
    result = subprocess.run(["make", f"CPCT_PATH={cpct_path}/"], cwd=tmp_path,
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.skipif(shutil.which("make") is None, reason="make is not installed")
def test_warning_357_sprite_fixture_is_fixed_and_compiles_cleanly(tmp_path):
    cpct_path = resolve_cpct_path()
    if cpct_path is None:
        pytest.skip("CPCtelera is not installed")
    source = """#include <cpctelera.h>
static const u8 spr_iv[16] = {0};
static const u8 spr_ghost[16] = {0};
void main(void) {
    u8* p;
    cpct_disableFirmware();
    cpct_setVideoMode(1);
    p = cpct_getScreenPtr(CPCT_VMEM_START, 8, 100);
    cpct_drawSprite((void*)spr_iv, p, 2, 8);
    cpct_drawSprite((void*)spr_ghost, p, 2, 8);
    while (1) { }
}
"""
    fixed, fixes = apply_deterministic_cpc_fixes(source)
    assert any("warning 357" in fix for fix in fixes)
    (tmp_path / "main.c").write_text(fixed, encoding="utf-8")
    assert prepare_amstrad_cpc_build_project(tmp_path, cpct_path)
    result = subprocess.run(
        ["make", f"CPCT_PATH={cpct_path}/"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "warning 357" not in output
