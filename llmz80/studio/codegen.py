"""Emit project data for the versioned Studio engine.

The generator only produces tables and configuration. Gameplay logic lives in
``resources/studio_engine`` and is compiled unchanged by both toolchains, so a
design change can never silently rewrite engine behaviour.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .models import AUDIO_EFFECTS, TILE_WALL, GameProject, TargetPlatform, VideoMode

ENGINE_ROOT = Path(__file__).resolve().parents[2] / "resources" / "studio_engine"

#: Character rows reserved at the top of the screen for the HUD.
FIELD_TOP = 2

#: Character-cell grid available on each target, as (columns, rows).
TARGET_GRID: dict[VideoMode, tuple[int, int]] = {
    VideoMode.SPECTRUM_BITMAP: (32, 24),
    VideoMode.CPC_MODE_0: (20, 25),
    VideoMode.CPC_MODE_1: (40, 25),
}

BEHAVIOUR_STATIC = 0
BEHAVIOUR_PLAYER = 1
BEHAVIOUR_PATROL_H = 2
BEHAVIOUR_PATROL_V = 3
BEHAVIOUR_BOUNCE = 4
BEHAVIOUR_CHASE = 5
BEHAVIOUR_GUARD = 6

#: Designed enemy behaviours, mirrored by the constants in engine.h.
BEHAVIOUR_CODES = {
    "patrol_h": BEHAVIOUR_PATROL_H,
    "patrol_v": BEHAVIOUR_PATROL_V,
    "bounce": BEHAVIOUR_BOUNCE,
    "chase": BEHAVIOUR_CHASE,
    "guard": BEHAVIOUR_GUARD,
}

#: Cells between a guard and the player before the guard gives chase.
GUARD_WAKE_DISTANCE = 5

CELL_PLAYER = 1
CELL_ENEMY = 2
CELL_COLLECTIBLE = 3

DIFFICULTY_CURVES = {"flat": 0, "linear": 1, "stepped": 2}

#: Roles the current engine can represent. Others are refused rather than faked.
SUPPORTED_ROLES = {"player", "enemy", "collectible"}


@dataclass(frozen=True)
class Actor:
    """One concrete instance expanded from an `EntitySpec` count."""

    source_id: str
    instance: int
    kind: int
    behaviour: int
    speed: int


def playfield(project: GameProject) -> tuple[int, int]:
    """Return the playfield size in cells, excluding the HUD rows."""
    columns, rows = TARGET_GRID[project.target.video_mode]
    return columns, rows - FIELD_TOP


def build_actors(project: GameProject) -> list[Actor]:
    """Expand entity counts into the flat actor table the engine iterates."""
    actors: list[Actor] = []
    enemy_index = 0
    for entity in project.entities:
        for instance in range(entity.count):
            if entity.role == "player":
                actors.append(
                    Actor(entity.id, instance, CELL_PLAYER, BEHAVIOUR_PLAYER, entity.speed)
                )
            elif entity.role == "enemy":
                if entity.behaviour == "auto":
                    behaviour = BEHAVIOUR_PATROL_H if enemy_index % 2 == 0 else BEHAVIOUR_PATROL_V
                else:
                    behaviour = BEHAVIOUR_CODES[entity.behaviour]
                enemy_index += 1
                actors.append(Actor(entity.id, instance, CELL_ENEMY, behaviour, entity.speed))
            else:
                actors.append(
                    Actor(entity.id, instance, CELL_COLLECTIBLE, BEHAVIOUR_STATIC, entity.speed)
                )
    # The player must be first so the engine finds it before any collision test.
    # A stable sort keeps each entity's instances in their authored order.
    actors.sort(key=lambda actor: 0 if actor.behaviour == BEHAVIOUR_PLAYER else 1)
    return actors


def spawn_table(project: GameProject, actors: list[Actor]) -> list[list[tuple[int, int]]]:
    """Map every actor to its authored spawn cell, per level.

    Cross-field validation on `GameProject` guarantees each entity has exactly
    `count` spawns per level, so instance indexing is total.
    """
    table: list[list[tuple[int, int]]] = []
    for level in project.levels:
        by_entity: dict[str, list[tuple[int, int]]] = {}
        for spawn in level.spawns:
            by_entity.setdefault(spawn.entity, []).append((spawn.col, spawn.row))
        positions: list[tuple[int, int]] = []
        for actor in actors:
            cells = by_entity.get(actor.source_id, ())
            if actor.instance >= len(cells):
                raise ValueError(
                    f"level {level.id} places {len(cells)} spawns for {actor.source_id} but the "
                    f"design declares more instances; re-author the level layout"
                )
            positions.append(cells[actor.instance])
        table.append(positions)
    return table


def tile_bitmaps(project: GameProject) -> tuple[list[int], list[int]]:
    """Pack level terrain into wall bits, returning the bytes and per-level offsets.

    One bit per cell, row-major and most-significant bit first. Each level starts
    on a byte boundary so the engine can index it from a single offset.
    """
    packed: list[int] = []
    offsets: list[int] = []
    for level in project.levels:
        offsets.append(len(packed))
        bits: list[int] = []
        for row in level.tiles:
            bits.extend(1 if tile == TILE_WALL else 0 for tile in row)
        for start in range(0, len(bits), 8):
            chunk = bits[start:start + 8]
            value = 0
            for position, bit in enumerate(chunk):
                value |= bit << (7 - position)
            packed.append(value)
    return packed, offsets


def _c_text(value: str, limit: int) -> str:
    ascii_only = value.encode("ascii", "replace").decode("ascii")
    return ascii_only.replace("\\", " ").replace('"', "'")[:limit]


def _array(name: str, values: list[int], element: str = "unsigned char") -> str:
    body = ", ".join(str(value) for value in values)
    return f"const {element} {name}[{len(values)}] = {{{body}}};"


def audio_mask(project: GameProject) -> int:
    """Bitmask of enabled effects, positioned by their engine constant."""
    mask = 0
    for index, effect in enumerate(AUDIO_EFFECTS):
        if effect in project.audio.effects:
            mask |= 1 << index
    return mask


def render_config_header(project: GameProject) -> str:
    actors = build_actors(project)
    cpc_mode = 0 if project.target.video_mode is VideoMode.CPC_MODE_0 else 1
    scheme = 1 if project.controls.scheme == "cursor_space" else 0
    return f"""/* Generated by LLMZ80 Studio from game.yml. Do not edit directly. */
#ifndef LLMZ80_GAME_CONFIG_H
#define LLMZ80_GAME_CONFIG_H

#define MAX_ACTORS {len(actors)}
#define MAX_LEVEL_HEIGHT {max(level.height for level in project.levels)}
#define LEVEL_COUNT {project.gameplay.level_count}
#define START_LIVES {project.gameplay.lives}
#define WIN_SCORE {project.gameplay.win_score}
#define SCORE_PER_COLLECTIBLE {project.gameplay.score_per_collectible}
#define DIFFICULTY_CURVE {DIFFICULTY_CURVES[project.gameplay.difficulty_curve]}
#define CONTROL_SCHEME {scheme}
#define CPC_MODE {cpc_mode}
#define GUARD_WAKE_DISTANCE {GUARD_WAKE_DISTANCE}
/* One bit per effect, in AUDIO_EFFECTS order; zero means the design is silent. */
#define AUDIO_EFFECT_MASK {audio_mask(project)}
/* Only targets with a free-running frame clock can report frame overruns. */
#define HAS_FRAME_CLOCK {1 if project.target.platform is TargetPlatform.SPECTRUM else 0}

#endif
"""


def render_game_data(project: GameProject) -> str:
    actors = build_actors(project)
    table = spawn_table(project, actors)
    walls, wall_offsets = tile_bitmaps(project)
    controls = (
        f"{project.controls.up}{project.controls.down}"
        f"{project.controls.left}{project.controls.right} MOVE"
        if project.controls.scheme == "qaop_space"
        else "CURSORS MOVE"
    )
    lines = [
        "/* Generated by LLMZ80 Studio from game.yml. Do not edit directly. */",
        '#include "engine.h"',
        "",
        f"const unsigned char g_actor_count = {len(actors)};",
        _array("g_actor_kind", [actor.kind for actor in actors]),
        _array("g_actor_speed", [actor.speed for actor in actors]),
        _array("g_actor_behaviour", [actor.behaviour for actor in actors]),
        _array("g_level_width", [level.width for level in project.levels]),
        _array("g_level_height", [level.height for level in project.levels]),
        _array("g_spawn_col", [cell[0] for level in table for cell in level]),
        _array("g_spawn_row", [cell[1] for level in table for cell in level]),
        _array("g_wall_bits", walls),
        _array("g_wall_offset", wall_offsets, element="unsigned int"),
        f'const char g_title_text[] = "{_c_text(project.metadata.title.upper(), 24)}";',
        f'const char g_controls_text[] = "{_c_text(controls.upper(), 24)}";',
        "",
    ]
    return "\n".join(lines)


def render_main(project: GameProject) -> str:
    return f"""/* Generated by LLMZ80 Studio from game.yml. Do not edit directly.
 * Project: {_c_text(project.metadata.slug, 48)}
 * Gameplay lives in the versioned Studio engine; this file only starts it.
 */
#include "engine.h"

void main(void) {{
    engine_run();
}}
"""


def engine_sources(project: GameProject) -> list[Path]:
    """Engine files copied verbatim into the generated project."""
    target = "spectrum" if project.target.platform is TargetPlatform.SPECTRUM else "cpc"
    common = ENGINE_ROOT / "common"
    return [
        common / "platform.h",
        common / "engine.h",
        common / "engine.c",
        ENGINE_ROOT / target / "platform.c",
    ]
