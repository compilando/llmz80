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
    code = (
        "#include <cpctelera.h>\nvoid main(void) {\n    u8 x = 0;\n    cpct_setVideoMode(1);\n}\n"
    )

    fixed, fixes = apply_deterministic_cpc_fixes(code)

    assert fixed.index("u8 x = 0;") < fixed.index("cpct_disableFirmware")
    assert fixed.index("cpct_disableFirmware") < fixed.index("cpct_setVideoMode")
    assert any("cpct_disableFirmware" in fix for fix in fixes)


def test_deterministic_fix_adds_keyboard_scan_before_key_check():
    code = (
        "#include <cpctelera.h>\nvoid main(void) {\n    if (cpct_isKeyPressed(Key_Space)) {}\n}\n"
    )

    fixed, fixes = apply_deterministic_cpc_fixes(code)

    assert fixed.index("cpct_scanKeyboard_f") < fixed.index("cpct_isKeyPressed")
    assert any("cpct_scanKeyboard_f" in fix for fix in fixes)


def test_deterministic_fix_reorders_draw_char_args():
    code = (
        "#include <cpctelera.h>\n"
        "void main(void) {\n"
        "    u8* pvmem;\n"
        "    cpct_drawCharM1('X', pvmem);\n"
        "    cpct_drawCharM1(ch, pvmem);\n"
        "}\n"
    )

    fixed, fixes = apply_deterministic_cpc_fixes(code)

    assert "cpct_drawCharM1(pvmem, 'X')" in fixed
    assert "cpct_drawCharM1(pvmem, ch)" in fixed
    assert any("drawChar" in fix for fix in fixes)


def test_deterministic_draw_char_fix_is_idempotent_for_pointer_first():
    code = """#include <cpctelera.h>
void draw(char ch) {
    u8* pvmem;
    cpct_drawCharM1(pvmem, ch);
}
"""
    fixed, fixes = apply_deterministic_cpc_fixes(code)
    assert "cpct_drawCharM1(pvmem, ch)" in fixed
    assert not any("drawChar" in fix for fix in fixes)


def test_deterministic_fix_replaces_lcg_random_without_entropy():
    code = (
        "#include <cpctelera.h>\n"
        "void main(void) {\n"
        "    cpct_setRandom_lcg_u8();\n"
        "    r = cpct_getRandom_lcg_u8();\n"
        "}\n"
    )

    fixed, fixes = apply_deterministic_cpc_fixes(code)

    assert "cpct_setRandom_lcg_u8" not in fixed
    assert "cpct_getRandom_lcg_u8()" not in fixed
    assert "cpct_getRandom_glfsr16_u8()" in fixed
    assert any("random" in fix for fix in fixes)


def test_deterministic_fix_replaces_invented_get_key_ascii():
    code = """#include <cpctelera.h>
void main(void) {
    u8 key;
    cpct_disableFirmware();
    key = cpct_getKeyASCII();
}
"""

    fixed, fixes = apply_deterministic_cpc_fixes(code)

    assert "cpct_getKeyASCII" not in fixed
    assert "cpct_getKeypressedAsASCII()" in fixed
    assert any("ASCII" in fix for fix in fixes)


def test_deterministic_fix_casts_high_hex_assignment_to_byte_variable():
    code = """#include <cpctelera.h>
static u8 hud_last_lives = (u8)0xFF;
void reset_hud(void) {
    hud_last_lives = 0xFF;
}
"""

    fixed, fixes = apply_deterministic_cpc_fixes(code)

    assert "hud_last_lives = (u8)0xFF;" in fixed
    assert any("high byte constants" in fix for fix in fixes)


def test_deterministic_fix_uses_cpctelera_u8_for_high_macro():
    fixed, _ = apply_deterministic_cpc_fixes("#define SCREEN_H 200\n")
    assert "#define SCREEN_H ((u8)200)" in fixed
    assert "uint8_t" not in fixed


def test_deterministic_fix_removes_warning_357_const_sprite_casts():
    code = """#include <cpctelera.h>
static const u8 spr_iv[16] = {0};
static const u8 spr_ghost[16] = {0};
void main(void) {
    u8* p;
    cpct_drawSprite((void*)spr_iv, p, 2, 8);
    cpct_drawSprite(( void * ) spr_ghost, p, 2, 8);
}
"""
    fixed, fixes = apply_deterministic_cpc_fixes(code)
    assert "cpct_drawSprite(spr_iv, p, 2, 8)" in fixed
    assert "cpct_drawSprite(spr_ghost, p, 2, 8)" in fixed
    assert "(void*)spr" not in fixed
    assert any("warning 357" in fix for fix in fixes)

    second, second_fixes = apply_deterministic_cpc_fixes(fixed)
    assert second == fixed
    assert not any("warning 357" in fix for fix in second_fixes)
