"""Public extension contracts for Studio plugins.

Plugins are intentionally project-oriented: they consume validated GameProject
objects and return artifacts or diagnostics. They must not mutate the project.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from .compiler import BuildResult, SourceResult
from .models import GameProject, TargetPlatform
from .planner import ProjectProposal


GENRE_PACK_GROUP = "llmz80.genre_packs"
TARGET_PLUGIN_GROUP = "llmz80.target_plugins"
CAPABILITY_GROUP = "llmz80.capabilities"
EXPORTER_GROUP = "llmz80.exporters"


@runtime_checkable
class CapabilityModule(Protocol):
    id: str
    name: str

    def validate(self, project: GameProject) -> list[str]: ...


@runtime_checkable
class CodeBackend(Protocol):
    platform: TargetPlatform

    def render(self, project: GameProject, output_dir: Path) -> SourceResult: ...
    def build(self, project: GameProject, output_dir: Path) -> BuildResult: ...


@runtime_checkable
class SemanticValidator(Protocol):
    id: str

    def validate(self, project: GameProject, source: str) -> list[str]: ...


@runtime_checkable
class EmulatorAdapter(Protocol):
    platform: TargetPlatform

    def run(self, project: GameProject, output_dir: Path) -> dict[str, Any]: ...


@runtime_checkable
class ModelProvider(Protocol):
    id: str

    def propose(self, project: GameProject, request: str) -> ProjectProposal: ...


@runtime_checkable
class ReleaseExporter(Protocol):
    id: str

    def export(
        self, project: GameProject, build_dir: Path, destination: Path
    ) -> tuple[Path, ...]: ...
