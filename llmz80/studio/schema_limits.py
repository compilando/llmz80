"""The schema's own limits, phrased as rules a model can follow.

`llm.py` explains the mechanism and this module is the remedy. The SDK
transforms a pydantic schema before it travels (`anthropic/lib/_parse/
_transform.py:163`): every keyword structured outputs does not support is
*popped out of the schema* and appended to the field's description as a dump
of what was removed -- literally `{maxLength: 240}`. A model reading that sees
a fragment of machinery, not an instruction, and writes what it was going to
write anyway. Pydantic then refuses the answer client-side, and the whole
generation is paid for and thrown away.

`studio-projects/cesar-mondongo-basket/studio.log` is the run that put this
here. The drafting stage spent 550 s producing a design and had it refused for
`entities.0.notes` at 240 characters; the design stage then spent 409 s and was
refused for the same field. Two complete deliberations, billed in full, over a
rule that fits on one line -- and one the model was never in a position to
know.

**Derived, never written by hand.** `models.py` carries thirty `max_length`
fields across a dozen nested models. Restating them in each of the prompts
that build a design is thirty chances for the prompt to drift from the schema
it describes, and drift here is silent: the prompt says 600, the schema says
240, and the model obeys the prompt and is refused. Reading the constraints
off the schema that will judge the answer is the only version of this that
cannot go stale.

**Stable output, because it rides in a cached prefix.** `structured` sends
these notes in the `system` block that carries the `cache_control` breakpoint.
A rendering that reordered itself between calls would be a different prefix
every time and would cache nothing, which shows up as a bill rather than as a
failing test -- hence the ordered walk and no `set` anywhere in it.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

#: What `transform_schema` keeps in the schema it sends. Anything else in a
#: node is demoted into the description as a `{key: value}` dump, which is
#: exactly the set worth restating in English. Kept as the complement of the
#: SDK's own list rather than as a list of "constraints we care about", so a
#: keyword the SDK starts dropping is caught by the walk instead of being
#: silently missed.
_SURVIVES = frozenset(
    {
        "type",
        "enum",
        "description",
        "title",
        "properties",
        "additionalProperties",
        "required",
        "items",
        "format",
        "$ref",
        "$defs",
        "anyOf",
        "oneOf",
        "allOf",
        "default",
    }
)

#: The bounded pairs, and the noun each one counts. A keyword outside this
#: table and outside `_NUMERIC` below is left out entirely rather than dumped
#: raw: `{pattern: ^[a-z][a-z0-9_]{0,31}$}` in a prompt is the same unreadable
#: machinery this module exists to replace, and every id in `models.py`
#: already carries a prose description saying it is lowercase.
_BOUNDED = (("minLength", "maxLength", "character"), ("minItems", "maxItems", "item"))

#: Numeric bounds, in the order they are said.
_NUMERIC = (
    ("minimum", "at least {value}"),
    ("maximum", "at most {value}"),
    ("exclusiveMinimum", "above {value}"),
    ("exclusiveMaximum", "below {value}"),
)

#: Where the walk gives up. Deep enough for `GameProject`, which nests four
#: levels at its deepest (project -> screens -> spawns -> position), and a
#: backstop for a schema that refers to itself through a chain `_seen` cannot
#: catch because each step has a different path.
_MAX_DEPTH = 8


def constraint_notes(schema: type[BaseModel]) -> str:
    """Every limit `schema` enforces that the model will never be shown.

    An empty string when there are none: `structured` appends this to the
    system prompt, and a heading with no rules under it reads as a rule the
    model is expected to work out for itself.

    Paths are dotted, with `[]` for a list -- `entities[].notes` rather than
    `entities.0.notes` -- because the rule is about every element and a number
    invites the model to think it is about the first one.
    """
    root = schema.model_json_schema()
    defs = root.get("$defs", {})
    limits: list[tuple[str, list[str]]] = []
    _walk(root, defs, path="", limits=limits, seen=(), depth=0)
    if not limits:
        return ""
    lines = [f"- {path}: {', '.join(rules)}" for path, rules in limits]
    return "THE ANSWER'S OWN LIMITS\n\n" + "\n".join(lines)


def _walk(
    node: dict[str, Any],
    defs: dict[str, Any],
    *,
    path: str,
    limits: list[tuple[str, list[str]]],
    seen: tuple[str, ...],
    depth: int,
) -> None:
    """Collect `node`'s dropped constraints, then everything below it.

    `seen` carries the `$defs` names already open on this branch rather than a
    set shared across the whole walk: a model reached twice from two different
    fields has two different paths and both are worth stating, but a model
    that reaches itself is a cycle and stops.
    """
    if depth > _MAX_DEPTH:
        return

    reference = node.get("$ref")
    if isinstance(reference, str):
        name = reference.rsplit("/", 1)[-1]
        if name in seen:
            return
        target = defs.get(name)
        if isinstance(target, dict):
            _walk(target, defs, path=path, limits=limits, seen=seen + (name,), depth=depth + 1)
        return

    for key in ("anyOf", "oneOf", "allOf"):
        variants = node.get(key)
        if isinstance(variants, list):
            for variant in variants:
                if isinstance(variant, dict):
                    _walk(variant, defs, path=path, limits=limits, seen=seen, depth=depth + 1)

    if path:
        rules = _rules(node)
        if rules:
            limits.append((path, rules))

    items = node.get("items")
    if isinstance(items, dict):
        _walk(items, defs, path=f"{path}[]", limits=limits, seen=seen, depth=depth + 1)

    properties = node.get("properties")
    if isinstance(properties, dict):
        for name, child in properties.items():
            if isinstance(child, dict):
                below = f"{path}.{name}" if path else name
                _walk(child, defs, path=below, limits=limits, seen=seen, depth=depth + 1)


def _rules(node: dict[str, Any]) -> list[str]:
    """`node`'s constraints that will not survive the trip, in English.

    Ordered by the tables above and not by the node, so the same schema
    renders the same bytes every time -- see the module docstring on why that
    is a billing concern and not a tidiness one.

    A lower bound of zero is dropped: `models.py` writes `ge=0` on several
    counts to say the field is unsigned, and "at least 0" forbids nothing
    while reading as though the model were being warned about something.
    """
    dropped = {key: node[key] for key in node if key not in _SURVIVES}
    rules: list[str] = []
    for low_key, high_key, noun in _BOUNDED:
        low, high = dropped.get(low_key), dropped.get(high_key)
        if low == high and isinstance(low, int):
            rules.append(f"exactly {_counted(low, noun)}")
            continue
        if isinstance(low, int) and low > 0:
            rules.append(f"at least {_counted(low, noun)}")
        if isinstance(high, int):
            rules.append(f"at most {_counted(high, noun)}")
    for key, phrasing in _NUMERIC:
        value = dropped.get(key)
        if value is not None and not (key == "minimum" and value == 0):
            rules.append(phrasing.format(value=value))
    return rules


def _counted(value: int, noun: str) -> str:
    """`1 character`, `4 characters`.

    A limit of one is not rare here -- `TileSpec.char` is a single character --
    and "at most 1 characters" reads as a typo, which is a poor advertisement
    for the rules printed underneath it.
    """
    return f"{value} {noun}" if value == 1 else f"{value} {noun}s"
