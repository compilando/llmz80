from pathlib import Path

from llmz80.cli import main
from llmz80.studio.store import ProjectStore
from tests.conftest import FakeMessageStream


def test_new_creates_a_valid_project_with_defaults(tmp_path: Path, capsys):
    code = main(["project", "new", str(tmp_path), "My Game"])

    assert code == 0
    printed = Path(capsys.readouterr().out.strip())
    assert printed == tmp_path / "my-game" / "game.yml"
    project = ProjectStore(tmp_path).load(printed)
    assert project.target.platform.value == "spectrum"
    assert len(project.screens) == 1
    assert len(project.entities) == 1


def test_new_accepts_a_target_and_brief(tmp_path: Path, capsys):
    code = main(["project", "new", str(tmp_path), "Cpc", "amstrad_cpc", "a maze full of ghosts"])

    assert code == 0
    project = ProjectStore(tmp_path).load(Path(capsys.readouterr().out.strip()))
    assert project.target.platform.value == "amstrad_cpc"
    assert project.metadata.brief == "a maze full of ghosts"


def test_new_rejects_an_unknown_target(tmp_path: Path, capsys):
    code = main(["project", "new", str(tmp_path), "Bad", "atari"])

    assert code == 2
    assert "not a valid TargetPlatform" in capsys.readouterr().out


def test_validate_reports_the_current_schema_version(tmp_path: Path, capsys):
    main(["project", "new", str(tmp_path), "Schema"])
    capsys.readouterr()

    code = main(["project", "validate", str(tmp_path / "schema" / "game.yml")])

    assert code == 0
    assert "schema v4" in capsys.readouterr().out


def test_help_lists_every_project_subcommand(capsys):
    assert main(["help"]) == 0

    printed = capsys.readouterr().out
    for command in ("new", "validate", "scaffold", "build", "test", "release", "write", "sprites"):
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

    `_project_command` imports `anthropic.Anthropic`, `ResponsesReferenceResearcher`,
    and the config loaders locally inside the branch, so patching the modules
    they come from (rather than names already bound in `llmz80.cli`) is what
    actually takes effect.
    """
    import anthropic

    import llmz80.studio.reference as reference_module
    import llmz80.utils.config as config_module

    monkeypatch.setattr(anthropic, "Anthropic", lambda **_: object())
    monkeypatch.setattr(config_module, "load_anthropic_api_key", lambda: "test-key")
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
    resolves `anthropic.Anthropic` and `ResponsesReferenceDesigner` through local
    imports inside the branch, so the modules they come from are patched
    rather than any name already bound in `llmz80.cli`.
    """
    import anthropic

    import llmz80.studio.reference_design as reference_design_module
    import llmz80.utils.config as config_module

    monkeypatch.setattr(anthropic, "Anthropic", lambda **_: object())
    monkeypatch.setattr(config_module, "load_anthropic_api_key", lambda: "test-key")
    monkeypatch.setattr(config_module, "load_config", lambda *_: {})
    monkeypatch.setattr(
        reference_design_module, "ResponsesReferenceDesigner", lambda *_a, **_k: designer
    )


class _FakeDesigner:
    def __init__(self, proposal):
        self._proposal = proposal

    def propose(self, project, dossier, feedback=None):
        return self._proposal


def _style_proposal():
    from llmz80.studio.planner import ProjectChange, ProjectProposal, TextValue

    return ProjectProposal(
        summary="tune the palette",
        changes=[
            ProjectChange(
                path="/presentation/style",
                operation="replace",
                value=TextValue(text="neon arcade"),
                reason="match the source",
            )
        ],
    )


# v3 had a test here, test_adapt_reports_a_proposal_apply_proposal_genuinely_
# refuses, proving a proposal could be refused by planner.apply_proposal's
# editing_status check specifically, distinctly from an ordinary schema (v3
# "solvability") violation -- it walled a collectible in on every side, which
# passed pydantic validation but failed the old solvability gate. There is no
# v4 proposal shape left that can do that: v4 dropped solvability outright
# (see editing.py's own docstring), and the one check editing_status still
# runs inside apply_proposal -- whether a screen fits its target's playfield
# -- is a strict subset of what GameProject.model_validate(document) already
# refuses a few lines earlier in that same function (planner.py's own
# docstring says as much). Anything that would trip editing_status's
# backend_error trips model_validate first, so that branch is unreachable
# through any proposal now; dropped rather than faked.


def test_adapt_reports_when_no_dossier_has_been_researched_yet(tmp_path: Path, capsys, monkeypatch):
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

    _stub_adapt_dependencies(monkeypatch, _FakeDesigner(_style_proposal()))
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

    _stub_adapt_dependencies(monkeypatch, _FakeDesigner(_style_proposal()))
    monkeypatch.setattr("builtins.input", lambda *_: "y")
    code = main(["project", "adapt", str(game_path)])

    printed = capsys.readouterr().out
    assert code == 0
    assert str(game_path) in printed
    assert game_path.read_text() != before
    assert ProjectStore(tmp_path).load(game_path).presentation.style == "neon arcade"


def test_adapt_repairs_a_refused_proposal_and_tells_the_user_it_retried(
    tmp_path: Path, capsys, monkeypatch
):
    """The live-run bug this loop exists for: a first proposal refused over a
    mechanically fixable error must not be thrown away whole. This proves the
    repair actually reaches `project adapt` end to end, and that a user
    watching the command sees why it took more than one model call."""
    from llmz80.studio.planner import ProjectChange, ProjectProposal, TextValue
    from llmz80.studio.reference import save_reference

    main(["project", "new", str(tmp_path), "Adapt Repair"])
    capsys.readouterr()
    directory = tmp_path / "adapt-repair"
    game_path = directory / "game.yml"
    save_reference(_identified_dossier("Repair Game"), directory)

    oversized_style = ProjectProposal(
        summary="paint it like the original",
        changes=[
            ProjectChange(
                path="/presentation/style",
                operation="replace",
                value=TextValue(text="x" * 100),
                reason="the dossier's visual_style ran long",
            )
        ],
    )

    class _RepairingDesigner:
        def __init__(self):
            self.calls = 0

        def propose(self, project, dossier, feedback=None):
            self.calls += 1
            return oversized_style if self.calls == 1 else _style_proposal()

    designer = _RepairingDesigner()
    _stub_adapt_dependencies(monkeypatch, designer)
    monkeypatch.setattr("builtins.input", lambda *_: "y")
    code = main(["project", "adapt", str(game_path)])

    printed = capsys.readouterr().out
    assert code == 0
    assert designer.calls == 2
    assert "Attempt 1 was refused, repairing:" in printed
    assert "80 characters" in printed
    assert ProjectStore(tmp_path).load(game_path).presentation.style == "neon arcade"


def test_reference_reports_rather_than_crashes_on_a_malformed_model_response(
    tmp_path: Path, capsys, monkeypatch
):
    """The Anthropic SDK parses the model's JSON into GameReference itself, inside
    client.messages.parse(): a response that satisfies the JSON schema but
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

    class _RaisingMessages:
        def stream(self, **_kwargs):
            # Satisfies GameReference's JSON schema field-by-field but fails
            # its cross-field model_validator -- a shape a real model
            # response could take, and exactly what the SDK's own post-parse
            # step would raise on.
            return FakeMessageStream(
                GameReference.model_validate(
                    {
                        "identified": True,
                        "confidence": "high",
                        "title": "Not Really",
                        "sources": [],
                    }
                )
            )

    class _RaisingClient:
        def __init__(self, **_kwargs):
            self.messages = _RaisingMessages()

    import anthropic

    import llmz80.utils.config as config_module

    monkeypatch.setattr(anthropic, "Anthropic", _RaisingClient)
    monkeypatch.setattr(config_module, "load_anthropic_api_key", lambda: "test-key")
    monkeypatch.setattr(config_module, "load_config", lambda *_: {})

    code = main(["project", "reference", str(game_path)])

    printed = capsys.readouterr().out
    assert code == 1
    assert "ERROR:" in printed
    assert "Traceback" not in printed


# --- project draft -----------------------------------------------------


def _stub_draft_dependencies(monkeypatch, drafter):
    """Route the `draft` command's OpenAI-backed collaborator to a fake.

    Same reasoning as `_stub_adapt_dependencies`: the branch resolves
    `anthropic.Anthropic` and `ResponsesDesignDrafter` through local imports, so
    the modules they come from are patched rather than any name already
    bound in `llmz80.cli`.

    The coherence examiner is stubbed alongside it because the stage builds
    one whenever it builds its own drafter -- a fake drafter left with a real
    examiner would reach for `.messages` on the fake client and fail there,
    which is not what these tests are about.
    """
    import anthropic

    import llmz80.studio.design_exam as design_exam_module
    import llmz80.studio.drafting as drafting_module
    import llmz80.utils.config as config_module

    monkeypatch.setattr(anthropic, "Anthropic", lambda **_: object())
    monkeypatch.setattr(config_module, "load_anthropic_api_key", lambda: "test-key")
    monkeypatch.setattr(config_module, "load_config", lambda *_: {})
    monkeypatch.setattr(drafting_module, "ResponsesDesignDrafter", lambda *_a, **_k: drafter)
    monkeypatch.setattr(
        design_exam_module, "ResponsesCoherenceExaminer", lambda *_a, **_k: _FakeExaminer()
    )


class _FakeExaminer:
    """An examiner that finds the design consistent with itself, so the CLI
    tests keep testing the command rather than the gate."""

    def examine(self, project):
        from llmz80.studio.design_exam import DesignCoherence

        return DesignCoherence(coherent=True, missing_entities=[], missing_tiles=[], quoted="")


class _FakeDrafter:
    def __init__(self, proposal):
        self._proposal = proposal

    def draft(self, project, dossier=None, feedback=None):
        return self._proposal


def _mechanics_proposal():
    from llmz80.studio.planner import ProjectChange, ProjectProposal, RowsValue

    return ProjectProposal(
        summary="state what this game does",
        changes=[
            ProjectChange(
                path="/mechanics",
                operation="replace",
                value=RowsValue(
                    rows=["el minero cava hacia abajo", "un murcielago le quita una vida"]
                ),
                reason="the brief says what this is",
            )
        ],
    )


def _drafted(tmp_path: Path, name: str) -> Path:
    main(
        ["project", "new", str(tmp_path), name, "spectrum", "un minero cava y esquiva murcielagos"]
    )
    return tmp_path / name.lower().replace(" ", "-") / "game.yml"


def test_draft_accepted_states_the_rules_and_saves_them(tmp_path: Path, capsys, monkeypatch):
    game_path = _drafted(tmp_path, "Draft Accept")
    capsys.readouterr()
    before = game_path.read_text()

    _stub_draft_dependencies(monkeypatch, _FakeDrafter(_mechanics_proposal()))
    monkeypatch.setattr("builtins.input", lambda *_: "y")
    code = main(["project", "draft", str(game_path)])

    printed = capsys.readouterr().out
    assert code == 0
    assert str(game_path) in printed
    assert game_path.read_text() != before
    assert ProjectStore(tmp_path).load(game_path).mechanics[0] == "el minero cava hacia abajo"


def test_draft_declined_leaves_game_yml_byte_for_byte_unchanged(
    tmp_path: Path, capsys, monkeypatch
):
    game_path = _drafted(tmp_path, "Draft Decline")
    capsys.readouterr()
    before = game_path.read_text()

    _stub_draft_dependencies(monkeypatch, _FakeDrafter(_mechanics_proposal()))
    monkeypatch.setattr("builtins.input", lambda *_: "n")
    code = main(["project", "draft", str(game_path)])

    printed = capsys.readouterr().out
    assert code == 0
    assert "Left unchanged." in printed
    assert game_path.read_text() == before


def test_draft_says_so_and_spends_nothing_on_a_design_that_is_already_somebodys(
    tmp_path: Path, capsys, monkeypatch
):
    """The command a person reaches for after `program` refused. Run against
    a design that already states its rules it must cost nothing and say why --
    proved by making the OpenAI client itself an error."""
    import anthropic

    game_path = _drafted(tmp_path, "Draft Stated")
    capsys.readouterr()
    store = ProjectStore(tmp_path)
    project = store.load(game_path)
    store.save(project.model_copy(update={"mechanics": ["ya lo dice"]}), game_path.parent)

    def _refuse_to_be_built(**_kwargs):
        raise AssertionError("the OpenAI client was built for a design nobody had to draft")

    monkeypatch.setattr(anthropic, "Anthropic", _refuse_to_be_built)
    code = main(["project", "draft", str(game_path)])

    printed = capsys.readouterr().out
    assert code == 0
    assert "nothing to draft" in printed
    assert "already states what it does" in printed


def test_a_drafter_that_states_nothing_is_reported_as_an_error_not_a_traceback(
    tmp_path: Path, capsys, monkeypatch
):
    """`DraftRefused` is a `ValueError`, so the handler `adapt` already has
    reports it -- no second one was added for it. This is what proves that,
    rather than the claim that it subclasses."""
    from llmz80.studio.planner import ProjectProposal

    game_path = _drafted(tmp_path, "Draft Refused")
    capsys.readouterr()

    _stub_draft_dependencies(
        monkeypatch,
        _FakeDrafter(ProjectProposal(summary="nothing at all", changes=[])),
    )
    code = main(["project", "draft", str(game_path)])

    printed = capsys.readouterr().out
    assert code == 1
    assert "ERROR:" in printed
    assert "mechanics" in printed
    assert "Traceback" not in printed


# --- project sprites ---------------------------------------------------


def _sprite_sheet_image():
    """A raw sheet with one solid, non-touching blob per column, on a white
    background -- what `SpriteArtist.draw_frames` (see `sprite_artist.py`
    and its own test suite's `_four_pose_sheet`) needs to survive
    `image_utils._clean_image`/`_scale_image` and come back as four distinct
    16x16 frames rather than three blank ones.

    Each blob is an ellipse, not a filled rectangle: `sprite_artist._judge_frames`
    now refuses any frame that packs to 0 or 256 of 256 opaque pixels (a real
    run showed that is exactly what a broken generation looks like -- see
    `sprite_artist.py`'s module docstring), and a filled rectangle crops, via
    `image_utils._clean_image`'s tight bounding-box crop, to a frame with no
    background left inside it at all -- a false positive for that same
    check. An ellipse leaves its own bounding box's corners as real
    background, the way a real character's silhouette always does.
    """
    from PIL import Image, ImageDraw

    column_width = 40
    width = column_width * 4
    height = 40
    sheet = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    colours = [(255, 0, 0, 255), (0, 128, 0, 255), (0, 0, 255, 255), (255, 165, 0, 255)]
    for index, colour in enumerate(colours):
        offset = index * column_width
        draw.ellipse((offset + 5, 5, offset + column_width - 5, height - 5), fill=colour)
    return sheet


class _FakeImageGenerator:
    """Stands in for the client `ClaudeGridSheetSource` draws through:
    returns a fixed, valid grid, makes no network call, and remembers how
    many times it was asked to draw.

    The grid is a filled left half -- neither blank nor solid, so it passes
    `sprite_grid.grid_errors` and `sprite_artist._judge_frames` alike --
    drawn in pen 0, which every target has.
    """

    def __init__(self, **_kwargs):
        self.calls = 0
        self.messages = self

    def stream(self, **_kwargs):
        from llmz80.studio.sprite_grid import TRANSPARENT, SpriteFrameGrid, SpriteSheetGrid
        from llmz80.studio.spriting import SPRITE_SIZE

        self.calls += 1
        half = "0" * (SPRITE_SIZE // 2) + TRANSPARENT * (SPRITE_SIZE // 2)
        grid = SpriteSheetGrid(
            frames=[SpriteFrameGrid(rows=[half] * SPRITE_SIZE) for _ in range(4)]
        )
        return FakeMessageStream(type("Response", (), {"parsed_output": grid})())


def _stub_sprites_dependencies(monkeypatch, generator):
    """Route the `sprites` command's model-backed collaborators to fakes.

    Same reasoning as `_stub_reference_dependencies`: `pipeline.sprites`
    resolves `anthropic.Anthropic` through a local import inside the branch,
    so the module it comes from is patched rather than any name already
    bound in `llmz80.cli`.
    """
    import anthropic

    import llmz80.utils.config as config_module

    monkeypatch.setattr(anthropic, "Anthropic", lambda **_: generator)
    monkeypatch.setattr(config_module, "load_anthropic_api_key", lambda: "test-key")
    monkeypatch.setattr(config_module, "load_config", lambda *_: {})


def test_sprites_draws_and_registers_missing_art(tmp_path: Path, capsys, monkeypatch):
    main(["project", "new", str(tmp_path), "Sprited"])
    capsys.readouterr()
    game_path = tmp_path / "sprited" / "game.yml"

    generator = _FakeImageGenerator()
    _stub_sprites_dependencies(monkeypatch, generator)

    code = main(["project", "sprites", str(game_path)])

    printed = capsys.readouterr().out
    assert code == 0
    project = ProjectStore(tmp_path).load(game_path)
    entity_sprites = sorted({entity.sprite for entity in project.entities})
    assert generator.calls == len(entity_sprites)
    registered = {asset.id: asset for asset in project.assets if asset.kind == "sprite"}
    assert sorted(registered) == entity_sprites
    for asset in registered.values():
        assert asset.frames == 4
        assert (tmp_path / "sprited" / asset.source).is_file()
        assert asset.id in printed


def test_sprites_declining_an_overwrite_leaves_existing_art_untouched(
    tmp_path: Path, capsys, monkeypatch
):
    main(["project", "new", str(tmp_path), "Sprite Decline"])
    capsys.readouterr()
    directory = tmp_path / "sprite-decline"
    game_path = directory / "game.yml"

    _stub_sprites_dependencies(monkeypatch, _FakeImageGenerator())
    assert main(["project", "sprites", str(game_path)]) == 0
    capsys.readouterr()
    before_game = game_path.read_text()
    before_project = ProjectStore(tmp_path).load(game_path)
    before_files = {
        asset.source: (directory / asset.source).read_bytes()
        for asset in before_project.assets
        if asset.kind == "sprite"
    }
    assert before_files, "the first run should have drawn some art to protect"

    second_generator = _FakeImageGenerator()
    _stub_sprites_dependencies(monkeypatch, second_generator)
    monkeypatch.setattr("builtins.input", lambda *_: "n")
    code = main(["project", "sprites", str(game_path)])

    printed = capsys.readouterr().out
    assert code == 0
    assert "Left unchanged." in printed
    assert second_generator.calls == 0
    assert game_path.read_text() == before_game
    for source, contents in before_files.items():
        assert (directory / source).read_bytes() == contents


def test_sprites_accepting_an_overwrite_redraws_the_existing_art(
    tmp_path: Path, capsys, monkeypatch
):
    main(["project", "new", str(tmp_path), "Sprite Accept"])
    capsys.readouterr()
    directory = tmp_path / "sprite-accept"
    game_path = directory / "game.yml"

    _stub_sprites_dependencies(monkeypatch, _FakeImageGenerator())
    assert main(["project", "sprites", str(game_path)]) == 0
    capsys.readouterr()
    before_project = ProjectStore(tmp_path).load(game_path)
    entity_sprites = sorted({entity.sprite for entity in before_project.entities})

    second_generator = _FakeImageGenerator()
    _stub_sprites_dependencies(monkeypatch, second_generator)
    monkeypatch.setattr("builtins.input", lambda *_: "y")
    code = main(["project", "sprites", str(game_path)])

    printed = capsys.readouterr().out
    assert code == 0
    assert second_generator.calls == len(entity_sprites)
    after_project = ProjectStore(tmp_path).load(game_path)
    registered = sorted(a.id for a in after_project.assets if a.kind == "sprite")
    assert registered == entity_sprites
    assert "Sprite art already exists for:" in printed


def test_sprites_prints_the_money_warning_before_constructing_a_generator(
    tmp_path: Path, capsys, monkeypatch
):
    main(["project", "new", str(tmp_path), "Sprite Warn"])
    capsys.readouterr()
    game_path = tmp_path / "sprite-warn" / "game.yml"

    class _StoppedBeforeSpending(Exception):
        pass

    printed_before_construction = []

    class _RefusingClient:
        def __init__(self, **_kwargs):
            printed_before_construction.append(capsys.readouterr().out)
            raise _StoppedBeforeSpending()

    import anthropic

    import llmz80.utils.config as config_module

    monkeypatch.setattr(anthropic, "Anthropic", _RefusingClient)
    monkeypatch.setattr(config_module, "load_anthropic_api_key", lambda: "test-key")
    monkeypatch.setattr(config_module, "load_config", lambda *_: {})

    import pytest

    with pytest.raises(_StoppedBeforeSpending):
        main(["project", "sprites", str(game_path)])

    assert printed_before_construction, "the client was never constructed"
    assert "Anthropic API" in printed_before_construction[0]


def test_write_reports_a_refused_design_instead_of_tracebacking(tmp_path: Path, capsys):
    """A design the gate refuses stops here as a printed verdict and exit 1.
    No API key is read and no OpenAI call is made: `pipeline.write` refuses
    before it builds a writer, which is the point of refusing there."""
    main(["project", "new", str(tmp_path), "Refused", "spectrum", "un juego como el zampabolas"])
    capsys.readouterr()

    code = main(["project", "write", str(tmp_path / "refused" / "game.yml")])

    printed = capsys.readouterr().out
    assert code == 1
    assert "not ready to be written" in printed
    assert "states no mechanics" in printed
