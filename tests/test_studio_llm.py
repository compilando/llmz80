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
from pydantic import BaseModel, Field

from llmz80.studio.llm import DEFAULT_MAX_TOKENS, structured
from llmz80.studio.spend import BudgetExhausted, run_budget, stage
from tests.conftest import FakeMessageStream, fake_message


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


class _Bounded(BaseModel):
    """A schema whose limit the API strips before the model ever sees it."""

    notes: str = Field(default="", max_length=240)


class _UsageMessages:
    """A `client.messages` that answers with usage, the way the real one does."""

    def __init__(self, parsed, usage):
        self.parsed = parsed
        self.usage = usage
        self.calls = []

    def stream(self, **kwargs):
        self.calls.append(kwargs)
        return FakeMessageStream(
            fake_message(self.parsed, usage=self.usage, stop_reason="end_turn")
        )


class _UsageClient:
    def __init__(self, parsed, usage):
        self.messages = _UsageMessages(parsed, usage)


class _Usage:
    def __init__(self, input_tokens=0, output_tokens=0, cache_read=0, cache_write=0):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.cache_read_input_tokens = cache_read
        self.cache_creation_input_tokens = cache_write


def test_the_schemas_own_limits_are_spelled_out_in_the_system_prompt():
    """The API strips `maxLength` and re-emits it as `{maxLength: 240}`.

    `studio-projects/cesar-mondongo-basket/studio.log` shows what that costs:
    the drafting stage and the design stage each produced a whole design and
    each had it refused for `entities.*.notes` at 240 characters -- 550 s and
    409 s of reasoning, billed and discarded, over a rule the model was never
    in a position to know.
    """
    client = _FakeClient(_Bounded(notes="short"))

    structured(client, "claude-opus-5", system="s", user="u", schema=_Bounded, missing="m")

    assert "240 characters" in client.messages.calls[0]["system"]


def test_a_schema_with_no_limits_leaves_the_system_prompt_exactly_as_it_was():
    """Nine call sites must keep the request they have, byte for byte."""
    client = _FakeClient(_Verdict(ok=True))

    structured(client, "claude-opus-5", system="s", user="u", schema=_Verdict, missing="m")

    assert client.messages.calls[0]["system"] == "s"


def test_the_limits_ride_inside_the_cached_prefix_not_after_it():
    """They are derived from the schema, so they are the same bytes every
    call -- which makes them cacheable, and makes putting them after the
    breakpoint a per-call charge for nothing."""
    client = _FakeClient(_Bounded(notes="x"))

    structured(
        client,
        "claude-opus-5",
        system="you draft designs",
        cached_prefix="the whole brief",
        user="draft",
        schema=_Bounded,
        missing="m",
    )

    blocks = client.messages.calls[0]["system"]
    assert "240 characters" in blocks[0]["text"]
    assert blocks[1] == {
        "type": "text",
        "text": "the whole brief",
        "cache_control": {"type": "ephemeral", "ttl": "1h"},
    }


def test_a_call_is_billed_to_the_open_run():
    client = _UsageClient(_Verdict(ok=True), _Usage(input_tokens=1000, output_tokens=2000))

    with run_budget() as ledger:
        with stage("program"):
            structured(client, "claude-opus-5", system="s", user="u", schema=_Verdict, missing="m")

    assert len(ledger.calls) == 1
    assert ledger.calls[0].input_tokens == 1000
    assert ledger.calls[0].output_tokens == 2000
    assert ledger.calls[0].stage == "program"


def test_cache_reads_and_writes_are_billed_at_their_own_rates():
    client = _UsageClient(_Verdict(ok=True), _Usage(cache_read=5000, cache_write=1000))

    with run_budget() as ledger:
        structured(client, "claude-opus-5", system="s", user="u", schema=_Verdict, missing="m")

    assert ledger.calls[0].cache_read_tokens == 5000
    assert ledger.calls[0].cache_write_tokens == 1000


def test_a_refused_answer_is_billed_too():
    """A retry is not free, and the survey that produced this module could not
    see them at all: two of the five stages of the cesar run spent an entire
    deliberation on an answer pydantic then threw away."""
    client = _ScriptedClient(_too_long(), _Verdict(ok=True))

    with run_budget() as ledger:
        structured(client, "claude-opus-5", system="s", user="u", schema=_Verdict, missing="m")

    assert len(ledger.calls) == 2


def test_a_call_whose_usage_never_arrived_is_billed_at_its_ceiling():
    """`get_final_message` raises from inside pydantic and the usage on the
    message it was parsing is not always recoverable. Charging that zero would
    let an unbounded number of them slip under a dollar ceiling."""
    client = _ScriptedClient(_too_long(), _Verdict(ok=True))

    with run_budget() as ledger:
        structured(
            client,
            "claude-opus-5",
            system="s",
            user="u",
            schema=_Verdict,
            missing="m",
            max_tokens=8000,
        )

    assert ledger.calls[0].estimated is True
    assert ledger.calls[0].output_tokens == 8000


def test_a_run_over_its_ceiling_makes_no_further_call_at_all():
    """The refusal has to arrive before the request, or it costs what it was
    trying to save."""
    client = _UsageClient(_Verdict(ok=True), _Usage(output_tokens=1_000_000))

    with run_budget(ceiling_dollars=1.0):
        structured(client, "claude-opus-5", system="s", user="u", schema=_Verdict, missing="m")
        with pytest.raises(BudgetExhausted):
            structured(client, "claude-opus-5", system="s", user="u", schema=_Verdict, missing="m")

    assert len(client.messages.calls) == 1


def test_with_no_run_open_nothing_is_billed_and_nothing_refuses():
    """Every offline caller -- every test, every injected fake -- goes on
    working without knowing this module counts anything."""
    client = _FakeClient(_Verdict(ok=True))

    structured(client, "claude-opus-5", system="s", user="u", schema=_Verdict, missing="m")

    assert len(client.messages.calls) == 1


class _BetaMessages:
    def __init__(self, parsed):
        self.parsed = parsed
        self.calls = []

    def stream(self, **kwargs):
        self.calls.append(kwargs)
        return FakeMessageStream(fake_message(self.parsed))


class _BetaClient:
    """A client whose beta endpoint is the only one that answers."""

    def __init__(self, parsed):
        self.messages = _FakeMessages(parsed)
        self.beta = type("Beta", (), {"messages": _BetaMessages(parsed)})()


def test_a_task_budget_goes_to_the_beta_endpoint_with_its_beta_named():
    """`task_budget` exists in `BetaOutputConfigParam` and nowhere else."""
    client = _BetaClient(_Verdict(ok=True))

    structured(
        client,
        "claude-opus-5",
        system="s",
        user="u",
        schema=_Verdict,
        missing="m",
        task_budget=48000,
    )

    assert client.messages.calls == []
    call = client.beta.messages.calls[0]
    assert call["betas"] == ["task-budgets-2026-03-13"]
    assert call["output_config"]["task_budget"] == {"type": "tokens", "total": 48000}


def test_a_task_budget_below_the_api_minimum_is_raised_to_it():
    """`total` under 20000 is a 400, and a 400 here arrives minutes into a run."""
    client = _BetaClient(_Verdict(ok=True))

    structured(
        client,
        "claude-opus-5",
        system="s",
        user="u",
        schema=_Verdict,
        missing="m",
        task_budget=1000,
    )

    assert client.beta.messages.calls[0]["output_config"]["task_budget"]["total"] == 20000


def test_without_a_task_budget_the_plain_endpoint_is_used():
    """Nine call sites must not be moved behind a beta flag to serve one."""
    client = _BetaClient(_Verdict(ok=True))

    structured(client, "claude-opus-5", system="s", user="u", schema=_Verdict, missing="m")

    assert len(client.messages.calls) == 1
    assert client.beta.messages.calls == []


def test_a_task_budget_and_an_effort_level_share_one_output_config():
    client = _BetaClient(_Verdict(ok=True))

    structured(
        client,
        "claude-opus-5",
        system="s",
        user="u",
        schema=_Verdict,
        missing="m",
        effort="high",
        task_budget=32000,
    )

    config = client.beta.messages.calls[0]["output_config"]
    assert config["effort"] == "high"
    assert config["task_budget"]["total"] == 32000


def test_a_task_budget_is_dropped_on_a_model_that_does_not_take_one():
    """A 400 here does not arrive politely: it arrives minutes into a paid run.

    Task budgets are an Opus 5 / Fable 5 / Sonnet 5 / Opus 4.8 / 4.7 feature.
    `config.yml` lets a role be pointed at any model, so the writer can be put
    on one that would reject the parameter -- and the parameter is an
    optimisation, not a requirement, so the request is worth more than it is.
    """
    client = _BetaClient(_Verdict(ok=True))

    structured(
        client,
        "claude-haiku-4-5",
        system="s",
        user="u",
        schema=_Verdict,
        missing="m",
        task_budget=48000,
    )

    assert client.beta.messages.calls == []
    assert "output_config" not in client.messages.calls[0]
