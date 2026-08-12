"""Turn packed sprite bytes into the `sprites.h` a generated game includes.

This is the boundary where a `PackedSprite` (see `spriting.py`) stops being pixels
in Python and becomes text a C compiler reads. The symbol names it emits are a
contract with the blitters written in Task 6 (Spectrum) and Task 7 (CPC) -- both
already assume `sprite_data[]`, `sprite_mask[]`, `sprite_frame_offset[][]` and the
rest exist with these exact names and shapes, so nothing here is free to change
without breaking that C.

Every offset in `sprite_frame_offset` is computed here, in Python, and baked into
the header as a literal. That is not a style choice: `docs/STUDIO_ROADMAP.md`
records that the generated program must contain no 16-bit multiplication, because
SDCC would satisfy `frame * bytes_per_frame` from a library module built for the
wrong `--sdcccall` ABI and the CPCtelera link fails on the mismatch, in a way that
looks nothing like a multiplication bug. Precomputing the table here means the
blitter only ever indexes `sprite_frame_offset[sprite][frame]` -- an array lookup,
never a multiply.
"""

from __future__ import annotations

import re

from llmz80.studio.spriting import PackedSprite

#: The include guard and comment banner name this module by. Kept as one constant
#: so the "defined exactly once" property tested for is trivially true.
_GUARD = "LLMZ80_SPRITES_H"

_VALID_C_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

#: Bytes per output line for the big data/mask arrays. Purely cosmetic -- it keeps
#: a generated header reviewable instead of one enormous line -- but SDCC and
#: z88dk both tolerate arbitrarily long initialiser lists either way.
_BYTES_PER_LINE = 16


def _checked_id(sprite_id: str) -> str:
    if not _VALID_C_IDENTIFIER.match(sprite_id):
        raise ValueError(
            f"sprite id {sprite_id!r} is not a valid C identifier "
            "(used both as a #define suffix and a variable name fragment)"
        )
    return sprite_id


def _frame_stride(packed: PackedSprite) -> int:
    """How many bytes one frame really advances by inside `packed.data`.

    On the Spectrum (`pack_spectrum`), `data` and `mask` are independent arrays of
    identical size, one `bytes_per_frame`-sized chunk per frame in each.

    On the CPC (`pack_cpc`), `PackedSprite.mask` is always empty: the mask does not
    travel separately, it is interleaved one byte ahead of every colour byte inside
    `data` (see that function's docstring for why `cpct_drawSpriteMasked` wants it
    laid out that way). A frame therefore really occupies `2 * bytes_per_frame`
    bytes of `data`, even though `bytes_per_frame` itself -- built from
    `width_bytes * height` -- says nothing about that doubling; it is purely a
    width/height figure, not a "how far to the next frame" figure.

    Reading this off `len(packed.mask) == 0` rather than a target flag keeps this
    module ignorant of which pack_* function produced a given sprite, matching how
    `spriting.py` itself draws that same distinction.
    """
    if len(packed.mask) == 0:
        return 2 * packed.bytes_per_frame
    return packed.bytes_per_frame


def _c_byte_array(name: str, data: bytes) -> str:
    """A `static const unsigned char NAME[] = { ... };` declaration, line-wrapped."""
    if not data:
        # A zero-length initialiser is not valid C; this only happens for a
        # zero-frame sprite, which `spriting._checked` already forbids upstream,
        # so this branch exists as a guard against that invariant breaking silently.
        raise ValueError(f"sprite {name!r} has no packed bytes")
    lines = []
    for start in range(0, len(data), _BYTES_PER_LINE):
        chunk = data[start : start + _BYTES_PER_LINE]
        lines.append("    " + ", ".join(f"0x{byte:02X}" for byte in chunk) + ",")
    body = "\n".join(lines)
    return f"static const unsigned char {name}[] = {{\n{body}\n}};"


def render_sprite_header(sprites: dict[str, PackedSprite]) -> str:
    """Render `sprites.h` from a project's packed sprites, keyed by sprite id.

    `sprites` is in the order the header numbers `SPRITE_<ID>` from: dictionary
    order, i.e. insertion order, not alphabetical. All sprites must share one
    `width_bytes` -- it becomes the single global `SPRITE_BYTES_WIDE` macro, so
    mixing e.g. a CPC mode-0 sprite with a mode-1 one in the same header would
    make that macro a lie for whichever sprite it does not match.
    """
    ids = [_checked_id(sprite_id) for sprite_id in sprites]
    count = len(ids)

    width_bytes_values = {packed.width_bytes for packed in sprites.values()}
    if len(width_bytes_values) > 1:
        raise ValueError(
            f"sprites disagree on width_bytes ({sorted(width_bytes_values)}); "
            "SPRITE_BYTES_WIDE can only hold one value, so a header cannot mix "
            "sprites packed for different platforms or modes"
        )
    # With no sprites at all there is nothing to read this back from; the value
    # is then never consulted because SPRITE_COUNT == 0 disables the blitter, so
    # any placeholder is harmless. 2 (the Spectrum's own width) is as good as any.
    bytes_wide = next(iter(width_bytes_values), 2)

    lines = [
        f"#ifndef {_GUARD}",
        f"#define {_GUARD}",
        "/* Generated by llmz80.studio.sprite_header -- do not edit by hand.",
        " *",
        " * sprite_frame_offset is precomputed here, in Python, rather than derived",
        " * in C from `frame * bytes_per_frame`: the generated program must contain no",
        " * 16-bit multiplication (see docs/STUDIO_ROADMAP.md), because SDCC would",
        " * satisfy that multiply from a library module built for the wrong",
        " * --sdcccall ABI and the CPCtelera link fails on the mismatch. */",
        "",
    ]

    for index, sprite_id in enumerate(ids):
        lines.append(f"#define SPRITE_{sprite_id.upper()} {index}")
    lines.append(f"#define SPRITE_COUNT {count}")
    lines.append(f"#define SPRITE_BYTES_WIDE {bytes_wide}")
    lines.append("")

    if count == 0:
        lines.append(f"#endif /* {_GUARD} */")
        return "\n".join(lines) + "\n"

    max_frames = max(packed.frames for packed in sprites.values())

    lines.append(f"#if SPRITE_COUNT > 0")
    lines.append("")

    # Per-sprite byte arrays. A CPC-style sprite (empty `.mask`) gets only a data
    # array; its mask lives inside that same array, so no second one is emitted.
    for sprite_id, packed in sprites.items():
        lines.append(_c_byte_array(f"sprite_{sprite_id}_data", packed.data))
        if packed.mask:
            lines.append(_c_byte_array(f"sprite_{sprite_id}_mask", packed.mask))
        lines.append("")

    data_pointers = ", ".join(f"sprite_{sprite_id}_data" for sprite_id in ids)
    lines.append(f"const unsigned char *const sprite_data[] = {{ {data_pointers} }};")

    # sprite_mask[] aliases sprite_data[] wherever the mask travels interleaved
    # (CPC); it points at the sprite's own mask array wherever one exists (Spectrum).
    mask_pointers = ", ".join(
        f"sprite_{sprite_id}_data" if not sprites[sprite_id].mask else f"sprite_{sprite_id}_mask"
        for sprite_id in ids
    )
    lines.append(f"const unsigned char *const sprite_mask[] = {{ {mask_pointers} }};")
    lines.append("")

    # Offsets: real per-frame stride (see _frame_stride) times frame index, padded
    # to a rectangular [SPRITE_COUNT][max_frames] array -- C has no ragged arrays.
    # A short sprite's unused columns repeat its last real offset rather than 0,
    # so a program that (buggily) reads past its own sprite_frames[] count still
    # lands inside that sprite's last real frame instead of at an arbitrary byte.
    offset_rows = []
    for sprite_id in ids:
        packed = sprites[sprite_id]
        stride = _frame_stride(packed)
        real = [frame * stride for frame in range(packed.frames)]
        padded = real + [real[-1]] * (max_frames - len(real))
        offset_rows.append("{" + ", ".join(str(value) for value in padded) + "}")
    lines.append(
        f"const unsigned int sprite_frame_offset[][{max_frames}] = {{\n    "
        + ",\n    ".join(offset_rows)
        + "\n};"
    )
    lines.append("")

    frame_counts = ", ".join(str(sprites[sprite_id].frames) for sprite_id in ids)
    lines.append(f"const unsigned char sprite_frames[] = {{{frame_counts}}};")
    lines.append("")

    # No PackedSprite carries colour-attribute data yet, so every sprite gets 0 --
    # meaningful only on the Spectrum, where 0 is PAPER_BLACK | INK_BLACK; the CPC
    # blitter ignores this array entirely but still needs it to exist so the same
    # generated program compiles unmodified against either platform library.
    attribute_bytes = ", ".join("0" for _ in ids)
    lines.append(f"const unsigned char sprite_attribute[] = {{{attribute_bytes}}};")
    lines.append("")
    lines.append("#endif /* SPRITE_COUNT */")
    lines.append("")
    lines.append(f"#endif /* {_GUARD} */")
    return "\n".join(lines) + "\n"
