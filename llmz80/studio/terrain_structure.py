"""Does a level's terrain carry the shape its typology promises?

Solvability proves a level can be finished; it says nothing about whether
finishing it means anything. An empty bordered room is trivially solvable
because every cell reaches every other cell, but a `maze_chase` with no
interior walls is not a maze -- it is a field with pellets scattered on it.
This module catches that gap: it checks that a level's interior wall layout
has the structure its genre pack's `terrain` kind implies, calibrated against
what `layout.py`'s own deterministic generators produce for that kind.

Two cheap measures are enough to catch the failures worth catching:

* interior wall ratio -- how much of the interior (excluding the border
  ring) is wall. Zero ratio is an empty room.
* interior wall components -- how many separate, non-touching wall shapes
  the interior holds, four-connected. A single solid block of wall (one
  component) can carry the same ratio as a real maze while offering none of
  its structure, so ratio alone cannot tell them apart; a low component
  count catches it.

Terrain kinds `layout.py` deliberately leaves bare (`open`, and anything not
in `TERRAIN_SHAPERS`) are exempt: a shooter arena or a snake grid is correct
with no interior walls at all, and holding it to a maze's standard would
reject a legitimate design.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from .layout import TERRAIN_SHAPERS
from .models import TILE_WALL, GameProject, GenreId, LevelSpec
from .packs import PACKS_BY_ID

Cell = tuple[int, int]

#: (minimum interior wall ratio, minimum interior wall components) per terrain
#: kind, derived from `layout.py`'s generators across the level sizes Studio
#: actually authors (its fixed 20x16 default and the wider range an editor's
#: resize can request), then halved or better for margin. A level `layout.py`
#: generates must clear these with room to spare; see
#: `tests/test_terrain_structure.py` for the exhaustive check that it does.
TERRAIN_THRESHOLDS: dict[str, tuple[float, int]] = {
    "maze": (0.02, 4),
    "ledges": (0.04, 2),
    "corridors": (0.10, 2),
    "chambers": (0.04, 2),
}


@dataclass(frozen=True)
class LevelStructure:
    level_id: str
    terrain: str
    exempt: bool
    interior_cells: int
    wall_cells: int
    wall_ratio: float
    wall_components: int
    min_wall_ratio: float
    min_wall_components: int

    @property
    def structured(self) -> bool:
        """Whether this level's terrain carries its typology's shape.

        Exempt terrain kinds (open arenas and anything `layout.py` does not
        shape) pass unconditionally; nothing about them implies structure.
        """
        if self.exempt:
            return True
        return (
            self.wall_ratio >= self.min_wall_ratio
            and self.wall_components >= self.min_wall_components
        )

    def as_dict(self) -> dict:
        return {
            "level": self.level_id,
            "terrain": self.terrain,
            "exempt": self.exempt,
            "interior_cells": self.interior_cells,
            "wall_cells": self.wall_cells,
            "wall_ratio": self.wall_ratio,
            "wall_components": self.wall_components,
            "min_wall_ratio": self.min_wall_ratio,
            "min_wall_components": self.min_wall_components,
            "structured": self.structured,
        }


@dataclass
class StructureReport:
    levels: list[LevelStructure] = field(default_factory=list)

    @property
    def structured(self) -> bool:
        return all(level.structured for level in self.levels)

    @property
    def failures(self) -> list[str]:
        reasons: list[str] = []
        for level in self.levels:
            if level.structured:
                continue
            reasons.append(
                f"{level.level_id}: {level.terrain} terrain has wall ratio "
                f"{level.wall_ratio:.3f} (needs >= {level.min_wall_ratio}) across "
                f"{level.wall_components} separate wall shape(s) (needs >= "
                f"{level.min_wall_components}) -- not enough interior structure "
                f"for a {level.terrain} level"
            )
        return reasons

    def as_dict(self) -> dict:
        return {
            "schema_version": 1,
            "structured": self.structured,
            "failures": self.failures,
            "levels": [level.as_dict() for level in self.levels],
        }


def _project_terrain(project: GameProject) -> str:
    """The terrain kind a project's genre implies.

    Mirrors `default_tiles`'s own fallback in `layout.py`: a pack lookup
    first, and for designs written before packs carried terrain, the same
    genre-name special case that module uses.
    """
    pack = PACKS_BY_ID.get(project.genre)
    if pack is not None:
        return pack.terrain
    return "maze" if project.genre == GenreId.MAZE_CHASE.value else "open"


def _interior_wall_components(tiles: list[str], width: int, height: int) -> int:
    """Count four-connected wall shapes inside the border ring."""
    seen: set[Cell] = set()
    components = 0
    for row in range(1, height - 1):
        for col in range(1, width - 1):
            if tiles[row][col] != TILE_WALL or (col, row) in seen:
                continue
            components += 1
            seen.add((col, row))
            queue: deque[Cell] = deque([(col, row)])
            while queue:
                c, r = queue.popleft()
                for nc, nr in ((c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1)):
                    if not (1 <= nc < width - 1 and 1 <= nr < height - 1):
                        continue
                    if tiles[nr][nc] != TILE_WALL or (nc, nr) in seen:
                        continue
                    seen.add((nc, nr))
                    queue.append((nc, nr))
    return components


def analyse_level_structure(terrain: str, level: LevelSpec) -> LevelStructure:
    interior_cells = max(0, level.width - 2) * max(0, level.height - 2)
    wall_cells = sum(
        row[1 : level.width - 1].count(TILE_WALL) for row in level.tiles[1 : level.height - 1]
    )
    ratio = wall_cells / interior_cells if interior_cells else 0.0
    components = _interior_wall_components(level.tiles, level.width, level.height)
    exempt = terrain not in TERRAIN_THRESHOLDS
    min_ratio, min_components = TERRAIN_THRESHOLDS.get(terrain, (0.0, 0))
    return LevelStructure(
        level_id=level.id,
        terrain=terrain,
        exempt=exempt,
        interior_cells=interior_cells,
        wall_cells=wall_cells,
        wall_ratio=ratio,
        wall_components=components,
        min_wall_ratio=min_ratio,
        min_wall_components=min_components,
    )


def structure_report(project: GameProject) -> StructureReport:
    terrain = _project_terrain(project)
    return StructureReport([analyse_level_structure(terrain, level) for level in project.levels])


#: Exposed for tests that want to confirm the shaped terrain kinds line up
#: with what this module holds to account.
STRUCTURED_TERRAIN_KINDS = frozenset(TERRAIN_SHAPERS)
