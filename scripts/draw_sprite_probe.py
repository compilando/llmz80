#!/usr/bin/env python3
"""Draw a few sprites for real and leave them somewhere you can look at them.

This is the gate the grid approach has not passed yet. Everything around it
is tested -- the palette a target really has, what a malformed grid is
refused for, what a good one becomes, that the packers accept the frames --
but none of that answers the only question that matters: **does the model
draw a sprite you would recognise at 16x16?**

Nobody has checked. Run this, open the PNGs, and decide. If the answer is
no, the fix is one class: `sprite_artist.ClaudeGridSheetSource` is swapped
for a source backed by a pixel-art API, and the schema, the validation, the
palette resolution and the retry loop all still stand.

    ANTHROPIC_API_KEY=... python scripts/draw_sprite_probe.py

Writes to `local/sprite_probe/`: one magnified PNG per subject per target,
plus every rejected attempt, so a bad run leaves as much evidence as a good
one.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from llmz80.studio.models import EntitySpec, TargetPlatform, VideoMode  # noqa: E402
from llmz80.studio.samples import blank_project  # noqa: E402
from llmz80.studio.sprite_artist import (  # noqa: E402
    ClaudeGridSheetSource,
    SpriteArtist,
    SpriteDrawFailure,
)
from llmz80.studio.sprite_grid import PREVIEW_SCALE  # noqa: E402

OUTPUT = Path("local/sprite_probe")

#: Deliberately a spread rather than three variations on "a person". A
#: standing figure, a creature and a small object are the three shapes the
#: previous, image-model path failed differently on -- see `sprite_artist.py`'s
#: module docstring, where `hero` came out squashed, `pellet` came out
#: inflated and only `enemy` survived -- so they are the three worth looking
#: at first.
SUBJECTS = [
    EntitySpec(id="hero", kind="minero", sprite="hero", notes="lleva un pico al hombro"),
    EntitySpec(id="bat", kind="perseguidor", sprite="bat", notes="un murciélago que vuela"),
    EntitySpec(id="key", kind="objeto", sprite="key", notes="una llave que se recoge"),
]

TARGETS = [
    ("spectrum", TargetPlatform.SPECTRUM, None),
    ("cpc_mode0", TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_0),
    ("cpc_mode1", TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_1),
]


def main() -> int:
    from anthropic import Anthropic

    from llmz80.utils.config import load_anthropic_api_key, load_config

    model = load_config("config.yml").get("anthropic", {}).get("model", "claude-opus-5")
    client = Anthropic(api_key=load_anthropic_api_key())
    artist = SpriteArtist(source=ClaudeGridSheetSource(client, model))

    OUTPUT.mkdir(parents=True, exist_ok=True)
    failures = 0
    for target_name, platform, mode in TARGETS:
        project = blank_project("Probe", platform, mode)
        for entity in SUBJECTS:
            stem = f"{target_name}_{entity.sprite}"
            print(f"-- {stem}", flush=True)
            try:
                drawn = artist.draw_frames(project, entity, on_progress=lambda m: print(f"   {m}"))
            except SpriteDrawFailure as failure:
                failures += 1
                print(f"   RECHAZADO tras {len(failure.sheets)} intentos")
                for index, (sheet, reason) in enumerate(
                    zip(failure.sheets, failure.reasons), start=1
                ):
                    sheet.save(OUTPUT / f"{stem}_fallo{index}.png")
                    print(f"      intento {index}: {reason}")
                continue
            drawn.sheet.save(OUTPUT / f"{stem}.png")
            for index, sheet in enumerate(drawn.sheets[:-1], start=1):
                sheet.save(OUTPUT / f"{stem}_rechazado{index}.png")
            print(f"   ok en {drawn.attempts} intento(s)")

    print(f"\nPNGs en {OUTPUT.resolve()} (ampliados x{PREVIEW_SCALE}).")
    print("Míralos. ¿Se reconoce cada figura? Ésa es la única pregunta.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
