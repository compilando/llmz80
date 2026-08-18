#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from llmz80.quality.emulator_smoke import smoke_test, write_smoke_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run bounded emulator or portable smoke checks")
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--platform", choices=("spectrum", "amstrad_cpc"))
    parser.add_argument(
        "--full",
        action="store_true",
        help="require real emulator boot, framebuffer capture and scripted input",
    )
    parser.add_argument("--seconds", type=int, default=3, help="minimum observation time")
    args = parser.parse_args()
    platform = args.platform or (args.run_dir / "platform.txt").read_text(encoding="utf-8").strip()
    report = smoke_test(args.run_dir, platform, full=args.full, seconds=args.seconds)
    path = args.run_dir / "emulator_report.json"
    write_smoke_report(report, path)
    print(
        f"Smoke report: {path} ({report['mode']}, "
        f"runtime_verified={report['runtime_verified']}, pass={report['quality_pass']})"
    )
    if report.get("emulator_error"):
        print(f"Emulator error: {report['emulator_error']}", file=sys.stderr)
    return 0 if report["quality_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
