# Generation quality roadmap

This file is the persistent source of truth for the generation-quality programme.
Update the status table and progress log in the same change that completes a task.

Status values: `pending`, `in_progress`, `blocked`, `complete`.

## Objective

Turn LLMZ80 from a generator that usually compiles into a generator that
reliably produces relevant, playable, resource-conscious Spectrum and Amstrad
CPC applications from prompts.

## Completion policy

A task is complete only when:

1. its implementation and automated tests are present;
2. its acceptance command passes;
3. user-facing behaviour is documented;
4. evidence is recorded in the progress log below.

The full programme is complete when all tasks are complete and `make quality-gate`
passes on both installed toolchains.

## Status

| ID | Task | Depends on | Status | Acceptance evidence |
| --- | --- | --- | --- | --- |
| Q01 | Strict build contract and warning policy | — | `complete` | Correct Spectrum subtype flag; unexpected source/tool warnings fail the quality gate; canonical non-empty artifacts and resource reports |
| Q02 | Reproducible prompt benchmark and scorecard | Q01 | `complete` | Versioned bilingual corpus covering both platforms; offline and live runners; JSON/Markdown report with quality metrics |
| Q03 | Deterministic `GenerationSpec` before C generation | Q02 | `complete` | Prompt becomes a validated spec containing behaviour, controls, states, presentation, timing and budgets; spec saved with every run |
| Q04 | Platform runtimes and archetype templates | Q03 | `complete` | Proven frame, input, sprite, collision and HUD primitives; generated code targets the narrow runtime contracts |
| Q05 | Capability-aware example metadata and retrieval | Q02 | `complete` | Every retrievable program has useful metadata; irrelevant/zero-score examples are excluded; bilingual retrieval tests pass |
| Q06 | Whole-context composer with evidence provenance | Q05 | `complete` | Small complete examples/capability excerpts only; no middle-of-program truncation; token budget and provenance saved |
| Q07 | Semantic validation and resource budgets | Q03,Q04 | `complete` | Detect timing, coordinate, bounds, redraw and state-machine risks; enforce code/data/RAM budgets from build outputs |
| Q08 | Automated emulator smoke and visual QA | Q02,Q07 | `complete` | Scripted boot, frame capture and input scenarios; non-blank/motion/HUD/end-state assertions where emulator supports them |
| Q09 | Controlled project/assets output mode | Q04,Q07 | `complete` | Fixed build templates support generated `main`, runtime and asset modules; deterministic sprite/tile conversion; single-file mode retained |
| Q10 | Quality-gated learning and candidate selection | Q02,Q03,Q07,Q08 | `complete` | Immutable run history; honest metrics; promotion only after quality evidence; optional multi-candidate compile/score/select flow |
| Q11 | Real execution gate and CPC ABI compatibility | Q01,Q08,Q10 | `complete` | ZEsarUX/Caprice32 boot, framebuffer and input evidence; CPCtelera builds force SDCC ABI 0; static evidence cannot promote learning |
| Q12 | Overflow-safe generation and repair completion | Q06,Q07,Q11 | `complete` | Range-aware fixed-point validation; quality-warning retries; relevant large-example context; compatible Qdrant client; warning-free CPC build and full CPC/Spectrum runtime evidence |
| Q13 | Live bilingual corpus hardening | Q02,Q07,Q08,Q12 | `complete` | 20/20 live cases build and pass real emulator QA; 90% first-build and 100% final-build rates; 0 unexpected final warnings; 113 tests and 53/53 catalog builds pass |
| Q14 | Maze-game intent, warning-357 and retrieval hardening | Q03,Q05,Q07,Q12 | `complete` | `comecocos`/Pac-Man maps to an interactive maze contract; const sprites compile without warning 357; learned context is metadata-preserving and content-deduplicated; rejected builds do not publish canonical DSKs |

## Task details

### Q01 — Strict build contract and warning policy

- Replace the ignored Spectrum `--subtype=tap` option with the verified
  `-subtype=default` contract, which produces the canonical TAP.
- Parse compiler output into SDK noise, generated-source warnings and structural
  build warnings.
- Save machine-readable `build_report.json` with command, return code, warnings,
  artifacts and code/data sizes.
- Reject missing/empty canonical artifacts and ignored/unknown options.
- Acceptance: unit tests, real minimal builds and complete catalog audit.

### Q02 — Reproducible prompt benchmark and scorecard

- Add a versioned bilingual prompt corpus with explicit required behaviours.
- Provide an offline evaluator for saved/generated source and a gated live runner.
- Record first-build success, repaired success, warning count, binary size,
  retrieval relevance, latency, calls and estimated token usage.
- Acceptance: deterministic report generation without API access; optional live
  results never overwrite the baseline implicitly.

### Q03 — Deterministic `GenerationSpec`

- Parse user intent into a typed, validated intermediate representation.
- Prefer deterministic extraction; use an optional model planner only for
  ambiguous/complex requests.
- Persist `generation_spec.json` and use it in generation, correction and QA.
- Acceptance: bilingual fixtures map to stable platform-aware specifications.

### Q04 — Platform runtimes and archetype templates

- Provide compile-certified primitives for frame pacing, input edges, sprites,
  dirty redraw, collision and text/HUD operations.
- Select a minimal archetype: static display, animation, collect game, platform
  movement, board game, scrolling scene or custom.
- Acceptance: runtime examples compile and benchmark prompts use the intended
  primitives rather than reimplementing hardware access.

### Q05 — Capability-aware metadata and retrieval

- Add curated/inferred metadata: description, capabilities, controls, video
  mode, APIs, assets, complexity and quality tier.
- Expand bilingual intent vocabulary and stop words.
- Apply a relevance threshold and deliberate foundation fallback.
- Keep learned code in a separate, quality-gated retrieval tier.
- Acceptance: golden retrieval tests for every benchmark intent.

### Q06 — Whole-context composer

- Replace character head/tail truncation with complete functions or complete
  compact programs.
- Select evidence by requested capability and API surface, not a fixed count.
- Keep local and vector scores calibrated and retain source provenance.
- Acceptance: no truncated C constructs and context stays within configured
  token budget.

### Q07 — Semantic validation and resource budgets

- Add checks for frame pacing, screen coordinate units/bounds, arithmetic
  overflow, sprite erase/redraw hazards, unreachable end states and excessive
  full-screen work.
- Parse Spectrum map/symbol output and CPC map/binary output.
- Define platform/archetype budgets with actionable diagnostics.
- Acceptance: known bad fixtures fail before API repair; known good runtimes pass.

### Q08 — Emulator smoke and visual QA

- Define an emulator adapter interface and capability discovery.
- Support bounded launch, screenshots and scripted input where the configured
  emulator exposes reliable automation.
- Add portable fallback checks when full automation is unavailable.
- Acceptance: fixtures demonstrate boot/non-blank output and at least one
  observable state transition per platform.

### Q09 — Controlled project/assets mode

- Generate only inside fixed, owned templates.
- Support `src/main.c`, runtime modules and generated asset modules without
  allowing arbitrary build-file generation.
- Add deterministic monochrome Spectrum and CPC mode 0/1 sprite converters.
- Acceptance: project-mode fixtures compile to TAP/DSK; missing assets fail
  before compilation; single-file output remains supported.

### Q10 — Quality-gated learning and candidate selection

- Store immutable generation runs instead of overwriting by prompt hash.
- Separate generation outcomes from compilation attempts and calculate honest
  denominators.
- Promote examples only with compiler, semantic and (when available) emulator
  evidence or explicit user rating.
- For configured complex prompts, generate multiple candidates, run the same
  gates and keep the highest-scoring result within a call/cost budget.
- Acceptance: migration tests for existing learning JSON, deterministic scoring
  tests and no unreviewed learned example entering RAG.

### Q11 — Real execution gate and CPC ABI compatibility

- Run both canonical artifacts in bounded emulator processes without requiring
  a visible desktop.
- Capture machine framebuffers before and after source-aware input injection.
- Reject BASIC-only startup, blank output and absent observable transitions.
- Compile CPCtelera projects with the classic SDCC calling convention required
  by its prebuilt assembly bindings.
- Acceptance: both reviewed flea artifacts pass real execution; the CPC build
  assembly pushes CPCtelera stack arguments; static-only evidence cannot enter
  learned RAG.

### Q12 — Overflow-safe generation and repair completion

- Reject constant expressions and fixed-point formats that exceed their declared
  integer type before invoking SDCC.
- Route actionable source warnings through the normal correction loop instead of
  stopping after a successful compiler exit.
- Admit at least one high-relevance complete example that fits the global context
  budget, even when it exceeds the small-example preference.
- Keep the Qdrant Python client within the server compatibility window.
- Acceptance: the rejected CPC flea case is caught pre-build, repaired with the
  intended features intact, compiles warning-free and passes full runtime QA.

### Q13 — Live bilingual corpus hardening

- Run all 20 Spanish/English benchmark prompts through the real API, compiler
  and emulator stacks with resumable, cost-bounded execution.
- Turn every repeated live failure into a deterministic validator, fixer,
  prompt-contract or emulator-adapter regression instead of relying on retries.
- Make scorecard retrieval metrics accept the persisted list-shaped provenance
  format and report the real capability recall.
- Acceptance: every case has a quality-passing build and full runtime report;
  the complete automated suite and catalog audit pass after all live fixes.

### Q14 — Maze-game intent, warning-357 and retrieval hardening

- Map Spanish and English Pac-Man/comecocos requests to an explicit four-way
  maze-collect contract with input, tiles, collision, collectibles, score,
  frame pacing and a finite end state.
- Reject static mockups that do not implement the requested gameplay mechanics.
- Detect and deterministically repair SDCC warning 357 caused by casting
  constant CPC sprite arrays to `void*`; retain the compiler-clean source form.
- Preserve learned-example capabilities, controls, APIs, video mode, archetype,
  quality tier and content hash in Qdrant. Apply a relevance floor, capability
  coverage, content-hash deduplication and a learned-context diversity cap.
- Gate a toolchain-named DSK candidate first and publish `output.dsk` only after
  build warnings, semantic checks and resource budgets pass.
- Acceptance: exact prompt/spec, semantic rejection, deterministic repair,
  real CPCtelera warning fixture, retrieval and staged-artifact regressions;
  full quality gate and catalog audit.

## Quality metrics

The scorecard must report at least:

- first-build compile rate;
- final compile rate and model repair count;
- unexpected compiler warnings;
- canonical artifact and program binary size;
- retrieval precision against expected capabilities;
- semantic validation errors/warnings;
- emulator boot, visual-change and scripted-input results;
- user/runtime quality rating;
- API calls, latency and token usage when available.

## Progress log

### 2026-08-09 — Programme started

- Created this persistent roadmap and acceptance policy.
- Baseline before Q01: 42 Python tests pass and 53/53 catalog entrypoints compile.
- Recent prompt runs compile on the first build, but review found an ignored
  Spectrum compiler option, weak retrieval for vague prompts, compile-only
  learning promotion and no runtime/visual verification.
- Q01 moved to `in_progress`.

### 2026-08-09 — Q01 complete

- Replaced the ignored Spectrum subtype argument with the verified
  `-subtype=default` Z88DK contract everywhere it is used or documented.
- Added warning classification and a stable `build_report.json` containing the
  command, status, canonical artifact, all artifacts, payload size and warnings.
- Structural, generated-source and unknown warnings now fail build quality even
  when the compiler exits successfully; known SDK and optimizer diagnostics are
  retained separately.
- Evidence: 45/45 Python tests pass, both minimal real-toolchain contracts pass,
  and `make audit-examples` compiles 53/53 retrievable programs.
- Q02 moved to `in_progress`.

### 2026-08-09 — Q02–Q06 complete

- Added `core-bilingual-v1`, a 20-case Spanish/English corpus for both platforms,
  deterministic JSON/Markdown scorecards and an explicitly gated live runner.
- Every run now persists a deterministic GenerationSpec; generation and repair
  must preserve its capabilities, states, timing and memory budgets.
- Added real-toolchain-tested Spectrum/CPC runtime primitives plus seven
  archetype loop contracts.
- Retrieval now carries inferred capability/API/video/complexity metadata,
  rejects zero-relevance entries and passes golden checks for every corpus case.
- Context composition keeps only complete programs and records hashes, token
  estimates, selection and drop reasons in `prompt_context.json`.

### 2026-08-09 — Q07–Q10 complete

- Semantic reports detect missing 50 Hz pacing, bounds errors, unsafe redraw,
  unsigned-coordinate risks, absent end states and static/binary budget excess.
- Added portable TAP/DSK smoke evidence and bounded ZEsarUX raw-frame capture;
  the reviewed Spectrum flea TAP boots and changes frames headlessly. CPC uses
  explicit portable evidence where Caprice32 does not expose frame capture.
- Added fixed project output, deterministic Spectrum/CPC mode 0/1 image packing,
  permitted module contracts and real TAP/DSK project-build fixtures.
- Learning uses immutable JSONL runs and honest derived statistics. Legacy and
  compile-only examples remain unpromoted; Qdrant rejects learned payloads
  without quality evidence. `--candidates 2|3` compiles, gates, scores and keeps
  the best bounded candidate.
- Final evidence: `make quality-gate` passes with 80 tests and 53/53 catalog
  builds. The offline scorecard is generated reproducibly; live corpus coverage
  remains opt-in because it consumes API calls.
- `make lint` passes its repository-wide critical-error profile and `make doctor`
  confirms both Python/toolchain/emulator stacks are available.

### 2026-08-10 — Q11 real-machine runtime gate complete

- Replaced CPC source heuristics with a bounded Caprice32 run using its own
  virtual-key queue and internal framebuffer screenshots under SDL dummy video.
- Added real ZEsarUX input through ZRCP and before/after screen capture; portable
  artifact checks are now explicitly marked as non-runtime evidence.
- Runtime evidence requires program load, non-blank output and an observable
  transition after scripted input. Only this evidence, or an explicit user
  rating, can promote a generated example into learning/RAG.
- Added `--runtime-check`; `make run-spectrum` and `make run-cpc` now require
  this gate before opening the interactive emulator, and candidate selection
  rejects a candidate whose requested full-runtime check failed.
- Found and fixed a foundational CPC toolchain defect: SDCC 4.6 defaulted to ABI
  1 while CPCtelera's prebuilt bindings require classic stack ABI 0. Generated
  CPC projects now compile and link with `--sdcccall 0`; an integration test
  verifies that the video-memory pointer is actually pushed before
  `cpct_clearScreen()` calls CPCtelera.

### 2026-08-10 — Q12 overflow-safe repair completion

- Added constant-expression range analysis for CPC/Z80 integer types. The
  validator now rejects signed i16 8.8 full-screen coordinates and SDCC warning
  158 implicit u8 conversions before compilation; CPC generation and repair
  instructions prescribe i16 10.6 or i32 8.8 explicitly.
- A successful compiler exit with generated-source warnings now enters the same
  bounded correction loop as a compiler error. An integration test proves that
  warning 158 is sent to the repair model and that the corrected second attempt
  is accepted.
- Context composition admits one complete, high-relevance example up to 18,000
  characters before applying the 9,000-character preference to later examples.
  This prevents the relevant CPC movement examples from all being discarded.
- Pinned the optional service to `qdrant/qdrant:v1.18.3` and the Python client to
  1.18.0. A real query against the installed 1.19.0 server returned results
  without the previous compatibility warning.
- Canonical CPC artifacts now come from the newest non-canonical build output,
  so a stale `output.dsk` cannot survive a rebuild. Caprice32 input timing now
  captures an immediately observable transition instead of waiting until a
  jump has returned to its starting frame.
- Repaired `local/20260810_090230_una-pulga-que-salta-por-la-pantalla` with
  signed 10.6 physics and an explicit checked u8 conversion. Its build report
  records zero unexpected warnings and its full Caprice32 report passes boot,
  load, non-blank output and visual transition. The equivalent Spectrum flea
  also passes full ZEsarUX runtime QA.
- Final evidence: 93/93 Python tests, lint, doctor, 53/53 real catalog builds and
  `make quality-gate` pass. All roadmap tasks are complete; live 20-case API
  benchmark population remains an explicit cost-bearing opt-in.

### 2026-08-10 — Q13 live bilingual corpus hardening complete

- Executed all 20 `core-bilingual-v1` prompts against GPT-5 with compilation
  and full ZEsarUX/Caprice32 runtime checks. The final scorecard records 20/20
  coverage, 90% first-build success, 100% final-build success, five recorded
  build repairs and zero unexpected final compiler warnings.
- Hardened high-byte handling for standard and CPCtelera byte types, including
  decimal/hex assignments and platform-correct macro casts (`uint8_t` versus
  `u8`). Typed byte macros and constants now propagate safely through semantic
  validation without false warning-158 failures.
- Rejected CPC runtime division/modulo before compilation because its helper
  routines conflict with the enforced CPCtelera SDCC ABI. Generation now uses
  shifts, masks, lookup tables or bounded subtraction instead.
- Made prevalidation repairs revalidate and refresh semantic evidence before a
  build; added exact-prompt resume support so passed live cases incur no repeat
  API cost.
- Made CPC draw-character argument repair type-aware and idempotent, expanded
  end-state recognition (`g_state`, `ST_FINISHED`, related conventions), and
  require certified platform input reads when the GenerationSpec requests input.
- Removed emulator false negatives caused by second-resolution screenshot name
  collisions, periodic animations returning to the sampled frame, irrelevant
  Space input in running states and cursor input on title screens. A bounded
  fallback capture now distinguishes periodic animation from static output.
- Corrected scorecard parsing for list-shaped retrieval provenance. Mean
  capability recall is 60% rather than the previous erroneous 0%.
- Recorded GPT-5 usage for this live hardening run: 282,849 input tokens and
  251,589 output tokens across 37 completed calls in 26 generated run folders,
  estimated at USD 2.8695 using the published GPT-5 token rates (embedding calls
  excluded).
- Final deterministic evidence: 113/113 Python tests and 53/53 catalog programs
  compile. `local/quality/live_full.json` and `.md` contain the persisted live
  scorecard; all roadmap tasks are complete.

### 2026-08-10 — Q14 maze-game and retrieval hardening complete

- The reported `un comecocos de una Abogada que se llama IV` prompt now maps to
  `maze_collect_game` instead of `static_display`. Its spec requires four-way
  input, sprites, tiles, collisions, collectible state, HUD/score, 50 Hz pacing
  and a finished state.
- Maze semantic validation rejects the original draw-once mockup and requires
  evidence of a maze model, collectible state, collision test, score state and
  player updates in addition to the existing input/frame/end-state gates.
- Added pre-build detection and deterministic removal of `(void*)` casts on
  constant `cpct_drawSprite` data. The exact two-sprite warning-357 fixture now
  compiles under the installed CPCtelera toolchain without generated warnings.
- Qdrant learned points now use content-stable IDs and retain generation
  metadata. Retrieval applies a score floor and capability overlap, limits
  learned examples to half the context and deduplicates identical source hashes
  even when timestamps/paths differ.
- CPC builds now gate `program.dsk` as a candidate. `output.dsk` is copied only
  after build quality passes, and previous canonical files are preserved outside
  the DSK glob while a retry is evaluated.
- Evidence: 126/126 Python tests, lint, the real warning-357 CPCtelera fixture,
  53/53 catalog builds and `make quality-gate` pass.
