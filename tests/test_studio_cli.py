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


def _stub_adapt_dependencies(monkeypatch, designer):
    """Route the `adapt` command's OpenAI-backed collaborator to a fake.

    Same reasoning as `_stub_reference_dependencies`: `_project_command`
    resolves `openai.OpenAI` and `ResponsesReferenceDesigner` through local
    imports inside the branch, so the modules they come from are patched
    rather than any name already bound in `llmz80.cli`.
    """
    import llmz80.studio.reference_design as reference_design_module
    import llmz80.utils.config as config_module
    import openai

    monkeypatch.setattr(openai, "OpenAI", lambda **_: object())
    monkeypatch.setattr(config_module, "load_api_key", lambda: "test-key")
    monkeypatch.setattr(config_module, "load_config", lambda *_: {})
    monkeypatch.setattr(
        reference_design_module, "ResponsesReferenceDesigner", lambda *_a, **_k: designer
    )


class _FakeDesigner:
    def __init__(self, proposal):
        self._proposal = proposal

    def propose(self, project, dossier):
        return self._proposal


def _lives_proposal():
    from llmz80.studio.planner import ProjectChange, ProjectProposal

    return ProjectProposal(
        summary="tune the difficulty",
        changes=[
            ProjectChange(
                path="/gameplay/lives",
                operation="replace",
                value_number=5,
                reason="match the source",
            )
        ],
    )


def _sealing_proposal(project):
    """Borrowed from tests/test_studio_planner_gate.py: a proposal apply_proposal
    genuinely refuses because it walls a collectible in on every side -- not one
    that merely fails schema validation, which would exercise a different path.
    """
    from llmz80.studio.planner import ProjectChange, ProjectProposal

    occupied = {(s.col, s.row) for s in project.levels[0].spawns}
    roles = {e.id: e.role for e in project.entities}
    neighbours = lambda c: [(c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)]
    target = next(
        (s.col, s.row)
        for s in project.levels[0].spawns
        if roles.get(s.entity) == "collectible"
        and not any(n in occupied for n in neighbours((s.col, s.row)))
    )
    rows = [list(row) for row in project.levels[0].tiles]
    for col, row in neighbours(target):
        rows[row][col] = "#"
    return ProjectProposal(
        summary="add decorative walls",
        changes=[
            ProjectChange(
                path="/levels/0/tiles",
                operation="replace",
                value_rows=["".join(row) for row in rows],
                reason="frame the pellet with masonry",
            )
        ],
    )


def test_adapt_reports_when_no_dossier_has_been_researched_yet(
    tmp_path: Path, capsys, monkeypatch
):
    main(["project", "new", str(tmp_path), "No Dossier"])
    capsys.readouterr()
    game_path = tmp_path / "no-dossier" / "game.yml"

    _stub_adapt_dependencies(monkeypatch, _FakeDesigner(None))
    code = main(["project", "adapt", str(game_path)])

    printed = capsys.readouterr().out
    assert code == 1
    assert "ERROR:" in printed
    assert "there is no researched game for this project yet" in printed
    assert "llmz80 project reference PATH" in printed


def test_adapt_declined_leaves_game_yml_byte_for_byte_unchanged(
    tmp_path: Path, capsys, monkeypatch
):
    from llmz80.studio.reference import save_reference

    main(["project", "new", str(tmp_path), "Adapt Decline"])
    capsys.readouterr()
    directory = tmp_path / "adapt-decline"
    game_path = directory / "game.yml"
    save_reference(_identified_dossier("Decline Game"), directory)
    before = game_path.read_text()

    _stub_adapt_dependencies(monkeypatch, _FakeDesigner(_lives_proposal()))
    monkeypatch.setattr("builtins.input", lambda *_: "n")
    code = main(["project", "adapt", str(game_path)])

    printed = capsys.readouterr().out
    assert code == 0
    assert "Left unchanged." in printed
    assert game_path.read_text() == before


def test_adapt_accepted_applies_the_proposal_and_saves_it(tmp_path: Path, capsys, monkeypatch):
    from llmz80.studio.reference import save_reference

    main(["project", "new", str(tmp_path), "Adapt Accept"])
    capsys.readouterr()
    directory = tmp_path / "adapt-accept"
    game_path = directory / "game.yml"
    save_reference(_identified_dossier("Accept Game"), directory)
    before = game_path.read_text()

    _stub_adapt_dependencies(monkeypatch, _FakeDesigner(_lives_proposal()))
    monkeypatch.setattr("builtins.input", lambda *_: "y")
    code = main(["project", "adapt", str(game_path)])

    printed = capsys.readouterr().out
    assert code == 0
    assert str(game_path) in printed
    assert game_path.read_text() != before
    assert ProjectStore(tmp_path).load(game_path).gameplay.lives == 5


def test_adapt_reports_a_proposal_apply_proposal_genuinely_refuses(
    tmp_path: Path, capsys, monkeypatch
):
    from llmz80.studio.reference import save_reference

    main(["project", "new", str(tmp_path), "Adapt Refuse"])
    capsys.readouterr()
    directory = tmp_path / "adapt-refuse"
    game_path = directory / "game.yml"
    save_reference(_identified_dossier("Refuse Game"), directory)
    before = game_path.read_text()
    proposal = _sealing_proposal(ProjectStore(tmp_path).load(game_path))

    _stub_adapt_dependencies(monkeypatch, _FakeDesigner(proposal))
    monkeypatch.setattr("builtins.input", lambda *_: "y")
    code = main(["project", "adapt", str(game_path)])

    printed = capsys.readouterr().out
    assert code == 1
    assert "ERROR:" in printed
    assert "REFUSED:" not in printed
    assert "would leave the game unplayable" in printed
    assert game_path.read_text() == before


def test_reference_reports_rather_than_crashes_on_a_malformed_model_response(
    tmp_path: Path, capsys, monkeypatch
):
    """The OpenAI SDK parses the model's JSON into GameReference itself, inside
    client.responses.parse(): a response that satisfies the JSON schema but
    violates a cross-field rule (an "identified" dossier with no sources) raises
    pydantic.ValidationError from there, before ResponsesReferenceResearcher or
    StudioService ever see a constructed object.

    Every other fake .parse() in this suite returns an already-built dossier,
    which bypasses that step entirely and cannot exercise this path. This one
    instead performs the real GameReference validation client-side, the way
    the SDK's own post-parser would, and lets the genuine ValidationError
    propagate -- without stubbing ResponsesReferenceResearcher itself, and
    without a network call.
    """
    from llmz80.studio.reference import GameReference

    main(["project", "new", str(tmp_path), "Malformed Response"])
    capsys.readouterr()
    game_path = tmp_path / "malformed-response" / "game.yml"

    class _RaisingResponses:
        def parse(self, **_kwargs):
            # Satisfies GameReference's JSON schema field-by-field but fails
            # its cross-field model_validator -- a shape a real model
            # response could take, and exactly what the SDK's own post-parse
            # step would raise on.
            return GameReference.model_validate(
                {"identified": True, "confidence": "high", "title": "Not Really", "sources": []}
            )

    class _RaisingClient:
        def __init__(self, **_kwargs):
            self.responses = _RaisingResponses()

    import llmz80.utils.config as config_module
    import openai

    monkeypatch.setattr(openai, "OpenAI", _RaisingClient)
    monkeypatch.setattr(config_module, "load_api_key", lambda: "test-key")
    monkeypatch.setattr(config_module, "load_config", lambda *_: {})

    code = main(["project", "reference", str(game_path)])

    printed = capsys.readouterr().out
    assert code == 1
    assert "ERROR:" in printed
    assert "Traceback" not in printed
