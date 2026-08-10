import json

from llmz80.core.learning import LearningSystem


GOOD_EVIDENCE = {
    "build_quality_pass": True,
    "semantic_quality_pass": True,
    "emulator": {
        "mode": "emulator_headless", "runtime_verified": True,
        "boot": True, "visual_change": True, "quality_pass": True,
    },
}


def test_runs_are_immutable_and_stats_use_honest_denominator(tmp_path):
    learning = LearningSystem("spectrum", str(tmp_path))
    first = learning.record_run("one", 1, "success", GOOD_EVIDENCE)
    second = learning.record_run("one", 4, "failure", {"reason": "compile"})
    lines = (tmp_path / "spectrum_runs.jsonl").read_text().splitlines()
    assert len(lines) == 2
    assert first.run_id != second.run_id
    assert learning.get_stats()["total_generations"] == 2
    assert learning.get_stats()["successful_compilations"] == 1
    assert learning.get_stats()["failed_compilations"] == 1


def test_unverified_compile_is_recorded_but_not_promoted(tmp_path):
    learning = LearningSystem("spectrum", str(tmp_path))
    key = learning.add_successful_example("prompt", "void main(void){}", evidence={})
    assert key is None
    assert learning.successful_examples == {}
    assert learning.get_stats()["total_generations"] == 1


def test_quality_evidence_promotes_without_overwriting_run_history(tmp_path):
    learning = LearningSystem("spectrum", str(tmp_path))
    first = learning.add_successful_example("prompt", "void main(void){}", evidence=GOOD_EVIDENCE)
    second = learning.add_successful_example("prompt", "void main(void){while(1){}}", evidence=GOOD_EVIDENCE)
    assert first == second
    assert len(learning.runs) == 2
    assert learning.successful_examples[first].promoted is True


def test_legacy_examples_migrate_as_unpromoted(tmp_path):
    legacy = {
        "abc": {
            "prompt": "old", "code": "void main(void){}", "platform": "spectrum",
            "timestamp": "2020-01-01T00:00:00", "compilation_attempts": 1,
            "rating": None, "tags": [],
        }
    }
    (tmp_path / "spectrum_successful_examples.json").write_text(json.dumps(legacy), encoding="utf-8")
    learning = LearningSystem("spectrum", str(tmp_path))
    assert learning.successful_examples["abc"].promoted is False


def test_dynamic_emulator_failure_blocks_promotion():
    evidence = dict(GOOD_EVIDENCE)
    evidence["emulator"] = {
        "mode": "emulator_headless", "runtime_verified": True,
        "boot": True, "visual_change": False, "quality_pass": False,
    }
    assert LearningSystem.should_promote(evidence) is False


def test_portable_static_evidence_never_promotes():
    evidence = dict(GOOD_EVIDENCE)
    evidence["emulator"] = {
        "mode": "portable_static", "runtime_verified": False,
        "static_pass": True, "quality_pass": False,
    }
    assert LearningSystem.should_promote(evidence) is False
