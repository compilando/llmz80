"""What a sprite that *moves* costs, which the published budget never said.

The figures in the writing prompt came from a loop that draws sprites and does
nothing else. A game that moves one must also put back what it covered, and
that pair -- `plat_save_under` and `plat_restore_under` -- was never measured
alongside the blitter. It turned out to dominate it:

    CPC, n=16, worst frames overrun   draw 1   restore 3   save 4   all three 9

So a prompt saying "about 16 with plat_sprite_px" was telling a game it could
move sixteen sprites when it could move three. A basketball design moved
exactly three, overran its frame, and was refused three attempts running while
the number it was working to said it had five times the room it had.

The pair is faster now, and this is the honest ceiling either way. Measured
after that work, in a loop that restores, saves and draws N sprites:

    Spectrum  n=2 cost 0   n=3 cost 1   n=4 cost 1   n=5 cost 2   n=8 cost 3
    CPC       n=3 cost 0   n=4 cost 0   n=5 cost 1   n=7 cost 1   n=8 cost 2

The gate accepts 1, so the ceilings are 4 and 7, and what is published is two
thirds of them as for every other figure here -- a real game also reads keys,
moves what it drew and tests collisions.
"""

from __future__ import annotations

import pytest

from llmz80.studio.acceptance import generation_prompt
from llmz80.studio.codegen import SPRITES_PER_FRAME, sprites_per_frame
from llmz80.studio.models import AssetSpec, TargetPlatform
from llmz80.studio.samples import blank_project


def _with_a_sprite(platform: TargetPlatform):
    """The budget paragraph only appears for a design that has sprites, which
    is right -- a game with none has nothing to spend."""
    project = blank_project("Budget", platform)
    project.assets = [
        AssetSpec(id="hero", kind="sprite", source="assets/hero.png", width=16, height=16)
    ]
    return project


class TestTheFigureExists:
    @pytest.mark.parametrize(
        "platform,expected",
        [(TargetPlatform.SPECTRUM, 2), (TargetPlatform.AMSTRAD_CPC, 4)],
    )
    def test_each_machine_publishes_what_it_measured(self, platform, expected):
        assert sprites_per_frame(platform, pixel_column=True, moving=True) == expected

    def test_moving_costs_more_than_drawing_on_every_machine(self):
        """The whole point. If these ever came out equal the measurement would
        have been of the wrong thing."""
        for platform in SPRITES_PER_FRAME:
            drawn = sprites_per_frame(platform, pixel_column=True, moving=False)
            moved = sprites_per_frame(platform, pixel_column=True, moving=True)

            assert moved < drawn, platform

    def test_an_unmeasured_target_still_answers_with_the_smaller_machine(self):
        """A target nobody has measured must not be handed the roomier of the
        two numbers on the strength of nothing."""
        assert sprites_per_frame("some_new_machine", pixel_column=True, moving=True) == 2

    def test_drawing_figures_are_untouched(self):
        assert sprites_per_frame(TargetPlatform.AMSTRAD_CPC, pixel_column=False) == 20
        assert sprites_per_frame(TargetPlatform.SPECTRUM, pixel_column=True) == 5


class TestTheWriterIsTold:
    @pytest.mark.parametrize("platform", [TargetPlatform.SPECTRUM, TargetPlatform.AMSTRAD_CPC])
    def test_the_prompt_carries_the_moving_figure(self, platform):
        prompt = generation_prompt(_with_a_sprite(platform))
        moving = sprites_per_frame(platform, pixel_column=True, moving=True)

        assert f"How many you can move: about {moving}." in prompt

    @pytest.mark.parametrize("platform", [TargetPlatform.SPECTRUM, TargetPlatform.AMSTRAD_CPC])
    def test_and_says_what_makes_a_sprite_dearer(self, platform):
        """A number with no rule attached cannot be applied to a design that
        has some sprites moving and some standing still."""
        prompt = generation_prompt(_with_a_sprite(platform))

        assert "plat_save_under" in prompt
        assert "moves" in prompt or "moving" in prompt
