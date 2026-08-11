from types import SimpleNamespace

from openai.lib._pydantic import to_strict_json_schema

from llmz80.studio.models import GenreId, TargetPlatform
from llmz80.studio.packs import create_default_project
import pytest

from llmz80.studio.planner import (
    ProjectProposal,
    ResponsesProjectPlanner,
    apply_proposal,
    proposal_diff,
)
from llmz80.studio.registry import genre_registry, target_registry


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


def test_builtin_genre_registry_has_stable_ids():
    registry = genre_registry(load_external=False)

    identifiers = {
        pack.id.value if hasattr(pack.id, "value") else pack.id for pack in registry.values()
    }
    # The enum names the two originals; the catalogue is free to add more.
    assert identifiers >= {genre.value for genre in GenreId}
    assert len(identifiers) == len(registry.values()), "typology ids must be unique"
    assert "maze" in registry.get("maze_chase").capabilities


def test_target_registry_declares_modes_budgets_and_emulators():
    registry = target_registry(load_external=False)
    spectrum = registry.get("spectrum")
    cpc = registry.get("amstrad_cpc")

    assert spectrum.binary_budget == 24576
    assert (
        spectrum.validate(create_default_project("ZX", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE))
        == []
    )
    assert {mode.value for mode in cpc.video_modes} == {"cpc_mode_0", "cpc_mode_1"}
    assert "cap32" in cpc.emulator_adapters


def test_responses_planner_requests_typed_proposal():
    proposal = ProjectProposal(
        summary="Increase challenge",
        changes=[
            {
                "path": "/gameplay/lives",
                "operation": "replace",
                "value_number": 2,
                "reason": "The commercial difficulty profile needs more tension.",
            }
        ],
    )

    class FakeResponses:
        def parse(self, **kwargs):
            assert kwargs["text_format"] is ProjectProposal
            assert "Never emit C code" in kwargs["input"][0]["content"]
            return SimpleNamespace(output_parsed=proposal)

    planner = ResponsesProjectPlanner(SimpleNamespace(responses=FakeResponses()))
    project = create_default_project("Maze", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)

    assert planner.propose(project, "Make it harder") == proposal


def test_reviewed_proposal_is_transactional_and_validated():
    project = create_default_project("Maze", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    proposal = ProjectProposal(
        summary="Tune difficulty",
        changes=[
            {
                "path": "/gameplay/lives",
                "operation": "replace",
                "value_number": 2,
                "reason": "Create a more demanding commercial mode.",
            }
        ],
    )

    changed = apply_proposal(project, proposal)

    assert changed.gameplay.lives == 2
    assert project.gameplay.lives == 3
    assert "REPLACE /gameplay/lives = 2" in proposal_diff(proposal)


@pytest.mark.parametrize("path", ["/schema_version", "/target/platform", "/acceptance/0"])
def test_ai_cannot_change_protected_contract(path):
    project = create_default_project("Maze", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    proposal = ProjectProposal(
        summary="Unsafe change",
        changes=[{"path": path, "operation": "replace", "value_number": 1, "reason": "test"}],
    )

    with pytest.raises(ValueError, match="protected"):
        apply_proposal(project, proposal)


def test_budget_change_requires_explicit_approval():
    project = create_default_project("Maze", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    proposal = ProjectProposal(
        summary="Larger binary",
        changes=[
            {
                "path": "/budgets/binary_bytes",
                "operation": "replace",
                "value_number": 30000,
                "reason": "More content.",
            }
        ],
    )

    with pytest.raises(ValueError, match="explicit approval"):
        apply_proposal(project, proposal)
    assert (
        apply_proposal(project, proposal, allow_budget_changes=True).budgets.binary_bytes == 30000
    )
