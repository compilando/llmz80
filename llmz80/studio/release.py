"""Reproducible release archives gated by complete quality evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from .models import GameProject


def export_release(project: GameProject, directory: Path, destination: Path | None = None) -> Path:
    build_dir = directory / "build"
    quality_path = build_dir / "studio_quality_report.json"
    if not quality_path.is_file():
        raise RuntimeError("run the complete Studio runtime test before exporting a release")
    quality = json.loads(quality_path.read_text(encoding="utf-8"))
    if not quality.get("quality_pass"):
        raise RuntimeError("release export requires every Studio quality gate to pass")
    artifact_name = "output.tap" if project.target.platform.value == "spectrum" else "output.dsk"
    required = [
        directory / "game.yml",
        build_dir / artifact_name,
        build_dir / "build_report.json",
        build_dir / "emulator_report.json",
        quality_path,
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing release evidence: " + ", ".join(missing))
    releases = directory / "releases"
    releases.mkdir(exist_ok=True)
    destination = (
        destination or releases / f"{project.metadata.slug}-{project.target.platform.value}.zip"
    )
    destination = destination.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    entries = {
        "game.yml": required[0].read_bytes(),
        artifact_name: required[1].read_bytes(),
        "reports/build_report.json": required[2].read_bytes(),
        "reports/emulator_report.json": required[3].read_bytes(),
        "reports/studio_quality_report.json": required[4].read_bytes(),
    }
    notes = (
        f"{project.metadata.title}\n"
        f"Target: {project.target.platform.value}\n"
        f"Genre: {project.genre}\n"
        f"Levels: {project.gameplay.level_count}\n"
        "Built and runtime-verified by LLMZ80 Studio.\n"
    ).encode("utf-8")
    entries["RELEASE_NOTES.txt"] = notes
    checksums = "".join(
        f"{hashlib.sha256(data).hexdigest()}  {name}\n" for name, data in sorted(entries.items())
    ).encode("ascii")
    entries["SHA256SUMS"] = checksums
    with ZipFile(destination, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(entries.items()):
            info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)
    return destination
