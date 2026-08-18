"""The pens a CPC really shows, and the one table that decides them.

Two defects this exists to hold shut.

**The Python table and the C disagreed.** `compiler.CPC_DEFAULT_PALETTE` named
its four entries HW_BLACK, HW_BLUE, HW_BRIGHT_YELLOW and HW_WHITE in comments
and then gave two of them the wrong RGB: `(0, 0, 255)` for HW_BLUE, which is
`(0, 0, 128)` on this hardware -- `(0, 0, 255)` is HW_BRIGHT_BLUE -- and
`(255, 255, 255)` for HW_WHITE, which is `(128, 128, 128)`; the CPC's white is
HW_BRIGHT_WHITE. So every CPC sprite was quantised against two colours the
machine was never going to show, and the docstring saying "what the packer
quantises sprites against is then what the machine really shows" was false in
half its cases. Nothing could notice, because the two halves were written down
in two files in two languages.

**Mode 0's sixteen pens were unreachable.** `apply_palette` programmed four
whatever the mode, `plat_ink` refused any index above three, and
`sprite_grid.palette_for` offered a four-character alphabet -- so the one
reason to choose mode 0 over mode 1 was switched off in software.
"""

from __future__ import annotations

import pytest

from llmz80.studio.models import PaletteEntry, TargetPlatform, VideoMode
from llmz80.studio.palette import HARDWARE_COLOURS, cpc_palette, cpc_pen, declared_attribute
from llmz80.studio.samples import blank_project


class TestTheHardwareTable:
    def test_every_channel_is_one_of_the_three_levels_the_cpc_has(self):
        """The CPC's 27 colours are 3x3x3: each channel off, half or full.

        A value outside that set would be a colour invented here rather than
        read off the machine, and the packers quantise against these numbers.
        """
        for colour in HARDWARE_COLOURS:
            for channel in colour.rgb:
                assert channel in (0, 128, 255), colour

    def test_a_hardware_value_fits_the_gate_array_register(self):
        for colour in HARDWARE_COLOURS:
            assert 0x00 <= colour.hardware <= 0x1F, colour

    def test_no_two_entries_claim_the_same_hardware_value(self):
        values = [colour.hardware for colour in HARDWARE_COLOURS]

        assert len(set(values)) == len(values)

    def test_the_names_that_bit_us_carry_the_right_colour(self):
        """Spelled out rather than derived, because the whole defect was a
        table nobody checked against the hardware it claimed to describe."""
        by_name = {colour.name: colour for colour in HARDWARE_COLOURS}

        assert by_name["HW_BLUE"].rgb == (0, 0, 128)
        assert by_name["HW_BRIGHT_BLUE"].rgb == (0, 0, 255)
        # The CPC's "white" is grey; its white is "bright white".
        assert by_name["HW_WHITE"].rgb == (128, 128, 128)
        assert by_name["HW_BRIGHT_WHITE"].rgb == (255, 255, 255)


class TestThePalettePerMode:
    def test_mode_1_has_four_pens_and_mode_0_has_sixteen(self):
        assert len(cpc_palette(1)) == 4
        assert len(cpc_palette(0)) == 16

    def test_pen_zero_is_black_in_both_modes(self):
        """Every design Studio ships draws on black, and `cpc_pen` relies on
        pen 0 being the paper when it refuses to hand black to a colour that
        did not ask for it."""
        assert cpc_palette(0)[0].rgb == (0, 0, 0)
        assert cpc_palette(1)[0].rgb == (0, 0, 0)

    def test_a_mode_that_does_not_exist_is_refused(self):
        with pytest.raises(ValueError, match="mode"):
            cpc_palette(2)

    def test_mode_0_names_no_colour_twice(self):
        rgbs = [colour.rgb for colour in cpc_palette(0)]

        assert len(set(rgbs)) == len(rgbs)


class TestNamingAColour:
    def test_mode_0_can_resolve_a_colour_mode_1_could_only_approximate(self):
        """The point of the whole change, stated as a difference.

        Four pens cannot show green at all: `cpc_pen` had to hand "green" the
        nearest of black, blue, bright yellow and white.
        """
        assert cpc_palette(0)[cpc_pen("green", mode=0)].rgb[1] > 0
        assert cpc_palette(1)[cpc_pen("green", mode=1)].rgb[1] == 0

    def test_prose_naming_no_colour_is_still_none(self):
        assert cpc_pen("a sort of shimmering", mode=0) is None

    def test_a_design_on_the_cpc_gets_a_pen_index_for_its_own_word(self):
        """`declared_attribute` is the seam a program reaches colour through:
        the design says `ladrillo`, `game_config.h` gets `COLOUR_LADRILLO`, and
        on this machine the value behind it is a pen rather than an attribute
        byte."""
        project = blank_project("Palette", TargetPlatform.AMSTRAD_CPC)
        project.target.video_mode = VideoMode.CPC_MODE_0
        project.presentation.palette = [PaletteEntry(id="ladrillo", colour="bright red")]

        pen = declared_attribute(project, "ladrillo")

        assert pen is not None
        assert cpc_palette(0)[pen].rgb == (255, 0, 0)

    def test_the_same_word_on_mode_1_lands_on_a_pen_mode_1_actually_has(self):
        project = blank_project("Palette", TargetPlatform.AMSTRAD_CPC)
        project.target.video_mode = VideoMode.CPC_MODE_1
        project.presentation.palette = [PaletteEntry(id="ladrillo", colour="bright red")]

        pen = declared_attribute(project, "ladrillo")

        assert pen is not None
        assert 0 <= pen < 4

    def test_black_is_only_offered_to_prose_that_asked_for_black(self):
        """Pen 0 is the paper. Handing it to a colour the palette cannot show
        paints that thing in the colour of the void behind it."""
        assert cpc_pen("black", mode=1) == 0
        assert cpc_pen("bright red", mode=1) != 0


class TestTheTwoHalvesCannotDriftAgain:
    """One table produces the RGB the packers quantise against and the
    hardware bytes the library programs. This is the test that says so."""

    @pytest.mark.parametrize("mode", [0, 1])
    def test_the_header_programs_exactly_the_pens_the_packers_quantise_against(self, mode):
        from llmz80.studio.codegen import render_config_header
        from llmz80.studio.palette import cpc_rgb

        project = blank_project("Pens", TargetPlatform.AMSTRAD_CPC)
        project.target.video_mode = VideoMode.CPC_MODE_0 if mode == 0 else VideoMode.CPC_MODE_1

        header = render_config_header(project)
        written = [
            int(value, 16)
            for line in header.splitlines()
            if line.startswith("#define CPC_PALETTE_PENS ")
            for value in line.split(" ", 2)[2].split(", ")
        ]

        assert f"#define CPC_PEN_COUNT {len(cpc_rgb(mode))}" in header
        assert written == [colour.hardware for colour in cpc_palette(mode)]

    def test_the_spectrum_header_carries_no_cpc_pens(self):
        from llmz80.studio.codegen import render_config_header

        header = render_config_header(blank_project("Pens", TargetPlatform.SPECTRUM))

        assert "CPC_PALETTE_PENS" not in header

    @pytest.mark.parametrize("mode", [0, 1])
    def test_the_grid_alphabet_is_one_character_per_pen(self, mode):
        """`grid_errors` measures a drawn row against the alphabet's length, so
        a pen with no character is a pen the model cannot name and a character
        with no pen is one the packer cannot resolve."""
        from llmz80.studio.sprite_grid import palette_for

        project = blank_project("Pens", TargetPlatform.AMSTRAD_CPC)
        project.target.video_mode = VideoMode.CPC_MODE_0 if mode == 0 else VideoMode.CPC_MODE_1

        palette = palette_for(project)

        assert len(palette.alphabet) == len(palette.pens)
        assert len(set(palette.alphabet)) == len(palette.alphabet)


class TestPensPastNine:
    """Mode 0's alphabet is `0123456789abcdef`, and two places read it back.

    Found by generating a game. The drafter chose mode 0 for a Breakout whose
    bricks are about colour, the artist drew a sheet using pen `f`, and the
    run died with

        invalid literal for int() with base 10: 'f'

    `GridPalette.alphabet` grew hex digits when mode 0's sixteen pens became
    reachable; `frames_from_grid` and `render_grid` went on calling `int()` on
    the character. One of them crashed and the other -- guarded by `isdigit()`
    -- would have quietly drawn every pen above 9 as transparent, which is the
    worse of the two because it produces art rather than an error.
    """

    def _sheet(self, character):
        from llmz80.studio.sprite_grid import SpriteFrameGrid, SpriteSheetGrid
        from llmz80.studio.spriting import SPRITE_SIZE

        row = character * SPRITE_SIZE
        return SpriteSheetGrid(frames=[SpriteFrameGrid(rows=[row] * SPRITE_SIZE)])

    def _mode_0_palette(self):
        from llmz80.studio.sprite_grid import palette_for

        project = blank_project("Pens", TargetPlatform.AMSTRAD_CPC)
        project.target.video_mode = VideoMode.CPC_MODE_0
        return palette_for(project)

    @pytest.mark.parametrize("character,index", [("0", 0), ("9", 9), ("a", 10), ("f", 15)])
    def test_a_character_resolves_to_its_pen(self, character, index):
        palette = self._mode_0_palette()

        assert palette.index_of(character) == index

    def test_a_hex_pen_survives_being_turned_into_pixels(self):
        from llmz80.studio.sprite_grid import frames_from_grid

        palette = self._mode_0_palette()

        frames = frames_from_grid(self._sheet("f"), palette)

        assert frames[0].getpixel((0, 0)) == (*palette.pens[15], 255)

    def test_a_hex_pen_is_drawn_in_the_preview_rather_than_dropped(self):
        """`render_grid` is what a person looks at to judge the art. A pen it
        skips reads as a hole in the sprite that is not in the sprite."""
        from llmz80.studio.sprite_grid import render_grid

        palette = self._mode_0_palette()

        image = render_grid(self._sheet("a"), palette, scale=1)

        assert image.getpixel((0, 0)) == (*palette.pens[10], 255)

    def test_the_transparent_character_is_still_transparent(self):
        from llmz80.studio.sprite_grid import TRANSPARENT, frames_from_grid

        palette = self._mode_0_palette()

        frames = frames_from_grid(self._sheet(TRANSPARENT), palette)

        assert frames[0].getpixel((0, 0))[3] == 0

    def test_a_character_the_mode_does_not_have_is_refused(self):
        """Mode 1 has four pens, so `a` names nothing there and must not be
        read as pen 10 of a palette that has four entries."""
        from llmz80.studio.sprite_grid import palette_for

        project = blank_project("Pens", TargetPlatform.AMSTRAD_CPC)
        project.target.video_mode = VideoMode.CPC_MODE_1

        with pytest.raises(ValueError):
            palette_for(project).index_of("a")
