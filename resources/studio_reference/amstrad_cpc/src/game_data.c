/* Reference program, maintained by hand. Not generated output. */
#include "engine.h"

const unsigned char g_actor_count = 10;
const unsigned char g_actor_kind[10] = {1, 2, 3, 3, 3, 3, 3, 3, 3, 3};
const unsigned char g_actor_speed[10] = {1, 1, 1, 1, 1, 1, 1, 1, 1, 1};
const unsigned char g_actor_behaviour[10] = {1, 2, 0, 0, 0, 0, 0, 0, 0, 0};
const unsigned char g_level_width[3] = {20, 20, 20};
const unsigned char g_level_height[3] = {16, 16, 16};
const unsigned char g_spawn_col[30] = {10, 1, 9, 18, 12, 3, 15, 7, 15, 10, 10, 8, 15, 10, 18, 12, 4, 16, 7, 18, 1, 16, 8, 1, 11, 2, 13, 6, 17, 7};
const unsigned char g_spawn_row[30] = {8, 1, 2, 3, 5, 7, 8, 10, 11, 13, 8, 1, 2, 4, 5, 7, 9, 10, 12, 13, 1, 1, 3, 5, 6, 8, 9, 11, 12, 14};
const unsigned char g_wall_bits[120] = {255, 255, 248, 0, 1, 128, 0, 24, 0, 1, 136, 136, 152, 0, 1, 128, 0, 24, 0, 1, 136, 136, 152, 0, 1, 128, 0, 24, 0, 1, 136, 136, 152, 0, 1, 128, 0, 31, 255, 255, 255, 255, 248, 0, 1, 128, 0, 25, 36, 145, 128, 0, 24, 0, 1, 146, 73, 24, 0, 1, 128, 0, 25, 36, 145, 128, 0, 24, 0, 1, 146, 73, 24, 0, 1, 128, 0, 31, 255, 255, 255, 255, 248, 0, 1, 132, 33, 24, 0, 1, 132, 33, 24, 0, 1, 132, 33, 24, 0, 1, 132, 33, 24, 0, 1, 132, 33, 24, 0, 1, 132, 33, 24, 0, 1, 128, 0, 31, 255, 255};
const unsigned int g_wall_offset[3] = {0, 40, 80};
const char g_title_text[] = "REFERENCE MAZE";
const char g_controls_text[] = "CURSORS MOVE";
