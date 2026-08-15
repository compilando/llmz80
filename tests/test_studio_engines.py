"""Third-party engines: what they must declare before they can be used."""

from pathlib import Path

import pytest

from llmz80.studio.engines import (
    ALLOWED_LICENCES,
    EngineClass,
    EnginePack,
    engine_registry,
)
from llmz80.studio.models import TargetPlatform


def _pack(**overrides) -> EnginePack:
    fields = dict(
        id="cpctelera",
        name="CPCtelera",
        platform=TargetPlatform.AMSTRAD_CPC,
        engine_class=EngineClass.LIBRARY,
        repository="https://github.com/lronaldo/cpctelera",
        commit="0" * 40,
        licence="GPL-3.0-or-later",
        vendor_dir=Path("vendor/cpctelera"),
        probe_map={"g_score": "_g_score", "g_state": "_g_state", "g_worst_frame_cost": "_g_wfc"},
        capabilities=frozenset({"masked_sprites", "hardware_scroll", "ay_music"}),
    )
    fields.update(overrides)
    return EnginePack(**fields)


def test_gpl_is_accepted_because_the_project_accepted_what_it_means():
    assert _pack().licence_errors() == []
    assert "GPL-3.0-or-later" in ALLOWED_LICENCES


def test_an_unknown_licence_is_refused_by_name():
    errors = _pack(licence="ask-the-author").licence_errors()

    assert len(errors) == 1
    assert "ask-the-author" in errors[0]


def test_an_engine_that_cannot_be_probed_is_refused():
    """Every gate this project owns reads the state contract out of memory. An
    engine that does not say where its state lives silently switches all of
    them off."""
    errors = _pack(probe_map={"g_score": "_g_score"}).probe_errors()

    assert len(errors) == 1
    assert "g_state" in errors[0]
    assert "g_worst_frame_cost" in errors[0]


def test_a_commit_that_is_not_pinned_is_refused():
    """A branch name is not a version: the engine under it changes and the
    games built against it stop being reproducible."""
    assert _pack(commit="main").pin_errors() != []
    assert _pack().pin_errors() == []


def test_the_registry_keeps_one_pack_per_id():
    registry = engine_registry(load_external=False, packs=(_pack(),))

    assert registry.get("cpctelera").name == "CPCtelera"
    with pytest.raises(KeyError, match="unknown plugin"):
        registry.get("mk1")
