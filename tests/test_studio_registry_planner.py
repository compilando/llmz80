from types import SimpleNamespace

from openai.lib._pydantic import to_strict_json_schema

from llmz80.studio.models import TargetPlatform
from llmz80.studio.samples import blank_project
import pytest

from llmz80.studio.planner import (
    ProjectProposal,
    ResponsesProjectPlanner,
    apply_proposal,
    proposal_diff,
)
from llmz80.studio.registry import target_registry
from tests.conftest import FakeMessageStream


def _iter_property_schemas(schema: dict):
    """Yield (name, sub-schema) for every property in a JSON Schema document,
    including those nested inside `$defs`. Strict structured output rejects
    the whole request unless each one carries a concrete type."""
    for definition in schema.get("$defs", {}).values():
        yield from _iter_property_schemas(definition)
    for name, prop_schema in schema.get("properties", {}).items():
        yield name, prop_schema


def test_project_proposal_is_usable_as_a_strict_structured_output_schema():
    """`ProjectChange.value` used to be typed `Any`, which pydantic renders as
    a bare `{"title": "Value"}` with no type key. OpenAI's structured-output
    mode ('response_format') requires every property schema to declare a type
    or a composition keyword (`anyOf`, `$ref`), and rejects the whole request
    with a 400 otherwise -- something no other test caught, because they all
    inject an already-built ProjectProposal through a fake client and never
    exercise the schema. Run the exact transform the OpenAI SDK applies to
    `text_format` before a call, so a schema regression fails here instead of
    against the live API.
    """
    schema = to_strict_json_schema(ProjectProposal)

    untyped = [
        name
        for name, prop_schema in _iter_property_schemas(schema)
        if not ({"type", "anyOf", "$ref"} & prop_schema.keys())
    ]

    assert untyped == []


def test_there_is_no_genre_registry_left_to_ask():
    import llmz80.studio.registry as registry

    assert not hasattr(registry, "genre_registry")
    assert not hasattr(registry, "GenrePack")


def test_a_third_party_target_still_registers():
    """The extension SDK keeps the group that Studio actually loads."""
    from llmz80.studio.models import TargetPlatform, VideoMode
    from llmz80.studio.registry import Registry, TargetPack

    extra = TargetPack(
        TargetPlatform.SPECTRUM,
        "ZX Spectrum 128K",
        (VideoMode.SPECTRUM_BITMAP,),
        49152,
        16384,
        ("zesarux",),
        audio_effects=True,
    )
    registry = Registry([extra])
    assert registry.get("spectrum").binary_budget == 49152


def test_target_registry_declares_modes_budgets_and_emulators():
    registry = target_registry(load_external=False)
    spectrum = registry.get("spectrum")
    cpc = registry.get("amstrad_cpc")

    assert spectrum.binary_budget == 24576
    assert spectrum.validate(blank_project("ZX", TargetPlatform.SPECTRUM)) == []
    assert {mode.value for mode in cpc.video_modes} == {"cpc_mode_0", "cpc_mode_1"}
    assert "cap32" in cpc.emulator_adapters


def test_responses_planner_requests_typed_proposal():
    proposal = ProjectProposal(
        summary="Increase challenge",
        changes=[
            {
                "path": "/gameplay/lives",
                "operation": "replace",
                "value": {"number": 2},
                "reason": "The commercial difficulty profile needs more tension.",
            }
        ],
    )

    class FakeMessages:
        def stream(self, **kwargs):
            assert kwargs["output_format"] is ProjectProposal
            assert "Never emit C code" in kwargs["system"]
            return FakeMessageStream(SimpleNamespace(parsed_output=proposal))

    planner = ResponsesProjectPlanner(SimpleNamespace(messages=FakeMessages()))
    project = blank_project("Maze", TargetPlatform.SPECTRUM)

    assert planner.propose(project, "Make it harder") == proposal


def test_reviewed_proposal_is_transactional_and_validated():
    project = blank_project("Maze", TargetPlatform.SPECTRUM)
    proposal = ProjectProposal(
        summary="Tune the HUD",
        changes=[
            {
                "path": "/presentation/hud_rows",
                "operation": "replace",
                "value": {"number": 1},
                "reason": "Free up a row for a taller playfield.",
            }
        ],
    )

    changed = apply_proposal(project, proposal)

    assert changed.presentation.hud_rows == 1
    assert project.presentation.hud_rows == 2
    assert "REPLACE /presentation/hud_rows = 1" in proposal_diff(proposal)


@pytest.mark.parametrize("path", ["/schema_version", "/target/platform", "/acceptance/0"])
def test_ai_cannot_change_protected_contract(path):
    project = blank_project("Maze", TargetPlatform.SPECTRUM)
    proposal = ProjectProposal(
        summary="Unsafe change",
        changes=[{"path": path, "operation": "replace", "value": {"number": 1}, "reason": "test"}],
    )

    with pytest.raises(ValueError, match="protected"):
        apply_proposal(project, proposal)


def test_budget_change_requires_explicit_approval():
    project = blank_project("Maze", TargetPlatform.SPECTRUM)
    proposal = ProjectProposal(
        summary="Larger binary",
        changes=[
            {
                "path": "/budgets/binary_bytes",
                "operation": "replace",
                "value": {"number": 30000},
                "reason": "More content.",
            }
        ],
    )

    with pytest.raises(ValueError, match="explicit approval"):
        apply_proposal(project, proposal)
    assert (
        apply_proposal(project, proposal, allow_budget_changes=True).budgets.binary_bytes == 30000
    )


# ---------------------------------------------------------------------------
# Colour and terrain artwork: the two things a design could describe and no
# stage could ever propose.
# ---------------------------------------------------------------------------


def test_a_tile_can_be_proposed_with_the_note_that_asks_for_artwork():
    """`TileValue` mirrors `TileSpec`, and a mirror missing a field is a field
    no proposal can ever set -- which is how terrain artwork stayed
    unreachable while the model that could describe it wrote every design."""
    from llmz80.studio.planner import TileValue

    value = TileValue(id="ladrillo", char="B", art_note="brickwork, mortar lines")

    assert value.json_value()["art_note"] == "brickwork, mortar lines"


def test_a_whole_palette_can_be_proposed():
    """A design's colours are a list of named entries, and an entity's or
    tile's `colour` may only name one the design declares (`structure.py`), so
    a proposal that cannot write the palette cannot use colour at all."""
    from llmz80.studio.planner import PaletteValue

    value = PaletteValue(
        palette=[{"id": "ladrillo", "colour": "cian"}, {"id": "pala", "colour": "amarillo"}]
    )

    assert value.json_value() == [
        {"id": "ladrillo", "colour": "cian"},
        {"id": "pala", "colour": "amarillo"},
    ]


def test_a_palette_proposal_applies_to_the_design():
    from llmz80.studio.models import TargetPlatform
    from llmz80.studio.planner import (
        PaletteValue,
        ProjectChange,
        ProjectProposal,
        apply_proposal,
    )
    from llmz80.studio.samples import blank_project

    project = blank_project("Coloured", TargetPlatform.SPECTRUM)
    proposal = ProjectProposal(
        summary="give the design its colours",
        changes=[
            ProjectChange(
                path="/presentation/palette",
                operation="replace",
                reason="the brief asks for cyan brickwork",
                value=PaletteValue(palette=[{"id": "ladrillo", "colour": "cian"}]),
            )
        ],
    )

    updated = apply_proposal(project, proposal)

    assert [entry.id for entry in updated.presentation.palette] == ["ladrillo"]
    assert updated.presentation.palette[0].colour == "cian"
