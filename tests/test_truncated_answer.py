"""A cut-off answer should say it was cut off.

Three writing attempts across two runs of a basketball game died reporting

    Invalid JSON: EOF while parsing a string at line 1 column 27294

which is pydantic describing a string that stops in the middle. It reads as a
schema mismatch -- something wrong with what the model said -- and it is not:
the answer never finished arriving. Whoever reads it goes looking at the schema
or the prompt, and the causes are the token ceiling or a stream that dropped.

`llm.structured` already knew how to say this, in the branch for an answer that
comes back *empty*: `stop_reason == "max_tokens"` raises a sentence naming the
ceiling. A truncated answer never reaches that branch, because the SDK raises
while parsing and the handler above catches it as an ordinary refusal.

Worth separating for the retry too, and not only for the report. Feeding a
model "your JSON was malformed at column 27294" when its answer was cut off
tells it to fix punctuation it never got to write; what it can act on is that
the answer was too long.
"""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from llmz80.studio.llm import structured
from tests.conftest import FakeMessageStream, fake_message


class Program(BaseModel):
    summary: str
    main_c: str


def _truncation() -> ValidationError:
    """The error the SDK really raises for a half-arrived answer."""
    try:
        Program.model_validate_json('{"summary":"a game","main_c":"void main(void) { whi')
    except ValidationError as exc:
        return exc
    raise AssertionError("that JSON should not have validated")


def _mismatch() -> ValidationError:
    """A complete answer that simply does not fit the schema."""
    try:
        Program.model_validate_json('{"summary":"a game"}')
    except ValidationError as exc:
        return exc
    raise AssertionError("that JSON should not have validated")


class _Client:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.requests = []
        self.messages = self

    def stream(self, **request):
        self.requests.append(request)
        return FakeMessageStream(self.outcomes.pop(0))


def _ask(client, attempts=1):
    return structured(
        client,
        "claude-opus-5",
        system="write a game",
        user="a breakout",
        schema=Program,
        missing="the model did not return program sources",
        attempts=attempts,
    )


class TestWhatTheReportSays:
    def test_a_truncated_answer_says_it_was_cut_off(self):
        client = _Client([_truncation()])

        with pytest.raises(ValueError) as raised:
            _ask(client)

        message = str(raised.value)
        assert "cut off" in message or "did not finish" in message

    def test_it_names_the_ceiling_so_the_reader_can_check_it(self):
        """The two causes are the ceiling and a dropped stream, and only one of
        them is a number anybody can look up."""
        client = _Client([_truncation()])

        with pytest.raises(ValueError) as raised:
            _ask(client)

        assert "64000" in str(raised.value)

    def test_an_answer_that_merely_does_not_fit_still_says_that(self):
        """The existing message is right for the case it was written for, and
        must not start claiming every refusal was a truncation."""
        client = _Client([_mismatch()])

        with pytest.raises(ValueError) as raised:
            _ask(client)

        message = str(raised.value)
        assert "did not fit Program" in message
        assert "cut off" not in message


class TestWhatTheRetryIsTold:
    def test_a_truncation_asks_for_a_shorter_answer(self):
        """Not for better punctuation. The model never reached the end of what
        it was writing, so the only thing it can act on is the length."""
        client = _Client([_truncation(), fake_message(Program(summary="s", main_c="c"))])

        _ask(client, attempts=2)

        retry = client.requests[1]["messages"][-1]["content"]
        assert "shorter" in retry or "too long" in retry

    def test_a_mismatch_still_gets_the_schema_complaint(self):
        client = _Client([_mismatch(), fake_message(Program(summary="s", main_c="c"))])

        _ask(client, attempts=2)

        retry = client.requests[1]["messages"][-1]["content"]
        assert "main_c" in retry

    def test_a_truncation_is_retried_rather_than_given_up_on(self):
        """It is the most transient failure this loop sees -- three of them in
        two runs, at three different lengths."""
        client = _Client([_truncation(), fake_message(Program(summary="s", main_c="c"))])

        answer = _ask(client, attempts=2)

        assert answer.summary == "s"
