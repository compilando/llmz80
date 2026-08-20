"""How Studio asks a model for a structured answer, described once.

Ten places in `llmz80/studio` ask a model a question whose answer must
satisfy a pydantic schema: the drafter, the reference researcher and the
design it proposes, the planner, both design examiners, the program writer,
the runtime examiner, and both grid drawers -- sprite sheets and tiles.
Every one of them used to spell the same request out by hand and follow it
with the same four-line check, differing only in the schema and in the words
of the error. That meant a change to how Studio talks to a model -- which is
exactly what moving off OpenAI's Responses API was -- had to be made ten
times, consistently, or not at all.

`structured` is that request. The callers keep what is genuinely theirs:
their system prompt, their schema, and the sentence they want to read when
the answer does not arrive.

Three things this module encodes that are easy to get wrong once and never
notice:

- **The system prompt is a parameter, not a message.** The Responses API
  this replaced took it as the first entry of `input`; the Messages API
  takes a `system` argument. A system prompt left in the message list still
  produces an answer, just one that carries no system authority -- a
  degradation with no error attached to it, which is why
  `tests/test_studio_llm.py` asserts on the parameter directly.

- **`max_tokens` is required**, so it is not optional here either. The
  default is sized for the largest caller: `generator.py` writes whole C
  programs, not verdicts.

- **No sampling parameters, ever.** `temperature`, `top_p` and `top_k` were
  removed from the model this targets; `config.yml` carried a
  `temperature: 0.3` for its predecessor, and sending it is a 400 rather
  than a value that gets ignored. Nothing here accepts one, so nothing can
  pass one through.

`effort` is a parameter, and it is left out of the request unless a caller
names a level: its default is already the high setting Studio wants, which is
why the `anthropic:` section of `config.yml` carries no key for it. (The
`openai:` section still carries `reasoning_effort` -- an OpenAI-era parameter
for a different API, read by `llmz80/utils/helpers.py` and the old generator
behind it, neither of which reaches this module. There is no config value here
to plumb through.)
The level goes *inside* `output_config` because that is the only place it
exists: the Messages API has no top-level `effort`, so one sent there is a
`TypeError` out of the SDK before a request is ever built -- loud, not silent.
Nesting it costs the schema nothing, because `messages.stream` merges the two
into `{**output_config, "format": <schema>}` (anthropic 0.122.0,
`resources/messages/messages.py:1156` -- the merge in the `stream` path, not
the one in `parse`, which this module cannot use at all: see the comment on
the call itself), spreading the caller's dict first -- so `output_format` and
`effort` compose rather than compete.

**`cached_prefix` is the stable half of a prompt, and it has to travel in
`system`.** The prompt cache is an *exact prefix match* over the rendered
request in the order `tools` -> `system` -> `messages`: the first differing
byte invalidates everything after it. A caller's stable text appended beside
its volatile text in the user turn would therefore be a different prefix on
every call and cache nothing at all -- the breakpoint has to sit ahead of
whatever changes, which means `system` and not `messages`. So a caller that
passes one gets two system blocks, the caller's own prompt and then the
prefix carrying the `cache_control`, and the retry loop below rewrites only
`messages` -- a repair attempt reads the cache the first attempt wrote.

**The TTL defaults to an hour, not to the API's five minutes**, and that is
not a preference. One program-writing attempt in this project takes four to
six minutes (measured: 195 s, 240 s, 282 s, 326 s across
`studio-projects/*/studio.log`), so under the 5-minute default the entry has
expired by the time the next attempt asks for it: every attempt pays the
1.25x cache *write* and reads nothing back, which is more expensive than not
caching. For the writer's 19 000-token prefix over the five attempts of a
repair loop: no caching bills 95k input tokens, a 5-minute TTL expiring each
time bills 119k, and the 1-hour TTL -- one 2x write, then four reads at 0.1x
-- bills 46k. "Simplifying" this back to the API default would make the
pipeline half again as expensive as having no cache.
"""

from __future__ import annotations

from typing import Any, Literal, Sequence, TypeVar, cast

from pydantic import BaseModel, ValidationError

from .schema_limits import constraint_notes
from .spend import current_ledger

Schema = TypeVar("Schema", bound=BaseModel)

#: The effort levels the API accepts, spelled out rather than imported from
#: `anthropic.types`: this module deliberately depends on a client's *shape*,
#: not on the SDK's type tree, which is what lets every test here pass a fake.
#: Narrowed to a `Literal` because nothing checks the value at runtime --
#: `OutputConfigParam` is a TypedDict -- so `"meduim"` would travel to the API
#: and come back a 400 `BadRequestError`, which the retry loop below does not
#: catch (it catches `ValidationError` only), after a paid round trip and, for
#: a per-tile call, minutes into a pipeline run. mypy refuses it for free.
Effort = Literal["low", "medium", "high", "xhigh", "max"]

#: The only two lifetimes a `cache_control` breakpoint accepts. A `Literal`
#: for the same reason `Effort` is one: `CacheControlEphemeralParam` is a
#: TypedDict (anthropic 0.122.0,
#: `types/cache_control_ephemeral_param.py` -- its own `ttl` is
#: `Literal["5m", "1h"]`), so nothing checks the string at runtime and a
#: plausible-looking `"1hr"` or `"60m"` would travel to the API and come back
#: a 400 `BadRequestError` -- which the retry loop below does not catch, and
#: which arrives only after the prefix it was meant to cache has been paid
#: for. mypy refuses it before the call is made.
CacheTTL = Literal["5m", "1h"]

#: Enough room for the largest structured answer Studio asks for -- a whole
#: C program from `generator.ProgramSources` -- rather than a value tuned to
#: the smallest. A verdict that needs a hundred tokens is not charged for
#: the ceiling; a program truncated at one is a failed generation.
#:
#: **Thinking is charged to this budget too.** The 16000 this used to be was
#: sized for the program alone, and a real run spent all 16000 of them
#: reasoning: `stop_reason` came back `max_tokens` with a single empty
#: thinking block and no program at all, so `parsed_output` was None and the
#: writer reported "the model did not return program sources" -- a truncation
#: wearing the mask of a refusal. The effort this model reasons at is the
#: high default (see the module docstring), so the ceiling has to hold a
#: full deliberation *and* the answer after it.
DEFAULT_MAX_TOKENS = 64000

#: The beta this project needs from the beta endpoint, and the only reason it
#: ever goes there: a task budget is the one way to tell a model how much room
#: the whole job has, so it wraps up rather than being cut off mid-sentence at
#: `max_tokens`. `studio-projects/cesar-mondongo-basket` is why that matters --
#: its third program attempt reasoned for 25 minutes and stopped at
#: `EOF while parsing a string at line 1 column 21706`, a whole 64000-token
#: deliberation billed for an answer nobody could read.
TASK_BUDGET_BETA = "task-budgets-2026-03-13"

#: What the API refuses a task budget below. Not a preference: `total` under
#: this is a 400.
MIN_TASK_BUDGET = 20000

#: The models that accept one at all. `config.yml` lets any role be pointed at
#: any model, so the writer can be moved onto one that would reject the
#: parameter -- and rejecting it means a 400 arriving minutes into a paid run,
#: after every stage before it has been paid for. A task budget is an
#: optimisation and the request is worth more than it is, so an unsupported
#: model simply does not get one.
TASK_BUDGET_MODELS = frozenset(
    {
        "claude-opus-5",
        "claude-opus-4-8",
        "claude-opus-4-7",
        "claude-sonnet-5",
        "claude-fable-5",
    }
)

#: How many times an answer the schema refuses is asked for again. Two, not
#: more: the first attempt is the model guessing at a rule it was never shown
#: (see `structured`), and the second is it being told the rule outright. A
#: model that breaks the same constraint twice with the constraint quoted at
#: it is not going to get it on the third.
DEFAULT_ATTEMPTS = 2


def structured(
    client: Any,
    model: str,
    *,
    system: str,
    user: str,
    schema: type[Schema],
    missing: str,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    tools: Sequence[dict[str, Any]] | None = None,
    attempts: int = DEFAULT_ATTEMPTS,
    effort: Effort | None = None,
    cached_prefix: str | None = None,
    cache_ttl: CacheTTL = "1h",
    task_budget: int | None = None,
) -> Schema:
    """One question, one schema-satisfying answer.

    `missing` is the caller's own sentence, raised as `ValueError` when the
    model answers with something the schema could not be read out of. Each
    call site says what *it* failed to get back ("a coherence verdict",
    "program sources"), and its own test matches on that wording, so the
    message belongs to the caller rather than to this module.

    `tools` is left out of the request entirely when no caller asks for it,
    rather than sent as an empty list: only `reference.py` searches the web,
    and an empty tool list is a different request from no tool list.

    `effort` is how much deliberation this one question is worth, and it is
    left out unless a caller names a level, because `high` is what the model
    does anyway. A caller passes one only to spend less: drawing an 8x8 tile
    does not need the reasoning that writing a whole C program does. It is set
    once, before the retry loop, which touches only `messages` -- so a repair
    attempt asks at the level the caller chose and not at the default it was
    trying to avoid.

    `cached_prefix` is the part of this question that will be identical the
    next time it is asked -- a contract, a design, a set of examples -- split
    out so the cache can be charged for it once instead of on every attempt.
    It becomes a second `system` block carrying the `cache_control`
    breakpoint, because caching matches a prefix in the order `tools` ->
    `system` -> `messages` and a breakpoint has to sit ahead of anything
    volatile (see the module docstring). A caller that passes nothing sends
    `system` as the plain string it has always been: nine of the ten call
    sites do, and their request is unchanged byte for byte.

    `cache_ttl` is how long that entry should outlive the call, and it
    defaults to `1h` rather than the API's `5m` because an attempt here takes
    longer than five minutes -- so the default would expire between attempts
    and charge a write per attempt for a cache nothing ever reads. The
    arithmetic is in the module docstring; the short version is that the
    5-minute default is more expensive than no cache at all.

    **An answer the schema refuses is asked for again, with the reason.**
    This is not belt-and-braces; it is required by how the SDK sends a
    schema. Constraints JSON Schema supports but structured outputs do not --
    `maxLength` above all, which these schemas use on fifteen fields -- are
    *stripped from the schema sent to the model* and enforced client-side
    afterwards. What reaches the model in their place is a description
    fragment reading `{default: , maxLength: 600}`, which is a dump of the
    removed keywords rather than an instruction, and is duly ignored. Pydantic
    then raises inside `messages.parse`.

    A real run is what put this here: the drafter wrote 600-and-something
    characters of `observability` prose and `llmz80 make` stopped dead at its
    second stage, having already paid for four minutes of web research. Note
    what the model did wrong -- it broke a rule nobody told it. So the retry
    quotes pydantic's own message ("String should have at most 600
    characters"), which names the field and the limit exactly, and that turns
    an unfixable failure into a fixable one.

    The alternative -- writing every limit into every prompt by hand -- was
    rejected: fifteen fields across ten call sites, each free to drift from
    the schema it is supposed to describe, to avoid a retry that costs one
    call only when something already went wrong.

    **The limits themselves are now stated up front, and the retry is the
    fallback rather than the plan.** `schema_limits.constraint_notes` derives
    them from `schema` and they are appended to `system`, so the model is told
    the rule before it writes rather than after. That is not a replacement for
    the retry -- a model can still break a rule it was shown -- but it turns
    the common case from two full generations into one. Derived and not
    written by hand, so it is not the drifting alternative rejected above; see
    that module for what a stale copy of a limit costs.

    `task_budget` is how many tokens the whole job is worth, told to the model
    so it paces itself. Distinct from `max_tokens`, which the model cannot see
    and which cuts it off wherever it happens to be. Only the writer passes
    one, and passing it is the one thing that sends this request to the beta
    endpoint.
    """
    if task_budget is not None and model not in TASK_BUDGET_MODELS:
        task_budget = None
    limits = constraint_notes(schema)
    instructed = f"{system}\n\n{limits}" if limits else system
    request: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "system": (
            instructed
            if cached_prefix is None
            else [
                {"type": "text", "text": instructed},
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
    if tools is not None:
        request["tools"] = tools
    output_config: dict[str, Any] = {}
    if effort is not None:
        output_config["effort"] = effort
    if task_budget is not None:
        output_config["task_budget"] = {
            "type": "tokens",
            "total": max(MIN_TASK_BUDGET, task_budget),
        }
    if output_config:
        request["output_config"] = output_config

    refusal: ValidationError | None = None
    for attempt in range(1, max(1, attempts) + 1):
        if refusal is None:
            content = user
        elif _was_cut_off(refusal):
            content = f"{user}\n\n{_truncation_feedback()}"
        else:
            content = f"{user}\n\n{_schema_feedback(refusal)}"
        request["messages"] = [{"role": "user", "content": content}]
        # Asked before the request rather than after it, so a run that has
        # spent its allowance stops without paying for the call that would
        # have told it so. Raises `BudgetExhausted`, which is a RuntimeError
        # and so travels straight out past the `except ValueError` every stage
        # wraps its own refusals in: a run that ran out of money is not a
        # design that could not be written, and "try the stage again" is the
        # wrong advice for it.
        ledger = current_ledger()
        if ledger is not None:
            ledger.check()
        try:
            # Streamed, not awaited whole. The SDK refuses outright to make a
            # non-streaming request whose `max_tokens` could keep the socket
            # open past ten minutes ("Streaming is required for operations
            # that may take longer than 10 minutes"), and the ceiling a
            # deliberating model needs to write a C program is well over that
            # line -- so `messages.parse` cannot be used at this size at all.
            # `messages.stream` accepts the same `output_format` and its final
            # message carries the same `parsed_output`, so only the call
            # changes: nothing downstream knows the difference.
            with _stream(client, request, task_budget) as stream:
                try:
                    response = stream.get_final_message()
                except BaseException:
                    # Billed on the way out, not skipped. Pydantic raises from
                    # *inside* this call, and an attempt whose answer was
                    # refused cost exactly as much to produce as one that was
                    # kept -- two of the five stages of the cesar run were
                    # nothing but that, and neither showed up anywhere.
                    _bill(_snapshot(stream), model, max_tokens)
                    raise
                _bill(response, model, max_tokens)
        except ValidationError as exc:
            refusal = exc
            if attempt == max(1, attempts):
                if _was_cut_off(exc):
                    raise ValueError(
                        "the answer was cut off before it finished: the JSON stops "
                        "mid-value, so this is not a schema mismatch. Either it hit "
                        f"the {max_tokens} token ceiling or the stream dropped. "
                        f"{exc}"
                    ) from exc
                raise ValueError(
                    f"the model's answer did not fit {schema.__name__}: {exc}"
                ) from exc
            continue

        parsed = response.parsed_output
        if parsed is None:
            # A truncated answer is not a missing one, and saying "the model
            # did not return program sources" about a program cut off at the
            # token ceiling sends whoever reads it looking at the prompt
            # instead of at `max_tokens`.
            if getattr(response, "stop_reason", None) == "max_tokens":
                raise ValueError(
                    f"{missing}: the answer hit the {max_tokens} token ceiling "
                    "before it was finished"
                )
            raise ValueError(missing)
        # The SDK types `parsed_output` as Any; it is the `schema` this
        # function was given, which is what the signature promises.
        return cast(Schema, parsed)
    raise AssertionError("unreachable")  # pragma: no cover


def _stream(client: Any, request: dict[str, Any], task_budget: int | None) -> Any:
    """The stream this request travels on, beta only when it has to be.

    `task_budget` lives in `BetaOutputConfigParam` and nowhere else (anthropic
    0.122.0, `types/beta/beta_output_config_param.py`), so a request carrying
    one has to go through `client.beta.messages` with the beta named. Every
    other request keeps the plain endpoint it has always used -- moving all
    ten call sites onto the beta path to serve the one that needs it would put
    every stage of the pipeline behind a flag that can be withdrawn.
    """
    if task_budget is None:
        return client.messages.stream(**request)
    return client.beta.messages.stream(**request, betas=[TASK_BUDGET_BETA])


def _snapshot(stream: Any) -> Any:
    """Whatever of the answer had arrived when it went wrong, or `None`.

    `MessageStream.current_message_snapshot` raises when nothing has been
    accumulated yet, and a fake client in a test has no such attribute at all.
    Both are the same answer here: no usage to read, so the call is billed at
    its ceiling instead.
    """
    try:
        return stream.current_message_snapshot
    except Exception:  # noqa: BLE001 -- see docstring: any failure means no usage
        return None


def _bill(response: Any, model: str, max_tokens: int) -> None:
    """Charge one call to the open run, if a run is open.

    Nothing here is conditional on the caller: `structured` is the only place
    a request is made, so it is the only place that can count them, and a
    caller that opted into an accounting API it could forget to call would be
    a caller that forgets. With no run open -- every test, every offline
    caller -- this does nothing at all.

    A response with no readable `usage` is billed at `max_tokens`. See
    `spend.Ledger.record` for why the over-estimate is the safe direction.
    """
    ledger = current_ledger()
    if ledger is None:
        return
    usage = getattr(response, "usage", None)
    if usage is None:
        ledger.record(model=model, output_tokens=None, max_tokens=max_tokens)
        return
    ledger.record(
        model=model,
        input_tokens=getattr(usage, "input_tokens", 0),
        output_tokens=getattr(usage, "output_tokens", 0),
        cache_read_tokens=getattr(usage, "cache_read_input_tokens", 0),
        cache_write_tokens=getattr(usage, "cache_creation_input_tokens", 0),
        max_tokens=max_tokens,
    )


def _was_cut_off(refusal: ValidationError) -> bool:
    """Whether this refusal is a half-arrived answer rather than a wrong one.

    Pydantic reports a truncated payload as `json_invalid`, and the message it
    carries is the parser's: "EOF while parsing" a string, an object or an
    array. That is the whole test -- a complete answer that happens not to fit
    the schema raises `missing`, `string_type` and their siblings, never
    `json_invalid`, so the two never collide.

    Worth telling apart because they need opposite responses. A wrong answer
    should be shown its complaint; a cut-off one never reached the end of what
    it was writing, and the only thing it can act on is the length.
    """
    return any(
        error.get("type") == "json_invalid" and "EOF while parsing" in str(error.get("msg", ""))
        for error in refusal.errors()
    )


def _truncation_feedback() -> str:
    """What to tell a model whose answer stopped halfway.

    Not the parser's complaint. "Invalid JSON: EOF while parsing a string at
    line 1 column 27294" describes punctuation the model never got to write,
    and pointing at it sends the next attempt looking for a syntax error in
    something that was, as far as it knew, still being typed.
    """
    return (
        "YOUR PREVIOUS ANSWER WAS CUT OFF\n\n"
        "It stopped part-way through and never arrived complete, so nothing was "
        "wrong with what you had written -- there was simply too much of it. "
        "Write the same program shorter: fewer helper functions, fewer comments, "
        "shorter names, and no code for anything the design did not ask for. "
        "Everything the contract requires still has to be there."
    )


def _schema_feedback(refusal: ValidationError) -> str:
    """What to tell the model about the answer its schema just refused.

    Pydantic's rendering is used verbatim rather than summarised: it already
    names the field, the rule and the offending value's shape, and any
    paraphrase here would be one more thing to keep in step with the schema.
    """
    return (
        "YOUR PREVIOUS ANSWER WAS REJECTED\n\n"
        "It did not fit the required shape. These are the exact complaints; "
        "fix every one of them and answer again.\n\n"
        f"{refusal}"
    )
