"""Third-party engines: what they must declare before they can be used."""

from pathlib import Path

import pytest

from llmz80.studio.engines import ALLOWED_LICENCES, EngineClass, EnginePack, engine_registry
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
        probe_map={"g_score": "g_score", "g_state": "g_state", "g_worst_frame_cost": "g_wfc"},
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
    errors = _pack(probe_map={"g_score": "g_score"}).probe_errors()

    assert len(errors) == 1
    assert "g_state" in errors[0]
    assert "g_worst_frame_cost" in errors[0]


def test_a_symbol_the_contract_does_not_have_is_refused_rather_than_ignored():
    """A typo in a probe name fails silently: the probe it was meant to enable
    never fires and no gate says why. This branch exists to remove exactly that
    kind of quiet abstention."""
    errors = _pack(
        probe_map={
            "g_score": "g_score",
            "g_state": "g_state",
            "g_worst_frame_cost": "g_wfc",
            "g_scores": "g_scores",
        }
    ).probe_errors()

    assert len(errors) == 1
    assert "g_scores" in errors[0]


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


def test_the_manifest_records_what_a_rebuild_would_need(tmp_path):
    from scripts.vendor_engine import write_manifest

    path = write_manifest(
        tmp_path,
        engine_id="cpctelera",
        repository="https://github.com/lronaldo/cpctelera",
        commit="a" * 40,
        licence="GPL-3.0-or-later",
    )

    import json

    manifest = json.loads(path.read_text(encoding="utf-8"))
    assert manifest["commit"] == "a" * 40
    assert manifest["licence"] == "GPL-3.0-or-later"
    assert manifest["repository"].endswith("cpctelera")


def test_vendoring_refuses_a_licence_nobody_read(tmp_path):
    import pytest

    from scripts.vendor_engine import write_manifest

    with pytest.raises(ValueError, match="not one this project has accepted"):
        write_manifest(
            tmp_path,
            engine_id="mystery",
            repository="https://example.invalid/mystery",
            commit="b" * 40,
            licence="UNKNOWN",
        )


def test_a_manifest_cannot_record_forty_characters_that_are_not_a_hash(tmp_path):
    """The script that writes a manifest and the pack that validates one test
    the same fact, so they test it the same way: a length-only check here would
    write a manifest no EnginePack could ever accept."""
    from scripts.vendor_engine import write_manifest

    with pytest.raises(ValueError, match="not a full commit hash"):
        write_manifest(
            tmp_path,
            engine_id="mystery",
            repository="https://example.invalid/mystery",
            commit="z" * 40,
            licence="MIT",
        )
