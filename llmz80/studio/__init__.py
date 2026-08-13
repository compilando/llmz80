"""Guided, project-first game creation for LLMZ80."""

from .models import GameProject

__all__ = ["GameProject", "ProjectStore"]


def __getattr__(name: str):
    # Deferred so that `llmz80.studio.models` stays importable on its own
    # during the v4 schema cut: `store` still pulls in consumers (`layout`,
    # ...) that haven't been migrated off the v3 vocabulary yet, and eagerly
    # importing them here would make the package itself fail to import.
    if name == "ProjectStore":
        from .store import ProjectStore

        return ProjectStore
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
