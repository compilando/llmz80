"""Project scaffolding: the library, the contracts, and the program the project owns."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from PIL import Image

from llmz80.core.project_mode import create_project_layout
from llmz80.core.build_quality import build_report, select_fresh_artifact, write_build_report
from llmz80.utils.config import load_config

from .acceptance import blitter_sprites, generation_prompt
from .codegen import (
    SUPPORTED_ROLES,
    library_sources,
    playfield,
    render_config_header,
    render_state_header,
)
from .models import GameProject, TargetPlatform, VideoMode
from .probes import write_probe_report
from .sprite_header import render_sprite_header, render_sprite_source
from .sprite_sheet import split_frames
from .spriting import PackedSprite, is_blitter_sprite, pack_cpc, pack_spectrum

#: A palette to quantise CPC sprite pixels against (see `spriting.pack_cpc`).
#: Two other sources were considered and rejected for now:
#:
#: - `PresentationSpec.palette` (models.py) is a list of raw ints with no
#:   defined meaning yet -- it is explicitly documented as unused. Treating
#:   it as RGB here would invent a contract before the task that owns colour
#:   has written one.
#: - The pre-Studio `image_utils.get_palette_for_platform` (repo root) lives
#:   outside the `llmz80` package, pulls in numpy/scipy, calls `sys.exit(1)`
#:   at import time if `resources/platforms.yml` is missing, and its own CPC
#:   colour table has gaps (no RGB past firmware colour 21). Importing it
#:   here would be a layering violation in exchange for an unreliable table.
#:
#: So this is a small fixed default, deliberately matching the four hardware
#: pens `cpc/platform.c`'s `apply_palette()` actually programs at runtime
#: (HW_BLACK, HW_BLUE, HW_BRIGHT_YELLOW, HW_WHITE): what the packer quantises
#: sprites against is then what the machine really shows, in both CPC video
#: modes (mode 1 uses exactly these four pens; mode 0 only ever produces
#: these same four pen indices too, since no more hardware pens are actually
#: set). Real per-design colour selection belongs to a later task.
CPC_DEFAULT_PALETTE: list[tuple[int, int, int]] = [
    (0, 0, 0),        # HW_BLACK
    (0, 0, 255),      # HW_BLUE
    (255, 255, 0),    # HW_BRIGHT_YELLOW
    (255, 255, 255),  # HW_WHITE
]


@dataclass(frozen=True)
class SourceResult:
    output_dir: Path
    main_c: Path
    files: tuple[Path, ...]


@dataclass(frozen=True)
class BuildResult:
    output_dir: Path
    success: bool
    artifact: Path | None
    report: dict[str, object]


def program_sources(project: GameProject, project_dir: Path) -> list[Path]:
    """The project's own C sources, which are written rather than generated."""
    directory = (project_dir / project.program_dir).expanduser()
    if not directory.is_dir():
        return []
    return sorted(
        path for path in directory.iterdir() if path.suffix in {".c", ".h"} and path.is_file()
    )


def validate_design_fits_target(project: GameProject) -> None:
    """Refuse designs the target machine cannot show, whoever writes the code.

    This is about the hardware, not about any particular program: a level wider
    than the character grid cannot be drawn however the program is written.
    """
    unsupported: list[str] = []
    unknown = sorted({entity.role for entity in project.entities} - SUPPORTED_ROLES)
    if unknown:
        unsupported.append("unsupported entity roles: " + ", ".join(unknown))
    columns, rows = playfield(project)
    for level in project.levels:
        if level.width > columns or level.height > rows:
            unsupported.append(
                f"level {level.id} is {level.width}x{level.height} but "
                f"{project.target.video_mode.value} offers {columns}x{rows} playable cells"
            )
    if unsupported:
        raise ValueError("this design does not fit the target: " + "; ".join(unsupported))


#: Share of `budgets.static_data_bytes` that packed sprites may occupy. The
#: rest of that budget is not free once sprites.h exists -- it is what the
#: program's own tables, the level grids the program writer embeds, and
#: generated headers like game_config.h still have to fit in, and none of
#: those are visible here to size precisely. A 50/50 split is a deliberately
#: simple, conservative default: it leaves sprites genuine room (the 2 KB
#: example this task was written against, eight frames across four entities,
#: clears it comfortably against every current budget) while guaranteeing
#: they can never eat the whole number before a line of game code exists.
SPRITE_STATIC_DATA_SHARE = 0.5


def packed_sprite_bytes(packed_sprites: dict[str, PackedSprite]) -> int:
    """Total bytes `sprites.h` will emit: every sprite's data plus its mask.

    Spectrum sprites keep mask separate from data (`PackedSprite.mask` is a
    same-length array); CPC sprites interleave the mask into `data` and leave
    `.mask` empty (see `spriting.pack_cpc`'s docstring). Summing both fields
    unconditionally is correct either way -- on the CPC it just adds zero.
    """
    return sum(len(sprite.data) + len(sprite.mask) for sprite in packed_sprites.values())


def validate_sprite_budget(project: GameProject, packed_sprites: dict[str, PackedSprite]) -> None:
    """Refuse a design whose packed sprites alone blow the static data budget.

    Only sprites are weighed against their reserved share here -- see
    `SPRITE_STATIC_DATA_SHARE` for why sprites cannot be allowed the whole
    budget. Nothing else Studio scaffolds is sized against this ceiling; the
    program's own tables are the program's business.
    """
    sprite_bytes = packed_sprite_bytes(packed_sprites)
    sprite_budget = int(project.budgets.static_data_bytes * SPRITE_STATIC_DATA_SHARE)
    if sprite_bytes > sprite_budget:
        raise ValueError(
            f"packed sprites are {sprite_bytes} bytes but the sprite budget is "
            f"{sprite_budget} bytes -- {int(SPRITE_STATIC_DATA_SHARE * 100)}% of the "
            f"{project.budgets.static_data_bytes} byte budgets.static_data_bytes, the rest "
            "reserved for the program's own tables, level grids and generated config that "
            "share the same budget. Drop a frame or an entity, or raise static_data_bytes."
        )


#: Matches a `//` remark, a `/* ... */` block, or a quoted string/char
#: literal, so `sprite_usage_errors` can blank each out before searching for
#: a real call -- a comment or string that merely mentions `plat_sprite` is
#: not a call to it. `re.DOTALL` lets the block-comment branch span lines;
#: `.count("\n")` in the substitution keeps line numbers meaningless here
#: (nothing downstream reports a line) but keeps the code roughly the same
#: length, which costs nothing and avoids joining two real statements that
#: happened to sit either side of a stripped comment.
_COMMENT_OR_STRING_RE = re.compile(
    r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*.*?\*/', re.DOTALL
)

#: A call to `plat_sprite`, the one function `resources/studio_lib/*/platform.c`
#: exposes for drawing an entity's art (see `platform.h`'s declaration and
#: `acceptance.py`'s "Sprites:" prompt line, which tells the writer this exact
#: name). Matched with a word boundary and an open paren so a substring like
#: `my_plat_sprite_helper(` does not count.
_SPRITE_CALL_RE = re.compile(r"\bplat_sprite\s*\(")


def _blanked(code: str) -> str:
    """`code` with every comment and string/char literal replaced by blanks."""
    return _COMMENT_OR_STRING_RE.sub(lambda match: "\n" * match.group(0).count("\n"), code)


def sprite_usage_errors(project: GameProject, sources: dict[str, str]) -> list[str]:
    """Refuse a program that has drawable sprites and never draws with any of them.

    A real end-to-end run exposed exactly this gap: a project with three
    generated sprites, a writing prompt that named each one by its
    `SPRITE_<ID>` constant and told the model to draw actors with
    `plat_sprite`, and an accepted program that called `plat_cell` seven
    times and `plat_sprite` zero. Nothing in the existing gates catches
    that -- the build compiles, the acceptance scenarios read state the
    program updates without ever putting the sprite on screen, and the
    animation gate (`feel.animation_report`) correctly abstains rather than
    fail when `g_anim_frame` was never declared, because abstaining is the
    only honest answer for a target (the CPC) whose emulator cannot read
    memory at all. This check is not that gate and does not touch its rule;
    it is the narrower, source-level fact that a project which *has* sprites
    the blitter would accept (`spriting.is_blitter_sprite`, via
    `acceptance.blitter_sprites` -- the one place that question is answered,
    see that function's own docstring) and a program that never once calls
    the function named to draw them are not a game that used its art.

    `sources` is the program's own files only (name -> body), never the
    library Studio copies in beside them: `resources/studio_lib/*/platform.c`
    both declares and calls `plat_sprite` internally, so scanning it would
    make this check pass unconditionally and catch nothing.

    Strictness: this is a source-level grep, after blanking out comments and
    string literals (`_blanked`) so a remark that merely mentions the name,
    or a string the program happens to print, cannot satisfy it. It is
    cheap and deterministic, and it is also shallow on purpose -- proving a
    sprite reached the screen needs the emulator, the way
    `feel.animation_report` and the acceptance scenarios already do for the
    claims only runtime evidence can settle. What this cannot catch: a call
    inside dead code (an `if (0)`, a branch the scripted acceptance inputs
    never take, a function nothing calls). That is a real gap, but it is the
    same gap every other capability check in
    `llmz80.core.semantic_validation.SemanticValidator` already accepts (its
    frame-pacing and input checks are the same kind of "is the call present"
    grep) rather than a new one invented here, and closing it needs the same
    machinery the animation gate uses, not a second copy of it.

    `g_anim_frame` is deliberately not required here. Whether the art
    animates is the animation gate's question, already answered correctly
    (including its abstain-on-CPC rule, which this must not disturb); whether
    the art is drawn at all is this one. A design can legitimately have a
    single-frame sprite that never animates, and conflating the two would
    make this check fail designs the animation gate was never meant to
    reject.
    """
    sprites = blitter_sprites(project)
    if not sprites:
        return []
    code = "\n".join(_blanked(body) for body in sources.values())
    if _SPRITE_CALL_RE.search(code):
        return []
    names = ", ".join(f"SPRITE_{asset.id.upper()}" for asset in sprites)
    return [
        f"this design has sprites ({names}) packed into sprites.h, but the program "
        "never calls plat_sprite -- draw at least one entity with "
        "plat_sprite(col, row, sprite, frame) instead of only plat_cell."
    ]


def render_project(project: GameProject, output_dir: Path) -> SourceResult:
    """Scaffold a buildable project around the program the project owns.

    Studio contributes the platform library, a header of target constants, the
    state contract to define, and the acceptance contract to satisfy. It does
    not contribute gameplay; `program_dir` does.
    """
    validate_design_fits_target(project)
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    project_dir = output_dir.parent
    cpc_mode = 0 if project.target.video_mode is VideoMode.CPC_MODE_0 else 1

    source_assets = [project_dir / asset.source for asset in project.assets]
    missing = [str(path) for path in source_assets if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing project assets: " + ", ".join(missing))
    asset_paths: list[Path] = []
    normalized_dir = output_dir / "generated_assets"
    normalized_dir.mkdir(exist_ok=True)
    pixels_per_byte = (
        8 if project.target.platform is TargetPlatform.SPECTRUM else (2 if cpc_mode == 0 else 4)
    )
    for asset, source in zip(project.assets, source_assets):
        with Image.open(source) as original:
            image = original.convert("RGBA")
            padded_width = (
                (image.width + pixels_per_byte - 1) // pixels_per_byte
            ) * pixels_per_byte
            if padded_width == image.width:
                asset_paths.append(source)
                continue
            normalized = Image.new("RGBA", (padded_width, image.height), (0, 0, 0, 0))
            normalized.paste(image, (0, 0))
            target = normalized_dir / f"{asset.id}.png"
            normalized.save(target)
            asset_paths.append(target)

    source_dir = output_dir / "src"
    source_dir.mkdir(parents=True, exist_ok=True)
    for stale in source_dir.glob("*"):
        if stale.is_file() and stale.suffix in {".c", ".h"}:
            stale.unlink()
    for piece in library_sources(project):
        shutil.copy2(piece, source_dir / piece.name)
    (source_dir / "game_config.h").write_text(render_config_header(project), encoding="utf-8")
    (source_dir / "game_state.h").write_text(render_state_header(), encoding="utf-8")

    # sprites.h is written unconditionally -- render_sprite_header({}) is a
    # valid, SPRITE_COUNT-0 header, and every project's platform.c includes
    # "sprites.h" (see plat_sprite), so a design with no sprite-kind assets
    # still needs one to build.
    packed_sprites: dict[str, PackedSprite] = {}
    for asset, source in zip(project.assets, asset_paths):
        if not is_blitter_sprite(asset):
            # Not a blitter sprite (see `spriting.is_blitter_sprite`): leave it
            # to the generic assets.c/assets.h conversion below, the way an
            # imported asset was handled before sprites.h existed.
            continue
        with Image.open(source) as sheet:
            frames = split_frames(sheet.convert("RGBA"), asset.frames)
        packed_sprites[asset.id] = (
            pack_spectrum(frames)
            if project.target.platform is TargetPlatform.SPECTRUM
            else pack_cpc(frames, mode=cpc_mode, palette=CPC_DEFAULT_PALETTE)
        )
    validate_sprite_budget(project, packed_sprites)
    (source_dir / "sprites.h").write_text(render_sprite_header(packed_sprites), encoding="utf-8")
    # The tables sprites.h only declares `extern` are defined here, once. Both
    # target builds pick this up the same way they pick up every other file in
    # src/: the Spectrum build globs src/*.c, and CPCtelera's build_config.mk
    # globs $(SRCDIR)/*.c -- neither needs telling about a new file by name.
    (source_dir / "sprites.c").write_text(render_sprite_source(packed_sprites), encoding="utf-8")

    owned = program_sources(project, project_dir)
    # A program that names one of its own files the same as a file Studio just
    # wrote (sprites.h above, platform.c/.h and game_config.h/game_state.h
    # below) would silently overwrite it in the copy loop that follows --
    # e.g. a program-supplied sprites.h that shadows the generated one and
    # loses every SPRITE_<ID> constant, with no error at all until (or unless)
    # a diagnostic downstream happens to mention it. Refuse that outright
    # instead: the model gets a clear, fixable error rather than a silently
    # broken build.
    reserved = {piece.name for piece in library_sources(project)} | {
        "game_config.h",
        "game_state.h",
        "sprites.h",
        "sprites.c",
    }
    shadowing = sorted(path.name for path in owned if path.name in reserved)
    if shadowing:
        raise ValueError(
            "the program may not define these files -- Studio generates them: "
            + ", ".join(shadowing)
        )
    for path in owned:
        shutil.copy2(path, source_dir / path.name)
    main_c = next((path for path in owned if path.name == "main.c"), None)
    if main_c is not None:
        shutil.copy2(main_c, output_dir / "main.c")

    create_project_layout(
        output_dir,
        project.target.platform.value,
        (output_dir / "main.c").read_text(encoding="utf-8") if main_c else "",
        assets=asset_paths,
        cpc_mode=cpc_mode,
    )
    (output_dir / "CONTRACT.md").write_text(generation_prompt(project), encoding="utf-8")

    design = output_dir / "design"
    design.mkdir(exist_ok=True)
    if (project_dir / "game.yml").exists():
        shutil.copy2(project_dir / "game.yml", design / "game.yml")
    manifest = {
        "schema_version": 3,
        "source_of_truth": "game.yml for the design, "
        f"{project.program_dir}/ for the program",
        "generated": False,
        "target": project.target.platform.value,
        "genre": project.genre,
        "library": sorted(path.name for path in library_sources(project)),
        "written_headers": ["game_config.h", "game_state.h"],
        "program": sorted(path.name for path in owned),
        "program_present": main_c is not None,
        "playfield_cells": list(playfield(project)),
    }
    (output_dir / "studio_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "generation_spec.json").write_text(
        json.dumps(
            {
                "schema_version": 2,
                "platform": project.target.platform.value,
                "archetype": project.genre,
                "budgets": {
                    "program_binary_bytes": project.budgets.binary_bytes,
                    "static_data_bytes": project.budgets.static_data_bytes,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    files = tuple(sorted(path for path in output_dir.rglob("*") if path.is_file()))
    return SourceResult(output_dir=output_dir, main_c=output_dir / "main.c", files=files)


def build_project(
    project: GameProject, output_dir: Path, config_path: Path = Path("config.yml")
) -> BuildResult:
    """Build a rendered project with the real toolchain and enforce warning/resource policy."""
    output_dir = output_dir.expanduser().resolve()
    if not (output_dir / "main.c").exists():
        render_project(project, output_dir)
    owned = program_sources(project, output_dir.parent)
    if not owned:
        # Without this the toolchain reports "undefined symbol: _main", which
        # says nothing about the project actually being empty.
        raise FileNotFoundError(
            f"this project has no program yet: put its C sources in "
            f"{project.program_dir}/, or run `llmz80 project write` to have them "
            f"written. The contract they must satisfy is in build/CONTRACT.md"
        )
    platform = project.target.platform.value
    sprite_errors = sprite_usage_errors(
        project, {path.name: path.read_text(encoding="utf-8") for path in owned}
    )
    if sprite_errors:
        # Refused without spending a compile: the toolchain has nothing to add
        # to a fact already visible in the sources, and `build_report` is
        # reused rather than hand-shaped so this refusal is a `quality_pass:
        # False` build report exactly like any other, which is what carries
        # it into `generator.repair_prompt`'s "THE BUILD FAILED" section --
        # the writer sees it and gets another attempt, instead of the whole
        # repair loop crashing on an uncaught exception.
        report = build_report(
            platform=platform,
            output_dir=output_dir,
            command=[],
            return_code=1,
            stdout="",
            stderr="\n".join(sprite_errors),
            artifacts=[],
        )
        report["stdout"] = ""
        report["stderr"] = "\n".join(sprite_errors)
        report["sprite_usage_errors"] = sprite_errors
        write_build_report(report, output_dir / "build_report.json")
        return BuildResult(output_dir=output_dir, success=False, artifact=None, report=report)
    config = load_config(str(config_path))
    cpct_path = None
    if platform == "spectrum":
        compiler = config.get("compiler", {}).get("spectrum", {})
        command = [compiler.get("c_compiler", "zcc"), *compiler.get("params", "").split()]
        sources = [
            str(path.relative_to(output_dir)) for path in sorted((output_dir / "src").glob("*.c"))
        ]
        # -m emits output.map, which probes.json needs to locate engine state.
        command += [*sources, "-m", "-o", "output", "-create-app", "-subtype=default"]
    else:
        from llm_z80 import prepare_amstrad_cpc_build_project, resolve_cpct_path

        cpct_path = resolve_cpct_path(config)
        if cpct_path is None:
            raise RuntimeError("CPCtelera was not found; configure CPCT_PATH")
        if not prepare_amstrad_cpc_build_project(output_dir, cpct_path):
            raise RuntimeError("could not prepare the CPCtelera project")
        command = ["make", f"CPCT_PATH={cpct_path}/"]

    process = subprocess.run(command, cwd=output_dir, capture_output=True, text=True, check=False)
    patterns = ("*.tap", "*.bin") if platform == "spectrum" else ("*.dsk", "*.bin")
    artifacts = [path for pattern in patterns for path in output_dir.rglob(pattern)]
    canonical = output_dir / ("output.tap" if platform == "spectrum" else "output.dsk")
    containers = [path for path in artifacts if path.suffix.casefold() == canonical.suffix]
    candidate = select_fresh_artifact(canonical, containers)
    report = build_report(
        platform=platform,
        output_dir=output_dir,
        command=command,
        return_code=process.returncode,
        stdout=process.stdout,
        stderr=process.stderr,
        artifacts=artifacts,
        cpct_path=cpct_path,
        candidate_artifact=candidate,
    )
    if (
        report["quality_pass"]
        and candidate is not None
        and candidate.resolve() != canonical.resolve()
    ):
        shutil.copy2(candidate, canonical)
        artifacts.append(canonical)
        report = build_report(
            platform=platform,
            output_dir=output_dir,
            command=command,
            return_code=process.returncode,
            stdout=process.stdout,
            stderr=process.stderr,
            artifacts=artifacts,
            cpct_path=cpct_path,
            candidate_artifact=canonical,
        )
    report["stdout"] = process.stdout[-12000:]
    report["stderr"] = process.stderr[-12000:]
    if report["quality_pass"]:
        report["probes"] = write_probe_report(output_dir, platform)
    write_build_report(report, output_dir / "build_report.json")
    return BuildResult(
        output_dir=output_dir,
        success=bool(report["quality_pass"]),
        artifact=canonical if canonical.is_file() else candidate,
        report=report,
    )
