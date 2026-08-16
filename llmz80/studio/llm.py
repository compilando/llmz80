"""How Studio asks a model for a structured answer, described once.

Eight places in `llmz80/studio` ask a model a question whose answer must
satisfy a pydantic schema: the drafter, the reference researcher and the
design it proposes, the planner, both design examiners, the program writer,
and the runtime examiner. Every one of them used to spell the same request
out by hand and follow it with the same four-line check, differing only in
the schema and in the words of the error. That meant a change to how Studio
talks to a model -- which is exactly what moving off OpenAI's Responses API
was -- had to be made eight times, consistently, or not at all.

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

`effort` is deliberately absent for the same reason it is not in
`config.yml` any more: its default is already the high setting Studio wants,
so naming it would be describing the default. `output_config` is where it
would go if a caller ever needed to lower it, and the SDK merges
`output_format` into that same object rather than treating the two as
alternatives -- so adding it later is a parameter, not a rewrite.
"""

from __future__ import annotations

from typing import Any, Sequence, TypeVar

from pydantic import BaseModel, ValidationError

Schema = TypeVar("Schema", bound=BaseModel)

#: Enough room for the largest structured answer Studio asks for -- a whole
#: C program from `generator.ProgramSources` -- rather than a value tuned to
#: the smallest. A verdict that needs a hundred tokens is not charged for
#: the ceiling; a program truncated at one is a failed generation.
DEFAULT_MAX_TOKENS = 16000

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
    rejected: fifteen fields across eight call sites, each free to drift from
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

    refusal: ValidationError | None = None
    for attempt in range(1, max(1, attempts) + 1):
        content = user if refusal is None else f"{user}\n\n{_schema_feedback(refusal)}"
        request["messages"] = [{"role": "user", "content": content}]
        try:
            response = client.messages.parse(**request)
        except ValidationError as exc:
            refusal = exc
            if attempt == max(1, attempts):
                raise ValueError(
                    f"the model's answer did not fit {schema.__name__}: {exc}"
                ) from exc
            continue

        parsed = response.parsed_output
        if parsed is None:
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
