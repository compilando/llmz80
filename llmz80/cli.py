"""CLI dispatcher preserving the original generator and adding Studio commands."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace


def _print_help() -> None:
    print(
        "LLMZ80\n"
        "\n"
        "  llmz80 make 'what the game should be' [--cpc] [--workspace PATH] [--play]\n"
        "                                   (the whole pipeline; calls the OpenAI API)\n"
        "  llmz80 play PROJECT|GAME.tap|GAME.dsk\n"
        "                                   (start the emulator and play it)\n"
        "  llmz80 studio [WORKSPACE|PROJECT]\n"
        "                                   (watch a run: stages, diary, verdict)\n"
        "  llmz80 project new WORKSPACE TITLE [spectrum|amstrad_cpc]"
        " ['what this game should be']\n"
        "  llmz80 project types             (kinds of game that exist, for inspiration)\n"
        "  llmz80 project validate PATH\n"
        "  llmz80 project contract PATH\n"
        "  llmz80 project reference PATH    (searches the web, calls the OpenAI API)\n"
        "  llmz80 project adapt PATH        (adapts the design to the researched game)\n"
        "  llmz80 project write PATH        (calls the OpenAI API)\n"
        "  llmz80 project sprites PATH      (calls the OpenAI API)\n"
        "  llmz80 project scaffold PATH\n"
        "  llmz80 project build PATH\n"
        "  llmz80 project test PATH\n"
        "  llmz80 project release PATH\n"
        "  llmz80 [legacy generator options]"
    )


def _openai_client_and_model() -> tuple[object, str]:
    """Resolve the configured OpenAI client and model name once.

    Three subcommands each read config.yml and construct a client; keeping the
    "gpt-5" default and the config lookup in one place means changing either
    is a single edit instead of three synchronised ones. The imports stay
    local to this function, not hoisted to module level, so subcommands that
    never touch OpenAI still cost nothing to import.
    """
    from openai import OpenAI

    from llmz80.utils.config import load_api_key, load_config

    model = load_config("config.yml").get("openai", {}).get("model", "gpt-5")
    return OpenAI(api_key=load_api_key()), model


def _openai_image_model() -> str:
    """Resolve the configured OpenAI image model.

    Kept separate from `_openai_client_and_model`: that function's "model" is
    the text/reasoning model three unrelated subcommands share, and reading
    the two out of the same call would make a caller that wants one always
    pay for looking up the other. `config.yml`'s `openai.image_model`
    defaults to `gpt-image-1` there already; the fallback here only matters
    for a config.yml that predates that key.
    """
    from llmz80.utils.config import load_config

    return load_config("config.yml").get("openai", {}).get("image_model", "gpt-image-1")


def _sprite_preview_array(sheet, args: SimpleNamespace):
    """A palette-index grid `image_utils.display_sprite` can render.

    `display_sprite` looks its colours up itself, via
    `config.get_palette_for_platform(args.platform, args.mode)` -- it has no
    way to be told to use a different table -- so the index chosen for each
    pixel here is the nearest match in that *same* table, not
    `llmz80.studio.compiler.CPC_DEFAULT_PALETTE`, the one actually used to
    pack the sprite for the CPC (and which that module's own docstring says
    has real gaps). The two tables are close but not identical, so this is a
    preview to judge the art by -- shape and roughly-right colour -- not a
    byte-for-byte look at what gets packed.
    """
    import numpy as np
    from config import get_palette_for_platform

    from llmz80.studio.spriting import ALPHA_THRESHOLD

    palette = get_palette_for_platform(args.platform, args.mode)
    width, height = sheet.size
    pixels = sheet.load()
    array = np.zeros((height, width), dtype=int)
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a < ALPHA_THRESHOLD:
                continue
            best_index, best_distance = 0, None
            for index, colour in enumerate(palette):
                distance = (r - colour[0]) ** 2 + (g - colour[1]) ** 2 + (b - colour[2]) ** 2
                if best_distance is None or distance < best_distance:
                    best_index, best_distance = index, distance
            array[y, x] = best_index
    return array


def _new_command(arguments: list[str]) -> int:
    """project new WORKSPACE TITLE [TARGET] [BRIEF]"""
    if not 2 <= len(arguments) <= 4:
        _print_help()
        return 2
    brief = arguments[3] if len(arguments) > 3 else ""
    from llmz80.studio.models import TargetPlatform
    from llmz80.studio.services import StudioService

    workspace, title = Path(arguments[0]).expanduser().resolve(), arguments[1]
    try:
        platform = TargetPlatform(arguments[2] if len(arguments) > 2 else "spectrum")
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2
    from llmz80.studio import pipeline

    service = StudioService.at(workspace)
    _project, directory = pipeline.create(service, title, platform, brief)
    print(directory / "game.yml")
    return 0


def _play_command(arguments: list[str]) -> int:
    """play PROJECT|GAME.tap|GAME.dsk

    Starts the emulator visible, with the game loading itself. It takes one
    path and nothing else: which emulator, which machine and how the game
    autostarts are not questions a person playing should have to answer --
    they are already answered by the gates that verified it.
    """
    if len(arguments) != 1 or not arguments[0].strip():
        print("ERROR: say which game to play: a project directory, a .tap or a .dsk")
        _print_help()
        return 2
    from llmz80.studio.play import play

    return play(Path(arguments[0]))


def _make_command(arguments: list[str]) -> int:
    """make IDEA [--cpc] [--workspace PATH] [--play]

    The only order that turns an idea into a game on its own. Its flags are
    parsed by hand like every other subcommand in this file, and there are
    only three of them on purpose: a fourth question to answer is a step back
    towards the six commands this replaces.
    """
    from llmz80.studio.make import make_game
    from llmz80.studio.models import TargetPlatform

    platform = TargetPlatform.SPECTRUM
    workspace = Path("studio-projects")
    then_play = False
    ideas: list[str] = []
    rest = list(arguments)
    while rest:
        argument = rest.pop(0)
        if argument == "--cpc":
            platform = TargetPlatform.AMSTRAD_CPC
        elif argument == "--play":
            then_play = True
        elif argument.startswith("--workspace="):
            workspace = Path(argument.split("=", 1)[1])
        elif argument == "--workspace":
            if not rest:
                print("ERROR: --workspace needs a path")
                return 2
            workspace = Path(rest.pop(0))
        elif argument.startswith("-"):
            print(f"ERROR: unknown option {argument}")
            _print_help()
            return 2
        else:
            ideas.append(argument)
    if len(ideas) != 1 or not ideas[0].strip():
        # Two positional arguments almost always means an unquoted idea, and
        # guessing that the words should be joined would silently build a
        # game from something the user did not write.
        print("ERROR: say what the game should be, in one quoted argument")
        _print_help()
        return 2

    result = make_game(ideas[0], platform=platform, workspace=workspace.expanduser().resolve())
    if not result.ok:
        return 1
    if then_play and result.artifact is not None:
        # Waited for: the person asked for this in the same breath as the
        # build, so the terminal has nothing else to do until they stop
        # playing.
        from llmz80.studio.play import play

        return play(result.artifact)
    return 0


def _project_command(arguments: list[str]) -> int:
    if arguments and arguments[0] == "new":
        return _new_command(arguments[1:])
    if arguments and arguments[0] == "types":
        from llmz80.studio.typologies import typology_hints

        print(typology_hints())
        return 0
    if len(arguments) != 2 or arguments[0] not in {
        "validate",
        "contract",
        "reference",
        "adapt",
        "write",
        "sprites",
        "scaffold",
        "generate",
        "build",
        "test",
        "release",
    }:
        _print_help()
        return 2
    from llmz80.studio.services import StudioService

    location = Path(arguments[1]).expanduser().resolve()
    service = StudioService.at(location.parent if location.name == "game.yml" else location.parent)
    try:
        project = service.open_project(location)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        return 2
    if arguments[0] == "validate":
        print(
            f"VALID: {project.metadata.title} ({project.target.platform.value}, "
            f"schema v{project.schema_version})"
        )
        return 0
    directory = location.parent if location.name == "game.yml" else location
    if arguments[0] == "contract":
        from llmz80.studio.acceptance import generation_prompt

        print(generation_prompt(project))
        return 0
    if arguments[0] == "reference":
        from llmz80.studio import pipeline

        def replace_dossier(title: str) -> bool:
            # reference.yml is meant to be hand-corrected once a search gets a
            # detail wrong, and a fresh search would silently overwrite those
            # corrections. `pipeline.research` puts this question before it
            # builds the OpenAI client, so declining costs nothing.
            print(f"An archived dossier already exists: {title}")
            return input("Replace it with a fresh search? [y/N] ").strip().casefold() == "y"

        try:
            # The OpenAI SDK parses the model's JSON into GameReference itself,
            # so a response that satisfies the JSON schema but violates a
            # cross-field rule -- an "identified" dossier with no sources, a
            # source missing its retrieved_at -- raises pydantic.ValidationError
            # from inside the SDK's post-parser, before Studio code ever sees
            # the object. That subclasses ValueError, so it is caught here
            # alongside the explicit ValueError research_reference raises when
            # parsing yields nothing. A network or API failure (a connection
            # drop, a bad key, a rate limit) is a different kind of problem
            # with a different remedy and is not a ValueError, so it is
            # deliberately left to propagate rather than folded into this.
            dossier = pipeline.research(
                service, project, directory, say=print, confirm=replace_dossier
            )
        except pipeline.Declined:
            print("Left unchanged.")
            return 0
        except pipeline.Unreadable as exc:
            # A malformed archive is unreadable rather than absent -- that is
            # what load_reference raises for -- so this refuses instead of
            # guessing whether it is safe to replace something it cannot show.
            print(f"ERROR: {exc}")
            print("Fix or remove reference.yml before researching again.")
            return 1
        except ValueError as exc:
            print(f"ERROR: {exc}")
            print(
                "The model's answer could not be read as a game reference. "
                "This is usually transient -- try again -- but check the "
                "configured model and API key if it keeps happening."
            )
            return 1
        if not dossier.identified:
            print("No game was identified. The design keeps its typology.")
            return 1
        # The publisher and year are not guaranteed -- magazine type-ins and
        # self-published titles legitimately lack one or both -- so a blank
        # parenthetical is dropped rather than printed as "( , )" or "()".
        known = [part for part in (dossier.publisher, str(dossier.year or "")) if part]
        on_publisher = f" ({', '.join(known)})" if known else ""
        print(f"{dossier.title}{on_publisher}")
        for source in dossier.sources:
            print(f"  {source.url}")
        print(directory / "reference.yml")
        return 0
    if arguments[0] == "adapt":
        from llmz80.studio import pipeline

        def apply_diff(diff: str) -> bool:
            # Nothing is saved until this says yes: the diff is the whole
            # point of this command existing beside `llmz80 make`, which
            # applies the same proposal with nobody to show it to.
            print(diff)
            return input("\nApply these changes? [y/N] ").strip().casefold() == "y"

        try:
            # A repair happens silently to the model, and `pipeline.adapt`
            # says each one through `say` -- the only sign a user watching
            # the command sees that it made more than one API call, so a
            # silent wait does not read as a hang.
            pipeline.adapt(service, project, directory, say=print, confirm=apply_diff)
        except pipeline.Declined:
            print("Left unchanged.")
            return 0
        except ValueError as exc:
            # `propose_from_reference` already repaired what it could; a
            # ValueError reaching here is either the "no dossier" guard, or
            # the repair loop having exhausted its attempts and raised
            # carrying the last refusal -- either way an ordinary outcome,
            # not a crash, so it is reported the same way as every other
            # refusal in this file, including release's.
            print(f"ERROR: {exc}")
            # The service has no business knowing what this command is
            # called, so the fix-it hint lives here rather than in its
            # exception message.
            if str(exc) == "there is no researched game for this project yet":
                print("Run `llmz80 project reference PATH` first.")
            return 1
        print(directory / "game.yml")
        return 0
    if arguments[0] == "write":
        from llmz80.studio import pipeline
        from llmz80.studio.reference import load_reference

        dossier = load_reference(directory)
        if dossier is not None and dossier.identified:
            # The publisher is not guaranteed -- magazine type-ins and
            # self-published titles legitimately have none -- so a blank
            # parenthetical is dropped rather than printed as "()".
            on_publisher = f" ({dossier.publisher})" if dossier.publisher else ""
            print(f"Writing as {dossier.title}{on_publisher}.")
        report = pipeline.write(service, project, directory, dossier=dossier, say=print)
        for attempt in report["attempts"]:
            print(
                f"  attempt {attempt['number']}: build={attempt['build_passed']} "
                f"acceptance={attempt['acceptance_passed']}"
            )
        print(directory / "write_report.json")
        return 0 if report["accepted"] else 1
    if arguments[0] == "sprites":
        from llmz80.studio import pipeline

        def redraw(existing: str) -> bool:
            # `draw_sprites` only ever fills a gap -- it never touches an id
            # that already has a sprite-kind asset -- so the one place this
            # command can overwrite hand-picked or previously generated art
            # is by evicting it first, which `pipeline.sprites` does only
            # once this says yes. The same courtesy `reference` extends a
            # hand-corrected dossier, for the same reason.
            print("Sprite art already exists for: " + existing)
            return (
                input("Redraw it, overwriting the existing art? [y/N] ").strip().casefold() == "y"
            )

        # Said before anything is constructed, let alone spent: the image API
        # is the most expensive call in this file.
        print("Drawing sprites with OpenAI's image API; this calls the OpenAI API.")
        try:
            drawn = pipeline.sprites(service, project, directory, say=print, confirm=redraw)
        except pipeline.Declined:
            print("Left unchanged.")
            return 0
        except ValueError as exc:
            print(f"ERROR: {exc}")
            return 1

        if not drawn:
            print("Every entity already has sprite art.")
            return 0
        from image_utils import display_sprite
        from PIL import Image

        mode = None
        if project.target.platform.value == "amstrad_cpc":
            mode = "mode0" if project.target.video_mode.value == "cpc_mode_0" else "mode1"
        preview_args = SimpleNamespace(platform=project.target.platform.value, mode=mode)
        for asset in drawn:
            sheet = Image.open(directory / asset.source).convert("RGBA")
            display_sprite(_sprite_preview_array(sheet, preview_args), preview_args)
            print(f"  {asset.id}: {directory / asset.source}")
        return 0
    if arguments[0] in {"scaffold", "generate"}:
        result = service.generate_sources(project, directory)
        print(result.output_dir)
        return 0
    if arguments[0] == "build":
        try:
            result = service.build(project, directory)
        except FileNotFoundError as exc:
            print(f"ERROR: {exc}")
            return 2
        print(result.artifact or result.output_dir / "build_report.json")
        return 0 if result.success else 1
    if arguments[0] == "test":
        from llmz80.studio import pipeline

        try:
            report = pipeline.test(service, project, directory, say=print)
        except (RuntimeError, FileNotFoundError) as exc:
            print(f"ERROR: {exc}")
            return 1
        print(directory / "build" / "emulator_report.json")
        return 0 if report["quality_pass"] else 1
    try:
        print(service.release(project, directory))
    except (RuntimeError, FileNotFoundError) as exc:
        # A refused release is an ordinary outcome, not a crash.
        print(f"ERROR: {exc}")
        return 1
    return 0


def main(argv: list[str] | None = None) -> int | None:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] == "make":
        return _make_command(arguments[1:])
    if arguments and arguments[0] == "play":
        return _play_command(arguments[1:])
    if arguments and arguments[0] == "studio":
        from llmz80.studio.tui import run_studio

        workspace = Path(arguments[1]) if len(arguments) > 1 else Path("studio-projects")
        run_studio(workspace)
        return 0
    if arguments and arguments[0] == "project":
        return _project_command(arguments[1:])
    if arguments and arguments[0] in {"help", "--help"}:
        _print_help()
        return 0

    from llm_z80 import main as legacy_main

    old = sys.argv
    try:
        sys.argv = [old[0], *arguments]
        return legacy_main()
    finally:
        sys.argv = old


if __name__ == "__main__":
    raise SystemExit(main())
