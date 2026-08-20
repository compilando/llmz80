"""Which model each kind of question is asked of.

Every collaborator in Studio defaulted to `claude-opus-5` and `config.yml`
named one model for all of them. That is right for the two stages that decide
what the game is and write its C, and it is what a survey of
`studio-projects/*/studio.log` found paying Opus rates to transcribe an 8x8
tile into eight rows of pen characters and to answer `coherent: true`.

A role is not a per-call-site model: it is a *kind* of question, so a new
examiner joins `exam` rather than adding a key.
"""

import pytest

from llmz80.utils.config import ROLES, model_for


def test_a_role_with_nothing_configured_falls_back_to_the_one_model():
    config = {"anthropic": {"model": "claude-opus-5"}}

    assert model_for("art", config) == "claude-opus-5"


def test_a_configured_role_wins_over_the_general_model():
    config = {"anthropic": {"model": "claude-opus-5", "models": {"art": "claude-sonnet-5"}}}

    assert model_for("art", config) == "claude-sonnet-5"
    assert model_for("program", config) == "claude-opus-5"


def test_an_empty_configuration_still_answers():
    """A checkout with no config.yml runs on defaults rather than refusing."""
    assert model_for("program", {}) == "claude-opus-5"


def test_an_unknown_role_is_refused_rather_than_silently_defaulted():
    """A typo that reads as "use the expensive model" is the failure this
    whole exercise is about, and it would never announce itself."""
    with pytest.raises(ValueError, match="unknown model role"):
        model_for("sprites", {"anthropic": {"model": "claude-opus-5"}})


def test_every_role_the_pipeline_asks_for_is_a_role_that_exists():
    """`pipeline.py` names these as string literals; this is what pairs them
    with the table, since a mistyped one would otherwise raise minutes into a
    paid run rather than here."""
    assert set(ROLES) == {"research", "design", "art", "exam", "program"}


def test_the_shipped_configuration_is_readable_and_names_known_roles():
    """The file people actually run with, not a fixture."""
    from llmz80.utils.config import load_config

    config = load_config("config.yml")

    for role in ROLES:
        assert model_for(role, config)
