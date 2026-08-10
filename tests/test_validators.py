"""Tests for pre-compilation validators."""

from llmz80.core.validators import CodeValidator


def test_validator_rejects_local_includes_for_single_file_output():
    code = '#include "sprites.h"\nvoid main(void) {}\n'

    result = CodeValidator("spectrum").validate(code)

    assert not result.is_valid
    assert any("Include local prohibido" in error for error in result.errors)


def test_amstrad_validator_rejects_unknown_cpct_function():
    code = """#include <cpctelera.h>

void main(void) {
    cpct_disableFirmware();
    cpct_madeUpFunction();
}
"""

    result = CodeValidator("amstrad_cpc").validate(code)

    assert not result.is_valid
    assert any("cpct_madeUpFunction" in error for error in result.errors)


def test_amstrad_validator_accepts_real_get_key_ascii_without_args():
    code = """#include <cpctelera.h>

void main(void) {
    u8 ascii;
    cpct_disableFirmware();
    ascii = cpct_getKeypressedAsASCII();
}
"""

    result = CodeValidator("amstrad_cpc").validate(code)

    assert result.is_valid


def test_amstrad_validator_rejects_invented_get_key_ascii():
    code = """#include <cpctelera.h>
void main(void) {
    u8 ascii;
    cpct_disableFirmware();
    ascii = cpct_getKeyASCII();
}
"""

    result = CodeValidator("amstrad_cpc").validate(code)

    assert not result.is_valid
    assert any("cpct_getKeyASCII" in error for error in result.errors)


def test_amstrad_validator_rejects_px2byte_m2():
    code = """#include <cpctelera.h>

void main(void) {
    cpct_disableFirmware();
    cpct_setVideoMode(2);
    cpct_px2byteM2(1, 0);
}
"""

    result = CodeValidator("amstrad_cpc").validate(code)

    assert not result.is_valid
    assert any("cpct_px2byteM2" in error for error in result.errors)


def test_amstrad_validator_requires_keyboard_scan_before_key_check():
    code = """#include <cpctelera.h>

void main(void) {
    cpct_disableFirmware();
    if (cpct_isKeyPressed(Key_Space)) {}
}
"""

    result = CodeValidator("amstrad_cpc").validate(code)

    assert not result.is_valid
    assert any("cpct_scanKeyboard" in error for error in result.errors)


def test_amstrad_validator_requires_disable_firmware_first_call():
    code = """#include <cpctelera.h>

void main(void) {
    cpct_setVideoMode(1);
    cpct_disableFirmware();
}
"""

    result = CodeValidator("amstrad_cpc").validate(code)

    assert not result.is_valid
    assert any("primera llamada ejecutable" in error for error in result.errors)


def test_syntax_validator_ignores_parentheses_in_comments():
    code = """#include <cpctelera.h>
// ((((((
void main(void) {
    cpct_disableFirmware();
}
"""

    result = CodeValidator("amstrad_cpc").validate(code)

    assert result.is_valid
    assert not any("Paréntesis desbalanceados" in error for error in result.errors)


def test_syntax_validator_does_not_warn_on_control_flow_without_braces():
    code = """#include <cpctelera.h>
static u8 turn; // 1=X (red), 2=O (cyan)

void main(void) {
    cpct_disableFirmware();
    if (turn)
        return;
}
"""

    result = CodeValidator("amstrad_cpc").validate(code)

    assert result.is_valid
    assert not any("puede necesitar punto y coma" in warning for warning in result.warnings)


def test_amstrad_validator_allows_disable_firmware_after_declarations_and_comments():
    code = """#include <cpctelera.h>

void main(void) {
    // Key edge detection states (declared before statements)
    u8 prevR = 0;

    cpct_disableFirmware();
    cpct_setVideoMode(1);
}
"""

    result = CodeValidator("amstrad_cpc").validate(code)

    assert result.is_valid


def test_amstrad_validator_rejects_draw_char_argument_order_from_old_prompt():
    code = """#include <cpctelera.h>

void main(void) {
    u8* pvmem;
    cpct_disableFirmware();
    cpct_setVideoMode(1);
    pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 0, 0);
    cpct_drawCharM1('X', pvmem);
}
"""

    result = CodeValidator("amstrad_cpc").validate(code)

    assert not result.is_valid
    assert any("cpct_drawCharM1" in error and "memoria como primer argumento" in error for error in result.errors)


def test_amstrad_validator_rejects_lcg_random_without_entropy():
    code = """#include <cpctelera.h>

void main(void) {
    u8 r;
    cpct_disableFirmware();
    r = cpct_getRandom_lcg_u8();
}
"""

    result = CodeValidator("amstrad_cpc").validate(code)

    assert not result.is_valid
    assert any("cpct_getRandom_lcg_u8" in error and "0 argumentos" in error for error in result.errors)


def test_spectrum_validator_rejects_nonexistent_zx_plot():
    code = """#include <arch/zx.h>
void main(void) {
    zx_plot(10, 10, 1);
}
"""

    result = CodeValidator("spectrum").validate(code)

    assert not result.is_valid
    assert any("zx_plot" in error and "no existe" in error for error in result.errors)


def test_spectrum_validator_rejects_uppercase_qaop_scancode():
    code = """#include <arch/zx.h>
#include <input.h>
void main(void) {
    if (in_key_pressed(IN_KEY_SCANCODE_Q)) { }
}
"""

    result = CodeValidator("spectrum").validate(code)

    assert not result.is_valid
    assert any("IN_KEY_SCANCODE_Q" in error for error in result.errors)


def test_amstrad_validator_counts_casted_call_arguments():
    code = """#include <cpctelera.h>

void main(void) {
    u8* p;
    cpct_disableFirmware();
    p = cpct_getScreenPtr(CPCT_VMEM_START, (GRID_X_PX >> 2), (u8)(GRID_Y_PX + 16));
}
"""

    result = CodeValidator("amstrad_cpc").validate(code)

    assert result.is_valid
