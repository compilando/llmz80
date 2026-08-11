"""The reference dossier: shape, rules and what it refuses to be."""

import pytest
from pydantic import ValidationError

from llmz80.studio.reference import GameReference, ReferenceSource


def _dossier(**overrides) -> GameReference:
    document = {
        "identified": True,
        "confidence": "high",
        "title": "Zampa Bolas",
        "publisher": "Iber Soft",
        "year": 1985,
        "platforms": ["spectrum"],
        "mechanics": ["eat every dot", "two ghosts chase the player"],
        "screen_layout": "score on the top row, maze below it",
        "pacing": "the player moves one cell per frame, ghosts one every four",
        "visual_style": "bright maze on black, chunky monochrome sprites",
        "level_structure": "three mazes of rising density",
        "sources": [
            {
                "url": "https://worldofspectrum.org/example",
                "title": "Zampa Bolas",
                "retrieved_at": "2026-08-11T09:00:00Z",
            }
        ],
    }
    document.update(overrides)
    return GameReference.model_validate(document)


def test_a_dossier_keeps_its_sources():
    dossier = _dossier()

    assert dossier.identified is True
    assert isinstance(dossier.sources[0], ReferenceSource)
    assert dossier.sources[0].url == "https://worldofspectrum.org/example"


def test_an_identified_dossier_without_sources_is_refused():
    """A claim about a real game with nothing behind it is worse than no claim."""
    with pytest.raises(ValidationError, match="sources"):
        _dossier(sources=[])


def test_an_unidentified_dossier_needs_no_sources():
    dossier = _dossier(identified=False, confidence="low", sources=[], title="")

    assert dossier.identified is False
    assert dossier.sources == []
