#!/usr/bin/env python3
"""Score saved runs against the bilingual prompt corpus. Calls nothing.

`--live` used to be here: it walked the corpus and shelled out to
`llm_z80.py` to generate each case first. That generator is gone, and the run
layout this reads -- `local/<timestamp>_<slug>/` with a `prompt.txt`, a
`platform.txt` and a `retrieval_context.json` beside the build report -- is
the layout *it* wrote. Studio writes `studio-projects/<slug>/build/` instead,
with no prompt file and no retrieval context, so this scores the archive of
legacy runs and nothing newer.

That makes it a historical instrument rather than a current one. It is kept
because the corpus and the scorecard are still the only cross-run quality
measure this project has, and pointing it at Studio's layout is a smaller job
than inventing one again; but nothing it reports describes a game Studio made.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from llmz80.quality.benchmark import evaluate_corpus, load_corpus, write_scorecard  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=PROJECT_ROOT / "benchmarks/prompts.yml")
    parser.add_argument("--runs-dir", type=Path, default=PROJECT_ROOT / "local")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "local/quality/scorecard")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    corpus = load_corpus(args.corpus)
    report = evaluate_corpus(corpus, args.runs_dir)
    json_path, markdown_path = write_scorecard(report, args.output)
    print(f"JSON scorecard: {json_path}")
    print(f"Markdown scorecard: {markdown_path}")
    print(
        f"Coverage: {report['summary']['evaluated_cases']}/" f"{report['summary']['total_cases']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
