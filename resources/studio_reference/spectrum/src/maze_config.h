/* Constants this reference program owns.
 * Target facts and the names this design coined -- SCREEN_COUNT, FIELD_TOP,
 * INPUT_<NAME>, SOUND_<NAME> -- come from Studio's game_config.h instead. What
 * a life or a pellet is worth is not a fact about the machine and not a word
 * the schema knows, so it is stated here, by the program that means it.
 */
#ifndef MAZE_REFERENCE_CONFIG_H
#define MAZE_REFERENCE_CONFIG_H

#define MAX_ACTORS 10
#define MAX_LEVEL_HEIGHT 16
#define GUARD_WAKE_DISTANCE 5

#define START_LIVES 3
#define SCORE_PER_COLLECTIBLE 10

/* What kind each actor in g_actor_kind is. Nothing above this program has a
 * fixed word for "enemy" any more, so these are this design's own. */
#define KIND_PLAYER 1
#define KIND_ENEMY 2
#define KIND_COLLECTIBLE 3

/* The characters this game is drawn with. plat_cell puts one on screen; the
 * two terrain characters are the ones design.yml declares for its tiles. */
#define GLYPH_WALL '#'
#define GLYPH_FLOOR '.'
#define GLYPH_PLAYER '@'
#define GLYPH_ENEMY 'M'
#define GLYPH_COLLECTIBLE '*'

#endif
