"""Edits to a `GameProject`, each one validated, none of them an interface.

Every operation takes a project and returns a new validated project; one that
would break a hard invariant raises `EditError` with a message meant to be
read by whoever asked for the edit.

There used to be eighteen of these -- paint a cell, fill a screen, resize
one, add an entity, retitle a scene, set the audio -- and ten of them had no
caller outside their own tests. They were an API for a map editor that was
never built, kept alive by a terminal wizard that opened panels over it; both
are gone. What is left is what something really calls: `rename_project`
(`pipeline.create`, so a new project carries its brief) and `editing_status`
(`screen.stage_line` and `planner`, to ask whether a design still fits its
machine).

`move_spawn`, `set_entity_count` and `describe_changes` are still here and
still proved, and nothing in the program calls them today. They are the
useful half of an editor -- move a thing, have more of a thing, say what
changed -- and the next honest step for them is either a caller or the same
deletion the other ten got.
"""

from __future__ import annotations

from collections import Counter
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


def open_char(project: GameProject) -> str:
    """The character this design uses for terrain it did not call solid.

    What `_free_cells` measures free floor with, which is how
    `set_entity_count` knows where another instance can stand.
    """
    for tile in project.tiles:
        if "solid" not in tile.traits:
            return tile.char
    return project.tiles[-1].char


def _free_cells(project: GameProject, screen: dict[str, Any]) -> list[tuple[int, int]]:
    taken = {(spawn["col"], spawn["row"]) for spawn in screen["spawns"]}
    free = open_char(project)
    return [
        (col, row)
        for row, line in enumerate(screen["tiles"])
        for col, tile in enumerate(line)
        if tile == free and (col, row) not in taken
    ]


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


# --- what changed ------------------------------------------------------------


def _plural(count: int, noun: str, verb: str) -> str:
    """`3 cells painted`, `1 cell painted` -- what a diary line is made of."""
    return f"{count} {noun}{'' if count == 1 else 's'} {verb}"


def _named(ids: list[str], limit: int = 3) -> str:
    """Up to `limit` ids, then a count: a diary line is one line."""
    if len(ids) <= limit:
        return ", ".join(ids)
    return ", ".join(ids[:limit]) + f" and {len(ids) - limit} more"


#: Fields `describe_changes` reads itself, and must therefore not report a
#: second time as "something else changed": the whole of `entities` and
#: `screens`, and the scalars a design form edits (with the two fields no
#: edit of anybody's owns -- the slug that follows a title, and the
#: `updated_at` every save stamps).
_COVERED = {
    "entities": None,
    "screens": None,
    "metadata": {"title", "brief", "slug", "updated_at"},
    "presentation": {"style"},
}


def describe_changes(before: GameProject, after: GameProject) -> str:
    """What changed between two versions of one design, as one diary line.

    Not a diff -- a diff is for reviewing a proposal before accepting it, and
    this is for whoever reads `studio.log` the next morning and wants to know
    whether they painted one wall or rebuilt the map. So it counts the things
    that are cheap to count and worth knowing (terrain cells repainted,
    spawns moved or placed, entities and screens gained or lost, the scalar
    fields a form edits) and, for everything else, names the top-level field
    that moved rather than describing it: `assets changed` after a sprite run
    says enough, and enumerating an image is not this line's job.

    Empty when the two are the same design. `metadata.updated_at` is left out
    of that judgement on purpose: `store.save` stamps it on every write, so
    two versions differing only there are two copies of one thing.
    """
    parts = _terrain_changes(before, after)
    parts += _roster_changes(before, after)
    parts += _scalar_changes(before, after)
    parts += _other_changes(before, after)
    return ", ".join(parts)


def _terrain_changes(before: GameProject, after: GameProject) -> list[str]:
    """Painted cells, resized screens and displaced spawns, per shared screen."""
    was = {screen.id: screen for screen in before.screens}
    painted = 0
    resized: list[str] = []
    moved = placed = removed = 0
    for screen in after.screens:
        old = was.get(screen.id)
        if old is None:
            continue
        if (old.width, old.height) != (screen.width, screen.height):
            resized.append(f"{screen.id} is now {screen.width}x{screen.height}")
        # Only the overlap the two versions share: a resize is reported as a
        # resize, and counting the rows it added as cells somebody painted
        # would drown the one cell they actually meant.
        for row in range(min(old.height, screen.height)):
            for col in range(min(old.width, screen.width)):
                if old.tiles[row][col] != screen.tiles[row][col]:
                    painted += 1
        gone = Counter((spawn.entity, spawn.col, spawn.row) for spawn in old.spawns)
        fresh = Counter((spawn.entity, spawn.col, spawn.row) for spawn in screen.spawns)
        left = Counter(entity for entity, _col, _row in (gone - fresh).elements())
        arrived = Counter(entity for entity, _col, _row in (fresh - gone).elements())
        # One spawn of an entity gone and one of the same entity arrived is
        # that entity moved -- what `m` does in the map editor, and what a
        # person reading this line will recognise as what they did.
        for entity in set(left) | set(arrived):
            shared = min(left[entity], arrived[entity])
            moved += shared
            placed += arrived[entity] - shared
            removed += left[entity] - shared
    parts = []
    if painted:
        parts.append(_plural(painted, "cell", "painted"))
    parts += resized
    for count, verb in ((moved, "moved"), (placed, "placed"), (removed, "removed")):
        if count:
            parts.append(_plural(count, "spawn", verb))
    return parts


def _roster_changes(before: GameProject, after: GameProject) -> list[str]:
    """Entities and screens gained, lost or recounted, named by their ids."""
    parts = []
    old_entities = {entity.id: entity for entity in before.entities}
    new_entities = {entity.id: entity for entity in after.entities}
    gained = [key for key in new_entities if key not in old_entities]
    lost = [key for key in old_entities if key not in new_entities]
    if gained:
        parts.append(
            f"{len(gained)} {'entity' if len(gained) == 1 else 'entities'} added: {_named(gained)}"
        )
    if lost:
        parts.append(
            f"{len(lost)} {'entity' if len(lost) == 1 else 'entities'} removed: {_named(lost)}"
        )
    for key, entity in new_entities.items():
        old = old_entities.get(key)
        if old is not None and old.count != entity.count:
            parts.append(f"{key} count {old.count}->{entity.count}")
    old_screens = [screen.id for screen in before.screens]
    new_screens = [screen.id for screen in after.screens]
    fresh = [key for key in new_screens if key not in old_screens]
    dropped = [key for key in old_screens if key not in new_screens]
    if fresh:
        parts.append(f"{_plural(len(fresh), 'screen', 'added')}: {_named(fresh)}")
    if dropped:
        parts.append(f"{_plural(len(dropped), 'screen', 'removed')}: {_named(dropped)}")
    return parts


def _scalar_changes(before: GameProject, after: GameProject) -> list[str]:
    """The three fields the design form edits -- named, not quoted: a brief
    runs to paragraphs and this is one line."""
    return [
        f"{name} changed"
        for name, old, new in (
            ("title", before.metadata.title, after.metadata.title),
            ("brief", before.metadata.brief, after.metadata.brief),
            ("style", before.presentation.style, after.presentation.style),
        )
        if old != new
    ]


def _other_changes(before: GameProject, after: GameProject) -> list[str]:
    """Top-level fields nothing above accounts for: named, and left at that.

    This is what keeps the line honest about an adaptation, which rewrites
    tiles, mechanics and scenes at once, and about a sprite run, which adds
    assets. Without it a save that changed everything except the terrain
    would have reported nothing at all.
    """
    old = before.model_dump(mode="json")
    new = after.model_dump(mode="json")
    fields = []
    for name, value in new.items():
        covered = _COVERED.get(name, set())
        if covered is None:
            continue
        was = old.get(name)
        if covered and isinstance(value, dict) and isinstance(was, dict):
            value = {key: item for key, item in value.items() if key not in covered}
            was = {key: item for key, item in was.items() if key not in covered}
        if was != value:
            fields.append(name)
    return [", ".join(sorted(fields)) + " changed"] if fields else []
