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
#include "tiles.h"

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
static unsigned char out_of_band;

/* Owned here, not by the program. The contract asks a game to expose the
 * worst it ever missed, and a game that keeps that number itself gets it
 * wrong in ways nothing can see from outside: the run this rule comes from
 * had a program storing the maximum from *before* it drew its first screen,
 * and a sibling project stored the last cost rather than the worst. Neither
 * is visible to a gate reading one number. Keeping the maximum in here
 * leaves the program nothing to get wrong, and the linker map carries the
 * symbol either way. */
unsigned char g_worst_frame_cost;

/* The colour plat_cell and plat_text write in, until a program says otherwise
 * with plat_ink. White on black is what this library hardcoded at every call
 * site before a design's declared colours were read at all, so it stays the
 * default: a program that never mentions colour looks exactly as it did. */
static unsigned char ink = PAPER_BLACK | INK_WHITE;

unsigned char plat_ink(unsigned char attribute) {
    unsigned char previous = ink;
    ink = attribute;
    return previous;
}

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
    out_of_band = 0;
    g_worst_frame_cost = 0;
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
 * The residual blind spot, stated as narrowly as it can honestly be put: a
 * loop that overruns out of band for fewer than SLOW_RUN iterations and
 * then keeps pace reports nothing. That is the price of telling a startup
 * gap from a slow loop by how many times it repeats, and it is a smaller
 * price than the two rules this replaced -- a magnitude bound that
 * approved every program at or below 5 Hz, and a twice-in-a-row rule that
 * failed a correct program five times because building its first level
 * between the resynchronisation and the loop's first wait counted as the
 * second gap. Neither of those was visible until a real game was drawn: however badly the others drag: the gap says "the loop was not running", the
 * fast iteration after it says "carry on", and nothing between them remembers
 * that this is the tenth time. Two out-of-band iterations in a row are the
 * only thing that is ever reported. Nothing else in the pipeline sees the difference
 * either. That is a gap, not a backstop; closing it needs a counter of gaps
 * rather than a flag, and this library has no room to spare for one it has
 * not yet seen a program need.
 *
 * resources/studio_reference/spectrum/src/engine.c already carries this idea as
 * frame_cost_primed, with the same diagnosis in its comment -- "the first
 * sample after a level starts measures how long someone took to press a key,
 * not the work". But a free-written program never inherits the reference
 * engine, and the library is in every build; that is the gap this closes. */
#define RESYNC_FRAMES 8

/* Out-of-band gaps in a row before the counter believes the loop itself is
 * slow. Startup produces them in ones and twos -- a title screen polling
 * without pacing itself is one, and the level being built between that
 * resynchronisation and the loop's first wait is a second -- while a loop
 * that genuinely does not fit in its frame produces one every iteration,
 * for hundreds. Recurrence *count* separates those cleanly where neither
 * magnitude nor "twice in a row" could: the first end-to-end run of the
 * drafting pipeline was failed five times over by a correctly written
 * program whose two startup gaps were read as a slow loop.
 *
 * The residual blind spot, and it is smaller than what it replaces: a loop
 * slow for two or three iterations and then fast again reports nothing. */
#define SLOW_RUN 4


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
        /* A gap this large is not one iteration running long, and the counter
         * cannot tell an absent loop from a slow one by size. It waits to see
         * whether it repeats: below SLOW_RUN it is forgiven as a
         * resynchronisation, at SLOW_RUN it is reported as one frame past the
         * bound -- the smallest value that cannot be mistaken for keeping
         * pace. The true magnitude is never reported, because after a gap this
         * large it is not known to be one iteration's worth of anything. */
        if (out_of_band < 255) ++out_of_band;
        cost = out_of_band >= SLOW_RUN ? (unsigned char)(RESYNC_FRAMES + 1) : 0;
    } else {
        out_of_band = 0;
        cost = (unsigned char)missed;
    }
    if (cost > g_worst_frame_cost) {
        g_worst_frame_cost = cost;
    }
    while (FRAME_CLOCK == start && ++guard < 12000) {
    }
    frame_mark = FRAME_CLOCK;
    return cost;
}

/* How many gaps plat_frame_baseline will forgive in one run. A game changes
 * scene, paints a screen and leaves a menu a handful of times; a loop that
 * overruns does it every iteration, thousands of times, and runs out of
 * forgiveness immediately. Eight is generous for the first and useless for the
 * second, which is the only property that matters here. */
#define BASELINES_ALLOWED 8

static unsigned char baselines_left = BASELINES_ALLOWED;

void plat_frame_baseline(void) {
    if (baselines_left == 0) return;
    --baselines_left;
    /* Resynchronise and forget: the mark moves to now, so the next
     * plat_wait_frame measures its own iteration and not the work that came
     * before this call. out_of_band is cleared for the same reason -- a
     * startup gap must not count towards the "slow for SLOW_RUN iterations in
     * a row" evidence that reports a genuinely slow loop. g_worst_frame_cost
     * is deliberately left alone rather than reset: a loop that really did
     * overrun before this call keeps its number, and only the gap being
     * closed here goes uncharged. */
    frame_mark = FRAME_CLOCK;
    out_of_band = 0;
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
            put_glyph(col, row, ROM_FONT + (((unsigned int)(code - 32)) << 3), ink);
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
        put_glyph(col, row, blank, ink);
        return;
    }
    put_glyph(col, row, ROM_FONT + (((unsigned int)(code - 32)) << 3), ink);
}

/* Draws a tile's own eight bytes into a cell, in the colour its art resolved
 * to. This is put_glyph with the bitmap coming from tiles.c instead of the ROM
 * font -- deliberately the same shape, because a tile occupies exactly what a
 * character occupies, which is what makes terrain art a drop-in replacement
 * for the character a design's tile carries.
 *
 * tile_data[] is indexed with the tile number and nothing else: a tile has one
 * pose, so there is no frame offset to add and no multiply for SDCC to satisfy
 * out of a library built for the wrong ABI (see sprite_header.py). */
void plat_tile(unsigned char col, unsigned char row, unsigned char tile) {
#if TILE_COUNT
    if (tile >= TILE_COUNT) return;
    if (col >= 32 || row >= 24) return;
    put_glyph(col, row, tile_data[tile], tile_attribute[tile]);
#else
    (void)col; (void)row; (void)tile;
#endif
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

/* The same sprite, addressed by scanline.
 *
 * `zx_saddrpdown` is what makes this short. Stepping one *pixel* line down is
 * `+256` only while the line stays inside its character row; at the eighth it
 * wraps to the next character row, and at the sixty-fourth to the next screen
 * third, which is a different bank of the display file altogether. That is
 * the same non-linearity plat_sprite above dodges by converting afresh per
 * half; here there is no cell to convert from, so the library routine that
 * knows the layout does the stepping instead of arithmetic invented here.
 *
 * The guard is 176, not 191: the sprite is sixteen lines tall and the display
 * is 192, so 176 is the last row whose sprite ends on the screen. Past it
 * `zx_saddrpdown` would walk out of the display file and into whatever is
 * above it, which on a 48K is the attribute area and then the system
 * variables -- a corruption that shows up as the game dying, minutes later,
 * somewhere else entirely.
 *
 * Attributes: the covered rows are those of the first and last scanline,
 * `py >> 3` and `(py + 15) >> 3`, which is two rows when py is a multiple of
 * eight and three when it is not. Written as a loop over that range rather
 * than as the four fixed writes plat_sprite makes, because the count is not
 * fixed: a sprite between cells that coloured only its first two rows would
 * appear with its last third in whatever colour the background happened to
 * be. */
void plat_sprite_py(unsigned char col, unsigned char py, unsigned char sprite,
                    unsigned char frame) {
#if SPRITE_COUNT
    const unsigned char *data;
    const unsigned char *mask;
    unsigned char *at;
    unsigned char line;
    unsigned char row;
    unsigned char last;
    if (sprite >= SPRITE_COUNT) return;
    if (col > 30 || py > 176) return;
    data = sprite_data[sprite] + sprite_frame_offset[sprite][frame];
    mask = sprite_mask[sprite] + sprite_frame_offset[sprite][frame];
    at = (unsigned char *)zx_pxy2saddr((unsigned char)(col << 3), py);
    for (line = 0; line < 16; ++line) {
        at[0] = (unsigned char)((at[0] & *mask++) | *data++);
        at[1] = (unsigned char)((at[1] & *mask++) | *data++);
        at = (unsigned char *)zx_saddrpdown(at);
    }
    last = (unsigned char)((py + 15) >> 3);
    for (row = (unsigned char)(py >> 3); row <= last; ++row) {
        *(unsigned char *)zx_cxy2aaddr(col, row) = sprite_attribute[sprite];
        *(unsigned char *)zx_cxy2aaddr(col + 1, row) = sprite_attribute[sprite];
    }
#else
    (void)col; (void)py; (void)sprite; (void)frame;
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
