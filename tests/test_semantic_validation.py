from llmz80.core.semantic_validation import (
    SemanticValidator,
    cpc_read_only_pointer_errors,
    constant_range_errors,
    estimate_static_data,
)


ANIMATION_SPEC = {
    "capabilities": ["animation", "sprite"],
    "states": ["running"],
    "timing": {"frame_sync_required": True},
    "budgets": {"static_data_bytes": 32},
}


def test_animation_without_frame_pacing_is_rejected():
    report = SemanticValidator("spectrum", ANIMATION_SPEC).validate(
        "#include <arch/zx.h>\nvoid main(void){while(1){zx_pxy2saddr(8,8);}}"
    )
    assert not report["quality_pass"]
    assert any("frame pacing" in error for error in report["errors"])


def test_certified_frame_and_bounded_coordinate_pass():
    report = SemanticValidator("spectrum", ANIMATION_SPEC).validate(
        "#include <arch/zx.h>\n#include <intrinsic.h>\n"
        "void main(void){while(1){intrinsic_halt();zx_pxy2saddr(8,8);}}"
    )
    assert report["quality_pass"]


def test_out_of_bounds_and_static_budget_are_rejected():
    spec = {"budgets": {"static_data_bytes": 4}}
    code = "u8 data[8]; void main(void){cpct_getScreenPtr(CPCT_VMEM_START,80,200);}"
    report = SemanticValidator("amstrad_cpc", spec).validate(code)
    assert len(report["errors"]) == 2
    assert estimate_static_data(code) == 8


def test_required_end_state_must_be_implemented():
    report = SemanticValidator("spectrum", {"states": ["running", "finished"]}).validate(
        "void main(void){while(1){}}"
    )
    assert any("finished state" in error for error in report["errors"])


def test_prefixed_state_machine_satisfies_required_end_state():
    code = "#define ST_RUNNING 0\n#define ST_FINISHED 1\nstatic u8 g_state = ST_RUNNING;"
    report = SemanticValidator("amstrad_cpc", {"states": ["running", "finished"]}).validate(code)
    assert not any("finished state" in error for error in report["errors"])


def test_cpc_i16_fixed_point_overflow_is_rejected_before_compilation():
    code = """
    #define FP_SHIFT 8
    #define GROUND_Y 192
    void main(void) {
        i16 x_fp, y_fp;
        x_fp = (i16)(160 << FP_SHIFT);
        y_fp = (i16)(GROUND_Y << FP_SHIFT);
    }
    """
    errors = constant_range_errors(code)
    assert any("40960 assigned to i16 x_fp" in error for error in errors)
    assert any("49152 assigned to i16 y_fp" in error for error in errors)


def test_cpc_i16_ten_six_fixed_point_coordinates_fit():
    code = """
    #define FP_SHIFT 6
    #define GROUND_Y 192
    void main(void) {
        i16 x_fp = (i16)(160 << FP_SHIFT);
        i16 y_fp = (i16)(GROUND_Y << FP_SHIFT);
        i16 max_x = (i16)(312 << FP_SHIFT);
    }
    """
    assert constant_range_errors(code) == []


def test_sdcc_u8_high_constant_requires_explicit_checked_cast():
    assert any(
        "warning 158" in error
        for error in constant_range_errors("void main(void){ const u8 y = 200 - 8; }")
    )
    assert constant_range_errors("void main(void){ const u8 y = (u8)(200 - 8); }") == []
    assert any(
        "warning 158" in error
        for error in constant_range_errors("void main(void){ uint8_t y = 160; }")
    )
    assert constant_range_errors("void main(void){ uint8_t y = (uint8_t)160; }") == []


def test_byte_assignment_from_typed_byte_constant_does_not_require_recast():
    code = "void main(void){ const uint8_t top = (uint8_t)160; uint8_t y; y = top; }"
    assert constant_range_errors(code) == []


def test_byte_assignment_from_explicitly_cast_macro_does_not_require_recast():
    code = "#define PLAYER_Y (u8)(200 - 24)\nvoid main(void){ u8 py; py = PLAYER_Y; }"
    assert constant_range_errors(code) == []


def test_cpc_runtime_division_and_modulo_are_rejected():
    code = "void main(void){ u16 v; u8 r; v /= 10; r = r % 79; }"
    report = SemanticValidator("amstrad_cpc").validate(code)
    assert not report["quality_pass"]
    assert any("Runtime division/modulo" in error for error in report["errors"])


def test_cpc_division_characters_in_comments_and_strings_are_ignored():
    code = 'void main(void){ /* no / or % operators */ const char* s = "/%"; }'
    report = SemanticValidator("amstrad_cpc").validate(code)
    assert not any("Runtime division/modulo" in error for error in report["errors"])


def test_required_input_must_have_a_platform_keyboard_read():
    spec = {"capabilities": ["input"]}
    missing = SemanticValidator("amstrad_cpc", spec).validate("void main(void) { while (1) {} }")
    present = SemanticValidator("amstrad_cpc", spec).validate(
        "void main(void) { cpct_scanKeyboard_f(); cpct_isKeyPressed(Key_Space); }"
    )
    assert any("requires input" in error for error in missing["errors"])
    assert not any("requires input" in error for error in present["errors"])


def test_cpc_const_sprite_void_cast_is_rejected_as_warning_357():
    code = """
    static const u8 spr_iv[16] = {0};
    void main(void) {
        u8* p;
        cpct_drawSprite((void*)spr_iv, p, 2, 8);
    }
    """
    errors = cpc_read_only_pointer_errors(code)
    assert len(errors) == 1
    assert "warning 357" in errors[0]
    assert not cpc_read_only_pointer_errors(code.replace("(void*)spr_iv", "spr_iv"))


def test_static_mockup_fails_maze_collect_game_contract():
    spec = {
        "archetype": "maze_collect_game",
        "capabilities": ["animation", "input"],
        "states": ["title", "running", "finished"],
        "timing": {"frame_sync_required": True},
    }
    code = """
    #include <cpctelera.h>
    static const u8 spr_iv[16] = {0};
    void main(void) {
        u8* p;
        cpct_drawSprite((void*)spr_iv, p, 2, 8);
        while (1) { }
    }
    """
    report = SemanticValidator("amstrad_cpc", spec).validate(code)
    assert report["quality_pass"] is False
    assert any("requires input" in error for error in report["errors"])
    assert any("Maze-collect game" in error for error in report["errors"])
    assert any("warning 357" in error for error in report["errors"])


def test_complete_maze_collect_loop_satisfies_semantic_contract():
    spec = {
        "archetype": "maze_collect_game",
        "capabilities": ["animation", "input"],
        "states": ["running", "finished"],
        "timing": {"frame_sync_required": True},
    }
    code = """
    #include <cpctelera.h>
    #define ST_RUNNING 0
    #define ST_FINISHED 1
    static u8 maze[8] = {1, 1, 1, 0, 0, 1, 1, 1};
    static u8 pellets[8] = {0, 0, 0, 1, 1, 0, 0, 0};
    static u8 player_x = 1;
    static u8 player_y = 1;
    static u8 score = 0;
    static u8 g_state = ST_RUNNING;
    static u8 is_wall(u8 x, u8 y) { return maze[x + y] != 0; }
    void main(void) {
        cpct_disableFirmware();
        while (1) {
            cpct_scanKeyboard_f();
            if (cpct_isKeyPressed(Key_CursorRight) && !is_wall(player_x + 1, player_y)) {
                player_x += 1;
                if (pellets[player_x]) { pellets[player_x] = 0; score += 1; }
                if (score == 2) { g_state = ST_FINISHED; }
            }
            cpct_waitVSYNC();
        }
    }
    """
    report = SemanticValidator("amstrad_cpc", spec).validate(code)
    assert report["quality_pass"], report["errors"]
