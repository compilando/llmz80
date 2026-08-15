"""What the run that is actually performed must show in memory.

This is the phase 2 examiner, and it is the third attempt at this gate. The
first hardcoded one game's expectations -- an actor stepping through a grid at
a fixed cadence, scoring one collectible at a time -- and rejected three
perfectly good games for not being that game. The second withdrew the gate
entirely, and an abstention was then read as a pass. So this one is written
against both failures at once, and everything in the prompt below that reads
like paranoia is one of them.

The rule the whole module is built on: **assert only what the run we already
have can witness.** `observation.observation_script` holds each declared
binding for fifty frames, twice, actions first and directions last, then lets
go. Nobody steers it. It cannot walk a frog to its goal or a miner to the
exit, so an examiner that predicts victory is guessing, and a guess that fails
a working program is the first failure repeating.

What it *can* predict, from what the design itself states, is narrow and
real: that the game is playing rather than sitting on its title screen once
the action key has been held; that a score whose mechanic ties it to the mere
act of moving does rise; that a life count never goes up. Every mechanic that
makes no such claim is reported as unchecked, and that list is the honest
measure of how much of the design nobody verified -- `services.acceptance_report`
publishes it for exactly that reason.

The examiner is injected and defaults to `None` everywhere, so tests and
offline runs make no API call and the gate goes on abstaining.
"""

from __future__ import annotations

from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict

from llmz80.core.state_contract import SYMBOLS_BY_NAME

from .models import GameProject


class RuntimeAssertion(BaseModel):
    """One claim about one symbol at one step of the run."""

    model_config = ConfigDict(extra="forbid")

    #: The id of the step this is judged at, from the list handed to the
    #: examiner. An id that is not on that list is discarded rather than
    #: judged: a step nobody runs cannot be observed, and an unobservable
    #: expectation fails every program equally.
    step: str
    #: A contract symbol this program actually exposes.
    symbol: str
    compare: Literal["equals", "at_least", "at_most", "changed", "unchanged"]
    #: What to compare against, when the claim is about a literal number.
    value: int | None = None
    #: What to compare against, when the claim is about the same symbol's
    #: reading at an earlier step. This is what makes "the score went up"
    #: sayable, and exact equality could not say it.
    baseline: str | None = None
    #: Which of the design's mechanics this comes from, numbered from one as
    #: they were listed. Zero for a claim that comes from the state contract
    #: rather than from any mechanic. An index, not the sentence itself,
    #: because a model asked to quote prose paraphrases it and the coverage
    #: count would then silently stop matching any mechanic at all.
    mechanic: int
    #: Why this run must show it, in one sentence. Read by a person deciding
    #: whether the gate was fair, and by nothing else.
    why: str


class UncheckableMechanic(BaseModel):
    """One rule of the design this run cannot witness, and why not."""

    model_config = ConfigDict(extra="forbid")

    #: Which mechanic, numbered from one as they were listed -- an index for
    #: the same reason `RuntimeAssertion.mechanic` is one, and here it earns
    #: it twice over: `runtime_examination` counts a mechanic named here as
    #: unchecked even if some assertion also cites it. That contradiction is
    #: not hypothetical. The first real run of this prompt against
    #: `studio-projects/fase-uno-cpc` declared its first mechanic unverifiable
    #: in prose and bound an assertion to it anyway, and prose cannot be
    #: matched back to the sentence it paraphrases, so the coverage number
    #: silently came out one better than the examiner itself believed.
    mechanic: int
    #: What would have to happen for anyone to check it, in one sentence.
    why: str


class RuntimeExam(BaseModel):
    """One examiner's verdict on what this design's run must show."""

    model_config = ConfigDict(extra="forbid")

    assertions: list[RuntimeAssertion]
    unverifiable: list[UncheckableMechanic]


class RuntimeExaminer(Protocol):
    def examine(
        self, project: GameProject, steps: list[dict[str, Any]], symbols: list[str]
    ) -> RuntimeExam: ...


#: Symbols an examiner is not offered, however faithfully the run read them.
#: Both already have a gate of their own that judges them properly, and both
#: cost a correct program a failure when judged crudely -- which is what a
#: model reaching for something to say about them does. `g_anim_frame` is
#: `feel.animation_report`'s, whose rules about which readings may be compared
#: are the reason it does not fail a program that animates on the fire key; a
#: bare "it changed between these two steps" here would fail any program whose
#: frame counter cycles back to where it started. `g_worst_frame_cost` is
#: `pacing.pacing_report`'s, and it is a running maximum the library keeps: a
#: model told the program must not write it says "unchanged", which fails
#: every correct program whose loop overruns once in the middle of the run.
#: Both were asserted, in exactly those words, by the first model this prompt
#: was tried on.
LIBRARY_GATED = ("g_anim_frame", "g_worst_frame_cost")


def examinable_symbols(symbols: list[str]) -> list[str]:
    """The symbols an assertion may be about: what the run read, less the two
    that belong to another gate."""
    return [name for name in sorted(symbols) if name not in LIBRARY_GATED]


def _symbol_menu(symbols: list[str]) -> str:
    """The symbols this program exposes, with what the contract says they mean.

    Only the ones the run really read. A design with no notion of lives never
    declares `g_lives`, nothing reads it, and an assertion about it would be
    judged "read nothing" -- a failure the program could not possibly repair.
    """
    return "\n".join(
        f"  {name}: "
        + (SYMBOLS_BY_NAME[name].meaning if name in SYMBOLS_BY_NAME else "no contract meaning")
        for name in symbols
    )


def _step_menu(steps: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"  {number}. {step['id']} -- holds {step['hold']} for {step['frames']} frames"
        for number, step in enumerate(steps, start=1)
    )


def examination_prompt(
    project: GameProject, steps: list[dict[str, Any]], symbols: list[str]
) -> str:
    """Everything the examiner is owed before it decides what to assert.

    Most of the length is hazards, and every one of them is a real reading
    from a real run in `studio-projects/`. A model asked "what should this
    game show?" answers about the game it imagines from the mechanics; it has
    to be told, in numbers it can check, that nobody is playing.
    """
    mechanics = (
        "\n".join(f"  {n}. {sentence}" for n, sentence in enumerate(project.mechanics, start=1))
        or "  (this design states no mechanics at all)"
    )
    return f"""SAY WHAT THIS PARTICULAR RUN MUST SHOW IN MEMORY

A harness is about to run this game in an emulator and read its variables
straight out of memory at the end of every step. You decide what those
readings must show for the program to be correct, and -- just as important --
which of the design's rules this run cannot check at all.

NOBODY IS PLAYING. The harness holds one key down for fifty frames, reads
memory, and moves to the next step, in the fixed order below. It never
chooses a direction, never aims, never waits for an opening and never
retries. It cannot make the player reach a goal, collect a thing, avoid an
enemy, or run out of lives. Whatever happens in those steps is whatever the
program does when four directions and an action key are held blindly in turn.

ASSERT ONLY WHAT MUST BE TRUE OF THAT RUN FOR EVERY CORRECT PROGRAM. A claim
that needs luck, skill, or a particular corner of the map is not one: report
it as unverifiable instead. Asserting little costs nothing. Asserting one
thing a correct program can fail costs a working game its attempts -- three
finished games were rejected that way by an earlier version of this examiner,
which had decided in advance what kind of game it was judging.

Hazards, every one of them a reading recorded from a real run of this system:

  * The game can end in the middle of the script. One mining game reached
    victory (g_state 3) on the seventh step and was back on its title screen
    (g_state 0) by the eighth, with four steps still to go. Anything you say
    about the game being in play belongs to the earliest steps, never to the
    last ones.
  * A design's silence is not a rule. That same mining design never mentions
    scoring in any mechanic, and its score ran from 0 to 525. Never assert
    that a symbol is unchanged just because no mechanic mentions it.
  * A score is not always monotonic across the whole run: a game returning to
    its title screen may reset it. A claim that it never falls is safe only
    while the game is still playing.
  * The first reading is taken a full second after the program started, so
    it is not the state the game begins in: whatever a mechanic says about
    the moment a game starts, by then the program has already run for fifty
    frames with a key held down.
  * A counter counts what the program decided it counts, not what you would
    have counted. A mining design naming one objective -- rescue the trapped
    miner -- read g_remaining 147 at its first step, because that program
    counts cells of dirt left to dig. Both readings honour the contract.
    Never assert an exact value for g_remaining, g_score or g_hiscore: bound
    them instead, which is true whatever the program is counting in.
  * A binding may do nothing where the player happens to stand. A frog game
    held all four directions and its score stayed 0 for the entire run, which
    was correct: its score only rises on reaching the far side of the road,
    and the harness cannot get there.

WHAT YOU MAY SAY. Each assertion names one step, one symbol, and one of:
  equals      the reading is exactly `value`
  at_least    the reading is >= `value`, or >= that symbol's reading at
              `baseline` -- this is how "the score went up or held" is said
  at_most     the reading is <= `value` or <= its reading at `baseline` --
              this is how "lives never go up" is said
  changed     the reading differs from `value`, or from its reading at
              `baseline`
  unchanged   the reading equals `value`, or its reading at `baseline`
Use `baseline` for a comparison against an earlier step of this same run, and
`value` for a comparison against a number. A baseline must be a step that runs
strictly before the step being judged. Set exactly one of the two.

THE CLAIM THIS RUN IS BEST AT. The action key is held for the first two
steps of the script. If the design's mechanics name the events that end a
game, and none of them can plausibly happen while one key is held blindly for
the first two seconds, then the game must still be in play at the end of the
second action step -- and that is worth asserting, because a program that
ends its game on a keypress, or that never leaves its title screen at all, is
precisely what this run can catch and what it was built to catch.

Prefer a bound to an exact value, and an early step to a late one. Give each
assertion the number of the mechanic it comes from, or 0 if it comes from the
meaning of the symbol itself rather than from any mechanic.

THE SYMBOLS THIS PROGRAM EXPOSES. These, and nothing else, will be read:

{_symbol_menu(symbols)}

THE STEPS, in the order they run:

{_step_menu(steps)}

THE DESIGN

Title: {project.metadata.title}
Controls: {", ".join(f"{n}={k}" for n, k in project.controls.bindings.items())}

Mechanics:
{mechanics}

Answer with `assertions` -- possibly empty -- and with `unverifiable`: one
sentence for each mechanic above this run cannot witness, naming the mechanic
and saying what would have to happen for anyone to check it.
"""


def usable_assertions(
    exam: RuntimeExam, steps: list[dict[str, Any]], symbols: list[str]
) -> tuple[list[RuntimeAssertion], list[str]]:
    """The assertions the harness can honour, and one sentence per one it cannot.

    Thrown away rather than failed, which is the whole point of this function:
    an assertion naming a step that does not run, or a symbol nothing reads,
    or a baseline that comes after the step it anchors, cannot be satisfied by
    any program whatsoever. Judging it would fail every game equally, and
    "your program is wrong" is the one thing that is certainly not what such
    an assertion means. The discarded sentences go into the report so the
    examiner's own mistakes stay visible instead of quietly shrinking the exam.
    """
    order = {step["id"]: number for number, step in enumerate(steps)}
    # The first step that holds a direction. Everything at or after it may be
    # any distance into a game that has already been won, lost or restarted --
    # a mining run reached victory on its seventh step and was back on its
    # title screen by the eighth -- so a claim that the game is *still in
    # play* is only safe up to and including it -- the earliest steps, where
    # least has had a chance to happen. The prompt says so too, and saying so was
    # not enough: an examiner bound `g_state == 1` to the idle step of a game
    # that happens never to end, which would have failed a correct program
    # the moment the same design did end. Advice the model may decline is
    # advice; this is the same rule the applier keeps rather than the prompt.
    from .models import HOLD_DIRECTIONS

    moving = [
        number for number, step in enumerate(steps) if step.get("hold") in HOLD_DIRECTIONS
    ]
    first_direction = moving[0] if moving else len(steps)
    kept: list[RuntimeAssertion] = []
    discarded: list[str] = []
    for assertion in exam.assertions:
        claim = f"{assertion.symbol} {assertion.compare} at {assertion.step}"
        if assertion.step not in order:
            discarded.append(f"{claim}: no step of this run is called {assertion.step!r}")
            continue
        if assertion.symbol not in symbols:
            discarded.append(f"{claim}: this program does not expose {assertion.symbol}")
            continue
        if assertion.symbol == "g_state" and order[assertion.step] > first_direction:
            discarded.append(
                f"{claim}: which screen is showing is only safe to claim before the "
                "first direction is held, since by then the game may have been won, "
                "lost or restarted"
            )
            continue
        if assertion.baseline is not None:
            if assertion.baseline not in order:
                discarded.append(f"{claim}: no step of this run is called {assertion.baseline!r}")
                continue
            if order[assertion.baseline] >= order[assertion.step]:
                discarded.append(
                    f"{claim}: its baseline {assertion.baseline} does not run before it"
                )
                continue
        elif assertion.value is None:
            discarded.append(f"{claim}: it names neither a value nor a baseline")
            continue
        kept.append(assertion)
    return kept, discarded


class ResponsesRuntimeExaminer:
    """Derives the run's expectations with the OpenAI Responses API."""

    def __init__(self, client: Any, model: str = "gpt-5") -> None:
        self.client = client
        self.model = model

    def examine(
        self, project: GameProject, steps: list[dict[str, Any]], symbols: list[str]
    ) -> RuntimeExam:
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You decide what a fixed, unsteered emulator run of a game must "
                        "show in memory. You assert only what every correct program must "
                        "produce in that exact run, and you say plainly which rules the "
                        "run cannot check. You never assert that the player achieves "
                        "anything."
                    ),
                },
                {"role": "user", "content": examination_prompt(project, steps, symbols)},
            ],
            text_format=RuntimeExam,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("the model did not return a runtime examination")
        return parsed
