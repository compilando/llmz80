import json
from zipfile import ZipFile

import pytest

from llmz80.studio.models import TargetPlatform
from llmz80.studio.release import export_release
from llmz80.studio.samples import blank_project
from llmz80.studio.store import ProjectStore


def _evidence(directory, passing=True, verification="observed"):
    """Evidence for a releasable game. `verification=None` omits the key entirely,
    which is how every report written before the key existed reads."""
    build = directory / "build"
    build.mkdir()
    (build / "output.tap").write_bytes(b"tap")
    for name in ("build_report.json", "emulator_report.json"):
        (build / name).write_text(json.dumps({"quality_pass": passing}))
    report = {"quality_pass": passing}
    if verification is not None:
        report["verification"] = verification
    (build / "studio_quality_report.json").write_text(json.dumps(report))


def test_release_is_reproducible_and_contains_evidence(tmp_path):
    project = blank_project("Release", TargetPlatform.SPECTRUM)
    directory = ProjectStore(tmp_path).create(project)
    _evidence(directory)

    first = export_release(project, directory, tmp_path / "first.zip")
    second = export_release(project, directory, tmp_path / "second.zip")

    assert first.read_bytes() == second.read_bytes()
    with ZipFile(first) as archive:
        assert set(archive.namelist()) >= {
            "game.yml",
            "output.tap",
            "SHA256SUMS",
            "reports/studio_quality_report.json",
        }


def test_release_rejects_missing_or_failed_quality_gate(tmp_path):
    project = blank_project("Rejected", TargetPlatform.SPECTRUM)
    directory = ProjectStore(tmp_path).create(project)
    with pytest.raises(RuntimeError, match="runtime test"):
        export_release(project, directory)
    _evidence(directory, passing=False)
    with pytest.raises(RuntimeError, match="every Studio quality gate"):
        export_release(project, directory)


def test_a_game_nobody_observed_is_not_released(tmp_path):
    """The build passed and every behaviour gate abstained. That is a candidate,
    not a release, and the difference has to be enforced somewhere the operator
    cannot skip by accident. The refusal names the level it actually read, so
    nobody has to guess which of the two checks turned them away."""
    project = blank_project("Unwatched", TargetPlatform.SPECTRUM)
    directory = ProjectStore(tmp_path).create(project)
    _evidence(directory, verification="built")

    with pytest.raises(RuntimeError, match="records verification 'built', not 'observed'"):
        export_release(project, directory)


def test_a_report_written_before_verification_existed_is_refused(tmp_path):
    """Every report on disk today predates the `verification` key. A missing
    claim is not a claim, so the absent key refuses exactly as `built` does."""
    project = blank_project("Legacy", TargetPlatform.SPECTRUM)
    directory = ProjectStore(tmp_path).create(project)
    _evidence(directory, verification=None)

    with pytest.raises(RuntimeError, match="every behaviour gate abstained"):
        export_release(project, directory)


def test_release_notes_state_the_verification_level(tmp_path):
    """The zip outlives the project directory, so it has to carry how much was
    known about the game rather than an unfalsifiable claim that it was verified."""
    project = blank_project("Noted", TargetPlatform.SPECTRUM)
    directory = ProjectStore(tmp_path).create(project)
    _evidence(directory)

    archive_path = export_release(project, directory, tmp_path / "noted.zip")

    with ZipFile(archive_path) as archive:
        notes = archive.read("RELEASE_NOTES.txt").decode("utf-8")
    assert "Verification: observed" in notes
