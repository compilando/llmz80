"""Deterministic, API-free scorecards for benchmark generation runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


SUPPORTED_PLATFORMS = {"spectrum", "amstrad_cpc"}


def load_corpus(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("benchmark corpus must use schema_version 1")
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("benchmark corpus must contain cases")
    seen: set[str] = set()
    for case in cases:
        required = {"id", "platform", "language", "prompt", "archetype", "required_capabilities"}
        if not isinstance(case, dict) or not required.issubset(case):
            raise ValueError(f"invalid benchmark case: {case!r}")
        if case["id"] in seen:
            raise ValueError(f"duplicate benchmark id: {case['id']}")
        if case["platform"] not in SUPPORTED_PLATFORMS:
            raise ValueError(f"unsupported platform in {case['id']}")
        if case["language"] not in {"es", "en"}:
            raise ValueError(f"unsupported language in {case['id']}")
        seen.add(case["id"])
    return data


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _matching_runs(runs_dir: Path, prompt: str, platform: str) -> list[Path]:
    matches = []
    for prompt_file in runs_dir.glob("*/prompt.txt"):
        try:
            run_platform = (prompt_file.parent / "platform.txt").read_text(encoding="utf-8").strip()
            run_prompt = prompt_file.read_text(encoding="utf-8").strip()
        except OSError:
            continue
        if run_platform == platform and run_prompt.casefold() == prompt.strip().casefold():
            matches.append(prompt_file.parent)
    return sorted(matches)


def _retrieval_metrics(run_dir: Path, required: set[str]) -> tuple[float | None, list[str]]:
    try:
        context = json.loads((run_dir / "retrieval_context.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        context = {}
    if isinstance(context, dict):
        examples = context.get("examples", [])
    elif isinstance(context, list):
        examples = context
    else:
        examples = []
    if not isinstance(examples, list):
        return None, []
    retrieved: set[str] = set()
    sources = []
    for item in examples:
        if not isinstance(item, dict):
            continue
        sources.append(str(item.get("path") or item.get("source") or "unknown"))
        caps = item.get("capabilities", [])
        if isinstance(caps, list):
            retrieved.update(str(cap) for cap in caps)
    if not required:
        return 1.0, sources
    return len(required & retrieved) / len(required), sources


def evaluate_run(case: dict[str, Any], run_dir: Path | None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": case["id"],
        "platform": case["platform"],
        "language": case["language"],
        "archetype": case["archetype"],
        "required_capabilities": sorted(case["required_capabilities"]),
        "run_dir": str(run_dir) if run_dir else None,
        "status": "missing",
        "first_build_success": False,
        "final_build_success": False,
        "repair_count": 0,
        "unexpected_warning_count": 0,
        "canonical_artifact_size": 0,
        "program_binary_size": None,
        "retrieval_recall": None,
        "semantic_errors": None,
        "semantic_warnings": None,
        "emulator": {"boot": None, "visual_change": None, "input_transition": None},
        "api": {"calls": None, "latency_ms": None, "input_tokens": None, "output_tokens": None},
    }
    if run_dir is None:
        return result

    reports = sorted(run_dir.glob("build_report_attempt_*.json"))
    final_report = _read_json(run_dir / "build_report.json")
    if not reports and final_report:
        reports = [run_dir / "build_report.json"]
    parsed_reports = [_read_json(path) for path in reports]
    result["status"] = "evaluated"
    result["first_build_success"] = bool(parsed_reports and parsed_reports[0].get("quality_pass"))
    result["final_build_success"] = bool(final_report.get("quality_pass"))
    result["repair_count"] = max(0, len(parsed_reports) - 1)
    result["unexpected_warning_count"] = int(final_report.get("unexpected_warning_count", 0))
    artifact = final_report.get("canonical_artifact") or {}
    binary = final_report.get("program_binary") or {}
    result["canonical_artifact_size"] = int(artifact.get("size_bytes", 0))
    result["program_binary_size"] = binary.get("size_bytes")

    required = set(case["required_capabilities"])
    recall, sources = _retrieval_metrics(run_dir, required)
    result["retrieval_recall"] = recall
    result["retrieval_sources"] = sources

    semantic = _read_json(run_dir / "semantic_report.json")
    if semantic:
        result["semantic_errors"] = len(semantic.get("errors", []))
        result["semantic_warnings"] = len(semantic.get("warnings", []))
    emulator = _read_json(run_dir / "emulator_report.json")
    if emulator:
        result["emulator"] = {
            key: emulator.get(key) for key in ("boot", "visual_change", "input_transition")
        }
    api = _read_json(run_dir / "generation_metrics.json")
    if api:
        result["api"] = {
            key: api.get(key)
            for key in ("calls", "latency_ms", "input_tokens", "output_tokens")
        }
    return result


def _aggregate(results: list[dict[str, Any]]) -> dict[str, Any]:
    evaluated = [item for item in results if item["status"] == "evaluated"]
    count = len(evaluated)
    ratio = lambda key: (sum(bool(item[key]) for item in evaluated) / count if count else None)
    recalls = [item["retrieval_recall"] for item in evaluated if item["retrieval_recall"] is not None]
    return {
        "total_cases": len(results),
        "evaluated_cases": count,
        "coverage": count / len(results) if results else 0.0,
        "first_build_rate": ratio("first_build_success"),
        "final_build_rate": ratio("final_build_success"),
        "total_repairs": sum(item["repair_count"] for item in evaluated),
        "unexpected_warnings": sum(item["unexpected_warning_count"] for item in evaluated),
        "mean_retrieval_recall": sum(recalls) / len(recalls) if recalls else None,
    }


def evaluate_corpus(corpus: dict[str, Any], runs_dir: Path) -> dict[str, Any]:
    results = []
    for case in sorted(corpus["cases"], key=lambda value: value["id"]):
        matches = _matching_runs(runs_dir, case["prompt"], case["platform"])
        results.append(evaluate_run(case, matches[-1] if matches else None))
    return {
        "schema_version": 1,
        "corpus": corpus.get("name", "unnamed"),
        "summary": _aggregate(results),
        "cases": results,
    }


def _percent(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.1f}%"


def scorecard_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        f"# LLMZ80 scorecard — {report['corpus']}",
        "",
        f"- Coverage: {_percent(summary['coverage'])} "
        f"({summary['evaluated_cases']}/{summary['total_cases']})",
        f"- First-build rate: {_percent(summary['first_build_rate'])}",
        f"- Final-build rate: {_percent(summary['final_build_rate'])}",
        f"- Repairs: {summary['total_repairs']}",
        f"- Unexpected warnings: {summary['unexpected_warnings']}",
        f"- Mean retrieval recall: {_percent(summary['mean_retrieval_recall'])}",
        "",
        "| Case | Platform | Result | First build | Final build | Warnings |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ]
    for case in report["cases"]:
        lines.append(
            f"| {case['id']} | {case['platform']} | {case['status']} | "
            f"{'yes' if case['first_build_success'] else 'no'} | "
            f"{'yes' if case['final_build_success'] else 'no'} | "
            f"{case['unexpected_warning_count']} |"
        )
    return "\n".join(lines) + "\n"


def write_scorecard(report: dict[str, Any], output_prefix: Path) -> tuple[Path, Path]:
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    json_path = output_prefix.with_suffix(".json")
    markdown_path = output_prefix.with_suffix(".md")
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(scorecard_markdown(report), encoding="utf-8")
    return json_path, markdown_path
