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
from .models import GameProject


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


def solid_char(project: GameProject) -> str:
    """The character this design uses for terrain it called solid.

    `solid` is a trait like any other and Studio attaches no meaning to it; this
    only picks which character a "fill with wall" style edit paints. A design
    that declares no solid tile paints with its first declared tile.
    """
    for tile in project.tiles:
        if "solid" in tile.traits:
            return tile.char
    return project.tiles[0].char


def open_char(project: GameProject) -> str:
    """The character this design uses for terrain it did not call solid."""
    for tile in project.tiles:
        if "solid" not in tile.traits:
            return tile.char
    return project.tiles[-1].char


# --- terrain -----------------------------------------------------------------


def set_tile(project: GameProject, screen_index: int, col: int, row: int, tile: str) -> GameProject:
    """Paint one cell with a character this design declared."""
    known = {declared.char for declared in project.tiles}
    if tile not in known:
        raise EditError(f"'{tile}' is not one of this design's tiles: " + " ".join(sorted(known)))
    document = _document(project)
    try:
        screen = document["screens"][screen_index]
    except IndexError:
        raise EditError(f"there is no screen {screen_index + 1}") from None
    if not (0 <= col < screen["width"] and 0 <= row < screen["height"]):
        raise EditError(
            f"({col}, {row}) is outside the "
            f"{screen['width']}x{screen['height']} grid of screen {screen['id']}"
        )
    rows = list(screen["tiles"])
    line = rows[row]
    rows[row] = line[:col] + tile + line[col + 1 :]
    screen["tiles"] = rows
    return _validated(document)


def _free_cells(project: GameProject, screen: dict[str, Any]) -> list[tuple[int, int]]:
    taken = {(spawn["col"], spawn["row"]) for spawn in screen["spawns"]}
    free = open_char(project)
    return [
        (col, row)
        for row, line in enumerate(screen["tiles"])
        for col, tile in enumerate(line)
        if tile == free and (col, row) not in taken
    ]


def toggle_tile(project: GameProject, screen_index: int, col: int, row: int) -> GameProject:
    """Swap one cell between this design's solid and open characters."""
    current = project.screens[screen_index].tiles[row][col]
    solid, free = solid_char(project), open_char(project)
    return set_tile(project, screen_index, col, row, free if current == solid else solid)


def fill_screen(project: GameProject, screen_index: int, tile: str) -> GameProject:
    """Repaint a whole screen with one declared character, keeping its border."""
    known = {declared.char for declared in project.tiles}
    if tile not in known:
        raise EditError(f"'{tile}' is not one of this design's tiles: " + " ".join(sorted(known)))
    document = _document(project)
    try:
        screen = document["screens"][screen_index]
    except IndexError:
        raise EditError(f"there is no screen {screen_index + 1}") from None
    screen["tiles"] = [tile * screen["width"] for _ in range(screen["height"])]
    return _validated(document)


# --- spawns ------------------------------------------------------------------


def move_spawn(
    project: GameProject, screen_index: int, spawn_index: int, col: int, row: int
) -> GameProject:
    document = _document(project)
    screen = document["screens"][screen_index]
    try:
        spawn = screen["spawns"][spawn_index]
    except IndexError:
        raise EditError(f"screen {screen['id']} has no spawn {spawn_index}") from None
    if not (0 <= col < screen["width"] and 0 <= row < screen["height"]):
        raise EditError(f"({col}, {row}) is outside the {screen['width']}x{screen['height']} grid")
    spawn["col"] = col
    spawn["row"] = row
    return _validated(document)


def _repaired(project: GameProject, document: dict[str, Any]) -> GameProject:
    """Move spawns that terrain or a resize left off this design's open cells."""
    free_char = open_char(project)
    for screen in document["screens"]:
        width = screen["width"]
        height = screen["height"]
        placed: set[tuple[int, int]] = set()
        stranded: list[dict[str, Any]] = []
        for spawn in screen["spawns"]:
            inside = 0 <= spawn["col"] < width and 0 <= spawn["row"] < height
            on_open = inside and screen["tiles"][spawn["row"]][spawn["col"]] == free_char
            cell = (spawn["col"], spawn["row"])
            if on_open and cell not in placed:
                placed.add(cell)
            else:
                stranded.append(spawn)
        if not stranded:
            continue
        supply = [
            (col, row)
            for row, line in enumerate(screen["tiles"])
            for col, tile in enumerate(line)
            if tile == free_char and (col, row) not in placed
        ]
        if len(supply) < len(stranded):
            raise EditError(
                f"screen {screen['id']} has {len(supply)} free floor cells for "
                f"{len(stranded)} displaced entities"
            )
        for spawn, cell in zip(stranded, supply):
            spawn["col"], spawn["row"] = cell
            placed.add(cell)
    return _validated(document)


# --- screens -------------------------------------------------------------


def resize_screen(project: GameProject, screen_index: int, width: int, height: int) -> GameProject:
    """Crop or extend one screen, keeping the terrain that still fits."""
    document = _document(project)
    screen = document["screens"][screen_index]
    free = open_char(project)
    old = screen["tiles"]
    rows = []
    for row in range(height):
        source = old[row] if row < len(old) else ""
        line = [source[col] if col < len(source) else free for col in range(width)]
        rows.append("".join(line))
    screen["width"] = width
    screen["height"] = height
    screen["tiles"] = rows
    return _repaired(project, document)


def rename_screen(project: GameProject, screen_index: int, name: str) -> GameProject:
    document = _document(project)
    document["screens"][screen_index]["name"] = name.strip()
    return _validated(document)


def set_screen_time_limit(
    project: GameProject, screen_index: int, seconds: int | None
) -> GameProject:
    document = _document(project)
    document["screens"][screen_index]["time_limit_seconds"] = seconds
    return _validated(document)


# --- entities ----------------------------------------------------------------


def set_entity_count(project: GameProject, entity_id: str, count: int) -> GameProject:
    """Change how many instances exist, adding or dropping spawns on every screen."""
    document = _document(project)
    entity = next((item for item in document["entities"] if item["id"] == entity_id), None)
    if entity is None:
        raise EditError(f"there is no entity '{entity_id}'")
    if count < 1:
        raise EditError("an entity needs at least one instance; remove it instead")
    previous = entity["count"]
    entity["count"] = count
    for screen in document["screens"]:
        owned = [spawn for spawn in screen["spawns"] if spawn["entity"] == entity_id]
        if count < previous:
            kept = 0
            remaining = []
            for spawn in screen["spawns"]:
                if spawn["entity"] == entity_id:
                    kept += 1
                    if kept > count:
                        continue
                remaining.append(spawn)
            screen["spawns"] = remaining
            continue
        supply = _free_cells(project, screen)
        needed = count - len(owned)
        if needed <= 0:
            # This screen already carries enough; only the others need filling.
            continue
        if len(supply) < needed:
            raise EditError(
                f"screen {screen['id']} has {len(supply)} free floor cells for "
                f"{needed} more {entity_id}"
            )
        stride = max(1, len(supply) // needed)
        for step in range(needed):
            col, row = supply[step * stride]
            screen["spawns"].append({"entity": entity_id, "col": col, "row": row})
    return _validated(document)


def add_entity(
    project: GameProject,
    entity_id: str,
    kind: str,
    *,
    sprite: str | None = None,
    count: int = 1,
) -> GameProject:
    """Declare a new entity and place it on every screen."""
    document = _document(project)
    if any(item["id"] == entity_id for item in document["entities"]):
        raise EditError(f"entity '{entity_id}' already exists")
    document["entities"].append({"id": entity_id, "kind": kind, "sprite": sprite, "count": count})
    for screen in document["screens"]:
        supply = _free_cells(project, screen)
        if len(supply) < count:
            raise EditError(
                f"screen {screen['id']} has {len(supply)} free floor cells for {count} {entity_id}"
            )
        stride = max(1, len(supply) // count)
        for step in range(count):
            col, row = supply[step * stride]
            screen["spawns"].append({"entity": entity_id, "col": col, "row": row})
    return _validated(document)


def remove_entity(project: GameProject, entity_id: str) -> GameProject:
    document = _document(project)
    entity = next((item for item in document["entities"] if item["id"] == entity_id), None)
    if entity is None:
        raise EditError(f"there is no entity '{entity_id}'")
    document["entities"] = [item for item in document["entities"] if item["id"] != entity_id]
    for screen in document["screens"]:
        screen["spawns"] = [spawn for spawn in screen["spawns"] if spawn["entity"] != entity_id]
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

    Only one question survives here: does this design fit the machine. Whether
    it can be played is no longer answerable by reading the map -- that was a
    rule about grid games, and it lied about anything with a jump -- and
    belongs to the examiner and the emulator.
    """
    backend_error: str | None = None
    try:
        validate_design_fits_target(project)
    except ValueError as exc:
        backend_error = str(exc)
    return {
        "buildable": backend_error is None,
        "backend_error": backend_error,
        "ready": backend_error is None,
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


def rename_project(
    project: GameProject,
    title: str,
    *,
    style: str | None = None,
    brief: str | None = None,
) -> GameProject:
    """Apply the scalar design fields a form edits, in one validated step.

    Grouped because a form submits them together: applying them one at a time
    would reject an edit that is only valid once all of them are in place.
    """
    document = _document(project)
    document["metadata"]["title"] = title
    if style is not None:
        document["presentation"]["style"] = style
    if brief is not None:
        document["metadata"]["brief"] = brief
    return _validated(document)
