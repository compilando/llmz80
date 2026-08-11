"""The reference dossier: shape, rules and what it refuses to be."""

import pytest
from pydantic import ValidationError

from llmz80.studio.reference import (
    RESEARCH_SYSTEM_PROMPT,
    GameReference,
    ReferenceSource,
    ResponsesReferenceResearcher,
    load_reference,
    reference_prompt,
    save_reference,
)


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


def test_an_identified_dossier_with_a_blank_title_is_refused():
    """Whitespace is not a title: the check must strip before judging it empty."""
    with pytest.raises(ValidationError, match="title"):
        _dossier(title="   ")


def test_an_unidentified_dossier_needs_no_sources():
    dossier = _dossier(identified=False, confidence="low", sources=[], title="")

    assert dossier.identified is False
    assert dossier.sources == []


def test_a_dossier_survives_a_round_trip(tmp_path):
    dossier = _dossier()
    saved = save_reference(dossier, tmp_path)

    assert saved == tmp_path / "reference.yml"
    assert load_reference(tmp_path) == dossier


def test_a_missing_dossier_reads_as_none(tmp_path):
    assert load_reference(tmp_path) is None


def test_a_dossier_that_fails_validation_is_refused_rather_than_ignored(tmp_path):
    """Silently ignoring a broken file would rebuild the design from nothing."""
    (tmp_path / "reference.yml").write_text("identified: yes please\n", encoding="utf-8")

    with pytest.raises(ValueError, match="reference.yml"):
        load_reference(tmp_path)


def test_a_dossier_with_broken_yaml_is_refused_rather_than_ignored(tmp_path):
    """The other half of the catch: syntactically invalid YAML, not just a bad document."""
    (tmp_path / "reference.yml").write_text(
        "identified: [true\n  confidence: high\n", encoding="utf-8"
    )

    with pytest.raises(ValueError, match="reference.yml"):
        load_reference(tmp_path)


def test_a_hand_edited_dossier_wins(tmp_path):
    """Correcting a wrong dossier by hand has to stick, or correcting it is pointless."""
    save_reference(_dossier(), tmp_path)
    path = tmp_path / "reference.yml"
    path.write_text(
        path.read_text(encoding="utf-8").replace("Iber Soft", "Topo Soft"), encoding="utf-8"
    )

    assert load_reference(tmp_path).publisher == "Topo Soft"


def test_the_prompt_block_carries_the_facts_and_the_sources():
    block = reference_prompt(_dossier())

    assert "REFERENCE GAME" in block
    assert "Zampa Bolas" in block
    assert "Iber Soft" in block
    assert "two ghosts chase the player" in block
    assert "https://worldofspectrum.org/example" in block


def test_an_unidentified_dossier_produces_no_prompt_block():
    assert reference_prompt(_dossier(identified=False, sources=[], title="")) == ""


def test_no_dossier_produces_no_prompt_block():
    assert reference_prompt(None) == ""


def test_an_unknown_publisher_with_a_year_reads_as_a_whole_sentence():
    """Magazine type-ins and self-published titles legitimately have no
    publisher; a bare ", 1985" left over from a blank publisher would read
    as a typo rather than a fact."""
    block = reference_prompt(_dossier(publisher="", year=1985))

    assert "Zampa Bolas (1985) for spectrum." in block
    assert ", 1985" not in block


def test_neither_publisher_nor_year_produces_no_dangling_parenthesis():
    block = reference_prompt(_dossier(publisher="", year=None))

    assert "Zampa Bolas for spectrum." in block
    assert "()" not in block


class _FakeResponses:
    """Stands in for client.responses, recording how it was called."""

    def __init__(self, parsed):
        self.parsed = parsed
        self.calls = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        return type("Response", (), {"output_parsed": self.parsed})()


class _FakeClient:
    def __init__(self, parsed):
        self.responses = _FakeResponses(parsed)


def test_research_asks_for_web_search_and_returns_the_dossier():
    client = _FakeClient(_dossier())
    brief = "Zampabolas runs through a walled maze eating every dot"

    dossier = ResponsesReferenceResearcher(client).research(brief, "spectrum")

    assert dossier.title == "Zampa Bolas"
    call = client.responses.calls[0]
    assert {"type": "web_search"} in call["tools"]
    assert call["text_format"] is GameReference
    assert call["input"][0] == {"role": "system", "content": RESEARCH_SYSTEM_PROMPT}
    assert "spectrum" in call["input"][1]["content"]
    assert brief in call["input"][1]["content"]


def test_research_refuses_an_empty_parse():
    """No dossier is a failure, not an unidentified game: they mean different things."""
    client = _FakeClient(None)

    with pytest.raises(ValueError, match="did not return"):
        ResponsesReferenceResearcher(client).research("something", "spectrum")
