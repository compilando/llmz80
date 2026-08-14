"""Safe YAML persistence and revision history for Studio projects."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml

from .models import GameProject

CURRENT_SCHEMA_VERSION = 4


def migrate(data: dict) -> dict:
    """Bring a persisted document up to the current schema version.

    There is no v3 to v4 upgrade and there is not meant to be one. v3 described
    a game as roles on a two-character grid; v4 lets a design declare its own
    vocabulary, and inventing tiles, entity kinds and mechanics for an old
    document would be authoring a game, not migrating one. Old projects are
    kept as they are and re-designed, which is why this says so out loud.
    """
    version = data.get("schema_version", 1)
    if version == CURRENT_SCHEMA_VERSION:
        return data
    raise ValueError(
        f"this project uses schema version {version}; Studio now reads v4 only. "
        "Designs before v4 described a game in a vocabulary v4 does not have, so "
        "there is no automatic upgrade: start a new project and carry over what "
        "you want from the old game.yml."
    )


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
