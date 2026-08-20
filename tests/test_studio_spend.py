"""What a run costs, counted, and the ceiling it may not go through.

Nothing in Studio used to read `usage` off a response. `llmz80/quality/
benchmark.py` reserved the four keys for it and left them `None`, so the only
way to learn what a run had cost was to read wall-clock times out of
`studio.log` and guess at a throughput. `studio-projects/
cesar-mondongo-basket` is what that hid: three program attempts, one of them
25 minutes long and truncated before it emitted a closing brace, and the run
ended on `Your credit balance is too low to access the Anthropic API` rather
than on any decision anybody made.

Two separate things are being tested here. The ledger *counts*, so a run can
be read afterwards. The ceiling *stops*, so a run cannot reach the state that
one did.
"""

from concurrent.futures import ThreadPoolExecutor

import pytest

from llmz80.studio.spend import BudgetExhausted, Ledger, current_ledger, run_budget, stage


def test_a_call_is_priced_at_its_model_s_published_rate():
    ledger = Ledger()

    ledger.record(model="claude-opus-5", input_tokens=1_000_000, output_tokens=0)

    assert ledger.dollars == pytest.approx(5.0)


def test_output_is_the_expensive_half():
    """The finding the whole exercise rests on: the bill is thinking.

    A run of `cesar-mondongo-basket` spent about 120k input tokens and about
    250k output tokens; at these rates that is $0.60 against $6.30.
    """
    ledger = Ledger()

    ledger.record(model="claude-opus-5", input_tokens=1_000_000, output_tokens=1_000_000)

    assert ledger.dollars == pytest.approx(30.0)


def test_a_cache_read_costs_a_tenth_and_a_one_hour_write_costs_double():
    ledger = Ledger()

    ledger.record(model="claude-opus-5", cache_read_tokens=1_000_000)
    ledger.record(model="claude-opus-5", cache_write_tokens=1_000_000)

    assert ledger.dollars == pytest.approx(0.5 + 10.0)


def test_an_unknown_model_is_priced_at_the_dearest_rate_known():
    """A model nobody put in the table must not read as free.

    The ceiling is the only thing standing between a mistyped model name and
    the run this module exists to prevent, and a zero price would disable it
    silently.
    """
    ledger = Ledger()

    ledger.record(model="claude-something-unreleased", output_tokens=1_000_000)

    assert ledger.dollars >= 25.0


def test_the_dollar_ceiling_stops_the_next_call():
    ledger = Ledger(ceiling_dollars=1.0)
    ledger.record(model="claude-opus-5", output_tokens=100_000)  # $2.50

    with pytest.raises(BudgetExhausted) as refusal:
        ledger.check()

    assert "$1.00" in str(refusal.value)
    assert "$2.50" in str(refusal.value)


def test_the_call_ceiling_stops_the_next_call_too():
    """The worst case in this pipeline is a call count, not a token count.

    Nested retries multiply: `structured(attempts=2)` inside
    `write_program(attempts=5)` inside four concurrent examination passes is
    118 calls for one `llmz80 make`, and every one of them is under whatever
    per-call ceiling it was given.
    """
    ledger = Ledger(ceiling_calls=2)
    for _ in range(2):
        ledger.record(model="claude-opus-5", output_tokens=1)

    with pytest.raises(BudgetExhausted) as refusal:
        ledger.check()

    assert "2" in str(refusal.value)


def test_a_run_under_its_ceiling_is_not_disturbed():
    ledger = Ledger(ceiling_dollars=10.0, ceiling_calls=50)
    ledger.record(model="claude-opus-5", output_tokens=100_000)

    ledger.check()


def test_a_call_whose_tokens_never_arrived_is_charged_at_its_ceiling():
    """Conservative on purpose, and the reason is arithmetic.

    A `ValidationError` is raised from inside `get_final_message`, and the
    usage on the message it was parsing is not always recoverable. Charging
    that call zero would let an unbounded number of them slip under a dollar
    ceiling; charging it `max_tokens` can only ever stop a run early, which is
    the failure worth having.
    """
    ledger = Ledger()

    ledger.record(model="claude-opus-5", output_tokens=None, max_tokens=64_000)

    assert ledger.dollars == pytest.approx(1.6)
    assert ledger.calls[0].estimated is True


def test_concurrent_passes_all_land():
    """`RepeatedExaminer` records from four threads at once.

    A `+=` on a float from four threads loses updates, and the loss is
    invisible: the run finishes and the total is merely wrong.
    """
    ledger = Ledger()

    with ThreadPoolExecutor(max_workers=4) as pool:
        for _ in range(200):
            pool.submit(ledger.record, model="claude-opus-5", output_tokens=1000)

    assert len(ledger.calls) == 200
    assert ledger.dollars == pytest.approx(200 * 1000 * 25 / 1_000_000)


def test_with_no_run_open_there_is_no_ledger_and_nothing_raises():
    """Every offline caller -- every test, every injected fake -- pays nothing.

    `structured` asks for the current ledger on every call; a test that never
    opened a run must not have to know that.
    """
    assert current_ledger() is None


def test_a_run_opens_a_ledger_and_closes_it_again():
    with run_budget(ceiling_dollars=5.0) as ledger:
        assert current_ledger() is ledger

    assert current_ledger() is None


def test_a_stage_labels_the_calls_made_inside_it():
    with run_budget() as ledger:
        with stage("program"):
            ledger.record(model="claude-opus-5", output_tokens=1000)
        with stage("sprites"):
            ledger.record(model="claude-sonnet-5", output_tokens=1000)

    assert [call.stage for call in ledger.calls] == ["program", "sprites"]


def test_the_report_totals_each_stage_and_the_run():
    with run_budget() as ledger:
        with stage("program"):
            ledger.record(model="claude-opus-5", output_tokens=100_000)
            ledger.record(model="claude-opus-5", output_tokens=100_000)
        with stage("sprites"):
            ledger.record(model="claude-sonnet-5", output_tokens=10_000)

    report = ledger.report()

    assert "program" in report and "sprites" in report
    assert "2 call" in report
    assert "$5.15" in report


def test_the_report_of_a_run_that_called_nothing_says_so():
    """`llmz80 project build` calls no model at all, and prints this line."""
    assert "no model calls" in Ledger().report()
