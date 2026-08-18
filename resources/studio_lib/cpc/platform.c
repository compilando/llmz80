/* Amstrad CPC implementation of the Studio engine platform layer.
 *
 * Cells are one 8x8 character block wide, so the engine grid maps directly to
 * CPCtelera's screen pointer arithmetic in both mode 0 and mode 1.
 */
#include <cpctelera.h>

#include "platform.h"
#include "game_config.h"
#include "sprites.h"
#include "tiles.h"

#if CPC_MODE == 0
#define CELL_BYTES 4
#define draw_string cpct_drawStringM0
#define set_draw_char cpct_setDrawCharM0
#else
#define CELL_BYTES 2
#define draw_string cpct_drawStringM1
#define set_draw_char cpct_setDrawCharM1
#endif

/* The pens this design's video mode uses, set explicitly so the result does
 * not depend on whichever palette the firmware left behind.
 *
 * CPC_PEN_COUNT and CPC_PALETTE_PENS come from game_config.h, which Studio
 * writes from `llmz80.studio.palette.HARDWARE_COLOURS` -- the same table the
 * sprite and tile packers quantise pixels against. That is the point of them
 * arriving from there rather than being written out here: the two used to be
 * stated separately and had drifted, with HW_BLUE recorded on the Python side
 * as (0, 0, 255) (which is HW_BRIGHT_BLUE) and HW_WHITE as (255, 255, 255)
 * (which is HW_BRIGHT_WHITE -- the CPC's "white" is grey). Half the palette
 * was quantised against colours this function never programmed.
 *
 * Sixteen pens in mode 0 and four in mode 1, which is what the pen's bit width
 * allows. Four was programmed in both until now, so mode 0's colours -- the
 * only reason to choose it over mode 1 -- were unreachable.
 *
 * Built on the stack on purpose. A file-scope initialised array lands in the
 * DATA segment, which this link does not initialise at run time, and a const
 * array would need a cast that raises SDCC warning 357. Either way the palette
 * would be filled with whatever happened to be in memory. The same hazard the
 * frame clock's `baselines_left` was caught by, one function down. */
/* The pen every later plat_cell and plat_text is drawn in, tracked so
 * plat_ink can hand back what it was. Declared here rather than beside
 * plat_ink because plat_init assigns it and comes first; see plat_ink for why
 * it carries no initialiser. */
static u8 draw_pen;

static void apply_palette(void) {
    u8 palette[CPC_PEN_COUNT] = { CPC_PALETTE_PENS };
    cpct_setPalette(palette, CPC_PEN_COUNT);
}

/* ---- the frame clock -------------------------------------------------
 *
 * The CPC has no ROM frame counter to read the way the Spectrum reads 23672,
 * and `cpct_disableFirmware()` above is what removes the firmware's own. So
 * this builds one. The CPC raises an interrupt 300 times a second -- six per
 * 50 Hz display frame -- and `cpct_setInterruptHandler` installs a handler it
 * calls each time, with every register saved by CPCtelera's own wrapper
 * (see ~/cpctelera/cpctelera/src/firmware/cpct_setInterruptHandler.s), so an
 * ordinary C function is safe here. Counting the sixths gives exactly the
 * free-running counter the other machine gets for nothing.
 *
 * This is what `pacing.pacing_report` used to abstain for. Its comment said
 * "writing a frame counter for the CPC is real work; until it exists, silence
 * is the honest reading", and it was right to abstain: `plat_wait_frame`
 * returned a literal zero, and a gate reading that zero as a game keeping
 * perfect time would have cleared every CPC program ever built. Now the two
 * machines run the same measurement, `codegen.has_frame_clock` says so for
 * both, and the gate judges both.
 *
 * Everything below this point mirrors `spectrum/platform.c` deliberately,
 * constant for constant, because two machines reporting the same number
 * differently is worse than either reporting nothing. The comments there
 * carry the reasoning for RESYNC_FRAMES, SLOW_RUN and BASELINES_ALLOWED, and
 * are not repeated here; what follows notes only where the CPC differs. */

/* Interrupts per display frame on this machine. The CPC's interrupt is at
 * 300 Hz and the display is 50 Hz. Not a tunable. */
#define INTERRUPTS_PER_FRAME 6

/* Whole frames since plat_init. `volatile` because the interrupt handler is
 * the only writer and every reader is outside it; without it SDCC is free to
 * hoist the read out of the wait loop below and spin forever.
 *
 * Read with interrupts left alone rather than disabled around the read. A
 * 16-bit read is two instructions on a Z80 and an interrupt landing between
 * them can tear the value -- but the interrupt increments this only once every
 * six firings, the torn value can only ever be off by the one increment being
 * written, and one frame of error in a counter whose gate tolerates one missed
 * frame is beneath the resolution of the thing being measured. Disabling
 * interrupts around it would cost more than the error it removes. */
static volatile unsigned int frame_clock;

/* Interrupts seen inside the current frame, 0..5. Only the handler touches
 * it. */
static unsigned char interrupt_tick;

static void count_frame(void) {
    if (++interrupt_tick >= INTERRUPTS_PER_FRAME) {
        interrupt_tick = 0;
        ++frame_clock;
    }
}

/* The counter as the last wait left it, and whether that wait already saw an
 * out-of-band gap. Both exactly as on the Spectrum. */
static unsigned int frame_mark;
static unsigned char out_of_band;

/* Defined here, as on the Spectrum, so the linker map carries the contract
 * symbol on both machines and no program has to keep the number itself. */
unsigned char g_worst_frame_cost;

#define RESYNC_FRAMES 8
#define SLOW_RUN 4

/* Waits for the next frame and returns what the previous iteration cost.
 *
 * The wait itself is `cpct_waitVSYNC()` rather than a spin on `frame_clock`,
 * for two reasons. It is what this function already did, and it synchronises
 * on the display rather than on our own count, which is the thing a program
 * drawing to the screen actually wants. The counter is only ever asked how
 * much time passed, never asked to end the wait, so a stopped interrupt makes
 * the *measurement* useless without making the *wait* hang -- the opposite of
 * the Spectrum, where the ROM counter drives both and the guard loop exists
 * because of it. */
unsigned char plat_wait_frame(void) {
    unsigned int start = frame_clock;
    unsigned int elapsed = (unsigned int)(start - frame_mark);
    unsigned int missed = elapsed > 1 ? (unsigned int)(elapsed - 1) : 0;
    unsigned char cost;
    if (missed > RESYNC_FRAMES) {
        if (out_of_band < 255) ++out_of_band;
        cost = out_of_band >= SLOW_RUN ? (unsigned char)(RESYNC_FRAMES + 1) : 0;
    } else {
        out_of_band = 0;
        cost = (unsigned char)missed;
    }
    if (cost > g_worst_frame_cost) {
        g_worst_frame_cost = cost;
    }
    cpct_waitVSYNC();
    frame_mark = frame_clock;
    return cost;
}

#define BASELINES_ALLOWED 8

/* Not initialised here, unlike the Spectrum's copy of the same counter.
 *
 * `apply_palette` above already records why: a file-scope initialised value
 * lands in the DATA segment, and this link does not initialise that segment at
 * run time, so the variable holds whatever was in memory. Measured on a real
 * CPC before this was moved into `plat_init`: it came up zero, every call to
 * `plat_frame_baseline` returned immediately, and a program that called it
 * read the same `g_worst_frame_cost` of 2 as one that did not -- the baseline
 * silently did nothing at all, on a machine where the counter it exists to
 * reset had only just started working.
 *
 * The same hazard applies to every other piece of state in this file, which is
 * why `frame_clock`, `interrupt_tick`, `frame_mark`, `out_of_band` and
 * `g_worst_frame_cost` are all assigned in `plat_init` rather than declared
 * with an initialiser. Zero-initialisation is not available here. */
static unsigned char baselines_left;

/* Resynchronise and forget, as on the Spectrum: the mark moves to now so the
 * next wait measures its own iteration, `out_of_band` is cleared so a startup
 * gap does not count towards the evidence for a genuinely slow loop, and
 * `g_worst_frame_cost` is deliberately left alone. */
void plat_frame_baseline(void) {
    if (baselines_left == 0) return;
    --baselines_left;
    frame_mark = frame_clock;
    out_of_band = 0;
}

void plat_init(void) {
    cpct_disableFirmware();
    cpct_setVideoMode(CPC_MODE);
    apply_palette();
    cpct_setBorder(HW_BLACK);
    cpct_clearScreen(0x00);
    /* The pen text is drawn in, and the matching `draw_pen` it is tracked by.
     * Both assigned here rather than at file scope: an initialised static
     * lands in the DATA segment, which this link does not initialise, so
     * `draw_pen` came up holding whatever was in memory and the first
     * `plat_ink` call reported a previous pen the program had never set.
     * The last pen is the brightest in both modes' palettes, which is the
     * white-on-black default a program that never mentions colour had before
     * a design's colours were read at all. */
    draw_pen = CPC_PEN_COUNT - 1;
    set_draw_char(draw_pen, 0);
    /* The frame clock, started here for the same reason the Spectrum's
     * plat_init calls intrinsic_ei() and seeds frame_mark: a counter nobody
     * started reads zero forever, and a mark left at zero makes the first
     * wait of a run subtract from a counter that has been advancing since
     * plat_init and report a cost the program never paid. */
    interrupt_tick = 0;
    frame_clock = 0;
    frame_mark = 0;
    out_of_band = 0;
    g_worst_frame_cost = 0;
    baselines_left = BASELINES_ALLOWED;
    cpct_setInterruptHandler(count_frame);
}

void plat_clear(void) {
    cpct_clearScreen(0x00);
}

void plat_border(unsigned char colour) {
    cpct_setBorder(colour == 2 ? HW_RED : HW_BLACK);
}

unsigned char plat_input(void) {
    unsigned char keys = 0;
    cpct_scanKeyboard_f();
#define X(bit, code) if (cpct_isKeyPressed(code)) keys |= bit;
    INPUT_BINDINGS(X)
#undef X
    return keys;
}

void plat_text(unsigned char col, unsigned char row, const char *text) {
    u8 *screen = cpct_getScreenPtr(CPCT_VMEM_START, (u8)(col * CELL_BYTES), (u8)(row * 8));
    draw_string((void *)text, screen);
}

/* Reuses the proven text path rather than a second glyph blitter: one
 * character, drawn where a cell is. */
void plat_cell(unsigned char col, unsigned char row, char glyph) {
    char text[2];
    if (col >= (80 / CELL_BYTES) || row >= 25) return;
    text[0] = glyph;
    text[1] = 0;
    plat_text(col, row, text);
}

/* The pen characters and text are drawn in. Colour on this machine is a pen
 * per pixel rather than an attribute per cell, so "the current ink" is the
 * foreground pen cpct_setDrawCharM* is told to use, and switching it is a call
 * to that same setter -- not a byte kept here and applied later. Pen 3 (white
 * in apply_palette's four) is what plat_init already set, so a program that
 * never calls this looks exactly as it did.
 *
 * The attribute a Spectrum program passes is accepted unchanged and read as a
 * pen index, because that is what `palette.declared_attribute` hands back on
 * this target: COLOUR_<ID> is a pen here and an attribute byte there, and the
 * program says plat_ink(COLOUR_LADRILLO) on both. Anything outside the pens
 * this mode programs is ignored rather than set, since cpct_setDrawCharM*
 * would encode the low bits of a bad index into a colour nobody chose.
 *
 * The bound is CPC_PEN_COUNT rather than a literal 4. It was 4 in both modes,
 * so a mode 0 design naming its twelfth colour had the call silently do
 * nothing and drew in whatever pen was current. */
unsigned char plat_ink(unsigned char attribute) {
    u8 previous = draw_pen;
    if (attribute < CPC_PEN_COUNT) {
        draw_pen = attribute;
        set_draw_char(draw_pen, 0);
    }
    return previous;
}

/* Draws a tile's own 8x8 block into one cell, through the *unmasked*
 * cpct_drawSprite (~/cpctelera/cpctelera/src/sprites/cpct_drawSprite.asm).
 * Unmasked is the point: terrain is the background, so there is nothing to
 * keep and no mask to interleave -- which also makes a tile half the bytes a
 * masked one would be.
 *
 * Bounds guard: one cell wide and one cell tall, so unlike plat_sprite the
 * last legal column is (80 / CELL_BYTES) - 1 and the last legal row is 24.
 * The crossing arithmetic plat_sprite's comment describes does not arise at
 * all here: eight pixel lines starting at a character row boundary stay inside
 * one 8-line block, which is exactly one cpct_getScreenPtr result plus the
 * callee's own per-line stepping.
 *
 * TILE_BYTES_WIDE is CELL_BYTES by construction (spriting.pack_cpc_tile packs
 * 8 pixels at the mode's pixels per byte, and a cell is 8 pixels), so the
 * width passed is the tile's real byte width and not an assumption. */
void plat_tile(unsigned char col, unsigned char row, unsigned char tile) {
#if TILE_COUNT
    u8 *screen;
    if (tile >= TILE_COUNT) return;
    if (col >= (80 / CELL_BYTES) || row >= 25) return;
    screen = cpct_getScreenPtr(CPCT_VMEM_START, (u8)(col * CELL_BYTES), (u8)(row * 8));
    cpct_drawSprite((void *)tile_data[tile], screen, TILE_BYTES_WIDE, TILE_HEIGHT);
#else
    (void)col; (void)row; (void)tile;
#endif
}

/* The CPC target declares no audio, so this is deliberately silent. The design
 * gate refuses any project that asks this machine for sound, which is why a
 * no-op here can never lose an effect the designer expected to hear. */
void plat_sound(unsigned char effect) {
    (void)effect;
}

/* Draws one 16x16 masked sprite as two rows of two cells, through
 * cpct_drawSpriteMasked (~/cpctelera/cpctelera/src/sprites/cpct_drawSpriteMasked.asm).
 *
 * Vertical boundary crossing: the CPC screen is laid out in eight interleaved
 * 8-pixel-line blocks per character row (cpct_getScreenPtr's own formula,
 * screen_start + 80*(y/8) + 2048*(y%8) + x -- see cpct_getScreenPtr.asm's
 * Details section), so a naive `address += stride` per pixel line is wrong
 * once a sprite's second half starts a new character row. That crossing is
 * *not* this function's job to get right: cpct_drawSpriteMasked.asm's own
 * per-line loop (labels dms_sprite_height_loop..dms_sprite_8bit_boundary_crossed,
 * lines ~161-186) already detects it -- `and #0x38` on the recomputed high
 * byte catches every 8th line -- and repoints DE by adding 0xC050 (three
 * banks forward, i.e. one bank back plus 0x50) to land on the next
 * character row. One cpct_getScreenPtr call up front is therefore enough;
 * no fresh call is needed per half the way the Spectrum blitter needs one
 * per third.
 *
 * What the callee will *not* do (documented directly above that loop, under
 * "Known limitations" in the same .asm): no boundary check or clipping
 * against the edge of video memory, and the crossing math it does do only
 * ever steps forward through the current 16K bank -- it never wraps back to
 * row 0. A sprite whose bottom half would fall past the last character row
 * corrupts whatever memory follows the screen instead of failing loudly, so
 * the guard below refuses that case rather than trust the call site.
 *
 * Bounds guard: the sprite is 2 cells wide and 2 cells tall. A row of cells
 * is 80 bytes wide regardless of mode (mode 0: 20 cells * 4 bytes; mode 1:
 * 40 cells * 2 bytes -- both 80), so the last column a 2-cell sprite can
 * start at is (80 / CELL_BYTES) - 2, i.e. col must be < (80 / CELL_BYTES) - 1.
 * The screen is 25 character rows (200 pixel lines / 8) with no third
 * boundary of its own -- unlike the Spectrum, one bank covers the whole
 * screen -- so the last row a 2-cell-tall sprite can start at is 23, i.e.
 * row must be < 24.
 *
 * Alignment/size: cpct_drawSpriteMasked only requires whole-byte width and a
 * byte-aligned destination (same doc, "As this function receives a
 * byte-pointer to memory..."). Both hold here for free: col*CELL_BYTES is
 * always a whole number of bytes because CELL_BYTES is the byte width of one
 * cell, and SPRITE_BYTES_WIDE (8 in mode 0, 4 in mode 1) is already the
 * sprite's width in whole bytes, not pixels. */
void plat_sprite(unsigned char col, unsigned char row, unsigned char sprite,
                 unsigned char frame) {
    plat_sprite_py(col, (unsigned char)(row * 8), sprite, frame);
}

/* The same sprite, addressed by scanline -- and on this machine that is what
 * the toolchain wanted all along.
 *
 * `cpct_getScreenPtr`'s third argument has always been a pixel line: its own
 * formula is screen_start + 80*(y/8) + 2048*(y%8) + x, with y in scanlines
 * (cpct_getScreenPtr.asm, Details). `plat_sprite` was passing `row * 8` and
 * throwing that away, so the whole cost of vertical movement here is not
 * multiplying. The interleaved-block crossing that makes the arithmetic look
 * frightening is handled by the callee either way: cpct_drawSpriteMasked.asm's
 * per-line loop detects every eighth line with `and #0x38` and repoints DE,
 * whatever line it started on.
 *
 * There is no attribute work to do, unlike the Spectrum: colour on this
 * machine lives in the pixel bytes, so a sprite straddling three character
 * rows costs exactly what one straddling two costs.
 *
 * The guard is 184, not 199: the sprite is sixteen lines tall and the display
 * is 200. Past it the callee, which does no bounds checking of its own (same
 * file, "Known limitations"), would step forward through the bank and
 * corrupt whatever follows the screen. */
void plat_sprite_py(unsigned char col, unsigned char py, unsigned char sprite,
                    unsigned char frame) {
#if SPRITE_COUNT
    u8 *screen;
    const u8 *bytes;
    if (sprite >= SPRITE_COUNT) return;
    if (col >= (80 / CELL_BYTES) - 1 || py > 184) return;
    screen = cpct_getScreenPtr(CPCT_VMEM_START, (u8)(col * CELL_BYTES), py);
    bytes = sprite_data[sprite] + sprite_frame_offset[sprite][frame];
    /* SPRITE_BYTES_WIDE is 8 in mode 0 and 4 in mode 1: sixteen pixels across,
     * at the mode's pixels per byte. The mask travels interleaved inside the
     * data, which is what cpct_drawSpriteMasked expects. */
    cpct_drawSpriteMasked((void *)bytes, screen, SPRITE_BYTES_WIDE, 16);
#else
    (void)col; (void)py; (void)sprite; (void)frame;
#endif
}


/* The same sprite at a pixel column. See the Spectrum copy of this function
 * for why the shifting happened in Python and not here; the arithmetic is
 * identical, and deliberately so -- the two machines differ in how many pixels
 * a byte holds and in nothing else this cares about.
 *
 * What differs: `cpct_getScreenPtr` wants a byte offset into the row, which is
 * what `px >> PIXELS_PER_BYTE_LOG` already is, so unlike every other function
 * in this file there is no multiply by CELL_BYTES -- a character cell is two
 * bytes in mode 1 and four in mode 0, but a byte is a byte. And there are no
 * attributes to write, because colour here lives in the pixels. */
void plat_sprite_px(unsigned int px, unsigned char py, unsigned char sprite,
                    unsigned char frame) {
#if SPRITE_COUNT
    u8 *screen;
    const u8 *bytes;
    unsigned char col;
    unsigned int block;
    if (sprite >= SPRITE_COUNT) return;
    if (px > MAX_SPRITE_PX || py > MAX_SPRITE_PY) return;
    col = (unsigned char)(px >> PIXELS_PER_BYTE_LOG);
    block = (unsigned int)(px & (PIXELS_PER_BYTE - 1) & (SPRITE_SHIFTS - 1))
            * SPRITE_SHIFT_STRIDE;
    screen = cpct_getScreenPtr(CPCT_VMEM_START, col, py);
    bytes = sprite_data[sprite] + sprite_frame_offset[sprite][frame] + block;
    cpct_drawSpriteMasked((void *)bytes, screen, SPRITE_BYTES_WIDE, 16);
#else
    (void)px; (void)py; (void)sprite; (void)frame;
#endif
}

/* Moves the picture by telling the CRTC where to start reading.
 *
 * `cpct_setVideoMemoryOffset` writes R13, and one unit of it is two bytes --
 * measured on a real machine, because CPCtelera's own examples disagree:
 * `advanced/hwscroll` comments "4-by-4 bytes" and `advanced/tilemap_hwscroll`
 * moves its software pointer by two for the same unit. A bar exactly one byte
 * wide, captured at offsets 0, 1 and 2, moved 2.00 and 4.00 bar-widths. The
 * tilemap example is right, which is what one would expect of the one whose
 * arithmetic has to line up with the hardware to work at all.
 *
 * Forty of those units is 80 bytes, one screen row, and moves the picture up
 * by exactly one character row -- also measured, with a full-width bar at
 * offsets 0, 40 and 80.
 *
 * So the offset is `origin / 2`, written as a shift: SDCC would satisfy the
 * division from its own routine, and this link refuses a routine built for the
 * other --sdcccall ABI (see sprite_header.py).
 *
 * Out of range is ignored rather than wrapped. R13 holds eight bits, so an
 * origin past MAX_SCROLL_ORIGIN would silently come back round to the start of
 * the screen: a scroller that did that would not look broken, it would look
 * like it jumped, which is the harder thing to diagnose. */
void plat_scroll_to(unsigned int origin) {
    if (origin > MAX_SCROLL_ORIGIN) return;
    cpct_setVideoMemoryOffset((u8)(origin >> 1));
}
