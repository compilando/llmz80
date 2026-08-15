"""The pipeline, once: one function per stage, and no interface in any of them.

There were three copies of this. `llmz80 project <stage>` had one, the
terminal wizard had another (`steps.py`), and `llmz80 make` made a third the
day it was written -- three places that knew a dossier must be archived before
a design can be adapted to it, that art is only ever overwritten by evicting
it first, and how to build the OpenAI collaborator each stage needs. A fix to
what a stage *does* had to be made three times or it was made once and the
other two drifted.

Each function here takes what it needs and returns what it produces. Nothing
prints, prompts, draws or exits: `say` is the only way anything leaves, and it
is the same callable `services.py` already takes as `on_progress`, so a stage
narrates itself into a diary or onto a terminal without knowing which.

The one difference between the callers that is *real* is asking. `llmz80
project reference` will not replace a hand-corrected dossier without a yes,
and `llmz80 project sprites` will not overwrite existing art without one;
`llmz80 make` asks nothing by design -- there is nobody at the keyboard, and
the whole point of the order is that it runs to the end. That difference is
`confirm`: a caller that has somebody to ask passes one, a caller that does
not leaves it out and gets the safe road (nothing is destroyed) rather than
the silent one. `Declined` is what a refusal comes back as, so a caller
reports it as the ordinary outcome it is instead of reading it as a failure.

The collaborator each stage needs -- researcher, designer, artist, writer --
is a parameter, defaulted to the OpenAI-backed one built inside the stage that
needs it. Built there, and not up front, for the reason `make.py` gives: a
missing API key should stop the stage that needed it, with everything the
earlier stages produced already on disk.

What is not here: `validate`, `contract`, `scaffold`, `build` and `release`.
Each has exactly one caller (`llmz80 project ...`) and is already one line
into `StudioService`; a pass-through with one caller is not a shared pipeline,
it is a longer way of writing the call.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .models import AssetSpec, GameProject, TargetPlatform
from .reference import GameReference
from .services import StudioService

#: Told what is happening while it happens. The same shape `services.py` takes
#: as `on_progress`, which is what lets a stage's own commentary reach a diary
#: or a terminal without this module knowing there is either.
Say = Callable[[str], None]

#: Asked before something already on disk is destroyed, and handed the thing
#: at stake (the archived dossier's title, the ids whose art would go, the
#: diff about to be applied) so the caller can phrase its own question. `True`
#: means go ahead.
Ask = Callable[[str], bool]


def _quiet(text: str) -> None:
    """Say nothing, which is what a stage does when nobody asked to be told."""


class Declined(Exception):
    """A `confirm` said no, so the stage did nothing and nothing changed.

    An ordinary outcome and not a failure: it is a person declining to
    overwrite their own work, and a caller that reports it as an error is
    telling them they did something wrong.
    """


class DesignRefused(ValueError):
    """The design gate refused to have a program written for this design.

    A `ValueError` like every other refusal a stage raises, so `llmz80 project
    write`'s existing `except ValueError` keeps reporting it unchanged; a
    distinct type only because the remedy is unlike any other stage failure's.
    Every other way `write` can fail -- the compiler giving up, the model
    returning nothing, a dropped connection -- is answered by running the
    stage again. This one is not: nothing in the CLI or the interface writes
    mechanics into a design, so `llmz80 project write` refuses identically
    forever, and only a person editing `game.yml` moves it. `make.py` tells
    the two apart on this type so it can say that instead of sending somebody
    back to a command that cannot succeed.
    """


class Unreadable(ValueError):
    """A dossier is archived and cannot be read.

    Told apart from every other `ValueError` a stage can raise because the
    remedy is different and specific: fix or remove `reference.yml`. Reading a
    malformed archive as an absent one would silently overwrite it, which is
    the very thing the confirmation exists to prevent.
    """


def create(
    service: StudioService,
    title: str,
    platform: TargetPlatform,
    brief: str = "",
) -> tuple[GameProject, Path]:
    """Start a project, with its brief already in it.

    The brief is applied through `editing.rename_project` and saved, rather
    than passed to `create_project`: it is a validated edit like any other,
    and a project is only ever changed one validated step at a time.

    Raises `FileExistsError` (from `ProjectStore.create`) when the slug is
    taken. Whether that is a refusal or an invitation to try another name is
    the caller's business -- `llmz80 project new` says so and stops, `llmz80
    make` counts up -- and not a rule about creating projects.
    """
    project, directory = service.create_project(title, platform)
    if brief:
        from .editing import rename_project

        project = rename_project(project, project.metadata.title, brief=brief)
        service.save_project(project, directory)
    return project, directory


def research(
    service: StudioService,
    project: GameProject,
    directory: Path,
    researcher: Any = None,
    *,
    say: Say = _quiet,
    confirm: Ask | None = None,
) -> GameReference:
    """Search the web for the real game the brief names, and archive the dossier.

    `reference.yml` is meant to be corrected by hand once a search gets a
    detail wrong, so `confirm` is asked -- with the archived dossier's title
    -- before a fresh search replaces one. That question is put before the
    OpenAI client is built, so declining costs nothing.

    The dossier is archived whether or not it identified a game (that is
    `research_reference`'s own rule): knowing a search already came up empty
    is worth as much as the dossier, and stops every later stage paying for
    the same search again.
    """
    try:
        existing = service.reference(directory)
    except ValueError as exc:
        raise Unreadable(str(exc)) from exc
    if existing is not None and confirm is not None:
        if not confirm(existing.title or "(unidentified)"):
            raise Declined("the archived dossier was kept")
    if researcher is None:
        from ..cli import _openai_client_and_model
        from .reference import ResponsesReferenceResearcher

        client, model = _openai_client_and_model()
        say(f"searching the web with {model}; this calls the OpenAI API")
        researcher = ResponsesReferenceResearcher(client, model=model)
    return service.research_reference(project, directory, researcher)


def draft(
    service: StudioService,
    project: GameProject,
    directory: Path,
    drafter: Any = None,
    dossier: GameReference | None = None,
    *,
    say: Say = _quiet,
    confirm: Ask | None = None,
    examiner: Any = None,
) -> GameProject:
    """Decide what this game is, and save what the draft came to.

    The stage nothing used to do. `adapt` dresses a design whose identity its
    own prompt forbids it to touch, and `samples.blank_project` has no
    authority over anything, so a brief reached the writer as one actor, two
    tiles and no rules -- which is `studio-projects/zampabolas` and
    `studio-projects/my-retro-game`, both written from designs that stated
    nothing.

    A design that does not want drafting is an ordinary outcome, not a
    failure: the project comes back untouched and `say` gets the reason.
    `needs_drafting` is asked before anything at all is built, for the reason
    `research`'s docstring gives about putting the question before the money
    -- this stage announces "this calls the OpenAI API" out loud, and a design
    that already states its rules must never hear it. The reason is worded
    here while the decision stays in `needs_drafting`, so there is still one
    place that decides and one that phrases.

    The dossier is read when it is not handed over, and drafting goes ahead
    without one: that is the whole point of the stage sitting after research
    rather than depending on it, and it is what unblocks a brief whose game
    nobody recognised. A dossier that is archived and unreadable is a
    different matter and stops the stage as `Unreadable`, exactly as it does
    in `research` -- drafting past a dossier somebody paid for because a line
    of YAML is malformed would spend a second call to ignore the first.

    `confirm` is handed the diff and decides whether it is applied, as in
    `adapt`, and for the same reason it is safe to go ahead without one.

    The coherence examiner is built here too, so `llmz80 make` and `llmz80
    project draft` both get the second acceptance test `draft_and_apply`
    describes -- the one that would have caught the frog design that names
    coches in three mechanics and declares no car.
    """
    from .drafting import draft_and_apply, needs_drafting
    from .planner import proposal_diff

    if not needs_drafting(project):
        say(
            "nothing to draft: "
            + (
                "this design already states what it does"
                if project.mechanics
                else "this design carries no brief to draft from"
            )
        )
        return project
    if dossier is None:
        try:
            dossier = service.reference(directory)
        except ValueError as exc:
            raise Unreadable(str(exc)) from exc
    if drafter is None:
        from ..cli import _openai_client_and_model
        from .design_exam import ResponsesCoherenceExaminer
        from .drafting import ResponsesDesignDrafter

        client, model = _openai_client_and_model()
        say(f"drafting the design with {model}; this calls the OpenAI API")
        drafter = ResponsesDesignDrafter(client, model=model)
        # Built inside the `if`, exactly as `adapt` builds its examiner: a
        # caller that injected its own drafter -- every test, every offline
        # run -- gets no examiner either and makes no call it did not ask for.
        if examiner is None:
            examiner = ResponsesCoherenceExaminer(client, model=model)
    drafted = draft_and_apply(project, drafter, dossier, examiner=examiner)
    for number, reason in enumerate(drafted.refusals, start=1):
        say(f"Attempt {number} was refused, repairing: {reason}")
    if confirm is not None and not confirm(proposal_diff(drafted.proposal)):
        raise Declined("the design was left undrafted")
    service.save_project(drafted.project, directory)
    return drafted.project


def adapt(
    service: StudioService,
    project: GameProject,
    directory: Path,
    designer: Any = None,
    dossier: GameReference | None = None,
    *,
    say: Say = _quiet,
    confirm: Ask | None = None,
    examiner: Any = None,
) -> GameProject:
    """Adapt the design to the researched game, and save what it comes to.

    `propose_from_reference` repairs its own refusals, and each one is said
    aloud: a repair is a second call to the model, and a silent wait reads as
    a hang. A design that applies cleanly but says nothing about what the
    brief asked for is one of those refusals -- the examiner's gaps go back to
    the designer as feedback, and only a design that still misses once its
    attempts are spent comes back as a `ValueError`.

    `confirm` is handed the diff and decides whether it is applied. Without
    one the adaptation is saved, which is safe for the same reason it is safe
    in `llmz80 make`: the proposal has already been validated through
    `apply_proposal`, and `game.yml`'s previous revision is kept by
    `ProjectStore.save` as it is for every save -- so nothing is lost, it is
    only unreviewed.

    Whether there is a game to adapt to at all is settled before the OpenAI
    client is built, for the same reason `research` puts its `confirm`
    question first: this stage announces "this calls the OpenAI API" out loud,
    and a project with no dossier used to hear that and then get an error --
    no call was ever made, but being told money was about to go out and then
    handed a failure reads as a charge that went wrong. The check is
    `service.identified_reference` rather than a copy of its two conditions,
    so the message `cli.py` matches on has one home.
    """
    dossier = service.identified_reference(directory, dossier)
    if designer is None:
        from ..cli import _openai_client_and_model
        from .design_exam import ResponsesDesignExaminer
        from .reference_design import ResponsesReferenceDesigner

        client, model = _openai_client_and_model()
        say(f"adapting the design with {model}; this calls the OpenAI API")
        designer = ResponsesReferenceDesigner(client, model=model)
        # Built here and not above the `if`, so a caller that injected its own
        # designer -- every test, every offline run -- gets no examiner either
        # and makes no API call it did not ask for. A caller that wants one
        # without the other passes it.
        if examiner is None:
            examiner = ResponsesDesignExaminer(client, model=model)
    _proposal, diff, updated, refusals = service.propose_from_reference(
        project, directory, designer, dossier, examiner=examiner
    )
    for number, reason in enumerate(refusals, start=1):
        say(f"Attempt {number} was refused, repairing: {reason}")
    if confirm is not None and not confirm(diff):
        raise Declined("the design was left unchanged")
    service.save_project(updated, directory)
    return updated


def _drawn_already(project: GameProject) -> list[str]:
    """The sprite ids this project already has art for.

    `entity.sprite or entity.id` is the id `draw_sprites` itself draws under
    (see its docstring: an entity with no sprite yet wants its own id), and
    asking the question the same way is what keeps the guard below from
    missing art that is genuinely there.
    """
    have = {asset.id for asset in project.assets if asset.kind == "sprite"}
    wanted = {entity.sprite or entity.id for entity in project.entities}
    return sorted(sprite_id for sprite_id in wanted if sprite_id in have)


def sprites(
    service: StudioService,
    project: GameProject,
    directory: Path,
    artist: Any = None,
    dossier: GameReference | None = None,
    *,
    say: Say = _quiet,
    confirm: Ask | None = None,
) -> list[AssetSpec]:
    """Draw the art this project is missing, and register each sheet as an asset.

    `draw_sprites` only ever fills a gap -- it never touches an entity that
    already wears a sprite-kind asset -- so the one way existing art is ever
    overwritten is here, by evicting it first, and that only happens when
    `confirm` is given and says yes. Without a `confirm` the existing art
    stays and only the gaps are filled: a caller with nobody to ask must not
    destroy artwork on its own authority.
    """
    existing = _drawn_already(project)
    if existing and confirm is not None:
        if not confirm(", ".join(existing)):
            raise Declined("the existing art was kept")
        for sprite_id in existing:
            asset = next(a for a in project.assets if a.kind == "sprite" and a.id == sprite_id)
            (directory / asset.source).unlink(missing_ok=True)
        remaining = [a for a in project.assets if not (a.kind == "sprite" and a.id in existing)]
        # `model_copy`, not `model_validate`: between evicting the old asset
        # and `draw_sprites` registering its replacement, an entity
        # legitimately names a sprite id no asset declares yet -- exactly what
        # `structure.py`'s reference check refuses. That gap is closed by
        # `add_asset` a moment later, and `model_copy` is what lets it exist
        # for the moment in between.
        project = project.model_copy(update={"assets": remaining})
        service.save_project(project, directory)
    if artist is None:
        from generators.openai_generator import OpenAIImageGenerator

        from ..cli import _openai_client_and_model, _openai_image_model
        from .sprite_artist import SpriteArtist

        # `OpenAIImageGenerator` takes an API key rather than a client, so the
        # key is read off the client already built instead of loaded twice.
        client, _model = _openai_client_and_model()
        artist = SpriteArtist(
            OpenAIImageGenerator(api_key=client.api_key, model=_openai_image_model())
        )
    return service.draw_sprites(project, directory, artist, dossier, on_progress=say)


def write(
    service: StudioService,
    project: GameProject,
    directory: Path,
    writer: Any = None,
    dossier: GameReference | None = None,
    *,
    say: Say = _quiet,
) -> dict[str, Any]:
    """Have the program written and repaired against the compiler.

    Nothing to confirm: this writes into the project's own program directory,
    and `write_report.json` records every attempt. The report it returns says
    whether the compiler ever accepted one -- what to do about a `False` is
    the caller's decision, and the two callers make different ones (`llmz80
    project write` exits 1, `llmz80 make` stops the order).

    A design its own gate refuses is not sent to the writer at all. Asking
    costs money and a minute and a half, and the answer is already known: a
    design that states no mechanics is `studio-projects/zampabolas`, whose
    program invented a losing condition nobody had asked for and was accepted
    on its first attempt. The refusal carries the gate's sentences rather than
    its check names, because a caller prints what it is given.
    """
    from .quality import design_quality_report, design_refusals

    design = design_quality_report(project)
    if not design["quality_pass"]:
        raise DesignRefused(
            "this design is not ready to be written:\n  " + "\n  ".join(design_refusals(design))
        )
    if writer is None:
        from ..cli import _openai_client_and_model
        from .generator import ResponsesProgramWriter

        client, model = _openai_client_and_model()
        say(f"writing the program with {model}; this calls the OpenAI API")
        writer = ResponsesProgramWriter(client, model=model, reference=dossier)
    return service.write_program(project, directory, writer, on_progress=say)


def test(
    service: StudioService,
    project: GameProject,
    directory: Path,
    *,
    say: Say = _quiet,
) -> dict[str, Any]:
    """Build it, run it in the emulator, and report what the gates saw.

    One line into `runtime_test`, and here rather than called directly by both
    callers for the reason the module docstring gives: this is a stage of the
    pipeline, the list of stages is what `make` and the command line have to
    agree on, and a stage missing from the list is how they stop agreeing.
    """
    return service.runtime_test(project, directory, on_progress=say)
