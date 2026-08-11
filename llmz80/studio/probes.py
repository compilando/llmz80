"""Locate engine state in the built binary so an emulator can read it.

The runtime gate used to infer that a game worked from pixels changing. These
probes turn that into a measurement: the linker already knows where the engine
keeps its score, lives and level, and both toolchains write that down.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from llmz80.core.state_contract import PROBE_WIDTHS, REQUIRED_SYMBOLS

#: Widths come from the shared state contract, which no engine owns.
PROBE_SYMBOLS = PROBE_WIDTHS

#: z88dk writes "NAME = $ADDR ; attributes"; only public symbols are useful.
_Z88DK_LINE = re.compile(r"^(?P<name>\S+)\s*=\s*\$(?P<addr>[0-9A-Fa-f]+)\s*;(?P<rest>.*)$")

#: SDCC's .noi file writes "DEF _name 0xADDR" for every global.
_SDCC_LINE = re.compile(r"^DEF\s+_(?P<name>\S+)\s+0x(?P<addr>[0-9A-Fa-f]+)\s*$")


def parse_z88dk_map(text: str) -> dict[str, int]:
    found: dict[str, int] = {}
    for line in text.splitlines():
        match = _Z88DK_LINE.match(line.strip())
        if not match:
            continue
        name = match.group("name")
        # z88dk decorates C symbols with a leading underscore.
        clean = name[1:] if name.startswith("_") else name
        if clean in PROBE_SYMBOLS and "public" in match.group("rest"):
            found[clean] = int(match.group("addr"), 16)
    return found


def parse_sdcc_noi(text: str) -> dict[str, int]:
    found: dict[str, int] = {}
    for line in text.splitlines():
        match = _SDCC_LINE.match(line.strip())
        if match and match.group("name") in PROBE_SYMBOLS:
            found[match.group("name")] = int(match.group("addr"), 16)
    return found


def extract_probes(output_dir: Path, platform: str) -> dict[str, int]:
    """Read whichever symbol file the platform's toolchain produced."""
    if platform == "spectrum":
        candidates = sorted(output_dir.glob("*.map"))
        parse = parse_z88dk_map
    else:
        candidates = sorted((output_dir / "obj").glob("*.noi"))
        parse = parse_sdcc_noi
    for path in candidates:
        found = parse(path.read_text(encoding="utf-8", errors="ignore"))
        if found:
            return found
    return {}


def write_probe_report(output_dir: Path, platform: str) -> dict:
    """Write probes.json and report which contract symbols are absent.

    Only the required symbols decide whether the contract was honoured. A design
    with no notion of remaining objectives is not failed for lacking one.
    """
    addresses = extract_probes(output_dir, platform)
    missing = sorted(set(PROBE_SYMBOLS) - set(addresses))
    missing_required = sorted(set(REQUIRED_SYMBOLS) - set(addresses))
    report = {
        "schema_version": 2,
        "platform": platform,
        "addresses": {name: addresses[name] for name in sorted(addresses)},
        "widths": {name: PROBE_SYMBOLS[name] for name in sorted(addresses)},
        "missing": missing,
        "missing_required": missing_required,
        "contract_honoured": not missing_required,
        "complete": not missing,
    }
    (output_dir / "probes.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report
