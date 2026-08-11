"""Built-in genre packs with safe, complete starting designs."""

from __future__ import annotations

from dataclasses import dataclass
from re import sub

from .acceptance import with_executable_scenarios
from .layout import default_spawns, default_tiles
from .models import (
    AcceptanceScenario,
    AudioSpec,
    BudgetSpec,
    ControlsSpec,
    EntitySpec,
    GameProject,
    GameplaySpec,
    GenreId,
    LevelSpec,
    MenuOption,
    Metadata,
    PresentationSpec,
    ProjectScope,
    SceneKind,
    SceneSpec,
    TargetPlatform,
    TargetSpec,
    VideoMode,
)


@dataclass(frozen=True)
class GenrePack:
    id: str
    name: str
    description: str
    capabilities: tuple[str, ...]

    def create(self, title: str, platform: TargetPlatform, scope: ProjectScope) -> GameProject:
        return create_default_project(title, platform, self.id, scope)


BUILTIN_PACKS = (
    GenrePack(
        GenreId.SINGLE_SCREEN_COLLECT,
        "Single-screen collect game",
        "Collect every item while avoiding hazards on one arcade screen.",
        ("input", "collision", "score", "lives", "levels", "menus"),
    ),
    GenrePack(
        GenreId.MAZE_CHASE,
        "Maze chase",
        "Navigate tile mazes, collect pellets and evade pursuing enemies.",
        ("tiles", "input", "collision", "enemy_ai", "score", "lives", "levels", "menus"),
    ),
)


def slugify(value: str) -> str:
    slug = sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return (slug or "new-game")[:48]


def _default_level(
    genre: str, entities: list[EntitySpec], index: int, *, width: int, height: int
) -> LevelSpec:
    tiles = default_tiles(genre, width, height, index)
    return LevelSpec(
        id=f"level_{index + 1}",
        name=f"LEVEL {index + 1}",
        width=width,
        height=height,
        tiles=tiles,
        spawns=default_spawns(entities, tiles, width, height, index),
    )


def create_default_project(
    title: str,
    platform: TargetPlatform,
    genre: GenreId | str,
    scope: ProjectScope = ProjectScope.COMPLETE,
) -> GameProject:
    """A complete starting design, with its acceptance criteria made runnable."""
    return with_executable_scenarios(_bare_project(title, platform, genre, scope))


def _bare_project(
    title: str,
    platform: TargetPlatform,
    genre: GenreId | str,
    scope: ProjectScope,
) -> GameProject:
    cpc = platform is TargetPlatform.AMSTRAD_CPC
    genre_id = genre.value if isinstance(genre, GenreId) else genre
    controls = ControlsSpec(
        scheme="cursor_space" if cpc else "qaop_space",
        left="CURSOR LEFT" if cpc else "O",
        right="CURSOR RIGHT" if cpc else "P",
        up="CURSOR UP" if cpc else "Q",
        down="CURSOR DOWN" if cpc else "A",
        action="SPACE",
    )
    entities = [
        EntitySpec(id="player", role="player", sprite="hero", speed=1),
        EntitySpec(id="enemy", role="enemy", sprite="enemy", speed=1, count=1),
        EntitySpec(id="collectible", role="collectible", sprite="pellet", count=8),
    ]
    return GameProject(
        metadata=Metadata(slug=slugify(title), title=title),
        scope=scope,
        genre=genre_id,
        target=TargetSpec(
            platform=platform,
            video_mode=VideoMode.CPC_MODE_1 if cpc else VideoMode.SPECTRUM_BITMAP,
        ),
        presentation=PresentationSpec(
            style=(
                "colourful maze arcade"
                if genre_id == GenreId.MAZE_CHASE.value
                else "clean arcade"
            )
        ),
        controls=controls,
        scenes=[
            SceneSpec(
                id="title",
                kind=SceneKind.TITLE,
                title=title,
                options=[MenuOption(label="START", target_scene="game")],
            ),
            SceneSpec(id="game", kind=SceneKind.GAMEPLAY, next_scene="level_complete"),
            SceneSpec(
                id="level_complete",
                kind=SceneKind.LEVEL_COMPLETE,
                title="LEVEL COMPLETE",
                next_scene="game",
            ),
            SceneSpec(
                id="game_over", kind=SceneKind.GAME_OVER, title="GAME OVER", next_scene="title"
            ),
        ],
        entities=entities,
        # Only ask for audio the target can actually produce, so a new project
        # never starts out failing its own design gate.
        audio=AudioSpec(effects=[] if cpc else ["start", "collect", "hit"]),
        gameplay=GameplaySpec(lives=3, win_score=100, level_count=3),
        levels=[
            _default_level(genre_id, entities, number - 1, width=20, height=16)
            for number in range(1, 4)
        ],
        budgets=BudgetSpec(
            binary_bytes=32768 if cpc else 24576,
            static_data_bytes=12288 if cpc else 8192,
            max_entities=16,
        ),
        acceptance=[
            AcceptanceScenario(
                id="start_game",
                given="the title screen is visible",
                when="the player presses action",
                then="gameplay starts",
            ),
            AcceptanceScenario(
                id="collect_scores",
                given="a collectible is visible",
                when="the player touches it",
                then="the score increases and the collectible disappears",
            ),
            AcceptanceScenario(
                id="enemy_costs_life",
                given="gameplay is active",
                when="the player touches an enemy",
                then="one life is lost and the player respawns",
            ),
        ],
    )
