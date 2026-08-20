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

What it says varies, and that was the third thing wrong with this gate. Four
examinations of one design, same prompt, left 5, 5, 5 and 6 of its seven
mechanics unchecked; across the five finished designs in `studio-projects/`,
four examinations in twenty produced no usable assertion at all and the gate
abstained on a run it had watched. It never over-claimed -- no correct game
was ever failed -- so what was wrong was the floor, not the ceiling. Two
things raise it, and neither touches the prompt, which has been iterated
twice already:

  * `RepeatedExaminer` sits the same exam four times concurrently and
    `merge_exams` reads the answers as one. A design where two rules are
    checkable now gets them checked whenever *any* pass finds them, instead
    of when the one pass that ran happened to.
  * `derived_assertions` states the two claims that follow from the design
    without asking anybody: that a program which has had its action key
    pressed and released twice is no longer on its title screen, and that a
    counter the design's own words describe as only ever rising has not
    fallen between the first two steps.

The examiner is injected and defaults to `None` everywhere, so tests and
offline runs make no API call and the gate goes on abstaining.
"""

from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict

from llmz80.core.state_contract import STATE_TITLE, SYMBOLS_BY_NAME

from .llm import Effort, structured
from .models import HOLD_ACTION, GameProject


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


def _symbol_menu(project: GameProject, symbols: list[str]) -> str:
    """The symbols this program exposes, with what each one means.

    Only the ones the run really read. A design with no notion of lives never
    declares `g_lives`, nothing reads it, and an assertion about it would be
    judged "read nothing" -- a failure the program could not possibly repair.

    A symbol the design itself declared is described in the design's own
    words and said to be the design's, because the contract has no meaning to
    offer for it and the reading it lists would otherwise be "no contract
    meaning" -- a symbol with no stated meaning is one no examiner will bind
    an assertion to, which is the whole reason this menu exists. These are
    the only symbols in the menu that can witness a rule of *this* game:
    `g_score` and `g_state` are the same six numbers in every game there is.
    """
    declared = {observable.symbol: observable.meaning for observable in project.observables}
    lines = []
    for name in symbols:
        if name in SYMBOLS_BY_NAME:
            lines.append(f"  {name}: {SYMBOLS_BY_NAME[name].meaning}")
        elif name in declared:
            lines.append(f"  {name}: {declared[name]} (declared by this design)")
        else:
            lines.append(f"  {name}: no stated meaning")
    return "\n".join(lines)


def _step_menu(steps: list[dict[str, Any]]) -> str:
    """The run, one step per line, each named by the id an assertion must use.

    Unnumbered, and that is the whole point. The menu used to number the steps
    `1. hold_action_a`, and the first examination of a design that declared
    its own observables came back naming every step `"1. hold_action_a"` --
    the menu line, not the id. `usable_assertions` discarded all five
    assertions as naming steps that do not run, so a design with two working
    observables in memory was judged by nothing at all and the gate abstained.
    Numbering a list whose items are identifiers invites exactly that, and the
    order is already stated by the sentence that introduces it.
    """
    return "\n".join(
        f"  {step['id']} -- holds {step['hold']} for {step['frames']} frames" for step in steps
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

`at_least 0` on a counter is not a claim about anything, and neither is
`at_most 3` on a symbol whose four values are the only ones there are. Do not
spend an assertion on either: an assertion no program can fail is the same as
no assertion, and this gate reports how much of the design nobody checked.

Prefer a bound to an exact value, and an early step to a late one. Give each
assertion the number of the mechanic it comes from, or 0 if it comes from the
meaning of the symbol itself rather than from any mechanic. A mechanic you
bind an assertion to must not also appear in `unverifiable`: the two answers
contradict each other, the honest reading is the one claiming less, and a
rule this run witnesses part of is reported as unchecked when you say both.

THE SYMBOLS THIS PROGRAM EXPOSES. These, and nothing else, will be read:

{_symbol_menu(project, symbols)}

Any symbol above marked "declared by this design" is this design's own
vocabulary, and the meaning shown is the sentence the design wrote for it.
The design declared it precisely so that one of its own rules could be
witnessed from outside, which the six fixed contract symbols cannot do.

Use them. For every symbol declared by this design whose stated meaning says
it only ever rises -- a count of things that have happened -- assert that it
is `at_least` its own reading at an earlier step, `baseline` and `step` both
among the earliest steps of the script, and give that assertion the number of
the mechanic the count belongs to. Do this even though the run cannot force
the counted event to happen: the claim is not that it rose, it is that it did
not fall, and it holds for every correct program while the game is still in
the same play. It is the strongest claim about a design's own rule that this
blind run can carry, and a program that resets that counter every frame,
decrements it, or wires it to nothing at all fails it -- none of which any
contract symbol could catch.

What such a symbol counts is only what its own sentence says. Bound it, never
predict an exact value, keep away from the late steps where a finished game
may have restarted and zeroed its counters, and say plainly in `unverifiable`
whichever part of the rule this run cannot witness -- but not the rule itself,
if you bound an assertion to it.

THE STEPS, in the order they run. Name one in `step` or `baseline` by its
id exactly as written here -- `hold_action_a`, not a number and not a
description:

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

    moving = [number for number, step in enumerate(steps) if step.get("hold") in HOLD_DIRECTIONS]
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


#: Phrases in an observable's own `meaning` that say the count only ever
#: rises. Matched against the design's sentence in either language Studio
#: writes designs in, because `minero-observable` says "solo sube" and the
#: prompt above says "only ever rises" -- the two halves of the same claim.
#:
#: Deliberately whole phrases rather than words like "total" or "acumulado":
#: a false positive here is an assertion nobody authored being judged against
#: a program that was right to reset its counter, which is the one outcome
#: this whole module is built to avoid. A phrase this list misses costs
#: nothing but the derivation -- the examiner is still asked the same
#: question and still free to say it.
ONLY_RISES = (
    "solo sube",
    "sólo sube",
    "solo aumenta",
    "sólo aumenta",
    "nunca baja",
    "nunca decrece",
    "no decrece",
    "only rises",
    "only goes up",
    "only increases",
    "never decreases",
    "never falls",
    "never goes down",
    "monotonic",
)


def _only_rises(meaning: str) -> bool:
    return any(phrase in meaning.casefold() for phrase in ONLY_RISES)


def derived_assertions(
    project: GameProject, steps: list[dict[str, Any]], symbols: list[str]
) -> list[RuntimeAssertion]:
    """The claims that follow from the design and need no model at all.

    Both of these were already in the prompt as instructions, and instructions
    are what the examiner keeps declining to follow reproducibly: over four
    examinations of each of the five finished designs, the title claim appeared
    in some sittings and not others, and four of those twenty examinations
    produced no usable assertion whatsoever -- the gate abstained on a run it
    had watched. Nine further sittings per design said the same: eighteen of
    the forty-five asserted nothing. A claim that can be derived should not be bought again every
    time at a price that includes forgetting it.

    Both carry `mechanic=0`, so neither improves the coverage count on its
    own. That is not modesty for its own sake: which of the design's sentences
    a symbol witnesses is a reading of prose, the one part of this the model
    is genuinely better at, and a derivation that guessed it would be the
    hardcoded gate returning by the back door. What these buy is the floor --
    the gate is awake, and the design's own counters are watched, on every run
    rather than on most of them.

    The title claim is `changed 0` rather than `equals 1` for the same reason
    the module prefers a bound to an exact value: "the program is no longer on
    its title screen" is what two press-and-release cycles of the action key
    prove, and a game that has already been won in two seconds is a different
    complaint. It is bound to the last action step, and only when the design
    binds an action key at all -- with only directions declared, nothing has
    pressed the key a title screen waits for, and every finished game in
    `studio-projects/` leaves its title on exactly that key
    (`INPUT_ACTION`/`INPUT_JUMP`, held by `observation_script`'s action steps).

    Every recorded run in `studio-projects/` satisfies it but one, and that
    one is the point: `un-minero-que-cava-tuneles-y` reads g_state 1 at its
    first action step and 0 at its second, having spent its three lives and
    come back to its title screen in two seconds of a held key. It was already
    refused (`quality_pass: false`) and redesigned as
    `un-minero-que-cava-tuneles-y-2`, so nothing correct is failed here -- but
    it is what this claim is for, and on that run the examiner asserted
    nothing at all.
    """
    derived: list[RuntimeAssertion] = []
    action_steps = [step for step in steps if step.get("hold") == HOLD_ACTION]
    if action_steps and "g_state" in symbols:
        derived.append(
            RuntimeAssertion(
                step=action_steps[-1]["id"],
                symbol="g_state",
                compare="changed",
                value=STATE_TITLE,
                mechanic=0,
                why=(
                    "the action key has been pressed and released twice by now, so a "
                    "program still showing its title screen never started at all"
                ),
            )
        )
    if len(steps) >= 2:
        for observable in project.observables:
            if observable.symbol in symbols and _only_rises(observable.meaning):
                derived.append(
                    RuntimeAssertion(
                        step=steps[1]["id"],
                        symbol=observable.symbol,
                        compare="at_least",
                        baseline=steps[0]["id"],
                        mechanic=0,
                        why=(
                            f"the design says {observable.symbol} only rises, and these "
                            "are the two earliest steps of the run, before anything can "
                            "have ended the game and zeroed it"
                        ),
                    )
                )
    return derived


def _shape(assertion: RuntimeAssertion) -> tuple[Any, ...]:
    """What makes two assertions the same claim. `mechanic` and `why` are left
    out: they are what the claim is *for*, not what it says, and two passes
    that make the same claim for different reasons must not both be judged."""
    return (
        assertion.step,
        assertion.symbol,
        assertion.compare,
        assertion.value,
        assertion.baseline,
    )


def dedupe(assertions: list[RuntimeAssertion]) -> list[RuntimeAssertion]:
    """One assertion per distinct claim, preferring the one that names a mechanic.

    The preference is the whole reason this is not a plain `set`. A derived
    assertion carries `mechanic=0` and an examiner's identical one carries the
    number of the rule it witnesses; keeping the derived one would silently
    delete that design's coverage -- `minero-observable`'s two declared
    observables are asserted by both, and dropping the examiner's attribution
    would take it from 2 of 7 mechanics checked back to 0.
    """
    kept: dict[tuple[Any, ...], RuntimeAssertion] = {}
    for assertion in assertions:
        seen = kept.get(_shape(assertion))
        if seen is None or (seen.mechanic == 0 and assertion.mechanic != 0):
            kept[_shape(assertion)] = assertion
    return list(kept.values())


def _predicts_a_reading(assertion: RuntimeAssertion) -> bool:
    """Whether this claim is a guess about how far the program got.

    A comparison against a literal number on anything but `g_state` is one: it
    says the score, the count of dug cells or the objectives left will have
    reached some particular number by some particular step, and nobody is
    playing. `g_state` is exempt because its four values are the four screens
    a game can be showing rather than a distance travelled, and
    `usable_assertions` already confines a claim about it to the steps before
    the first direction is held.

    Everything else compares one reading of this run against another reading
    of the same run -- "it did not fall", "it did not change" -- which
    predicts a direction rather than an outcome.
    """
    return assertion.baseline is None and assertion.symbol != "g_state"


def merge_exams(exams: list[RuntimeExam]) -> RuntimeExam:
    """Several sittings of the same exam, read as one.

    The union, not the intersection, and the reason is the measurement that
    prompted this: four examinations of the same design and the same prompt
    left 5, 5, 5 and 6 of its seven mechanics unchecked, and four of twenty
    examinations across the five finished designs asserted nothing at all. The
    worst sitting is what a single call is, and a design where two rules are
    checkable should have them checked every time rather than sometimes.

    Union is safe here because every assertion is filtered afterwards by
    `usable_assertions` and because of what these assertions are: a comparison
    against another reading of the same run cannot be made true or false by
    how far a player got. The one shape that can is a literal number about a
    counter, and that is the shape three finished games were rejected over, so
    it is the one shape that must be *agreed* -- two passes have to make the
    same claim before it is judged. That is stricter than the single call it
    replaces, where one pass saying `g_score at_least 1` was enough to fail a
    frog whose score correctly never moved.

    A mechanic a pass declared unverifiable loses that pass's attribution --
    the contradiction rule `runtime_examination` applies, moved here so it is
    applied per sitting -- but the assertion itself is kept and still judged,
    and another pass that had no such doubt may still attribute it. Only a
    mechanic *every* pass declined is reported as unverifiable, because
    between separate sittings there is no contradiction to resolve, only two
    opinions, and the union of opinions is the mechanism.
    """
    honest: list[list[RuntimeAssertion]] = []
    for exam in exams:
        declined = {item.mechanic for item in exam.unverifiable}
        honest.append(
            [
                (
                    assertion.model_copy(update={"mechanic": 0})
                    if assertion.mechanic in declined
                    else assertion
                )
                for assertion in exam.assertions
            ]
        )
    votes: Counter[tuple[Any, ...]] = Counter()
    for assertions in honest:
        votes.update({_shape(a) for a in assertions if _predicts_a_reading(a)})
    merged = [
        assertion
        for assertions in honest
        for assertion in assertions
        if not _predicts_a_reading(assertion) or votes[_shape(assertion)] > 1
    ]
    unanimous: set[int] = (
        set.intersection(*({item.mechanic for item in exam.unverifiable} for exam in exams))
        if exams
        else set()
    )
    reasons: dict[int, UncheckableMechanic] = {}
    for exam in exams:
        for item in exam.unverifiable:
            if item.mechanic in unanimous:
                reasons.setdefault(item.mechanic, item)
    return RuntimeExam(assertions=dedupe(merged), unverifiable=list(reasons.values()))


#: How many times one design is examined before its answers are merged.
#:
#: Four is measured, not chosen. Nine sittings were recorded for each of the
#: five finished designs in `studio-projects/` and every subset of them scored
#: offline against the same recorded readings, so that a change in the merge
#: could not be read as a change in the model's mood. For
#: `minero-observable` -- the design whose coverage prompted this, two of its
#: seven mechanics checked on a good day -- three sittings in nine checked
#: nothing at all. Of the 126 four-subsets of those nine, every single one
#: checks both mechanics; of the 84 three-subsets, one does not. Two sittings
#: still leave three in thirty-six checking nothing.
#:
#: A fifth pass was scored too and buys nothing there; it lifts the two
#: designs that declare no observables of their own from 44% to 55% of runs
#: finding their one thin `g_state` attribution, which is a checkbox better
#: won by declaring an observable than by paying for another opinion.
#:
#: **Three, not four, and the fourth was given up for a reason and not to
#: save a call.** This sits inside `write_program`'s attempt loop, and until
#: `EXAMINATION_EFFORT` existed each pass was a full-effort reasoning call
#: with 64000 tokens of room: four of the most expensive requests in the
#: pipeline, per set of symbols, to derive an expectation. Lowering what a
#: pass costs is what paid for keeping the coverage, and it pays for more of
#: it than dropping to two would have -- three passes at `medium` cost less
#: than one at `high`, where two would have cost the 1-in-12 of the
#: three-subsets above turning into the 1-in-12 of the two-subsets, which is
#: a gate that abstains on a design it should have checked.
#:
#: The scoring above is what makes the difference sayable: of the 84
#: three-subsets of those nine sittings, one checks nothing on
#: `minero-observable`; of the 36 two-subsets, three do. This buys back the
#: money without buying it out of the one design that was already marginal.
EXAMINATION_PASSES = 3

#: What deriving an expectation is worth, and the reason it can be lowered at
#: all: the exam reads a design that is already written and a list of symbols
#: the program already exposes, and says what memory must show. It is not open
#: work -- the answer is bounded by the mechanics the design declares.
EXAMINATION_EFFORT: Effort = "medium"
EXAMINATION_MAX_TOKENS = 16000


class RepeatedExaminer:
    """Sits one examiner's exam several times and merges the answers.

    A wrapper rather than a loop inside `runtime_examination` so that what
    calls the API decides how often, and every offline caller -- every test,
    every injected fake -- goes on getting exactly one call to exactly one
    examiner.

    The passes run concurrently: this sits inside `write_program`'s attempt
    loop, where the alternative is three sequential reasoning calls added to
    the wait before a line of C is written. A pass that raises is dropped and
    the rest are merged; only when every pass fails does this raise, so
    `runtime_examination` goes on treating a model having a bad day as no
    examiner at all rather than as a failed program.
    """

    def __init__(self, examiner: RuntimeExaminer, passes: int = EXAMINATION_PASSES) -> None:
        self.examiner = examiner
        self.passes = max(1, passes)

    def examine(
        self, project: GameProject, steps: list[dict[str, Any]], symbols: list[str]
    ) -> RuntimeExam:
        exams: list[RuntimeExam] = []
        failures: list[Exception] = []
        with ThreadPoolExecutor(max_workers=self.passes) as pool:
            futures = [
                pool.submit(self.examiner.examine, project, steps, symbols)
                for _ in range(self.passes)
            ]
            for future in futures:
                try:
                    exams.append(future.result())
                except Exception as exc:  # noqa: BLE001 -- see docstring
                    failures.append(exc)
        if not exams:
            raise failures[0]
        return merge_exams(exams)


class ResponsesRuntimeExaminer:
    """Derives the run's expectations with the model."""

    def __init__(self, client: Any, model: str = "claude-opus-5") -> None:
        self.client = client
        self.model = model

    def examine(
        self, project: GameProject, steps: list[dict[str, Any]], symbols: list[str]
    ) -> RuntimeExam:
        return structured(
            self.client,
            self.model,
            system=(
                "You decide what a fixed, unsteered emulator run of a game must "
                "show in memory. You assert only what every correct program must "
                "produce in that exact run, and you say plainly which rules the "
                "run cannot check. You never assert that the player achieves "
                "anything."
            ),
            user=examination_prompt(project, steps, symbols),
            schema=RuntimeExam,
            effort=EXAMINATION_EFFORT,
            max_tokens=EXAMINATION_MAX_TOKENS,
            missing="the model did not return a runtime examination",
        )
