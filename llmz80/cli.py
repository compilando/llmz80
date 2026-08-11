"""CLI dispatcher preserving the original generator and adding Studio commands."""

from __future__ import annotations

import sys
from pathlib import Path


def _print_help() -> None:
    print(
        "LLMZ80\n"
        "\n"
        "  llmz80 studio [WORKSPACE]\n"
        "  llmz80 project new WORKSPACE TITLE [spectrum|amstrad_cpc]"
        " [TYPE] ['what this game should be']\n"
        "  llmz80 project types\n"
        "  llmz80 project validate PATH\n"
        "  llmz80 project contract PATH\n"
        "  llmz80 project reference PATH    (searches the web, calls the OpenAI API)\n"
        "  llmz80 project adapt PATH        (adapts the design to the researched game)\n"
        "  llmz80 project write PATH        (calls the OpenAI API)\n"
        "  llmz80 project scaffold PATH\n"
        "  llmz80 project build PATH\n"
        "  llmz80 project test PATH\n"
        "  llmz80 project release PATH\n"
        "  llmz80 [legacy generator options]"
    )


def _new_command(arguments: list[str]) -> int:
    """project new WORKSPACE TITLE [TARGET] [TYPE] [BRIEF]"""
    if not 2 <= len(arguments) <= 5:
        _print_help()
        return 2
    brief = arguments[4] if len(arguments) > 4 else ""
    from llmz80.studio.models import TargetPlatform
    from llmz80.studio.packs import PACKS_BY_ID
    from llmz80.studio.services import StudioService

    workspace, title = Path(arguments[0]).expanduser().resolve(), arguments[1]
    try:
        platform = TargetPlatform(arguments[2] if len(arguments) > 2 else "spectrum")
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2
    genre = arguments[3] if len(arguments) > 3 else "maze_chase"
    if genre not in PACKS_BY_ID:
        print(f"ERROR: unknown game type '{genre}'. Available:")
        for pack in PACKS_BY_ID.values():
            print(f"  {pack.id:24} {pack.description}")
        return 2
    service = StudioService.at(workspace)
    project, directory = service.create_project(title, platform, genre)
    if brief:
        from llmz80.studio.editing import rename_project

        project = rename_project(project, project.metadata.title, brief=brief)
        service.save_project(project, directory)
    print(directory / "game.yml")
    return 0


def _project_command(arguments: list[str]) -> int:
    if arguments and arguments[0] == "new":
        return _new_command(arguments[1:])
    if arguments and arguments[0] == "types":
        from llmz80.studio.packs import BUILTIN_PACKS

        for pack in BUILTIN_PACKS:
            print(f"  {pack.id:24} {pack.terrain:10} {pack.description}")
        return 0
    if len(arguments) != 2 or arguments[0] not in {
        "validate",
        "contract",
        "reference",
        "adapt",
        "write",
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
        from openai import OpenAI

        from llmz80.studio.reference import ResponsesReferenceResearcher
        from llmz80.utils.config import load_api_key, load_config

        # reference.yml is meant to be hand-corrected once a search gets a
        # detail wrong, and re-running this command would silently overwrite
        # those corrections. A malformed archive is treated as unreadable
        # rather than absent -- load_reference raises for exactly that reason
        # -- so this refuses rather than guessing whether it is safe to
        # replace something it cannot show the user.
        try:
            existing = service.reference(directory)
        except ValueError as exc:
            print(f"ERROR: {exc}")
            print("Fix or remove reference.yml before researching again.")
            return 1
        if existing is not None:
            print(f"An archived dossier already exists: {existing.title or '(unidentified)'}")
            if input("Replace it with a fresh search? [y/N] ").strip().casefold() != "y":
                print("Left unchanged.")
                return 0

        model = load_config("config.yml").get("openai", {}).get("model", "gpt-5")
        print(f"Researching with {model}; this searches the web and calls the OpenAI API.")
        researcher = ResponsesReferenceResearcher(OpenAI(api_key=load_api_key()), model=model)
        dossier = service.research_reference(project, directory, researcher)
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
        from openai import OpenAI

        from llmz80.studio.planner import apply_proposal
        from llmz80.studio.reference_design import ResponsesReferenceDesigner
        from llmz80.utils.config import load_api_key, load_config

        model = load_config("config.yml").get("openai", {}).get("model", "gpt-5")
        designer = ResponsesReferenceDesigner(OpenAI(api_key=load_api_key()), model=model)
        try:
            proposal, diff = service.propose_from_reference(project, directory, designer)
        except ValueError as exc:
            print(f"ERROR: {exc}")
            return 1
        print(diff)
        if input("\nApply these changes? [y/N] ").strip().casefold() != "y":
            print("Left unchanged.")
            return 0
        try:
            updated = apply_proposal(project, proposal)
        except ValueError as exc:
            print(f"REFUSED: {exc}")
            return 1
        service.save_project(updated, directory)
        print(directory / "game.yml")
        return 0
    if arguments[0] == "write":
        from openai import OpenAI

        from llmz80.studio.generator import ResponsesProgramWriter
        from llmz80.studio.reference import load_reference
        from llmz80.utils.config import load_api_key, load_config

        settings = load_config("config.yml")
        model = settings.get("openai", {}).get("model", "gpt-5")
        print(f"Writing the program with {model}; this calls the OpenAI API.")
        dossier = load_reference(directory)
        if dossier is not None and dossier.identified:
            # The publisher is not guaranteed -- magazine type-ins and
            # self-published titles legitimately have none -- so a blank
            # parenthetical is dropped rather than printed as "()".
            on_publisher = f" ({dossier.publisher})" if dossier.publisher else ""
            print(f"Writing as {dossier.title}{on_publisher}.")
        writer = ResponsesProgramWriter(
            OpenAI(api_key=load_api_key()), model=model, reference=dossier
        )
        report = service.write_program(project, directory, writer)
        for attempt in report["attempts"]:
            print(
                f"  attempt {attempt['number']}: build={attempt['build_passed']} "
                f"acceptance={attempt['acceptance_passed']}"
            )
        print(directory / "write_report.json")
        return 0 if report["accepted"] else 1
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
        try:
            report = service.runtime_test(project, directory)
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
