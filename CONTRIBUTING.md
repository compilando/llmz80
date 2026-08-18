# Contributing to LLMZ80

Thanks for wanting to. This is what you need to know.

## Contents

- [Getting set up](#getting-set-up)
- [The shape of the codebase](#the-shape-of-the-codebase)
- [How this project writes code](#how-this-project-writes-code)
- [Testing](#testing)
- [Pull requests](#pull-requests)
- [Reporting a bug](#reporting-a-bug)
- [Areas that want help](#areas-that-want-help)

---

## Getting set up

```bash
git clone https://github.com/compilando/llmz80.git
cd llmz80
make install-dev
cp .env.example .env        # then put your ANTHROPIC_API_KEY in it
make doctor                 # tells you exactly what is missing
make test
```

Python 3.10 – 3.13. `make doctor` checks the interpreter, the API key, both
native toolchains and the emulators, and names whichever one is not there.

**You do not need an API key to work on most of this.** The whole test suite
runs offline: every call to a model goes through `llmz80.studio.llm.structured`,
and the tests hand it a fake client. You need a key only to run a real
generation end to end.

**You do not need both toolchains either.** Tests that need `zcc` or CPCtelera
skip themselves when it is absent — but if you are touching the CPC path,
install CPCtelera and *run its `setup.sh`*, or those tests will go on quietly
skipping and you will not know whether your change works. See the README.

---

## The shape of the codebase

Two things are worth understanding before changing anything.

**The design is a document, not a prompt.** `llmz80/studio/models.py` defines
schema v4: a design names its own tiles, entities, mechanics, observables and
palette, and nothing here has an opinion about what any of them mean. There is
no genre enum, no fixed tile alphabet, no list of allowed entity roles. If you
find yourself adding one, that is the thing v4 exists to prevent — the pipeline
should be able to make a game nobody anticipated.

**A gate measures or it abstains.** Every quality gate answers
`quality_pass: True`, `False`, or `None`. `None` means "I could not watch this",
and it is never treated as a pass: `generator.py` accepts an attempt only when
nothing definitely refused it, and `release` additionally requires that at least
one behaviour gate really did watch. If you add a gate, it must be able to say
"I don't know" — and if you make an existing one able to judge a case it used to
abstain on, say so in its docstring, because somebody reading the report needs
to know what changed.

Where things live:

| I want to… | Go to |
|---|---|
| change what a design can say | `studio/models.py`, then `studio/structure.py` for cross-field rules |
| change what the writer is told | `studio/acceptance.py` (`generation_prompt`) |
| change the C the game is built against | `resources/studio_lib/`, and `studio/codegen.py` for the generated headers |
| add or change a quality gate | `studio/{acceptance,feel,pacing,attributes}.py`, wired in `studio/services.py` |
| change how sprites are drawn or packed | `studio/sprite_artist.py`, `studio/spriting.py` |
| change how a target is built | `studio/compiler.py`, `core/toolchain.py` |
| change what the emulator does | `quality/emulator_smoke.py`, `studio/observation.py` |

`resources/studio_reference/` holds a complete maze game for each machine. It is
not generated from anything and nothing generates from it: it exists so the
gates can be proved both to pass a good program and to fail a sabotaged one. If
you change a gate, sabotage the reference program and check that your gate
notices.

---

## How this project writes code

The house style is unusual and deliberate, so it is written down.

**Comments say why, and cite the run that taught it.** Not what the code does —
the code does that. The comments here record the failure that produced the line:
which program broke, what it reported, what was tried first and why it was
worse. That is what stops the next person re-introducing the bug while tidying
up. If you fix something a comment describes, update the comment; if you delete
code a comment justifies, delete both.

```python
#: Frames each step holds its key. Fifty is one second at 50 Hz: long enough
#: that a program pacing itself on the frame clock has certainly moved.
STEP_FRAMES = 50
```

**Tests are prose about behaviour.** Name them as sentences, and use the
docstring to say what the test is protecting against, not what it does.

```python
def test_a_checkout_whose_toolchain_was_never_built_is_refused(self):
    """The failure this predicate exists to move earlier.

    A fresh clone has every source file and no compiler, so accepting it
    hands `make` a path it cannot execute: exit code 127, and a diagnostic
    that says nothing about setup never having been run.
    """
```

**Write the test first.** Every behaviour change in this repository has a test
that failed before the change and passes after it. Run it red first — a test
that never failed has not proved anything about the code.

**Formatting is not negotiated.** `make format` (isort, then black, line length
100). CI fails on unformatted code, and on any mypy or bandit finding, so run
`make quality-gate` before you push.

**Type everything.** `disallow_untyped_defs` is on and the tree is clean under
it. `object` as a parameter type is a way of saying "unchecked" — write a
`Protocol` instead; there are two in `studio/sprite_artist.py` to copy.

**English.** Code, comments, commit messages, diary lines, everything the
interface prints. The exceptions are linguistic data: `core/example_catalog.py`
holds Spanish stopwords and search terms, `studio/palette.py` and
`studio/runtime_exam.py` match colour and comparison words in both languages,
and `benchmarks/prompts.yml` is bilingual on purpose. A design's *own* prose is
whatever language it was briefed in — `Metadata.language` defaults to `es`.

**Commit messages** say what changed and why, in the imperative, with the
reasoning in the body. Conventional Commits prefix (`feat`, `fix`, `refactor`,
`test`, `docs`, `chore`, `style`).

---

## Testing

```bash
make test                            # everything
.venv/bin/pytest tests/test_studio_acceptance.py -v
.venv/bin/pytest -k toolchain -rs    # -rs shows what skipped, and why
make coverage
make check                           # tests, plus compile every retrievable example
```

`-rs` matters. A toolchain test that silently skips looks exactly like one that
passes, and this repository has already been bitten by nine CPC tests skipping
for months because no CPCtelera was installed.

Tests that talk to a model use the `FakeMessageStream` and `fake_message`
helpers in `tests/conftest.py`. Nothing in the suite makes a network call.

---

## Pull requests

1. Branch off `main`: `git checkout -b feat/what-it-does`
2. Write the failing test, then the change
3. `make quality-gate`
4. Push and open a PR describing what changed, why, and how you know it works

Keep a PR to one idea. A refactor and a behaviour change in the same diff is two
PRs wearing a coat.

---

## Reporting a bug

Open an issue with:

- What you ran, exactly
- What happened, and what you expected
- `make doctor` output
- For a generation failure: the `build/build_report.json` and `studio.log` from
  the project directory — they carry the compiler's own words and the diary of
  the run, which is almost always enough to see the cause

---

## Areas that want help

- **CPC audio.** `plat_sound` is a no-op on the CPC and the design gate refuses
  any CPC project that asks for sound. CPCtelera bundles Arkos Tracker, which
  is a music player rather than an effects API, so the first question is what
  five short effects should even be on an AY.
- **Measuring what the pixel blitters cost.** `plat_sprite_py` and
  `plat_sprite_px` are both slower per call than `plat_sprite`, and the pacing
  gate allows one missed frame. Nobody has measured how many moving sprites a
  real game can afford on either machine, so nothing in the writing prompt can
  tell a model where the line is.
- **Per-sprite shift counts.** `presentation.smooth_horizontal` is one flag for
  the whole design, because `SPRITE_SHIFTS` and `SPRITE_BYTES_WIDE` are one
  macro each. A game whose ball must slide and whose walls need not pays for
  both. Per-sprite would mean a width table the blitter reads on every call, on
  the hottest path there is -- worth doing only with a measurement to justify
  it.
- **Scrolling.** Neither machine has it, and they are not in the same
  position. The Spectrum has no hardware scroll: moving the picture means
  moving 6912 bytes, so full-screen smooth scrolling is not realistic from C --
  a windowed or character-step scroll is.

  The CPC has one, through the CRTC display start address
  (`cpct_setVideoMemoryOffset`), and it is coarser than it is usually
  described: one unit is **2 bytes**, which is 4 pixels in mode 0 and 8 in
  mode 1, and a whole screen row is 40 units and scrolls vertically by one
  character row. Measured on a real machine, because CPCtelera's own examples
  disagree -- `advanced/hwscroll` says four bytes in a comment,
  `advanced/tilemap_hwscroll` moves its pointer by two, and the second is the
  one whose arithmetic has to line up with the hardware to work at all.

  So coarse scrolling is nearly free on the CPC and pixel-smooth is not:
  sub-unit horizontal wants the background redrawn shifted, sub-row vertical
  wants the CRTC's vertical total adjust (R5, via `cpct_setCRTCReg`). Also
  worth knowing before starting: R13 is eight bits, so the offset alone covers
  512 bytes and anything further needs `cpct_setVideoMemoryPage` and a plan for
  the wrap.
- **A colour gate for the CPC,** since the Spectrum attribute gate has no
  meaning there and the CPC now has sixteen pens to get wrong.
- **More retrieval examples,** for either machine.

---

## Licence

Contributions are made under the MIT licence, the same as the project.
