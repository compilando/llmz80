/* LLMZ80 Studio engine: platform abstraction.
 *
 * Every target implements this header. The shared engine never touches target
 * headers, so gameplay rules stay identical on ZX Spectrum and Amstrad CPC.
 * Types are plain C so the header compiles under z88dk/sdcc and SDCC alike.
 */
#ifndef LLMZ80_PLATFORM_H
#define LLMZ80_PLATFORM_H

/* Input is one bit per binding the design declared. game_config.h names each
 * bit (INPUT_LEFT, INPUT_JUMP, whatever the design coined) and lists them all
 * in the INPUT_BINDINGS X-macro, so this header fixes no key and no meaning. */
void plat_init(void);
void plat_clear(void);
/* Waits for the next display frame and returns how many whole display frames
 * elapsed while the previous iteration did its work. Zero means the work fitted
 * inside its frame; anything higher counts frames the loop missed.
 *
 * The cost is measured between consecutive calls, so a loop that never calls
 * this charges its whole duration to whoever calls next. Menus must still poll
 * in a tight loop -- a frame-gated poll can miss a short scripted keypress --
 * so the way to satisfy both is to call this once as you leave such a loop and
 * ignore what it returns: that resynchronises the measurement before the
 * gameplay loop takes its first reading, and costs one frame at a screen
 * transition. Targets with no free-running frame clock always return zero, and
 * game_config.h reports which is which through HAS_FRAME_CLOCK. */
unsigned char plat_wait_frame(void);

/* Starts the frame measurement afresh, charging nobody for the gap that just
 * closed. Call it after work that is not an iteration of the game loop:
 * painting a screen when a level or a scene starts, or leaving a menu that
 * polled tightly for a key.
 *
 * This is what makes the advice above have an effect. Ignoring what
 * plat_wait_frame returns does not undo the number it already wrote into
 * g_worst_frame_cost, and that number is a maximum kept for the whole
 * session -- so a screen that took six frames to paint used to read, forever
 * after, as a game loop that missed six frames. Ten consecutive program
 * attempts were failed by exactly that, each one reading its worst cost at
 * the step where its title screen handed over to the game and never at any
 * later step.
 *
 * It is not a way to hide a slow loop: only a few gaps per run are forgiven
 * (see the counter in each platform.c), which is enough for scene changes and
 * menus and far too few for a loop that overruns every iteration. */
void plat_frame_baseline(void);
unsigned char plat_input(void);
void plat_text(unsigned char col, unsigned char row, const char *text);
/* Draws one character of the ROM font at a character cell, in the current ink
 * (see plat_ink). This is how terrain whose tile has no artwork is drawn: the
 * design's tile carries a character, and this puts it on screen. A tile that
 * *has* artwork is drawn with plat_tile below, and looks like terrain rather
 * than like a letter. */
void plat_cell(unsigned char col, unsigned char row, char glyph);
void plat_border(unsigned char colour);

/* Draws one 8x8 block of the design's own terrain artwork into the character
 * cell at (col, row), in the colour that tile's art resolved to. Tiles come
 * from tiles.h, which Studio generates beside your sources: it defines a
 * TILE_<ID> for every tile the design gave art to, and TILE_COUNT is zero when
 * it gave none -- and then this does nothing, so terrain falls back to
 * plat_cell.
 *
 * Unlike plat_sprite this covers exactly one cell, because a tile is what a
 * cell *is* rather than something drawn over it: there is no mask, and the
 * whole cell is replaced. */
void plat_tile(unsigned char col, unsigned char row, unsigned char tile);

/* Sets the colour every later plat_cell and plat_text writes in, and returns
 * what it was, so a caller can put it back. The value is one target attribute
 * byte; game_config.h defines COLOUR_<ID> for each colour the design's palette
 * named, so a program says plat_ink(COLOUR_LADRILLO) rather than picking a
 * number. Until something calls this, cells and text are drawn in the
 * library's own default (white on black), which is what every program got
 * before a design's colours were read at all. */
unsigned char plat_ink(unsigned char attribute);

/* Draws one 16x16 masked sprite whose top-left corner sits at character cell
 * (col, row), so it covers two cells each way. Sprites come from sprites.h,
 * which Studio generates beside your sources; SPRITE_COUNT is zero when the
 * design carries no artwork, and then this does nothing. */
void plat_sprite(unsigned char col, unsigned char row, unsigned char sprite,
                 unsigned char frame);

/* The same sprite, at a pixel row instead of a character row: `py` is a
 * scanline, so `py` and `py + 1` are one pixel apart rather than eight. The
 * column is still a character column -- moving by less than one byte across
 * needs a differently shifted copy of the sprite, which is a different piece
 * of work with a real memory cost, and this one has none.
 *
 * Use it for anything a player watches move down or up: a jump, a fall, a
 * lift, a ball. Use plat_sprite above for anything that sits on the grid --
 * it is cheaper, and a thing that only ever appears in cells looks no better
 * for being drawn through the slower path.
 *
 * Two costs to know about, both on the Spectrum and neither fatal:
 *
 * A sprite at a row that is not a multiple of eight covers three character
 * rows rather than two, so it takes six attribute cells rather than four, and
 * the two extra cells take the sprite's colour away from whatever was behind
 * them. On a machine with one colour per cell that is the price of smooth
 * vertical movement, and it is the same price every commercial game of the
 * era paid.
 *
 * It is also slower than plat_sprite -- the address of each pixel line has to
 * be stepped rather than derived by adding 256 -- so a program that moves
 * many sprites this way should watch what plat_wait_frame reports.
 *
 * Erasing is the program's business either way, and a little more work here:
 * the rows to repaint are the three the sprite covered, not two.
 *
 * `py` is bounded by the screen, not by the playfield: 0 to 176 on the
 * Spectrum (192 lines less the sprite's 16) and 0 to 184 on the CPC. Out of
 * range draws nothing rather than writing past the screen. */
void plat_sprite_py(unsigned char col, unsigned char py, unsigned char sprite,
                    unsigned char frame);

/* Plays effect N, where N is the index the design gave it -- game_config.h
 * defines SOUND_<NAME> for each one it declared. What each index sounds like
 * is this library's business; what it is called is the design's. A target
 * with no audio implements this as a no-op, and the design gate refuses a
 * project that asks a silent machine for sound. */
void plat_sound(unsigned char effect);

#endif
