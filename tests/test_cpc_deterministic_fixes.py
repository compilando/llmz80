"""Tests for safe deterministic CPCtelera fixes."""

from llmz80.utils.helpers import apply_deterministic_cpc_fixes


def test_deterministic_fix_adds_cpctelera_include():
    code = "void main(void) {\n    cpct_disableFirmware();\n}\n"

    fixed, fixes = apply_deterministic_cpc_fixes(code)

    assert fixed.startswith("#include <cpctelera.h>")
    assert any("cpctelera.h" in fix for fix in fixes)


def test_deterministic_fix_adds_disable_firmware_for_hardware_calls():
    code = "#include <cpctelera.h>\nvoid main(void) {\n    cpct_setVideoMode(1);\n}\n"

    fixed, fixes = apply_deterministic_cpc_fixes(code)

    assert "cpct_disableFirmware();" in fixed
    assert fixed.index("cpct_disableFirmware") < fixed.index("cpct_setVideoMode")
    assert any("cpct_disableFirmware" in fix for fix in fixes)


def test_deterministic_fix_preserves_leading_declarations():
    code = "#include <cpctelera.h>\nvoid main(void) {\n    u8 x = 0;\n    cpct_setVideoMode(1);\n}\n"

    fixed, fixes = apply_deterministic_cpc_fixes(code)

    assert fixed.index("u8 x = 0;") < fixed.index("cpct_disableFirmware")
    assert fixed.index("cpct_disableFirmware") < fixed.index("cpct_setVideoMode")
    assert any("cpct_disableFirmware" in fix for fix in fixes)


def test_deterministic_fix_adds_keyboard_scan_before_key_check():
    code = "#include <cpctelera.h>\nvoid main(void) {\n    if (cpct_isKeyPressed(Key_Space)) {}\n}\n"

    fixed, fixes = apply_deterministic_cpc_fixes(code)

    assert fixed.index("cpct_scanKeyboard_f") < fixed.index("cpct_isKeyPressed")
    assert any("cpct_scanKeyboard_f" in fix for fix in fixes)


def test_deterministic_fix_reorders_draw_char_args():
    code = "#include <cpctelera.h>\nvoid main(void) {\n    u8* pvmem;\n    cpct_drawCharM1('X', pvmem);\n    cpct_drawCharM1(ch, pvmem);\n}\n"

    fixed, fixes = apply_deterministic_cpc_fixes(code)

    assert "cpct_drawCharM1(pvmem, 'X')" in fixed
    assert "cpct_drawCharM1(pvmem, ch)" in fixed
    assert any("drawChar" in fix for fix in fixes)


def test_deterministic_fix_replaces_lcg_random_without_entropy():
    code = "#include <cpctelera.h>\nvoid main(void) {\n    cpct_setRandom_lcg_u8();\n    r = cpct_getRandom_lcg_u8();\n}\n"

    fixed, fixes = apply_deterministic_cpc_fixes(code)

    assert "cpct_setRandom_lcg_u8" not in fixed
    assert "cpct_getRandom_lcg_u8()" not in fixed
    assert "cpct_getRandom_glfsr16_u8()" in fixed
    assert any("random" in fix for fix in fixes)
