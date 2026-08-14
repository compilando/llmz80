"""Edits to a `GameProject`, each one validated, none of them an interface.

Every operation takes a project and returns a new validated project; one that
would break a hard invariant raises `EditError` with a message meant to be
read by whoever asked for the edit.

There used to be eighteen of these -- paint a cell, fill a screen, resize one,
move a spawn, add an entity, retitle a scene, set the audio, say what a save
changed. They were an API for a map editor that was never built, kept alive by
a terminal wizard that opened panels over it, and when the wizard went they
were left with no caller but their own tests. An API documented as dead is
still an API: in three months nobody remembers it was dead on purpose.

So what is left is what something really calls, and nothing else:
`rename_project`, from `pipeline.create`, so a project carries the brief it
was made with; `editing_status`, from `screen.stage_line` and `planner`, to
ask whether a design still fits its machine. The rest is in git if it is ever
wanted back.
"""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from .compiler import validate_design_fits_target
from .models import GameProject


class EditError(ValueError):
    """An edit the design cannot accept, phrased for the person editing."""


def _validated(document: dict[str, Any]) -> GameProject:
    try:
        return GameProject.model_validate(document)
    except ValidationError as exc:
        first = exc.errors()[0]
        message = first.get("msg", "invalid edit")
        raise EditError(message.removeprefix("Value error, ")) from exc


def _document(project: GameProject) -> dict[str, Any]:
    return project.model_dump(mode="json")


def editing_status(project: GameProject) -> dict[str, Any]:
    """Gate state for the design as it currently stands.

    Only one question survives here: does this design fit the machine. Whether
    it can be played is no longer answerable by reading the map -- that was a
    rule about grid games, and it lied about anything with a jump -- and
    belongs to the examiner and the emulator.
    """
    backend_error: str | None = None
    try:
        validate_design_fits_target(project)
    except ValueError as exc:
        backend_error = str(exc)
    return {
        "buildable": backend_error is None,
        "backend_error": backend_error,
        "ready": backend_error is None,
    }


def rename_project(
    project: GameProject,
    title: str,
    *,
    style: str | None = None,
    brief: str | None = None,
) -> GameProject:
    """Apply the design's scalar fields -- title, style, brief -- in one
    validated step.

    Grouped because they are decided together: applying them one at a time
    would reject an edit that is only valid once all of them are in place.
    `pipeline.create` uses it for the brief alone, which is the one field a
    project cannot be created holding and cannot usefully be without.
    """
    document = _document(project)
    document["metadata"]["title"] = title
    if style is not None:
        document["presentation"]["style"] = style
    if brief is not None:
        document["metadata"]["brief"] = brief
    return _validated(document)
