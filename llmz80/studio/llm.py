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
why `config.yml` no longer carries a key for it either. (What it carried was
`reasoning_effort`, an OpenAI-era parameter for a different API. The code that
still reads it -- `llmz80/utils/helpers.py`, and the old generator behind it --
does not reach this module, so there is no config value here to plumb through.)
The level goes *inside* `output_config` because that is the only place it
exists: the Messages API has no top-level `effort`, so one sent there is a
`TypeError` out of the SDK before a request is ever built -- loud, not silent.
Nesting it costs the schema nothing, because `messages.stream` merges the two
into `{**output_config, "format": <schema>}` (anthropic 0.122.0,
`resources/messages/messages.py:1275`), spreading the caller's dict first --
so `output_format` and `effort` compose rather than compete.
"""

from __future__ import annotations

from typing import Any, Literal, Sequence, TypeVar

from pydantic import BaseModel, ValidationError

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
    """
    request: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user}],
        "output_format": schema,
    }
    if tools is not None:
        request["tools"] = tools
    if effort is not None:
        request["output_config"] = {"effort": effort}

    refusal: ValidationError | None = None
    for attempt in range(1, max(1, attempts) + 1):
        content = user if refusal is None else f"{user}\n\n{_schema_feedback(refusal)}"
        request["messages"] = [{"role": "user", "content": content}]
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
            with client.messages.stream(**request) as stream:
                response = stream.get_final_message()
        except ValidationError as exc:
            refusal = exc
            if attempt == max(1, attempts):
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
        return parsed
    raise AssertionError("unreachable")  # pragma: no cover


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
