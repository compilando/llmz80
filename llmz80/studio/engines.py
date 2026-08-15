"""Third-party engines and libraries a project can be built with.

Studio does not write engines and is not going to. It vendors them: a checkout
pinned to one commit under `vendor/<id>/`, with its licence recorded, and one
`EnginePack` saying what it is, what it can do, and where its state lives.

`probe_map` is the field that makes everything else survive the change. The
state contract in `llmz80.core.state_contract` can be demanded of a program
*we* had written; it cannot be demanded of somebody else's engine, which names
its score whatever it named it. So each pack declares where its own state
lives and `probes.py` reads that instead. Without it, every gate this project
owns switches off the moment a game is built with an engine, and N engines
would need N sets of gates -- which is the arithmetic that kills a
multi-engine pipeline before it starts.

`engine_class` is not decoration: a `LIBRARY` still has the program written in
C by a model, so the output space stays unrestricted and the writing prompt
must teach its API. A `DSL` engine has the model emit data only and never a
line of code. Two different pipelines, and a gate that does not know which one
it is judging will judge one of them wrongly.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from importlib.metadata import entry_points
from pathlib import Path
from typing import Iterable, Mapping

from llmz80.core.state_contract import REQUIRED_SYMBOLS

from .models import TargetPlatform
from .registry import Registry

#: The entry-point group an installed package registers an `EnginePack` under,
#: mirroring `registry.TARGET_PLUGIN_GROUP` for machines and reusing its
#: `Registry`: one seam, one duplicate-id rule, one "unknown plugin" message.
ENGINE_PLUGIN_GROUP = "llmz80.engine_plugins"

#: Licences a vendored engine may carry. GPL is on the list because this
#: project decided (2026-08-14) that a generated game being a derivative work
#: of a GPL engine is a consequence it accepts. An unknown or bespoke licence
#: is not on it, and not because of its terms: a pipeline that publishes what
#: it builds cannot honour terms nobody has read.
ALLOWED_LICENCES = frozenset(
    {
        "MIT",
        "BSD-2-Clause",
        "BSD-3-Clause",
        "Zlib",
        "Apache-2.0",
        "LGPL-2.1-or-later",
        "LGPL-3.0-or-later",
        "GPL-2.0-only",
        "GPL-2.0-or-later",
        "GPL-3.0-only",
        "GPL-3.0-or-later",
        "CC0-1.0",
        "Unlicense",
    }
)


class EngineClass(str, Enum):
    #: The model writes C against the engine's API. Restricts nothing about
    #: what it can write.
    LIBRARY = "library"
    #: The model emits data the engine reads. Writes no code at all.
    DSL = "dsl"


@dataclass(frozen=True)
class EnginePack:
    id: str
    name: str
    platform: TargetPlatform
    engine_class: EngineClass
    repository: str
    #: A full 40-character git commit. A branch is not a version.
    commit: str
    #: SPDX identifier, read off the engine's own licence file by whoever
    #: vendored it.
    licence: str
    vendor_dir: Path
    #: Contract symbol -> the name or address this engine keeps it under.
    probe_map: Mapping[str, str]
    capabilities: frozenset[str]

    def licence_errors(self) -> list[str]:
        if self.licence in ALLOWED_LICENCES:
            return []
        return [
            f"{self.id} declares licence {self.licence!r}, which is not one this "
            "project has accepted. Read the engine's licence file, record its SPDX "
            "identifier, and add it to ALLOWED_LICENCES only if the games this "
            "pipeline publishes can honour it"
        ]

    def probe_errors(self) -> list[str]:
        missing = sorted(set(REQUIRED_SYMBOLS) - set(self.probe_map))
        if not missing:
            return []
        return [
            f"{self.id} does not say where these required contract symbols live, "
            "so every behaviour gate would abstain on any game built with it: " + ", ".join(missing)
        ]

    def pin_errors(self) -> list[str]:
        if len(self.commit) == 40 and all(c in "0123456789abcdef" for c in self.commit.lower()):
            return []
        return [
            f"{self.id} is pinned to {self.commit!r}, which is not a full commit "
            "hash: a game built against a moving reference cannot be rebuilt"
        ]

    def errors(self) -> list[str]:
        return [*self.licence_errors(), *self.probe_errors(), *self.pin_errors()]


def engine_registry(
    load_external: bool = True, packs: Iterable[EnginePack] = ()
) -> Registry[EnginePack]:
    """Every engine available, built-ins first.

    There are no built-ins yet on purpose: the first pack lands with the
    CPCtelera integration, and an empty registry is the honest statement that
    no engine is usable until one has been vendored and checked.
    """
    registry: Registry[EnginePack] = Registry(packs)
    if load_external:
        for point in entry_points(group=ENGINE_PLUGIN_GROUP):
            registry.register(point.load())
    return registry
