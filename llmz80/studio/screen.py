"""State for the Studio command screen, decided without drawing anything.

Precedent for this is `tui.render_map`: a module-level function over plain
data, kept separate from the widgets so it can be read and tested without a
running application. `stage_line` extends that principle from one pane's
terrain to the whole project's status line -- what has been researched,
designed, drawn, written, gated and released.

Every stage's state is read from the design already in memory and from what
the pipeline has written to disk; nothing here calls an API or runs a build.
That is what lets the six stages of a project be known instantly, including
for a project that was never opened.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .compiler import program_sources
from .editing import editing_status
from .models import GameProject
from .reference import load_reference
from .spriting import is_blitter_sprite

#: Named so both this module and its tests can spell a state once. `done` and
#: `pending` are self-explanatory; `failed` means a stage was attempted --
#: something is on disk to show for it -- and what is there was refused,
#: either by validation, by a gate, or by the person who reviewed it. Three
#: states and no more: a fourth invites nuance a one-line status strip cannot
#: show, and every stage below is folded into one of these three even where
#: that folding loses a real distinction (see each helper's docstring for
#: where it does).
StageState = Literal["done", "pending", "failed"]


@dataclass(frozen=True)
class Stage:
    """One cell of the command screen's status line."""

    name: str
    state: StageState
    detail: str = ""


#: The order the status line draws stages in: the pipeline a project moves
#: through, from identifying a real game to shipping one.
STAGE_NAMES = ("referencia", "diseño", "sprites", "programa", "gates", "release")


def stage_line(project: GameProject | None, directory: Path | None) -> list[Stage]:
    """The six-stage status line for `project`, or nothing without one.

    A pure function over the project already in memory and whatever
    `directory` (the project's own folder, the one holding `game.yml`) holds
    on disk. Nothing here is asked to run a build or call an API to find out
    where things stand -- every stage below reads evidence that some earlier,
    explicit action already left behind.

    `directory` is `None` for a project that exists only in memory and has
    never been saved; every disk-backed stage then reads as `pending`; that is
    correct rather than a special case, since nothing has been attempted where
    there is nowhere yet to attempt it.
    """
    if project is None:
        return []
    return [
        _reference_stage(directory),
        _design_stage(project),
        _sprite_stage(project),
        _program_stage(project, directory),
        _gates_stage(directory),
        _release_stage(project, directory),
    ]


def _reference_stage(directory: Path | None) -> Stage:
    """referencia -- what `load_reference` finds beside `game.yml`.

    Three cases on disk, three states: no `reference.yml` at all means the
    game was never researched (`pending`); one that exists but never
    identified a game (`identified=False`) means the research ran and came up
    empty (`failed`) -- a materially different thing from never having looked,
    which is exactly why `load_reference` returning `None` and a dossier with
    `identified=False` must not collapse into the same state here. A dossier
    that identified a game is `done`, and its detail names what was found and
    how much stands behind it, which is the two things `reference_prompt`
    itself leads with.

    `load_reference` raises on a malformed file rather than returning `None`
    for it, precisely so a broken dossier is not mistaken for an absent one;
    that raise is caught here and turned into `failed` rather than escaping to
    the caller, since the command screen has to render one way or another.
    Whether the file is broken YAML or a search that found nothing, both read
    as "attempted, not usable" from the one boolean disk gives us -- the
    detail text is what tells them apart for a person reading the screen.
    """
    if directory is None:
        return Stage("referencia", "pending")
    try:
        dossier = load_reference(directory)
    except ValueError as exc:
        return Stage("referencia", "failed", f"reference.yml is unreadable: {exc}")
    if dossier is None:
        return Stage("referencia", "pending")
    if not dossier.identified:
        return Stage("referencia", "failed", "no matching game was found")
    return Stage(
        "referencia",
        "done",
        f"{dossier.title} · {len(dossier.sources)} fuentes",
    )


def _design_stage(project: GameProject) -> Stage:
    """diseño -- `editing_status`'s own verdict on the design in memory.

    Unlike every other stage, this one has no `pending`: a `GameProject`
    cannot exist without entities, levels and scenes already in place, so
    there is no "not yet attempted" state for its own rules to be in --
    `editing_status` always has an answer, computed fresh from what the
    project holds right now. `ready` is `done`; anything else is `failed`,
    with the solvability and structure failures (and the target-fit error,
    when the design does not even fit the hardware) joined as the detail, the
    same reasons `editing_status` already collects for the terminal UI.
    """
    status = editing_status(project)
    if status["ready"]:
        return Stage("diseño", "done")
    reasons = [*status["solvability_failures"], *status["structure_failures"]]
    if status["backend_error"]:
        reasons.append(status["backend_error"])
    return Stage("diseño", "failed", "; ".join(reasons))


def _sprite_stage(project: GameProject) -> Stage:
    """sprites -- the project's own `kind == "sprite"` assets, measured
    against `is_blitter_sprite`, the one place that rule is written.

    No sprite assets at all is `pending`: nothing has been imported or drawn
    yet. At least one that `is_blitter_sprite` rejects is `failed`: artwork
    exists but the blitter this project targets cannot use it as-is. Every
    sprite asset accepted is `done`.

    What this cannot tell apart: a sprite-generation attempt that raised
    before producing an image leaves the same zero assets as never having
    tried, so it reads as `pending`, not `failed`, indistinguishable from
    "never asked". Closing that gap needs an attempt record -- something like
    `write_report.json` for the program stage below -- persisted by whatever
    drives `SpriteArtist`, which today reports failures only in memory.
    """
    sprites = [asset for asset in project.assets if asset.kind == "sprite"]
    if not sprites:
        return Stage("sprites", "pending")
    accepted = [asset for asset in sprites if is_blitter_sprite(asset)]
    if len(accepted) == len(sprites):
        return Stage("sprites", "done", f"{len(accepted)} sprites")
    return Stage(
        "sprites", "failed", f"{len(accepted)}/{len(sprites)} accepted by the blitter"
    )


def _program_stage(project: GameProject, directory: Path | None) -> Stage:
    """programa -- whether the project owns a program, per `program_sources`.

    This is ownership, not correctness: `store_program` (`generator.py`) only
    ever writes a complete `ProgramSources` -- `main.c` included, enforced by
    that model's own validator -- so once any attempt has ever produced a
    program at all, `main.c` sits in `project.program_dir` and stays `done`
    even if a later attempt's build or acceptance gates failed; that verdict
    belongs to the `gates` stage, not this one.

    Because a rejected attempt still leaves whatever it wrote, the only way
    `main.c` can be missing after an attempt is a writer that raised before
    returning anything -- `write_program` records that in `write_report.json`
    (written by `StudioService.write_program`) without ever calling
    `store_program`. So: no `write_report.json` and no `main.c` is `pending`
    (never attempted); a `write_report.json` with still no `main.c` is
    `failed`, and its `last_error` is the detail; `main.c` present is `done`
    regardless of what either report says.
    """
    if directory is None:
        return Stage("programa", "pending")
    sources = program_sources(project, directory)
    if any(path.name == "main.c" for path in sources):
        return Stage("programa", "done", f"{len(sources)} sources")
    report_path = directory / "write_report.json"
    if not report_path.is_file():
        return Stage("programa", "pending")
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        detail = report.get("last_error") or "the writer produced nothing usable"
    except (OSError, ValueError):
        detail = "write_report.json is unreadable"
    return Stage("programa", "failed", detail)


def _gates_stage(directory: Path | None) -> Stage:
    """gates -- the verdict `studio_quality_report.json` already recorded.

    Written by `StudioService.runtime_test` (`services.py`) at
    `<project>/build/studio_quality_report.json`, the same path
    `release.export_release` itself reads before allowing a release. No file
    is `pending`: the runtime test that would produce it has never completed.
    A file whose `quality_pass` is false is `failed`, with the gates it names
    (design, build, runtime) that did not pass as the detail. `quality_pass`
    true is `done`.

    A report that exists but will not parse is treated as `failed` rather
    than `pending`, on the same reasoning as the reference stage: something
    was clearly attempted, even if what it left behind cannot be trusted.
    """
    if directory is None:
        return Stage("gates", "pending")
    path = directory / "build" / "studio_quality_report.json"
    if not path.is_file():
        return Stage("gates", "pending")
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return Stage("gates", "failed", "studio_quality_report.json is unreadable")
    gates = report.get("gates") or {}
    if report.get("quality_pass"):
        return Stage("gates", "done", f"{len(gates)}/{len(gates)} gates")
    failing = [name for name, passed in gates.items() if not passed]
    return Stage("gates", "failed", "failing: " + ", ".join(failing) if failing else "not passing")


def _release_stage(project: GameProject, directory: Path | None) -> Stage:
    """release -- whether `release.export_release`'s own archive exists.

    `export_release` writes to `<project>/releases/<slug>-<platform>.zip` by
    default (or wherever the caller points it, but the command screen only
    knows the default it would use); its presence is `done`. Its absence is
    `pending`.

    There is no reachable `failed` here: `export_release` raises before it
    creates the `releases` directory or any file in it, whether the reason is
    a missing quality report, a failing one, or missing build evidence -- so a
    rejected release attempt leaves exactly the same nothing on disk that no
    attempt at all does. Telling those apart would need `export_release` (or
    its caller) to persist a record of the attempt and why it was refused,
    the way `write_report.json` already does for the program stage.
    """
    if directory is None:
        return Stage("release", "pending")
    archive = directory / "releases" / f"{project.metadata.slug}-{project.target.platform.value}.zip"
    if archive.is_file():
        return Stage("release", "done", archive.name)
    return Stage("release", "pending")
