from llmz80.core.build_quality import (
    build_report,
    classify_build_warnings,
    quality_rejection_diagnostics,
    select_fresh_artifact,
)


def test_warning_classifier_rejects_ignored_options_and_source_warnings(tmp_path):
    cpct = tmp_path / "cpctelera"
    output = "\n".join(
        [
            "at 1: warning 117: unknown compiler option '--subtype=tap' ignored",
            "main.c:12: warning 42: suspicious generated code",
            "main.c:20: warning 110: conditional flow changed by optimizer",
            f"{cpct}/src/video.h:33: warning 283: function declarator with no prototype",
        ]
    )

    groups = classify_build_warnings(output, cpct_path=cpct)

    assert len(groups["structural"]) == 1
    assert len(groups["source"]) == 1
    assert len(groups["allowed"]) == 1
    assert len(groups["sdk"]) == 1


def test_build_report_requires_nonempty_canonical_artifact(tmp_path):
    artifact = tmp_path / "output.tap"
    artifact.write_bytes(b"tap")
    (tmp_path / "output_CODE.bin").write_bytes(b"code")

    report = build_report(
        platform="spectrum",
        output_dir=tmp_path,
        command=["zcc", "-subtype=default"],
        return_code=0,
        stdout="",
        stderr="",
        artifacts=[artifact],
    )

    assert report["quality_pass"] is True
    assert report["canonical_artifact"]["size_bytes"] == 3
    assert report["program_binary"]["size_bytes"] == 4


def test_build_report_fails_quality_on_structural_warning(tmp_path):
    artifact = tmp_path / "output.tap"
    artifact.write_bytes(b"tap")

    report = build_report(
        platform="spectrum",
        output_dir=tmp_path,
        command=["zcc", "--bad"],
        return_code=0,
        stdout="",
        stderr="warning: unknown compiler option '--bad' ignored",
        artifacts=[artifact],
    )

    assert report["compile_succeeded"] is True
    assert report["quality_pass"] is False
    assert report["unexpected_warning_count"] == 1


def test_quality_rejection_exposes_source_warning_to_correction_loop(tmp_path):
    artifact = tmp_path / "output.dsk"
    artifact.write_bytes(b"dsk")
    report = build_report(
        platform="amstrad_cpc",
        output_dir=tmp_path,
        command=["make"],
        return_code=0,
        stdout="src/main.c:77: warning 158: overflow in implicit constant conversion",
        stderr="",
        artifacts=[artifact],
    )
    diagnostics = quality_rejection_diagnostics(report)
    assert any("warning 158" in line for line in diagnostics)
    assert report["compile_succeeded"] is True
    assert report["quality_pass"] is False


def test_fresh_build_artifact_replaces_stale_canonical_copy(tmp_path):
    canonical = tmp_path / "output.dsk"
    generated = tmp_path / "program.dsk"
    canonical.write_bytes(b"old")
    generated.write_bytes(b"new")
    assert select_fresh_artifact(canonical, [canonical, generated]) == generated


def test_cpc_candidate_can_be_gated_before_canonical_publication(tmp_path):
    candidate = tmp_path / "program.dsk"
    candidate.write_bytes(b"candidate")

    report = build_report(
        platform="amstrad_cpc",
        output_dir=tmp_path,
        command=["make"],
        return_code=0,
        stdout="",
        stderr="",
        artifacts=[candidate],
        candidate_artifact=candidate,
    )

    assert report["quality_pass"] is True
    assert report["canonical_artifact"]["exists"] is True
    assert report["canonical_artifact"]["published"] is False
    assert report["canonical_artifact"]["staged_from"] == "program.dsk"
    assert not (tmp_path / "output.dsk").exists()
