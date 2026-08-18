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
