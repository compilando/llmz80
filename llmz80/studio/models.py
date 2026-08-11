"""Versioned intermediate representation for editable retro-game projects."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from llmz80.core.state_contract import SYMBOLS_BY_NAME


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class TargetPlatform(str, Enum):
    SPECTRUM = "spectrum"
    AMSTRAD_CPC = "amstrad_cpc"


class ProjectKind(str, Enum):
    GAME = "game"
    GRAPHICS_DEMO = "graphics_demo"
    TEXT_ADVENTURE = "text_adventure"


class ProjectScope(str, Enum):
    PROTOTYPE = "prototype"
    COMPLETE = "complete"
    COMMERCIAL = "commercial"


class GenreId(str, Enum):
    SINGLE_SCREEN_COLLECT = "single_screen_collect"
    MAZE_CHASE = "maze_chase"


class VideoMode(str, Enum):
    SPECTRUM_BITMAP = "spectrum_bitmap"
    CPC_MODE_0 = "cpc_mode_0"
    CPC_MODE_1 = "cpc_mode_1"


class SceneKind(str, Enum):
    TITLE = "title"
    MENU = "menu"
    GAMEPLAY = "gameplay"
    LEVEL_COMPLETE = "level_complete"
    GAME_OVER = "game_over"
    CREDITS = "credits"


class Metadata(StrictModel):
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{0,47}$")
    title: str = Field(min_length=1, max_length=32)
    #: What this game is, in the designer's own words. A typology gives a
    #: starting shape; this says what makes this one itself, and it is the only
    #: part of the design that structured fields cannot express.
    brief: str = Field(default="", max_length=2000)
    author: str = Field(default="LLMZ80 Studio", max_length=32)
    language: Literal["en", "es"] = "es"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TargetSpec(StrictModel):
    platform: TargetPlatform
    video_mode: VideoMode
    frame_hz: Literal[50] = 50


class PresentationSpec(StrictModel):
    style: str = Field(default="classic arcade", min_length=1, max_length=80)
    palette: list[int] = Field(default_factory=list, max_length=16)
    show_score: bool = True
    show_lives: bool = True


class ControlsSpec(StrictModel):
    scheme: Literal["qaop_space", "cursor_space", "joystick"]
    left: str
    right: str
    up: str
    down: str
    action: str


class MenuOption(StrictModel):
    label: str = Field(min_length=1, max_length=24)
    target_scene: str


class SceneSpec(StrictModel):
    id: str = Field(pattern=r"^[a-z][a-z0-9_]{1,31}$")
    kind: SceneKind
    title: str = Field(default="", max_length=32)
    next_scene: str | None = None
    options: list[MenuOption] = Field(default_factory=list, max_length=6)


class EntitySpec(StrictModel):
    id: str = Field(pattern=r"^[a-z][a-z0-9_]{1,31}$")
    role: Literal["player", "enemy", "collectible", "hazard", "exit"]
    sprite: str
    speed: int = Field(default=1, ge=1, le=4)
    count: int = Field(default=1, ge=1, le=32)
    #: How an enemy moves. "auto" keeps the historical alternation between
    #: horizontal and vertical patrol so existing designs are unaffected.
    behaviour: Literal["auto", "patrol_h", "patrol_v", "bounce", "chase", "guard"] = "auto"

    @model_validator(mode="after")
    def validate_behaviour(self) -> "EntitySpec":
        if self.behaviour != "auto" and self.role != "enemy":
            raise ValueError(f"{self.role} entities cannot declare a movement behaviour")
        return self


class GameplaySpec(StrictModel):
    lives: int = Field(default=3, ge=1, le=9)
    win_score: int = Field(default=100, ge=1, le=99999)
    level_count: int = Field(default=3, ge=1, le=32)
    difficulty_curve: Literal["flat", "linear", "stepped"] = "linear"
    #: Single source of truth for scoring; the engine header is generated from it.
    score_per_collectible: int = Field(default=10, ge=1, le=1000)


#: Terrain characters accepted in `LevelSpec.tiles`.
TILE_FLOOR = "."
TILE_WALL = "#"
TILE_CHARS = frozenset({TILE_FLOOR, TILE_WALL})


class SpawnSpec(StrictModel):
    """Where one instance of an entity starts a level."""

    entity: str = Field(pattern=r"^[a-z][a-z0-9_]{1,31}$")
    col: int = Field(ge=0, le=39)
    row: int = Field(ge=0, le=24)


class LevelSpec(StrictModel):
    id: str = Field(pattern=r"^[a-z][a-z0-9_]{1,31}$")
    name: str = Field(min_length=1, max_length=24)
    width: int = Field(ge=8, le=40)
    height: int = Field(ge=8, le=25)
    time_limit_seconds: int | None = Field(default=None, ge=10, le=999)
    #: One string per row, each `width` characters drawn from `TILE_CHARS`.
    tiles: list[str] = Field(min_length=8, max_length=25)
    #: One entry per entity instance placed on this level.
    spawns: list[SpawnSpec] = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def validate_grid(self) -> "LevelSpec":
        if len(self.tiles) != self.height:
            raise ValueError(
                f"level {self.id} declares height {self.height} but has {len(self.tiles)} tile rows"
            )
        for index, row in enumerate(self.tiles):
            if len(row) != self.width:
                raise ValueError(
                    f"level {self.id} row {index} is {len(row)} characters, expected {self.width}"
                )
            unknown = sorted(set(row) - TILE_CHARS)
            if unknown:
                raise ValueError(
                    f"level {self.id} row {index} uses unknown tiles: " + ", ".join(unknown)
                )

        occupied: set[tuple[int, int]] = set()
        for spawn in self.spawns:
            if spawn.col >= self.width or spawn.row >= self.height:
                raise ValueError(
                    f"level {self.id} spawns {spawn.entity} outside the "
                    f"{self.width}x{self.height} grid"
                )
            if self.tiles[spawn.row][spawn.col] == TILE_WALL:
                raise ValueError(
                    f"level {self.id} spawns {spawn.entity} inside a wall at "
                    f"({spawn.col}, {spawn.row})"
                )
            cell = (spawn.col, spawn.row)
            if cell in occupied:
                raise ValueError(f"level {self.id} has two spawns on cell {cell}")
            occupied.add(cell)
        return self


#: Sound effects the engine knows how to trigger, in engine constant order.
AUDIO_EFFECTS = ("start", "collect", "hit", "level", "game_over")


class AudioSpec(StrictModel):
    music: bool = False
    effects: list[Literal["start", "collect", "hit", "level", "game_over"]] = Field(
        default_factory=lambda: ["collect", "hit", "start"], max_length=5
    )

    @model_validator(mode="after")
    def validate_effects(self) -> "AudioSpec":
        if len(set(self.effects)) != len(self.effects):
            raise ValueError("audio effects must be unique")
        return self


class AssetSpec(StrictModel):
    id: str = Field(pattern=r"^[a-z][a-z0-9_]{1,31}$")
    kind: Literal["sprite", "tileset", "font", "screen"] = "sprite"
    source: str = Field(pattern=r"^assets/[A-Za-z0-9_.-]+$")
    width: int = Field(ge=1, le=640)
    height: int = Field(ge=1, le=400)


class BudgetSpec(StrictModel):
    binary_bytes: int = Field(ge=4096, le=65535)
    static_data_bytes: int = Field(ge=1024, le=32768)
    stack_bytes: int = Field(default=1024, ge=256, le=4096)
    max_entities: int = Field(default=16, ge=1, le=64)
    frame_budget_cycles: int = Field(default=70000, ge=10000, le=80000)


#: Directions a scenario can hold, plus the action key.
ScenarioHold = Literal["left", "right", "up", "down", "action", "none"]


class AcceptanceScenario(StrictModel):
    """One acceptance criterion, in prose and optionally as a runnable check.

    The prose form documents intent for a reader. The `hold`/`frames`/`expect`
    triple turns the same criterion into something the runtime gate executes and
    a generator can be shown in advance, so the program is written against the
    exact test it will face.
    """

    id: str = Field(pattern=r"^[a-z][a-z0-9_]{1,31}$")
    given: str
    when: str
    then: str
    #: Input held during this step; "none" waits without touching the keyboard.
    hold: ScenarioHold | None = None
    #: Display frames to hold it for, at 50 Hz.
    frames: int = Field(default=50, ge=1, le=1000)
    #: State-contract symbols and the values they must hold once the step ends.
    expect: dict[str, int] = Field(default_factory=dict)

    @property
    def executable(self) -> bool:
        return self.hold is not None and bool(self.expect)

    @model_validator(mode="after")
    def validate_expectations(self) -> "AcceptanceScenario":
        unknown = sorted(set(self.expect) - set(SYMBOLS_BY_NAME))
        if unknown:
            raise ValueError(
                f"scenario {self.id} expects symbols outside the state contract: "
                + ", ".join(unknown)
            )
        if self.expect and self.hold is None:
            raise ValueError(f"scenario {self.id} states expectations but no input to reach them")
        return self


class GameProject(StrictModel):
    schema_version: Literal[3] = 3
    metadata: Metadata
    kind: ProjectKind = ProjectKind.GAME
    scope: ProjectScope = ProjectScope.COMPLETE
    genre: str = Field(pattern=r"^[a-z][a-z0-9_]{2,63}$")
    target: TargetSpec
    presentation: PresentationSpec
    controls: ControlsSpec
    initial_scene: str = "title"
    scenes: list[SceneSpec] = Field(min_length=2)
    entities: list[EntitySpec] = Field(min_length=2)
    gameplay: GameplaySpec
    levels: list[LevelSpec] = Field(min_length=1)
    audio: AudioSpec = Field(default_factory=AudioSpec)
    assets: list[AssetSpec] = Field(default_factory=list)
    #: Directory inside the project holding the program's C sources. The program
    #: is written, not generated, so it is the artifact of record and lives with
    #: the design rather than being reconstructed from it.
    program_dir: str = Field(default="program", pattern=r"^[A-Za-z0-9_][A-Za-z0-9_./-]{0,63}$")
    budgets: BudgetSpec
    acceptance: list[AcceptanceScenario] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_contract(self) -> "GameProject":
        mode = self.target.video_mode
        if (
            self.target.platform is TargetPlatform.SPECTRUM
            and mode is not VideoMode.SPECTRUM_BITMAP
        ):
            raise ValueError("Spectrum projects require spectrum_bitmap video mode")
        if self.target.platform is TargetPlatform.AMSTRAD_CPC and mode is VideoMode.SPECTRUM_BITMAP:
            raise ValueError("Amstrad CPC projects require cpc_mode_0 or cpc_mode_1")

        scene_ids = [scene.id for scene in self.scenes]
        if len(scene_ids) != len(set(scene_ids)):
            raise ValueError("scene ids must be unique")
        if self.initial_scene not in scene_ids:
            raise ValueError("initial_scene must reference an existing scene")
        if not any(scene.kind is SceneKind.GAMEPLAY for scene in self.scenes):
            raise ValueError("at least one gameplay scene is required")
        references = [scene.next_scene for scene in self.scenes if scene.next_scene]
        references += [option.target_scene for scene in self.scenes for option in scene.options]
        unknown = sorted(set(references) - set(scene_ids))
        if unknown:
            raise ValueError("unknown scene references: " + ", ".join(unknown))

        entity_ids = [entity.id for entity in self.entities]
        if len(entity_ids) != len(set(entity_ids)):
            raise ValueError("entity ids must be unique")
        if sum(entity.count for entity in self.entities) > self.budgets.max_entities:
            raise ValueError("entity count exceeds max_entities budget")
        if not any(entity.role == "player" for entity in self.entities):
            raise ValueError("a player entity is required")
        if self.genre == GenreId.MAZE_CHASE.value and not any(
            entity.role == "collectible" for entity in self.entities
        ):
            raise ValueError("maze_chase requires collectible entities")
        if self.gameplay.level_count != len(self.levels):
            raise ValueError("gameplay.level_count must match the number of levels")

        expected_placements = {entity.id: entity.count for entity in self.entities}
        for level in self.levels:
            unknown_spawns = sorted(
                {spawn.entity for spawn in level.spawns} - set(expected_placements)
            )
            if unknown_spawns:
                raise ValueError(
                    f"level {level.id} spawns unknown entities: " + ", ".join(unknown_spawns)
                )
            placed = Counter(spawn.entity for spawn in level.spawns)
            mismatched = sorted(
                f"{entity} placed {placed.get(entity, 0)} times, expected {count}"
                for entity, count in expected_placements.items()
                if placed.get(entity, 0) != count
            )
            if mismatched:
                raise ValueError(f"level {level.id}: " + "; ".join(mismatched))

        asset_ids = [asset.id for asset in self.assets]
        if len(asset_ids) != len(set(asset_ids)):
            raise ValueError("asset ids must be unique")
        return self
