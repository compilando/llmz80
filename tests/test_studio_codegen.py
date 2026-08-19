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


def test_the_config_header_defines_a_constant_per_declared_colour():
    """`plat_ink(COLOUR_LADRILLO)` only compiles if something defines the name.
    The value is target-specific -- an attribute byte on the Spectrum, a pen on
    the CPC -- which is why it is resolved here rather than written by hand into
    a prompt (see `palette.declared_attribute`)."""
    from llmz80.studio.models import PaletteEntry

    project = blank_project("Coloured", TargetPlatform.SPECTRUM)
    project.presentation.palette = [
        PaletteEntry(id="ladrillo", colour="cian"),
        PaletteEntry(id="pala", colour="amarillo brillante"),
    ]

    header = render_config_header(project)

    assert "#define COLOUR_LADRILLO 5" in header
    assert "#define COLOUR_PALA 70" in header


def test_the_same_colours_become_pens_on_the_cpc():
    from llmz80.studio.models import PaletteEntry

    project = blank_project("Coloured", TargetPlatform.AMSTRAD_CPC)
    project.presentation.palette = [PaletteEntry(id="pala", colour="blanco")]

    header = render_config_header(project)

    assert "#define COLOUR_PALA 3" in header


def test_a_colour_whose_prose_names_nothing_is_left_out_rather_than_guessed():
    """A palette entry reading "the colour of a stormy afternoon" resolves to
    no machine colour at all; defining it as white would put a colour nobody
    chose behind the design's own name for it."""
    from llmz80.studio.models import PaletteEntry

    project = blank_project("Vague", TargetPlatform.SPECTRUM)
    project.presentation.palette = [PaletteEntry(id="mood", colour="a stormy afternoon")]

    header = render_config_header(project)

    assert "COLOUR_MOOD" not in header


class TestThePixelRowBound:
    """`MAX_SPRITE_PY` is written down in three places that have to agree.

    The guard inside each `plat_sprite_py`, the macro a program reads, and the
    sentence `acceptance.generation_prompt` puts in front of the model. They
    differ per machine -- 176 on a Spectrum, 184 on a CPC -- and a prompt
    naming the Spectrum's number on a CPC quietly costs eight rows of screen,
    while the reverse tells a program to draw where the guard refuses and
    looks like a broken blitter.
    """

    def test_each_machine_gets_its_own_screen_less_the_sprite(self):
        from llmz80.studio.codegen import max_sprite_py

        assert max_sprite_py(TargetPlatform.SPECTRUM) == 192 - 16
        assert max_sprite_py(TargetPlatform.AMSTRAD_CPC) == 200 - 16

    def test_the_header_carries_it(self):
        from llmz80.studio.codegen import max_sprite_py

        for platform in TargetPlatform:
            header = render_config_header(blank_project("Bound", platform))

            assert f"#define MAX_SPRITE_PY {max_sprite_py(platform)}" in header

    def test_the_library_guard_matches_the_macro(self):
        """Read out of the C, because the C is where it is enforced.

        A guard that drifted from the macro would let a program draw where the
        library then refuses -- the failure mode being a sprite that simply
        never appears, at one edge of the screen, with nothing said.
        """
        from llmz80.studio.codegen import LIBRARY_ROOT, max_sprite_py

        for platform, directory in (
            (TargetPlatform.SPECTRUM, "spectrum"),
            (TargetPlatform.AMSTRAD_CPC, "cpc"),
        ):
            source = (LIBRARY_ROOT / directory / "platform.c").read_text(encoding="utf-8")

            assert f"py > {max_sprite_py(platform)}" in source, directory

    def test_the_writing_prompt_names_the_same_number(self):
        from llmz80.studio.acceptance import generation_prompt
        from llmz80.studio.codegen import max_sprite_py
        from llmz80.studio.models import AssetSpec

        for platform in TargetPlatform:
            project = blank_project("Bound", platform)
            project.assets = [
                AssetSpec(id="hero", kind="sprite", source="assets/hero.png", width=16, height=16)
            ]

            prompt = generation_prompt(project)

            assert "plat_sprite_py" in prompt, platform
            assert f"py runs 0 to {max_sprite_py(platform)}" in prompt, platform
