#!/usr/bin/env python3
"""Evaluate saved runs, or explicitly generate a bounded live benchmark."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from llmz80.quality.benchmark import evaluate_corpus, load_corpus, write_scorecard


def _has_passing_runtime_run(runs_dir: Path, prompt: str, platform: str) -> bool:
    for prompt_file in runs_dir.glob("*/prompt.txt"):
        run_dir = prompt_file.parent
        try:
            if prompt_file.read_text(encoding="utf-8").strip().casefold() != prompt.strip().casefold():
                continue
            if (run_dir / "platform.txt").read_text(encoding="utf-8").strip() != platform:
                continue
            build = json.loads((run_dir / "build_report.json").read_text(encoding="utf-8"))
            emulator = json.loads((run_dir / "emulator_report.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if build.get("quality_pass") and emulator.get("quality_pass"):
            return True
    return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=PROJECT_ROOT / "benchmarks/prompts.yml")
    parser.add_argument("--runs-dir", type=Path, default=PROJECT_ROOT / "local")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "local/quality/scorecard")
    parser.add_argument("--live", action="store_true", help="generate benchmark cases through the API first")
    parser.add_argument("--allow-api", action="store_true", help="required confirmation for --live")
    parser.add_argument("--limit", type=int, help="maximum live cases; required with --live")
    parser.add_argument(
        "--runtime-check", action="store_true",
        help="require real emulator evidence for every live generated case",
    )
    parser.add_argument(
        "--resume-passed", action="store_true",
        help="skip live cases that already have passing build and emulator reports",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    corpus = load_corpus(args.corpus)
    if args.live:
        if not args.allow_api or args.limit is None or args.limit < 1:
            raise SystemExit("--live requires both --allow-api and a positive --limit")
        for case in corpus["cases"][: args.limit]:
            if args.resume_passed and _has_passing_runtime_run(
                args.runs_dir, case["prompt"], case["platform"]
            ):
                print(f"live case already passed: {case['id']}")
                continue
            command = [
                sys.executable,
                str(PROJECT_ROOT / "llm_z80.py"),
                "--platform",
                case["platform"],
                "--prompt",
                case["prompt"],
            ]
            if args.runtime_check:
                command.append("--runtime-check")
            completed = subprocess.run(command, cwd=PROJECT_ROOT, check=False)
            if completed.returncode:
                print(f"live case failed: {case['id']}", file=sys.stderr)
    report = evaluate_corpus(corpus, args.runs_dir)
    json_path, markdown_path = write_scorecard(report, args.output)
    print(f"JSON scorecard: {json_path}")
    print(f"Markdown scorecard: {markdown_path}")
    print(
        f"Coverage: {report['summary']['evaluated_cases']}/"
        f"{report['summary']['total_cases']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
