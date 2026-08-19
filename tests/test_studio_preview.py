"""Showing a drawn sprite sheet in the terminal."""

from PIL import Image

from llmz80.studio.preview import RESET, sprite_lines


def _sheet(pixels: list[list[tuple[int, int, int, int]]]) -> Image.Image:
    height = len(pixels)
    width = len(pixels[0])
    image = Image.new("RGBA", (width, height))
    image.putdata([pixel for row in pixels for pixel in row])
    return image


class TestSpriteLines:
    def test_one_line_per_pixel_row(self):
        opaque = (255, 0, 0, 255)
        sheet = _sheet([[opaque, opaque], [opaque, opaque], [opaque, opaque]])

        assert len(sprite_lines(sheet)) == 3

    def test_a_pixel_is_painted_with_its_own_colour(self):
        """No palette lookup, which is the whole point of this module.

        The preview it replaces quantised each pixel against
        `config.get_palette_for_platform`, a table that is *not* the one
        `compiler.CPC_DEFAULT_PALETTE` packs the sprite with -- the CLI's own
        docstring said so. But the sheet is drawn from the packer's palette to
        begin with (`sprite_grid.palette_for`), so its pixels already are what
        the machine will show, and re-quantising them could only move them
        away from it.
        """
        sheet = _sheet([[(18, 52, 86, 255)]])

        assert "48;2;18;52;86" in sprite_lines(sheet)[0]

    def test_every_line_ends_by_resetting_the_colour(self):
        sheet = _sheet([[(1, 2, 3, 255)], [(4, 5, 6, 255)]])

        for line in sprite_lines(sheet):
            assert line.endswith(RESET)

    def test_a_transparent_pixel_is_not_painted(self):
        """Mask, not colour. A sprite's transparent pixels are where the
        background shows through, and painting them any colour at all -- black
        included -- draws a box around art that has none."""
        clear = (0, 0, 0, 0)
        sheet = _sheet([[clear]])

        assert "48;2;" not in sprite_lines(sheet)[0]

    def test_a_half_transparent_pixel_counts_as_solid(self):
        """The same threshold the packers apply, so the preview and the
        packed sprite disagree about no pixel."""
        from llmz80.studio.spriting import ALPHA_THRESHOLD

        sheet = _sheet([[(9, 9, 9, ALPHA_THRESHOLD)]])

        assert "48;2;9;9;9" in sprite_lines(sheet)[0]

    def test_a_pixel_just_under_the_threshold_is_transparent(self):
        from llmz80.studio.spriting import ALPHA_THRESHOLD

        sheet = _sheet([[(9, 9, 9, ALPHA_THRESHOLD - 1)]])

        assert "48;2;" not in sprite_lines(sheet)[0]

    def test_a_sheet_in_a_mode_without_alpha_is_read_anyway(self):
        """`Image.open(...).convert("RGBA")` is the caller's job, but a plain
        RGB sheet reaching here must render rather than raise."""
        sheet = Image.new("RGB", (2, 1), (7, 7, 7))

        assert "48;2;7;7;7" in sprite_lines(sheet)[0]
