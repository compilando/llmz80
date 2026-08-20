"""The limits the model is never shown, said out loud.

`llmz80/studio/llm.py` documents why these have to be spelled out: the SDK
transforms a pydantic schema before sending it, and every keyword structured
outputs does not support -- `maxLength` above all -- is *removed from the
schema* and re-emitted as a dump inside the field's description, reading
`{maxLength: 600}`. That is not an instruction, and it is duly ignored.

`studio-projects/cesar-mondongo-basket/studio.log` is what this cost. Both the
drafting stage and the design stage produced a whole design, and both had it
refused by pydantic for `entities.*.notes` running past 240 characters -- 550 s
and 409 s of reasoning, thrown away and paid for, over a rule nobody had told
the model. `constraint_notes` is that rule, derived from the schema so it
cannot drift from it.
"""

from typing import Annotated

import pytest
from pydantic import BaseModel, Field, StringConstraints

from llmz80.studio.schema_limits import constraint_notes


class _Inner(BaseModel):
    notes: str = Field(default="", max_length=240)


class _Outer(BaseModel):
    title: str = Field(min_length=1, max_length=32)
    entities: list[_Inner] = Field(default_factory=list, max_length=8)
    count: int = Field(ge=1, le=64)
    free: str = ""


def test_a_string_length_limit_is_stated_with_its_field_and_its_number():
    notes = constraint_notes(_Outer)

    assert "title" in notes
    assert "32" in notes


def test_a_limit_on_a_nested_model_is_reached_and_named_by_its_path():
    """The one that actually cost money.

    `entities.0.notes` is where both refusals in the cesar run landed, and a
    walk that stopped at the top level would have said nothing about it.
    """
    notes = constraint_notes(_Outer)

    assert "entities[].notes" in notes
    assert "240" in notes


def test_a_list_length_limit_is_stated_as_items_not_as_characters():
    notes = constraint_notes(_Outer)

    assert "entities" in notes
    assert "8 items" in notes


def test_numeric_bounds_are_stated_too():
    notes = constraint_notes(_Outer)

    assert "count" in notes
    assert "1" in notes and "64" in notes


def test_a_field_with_no_constraint_is_not_mentioned():
    """Only what the model cannot see is worth the tokens.

    Listing every field would restate the schema the model already has, and
    this text rides in the cached prefix of every structured call there is.
    """
    assert "free" not in constraint_notes(_Outer)


def test_a_schema_with_no_constraints_at_all_says_nothing():
    """An empty string, not a heading with nothing under it.

    `structured` appends this to the system prompt, and a heading followed by
    no rules reads as a rule the model is expected to infer.
    """

    class _Plain(BaseModel):
        anything: str

    assert constraint_notes(_Plain) == ""


def test_a_self_referential_schema_terminates():
    """A design can nest; the walk must not.

    Not hypothetical for this project: `models.py` reaches `GameProject` from
    several directions, and a naive walk over `$defs` revisits it forever.
    """

    class _Node(BaseModel):
        label: Annotated[str, StringConstraints(max_length=16)]
        child: "_Node | None" = None

    _Node.model_rebuild()

    notes = constraint_notes(_Node)

    assert "label" in notes


def test_the_real_design_schema_names_the_field_that_broke_two_runs():
    """The regression proper, against the schema that actually ships."""
    from llmz80.studio.models import GameProject

    notes = constraint_notes(GameProject)

    assert "entities[].notes" in notes
    assert "240" in notes


def test_the_notes_are_stable_between_calls():
    """They ride in a cached prefix; an unstable rendering caches nothing.

    Dictionary iteration order is stable in this interpreter, but a future
    `set` in the walk would not be, and the failure it causes -- a cache that
    silently never hits -- shows up as a bill, not as a broken test.
    """
    assert constraint_notes(_Outer) == constraint_notes(_Outer)


@pytest.mark.parametrize("schema", [_Outer, _Inner])
def test_every_line_is_a_sentence_the_model_can_act_on(schema):
    """No `{maxLength: 240}` dumps: that is the thing being fixed."""
    for line in constraint_notes(schema).splitlines():
        assert "maxLength" not in line
        assert "maxItems" not in line


def test_a_lower_bound_of_zero_is_not_stated():
    """`at least 0` on a count is noise, and noise is billed.

    `GameProject.presentation.hud_rows` is `ge=0`: a rule that forbids nothing
    still costs tokens in every prompt these notes ride in, and reads as though
    the model were being warned about something.
    """

    class _Countable(BaseModel):
        rows: int = Field(ge=0, le=4)
        names: list[str] = Field(default_factory=list, min_length=0, max_length=4)

    notes = constraint_notes(_Countable)

    assert "at least 0" not in notes
    assert "at most 4" in notes


def test_a_limit_of_one_is_written_in_the_singular():
    """`at most 1 characters` reads as a typo and undermines the rest."""

    class _Single(BaseModel):
        char: str = Field(min_length=1, max_length=1)
        one: list[str] = Field(default_factory=list, max_length=1)

    notes = constraint_notes(_Single)

    assert "1 characters" not in notes
    assert "1 items" not in notes
    assert "exactly 1 character" in notes
