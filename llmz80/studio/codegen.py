"""Target facts and the pieces library a project's program can build against.

Nothing here generates gameplay. Studio scaffolds a buildable project -- the
platform library, a header of target constants, and the design's contract -- and
the program itself is written into the project and owned by it.
"""

from __future__ import annotations

from pathlib import Path

from llmz80.core.state_contract import STATE_CONTRACT

from .models import AUDIO_EFFECTS, GameProject, TargetPlatform, VideoMode

LIBRARY_ROOT = Path(__file__).resolve().parents[2] / "resources" / "studio_lib"

#: Character rows a program is expected to reserve at the top for its HUD.
FIELD_TOP = 2

#: Character-cell grid available on each target, as (columns, rows).
TARGET_GRID: dict[VideoMode, tuple[int, int]] = {
    VideoMode.SPECTRUM_BITMAP: (32, 24),
    VideoMode.CPC_MODE_0: (20, 25),
    VideoMode.CPC_MODE_1: (40, 25),
}

DIFFICULTY_CURVES = {"flat": 0, "linear": 1, "stepped": 2}

#: Roles the design vocabulary understands. A program may interpret them freely.
SUPPORTED_ROLES = {"player", "enemy", "collectible"}


def playfield(project: GameProject) -> tuple[int, int]:
    """Playfield size in cells once the HUD rows are taken out."""
    columns, rows = TARGET_GRID[project.target.video_mode]
    return columns, rows - FIELD_TOP


def audio_mask(project: GameProject) -> int:
    """Bitmask of enabled effects, positioned by their library constant."""
    mask = 0
    for index, effect in enumerate(AUDIO_EFFECTS):
        if effect in project.audio.effects:
            mask |= 1 << index
    return mask


def library_sources(project: GameProject) -> list[Path]:
    """Platform pieces copied into a project. A program may ignore them."""
    target = "spectrum" if project.target.platform is TargetPlatform.SPECTRUM else "cpc"
    return [
        LIBRARY_ROOT / "common" / "platform.h",
        LIBRARY_ROOT / target / "platform.c",
    ]


def render_config_header(project: GameProject) -> str:
    """Target and design constants the platform library and a program can use."""
    cpc_mode = 0 if project.target.video_mode is VideoMode.CPC_MODE_0 else 1
    scheme = 1 if project.controls.scheme == "cursor_space" else 0
    columns, rows = playfield(project)
    return f"""/* Written by LLMZ80 Studio from game.yml. Constants only, no behaviour. */
#ifndef LLMZ80_GAME_CONFIG_H
#define LLMZ80_GAME_CONFIG_H

#define LEVEL_COUNT {project.gameplay.level_count}
#define START_LIVES {project.gameplay.lives}
#define WIN_SCORE {project.gameplay.win_score}
#define SCORE_PER_COLLECTIBLE {project.gameplay.score_per_collectible}
#define DIFFICULTY_CURVE {DIFFICULTY_CURVES[project.gameplay.difficulty_curve]}
#define CONTROL_SCHEME {scheme}
#define CPC_MODE {cpc_mode}
#define PLAYFIELD_COLS {columns}
#define PLAYFIELD_ROWS {rows}
/* One bit per effect, in AUDIO_EFFECTS order; zero means the design is silent. */
#define AUDIO_EFFECT_MASK {audio_mask(project)}
/* Only targets with a free-running frame clock can report frame overruns. */
#define HAS_FRAME_CLOCK {1 if project.target.platform is TargetPlatform.SPECTRUM else 0}

#endif
"""


def render_state_header() -> str:
    """Declarations for the observable state contract, for a program to define."""
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
    lines.extend(["", "#endif", ""])
    return "\n".join(lines)
