"""`tiles.h` and `tiles.c`: the two halves of a project's terrain artwork.

Shaped after `sprites.h`/`sprites.c` (see `test_sprite_header.py`) and for the
same reasons -- declarations in the header because both `platform.c` and the
program include it, definitions in one `.c` so the pixels are stored once --
but a tile is simpler than a sprite: no frames, no mask, no offset table.
"""

import pytest

from llmz80.studio.spriting import PackedTile
from llmz80.studio.tile_header import render_tile_header, render_tile_source


def _tile(byte: int = 0xFF, *, attribute: int = 0x47, width_bytes: int = 1) -> PackedTile:
    return PackedTile(bytes([byte] * 8 * width_bytes), width_bytes, attribute=attribute)


def test_the_header_numbers_each_tile_in_insertion_order():
    header = render_tile_header({"wall": _tile(), "ladrillo": _tile()})

    assert "#define TILE_WALL 0" in header
    assert "#define TILE_LADRILLO 1" in header
    assert "#define TILE_COUNT 2" in header


def test_the_header_declares_the_tables_without_defining_them():
    """Included by both platform.c and main.c, so a definition here would make
    the linker see two of everything -- the same rule sprites.h follows."""
    header = render_tile_header({"wall": _tile()})

    assert "extern const unsigned char *const tile_data[];" in header
    assert "extern const unsigned char tile_attribute[];" in header
    assert "static const unsigned char" not in header


def test_the_header_publishes_the_row_width_the_blitter_must_step_by():
    header = render_tile_header({"wall": _tile(width_bytes=2)})

    assert "#define TILE_BYTES_WIDE 2" in header
    assert "#define TILE_HEIGHT 8" in header


def test_a_project_with_no_tile_art_still_gets_a_valid_header():
    """platform.c includes tiles.h unconditionally (that is where plat_tile
    lives), so a design that declared no artwork must still compile."""
    header = render_tile_header({})

    assert "#define TILE_COUNT 0" in header
    assert "extern const unsigned char *const tile_data[];" not in header


def test_the_source_defines_the_bytes_and_the_pointer_table():
    source = render_tile_source({"wall": _tile(byte=0x81)})

    assert "static const unsigned char tile_wall_data[] = {" in source
    assert "0x81" in source
    assert "const unsigned char *const tile_data[] = { tile_wall_data };" in source


def test_the_source_carries_each_tiles_attribute_byte():
    source = render_tile_source({"wall": _tile(attribute=0x45), "floor": _tile(attribute=0x02)})

    assert "const unsigned char tile_attribute[] = {69, 2};" in source


def test_a_source_with_no_tile_art_is_not_an_empty_translation_unit():
    """z88dk warns on an empty translation unit and Studio's build policy
    treats a warning from its own generated source as build-breaking -- the
    same trap `sprites.c` documents."""
    source = render_tile_source({})

    assert "typedef" in source


def test_tiles_packed_for_different_modes_cannot_share_a_header():
    """TILE_BYTES_WIDE can hold one value, so a header mixing a Spectrum tile
    with a CPC one would be a lie for whichever it does not match."""
    with pytest.raises(ValueError, match="width_bytes"):
        render_tile_header({"wall": _tile(width_bytes=1), "floor": _tile(width_bytes=2)})


def test_a_tile_id_that_is_not_a_c_identifier_is_refused():
    with pytest.raises(ValueError, match="not a valid C identifier"):
        render_tile_header({"la-pared": _tile()})
