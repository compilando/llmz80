"""Safe YAML persistence and revision history for Studio projects."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml

from .layout import default_spawns, default_tiles
from .models import GameProject

CURRENT_SCHEMA_VERSION = 3


class _EntityView:
    """Minimal entity shape the layout helpers need, read from raw YAML."""

    def __init__(self, document: dict) -> None:
        self.id = document["id"]
        self.role = document["role"]
        self.count = int(document.get("count", 1))


def _upgrade_v2_to_v3(data: dict) -> dict:
    """Author terrain and spawns for a design that predates the tile grid.

    v2 levels carried only dimensions, and the engine derived positions itself.
    Migration authors that same layout into the document so it becomes editable
    content rather than an implicit generator rule.
    """
    entities = [_EntityView(entity) for entity in data.get("entities", [])]
    genre = data.get("genre", "")
    levels = []
    for index, level in enumerate(data.get("levels", [])):
        upgraded = dict(level)
        width = int(level["width"])
        height = int(level["height"])
        tiles = default_tiles(genre, width, height, index)
        upgraded["tiles"] = tiles
        upgraded["spawns"] = [
            spawn.model_dump(mode="json")
            for spawn in default_spawns(entities, tiles, width, height, index)
        ]
        levels.append(upgraded)
    upgraded_document = dict(data)
    upgraded_document["levels"] = levels
    upgraded_document["schema_version"] = 3
    return upgraded_document


#: Applied in order until the document reaches `CURRENT_SCHEMA_VERSION`.
MIGRATIONS = {2: _upgrade_v2_to_v3}


def migrate(data: dict) -> dict:
    """Bring a persisted document up to the current schema version."""
    version = data.get("schema_version", 1)
    while version != CURRENT_SCHEMA_VERSION:
        upgrade = MIGRATIONS.get(version)
        if upgrade is None:
            raise ValueError(
                f"cannot migrate schema version {version} to {CURRENT_SCHEMA_VERSION}"
            )
        data = upgrade(data)
        version = data["schema_version"]
    return data


class ProjectStore:
    filename = "game.yml"

    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace.expanduser().resolve()

    def project_path(self, slug: str) -> Path:
        return self.workspace / slug

    def list_projects(self) -> list[Path]:
        if not self.workspace.exists():
            return []
        return sorted(path.parent for path in self.workspace.glob(f"*/{self.filename}"))

    def load(self, location: str | Path) -> GameProject:
        path = Path(location).expanduser()
        if path.is_dir() or not path.suffix:
            candidate = path / self.filename
            path = (
                candidate
                if candidate.exists() or path.is_dir()
                else self.project_path(str(path)) / self.filename
            )
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"invalid project document: {path}")
        return GameProject.model_validate(migrate(data))

    def save(self, project: GameProject, directory: Path | None = None) -> Path:
        directory = (directory or self.project_path(project.metadata.slug)).expanduser().resolve()
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / self.filename
        old = path.read_text(encoding="utf-8") if path.exists() else None
        project.metadata.updated_at = datetime.now(timezone.utc)
        text = yaml.safe_dump(
            project.model_dump(mode="json"),
            allow_unicode=True,
            sort_keys=False,
            width=100,
        )
        if old is not None and old != text:
            revisions = directory / ".llmz80" / "revisions"
            revisions.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            (revisions / f"game-{stamp}.yml").write_text(old, encoding="utf-8")
        temporary = path.with_suffix(".yml.tmp")
        temporary.write_text(text, encoding="utf-8")
        temporary.replace(path)
        return path

    def create(self, project: GameProject) -> Path:
        directory = self.project_path(project.metadata.slug)
        if (directory / self.filename).exists():
            raise FileExistsError(f"project already exists: {directory}")
        self.save(project, directory)
        return directory
