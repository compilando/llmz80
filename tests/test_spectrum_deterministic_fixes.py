"""Tests for safe, header-verified Spectrum fixes."""

from llmz80.utils.helpers import apply_deterministic_spectrum_fixes


def test_spectrum_fix_normalises_qaop_scancodes_only():
    code = """#include <input.h>
void main(void) {
    if (in_key_pressed(IN_KEY_SCANCODE_Q)) { }
    if (in_key_pressed(IN_KEY_SCANCODE_SPACE)) { }
}
"""

    fixed, fixes = apply_deterministic_spectrum_fixes(code)

    assert "IN_KEY_SCANCODE_q" in fixed
    assert "IN_KEY_SCANCODE_Q" not in fixed
    assert "IN_KEY_SCANCODE_SPACE" in fixed
    assert fixes


def test_spectrum_fix_casts_high_byte_constants_for_sdcc():
    code = """#include <stdint.h>
#define PADDLE_Y 176
#define SCREEN_W 256
static uint8_t ball_y = 160;
"""
    fixed, fixes = apply_deterministic_spectrum_fixes(code)
    assert "#define PADDLE_Y ((uint8_t)176)" in fixed
    assert "#define SCREEN_W 256" in fixed
    assert "static uint8_t ball_y = (uint8_t)160;" in fixed
    assert any("high byte constants" in fix for fix in fixes)
