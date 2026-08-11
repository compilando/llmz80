"""Editing operations on a `GameProject`, independent of any user interface.

Every operation takes a project and returns a new validated project, so the
terminal UI stays a renderer and the same operations can be driven by tests, a
script or a future editor. An operation that would break a hard invariant raises
`EditError` with a message meant to be shown to the user.
"""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from .compiler import validate_design_fits_target
from .layout import default_tiles
from .models import TILE_FLOOR, TILE_WALL, GameProject
from .solvability import solvability_report


class EditError(ValueError):
    """An edit the design cannot accept, phrased for the person editing."""


def _validated(document: dict[str, Any]) -> GameProject:
    try:
        return GameProject.model_validate(document)
    except ValidationError as exc:
        first = exc.errors()[0]
        message = first.get("msg", "invalid edit")
        raise EditError(message.removeprefix("Value error, ")) from exc


def _document(project: GameProject) -> dict[str, Any]:
    return project.model_dump(mode="json")


def _free_cells(level: dict[str, Any]) -> list[tuple[int, int]]:
    taken = {(spawn["col"], spawn["row"]) for spawn in level["spawns"]}
    return [
        (col, row)
        for row, line in enumerate(level["tiles"])
        for col, tile in enumerate(line)
        if tile == TILE_FLOOR and (col, row) not in taken
    ]


# --- terrain -----------------------------------------------------------------


def set_tile(project: GameProject, level_index: int, col: int, row: int, tile: str) -> GameProject:
    """Paint one cell. Walling a cell that holds a spawn is refused."""
    if tile not in (TILE_FLOOR, TILE_WALL):
        raise EditError(f"unknown tile '{tile}'")
    document = _document(project)
    try:
        level = document["levels"][level_index]
    except IndexError:
        raise EditError(f"there is no level {level_index + 1}") from None
    if not (0 <= col < level["width"] and 0 <= row < level["height"]):
        raise EditError(f"({col}, {row}) is outside the {level['width']}x{level['height']} grid")
    occupant = next(
        (
            spawn
            for spawn in level["spawns"]
            if spawn["col"] == col and spawn["row"] == row
        ),
        None,
    )
    if tile == TILE_WALL and occupant is not None:
        raise EditError(f"move {occupant['entity']} before walling ({col}, {row})")
    rows = [list(line) for line in level["tiles"]]
    rows[row][col] = tile
    level["tiles"] = ["".join(line) for line in rows]
    return _validated(document)


def toggle_tile(project: GameProject, level_index: int, col: int, row: int) -> GameProject:
    current = project.levels[level_index].tiles[row][col]
    return set_tile(
        project, level_index, col, row, TILE_FLOOR if current == TILE_WALL else TILE_WALL
    )


def fill_level(project: GameProject, level_index: int, tile: str) -> GameProject:
    """Reset terrain to the generated pattern, or clear it to open floor."""
    document = _document(project)
    level = document["levels"][level_index]
    if tile == "pattern":
        level["tiles"] = default_tiles(project.genre, level["width"], level["height"], level_index)
    elif tile == TILE_FLOOR:
        level["tiles"] = [TILE_FLOOR * level["width"] for _ in range(level["height"])]
    else:
        raise EditError("fill accepts the generated pattern or open floor")
    return _repaired(document)


# --- spawns ------------------------------------------------------------------


def move_spawn(
    project: GameProject, level_index: int, spawn_index: int, col: int, row: int
) -> GameProject:
    document = _document(project)
    level = document["levels"][level_index]
    try:
        spawn = level["spawns"][spawn_index]
    except IndexError:
        raise EditError(f"level {level['id']} has no spawn {spawn_index}") from None
    if not (0 <= col < level["width"] and 0 <= row < level["height"]):
        raise EditError(f"({col}, {row}) is outside the {level['width']}x{level['height']} grid")
    spawn["col"] = col
    spawn["row"] = row
    return _validated(document)


def _repaired(document: dict[str, Any]) -> GameProject:
    """Move spawns that terrain or a resize left in a wall or out of bounds."""
    for level in document["levels"]:
        width = level["width"]
        height = level["height"]
        placed: set[tuple[int, int]] = set()
        stranded: list[dict[str, Any]] = []
        for spawn in level["spawns"]:
            inside = 0 <= spawn["col"] < width and 0 <= spawn["row"] < height
            on_floor = inside and level["tiles"][spawn["row"]][spawn["col"]] == TILE_FLOOR
            cell = (spawn["col"], spawn["row"])
            if on_floor and cell not in placed:
                placed.add(cell)
            else:
                stranded.append(spawn)
        if not stranded:
            continue
        supply = [
            (col, row)
            for row, line in enumerate(level["tiles"])
            for col, tile in enumerate(line)
            if tile == TILE_FLOOR and (col, row) not in placed
        ]
        if len(supply) < len(stranded):
            raise EditError(
                f"level {level['id']} has {len(supply)} free floor cells for "
                f"{len(stranded)} displaced entities"
            )
        for spawn, cell in zip(stranded, supply):
            spawn["col"], spawn["row"] = cell
            placed.add(cell)
    return _validated(document)


# --- levels ------------------------------------------------------------------


def resize_level(project: GameProject, level_index: int, width: int, height: int) -> GameProject:
    """Crop or extend one level, keeping the terrain that still fits."""
    document = _document(project)
    level = document["levels"][level_index]
    old = level["tiles"]
    rows = []
    for row in range(height):
        source = old[row] if row < len(old) else ""
        line = [
            source[col] if col < len(source) else TILE_FLOOR
            for col in range(width)
        ]
        rows.append("".join(line))
    level["width"] = width
    level["height"] = height
    level["tiles"] = rows
    return _repaired(document)


def rename_level(project: GameProject, level_index: int, name: str) -> GameProject:
    document = _document(project)
    document["levels"][level_index]["name"] = name.strip()
    return _validated(document)


def set_time_limit(project: GameProject, level_index: int, seconds: int | None) -> GameProject:
    document = _document(project)
    document["levels"][level_index]["time_limit_seconds"] = seconds
    return _validated(document)


# --- entities ----------------------------------------------------------------


def set_entity_count(project: GameProject, entity_id: str, count: int) -> GameProject:
    """Change how many instances exist, adding or dropping spawns per level."""
    document = _document(project)
    entity = next((item for item in document["entities"] if item["id"] == entity_id), None)
    if entity is None:
        raise EditError(f"there is no entity '{entity_id}'")
    if count < 1:
        raise EditError("an entity needs at least one instance; remove it instead")
    previous = entity["count"]
    entity["count"] = count
    for level in document["levels"]:
        owned = [spawn for spawn in level["spawns"] if spawn["entity"] == entity_id]
        if count < previous:
            kept = 0
            remaining = []
            for spawn in level["spawns"]:
                if spawn["entity"] == entity_id:
                    kept += 1
                    if kept > count:
                        continue
                remaining.append(spawn)
            level["spawns"] = remaining
            continue
        supply = _free_cells(level)
        needed = count - len(owned)
        if len(supply) < needed:
            raise EditError(
                f"level {level['id']} has {len(supply)} free floor cells for "
                f"{needed} more {entity_id}"
            )
        stride = max(1, len(supply) // needed)
        for step in range(needed):
            col, row = supply[step * stride]
            level["spawns"].append({"entity": entity_id, "col": col, "row": row})
    return _validated(document)


def set_entity_speed(project: GameProject, entity_id: str, speed: int) -> GameProject:
    document = _document(project)
    entity = next((item for item in document["entities"] if item["id"] == entity_id), None)
    if entity is None:
        raise EditError(f"there is no entity '{entity_id}'")
    entity["speed"] = speed
    return _validated(document)


def set_entity_behaviour(project: GameProject, entity_id: str, behaviour: str) -> GameProject:
    document = _document(project)
    entity = next((item for item in document["entities"] if item["id"] == entity_id), None)
    if entity is None:
        raise EditError(f"there is no entity '{entity_id}'")
    entity["behaviour"] = behaviour
    return _validated(document)


def add_entity(
    project: GameProject,
    entity_id: str,
    role: str,
    *,
    sprite: str = "sprite",
    count: int = 1,
    speed: int = 1,
) -> GameProject:
    document = _document(project)
    if any(item["id"] == entity_id for item in document["entities"]):
        raise EditError(f"entity '{entity_id}' already exists")
    document["entities"].append(
        {"id": entity_id, "role": role, "sprite": sprite, "speed": speed, "count": count}
    )
    for level in document["levels"]:
        supply = _free_cells(level)
        if len(supply) < count:
            raise EditError(
                f"level {level['id']} has {len(supply)} free floor cells for {count} {entity_id}"
            )
        stride = max(1, len(supply) // count)
        for step in range(count):
            col, row = supply[step * stride]
            level["spawns"].append({"entity": entity_id, "col": col, "row": row})
    return _validated(document)


def remove_entity(project: GameProject, entity_id: str) -> GameProject:
    document = _document(project)
    entity = next((item for item in document["entities"] if item["id"] == entity_id), None)
    if entity is None:
        raise EditError(f"there is no entity '{entity_id}'")
    if entity["role"] == "player":
        raise EditError("the player entity cannot be removed")
    document["entities"] = [item for item in document["entities"] if item["id"] != entity_id]
    for level in document["levels"]:
        level["spawns"] = [
            spawn for spawn in level["spawns"] if spawn["entity"] != entity_id
        ]
    return _validated(document)


# --- scenes ------------------------------------------------------------------


def set_scene_title(project: GameProject, scene_index: int, title: str) -> GameProject:
    document = _document(project)
    document["scenes"][scene_index]["title"] = title.strip()
    return _validated(document)


def set_scene_next(project: GameProject, scene_index: int, next_scene: str | None) -> GameProject:
    document = _document(project)
    document["scenes"][scene_index]["next_scene"] = next_scene or None
    return _validated(document)


# --- live status -------------------------------------------------------------


def editing_status(project: GameProject) -> dict[str, Any]:
    """Gate state for the design as it currently stands.

    Model invariants are already enforced by every operation above, so this
    reports the two an editor cannot enforce keystroke by keystroke: whether the
    design fits the target machine, and whether its levels are solvable. Both are
    advisory while editing and blocking at release.
    """
    solvability = solvability_report(project)
    backend_error: str | None = None
    try:
        validate_design_fits_target(project)
    except ValueError as exc:
        backend_error = str(exc)
    return {
        "solvable": solvability.solvable,
        "solvability_failures": solvability.failures,
        "buildable": backend_error is None,
        "backend_error": backend_error,
        "ready": solvability.solvable and backend_error is None,
    }


def set_audio(
    project: GameProject, *, effects: list[str] | None = None, music: bool | None = None
) -> GameProject:
    """Change the audio the design asks for.

    The design gate, not this operation, decides whether the target can deliver
    it: a designer may legitimately author sound before switching to a machine
    that can play it.
    """
    document = _document(project)
    if effects is not None:
        document["audio"]["effects"] = list(effects)
    if music is not None:
        document["audio"]["music"] = music
    return _validated(document)
