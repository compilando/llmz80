"""Versioned intermediate representation for editable retro-game projects.

Schema v4 declares *how* a design states its vocabulary, never *which*
vocabulary it may state. There is no genre, no fixed entity role and no fixed
tile alphabet here: a design names its own tiles, entities, mechanics and
observables, and the program written from it decides what any of them mean.

Whole-project validation lives in `structure.py`, not here: this module owns
the shape of each field, that one owns whether the pieces refer to each other
consistently and whether the result fits the machine.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class TargetPlatform(str, Enum):
    SPECTRUM = "spectrum"
    AMSTRAD_CPC = "amstrad_cpc"


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


#: Identifiers a design may coin: tiles, entities, screens, palette entries.
ID_PATTERN = r"^[a-z][a-z0-9_]{1,31}$"

#: Key labels a binding may name. Kept small and machine-independent; the
#: per-target scancode each one maps to lives in `codegen.KEY_CODES`.
KEY_LABELS: tuple[str, ...] = (
    tuple(chr(code) for code in range(ord("A"), ord("Z") + 1))
    + tuple(str(digit) for digit in range(10))
    + ("SPACE", "ENTER", "LEFT", "RIGHT", "UP", "DOWN")
)

#: One input byte carries one bit per binding, so eight is the hard ceiling.
MAX_BINDINGS = 8


class Metadata(StrictModel):
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{0,47}$")
    title: str = Field(min_length=1, max_length=32)
    #: What this game is, in the designer's own words.
    brief: str = Field(default="", max_length=2000)
    author: str = Field(default="LLMZ80 Studio", max_length=32)
    language: Literal["en", "es"] = "es"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TargetSpec(StrictModel):
    platform: TargetPlatform
    video_mode: VideoMode
    frame_hz: Literal[50] = 50


class PaletteEntry(StrictModel):
    """One colour the design names. What it becomes on each machine is decided
    when the art is packed, not here: this is the design's own vocabulary."""

    id: str = Field(pattern=ID_PATTERN)
    colour: str = Field(min_length=1, max_length=32)


class PresentationSpec(StrictModel):
    style: str = Field(default="classic arcade", min_length=1, max_length=80)
    palette: list[PaletteEntry] = Field(default_factory=list, max_length=16)
    show_score: bool = True
    show_lives: bool = True


class ControlsSpec(StrictModel):
    """Named inputs. The design coins the names -- `jump`, `fire`, `pump` --
    and Studio only guarantees each maps to a key the machine can read."""

    bindings: dict[str, str] = Field(min_length=1, max_length=MAX_BINDINGS)

    @model_validator(mode="after")
    def validate_bindings(self) -> "ControlsSpec":
        import re

        for name, key in self.bindings.items():
            if not re.match(r"^[a-z][a-z0-9_]{1,15}$", name):
                raise ValueError(f"binding name {name!r} is not a usable identifier")
            if key not in KEY_LABELS:
                raise ValueError(
                    f"binding {name!r} names key {key!r}, which is not one of: "
                    + ", ".join(KEY_LABELS)
                )
        return self


class TileSpec(StrictModel):
    """One kind of terrain cell. `traits` is free vocabulary: `solid` means
    nothing to Studio, it means whatever the program decides it means."""

    id: str = Field(pattern=ID_PATTERN)
    char: str = Field(min_length=1, max_length=1)
    #: Asset id of this tile's artwork. Unused until the graphics phase.
    art: str | None = Field(default=None, pattern=ID_PATTERN)
    #: Palette entry id this tile is drawn in.
    colour: str | None = Field(default=None, pattern=ID_PATTERN)
    traits: list[str] = Field(default_factory=list, max_length=8)

    @model_validator(mode="after")
    def validate_char(self) -> "TileSpec":
        if not self.char.isprintable() or self.char == " ":
            raise ValueError(f"tile {self.id} needs a printable, non-blank character")
        return self


class EntitySpec(StrictModel):
    """One kind of actor. `kind` is the design's own word for it."""

    id: str = Field(pattern=ID_PATTERN)
    kind: str = Field(min_length=1, max_length=32)
    sprite: str | None = Field(default=None, pattern=ID_PATTERN)
    #: Named poses the artwork carries: walk, jump, die.
    poses: list[str] = Field(default_factory=list, max_length=8)
    count: int = Field(default=1, ge=1, le=64)
    colour: str | None = Field(default=None, pattern=ID_PATTERN)
    #: What this actor does, for the writer and the examiner to read.
    notes: str = Field(default="", max_length=240)


class ObservableSpec(StrictModel):
    """A symbol this design exposes on top of the base state contract, so the
    examiner can assert something the contract has no word for."""

    symbol: str = Field(pattern=r"^g_[a-z][a-z0-9_]{1,29}$")
    width: Literal[1, 2] = 1
    meaning: str = Field(min_length=1, max_length=160)


class SpawnSpec(StrictModel):
    entity: str = Field(pattern=ID_PATTERN)
    col: int = Field(ge=0, le=39)
    row: int = Field(ge=0, le=24)


class ScreenSpec(StrictModel):
    """One screen of the game, and where it leads."""

    id: str = Field(pattern=ID_PATTERN)
    name: str = Field(min_length=1, max_length=24)
    width: int = Field(ge=8, le=40)
    height: int = Field(ge=8, le=25)
    time_limit_seconds: int | None = Field(default=None, ge=10, le=999)
    tiles: list[str] = Field(min_length=8, max_length=25)
    spawns: list[SpawnSpec] = Field(default_factory=list, max_length=64)
    #: Direction taken out of this screen -> the screen it reaches.
    exits: dict[str, str] = Field(default_factory=dict, max_length=8)

    @model_validator(mode="after")
    def validate_grid(self) -> "ScreenSpec":
        if len(self.tiles) != self.height:
            raise ValueError(
                f"screen {self.id} declares height {self.height} "
                f"but has {len(self.tiles)} rows"
            )
        for index, row in enumerate(self.tiles):
            if len(row) != self.width:
                raise ValueError(
                    f"screen {self.id} row {index} is {len(row)} characters, "
                    f"expected {self.width}"
                )
        for spawn in self.spawns:
            if spawn.col >= self.width or spawn.row >= self.height:
                raise ValueError(
                    f"screen {self.id} spawns {spawn.entity} outside its "
                    f"{self.width}x{self.height} grid"
                )
        return self


class MenuOption(StrictModel):
    label: str = Field(min_length=1, max_length=24)
    target_scene: str


class SceneSpec(StrictModel):
    """Flow between screens of presentation. This is not a genre: every game
    has a way in and a way out."""

    id: str = Field(pattern=ID_PATTERN)
    kind: SceneKind
    title: str = Field(default="", max_length=32)
    next_scene: str | None = None
    options: list[MenuOption] = Field(default_factory=list, max_length=6)


#: Sound effects the platform library knows how to trigger.
AUDIO_EFFECTS = ("start", "collect", "hit", "level", "game_over")


class AudioSpec(StrictModel):
    music: bool = False
    effects: list[Literal["start", "collect", "hit", "level", "game_over"]] = Field(
        default_factory=list, max_length=5
    )

    @model_validator(mode="after")
    def validate_effects(self) -> "AudioSpec":
        if len(set(self.effects)) != len(self.effects):
            raise ValueError("audio effects must be unique")
        return self


class AssetSpec(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
    kind: Literal["sprite", "tileset", "font", "screen"] = "sprite"
    source: str = Field(pattern=r"^assets/[A-Za-z0-9_.-]+$")
    width: int = Field(ge=1, le=640)
    height: int = Field(ge=1, le=400)
    frames: int = Field(default=1, ge=1, le=8)

    @property
    def frame_width(self) -> int:
        return self.width // self.frames

    @model_validator(mode="after")
    def validate_frames(self) -> "AssetSpec":
        if self.width % self.frames:
            raise ValueError(
                f"{self.id}: a sheet {self.width} wide cannot hold "
                f"{self.frames} whole frames"
            )
        return self


class BudgetSpec(StrictModel):
    binary_bytes: int = Field(ge=4096, le=65535)
    static_data_bytes: int = Field(ge=1024, le=32768)
    stack_bytes: int = Field(default=1024, ge=256, le=4096)
    max_entities: int = Field(default=16, ge=1, le=64)
    frame_budget_cycles: int = Field(default=70000, ge=10000, le=80000)


class GameProject(StrictModel):
    schema_version: Literal[4] = 4
    metadata: Metadata
    target: TargetSpec
    presentation: PresentationSpec
    controls: ControlsSpec
    budgets: BudgetSpec
    tiles: list[TileSpec] = Field(min_length=1, max_length=32)
    entities: list[EntitySpec] = Field(min_length=1, max_length=32)
    observables: list[ObservableSpec] = Field(default_factory=list, max_length=16)
    #: What the game does, in the designer's own sentences. The examiner derives
    #: its script from these, and the writer implements them.
    mechanics: list[str] = Field(default_factory=list, max_length=32)
    screens: list[ScreenSpec] = Field(min_length=1, max_length=64)
    initial_screen: str
    scenes: list[SceneSpec] = Field(min_length=2)
    initial_scene: str = "title"
    audio: AudioSpec = Field(default_factory=AudioSpec)
    assets: list[AssetSpec] = Field(default_factory=list)
    program_dir: str = Field(
        default="program", pattern=r"^[A-Za-z0-9_][A-Za-z0-9_./-]{0,63}$"
    )

    @model_validator(mode="after")
    def validate_structure(self) -> "GameProject":
        from .structure import structural_errors

        errors = structural_errors(self)
        if errors:
            raise ValueError("; ".join(errors))
        return self
