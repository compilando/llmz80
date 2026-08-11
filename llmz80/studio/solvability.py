"""Reachability and time-budget analysis over authored level terrain.

The engine moves the player one cell per frame through four-connected floor,
so a level is only playable if every collectible sits in the same connected
region as the player spawn. This module proves that from `game.yml` alone, with
no build and no emulator, which is what makes it usable as an editing gate.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from .models import TILE_WALL, GameProject, LevelSpec

#: The gameplay loop advances the player at most one cell per 50 Hz frame.
PLAYER_CELLS_PER_SECOND = 50

Cell = tuple[int, int]


@dataclass(frozen=True)
class LevelSolvability:
    level_id: str
    total_floor: int
    reachable_floor: int
    collectible_count: int
    unreachable_collectibles: tuple[Cell, ...] = ()
    unreachable_enemies: tuple[Cell, ...] = ()
    #: Steps to the collectible furthest from the spawn; a lower bound on any
    #: route that collects everything.
    minimum_steps: int = 0
    #: Greedy nearest-first route length, reported as a realistic expectation.
    estimated_steps: int = 0
    time_limit_seconds: int | None = None
    time_limit_feasible: bool = True

    @property
    def solvable(self) -> bool:
        return not self.unreachable_collectibles and self.time_limit_feasible

    def as_dict(self) -> dict:
        return {
            "level": self.level_id,
            "total_floor": self.total_floor,
            "reachable_floor": self.reachable_floor,
            "collectible_count": self.collectible_count,
            "unreachable_collectibles": [list(cell) for cell in self.unreachable_collectibles],
            "unreachable_enemies": [list(cell) for cell in self.unreachable_enemies],
            "minimum_steps": self.minimum_steps,
            "estimated_steps": self.estimated_steps,
            "time_limit_seconds": self.time_limit_seconds,
            "time_limit_feasible": self.time_limit_feasible,
            "solvable": self.solvable,
        }


@dataclass
class SolvabilityReport:
    levels: list[LevelSolvability] = field(default_factory=list)

    @property
    def solvable(self) -> bool:
        return all(level.solvable for level in self.levels)

    @property
    def failures(self) -> list[str]:
        reasons: list[str] = []
        for level in self.levels:
            if level.unreachable_collectibles:
                cells = ", ".join(f"({col}, {row})" for col, row in level.unreachable_collectibles)
                reasons.append(
                    f"{level.level_id}: walls seal off {len(level.unreachable_collectibles)} "
                    f"collectible(s) at {cells}"
                )
            if not level.time_limit_feasible:
                reasons.append(
                    f"{level.level_id}: {level.time_limit_seconds}s allows "
                    f"{level.time_limit_seconds * PLAYER_CELLS_PER_SECOND} steps but collecting "
                    f"everything needs at least {level.minimum_steps}"
                )
        return reasons

    def as_dict(self) -> dict:
        return {
            "schema_version": 1,
            "solvable": self.solvable,
            "failures": self.failures,
            "levels": [level.as_dict() for level in self.levels],
        }


def _distances(level: LevelSpec, start: Cell) -> dict[Cell, int]:
    """Breadth-first step counts from `start` over four-connected floor."""
    seen = {start: 0}
    queue: deque[Cell] = deque([start])
    while queue:
        col, row = queue.popleft()
        step = seen[(col, row)] + 1
        for next_col, next_row in (
            (col + 1, row),
            (col - 1, row),
            (col, row + 1),
            (col, row - 1),
        ):
            if not (0 <= next_col < level.width and 0 <= next_row < level.height):
                continue
            if level.tiles[next_row][next_col] == TILE_WALL:
                continue
            if (next_col, next_row) in seen:
                continue
            seen[(next_col, next_row)] = step
            queue.append((next_col, next_row))
    return seen


def _greedy_route(level: LevelSpec, start: Cell, targets: list[Cell]) -> int:
    """Length of a nearest-first route visiting every reachable target."""
    remaining = list(targets)
    position = start
    total = 0
    while remaining:
        reach = _distances(level, position)
        candidates = [(reach[cell], cell) for cell in remaining if cell in reach]
        if not candidates:
            break
        step, chosen = min(candidates)
        total += step
        position = chosen
        remaining.remove(chosen)
    return total


def analyse_level(project: GameProject, level: LevelSpec) -> LevelSolvability:
    roles = {entity.id: entity.role for entity in project.entities}
    player_cells = [
        (spawn.col, spawn.row) for spawn in level.spawns if roles.get(spawn.entity) == "player"
    ]
    collectibles = [
        (spawn.col, spawn.row) for spawn in level.spawns if roles.get(spawn.entity) == "collectible"
    ]
    enemies = [
        (spawn.col, spawn.row) for spawn in level.spawns if roles.get(spawn.entity) == "enemy"
    ]
    total_floor = sum(row.count(".") for row in level.tiles)

    if not player_cells:
        return LevelSolvability(
            level_id=level.id,
            total_floor=total_floor,
            reachable_floor=0,
            collectible_count=len(collectibles),
            unreachable_collectibles=tuple(collectibles),
            unreachable_enemies=tuple(enemies),
            time_limit_seconds=level.time_limit_seconds,
        )

    reach = _distances(level, player_cells[0])
    unreachable = tuple(cell for cell in collectibles if cell not in reach)
    reachable_targets = [cell for cell in collectibles if cell in reach]
    minimum_steps = max((reach[cell] for cell in reachable_targets), default=0)
    estimated_steps = _greedy_route(level, player_cells[0], reachable_targets)

    feasible = True
    if level.time_limit_seconds is not None:
        budget = level.time_limit_seconds * PLAYER_CELLS_PER_SECOND
        feasible = budget >= minimum_steps

    return LevelSolvability(
        level_id=level.id,
        total_floor=total_floor,
        reachable_floor=len(reach),
        collectible_count=len(collectibles),
        unreachable_collectibles=unreachable,
        unreachable_enemies=tuple(cell for cell in enemies if cell not in reach),
        minimum_steps=minimum_steps,
        estimated_steps=estimated_steps,
        time_limit_seconds=level.time_limit_seconds,
        time_limit_feasible=feasible,
    )


#: Directions a swept key can move the player, as (name, column step, row step).
SWEEP_DIRECTIONS = (("right", 1, 0), ("left", -1, 0), ("down", 0, 1), ("up", 0, -1))


def sweep_plan(project: GameProject, level_index: int = 0) -> dict:
    """Pick one held direction that provably collects something.

    Holding a single key is the only input a bounded emulator run can deliver
    reliably: exact per-cell steps would need frame-accurate key timing the
    remote protocol cannot promise. Sweeping until a wall stops the player is
    timing independent, so the expected score becomes an exact assertion.
    """
    level = project.levels[level_index]
    roles = {entity.id: entity.role for entity in project.entities}
    player = next(
        ((spawn.col, spawn.row) for spawn in level.spawns if roles.get(spawn.entity) == "player"),
        None,
    )
    collectibles = {
        (spawn.col, spawn.row)
        for spawn in level.spawns
        if roles.get(spawn.entity) == "collectible"
    }
    best = {"direction": None, "collected": 0, "distance": 0}
    if player is None:
        return best
    for name, step_col, step_row in SWEEP_DIRECTIONS:
        col, row = player
        collected = 0
        steps = 0
        furthest = 0
        while True:
            col += step_col
            row += step_row
            if not (0 <= col < level.width and 0 <= row < level.height):
                break
            if level.tiles[row][col] == TILE_WALL:
                break
            steps += 1
            if (col, row) in collectibles:
                collected += 1
                # Only travel as far as the last collectible actually needs.
                furthest = steps
        if collected > best["collected"]:
            best = {"direction": name, "collected": collected, "distance": furthest}
    return best


def solvability_report(project: GameProject) -> SolvabilityReport:
    return SolvabilityReport([analyse_level(project, level) for level in project.levels])
