"""One order: an idea goes in, a game comes out.

Every stage this runs already exists as a subcommand of `llmz80 project`, and
until now getting a game meant typing six of them in the right order and
answering the questions each one asks along the way. This is the same six
stages with nobody at the keyboard: it creates the project, researches the
real game the idea resembles, adapts the design to it, draws the missing art,
writes the program and repairs it against the compiler, then builds it and
watches it run. It asks nothing -- the order either runs to the end or stops
at the stage that failed and says so.

It owns no pipeline logic of its own. Each stage is one call into
`pipeline.py`, the same call `llmz80 project <stage>` makes, so a fix to what
a stage *does* lands in one place and both callers get it. What this
module adds is the three things a chain of commands never had: the order, a
diary written while it happens rather than a report handed over at the end,
and the rule for what a failure means -- which is "stop", because a program
that does not build is not a game and the next stage would only be spending
money on top of a broken one.

Stages are injected (`Stages`, `ServiceStages`) for the same reason
`generator.write_program` takes its `verify` and `writer` as parameters: four
of the six spend money on the OpenAI API and one drives a real emulator, so
the only way to test the *order* -- and what happens when one of them refuses
-- is to be able to run it against stages that do neither.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Protocol

from . import pipeline, wizard
from .journal import FILENAME as JOURNAL_FILENAME, Journal
from .models import AssetSpec, GameProject, TargetPlatform
from .play import how_to_play
from .reference import GameReference
from .services import StudioService

#: Told what is happening while it happens: the same callable `services.py`
#: takes as `on_progress`, so a stage's own commentary reaches the diary
#: without this module inventing a second way to say things.
Say = Callable[[str], None]

#: `Metadata.title` is capped at 32 characters, and a second run of the same
#: idea needs room to become "… 2" without the suffix being truncated away
#: (which would loop forever looking for a free slug). 28 leaves that room.
TITLE_LIMIT = 28

#: How many same-titled projects a workspace will hold before this gives up.
#: A person who has asked for the same idea ninety-nine times has a problem
#: this command cannot solve.
MAX_SAME_TITLE = 99

#: What is said before anything is spent. Announcing is not asking: the order
#: goes ahead, but nobody should discover afterwards that it made four rounds
#: of paid API calls. `diseño` costs money *here* (it adapts the design to the
#: researched game) even though `wizard` marks it free -- there the stage is a
#: person editing a map by hand.
PAID_STAGES = ("referencia", "diseño", "sprites", "programa")

#: The `llmz80 project` subcommand that redoes each stage, for the one line a
#: stopped run owes the person reading it: everything before the failure is on
#: disk and stays there, so the way out is to retry that stage over the same
#: project, not to run the whole order again and pay for all of it twice.
RESUMES = {
    "referencia": "reference",
    "diseño": "adapt",
    "sprites": "sprites",
    "programa": "write",
    "gates": "test",
}


class Stages(Protocol):
    """The six pieces of work `make_game` puts in order.

    Each one is whole: it does its own saving, and returns what the diary
    needs to describe it. `say` is how a stage narrates itself while it runs
    -- the long ones (sprites, program, gates) forward it straight into the
    service as `on_progress`.
    """

    def create(
        self, title: str, brief: str, platform: TargetPlatform
    ) -> tuple[GameProject, Path]: ...

    def research(self, project: GameProject, directory: Path, say: Say) -> GameReference: ...

    def adapt(
        self, project: GameProject, directory: Path, dossier: GameReference, say: Say
    ) -> GameProject: ...

    def sprites(
        self, project: GameProject, directory: Path, dossier: GameReference | None, say: Say
    ) -> list[AssetSpec]: ...

    def write(
        self, project: GameProject, directory: Path, dossier: GameReference | None, say: Say
    ) -> dict[str, Any]: ...

    def test(self, project: GameProject, directory: Path, say: Say) -> dict[str, Any]: ...


@dataclass(frozen=True)
class MakeResult:
    """Where the game landed, or where the order stopped."""

    project_dir: Path | None
    #: The tape or disk image, once the gates have seen it run. `None` while
    #: no build has produced one.
    artifact: Path | None = None
    #: The stage id (`referencia`, `programa`, …) that stopped the order, or
    #: "" when nothing did. Deliberately the id `wizard` and the diary use, so
    #: "it stopped at programa" means the same thing in the log, on screen and
    #: in a bug report.
    failed: str = ""
    error: str = ""

    @property
    def ok(self) -> bool:
        return not self.failed


class _Stopped(Exception):
    """A stage refused or raised, so nothing after it runs."""

    def __init__(self, step: str, reason: str, cause: BaseException | None = None) -> None:
        super().__init__(reason)
        self.step = step
        self.reason = reason
        #: What the stage actually raised, kept rather than flattened into
        #: `reason`, because the last line this command prints is advice and
        #: the right advice depends on the kind of failure, not on its words.
        #: See `_retry_hint`.
        self.cause = cause


class StageRefused(Exception):
    """A stage that ran to the end and produced something unacceptable.

    Distinct from the exceptions a stage raises by accident (a dropped
    connection, a missing toolchain) only in what it reads like: this is the
    program that never built, the gates that watched and refused. Both stop
    the order in the same way -- the difference matters to the person reading
    the message, not to the control flow.
    """


@dataclass
class _Diary:
    """Writes each stage into `studio.log` and onto the screen at once.

    Both come from `Journal`, which returns the very line it wrote, so the
    file and the terminal cannot start telling different stories -- the whole
    reason `journal.py` returns its lines instead of just writing them.
    """

    journal: Journal
    out: Callable[[str], None]

    def say(self, text: str) -> None:
        self.out(self.journal.note(text))

    def stage(self, step: wizard.Step, label: str, work: Callable[[], tuple[Any, str]]) -> Any:
        """Run one stage between a START and an END line, and stop the order
        if it fails.

        The heading is `"{number} {name} — {label}"`: the stage's number and
        its id, never its label, so a diary can be searched a year later and
        `4 programa` goes on meaning the same thing whatever the interface
        watching it happens to call that stage.
        """
        token = self.journal.start(f"{step.number} {step.name} — {label}")
        self.out(token.line)
        try:
            value, summary = work()
        except Exception as exc:
            self.out(self.journal.finish(token, ok=False))
            self.out(self.journal.write("ERROR", f"{step.name}: {exc}"))
            raise _Stopped(step.name, str(exc), exc) from exc
        self.out(self.journal.finish(token, ok=True, text=summary))
        return value

    def skip(self, step: wizard.Step, why: str) -> None:
        self.out(self.journal.write("SKIP", f"{step.number} {step.name} — {why}"))

    def warn(self, text: str) -> None:
        """Something that is not a failure yet and will become one."""
        self.out(self.journal.write("WARN", text))


@dataclass
class ServiceStages:
    """The real six: `pipeline`'s stages, under the names this order calls them.

    Nothing but an adapter, and deliberately: what a stage *does* lives in
    `pipeline.py`, which `llmz80 project ...` calls too, so a fix to a stage
    reaches both. What is left here is this order's own two decisions -- that
    a taken name becomes the next number rather than a refusal, and that
    nothing is ever asked (no `confirm` is passed, which is what tells
    `pipeline` to keep existing work rather than destroy it unattended).
    """

    service: StudioService

    def create(self, title: str, brief: str, platform: TargetPlatform) -> tuple[GameProject, Path]:
        """Start the project, giving it a directory nothing else is using.

        `ProjectStore.create` refuses to overwrite an existing project, and a
        person who types the same idea twice is usually asking for another
        attempt at it (the models are not deterministic), not reporting a
        mistake. So a taken slug becomes "… 2", "… 3": two runs of one idea
        leave two games side by side rather than one refusal.
        """
        for attempt in range(1, MAX_SAME_TITLE + 1):
            candidate = title if attempt == 1 else f"{title} {attempt}"
            try:
                return pipeline.create(self.service, candidate, platform, brief)
            except FileExistsError:
                continue
        raise StageRefused(
            f"the workspace already holds {MAX_SAME_TITLE} projects called {title!r}; "
            "give the idea different words, or point --workspace somewhere else"
        )

    def research(self, project: GameProject, directory: Path, say: Say) -> GameReference:
        return pipeline.research(self.service, project, directory, say=say)

    def adapt(
        self, project: GameProject, directory: Path, dossier: GameReference, say: Say
    ) -> GameProject:
        """Adapt the design to the researched game and save it.

        No `confirm`, unlike `llmz80 project adapt`: the proposal has already
        been validated through `apply_proposal`, and there is nobody at the
        keyboard to read a diff. The diff is not lost -- `game.yml`'s previous
        revision is kept by `ProjectStore.save`, as it is for every save.
        """
        return pipeline.adapt(self.service, project, directory, dossier=dossier, say=say)

    def sprites(
        self, project: GameProject, directory: Path, dossier: GameReference | None, say: Say
    ) -> list[AssetSpec]:
        return pipeline.sprites(self.service, project, directory, dossier=dossier, say=say)

    def write(
        self, project: GameProject, directory: Path, dossier: GameReference | None, say: Say
    ) -> dict[str, Any]:
        return pipeline.write(self.service, project, directory, dossier=dossier, say=say)

    def test(self, project: GameProject, directory: Path, say: Say) -> dict[str, Any]:
        return pipeline.test(self.service, project, directory, say=say)


def title_from(idea: str) -> str:
    """A title short enough for `Metadata.title`, cut where a word ends.

    The idea itself stays whole in `metadata.brief`; this is only what the
    project is called on disk and in the interface, so cutting mid-word would
    cost nothing but read as a bug.
    """
    words = " ".join(idea.split())
    if len(words) <= TITLE_LIMIT:
        return words
    cut = words[:TITLE_LIMIT]
    if " " in cut and not words[TITLE_LIMIT].isspace():
        cut = cut[: cut.rindex(" ")]
    return cut.strip(" ,.;:-") or words[:TITLE_LIMIT]


def artifact_path(project: GameProject, directory: Path) -> Path:
    """Where the build leaves the tape or the disk image.

    Named the same way `release.export_release` names it when it looks for the
    evidence to package, and for the same reason: the toolchain publishes one
    canonical artifact per platform, and both places have to agree on which
    file that is.
    """
    name = "output.tap" if project.target.platform.value == "spectrum" else "output.dsk"
    return directory / "build" / name


def make_game(
    idea: str,
    *,
    platform: TargetPlatform = TargetPlatform.SPECTRUM,
    workspace: Path = Path("studio-projects"),
    stages: Stages | None = None,
    out: Callable[[str], None] = print,
) -> MakeResult:
    """Turn `idea` into a built, emulator-tested game, saying so as it goes.

    `stages` defaults to `ServiceStages` over a service opened on `workspace`;
    passing one makes `workspace` irrelevant, since the stages then own
    wherever the project goes.

    The diary only starts once the project exists -- it lives inside it -- so
    the creation of the project is an `OPEN` line rather than a START/END
    pair, exactly as it is when the interface creates one. Everything after
    that is a stage with a beginning, an end and a duration.
    """
    if not idea.strip():
        return MakeResult(project_dir=None, failed="proyecto", error="an idea is required")
    stages = stages or ServiceStages(StudioService.at(workspace))
    steps = {step.name: step for step in wizard.steps(None, None)}

    out(
        "This runs the whole pipeline and spends money on the OpenAI API in "
        f"{len(PAID_STAGES)} stages ({', '.join(PAID_STAGES)}); it asks nothing else."
    )
    title = title_from(idea)
    try:
        project, directory = stages.create(title, idea, platform)
    except Exception as exc:
        out(f"ERROR: {exc}")
        return MakeResult(project_dir=None, failed="proyecto", error=str(exc))

    diary = _Diary(Journal.for_project(directory), out)
    diary.out(
        diary.journal.write(
            "OPEN", f"made {directory / 'game.yml'} · {project.target.platform.value}"
        )
    )

    try:
        dossier = diary.stage(
            steps["referencia"],
            "searching for a real game like this",
            lambda: _research(stages, project, directory, diary),
        )
        if dossier is not None and dossier.identified:
            project = diary.stage(
                steps["diseño"],
                f"adapting the design to {dossier.title}",
                lambda: _adapt(stages, project, directory, dossier, diary),
            )
        else:
            # Not a failure, and the one place this says so out loud: a game
            # need not be based on a real one, and the design simply keeps
            # the typology it was created with.
            diary.skip(steps["diseño"], "no researched game to adapt to")
            _warn_the_design_will_state_nothing(project, directory, diary, steps)
        diary.stage(
            steps["sprites"],
            "drawing the missing art",
            lambda: _sprites(stages, project, directory, dossier, diary),
        )
        diary.stage(
            steps["programa"],
            "writing the program against the compiler",
            lambda: _write(stages, project, directory, dossier, diary),
        )
        diary.stage(
            steps["gates"],
            "building it and running it",
            lambda: _test(stages, project, directory, diary),
        )
    except _Stopped as stop:
        # Which stage, and what it said. The diary is named because it is the
        # only place the rest of the story is: this stage's own commentary,
        # and how far the ones before it got.
        out(f"STOPPED at {steps[stop.step].number} {stop.step}: {stop.reason}")
        story = f"The whole story is in {directory / JOURNAL_FILENAME}"
        # A stage that got as far as compiling left the toolchain's own words
        # in build/, which the diary summarises but does not quote; a stage
        # that failed before that has no build/ to point at, and naming an
        # empty place is worse than naming none.
        if (directory / "build").is_dir():
            story += f", and what the toolchain said in {directory / 'build'}"
        out(story + ".")
        out(_retry_hint(stop, directory))
        return MakeResult(project_dir=directory, failed=stop.step, error=stop.reason)

    artifact = artifact_path(project, directory)
    if not artifact.is_file():
        # The gates did not refuse, so the game ran -- but nothing published
        # the canonical artifact, and printing a path to a file that is not
        # there would be the one lie this command must not tell.
        reason = f"the gates passed but no artifact was published at {artifact}"
        out(f"STOPPED at {steps['gates'].number} gates: {reason}")
        return MakeResult(project_dir=directory, failed="gates", error=reason)
    out(f"Done. The project, its diary and its evidence are in {directory}.")
    out(str(artifact))
    # The last line, and the only one that is an instruction: a path is
    # where the game is, not how to play it, and somebody who has waited out
    # four paid stages should not have to go looking for the order that
    # opens it.
    out(f"Play it: {how_to_play(directory)}")
    return MakeResult(project_dir=directory, artifact=artifact)


def _warn_the_design_will_state_nothing(
    project: GameProject,
    directory: Path,
    diary: _Diary,
    steps: dict[str, wizard.Step],
) -> None:
    """Say, where the cause is, that the design has been left with no mechanics.

    `diseño` is the only stage that ever writes any: a project is created with
    `mechanics: []` (`samples.blank_project`) and nothing else in Studio fills
    the list. So skipping it over a brief means `programa`'s design gate will
    refuse, three stages and one paid round of art later.

    Before this the order said nothing here: it went on to pay for the art and
    stopped three stages later at `programa`, naming the stage where the
    consequence surfaced rather than the one where the cause was. The
    condition is asked of `design_quality_report` rather than restated as
    `not project.mechanics`, so this warns exactly when the gate would refuse
    and not one case wider.
    """
    from .quality import MECHANICS_CHECK, design_quality_report

    if MECHANICS_CHECK not in design_quality_report(project)["failures"]:
        return
    diary.warn(
        "this design therefore states no mechanics, and a brief with none is "
        f"refused at {steps['programa'].number} {steps['programa'].name}: write one "
        f"sentence per rule into `mechanics` in {directory / 'game.yml'} for the "
        "order to get past it"
    )


def _retry_hint(stop: _Stopped, directory: Path) -> str:
    """The last line a stopped order prints: what to do, not what happened.

    `llmz80 project <stage>` is the right answer for every failure that a
    second run could go differently on -- a compiler that gave up, a model
    that returned nothing, a dropped connection. It is a lie for the design
    gate, which refuses because the design states no mechanics and will refuse
    identically forever: nothing in the CLI or the interface writes mechanics,
    only the designer's proposal in `diseño` does, and that is the stage that
    was skipped. This branch's own review traced that road to its end -- the
    hint sent the reader to `llmz80 project write`, which refuses the same way
    however often it is run, and `llmz80 project adapt` refuses too because no
    game was identified. So this names the file and the field instead, and
    only then the command that will run.
    """
    if isinstance(stop.cause, pipeline.DesignRefused):
        return (
            f"This design needs mechanics before a program can be written for it: "
            f"add them to `mechanics` in {directory / 'game.yml'}, one sentence per "
            f"rule, and then `llmz80 project write {directory}` will run."
        )
    return (
        f"Nothing is lost: retry this stage with `llmz80 project {RESUMES[stop.step]} {directory}`."
    )


# --- the stages, each with the sentence its END line ends in -----------------
#
# Split out rather than written inline as lambdas: every one of them ends in a
# summary the diary keeps forever ("END 3 sprites — ok in 84 s. drew hero,
# ghost"), and a summary is the part worth reading a year later.


def _research(stages: Stages, project: GameProject, directory: Path, diary: _Diary):
    dossier = stages.research(project, directory, diary.say)
    if dossier is None or not dossier.identified:
        return dossier, "no game identified; the design keeps its typology"
    known = [part for part in (dossier.publisher, str(dossier.year or "")) if part]
    on_publisher = f" ({', '.join(known)})" if known else ""
    return dossier, f"{dossier.title}{on_publisher}, {len(dossier.sources)} source(s)"


def _adapt(
    stages: Stages, project: GameProject, directory: Path, dossier: GameReference, diary: _Diary
):
    updated = stages.adapt(project, directory, dossier, diary.say)
    return updated, f"design adapted to {dossier.title}"


def _sprites(
    stages: Stages,
    project: GameProject,
    directory: Path,
    dossier: GameReference | None,
    diary: _Diary,
):
    drawn = stages.sprites(project, directory, dossier, diary.say)
    if not drawn:
        return drawn, "every entity already had its art"
    return drawn, "drew " + ", ".join(asset.id for asset in drawn)


def _write(
    stages: Stages,
    project: GameProject,
    directory: Path,
    dossier: GameReference | None,
    diary: _Diary,
):
    report = stages.write(project, directory, dossier, diary.say)
    attempts = len(report.get("attempts") or [])
    if not report.get("accepted"):
        # The writer had its attempts and the compiler refused every one of
        # them. Nothing after this could improve on that, and the emulator
        # has nothing to run, so the order stops here with the last thing the
        # toolchain actually said.
        raise StageRefused(
            report.get("last_error")
            or "the program was not accepted after " f"{attempts} attempt(s)"
        )
    return report, f"accepted after {attempts} attempt(s)"


def _test(stages: Stages, project: GameProject, directory: Path, diary: _Diary):
    report = stages.test(project, directory, diary.say)
    if report.get("quality_pass") is False:
        # A gate that watched and refused. `None` is not a refusal -- the CPC
        # has no memory probe adapter, so its gates abstain -- and treating it
        # as one would fail every CPC game that ever built and ran.
        failures = (report.get("acceptance") or {}).get("failures") or []
        detail = ": " + ", ".join(map(str, failures)) if failures else ""
        raise StageRefused(f"the game ran but the gates refused it{detail}")
    verdict = "gates passed" if report.get("quality_pass") else "ran; the gates abstained"
    return report, verdict
