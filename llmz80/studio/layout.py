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


def default_tiles(genre: str, width: int, height: int, level_index: int) -> list[str]:
    """Return one terrain row per level row."""
    walls_inside = genre == GenreId.MAZE_CHASE.value
    step_x, step_y = PILLAR_PATTERNS[level_index % len(PILLAR_PATTERNS)]
    rows: list[str] = []
    for row in range(height):
        cells: list[str] = []
        for column in range(width):
            on_border = row in (0, height - 1) or column in (0, width - 1)
            pillar = (
                walls_inside
                and 1 < row < height - 2
                and 1 < column < width - 2
                and row % step_y == 0
                and column % step_x == 0
            )
            cells.append(TILE_WALL if on_border or pillar else TILE_FLOOR)
        rows.append("".join(cells))
    return rows


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

    needed = sum(entity.count for entity in entities if entity.role != "player")
    if needed > len(available):
        raise ValueError(
            f"level {level_index + 1} has {len(available)} free floor cells "
            f"for {needed} entity instances"
        )

    # Evenly spaced indices over the supply. With needed <= len(available) these
    # are strictly increasing, so no two instances can share a cell.
    chosen = [available[(index * len(available)) // needed] for index in range(needed)]

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
            column, row = chosen[cursor]
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
