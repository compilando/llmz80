"""The generated header and source, judged as text a compiler will read.

`sprites.h` is included by two translation units (`platform.c` and the
program's `main.c`), so it must carry `#define`s and `extern` declarations
only -- never a definition with a body, or two translation units each define
`sprite_data[]` and the like, and the linker refuses to link
(`error: duplicate definition: main_c::_sprite_data`). `sprites.c` is where
those tables actually live, compiled exactly once.
"""

import pytest
from PIL import Image

from llmz80.studio.sprite_header import render_sprite_header, render_sprite_source
from llmz80.studio.spriting import PackedSprite, pack_spectrum


def _packed(frames: int = 2, width_bytes: int = 2) -> PackedSprite:
    """A Spectrum-shaped sprite: data and mask are separate, equal-sized arrays."""
    return PackedSprite(
        bytes(width_bytes * 16 * frames), bytes(width_bytes * 16 * frames), width_bytes, 16, frames
    )


def _cpc_packed(frames: int = 2, width_bytes: int = 8) -> PackedSprite:
    """A CPC-shaped sprite: `mask` is empty, `data` carries interleaved mask+colour bytes."""
    return PackedSprite(bytes(2 * width_bytes * 16 * frames), b"", width_bytes, 16, frames)


def test_the_header_names_every_sprite_and_its_frames():
    text = render_sprite_header({"hero": _packed(2), "enemy": _packed(1)})

    assert "#define SPRITE_HERO 0" in text
    assert "#define SPRITE_ENEMY 1" in text
    assert "#define SPRITE_COUNT 2" in text
    assert "sprite_frames[]" in text


def test_the_header_compiles_as_declarations_only_once():
    text = render_sprite_header({"hero": _packed(1)})

    assert text.count("#ifndef LLMZ80_SPRITES_H") == 1
    assert "#endif" in text


def test_an_empty_set_still_produces_a_valid_header():
    """A project with no artwork must still compile; the library falls back to shapes."""
    text = render_sprite_header({})

    assert "#define SPRITE_COUNT 0" in text


def test_the_bytes_wide_macro_reflects_the_packed_width():
    text = render_sprite_header({"hero": _packed(1, width_bytes=2)})
    assert "#define SPRITE_BYTES_WIDE 2" in text

    text = render_sprite_header({"hero": _cpc_packed(1, width_bytes=8)})
    assert "#define SPRITE_BYTES_WIDE 8" in text


def test_indices_follow_dictionary_order_not_alphabetical_order():
    text = render_sprite_header({"zebra": _packed(1), "alpha": _packed(1)})

    assert "#define SPRITE_ZEBRA 0" in text
    assert "#define SPRITE_ALPHA 1" in text


def test_mismatched_width_bytes_across_sprites_is_rejected():
    """SPRITE_BYTES_WIDE is a single, global macro; sprites packed for different
    modes (or different platforms) cannot coexist in one header."""
    with pytest.raises(ValueError, match="width_bytes"):
        render_sprite_header(
            {"hero": _packed(1, width_bytes=2), "enemy": _cpc_packed(1, width_bytes=8)}
        )


def test_a_sprite_id_that_is_not_a_valid_c_identifier_is_rejected():
    with pytest.raises(ValueError, match="identifier"):
        render_sprite_header({"my-hero": _packed(1)})


# ---------------------------------------------------------------------------
# The header carries no definitions: this is the property the whole split
# exists to guarantee, so it is pinned directly rather than only implied by
# the tests above.
# ---------------------------------------------------------------------------


def test_the_header_declares_the_tables_extern_and_defines_nothing():
    text = render_sprite_header({"hero": _packed(2), "enemy": _packed(1)})

    for table in (
        "sprite_data",
        "sprite_mask",
        "sprite_frame_offset",
        "sprite_frames",
        "sprite_attribute",
    ):
        assert (
            f"extern const unsigned char *const {table}[]" in text
            or (f"extern const unsigned int {table}" in text)
            or f"extern const unsigned char {table}[]" in text
        ), table
    # None of the byte data itself, nor any array initialiser, appears in the
    # header -- those live in sprites.c only.
    assert "0x" not in text
    assert "= {" not in text
    assert "static" not in text


def test_an_empty_set_header_has_no_extern_block_at_all():
    """With SPRITE_COUNT 0 there is nothing to declare -- no #if SPRITE_COUNT
    block, no externs -- the same shape render_sprite_source produces for the
    same input (see test_an_empty_source_is_just_the_include below)."""
    text = render_sprite_header({})

    assert "extern" not in text
    assert "#if SPRITE_COUNT" not in text


# ---------------------------------------------------------------------------
# sprites.c: the one place the tables are actually defined.
# ---------------------------------------------------------------------------


def test_the_source_includes_the_header_and_defines_the_tables():
    text = render_sprite_source({"hero": _packed(2), "enemy": _packed(1)})

    assert '#include "sprites.h"' in text
    assert "const unsigned char *const sprite_data[] = {" in text
    assert "const unsigned char *const sprite_mask[] = {" in text
    assert "const unsigned int sprite_frame_offset[][" in text
    assert "const unsigned char sprite_frames[] = " in text
    assert "const unsigned char sprite_attribute[] = " in text


def test_an_empty_source_is_just_the_include_and_a_placeholder():
    """No sprites means no `#if SPRITE_COUNT` block and no sprite tables --
    but the file still needs one real declaration. A file holding only an
    `#include` is, to a strict C compiler, an empty translation unit, and
    z88dk's cc1 warns about exactly that ("ISO C forbids an empty
    translation unit"); Studio's build policy fails a build on any warning
    from its own generated sources, so this is a real build-breaking case,
    not a cosmetic one."""
    text = render_sprite_source({})

    assert '#include "sprites.h"' in text
    assert "#if SPRITE_COUNT" not in text
    assert "sprite_data" not in text
    assert "typedef int" in text


def test_sprite_frames_records_each_sprites_own_count():
    text = render_sprite_source({"hero": _packed(3), "enemy": _packed(1)})

    # dict order is hero=0, enemy=1; frame counts 3 and 1 respectively.
    assert "sprite_frames[] = {3, 1}" in text.replace("\n", " ").replace("  ", " ")


def test_frame_offset_on_the_spectrum_is_plain_frame_times_bytes_per_frame():
    """Spectrum data/mask are independent arrays, one bytes_per_frame chunk each."""
    packed = _packed(frames=3, width_bytes=2)  # bytes_per_frame = 2 * 16 = 32
    text = render_sprite_source({"hero": packed})

    assert "{0, 32, 64}" in text.replace("\n", " ")


def test_frame_offset_on_the_cpc_accounts_for_the_interleaved_mask():
    """CPC frames are twice `width_bytes * height` long in `data` because the mask
    rides along interleaved with the colour bytes. `PackedSprite.bytes_per_frame`
    already reports that true, doubled stride (it is interleaving-aware), so the
    offset table is just frame index times `bytes_per_frame` -- same formula as
    the Spectrum test above, only the value differs because the stride does."""
    packed = _cpc_packed(frames=3, width_bytes=8)  # bytes_per_frame = 2 * 8*16 = 256
    text = render_sprite_source({"hero": packed})

    assert "{0, 256, 512}" in text.replace("\n", " ")


def test_ragged_frame_counts_still_produce_a_rectangular_array():
    """C requires a rectangular 2D array; the short sprite's row is padded so both
    rows have the same number of columns, and the padding repeats the last real
    offset so an out-of-range read (a bug elsewhere) still lands in-bounds."""
    text = render_sprite_source(
        {"hero": _packed(3, width_bytes=2), "enemy": _packed(1, width_bytes=2)}
    )

    squeezed = text.replace("\n", " ")
    assert "{0, 32, 64}" in squeezed  # hero: three real frames
    assert "{0, 0, 0}" in squeezed  # enemy: one real frame, padded by repeating offset 0


def test_cpc_mask_pointers_alias_the_data_pointers():
    """On the CPC the mask travels interleaved inside `data`, so `sprite_mask[]`
    must point at the very same bytes as `sprite_data[]`, not at a separate array."""
    text = render_sprite_source({"hero": _cpc_packed(1)})

    assert "sprite_mask" in text
    # No second byte array should be emitted for the mask on this target.
    assert text.count("sprite_hero_data[]") == 1
    assert "sprite_hero_mask[]" not in text


def test_spectrum_mask_pointers_reference_a_separate_array():
    text = render_sprite_source({"hero": _packed(1)})

    assert "sprite_hero_data[]" in text
    assert "sprite_hero_mask[]" in text


def test_attribute_bytes_are_emitted_as_zero_for_every_sprite():
    """`_packed` builds a `PackedSprite` directly, without going through
    `pack_spectrum`, so `.attribute` is whatever a bare construction defaults
    to (0) -- this pins that default, not the packer's colour logic."""
    text = render_sprite_source({"hero": _packed(1), "enemy": _packed(1)})

    assert "sprite_attribute[] = {0, 0}" in text.replace("\n", " ").replace("  ", " ")


def test_a_sprites_own_nonzero_attribute_reaches_the_source():
    """A hand-built PackedSprite with a specific attribute byte must come out
    the other end unchanged, in the right position for its sprite id."""
    red = PackedSprite(bytes(32), bytes(32), 2, 16, 1, attribute=0x42)
    black = _packed(1)
    text = render_sprite_source({"hero": red, "enemy": black})

    assert "sprite_attribute[] = {66, 0}" in text.replace("\n", " ").replace("  ", " ")


def test_pack_spectrums_ink_reaches_the_source_not_just_the_packed_sprite():
    """End to end: a red frame packed by `pack_spectrum` must show up as
    attribute 66 (0x42, INK_RED | BRIGHT) in the rendered source text, not
    merely on the `PackedSprite` object that never gets rendered."""
    red_frame = Image.new("RGBA", (16, 16), (255, 0, 0, 255))
    packed = pack_spectrum([red_frame])

    text = render_sprite_source({"hero": packed})

    assert "sprite_attribute[] = {66}" in text.replace("\n", " ").replace("  ", " ")


def test_mismatched_width_bytes_across_sprites_is_rejected_in_the_source_too():
    with pytest.raises(ValueError, match="width_bytes"):
        render_sprite_source(
            {"hero": _packed(1, width_bytes=2), "enemy": _cpc_packed(1, width_bytes=8)}
        )


def test_a_sprite_id_that_is_not_a_valid_c_identifier_is_rejected_in_the_source_too():
    with pytest.raises(ValueError, match="identifier"):
        render_sprite_source({"my-hero": _packed(1)})


def test_the_per_sprite_byte_arrays_stay_static():
    """Nothing outside sprites.c ever needs a sprite's raw bytes by name, only
    through the sprite_data[]/sprite_mask[] pointer tables -- so these keep
    internal linkage, unlike the pointer tables themselves."""
    text = render_sprite_source({"hero": _packed(1)})

    assert "static const unsigned char sprite_hero_data[] = {" in text
    assert "static const unsigned char sprite_hero_mask[] = {" in text


class TestPreShiftedLayout:
    """What the header must say so a blitter can find one shifted copy.

    Three facts, and only three: how many copies exist (`SPRITE_SHIFTS`), how
    far apart they are (`SPRITE_SHIFT_STRIDE`), and where the frame they
    belong to starts (`sprite_frame_offset`, unchanged). A copy is then
    `sprite_data[s] + sprite_frame_offset[s][f] + shift * SPRITE_SHIFT_STRIDE`,
    which is an add and a multiply by a constant -- no second offset table,
    and no 16-bit multiply of the kind the CPCtelera link refuses.
    """

    def test_an_unshifted_project_says_one(self):
        text = render_sprite_header({"hero": _packed()})

        assert "#define SPRITE_SHIFTS 1" in text

    def test_a_shifted_project_says_how_many_and_how_far(self):
        packed = pack_spectrum([Image.new("RGBA", (16, 16), (255, 255, 255, 255))], shifts=8)

        text = render_sprite_header({"hero": packed})

        assert "#define SPRITE_SHIFTS 8" in text
        assert f"#define SPRITE_SHIFT_STRIDE {packed.bytes_per_block}" in text
        assert f"#define SPRITE_BYTES_WIDE {packed.width_bytes}" in text

    def test_the_stride_is_a_whole_copy_of_one_frame(self):
        packed = pack_spectrum([Image.new("RGBA", (16, 16), (255, 255, 255, 255))], shifts=8)

        assert packed.bytes_per_block == packed.width_bytes * 16
        assert packed.bytes_per_frame == packed.bytes_per_block * 8

    def test_the_cpc_stride_counts_the_interleaved_mask(self):
        """A CPC copy carries its mask inside `data`, so a stride that counted
        only colour bytes would land the blitter half a copy short."""
        from llmz80.studio.palette import cpc_rgb
        from llmz80.studio.spriting import pack_cpc

        packed = pack_cpc(
            [Image.new("RGBA", (16, 16), (255, 255, 255, 255))],
            mode=1,
            palette=cpc_rgb(1),
            shifts=4,
        )

        text = render_sprite_header({"hero": packed})

        assert f"#define SPRITE_SHIFT_STRIDE {2 * packed.width_bytes * 16}" in text
        assert "#define SPRITE_SHIFTS 4" in text

    def test_frame_offsets_still_step_a_whole_frame(self):
        """The offset table knows nothing about shifting, and must not: a
        frame's copies sit together, so its start is still `frame *
        bytes_per_frame` and `g_anim_frame` indexes it the way it always did.
        """
        packed = pack_spectrum([Image.new("RGBA", (16, 16), (255, 255, 255, 255))] * 3, shifts=8)

        source = render_sprite_source({"hero": packed})
        expected = [frame * packed.bytes_per_frame for frame in range(3)]

        assert ", ".join(str(offset) for offset in expected) in source

    def test_sprites_may_not_disagree_about_how_many_copies_they_have(self):
        """Same rule as `SPRITE_BYTES_WIDE`, and for the same reason: one macro
        cannot hold two answers, and a blitter reading the wrong one walks off
        the end of a sprite."""
        shifted = pack_spectrum([Image.new("RGBA", (16, 16), (255, 255, 255, 255))], shifts=8)

        with pytest.raises(ValueError, match="SPRITE_SHIFTS"):
            render_sprite_header({"hero": shifted, "enemy": _packed(frames=1, width_bytes=3)})
