"""The one adapter every structured Studio call goes through.

Eight call sites across `llmz80/studio` used to spell out the same request
by hand -- a system prompt, a user prompt, a pydantic schema, and the same
four-line "was it None?" check with only the error message differing. They
now all go through `structured`, so the shape of a request to the model is
described once, and a fake client in a test stands in for all eight.

No network call is made anywhere in this file: `client.messages.parse` is
replaced by a fake that records the kwargs it received.
"""

import pytest
from pydantic import BaseModel

from llmz80.studio.llm import structured


class _Verdict(BaseModel):
    ok: bool


class _FakeMessages:
    """Stands in for `client.messages`: records the kwargs `parse` received."""

    def __init__(self, parsed):
        self.parsed = parsed
        self.calls = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        return type("Response", (), {"parsed_output": self.parsed})()


class _FakeClient:
    def __init__(self, parsed):
        self.messages = _FakeMessages(parsed)


def test_the_system_prompt_travels_as_its_own_parameter():
    """Not as the first entry of `messages`.

    This is the one difference that would silently degrade rather than fail:
    a system prompt sent as an ordinary user turn still produces an answer,
    just one that no longer carries system authority. Asserting on it here
    is what stops a future edit from quietly putting it back in the list.
    """
    client = _FakeClient(_Verdict(ok=True))

    structured(
        client,
        "claude-opus-5",
        system="YOU ARE A JUDGE",
        user="judge this",
        schema=_Verdict,
        missing="the model did not return a verdict",
    )

    call = client.messages.calls[0]
    assert call["system"] == "YOU ARE A JUDGE"
    assert call["messages"] == [{"role": "user", "content": "judge this"}]


def test_the_schema_travels_as_output_format_and_the_parsed_value_comes_back():
    client = _FakeClient(_Verdict(ok=True))

    verdict = structured(
        client,
        "claude-opus-5",
        system="s",
        user="u",
        schema=_Verdict,
        missing="the model did not return a verdict",
    )

    assert verdict.ok is True
    assert client.messages.calls[0]["output_format"] is _Verdict


def test_max_tokens_is_always_sent():
    """The API rejects a request without it, so no caller may forget it."""
    client = _FakeClient(_Verdict(ok=True))

    structured(
        client, "claude-opus-5", system="s", user="u", schema=_Verdict, missing="m"
    )

    assert client.messages.calls[0]["max_tokens"] > 0


def test_no_sampling_parameters_are_sent():
    """`temperature`, `top_p` and `top_k` are rejected outright by the model.

    `config.yml` carried a `temperature: 0.3` for the OpenAI models this
    module replaced, and sending it to Claude Opus 5 is a 400 rather than a
    parameter that gets ignored. Nothing here may reintroduce one.
    """
    client = _FakeClient(_Verdict(ok=True))

    structured(
        client, "claude-opus-5", system="s", user="u", schema=_Verdict, missing="m"
    )

    call = client.messages.calls[0]
    assert "temperature" not in call
    assert "top_p" not in call
    assert "top_k" not in call


def test_tools_are_sent_only_when_a_caller_asks_for_them():
    """Only `reference.py` searches the web; the other seven must not carry
    a `tools` key at all rather than an empty list."""
    without = _FakeClient(_Verdict(ok=True))
    structured(
        without, "claude-opus-5", system="s", user="u", schema=_Verdict, missing="m"
    )
    assert "tools" not in without.messages.calls[0]

    search = [{"type": "web_search_20260209", "name": "web_search"}]
    with_tools = _FakeClient(_Verdict(ok=True))
    structured(
        with_tools,
        "claude-opus-5",
        system="s",
        user="u",
        schema=_Verdict,
        missing="m",
        tools=search,
    )
    assert with_tools.messages.calls[0]["tools"] == search


def test_an_unparsed_answer_raises_the_callers_own_message():
    """Each of the eight call sites says what *it* failed to get back, and
    its own test matches on that wording -- so the message is the caller's,
    not this module's."""
    client = _FakeClient(None)

    with pytest.raises(ValueError, match="did not return a coherence verdict"):
        structured(
            client,
            "claude-opus-5",
            system="s",
            user="u",
            schema=_Verdict,
            missing="the model did not return a coherence verdict",
        )


class _ScriptedMessages:
    """Raises what it is told to, in order, then returns a good answer."""

    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)
        self.calls = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        outcome = self.outcomes[min(len(self.calls), len(self.outcomes)) - 1]
        if isinstance(outcome, Exception):
            raise outcome
        return type("Response", (), {"parsed_output": outcome})()


class _ScriptedClient:
    def __init__(self, *outcomes):
        self.messages = _ScriptedMessages(*outcomes)


def _too_long() -> Exception:
    """The real failure this retry exists for.

    The SDK strips `maxLength` out of the schema it sends and validates it
    client-side afterwards, so the model is never told the limit as a rule
    and pydantic raises inside `messages.parse`. Reproduced here through the
    same pydantic model rather than a hand-built exception, so the message
    the retry feeds back is the message the API path really produces.
    """
    from pydantic import BaseModel, Field, ValidationError

    class _Bounded(BaseModel):
        note: str = Field(max_length=5)

    try:
        _Bounded(note="far too long to fit")
    except ValidationError as exc:
        return exc
    raise AssertionError("that should not have validated")


def test_an_answer_the_schema_refuses_is_asked_again_with_what_was_wrong():
    """A constraint the model was never shown cannot be obeyed by luck twice,
    so the retry has to say what broke -- and pydantic's own message already
    says it exactly ("String should have at most 5 characters")."""
    client = _ScriptedClient(_too_long(), _Verdict(ok=True))

    verdict = structured(
        client, "claude-opus-5", system="s", user="u", schema=_Verdict, missing="m"
    )

    assert verdict.ok is True
    assert len(client.messages.calls) == 2
    retry = client.messages.calls[1]["messages"][0]["content"]
    assert "at most 5 characters" in retry
    assert retry.startswith("u")


def test_a_model_that_keeps_breaking_the_schema_gives_up_with_the_last_error():
    client = _ScriptedClient(_too_long())

    with pytest.raises(ValueError, match="at most 5 characters"):
        structured(
            client, "claude-opus-5", system="s", user="u", schema=_Verdict, missing="m"
        )

    assert len(client.messages.calls) == 2


def test_a_good_first_answer_is_never_asked_twice():
    client = _ScriptedClient(_Verdict(ok=True))

    structured(client, "claude-opus-5", system="s", user="u", schema=_Verdict, missing="m")

    assert len(client.messages.calls) == 1
