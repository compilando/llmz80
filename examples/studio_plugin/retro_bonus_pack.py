"""Small third-party target-plugin example for the Studio extension SDK.

Registered under `llmz80.target_plugins`, the group `registry.target_registry`
really loads. The genre-pack group this example used to demonstrate is gone:
Studio no longer decides what kinds of game exist.
"""

from llmz80.studio.models import TargetPlatform, VideoMode
from llmz80.studio.registry import TargetPack


PACK = TargetPack(
    id=TargetPlatform.SPECTRUM,
    name="ZX Spectrum 128K",
    video_modes=(VideoMode.SPECTRUM_BITMAP,),
    binary_budget=49152,
    data_budget=16384,
    emulator_adapters=("zesarux", "fuse"),
    audio_effects=True,
)
