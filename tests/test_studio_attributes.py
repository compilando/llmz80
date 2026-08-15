"""Finding drawn pixels no player can see."""

from llmz80.studio.attributes import ATTRIBUTE_ORIGIN, cell_offset, invisible_cells


def _blank_screen() -> bytearray:
    """A screen with nothing drawn and white ink on black paper everywhere."""
    screen = bytearray(6912)
    for index in range(768):
        screen[ATTRIBUTE_ORIGIN + index] = 0x07
    return screen


def test_the_cell_offset_follows_the_thirds_the_hardware_has():
    """Row 8 starts the second third, which is 2048 bytes in, not 8 rows of 32."""
    assert cell_offset(0, 0) == 0
    assert cell_offset(1, 0) == 1
    assert cell_offset(0, 1) == 32
    assert cell_offset(0, 8) == 2048
    assert cell_offset(31, 23) == 2048 * 2 + 7 * 32 + 31


def test_pixels_drawn_in_a_cell_whose_ink_matches_its_paper_are_invisible():
    screen = _blank_screen()
    screen[cell_offset(4, 9)] = 0xFF
    screen[ATTRIBUTE_ORIGIN + 9 * 32 + 4] = 0x00  # INK_BLACK on PAPER_BLACK

    assert invisible_cells(bytes(screen)) == [(4, 9)]


def test_the_same_pixels_in_a_readable_cell_are_fine():
    screen = _blank_screen()
    screen[cell_offset(4, 9)] = 0xFF

    assert invisible_cells(bytes(screen)) == []


def test_an_empty_cell_is_not_invisible_content():
    """A black-on-black cell with nothing in it is just background."""
    screen = _blank_screen()
    screen[ATTRIBUTE_ORIGIN + 0] = 0x00

    assert invisible_cells(bytes(screen)) == []


def test_bright_does_not_separate_an_ink_from_its_own_paper():
    """BRIGHT applies to both halves of the attribute, so it cannot make an ink
    visible against a paper of the same colour."""
    screen = _blank_screen()
    screen[cell_offset(0, 0)] = 0xFF
    screen[ATTRIBUTE_ORIGIN + 0] = 0x40 | 0x02 | (0x02 << 3)  # bright red on red

    assert invisible_cells(bytes(screen)) == [(0, 0)]


def test_a_screen_of_the_wrong_size_is_no_screen():
    assert invisible_cells(b"") == []
    assert invisible_cells(bytes(100)) == []


def test_a_run_that_kept_no_display_file_abstains_rather_than_passing():
    """The CPC harness has no remote protocol to read memory through, so it
    writes no dump at all; a run whose ZRCP answer arrived short writes none
    either. Neither is evidence that every cell was readable."""
    from llmz80.studio.attributes import attribute_report

    report = attribute_report({"screen_dump": None})

    assert report["observed"] is False
    assert report["quality_pass"] is None
    assert "no display file" in report["reason"]


def test_a_truncated_dump_abstains_instead_of_judging_the_half_it_has(tmp_path):
    dump = tmp_path / "screen.bin"
    dump.write_bytes(bytes(4096))
    from llmz80.studio.attributes import attribute_report

    report = attribute_report({"screen_dump": str(dump)})

    assert report["observed"] is False
    assert report["quality_pass"] is None


def test_a_dump_that_cannot_be_read_abstains(tmp_path):
    from llmz80.studio.attributes import attribute_report

    report = attribute_report({"screen_dump": str(tmp_path / "absent.bin")})

    assert report["observed"] is False
    assert report["quality_pass"] is None


def test_a_readable_screen_is_watched_and_approved(tmp_path):
    dump = tmp_path / "screen.bin"
    screen = _blank_screen()
    screen[cell_offset(10, 10)] = 0xFF
    dump.write_bytes(bytes(screen))
    from llmz80.studio.attributes import attribute_report

    report = attribute_report({"screen_dump": str(dump)})

    assert report["observed"] is True
    assert report["quality_pass"] is True
    assert report["invisible_cells"] == []


def test_a_failure_names_a_dozen_cells_and_counts_the_rest(tmp_path):
    """A screen drawn entirely in its own paper colour has 768 invisible cells,
    and a diagnostic listing all 768 is not one."""
    dump = tmp_path / "screen.bin"
    screen = bytearray(6912)
    for index in range(6144):
        screen[index] = 0xFF
    dump.write_bytes(bytes(screen))
    from llmz80.studio.attributes import attribute_report

    report = attribute_report({"screen_dump": str(dump)})

    assert report["quality_pass"] is False
    assert len(report["invisible_cells"]) == 768
    assert "and 756 more" in report["failures"][0]
