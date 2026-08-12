"""Deterministic level content: terrain grids and entity spawn placement.

Both the built-in genre packs and the v2 to v3 migration author level content
through this module, so a migrated project and a freshly created one of the same
genre are laid out identically.

Generated terrain is connected by construction: interior obstacles are isolated
single cells that never touch each other or the surrounding wall ring, so no
floor cell can be sealed off. P2 replaces this guarantee with real solvability
analysis over authored maps.

`PILLAR_PATTERNS` cycles by level index for visual variety alone -- (4, 4),
(3, 3), (5, 2) are not ordered from sparse to dense, and nothing here asks
terrain density to track difficulty. The lever that does is spawn placement:
`default_spawns` pushes collectibles further from the player as `level_index`
rises (see its docstring), which is what `difficulty.py`'s gate actually
measures -- route length -- and it works for every terrain kind, including
`open`, where there is no terrain to densify. See
`tests/test_difficulty_escalation.py` for the exhaustive proof that this
holds for every built-in genre on every target.
"""

from __future__ import annotations

import math
from collections import deque

from .models import TILE_FLOOR, TILE_WALL, GameProject, GenreId, SpawnSpec

#: Interior obstacle spacing per level index; each pair keeps gaps of at least
#: one floor cell in both axes.
PILLAR_PATTERNS: tuple[tuple[int, int], ...] = ((4, 4), (3, 3), (5, 2))


def _blank(width: int, height: int) -> list[list[str]]:
    return [
        [
            TILE_WALL if row in (0, height - 1) or column in (0, width - 1) else TILE_FLOOR
            for column in range(width)
        ]
        for row in range(height)
    ]


def _maze(rows, width, height, index):
    step_x, step_y = PILLAR_PATTERNS[index % len(PILLAR_PATTERNS)]
    for row in range(2, height - 2):
        for column in range(2, width - 2):
            if row % step_y == 0 and column % step_x == 0:
                rows[row][column] = TILE_WALL


def _ledges(rows, width, height, index):
    """Horizontal platforms with a gap, staggered so a climb is possible."""
    span = max(4, width // 4)
    for number, row in enumerate(range(3, height - 2, 4)):
        offset = (number + index) % 2
        start = 2 + offset * span
        for column in range(start, min(width - 2, start + span * 2)):
            rows[row][column] = TILE_WALL


def _corridors(rows, width, height, index):
    """Serpentine lanes: full-width walls with one alternating opening."""
    for number, row in enumerate(range(3, height - 2, 3)):
        gap = 1 if (number + index) % 2 else width - 2
        for column in range(1, width - 1):
            if column != gap:
                rows[row][column] = TILE_WALL


def _chambers(rows, width, height, index):
    """Four rooms around a cross wall.

    The dividing wall needs a doorway on each side of the other wall, or a
    quadrant ends up sealed off with no way in. Cutting one doorway per wall
    looks symmetric and is wrong; the solvability gate rejects it.
    """
    middle_row = height // 2
    middle_col = width // 2
    left_door = 1 + (index * 3) % max(1, middle_col - 2)
    right_door = middle_col + 1 + (index * 2) % max(1, width - middle_col - 3)
    top_door = 1 + (index * 2) % max(1, middle_row - 2)
    bottom_door = middle_row + 1 + (index * 3) % max(1, height - middle_row - 3)
    for column in range(1, width - 1):
        if column not in (left_door, right_door):
            rows[middle_row][column] = TILE_WALL
    for row in range(1, height - 1):
        if row in (top_door, bottom_door) or row == middle_row:
            continue
        rows[row][middle_col] = TILE_WALL


#: How each terrain kind carves the interior. "open" leaves it bare.
TERRAIN_SHAPERS = {
    "maze": _maze,
    "ledges": _ledges,
    "corridors": _corridors,
    "chambers": _chambers,
}


def default_tiles(
    genre: str, width: int, height: int, level_index: int, terrain: str | None = None
) -> list[str]:
    """Return one terrain row per level row.

    Terrain is named by the genre pack. It is passed explicitly where known so
    that adding a typology needs no change here; the genre name is only
    consulted as a fallback for designs written before packs carried terrain.
    """
    if terrain is None:
        terrain = "maze" if genre == GenreId.MAZE_CHASE.value else "open"
    rows = _blank(width, height)
    shaper = TERRAIN_SHAPERS.get(terrain)
    if shaper is not None:
        shaper(rows, width, height, level_index)
    return ["".join(row) for row in rows]


def _floor_cells(tiles: list[str]) -> list[tuple[int, int]]:
    return [
        (column, row)
        for row, line in enumerate(tiles)
        for column, tile in enumerate(line)
        if tile == TILE_FLOOR
    ]


def _player_cell(tiles: list[str], width: int, height: int) -> tuple[int, int]:
    """The grid centre, or the reachable floor cell closest to it.

    A pillar or a chamber wall can land exactly on the centre cell (`chambers`
    always does, since its dividing walls cross there). Falling back to
    whichever floor cell happens to come first in reading order used to plant
    the player in a top-left corner whenever that happened -- fine for
    solvability, but it collapses the reachable area available to spawn
    placement on one side of the level. Nearest-to-centre keeps the player
    roughly where a design intends it and keeps spawn placement's reachable
    area roughly symmetric, level to level.
    """
    preferred = (width // 2, height // 2)
    if tiles[preferred[1]][preferred[0]] == TILE_FLOOR:
        return preferred
    return min(
        _floor_cells(tiles),
        key=lambda cell: abs(cell[0] - preferred[0]) + abs(cell[1] - preferred[1]),
    )


def _distances(tiles: list[str], width: int, height: int, start: tuple[int, int]) -> dict:
    """Four-connected BFS step counts from `start` over floor cells.

    Shared by spawn placement so "furthest from the player" and "how far
    around the ring to place a collectible" both read the level's actual
    connectivity rather than raw straight-line distance, which a maze pillar
    or a ledge gap can make a poor stand-in for.
    """
    seen = {start: 0}
    queue: deque[tuple[int, int]] = deque([start])
    while queue:
        col, row = queue.popleft()
        step = seen[(col, row)] + 1
        for next_col, next_row in (
            (col + 1, row),
            (col - 1, row),
            (col, row + 1),
            (col, row - 1),
        ):
            if not (0 <= next_col < width and 0 <= next_row < height):
                continue
            if tiles[next_row][next_col] == TILE_WALL:
                continue
            if (next_col, next_row) in seen:
                continue
            seen[(next_col, next_row)] = step
            queue.append((next_col, next_row))
    return seen


#: Fraction of the reachable pool's furthest distance that collectibles are
#: aimed at, as a function of level index: 0.15 on level 1, 0.425 on level 2,
#: capped at 0.9 from level 3 on. This is the difficulty lever -- each rise
#: pushes the whole ring of collectibles further from the player, so the
#: greedy route `difficulty.py` measures grows with it. Chosen empirically
#: (see `tests/test_difficulty_escalation.py`) to clear every built-in
#: genre's route-length gate with margin, on both targets, while still
#: leaving level 1 enough room that its collectibles are not all mutually
#: adjacent -- a ring pulled in too tight reads as one clump, not a level.
SPAWN_RADIUS_MIN_FRACTION = 0.15
SPAWN_RADIUS_STEP_FRACTION = 0.275
SPAWN_RADIUS_MAX_FRACTION = 0.9


def default_spawns(
    entities: list, tiles: list[str], width: int, height: int, level_index: int
) -> list[SpawnSpec]:
    """Place every entity instance on a distinct, reachable floor cell.

    Collectibles are aimed at points spread evenly around the player at a
    target radius that grows with `level_index` (see `SPAWN_RADIUS_*`), so
    later levels require a longer route to gather everything -- the signal
    `difficulty.py` reads back out as "harder". Enemies still take the cells
    furthest from the player regardless of level, so a level never opens with
    one already on top of the player; that policy is level-index independent
    on purpose; the schema cannot vary an enemy's count or speed per level, so
    only its distance from the player is worth escalating on this axis, and
    the far cells it needs are excluded from the collectible pool first.
    """
    player_cell = _player_cell(tiles, width, height)
    reach = _distances(tiles, width, height, player_cell)
    available = sorted(
        (cell for cell in reach if cell != player_cell), key=lambda cell: reach[cell]
    )

    enemy_total = sum(entity.count for entity in entities if entity.role == "enemy")
    needed = sum(entity.count for entity in entities if entity.role not in {"player", "enemy"})
    if needed + enemy_total > len(available):
        raise ValueError(
            f"level {level_index + 1} has {len(available)} free floor cells "
            f"for {needed + enemy_total} entity instances"
        )

    # Furthest first, so the nearest of the reserved cells goes to the first
    # enemy instance -- an arbitrary but deterministic assignment order.
    enemy_cells = list(reversed(available[len(available) - enemy_total :])) if enemy_total else []
    pool = available[: len(available) - enemy_total] if enemy_total else list(available)

    chosen: list[tuple[int, int]] = []
    if needed:
        radius_fraction = min(
            SPAWN_RADIUS_MAX_FRACTION,
            SPAWN_RADIUS_MIN_FRACTION + level_index * SPAWN_RADIUS_STEP_FRACTION,
        )
        furthest = max((reach[cell] for cell in pool), default=0)
        target_radius = radius_fraction * furthest
        player_col, player_row = player_cell
        remaining = list(pool)
        for index in range(needed):
            angle = 2 * math.pi * index / needed
            target_col = player_col + target_radius * math.cos(angle)
            target_row = player_row + target_radius * math.sin(angle)
            nearest = min(
                remaining,
                key=lambda cell: (cell[0] - target_col) ** 2 + (cell[1] - target_row) ** 2,
            )
            chosen.append(nearest)
            remaining.remove(nearest)

    enemy_supply = list(enemy_cells)
    spawns = [
        SpawnSpec(entity=entity.id, col=player_cell[0], row=player_cell[1])
        for entity in entities
        if entity.role == "player"
    ]
    cursor = 0
    for entity in entities:
        if entity.role == "player":
            continue
        for _ in range(entity.count):
            column, row = enemy_supply.pop(0) if entity.role == "enemy" else chosen[cursor]
            if entity.role != "enemy":
                cursor += 1
            spawns.append(SpawnSpec(entity=entity.id, col=column, row=row))
    return spawns


def relayout(
    project: GameProject, *, width: int | None = None, height: int | None = None
) -> GameProject:
    """Re-author every level for the project's current entities.

    Changing an entity count invalidates the spawn lists of every level. This
    rebuilds them so the design stays valid, and is the operation an editor
    performs after an entity edit or a level resize. Terrain and spawns are
    rewritten together because a resize can move a spawn into a wall.
    """
    document = project.model_dump(mode="json")
    for index, level in enumerate(document["levels"]):
        level["width"] = width if width is not None else level["width"]
        level["height"] = height if height is not None else level["height"]
        width_value = level["width"]
        height_value = level["height"]
        tiles = default_tiles(project.genre, width_value, height_value, index)
        level["tiles"] = tiles
        level["spawns"] = [
            spawn.model_dump(mode="json")
            for spawn in default_spawns(project.entities, tiles, width_value, height_value, index)
        ]
    return GameProject.model_validate(document)
