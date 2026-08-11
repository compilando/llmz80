# LLMZ80 Studio delivery roadmap

This is the durable execution record for the project-first guided game creator. A stage is only
marked complete when its acceptance evidence exists in the repository or test output.

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

- `game.yml` (GameProject schema v3) is the editable source of truth.
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
| S06 | Asset pipeline | In progress | Project-owned image import and deterministic Spectrum/CPC packing; imported assets are not yet referenced by the generated C, which draws primitives |
| S07 | Structured AI design assistance | Implemented | Responses typed proposals, visible diff, separate apply action and protected contracts |
| S08 | Automated gameplay QA | In progress | Design, build and runtime gates plus solvability analysis and, on Spectrum, memory-probed assertions that a scripted sweep scores exactly what the design predicts; CPC state probes and life/level transitions next |
| S09 | Commercial vertical slices | In progress | Quality-gated reproducible release archive; content/presentation polish next |
| S10 | Extension SDK | Implemented | Public typed protocols, entry-point groups, compatibility rules and installable example |

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

Still open:

- Imported assets are normalised and packed, but the engine draws built-in cell shapes and never
  references them. Masked sprite blitting is required before assets reach the screen.
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
- `presentation.palette` is unused; both targets draw with fixed pens.
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
- The probe proves that collecting scores. It does not yet prove that a collision costs a life or
  that clearing a level advances it; both need a scripted encounter rather than a single sweep.

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
| P6 | Real playability probes: export the toolchain symbol map to `probes.json` and assert score, lives and level transitions from memory during a scripted input replay | S08 and S09 as claimed | **Partly done.** Both toolchains export `probes.json`. On Spectrum a scripted sweep collects a predicted number of items and the gate asserts the resulting score and remaining count from memory. Lives and level transitions are not scripted yet, and the CPC abstains for lack of a memory adapter |
| P7 | Advanced AI design assistance over tilemaps, per-genre polish, loading screen, high-score table, tape and disk mastering | commercial release | **Partly done.** AI proposals are refused when they would leave the game unplayable, and a high score is kept and probe-verified on target. Loading screen, tape and disk mastering and per-genre polish are **not** delivered |

Not yet covered anywhere above and still required for a commercial claim: masked sprite blitting,
loading screen, and tape and disk mastering. The high score is kept in memory only; neither target
has storage here, so it does not survive a power cycle.

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
