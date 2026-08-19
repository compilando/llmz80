"""Restoring what was behind a sprite, instead of repainting the terrain.

Found by watching a generated game. A CPC Breakout drew its ball correctly and
flickered, and the cause was in the shape of the loop the contract left it:

    plat_wait_frame();
    keys = plat_input();
    ...
    erase_ball();          <- repaints up to nine tiles
    ...collisions, bricks, bounces...
    draw_ball();           <- the ball reappears, much later

Two costs, and they compound. The ball is absent from the screen for most of
the frame's compute, so the beam catches the gap; and erasing a 16x16 ball by
repainting nine 8x8 tiles is about twice the byte writes of simply putting
back what was there.

Putting back what was there is the era's own answer and the one thing the
program cannot do for itself: it would have to know what is behind the sprite,
which is terrain here and could be text, another sprite or a scrolled backdrop
in the next design. The library knows -- it is on the screen -- so the library
keeps it.

The buffer belongs to the caller, not to the library. Two moving actors need
two backing stores, and which order they are restored in is a fact about the
program's own draw order; a library holding one hidden buffer would silently
be wrong for the second sprite.
"""

from __future__ import annotations

import pytest

from llmz80.studio.codegen import render_config_header, sprite_under_bytes
from llmz80.studio.models import TargetPlatform, VideoMode
from llmz80.studio.samples import blank_project
from llmz80.studio.spriting import SPRITE_SIZE


def _project(platform, mode=None, *, smooth=False):
    project = blank_project("Under", platform)
    if mode is not None:
        project.target.video_mode = mode
    project.presentation.smooth_horizontal = smooth
    return project


class TestHowBigTheBackingStoreIs:
    """One 16x16 sprite's footprint, in the bytes that machine really writes."""

    @pytest.mark.parametrize(
        "mode,width",
        [(VideoMode.CPC_MODE_0, SPRITE_SIZE // 2), (VideoMode.CPC_MODE_1, SPRITE_SIZE // 4)],
    )
    def test_the_cpc_saves_pixels_and_nothing_else(self, mode, width):
        """Colour lives in the pixel bytes on this machine, so there is no
        attribute area to remember."""
        project = _project(TargetPlatform.AMSTRAD_CPC, mode)

        assert sprite_under_bytes(project) == width * SPRITE_SIZE

    def test_the_spectrum_saves_its_attributes_too(self):
        """`plat_sprite_px` writes an attribute per covered cell, so a restore
        that put back only the bitmap would leave the sprite's colour behind on
        the background -- a rectangle of the wrong ink following the actor."""
        project = _project(TargetPlatform.SPECTRUM)
        width = SPRITE_SIZE // 8

        assert sprite_under_bytes(project) == width * SPRITE_SIZE + width * 3

    def test_a_shifted_sprite_needs_the_extra_byte(self):
        """Pre-shifted art is one byte wider, so it covers one more column --
        of pixels on both machines, and of attributes on the Spectrum."""
        plain = sprite_under_bytes(_project(TargetPlatform.SPECTRUM))
        shifted = sprite_under_bytes(_project(TargetPlatform.SPECTRUM, smooth=True))

        assert shifted > plain
        assert shifted == 3 * SPRITE_SIZE + 3 * 3

    @pytest.mark.parametrize("platform", list(TargetPlatform))
    def test_the_header_publishes_it(self, platform):
        """A program declares `unsigned char under[SPRITE_UNDER_BYTES]`, so the
        number has to be a macro rather than something it works out."""
        header = render_config_header(_project(platform))

        assert f"#define SPRITE_UNDER_BYTES {sprite_under_bytes(_project(platform))}" in header

    def test_it_is_never_zero(self):
        """A zero-length array is not C, and a design with no sprites still
        compiles the same platform library."""
        for platform in TargetPlatform:
            assert sprite_under_bytes(_project(platform)) > 0


class TestThreeRowsBecauseASpriteStraddles:
    def test_the_attribute_allowance_is_three_rows_not_two(self):
        """A sprite at a py that is not a multiple of 8 covers three character
        rows, and `plat_sprite_px` colours all three. Saving two would restore
        two and leave the third wearing the sprite's ink for ever."""
        project = _project(TargetPlatform.SPECTRUM)
        width = SPRITE_SIZE // 8

        attributes = sprite_under_bytes(project) - width * SPRITE_SIZE

        assert attributes == width * 3


class TestTheContractTellsTheWriterWhenToDraw:
    """Half A. The mechanism above shrinks the gap; this moves it to where the
    beam is not looking."""

    def _prompt(self, platform):
        from llmz80.studio.acceptance import generation_prompt
        from llmz80.studio.models import AssetSpec

        project = _project(platform)
        project.assets = [
            AssetSpec(id="hero", kind="sprite", source="assets/hero.png", width=16, height=16)
        ]
        return generation_prompt(project)

    @pytest.mark.parametrize("platform", list(TargetPlatform))
    def test_the_writer_is_told_to_draw_first_and_think_afterwards(self, platform):
        prompt = self._prompt(platform)

        assert "plat_wait_frame" in prompt
        assert "before" in prompt or "first" in prompt

    @pytest.mark.parametrize("platform", list(TargetPlatform))
    def test_the_writer_is_offered_the_backing_store(self, platform):
        prompt = self._prompt(platform)

        assert "plat_save_under" in prompt
        assert "plat_restore_under" in prompt
        assert "SPRITE_UNDER_BYTES" in prompt

    @pytest.mark.parametrize("platform", list(TargetPlatform))
    def test_the_writer_is_warned_about_overlap(self, platform):
        """Save-under saves whatever is on screen, so a sprite drawn over
        another saves the other one as background. Restoring out of order
        leaves a copy behind -- the one failure this mechanism has, and the
        one a writer will meet the first time two actors touch."""
        prompt = self._prompt(platform)

        assert "reverse" in prompt
