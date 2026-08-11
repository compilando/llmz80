from pathlib import Path

from llmz80.cli import main
from llmz80.studio.store import ProjectStore


def test_new_creates_a_valid_project_with_defaults(tmp_path: Path, capsys):
    code = main(["project", "new", str(tmp_path), "My Game"])

    assert code == 0
    printed = Path(capsys.readouterr().out.strip())
    assert printed == tmp_path / "my-game" / "game.yml"
    project = ProjectStore(tmp_path).load(printed)
    assert project.target.platform.value == "spectrum"
    assert project.genre == "maze_chase"


def test_new_accepts_a_target_and_genre(tmp_path: Path, capsys):
    code = main(["project", "new", str(tmp_path), "Cpc", "amstrad_cpc", "single_screen_collect"])

    assert code == 0
    project = ProjectStore(tmp_path).load(Path(capsys.readouterr().out.strip()))
    assert project.target.platform.value == "amstrad_cpc"
    assert project.genre == "single_screen_collect"


def test_new_rejects_an_unknown_target(tmp_path: Path, capsys):
    code = main(["project", "new", str(tmp_path), "Bad", "atari"])

    assert code == 2
    assert "not a valid TargetPlatform" in capsys.readouterr().out


def test_validate_reports_the_current_schema_version(tmp_path: Path, capsys):
    main(["project", "new", str(tmp_path), "Schema"])
    capsys.readouterr()

    code = main(["project", "validate", str(tmp_path / "schema" / "game.yml")])

    assert code == 0
    assert "schema v3" in capsys.readouterr().out


def test_help_lists_every_project_subcommand(capsys):
    assert main(["help"]) == 0

    printed = capsys.readouterr().out
    for command in ("new", "validate", "generate", "build", "test", "release"):
        assert f"llmz80 project {command}" in printed


def test_help_lists_the_write_command(capsys):
    main(["help"])

    assert "llmz80 project write PATH" in capsys.readouterr().out
