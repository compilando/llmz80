"""Extensible registry for the machines Studio can target."""

from __future__ import annotations

from importlib.metadata import entry_points
from typing import Generic, Iterable, TypeVar

from dataclasses import dataclass

from .models import GameProject, TargetPlatform, VideoMode

#: The entry-point group an installed package registers a `TargetPack` under,
#: and the only extension seam Studio really has: `target_registry` below
#: iterates it and adds whatever it finds to the built-in machines.
#:
#: It lived in a `plugins.py` that also declared six other protocols --
#: capability modules, code backends, model providers, release exporters --
#: none of which anything ever implemented or checked, and two other group
#: names nothing ever read. Contracts nobody has implemented are not an
#: extension seam; they are a description of one. This is the seam, and it
#: lives with its only reader.
#:
#: `examples/studio_plugin` is a working registration; nothing in this
#: repository registers one, so the loop below finds nothing here.
TARGET_PLUGIN_GROUP = "llmz80.target_plugins"


@dataclass(frozen=True)
class TargetPack:
    id: TargetPlatform
    name: str
    video_modes: tuple[VideoMode, ...]
    binary_budget: int
    data_budget: int
    emulator_adapters: tuple[str, ...]
    #: Audio the generated engine can actually produce on this machine. A design
    #: asking for more is refused by name rather than quietly losing its sound.
    audio_effects: bool = False
    audio_music: bool = False

    def validate(self, project: GameProject) -> list[str]:
        errors = []
        if project.target.platform is not self.id:
            errors.append(f"project target is not {self.id.value}")
        if project.target.video_mode not in self.video_modes:
            errors.append(f"unsupported video mode: {project.target.video_mode.value}")
        if project.budgets.binary_bytes > self.binary_budget:
            errors.append("binary budget exceeds the target pack maximum")
        errors.extend(self.audio_gaps(project))
        return errors

    def audio_gaps(self, project: GameProject) -> list[str]:
        """Audio the design asks for that this target cannot deliver."""
        gaps = []
        if project.audio.effects and not self.audio_effects:
            gaps.append(
                f"{self.name} cannot play sound effects yet; remove them or choose another target"
            )
        if project.audio.music and not self.audio_music:
            gaps.append(
                f"{self.name} cannot play music yet; set audio.music to false "
                "or choose another target"
            )
        return gaps


def audio_gaps(project: GameProject) -> list[str]:
    """Audio gaps for the project's own target, resolved through the registry."""
    pack = target_registry().get(project.target.platform.value)
    return pack.audio_gaps(project)


#: Genres used to be registered here beside targets, as though "what machine
#: is this" and "what kind of game is this" were the same sort of question.
#: They are not: a target is a fact with a fixed set of answers, and a genre
#: was a guess that turned into a straitjacket. Only targets are a registry
#: now; typologies live in typologies.py as prompt material.
BUILTIN_TARGETS = (
    TargetPack(
        TargetPlatform.SPECTRUM,
        "ZX Spectrum 48K",
        (VideoMode.SPECTRUM_BITMAP,),
        24576,
        8192,
        ("zesarux", "fuse"),
        audio_effects=True,
        audio_music=False,
    ),
    TargetPack(
        TargetPlatform.AMSTRAD_CPC,
        "Amstrad CPC 464/6128",
        (VideoMode.CPC_MODE_0, VideoMode.CPC_MODE_1),
        32768,
        12288,
        ("cap32", "caprice32", "cpcec"),
        # No audio yet. Arkos would mean bundling song assets into every
        # generated game, and driving the PSG directly shares the PPI with
        # cpct_scanKeyboard_f, which would put the verified input path at risk.
        audio_effects=False,
        audio_music=False,
    ),
)


T = TypeVar("T")


class Registry(Generic[T]):
    def __init__(self, items: Iterable[T] = ()) -> None:
        self._items: dict[str, T] = {}
        for item in items:
            self.register(item)

    def register(self, item: T) -> None:
        key = str(
            getattr(item, "id").value
            if hasattr(getattr(item, "id"), "value")
            else getattr(item, "id")
        )
        if key in self._items:
            raise ValueError(f"duplicate plugin id: {key}")
        self._items[key] = item

    def get(self, key: str) -> T:
        try:
            return self._items[key]
        except KeyError as exc:
            raise KeyError(f"unknown plugin: {key}") from exc

    def values(self) -> tuple[T, ...]:
        return tuple(self._items.values())


def target_registry(load_external: bool = True) -> Registry[TargetPack]:
    registry = Registry(BUILTIN_TARGETS)
    if load_external:
        for point in entry_points(group=TARGET_PLUGIN_GROUP):
            registry.register(point.load())
    return registry
