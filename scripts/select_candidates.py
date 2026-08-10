#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from llmz80.quality.candidates import select_candidate, write_selection


def main() -> int:
    parser = argparse.ArgumentParser(description="Select the best fully evaluated candidate")
    parser.add_argument("run_dirs", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = select_candidate(args.run_dirs)
    output = args.output or Path(report["selected"]["run_dir"]) / "candidate_selection.json"
    write_selection(report, output)
    print(f"Selected: {report['selected']['run_dir']} (score={report['selected']['score']})")
    return 0 if report["selected"]["quality_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
