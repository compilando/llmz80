"""`llmz80 make`, judged as an orchestrator: the order, the skip, and the stop.

Not one model call and not one emulator is started here. Four of the six
stages spend money and one drives a real emulator, so `make_game` takes them
as a parameter -- the same reason `generator.write_program` takes its `verify`
and `writer` -- and everything below runs against stages that only record
that they were asked.

The one stage that is real is `create`: it is free, it writes the project the
diary lives inside, and faking it would leave the diary with nowhere to go.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from llmz80.studio.journal import FILENAME
from llmz80.studio.make import MakeResult, ServiceStages, StageRefused, make_game, title_from
from llmz80.studio.models import TargetPlatform
from llmz80.studio.reference import GameReference, ReferenceSource
from llmz80.studio.services import StudioService


def _dossier(identified: bool = True) -> GameReference:
    if not identified:
        return GameReference(identified=False, confidence="low")
    return GameReference(
        identified=True,
        confidence="high",
        title="Manic Miner",
        publisher="Bug-Byte",
        year=1983,
        sources=[
            ReferenceSource(
                url="https://example.com/manic-miner",
                title="Manic Miner at World of Spectrum",
                retrieved_at=datetime(1983, 1, 1, tzinfo=timezone.utc),
            )
        ],
    )


class _FakeStages:
    """Records the order it was asked in, and can be told to refuse at one stage.

    `create` is delegated to the real `ServiceStages`, so the project, its
    `game.yml` and the directory the diary is written into all exist exactly
    as they would in anger.
    """

    def __init__(
        self,
        workspace: Path,
        *,
        dossier: GameReference | None = None,
        refuse_at: str = "",
        accepted: bool = True,
        quality_pass: bool | None = True,
        publishes: bool = True,
    ) -> None:
        self.real = ServiceStages(StudioService.at(workspace))
        self.calls: list[str] = []
        self.said: list[str] = []
        self.dossier = dossier if dossier is not None else _dossier()
        self.refuse_at = refuse_at
        self.accepted = accepted
        self.quality_pass = quality_pass
        self.publishes = publishes

    def _record(self, name: str) -> None:
        self.calls.append(name)
        if self.refuse_at == name:
            raise StageRefused(f"{name} refused on purpose")

    def create(self, title, brief, platform):
        self._record("create")
        return self.real.create(title, brief, platform)

    def research(self, project, directory, say):
        self._record("research")
        say("searching the web")
        return self.dossier

    def draft(self, project, directory, dossier, say):
        """States rules the way the real stage does, and saves them, so a test
        can read the design `programa` would have refused off disk."""
        self._record("draft")
        updated = project.model_copy(
            update={"mechanics": ["el minero salta entre cornisas", "caer desde alto le mata"]}
        )
        self.real.service.save_project(updated, directory)
        return updated

    def adapt(self, project, directory, dossier, say):
        self._record("adapt")
        return project

    def sprites(self, project, directory, dossier, say):
        self._record("sprites")
        say("hero: 4 poses packed")
        return []

    def write(self, project, directory, dossier, say):
        self._record("write")
        return {
            "accepted": self.accepted,
            "attempts": [{"number": 1}],
            "last_error": "the compiler said no",
        }

    def test(self, project, directory, say):
        self._record("test")
        # The artifact is what the last line of a run points at, so a stage
        # standing in for the real toolchain has to leave one where the real
        # one would.
        artifact = directory / "build" / "output.tap"
        if self.publishes:
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_bytes(b"TAP")
        return {"quality_pass": self.quality_pass, "acceptance": {"failures": []}}


def _run(tmp_path: Path, printed: list[str], **kwargs) -> tuple[MakeResult, _FakeStages]:
    stages = _FakeStages(tmp_path, **kwargs)
    result = make_game(
        "un minero cruza cornisas de piedra saltando entre ellas",
        workspace=tmp_path,
        stages=stages,
        out=printed.append,
    )
    return result, stages


def test_the_whole_sequence_runs_in_order(tmp_path: Path):
    printed: list[str] = []

    result, stages = _run(tmp_path, printed)

    assert stages.calls == ["create", "research", "draft", "adapt", "sprites", "write", "test"]
    assert result.ok
    assert result.project_dir is not None and (result.project_dir / "game.yml").is_file()


def test_the_money_is_announced_before_anything_is_spent(tmp_path: Path):
    """Announcing is not asking -- but it has to come before the first stage."""
    printed: list[str] = []

    _run(tmp_path, printed)

    assert "Anthropic API in 5 stages" in printed[0]
    assert "referencia" in printed[0] and "programa" in printed[0]


def test_an_unidentified_game_skips_the_adaptation_and_carries_on(tmp_path: Path):
    printed: list[str] = []

    result, stages = _run(tmp_path, printed, dossier=_dossier(identified=False))

    assert stages.calls == ["create", "research", "draft", "sprites", "write", "test"]
    assert result.ok
    assert any("SKIP" in line and "diseño" in line for line in printed)


def test_the_order_drafts_before_it_adapts():
    """Drafting decides what the game is; adapting decides what it looks like.
    A dossier can only dress a design that already states something."""
    from llmz80.studio.make import PAID_STAGES

    assert PAID_STAGES.index("redacción") < PAID_STAGES.index("diseño")
    assert PAID_STAGES.index("referencia") < PAID_STAGES.index("redacción")


def test_an_unidentified_game_no_longer_dead_ends_the_order(tmp_path: Path):
    """Research finding nothing used to mean `diseño` was skipped, `mechanics`
    stayed empty, and `programa` refused three stages later while the order
    warned about it here. Drafting runs from the brief alone, so the design
    that reaches `programa` states its rules and the gate that used to refuse
    it passes -- which is why the warning that named that road is gone.
    """
    from llmz80.studio.quality import design_quality_report

    printed: list[str] = []

    result, stages = _run(tmp_path, printed, dossier=_dossier(identified=False))

    assert result.ok
    assert stages.calls == ["create", "research", "draft", "sprites", "write", "test"]
    assert not [line for line in printed if "WARN" in line]
    assert result.project_dir is not None
    saved = StudioService.at(tmp_path).open_project(result.project_dir)
    assert saved.mechanics
    assert design_quality_report(saved)["quality_pass"]


def test_a_design_gate_refusal_names_the_file_to_edit_not_a_command_that_cannot_work(
    tmp_path: Path,
):
    """The retry hint is `llmz80 project write PATH` for every failure a second
    run could go differently on. The design gate is not one of those: nothing
    in the CLI or the interface writes mechanics into a design, so that
    command refuses identically forever and `llmz80 project adapt` refuses too
    (no game was identified). The hint has to name the file and the field.

    `write` here is the real `pipeline.write` over the real project, so the
    refusal is the gate's own and no writer is ever built or called.
    """
    from llmz80.studio import pipeline

    class _RealDesignGate(_FakeStages):
        def draft(self, project, directory, dossier, say):
            # The one road left to `programa` with no mechanics: a drafting
            # stage that came back with nothing. The real one raises instead,
            # which stops the order two stages earlier -- so this is the gate
            # being driven deliberately, not a route `make` can take.
            self._record("draft")
            return project

        def write(self, project, directory, dossier, say):
            self._record("write")
            return pipeline.write(self.real.service, project, directory, _NeverCalled())

    class _NeverCalled:
        def write(self, project, feedback=None):
            raise AssertionError("the writer must not be asked")

    printed: list[str] = []
    stages = _RealDesignGate(tmp_path, dossier=_dossier(identified=False))
    result = make_game(
        "un minero cruza cornisas de piedra saltando entre ellas",
        workspace=tmp_path,
        stages=stages,
        out=printed.append,
    )

    assert result.failed == "programa"
    assert result.project_dir is not None
    hint = printed[-1]
    assert "llmz80 project draft" in hint
    assert str(result.project_dir / "game.yml") in hint
    assert "mechanics" in hint
    assert not hint.startswith("Nothing is lost")


def test_every_other_failure_still_says_to_retry_the_stage(tmp_path: Path):
    """A stage that could go differently on a second run -- here the art -- is
    still answered by the command that redoes it."""
    printed: list[str] = []

    result, _stages = _run(tmp_path, printed, refuse_at="sprites")

    assert result.failed == "sprites"
    assert printed[-1] == (
        f"Nothing is lost: retry this stage with `llmz80 project sprites {result.project_dir}`."
    )


def test_a_failed_stage_stops_the_order_and_says_which(tmp_path: Path):
    printed: list[str] = []

    result, stages = _run(tmp_path, printed, refuse_at="sprites")

    assert stages.calls == ["create", "research", "draft", "adapt", "sprites"]
    assert not result.ok
    assert result.failed == "sprites"
    assert "sprites refused on purpose" in result.error
    assert any(line.startswith("STOPPED at 4 sprites:") for line in printed)


def test_a_program_the_compiler_never_accepted_stops_the_order(tmp_path: Path):
    """The refusal a fake writer cannot express by raising: the loop ran to the
    end of its attempts and none of them built."""
    printed: list[str] = []

    result, stages = _run(tmp_path, printed, accepted=False)

    assert "test" not in stages.calls
    assert result.failed == "programa"
    assert "the compiler said no" in result.error


def test_gates_that_watched_and_refused_stop_the_order(tmp_path: Path):
    printed: list[str] = []

    result, _stages = _run(tmp_path, printed, quality_pass=False)

    assert result.failed == "gates"
    assert "the gates refused it" in result.error


def test_gates_that_abstain_are_not_a_refusal(tmp_path: Path):
    """The CPC has no memory probe adapter, so its gates report `None`. Reading
    that as a failure would refuse every CPC game that built and ran."""
    printed: list[str] = []

    result, _stages = _run(tmp_path, printed, quality_pass=None)

    assert result.ok
    assert any("abstained" in line for line in printed)


def test_the_diary_records_every_stage_and_survives_the_run(tmp_path: Path):
    printed: list[str] = []

    result, _stages = _run(tmp_path, printed)

    assert result.project_dir is not None
    diary = (result.project_dir / FILENAME).read_text(encoding="utf-8")
    # The kind column is eight characters wide (`journal.Kind`), which is what
    # makes the left margin of a diary scannable; these are the lines as they
    # are actually written, padding included.
    for stage in (
        "1 referencia",
        "2 redacción",
        "3 diseño",
        "4 sprites",
        "5 programa",
        "6 gates",
    ):
        assert f"START   {stage}" in diary
        assert f"END     {stage}" in diary
    assert "OPEN" in diary
    # And what a stage narrated while it ran, not only its verdict.
    assert "hero: 4 poses packed" in diary


def test_what_the_diary_writes_is_what_the_screen_shows(tmp_path: Path):
    """`Journal` returns the line it wrote so the two cannot diverge; this is
    the assertion that keeps `make` using it that way."""
    printed: list[str] = []

    result, _stages = _run(tmp_path, printed)

    assert result.project_dir is not None
    diary = (result.project_dir / FILENAME).read_text(encoding="utf-8").splitlines()
    assert [line for line in printed if line in diary] == diary


def test_a_failed_run_still_leaves_the_diary_and_points_at_it(tmp_path: Path):
    printed: list[str] = []

    result, _stages = _run(tmp_path, printed, refuse_at="write")

    assert result.project_dir is not None
    assert (result.project_dir / FILENAME).is_file()
    assert any(str(result.project_dir / FILENAME) in line for line in printed)
    # And the way out: the stage that failed, over the project that already
    # exists -- not the whole order again, paid for twice.
    assert any(f"llmz80 project write {result.project_dir}" in line for line in printed)


def test_a_run_that_publishes_no_artifact_is_not_reported_as_a_game(tmp_path: Path):
    """The gates can only refuse what they watched; a missing tape is a
    different failure, and printing its path would be the one lie this
    command must not tell."""
    printed: list[str] = []

    result, _stages = _run(tmp_path, printed, publishes=False)

    assert result.failed == "gates"
    assert "no artifact was published" in result.error
    assert result.artifact is None


def test_it_ends_with_the_path_of_the_game_and_the_order_that_plays_it(tmp_path: Path):
    """A path says where the game is; it does not say how to play it, and
    somebody who has waited out four paid stages should not have to look that
    up."""
    printed: list[str] = []

    result, _stages = _run(tmp_path, printed)

    assert result.project_dir is not None
    artifact = result.project_dir / "build" / "output.tap"
    assert printed[-2] == str(artifact)
    assert printed[-1] == f"Play it: llmz80 play {result.project_dir}"
    assert result.artifact == artifact


def test_the_cpc_gets_a_disk_image_and_its_own_video_mode(tmp_path: Path):
    stages = _FakeStages(tmp_path)
    printed: list[str] = []

    result = make_game(
        "cuatro fantasmas te persiguen por un laberinto",
        platform=TargetPlatform.AMSTRAD_CPC,
        workspace=tmp_path,
        stages=stages,
        out=printed.append,
    )

    project = StudioService.at(tmp_path).open_project(result.project_dir)
    assert project.target.platform is TargetPlatform.AMSTRAD_CPC
    assert printed[-1].endswith("output.dsk")


def test_the_idea_is_kept_whole_as_the_brief(tmp_path: Path):
    """The title is cut to fit `Metadata.title`; the idea itself is not."""
    idea = "un minero cruza cornisas de piedra saltando entre ellas"
    stages = _FakeStages(tmp_path)

    result = make_game(idea, workspace=tmp_path, stages=stages, out=lambda _: None)

    project = StudioService.at(tmp_path).open_project(result.project_dir)
    assert project.metadata.brief == idea
    assert project.metadata.title == "un minero cruza cornisas de"


def test_an_empty_idea_is_refused_before_a_project_exists(tmp_path: Path):
    printed: list[str] = []

    result = make_game("   ", workspace=tmp_path, out=printed.append)

    assert not result.ok
    assert result.project_dir is None
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    "idea, expected",
    [
        ("a miner", "a miner"),
        ("un minero cruza cornisas de piedra", "un minero cruza cornisas de"),
        ("supercalifragilisticoespialidoso jump", "supercalifragilisticoespiali"),
        ("  spaced   out  words ", "spaced out words"),
    ],
)
def test_a_title_is_cut_where_a_word_ends(idea: str, expected: str):
    assert title_from(idea) == expected
    assert len(title_from(idea)) <= 32


def test_the_same_idea_twice_makes_a_second_game_rather_than_refusing(tmp_path: Path):
    """A person retyping an idea is asking for another attempt at it, not
    reporting a mistake; `ProjectStore.create` refuses to overwrite, so the
    second run takes the next free name."""
    first = make_game(
        "un minero", workspace=tmp_path, stages=_FakeStages(tmp_path), out=lambda _: None
    )
    second = make_game(
        "un minero", workspace=tmp_path, stages=_FakeStages(tmp_path), out=lambda _: None
    )

    assert first.ok and second.ok
    assert first.project_dir != second.project_dir
    assert second.project_dir is not None and second.project_dir.name == "un-minero-2"


class _ExplodingStages(_FakeStages):
    def research(self, project, directory, say):
        self.calls.append("research")
        raise RuntimeError("connection reset by peer")


def test_a_stage_that_crashes_is_reported_like_one_that_refused(tmp_path: Path):
    """A dropped connection and a compiler that said no stop the order the same
    way: the difference matters to the person reading the message, not here."""
    printed: list[str] = []
    stages = _ExplodingStages(tmp_path)

    result = make_game("un minero", workspace=tmp_path, stages=stages, out=printed.append)

    assert stages.calls == ["create", "research"]
    assert result.failed == "referencia"
    assert "connection reset by peer" in result.error
    assert any("ERROR" in line and "connection reset" in line for line in printed)


# --- the command line --------------------------------------------------------


def _capture_make(monkeypatch) -> dict[str, Any]:
    """Stop at the boundary: what `llmz80 make` passed on, without running it."""
    seen: dict[str, Any] = {}
    import llmz80.studio.make as make_module

    def fake(idea, *, platform, workspace, **_kwargs):
        seen.update(idea=idea, platform=platform, workspace=workspace)
        return MakeResult(project_dir=workspace, artifact=workspace / "output.tap")

    monkeypatch.setattr(make_module, "make_game", fake)
    return seen


def test_the_command_defaults_to_the_spectrum_and_the_studio_workspace(monkeypatch):
    from llmz80.cli import main

    seen = _capture_make(monkeypatch)

    assert main(["make", "un minero"]) == 0
    assert seen["idea"] == "un minero"
    assert seen["platform"] is TargetPlatform.SPECTRUM
    assert seen["workspace"] == Path("studio-projects").expanduser().resolve()


def test_cpc_changes_the_machine_and_workspace_changes_the_place(monkeypatch, tmp_path: Path):
    from llmz80.cli import main

    seen = _capture_make(monkeypatch)

    assert main(["make", "un laberinto", "--cpc", "--workspace", str(tmp_path)]) == 0
    assert seen["platform"] is TargetPlatform.AMSTRAD_CPC
    assert seen["workspace"] == tmp_path


def test_workspace_also_takes_an_equals_sign(monkeypatch, tmp_path: Path):
    from llmz80.cli import main

    seen = _capture_make(monkeypatch)

    main(["make", "un laberinto", f"--workspace={tmp_path}"])
    assert seen["workspace"] == tmp_path


def test_an_unquoted_idea_is_refused_rather_than_guessed_at(capsys):
    from llmz80.cli import main

    code = main(["make", "un", "minero"])

    assert code == 2
    assert "one quoted argument" in capsys.readouterr().out


def test_an_unknown_option_is_refused(capsys):
    from llmz80.cli import main

    assert main(["make", "una idea", "--turbo"]) == 2
    assert "unknown option --turbo" in capsys.readouterr().out


def test_a_failed_run_exits_non_zero(monkeypatch):
    import llmz80.studio.make as make_module
    from llmz80.cli import main

    monkeypatch.setattr(
        make_module,
        "make_game",
        lambda *_a, **_k: MakeResult(project_dir=None, failed="programa", error="no"),
    )

    assert main(["make", "una idea"]) == 1


def test_the_help_leads_with_the_one_command(capsys):
    from llmz80.cli import main

    main(["help"])

    printed = capsys.readouterr().out
    assert "llmz80 make" in printed
    assert "--cpc" in printed


# --- and then playing it ----------------------------------------------------


def _capture_play(monkeypatch) -> list[Path]:
    """Stop at the boundary again: which game would have been played."""
    played: list[Path] = []
    import llmz80.studio.play as play_module

    def fake(target, **_kwargs):
        played.append(Path(target))
        return 0

    monkeypatch.setattr(play_module, "play", fake)
    return played


def test_play_starts_the_game_at_the_path_it_was_given(monkeypatch, tmp_path: Path):
    from llmz80.cli import main

    played = _capture_play(monkeypatch)

    assert main(["play", str(tmp_path)]) == 0
    assert played == [tmp_path]


def test_play_without_a_path_says_what_it_needs(monkeypatch, capsys):
    from llmz80.cli import main

    played = _capture_play(monkeypatch)

    assert main(["play"]) == 2
    assert "say which game to play" in capsys.readouterr().out
    assert played == []


def test_make_can_play_the_game_it_has_just_built(monkeypatch, tmp_path: Path):
    """Fifteen minutes of waiting should not end with another order to type."""
    from llmz80.cli import main

    seen = _capture_make(monkeypatch)
    played = _capture_play(monkeypatch)

    assert main(["make", "un minero", "--workspace", str(tmp_path), "--play"]) == 0
    assert seen["idea"] == "un minero"
    assert played == [tmp_path / "output.tap"]


def test_make_without_the_flag_plays_nothing(monkeypatch, tmp_path: Path):
    from llmz80.cli import main

    _capture_make(monkeypatch)
    played = _capture_play(monkeypatch)

    main(["make", "un minero", "--workspace", str(tmp_path)])

    assert played == []


def test_a_run_that_stopped_is_not_played(monkeypatch, tmp_path: Path):
    """There is nothing to play: the order stopped before an artifact
    existed, and `--play` is not a reason to pretend otherwise."""
    import llmz80.studio.make as make_module
    from llmz80.cli import main

    monkeypatch.setattr(
        make_module,
        "make_game",
        lambda *_a, **_k: MakeResult(project_dir=tmp_path, failed="programa", error="no"),
    )
    played = _capture_play(monkeypatch)

    assert main(["make", "una idea", "--play"]) == 1
    assert played == []


def test_the_help_names_the_order_that_plays_a_game(capsys):
    from llmz80.cli import main

    main(["help"])

    printed = capsys.readouterr().out
    assert "llmz80 play" in printed
    assert "--play" in printed
