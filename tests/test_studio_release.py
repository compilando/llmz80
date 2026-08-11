import json
from zipfile import ZipFile

import pytest

from llmz80.studio.models import GenreId, TargetPlatform
from llmz80.studio.packs import create_default_project
from llmz80.studio.release import export_release
from llmz80.studio.store import ProjectStore


def _evidence(directory, passing=True):
    build = directory / "build"
    build.mkdir()
    (build / "output.tap").write_bytes(b"tap")
    for name in ("build_report.json", "emulator_report.json"):
        (build / name).write_text(json.dumps({"quality_pass": passing}))
    (build / "studio_quality_report.json").write_text(json.dumps({"quality_pass": passing}))


def test_release_is_reproducible_and_contains_evidence(tmp_path):
    project = create_default_project("Release", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
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
    project = create_default_project("Rejected", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    directory = ProjectStore(tmp_path).create(project)
    with pytest.raises(RuntimeError, match="runtime test"):
        export_release(project, directory)
    _evidence(directory, passing=False)
    with pytest.raises(RuntimeError, match="every Studio quality gate"):
        export_release(project, directory)
