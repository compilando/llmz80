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
    for command in ("new", "validate", "scaffold", "build", "test", "release", "write"):
        assert f"llmz80 project {command}" in printed


def test_help_lists_the_write_command(capsys):
    main(["help"])

    assert "llmz80 project write PATH" in capsys.readouterr().out


def test_release_without_evidence_reports_rather_than_crashes(tmp_path: Path, capsys):
    main(["project", "new", str(tmp_path), "Unproven"])
    capsys.readouterr()

    code = main(["project", "release", str(tmp_path / "unproven" / "game.yml")])

    printed = capsys.readouterr().out
    assert code == 1
    assert "ERROR:" in printed
    assert "Traceback" not in printed


def test_the_help_lists_the_reference_commands(capsys):
    from llmz80.cli import main

    main(["help"])

    printed = capsys.readouterr().out
    assert "project reference PATH" in printed
    assert "project adapt PATH" in printed


def _stub_reference_dependencies(monkeypatch, researcher):
    """Route the `reference` command's OpenAI-backed collaborators to a fake.

    `_project_command` imports `openai.OpenAI`, `ResponsesReferenceResearcher`,
    and the config loaders locally inside the branch, so patching the modules
    they come from (rather than names already bound in `llmz80.cli`) is what
    actually takes effect.
    """
    import llmz80.studio.reference as reference_module
    import llmz80.utils.config as config_module
    import openai

    monkeypatch.setattr(openai, "OpenAI", lambda **_: object())
    monkeypatch.setattr(config_module, "load_api_key", lambda: "test-key")
    monkeypatch.setattr(config_module, "load_config", lambda *_: {})
    monkeypatch.setattr(
        reference_module, "ResponsesReferenceResearcher", lambda *_a, **_k: researcher
    )


class _FakeResearcher:
    def __init__(self, dossier):
        self._dossier = dossier

    def research(self, brief, platform):
        return self._dossier


def _identified_dossier(title="Fresh Search Result"):
    from datetime import datetime, timezone

    from llmz80.studio.reference import GameReference, ReferenceSource

    return GameReference(
        identified=True,
        confidence="high",
        title=title,
        sources=[
            ReferenceSource(
                url="https://example.com/game",
                title="source",
                retrieved_at=datetime.now(timezone.utc),
            )
        ],
    )


def test_reference_asks_before_replacing_an_archived_dossier_and_honours_no(
    tmp_path: Path, capsys, monkeypatch
):
    main(["project", "new", str(tmp_path), "Archived"])
    capsys.readouterr()
    game_path = tmp_path / "archived" / "game.yml"
    reference_path = tmp_path / "archived" / "reference.yml"

    _stub_reference_dependencies(monkeypatch, _FakeResearcher(_identified_dossier("First Search")))
    monkeypatch.setattr("builtins.input", lambda *_: "y")
    assert main(["project", "reference", str(game_path)]) == 0
    capsys.readouterr()
    before = reference_path.read_text()

    prompts = []
    _stub_reference_dependencies(monkeypatch, _FakeResearcher(_identified_dossier("Second Search")))
    monkeypatch.setattr("builtins.input", lambda prompt="": prompts.append(prompt) or "n")
    code = main(["project", "reference", str(game_path)])

    printed = capsys.readouterr().out
    assert code == 0
    assert "First Search" in printed
    assert any("Replace it with a fresh search?" in prompt for prompt in prompts)
    assert "Left unchanged." in printed
    assert reference_path.read_text() == before


def test_reference_replaces_an_archived_dossier_on_yes(tmp_path: Path, capsys, monkeypatch):
    main(["project", "new", str(tmp_path), "Archived Two"])
    capsys.readouterr()
    game_path = tmp_path / "archived-two" / "game.yml"
    reference_path = tmp_path / "archived-two" / "reference.yml"

    _stub_reference_dependencies(monkeypatch, _FakeResearcher(_identified_dossier("First Search")))
    monkeypatch.setattr("builtins.input", lambda *_: "y")
    assert main(["project", "reference", str(game_path)]) == 0
    capsys.readouterr()

    _stub_reference_dependencies(monkeypatch, _FakeResearcher(_identified_dossier("Second Search")))
    monkeypatch.setattr("builtins.input", lambda *_: "y")
    code = main(["project", "reference", str(game_path)])

    assert code == 0
    assert "Second Search" in reference_path.read_text()
    assert "First Search" not in reference_path.read_text()


def test_reference_reports_rather_than_crashes_on_a_malformed_archive(
    tmp_path: Path, capsys, monkeypatch
):
    main(["project", "new", str(tmp_path), "Broken Archive"])
    capsys.readouterr()
    directory = tmp_path / "broken-archive"
    (directory / "reference.yml").write_text("not: [valid, reference", encoding="utf-8")

    _stub_reference_dependencies(monkeypatch, _FakeResearcher(_identified_dossier()))
    code = main(["project", "reference", str(directory / "game.yml")])

    printed = capsys.readouterr().out
    assert code == 1
    assert "ERROR:" in printed
    assert "Traceback" not in printed
