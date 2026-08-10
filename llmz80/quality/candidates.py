"""Deterministic scoring and selection across fully gated generation runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def score_candidate(run_dir: Path) -> dict[str, Any]:
    build = _read(run_dir / "build_report.json")
    semantic = _read(run_dir / "semantic_report.json")
    emulator = _read(run_dir / "emulator_report.json")
    runtime_required = emulator.get("requested_full") is True
    runtime_pass = emulator.get("runtime_verified") is True and emulator.get("quality_pass") is True
    score = 0.0
    score += 50.0 if build.get("quality_pass") else 0.0
    score += 20.0 if semantic.get("quality_pass") else 0.0
    score += 15.0 if emulator.get("runtime_verified") and emulator.get("boot") else 0.0
    score += 10.0 if emulator.get("runtime_verified") and emulator.get("visual_change") else 0.0
    score += 5.0 if emulator.get("runtime_verified") and emulator.get("input_transition") else 0.0
    score -= 5.0 * int(build.get("unexpected_warning_count", 0))
    score -= 10.0 * len(semantic.get("errors", []))
    score -= 1.0 * len(semantic.get("warnings", []))
    binary = (build.get("program_binary") or {}).get("size_bytes")
    quality_pass = bool(
        build.get("quality_pass")
        and semantic.get("quality_pass")
        and (runtime_pass if runtime_required else True)
    )
    return {
        "run_dir": str(run_dir), "score": score,
        "quality_pass": quality_pass,
        "runtime_verified": bool(emulator.get("runtime_verified")),
        "program_binary_size": binary,
    }


def select_candidate(run_dirs: Iterable[Path]) -> dict[str, Any]:
    candidates = [score_candidate(path) for path in run_dirs]
    if not candidates:
        raise ValueError("at least one candidate is required")
    candidates.sort(key=lambda item: (
        -item["score"],
        item["program_binary_size"] if item["program_binary_size"] is not None else 10**9,
        item["run_dir"],
    ))
    return {"schema_version": 1, "selected": candidates[0], "candidates": candidates}


def write_selection(report: dict[str, Any], path: Path) -> None:
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
