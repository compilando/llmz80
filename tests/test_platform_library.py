"""The platform library stops naming five keys, five sounds and four shapes."""

import re
import shutil
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path

import pytest

LIB = Path(__file__).resolve().parents[1] / "resources" / "studio_lib"


def test_the_header_no_longer_fixes_five_inputs_and_five_cell_kinds():
    header = (LIB / "common" / "platform.h").read_text(encoding="utf-8")
    for gone in ("IN_LEFT", "IN_ACTION", "CELL_PLAYER", "CELL_WALL",
                 "SOUND_START", "SOUND_COLLECT"):
        assert gone not in header, f"{gone} survives in platform.h"


def test_the_header_declares_plat_cell_as_a_character():
    header = (LIB / "common" / "platform.h").read_text(encoding="utf-8")
    assert "void plat_cell(unsigned char col, unsigned char row, char glyph);" in header


def test_both_targets_read_input_through_the_generated_binding_list():
    for target in ("spectrum", "cpc"):
        source = (LIB / target / "platform.c").read_text(encoding="utf-8")
        assert "INPUT_BINDINGS(X)" in source, target
        assert "#undef X" in source, target


def test_no_hardcoded_actor_shapes_remain():
    source = (LIB / "spectrum" / "platform.c").read_text(encoding="utf-8")
    for gone in ("shape_player", "shape_enemy", "shape_item", "shape_wall"):
        assert gone not in source, f"{gone} survives in the Spectrum library"


def test_sounds_are_dispatched_by_index_not_by_a_fixed_name():
    source = (LIB / "spectrum" / "platform.c").read_text(encoding="utf-8")
    assert "SOUND_COLLECT" not in source
    assert "case 0:" in source


def test_the_spectrum_wait_declines_an_isolated_gap_and_reports_a_repeated_one():
    """The bound and the branch that applies it, pinned by value.

    The behaviour is proved by the compiled harness below; this reads the
    source so that a machine with no C compiler still refuses a silent
    removal. It pins the number as well as the name because the number is the
    judgement call: an earlier version clamped on magnitude alone and any
    value at all would have satisfied a test that only looked for the symbol.
    """
    source = (LIB / "spectrum" / "platform.c").read_text(encoding="utf-8")
    assert "#define RESYNC_FRAMES 8" in source
    assert "cost = resyncing ? (unsigned char)(RESYNC_FRAMES + 1) : 0;" in source


def _wait_frame_harness() -> str:
    """The library's own frame-cost arithmetic, lifted out to run on the host.

    Copying the rule into the test would have tested the copy. This takes the
    real lines -- the bound, the two statics and the function -- and supplies
    only what the Spectrum would have supplied: a frame counter. Everything
    judged below is therefore the code that ships.
    """
    source = (LIB / "spectrum" / "platform.c").read_text(encoding="utf-8")
    bound = re.search(r"^#define RESYNC_FRAMES .*$", source, re.M)
    statics = re.search(
        r"^static unsigned int frame_mark;\nstatic unsigned char resyncing;$", source, re.M
    )
    wait = re.search(r"^unsigned char plat_wait_frame\(void\) \{.*?^\}$", source, re.M | re.S)
    assert bound and statics and wait, "the Spectrum wait no longer has the shape this test lifts"
    return f"""#include <stdio.h>

static volatile unsigned int fake_clock;
#define FRAME_CLOCK fake_clock

{statics.group(0)}
{bound.group(0)}

{wait.group(0)}

/* Each call advances the counter to `now` and asks what the iteration cost.
 * The wait's own guard loop times out because nothing else moves the clock,
 * which is exactly what a Spectrum with a stopped interrupt would do and is
 * harmless here: the reading is taken before the wait. */
static unsigned int trace(unsigned int step, int count, char *out) {{
    unsigned int now = 1000;
    int i;
    frame_mark = now;
    resyncing = 0;
    for (i = 0; i < count; ++i) {{
        now += step;
        fake_clock = now;
        out += sprintf(out, "%u ", (unsigned int)plat_wait_frame());
    }}
    return now;
}}

int main(void) {{
    char line[128];
    unsigned int now;
    int i;
    trace(1, 4, line);
    printf("steady %s\\n", line);
    trace(3, 4, line);
    printf("slow %s\\n", line);
    trace(30, 4, line);
    printf("absent_every_time %s\\n", line);

    /* One gap, then a loop that keeps pace: a title screen handing over to
     * gameplay. Nothing here may be reported. */
    now = 1000;
    frame_mark = now;
    resyncing = 0;
    line[0] = 0;
    {{
        char *out = line;
        now += 30;
        fake_clock = now;
        out += sprintf(out, "%u ", (unsigned int)plat_wait_frame());
        for (i = 0; i < 3; ++i) {{
            now += 1;
            fake_clock = now;
            out += sprintf(out, "%u ", (unsigned int)plat_wait_frame());
        }}
    }}
    printf("one_gap %s\\n", line);
    return 0;
}}
"""


@lru_cache(maxsize=1)
def _wait_frame_traces() -> dict[str, list[int]]:
    compiler = shutil.which("cc")
    if compiler is None:
        pytest.skip("no host C compiler; the source-level test above still applies")
    with tempfile.TemporaryDirectory() as work:
        source = Path(work) / "wait_frame.c"
        binary = Path(work) / "wait_frame"
        source.write_text(_wait_frame_harness(), encoding="utf-8")
        subprocess.run(
            [compiler, "-O0", "-Werror", "-o", str(binary), str(source)],
            check=True,
            capture_output=True,
        )
        output = subprocess.run([str(binary)], check=True, capture_output=True, text=True).stdout
    return {
        line.split()[0]: [int(value) for value in line.split()[1:]]
        for line in output.strip().splitlines()
    }


def test_a_loop_that_keeps_pace_is_charged_nothing():
    assert _wait_frame_traces()["steady"] == [0, 0, 0, 0]


def test_a_loop_that_takes_three_frames_an_iteration_is_reported_in_full():
    """16.7 Hz, above MAX_MISSED_FRAMES and below the resynchronisation bound:
    the band the gate exists to catch, reported honestly every iteration."""
    assert _wait_frame_traces()["slow"] == [2, 2, 2, 2]


def test_the_gap_left_by_a_loop_that_was_not_running_is_charged_to_nobody():
    """my-retro-game's title screen polls without pacing itself, so the first
    wait of gameplay saw 30-odd frames it had not spent. That reading is
    declined, and the fast iterations after it still read zero."""
    assert _wait_frame_traces()["one_gap"] == [0, 0, 0, 0]


def test_a_loop_that_is_out_of_band_every_iteration_is_not_forgiven_twice():
    """The distinction the bound rests on: absence happens once per transition,
    slowness happens every iteration. An earlier version tested magnitude alone
    and so certified every program at or below 5 Hz -- a 5 Hz loop passing while
    a 5.6 Hz loop failed. Recurrence separates them, and the repeat is reported
    as one frame past the bound, which fails the gate."""
    assert _wait_frame_traces()["absent_every_time"] == [0, 9, 9, 9]
