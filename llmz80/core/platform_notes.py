"""Constraints that only showed themselves by building for the real machines.

Every note here was paid for once: a build that failed, a link that refused, or
a program that booted and drew a screen while doing the wrong thing. Handing
them to whoever writes the code is the cheapest failure prevention available,
which is why they live in the prompt rather than only in a roadmap.
"""

from __future__ import annotations

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
    can miss a short scripted keypress entirely.
  * Keep the work inside one 50 Hz frame. Redrawing the whole playfield every
    frame will not fit; redraw only the cells that changed.
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
  * Key constants from input.h are spelled IN_KEY_SCANCODE_ plus the key as it
    appears on the keyboard: IN_KEY_SCANCODE_SPACE, and lower case letters as
    IN_KEY_SCANCODE_q, IN_KEY_SCANCODE_a, IN_KEY_SCANCODE_o, IN_KEY_SCANCODE_p.
    Read them with in_key_pressed().
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
  * Mode 1 has four pens in total. Distinguish more than four kinds of thing by
    shape or size, not by colour alone.
  * With the firmware disabled there is no free-running frame counter.
"""


def platform_notes(platform: str) -> str:
    """Hazard notes for one target, ready to paste into a prompt."""
    specific = SPECTRUM_NOTES if platform == "spectrum" else CPC_NOTES
    return "PLATFORM NOTES\n" + COMMON_NOTES.rstrip() + "\n" + specific.rstrip() + "\n"
