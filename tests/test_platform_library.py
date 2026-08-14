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
