/* LLMZ80 Studio engine: target-independent gameplay runtime.
 *
 * Rules live here once. Targets only implement platform.h, and projects only
 * contribute the tables in game_data.c, so both machines run the same game.
 */
#include "platform.h"
#include "engine.h"
#include "game_state.h"
#include "game_config.h"
#include "maze_config.h"

static unsigned char a_col[MAX_ACTORS];
static unsigned char a_row[MAX_ACTORS];
static unsigned char a_alive[MAX_ACTORS];
static unsigned char a_tick[MAX_ACTORS];
static unsigned char a_dir[MAX_ACTORS];
static unsigned char a_dir_v[MAX_ACTORS];

/* Runtime probe contract: these five have external linkage on purpose so they
 * appear in the linker map and an emulator can read them from memory. Making
 * them static would hide the only observable proof that the rules ran. */
unsigned char g_level;
unsigned char g_lives;
unsigned char g_remaining;
unsigned int g_score;
/* Worst number of display frames a single game iteration has missed. Zero
 * means the loop always finished inside its frame. */
unsigned char g_worst_frame_cost;
/* Survives a game over on purpose: the high score is the reason to replay.
 * It cannot survive a power cycle, since neither target has storage here. */
unsigned int g_hiscore;
/* Which screen is showing: 0 title, 1 playing, 2 game over, 3 victory. */
unsigned char g_state;

static unsigned char player_index;
/* The menu loops poll without waiting on frames, so the first sample after a
 * level starts measures how long someone took to press a key, not the work.
 * It is discarded rather than reported as an overrun. */
static unsigned char frame_cost_primed;

/* No 16-bit division, modulo or multiplication anywhere in the engine: SDCC
 * satisfies them from library modules built for sdcccall(1), which the linker
 * rejects against CPCtelera's sdcccall(0) ABI. Repeated subtraction instead. */
void engine_format_number(unsigned int value, char *out) {
    static const unsigned int powers[5] = {10000, 1000, 100, 10, 1};
    unsigned char index;
    unsigned char digit;
    for (index = 0; index < 5; ++index) {
        digit = 0;
        while (value >= powers[index]) {
            value -= powers[index];
            ++digit;
        }
        out[index] = (char)('0' + digit);
    }
    out[5] = 0;
}

static void write_digit(unsigned char col, unsigned char row, unsigned char value) {
    char single[2];
    if (value > 9) value = 9;
    single[0] = (char)('0' + value);
    single[1] = 0;
    plat_text(col, row, single);
}

/* Level offset into the flat spawn tables, accumulated to avoid a 16-bit multiply. */
static unsigned int spawn_base(void) {
    unsigned int base = 0;
    unsigned char step;
    for (step = 1; step < g_level; ++step) base += g_actor_count;
    return base;
}

/* Bit index of the first cell of each row, rebuilt whenever a level loads.
 * This replaces the row * width multiply the wall lookup would otherwise need. */
static unsigned int row_bit[MAX_LEVEL_HEIGHT];
static unsigned int wall_byte_base;

static const unsigned char bit_mask[8] = {0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01};

static void index_rows(void) {
    unsigned char width = g_level_width[g_level - 1];
    unsigned char height = g_level_height[g_level - 1];
    unsigned char row;
    unsigned int cursor = 0;
    wall_byte_base = g_wall_offset[g_level - 1];
    for (row = 0; row < height; ++row) {
        row_bit[row] = cursor;
        cursor += width;
    }
}

static unsigned char is_wall(unsigned char col, unsigned char row) {
    unsigned int index = row_bit[row] + col;
    return (unsigned char)(
        g_wall_bits[wall_byte_base + (index >> 3)] & bit_mask[(unsigned char)index & 7]
    );
}

static void draw_hud(void) {
    char buffer[6];
    engine_format_number(g_score, buffer);
    plat_text(0, 0, "SCORE ");
    plat_text(6, 0, buffer);
    plat_text(0, 1, "LIVES   LEVEL");
    write_digit(6, 1, g_lives);
    write_digit(14, 1, g_level);
#if HAS_FRAME_CLOCK
    plat_text(12, 0, "LAG");
    write_digit(16, 0, g_worst_frame_cost);
#endif
}

/* Collectibles share cells with moving actors, so erasing must not lose them. */
static void restore_cell(unsigned char col, unsigned char row) {
    unsigned char index;
    if (is_wall(col, row)) {
        plat_cell(col, (unsigned char)(row + FIELD_TOP), GLYPH_WALL);
        return;
    }
    for (index = 0; index < g_actor_count; ++index) {
        if (a_alive[index] && g_actor_kind[index] == KIND_COLLECTIBLE
            && a_col[index] == col && a_row[index] == row) {
            plat_cell(col, (unsigned char)(row + FIELD_TOP), GLYPH_COLLECTIBLE);
            return;
        }
    }
    plat_cell(col, (unsigned char)(row + FIELD_TOP), GLYPH_FLOOR);
}

/* Later levels move faster: the design says the chase tightens, and this is
 * where this program decided that means one step of speed per level. */
static unsigned char actor_tick_limit(unsigned char index) {
    unsigned char speed = (unsigned char)(g_actor_speed[index] + g_level - 1);
    if (speed > 4) speed = 4;
    return (unsigned char)(5 - speed);
}

static void draw_terrain(void) {
    unsigned char width = g_level_width[g_level - 1];
    unsigned char height = g_level_height[g_level - 1];
    unsigned char row;
    unsigned char col;
    for (row = 0; row < height; ++row) {
        for (col = 0; col < width; ++col) {
            plat_cell(col, (unsigned char)(row + FIELD_TOP),
                      is_wall(col, row) ? GLYPH_WALL : GLYPH_FLOOR);
        }
    }
}

/* One character per kind of actor. g_actor_kind is this program's own
 * numbering, so this is the only place the two vocabularies meet. */
static char kind_glyph(unsigned char kind) {
    if (kind == KIND_PLAYER) return GLYPH_PLAYER;
    if (kind == KIND_ENEMY) return GLYPH_ENEMY;
    if (kind == KIND_COLLECTIBLE) return GLYPH_COLLECTIBLE;
    return GLYPH_FLOOR;
}

static void load_level(void) {
    unsigned int base;
    unsigned char index;
    plat_clear();
    draw_hud();
    index_rows();
    draw_terrain();
    g_remaining = 0;
    g_worst_frame_cost = 0;
    frame_cost_primed = 0;
    base = spawn_base();
    for (index = 0; index < g_actor_count; ++index) {
        a_col[index] = g_spawn_col[base + index];
        a_row[index] = g_spawn_row[base + index];
        a_alive[index] = 1;
        a_tick[index] = 0;
        a_dir[index] = 1;
        a_dir_v[index] = 1;
        if (g_actor_behaviour[index] == BEHAVIOUR_PLAYER) player_index = index;
        if (g_actor_kind[index] == KIND_COLLECTIBLE) ++g_remaining;
        plat_cell(a_col[index], (unsigned char)(a_row[index] + FIELD_TOP),
                  kind_glyph(g_actor_kind[index]));
    }
}

static void reset_game(void) {
    g_state = 1;
    g_score = 0;
    g_lives = START_LIVES;
    g_level = 1;
    load_level();
}

#define START_KEYS (INPUT_ACTION | INPUT_RIGHT)

/* Menus poll tightly rather than once per frame: a scripted emulator keypress
 * lasts only a few hundred milliseconds and a frame-gated poll can miss it. */
static void wait_for_release(void) {
    unsigned int guard = 0;
    while ((plat_input() & START_KEYS) && ++guard < 60000) {
    }
}

static void wait_for_press(void) {
    while (!(plat_input() & START_KEYS)) {
    }
}

static void banner(const char *first, const char *second) {
    char buffer[6];
    plat_clear();
    plat_text(1, 6, first);
    plat_text(1, 8, second);
    plat_text(1, 10, "SCORE ");
    engine_format_number(g_score, buffer);
    plat_text(7, 10, buffer);
    plat_text(1, 12, "PRESS ACTION");
    wait_for_release();
    wait_for_press();
}

/* Gameplay starts on key-down, not key-up, so the first rendered gameplay frame
 * arrives while an automated harness is still holding the scripted key. */
static void title_screen(void) {
    char hiscore[6];
    g_state = 0;
    plat_border(0);
    plat_clear();
    plat_text(1, 4, g_title_text);
    plat_text(1, 7, g_controls_text);
    plat_text(1, 9, "PRESS ACTION TO START");
    engine_format_number(g_hiscore, hiscore);
    plat_text(1, 11, "HISCORE ");
    plat_text(9, 11, hiscore);
    wait_for_release();
    wait_for_press();
}

static void collect_at(unsigned char col, unsigned char row) {
    unsigned char index;
    for (index = 0; index < g_actor_count; ++index) {
        if (a_alive[index] && g_actor_kind[index] == KIND_COLLECTIBLE
            && a_col[index] == col && a_row[index] == row) {
            a_alive[index] = 0;
            --g_remaining;
            g_score += SCORE_PER_COLLECTIBLE;
            if (g_score > g_hiscore) g_hiscore = g_score;
            plat_sound(SOUND_COLLECT);
            draw_hud();
        }
    }
}

static void move_player(void) {
    unsigned char keys = plat_input();
    unsigned char col = a_col[player_index];
    unsigned char row = a_row[player_index];
    unsigned char width = g_level_width[g_level - 1];
    unsigned char height = g_level_height[g_level - 1];

    if ((keys & INPUT_LEFT) && col > 0) --col;
    else if ((keys & INPUT_RIGHT) && col + 1 < width) ++col;
    if ((keys & INPUT_UP) && row > 0) --row;
    else if ((keys & INPUT_DOWN) && row + 1 < height) ++row;

    if (col == a_col[player_index] && row == a_row[player_index]) return;
    if (is_wall(col, row)) {
        /* Diagonal input into a wall corner still allows the free axis. */
        if (!is_wall(col, a_row[player_index])) row = a_row[player_index];
        else if (!is_wall(a_col[player_index], row)) col = a_col[player_index];
        else return;
        if (col == a_col[player_index] && row == a_row[player_index]) return;
    }
    restore_cell(a_col[player_index], a_row[player_index]);
    a_col[player_index] = col;
    a_row[player_index] = row;
    collect_at(col, row);
    plat_cell(col, (unsigned char)(row + FIELD_TOP), GLYPH_PLAYER);
}

/* Out of bounds counts as blocked. Unsigned wrap turns col - 1 at column zero
 * into 255, which fails the width test, so no separate underflow check. */
static unsigned char blocked(unsigned char col, unsigned char row) {
    if (col >= g_level_width[g_level - 1] || row >= g_level_height[g_level - 1]) return 1;
    return is_wall(col, row);
}

static unsigned char steps_apart(unsigned char first, unsigned char second) {
    return first > second ? (unsigned char)(first - second) : (unsigned char)(second - first);
}

/* One greedy step along the axis the player is furthest away on, falling back
 * to the other axis when the preferred one is walled. */
static void step_toward_player(unsigned char *col, unsigned char *row) {
    unsigned char player_col = a_col[player_index];
    unsigned char player_row = a_row[player_index];
    unsigned char apart_col = steps_apart(*col, player_col);
    unsigned char apart_row = steps_apart(*row, player_row);
    unsigned char try_col = *col;
    unsigned char try_row = *row;
    unsigned char prefer_col = apart_col >= apart_row;

    if (prefer_col) {
        if (player_col > *col) ++try_col; else if (player_col < *col) --try_col;
    } else {
        if (player_row > *row) ++try_row; else if (player_row < *row) --try_row;
    }
    if (!blocked(try_col, try_row)) {
        *col = try_col;
        *row = try_row;
        return;
    }
    try_col = *col;
    try_row = *row;
    if (prefer_col) {
        if (player_row > *row) ++try_row; else if (player_row < *row) --try_row;
    } else {
        if (player_col > *col) ++try_col; else if (player_col < *col) --try_col;
    }
    if (!blocked(try_col, try_row)) {
        *col = try_col;
        *row = try_row;
    }
}

static void patrol_axis(unsigned char *value, unsigned char *direction,
                        unsigned char col, unsigned char row, unsigned char horizontal) {
    unsigned char next = (unsigned char)(*direction ? *value + 1 : *value - 1);
    unsigned char try_col = horizontal ? next : col;
    unsigned char try_row = horizontal ? row : next;
    if (blocked(try_col, try_row)) {
        *direction = (unsigned char)(*direction ? 0 : 1);
        return;
    }
    *value = next;
}

/* Returns 1 when the player lost a life this frame. */
static unsigned char move_enemies(void) {
    unsigned char index;
    unsigned char behaviour;
    unsigned char col;
    unsigned char row;

    for (index = 0; index < g_actor_count; ++index) {
        behaviour = g_actor_behaviour[index];
        if (!a_alive[index]) continue;
        if (behaviour < BEHAVIOUR_PATROL_H) continue;
        if (++a_tick[index] < actor_tick_limit(index)) continue;
        a_tick[index] = 0;
        col = a_col[index];
        row = a_row[index];
        if (behaviour == BEHAVIOUR_PATROL_H) {
            patrol_axis(&col, &a_dir[index], col, row, 1);
        } else if (behaviour == BEHAVIOUR_PATROL_V) {
            patrol_axis(&row, &a_dir[index], col, row, 0);
        } else if (behaviour == BEHAVIOUR_BOUNCE) {
            patrol_axis(&col, &a_dir[index], col, row, 1);
            patrol_axis(&row, &a_dir_v[index], col, row, 0);
        } else if (behaviour == BEHAVIOUR_CHASE) {
            step_toward_player(&col, &row);
        } else if (behaviour == BEHAVIOUR_GUARD) {
            if (steps_apart(col, a_col[player_index]) + steps_apart(row, a_row[player_index])
                <= GUARD_WAKE_DISTANCE) {
                step_toward_player(&col, &row);
            }
        }
        if (col == a_col[index] && row == a_row[index]) continue;
        restore_cell(a_col[index], a_row[index]);
        a_col[index] = col;
        a_row[index] = row;
        plat_cell(col, (unsigned char)(row + FIELD_TOP), GLYPH_ENEMY);
        if (col == a_col[player_index] && row == a_row[player_index]) return 1;
    }
    return 0;
}

void engine_run(void) {
    unsigned char cost;
    /* Assigned here, not at declaration: the CPC link leaves the data segment
     * uninitialised, so a declaration initialiser would be whatever was in RAM. */
    g_hiscore = 0;
    plat_init();
    title_screen();
    plat_sound(SOUND_START);
    reset_game();
    while (1) {
        move_player();
        if (move_enemies()) {
            plat_sound(SOUND_HIT);
            if (g_lives > 0) --g_lives;
            if (g_lives == 0) {
                plat_border(2);
                g_state = 2;
                plat_sound(SOUND_GAME_OVER);
                banner("GAME OVER", g_title_text);
                plat_border(0);
                title_screen();
                reset_game();
            } else {
                load_level();
            }
        } else if (g_remaining == 0) {
            if (g_level < SCREEN_COUNT) {
                ++g_level;
                plat_sound(SOUND_LEVEL);
                banner("LEVEL COMPLETE", "GET READY");
                load_level();
            } else {
                g_state = 3;
                banner("YOU WIN", g_title_text);
                title_screen();
                reset_game();
            }
        }
        cost = plat_wait_frame();
        if (!frame_cost_primed) {
            frame_cost_primed = 1;
        } else if (cost > g_worst_frame_cost) {
            g_worst_frame_cost = cost;
            draw_hud();
        }
    }
}
