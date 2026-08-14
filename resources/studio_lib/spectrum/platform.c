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
#define FRAMES ((volatile unsigned char *)23672)

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
    zx_border(INK_BLACK);
    zx_cls(PAPER_BLACK | INK_WHITE);
}

void plat_clear(void) {
    zx_cls(PAPER_BLACK | INK_WHITE);
}

void plat_border(unsigned char colour) {
    zx_border(colour);
}

/* Above this many missed frames the gap was not one iteration running long: it
 * was a stretch during which this loop was not running at all -- a title
 * screen polling for a key without pacing itself, a level being built, a tape
 * access. Both look identical from here, because all this counter knows is how
 * long it has been since somebody last called; so rather than report an
 * absence as a slowness, the wait treats it as a resynchronisation and charges
 * nothing. This is not hypothetical. my-retro-game's title screen polls the
 * action key in a tight loop with no wait, so the first wait inside gameplay
 * charged the whole title screen -- 38 frames -- to an iteration that really
 * ran in about three, and the pacing gate failed a program whose loop was fast.
 *
 * The trade-off, stated plainly: a program that overran by more than this on
 * *every* iteration would report zero and be judged as keeping pace. That is a
 * program drawing under six frames a second, which the animation gate, the
 * visual-change check and any person looking at the screen all reject long
 * before frame pacing becomes the interesting question. What stays measured is
 * 2..RESYNC_FRAMES, which is exactly the band where a game judders instead of
 * looking broken -- the band MAX_MISSED_FRAMES in llmz80/studio/pacing.py
 * exists to catch. */
#define RESYNC_FRAMES 8

/* Uses the ROM frame counter, with a guard so a stopped interrupt cannot hang.
 * The counter also measures the work: the number of frames that elapsed since
 * the previous wait is what the last iteration cost, up to the resynchronisation
 * bound above. Only the counter's low byte is read, so a gap longer than 256
 * frames wraps and can land back inside the plausible band; the bound is a
 * plausibility filter, not a proof, and the honest fix stays the same -- every
 * loop a program writes should call this, including its menus. */
unsigned char plat_wait_frame(void) {
    static unsigned char previous;
    unsigned char start = *FRAMES;
    /* One frame between consecutive waits means the work kept pace, so the
     * frames actually lost is the elapsed count less that one. */
    unsigned char elapsed = (unsigned char)(start - previous);
    unsigned char cost = elapsed > 1 ? (unsigned char)(elapsed - 1) : 0;
    unsigned int guard = 0;
    if (cost > RESYNC_FRAMES) {
        cost = 0;
    }
    while (*FRAMES == start && ++guard < 12000) {
    }
    previous = *FRAMES;
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
