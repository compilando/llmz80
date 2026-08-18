"""Pre-shifted sprite art: the same figure packed at every sub-byte offset.

A sprite moves down by one pixel for the cost of a different address
(`plat_sprite_py`). It cannot move *across* by one pixel that way, because a
byte of screen holds several pixels -- eight on the Spectrum, four in CPC mode
1, two in mode 0 -- and a sprite whose left edge falls inside a byte has its
bits in different positions. The era's answer, and this one, is to pack the
figure once per offset and pick the copy that matches.

The thing worth getting right here is that it is one mechanism, not three. The
packers already walk the source image pixel by pixel and put pixel `x` into
byte `x // pixels_per_byte`; a shifted copy is the *same walk over a wider
canvas with the figure pasted `k` pixels in*. No byte rotation, no carry
between bytes, no per-machine bit surgery -- which is what makes the Spectrum,
mode 0 and mode 1 come out of one code path with only `pixels_per_byte`
differing.
"""

from __future__ import annotations

import pytest
from PIL import Image

from llmz80.studio.models import TargetPlatform, VideoMode
from llmz80.studio.palette import cpc_rgb
from llmz80.studio.samples import blank_project
from llmz80.studio.spriting import (
    SPRITE_SIZE,
    pack_cpc,
    pack_spectrum,
    pixels_per_byte,
    shift_count,
)


def _frame(*, left_column_only: bool = False) -> Image.Image:
    """A frame with one opaque column at x=0, or a recognisable blob."""
    image = Image.new("RGBA", (SPRITE_SIZE, SPRITE_SIZE), (0, 0, 0, 0))
    pixels = image.load()
    for y in range(SPRITE_SIZE):
        if left_column_only:
            pixels[0, y] = (255, 255, 255, 255)
        else:
            for x in range(SPRITE_SIZE):
                if (x + y) % 3 == 0:
                    pixels[x, y] = (255, 255, 255, 255)
    return image


class TestHowManyShifts:
    """One per pixel position inside a byte, which is the machine's own number."""

    def test_each_target_asks_for_its_own_pixels_per_byte(self):
        assert shift_count(TargetPlatform.SPECTRUM, VideoMode.SPECTRUM_BITMAP) == 8
        assert shift_count(TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_0) == 2
        assert shift_count(TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_1) == 4

    def test_it_is_the_same_number_the_packers_pack_with(self):
        """Stated as an identity rather than as two coincidental tables: a
        shift count that disagreed with the packer's pixels-per-byte would
        produce copies for offsets that do not exist, or miss ones that do."""
        for platform, mode in (
            (TargetPlatform.SPECTRUM, VideoMode.SPECTRUM_BITMAP),
            (TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_0),
            (TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_1),
        ):
            assert shift_count(platform, mode) == pixels_per_byte(platform, mode)


class TestSpectrumShifting:
    def test_one_shift_is_exactly_what_it_always_was(self):
        """The default has to be byte-for-byte the old output, or every
        existing project's art changes underneath it."""
        plain = pack_spectrum([_frame()])
        explicit = pack_spectrum([_frame()], shifts=1)

        assert plain.data == explicit.data
        assert plain.mask == explicit.mask
        assert plain.width_bytes == 2
        assert plain.shifts == 1

    def test_shifted_art_is_one_byte_wider(self):
        """A figure 16 pixels across, pushed up to 7 pixels right, needs 23
        columns -- which is three bytes, not two. One byte wider is the whole
        size story, on every target."""
        packed = pack_spectrum([_frame()], shifts=8)

        assert packed.width_bytes == 3
        assert packed.shifts == 8

    def test_every_shift_of_every_frame_is_present(self):
        packed = pack_spectrum([_frame(), _frame()], shifts=8)

        assert packed.frames == 2
        assert len(packed.data) == 2 * 8 * 3 * SPRITE_SIZE
        assert len(packed.mask) == len(packed.data)

    def test_a_frame_still_means_the_distance_to_the_next_frame(self):
        """`sprite_header` builds its offset table as `frame * bytes_per_frame`
        and nothing else, so this property carries the whole layout."""
        packed = pack_spectrum([_frame(), _frame(), _frame()], shifts=8)

        assert packed.bytes_per_frame == 8 * 3 * SPRITE_SIZE
        assert len(packed.data) == packed.frames * packed.bytes_per_frame

    def test_shift_k_moves_the_figure_k_pixels_right(self):
        """The claim the whole feature rests on, read off the packed bits.

        One opaque column at x=0 must appear as bit 7 of byte 0 at shift 0 and
        walk one bit right per shift, reaching bit 0 at shift 7 -- and never
        spill into byte 1, because the figure is only one pixel wide.
        """
        packed = pack_spectrum([_frame(left_column_only=True)], shifts=8)
        stride = 3 * SPRITE_SIZE

        for shift in range(8):
            row = packed.data[shift * stride : shift * stride + 3]
            assert row[0] == 0x80 >> shift, shift
            assert row[1] == 0x00, shift
            assert row[2] == 0x00, shift

    def test_a_figure_at_the_right_edge_spills_into_the_extra_byte(self):
        """The reason the copy is a byte wider at all: at shift 7 the last
        pixel of a 16-wide figure lands in the third byte, and a packer that
        kept two bytes would drop it."""
        packed = pack_spectrum([_frame()], shifts=8)
        stride = 3 * SPRITE_SIZE
        last_shift = packed.data[7 * stride : 8 * stride]

        assert any(last_shift[byte] for byte in range(2, stride, 3))

    def test_the_mask_keeps_the_background_where_nothing_was_pasted(self):
        """A shifted copy's padding is transparent, and transparent means
        "keep the background" -- so the columns the figure was pushed off must
        be all-ones in the mask, not all-zeros erasing the screen."""
        packed = pack_spectrum([_frame(left_column_only=True)], shifts=8)
        stride = 3 * SPRITE_SIZE

        row = packed.mask[7 * stride : 7 * stride + 3]
        assert row[0] == 0xFF ^ 0x01
        assert row[1] == 0xFF
        assert row[2] == 0xFF

    def test_the_attribute_is_read_off_the_art_not_off_the_padding(self):
        """Every shifted copy adds transparent pixels, and a sprite whose ink
        was averaged over them would drift towards black as it shifts."""
        plain = pack_spectrum([_frame()])
        shifted = pack_spectrum([_frame()], shifts=8)

        assert shifted.attribute == plain.attribute


class TestCpcShifting:
    @pytest.mark.parametrize("mode,shifts,plain_width", [(0, 2, 8), (1, 4, 4)])
    def test_shifted_art_is_one_byte_wider_in_both_modes(self, mode, shifts, plain_width):
        packed = pack_cpc([_frame()], mode=mode, palette=cpc_rgb(mode), shifts=shifts)

        assert packed.width_bytes == plain_width + 1
        assert packed.shifts == shifts

    @pytest.mark.parametrize("mode,shifts", [(0, 2), (1, 4)])
    def test_the_interleaved_mask_still_doubles_the_stride(self, mode, shifts):
        """CPC art carries its mask inside `data`, one byte ahead of each
        colour byte, so a shifted layout must double the same way an unshifted
        one does or `bytes_per_frame` lies to the offset table."""
        packed = pack_cpc([_frame(), _frame()], mode=mode, palette=cpc_rgb(mode), shifts=shifts)

        assert packed.mask == b""
        assert packed.bytes_per_frame == shifts * 2 * packed.width_bytes * SPRITE_SIZE
        assert len(packed.data) == packed.frames * packed.bytes_per_frame

    @pytest.mark.parametrize("mode,shifts", [(0, 2), (1, 4)])
    def test_one_shift_is_exactly_what_it_always_was(self, mode, shifts):
        plain = pack_cpc([_frame()], mode=mode, palette=cpc_rgb(mode))
        explicit = pack_cpc([_frame()], mode=mode, palette=cpc_rgb(mode), shifts=1)

        assert plain.data == explicit.data
        assert plain.shifts == 1

    def test_mode_0_shift_1_moves_the_figure_one_pixel(self):
        """Mode 0 has two pixels to a byte, so its only sub-byte offset is 1 --
        and the pens interleave across the byte rather than sitting in
        nibbles, which is exactly why this is checked against the packer's own
        output for a known-shifted source rather than by rotating bits."""
        source = _frame(left_column_only=True)
        moved = Image.new("RGBA", (SPRITE_SIZE, SPRITE_SIZE), (0, 0, 0, 0))
        moved.paste(source, (1, 0))

        shifted = pack_cpc([source], mode=0, palette=cpc_rgb(0), shifts=2)
        expected = pack_cpc([moved], mode=0, palette=cpc_rgb(0), shifts=1)
        stride = 2 * shifted.width_bytes * SPRITE_SIZE
        block = shifted.data[stride : 2 * stride]

        # The shifted copy is a byte wider, so compare the bytes the narrower
        # reference covers, row by row.
        for row in range(SPRITE_SIZE):
            wide = block[row * 2 * shifted.width_bytes :][: 2 * 8]
            narrow = expected.data[row * 2 * 8 :][: 2 * 8]
            assert wide == narrow, row


class TestTheCostIsVisible:
    def test_shifting_multiplies_the_bytes_and_the_budget_gate_sees_it(self):
        """No new gate for this. `compiler.packed_sprite_bytes` already sums
        data and mask, and `validate_sprite_budget` already refuses artwork
        that will not fit -- so pre-shifted art is weighed by the machinery
        that weighs everything else, and a design that asks for more than its
        static_data_bytes allows is refused with the number.
        """
        from llmz80.studio.compiler import packed_sprite_bytes

        plain = {"hero": pack_spectrum([_frame()])}
        shifted = {"hero": pack_spectrum([_frame()], shifts=8)}

        assert packed_sprite_bytes(plain) == 2 * 2 * SPRITE_SIZE
        assert packed_sprite_bytes(shifted) == 8 * 2 * 3 * SPRITE_SIZE
        assert packed_sprite_bytes(shifted) == 12 * packed_sprite_bytes(plain)


class TestTheRightHandBound:
    """`MAX_SPRITE_PX` has to know about the extra byte, or the last column
    corrupts memory.

    A shifted copy is one byte wider than the sprite, so the rightmost pixel a
    sprite can start at is one byte further left than it would otherwise be --
    and *further right* by `shifts - 1`, because the sub-byte positions inside
    that last legal byte are all reachable. Getting either half wrong is
    invisible until something at the right edge of the screen scribbles past
    the display file.
    """

    @pytest.mark.parametrize(
        "platform,mode,smooth,expected",
        [
            # Spectrum: 256 pixels, 32 bytes, sprite 2 bytes (3 shifted).
            (TargetPlatform.SPECTRUM, VideoMode.SPECTRUM_BITMAP, False, 240),
            (TargetPlatform.SPECTRUM, VideoMode.SPECTRUM_BITMAP, True, (32 - 3) * 8 + 7),
            # CPC mode 0: 160 pixels, 80 bytes, sprite 8 bytes (9 shifted).
            (TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_0, False, 144),
            (TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_0, True, (80 - 9) * 2 + 1),
            # CPC mode 1: 320 pixels, 80 bytes, sprite 4 bytes (5 shifted).
            (TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_1, False, 304),
            (TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_1, True, (80 - 5) * 4 + 3),
        ],
    )
    def test_the_bound_accounts_for_the_widened_copy(self, platform, mode, smooth, expected):
        from llmz80.studio.codegen import max_sprite_px

        project = blank_project("Bound", platform)
        project.target.video_mode = mode
        project.presentation.smooth_horizontal = smooth

        assert max_sprite_px(project) == expected

    def test_an_unshifted_bound_is_just_the_screen_less_the_sprite(self):
        from llmz80.studio.codegen import max_sprite_px

        for platform, mode, width in (
            (TargetPlatform.SPECTRUM, VideoMode.SPECTRUM_BITMAP, 256),
            (TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_0, 160),
            (TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_1, 320),
        ):
            project = blank_project("Bound", platform)
            project.target.video_mode = mode

            assert max_sprite_px(project) == width - SPRITE_SIZE

    def test_mode_1_needs_more_than_a_byte_to_say_it(self):
        """Which is why `plat_sprite_px` takes an int. 320 pixels across does
        not fit in the `unsigned char` every other coordinate here uses."""
        from llmz80.studio.codegen import max_sprite_px

        project = blank_project("Bound", TargetPlatform.AMSTRAD_CPC)
        project.target.video_mode = VideoMode.CPC_MODE_1

        assert max_sprite_px(project) > 255

    def test_the_header_carries_the_machine_facts_the_blitter_divides_by(self):
        from llmz80.studio.codegen import render_config_header

        project = blank_project("Bound", TargetPlatform.AMSTRAD_CPC)
        project.target.video_mode = VideoMode.CPC_MODE_1
        header = render_config_header(project)

        assert "#define PIXELS_PER_BYTE 4" in header
        assert "#define PIXELS_PER_BYTE_LOG 2" in header
        assert "#define MAX_SPRITE_PX 304" in header

    def test_the_log_really_is_the_log(self):
        """A shift that did not divide by PIXELS_PER_BYTE would put every
        sprite in the wrong column, on one target only."""
        from llmz80.studio.codegen import pixels_per_byte_log

        for platform, mode in (
            (TargetPlatform.SPECTRUM, VideoMode.SPECTRUM_BITMAP),
            (TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_0),
            (TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_1),
        ):
            assert 1 << pixels_per_byte_log(platform, mode) == pixels_per_byte(platform, mode)


class TestADesignCanAskForIt:
    """The flag has to be reachable by the pipeline, not only by hand-editing
    game.yml -- otherwise the whole feature is a manual one."""

    def test_the_planner_can_write_a_boolean(self):
        from llmz80.studio.planner import FlagValue, ProjectChange, ProjectProposal, apply_proposal

        project = blank_project("Smooth", TargetPlatform.SPECTRUM)
        assert project.presentation.smooth_horizontal is False

        updated = apply_proposal(
            project,
            ProjectProposal(
                summary="the ball slides",
                changes=[
                    ProjectChange(
                        path="/presentation/smooth_horizontal",
                        operation="replace",
                        reason="the ball must not jump eight pixels at a time",
                        value=FlagValue(flag=True),
                    )
                ],
            ),
        )

        assert updated.presentation.smooth_horizontal is True

    def test_the_drafter_is_told_what_it_costs(self):
        """A flag offered without its price is a flag that gets set on every
        design, and the Spectrum's twelvefold art would then push most of them
        past their own budget at build time rather than at design time."""
        from llmz80.studio.drafting import DRAFT_SYSTEM_PROMPT

        prompt = DRAFT_SYSTEM_PROMPT

        assert "smooth_horizontal" in prompt
        assert "12x" in prompt
        assert "static_data_bytes" in prompt
