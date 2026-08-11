/* Constants this reference program owns.
 * Design constants come from Studio's game_config.h instead, so a change
 * to lives or scoring in game.yml still reaches the program. */
#ifndef MAZE_REFERENCE_CONFIG_H
#define MAZE_REFERENCE_CONFIG_H

#define MAX_ACTORS 10
#define MAX_LEVEL_HEIGHT 16
#define GUARD_WAKE_DISTANCE 5
/* One bit per effect, in AUDIO_EFFECTS order; zero means the design is silent. */
/* Only targets with a free-running frame clock can report frame overruns. */

#endif
