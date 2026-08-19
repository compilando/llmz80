import pytest

from llmz80.studio.generator import writing_prompt
from llmz80.studio.models import GameProject, TargetPlatform
from llmz80.studio.retrieval import (
    MAX_EXAMPLE_CHARS,
    catalog_examples,
    examples_prompt,
    reference_program,
    retrieval_query,
)
from llmz80.studio.samples import blank_project


@pytest.fixture
def project():
    return blank_project("Retrieved", TargetPlatform.SPECTRUM)


def test_the_retrieval_query_is_built_from_the_designs_own_words():
    document = blank_project("Query", TargetPlatform.SPECTRUM).model_dump(mode="json")
    document["metadata"]["brief"] = "laberinto de piedra"
    document["mechanics"] = ["el jugador salta"]
    document["entities"][0]["kind"] = "explorador"
    query = retrieval_query(GameProject.model_validate(document))
    assert "laberinto de piedra" in query
    assert "explorador" in query
    assert "salta" in query


@pytest.mark.parametrize("platform", list(TargetPlatform))
def test_examples_come_from_the_projects_own_platform(platform):
    project = blank_project("Platform", platform)

    found = catalog_examples(project)

    assert found, "the certified corpus should offer something for every target"
    for _name, source in found:
        if platform is TargetPlatform.SPECTRUM:
            assert "cpct_" not in source
        else:
            assert "zx_cls" not in source


def test_the_reference_program_is_offered_for_both_targets():
    for platform in TargetPlatform:
        project = blank_project("Ref", platform)

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
        # There is no acceptance section any more: deriving one assumed a
        # pellet sweeper, and the examiner that replaces it is phase 2.
        assert "Terrain characters" in prompt
