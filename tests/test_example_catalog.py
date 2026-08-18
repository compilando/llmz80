"""Tests for deterministic, program-centred example retrieval."""

from pathlib import Path

from llmz80.core.example_catalog import MAIN_RE, ExampleCatalog
from llmz80.quality.benchmark import load_corpus

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_cpc_catalog_indexes_programs_not_asset_translation_units():
    catalog = ExampleCatalog(
        "amstrad_cpc",
        [
            REPO_ROOT / "examples" / "amstrad_cpc",
            REPO_ROOT / "examples" / "amstrad_cpc_level2",
        ],
    )

    entries = catalog.discover()

    assert entries
    assert all(
        MAIN_RE.search(entry["file_path"].read_text(encoding="utf-8", errors="ignore"))
        for entry in entries
    )
    assert not any(entry["path"].endswith("sprites.c") for entry in entries)
    assert all(entry["has_makefile"] for entry in entries)
    assert any(entry["path"].startswith("amstrad_cpc_level2/") for entry in entries)
    assert not any("arkosAudio" in entry["path"] for entry in entries)


def test_catalog_retrieval_is_stable_and_intent_aware():
    catalog = ExampleCatalog("spectrum", REPO_ROOT / "examples" / "spectrum")

    first = catalog.search("juego con teclado QAOP y graficos", limit=5)
    second = catalog.search("juego con teclado QAOP y graficos", limit=5)

    assert [example["path"] for example in first] == [example["path"] for example in second]
    assert any("keyboard" in example["path"] or "qaop" in example["path"] for example in first)
    assert all("main(" in example["content"] for example in first)


def test_cpc_catalog_keeps_support_context_for_complete_project():
    catalog = ExampleCatalog("amstrad_cpc", REPO_ROOT / "examples" / "amstrad_cpc")

    examples = catalog.search("sprite", limit=6)

    assert examples
    assert any("SUPPORT FILE" in example["content"] for example in examples)


def test_every_entry_has_capability_metadata():
    catalogs = (
        ExampleCatalog("spectrum", REPO_ROOT / "examples" / "spectrum"),
        ExampleCatalog(
            "amstrad_cpc",
            [
                REPO_ROOT / "examples" / "amstrad_cpc",
                REPO_ROOT / "examples" / "amstrad_cpc_level2",
            ],
        ),
    )
    for catalog in catalogs:
        for entry in catalog.discover():
            assert entry["description"] != "main"
            assert isinstance(entry["capabilities"], list)
            assert entry["quality_tier"] == "certified"
            assert entry["complexity"] in {"small", "medium", "large"}


def test_benchmark_queries_retrieve_capability_evidence():
    corpus = load_corpus(REPO_ROOT / "benchmarks/prompts.yml")
    catalogs = {
        "spectrum": ExampleCatalog("spectrum", REPO_ROOT / "examples" / "spectrum"),
        "amstrad_cpc": ExampleCatalog(
            "amstrad_cpc",
            [
                REPO_ROOT / "examples" / "amstrad_cpc",
                REPO_ROOT / "examples" / "amstrad_cpc_level2",
            ],
        ),
    }
    for case in corpus["cases"]:
        examples = catalogs[case["platform"]].search(case["prompt"], limit=5)
        retrieved = set().union(*(set(item["capabilities"]) for item in examples))
        assert retrieved & set(case["required_capabilities"]), case["id"]
