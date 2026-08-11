/* LLMZ80 Studio engine: shared gameplay runtime.
 *
 * This file is versioned engine source, not generated output. Everything that
 * varies per project lives in the generated game_config.h and game_data.c.
 */
#ifndef LLMZ80_ENGINE_H
#define LLMZ80_ENGINE_H

#define BEHAVIOUR_STATIC 0
#define BEHAVIOUR_PLAYER 1
#define BEHAVIOUR_PATROL_H 2
#define BEHAVIOUR_PATROL_V 3
#define BEHAVIOUR_BOUNCE 4
#define BEHAVIOUR_CHASE 5
#define BEHAVIOUR_GUARD 6

/* Generated data contract. game_data.c defines every symbol below. */
extern const unsigned char g_actor_count;
extern const unsigned char g_actor_kind[];
extern const unsigned char g_actor_speed[];
extern const unsigned char g_actor_behaviour[];
extern const unsigned char g_level_width[];
extern const unsigned char g_level_height[];
extern const unsigned char g_spawn_col[];
extern const unsigned char g_spawn_row[];
/* One bit per cell, row-major and MSB first; g_wall_offset indexes each level. */
extern const unsigned char g_wall_bits[];
extern const unsigned int g_wall_offset[];
extern const char g_title_text[];
extern const char g_controls_text[];

/* Runtime probe contract. These have external linkage so they land in the
 * linker map and an emulator can read them straight out of memory, which is
 * how the runtime gate proves the rules ran rather than inferring it from
 * pixels. Renaming one breaks probes.json; treat them as public API. */
extern unsigned char g_level;
extern unsigned char g_lives;
extern unsigned char g_remaining;
extern unsigned int g_score;
extern unsigned char g_worst_frame_cost;
extern unsigned int g_hiscore;
extern unsigned char g_state;

void engine_run(void);
void engine_format_number(unsigned int value, char *out);

#endif
