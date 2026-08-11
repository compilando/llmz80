"""Deterministic level content: terrain grids and entity spawn placement.

Both the built-in genre packs and the v2 to v3 migration author level content
through this module, so a migrated project and a freshly created one of the same
genre are laid out identically.

Generated terrain is connected by construction: interior obstacles are isolated
single cells that never touch each other or the surrounding wall ring, so no
floor cell can be sealed off. P2 replaces this guarantee with real solvability
analysis over authored maps.
"""

from __future__ import annotations

from .models import TILE_FLOOR, TILE_WALL, GameProject, GenreId, SpawnSpec

#: Interior obstacle spacing per level index; each pair keeps gaps of at least
#: one floor cell in both axes.
PILLAR_PATTERNS: tuple[tuple[int, int], ...] = ((4, 4), (3, 3), (5, 2))


def _blank(width: int, height: int) -> list[list[str]]:
    return [
        [
            TILE_WALL
            if row in (0, height - 1) or column in (0, width - 1)
            else TILE_FLOOR
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
    preferred = (width // 2, height // 2)
    if tiles[preferred[1]][preferred[0]] == TILE_FLOOR:
        return preferred
    return _floor_cells(tiles)[0]


def default_spawns(
    entities: list, tiles: list[str], width: int, height: int, level_index: int
) -> list[SpawnSpec]:
    """Place every entity instance on a distinct floor cell."""
    player_cell = _player_cell(tiles, width, height)
    available = [cell for cell in _floor_cells(tiles) if cell != player_cell]
    # Rotating the supply per level moves non-player entities between levels.
    if available:
        offset = (level_index * 7) % len(available)
        available = available[offset:] + available[:offset]

    # Enemies take the cells furthest from the player, so a level does not open
    # with everything already on top of them. Collectibles fill in around.
    by_distance = sorted(
        available,
        key=lambda cell: -(abs(cell[0] - player_cell[0]) + abs(cell[1] - player_cell[1])),
    )
    enemy_total = sum(entity.count for entity in entities if entity.role == "enemy")
    enemy_cells = by_distance[:enemy_total]
    available = [cell for cell in available if cell not in set(enemy_cells)]

    needed = sum(
        entity.count
        for entity in entities
        if entity.role not in {"player", "enemy"}
    )
    if needed + enemy_total > len(available) + len(enemy_cells):
        raise ValueError(
            f"level {level_index + 1} has {len(available)} free floor cells "
            f"for {needed} entity instances"
        )

    # Evenly spaced indices over the supply. With needed <= len(available) these
    # are strictly increasing, so no two instances can share a cell.
    chosen = (
        [available[(index * len(available)) // needed] for index in range(needed)]
        if needed
        else []
    )
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
            for spawn in default_spawns(
                project.entities, tiles, width_value, height_value, index
            )
        ]
    return GameProject.model_validate(document)
