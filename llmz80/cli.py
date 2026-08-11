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
        " [maze_chase|single_screen_collect]\n"
        "  llmz80 project validate PATH\n"
        "  llmz80 project contract PATH\n"
        "  llmz80 project generate PATH\n"
        "  llmz80 project build PATH\n"
        "  llmz80 project test PATH\n"
        "  llmz80 project release PATH\n"
        "  llmz80 [legacy generator options]"
    )


def _new_command(arguments: list[str]) -> int:
    """project new WORKSPACE TITLE [TARGET] [GENRE]"""
    if not 2 <= len(arguments) <= 4:
        _print_help()
        return 2
    from llmz80.studio.models import GenreId, TargetPlatform
    from llmz80.studio.services import StudioService

    workspace, title = Path(arguments[0]).expanduser().resolve(), arguments[1]
    try:
        platform = TargetPlatform(arguments[2] if len(arguments) > 2 else "spectrum")
        genre = GenreId(arguments[3] if len(arguments) > 3 else "maze_chase")
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2
    _, directory = StudioService.at(workspace).create_project(title, platform, genre)
    print(directory / "game.yml")
    return 0


def _project_command(arguments: list[str]) -> int:
    if arguments and arguments[0] == "new":
        return _new_command(arguments[1:])
    if len(arguments) != 2 or arguments[0] not in {
        "validate",
        "contract",
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
    project = service.open_project(location)
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
    if arguments[0] == "generate":
        result = service.generate_sources(project, directory)
        print(result.output_dir)
        return 0
    if arguments[0] == "build":
        result = service.build(project, directory)
        print(result.artifact or result.output_dir / "build_report.json")
        return 0 if result.success else 1
    if arguments[0] == "test":
        report = service.runtime_test(project, directory)
        print(directory / "build" / "emulator_report.json")
        return 0 if report["quality_pass"] else 1
    print(service.release(project, directory))
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
