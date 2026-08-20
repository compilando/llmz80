# Changelog

Every notable change to this project is recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and
this project uses [Semantic Versioning](https://semver.org/).

## [Unreleased] - 2026-08-20

### Added

- **What a run costs, counted while it costs it** (`llmz80/studio/spend.py`).
  Nothing read `usage` off a response before this: `llmz80/quality/benchmark.py`
  reserved the four keys and left them `None`, so the only way to learn what a
  game had cost was to read wall-clock times out of `studio.log` and guess at a
  throughput. Every call is now priced by model and attributed to the stage that
  made it, and `llmz80 make` writes the per-stage total into `studio.log` and
  onto the screen. Refused answers are counted too — two of the five stages of
  `studio-projects/cesar-mondongo-basket` were nothing but those.
- **A ceiling a run cannot go through**, in dollars and in calls, from a new
  `budget:` section of `config.yml` (defaults: $12 and 60 calls). That run
  ended after 3.5 hours on `Your credit balance is too low to access the
  Anthropic API` rather than on any decision, because nothing in the pipeline
  knew what it had spent or had the authority to stop. The call ceiling is the
  one that catches a runaway early: the retries here multiply rather than add,
  and the theoretical worst case is about 100 calls, each individually
  reasonable.
- **The schema's own limits, stated to the model** (`llmz80/studio/schema_limits.py`).
  The SDK strips every keyword structured outputs does not support — `maxLength`
  above all — and re-emits it inside the field description as `{maxLength: 240}`,
  which is a dump rather than an instruction. The drafting *and* the design
  stages of that run each produced a whole design and each had it refused for
  `entities.*.notes` at 240 characters: 550 s and 409 s of reasoning, billed and
  discarded, over a rule nobody had told the model. The limits are derived from
  the schema, so they cannot drift from it.
- **A model per kind of question** (`anthropic.models` in `config.yml`,
  `utils.config.model_for`). `design` and `program` stay on Opus; `art` and
  `exam` move to Sonnet. An 8x8 tile of eight pen characters and a
  `coherent: true` were being charged at the same rate as writing a C program.

### Changed

- **Every call site now says what its answer is worth.** `effort` and
  `max_tokens` were left at their defaults everywhere, which meant `high` and
  64000 tokens for a boolean verdict — `llm.py`'s own docstring had named this
  exact case as the one `effort` exists for, and no caller had ever passed one.
  Art draws at `low`, verdicts and examinations at `medium`, the writer keeps
  both defaults. Ceilings bound thinking too, so they bound the bill.
- **The writer's standing context is cached** (`generator.standing_context`).
  About 15 300 of its 15 500 prompt tokens — the design, the platform library,
  the retrieved examples — are identical on all five attempts and were re-billed
  in full each time. They now travel in a `system` block behind a one-hour cache
  breakpoint, leaving about 255 volatile tokens per attempt.
- **The writer is told how much the whole job is worth** (`task_budget`), so it
  paces itself to an ending instead of being cut off at `max_tokens`. Attempt 3
  of that run reasoned for 25 minutes and stopped at `EOF while parsing a string
  at line 1 column 21706` — a full deliberation billed for an answer nothing
  could read. Dropped automatically on models that do not accept the parameter.
- `EXAMINATION_PASSES` 4 → 3. Not a saving on its own: what paid for keeping the
  coverage was making each pass cheaper. Of the 84 three-subsets of the nine
  recorded sittings, one checks nothing on `minero-observable`; of the 36
  two-subsets, three do — so two passes was refused.

## [Unreleased] - 2026-08-18

### Removed

- **The legacy generator, and everything only it reached.** `llm_z80.py`, its
  OpenAI client (`llmz80/api/generator.py`), the whole embeddings and Qdrant
  retrieval stack, the code validators, the learning system, the standalone
  sprite image generators and four shell build scripts: about 11 000 lines.
  Studio replaced it months ago and the newest run it ever wrote is dated
  2026-08-11. `llmz80 <unknown-command>` used to fall through to it; it now
  prints the help text and exits 2.
- Eight runtime dependencies: `openai`, `scipy`, `requests`, `termcolor`,
  `qdrant-client`, `fastembed` and both Google AI SDKs. What is left is
  `anthropic`, `pydantic`, `textual`, `python-dotenv`, `Pillow`, `numpy` and
  `PyYAML`.
- Six `config.yml` sections nothing read (`examples`, `generation`, `logging`,
  `output`, `paths`, `prompt_files`), `resources/platforms.yml`, and the two
  legacy system prompts.
- `scripts/evaluate_generation.py --live`, which shelled out to the deleted
  generator. The scorecard still scores the archive of legacy runs, which its
  docstring now says out loud.
- 99 build artifacts that `.gitignore` already excluded but that were committed
  before those rules existed.

### Fixed

- **`acceptance.step_mismatches` could crash a whole run.** An expectation
  naming neither a `value` nor a `baseline` reached `actual >= None` and raised
  `TypeError`, which nothing catches, so one malformed rule ended the run
  instead of failing its own step.
- **The CPC build depended on the working directory.** The CPCtelera project
  templates were found through a cwd-relative path, so `llmz80 make` started
  anywhere but the checkout root copied no `cfg/` and died inside `make`
  complaining about a missing `build_config.mk`. The Spectrum half of this was
  fixed in 76fd144; the CPC half was not.
- **An unbuilt CPCtelera is now refused where it can be explained.** CPCtelera
  compiles with the SDCC inside its own checkout, which `setup.sh` builds, so a
  bare clone passed every check and then failed with exit code 127.
  `resolve_cpct_path` requires the compiler to exist, and `make doctor` says so.
- `cli._project_command` bound one name to two different result types across
  two branches and read fields off whichever it got; `services.add_asset` took
  a `str` where a four-value `Literal` was required.
- **Two initialised statics in the CPC platform library held garbage.** This
  link does not initialise the DATA segment -- something `apply_palette` had
  already recorded for itself -- so `baselines_left` came up zero and made
  every `plat_frame_baseline()` call a no-op, and `draw_pen` made `plat_ink`
  report a previous pen the program had never set. Both are assigned in
  `plat_init` now.
- The comment in `generator.py` explaining why CPC gates abstain had been wrong
  since ZEsarUX replaced Caprice32: three of the five behaviour gates really do
  watch a CPC game now.

### Added

- **`plat_save_under` / `plat_restore_under`**, so a moving sprite can be
  rubbed out by putting back what was behind it. Found by watching a generated
  CPC Breakout flicker: its loop erased the ball by repainting up to nine tiles
  at the top and redrew it at the bottom, so the ball was absent from the
  picture for the whole of the collision and scoring work between them. Both
  halves were the contract's fault rather than the program's -- repainting
  terrain was the only erase on offer, and nothing said when to draw.

  The backing store belongs to the caller (`SPRITE_UNDER_BYTES`, published per
  target), because two moving actors need two of them and a hidden buffer in
  the library would silently hold only the last. It costs about half the byte
  writes of a terrain repaint and works over anything on the screen, which a
  terrain repaint cannot: text, another sprite, a scrolled backdrop. Proved on
  a real 48K over a background written straight into the bitmap that no tile
  map describes -- with a control build that does not restore, so the test
  cannot pass on a sprite that never reached the screen.

  The writing prompt now also says to draw in the lines straight after
  `plat_wait_frame` and think afterwards, and to restore in reverse draw order
  where actors overlap.
- **Coarse hardware scrolling on the Amstrad CPC.** `plat_scroll_to(origin)`
  moves the whole picture by changing where the CRTC starts reading, which
  costs one register write and no memory movement. A design asks for it with
  `presentation.scrolling`, and a Spectrum design that asks is refused at
  design time with the reason -- that machine has no such register and would
  have to move 6912 bytes.

  Both granularities were measured on a real CPC rather than taken from the
  documentation, because CPCtelera's own examples disagree: one step is **2
  bytes** (4 pixels across in mode 0, 8 in mode 1) and one screen row of them
  moves the picture up by exactly one character row. `advanced/hwscroll`'s
  comment saying four bytes is wrong; `advanced/tilemap_hwscroll` is right.

  Coarse is all it is, and the API says so rather than pretending: sub-step
  horizontal would need the background redrawn shifted and sub-row vertical the
  CRTC's vertical adjust. `origin` reaches 510 bytes, the whole range an
  eight-bit R13 holds, and past that is ignored rather than wrapped -- a
  scroller that wrapped would not look broken, it would look like it jumped.
  Nothing is copied, so drawing the incoming edge stays the program's job, and
  the writing prompt says so.
- **Sprites can sit on a pixel row.** `plat_sprite_py(col, py, sprite, frame)`
  takes a scanline where `plat_sprite` takes a character row, so anything a
  player watches rise or fall moves smoothly instead of in eight-pixel steps.
  Neither machine needs a differently packed sprite for it: z88dk's
  `zx_saddrpdown` steps one pixel line and crosses the Spectrum's non-linear
  thirds by itself, and `cpct_getScreenPtr` had always taken its y in
  scanlines -- `plat_sprite` was multiplying a row by eight to throw that away.
  On the Spectrum a sprite between cells covers three character rows, so the
  blitter colours six attribute cells rather than four. Proved by reading the
  display file out of a running 48K: the sprite's bytes land at pixel row 59,
  across a screen-third boundary.
- **Sprites can move across by single pixels**, when the design asks with
  `presentation.smooth_horizontal`. A byte of screen holds several pixels, so a
  figure whose left edge falls inside a byte has its bits in different
  positions; the packers now emit one copy of every frame per position -- eight
  on the Spectrum, four in CPC mode 1, two in mode 0 -- and
  `plat_sprite_px(px, py, sprite, frame)` picks between them.

  One mechanism rather than three. A shifted copy is the packers' existing
  pixel-by-pixel walk over a canvas one byte wider with the figure pasted `k`
  pixels in, so the Spectrum's one-bit pixels and the CPC's interleaved pens
  come out of the code that was already there with only `pixels_per_byte`
  differing -- no byte rotation, no carry chains, no per-machine bit surgery.
  The blitter finds a copy at
  `sprite_frame_offset[s][f] + shift * SPRITE_SHIFT_STRIDE`, which needs no
  second offset table and no 16-bit multiply.

  It costs twelve times the art on the Spectrum, and `validate_sprite_budget`
  already weighs that against `budgets.static_data_bytes` -- no new gate. A
  design that did not ask still compiles against `plat_sprite_px`; it rounds
  down to the byte, so a program cannot be broken by a decision taken in
  game.yml after it was written. Proved on a real 48K: at pixel column 21 the
  bytes on screen are the copy packed for offset 5, and the same program on a
  design that did not ask draws the plain art five pixels left.
- **`MAX_SPRITE_PY` and `MAX_SPRITE_PX`** in game_config.h, derived from each
  machine's own screen so the library's guard, the macro and the writing
  prompt cannot name three different numbers. `MAX_SPRITE_PX` also allows for
  the extra byte a shifted copy occupies, which moves the bound in both
  directions at once and is exactly the kind of arithmetic that looks right
  when only half of it is written.
- **`FlagValue`** in the planner, so a design can be asked for a yes or a no --
  the first of them being `smooth_horizontal`.
- **The Amstrad CPC counts frames**, so the pacing gate judges it instead of
  abstaining. `cpct_setInterruptHandler` installs a handler the machine calls
  six times per display frame, and counting those sixths is the free-running
  counter the Spectrum reads out of the ROM. Everything downstream mirrors
  `spectrum/platform.c` constant for constant. Read back out of a real CPC: a
  program that spins before its loop reports the gap, and the same program
  with one `plat_frame_baseline()` call reports zero. Both read zero before.
- **Mode 0's sixteen pens are reachable.** The library programmed four pens
  whatever the mode, `plat_ink` refused any index above three, and the drawing
  alphabet offered four characters -- so the only reason to choose mode 0 over
  mode 1 was switched off in software.

### Changed

- **One table decides the CPC's colours.** The RGB the packers quantise
  against and the hardware bytes the library programs used to be written down
  separately, in two files in two languages, and they had drifted: HW_BLUE was
  recorded as (0, 0, 255), which is HW_BRIGHT_BLUE, and HW_WHITE as
  (255, 255, 255), which is HW_BRIGHT_WHITE -- the CPC's "white" is grey. Half
  of every CPC sprite was quantised against colours the machine never showed.
  `palette.HARDWARE_COLOURS` is now the single source and a test pins the two
  halves to each other.
- **The CPC toolchain moved out of the legacy generator** into
  `llmz80/core/toolchain.py`, which was the single import keeping 1 591 retired
  lines in the live pipeline's graph. `vendor/cpctelera` joins the search path,
  so the commit pinned in `ENGINE.json` can finally be what a build uses.
- **Everything is in English** — code, comments, progress lines, the diary's
  stage ids (`referencia` → `reference`, `redacción` → `drafting`, `diseño` →
  `design`, `programa` → `program`), the README and this file. Linguistic data
  stays bilingual on purpose: the Spanish stopwords in the retrieval catalogue,
  the colour and comparison words the palette and runtime examiner match, and
  the bilingual benchmark corpus. A design's own prose is still written in
  whatever language it was briefed in.
  ⚠️ A `studio.log` written before this change uses the old stage ids.
- The sprite preview no longer quantises the sheet against a palette that is not
  the one it was packed with. `studio/preview.py` paints the pixels as they are,
  which is exact, because the sheet was drawn from the packer's own palette.
- CI enforces what it used to only report. `black`, `isort`, `flake8`, `mypy`
  and `bandit` all run over `llmz80`, `tests` and `scripts`, and none of them
  are advisory any more. `black --check` and `isort --check-only` had in fact
  been failing on every push. Flake8 goes from 688 findings to nine complexity
  advisories; mypy from 103 errors to none.
- The Makefile drops the legacy `generate*`, `run*` and `qdrant-*` targets for
  `make game`, `make play` and `make format-check`.

## [Unreleased] - 2026-08-16

### Changed

- **Studio thinks with Claude Opus 5, not GPT-5.** The eight structured calls
  (`drafting`, `reference`, `reference_design`, `planner`, both design
  examiners, `generator`, `runtime_exam`) go through one new adapter,
  `llmz80/studio/llm.py`, instead of repeating the same request eight times.
- **`config.yml` no longer carries `temperature`** in the Studio section: the
  model rejects it with a 400 rather than ignoring it. Nor `reasoning_effort`,
  whose replacement already defaults to the high setting Studio wants.
- `reference.py`'s web search uses the `web_search_20260209` server tool.
- **`ANTHROPIC_API_KEY` is the key Studio needs.**

### Added

- **Sprites are drawn by the model as a grid of palette indices**
  (`llmz80/studio/sprite_grid.py`), not as a 1024×1024 image to rescue a 16×16
  sprite from. Two whole classes of failure stop being possible rather than
  being detected: there is no character for a mid grey, so no antialiasing, and
  no character outside the machine's alphabet, so no colour it cannot show. A
  shape failure — a short row, an empty frame — comes back as a sentence naming
  the frame and the row, and feeds the retry loop that already existed.
- `SpriteArtist` gains a seam, `SheetSource`, with two implementations. The
  retry loop, the judging of frames and the keeping of every attempt are common
  to both.
- Per-machine prompt templates for the grid path (`resources/sprite_grid_*.txt`),
  including the warning that a CPC mode 0 pixel is twice as wide as it is tall.

### Changed (embeddings)

- Embeddings were computed locally with `fastembed`
  (`BAAI/bge-small-en-v1.5`), no API key and no network call.
- ⚠️ Vectors went from 1536 to 384 dimensions; older collections and caches had
  to be recreated rather than migrated.

*(Both entries are historical: the embeddings stack was removed on 2026-08-18.)*

## [Unreleased] - 2026-06-02

### Added

- A gap report and improvement plan for Z80 assembly retro vibe-coding on the
  Amstrad CPC (`docs/RETRO_VIBE_CODING_GAP_REPORT.md`).
- A self-contained CPCtelera `main.c` contract, in the prompt, the validation
  and retrieval.
- Safe deterministic fixes applied to generated CPCtelera code before compiling.
- A record of the build environment, and verification of `.dsk` / `.tap`
  artifacts.

### Changed

- The CPCtelera validator treats unknown `cpct_*` functions, problematic
  standard APIs, local includes and initialisation-order errors as critical
  failures.
- Amstrad CPC retrieval examples are filtered towards self-contained snippets
  compatible with the `main.c` contract.
- Fixed validator false positives from comments containing parentheses,
  semicolon heuristics, and declarations before `cpct_disableFirmware()`.
- Corrected the CPCtelera documentation for `cpct_drawCharM*()` and for the
  random functions the local install really has.

## [Unreleased] - 2024-11-20

### Added

- Documentation for AI coding assistants, a Cursor rules file, a contribution
  guide, an MIT licence file, a rewritten README, development dependencies and
  this changelog.

### Changed

- `requirements.txt` reorganised, with `python-dotenv` and `termcolor` pinned
  to earlier releases.

---

## Commit conventions

[Conventional Commits](https://www.conventionalcommits.org/): `feat`, `fix`,
`docs`, `style`, `refactor`, `test`, `chore`.

## Release process

1. Update the version where it appears
2. Update this file
3. `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
4. `git push && git push --tags`
5. Open a GitHub release with the notes from this file
