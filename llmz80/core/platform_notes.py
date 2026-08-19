"""Constraints that only showed themselves by building for the real machines.

Every note here was paid for once: a build that failed, a link that refused, or
a program that booted and drew a screen while doing the wrong thing. Handing
them to whoever writes the code is the cheapest failure prevention available,
which is why they live in the prompt rather than only in a roadmap.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - import cost, not behaviour
    from llmz80.studio.models import GameProject

COMMON_NOTES = """
Both machines, learned from real failures:

  * The build rejects any unexpected compiler warning, not just errors. Code
    that merely compiles is not accepted. Warnings seen most often: unreachable
    code after a return or an always-true loop, and an unused function
    argument. Remove the cause rather than suppressing it.

  * Start gameplay on key press, not key release. An automated test holds a key
    for a few hundred milliseconds and photographs the screen while it is still
    held; a program that waits for release shows a menu and looks broken.
  * Poll menus in a tight loop rather than once per frame. A frame-gated poll
    can miss a short scripted keypress entirely. Call plat_wait_frame once as
    you leave such a loop and ignore what it returns: the frame cost is
    measured between consecutive calls, so without that the time a person spent
    on the menu is charged to the first iteration of the gameplay loop.
  * Keep the work inside one 50 Hz frame. Redrawing the whole playfield every
    frame will not fit; redraw only the cells that changed.
  * Byte constants from 128 to 255 need an explicit cast, or SDCC raises
    warning 158 and the build refuses the program. Write (u8)0xFF, not 0xFF.
    The build applies this cast itself if you forget, but a program it has to
    rewrite is one whose line numbers no longer match what you sent.
  * Do not redefine anything the generated headers already define. They are
    listed in the design above with their values; a second #define of one of
    them is a warning, and the build refuses unexpected warnings.
"""

SPECTRUM_NOTES = """
ZX Spectrum 48K, with z88dk and the sdcc_iy library:

  * Screen memory is not linear. Within a character row consecutive pixel lines
    are 256 bytes apart; use zx_cxy2saddr and zx_cxy2aaddr rather than arithmetic.
  * Drawing text through the ROM font at 0x3D00 avoids linking stdio and keeps
    the binary far smaller than printf does.
  * Interrupts start disabled under this crt, so the ROM frame counter at
    23672 never advances and a loop waiting for it to change hangs forever.
    Call intrinsic_ei() from <intrinsic.h> once at start-up before using it as
    a clock. Measured: without it, twenty consecutive waits all timed out;
    with it, all twenty saw a tick.
  * bit_beep disables interrupts while it plays, so time spent making sound is
    invisible to that counter even once they are enabled.
  * Give any wait loop a bounded guard anyway. A program that hangs still
    boots, still draws its first screen, and looks alive while doing nothing.
  * bit_beep blocks. A long effect inside the game loop costs frames.
  * Do not read the keyboard yourself. plat_input() already scans every key the
    design bound and returns one bit per binding; the bits are named
    INPUT_<NAME> in game_config.h. Calling in_key_pressed() with a scancode of
    your own choosing binds a key the design never declared.
"""

CPC_NOTES = """
Amstrad CPC, with CPCtelera and SDCC:

  * Never use 16-bit division, modulo or multiplication. SDCC satisfies those
    from library modules built for sdcccall(1) and the link enforces
    sdcccall(0), so the build fails with conflicting-ABI warnings. Use repeated
    subtraction, accumulation or shifts instead.
  * Only const data survives. A file-scope initialised non-const array lands in
    the data segment, which this link does not initialise, so it holds whatever
    was in memory. Assign such values at run time or make the table const.
  * cpct_setPalette takes a mutable pointer. Casting a const array to it raises
    SDCC warning 357, and the build policy rejects unexpected warnings.
"""

#: What is true in one video mode and false in the other. Mode 1's advice --
#: tell things apart by shape, since four pens cannot do it -- is right there
#: and wrong by twelve pens in mode 0, and a basketball design running in mode
#: 0 was given it.
CPC_MODE_NOTES = {
    0: """  * Mode 0 has sixteen pens and 20 columns. Colour is what this mode is for:
    tell things apart with it. The trade is width -- half the columns mode 1
    has -- so a screen here is 20 cells across and no wider.
""",
    1: """  * Mode 1 has four pens in total and 40 columns. Distinguish more than four
    kinds of thing by shape or size, not by colour alone.
""",
}


def platform_notes(project: "GameProject") -> str:
    """Hazard notes for the machine *and the mode* this design runs in.

    Takes the project rather than a platform string, which it did until a
    basketball game running in mode 0 was told "Mode 1 has four pens in total.
    Distinguish more than four kinds of thing by shape or size" -- advice for
    the other mode, wrong by twelve pens about the one it was in. A note that
    depends on the video mode cannot be chosen from the platform alone.
    """
    if project.target.platform.value == "spectrum":
        specific = SPECTRUM_NOTES.rstrip()
    else:
        mode = 0 if project.target.video_mode.value == "cpc_mode_0" else 1
        specific = CPC_NOTES.rstrip() + "\n" + CPC_MODE_NOTES[mode].rstrip()
    return "PLATFORM NOTES\n" + COMMON_NOTES.rstrip() + "\n" + specific + "\n"
