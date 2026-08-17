# Cacheable structured calls Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `llm.structured()` cache the stable half of a prompt and accept a per-call effort level, so the writer's five repair attempts stop re-paying for the same 19 000-token prefix.

**Architecture:** `structured()` gains two optional parameters. `cached_prefix` moves the stable part of a request into a second `system` block carrying `cache_control`, leaving only the volatile part in the user turn; `effort` becomes `output_config={"effort": ...}`. Both default to today's exact behaviour, so every one of the eleven call sites keeps working untouched until it opts in. Only the program writer opts in within this plan — it is the caller with a repair loop, and therefore the only one that can read a cache it just wrote.

**Tech Stack:** Python 3.12, `anthropic` 0.122.0 (`client.messages.stream` + `output_format`), pydantic v2, pytest. The fake client used by every test lives in `tests/conftest.py` as `FakeMessageStream` / `fake_message`.

**Scope:** This is block 1 of three in `docs/superpowers/specs/2026-08-17-multi-file-z80-programs-design.md`. Blocks 2 (`architecture` and `exam` stages) and 3 (per-module writing) get their own plans; this one ships and is useful on its own — it makes today's five-attempt repair loop roughly half the input cost with no other change.

---

## Why the TTL is not a preference

The default cache TTL is 5 minutes. One writing attempt in this project takes **4-6 minutes**
(measured: attempts of 195 s, 240 s, 282 s, 326 s in `studio-projects/*/studio.log`), so with
the default TTL the entry usually expires between attempts and every attempt pays a 1.25×
write for nothing — **worse than not caching at all**. Arithmetic for the writer's 19 000-token
prefix over five attempts:

| | input tokens billed |
|---|---|
| No caching | 5 × 19k = **95k** |
| 5-minute TTL, entry expires each time | 5 × 19k × 1.25 = **119k** |
| 1-hour TTL | 19k × 2 + 4 × 19k × 0.1 = **46k** |

So a caller that opts in gets `ttl: "1h"` by default. This is recorded here because a future
reader who "simplifies" it back to the 5-minute default would silently make the pipeline more
expensive, not less.

## File Structure

| File | Responsibility | Change |
|---|---|---|
| `llmz80/studio/llm.py` | The one place a structured request is built | Modify: add `cached_prefix`, `cache_ttl`, `effort` |
| `tests/test_studio_llm.py` | Pins the request shape for all eleven call sites | Modify: add tests |
| `tests/test_studio_live_cache.py` | Proves against the real API that the shape is accepted and the cache is read | Create |
| `llmz80/studio/generator.py` | The program writer, the only caller with a repair loop | Modify: opt in |
| `tests/test_studio_generator.py` | Pins what the writer sends | Modify: add tests |

---

### Task 1: `effort` reaches the request

**Files:**
- Modify: `llmz80/studio/llm.py:66-131`
- Test: `tests/test_studio_llm.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_studio_llm.py`:

```python
def test_effort_travels_inside_output_config():
    """The key is nested, so the schema and the effort level reach the model
    together instead of one displacing the other: `messages.stream` builds
    `{**output_config, "format": <schema>}` (anthropic 0.122.0,
    `resources/messages/messages.py:1275`), spreading the caller's dict first."""
    client = _FakeClient(_Verdict(ok=True))

    structured(
        client,
        "claude-opus-5",
        system="s",
        user="u",
        schema=_Verdict,
        missing="m",
        effort="medium",
    )

    call = client.messages.calls[0]
    assert call["output_config"] == {"effort": "medium"}
    assert "effort" not in call


def test_no_output_config_is_sent_when_no_effort_is_asked_for():
    """Every existing call site passes no effort and must keep sending exactly
    what it sends today -- `high` is already the default the model applies, so
    naming it would be describing the default (see the module docstring)."""
    client = _FakeClient(_Verdict(ok=True))

    structured(client, "claude-opus-5", system="s", user="u", schema=_Verdict, missing="m")

    assert "output_config" not in client.messages.calls[0]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_studio_llm.py -k effort -v`
Expected: FAIL — `TypeError: structured() got an unexpected keyword argument 'effort'`

- [ ] **Step 3: Write the minimal implementation**

In `llmz80/studio/llm.py`, add the parameter to the signature after `attempts`:

```python
    attempts: int = DEFAULT_ATTEMPTS,
    effort: Effort | None = None,
```

and after the `if tools is not None:` block (never inside the retry loop — see the
`effort_survives_a_retry` test below), add:

```python
    if effort is not None:
        request["output_config"] = {"effort": effort}
```

The rationale belongs in the module docstring, not beside these two lines: an inline
comment restating what the `if` already shows is narration by this file's own standard.
Say there that the key is nested because there is nowhere else for it to go — there is no
top-level `effort` in the request surface, and sent as one, `stream(**request)` raises
`TypeError: got an unexpected keyword argument 'effort'` before any network I/O. It is the
loudest possible failure, not a silent one.

Add a test that the level survives the retry loop, too — the property that makes the
placement correct (set before the loop; the loop only re-assigns `messages`) is otherwise
unpinned, and Task 2 rebuilds the request's system half in this same function:

```python
def test_effort_survives_a_retry():
    """The repair attempt is the same request with a different user turn."""
    client = _ScriptedClient(_too_long(), _Verdict(ok=True))
    structured(client, "claude-opus-5", system="s", user="u", schema=_Verdict,
               missing="m", effort="medium")
    assert client.messages.calls[1]["output_config"] == {"effort": "medium"}
```

And constrain the type rather than taking a bare `str`: `OutputConfigParam.effort` is
`Optional[Literal["low","medium","high","xhigh","max"]]` upstream, `OutputConfigParam` is a
TypedDict so nothing validates at runtime, and a typo reaches the API as a 400 the retry
loop does not catch — a paid round trip, minutes into a pipeline run, for a free
check-time error. Spell the alias out in `llm.py` rather than importing it, so the module
keeps depending on the client's shape and not on the SDK's types:

```python
Effort = Literal["low", "medium", "high", "xhigh", "max"]
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_studio_llm.py -v`
Expected: PASS, 14 tests

- [ ] **Step 5: Commit**

```bash
git add llmz80/studio/llm.py tests/test_studio_llm.py
git commit -m "feat(studio): let a caller choose how hard the model thinks"
```

---

### Task 2: a cached prefix travels as its own system block

**Files:**
- Modify: `llmz80/studio/llm.py:66-140`
- Test: `tests/test_studio_llm.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_studio_llm.py`:

```python
def test_a_cached_prefix_becomes_a_second_system_block_with_cache_control():
    """Caching is an exact prefix match over `tools` then `system` then
    `messages`, so the stable half has to sit in `system` -- ahead of anything
    that changes -- with the breakpoint on it."""
    client = _FakeClient(_Verdict(ok=True))

    structured(
        client,
        "claude-opus-5",
        system="you write programs",
        cached_prefix="the whole contract and the design",
        user="repair this",
        schema=_Verdict,
        missing="m",
    )

    call = client.messages.calls[0]
    assert call["system"] == [
        {"type": "text", "text": "you write programs"},
        {
            "type": "text",
            "text": "the whole contract and the design",
            "cache_control": {"type": "ephemeral", "ttl": "1h"},
        },
    ]
    assert call["messages"] == [{"role": "user", "content": "repair this"}]


def test_the_prefix_defaults_to_the_one_hour_ttl_and_the_caller_may_override():
    """One writing attempt takes 4-6 minutes, so the 5-minute default expires
    between attempts and every attempt pays a 1.25x write for nothing -- worse
    than not caching. See the plan's TTL arithmetic."""
    client = _FakeClient(_Verdict(ok=True))

    structured(
        client,
        "claude-opus-5",
        system="s",
        cached_prefix="p",
        user="u",
        schema=_Verdict,
        missing="m",
        cache_ttl="5m",
    )

    assert client.messages.calls[0]["system"][1]["cache_control"] == {
        "type": "ephemeral",
        "ttl": "5m",
    }


def test_without_a_prefix_the_system_prompt_stays_a_plain_string():
    """Ten of the eleven call sites pass no prefix, and their request must be
    byte-identical to what it is today -- a request that changed shape would
    invalidate any cache they do have and change what the model is sent."""
    client = _FakeClient(_Verdict(ok=True))

    structured(client, "claude-opus-5", system="s", user="u", schema=_Verdict, missing="m")

    assert client.messages.calls[0]["system"] == "s"


def test_schema_repair_feedback_lands_after_the_cached_prefix():
    """The retry appends pydantic's complaint to the volatile half. If it were
    appended to the prefix, the second attempt would miss the cache the first
    one just wrote -- which is the entire point of splitting them."""
    client = _ScriptedClient(_too_long(), _Verdict(ok=True))

    structured(
        client,
        "claude-opus-5",
        system="s",
        cached_prefix="stable",
        user="volatile",
        schema=_Verdict,
        missing="m",
    )

    first, second = client.messages.calls
    assert first["system"][1]["text"] == "stable"
    assert second["system"][1]["text"] == "stable"
    assert "String should have at most 5 characters" in second["messages"][0]["content"]
    assert second["messages"][0]["content"].startswith("volatile")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_studio_llm.py -k "prefix or ttl or feedback_lands" -v`
Expected: FAIL — `TypeError: structured() got an unexpected keyword argument 'cached_prefix'`

- [ ] **Step 3: Write the minimal implementation**

In `llmz80/studio/llm.py`, add to the signature after `effort`:

```python
    cached_prefix: str | None = None,
    cache_ttl: str = "1h",
```

Replace the `request` construction (currently `llm.py:122-128`) with:

```python
    request: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        # A prefix is cached where caching can see it. The cache key is the
        # exact bytes of the rendered prompt, rendered `tools` then `system`
        # then `messages`, so the stable half must sit in `system` ahead of
        # everything that changes -- a prefix appended to the user turn beside
        # the volatile half would be a different prefix on every call and cache
        # nothing.
        #
        # `ttl` is 1h rather than the 5-minute default because one writing
        # attempt in this project takes 4-6 minutes: with the default the entry
        # expires between attempts and each one pays a 1.25x write for nothing,
        # which is more expensive than not caching (see
        # docs/superpowers/plans/2026-08-17-cacheable-structured-calls.md).
        "system": (
            system
            if cached_prefix is None
            else [
                {"type": "text", "text": system},
                {
                    "type": "text",
                    "text": cached_prefix,
                    "cache_control": {"type": "ephemeral", "ttl": cache_ttl},
                },
            ]
        ),
        "messages": [{"role": "user", "content": user}],
        "output_format": schema,
    }
```

- [ ] **Step 4: Run the whole file to verify nothing else moved**

Run: `.venv/bin/python -m pytest tests/test_studio_llm.py -v`
Expected: PASS, 18 tests

- [ ] **Step 5: Run the whole suite — ten other call sites go through this function**

Run: `.venv/bin/python -m pytest tests/ -q`
Expected: PASS, 1017 tests

- [ ] **Step 6: Commit**

```bash
git add llmz80/studio/llm.py tests/test_studio_llm.py
git commit -m "feat(studio): put the stable half of a prompt where caching can see it"
```

---

### Task 3: prove it against the real API

The fake client proves what Studio *sends*. It cannot prove the API accepts `output_config`
beside `output_format`, and it cannot prove a second call actually reads the cache. Both are
assumptions this whole plan rests on, so they get measured once, against the live API, the way
`tests/test_studio_tile_blitter_toolchain.py` measures the blitter against real video memory.

**Files:**
- Create: `tests/test_studio_live_cache.py`

- [ ] **Step 1: Write the test**

Create `tests/test_studio_live_cache.py`:

```python
"""Live-API proof that the cached-prefix request shape works.

Two assumptions this plan rests on cannot be checked with a fake client:

- that the API accepts `output_config` alongside `output_format` (the SDK merges
  the two into one object, so a conflict would be a 400 nobody predicted), and
- that a second call with the same prefix really reads the cache.

Both are measured here rather than assumed. Skipped without an API key, the way
the toolchain tests skip without z88dk -- and this one spends money, so it is
one pair of small calls and no more.
"""

from __future__ import annotations

import os

import pytest
from pydantic import BaseModel

from llmz80.studio.llm import structured

no_key = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY") and not os.path.isfile(".env"),
    reason="no Anthropic credentials available",
)


class _Answer(BaseModel):
    ok: bool


def _client():
    from anthropic import Anthropic

    from llmz80.utils.config import load_anthropic_api_key

    return Anthropic(api_key=load_anthropic_api_key())


#: Comfortably over Opus 5's 512-token minimum cacheable prefix -- a shorter
#: prefix caches silently not at all, which would make this test pass for the
#: wrong reason.
PREFIX = (
    "You are checking that a long, stable instruction block can be cached. "
    "This sentence exists only to take up tokens, and it is repeated. " * 120
)


@no_key
def test_effort_and_a_cached_prefix_are_accepted_together():
    """One request carrying both. A 400 here means the request shape in
    `structured` is wrong, whatever the fake client says."""
    answer = structured(
        _client(),
        "claude-opus-5",
        system="Answer with ok=true.",
        cached_prefix=PREFIX,
        user="Say ok.",
        schema=_Answer,
        missing="the model did not answer",
        max_tokens=2000,
        effort="low",
    )

    assert answer.ok is True


@no_key
def test_the_second_call_reads_the_prefix_from_cache():
    """The measurement the whole plan turns on. Two calls sharing a prefix and
    differing in the user turn: the second must report cache reads.

    `structured` returns only the parsed answer, so usage is read off the raw
    SDK call here rather than through it -- this test is about the transport,
    not about Studio's own layer.
    """
    from anthropic import Anthropic  # noqa: F401  (imported for its side-effect-free typing)

    client = _client()
    system = [
        {"type": "text", "text": "Answer with ok=true."},
        {
            "type": "text",
            "text": PREFIX,
            "cache_control": {"type": "ephemeral", "ttl": "1h"},
        },
    ]

    def ask(question: str):
        with client.messages.stream(
            model="claude-opus-5",
            max_tokens=2000,
            system=system,
            messages=[{"role": "user", "content": question}],
            output_format=_Answer,
            output_config={"effort": "low"},
        ) as stream:
            return stream.get_final_message()

    first = ask("Say ok.")
    second = ask("Say ok again.")

    assert first.usage.cache_creation_input_tokens > 0, first.usage
    assert second.usage.cache_read_input_tokens > 0, second.usage
```

- [ ] **Step 2: Run it**

Run: `.venv/bin/python -m pytest tests/test_studio_live_cache.py -v`
Expected: PASS, 2 tests. If `test_effort_and_a_cached_prefix_are_accepted_together` fails with
a 400 naming `output_config`, stop and report it — Task 1's shape is wrong and the rest of the
plan needs revisiting before continuing.

- [ ] **Step 3: Commit**

```bash
git add tests/test_studio_live_cache.py
git commit -m "test(studio): measure the cached prefix against the real API"
```

---

### Task 4: the program writer opts in

This is where the plan pays for itself. `ResponsesProgramWriter.write` already splits its input
exactly the way caching wants: `writing_prompt(project, reference=...)` is identical across the
five attempts of one repair loop, and the rejection feedback is appended at the end. Passing
the first as `cached_prefix` and the second as `user` turns four of five attempts into cache
reads.

**Files:**
- Modify: `llmz80/studio/generator.py:245-273`
- Test: `tests/test_studio_generator.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_studio_generator.py`:

```python
def test_the_writer_sends_the_unchanging_prompt_as_a_cached_prefix():
    """The prompt is the same 19 000 tokens on every attempt of a repair loop;
    only the rejection feedback differs. Sent as a cached prefix, the four
    attempts after the first read it instead of re-paying for it."""
    client = _FakeClient(
        ProgramSources(summary="s", files=[ProgramFile(name="main.c", body="void main(void){}")])
    )
    writer = ResponsesProgramWriter(client, "claude-opus-5")
    project = blank_project("Cached", TargetPlatform.SPECTRUM)

    writer.write(project)

    call = client.messages.calls[0]
    assert isinstance(call["system"], list)
    assert call["system"][1]["cache_control"] == {"type": "ephemeral", "ttl": "1h"}
    assert "OBSERVABLE STATE CONTRACT" in call["system"][1]["text"]


def test_rejection_feedback_is_the_only_thing_that_changes_between_attempts():
    """The prefix must be byte-identical across attempts or the cache is never
    read. The feedback therefore goes in the user turn, alone."""
    client = _FakeClient(
        ProgramSources(summary="s", files=[ProgramFile(name="main.c", body="void main(void){}")])
    )
    writer = ResponsesProgramWriter(client, "claude-opus-5")
    project = blank_project("Cached", TargetPlatform.SPECTRUM)

    writer.write(project)
    writer.write(project, feedback="THE BUILD FAILED\n\nsrc/main.c:16: too many pancakes")

    first, second = client.messages.calls
    assert first["system"][1]["text"] == second["system"][1]["text"]
    assert "too many pancakes" in second["messages"][0]["content"]
    assert "too many pancakes" not in second["system"][1]["text"]


def test_a_first_attempt_still_carries_a_user_turn_the_model_can_answer():
    """A cached prefix moves the design into `system`; the user turn must still
    say something, or the request is a wall of instructions with no ask."""
    client = _FakeClient(
        ProgramSources(summary="s", files=[ProgramFile(name="main.c", body="void main(void){}")])
    )
    writer = ResponsesProgramWriter(client, "claude-opus-5")

    writer.write(blank_project("Cached", TargetPlatform.SPECTRUM))

    assert client.messages.calls[0]["messages"][0]["content"].strip()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_studio_generator.py -k "cached or rejection or first_attempt" -v`
Expected: FAIL — `AssertionError: assert False` on `isinstance(call["system"], list)`, because
the writer still sends one flat user turn.

- [ ] **Step 3: Check the test file has what those tests need**

Run: `grep -n "^from\|^import\|_FakeClient\|blank_project" tests/test_studio_generator.py | head -20`
Expected: `ProgramSources`, `ProgramFile`, `ResponsesProgramWriter`, `blank_project`,
`TargetPlatform` and `_FakeClient` are all already imported or defined in the file. If any is
missing, add the import before continuing:

```python
from llmz80.studio.generator import ProgramFile, ProgramSources, ResponsesProgramWriter
from llmz80.studio.models import TargetPlatform
from llmz80.studio.samples import blank_project
```

- [ ] **Step 4: Write the implementation**

In `llmz80/studio/generator.py`, replace the body of `ResponsesProgramWriter.write` (currently
`generator.py:263-273`) with:

```python
    def write(self, project: GameProject, feedback: str | None = None) -> ProgramSources:
        # Split where the repair loop already splits. `writing_prompt` is
        # identical on every attempt -- contract, platform notes, platform.h,
        # the design, the examples -- and only the rejection feedback differs,
        # so the first goes in the cached prefix and the second in the user
        # turn. Four of five attempts then read the prefix instead of paying
        # for it again: 19 000 tokens each time.
        prefix = writing_prompt(project, reference=self.reference)
        ask = (
            "Write the program this design asks for."
            if not feedback
            else "YOUR PREVIOUS ATTEMPT WAS REJECTED\n\n" + feedback
        )
        return structured(
            self.client,
            self.model,
            system=(
                "You write complete, small C programs for 8-bit Z80 home computers. "
                "You honour the stated contract exactly and you never invent build files."
            ),
            cached_prefix=prefix,
            user=ask,
            schema=ProgramSources,
            missing="the model did not return program sources",
        )
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_studio_generator.py -v`
Expected: PASS. If an existing test asserts the whole prompt is in `call["user"]` or in
`messages[0]["content"]`, update it to read `call["system"][1]["text"]` — the content did not
change, only which half of the request carries it.

- [ ] **Step 6: Run the whole suite**

Run: `.venv/bin/python -m pytest tests/ -q`
Expected: PASS, 1020 tests

- [ ] **Step 7: Commit**

```bash
git add llmz80/studio/generator.py tests/test_studio_generator.py
git commit -m "perf(studio): stop paying for the same 19k prompt five times"
```

---

### Task 5: effort where it is not `high`

Two callers do mechanical work: drawing a 16×16 sprite grid and drawing an 8×8 tile. Opus 5's
`low` and `medium` levels are strong, and these two are the highest-volume calls in a run
(seven of them in the Arkanoid run this plan follows).

**Files:**
- Modify: `llmz80/studio/sprite_artist.py:304`, `llmz80/studio/sprite_artist.py:735`
- Test: `tests/test_studio_tile_drawing.py`, `tests/test_sprite_grid_source.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_sprite_grid_source.py`:

```python
def test_drawing_a_sprite_grid_does_not_ask_for_the_highest_effort():
    """Writing 256 pen characters is mechanical next to designing a game, and
    these are the most numerous calls in a run. `high` is the API default, so
    the only way to spend less is to say so."""
    from llmz80.studio.sprite_artist import ClaudeGridSheetSource
    from llmz80.studio.models import TargetPlatform
    from llmz80.studio.samples import blank_project

    client = _FakeClient(_grid())
    source = ClaudeGridSheetSource(client)

    source.draw(blank_project("Effort", TargetPlatform.SPECTRUM), "draw a hero")

    assert client.messages.calls[0]["output_config"] == {"effort": "medium"}
```

Append to `tests/test_studio_tile_drawing.py`:

```python
def test_drawing_a_tile_does_not_ask_for_the_highest_effort():
    from llmz80.studio.sprite_artist import ClaudeGridTileSource
    from llmz80.studio.samples import blank_project

    client = _GridClient(["0" * TILE_SIZE] * TILE_SIZE)
    calls: list[dict] = []
    original = client.stream

    def recording(**kwargs):
        calls.append(kwargs)
        return original(**kwargs)

    client.stream = recording
    ClaudeGridTileSource(client).draw(blank_project("Effort", TargetPlatform.SPECTRUM), "a wall")

    assert calls[0]["output_config"] == {"effort": "medium"}
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_sprite_grid_source.py tests/test_studio_tile_drawing.py -k effort -v`
Expected: FAIL — `KeyError: 'output_config'`

- [ ] **Step 3: Check `_grid()` and `_FakeClient` exist in the sprite-grid test file**

Run: `grep -n "def _grid\|class _FakeClient" tests/test_sprite_grid_source.py`
Expected: both present. If `_grid()` is not, add it above the new test:

```python
def _grid():
    from llmz80.studio.sprite_grid import SpriteFrameGrid, SpriteSheetGrid
    from llmz80.studio.spriting import SPRITE_SIZE

    row = "0" * SPRITE_SIZE
    return SpriteSheetGrid(frames=[SpriteFrameGrid(rows=[row] * SPRITE_SIZE) for _ in range(4)])
```

- [ ] **Step 4: Write the implementation**

In `llmz80/studio/sprite_artist.py`, add above `class ClaudeGridSheetSource`:

```python
#: How hard the model is asked to think about a grid of pen characters. Drawing
#: one is mechanical beside designing a game or writing a program, and these are
#: the most numerous model calls in a run -- seven in the Arkanoid this was
#: measured against. `high` is the API default, so spending less has to be said
#: out loud. Raised if a target's art starts coming back rejected: the retry
#: loop makes a wrong setting visible rather than silent.
DRAWING_EFFORT = "medium"
```

Then add `effort=DRAWING_EFFORT,` to the `structured(...)` call in
`ClaudeGridSheetSource.draw` (after `missing=...`) and to the one in
`ClaudeGridTileSource.draw`.

- [ ] **Step 5: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_sprite_grid_source.py tests/test_studio_tile_drawing.py -v`
Expected: PASS

- [ ] **Step 6: Run the whole suite**

Run: `.venv/bin/python -m pytest tests/ -q`
Expected: PASS, 1022 tests

- [ ] **Step 7: Commit**

```bash
git add llmz80/studio/sprite_artist.py tests/test_sprite_grid_source.py tests/test_studio_tile_drawing.py
git commit -m "perf(studio): stop thinking hard about 8x8 blocks"
```

---

### Task 6: prove the saving end to end

**Files:**
- Modify: none. This task measures.

- [ ] **Step 1: Rebuild a project's program and read the usage back**

Run:

```bash
.venv/bin/llmz80 project write studio-projects/un-juego-tipo-arkanoid-pala-2
```

Expected: the stage behaves exactly as before — the same gates, the same verdict lines. The
change is invisible in the output, which is the point.

- [ ] **Step 2: Confirm the tile and sprite stages still draw acceptable art at `medium`**

Run:

```bash
rm -rf /tmp/effort-check && .venv/bin/llmz80 make "un laberinto con un minero que cava tuneles y dos murcielagos que patrullan" --workspace /tmp/effort-check
```

Expected: stage 4 draws its art without exhausting attempts. If any asset is rejected three
times, raise `DRAWING_EFFORT` to `"high"` in `llmz80/studio/sprite_artist.py`, re-run, and
record which target and which asset forced it in the commit message — a measured reason to
spend more, not a guess.

- [ ] **Step 3: Commit whatever the measurement changed**

```bash
git add -A && git commit -m "chore(studio): record what the effort measurement showed"
```

(If nothing changed, skip the commit and say so.)

---

## Self-review

**Spec coverage for block 1.** The spec's "How the work is sent to the model" section asks for
four things: a cacheable prefix (Task 2, proved in Task 3), per-stage effort (Tasks 1 and 5),
the `ttl` decision (Task 2, with the arithmetic recorded above), and the one-then-rest
concurrency shape. **The last one is deliberately not here**: nothing in Studio issues parallel
model calls yet, so there is no code for it to apply to. It belongs to block 3, where
per-module writing introduces the parallelism, and the spec's implementation order says the
same.

**Placeholders.** None: every step carries the code or the exact command, and Task 6's
conditional branch names the file, the constant and the new value rather than saying "tune it".

**Type consistency.** `cached_prefix`, `cache_ttl` and `effort` are spelled the same in the
signature (Task 1, Task 2), the writer's call (Task 4), the artist's calls (Task 5) and every
assertion. `DRAWING_EFFORT` is defined once and referenced twice. The tests read
`client.messages.calls[0]` because `_FakeMessages.stream` records into `calls` — the shape
`tests/conftest.py` already provides.

**One thing a reader should not miss:** Task 4 moves the design out of the user turn and into
`system`. That changes nothing about what the model is told and everything about what is
billed — but it does mean that from here on, "the prompt" for the writer is
`call["system"][1]["text"]`, not `call["messages"][0]["content"]`. Any later test that greps
the writer's prompt has to look there.
