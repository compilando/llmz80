# LLMZ80

Make a playable ZX Spectrum or Amstrad CPC game from one sentence, and prove it
runs before calling it finished.

You describe the game. Studio designs it, draws its art, writes the C, builds it
with the machine's real toolchain, boots the result in an emulator, presses keys
at it and reads the running program's memory to check it did what the design
said it would. A game that compiles but does not behave is refused and rewritten.

```bash
llmz80 make "a miner crosses stone ledges, jumping between them, to reach the keys"
```

Out the other end: `output.tap` (or `output.dsk`), the sources it was built
from, and the evidence for every claim made about it.

---

## Contents

- [What it does](#what-it-does)
- [Requirements](#requirements)
- [Install](#install)
- [Configure](#configure)
- [Use](#use)
- [Evidence](#evidence)
- [The two machines](#the-two-machines)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Licence](#licence)

---

## What it does

`llmz80 make` runs six stages, in order, and stops at the first one that cannot
honestly finish.

| Stage | What happens |
|---|---|
| **reference** | Searches the web for the game the brief sounds like, and archives what it finds |
| **drafting** | Writes the design: tiles, entities, mechanics, controls, palette, screens |
| **design** | Adapts that design towards the researched game, as a diff you can refuse |
| **sprites** | Draws each entity's 16×16 sheet and each tile's 8×8 block, in the target's real palette |
| **program** | Writes the C, builds it, and rewrites it against the compiler and the gates until it passes or runs out of attempts |
| **gates** | Boots the binary, presses each declared key, reads memory, and judges what it saw |

The design is a versioned document (`game.yml`) you can read and edit between
any two stages. Nothing is hidden in a prompt.

**What is not generated:** the engine. There isn't one. Studio writes a small
platform library (`plat_sprite`, `plat_tile`, `plat_text`, `plat_input`,
`plat_wait_frame`, …) that is identical in shape on both machines, and the model
writes the game against it in ordinary C. The program is the artifact of record.

**How a game is judged.** Not by pixels. The design declares observables —
`g_score`, `g_lives`, whatever counters its own rules need — the program defines
them at file scope, the linker map says where they live, and the emulator reads
those addresses after each scripted keypress. "The score rose when the player
collected something" is then a measurement rather than an impression.

---

## Requirements

| | |
|---|---|
| Python | 3.10 – 3.13 |
| Anthropic API key | required — this is the only paid service used |
| **ZX Spectrum** | [z88dk](https://z88dk.org/) (`zcc`) |
| **Amstrad CPC** | [CPCtelera](https://github.com/lronaldo/cpctelera), set up with its own `setup.sh` |
| Emulator | [ZEsarUX](https://github.com/chernandezba/zesarux) — drives the quality gates on **both** machines, because it is the one that speaks a protocol the harness can read memory through |

Caprice32 and CPCEC work for playing a finished CPC game, but not for judging
one.

---

## Install

```bash
git clone https://github.com/compilando/llmz80.git
cd llmz80
make setup          # creates .venv, installs, writes .env from the example
make doctor         # checks Python, the key, both toolchains and the emulators
```

`make doctor` is the one that tells you what is missing, including the CPCtelera
trap below.

### z88dk (ZX Spectrum)

```bash
# Arch
yay -S z88dk
# Debian / Ubuntu
sudo apt install z88dk
# macOS
brew install z88dk
```

### CPCtelera (Amstrad CPC)

CPCtelera does **not** build with your system SDCC. It bundles its own under
`tools/sdcc-*/`, and `setup.sh` is what puts it there — a clone alone compiles
nothing and fails with `sdcc: No such file or directory`.

```bash
git clone https://github.com/lronaldo/cpctelera.git ~/cpctelera
cd ~/cpctelera
./setup.sh                       # downloads and builds the toolchain; takes a while
export CPCT_PATH=~/cpctelera/cpctelera
```

`resolve_cpct_path` looks for a **set-up** CPCtelera in this order: `$CPCT_PATH`,
`compiler.amstrad_cpc.cpct_path` in `config.yml`, this repository's vendored
checkout under `vendor/`, then `~/cpctelera{,/cpctelera}` and `/opt/cpctelera`.
One that has not been set up is refused here rather than at the link step.

---

## Configure

### `.env`

```bash
ANTHROPIC_API_KEY=sk-ant-...
```

Get one at <https://console.anthropic.com/settings/keys>.

### `config.yml`

Three sections, all of them read:

```yaml
anthropic:
  model: claude-opus-5

compiler:
  spectrum:
    c_compiler: "zcc"
    params: "+zx -vn -O3 -clib=sdcc_iy"
  amstrad_cpc:
    c_compiler: "sdcc"
    params: "-mz80 --sdcccall 0 --no-std-crt0"   # CPCtelera needs the classic stack ABI

emulator:                                        # what `llmz80 play` opens
  spectrum:  {name: "zesarux", params: "--machine 48k"}
  amstrad_cpc: {name: "cap32", params: "--machine 6128"}
```

There is deliberately no `temperature` and no `reasoning_effort`: this model
family rejects the first with a 400, and the second's replacement already
defaults to the setting Studio wants.

---

## Use

### One command

```bash
llmz80 make "a miner crosses stone ledges to reach the keys"
llmz80 make "four ghosts chase you around a maze" --cpc --workspace ~/games
llmz80 make "single-player pong with a score" --play      # opens the emulator when it is done
```

Or through the Makefile:

```bash
make game BRIEF="a miner crosses stone ledges to reach the keys"
make game BRIEF="four ghosts chase you around a maze" PLATFORM=amstrad_cpc
```

### Watching it work

`llmz80 make` runs in the terminal you typed it in. In another one:

```bash
make studio                        # or: make studio WORKSPACE=~/games
llmz80 studio ~/games/cave-runner  # or follow one project
```

A screen that does no work, decides nothing and writes nothing. It shows the
project's identity, a six-step strip with each step's state (`✓` done, `✗`
failed, `—` still to do), the diary as it is written, and the verdict.

Six steps, not seven: `release` is a deliberate act, not part of the order, so
the strip never carries a stage that will read `—` for the life of every game.

Nothing tells it anything. The strip is read off the evidence each stage leaves
on disk and the diary is followed line by line out of `<project>/studio.log`, so
the file and the screen cannot tell different stories, the run survives the
screen closing, the screen survives the run crashing, and yesterday's run can be
looked at this morning with the same command. Pointed at a workspace it follows
whichever project was written to last, so you can open it before starting a run.

`q` quits.

### Stage by stage

```bash
llmz80 project types                              # kinds of game, for inspiration
llmz80 project new ~/games "Cave Runner" spectrum \
    "The miner crosses ledges to reach the keys. Falling off costs a life."

P=~/games/cave-runner
llmz80 project validate $P     # the design, without building
llmz80 project contract $P     # what a program must satisfy
llmz80 project reference $P    # searches the web, archives the dossier   [API]
llmz80 project draft $P        # writes the design the brief asks for     [API]
llmz80 project adapt $P        # proposes a design diff, asks to apply    [API]
llmz80 project sprites $P      # draws the art, previews it in the terminal [API]
llmz80 project write $P        # writes and repairs the program           [API]
llmz80 project scaffold $P     # lays out the buildable project
llmz80 project build $P
llmz80 project test $P         # emulator, reading memory
llmz80 project release $P      # a zip, with its evidence
```

Each step runs what precedes it, so `test` builds and `release` refuses unless
every gate passed **and** at least one behaviour gate actually watched the
program run — a build whose gates all abstained is a candidate, not a release.
Exit codes are 0 or 1, so they compose in CI.

### Playing one

```bash
llmz80 play ~/games/cave-runner
llmz80 play game.tap
make play TARGET=~/games/cave-runner
```

---

## Evidence

Everything a run claims, it leaves behind:

```
build/studio_quality_report.json   design, build and runtime gates
build/emulator_report.json         what memory read after each scripted input
build/probes.json                  where that state sits in the binary
build/build_report.json            the compiler's own words, and the artifact
build/CONTRACT.md                  what the program was asked to satisfy
build/main.c, build/src/           the sources it was built from
write_report.json                  each attempt, and what was fed back
studio.log                         the diary
```

A design that builds and runs is still refused if a level is unsolvable, if the
target cannot produce the audio it asks for, or if the screen never changes.

---

## The two machines

They are not at parity, and it is worth knowing where.

| | ZX Spectrum | Amstrad CPC |
|---|---|---|
| Toolchain | z88dk | CPCtelera |
| Artifact | `.tap` | `.dsk` |
| Screen | 32×24 cells | 20×25 (mode 0) or 40×25 (mode 1) |
| Colour | one attribute per 8×8 cell | pens in the pixels — no clash |
| Pens | 8 inks × 2 brightnesses | 16 (mode 0) or 4 (mode 1) |
| Sound | beeper, five effects | **none implemented** (`plat_sound` is a no-op) |
| Build gate | ✅ | ✅ |
| Acceptance / animation / state probe | ✅ | ✅ (ZEsarUX reads its memory over ZRCP) |
| Pacing gate | ✅ | ✅ (a 300 Hz interrupt handler counts the six ticks per frame) |
| Attribute gate | ✅ | ⛔ abstains — a CPC screen has no attribute area; judging its colour wants a different gate |

The one CPC gap left is sound: `plat_sound` is a no-op and the design gate
refuses any CPC project that asks for audio. CPCtelera bundles Arkos Tracker,
which is where the fix starts.

And a limit that is not about either machine: every position is a character
cell on both, so nothing moves by less than eight pixels and nothing scrolls.
Vertical sub-cell movement is close to free — `cpct_getScreenPtr` already takes
a pixel row and z88dk has `zx_pxy2saddr` — while horizontal needs pre-shifted
sprite variants, eight on the Spectrum and two or four on the CPC.

---

## Architecture

```
llmz80/
  cli.py              the commands
  studio/             the pipeline: design, art, codegen, build, gates
    models.py           the versioned design document (schema v4)
    drafting.py         writes a design from a brief
    reference.py        researches the game the brief sounds like
    sprite_artist.py    draws sheets and tiles as palette grids
    spriting.py         packs those into Spectrum and CPC sprite bytes
    codegen.py          game_config.h, game_state.h, the platform library
    compiler.py         lays out and builds the project
    probes.py           finds engine state in the linker map
    observation.py      the script the emulator drives
    acceptance.py       what the readings had to show
    feel.py             did it animate
    pacing.py           did the loop fit in its frame
    attributes.py       could a player see it
    generator.py        write, judge, repair, repeat
    make.py             the whole order, and the diary
    tui.py, screen.py   the watching screen
  core/
    state_contract.py   the symbols every program exposes
    toolchain.py        where the toolchains are, and whether they work
    example_catalog.py  the local retrieval corpus
  quality/
    emulator_smoke.py   ZEsarUX over ZRCP, both machines
  utils/

resources/
  studio_lib/         platform.h and one platform.c per machine
  studio_reference/   a complete maze game per machine: proof the gates work
examples/             compiling z88dk and CPCtelera programs, for retrieval
templates/amstrad_cpc/  the CPCtelera project skeleton
```

### Development

```bash
make install-dev
make test              # pytest
make check             # tests + compile every retrievable example
make format            # isort + black
make quality-gate      # everything CI runs
```

CI runs flake8 (syntax errors fail), black, isort, mypy and bandit across
`llmz80`, `tests` and `scripts`. None of them are advisory.

---

## Troubleshooting

**`ANTHROPIC_API_KEY is required`** — put it in `.env` or the environment.

**`CPCtelera was not found; configure CPCT_PATH`** — either it is not installed,
or it is installed but never set up. `make doctor` distinguishes the two. A
clone without `setup.sh` has no compiler inside it.

**`sdcc: No such file or directory` from `make`** — the same thing, from an
older checkout that predates the set-up check.

**The Spectrum build fails on `zcc`** — check `zcc +zx --version`. The exact
command Studio runs is in `build/build_report.json`.

**The gates all abstain** — the emulator driving them is ZEsarUX and nothing
else. `zesarux --version`. Without it the pipeline still builds a game; it just
cannot say whether it works.

**A CPC game passes with less evidence than a Spectrum one** — expected, see
[The two machines](#the-two-machines).

**The emulator opens nothing** — `llmz80 play` uses whatever `config.yml` names,
which is not necessarily what the gates use. The artifact is in
`<project>/build/` either way.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Areas that want help:

- CPC audio, through CPCtelera's bundled Arkos Tracker
- A colour gate for the CPC, since the Spectrum attribute gate has no meaning
  there
- Sub-cell movement and scrolling (see the table above)
- More retrieval examples, for both machines

---

## Licence

MIT — see [LICENSE](LICENSE).

Built on [z88dk](https://z88dk.org/), [CPCtelera](https://github.com/lronaldo/cpctelera)
and [ZEsarUX](https://github.com/chernandezba/zesarux), none of which are ours
and all of which are why this works.
