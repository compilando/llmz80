"""Turn packed sprite bytes into the `sprites.h`/`sprites.c` a generated game uses.

This is the boundary where a `PackedSprite` (see `spriting.py`) stops being pixels
in Python and becomes text a C compiler reads. The symbol names it emits are a
contract with the blitters written in Task 6 (Spectrum) and Task 7 (CPC) -- both
already assume `sprite_data[]`, `sprite_mask[]`, `sprite_frame_offset[][]` and the
rest exist with these exact names and shapes, so nothing here is free to change
without breaking that C.

`sprites.h` (`render_sprite_header`) is included by two translation units:
`platform.c`, which implements `plat_sprite`, and the program's own `main.c`,
which calls it and (usually) reads the `SPRITE_<ID>` constants directly. It
therefore carries only `#define`s and `extern` declarations -- nothing with a
body, or the linker sees two definitions of `sprite_data[]` and the like and
refuses to link (`error: duplicate definition: main_c::_sprite_data`). The
actual tables live in `sprites.c` (`render_sprite_source`), compiled exactly
once and linked in, so a project's sprite pixels are stored once, not once per
translation unit that happens to include the header.

Every offset in `sprite_frame_offset` is computed here, in Python, and baked into
the source as a literal. That is not a style choice: `docs/STUDIO_ROADMAP.md`
records that the generated program must contain no 16-bit multiplication, because
SDCC would satisfy `frame * bytes_per_frame` from a library module built for the
wrong `--sdcccall` ABI and the CPCtelera link fails on the mismatch, in a way that
looks nothing like a multiplication bug. Precomputing the table here means the
blitter only ever indexes `sprite_frame_offset[sprite][frame]` -- an array lookup,
never a multiply.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

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


@dataclass(frozen=True)
class _Layout:
    """The shape both `sprites.h` and `sprites.c` must agree on.

    Computed once and shared by both render functions so the two files can
    never drift apart on ids, count, width or the frame table's shape --
    the two are always rendered from the same `_Layout` for the same
    `sprites` dict.
    """

    ids: list[str]
    count: int
    bytes_wide: int
    max_frames: int


def _layout(sprites: dict[str, PackedSprite]) -> _Layout:
    ids = [_checked_id(sprite_id) for sprite_id in sprites]

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
    max_frames = max((packed.frames for packed in sprites.values()), default=0)
    return _Layout(ids=ids, count=len(ids), bytes_wide=bytes_wide, max_frames=max_frames)


#: Shared banner, identical in both generated files so a reader can tell at a
#: glance that `sprites.h` and `sprites.c` are two halves of the same output.
_BANNER = (
    "/* Generated by llmz80.studio.sprite_header -- do not edit by hand.\n"
    " *\n"
    " * sprite_frame_offset is precomputed here, in Python, rather than derived\n"
    " * in C from `frame * bytes_per_frame`: the generated program must contain no\n"
    " * 16-bit multiplication (see docs/STUDIO_ROADMAP.md), because SDCC would\n"
    " * satisfy that multiply from a library module built for the wrong\n"
    " * --sdcccall ABI and the CPCtelera link fails on the mismatch. */"
)


def render_sprite_header(sprites: dict[str, PackedSprite]) -> str:
    """Render `sprites.h` from a project's packed sprites, keyed by sprite id.

    `sprites` is in the order the header numbers `SPRITE_<ID>` from: dictionary
    order, i.e. insertion order, not alphabetical. All sprites must share one
    `width_bytes` -- it becomes the single global `SPRITE_BYTES_WIDE` macro, so
    mixing e.g. a CPC mode-0 sprite with a mode-1 one in the same header would
    make that macro a lie for whichever sprite it does not match.

    This header carries `#define`s and `extern` declarations only -- never a
    definition with a body. It is included by both `platform.c` (which
    implements `plat_sprite`) and the program's own `main.c`; a definition
    here would make the linker see two of everything. The actual tables are
    `render_sprite_source`'s job, compiled once into `sprites.c`.
    """
    layout = _layout(sprites)

    lines = [
        f"#ifndef {_GUARD}",
        f"#define {_GUARD}",
        _BANNER,
        "",
    ]

    for index, sprite_id in enumerate(layout.ids):
        lines.append(f"#define SPRITE_{sprite_id.upper()} {index}")
    lines.append(f"#define SPRITE_COUNT {layout.count}")
    lines.append(f"#define SPRITE_BYTES_WIDE {layout.bytes_wide}")
    lines.append("")

    if layout.count == 0:
        lines.append(f"#endif /* {_GUARD} */")
        return "\n".join(lines) + "\n"

    lines.append("#if SPRITE_COUNT > 0")
    lines.append("")
    lines.append("/* Defined once, in sprites.c -- see that file for why. */")
    lines.append("extern const unsigned char *const sprite_data[];")
    lines.append("extern const unsigned char *const sprite_mask[];")
    lines.append(
        f"extern const unsigned int sprite_frame_offset[][{layout.max_frames}];"
    )
    lines.append("extern const unsigned char sprite_frames[];")
    lines.append("extern const unsigned char sprite_attribute[];")
    lines.append("")
    lines.append("#endif /* SPRITE_COUNT */")
    lines.append("")
    lines.append(f"#endif /* {_GUARD} */")
    return "\n".join(lines) + "\n"


def render_sprite_source(sprites: dict[str, PackedSprite]) -> str:
    """Render `sprites.c`: the one place a project's packed sprite bytes and
    the tables built from them are actually defined.

    Compiled exactly once and linked into the program (see `compiler.py`'s
    `render_project`), so a project's pixels are stored once, not once per
    translation unit that includes `sprites.h`. Must be rendered from the
    same `sprites` dict as the matching `render_sprite_header` call -- both
    derive their shape from `_layout`, so passing mismatched dicts to the two
    functions (rather than the same dict to both) is the one way to make
    these two files disagree.
    """
    layout = _layout(sprites)

    lines = [_BANNER, "", '#include "sprites.h"', ""]

    if layout.count == 0:
        # A file with only an #include and no declaration is, to a strict C
        # compiler, an empty translation unit -- z88dk's cc1 warns "ISO C
        # forbids an empty translation unit", and Studio's own build policy
        # treats a warning from its own generated source as build-breaking.
        # One inert typedef keeps the file non-empty without claiming
        # anything about sprites that do not exist.
        lines.append("typedef int llmz80_sprites_c_is_not_an_empty_translation_unit;")
        lines.append("")
        return "\n".join(lines) + "\n"

    lines.append("#if SPRITE_COUNT > 0")
    lines.append("")

    # Per-sprite byte arrays. A CPC-style sprite (empty `.mask`) gets only a data
    # array; its mask lives inside that same array, so no second one is emitted.
    # These stay `static`: nothing outside this file ever needs a sprite's raw
    # bytes by name, only through the `sprite_data[]`/`sprite_mask[]` pointer
    # tables below, so there is no reason to give them external linkage.
    for sprite_id, packed in sprites.items():
        lines.append(_c_byte_array(f"sprite_{sprite_id}_data", packed.data))
        if packed.mask:
            lines.append(_c_byte_array(f"sprite_{sprite_id}_mask", packed.mask))
        lines.append("")

    data_pointers = ", ".join(f"sprite_{sprite_id}_data" for sprite_id in layout.ids)
    lines.append(f"const unsigned char *const sprite_data[] = {{ {data_pointers} }};")

    # sprite_mask[] aliases sprite_data[] wherever the mask travels interleaved
    # (CPC); it points at the sprite's own mask array wherever one exists (Spectrum).
    mask_pointers = ", ".join(
        f"sprite_{sprite_id}_data" if not sprites[sprite_id].mask else f"sprite_{sprite_id}_mask"
        for sprite_id in layout.ids
    )
    lines.append(f"const unsigned char *const sprite_mask[] = {{ {mask_pointers} }};")
    lines.append("")

    # Offsets: PackedSprite.bytes_per_frame is already the true per-frame stride
    # for both targets -- on the CPC it accounts for the interleaved mask, so it
    # must not be doubled again here. Frame index times that stride, padded to a
    # rectangular [SPRITE_COUNT][max_frames] array -- C has no ragged arrays. A
    # short sprite's unused columns repeat its last real offset rather than 0, so
    # a program that (buggily) reads past its own sprite_frames[] count still
    # lands inside that sprite's last real frame instead of an arbitrary byte.
    offset_rows = []
    for sprite_id in layout.ids:
        packed = sprites[sprite_id]
        real = [frame * packed.bytes_per_frame for frame in range(packed.frames)]
        padded = real + [real[-1]] * (layout.max_frames - len(real))
        offset_rows.append("{" + ", ".join(str(value) for value in padded) + "}")
    lines.append(
        f"const unsigned int sprite_frame_offset[][{layout.max_frames}] = {{\n    "
        + ",\n    ".join(offset_rows)
        + "\n};"
    )
    lines.append("")

    frame_counts = ", ".join(str(sprites[sprite_id].frames) for sprite_id in layout.ids)
    lines.append(f"const unsigned char sprite_frames[] = {{{frame_counts}}};")
    lines.append("")

    # PackedSprite.attribute (see spriting.py's _spectrum_attribute) carries the
    # one Spectrum ink+PAPER_BLACK[+BRIGHT] byte a sprite's opaque pixels resolve
    # to. The CPC blitter ignores this array entirely -- colour lives in its
    # pixel data instead -- but the array still needs to exist so the same
    # generated program compiles unmodified against either platform library.
    attribute_bytes = ", ".join(str(sprites[sprite_id].attribute) for sprite_id in layout.ids)
    lines.append(f"const unsigned char sprite_attribute[] = {{{attribute_bytes}}};")
    lines.append("")
    lines.append("#endif /* SPRITE_COUNT */")
    return "\n".join(lines) + "\n"
