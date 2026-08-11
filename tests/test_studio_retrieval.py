from pathlib import Path

import pytest

from llmz80.studio.editing import set_entity_behaviour
from llmz80.studio.generator import writing_prompt
from llmz80.studio.models import GenreId, TargetPlatform
from llmz80.studio.packs import create_default_project
from llmz80.studio.retrieval import (
    MAX_EXAMPLE_CHARS,
    catalog_examples,
    examples_prompt,
    reference_program,
    retrieval_query,
)


@pytest.fixture
def project():
    return create_default_project("Retrieved", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)


def test_the_query_describes_the_design_not_the_title(project):
    query = retrieval_query(project)

    assert "maze chase" in query
    assert "player" in query and "enemy" in query
    assert "tile map walls" in query
    assert project.metadata.title.lower() not in query


def test_a_designed_behaviour_widens_the_query(project):
    edited = set_entity_behaviour(project, "enemy", "chase")

    assert "chase" in retrieval_query(edited)


@pytest.mark.parametrize("platform", list(TargetPlatform))
def test_examples_come_from_the_projects_own_platform(platform):
    project = create_default_project("Platform", platform, GenreId.MAZE_CHASE)

    found = catalog_examples(project)

    assert found, "the certified corpus should offer something for every target"
    for _name, source in found:
        if platform is TargetPlatform.SPECTRUM:
            assert "cpct_" not in source
        else:
            assert "zx_cls" not in source


def test_the_reference_program_is_offered_for_both_targets():
    for platform in TargetPlatform:
        project = create_default_project("Ref", platform, GenreId.MAZE_CHASE)

        found = reference_program(project)

        assert found is not None
        name, source = found
        assert name.endswith("engine.c")
        assert "g_score" in source


def test_long_examples_are_trimmed_rather_than_dropped(project):
    for _name, source in catalog_examples(project):
        assert len(source) <= MAX_EXAMPLE_CHARS + 40


def test_the_reference_comes_before_the_catalog(project):
    prompt = examples_prompt(project)

    assert prompt.index("satisfies the state contract") < prompt.index("certified example")


def test_examples_are_optional_in_the_writing_prompt(project):
    with_examples = writing_prompt(project)
    without = writing_prompt(project, with_examples=False)

    assert "WORKED EXAMPLES" in with_examples
    assert "WORKED EXAMPLES" not in without
    # The contract must survive either way; examples are help, not the brief.
    for prompt in (with_examples, without):
        assert "OBSERVABLE STATE CONTRACT" in prompt
        assert "RUNTIME ACCEPTANCE" in prompt
