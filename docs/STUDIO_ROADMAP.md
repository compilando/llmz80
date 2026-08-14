# LLMZ80 Studio delivery roadmap

This is the durable execution record for the project-first guided game creator. A stage is only
marked complete when its acceptance evidence exists in the repository or test output.

## Direction change, 2026-08-14 — the IR stops deciding what a game is

Phase 1 of the v4 cut is in. The IR no longer fixes the vocabulary of every
game. `tiles` carry a `char` and free `traits`, `entities` carry a `kind` the
design coins for itself, `mechanics` are prose the writer and the examiner
read, `observables` add symbols on top of the state contract, and `screens` are
connected by `exits`. Gone with v3: `genre`, `gameplay`, `levels`, the fixed
`player`/`enemy`/`collectible` roles, the `#`/`.` terrain and the genre
registry. The state contract now requires only `g_score` and `g_state`; lives
and levels are notions a design may or may not have.

The reason is in `studio-projects/archive-v3/`. Eighteen "genres" produced one
game — four archived projects declare four different genres and describe the
same grid sweep — and two of the seven generated projects, `zampabolas` and
`atic-atac-2000`, burned all five attempts against an examiner that predicted
one game's cadence and failed anything else. `brick-wall` fell to the same
expectation on its third.

Three gates are withdrawn, not deferred: solvability, difficulty curve and
terrain structure. All three assumed a four-direction grid with no jump, so on
a platformer they did not measure a weakness, they reported a fiction.

The behaviour gate **abstains**. `probe_report` records what memory said and
returns `quality_pass: None`; acceptance no longer derives scenarios from the
design. Deriving a real expectation from a design's own mechanics is the phase 2
examiner's job, and until it exists there is nothing honest to judge a reading
against. An abstention is the accurate report; a guess is what rejected
`zampabolas` five times.

Acceptance evidence for the phase: `studio-projects/fase-uno` validates and
reopens with two screens joined by `exits` (`screen_1 -right-> screen_2`,
`screen_2 -left-> screen_1`), an entity of `kind: perseguidor`, a `jump: SPACE`
binding beside `left`/`right`, and a third tile carrying its own `climbable`
trait — four things v3 could not express, none of which needed a validation
rule relaxed to pass.

## Direction change, 2026-08-11

The engine was the wrong deliverable; the verification apparatus was the right
one. Work now aims at a generator writing the game, with everything built here
serving as help and proof rather than as a runtime the design merely configures.

The pivot rests on one idea: the observable state contract stops belonging to
the engine and becomes what is demanded of whoever writes the code. Any program
honouring it can be probed and judged, whether a template, a person or a model
produced it. `resources/studio_engine` is on its way to being one optional
library of pieces among others, not the thing every game must be built from.

One consequence deserves attention because it contradicts product contract
point 2 below: when a model writes the game, generated C stops being a
reproducible build artifact and becomes the artifact of record. That point will
have to be rewritten when the change lands, not quietly ignored.

## Product contract

- `game.yml` (GameProject schema v4) is the editable source of truth, and it declares its
  own vocabulary: tiles, entity kinds, control bindings and mechanics are the design's words,
  not Studio's.
- The program is written into the project and owned by it. It is the artifact of record, not a
  reproducible build output, because a written program cannot be reconstructed from the design.
- AI returns typed design proposals; applying them is a separate, reviewable operation.
- Every supported game must pass design, build, resource, semantic, runtime and playability gates.
- The legacy prompt-to-C command remains compatible while projects migrate incrementally.

## Stages

| Stage | Outcome | Status | Evidence / next gate |
|---|---|---|---|
| S01 | Separate application services from the legacy CLI | Implemented | TUI/headless services own create, save, generate, build and runtime test |
| S02 | Versioned `GameProject` IR and safe persistence | Implemented | Models, cross-field validation, atomic YAML and revision history |
| S03 | Extensible target/genre/capability registries | Implemented | Built-in target/genre packs, public protocols and entry-point discovery |
| S04 | Guided Textual TUI | In progress | Create/open/edit/save/generate vertical slice; scalar fields only, no scene/level/entity editors |
| S05 | Modular deterministic game engine | Withdrawn | Replaced by scaffolding: `resources/studio_lib` offers platform pieces with no game loop, and the program lives in the project's `program_dir`. The former engine is kept as a reference program under `resources/studio_reference` |
| S06 | Asset pipeline | In progress | Project-owned image import and deterministic Spectrum/CPC packing; a sprite-kind 16x16 asset is packed into `sprites.h` and blittable on both targets (S12), but every other imported asset still falls back to the generic `assets.c` conversion, which no generated C references |
| S07 | Structured AI design assistance | Implemented | Responses typed proposals, visible diff, separate apply action and protected contracts |
| S08 | Automated gameplay QA | Withdrawn and rebuilt in F2 | The solvability, terrain-structure and difficulty-curve analyses are deleted: each assumed a four-direction grid with no jump and so judged designs it could not read. The scripted-sweep and one-life-per-catch assertions are deleted with the fixed roles they predicted. What survives is the machinery, not the verdict: both toolchains still export `probes.json`, the emulator still reads the state contract out of memory, and the report now records the reading and abstains (`quality_pass: None`). F2 rebuilds the verdict on an examiner that derives expectations from the design's own `mechanics` and `observables` |
| S09 | Commercial vertical slices | In progress | Quality-gated reproducible release archive; content/presentation polish next |
| S10 | Extension SDK | Implemented | Public typed protocols, entry-point groups, compatibility rules and installable example |
| S11 | Real-game references driving the design | Implemented | Cited dossier in `reference.yml`, a proposal with an approvable diff, and a prompt block for the writer; adaptation is one-shot, so a refused proposal is discarded whole and retrying starts from a designer with no memory of what failed |
| S12 | Masked sprite blitting | In progress | Spectrum `plat_sprite` proven byte-for-byte: drawn over a non-zero background at a display-file third boundary, all 32 bytes read back over ZEsarUX's remote protocol match `spriting.pack_spectrum`'s independently packed data. CPC `plat_sprite` compiles through the real CPCtelera path and visibly draws against a no-sprite control build, but not proven byte-for-byte — the installed Caprice32 cannot dump memory. Sprites are 16x16, four frames, one Spectrum ink per sprite from the art's dominant opaque colour on fixed `PAPER_BLACK`; CPC colour comes from a fixed four-pen approximation of what `apply_palette()` programs, not the design's still-unused `presentation.palette`. Packed sprites are refused past half of `budgets.static_data_bytes`, both numbers named in the message — a conservative split with no empirical backing beyond one 2 KB example. `design_prompt` now tells the writer to draw actors with `plat_sprite` and terrain with `plat_cell`, and `llmz80 project sprites PATH` draws and previews the art, but no generated or reference program in the repository calls `plat_sprite` yet — only a hand-written probe program does — and no gate checks that a written program follows the instruction or steps through a sprite's frames |

## Current vertical-slice acceptance

- [x] Create a Spectrum or CPC project without an API call.
- [x] Choose single-screen collect or maze chase.
- [x] Include title flow, controls, player, enemies, collectibles and three levels.
- [x] Persist and reopen a strictly validated YAML design.
- [x] Display the main technical budgets in the TUI.
- [x] Generate deterministic target-specific C from the saved project.
- [x] Compile the generated project with both real toolchains from Studio.
- [x] Run it, capture runtime evidence and return to Studio with a report.
- [x] Edit scenes, entities and levels without hand-editing YAML.
- [x] Apply an AI proposal through a visible diff with cost approval.

## Known gap between the IR and the engine

The design IR is still richer than the code the engine can emit, though P0 closed the widest part
of the gap. This gap, not the missing screens, is what blocks the remaining commercial work.

Closed by P0:

- Entity counts are no longer fixed. The engine iterates a generated actor table, and
  `validate_backend_support` now enforces real capability limits — one player, at least one
  collectible, the `max_entities` budget, and the target's character grid — instead of a
  hardcoded 1/1/8 shape.
- Levels receive distinct generated spawn layouts rather than a redrawn identical screen.
- Scoring has one source of truth: `gameplay.score_per_collectible` feeds both the generated
  `SCORE_PER_COLLECTIBLE` and `quality.design_quality_report`.

Closed by P1:

- `LevelSpec` carries authored terrain (`tiles`) and `spawns`. Level identity is now content in
  `game.yml`, not a rule inside the generator, and the engine blocks movement into walls.
- v2 documents migrate to v3 on load, authoring the layout the old generator implied.

Closed by S12:

- Masked sprite blitting exists and is proven on target, not just compiled: the Spectrum's
  `plat_sprite` matches independently packed bytes exactly, byte for byte, read back from real
  video memory over ZEsarUX's remote protocol; the CPC's compiles through the real CPCtelera path
  and visibly draws against a no-sprite control build. A sprite-kind 16x16 asset is now packed into
  `sprites.h` as a `SPRITE_<ID>` constant that generated C actually holds and blits — the specific
  "packed but never referenced" gap this bullet used to name is closed for that one asset shape.

Still open:

- Terrain still draws through `plat_cell`'s built-in shapes; only actors are wired to sprites, and
  even that is only prompted, not yet proven in a real program. `design_prompt` tells the writer to
  draw actors with `plat_sprite` and terrain with `plat_cell` once a design has sprite assets, but
  no generated or reference program in this repository calls `plat_sprite` yet — only a hand-written
  probe program in `tests/test_sprite_blitter_toolchain.py` does — and no gate checks that a written
  program actually follows the instruction.
- Nothing generated yet animates. `g_anim_frame` joined the state contract as an optional symbol,
  and `llmz80/studio/feel.py` now judges it between scripted acceptance steps — the frame must
  advance while a step holds a direction and hold still while a step waits — so a gate does observe
  animation where a program declares the symbol. What it cannot do yet is find one to observe:
  `plat_sprite` still takes a frame index and `sprites.h`'s `sprite_frames[]` array still carries
  each sprite's frame count, but no generated or reference program in this repository calls
  `plat_sprite` or declares `g_anim_frame`, so the gate abstains on every real run today. That part
  is unchanged from before this plan.
- `budgets.frame_budget_cycles` is still a declared number rather than a measured one. The engine
  now counts missed frames on target and shows the worst case in the HUD, but that is a pass/fail
  signal read from a captured frame, not a cycle count, and it cannot gate automatically until the
  memory probes in P6 exist. The CPC has no free-running frame clock with the firmware disabled,
  so it reports nothing; the catalog's `measureCycles` example is the starting point there.
- Enemy chase is a greedy single-axis step, so a concave wall traps a chaser until the player
  moves. Real pathfinding is not attempted.
- Solvability proves a route exists; it does not model enemy threat, so a level can pass the gate
  and still be unfair. That needs the runtime probes from P6.
- The time-limit check assumes the player advances one cell per frame. With `time_limit_seconds`
  bounded below at 10 seconds, a level under roughly 500 steps can never fail it.
- `presentation.palette` is unused; both targets draw with fixed pens, sprites included. CPC sprite
  colour comes from `compiler.py`'s `CPC_DEFAULT_PALETTE`, a fixed four-entry approximation of the
  pens the platform library's `apply_palette()` actually programs — not from the design's palette.
- CPC mode 1 has four pens, so collectibles share the enemy pen and are distinguished by being
  drawn at half height.
- Audio exists on the Spectrum only. The CPC declares no audio, and no target offers music, so
  `audio.music` can currently only be false anywhere. The `spectrum_128` target does not exist.
- No gate observes sound actually being produced. The emulator harness runs with audio disabled
  and captures no waveform, so "the effect played" is inferred from the code path being reached,
  not measured.
- Memory probing works on the Spectrum only. The installed Caprice32 does not resolve
  `CAP32_SNAPSHOT` as an autocmd: passing it types the literal characters into the emulated CPC,
  while `CAP32_EXIT` correctly maps to F10. Until a build exposes snapshot dumping, or another CPC
  emulator with a remote protocol is adopted, CPC state stays unobserved and the gate abstains.
- The probe proves that collecting scores and, when the design places a chasing enemy,
  `enemy_costs_life` now scripts the encounter too: the emulator waits for the chaser to reach the
  player's spawn and asserts one life lost without ending the game. A patrolling, bouncing or
  guarding enemy's position after N frames is not predictable from the design alone, so a collision
  with one of those stays prose rather than a check that would only usually be true. Clearing a
  level advancing it is still unproven either way — no scenario scripts it, and this plan did not
  touch that gap.

Consequence for sequencing: visual editors built before the engine is data-driven would author
designs that `validate_backend_support` rejects. Engine expressiveness comes first.

## Engine constraints discovered on target

- The engine must contain no 16-bit division, modulo or multiplication. SDCC satisfies those from
  library modules built for `sdcccall(1)`, and the CPCtelera link enforces `sdcccall(0)`, so the
  build fails at link time with conflicting-ABI warnings. Use repeated subtraction or accumulation.
- Menus must poll input tightly instead of once per frame, and gameplay must start on key-down.
  A frame-gated poll can miss a scripted emulator keypress, and starting on key-up leaves the
  runtime harness photographing a static menu while it still holds the key.
- Caprice32 has been observed to hang past its 30-second harness timeout immediately after an
  earlier run of the same binary timed out. It is not reproducible in isolation and remains an
  open risk for the release gate.
- On CPC, only `const` data can be relied on at run time. A file-scope initialised, non-const
  array lands in the DATA segment, which this link does not initialise, so it contains whatever
  was in memory. Build such tables on the stack instead. The symptom is subtle: the program links,
  boots and produces a non-blank screen, so only looking at the captured frame reveals it.
- CPCtelera's `cpct_setPalette` takes a mutable pointer. Casting a const array to it raises SDCC
  warning 357, which the build policy rejects.
- z88dk's `bit_beep` runs with interrupts disabled. A dedicated probe played a beep spanning many
  frames and the ROM frame counter reported "FRAMES ADVANCED 00", so the engine's frame-cost
  readout cannot see time spent inside beeper effects and under-reports whenever they play.
  A LAG of zero therefore means the drawing and movement work fitted, not that the audio did.

## Remaining plan

Ordered by what unblocks what, not by product visibility.

| Phase | Work | Unblocks | Acceptance evidence |
|---|---|---|---|
| P0 | Replace the per-target f-string monoliths with a versioned static engine runtime (`resources/studio_engine/{common,spectrum,cpc}`) plus generated `game_data.c` and `game_config.h`; entity tables of arbitrary size; retire `validate_backend_support` restrictions one at a time, each behind a passing build | everything below | **Done.** Both targets build and run a 3-enemy, 12-collectible, 3-distinct-level design with zero unexpected warnings; regeneration is byte-identical; 53/53 catalog unaffected |
| P1 | Schema v3: `LevelSpec.tiles`, spawn points and tileset reference, with a v2 to v3 migration through the existing revision history | maps, solvability, enemy AI | **Done.** v2 documents migrate on load to the same layout; validators reject spawns in walls, duplicate cells and spawn counts that disagree with entity counts; the engine blocks movement into walls on both targets |
| P2 | Solvability analysis in Python (reachability of collectibles and exit, shortest path length, time limit feasibility) wired into `design_quality_report` | editors, AI level proposals | **Done.** `every_level_is_solvable` fails with the sealed cells named; a design that builds and runs is still refused at release |
| P3 | Visual scene, map, entity and level editors in the TUI | vertical-slice acceptance item 9 | **Done.** `llmz80/studio/editing.py` holds every operation as a pure function; Map and Entities tabs drive it and show gate state live; an edited design builds and runs on both targets |
| P4 | Multi-enemy engine: per-entity behaviour (horizontal and vertical patrol, greedy chase, guard, bounce) and difficulty scaling driven by `difficulty_curve` | advanced AI, genre polish | **Done.** `EntitySpec.behaviour` drives the engine; at the full 16-entity budget with all five behaviours the Spectrum reports zero missed frames on target and both machines build, run and release |
| P5 | Audio: AY playback on CPC, beeper effects on Spectrum 48K, with a new `spectrum_128` target for real music; audio capability declared per target so unsupported requests degrade explicitly | polish | **Partly done.** The capability contract and explicit degradation are in place and Spectrum plays beeper effects for 314 bytes. CPC audio, Spectrum music and the `spectrum_128` target are **not** delivered |
| P6 | Real playability probes: export the toolchain symbol map to `probes.json` and assert score, lives and level transitions from memory during a scripted input replay | S08 and S09 as claimed | **Partly done.** Both toolchains export `probes.json`. On Spectrum a scripted sweep collects a predicted number of items and the gate asserts the resulting score and remaining count from memory, and a chasing enemy's catch is scripted to cost exactly one life. Patrol/bounce/guard enemies still leave life loss as prose, level transitions are not scripted at all, and the CPC abstains for lack of a memory adapter |
| P7 | Advanced AI design assistance over tilemaps, per-genre polish, loading screen, high-score table, tape and disk mastering | commercial release | **Partly done.** AI proposals are refused when they would leave the game unplayable, and a high score is kept and probe-verified on target. Loading screen, tape and disk mastering and per-genre polish are **not** delivered |

Not yet covered anywhere above and still required for a commercial claim: loading screen, and tape
and disk mastering. Masked sprite blitting is now S12 in the Stages table above — the blitter itself
is proven on target, but no generated game draws an entity through it yet; see S12's evidence and
the sprite bullets under "Known gap between the IR and the engine". The high score is kept in memory
only; neither target has storage here, so it does not survive a power cycle.

## Architecture decisions

1. Pydantic v2 owns validation and schema evolution.
2. Textual owns the terminal UI; no business rules live in widget callbacks.
3. Genre packs provide valid defaults and acceptance scenarios, not prompt fragments.
4. External packs use Python entry point group `llmz80.genre_packs`.
5. OpenAI Responses structured outputs produce `ProjectProposal`; they never produce or overwrite C.
6. Existing example libraries remain the certification corpus for backends and generated runtime modules.
7. The generator emits data, not logic: gameplay code lives in a versioned engine runtime that both
   toolchains compile, and `game.yml` only produces tables and configuration headers.

## Verification log

- 2026-08-10: Spectrum playable pack compiled with Z88DK, 6,597-byte payload, zero warnings.
- 2026-08-10: CPC playable pack compiled with CPCtelera, 1,774-byte payload, zero warnings.
- 2026-08-10: ZEsarUX headless test passed boot, non-blank framebuffer and input transition.
- 2026-08-10: Caprice32 headless test passed boot, non-blank framebuffer and input transition.
- 2026-08-10: complete release flow passed on both targets; design/build/runtime gates were true
  and each reproducible ZIP contained the canonical artifact, design, three reports and checksums.
- 2026-08-10: 154 automated tests passed and the certified legacy catalog remained at 53/53 builds.
- 2026-08-10 (P0): the two per-target f-string emitters were replaced by a versioned engine runtime
  compiled from `src/` by both toolchains. The generator now emits only `main.c`, `game_config.h`
  and `game_data.c`.
- 2026-08-10 (P0): a 3-enemy, 12-collectible, 3-level design built with zero unexpected warnings on
  both targets. Spectrum `output.tap` 6,357 bytes, down from 6,597 for the old single-enemy build
  because the ROM-font text routine replaced stdio. CPC `program.bin` 3,015 bytes, up from 1,774.
- 2026-08-10 (P0): ZEsarUX and Caprice32 both passed boot, program load, non-blank output and input
  transition. Spectrum now shows the change in the screenshot pair rather than only in the raw
  frame stream, so the gate observes gameplay starting rather than a static menu.
- 2026-08-10 (P0): the complete release flow produced quality-gated archives on both targets.
- 2026-08-10 (P0): 158 automated tests passed and the catalog remained at 53/53. One pre-existing
  environment failure remains: `test_studio_tui.py` needs `pytest-asyncio`, which is not installed.
- 2026-08-10 (P1): levels became authored content. `game.yml` now carries a tile grid and explicit
  spawn points per level, and `store.load` migrates v2 documents to the identical layout the old
  generator produced.
- 2026-08-10 (P1): both targets built and ran a walled maze with 3 enemies and 12 collectibles.
  Spectrum `output.tap` 7,089 bytes against a 24,576-byte budget; CPC `program.bin` 3,754 bytes
  against 32,768. Captured frames show the wall ring, interior pillars, player, enemies and
  collectibles rendering correctly on both machines.
- 2026-08-10 (P1): 165 automated tests passed, including a reachability check over generated
  terrain and a v2-to-v3 migration round trip, and the catalog remained at 53/53.
- 2026-08-10 (P2): solvability became a design gate. `llmz80/studio/solvability.py` runs a
  breadth-first search from the player spawn over four-connected floor and reports unreachable
  collectibles, unreachable enemies, the distance to the furthest collectible and a nearest-first
  route estimate. `design_quality_report` gained `every_level_is_solvable` and a per-level report.
- 2026-08-10 (P2): a design whose walls seal one collectible compiled cleanly and passed both the
  build and runtime gates, and was still refused at release with the reason
  "level_1: walls seal off 1 collectible(s) at (9, 2)". Analysis needs no build and no emulator,
  so an editor can run it on every keystroke.
- 2026-08-10 (P2): 169 automated tests passed.
- 2026-08-10 (P3): editing moved into `llmz80/studio/editing.py` as pure operations that each
  return a newly validated project, keeping architecture decision 2 intact. The TUI gained a Map
  tab that paints terrain, moves spawns, resizes and renames levels, and an Entities tab that adds,
  removes and retunes entities. Both show the solvability and engine-capability gates live.
- 2026-08-10 (P3): a design edited only through those operations — level renamed and resized to
  18x14, three enemies plus a new two-instance guard entity, and a hand-painted wall — built and
  passed the runtime gate on both targets, with the painted wall visible in the captured frame.
- 2026-08-10 (P4): enemy movement became a design field. `EntitySpec.behaviour` selects horizontal
  or vertical patrol, bounce, greedy chase or guard, with "auto" preserving the previous
  index-based alternation so existing designs are unchanged.
- 2026-08-10 (P4): the engine measures its own frame cost where the target allows it. At the full
  16-entity budget, with all five behaviours in play, the Spectrum HUD read "LAG 0" in the captured
  frame: not one missed frame. Both targets built, ran and released; Spectrum `output.tap` 7,837
  bytes and CPC `program.bin` 4,309 bytes, both inside budget.
- 2026-08-10 (P4): 200 automated tests passed and the catalog remained at 53/53.
- 2026-08-10 (P5): audio became a declared target capability. `TargetPack` states what each machine
  can produce, new projects only ask for what their target supports, and `design_quality_report`
  refuses anything beyond it by name rather than dropping it silently.
- 2026-08-10 (P5): the Spectrum plays beeper effects through the certified `bit_beep` for 314
  bytes, taking `output.tap` from 7,837 to 8,151. A design asking the CPC for effects, or either
  machine for music, fails the design gate and cannot be released.
- 2026-08-10 (P5): 204 automated tests passed and the catalog remained at 53/53. CPC audio,
  music and the `spectrum_128` target remain undelivered; see the open items above.
- 2026-08-10 (P6): engine state became observable. Five variables now have external linkage as a
  declared probe contract, `zcc` is invoked with `-m`, and `probes.json` records their addresses
  from the z88dk map on Spectrum and the SDCC `.noi` file on CPC. Both targets resolved all five.
- 2026-08-10 (P6): the Spectrum runtime gate now reads those addresses over ZRCP. On the title
  screen every probe read zero; after the scripted key started the game they read level 1,
  lives 3, remaining 8 and score 0, matching the design exactly. The gate compares the reading
  against the design and fails on any mismatch, and `g_worst_frame_cost` being checked for zero
  makes the P4 frame budget an automatic assertion rather than something read off a screenshot.
- 2026-08-10 (P6): a target with no memory adapter records the gate as unobserved rather than
  passed, so the CPC cannot inherit the Spectrum's evidence.
- 2026-08-10 (P6): 211 automated tests passed and the catalog remained at 53/53.
- 2026-08-10 (P6b): the gate stopped at proving initialisation and now proves a rule. `sweep_plan`
  reads the level and picks one direction whose held key must collect a known number of items;
  the emulator holds that key and the probe compares the result against the prediction. On the
  built-in maze design, holding down collected one item and memory read score 10 and remaining 7,
  exactly as the design predicts. A build that failed to award the point would fail the gate.
- 2026-08-10 (P6b): 217 automated tests passed, the catalog remained at 53/53, and both targets
  built, ran and released; the CPC still abstains from the state probe.

- 2026-08-10 (P7): `apply_proposal` now runs the solvability and engine-capability gates before it
  returns. A proposal that walls a collectible in is refused with the sealed cells named, and one
  that widens a level past the target grid is refused too. Hand editing keeps treating those as
  advisory, because a person watches each cell change; a bulk model edit gets no such supervision.
  `allow_unplayable` exists for the deliberate case, mirroring `allow_budget_changes`.
- 2026-08-10 (P7): the engine keeps a high score across game overs and shows it on the title
  screen. It is part of the probe contract, and a run that collected one item read
  `g_hiscore` 10 alongside `g_score` 10 from emulated memory.
- 2026-08-10 (P7): 224 automated tests passed, the catalog remained at 53/53, and both targets
  built, ran and released. Spectrum `output.tap` 8,155 bytes, CPC `program.bin` 4,387 bytes.
- 2026-08-10 (P7): a probe read that outran the emulator's bounded lifetime surfaced only as a
  broken pipe and silently dropped the last symbol. The session now sizes that lifetime from the
  work it intends to do, records the sweep before any I/O can fail, and lets one unreadable symbol
  fail without abandoning the rest.

- 2026-08-11 (A): the state contract moved to `llmz80/core/state_contract.py`, free of Studio
  imports so the legacy prompt-to-C generator can use it. It names four required symbols
  (`g_score`, `g_lives`, `g_level`, `g_state`) and three optional ones, and renders itself as
  prompt text stating the rules that cost real build failures to learn: never static, and assign
  starting values at run time because the CPC link leaves the data segment uninitialised.
- 2026-08-11 (A): the engine gained `g_state` and now initialises `g_hiscore` at run time. That
  second change fixes a latent fault shipped in P7: the high score had no run-time initialiser, so
  on CPC it would have held whatever was in memory.
- 2026-08-11 (B): acceptance criteria became executable. `AcceptanceScenario` carries an optional
  `hold`/`frames`/`expect` triple, validated against the contract, and `llmz80/studio/acceptance.py`
  turns a design into an emulator script and into the prompt text a generator is shown beforehand.
  The emulator runs the whole ordered script in one boot, reading the contract after every step.
- 2026-08-11 (B): on the built-in maze design both steps passed on target. Holding action for 30
  frames read `g_state` 1, `g_level` 1, `g_score` 0; holding down for 60 frames read `g_score` 10
  and `g_remaining` 7.
- 2026-08-11 (B): the gate was shown to fail, not just to pass. With `g_score += SCORE_PER_COLLECTIBLE`
  sabotaged to `g_score += 0`, the build still succeeded and the program still booted, drew and
  answered input, and the acceptance gate rejected it with `g_score: expected 10, read 0`. That
  message is the repair signal a generator needs, and no earlier gate could produce it.
- 2026-08-11 (A/B): `llmz80 project contract PATH` prints the contract and the runtime acceptance
  for a design, so the prompt is usable before the generator is wired to it.
- 2026-08-11 (A/B): 241 automated tests passed and the catalog remained at 53/53.

## Environment note

Run the tests through the project's virtual environment, as the Makefile does. The system
interpreter lacks `pytest-asyncio`, which silently reduces the Textual pilot test to a skip-like
failure, and it was in that blind spot that the Map tab shipped with a duplicate widget id.

    .venv/bin/python -m pytest tests/
- 2026-08-10 (P3): 191 automated tests passed. The Textual pilot test still cannot run in this
  environment because `pytest-asyncio`, though declared in `pyproject.toml`, is not installed, so
  the widget wiring itself is unverified here; the editing operations it calls are covered by 20
  synchronous tests.

## 2026-08-11 (C): the engine left the product

- `resources/studio_engine` became `resources/studio_lib`, holding only `platform.h` and the two
  `platform.c` implementations. `engine.c` and `engine.h` were deleted from it. Studio no longer
  emits actor tables, spawn tables or wall bitmaps; `codegen.py` writes constants and nothing else.
- `GameProject.program_dir` names the directory inside the project holding its C sources.
  `render_project` scaffolds around them: the library, `game_config.h` with the design's constants,
  `game_state.h` declaring the contract, and `CONTRACT.md` with the full generation prompt.
  A project with no program still scaffolds and records `program_present: false`.
- `validate_backend_support` became `validate_design_fits_target`. What remains is about the
  machine, not about any program: a level wider than the character grid cannot be drawn however
  the code is written.
- The former engine survives as a reference program in `resources/studio_reference`, one per
  target, with the design it satisfies. It is not retrievable context yet: the example catalog and
  its audit compile one source file per entry, so a multi-file program cannot join them without
  changing both.
- The generation prompt gained the design itself: entities with roles, counts and behaviours, and
  every level as the same ASCII grid the designer edits, with starting positions.
- Evidence: the reference program, carried into a project as its own `program_dir`, scaffolded,
  built and ran on both targets, and the acceptance gate passed both steps on Spectrum. 238
  automated tests passed and the catalog remained at 53/53.
- Still open: nothing generates a program yet. Until a generator is wired to `CONTRACT.md` and the
  repair loop is fed with acceptance mismatches, a project's program has to be written by hand.

## 2026-08-11 (D): a program gets written, and repaired

- `llmz80/studio/generator.py` asks a writer for the program, stores it in the project's
  `program_dir`, verifies it, and feeds what failed back in. The writer is injected, so the loop
  runs in tests without an API call and a different writer drops in without touching the loop.
- `ProgramSources` refuses anything that is not a `.c` or `.h`, requires `main.c` and rejects
  empty files, so a writer cannot smuggle a Makefile past the scaffold.
- `repair_prompt` gives back the most specific evidence available: compiler diagnostics when the
  build failed, the missing contract symbols when the linker map lacks them, and the exact memory
  mismatches when the program built and ran but behaved wrongly.
- `llmz80/core/platform_notes.py` puts every constraint learned by building into the prompt: the
  CPC ABI rule, const-only data, warning 357, four pens in mode 1, the ROM frame counter needing
  interrupts, bit_beep blocking, and starting gameplay on key press rather than release.
- Evidence, with the real toolchain and the real emulator: a writer handed over the reference
  program with `g_score += SCORE_PER_COLLECTIBLE` changed to `g_score += 0`. It compiled cleanly
  and ran, and the loop rejected it, fed back
  "After holding down for 60 frames: g_score: expected 10, read 0", and accepted the corrected
  program on the second attempt.
- A target that cannot be observed accepts on the build alone and records the acceptance verdict
  as unobserved. It never inherits a pass it did not earn.
- `llmz80 project write PATH` runs this against the OpenAI API. 250 automated tests passed and the
  catalog remained at 53/53.
- Still open: the writer has never been run against a live model here, so the prompt's quality is
  untested. Retrieval does not yet feed the reference program or per-genre examples into it.

## 2026-08-11 (D2): measured, and a correction

Three live runs of `llmz80 project write` against gpt-5, writing a Manic Miner
design: a 30x18 cavern with ledges, eight keys and two patrolling nasties.

- Run 1 produced nothing: `ProgramSources` used a dict field, which generates
  `minProperties`, which structured outputs reject. Only a live call shows this.
- Run 2, after reshaping the schema: 3 of 3 attempts compiled, 0 behaved. Two
  earlier attempts had been rejected for warnings alone, which the prompt never
  said were fatal, and one for spelling `IN_KEY_SCANCODE_space`.
- Run 3, after stating both: 3 of 3 compiled again, 0 behaved.

The behaviour failure was isolated without further API spend, using two probe
programs built by hand:

- The harness delivers keys correctly. A probe that sets a marker when P is held
  read that marker back, so scripted input was never the problem.
- The ROM frame counter at 23672 does not advance under this crt: twenty
  consecutive waits all timed out. Generated programs paced their game loop on
  it, so the loop hung on its first frame. `g_state` was already 1 by then,
  which is why the gate saw a started game that never scored.
- `intrinsic_ei()` fixes it: the same probe then saw all twenty ticks.

**A correction to the P4 entry above.** The Spectrum HUD reading "LAG 0" was
recorded as evidence that no frame was ever missed. It was not: the counter it
read never moved, and `plat_wait_frame` only escaped through its guard. The
frame cost figure was vacuous, and the reference program's frame pacing was a
delay loop rather than frame sync.

Fixing it exposed a second error in the same measurement. With interrupts
enabled the reading became 1, not 0, because one frame between consecutive
waits is the loop keeping pace rather than losing anything; the count was off by
one and had never been exercised against a running clock to show it. The library
now enables interrupts in `plat_init` and reports elapsed frames less that one.
The reference program then measured zero frames lost, and this time the figure
means what P4 claimed.

Retrieval already exists from Q05/Q06 and is not wired into the program writer:
`ExampleCatalog.search` returns useful hits but a Spectrum query also returns
Amstrad CPC entries, so the platform filter needs looking at before it feeds a
prompt.

## 2026-08-11 (E): retrieval wired in, and a game

Retrieval already existed from Q05/Q06 and only needed connecting. An earlier
note here claimed its platform filter was broken; that was wrong. The filter
works by directory, and the failing query had been given the corpus root rather
than `examples/<platform>`.

`llmz80/studio/retrieval.py` asks the catalog what a design needs and puts the
reference program first, since it is the one program known to satisfy the
contract on that machine, followed by up to two certified examples. The prompt
grows from about 8k to 36k characters.

With examples in the prompt, gpt-5 wrote a Manic Miner design that was accepted
on its first attempt: memory read `g_state` 1, `g_level` 1, `g_score` 0 after
the start key, then `g_score` 30 and `g_remaining` 5 after holding right, and
zero frames lost. Every previous run had failed all three attempts.

**That first success was not a game.** Looking at the captured frame showed a
tape loader, and the program contained no drawing call at all. It implemented
the rules, satisfied the state contract and passed acceptance while putting
nothing on screen. Two faults let that through:

- The screen was captured about two seconds in, while the tape was still
  loading, so no capture ever showed the program. A frame is now taken after
  the scripted inputs, which is the only one that can show gameplay.
- `visual_change` accepted a difference in the raw frame stream, which a tape
  loader produces on its own. With a settled post-input frame available the gate
  now requires that frame to differ from the first one.

The writer is also told plainly that drawing is part of the job.

Re-running the invisible program against the hardened gate rejects it
(`visual_change` false) while the reference program still passes, so the gate
discriminates rather than merely tightening. A fresh run then produced a program
accepted on its third attempt whose captured frame shows ledges, the miner,
keys, two nasties and a HUD reading SCORE 00030, matching what acceptance
demanded.

## 2026-08-11 (F): typologies as data

Genres were an enum with two members, so every new kind of game meant editing
code. They are now entries in `resources/genres.yml`: what the game is made of
and what shape its space has. Eighteen are catalogued, covering maze chase,
single-screen collect, two platformers, climbing, three shooters, brick breaker,
snake, block pusher, top-down adventure, dodging, lane racing, static defence,
boss arena, digging and memory sequence.

Terrain became a named shape rather than a genre comparison: `open`, `maze`,
`ledges`, `corridors` and `chambers`. Adding a typology needs no change in
`layout.py`.

The solvability gate earned its keep during this work. Three typologies using
`chambers` failed it immediately: cutting one doorway per dividing wall looks
symmetric but seals the quadrant that neither doorway touches. The gate named
the sealed cells; the shaper now cuts a doorway on each side of the crossing
wall. All eighteen typologies now produce, on both targets, a design that passes
the design gate, is solvable on every level, fits the target grid and carries a
runnable acceptance step: thirty-six designs, no failures.

Retrieval asks with the typology's own keywords, since an id retrieves poorly:
"breakout" finds less than "ball bat bricks bounce paddle".

`llmz80 project types` lists them, and `project new` names them all when given
an unknown one.

A live run on `breakout`, deliberately the typology furthest from the design
already proven, did not converge: two attempts failed to build and the third
built but scored nothing where the design predicted ten. Three attempts is the
current ceiling and it was reached. The typologies are verified as designs, not
as generated games; only maze chase and the platformer have been carried through
to a working program.

## 2026-08-11 (G): the terminal front end, compacted

Seven tabs and seventy-four widgets became three panes and nineteen. Labels sit
beside their fields rather than above them, entities are one table instead of a
select and five controls, the three separate gate readouts became one status
line, and the actions moved onto keys. It boots and shows a map in an 80x24
terminal, which the previous layout did not.

The front end had also fallen behind the product: it still offered "Generate
sources" from the era when Studio produced the game, and had no way to have a
program written. `ctrl+w` does that now, and says it spends money before it does.

`editing.rename_project` applies the scalar form fields in one validated step.
Applying them one at a time would reject an edit that is only valid once all of
them are in place, and putting that rule in a widget callback would have put a
domain decision back in the UI.

Attempts default to five rather than three. The breakout run reached a building
program on its third attempt and had no attempt left to fix its behaviour, which
is the shape of failure extra attempts address.

## 2026-08-11 (H): two faults the front end had all along

Reported as "the operations do nothing, or nothing is shown".

Building takes seconds and a runtime test tens of them, and both ran on the UI
thread. The app froze so completely that even the "Building..." line never
appeared, so a command that was working looked like a command that did nothing.
Slow work now runs through an async worker awaiting `asyncio.to_thread`, and the
result is applied from the UI task itself rather than across threads. Verified
against a real build: the status line reads "Building..." while it runs, the
interface still accepts typing, and it settles to "ready" afterwards.

The second is more fundamental: there was nowhere to say what the game should
be. A typology is a starting shape and the structured fields say what the game
is made of, but neither expresses "Zampabolas, and eating a power dot makes the
ghosts edible". `Metadata.brief` holds the designer's own words, appears first
in the design prompt, and feeds the retrieval query, where it describes the game
far better than an id does. It is on the Project pane and is the fifth argument
to `project new`.

## 2026-08-11 (I): writing a Zampabolas, and what it exposed

Asked for a Pac-Man style game, and the attempt found four faults.

- `set_entity_count` divided by zero when asked for the count an entity already
  had, which is what happens when a genre pack already supplies it.
- A refused release raised a traceback from the CLI. Refusing is an ordinary
  outcome and now prints one line.
- The acceptance step for scoring checked the score and the count of things
  left, and nothing else. A design whose enemies killed the player three times
  during that same step passed it: the program had scored, and the step never
  asked whether anyone was still alive. It now requires `g_state` to be playing
  and lives to be untouched, which is what "collecting scores" was always meant
  to mean.
- Level content placed enemies by even spacing, so a chaser could start beside
  the player. Enemies now take the cells furthest from the player.

The fourth fix was not enough, and that is the useful part. Four chasers at the
player's own speed end the game in under a second whatever the layout, and the
captured frame reads GAME OVER, SCORE 00010: it ate one dot and lost three
lives. `solvability` gained a `threat` report for a chaser starting within three
cells, deliberately reported as a warning rather than a gate, because deciding
whether a pursuit is survivable needs a simulation this does not do and
rejecting playable designs on a guess costs more than it saves.

The underlying limit is the speed scale. Speed runs from one cell every four
frames to one every frame, so every value is between 12 and 50 cells a second
and there is no way to say "the enemies are slower than the player walks".
Giving the player speed 4 to outrun them asks for a cell every frame, which no
sensible program implements, and three attempts failed the acceptance step
because the program moved at a playable pace instead.

So: the program works and the design does not. Studio produced a Zampabolas
that compiles, boots, draws its maze, scores, loses lives and reaches a game
over screen. It is unplayably hard, and no gate here can currently say so.

## 2026-08-12 (J): difficulty and animation, gated instead of declared

- `llmz80/studio/difficulty.py` turns `gameplay.difficulty_curve` from a word into a check: it reads
  `solvability.analyse_level`'s route length and each level's `time_limit_seconds` and refuses a
  `linear` or `stepped` design whose levels never get harder, or that gets measurably easier
  anywhere. `layout.py`'s per-typology generators were reworked to escalate on that same lever, and
  `tests/test_difficulty_escalation.py` proves it for the whole catalogue rather than a sample: all
  eighteen typologies in `resources/genres.yml`, on both targets, pass solvability, terrain
  structure and the difficulty gate at every level. This is a design-level proof -- pure analysis
  over the generated IR, no build or emulator involved, the same way (F)'s typology proof was.
- `EntitySpec.count` still cannot vary per level -- `GameProject.validate_contract` requires every
  level to place exactly `entity.count` instances of every entity, so "more enemies later" stays
  inexpressible. `difficulty.py` states this as a limitation rather than a gap it papers over: route
  length and time limit are the only two difficulty signals today's IR can actually measure.
- `g_anim_frame` joined the state contract as an optional symbol (`llmz80/core/state_contract.py`),
  and `llmz80/studio/feel.py` judges it between the scripted acceptance steps that already exist:
  the frame must differ between two consecutive steps held in a direction and must not differ
  between a moving step and a following idle one. Classification reads the step's own `hold` --
  now threaded into `step_readings` -- rather than a naming habit on the step id, which no real
  scenario ever followed.
- `enemy_costs_life` moved from permanently-prose to conditionally-executable. Where a design places
  a `behaviour == "chase"` enemy, `derive_scenarios` now scripts the encounter: hold nothing
  (`hold="none"`) for exactly the frames `chase_catch_frames` computes from the chaser's shortest
  route to the player's spawn, and expect `g_lives` down by one with `g_state` still playing. A
  patrolling, bouncing or guarding enemy's position depends on where it moved on its own, so a
  collision with one of those still cannot be predicted and stays prose.
- Fixed the bug that would have silently defeated the bullet above: `StudioService.scenario_script`
  resolved every scripted hold through a keyboard map and dropped whatever did not resolve --
  including every `hold="none"` waiting step, since waiting was never going to be in that map. An
  unresolvable hold (a control scheme with genuinely no key for a direction) is now logged rather
  than silently dropped.
- What this does not yet prove: no generated or reference program in the repository declares
  `g_anim_frame` or calls `plat_sprite`, so the animation gate abstains (`observed: False`) on every
  real run today. It was verified with synthetic `step_readings` and a mocked wiring test
  (`test_zesarux_step_reading_carries_the_step_hold`), not against a compiled program on a real
  emulator. Clearing a level advancing `g_level`, and a collision with any non-chasing enemy, remain
  entirely unscripted.
- Both runtime gates abstain on the CPC, unchanged: `_run_caprice32` builds no `step_readings` at
  all, so the scripted encounter and the animation judgement are both unobserved there, never
  passed.
- The TUI's resting screen shrank further to one command screen -- header, brief-box, stage-line,
  stage-detail, shortcuts: seven rows measured the same way as before (`Widget.size.height` under
  `run_test`), plus a footer -- with design/map/entities/sprites/diff/log as panels opened one at a
  time over it, and research (`ctrl+f`), adapt (`ctrl+a`) and sprite drawing (`ctrl+d`) reachable
  from it alongside save/new/open/write/build/test/release.
- 775 automated tests collected, 774 passing with one known-flaky emulator test deselected.

## 2026-08-14 (K): the front end stopped being a keyboard and became a wizard

Reported as "I never know which key I am supposed to press".

Ten `ctrl+<letter>` shortcuts sat on the resting screen with nothing to say which
of them was next. That `ctrl+f` had to come before `ctrl+a`, and that `ctrl+t`
rather than `ctrl+b` was what produced the quality report, was knowledge the
screen demanded and never offered: the order of the pipeline lived in the
person's head and the screen quizzed them on it. Pressing the wrong one was
refused, and there was no way to learn it would be refused except by pressing it.

The second complaint was the same shape from the other side: the pipeline said
nothing while it worked. Having a program written and repaired takes minutes,
and the screen reported the result and nothing before it, so a command that was
working looked exactly like one that had hung.

- `llmz80/studio/wizard.py` answers the first: a pure state machine over
  `screen.stage_line`, which already decides what has been done from the design
  in memory and the evidence on disk. The wizard adds only the three things that
  module does not have -- the order, the words to put on screen, and the rule for
  what may be walked past -- and re-derives none of the "is this done" logic,
  because two answers to that question drift apart within a week. Nothing in it
  draws, calls an API or touches disk, so the whole flow is tested without
  starting Textual.
- The screen stands on one step at a time and names it: `Paso 3 de 6: sprites`,
  what the step is for, and which key does it. Ten keys became five -- `Enter`
  does the step, `→` leaves it behind, `Esc` goes back a step (and saves, on the
  way out of an editor), `R` does a finished one over after asking, `Q` quits --
  plus `A` inside `diseño`, which adapts the design to the researched game as one
  reviewable diff and is offered only where a dossier exists to adapt to. A key is
  named only where it would work: `→` reads `omitir` on `referencia` and
  `sprites`, which the pipeline can genuinely spare, and is not offered on
  `programa` or `gates`, without which there is nothing to release. `Enter` says
  `gasta dinero (API)` before it spends any.
- `llmz80/studio/journal.py` answers the second: every project gets an
  append-only diary in `<project>/studio.log` -- what started, what it said along
  the way, what it ended as, and how many seconds it took. Every line is written
  to the file *and returned*, so what a person watches and what the file remembers
  are the same characters rather than two renderings of one event. The diary sits
  below the wizard permanently instead of behind a key; the `l` log panel went
  with the ten shortcuts, because a diary you have to press something to see is a
  diary nobody reads.
- Walked end to end with `run_test` on an empty workspace, pressing only what the
  screen names. `Enter` on step 0 opens the creation panel (an empty workspace has
  exactly one sensible thing to do in it), and `→`, `Enter`, `Esc`, `→`, `→` from
  there reach a `game.yml` that `project validate` accepts, leaving `ABRIR`,
  `OMITIR 1 referencia`, `GUARDAR` and `OMITIR 3 sprites` in the diary with their
  timestamps.
- That walk failed its own acceptance criterion at the first stop, and the fix
  is the rest of this entry. The creation panel could not be worked with the
  keys the wizard teaches: nothing was focused, so the only way to a field was
  `Tab`, which the wizard never names; `Enter` reopened the same panel and did
  nothing; the panel's help named `Esc`, the way out, and nothing about the way
  in; and the `Create` button -- the only control that starts a project -- sat
  below the fold on any terminal shorter than 34 rows, including the classic
  80x24. The panel now focuses its first field on opening, `Enter` creates from
  any field, the help names `Enter`/`Tab`/`Esc`, and the whole form fits 80x24
  with the diary still visible under it, pinned by
  `test_a_project_can_be_created_on_an_eighty_by_twentyfour_terminal`.
- It also had a target and a brief but no title, because `action_create` read
  `#f-title` out of the *design* panel, which is hidden: every project born in
  the wizard was called "My Retro Game". The creation panel has its own
  `#f-create-title`, focused first, and its brief is an `Input` rather than a
  `TextArea` -- `Enter` in a text area inserts a newline, so the one key the
  wizard teaches did nothing in the one field a person was most likely to be
  standing in. The design panel keeps its full text area for writing the brief
  properly afterwards.
- Two more things that walk exposed, both fixed here. `#wizard-summary` was
  pinned to one row, which fitted 120 columns and silently dropped `[→] omitir`
  and the `gasta dinero (API)` warning off the right-hand edge of an 80 -- the
  narrowest screen hid the key that walks past the steps that spend money. And
  refusing to skip `programa` lived five seconds in a toast and was written
  nowhere; it is an `AVISO` line now, because wanting to walk past a step is a
  decision even when the pipeline denies it.
- `Created`, `Opened` and `Saved` were written to the panel and to no file, so
  the diary a person reads and the diary they keep told different stories. They
  are journal lines now (`ABRIR` carries the target, `GUARDAR` replaces
  "Saved"), and the panel and `studio.log` agree line for line -- with one
  stated exception that cannot be otherwise: the workspace banner at mount,
  written before any project exists to own a diary.
