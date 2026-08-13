"""The blank document a new project starts from.

This is not a template and has no authority: it is one screen, one actor and
two tiles, so that a freshly created project is openable, saveable and
buildable while its designer decides what it is. Everything about it is meant
to be replaced.
"""

from __future__ import annotations

from re import sub

from .models import (
    BudgetSpec,
    ControlsSpec,
    EntitySpec,
    GameProject,
    MenuOption,
    Metadata,
    PresentationSpec,
    SceneSpec,
    ScreenSpec,
    SpawnSpec,
    TargetPlatform,
    TargetSpec,
    TileSpec,
    VideoMode,
)

#: The blank screen: a bordered room that fits every target's playfield.
BLANK_WIDTH = 20
BLANK_HEIGHT = 14


def slugify(value: str) -> str:
    slug = sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return (slug or "new-game")[:48]


def _blank_rows() -> list[str]:
    top = "#" * BLANK_WIDTH
    middle = "#" + "." * (BLANK_WIDTH - 2) + "#"
    return [top] + [middle] * (BLANK_HEIGHT - 2) + [top]


def blank_project(title: str, platform: TargetPlatform) -> GameProject:
    """A valid, empty starting point for `title` on `platform`."""
    cpc = platform is TargetPlatform.AMSTRAD_CPC
    return GameProject(
        metadata=Metadata(slug=slugify(title), title=title),
        target=TargetSpec(
            platform=platform,
            video_mode=VideoMode.CPC_MODE_1 if cpc else VideoMode.SPECTRUM_BITMAP,
        ),
        presentation=PresentationSpec(style="classic arcade"),
        controls=ControlsSpec(
            bindings=(
                {"left": "LEFT", "right": "RIGHT", "up": "UP", "down": "DOWN", "action": "SPACE"}
                if cpc
                else {"left": "O", "right": "P", "up": "Q", "down": "A", "action": "SPACE"}
            )
        ),
        budgets=BudgetSpec(
            binary_bytes=32768 if cpc else 24576,
            static_data_bytes=12288 if cpc else 8192,
            max_entities=16,
        ),
        tiles=[
            TileSpec(id="wall", char="#", traits=["solid"]),
            TileSpec(id="floor", char="."),
        ],
        entities=[EntitySpec(id="hero", kind="player", notes="the one the player moves")],
        mechanics=["the player moves with the bound direction keys"],
        screens=[
            ScreenSpec(
                id="screen_1",
                name="SCREEN 1",
                width=BLANK_WIDTH,
                height=BLANK_HEIGHT,
                tiles=_blank_rows(),
                spawns=[SpawnSpec(entity="hero", col=BLANK_WIDTH // 2, row=BLANK_HEIGHT // 2)],
            )
        ],
        initial_screen="screen_1",
        scenes=[
            SceneSpec(
                id="title",
                kind="title",
                title=title[:32],
                options=[MenuOption(label="START", target_scene="game")],
            ),
            SceneSpec(id="game", kind="gameplay", next_scene="game_over"),
            SceneSpec(id="game_over", kind="game_over", title="GAME OVER", next_scene="title"),
        ],
    )
