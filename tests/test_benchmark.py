import json
from pathlib import Path

from llmz80.quality.benchmark import evaluate_corpus, load_corpus, write_scorecard
from scripts.evaluate_generation import _has_passing_runtime_run


ROOT = Path(__file__).resolve().parents[1]


def test_versioned_corpus_is_bilingual_and_covers_platforms():
    corpus = load_corpus(ROOT / "benchmarks/prompts.yml")
    assert len(corpus["cases"]) >= 20
    assert {case["language"] for case in corpus["cases"]} == {"es", "en"}
    assert {case["platform"] for case in corpus["cases"]} == {"spectrum", "amstrad_cpc"}


def test_offline_scorecard_is_deterministic(tmp_path):
    corpus = {
        "schema_version": 1,
        "name": "fixture",
        "cases": [{
            "id": "one", "platform": "spectrum", "language": "en",
            "prompt": "Hello", "archetype": "static_display",
            "required_capabilities": ["text"],
        }],
    }
    run = tmp_path / "runs/20260101_hello"
    run.mkdir(parents=True)
    (run / "prompt.txt").write_text("Hello", encoding="utf-8")
    (run / "platform.txt").write_text("spectrum", encoding="utf-8")
    (run / "build_report.json").write_text(json.dumps({
        "quality_pass": True,
        "unexpected_warning_count": 0,
        "canonical_artifact": {"size_bytes": 321},
        "program_binary": {"size_bytes": 123},
    }), encoding="utf-8")
    (run / "retrieval_context.json").write_text(json.dumps({
        "examples": [{"path": "text.c", "capabilities": ["text"]}],
    }), encoding="utf-8")

    first = evaluate_corpus(corpus, tmp_path / "runs")
    second = evaluate_corpus(corpus, tmp_path / "runs")
    assert first == second
    assert first["summary"]["first_build_rate"] == 1.0
    assert first["cases"][0]["program_binary_size"] == 123
    json_path, markdown_path = write_scorecard(first, tmp_path / "report/scorecard")
    assert json.loads(json_path.read_text())["schema_version"] == 1
    assert "First-build rate: 100.0%" in markdown_path.read_text()


def test_live_resume_requires_both_build_and_runtime_quality(tmp_path):
    run = tmp_path / "one"
    run.mkdir()
    (run / "prompt.txt").write_text("Hello", encoding="utf-8")
    (run / "platform.txt").write_text("spectrum", encoding="utf-8")
    (run / "build_report.json").write_text(
        json.dumps({"quality_pass": True}), encoding="utf-8"
    )
    (run / "emulator_report.json").write_text(
        json.dumps({"quality_pass": False}), encoding="utf-8"
    )
    assert not _has_passing_runtime_run(tmp_path, "Hello", "spectrum")
    (run / "emulator_report.json").write_text(
        json.dumps({"quality_pass": True}), encoding="utf-8"
    )
    assert _has_passing_runtime_run(tmp_path, "Hello", "spectrum")


def test_scorecard_reads_list_shaped_retrieval_context(tmp_path):
    corpus = {
        "schema_version": 1,
        "name": "list-context",
        "cases": [{
            "id": "one", "platform": "spectrum", "language": "en",
            "prompt": "Hello", "archetype": "static_display",
            "required_capabilities": ["text", "input"],
        }],
    }
    run = tmp_path / "runs/one"
    run.mkdir(parents=True)
    (run / "prompt.txt").write_text("Hello", encoding="utf-8")
    (run / "platform.txt").write_text("spectrum", encoding="utf-8")
    (run / "build_report.json").write_text(json.dumps({"quality_pass": True}), encoding="utf-8")
    (run / "retrieval_context.json").write_text(json.dumps([
        {"path": "example.c", "capabilities": ["text", "input"]}
    ]), encoding="utf-8")
    report = evaluate_corpus(corpus, tmp_path / "runs")
    assert report["cases"][0]["retrieval_recall"] == 1.0
    assert report["cases"][0]["retrieval_sources"] == ["example.c"]
