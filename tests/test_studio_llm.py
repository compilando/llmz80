"""The one adapter every structured Studio call goes through.

Eight call sites across `llmz80/studio` used to spell out the same request
by hand -- a system prompt, a user prompt, a pydantic schema, and the same
four-line "was it None?" check with only the error message differing. They
now all go through `structured`, so the shape of a request to the model is
described once, and a fake client in a test stands in for all eight.

No network call is made anywhere in this file: `client.messages.stream` is
replaced by a fake that records the kwargs it received and hands back a final
message, the way the real stream manager does.
"""

import pytest
from pydantic import BaseModel

from llmz80.studio.llm import DEFAULT_MAX_TOKENS, structured
from tests.conftest import FakeMessageStream


class _Verdict(BaseModel):
    ok: bool


class _FakeMessages:
    """Stands in for `client.messages`: records the kwargs `stream` received."""

    def __init__(self, parsed):
        self.parsed = parsed
        self.calls = []

    def stream(self, **kwargs):
        self.calls.append(kwargs)
        return FakeMessageStream(type("Response", (), {"parsed_output": self.parsed})())


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

    structured(client, "claude-opus-5", system="s", user="u", schema=_Verdict, missing="m")

    assert client.messages.calls[0]["max_tokens"] > 0


def test_no_sampling_parameters_are_sent():
    """`temperature`, `top_p` and `top_k` are rejected outright by the model.

    `config.yml` carried a `temperature: 0.3` for the OpenAI models this
    module replaced, and sending it to Claude Opus 5 is a 400 rather than a
    parameter that gets ignored. Nothing here may reintroduce one.
    """
    client = _FakeClient(_Verdict(ok=True))

    structured(client, "claude-opus-5", system="s", user="u", schema=_Verdict, missing="m")

    call = client.messages.calls[0]
    assert "temperature" not in call
    assert "top_p" not in call
    assert "top_k" not in call


def test_tools_are_sent_only_when_a_caller_asks_for_them():
    """Only `reference.py` searches the web; the other seven must not carry
    a `tools` key at all rather than an empty list."""
    without = _FakeClient(_Verdict(ok=True))
    structured(without, "claude-opus-5", system="s", user="u", schema=_Verdict, missing="m")
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

    def stream(self, **kwargs):
        self.calls.append(kwargs)
        outcome = self.outcomes[min(len(self.calls), len(self.outcomes)) - 1]
        if isinstance(outcome, Exception):
            return FakeMessageStream(outcome)
        return FakeMessageStream(type("Response", (), {"parsed_output": outcome})())


class _ScriptedClient:
    def __init__(self, *outcomes):
        self.messages = _ScriptedMessages(*outcomes)


def _too_long() -> Exception:
    """The real failure this retry exists for.

    The SDK strips `maxLength` out of the schema it sends and validates it
    client-side afterwards, so the model is never told the limit as a rule
    and pydantic raises while the stream is finished. Reproduced here through the
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
        structured(client, "claude-opus-5", system="s", user="u", schema=_Verdict, missing="m")

    assert len(client.messages.calls) == 2


def test_a_good_first_answer_is_never_asked_twice():
    client = _ScriptedClient(_Verdict(ok=True))

    structured(client, "claude-opus-5", system="s", user="u", schema=_Verdict, missing="m")

    assert len(client.messages.calls) == 1


class _TruncatedMessages:
    """A model that spent its whole budget thinking and answered nothing."""

    def __init__(self):
        self.calls = []

    def stream(self, **kwargs):
        self.calls.append(kwargs)
        return FakeMessageStream(
            type("Response", (), {"parsed_output": None, "stop_reason": "max_tokens"})()
        )


class _TruncatedClient:
    def __init__(self):
        self.messages = _TruncatedMessages()


def test_a_truncated_answer_says_so_instead_of_reading_as_a_refusal():
    """`stop_reason: max_tokens` is a ceiling to raise, not a prompt to fix.

    A real run spent all of its output budget reasoning and came back with an
    empty thinking block, so `parsed_output` was None and the program writer
    reported "the model did not return program sources" -- which sent the
    reader to the prompt rather than to `max_tokens`.
    """
    client = _TruncatedClient()

    with pytest.raises(ValueError) as failure:
        structured(
            client,
            "claude-opus-5",
            system="s",
            user="u",
            schema=_Verdict,
            missing="the model did not return program sources",
            max_tokens=1234,
        )

    assert "the model did not return program sources" in str(failure.value)
    assert "1234 token ceiling" in str(failure.value)


def test_the_default_ceiling_holds_a_deliberation_and_a_program():
    """Thinking tokens are charged to `max_tokens` at this model's effort.

    16000 was sized for the C program alone and a whole run was lost to it.
    """
    assert DEFAULT_MAX_TOKENS >= 64000


def test_effort_travels_inside_output_config():
    """Nested, so the schema and the level reach the model together.

    `output_config` is where the level goes and also where the SDK puts the
    schema: `messages.stream` merges them into `{**output_config, "format":
    <schema>}`, so neither displaces the other. There is no top-level `effort`
    to send it to instead -- that spelling is a `TypeError` out of the SDK --
    so what this pins is the nesting, and that `output_format` survives it.
    """
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


def test_effort_survives_a_retry():
    """The repair attempt is the same request with a different user turn.

    A rebuild inside the loop would drop the level silently -- the writer's
    repair attempts would each cost the full reasoning the caller paid to
    avoid, and every other test here answers on the first attempt.
    """
    client = _ScriptedClient(_too_long(), _Verdict(ok=True))

    structured(
        client,
        "claude-opus-5",
        system="s",
        user="u",
        schema=_Verdict,
        missing="m",
        effort="medium",
    )

    assert client.messages.calls[1]["output_config"] == {"effort": "medium"}


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
    """Nine of the ten call sites pass no prefix, and their request must be
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


def test_a_cached_prefix_and_an_effort_level_both_reach_the_request():
    """They are built in the same function, and the writer -- the one caller
    that wants a cached prefix -- is also the one that names an effort level.
    A refactor that dropped either would leave the other's test green.
    """
    client = _FakeClient(_Verdict(ok=True))

    structured(
        client,
        "claude-opus-5",
        system="s",
        cached_prefix="p",
        user="u",
        schema=_Verdict,
        missing="m",
        effort="medium",
    )

    call = client.messages.calls[0]
    assert call["output_config"] == {"effort": "medium"}
    assert call["system"][1]["cache_control"] == {"type": "ephemeral", "ttl": "1h"}
