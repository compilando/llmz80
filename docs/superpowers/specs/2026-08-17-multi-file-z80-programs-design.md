# Generated programs as real projects

Design, 2026-08-17. Approved by Oscar in conversation before this document was written.

## The problem

A finished game arrives as one `main.c`. The Arkanoid this design was written against is
474 lines and 23 functions in a single file — every rule, every draw call, every scene
transition, the HUD and the level layout in one translation unit.

Nothing forbids more files. `ProgramSources` already accepts a list of `.c`/`.h` sources,
`compiler.program_sources` globs whatever the program directory holds, both toolchains
compile by glob (`src/*.c` for z88dk, `$(SRCDIR)/*.c` for CPCtelera), there is already a
passing multi-file link test, and the state contract already says "define every required
symbol exactly once, across all your files". What is missing is that **nothing asks for
structure**: the writer is told "return one file per source, named like main.c" and that is
the end of it.

The standard to match is explicit, and it is not a Studio invention: **whatever an LLM would
produce if asked for the same game in JS or C# following clean code practices.** One unit of
content per file — a screen per file in an Arkanoid, a character per file in a Skool
Daze — domain separated from platform, `main` only orchestrating.

Two things follow from that, and the second is the one that matters most:

1. The program becomes readable and repairable per module.
2. **The ceiling on how ambitious a game can be goes away.** With one file per module, each
   module is written in its own model call, so the whole program no longer has to fit in a
   single response. Six Skool Daze characters are six calls that share one prefix, not one
   call holding 3000 lines.

## What is decided

### The model proposes the decomposition; Studio checks properties

Studio does not derive the file list from `game.yml` by a mapping table and does not impose
file names. The `architecture` stage asks the writer for structure the way you would ask in
any modern language — *"structure this game as a real project: separated responsibilities,
one unit of content per file, names from the domain"* — and it answers with the module index
and the headers.

What Studio verifies, and refuses with the reason:

- `main.c` only orchestrates: no game rules, no per-cell drawing.
- Every `.c` has its `.h`; no include cycles.
- One unit of content per file, and one file per unit — a screen is not split across two
  files, and two screens do not share one. Made checkable by the index itself: each entry
  declares which unit of the design it covers (`screen_1`, `einstein`, or `none` for
  cross-cutting modules like `render` or `rules`), and Studio checks that mapping is a
  bijection against the units the design declares — every screen and every entity with
  behaviour claimed exactly once, nothing claimed twice, no entry naming a unit the design
  does not have. Studio never decides *which* units get their own file; it checks the model's
  own answer is consistent with the design.
- Contract symbols defined exactly once across the whole set.

An index a reasonable model would propose for the two games above, as an illustration and
not as a rule:

```
Arkanoid                     Skool Daze
  main.c                       main.c
  world.h                      world.h
  rules.c/h                    rules.c/h
  screen_1.c/h                 einstein.c/h
  screen_2.c/h                 angelface.c/h
  render.c/h                   render.c/h
                               hud.c/h
```

### The interface is the contract between modules

The `architecture` stage produces headers only:

- `world.h` — the shared game state, in structs. No drawing, no platform.
- `<module>.h` — what that module exposes: signatures and types, no bodies.

Three rules, each with a machine reason:

1. **Domain modules do not include `platform.h`.** That is what makes them compilable on the
   host with gcc, which is the whole point of the stage after it. Checked with a grep, not
   with trust.
2. **Contract symbols live in one module, not spread out.** They cannot be `static` (a static
   symbol is absent from the linker map) and must be defined once; concentrating them removes
   the "defined twice" failure that writing modules in separate calls would otherwise invite.
3. **Shared state passes by pointer.** A 200-byte `struct world` copied by value per call is
   exactly the cost the pacing gate measures.

`world.h` is what makes per-module calls possible at all: each call carries `world.h` and the
module's own `.h`, never another module's implementation.

### The domain is host-testable, and a separate examiner writes the tests

The `exam` stage receives the declared mechanics and the headers — never an implementation —
and returns a `domain_tests.c` of assertions. Studio compiles it with gcc alongside the
domain modules and runs it. Seconds, not minutes.

```
gcc -std=c99 -Wall -Werror world.h rules.c screen_1.c domain_tests.c -o host_exam
./host_exam        →  fails at the assertion line, with its message
```

Four things keep this from being theatre:

- **Identical arithmetic.** The domain uses fixed-width types (`uint8_t`, `uint16_t`), never
  bare `int`. Verified: `zcc +zx`, `sdcc -mz80` and `gcc` all accept `<stdint.h>`. Without
  this the host would have 4-byte ints where the Z80 has 2, and an overflow that breaks the
  real game would pass the test — a test that lies is worse than no test.
- **What counts as domain is declared by the index and verified by a grep.** A module marked
  domain that includes `platform.h`, `cpctelera.h` or `<arch/zx.h>` is refused on delivery.
- **A failure reaches the writer as one more diagnostic**, on the same path as a compiler
  error or the pacing gate, and *before* compiling for Z80 and booting the emulator — so a
  rules error costs seconds instead of the eight minutes it costs today.
- **The examiner can be wrong too.** If the writer cannot satisfy an assertion in two
  attempts, Studio redoes the exam once with the failure in view; if the second exam agrees,
  the problem is the code. Without this, one impossible assertion traps the writer until the
  attempt budget is gone.

The host exam replaces nothing. Build, acceptance, animation, pacing, attributes, state
probes and the screen capture all stay where they are. This is one more net, placed before
them because it is the fastest.

### The module boundary is crossed per frame, not per cell

Without LTO each `.c` is its own translation unit and a call across modules is not inlined —
and the pacing gate measures that. The contract rule: the domain is called a few times per
frame (advance state, resolve collisions), and what runs per cell or per pixel — blitting,
erasing, the HUD — lives inside its own module as `static` functions, which SDCC can
optimise.

```
main.c:     step_world(&w);      ← 1 call/frame
            render_world(&w);    ← 1 call/frame

render.c:   static void put_cell(...)     ← per cell, static
            static void blit_actor(...)

Forbidden:  main.c calling render_cell() 280 times.
```

### Modules are written one per call, in parallel, against a frozen interface

Each `.c` is written in its own call, carrying:

```
state contract + platform.h (platform modules only)
world.h + its own .h + the .h of what it depends on
the slice of the design that is its own   (that screen; that character; those mechanics)
the exam assertions that name its interface
```

Never another module's implementation. That is what removes the ceiling.

**They go out in parallel.** No module depends on another's code — the contract is entirely
in the headers — so the N calls are issued together. Six characters are one wait, not six.
The risk is real and stated: if the interface came out wrong, N wrong calls are paid at once
instead of discovering it on the first. The trade is accepted because the interface is small,
the exam reads it before anything is implemented, and today the wait is the worst defect of
the cycle.

**The interface is frozen during implementation.** A module may not change a header: two
modules written against different signatures do not link, and the diagnostic appears far from
the cause. A module that needs to change the interface is refused with that reason, and that
returns the project to `architecture`, which redoes headers and exam. Expensive on purpose —
it makes the interface get thought about in the stage that owns it.

**Repair is aimed at the guilty file.** A compilation error or a host assertion names its
file: only that file is rewritten, with its diagnostic, and the rest of the program stays.
Runtime verdicts do not always know whose they are — pacing and animation are measured over
the whole program, so their repair goes to the module the diagnostic points at when there is
one (the one that draws, for attributes; the loop, for pacing) and to `main.c` when there is
no signal. Never to all six at once, which is how what already worked would break.

**Budget.** Today it is 5 attempts at the whole program. It becomes 3 attempts per module
with a global cap on repair calls per project, so one impossible module cannot eat the others'
budget or spend without end.

### How the work is sent to the model

Measured in this repository: the writer's prompt is 43 902 characters = **19 160 input
tokens**; the output is a 474-line `main.c`; ~4-6 min per writing attempt, 2 s of
compilation, ~2 min of emulator. Opus 5 is $5/M input and $25/M output; a cache read is
≈0.1× and a write 1.25×.

**Granularity.** Per module, not per layer and not per function. Per function each call would
need almost the module's context anyway, so the same prefix is paid N times for nothing.

**Prefix caching, which requires reordering the prompt.** Caching is an exact prefix match, so
the stable part goes first with a `cache_control` breakpoint and the per-module part after it:

```
[ state contract + platform notes + platform.h + design + headers ]  ← ~19k tokens, cache_control
[ this module: its .h, its slice of the design, its assertions ]     ← changes per call
```

With 8 calls: without caching 8 × 19k ≈ **152k input tokens** at full price ($0.76); with
caching ≈ 19k×1.25 + 7×19k×0.1 ≈ **37k equivalent** ($0.19). Opus 5's minimum cacheable
prefix is 512 tokens, so a 19k prefix caches comfortably.

**Concurrency has one catch.** A cache entry is only readable once the first response begins
streaming, so N simultaneous calls all pay full price. The shape is therefore: issue one, wait
for its first token (~10-20 s), then fire the remaining N-1 — nearly all of the latency win,
and real cache reads.

**Effort per stage, not one for everything.** Studio passes no `effort` today (it takes the
`high` default). Architecture and exam get `xhigh`; domain modules `high`; render and HUD are
mechanical and do well at `medium`. Note `thinking: disabled` combined with `xhigh`/`max` is a
400 — not used here, but recorded.

**Rejected with reason.** The Batches API gives 50% off but can take up to 24 h — useless for
a cycle a human waits on. Several modules in one response reintroduces the ceiling and
re-couples repairs.

Resulting pipeline, first-pass latency estimate with no repairs:

```
architecture         xhigh   ~3 min      1 call        headers + module index
exam  ∥  render/main         ~3 min      1 + 2         the exam does not block who does not need it
domain (N modules)   high    ~3 min      N in parallel (1 + rest, so they cache)
host tests                   seconds     gcc
Z80 build + emulator         ~2.5 min
                             ─────────
                             ~12 min
```

Today it is 4-8 min per attempt at the whole program, up to 5 attempts; the run this design
was written after spent 35 min and failed. A repair goes from rewriting the program to
rewriting one file (~2 min).

## Stages and commands

```
llmz80 project architecture PATH   headers + module index      → architecture_report.json
llmz80 project exam PATH           domain assertions           → exam_report.json
llmz80 project write PATH          the modules, in parallel    → write_report.json
llmz80 make "..."                  chains them, as it does now
```

First-class stages rather than substeps of `write`, because this session paid twice for not
being able to retry only the part that fell over — 2100 s lost per stage.

## What gets refused

| Gate | Refuses | Acts |
|---|---|---|
| Structure | `main.c` with game rules or per-cell drawing; a `.c` with no `.h`; an include cycle; a content unit split across files | on delivering the architecture |
| Pure domain | a domain module including `platform.h`, `cpctelera.h` or `<arch/zx.h>`; a bare `int` in its interface | on delivering headers, and each `.c` |
| Frozen interface | a module that changes a header | on delivering the module → back to `architecture` |
| Host exam | an assertion that fails under gcc | before compiling for Z80 |
| Observable contract | a contract symbol defined twice across modules, or not at all | at link time |

Each refusal travels as a diagnostic into the repair loop, never as an uncaught exception —
the same rule `compiler.build_project` already follows for `sprite_usage_errors`.

Untouched: build, acceptance, animation, pacing, attributes, state probes, mandatory
`plat_sprite`/`plat_tile`, the binary and static-data budgets, and the screen capture that
requires something to be visible.

## Compatibility

- **`llmz80 project write` changes meaning**: it writes modules against an interface that
  already exists. With no prior `architecture` it fails saying what is missing rather than
  inventing headers.
- **The five projects already in `studio-projects/`** hold a single `main.c`. They keep
  building and playing: the new gates act on *writing*, not on building.
- **`ProgramSources` gains a per-file role** (domain / platform / main) as a defaulted field,
  so a one-file program still validates.
- **`llm.structured()` is reordered** for a cacheable prefix and gains `effort` and
  `cache_control`. Every one of the pipeline's calls goes through it, so it ships with its
  tests before anything else.
- **Existing tests**: all 1013 stay. The ones asserting "the program is a `main.c`" assert
  "the program satisfies the contract" instead; writer fakes that return one file keep
  returning one file.

## Deliberately out of scope

No build system of our own (both toolchains already compile by glob), no generated Makefiles,
no domain library shared between games, no test framework on the Z80 (tests run on the host),
no incremental patches — the unit of rewriting is the file.

## Implementation order

Three blocks, in this order, each shippable on its own with the suite green:

1. **`llm.structured()`** — reordered for a cacheable prefix, plus `effort` and
   `cache_control`. Every call in the pipeline goes through it, so it lands first, alone, with
   its own tests. Nothing else in this design depends on it being done first, but everything
   gets cheaper and faster once it is.
2. **`architecture` and `exam` stages** — the module index and headers, the structure and
   pure-domain gates, the host exam and its gcc run, and the two new commands and reports.
   At the end of this block `write` still writes the whole program in one call: the gates
   exist and are checked, and nothing has been parallelised yet. That is a real, testable
   halfway point rather than a broken one.
3. **Per-module writing** — the frozen interface, the parallel calls with the one-then-rest
   cache shape, aimed repair, and the per-module attempt budget.

## Risks

- **A wrong interface costs N calls at once.** Bounded by the exam, which reads it before
  anything is implemented, and by the global repair cap.
- **An impossible assertion traps the writer.** Bounded by redoing the exam once before
  blaming the code.
- **Modularisation costs cycles on a Z80.** The per-frame boundary rule is the mitigation and
  the pacing gate is the judge — terrain art already proved those gates measure real cost.
