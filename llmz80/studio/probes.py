"""Locate engine state in the built binary so an emulator can read it.

The runtime gate used to infer that a game worked from pixels changing. These
probes turn that into a measurement: the linker already knows where the engine
keeps its score, lives and level, and both toolchains write that down.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Mapping

from llmz80.core.state_contract import PROBE_WIDTHS, REQUIRED_SYMBOLS

#: Widths come from the shared state contract, which no engine owns.
PROBE_SYMBOLS = PROBE_WIDTHS


def _wanted(observables: Mapping[str, int] | None) -> dict[str, int]:
    """Every symbol worth locating: the contract's, plus this design's own.

    A design's observables are passed in as a plain symbol -> width mapping
    rather than as the `GameProject` they come from, and this module goes on
    importing nothing from the IR. Two reasons, one of them the reason the
    whole chain was dead: a linker map knows nothing about designs, so the
    only thing this parser needs is the name and how many bytes to read, and
    a mapping keeps every parser here callable from a test that has a map
    file and no project. The other is that `ObservableSpec` already validates
    the shape at the edge -- the `g_` prefix, the width being 1 or 2 -- so
    re-stating it here would be a second opinion about a settled question.

    Contract symbols win a collision. `structure._reference_errors` already
    refuses a design whose observable shadows a contract symbol, so a
    collision cannot come from a validated project at all; the ordering is
    here so that a caller passing a raw mapping cannot quietly change what
    `g_score` means either.
    """
    return {**(observables or {}), **PROBE_SYMBOLS}


#: z88dk writes "NAME = $ADDR ; attributes"; only public symbols are useful.
_Z88DK_LINE = re.compile(r"^(?P<name>\S+)\s*=\s*\$(?P<addr>[0-9A-Fa-f]+)\s*;(?P<rest>.*)$")

#: SDCC's .noi file writes "DEF _name 0xADDR" for every global.
_SDCC_LINE = re.compile(r"^DEF\s+_(?P<name>\S+)\s+0x(?P<addr>[0-9A-Fa-f]+)\s*$")


def parse_z88dk_map(text: str, observables: Mapping[str, int] | None = None) -> dict[str, int]:
    found: dict[str, int] = {}
    wanted = _wanted(observables)
    for line in text.splitlines():
        match = _Z88DK_LINE.match(line.strip())
        if not match:
            continue
        name = match.group("name")
        # z88dk decorates C symbols with a leading underscore.
        clean = name[1:] if name.startswith("_") else name
        if clean in wanted and "public" in match.group("rest"):
            found[clean] = int(match.group("addr"), 16)
    return found


def parse_sdcc_noi(text: str, observables: Mapping[str, int] | None = None) -> dict[str, int]:
    found: dict[str, int] = {}
    wanted = _wanted(observables)
    for line in text.splitlines():
        match = _SDCC_LINE.match(line.strip())
        if match and match.group("name") in wanted:
            found[match.group("name")] = int(match.group("addr"), 16)
    return found


def extract_probes(
    output_dir: Path, platform: str, observables: Mapping[str, int] | None = None
) -> dict[str, int]:
    """Read whichever symbol file the platform's toolchain produced."""
    if platform == "spectrum":
        candidates = sorted(output_dir.glob("*.map"))
        parse = parse_z88dk_map
    else:
        candidates = sorted((output_dir / "obj").glob("*.noi"))
        parse = parse_sdcc_noi
    for path in candidates:
        found = parse(path.read_text(encoding="utf-8", errors="ignore"), observables)
        if found:
            return found
    return {}


def write_probe_report(
    output_dir: Path, platform: str, observables: Mapping[str, int] | None = None
) -> dict:
    """Write probes.json and report which declared symbols are absent.

    Only the required symbols decide whether the *contract* was honoured. A
    design with no notion of remaining objectives is not failed for lacking one.

    A design's own observables are looked for beside the contract's symbols,
    and they were the link that broke the whole chain: `ObservableSpec` has
    existed since schema v4 and `codegen.render_state_header` has always
    declared them for the writer, but this report only ever searched the
    contract, so a symbol a design declared was never located in the linker
    map, never read out of memory, and never reached a gate however faithfully
    the program defined it. Across the four finished games in
    `studio-projects/` the runtime examiner checked none of their own
    mechanics -- everything it could assert came from `g_score` and `g_state`.
    """
    addresses = extract_probes(output_dir, platform, observables)
    wanted = _wanted(observables)
    missing = sorted(set(PROBE_SYMBOLS) - set(addresses))
    missing_required = sorted(set(REQUIRED_SYMBOLS) - set(addresses))
    declared = sorted(observables or {})
    report = {
        "schema_version": 3,
        "platform": platform,
        "addresses": {name: addresses[name] for name in sorted(addresses)},
        "widths": {name: wanted[name] for name in sorted(addresses)},
        "missing": missing,
        "missing_required": missing_required,
        # What the design declared, so a reader of probes.json alone can tell
        # "this design declared nothing" from "this program defined nothing".
        "observables": declared,
        "missing_observables": [name for name in declared if name not in addresses],
        "contract_honoured": not missing_required,
        "complete": not missing,
    }
    (output_dir / "probes.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report


def contract_failures(report: dict) -> list[str]:
    """Diagnostics for symbols the linker map does not carry that it must.

    Separated from `write_probe_report` so the build can refuse on them
    without the compiler having to be running to test the refusal. What used
    to happen instead: the report recorded the absence, `repair_prompt` told
    the writer about it, and the loop accepted the attempt anyway, because
    `attempt.build_passed` only ever read `build.quality_pass`.
    """
    failures = []
    missing = report.get("missing_required") or []
    if missing:
        failures.append(
            "these required contract symbols are absent from the linker map, which "
            "means they were declared static, declared inside a function, or "
            "optimised away because nothing reads them: " + ", ".join(missing)
        )
    # A declared observable the program never defined is judged exactly like a
    # missing required symbol, and for the same reason rather than by analogy:
    # the design promised a window onto one of its own rules and the program
    # did not open it, so every gate downstream goes on saying nothing about
    # that rule while the build reports success. The softer alternative --
    # reporting the absence and building anyway -- is the one this module
    # already learned not to take: `missing_required` was recorded, fed to
    # `repair_prompt`, and the attempt accepted regardless, because
    # `attempt.build_passed` only ever read `build.quality_pass`.
    absent = report.get("missing_observables") or []
    if absent:
        failures.append(
            "this design declares these observables in game.yml and game_state.h "
            "declares them extern, but they are absent from the linker map: define "
            "each one exactly once at file scope, not static and not inside a "
            "function, and keep it updated as the rule it names happens: " + ", ".join(absent)
        )
    return failures
