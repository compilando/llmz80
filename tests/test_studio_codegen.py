"""game_config.h carries the target's facts and the design's key bindings."""

from llmz80.studio.codegen import render_config_header, render_state_header
from llmz80.studio.models import GameProject, TargetPlatform
from llmz80.studio.samples import blank_project


def test_the_header_states_the_playfield_and_the_mode():
    header = render_config_header(blank_project("Config", TargetPlatform.SPECTRUM))
    assert "#define PLAYFIELD_COLS 32" in header
    assert "#define PLAYFIELD_ROWS 22" in header
    assert "#define HAS_FRAME_CLOCK 1" in header


def test_every_binding_becomes_a_named_bit():
    project = blank_project("Keys", TargetPlatform.SPECTRUM)
    header = render_config_header(project)
    assert "#define INPUT_LEFT 0x01" in header
    bindings = list(project.controls.bindings)
    assert f"#define INPUT_ACTION 0x{1 << bindings.index('action'):02X}" in header


def test_the_binding_list_is_an_x_macro_over_real_scancodes():
    header = render_config_header(blank_project("Keys", TargetPlatform.SPECTRUM))
    assert "#define INPUT_BINDINGS(X)" in header
    assert "X(INPUT_LEFT, IN_KEY_SCANCODE_o)" in header
    assert "X(INPUT_ACTION, IN_KEY_SCANCODE_SPACE)" in header


def test_the_cpc_gets_cpctelera_key_names():
    header = render_config_header(blank_project("Keys", TargetPlatform.AMSTRAD_CPC))
    assert "X(INPUT_LEFT, Key_CursorLeft)" in header
    assert "X(INPUT_ACTION, Key_Space)" in header


def test_a_design_that_coins_its_own_binding_gets_its_own_bit():
    project = blank_project("Jumper", TargetPlatform.SPECTRUM)
    document = project.model_dump(mode="json")
    document["controls"]["bindings"] = {"left": "O", "right": "P", "jump": "SPACE"}
    header = render_config_header(GameProject.model_validate(document))
    assert "#define INPUT_JUMP 0x04" in header
    assert "X(INPUT_JUMP, IN_KEY_SCANCODE_SPACE)" in header


def test_the_design_numbers_its_own_sounds():
    """The library plays effect N; what N is called belongs to the design."""
    project = blank_project("Noisy", TargetPlatform.SPECTRUM)
    document = project.model_dump(mode="json")
    document["audio"]["effects"] = ["dig", "fall"]
    header = render_config_header(GameProject.model_validate(document))
    assert "#define SOUND_DIG 0" in header
    assert "#define SOUND_FALL 1" in header
    assert "#define AUDIO_EFFECT_MASK 3" in header


def test_a_silent_design_declares_no_sound_at_all():
    header = render_config_header(blank_project("Silent", TargetPlatform.SPECTRUM))
    assert "#define AUDIO_EFFECT_MASK 0" in header
    assert "#define SOUND_" not in header


def test_the_hud_rows_come_from_the_design():
    project = blank_project("Hud", TargetPlatform.SPECTRUM)
    document = project.model_dump(mode="json")
    document["presentation"]["hud_rows"] = 0
    header = render_config_header(GameProject.model_validate(document))
    assert "#define FIELD_TOP 0" in header
    assert "#define PLAYFIELD_ROWS 24" in header


def test_the_state_header_declares_the_designs_own_observables():
    project = blank_project("Observed", TargetPlatform.SPECTRUM)
    document = project.model_dump(mode="json")
    document["observables"] = [{"symbol": "g_keys", "width": 1, "meaning": "llaves"}]
    header = render_state_header(GameProject.model_validate(document))
    assert "extern unsigned char g_keys;" in header
    assert "extern unsigned int g_score;" in header
