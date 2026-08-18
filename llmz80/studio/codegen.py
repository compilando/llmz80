"""Target facts and the pieces library a project's program can build against.

Nothing here generates gameplay. Studio scaffolds a buildable project -- the
platform library and a header of target constants -- and the program itself is
written into the project and owned by it.
"""

from __future__ import annotations

from pathlib import Path

from llmz80.core.state_contract import STATE_CONTRACT

from .models import GameProject, TargetPlatform, VideoMode
from .structure import playfield

LIBRARY_ROOT = Path(__file__).resolve().parents[2] / "resources" / "studio_lib"

#: Design key label -> the constant each toolchain reads it with. z88dk's
#: scancodes come from <input.h>; CPCtelera's key ids from <cpctelera.h>.
KEY_CODES: dict[TargetPlatform, dict[str, str]] = {
    TargetPlatform.SPECTRUM: {
        **{
            chr(code): f"IN_KEY_SCANCODE_{chr(code).lower()}"
            for code in range(ord("A"), ord("Z") + 1)
        },
        **{str(digit): f"IN_KEY_SCANCODE_{digit}" for digit in range(10)},
        "SPACE": "IN_KEY_SCANCODE_SPACE",
        "ENTER": "IN_KEY_SCANCODE_ENTER",
        # The 48K has no cursor keys; 5678 are what every game of the era used.
        "LEFT": "IN_KEY_SCANCODE_5",
        "DOWN": "IN_KEY_SCANCODE_6",
        "UP": "IN_KEY_SCANCODE_7",
        "RIGHT": "IN_KEY_SCANCODE_8",
    },
    TargetPlatform.AMSTRAD_CPC: {
        **{chr(code): f"Key_{chr(code)}" for code in range(ord("A"), ord("Z") + 1)},
        **{str(digit): f"Key_{digit}" for digit in range(10)},
        "SPACE": "Key_Space",
        "ENTER": "Key_Return",
        "LEFT": "Key_CursorLeft",
        "DOWN": "Key_CursorDown",
        "UP": "Key_CursorUp",
        "RIGHT": "Key_CursorRight",
    },
}


#: Scanlines each machine's display has. Not a design choice and not
#: configurable: 192 on a Spectrum, 200 on a CPC.
SCREEN_LINES: dict[TargetPlatform, int] = {
    TargetPlatform.SPECTRUM: 192,
    TargetPlatform.AMSTRAD_CPC: 200,
}


def max_sprite_py(platform: TargetPlatform) -> int:
    """The last pixel row a 16-line sprite can start on and still fit.

    Derived rather than written down twice, because it is written down in
    three places that must agree: the guard in each `plat_sprite_py`, the
    `MAX_SPRITE_PY` macro a program reads, and the sentence the writing prompt
    puts in front of the model. A prompt naming 176 on a machine whose guard
    says 184 costs the CPC eight rows of screen and says nothing about it; the
    reverse silently draws nothing and looks like a broken blitter.
    """
    from .spriting import SPRITE_SIZE

    return SCREEN_LINES[platform] - SPRITE_SIZE


#: Pixels each machine's display is across. Not a design choice: a Spectrum is
#: 256, a CPC row is 80 bytes and therefore 160 pixels in mode 0 and 320 in
#: mode 1. Mode 1's 320 is why `plat_sprite_px` takes an int -- a pixel column
#: there does not fit in the `unsigned char` every other coordinate uses.
SCREEN_PIXELS: dict[VideoMode, int] = {
    VideoMode.SPECTRUM_BITMAP: 256,
    VideoMode.CPC_MODE_0: 160,
    VideoMode.CPC_MODE_1: 320,
}


def pixels_per_byte_log(platform: TargetPlatform, mode: VideoMode) -> int:
    """The shift that divides a pixel column by `pixels_per_byte`.

    Emitted as `PIXELS_PER_BYTE_LOG` so the blitter can shift rather than
    divide: SDCC satisfies `/ 8` from its own routine, and the CPC link
    refuses a routine built for the other `--sdcccall` ABI (see
    `sprite_header.py`). Every value here is a power of two, so the shift is
    exact rather than an approximation somebody has to remember to check --
    and `test_preshifted_sprites` asserts `1 << log == pixels_per_byte` on
    every target rather than trusting this table twice.
    """
    from .spriting import pixels_per_byte

    return pixels_per_byte(platform, mode).bit_length() - 1


def max_sprite_px(project: GameProject) -> int:
    """The last pixel column a sprite can start at and still fit on screen.

    Two corrections to the obvious "screen width less sixteen", both of which
    only matter once a design asks for pre-shifted art, and both of which are
    invisible until something at the right edge writes past the display file.

    A shifted copy is one byte wider than the sprite, so the last legal *byte*
    column moves one to the left. And every sub-byte position inside that byte
    is reachable, so the last legal *pixel* column moves `shifts - 1` back to
    the right. On the Spectrum that is 240 unshifted and 239 shifted; the two
    corrections nearly cancel, which is exactly why writing either one alone
    would look right.

    Derived here rather than in the C for the same reason `max_sprite_py` is:
    the number is stated in three places that must agree -- the guard, the
    macro, and the sentence the writing prompt puts in front of the model --
    and it differs per target *and* per design.
    """
    from .spriting import SPRITE_SIZE, shift_count

    mode = project.target.video_mode
    per_byte = _pixels_per_byte(project.target.platform, mode)
    row_bytes = SCREEN_PIXELS[mode] // per_byte
    shifts = (
        shift_count(project.target.platform, mode) if project.presentation.smooth_horizontal else 1
    )
    sprite_bytes = SPRITE_SIZE // per_byte + (1 if shifts > 1 else 0)
    return (row_bytes - sprite_bytes) * per_byte + shifts - 1


def _pixels_per_byte(platform: TargetPlatform, mode: VideoMode) -> int:
    from .spriting import pixels_per_byte

    return pixels_per_byte(platform, mode)


#: Bytes the picture moves for one step of a target's hardware scroll, and 0
#: for a target that has none.
#:
#: Two on the Amstrad CPC, and measured rather than quoted: CPCtelera's own
#: examples disagree, `advanced/hwscroll` saying four bytes in a comment while
#: `advanced/tilemap_hwscroll` advances its software pointer by two for the
#: same unit. A probe drawing a bar exactly one byte wide -- so the bar's width
#: in captured pixels is the unit being measured, whatever scale the emulator
#: captured at -- read 2.00 bytes at offset 1 and 4.00 at offset 2 on a real
#: machine. The tilemap example is right, which is what one would expect of the
#: one whose arithmetic has to stay in step with the hardware to work at all.
#:
#: Zero for the Spectrum, which has no register for this at all. Zero rather
#: than absent so a program can write `#if SCROLL_STEP_BYTES` and compile one
#: source for both machines.
SCROLL_STEP_BYTES: dict[TargetPlatform | str | None, int] = {
    TargetPlatform.SPECTRUM: 0,
    TargetPlatform.AMSTRAD_CPC: 2,
}

#: Bytes in one screen row, which is the vertical step: advancing the display
#: start by a whole row moves the picture up by one character row. Measured on
#: the same machine -- 40 steps of 2 bytes moved a full-width bar up by exactly
#: one character row, and 80 steps by two.
SCROLL_ROW_BYTES: dict[TargetPlatform | str | None, int] = {
    TargetPlatform.SPECTRUM: 32,
    TargetPlatform.AMSTRAD_CPC: 80,
}

#: Steps the CPC's offset register can hold. R13 is eight bits, so 255 -- and
#: past that the *page* has to change, which is a second register
#: (`cpct_setVideoMemoryPage`) and a wrap the game has to plan for. The bound
#: is published rather than left to be discovered, because a scroller that ran
#: off the end would not fail, it would jump.
SCROLL_MAX_STEPS = 255


def scrolls_in_hardware(platform: TargetPlatform | str | None) -> bool:
    """Whether this target can move its picture without moving its pixels.

    A `str` is accepted beside the enum for the same reason `has_frame_clock`
    accepts one, and an unknown target answers no: a machine this project has
    never heard of has not shown it can do this either.
    """
    return bool(SCROLL_STEP_BYTES.get(platform, 0))


def max_scroll_origin(platform: TargetPlatform | str | None) -> int:
    """The furthest byte `plat_scroll_to` can start the display at."""
    return SCROLL_STEP_BYTES.get(platform, 0) * SCROLL_MAX_STEPS


#: Targets whose `plat_wait_frame` actually counts the frames the previous
#: iteration cost. `resources/studio_lib/spectrum/platform.c` reads the ROM
#: frame counter at 23672; `resources/studio_lib/cpc/platform.c` builds the
#: equivalent out of `cpct_setInterruptHandler`, counting the six interrupts
#: the CPC raises per display frame. Both then return the elapsed count less
#: the one frame the wait itself is worth.
#:
#: The CPC was not on this list until the counter existed, and that was the
#: honest state rather than an oversight: with the firmware disabled it had no
#: free-running counter, `plat_wait_frame` returned a literal zero, and reading
#: that zero as a game keeping perfect time would have cleared the whole
#: platform on the strength of a number nobody computed.
_FRAME_CLOCK_PLATFORMS = frozenset(
    {TargetPlatform.SPECTRUM.value, TargetPlatform.AMSTRAD_CPC.value}
)


def has_frame_clock(platform: TargetPlatform | str | None) -> bool:
    """Whether this target can say how many frames an iteration overran by.

    One predicate, two readers: `render_config_header` writes it into
    game_config.h as `HAS_FRAME_CLOCK`, and `pacing.pacing_report` asks it
    whether `g_worst_frame_cost` is a measurement or a placeholder zero. They
    used to decide it separately, and the drift would have been silent and in
    the bad direction: giving the CPC a frame counter means editing the C and
    the define, after which the pacing gate would keep abstaining on a target
    that had started measuring for real. Nothing would have failed to say so.

    A `str` is accepted beside the enum because the gate reads its platform out
    of a runtime report, where it has already been through YAML; the rejected
    alternative was for the gate to re-parse that string into a `TargetPlatform`
    first, which would have raised on an unrecognised target where abstaining is
    the answer this floor wants. An unknown platform is not a frame clock.
    """
    return platform in _FRAME_CLOCK_PLATFORMS


def audio_mask(project: GameProject) -> int:
    """Bitmask of the effects this design declared, one bit per slot.

    Numbered by the design's own declaration order rather than by a fixed
    catalogue: the platform library plays effect N, and which sound N is stays
    the library's business, while what it is called stays the design's.
    """
    return (1 << len(project.audio.effects)) - 1


def library_sources(project: GameProject) -> list[Path]:
    """Platform pieces copied into a project. A program may ignore them."""
    target = "spectrum" if project.target.platform is TargetPlatform.SPECTRUM else "cpc"
    return [
        LIBRARY_ROOT / "common" / "platform.h",
        LIBRARY_ROOT / target / "platform.c",
    ]


def _binding_lines(project: GameProject) -> tuple[list[str], list[str]]:
    """One named bit and one X-macro entry per binding, in declaration order."""
    codes = KEY_CODES[project.target.platform]
    bits: list[str] = []
    entries: list[str] = []
    for index, (name, key) in enumerate(project.controls.bindings.items()):
        macro = f"INPUT_{name.upper()}"
        bits.append(f"#define {macro} 0x{1 << index:02X}")
        entries.append(f"    X({macro}, {codes[key]}) \\")
    return bits, entries


def _colour_lines(project: GameProject) -> list[str]:
    """`#define COLOUR_<ID>` for every palette entry this target can show."""
    from .palette import declared_attribute

    lines = []
    for entry in project.presentation.palette:
        value = declared_attribute(project, entry.id)
        if value is None:
            continue
        lines.append(f"#define COLOUR_{entry.id.upper()} {value}  /* {entry.colour} */")
    return lines


def _cpc_palette_lines(project: GameProject) -> list[str]:
    """The hardware pens `cpc/platform.c` programs, or nothing on the Spectrum.

    Written here rather than hard-coded in the C for the reason the two used
    to get wrong: the packers quantise a drawn pixel against an RGB table in
    Python, and `apply_palette` sets pens in C, and when those were written
    down separately they drifted -- HW_BLUE recorded as (0, 0, 255), which is
    HW_BRIGHT_BLUE, and HW_WHITE as (255, 255, 255), which is HW_BRIGHT_WHITE.
    Half the palette quantised sprites against colours the machine was never
    asked to show, and nothing could notice, because neither half knew the
    other existed. Now one table (`palette.HARDWARE_COLOURS`) produces both.

    It is also what makes mode 0's sixteen pens reachable at all: the C used
    to program four whatever the mode.
    """
    if project.target.platform is not TargetPlatform.AMSTRAD_CPC:
        return []
    from .palette import cpc_mode, cpc_palette

    pens = cpc_palette(cpc_mode(project))
    values = ", ".join(f"0x{colour.hardware:02X}" for colour in pens)
    names = ", ".join(colour.name for colour in pens)
    return [
        "/* The pens this design's video mode programs, from",
        " * llmz80.studio.palette.HARDWARE_COLOURS -- the same table the sprite",
        " * and tile packers quantise against, so what is drawn is what shows.",
        f" * In order: {names}. */",
        f"#define CPC_PEN_COUNT {len(pens)}",
        f"#define CPC_PALETTE_PENS {values}",
    ]


def render_config_header(project: GameProject) -> str:
    """Target and design constants the platform library and a program can use."""
    cpc_mode = 0 if project.target.video_mode is VideoMode.CPC_MODE_0 else 1
    mode = project.target.video_mode
    columns, rows = playfield(project)
    bits, entries = _binding_lines(project)
    # The last X-macro line must not carry a trailing backslash.
    entries[-1] = entries[-1].rstrip(" \\")
    return "\n".join(
        [
            "/* Written by LLMZ80 Studio from game.yml. Constants only, no behaviour. */",
            "#ifndef LLMZ80_GAME_CONFIG_H",
            "#define LLMZ80_GAME_CONFIG_H",
            "",
            f"#define CPC_MODE {cpc_mode}",
            f"#define PLAYFIELD_COLS {columns}",
            f"#define PLAYFIELD_ROWS {rows}",
            f"#define FIELD_TOP {project.presentation.hud_rows}",
            f"#define SCREEN_COUNT {len(project.screens)}",
            "/* One bit per declared effect; zero means the design is silent. */",
            f"#define AUDIO_EFFECT_MASK {audio_mask(project)}",
            *[
                f"#define SOUND_{name.upper()} {index}"
                for index, name in enumerate(project.audio.effects)
            ],
            "/* Only targets with a free-running frame clock report overruns. */",
            f"#define HAS_FRAME_CLOCK {1 if has_frame_clock(project.target.platform) else 0}",
            "/* The last pixel row plat_sprite_py can start a sprite on. */",
            f"#define MAX_SPRITE_PY {max_sprite_py(project.target.platform)}",
            "/* How a pixel column becomes a byte column, and the rightmost one a",
            " * sprite can start at. MAX_SPRITE_PX already allows for the extra byte",
            " * a pre-shifted copy occupies, so it moves when smooth_horizontal does. */",
            f"#define PIXELS_PER_BYTE {_pixels_per_byte(project.target.platform, mode)}",
            f"#define PIXELS_PER_BYTE_LOG " f"{pixels_per_byte_log(project.target.platform, mode)}",
            f"#define MAX_SPRITE_PX {max_sprite_px(project)}",
            "/* Hardware scrolling. SCROLL_STEP_BYTES is 0 on a machine that has",
            " * none, so `#if SCROLL_STEP_BYTES` compiles one source for both.",
            " * The step is coarse: 2 bytes is 4 pixels across in CPC mode 0 and 8",
            " * in mode 1, and SCROLL_ROW_BYTES of it moves the picture up by one",
            " * character row. */",
            f"#define SCROLL_STEP_BYTES {SCROLL_STEP_BYTES.get(project.target.platform, 0)}",
            f"#define SCROLL_ROW_BYTES {SCROLL_ROW_BYTES.get(project.target.platform, 0)}",
            f"#define MAX_SCROLL_ORIGIN {max_scroll_origin(project.target.platform)}",
            *_cpc_palette_lines(project),
            # One per colour the design's palette named and this machine can
            # show. Resolved here rather than written into a prompt because the
            # value is target-specific -- a Spectrum attribute byte, a CPC pen
            # -- while the name a program says is the design's own either way
            # (see palette.declared_attribute). An entry whose prose names no
            # colour is left out rather than defaulted: defining it as white
            # would put a colour nobody chose behind the design's word for it,
            # and a program that used the name would then fail to compile,
            # which is the loud version of that mistake.
            *_colour_lines(project),
            "",
            "/* One bit per binding the design declared, in its own order. */",
            *bits,
            "",
            "/* Expand with your own X to read every bound key:",
            " *   #define X(bit, code) if (pressed(code)) keys |= bit;",
            " *   INPUT_BINDINGS(X)",
            " *   #undef X                                              */",
            "#define INPUT_BINDINGS(X) \\",
            *entries,
            "",
            "#endif",
            "",
        ]
    )


def render_state_header(project: GameProject) -> str:
    """Declarations for the state contract plus this design's own observables.

    Only the required symbols are declared outright. The optional ones are
    named in a comment instead, because `contract_prompt` tells the writer that
    a design with no such notion must not declare them at all -- and handing it
    a header that declares all of them anyway is the same prompt contradicting
    itself twelve lines later. A game with lives declares g_lives itself; a
    puzzle without them is not nudged into inventing one.
    """
    lines = [
        "/* The observable state contract. Define these once in your program.",
        " * They are read out of emulated memory to judge the program's behaviour,",
        " * so they must have external linkage and keep these exact names. */",
        "#ifndef LLMZ80_GAME_STATE_H",
        "#define LLMZ80_GAME_STATE_H",
        "",
    ]
    for symbol in STATE_CONTRACT:
        if not symbol.required:
            continue
        ctype = "unsigned int" if symbol.width == 2 else "unsigned char"
        lines.append(f"extern {ctype} {symbol.name};  /* {symbol.meaning} */")
    optional = [symbol for symbol in STATE_CONTRACT if not symbol.required]
    if optional:
        lines.extend(
            [
                "",
                "/* Declare and define these yourself, and only the ones this game",
                " * actually has a notion of:",
            ]
        )
        for symbol in optional:
            ctype = "unsigned int" if symbol.width == 2 else "unsigned char"
            lines.append(f" *   {ctype} {symbol.name};  {symbol.meaning}")
        lines.append(" */")
    if project.observables:
        lines.extend(["", "/* Declared by this design in game.yml. */"])
        for observable in project.observables:
            ctype = "unsigned int" if observable.width == 2 else "unsigned char"
            lines.append(f"extern {ctype} {observable.symbol};  /* {observable.meaning} */")
    lines.extend(["", "#endif", ""])
    return "\n".join(lines)
