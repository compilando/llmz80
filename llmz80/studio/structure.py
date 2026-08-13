"""Whole-design validation: do the pieces refer to each other, and does the
result fit the machine.

Every check here is answerable by looking at the document and at the target's
character grid. Nothing here knows what a game is: it does not ask whether a
level is solvable, whether difficulty rises, or whether an actor may stand on a
cell some trait calls solid. Those were rules about one kind of game, and they
are why eighteen typologies produced one.

The three passes below are split by *what kind of question they ask*, not by
what object they look at: identity (is every id, character and symbol
declared once), reference (does everything a field names actually exist) and
fit (does it fit the entity budget or the machine's screen). A tile's colour
and an entity's colour fail the same way, so they share a pass even though
they sit on different models.

Every message names the object at fault and the offending value in quotes,
and -- where the valid set is short enough to be useful on its own -- lists
what was declared instead. A person and a design-proposing model both read
these, and "screen exits right to unknown screen 'cripta'; declared:
screen_1, screen_2" is the difference between one retry and three.
"""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING, Iterable

from llmz80.core.state_contract import SYMBOLS_BY_NAME

if TYPE_CHECKING:  # pragma: no cover - import cycle guard only
    from .models import GameProject

#: Character-cell grid available on each target, as (columns, rows). Keyed by
#: the VideoMode enum's *value* (a plain string) rather than the enum itself,
#: so this module never has to import `models` outside of TYPE_CHECKING --
#: which is what lets `GameProject.validate_structure` call back into this
#: module without a real import cycle.
TARGET_GRID: dict[str, tuple[int, int]] = {
    "spectrum_bitmap": (32, 24),
    "cpc_mode_0": (20, 25),
    "cpc_mode_1": (40, 25),
}


def playfield(project: "GameProject") -> tuple[int, int]:
    """Playfield size in cells once the design's own HUD rows are taken out."""
    mode = project.target.video_mode.value
    try:
        columns, rows = TARGET_GRID[mode]
    except KeyError:
        raise KeyError(f"no character grid known for video mode {mode!r}") from None
    return columns, rows - project.presentation.hud_rows


def structural_errors(project: "GameProject") -> list[str]:
    """Every way this design fails to refer to itself, or to fit its machine."""
    errors: list[str] = []
    errors += _identity_errors(project)
    errors += _reference_errors(project)
    errors += _fit_errors(project)
    return errors


def _repeated(values: Iterable[str]) -> list[tuple[str, int]]:
    """Every value that occurs more than once, as (value, count), sorted."""
    counts = Counter(values)
    return sorted((value, count) for value, count in counts.items() if count > 1)


#: Names to list before a message stops being an aid and starts being a wall.
#: A reader scanning for a typo can hold a dozen; past that the tail is longer
#: than the error it decorates, and a design with many screens repeats it once
#: per broken reference.
_NAME_LIMIT = 12


def _named(values: Iterable[str]) -> str:
    """A short, sorted list of valid names, for the tail of a message."""
    names = sorted(values)
    if not names:
        return "(none declared)"
    if len(names) > _NAME_LIMIT:
        return ", ".join(names[:_NAME_LIMIT]) + f", ... ({len(names) - _NAME_LIMIT} more)"
    return ", ".join(names)


def _identity_errors(project: "GameProject") -> list[str]:
    """Every id, character and symbol this design must not repeat."""
    errors = []
    for tile_id, count in _repeated(tile.id for tile in project.tiles):
        errors.append(f"tile id {tile_id!r} is declared {count} times")
    for char, count in _repeated(tile.char for tile in project.tiles):
        sharing = sorted(tile.id for tile in project.tiles if tile.char == char)
        errors.append(f"two tiles share the character {char!r}: {', '.join(sharing)}")
    for entity_id, count in _repeated(entity.id for entity in project.entities):
        errors.append(f"entity id {entity_id!r} is declared {count} times")
    for screen_id, count in _repeated(screen.id for screen in project.screens):
        errors.append(f"screen id {screen_id!r} is declared {count} times")
    for scene_id, count in _repeated(scene.id for scene in project.scenes):
        errors.append(f"scene id {scene_id!r} is declared {count} times")
    for entry_id, count in _repeated(entry.id for entry in project.presentation.palette):
        errors.append(f"palette entry id {entry_id!r} is declared {count} times")
    for asset_id, count in _repeated(asset.id for asset in project.assets):
        errors.append(f"asset id {asset_id!r} is declared {count} times")
    for symbol, count in _repeated(observable.symbol for observable in project.observables):
        errors.append(f"observable {symbol!r} is declared {count} times")
    return errors


def _reference_errors(project: "GameProject") -> list[str]:
    """Every value a field names, checked against what the design actually
    declares: palette and asset ids from tiles and entities, tile characters
    and entity ids from screens, screen ids from exits and initial_screen,
    scene ids from initial_scene and the scene graph, and an observable's
    symbol against the base state contract it must not shadow."""
    errors = []
    palette = {entry.id for entry in project.presentation.palette}
    assets = {asset.id for asset in project.assets}
    known_chars = {tile.char for tile in project.tiles}
    declared_counts = {entity.id: entity.count for entity in project.entities}

    for tile in project.tiles:
        if tile.colour and tile.colour not in palette:
            errors.append(
                f"tile {tile.id} names undeclared palette entry {tile.colour!r}; "
                f"declared: {_named(palette)}"
            )
        if tile.art and tile.art not in assets:
            errors.append(
                f"tile {tile.id} names undeclared asset {tile.art!r}; "
                f"declared: {_named(assets)}"
            )
    for entity in project.entities:
        if entity.colour and entity.colour not in palette:
            errors.append(
                f"entity {entity.id} names undeclared palette entry {entity.colour!r}; "
                f"declared: {_named(palette)}"
            )
        if entity.sprite and entity.sprite not in assets:
            errors.append(
                f"entity {entity.id} names undeclared asset {entity.sprite!r}; "
                f"declared: {_named(assets)}"
            )

    screen_ids = {screen.id for screen in project.screens}
    for screen in project.screens:
        unknown_chars = sorted({char for row in screen.tiles for char in row} - known_chars)
        if unknown_chars:
            errors.append(
                f"screen {screen.id} uses undeclared tile characters "
                + ", ".join(repr(char) for char in unknown_chars)
            )
        placed = Counter(spawn.entity for spawn in screen.spawns)
        for entity_id, count in sorted(placed.items()):
            if entity_id not in declared_counts:
                errors.append(
                    f"screen {screen.id} spawns unknown entity {entity_id!r}; "
                    f"declared: {_named(declared_counts)}"
                )
            elif count > declared_counts[entity_id]:
                errors.append(
                    f"screen {screen.id} places {entity_id!r} {count} times but "
                    f"declares {declared_counts[entity_id]}"
                )
        for direction, destination in sorted(screen.exits.items()):
            if destination not in screen_ids:
                errors.append(
                    f"screen {screen.id} exits {direction} to unknown screen "
                    f"{destination!r}; declared: {_named(screen_ids)}"
                )

    if project.initial_screen not in screen_ids:
        errors.append(
            f"initial_screen {project.initial_screen!r} names no declared screen; "
            f"declared: {_named(screen_ids)}"
        )

    scene_ids = {scene.id for scene in project.scenes}
    if project.initial_scene not in scene_ids:
        errors.append(
            f"initial_scene {project.initial_scene!r} names no declared scene; "
            f"declared: {_named(scene_ids)}"
        )
    for scene in project.scenes:
        if scene.next_scene and scene.next_scene not in scene_ids:
            errors.append(
                f"scene {scene.id} next_scene names unknown scene {scene.next_scene!r}; "
                f"declared: {_named(scene_ids)}"
            )
        for option in scene.options:
            if option.target_scene not in scene_ids:
                errors.append(
                    f"scene {scene.id} option {option.label!r} targets unknown scene "
                    f"{option.target_scene!r}; declared: {_named(scene_ids)}"
                )

    for observable in project.observables:
        if observable.symbol in SYMBOLS_BY_NAME:
            errors.append(f"observable {observable.symbol} is already in the state contract")
    return errors


def _fit_errors(project: "GameProject") -> list[str]:
    """What has to fit: a screen in its target's playfield, and a screen's
    placed actors in the entity budget."""
    errors = []
    columns, rows = playfield(project)
    for screen in project.screens:
        if screen.width > columns or screen.height > rows:
            errors.append(
                f"screen {screen.id} is {screen.width}x{screen.height} but "
                f"{project.target.video_mode.value} offers {columns}x{rows} playable cells"
            )
        if len(screen.spawns) > project.budgets.max_entities:
            errors.append(
                f"screen {screen.id} places {len(screen.spawns)} actors, which "
                f"exceeds the max_entities budget of {project.budgets.max_entities}"
            )
    return errors
