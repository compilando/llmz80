"""Built-in genre packs with safe, complete starting designs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from re import sub

import yaml

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
    """One typology: what the game is made of and what shape its space has."""

    id: str
    name: str
    description: str
    capabilities: tuple[str, ...]
    terrain: str = "open"
    style: str = "classic arcade"
    enemy_count: int = 1
    enemy_behaviour: str = "auto"
    enemy_speed: int = 1
    collectibles: int = 8

    def create(self, title: str, platform: TargetPlatform, scope: ProjectScope) -> GameProject:
        return create_default_project(title, platform, self.id, scope)


GENRES_FILE = Path(__file__).resolve().parents[2] / "resources" / "genres.yml"


def load_genre_packs(path: Path | None = None) -> tuple[GenrePack, ...]:
    """Read the typology catalogue.

    Typologies are data so that adding one is an entry in genres.yml rather than
    a branch in code. A malformed entry raises here rather than producing a
    half-formed design later.
    """
    document = yaml.safe_load((path or GENRES_FILE).read_text(encoding="utf-8"))
    packs: list[GenrePack] = []
    for entry in document.get("genres", []):
        enemies = entry.get("enemies") or {}
        packs.append(
            GenrePack(
                id=entry["id"],
                name=entry["name"],
                description=entry["description"],
                capabilities=tuple(str(entry.get("keywords", "")).split()),
                terrain=entry.get("terrain", "open"),
                style=entry.get("style", "classic arcade"),
                enemy_count=int(enemies.get("count", 1)),
                enemy_behaviour=str(enemies.get("behaviour", "auto")),
                enemy_speed=int(enemies.get("speed", 1)),
                collectibles=int(entry.get("collectibles", 8)),
            )
        )
    if not packs:
        raise ValueError("the genre catalogue is empty")
    return tuple(packs)


BUILTIN_PACKS = load_genre_packs()
PACKS_BY_ID = {pack.id: pack for pack in BUILTIN_PACKS}


def slugify(value: str) -> str:
    slug = sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return (slug or "new-game")[:48]


def _default_level(
    genre: str,
    entities: list[EntitySpec],
    index: int,
    *,
    width: int,
    height: int,
    terrain: str | None = None,
) -> LevelSpec:
    tiles = default_tiles(genre, width, height, index, terrain)
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
    pack = PACKS_BY_ID.get(genre_id)
    entities = [
        EntitySpec(id="player", role="player", sprite="hero", speed=1),
        EntitySpec(
            id="enemy",
            role="enemy",
            sprite="enemy",
            speed=pack.enemy_speed if pack else 1,
            count=pack.enemy_count if pack else 1,
            behaviour=pack.enemy_behaviour if pack else "auto",
        ),
        EntitySpec(
            id="collectible",
            role="collectible",
            sprite="pellet",
            count=pack.collectibles if pack else 8,
        ),
    ]
    return GameProject(
        metadata=Metadata(slug=slugify(title), title=title),
        scope=scope,
        genre=genre_id,
        target=TargetSpec(
            platform=platform,
            video_mode=VideoMode.CPC_MODE_1 if cpc else VideoMode.SPECTRUM_BITMAP,
        ),
        presentation=PresentationSpec(style=pack.style if pack else "clean arcade"),
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
            _default_level(
                genre_id,
                entities,
                number - 1,
                width=20,
                height=16,
                terrain=pack.terrain if pack else None,
            )
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
