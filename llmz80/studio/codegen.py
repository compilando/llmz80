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
            "#define HAS_FRAME_CLOCK "
            f"{1 if project.target.platform is TargetPlatform.SPECTRUM else 0}",
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
    """Declarations for the state contract plus this design's own observables."""
    lines = [
        "/* The observable state contract. Define these once in your program.",
        " * They are read out of emulated memory to judge the program's behaviour,",
        " * so they must have external linkage and keep these exact names. */",
        "#ifndef LLMZ80_GAME_STATE_H",
        "#define LLMZ80_GAME_STATE_H",
        "",
    ]
    for symbol in STATE_CONTRACT:
        ctype = "unsigned int" if symbol.width == 2 else "unsigned char"
        lines.append(f"extern {ctype} {symbol.name};  /* {symbol.meaning} */")
    if project.observables:
        lines.extend(["", "/* Declared by this design in game.yml. */"])
        for observable in project.observables:
            ctype = "unsigned int" if observable.width == 2 else "unsigned char"
            lines.append(f"extern {ctype} {observable.symbol};  /* {observable.meaning} */")
    lines.extend(["", "#endif", ""])
    return "\n".join(lines)
