"""The platform library stops naming five keys, five sounds and four shapes."""

from pathlib import Path

LIB = Path(__file__).resolve().parents[1] / "resources" / "studio_lib"


def test_the_header_no_longer_fixes_five_inputs_and_five_cell_kinds():
    header = (LIB / "common" / "platform.h").read_text(encoding="utf-8")
    for gone in ("IN_LEFT", "IN_ACTION", "CELL_PLAYER", "CELL_WALL",
                 "SOUND_START", "SOUND_COLLECT"):
        assert gone not in header, f"{gone} survives in platform.h"


def test_the_header_declares_plat_cell_as_a_character():
    header = (LIB / "common" / "platform.h").read_text(encoding="utf-8")
    assert "void plat_cell(unsigned char col, unsigned char row, char glyph);" in header


def test_both_targets_read_input_through_the_generated_binding_list():
    for target in ("spectrum", "cpc"):
        source = (LIB / target / "platform.c").read_text(encoding="utf-8")
        assert "INPUT_BINDINGS(X)" in source, target
        assert "#undef X" in source, target


def test_no_hardcoded_actor_shapes_remain():
    source = (LIB / "spectrum" / "platform.c").read_text(encoding="utf-8")
    for gone in ("shape_player", "shape_enemy", "shape_item", "shape_wall"):
        assert gone not in source, f"{gone} survives in the Spectrum library"


def test_sounds_are_dispatched_by_index_not_by_a_fixed_name():
    source = (LIB / "spectrum" / "platform.c").read_text(encoding="utf-8")
    assert "SOUND_COLLECT" not in source
    assert "case 0:" in source


def test_the_spectrum_wait_refuses_to_bill_an_absent_loop_as_a_slow_one():
    """A loop that never calls the wait -- my-retro-game's title screen polls
    the action key without pacing itself -- leaves a gap of dozens of frames
    that the next wait would otherwise charge to a single iteration. That made
    a program whose loop ran in about three frames report 38 missed ones, and
    the pacing gate failed it. The library cannot tell a slow iteration from an
    absent one, so beyond a plausibility bound it reports nothing rather than
    reporting the wrong thing.
    """
    source = (LIB / "spectrum" / "platform.c").read_text(encoding="utf-8")
    assert "#define RESYNC_FRAMES" in source
    assert "if (cost > RESYNC_FRAMES) {" in source, "the plausibility bound is not applied"
