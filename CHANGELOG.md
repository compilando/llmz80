# Changelog

Every notable change to this project is recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and
this project uses [Semantic Versioning](https://semver.org/).

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
