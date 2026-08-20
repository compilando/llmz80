"""What a run costs while it is costing it, and the ceiling it may not pass.

Studio read `usage` off nothing. Ten call sites asked a model a question and
threw the accounting half of every answer away, and `llmz80/quality/
benchmark.py` reserved `input_tokens` and `output_tokens` and left them
`None`. The only way to learn what a game had cost was to read wall-clock
times out of `studio.log` and multiply by a guessed throughput, which is how
the survey that produced this module had to be done.

`studio-projects/cesar-mondongo-basket` is the run it was done on, and it is
worth stating what it did, because both halves of this module answer to it.
Five stages, about nineteen model calls, roughly 250k output tokens -- and it
ended not on a decision but on `Your credit balance is too low to access the
Anthropic API`, three attempts into a program stage that had already run for
59 minutes. Nothing in the pipeline knew what it had spent, and nothing could
have stopped it.

So: a `Ledger` **counts**, and a ceiling **stops**.

**The bill is output, not input.** That run sent about 120k input tokens and
received about 250k output tokens: $0.60 against $6.30. It is the reason the
prices below are kept per-direction rather than averaged, and the reason
`report` prints both -- an optimisation that halves the prompt and leaves the
reasoning alone moves almost nothing.

**A ceiling is a call count as well as a sum of money.** The retries in this
pipeline multiply rather than add: `structured(attempts=2)` inside
`write_program(attempts=5)` inside `RepeatedExaminer`'s four passes reaches
118 model calls for a single `llmz80 make`, and every one of them is
individually well under any per-call limit. A dollar ceiling catches that late
and a call ceiling catches it early, so both exist.

**A global, not a contextvar.** `RepeatedExaminer` runs its passes on a
`ThreadPoolExecutor`, and `Executor.submit` does not carry a context into the
worker: four of the most expensive calls in the pipeline would have recorded
into nothing. A module-level ledger behind a lock is what those threads can
reach, and `run_budget` is what keeps it from leaking between tests.
"""

from __future__ import annotations

import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterator

#: Published Anthropic rates in dollars per million tokens, input then output
#: (2026-08). Only the models Studio can be pointed at are here; anything else
#: is priced by `_UNKNOWN` below.
PRICES: dict[str, tuple[float, float]] = {
    "claude-opus-5": (5.0, 25.0),
    "claude-opus-4-8": (5.0, 25.0),
    "claude-opus-4-7": (5.0, 25.0),
    "claude-opus-4-6": (5.0, 25.0),
    "claude-sonnet-5": (3.0, 15.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-haiku-4-5": (1.0, 5.0),
    "claude-fable-5": (10.0, 50.0),
}

#: What a model nobody listed is charged. The dearest rate known, not zero and
#: not an average: this number's only job is to keep a ceiling working, and a
#: mistyped model name that reads as free disables the one guard that would
#: have caught it.
_UNKNOWN = (10.0, 50.0)

#: A read off the prompt cache is a tenth of the input rate; a write at the
#: hour-long TTL is double it. `llm.py` sends `ttl="1h"` and explains why the
#: API's five-minute default is more expensive here than not caching at all,
#: so 2.0 is the multiplier this project actually pays.
_CACHE_READ = 0.1
_CACHE_WRITE = 2.0


class BudgetExhausted(RuntimeError):
    """The run has spent what it was allowed and the next call was refused.

    A `RuntimeError` rather than a `ValueError` so it passes straight through
    the `except ValueError` a stage wraps its refusals in: a design that could
    not be written and a budget that ran out are not the same outcome, and
    telling somebody to run the stage again is wrong advice for the second.
    """


@dataclass
class Call:
    """One request, priced.

    `estimated` marks a call whose usage never arrived -- see `Ledger.record`
    -- so a report can say which of its numbers are measurements and which are
    upper bounds.
    """

    stage: str
    model: str
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int
    dollars: float
    estimated: bool


@dataclass
class Ledger:
    """Every call this run has made, and what it is allowed to make.

    `ceiling_dollars` and `ceiling_calls` are both optional and both hard.
    `None` means unbounded, which is what an offline caller and every test
    gets; `llmz80 make` sets them from `config.yml`.
    """

    ceiling_dollars: float | None = None
    ceiling_calls: int | None = None
    calls: list[Call] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    @property
    def dollars(self) -> float:
        with self._lock:
            return sum(call.dollars for call in self.calls)

    def check(self) -> None:
        """Raise if this run has already spent what it was allowed.

        Asked *before* a call rather than after one, so the refusal costs
        nothing. It deliberately does not try to predict what the pending call
        will cost: `max_tokens` is the only bound available and it is the
        ceiling rather than the expectation, so predicting with it would
        refuse the last affordable call of nearly every run.
        """
        spent, made = self.dollars, len(self.calls)
        if self.ceiling_dollars is not None and spent >= self.ceiling_dollars:
            raise BudgetExhausted(
                f"this run has spent ${spent:.2f} of its ${self.ceiling_dollars:.2f} "
                f"ceiling over {made} model call(s), so no further call was made. "
                "Raise `budget.dollars` in config.yml to allow more."
            )
        if self.ceiling_calls is not None and made >= self.ceiling_calls:
            raise BudgetExhausted(
                f"this run has made {made} model calls, its whole allowance of "
                f"{self.ceiling_calls}, costing ${spent:.2f}, so no further call was "
                "made. Raise `budget.calls` in config.yml to allow more."
            )

    def record(
        self,
        *,
        model: str,
        stage_name: str | None = None,
        input_tokens: int | None = 0,
        output_tokens: int | None = 0,
        cache_read_tokens: int | None = 0,
        cache_write_tokens: int | None = 0,
        max_tokens: int = 0,
    ) -> Call:
        """Price one call and add it to the run.

        `output_tokens=None` means the usage never arrived, which happens for
        real: pydantic raises from inside `get_final_message`, and the message
        it was parsing is not always recoverable from the stream. Such a call
        is charged at `max_tokens` -- its ceiling, so an upper bound -- rather
        than at zero. Zero would let an unbounded number of refused answers
        slip under a dollar ceiling, and the only thing an over-estimate can
        do is stop a run early, which is the cheaper mistake.
        """
        rate_in, rate_out = PRICES.get(model, _UNKNOWN)
        estimated = output_tokens is None
        counted_out = max_tokens if estimated else int(output_tokens or 0)
        counted_in = int(input_tokens or 0)
        read = int(cache_read_tokens or 0)
        written = int(cache_write_tokens or 0)
        dollars = (
            counted_in * rate_in
            + counted_out * rate_out
            + read * rate_in * _CACHE_READ
            + written * rate_in * _CACHE_WRITE
        ) / 1_000_000
        call = Call(
            stage=stage_name if stage_name is not None else current_stage(),
            model=model,
            input_tokens=counted_in,
            output_tokens=counted_out,
            cache_read_tokens=read,
            cache_write_tokens=written,
            dollars=dollars,
            estimated=estimated,
        )
        with self._lock:
            self.calls.append(call)
        return call

    def report(self) -> str:
        """One line per stage and one for the run, for a log or a terminal.

        Written for somebody deciding what to change next, which is why the
        two token directions stay apart: the survey this module came out of
        turned entirely on the input half being negligible.
        """
        with self._lock:
            calls = list(self.calls)
        if not calls:
            return "no model calls were made"
        lines = []
        for name in dict.fromkeys(call.stage for call in calls):
            of_stage = [call for call in calls if call.stage == name]
            lines.append(
                f"  {name}: {len(of_stage)} call(s), "
                f"{sum(call.input_tokens for call in of_stage):,} in / "
                f"{sum(call.output_tokens for call in of_stage):,} out, "
                f"${sum(call.dollars for call in of_stage):.2f}"
            )
        total = sum(call.dollars for call in calls)
        estimated = sum(1 for call in calls if call.estimated)
        footer = f"{len(calls)} call(s), ${total:.2f}"
        if estimated:
            footer += f" ({estimated} charged at their ceiling, usage never arrived)"
        return "\n".join(lines + [f"  total: {footer}"])


#: The run currently open, if any. See the module docstring for why this is a
#: module global and not a `contextvar`.
_LEDGER: Ledger | None = None

#: What the calls being made right now are for. A plain string rather than an
#: enum: `pipeline.py` already names its stages for `studio.log` and a second
#: vocabulary to keep in step with those would drift.
_STAGE = "unattributed"


def current_ledger() -> Ledger | None:
    """The open run's ledger, or `None` when nobody opened one."""
    return _LEDGER


def current_stage() -> str:
    """What is being paid for right now."""
    return _STAGE


@contextmanager
def run_budget(
    ceiling_dollars: float | None = None, ceiling_calls: int | None = None
) -> Iterator[Ledger]:
    """Open a run with a ceiling, and close it again afterwards.

    Restores whatever was there before rather than clearing to `None`, so a
    nested run -- a test inside a test, a benchmark driving several games --
    cannot silently discard its parent's accounting.
    """
    global _LEDGER
    previous = _LEDGER
    ledger = Ledger(ceiling_dollars=ceiling_dollars, ceiling_calls=ceiling_calls)
    _LEDGER = ledger
    try:
        yield ledger
    finally:
        _LEDGER = previous


@contextmanager
def stage(name: str) -> Iterator[None]:
    """Attribute every call made inside to `name`.

    Set globally for the same reason the ledger is: the four passes of
    `RepeatedExaminer` run on threads that would otherwise be attributed to
    nothing, and they belong to whichever stage opened them.
    """
    global _STAGE
    previous = _STAGE
    _STAGE = name
    try:
        yield
    finally:
        _STAGE = previous
