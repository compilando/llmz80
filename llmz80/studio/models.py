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

import re
import string
from collections import Counter
from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

#: Control characters no design ever means to contain. Tab, newline and
#: carriage return are left out of it: prose may legitimately wrap.
_CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _readable(value: str) -> str:
    """Refuse a design string carrying characters nothing can render.

    Not a hypothetical. The first end-to-end run after the drafting stage
    landed came back from the adaptation stage with eight NUL bytes in
    `mechanics`, one in each place an accented character belonged --
    "pulsaci\\0n", "murci\\0lagos". Nothing noticed: identifiers are pattern
    checked but the prose fields had no constraint on their contents at all,
    so the corruption round-tripped through YAML as a `\\0` escape and reached
    `design_prompt`, which puts those sentences in front of the model that
    writes the program. A NUL that survives into a C comment or a string
    literal stops being cosmetic.

    Where the corruption comes from is still unknown -- it happens inside the
    model call, and the same field written by the drafting stage was clean.
    That is exactly why the guard is here rather than at the suspected
    source: this catches it whatever produced it.

    Still unknown, and deliberately not assumed settled by its sibling.
    `_unstructured` below guards a second corruption of the same shape whose
    source *was* traced -- to the model, by replaying the calls and reading
    the raw responses -- but nobody has replayed this one, so the two share a
    resemblance and not a finding.
    """
    found = _CONTROL_CHARACTERS.search(value)
    if found:
        raise ValueError(
            f"this text carries a control character (0x{ord(found.group()):02x}) at "
            f"position {found.start()}, which no design means and nothing can draw: "
            + repr(value[max(0, found.start() - 20) : found.start() + 20])
        )
    return value


#: The separator between two objects of a JSON array: `},{`, with the
#: insignificant whitespace JSON allows around it. Deliberately *not* a brace
#: on its own. A design sentence may legitimately hold one -- a mechanic
#: describing a `{` key legend, a style naming a font -- and refusing every
#: brace would fail honest prose to catch a machine artefact. What no design
#: means is a closing brace, a comma and an opening brace in that order:
#: outside a JSON document that sequence says nothing, and inside one it says
#: "this object ends and the next begins".
_JSON_OBJECT_SEPARATOR = re.compile(r"\}\s*,\s*\{")


def _unstructured(value: str) -> str:
    """Refuse a design string carrying the punctuation of the transport that
    brought it.

    Not a hypothetical, and the second of its kind after the NUL bytes
    `_readable` describes. Three designs on disk carried `},{` welded to the
    end of a text value: `studio-projects/minero-vigilado` has an entity whose
    `kind` is `minero},{`, and `studio-projects/minero-observable` and
    `studio-projects/un-minero-que-cava-tuneles-y-2` (the same design, copied)
    have a `presentation.style` ending `tiny sprites},{`. All three reached
    the examiner and the program writer as they were.

    Both stages that ask a model for a `ProjectProposal` produced one: the
    `kind` came from `drafting`, and the `style` from `reference_design`
    (`minero-vigilado` has no `reference.yml`, so no adaptation ever ran
    there). Nothing between the model and `game.yml` concatenates or restitches
    a value -- `planner.apply_proposal` deep-copies `change.value` into the
    document and revalidates -- so the separator was inside the string when
    the SDK parsed it, which means the model emitted it there.

    Replaying both calls against gpt-5 shows the pressure that produces it.
    `ProjectChange` declares ten properties and strict structured output
    requires every one of them, so after writing `value_text` the model must
    still emit six `value_*: null` fields before it may close the object. In
    the captured raw responses it stalls at exactly that point, padding with
    runs of 1 to 762 literal spaces between the closing quote and the
    `, "value_number": null` tail. `},{` is that same impatience arriving one
    token early: a brace, a comma and a brace are ordinary string characters,
    so the grammar that masks them *between* fields permits them *inside* the
    value, and the model's attempt to start the next change is absorbed as
    text.

    Refused here rather than in `planner`, for the reason `_readable` gives:
    this is the one place a document must pass through however it was written,
    and it costs nothing. Being a validation error also makes it repairable --
    `apply_proposal` revalidates the whole document, so
    `planner.propose_apply_repair` catches this, hands
    `planner.repair_feedback` the offending path, and the model gets another
    attempt instead of the run dying.
    """
    found = _JSON_OBJECT_SEPARATOR.search(value)
    if found:
        raise ValueError(
            f"this text carries the JSON separator {found.group()!r} at position "
            f"{found.start()}, which no design means: it is the punctuation between "
            "two objects of the response that carried it, not part of the value. "
            + repr(value[max(0, found.start() - 30) : found.start() + 10])
        )
    return value


#: Prose a design writes for a person or for the model that reads the design.
#: Length limits stay on the fields themselves, since each has its own.
#:
#: What wears it is every string field a design carries that the schema does
#: not otherwise pin down -- no pattern, no enum, no single character. That is
#: the rule, and it is wider than "the fields that read like sentences",
#: because `EntitySpec.kind` does not read like one and is exactly where the
#: `},{` incident landed. Fields with a pattern (`id`, `symbol`, a tile's
#: `char`, an asset's `source`) or a fixed vocabulary (a binding's key label)
#: need nothing from this: their own constraint already refuses anything a
#: broken response could smuggle in. So do a screen's terrain rows, which
#: `structure._reference_errors` checks character by character against the
#: tiles the design declares.
Prose = Annotated[str, AfterValidator(_readable), AfterValidator(_unstructured)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class TargetPlatform(str, Enum):
    SPECTRUM = "spectrum"
    AMSTRAD_CPC = "amstrad_cpc"


class VideoMode(str, Enum):
    SPECTRUM_BITMAP = "spectrum_bitmap"
    CPC_MODE_0 = "cpc_mode_0"
    CPC_MODE_1 = "cpc_mode_1"


#: Identifiers a design may coin: tiles, entities, screens, palette entries.
ID_PATTERN = r"^[a-z][a-z0-9_]{0,31}$"

#: A project slug: like an id, but may start with a digit and use hyphens,
#: because it doubles as a filesystem/URL-safe directory name.
SLUG_PATTERN = r"^[a-z0-9][a-z0-9-]{0,47}$"

#: An observable's C symbol: the `g_` prefix the generated state contract
#: expects, and unlike an id it has a floor of two characters after it.
SYMBOL_PATTERN = r"^g_[a-z][a-z0-9_]{1,29}$"

#: A control binding's name: capped shorter than an id since it is read
#: back as a bit name in the input byte, and floored at two characters.
BINDING_PATTERN = r"^[a-z][a-z0-9_]{1,15}$"

#: An asset source path: rooted under assets/, unlike an id, because it
#: names a file on disk rather than a symbol in the design.
PATH_PATTERN = r"^assets/[A-Za-z0-9_.-]+$"

#: Key labels a binding may name. Kept small and machine-independent; the
#: per-target scancode each one maps to lives in `codegen.KEY_CODES`.
KEY_LABELS: tuple[str, ...] = (
    tuple(string.ascii_uppercase)
    + tuple(string.digits)
    + ("SPACE", "ENTER", "LEFT", "RIGHT", "UP", "DOWN")
)

#: One input byte carries one bit per binding, so eight is the hard ceiling.
MAX_BINDINGS = 8

#: The vocabulary a scripted step's `hold` may state, and the only thing that
#: says whether the player was moving while the emulator read memory.
#: `observation.observation_script` writes it and `feel.animation_report`
#: reads it, so it lives here rather than in either of them. The two copies
#: never disagreed about the four words; what rotted was the prose around
#: them. `feel.py`'s docstring sent the reader to a `ScenarioHold` in this
#: module, a class deleted before this branch began, so the one written
#: explanation of what a hold means pointed at nothing -- and a vocabulary
#: two modules must agree on is worth no more than the sentence that says
#: what agreeing on it buys, which is a moving step never judged as though
#: the player stood still. A design coins its own binding names (`jump`,
#: `fire`, `pump`), so a name outside `HOLD_DIRECTIONS` says nothing about
#: movement and is held as `HOLD_ACTION`, which the gate leaves out of its
#: comparison rather than guessing at.
HOLD_NONE = "none"
HOLD_ACTION = "action"
HOLD_DIRECTIONS: tuple[str, ...] = ("left", "right", "up", "down")


class Metadata(StrictModel):
    slug: str = Field(pattern=SLUG_PATTERN)
    title: Prose = Field(min_length=1, max_length=32)
    #: What this game is, in the designer's own words.
    brief: Prose = Field(default="", max_length=2000)
    author: Prose = Field(default="LLMZ80 Studio", max_length=32)
    language: Literal["en", "es"] = "es"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TargetSpec(StrictModel):
    platform: TargetPlatform
    video_mode: VideoMode
    frame_hz: Literal[50] = 50

    @model_validator(mode="after")
    def validate_video_mode(self) -> "TargetSpec":
        """A machine can only show its own video modes.

        This is a fact about the hardware, not a rule about games: the platform
        library is chosen by `platform` and the mode constants by `video_mode`,
        so a mismatched pair builds a binary that is wrong with no error to
        show for it.
        """
        spectrum = self.platform is TargetPlatform.SPECTRUM
        if spectrum and self.video_mode is not VideoMode.SPECTRUM_BITMAP:
            raise ValueError("the Spectrum only has spectrum_bitmap")
        if not spectrum and self.video_mode is VideoMode.SPECTRUM_BITMAP:
            raise ValueError("the CPC has cpc_mode_0 and cpc_mode_1, not spectrum_bitmap")
        return self


class PaletteEntry(StrictModel):
    """One colour the design names. What it becomes on each machine is decided
    when the art is packed, not here: this is the design's own vocabulary."""

    id: str = Field(pattern=ID_PATTERN)
    colour: Prose = Field(min_length=1, max_length=32)


class PresentationSpec(StrictModel):
    style: Prose = Field(default="classic arcade", min_length=1, max_length=80)
    palette: list[PaletteEntry] = Field(default_factory=list, max_length=16)
    show_score: bool = True
    show_lives: bool = True
    #: Character rows reserved at the top for a HUD. Two is what a score and
    #: lives line needs, not a fact about the machine: a design that shows
    #: neither can have the rows back, and one that wants a bigger status area
    #: can take more.
    hud_rows: int = Field(default=2, ge=0, le=4)
    #: Nothing checks that `show_score` has rows to be drawn in. Deciding a
    #: score needs its own rows is the kind of rule v4 exists to remove: a
    #: design may well paint it over the playfield.


class ControlsSpec(StrictModel):
    """Named inputs. The design coins the names -- `jump`, `fire`, `pump` --
    and Studio only guarantees each maps to a key the machine can read."""

    bindings: dict[str, str] = Field(min_length=1, max_length=MAX_BINDINGS)

    @model_validator(mode="after")
    def validate_bindings(self) -> "ControlsSpec":
        import re

        for name, key in self.bindings.items():
            if not re.match(BINDING_PATTERN, name):
                raise ValueError(f"binding name {name!r} is not a usable identifier")
            if key not in KEY_LABELS:
                raise ValueError(
                    f"binding {name!r} names key {key!r}, which is not a "
                    "recognized key label (see KEY_LABELS)"
                )
        counted = Counter(self.bindings.values())
        repeated = sorted(key for key, times in counted.items() if times > 1)
        if repeated:
            raise ValueError("these keys are bound to more than one action: " + ", ".join(repeated))
        return self


class TileSpec(StrictModel):
    """One kind of terrain cell. `traits` is free vocabulary: `solid` means
    nothing to Studio, it means whatever the program decides it means."""

    id: str = Field(pattern=ID_PATTERN)
    #: Printable ASCII only, and neither quote nor backslash: this character
    #: reaches both a C char literal in the written program and the design
    #: prompt, where it is shown as '{char}'.
    char: str = Field(min_length=1, max_length=1, pattern=r"^[\x21-\x26\x28-\x5b\x5d-\x7e]$")
    #: Asset id of this tile's artwork. Unused until the graphics phase.
    art: str | None = Field(default=None, pattern=ID_PATTERN)
    #: Palette entry id this tile is drawn in.
    colour: str | None = Field(default=None, pattern=ID_PATTERN)
    traits: list[Annotated[str, StringConstraints(pattern=ID_PATTERN)]] = Field(
        default_factory=list, max_length=8
    )


class EntitySpec(StrictModel):
    """One kind of actor. `kind` is the design's own word for it."""

    id: str = Field(pattern=ID_PATTERN)
    #: `Prose`, not a bare string, and the field that made the rule
    #: explicit: it is the design's own free-written word, so nothing else
    #: constrains what may be in it, and `minero},{` is what came back from
    #: the drafter for `studio-projects/minero-vigilado`.
    kind: Prose = Field(min_length=1, max_length=32)
    sprite: str | None = Field(default=None, pattern=ID_PATTERN)
    #: Named poses the artwork carries: walk, jump, die.
    poses: list[Annotated[str, StringConstraints(pattern=ID_PATTERN)]] = Field(
        default_factory=list, max_length=8
    )
    #: How many instances of this entity the design has to spend; `structure.py`
    #: reads it as the per-screen budget, so a screen may place at most this
    #: many spawns of one entity, across however many screens it likes.
    count: int = Field(default=1, ge=1, le=64)
    colour: str | None = Field(default=None, pattern=ID_PATTERN)
    #: What this actor does, for the writer and the examiner to read.
    notes: Prose = Field(default="", max_length=240)


class ObservableSpec(StrictModel):
    """A symbol this design exposes on top of the base state contract, so the
    examiner can assert something the contract has no word for."""

    symbol: str = Field(pattern=SYMBOL_PATTERN)
    width: Literal[1, 2] = 1
    meaning: Prose = Field(min_length=1, max_length=160)


class SpawnSpec(StrictModel):
    entity: str = Field(pattern=ID_PATTERN)
    col: int = Field(ge=0, le=39)
    row: int = Field(ge=0, le=24)


class ScreenSpec(StrictModel):
    """One screen of the game, and where it leads."""

    id: str = Field(pattern=ID_PATTERN)
    name: Prose = Field(min_length=1, max_length=24)
    width: int = Field(ge=8, le=40)
    height: int = Field(ge=8, le=25)
    time_limit_seconds: int | None = Field(default=None, ge=10, le=999)
    tiles: list[str] = Field(min_length=8, max_length=25)
    #: Two spawns may share a cell: a stack that separates on the first
    #: frame is the program's business to resolve, not the design's.
    spawns: list[SpawnSpec] = Field(default_factory=list, max_length=64)
    #: Direction taken out of this screen -> the screen it reaches.
    exits: dict[Annotated[str, StringConstraints(pattern=ID_PATTERN)], str] = Field(
        default_factory=dict, max_length=8
    )

    @model_validator(mode="after")
    def validate_grid(self) -> "ScreenSpec":
        if len(self.tiles) != self.height:
            raise ValueError(
                f"screen {self.id} declares height {self.height} " f"but has {len(self.tiles)} rows"
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
    label: Prose = Field(min_length=1, max_length=24)
    target_scene: str = Field(pattern=ID_PATTERN)


class SceneSpec(StrictModel):
    """Flow between screens of presentation. This is not a genre: every game
    has a way in and a way out."""

    id: str = Field(pattern=ID_PATTERN)
    #: What kind of scene this is is vocabulary the design coins on its own
    #: ("title", "credits", "boss_intro", ...). Studio only walks the graph
    #: -- id, next_scene, options -- and never branches on this value.
    kind: str = Field(pattern=ID_PATTERN)
    title: Prose = Field(default="", max_length=32)
    next_scene: str | None = Field(default=None, pattern=ID_PATTERN)
    options: list[MenuOption] = Field(default_factory=list, max_length=6)


class AudioSpec(StrictModel):
    music: bool = False
    #: Effects this design names, in the order it wants them numbered. The
    #: platform library plays effect N; what N sounds like is the library's
    #: business, and what it is called is the design's. Five is what the
    #: library implements, not a statement about what a game may have.
    effects: list[Annotated[str, StringConstraints(pattern=ID_PATTERN)]] = Field(
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
    source: str = Field(pattern=PATH_PATTERN)
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
                f"{self.id}: a sheet {self.width} wide cannot hold " f"{self.frames} whole frames"
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
    mechanics: list[Annotated[Prose, StringConstraints(max_length=200)]] = Field(
        default_factory=list, max_length=32
    )
    screens: list[ScreenSpec] = Field(min_length=1, max_length=64)
    initial_screen: str = Field(pattern=ID_PATTERN)
    scenes: list[SceneSpec] = Field(min_length=2, max_length=16)
    initial_scene: str = Field(default="title", pattern=ID_PATTERN)
    audio: AudioSpec = Field(default_factory=AudioSpec)
    assets: list[AssetSpec] = Field(default_factory=list, max_length=32)
    program_dir: str = Field(default="program", pattern=r"^[A-Za-z0-9_][A-Za-z0-9_./-]{0,63}$")

    @model_validator(mode="after")
    def validate_structure(self) -> "GameProject":
        # Deferred import, not a cycle: `structure` only needs `GameProject`
        # under TYPE_CHECKING. The deferral exists because task 1 (this file)
        # wires the call before task 2 writes the module it calls -- the v4
        # cut's declared red window, not an import-order accident.
        from .structure import structural_errors

        errors = structural_errors(self)
        if errors:
            raise ValueError("\n".join(errors))
        return self
