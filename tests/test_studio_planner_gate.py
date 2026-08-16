import pytest
from openai.lib._pydantic import to_strict_json_schema
from pydantic import ValidationError

from llmz80.studio.models import TargetPlatform
from llmz80.studio.planner import (
    EntityValue,
    NumberValue,
    ProjectChange,
    ProjectProposal,
    RowsValue,
    TextValue,
    apply_proposal,
    propose_apply_repair,
)
from llmz80.studio.samples import blank_project


@pytest.fixture
def project():
    return blank_project("Planner", TargetPlatform.SPECTRUM)


def test_a_proposal_that_outgrows_the_target_grid_is_refused(project):
    """`GameProject.model_validate` refuses a screen wider than its target's
    playable grid (see `structure._fit_errors`) unconditionally -- this is a
    fact about the hardware, not a rule `allow_unplayable` can waive, so a
    proposal that outgrows it never even reaches `apply_proposal`'s own
    playability gate.
    """
    screen = project.screens[0]
    wide = ["." * 40 for _ in range(screen.height)]
    proposal = ProjectProposal(
        summary="widen the first screen",
        changes=[
            ProjectChange(
                path="/screens/0/width",
                operation="replace",
                value=NumberValue(number=40),
                reason="more room to run",
            ),
            ProjectChange(
                path="/screens/0/tiles",
                operation="replace",
                value=RowsValue(rows=wide),
                reason="more room to run",
            ),
        ],
    )

    with pytest.raises(ValueError, match="playable cells"):
        apply_proposal(project, proposal)


def test_a_playable_proposal_still_applies(project):
    proposal = ProjectProposal(
        summary="tune the presentation",
        changes=[
            ProjectChange(
                path="/presentation/style",
                operation="replace",
                value=TextValue(text="moody pixel-art dungeon"),
                reason="match the new mechanics",
            )
        ],
    )

    applied = apply_proposal(project, proposal)

    assert applied.presentation.style == "moody pixel-art dungeon"


def test_a_proposal_can_change_mechanics_and_a_screens_tiles(project):
    """`/mechanics` and a screen's `tiles` are proposable in v4 -- neither
    existed as a field a v3 proposal could touch at all: `/gameplay` had no
    prose slot for what the game does, and terrain lived under `/levels`, not
    `/screens`.
    """
    screen = project.screens[0]
    rows = [list(row) for row in screen.tiles]
    rows[1][5] = "#"  # a single interior cell, away from the entity's spawn
    edited_tiles = ["".join(row) for row in rows]
    proposal = ProjectProposal(
        summary="declare a mechanic and add a pillar",
        changes=[
            ProjectChange(
                path="/mechanics",
                operation="replace",
                value=RowsValue(rows=["the player explores the screen and avoids obstacles"]),
                reason="the design had no stated mechanics yet",
            ),
            ProjectChange(
                path="/screens/0/tiles",
                operation="replace",
                value=RowsValue(rows=edited_tiles),
                reason="break up the empty room with a single pillar",
            ),
        ],
    )

    applied = apply_proposal(project, proposal)

    assert applied.mechanics == ["the player explores the screen and avoids obstacles"]
    assert applied.screens[0].tiles == edited_tiles


def test_a_change_can_carry_a_whole_entity():
    """A design that states nothing has no entity to edit a field of: the
    drafting stage has to add one, and a `TextValue` cannot hold an object."""
    from llmz80.studio.planner import EntityValue

    change = ProjectChange(
        path="/entities/-",
        operation="add",
        reason="the brief asks for enemy fighters and the design has none",
        value=EntityValue(id="caza", kind="enemigo", notes="cruza la pantalla disparando"),
    )

    assert change.applied_value == {
        "id": "caza",
        "kind": "enemigo",
        "sprite": None,
        "poses": [],
        "count": 1,
        "colour": None,
        "notes": "cruza la pantalla disparando",
    }


def test_a_change_can_carry_a_whole_tile():
    from llmz80.studio.planner import TileValue

    change = ProjectChange(
        path="/tiles/-",
        operation="add",
        reason="the brief asks for water the player cannot cross",
        value=TileValue(id="agua", char="~", traits=["solid"]),
    )

    assert change.applied_value["id"] == "agua"
    assert change.applied_value["char"] == "~"
    assert change.applied_value["traits"] == ["solid"]


def test_a_value_that_mixes_two_shapes_is_refused():
    """The one-shape-per-change rule is what keeps `value` unambiguous.

    It used to need a validator counting how many of seven sibling `value_*`
    fields were set. Now the anyOf does it: no branch of the union accepts an
    entity's `kind` beside a tile's `char`, because every variant forbids the
    others' fields. This test is what says the anyOf really is that strict,
    rather than quietly picking a branch and dropping what did not fit.
    """
    with pytest.raises(ValidationError):
        ProjectChange.model_validate(
            {
                "path": "/entities/-",
                "operation": "add",
                "reason": "two shapes at once",
                "value": {"id": "uno", "kind": "actor", "char": "#"},
            }
        )


def test_a_whole_entity_a_proposal_added_becomes_one_the_design_declares(project):
    """`/entities/-` is the first path a proposal ever *added* to rather than
    edited a field of, so what matters is not that the change validates but
    that `apply_proposal` lands it in the document as a real `EntitySpec`."""
    from llmz80.studio.planner import EntityValue

    proposal = ProjectProposal(
        summary="give the design the enemy its brief asks for",
        changes=[
            ProjectChange(
                path="/entities/-",
                operation="add",
                reason="the brief asks for enemy fighters and the design has none",
                value=EntityValue(id="caza", kind="enemigo", count=3),
            )
        ],
    )

    applied = apply_proposal(project, proposal)

    assert [entity.id for entity in applied.entities] == ["actor", "caza"]
    assert applied.entities[1].kind == "enemigo"
    assert applied.entities[1].count == 3


def test_a_whole_observable_a_proposal_added_becomes_one_the_design_declares(project):
    """`/observables/-` is the path that had never existed at all: `game.yml`
    could carry observables since schema v4 and no stage could propose one, so
    every finished game was judged on the six fixed contract symbols and not
    one of its own rules was ever witnessed. What matters here is the same
    thing `/entities/-` had to prove: that the change lands in the document as
    a real `ObservableSpec`, width and meaning intact."""
    from llmz80.studio.planner import ObservableValue

    proposal = ProjectProposal(
        summary="make the digging rule checkable from outside",
        changes=[
            ProjectChange(
                path="/observables/-",
                operation="add",
                reason="no contract symbol can witness dirt turning into floor",
                value=ObservableValue(
                    symbol="g_dug",
                    width=2,
                    meaning="celdas de tierra excavadas; solo sube",
                ),
            )
        ],
    )

    applied = apply_proposal(project, proposal)

    assert [observable.symbol for observable in applied.observables] == ["g_dug"]
    assert applied.observables[0].width == 2
    assert applied.observables[0].meaning == "celdas de tierra excavadas; solo sube"


def test_a_proposal_whose_text_carries_the_json_separator_is_refused_and_repairable(project):
    """The `},{` corruption arrives as a `ProjectChange` text value, so this is
    the path the guard in `models._unstructured` actually has to cover.

    Both halves matter. The refusal is what stops `minero},{` reaching the
    program writer, as it did in `studio-projects/minero-vigilado`. Being a
    plain validation error is what makes the run survive it: the model emitted
    the separator in 2 of 14 replayed calls, so a refusal that ended the stage
    would cost roughly one draft in seven, while `propose_apply_repair` turns
    it into another attempt with the offending path named.
    """
    corrupt = ProjectProposal(
        summary="name the actor",
        changes=[
            ProjectChange(
                path="/entities/0/kind",
                operation="replace",
                value=TextValue(text="minero},{"),
                reason="the brief's protagonist is a miner",
            )
        ],
    )
    clean = ProjectProposal(
        summary="name the actor",
        changes=[
            ProjectChange(
                path="/entities/0/kind",
                operation="replace",
                value=TextValue(text="minero"),
                reason="the brief's protagonist is a miner",
            )
        ],
    )

    with pytest.raises(ValueError, match="JSON separator"):
        apply_proposal(project, corrupt)

    attempts = [corrupt, clean]
    seen: list[str | None] = []

    def propose(feedback: str | None) -> ProjectProposal:
        seen.append(feedback)
        return attempts.pop(0)

    applied = propose_apply_repair(project, propose, lambda _updated: None)

    assert applied.project.entities[0].kind == "minero"
    assert "JSON separator" in applied.refusals[0]
    assert "entities/0/kind" in (seen[1] or "")


def test_changes_of_different_shapes_still_apply_in_the_order_they_were_written(project):
    """Cross-type ordering is what `apply_proposal` promises, and it is what a
    schema change could quietly take away.

    Index-based JSON pointers make the order load-bearing: `/entities/-`
    appending an actor is what *creates* the index `/entities/1/notes` then
    edits, so the two are not interchangeable and neither is any other pair
    where an add feeds a later path. The reason to pin it now is that one of
    the shapes considered for this schema -- a separate ordered list per value
    type, entities in one and text in another -- would have applied every add
    before every edit and passed every other test in this file.
    """
    proposal = ProjectProposal(
        summary="add the enemy the brief asks for, then say what it does",
        changes=[
            ProjectChange(
                path="/entities/-",
                operation="add",
                reason="the design has no enemy yet",
                value=EntityValue(id="murcielago", kind="enemigo"),
            ),
            ProjectChange(
                path="/entities/1/notes",
                operation="replace",
                reason="say what the enemy the previous change added does",
                value=TextValue(text="patrulla la cueva de lado a lado"),
            ),
        ],
    )

    applied = apply_proposal(project, proposal)

    assert [entity.id for entity in applied.entities] == ["actor", "murcielago"]
    assert applied.entities[1].notes == "patrulla la cueva de lado a lado"


def test_a_change_declares_one_value_property_and_no_null_siblings():
    """What the model has to write per change, counted at the schema.

    This is the whole point of the anyOf. Strict structured output requires
    every declared property, so seven sibling `value_*` fields meant six
    `null`s after each value the model actually wrote -- and the replayed raw
    responses show it stalling in exactly that gap, padding with runs of up to
    762 literal spaces and twice spilling `},{` into the string it had not
    finished. Four properties, with `value` last, leaves nothing to stall
    towards. A regression that reintroduces a sibling would be invisible in
    every behavioural test here and expensive in every real response.
    """
    schema = to_strict_json_schema(ProjectProposal)["$defs"]["ProjectChange"]

    assert list(schema["properties"]) == ["path", "operation", "reason", "value"]
    assert schema["required"] == ["path", "operation", "reason", "value"]
    assert "anyOf" in schema["properties"]["value"]
