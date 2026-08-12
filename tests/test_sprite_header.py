"""The generated header, judged as text a compiler will read."""

import pytest

from llmz80.studio.spriting import PackedSprite
from llmz80.studio.sprite_header import render_sprite_header


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


def test_sprite_frames_records_each_sprites_own_count():
    text = render_sprite_header({"hero": _packed(3), "enemy": _packed(1)})

    # dict order is hero=0, enemy=1; frame counts 3 and 1 respectively.
    assert "sprite_frames[] = {3, 1}" in text.replace("\n", " ").replace("  ", " ")


def test_frame_offset_on_the_spectrum_is_plain_frame_times_bytes_per_frame():
    """Spectrum data/mask are independent arrays, one bytes_per_frame chunk each."""
    packed = _packed(frames=3, width_bytes=2)  # bytes_per_frame = 2 * 16 = 32
    text = render_sprite_header({"hero": packed})

    assert "{0, 32, 64}" in text.replace("\n", " ")


def test_frame_offset_on_the_cpc_accounts_for_the_interleaved_mask():
    """CPC frames are twice `bytes_per_frame` long in `data` because the mask rides
    along interleaved with the colour bytes; the offset table must stride by that
    real length, not by `PackedSprite.bytes_per_frame` alone."""
    packed = _cpc_packed(frames=3, width_bytes=8)  # bytes_per_frame = 8*16 = 128
    text = render_sprite_header({"hero": packed})

    assert "{0, 256, 512}" in text.replace("\n", " ")


def test_ragged_frame_counts_still_produce_a_rectangular_array():
    """C requires a rectangular 2D array; the short sprite's row is padded so both
    rows have the same number of columns, and the padding repeats the last real
    offset so an out-of-range read (a bug elsewhere) still lands in-bounds."""
    text = render_sprite_header({"hero": _packed(3, width_bytes=2), "enemy": _packed(1, width_bytes=2)})

    squeezed = text.replace("\n", " ")
    assert "{0, 32, 64}" in squeezed  # hero: three real frames
    assert "{0, 0, 0}" in squeezed  # enemy: one real frame, padded by repeating offset 0


def test_cpc_mask_pointers_alias_the_data_pointers():
    """On the CPC the mask travels interleaved inside `data`, so `sprite_mask[]`
    must point at the very same bytes as `sprite_data[]`, not at a separate array."""
    text = render_sprite_header({"hero": _cpc_packed(1)})

    assert "sprite_mask" in text
    # No second byte array should be emitted for the mask on this target.
    assert text.count("sprite_hero_data[]") == 1
    assert "sprite_hero_mask[]" not in text


def test_spectrum_mask_pointers_reference_a_separate_array():
    text = render_sprite_header({"hero": _packed(1)})

    assert "sprite_hero_data[]" in text
    assert "sprite_hero_mask[]" in text


def test_attribute_bytes_are_emitted_as_zero_for_every_sprite():
    text = render_sprite_header({"hero": _packed(1), "enemy": _packed(1)})

    assert "sprite_attribute[] = {0, 0}" in text.replace("\n", " ").replace("  ", " ")


def test_mismatched_width_bytes_across_sprites_is_rejected():
    """SPRITE_BYTES_WIDE is a single, global macro; sprites packed for different
    modes (or different platforms) cannot coexist in one header."""
    with pytest.raises(ValueError, match="width_bytes"):
        render_sprite_header({"hero": _packed(1, width_bytes=2), "enemy": _cpc_packed(1, width_bytes=8)})


def test_a_sprite_id_that_is_not_a_valid_c_identifier_is_rejected():
    with pytest.raises(ValueError, match="identifier"):
        render_sprite_header({"my-hero": _packed(1)})
