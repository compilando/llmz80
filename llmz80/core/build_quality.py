"""Structured build diagnostics and artifact quality reports."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable, Sequence

WARNING_RE = re.compile(r"\bwarning\b", re.IGNORECASE)
WARNING_CODE_RE = re.compile(r"\bwarning\s+(\d+)\s*:", re.IGNORECASE)
STRUCTURAL_PATTERNS = (
    re.compile(r"unknown compiler option", re.IGNORECASE),
    re.compile(r"unrecogni[sz]ed (?:command line )?option", re.IGNORECASE),
    re.compile(r"option .+ ignored", re.IGNORECASE),
    re.compile(r"unknown target|unknown subtype", re.IGNORECASE),
)
SOURCE_PATH_RE = re.compile(r"(?:^|[/\\])(?:src[/\\])?main\.c(?::|\(|$)", re.IGNORECASE)

# SDCC emits this informational optimizer diagnostic for valid control-flow
# transformations. It is retained in the report but does not lower quality.
ALLOWED_WARNING_CODES = {"110"}


def select_fresh_artifact(canonical: Path, artifacts: Iterable[Path]) -> Path | None:
    """Prefer the newest non-canonical build output over a stale canonical copy."""
    canonical_resolved = canonical.resolve()
    generated = [
        path for path in artifacts if path.is_file() and path.resolve() != canonical_resolved
    ]
    if generated:
        return max(generated, key=lambda path: path.stat().st_mtime_ns)
    return canonical if canonical.is_file() else None


def classify_build_warnings(output: str, cpct_path: Path | None = None) -> dict[str, list[str]]:
    """Classify warning lines into actionable and known-noise groups."""
    groups: dict[str, list[str]] = {
        "structural": [],
        "source": [],
        "sdk": [],
        "allowed": [],
        "other": [],
    }
    cpct_text = str(cpct_path.resolve()) if cpct_path else ""

    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line or not WARNING_RE.search(line):
            continue
        if any(pattern.search(line) for pattern in STRUCTURAL_PATTERNS):
            groups["structural"].append(line)
            continue
        code_match = WARNING_CODE_RE.search(line)
        if code_match and code_match.group(1) in ALLOWED_WARNING_CODES:
            groups["allowed"].append(line)
            continue
        if cpct_text and cpct_text in line:
            groups["sdk"].append(line)
            continue
        if SOURCE_PATH_RE.search(line):
            groups["source"].append(line)
            continue
        groups["other"].append(line)

    return groups


def _artifact_records(output_dir: Path, artifacts: Iterable[Path]) -> list[dict[str, Any]]:
    records = []
    for artifact in sorted({path.resolve() for path in artifacts}):
        try:
            relative = artifact.relative_to(output_dir.resolve())
        except ValueError:
            relative = artifact
        records.append({"path": str(relative), "size_bytes": artifact.stat().st_size})
    return records


def detect_program_binary(platform: str, output_dir: Path) -> Path | None:
    """Return the payload binary whose size reflects the program, not its container."""
    candidates = (
        [output_dir / "output_CODE.bin"]
        if platform == "spectrum"
        else [output_dir / "obj" / "program.bin", output_dir / "program.bin"]
    )
    return next((path for path in candidates if path.is_file()), None)


def build_report(
    *,
    platform: str,
    output_dir: Path,
    command: Sequence[str],
    return_code: int,
    stdout: str,
    stderr: str,
    artifacts: Iterable[Path],
    cpct_path: Path | None = None,
    candidate_artifact: Path | None = None,
) -> dict[str, Any]:
    """Create a serialisable report for one real-toolchain invocation."""
    artifact_records = _artifact_records(output_dir, artifacts)
    warnings = classify_build_warnings(stdout + "\n" + stderr, cpct_path=cpct_path)
    program_binary = detect_program_binary(platform, output_dir)
    canonical_name = "output.tap" if platform == "spectrum" else "output.dsk"
    canonical = output_dir / canonical_name
    canonical_published = canonical.is_file() and canonical.stat().st_size > 0
    quality_artifact = candidate_artifact if candidate_artifact is not None else canonical
    canonical_ok = quality_artifact.is_file() and quality_artifact.stat().st_size > 0
    unexpected_warning_count = sum(
        len(warnings[name]) for name in ("structural", "source", "other")
    )
    spec = {}
    try:
        spec = json.loads((output_dir / "generation_spec.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
    binary_size = program_binary.stat().st_size if program_binary else None
    binary_budget = spec.get("budgets", {}).get("program_binary_bytes")
    resource_errors = []
    if binary_budget is not None and binary_size is not None and binary_size > int(binary_budget):
        resource_errors.append(
            f"program binary {binary_size} exceeds budget {int(binary_budget)} bytes"
        )
    semantic = {}
    try:
        semantic = json.loads((output_dir / "semantic_report.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
    semantic_pass = semantic.get("quality_pass", True)
    resources = {
        "program_binary_bytes": binary_size,
        "program_binary_budget_bytes": binary_budget,
        "errors": resource_errors,
        "quality_pass": not resource_errors,
    }
    return {
        "schema_version": 1,
        "platform": platform,
        "command": list(command),
        "return_code": return_code,
        "compile_succeeded": return_code == 0,
        "canonical_artifact": {
            "path": canonical_name,
            "exists": canonical_ok,
            "size_bytes": quality_artifact.stat().st_size if canonical_ok else 0,
            "published": canonical_published,
            "staged_from": (
                str(quality_artifact.relative_to(output_dir))
                if canonical_ok and quality_artifact.resolve() != canonical.resolve()
                else None
            ),
        },
        "artifacts": artifact_records,
        "program_binary": (
            {
                "path": str(program_binary.relative_to(output_dir)),
                "size_bytes": program_binary.stat().st_size,
            }
            if program_binary
            else None
        ),
        "warnings": warnings,
        "unexpected_warning_count": unexpected_warning_count,
        "resources": resources,
        "semantic_quality_pass": semantic_pass,
        "quality_pass": (
            return_code == 0
            and canonical_ok
            and unexpected_warning_count == 0
            and not resource_errors
            and semantic_pass
        ),
    }


def quality_rejection_diagnostics(report: dict[str, Any]) -> list[str]:
    """Return actionable diagnostics for a successful compile rejected by policy."""
    diagnostics = [
        "BUILD QUALITY REJECTION: compilation succeeded, but the result is not acceptable."
    ]
    for group in ("source", "other"):
        diagnostics.extend(report.get("warnings", {}).get(group, []))
    diagnostics.extend(report.get("resources", {}).get("errors", []))
    if not report.get("semantic_quality_pass", True):
        diagnostics.append(
            "Semantic validation failed; inspect semantic_report.json and repair every error."
        )
    canonical = report.get("canonical_artifact", {})
    if not canonical.get("exists", False):
        diagnostics.append(f"Required artifact {canonical.get('path', 'output')} was not produced.")
    if len(diagnostics) == 1:
        diagnostics.append(
            "The build failed an unspecified quality condition; inspect build_report.json."
        )
    return diagnostics


def write_build_report(report: dict[str, Any], path: Path) -> None:
    """Write a stable, human-readable JSON report."""
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
