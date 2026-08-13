"""Whole-design validation: do the pieces refer to each other, and does the
result fit the machine.

Every check here is answerable by looking at the document and at the target's
character grid. Nothing here knows what a game is: it does not ask whether a
level is solvable, whether difficulty rises, or whether an actor may stand on a
cell some trait calls solid. Those were rules about one kind of game, and they
are why eighteen typologies produced one.
"""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from llmz80.core.state_contract import SYMBOLS_BY_NAME

if TYPE_CHECKING:  # pragma: no cover - import cycle guard only
    from .models import GameProject

#: Character-cell grid available on each target, as (columns, rows).
TARGET_GRID: dict[str, tuple[int, int]] = {
    "spectrum_bitmap": (32, 24),
    "cpc_mode_0": (20, 25),
    "cpc_mode_1": (40, 25),
}

#: Character rows reserved at the top for a HUD.
FIELD_TOP = 2


def playfield(project: "GameProject") -> tuple[int, int]:
    """Playfield size in cells once the HUD rows are taken out."""
    columns, rows = TARGET_GRID[project.target.video_mode.value]
    return columns, rows - FIELD_TOP


def structural_errors(project: "GameProject") -> list[str]:
    """Every way this design fails to refer to itself, or to fit its machine."""
    errors: list[str] = []
    errors += _tile_errors(project)
    errors += _reference_errors(project)
    errors += _screen_errors(project)
    errors += _observable_errors(project)
    errors += _scene_errors(project)
    return errors


def _tile_errors(project: "GameProject") -> list[str]:
    errors = []
    ids = Counter(tile.id for tile in project.tiles)
    for tile_id, count in sorted(ids.items()):
        if count > 1:
            errors.append(f"tile id {tile_id!r} is declared {count} times")
    chars = Counter(tile.char for tile in project.tiles)
    for char, count in sorted(chars.items()):
        if count > 1:
            errors.append(f"two tiles share the character {char!r}")
    return errors


def _reference_errors(project: "GameProject") -> list[str]:
    """Palette and asset ids named by tiles and entities must exist."""
    errors = []
    palette = {entry.id for entry in project.presentation.palette}
    assets = {asset.id for asset in project.assets}
    for tile in project.tiles:
        if tile.colour and tile.colour not in palette:
            errors.append(f"tile {tile.id} names undeclared palette entry {tile.colour!r}")
        if tile.art and tile.art not in assets:
            errors.append(f"tile {tile.id} names undeclared asset {tile.art!r}")
    entity_ids = Counter(entity.id for entity in project.entities)
    for entity_id, count in sorted(entity_ids.items()):
        if count > 1:
            errors.append(f"entity id {entity_id!r} is declared {count} times")
    for entity in project.entities:
        if entity.colour and entity.colour not in palette:
            errors.append(f"entity {entity.id} names undeclared palette entry {entity.colour!r}")
    return errors


def _screen_errors(project: "GameProject") -> list[str]:
    errors = []
    known_chars = {tile.char for tile in project.tiles}
    declared = {entity.id: entity.count for entity in project.entities}
    screen_ids = [screen.id for screen in project.screens]
    duplicated = sorted({name for name in screen_ids if screen_ids.count(name) > 1})
    errors += [f"screen id {name!r} is declared twice" for name in duplicated]
    columns, rows = playfield(project)
    for screen in project.screens:
        if screen.width > columns or screen.height > rows:
            errors.append(
                f"screen {screen.id} is {screen.width}x{screen.height} but "
                f"{project.target.video_mode.value} offers {columns}x{rows} playable cells"
            )
        for row in screen.tiles:
            for char in row:
                if char not in known_chars:
                    errors.append(f"screen {screen.id} uses undeclared tile character {char!r}")
                    break
            else:
                continue
            break
        placed = Counter(spawn.entity for spawn in screen.spawns)
        for entity, count in sorted(placed.items()):
            if entity not in declared:
                errors.append(f"screen {screen.id} spawns unknown entity {entity!r}")
            elif count > declared[entity]:
                errors.append(
                    f"screen {screen.id} places {entity} {count} times but "
                    f"declares {declared[entity]}"
                )
        if len(screen.spawns) > project.budgets.max_entities:
            errors.append(
                f"screen {screen.id} places {len(screen.spawns)} actors, which "
                f"exceeds the max_entities budget of {project.budgets.max_entities}"
            )
        for direction, destination in sorted(screen.exits.items()):
            if destination not in screen_ids:
                errors.append(
                    f"screen {screen.id} exits {direction} to unknown screen " f"{destination!r}"
                )
    if project.initial_screen not in screen_ids:
        errors.append("initial_screen names no declared screen")
    return errors


def _observable_errors(project: "GameProject") -> list[str]:
    errors = []
    seen: set[str] = set()
    for observable in project.observables:
        if observable.symbol in SYMBOLS_BY_NAME:
            errors.append(f"observable {observable.symbol} is already in the state contract")
        if observable.symbol in seen:
            errors.append(f"observable {observable.symbol} is declared twice")
        seen.add(observable.symbol)
    return errors


def _scene_errors(project: "GameProject") -> list[str]:
    errors = []
    scene_ids = [scene.id for scene in project.scenes]
    if len(scene_ids) != len(set(scene_ids)):
        errors.append("scene ids must be unique")
    if project.initial_scene not in scene_ids:
        errors.append("initial_scene must reference an existing scene")
    references = [scene.next_scene for scene in project.scenes if scene.next_scene]
    references += [option.target_scene for scene in project.scenes for option in scene.options]
    unknown = sorted(set(references) - set(scene_ids))
    if unknown:
        errors.append("unknown scene references: " + ", ".join(unknown))
    return errors
