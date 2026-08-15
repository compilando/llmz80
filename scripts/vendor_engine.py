#!/usr/bin/env python3
"""Vendor a third-party engine at a pinned commit.

The checkout itself is not committed -- these repositories are large and
already have a home. What *is* committed is `vendor/<id>/ENGINE.json`, which
records the repository, the commit and the licence somebody read. That is
everything a rebuild needs, and it is auditable in a way a copied tree is not.

Usage:
    python scripts/vendor_engine.py cpctelera \\
        https://github.com/lronaldo/cpctelera <40-char-commit> GPL-3.0-or-later
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from llmz80.studio.engines import ALLOWED_LICENCES, is_pinned_commit

VENDOR_ROOT = Path(__file__).resolve().parents[1] / "vendor"


def write_manifest(
    directory: Path, *, engine_id: str, repository: str, commit: str, licence: str
) -> Path:
    """Record what a rebuild needs, refusing a licence nobody has read.

    The refusal happens here rather than after the clone so a licence problem
    costs a second instead of a gigabyte.
    """
    if licence not in ALLOWED_LICENCES:
        raise ValueError(
            f"licence {licence!r} is not one this project has accepted. Read the "
            "engine's own licence file and record its SPDX identifier; if it is "
            "genuinely acceptable, add it to engines.ALLOWED_LICENCES in its own "
            "commit, with the reason"
        )
    # The same predicate `EnginePack.pin_errors` uses, imported rather than
    # restated: a manifest this script accepts and a pack that then rejects it
    # would be a disagreement about the one fact both exist to record.
    if not is_pinned_commit(commit):
        raise ValueError(f"{commit!r} is not a full commit hash")
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "ENGINE.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "id": engine_id,
                "repository": repository,
                "commit": commit,
                "licence": licence,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def vendor(engine_id: str, repository: str, commit: str, licence: str) -> Path:
    directory = VENDOR_ROOT / engine_id
    write_manifest(
        directory, engine_id=engine_id, repository=repository, commit=commit, licence=licence
    )
    checkout = directory / "src"
    if not checkout.is_dir():
        subprocess.run(["git", "init", "-q", str(checkout)], check=True)
        subprocess.run(
            ["git", "-C", str(checkout), "remote", "add", "origin", repository], check=True
        )
    # A pinned shallow fetch rather than a clone: the commit is the version,
    # and its history is not something this project ever reads.
    subprocess.run(
        ["git", "-C", str(checkout), "fetch", "--depth", "1", "origin", commit], check=True
    )
    subprocess.run(["git", "-C", str(checkout), "checkout", "-q", "FETCH_HEAD"], check=True)
    return checkout


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(__doc__)
        raise SystemExit(2)
    print(vendor(*sys.argv[1:5]))
