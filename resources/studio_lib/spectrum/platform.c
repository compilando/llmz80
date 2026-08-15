/* ZX Spectrum implementation of the Studio engine platform layer.
 *
 * Text is rendered straight from the ROM font instead of stdio so the binary
 * stays small and drawing is fully deterministic under the emulator harness.
 */
#include <arch/zx.h>
#include <input.h>
#include <intrinsic.h>
#include <sound.h>

#include "platform.h"
#include "game_config.h"
#include "sprites.h"

#define ROM_FONT ((const unsigned char *)0x3D00)
/* The ROM frame counter: three bytes at 23672, bumped by the 50 Hz interrupt.
 * Sixteen of them are read at once, because `ld hl,(nn)` is a single
 * uninterruptible instruction and so cannot catch the pair mid-increment. The
 * byte-wide read this replaces wrapped every 256 frames, and that was not a
 * footnote: a gap longer than a wrap landed back inside the plausible band and
 * was reported as a real overrun. Sixteen bits move the horizon from five
 * seconds to twenty-one minutes, which removes the ambiguity instead of
 * filtering it. */
#define FRAME_CLOCK (*(volatile unsigned int *)23672)

/* The counter as the last wait left it, and whether that wait already saw an
 * out-of-band gap. File scope so plat_init can seed the first and clear the
 * second; a function-local static could not be seeded before the first call. */
static unsigned int frame_mark;
static unsigned char resyncing;

static void put_glyph(unsigned char col, unsigned char row, const unsigned char *glyph,
                      unsigned char attribute) {
    unsigned char *address = (unsigned char *)zx_cxy2saddr(col, row);
    unsigned char *attributes = (unsigned char *)zx_cxy2aaddr(col, row);
    unsigned char line;
    for (line = 0; line < 8; ++line) {
        address[(unsigned int)line << 8] = glyph[line];
    }
    *attributes = attribute;
}

void plat_init(void) {
    /* Without this the ROM frame counter never advances, so plat_wait_frame
     * degenerates into a busy loop and reports a frame cost of zero forever. */
    intrinsic_ei();
    /* Seeded here rather than left to zero-initialisation: the first wait of a
     * run subtracts this from a counter the ROM has been advancing since
     * power-on, and an unseeded mark made that first reading arbitrary --
     * roughly one run in fifteen used to report a frame cost it never paid,
     * which condemned the whole run, since g_worst_frame_cost is a maximum. */
    frame_mark = FRAME_CLOCK;
    resyncing = 0;
    zx_border(INK_BLACK);
    zx_cls(PAPER_BLACK | INK_WHITE);
}

void plat_clear(void) {
    zx_cls(PAPER_BLACK | INK_WHITE);
}

void plat_border(unsigned char colour) {
    zx_border(colour);
}

/* A reported cost of `c` means the iteration occupied `c + 1` frames and so ran
 * at 50/(c + 1) Hz: 1 is 25 Hz and passes, 2 is 16.7 Hz and fails, 9 is 5 Hz.
 * That mapping is what makes this constant and MAX_MISSED_FRAMES judgeable at
 * all, so it is written down rather than left to be re-derived.
 *
 * What this bound exists for is not slowness. A loop that never calls the wait
 * -- a title screen polling for a keypress, which llmz80/core/platform_notes.py
 * requires, since a frame-gated poll can miss a short scripted press -- leaves
 * the counter running, and the next caller would otherwise be charged for every
 * frame of it. my-retro-game reported g_worst_frame_cost = 38 exactly that way,
 * while its game loop was really finishing in about three frames.
 *
 * The test is recurrence, not magnitude. A loop that was absent produces one
 * out-of-band gap per transition; a loop that is merely this slow produces one
 * on every iteration. So an isolated gap is forgiven and the second in a row is
 * reported. Clamping on magnitude alone was tried first and was worse than
 * useless: it approved every program at or below 5 Hz while still failing one
 * at 5.6 Hz, certifying the worst loops in the name of protecting the fast
 * ones, and the three backstops that clamp claimed to rely on do not exist --
 * feel.animation_report compares readings 50 frames apart and still sees a
 * 5 Hz loop animate, emulator_smoke's visual_change only catches a frozen
 * screen, and no person watches this pipeline at all.
 *
 * The residual blind spot, stated exactly: a single slow iteration bracketed by
 * fast ones reports zero. A stutter that never repeats is invisible here, and
 * nothing else in the pipeline sees it either. That is a gap, not a backstop.
 *
 * resources/studio_reference/spectrum/src/engine.c already carries this idea as
 * frame_cost_primed, with the same diagnosis in its comment -- "the first
 * sample after a level starts measures how long someone took to press a key,
 * not the work". But a free-written program never inherits the reference
 * engine, and the library is in every build; that is the gap this closes. */
#define RESYNC_FRAMES 8

/* Waits for the next frame off the ROM counter, with a guard so a stopped
 * interrupt cannot hang, and returns what the previous iteration cost. */
unsigned char plat_wait_frame(void) {
    unsigned int start = FRAME_CLOCK;
    /* One frame between consecutive waits means the work kept pace, so the
     * frames actually lost is the elapsed count less that one. */
    unsigned int elapsed = (unsigned int)(start - frame_mark);
    unsigned int missed = elapsed > 1 ? (unsigned int)(elapsed - 1) : 0;
    unsigned int guard = 0;
    unsigned char cost;
    if (missed > RESYNC_FRAMES) {
        /* An isolated gap is a loop that was not running. A second one in a
         * row is a loop that is simply this slow, and must not be forgiven: it
         * is reported as one frame past the bound, the smallest value that
         * cannot be mistaken for keeping pace. The true magnitude is not
         * reported, because after a gap this large it is not known to be one
         * iteration's worth of anything. */
        cost = resyncing ? (unsigned char)(RESYNC_FRAMES + 1) : 0;
        resyncing = 1;
    } else {
        cost = (unsigned char)missed;
        resyncing = 0;
    }
    while (FRAME_CLOCK == start && ++guard < 12000) {
    }
    frame_mark = FRAME_CLOCK;
    return cost;
}

unsigned char plat_input(void) {
    unsigned char keys = 0;
#define X(bit, code) if (in_key_pressed(code)) keys |= bit;
    INPUT_BINDINGS(X)
#undef X
    return keys;
}

void plat_text(unsigned char col, unsigned char row, const char *text) {
    while (*text != 0 && col < 32) {
        unsigned char code = (unsigned char)*text;
        if (code >= 32) {
            put_glyph(col, row, ROM_FONT + (((unsigned int)(code - 32)) << 3),
                      PAPER_BLACK | INK_WHITE);
        }
        ++col;
        ++text;
    }
}

/* The ROM font starts at code 32, eight bytes per glyph. Anything outside the
 * printable range draws a blank, which is what erasing a cell means here. */
void plat_cell(unsigned char col, unsigned char row, char glyph) {
    unsigned char code = (unsigned char)glyph;
    static const unsigned char blank[8] = {0, 0, 0, 0, 0, 0, 0, 0};
    if (col >= 32 || row >= 24) return;
    if (code < 32 || code > 127) {
        put_glyph(col, row, blank, PAPER_BLACK | INK_WHITE);
        return;
    }
    put_glyph(col, row, ROM_FONT + (((unsigned int)(code - 32)) << 3),
              PAPER_BLACK | INK_WHITE);
}

/* Draws one 16x16 masked sprite as four character cells: two cells wide,
 * two tall. Each half calls zx_cxy2saddr afresh rather than adding a fixed
 * offset to the first half's address -- the Spectrum's screen file is split
 * into three non-linear thirds, and only a fresh conversion gets the right
 * address when the sprite's second row of cells lands in the next third. */
void plat_sprite(unsigned char col, unsigned char row, unsigned char sprite,
                 unsigned char frame) {
#if SPRITE_COUNT
    const unsigned char *data;
    const unsigned char *mask;
    unsigned char half;
    unsigned char line;
    if (sprite >= SPRITE_COUNT) return;
    if (col > 30 || row > 22) return;
    /* Frame offsets come precomputed from the header: multiplying here would
     * pull in SDCC's 16-bit routines, which the CPCtelera link rejects and
     * which cost more than a table lookup anyway. */
    data = sprite_data[sprite] + sprite_frame_offset[sprite][frame];
    mask = sprite_mask[sprite] + sprite_frame_offset[sprite][frame];
    for (half = 0; half < 2; ++half) {
        unsigned char *base = (unsigned char *)zx_cxy2saddr(col, row + half);
        for (line = 0; line < 8; ++line) {
            unsigned char *at = base + ((unsigned int)line << 8);
            at[0] = (unsigned char)((at[0] & *mask++) | *data++);
            at[1] = (unsigned char)((at[1] & *mask++) | *data++);
        }
    }
    /* One attribute per covered cell. A single ink per sprite is what the
     * machine affords and what the era used; per-cell colour would need the
     * packer to carry an attribute plane. */
    *(unsigned char *)zx_cxy2aaddr(col, row) = sprite_attribute[sprite];
    *(unsigned char *)zx_cxy2aaddr(col + 1, row) = sprite_attribute[sprite];
    *(unsigned char *)zx_cxy2aaddr(col, row + 1) = sprite_attribute[sprite];
    *(unsigned char *)zx_cxy2aaddr(col + 1, row + 1) = sprite_attribute[sprite];
#else
    (void)col; (void)row; (void)sprite; (void)frame;
#endif
}

/* Beeper effects through z88dk's certified bit_beep, kept short because the
 * call blocks: every millisecond spent here is a millisecond the game loop is
 * not running. AUDIO_EFFECT_MASK lets the design switch each effect off.
 *
 * Five distinct sounds, by index. The design decides what each one is called
 * and what it means; this only guarantees that effect 0 and effect 1 do not
 * sound alike. Anything past the fifth is silent rather than wrong. */
void plat_sound(unsigned char effect) {
#if AUDIO_EFFECT_MASK
    if (!(AUDIO_EFFECT_MASK & (1 << effect))) return;
    switch (effect) {
        case 0: bit_beep(10, 400); break;
        case 1: bit_beep(6, 250); break;
        case 2: bit_beep(18, 900); break;
        case 3: bit_beep(10, 300); break;
        case 4: bit_beep(30, 1400); break;
        default: break;
    }
#else
    (void)effect;
#endif
}
