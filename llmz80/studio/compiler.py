"""Deterministic source generation from GameProject v2."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from PIL import Image

from llmz80.core.project_mode import create_project_layout
from llmz80.core.build_quality import build_report, select_fresh_artifact, write_build_report
from llmz80.utils.config import load_config

from .codegen import (
    SUPPORTED_ROLES,
    build_actors,
    engine_sources,
    playfield,
    render_config_header,
    render_game_data,
    render_main,
)
from .models import GameProject, TargetPlatform, VideoMode
from .probes import write_probe_report


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


def validate_backend_support(project: GameProject) -> None:
    """Refuse designs the current deterministic engine cannot represent faithfully."""
    unsupported: list[str] = []

    roles = [entity.role for entity in project.entities]
    unknown = sorted({role for role in roles if role not in SUPPORTED_ROLES})
    if unknown:
        unsupported.append("unsupported entity roles: " + ", ".join(unknown))

    players = sum(entity.count for entity in project.entities if entity.role == "player")
    if players != 1:
        unsupported.append(f"player count {players} (supported: 1)")
    collectibles = sum(
        entity.count for entity in project.entities if entity.role == "collectible"
    )
    if collectibles < 1:
        unsupported.append("at least one collectible is required to finish a level")

    actors = build_actors(project)
    if len(actors) > project.budgets.max_entities:
        unsupported.append(
            f"actor count {len(actors)} exceeds the max_entities budget "
            f"{project.budgets.max_entities}"
        )

    columns, rows = playfield(project)
    for level in project.levels:
        if level.width > columns or level.height > rows:
            unsupported.append(
                f"level {level.id} is {level.width}x{level.height} but "
                f"{project.target.video_mode.value} offers {columns}x{rows} playable cells"
            )
        elif level.width * level.height <= len(actors):
            unsupported.append(
                f"level {level.id} has {level.width * level.height} cells for "
                f"{len(actors)} actors plus a free player cell"
            )

    if unsupported:
        raise ValueError(
            "the current Studio engine cannot represent this design faithfully: "
            + "; ".join(unsupported)
        )


def render_project(project: GameProject, output_dir: Path) -> SourceResult:
    validate_backend_support(project)
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    code = render_main(project)
    cpc_mode = 0 if project.target.video_mode is VideoMode.CPC_MODE_0 else 1
    source_assets = [output_dir.parent / asset.source for asset in project.assets]
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

    # The engine is copied before the layout is written so the project manifest
    # records it as owned source, and both toolchains glob it out of src/.
    source_dir = output_dir / "src"
    source_dir.mkdir(parents=True, exist_ok=True)
    for engine_file in engine_sources(project):
        shutil.copy2(engine_file, source_dir / engine_file.name)
    (source_dir / "game_config.h").write_text(render_config_header(project), encoding="utf-8")
    (source_dir / "game_data.c").write_text(render_game_data(project), encoding="utf-8")

    create_project_layout(
        output_dir,
        project.target.platform.value,
        code,
        assets=asset_paths,
        cpc_mode=cpc_mode,
    )

    design = output_dir / "design"
    design.mkdir(exist_ok=True)
    (
        shutil.copy2(output_dir.parent / "game.yml", design / "game.yml")
        if (output_dir.parent / "game.yml").exists()
        else None
    )
    manifest = {
        "schema_version": 2,
        "source_of_truth": "game.yml",
        "generated": True,
        "target": project.target.platform.value,
        "genre": project.genre,
        "modules": sorted(path.name for path in engine_sources(project))
        + ["game_config.h", "game_data.c", "main.c"],
        "actor_count": len(build_actors(project)),
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
    config = load_config(str(config_path))
    platform = project.target.platform.value
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
