from pathlib import Path
from subprocess import CompletedProcess
import json

import llm_z80


class RepairingGenerator:
    def __init__(self):
        self.diagnostic = ""
        self.metrics_saved = 0

    def suggest_code_correction(self, failed_code, error_output, platform, **kwargs):
        self.diagnostic = error_output
        return failed_code.replace("int broken = 1;", "int repaired = 1;")

    def save_generation_metrics(self, output_dir: Path):
        self.metrics_saved += 1


def _report(quality_pass: bool):
    source = [] if quality_pass else [
        "main.c:7: warning 158: overflow in implicit constant conversion"
    ]
    return {
        "quality_pass": quality_pass,
        "unexpected_warning_count": len(source),
        "warnings": {"structural": [], "source": source, "other": [], "sdk": [], "allowed": []},
        "resources": {"errors": [], "quality_pass": True},
        "semantic_quality_pass": True,
        "canonical_artifact": {"path": "output.tap", "exists": True, "size_bytes": 8},
        "program_binary": None,
    }


def test_successful_compile_with_source_warning_is_repaired_and_retried(tmp_path, monkeypatch):
    (tmp_path / "main.c").write_text(
        "void main(void){ int broken = 1; while(1){} }", encoding="utf-8"
    )
    artifact = tmp_path / "output.tap"
    artifact.write_bytes(b"\x06\x00header")
    reports = iter((_report(False), _report(True)))
    monkeypatch.setattr(llm_z80, "build_report", lambda **kwargs: next(reports))
    monkeypatch.setattr(llm_z80, "save_build_environment_report", lambda *args: None)
    monkeypatch.setattr(
        llm_z80.subprocess,
        "run",
        lambda *args, **kwargs: CompletedProcess(args[0], 0, stdout="", stderr=""),
    )
    generator = RepairingGenerator()

    passed = llm_z80.attempt_compilation_and_correction(
        "spectrum",
        tmp_path,
        {"compiler": {"spectrum": {"c_compiler": "zcc", "params": ""}},
         "paths": {"spectrum": {"output_artifact": "output.tap"}}},
        generator,
        "test request",
        max_attempts=2,
        enable_validation=False,
    )

    assert passed is True
    assert "warning 158" in generator.diagnostic
    assert "int repaired = 1;" in (tmp_path / "main.c").read_text(encoding="utf-8")
    assert (tmp_path / "main_attempt_1.c").is_file()


def test_runtime_quality_failure_is_repaired_and_retried(tmp_path, monkeypatch):
    (tmp_path / "main.c").write_text(
        "void main(void){ int broken = 1; while(1){} }", encoding="utf-8"
    )
    (tmp_path / "output.tap").write_bytes(b"\x06\x00header")
    reports = iter((_report(True), _report(True)))
    smoke_reports = iter((
        {
            "quality_pass": False, "runtime_verified": True, "boot": True,
            "program_loaded": True, "non_blank_output": True, "visual_change": False,
            "scripted_input_sent": True, "input_transition": False, "scripted_input": "p",
        },
        {
            "quality_pass": True, "runtime_verified": True, "boot": True,
            "program_loaded": True, "non_blank_output": True, "visual_change": True,
            "scripted_input_sent": True, "input_transition": True, "scripted_input": "p",
        },
    ))
    monkeypatch.setattr(llm_z80, "build_report", lambda **kwargs: next(reports))
    monkeypatch.setattr(llm_z80, "smoke_test", lambda *args, **kwargs: next(smoke_reports))
    monkeypatch.setattr(llm_z80, "save_build_environment_report", lambda *args: None)
    monkeypatch.setattr(
        llm_z80.subprocess,
        "run",
        lambda *args, **kwargs: CompletedProcess(args[0], 0, stdout="", stderr=""),
    )
    generator = RepairingGenerator()

    passed = llm_z80.attempt_compilation_and_correction(
        "spectrum",
        tmp_path,
        {"compiler": {"spectrum": {"c_compiler": "zcc", "params": ""}},
         "paths": {"spectrum": {"output_artifact": "output.tap"}}},
        generator,
        "test request",
        max_attempts=2,
        enable_validation=False,
        runtime_check=True,
    )

    assert passed is True
    assert "RUNTIME QUALITY REJECTION" in generator.diagnostic
    assert "visual_change: False" in generator.diagnostic


def test_prevalidation_correction_refreshes_semantic_evidence_before_build(tmp_path, monkeypatch):
    (tmp_path / "main.c").write_text("void main(void){while(1){}}", encoding="utf-8")
    (tmp_path / "generation_spec.json").write_text(
        json.dumps({"states": ["running", "finished"]}), encoding="utf-8"
    )
    (tmp_path / "output.tap").write_bytes(b"\x06\x00header")

    class SemanticRepairGenerator(RepairingGenerator):
        def suggest_code_correction(self, failed_code, error_output, platform, **kwargs):
            self.diagnostic = error_output
            return "void main(void){int game_over=0;while(1){game_over=0;}}"

    monkeypatch.setattr(llm_z80, "save_build_environment_report", lambda *args: None)
    monkeypatch.setattr(
        llm_z80.subprocess,
        "run",
        lambda *args, **kwargs: CompletedProcess(args[0], 0, stdout="", stderr=""),
    )
    generator = SemanticRepairGenerator()
    passed = llm_z80.attempt_compilation_and_correction(
        "spectrum",
        tmp_path,
        {"compiler": {"spectrum": {"c_compiler": "zcc", "params": ""}},
         "paths": {"spectrum": {"output_artifact": "output.tap"}}},
        generator,
        "test request",
        max_attempts=1,
        enable_validation=True,
    )

    semantic = json.loads((tmp_path / "semantic_report.json").read_text(encoding="utf-8"))
    assert passed is True
    assert semantic["quality_pass"] is True
    assert "finished state" in generator.diagnostic
