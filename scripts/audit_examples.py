#!/usr/bin/env python3
"""Compile every program that the local retrieval catalog may select."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from llmz80.core.code_context import find_nearest_makefile  # noqa: E402
from llmz80.core.build_quality import classify_build_warnings  # noqa: E402
from llmz80.core.example_catalog import ExampleCatalog  # noqa: E402


def resolve_cpct_path() -> Path | None:
    candidates = (
        os.environ.get("CPCT_PATH"),
        str(Path.home() / "cpctelera" / "cpctelera"),
        str(Path.home() / "cpctelera"),
        "/opt/cpctelera",
    )
    for candidate in candidates:
        if candidate:
            path = Path(candidate).expanduser().resolve()
            if (path / "cfg" / "global_main_makefile.mk").exists():
                return path
    return None


def compile_spectrum(source: Path, work_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "zcc", "+zx", "-vn", "-O3", "-clib=sdcc_iy", str(source),
            "-o", str(work_dir / "output"), "-create-app", "-subtype=default",
        ],
        cwd=work_dir,
        capture_output=True,
        text=True,
        check=False,
    )


def compile_cpc(source: Path, examples_dir: Path, work_dir: Path, cpct_path: Path) -> subprocess.CompletedProcess[str]:
    makefile = find_nearest_makefile(source, examples_dir)
    if makefile is None:
        return subprocess.CompletedProcess([], 2, "", "No Makefile found")
    project_copy = work_dir / "project"
    shutil.copytree(makefile.parent, project_copy)
    return subprocess.run(
        ["make", f"CPCT_PATH={cpct_path}/"],
        cwd=project_copy,
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--platform", choices=("all", "spectrum", "amstrad_cpc"), default="all"
    )
    parser.add_argument("--json", type=Path, help="Optional JSON report path")
    args = parser.parse_args()

    platforms = ("spectrum", "amstrad_cpc") if args.platform == "all" else (args.platform,)
    cpct_path = resolve_cpct_path() if "amstrad_cpc" in platforms else None
    if "spectrum" in platforms and shutil.which("zcc") is None:
        print("ERROR: zcc is not installed", file=sys.stderr)
        return 2
    if "amstrad_cpc" in platforms and (shutil.which("make") is None or cpct_path is None):
        print("ERROR: make/CPCtelera is not available", file=sys.stderr)
        return 2

    report = []
    for platform in platforms:
        roots = [REPO_ROOT / "examples" / platform]
        if platform == "amstrad_cpc":
            roots.append(REPO_ROOT / "examples" / "amstrad_cpc_level2")
        catalog = ExampleCatalog(platform, roots)
        for entry in catalog.discover():
            with tempfile.TemporaryDirectory(prefix="llmz80-example-") as temp:
                work_dir = Path(temp)
                if platform == "spectrum":
                    result = compile_spectrum(entry["file_path"], work_dir)
                else:
                    assert cpct_path is not None
                    result = compile_cpc(
                        entry["file_path"], entry["examples_dir"], work_dir, cpct_path
                    )
                combined = (result.stdout or "") + (result.stderr or "")
                warnings = classify_build_warnings(
                    combined,
                    cpct_path=cpct_path if platform == "amstrad_cpc" else None,
                )
                item = {
                    "platform": platform,
                    "path": entry["path"],
                    "success": result.returncode == 0 and not warnings["structural"],
                    "returncode": result.returncode,
                    "warnings": warnings,
                    "error_tail": "\n".join(combined.splitlines()[-20:]) if result.returncode else "",
                }
                report.append(item)
                state = "PASS" if item["success"] else "FAIL"
                print(f"{state} {platform} {entry['path']}")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    passed = sum(item["success"] for item in report)
    print(f"\n{passed}/{len(report)} catalog programs compile")
    return 0 if passed == len(report) else 1


if __name__ == "__main__":
    raise SystemExit(main())
