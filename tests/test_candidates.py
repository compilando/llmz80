import json

from llmz80.quality.candidates import select_candidate


def _candidate(path, *, build=True, semantic=True, boot=True, visual=True, size=100,
               runtime_required=False, runtime_pass=True):
    path.mkdir()
    (path / "build_report.json").write_text(json.dumps({
        "quality_pass": build, "unexpected_warning_count": 0,
        "program_binary": {"size_bytes": size},
    }), encoding="utf-8")
    (path / "semantic_report.json").write_text(json.dumps({
        "quality_pass": semantic, "errors": [], "warnings": [],
    }), encoding="utf-8")
    (path / "emulator_report.json").write_text(json.dumps({
        "requested_full": runtime_required, "runtime_verified": runtime_pass,
        "quality_pass": runtime_pass, "boot": boot,
        "visual_change": visual, "input_transition": True,
    }), encoding="utf-8")


def test_candidate_selection_prefers_quality_then_smaller_binary(tmp_path):
    first, second, broken = tmp_path / "first", tmp_path / "second", tmp_path / "broken"
    _candidate(first, size=300)
    _candidate(second, size=200)
    _candidate(broken, build=False, size=10)
    report = select_candidate([broken, first, second])
    assert report["selected"]["run_dir"] == str(second)
    assert [item["run_dir"] for item in report["candidates"]] == [str(second), str(first), str(broken)]


def test_candidate_runtime_gate_rejects_a_failed_full_run(tmp_path):
    good, failed = tmp_path / "good", tmp_path / "failed"
    _candidate(good, runtime_required=True, runtime_pass=True, size=200)
    _candidate(failed, runtime_required=True, runtime_pass=False, size=100)
    report = select_candidate([failed, good])
    assert report["selected"]["run_dir"] == str(good)
    assert report["candidates"][1]["quality_pass"] is False
