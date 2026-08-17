"""Tests for the sprite-required gate.

A real end-to-end run exposed a program that had three generated sprites
available, was told by name to draw actors with `plat_sprite`, and never
called it once -- it drew every actor with `plat_cell` instead, and nothing
existing caught that: the build compiled, the acceptance scenarios read
state the program updated without ever touching the screen with a sprite,
and the animation gate correctly abstained because `g_anim_frame` was never
declared (abstaining, not failing, is the right answer for a target whose
emulator cannot read memory -- see `llmz80.studio.feel`).

`llmz80.studio.compiler.sprite_usage_errors` closes that gap: a project that
has sprites the blitter would actually pack (`spriting.is_blitter_sprite`,
via `acceptance.blitter_sprites`) and a program that never calls
`plat_sprite` is refused. See that function's own docstring for exactly how
strict the check is (a source-level grep after blanking comments and string
literals -- cheap and deterministic, not proof a sprite reached the screen)
and why `g_anim_frame` is deliberately not folded into it.

These tests never invoke the real z88dk/CPCtelera toolchain: the pure check
is exercised directly, and the `build_project` wiring is exercised with
`subprocess.run` replaced by a fake that always "succeeds" instantly, so the
suite stays fast and does not depend on a toolchain being installed. The
genuine link-and-boot proof that `plat_sprite` itself works lives in
`tests/test_sprite_blitter_toolchain.py`.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from PIL import Image

from llmz80.core.state_contract import REQUIRED_SYMBOLS, required_declarations
from llmz80.studio import compiler as compiler_module
from llmz80.studio.compiler import build_project, render_project, sprite_usage_errors
from llmz80.studio.generator import ProgramFile, ProgramSources, write_program
from llmz80.studio.models import AssetSpec, TargetPlatform
from llmz80.studio.samples import blank_project
from llmz80.studio.store import ProjectStore

#: The required half of the observable state contract. Nothing here is
#: compiled -- `_fake_toolchain` writes the map these declarations would have
#: produced -- so this is realism, not what satisfies the gate: deleting it
#: leaves every test in this module passing. It is here because the two
#: programs below stand in for real ones, and a reader comparing them should
#: find them differing in the one thing this module is about, whether they
#: call `plat_sprite`, and not in whether they look like programs Studio
#: would accept. Derived from the contract so it cannot fall behind it.
CONTRACT_STATE = required_declarations()

NO_SPRITE_MAIN = (
    '#include "platform.h"\n\n' + CONTRACT_STATE + "\n"
    "void main(void) {\n"
    "    plat_init();\n"
    "    plat_cell(0, 0, '#');\n"
    "    while (1) { }\n"
    "}\n"
)

DRAWS_SPRITE_MAIN = (
    '#include "platform.h"\n'
    '#include "sprites.h"\n\n' + CONTRACT_STATE + "\n"
    "void main(void) {\n"
    "    plat_init();\n"
    "    plat_sprite(0, 0, SPRITE_HERO, 0);\n"
    "    while (1) { }\n"
    "}\n"
)


def _sprite_image() -> Image.Image:
    """A 16x16 RGBA sprite, half opaque -- a real blitter-sprite shape."""
    image = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    pixels = image.load()
    for y in range(16):
        for x in range(16):
            pixels[x, y] = (255, 0, 0, 255) if (x + y) % 2 == 0 else (0, 0, 0, 0)
    return image


def _sprite_asset(directory: Path, asset_id: str = "hero") -> AssetSpec:
    """Write a real 16x16 sheet and its `AssetSpec`, without going through
    `StudioService.add_asset` -- these tests only need the file and the spec
    `is_blitter_sprite` will accept, the same shortcut
    `test_studio_compiler.py`'s own `_add_sprite_asset` takes."""
    assets_dir = directory / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{asset_id}.png"
    _sprite_image().save(assets_dir / filename)
    return AssetSpec(id=asset_id, source=f"assets/{filename}", width=16, height=16, frames=1)


# ---------------------------------------------------------------------------
# The pure check: no filesystem, no toolchain, just project + source text.
# ---------------------------------------------------------------------------


def test_no_sprites_means_no_check_regardless_of_source():
    """A design with no art must build exactly as it does today."""
    project = blank_project("NoArt", TargetPlatform.SPECTRUM)
    assert project.assets == []
    assert sprite_usage_errors(project, {"main.c": NO_SPRITE_MAIN}) == []


def test_sprites_but_no_plat_sprite_call_is_refused(tmp_path: Path):
    project = blank_project("Ungrateful", TargetPlatform.SPECTRUM)
    project.assets = [_sprite_asset(tmp_path)]

    errors = sprite_usage_errors(project, {"main.c": NO_SPRITE_MAIN})

    assert len(errors) == 1
    assert "plat_sprite" in errors[0]
    assert "SPRITE_HERO" in errors[0]  # names what to draw with


def test_sprites_and_a_real_call_are_accepted(tmp_path: Path):
    project = blank_project("Grateful", TargetPlatform.SPECTRUM)
    project.assets = [_sprite_asset(tmp_path)]

    assert sprite_usage_errors(project, {"main.c": DRAWS_SPRITE_MAIN}) == []


def test_a_call_only_inside_a_comment_or_string_does_not_count(tmp_path: Path):
    """A naive grep would be fooled by this. Blanking comments and string
    literals before searching (see `compiler._blanked`) is why this check is
    not that -- see `sprite_usage_errors`'s docstring for what it still
    cannot catch (a real call that is merely unreachable)."""
    project = blank_project("Sneaky", TargetPlatform.SPECTRUM)
    project.assets = [_sprite_asset(tmp_path)]
    source = (
        '#include "platform.h"\n\n'
        "/* plat_sprite(0, 0, SPRITE_HERO, 0); -- TODO draw the hero */\n"
        'static const char *note = "call plat_sprite(0,0,0,0) later";\n'
        "void main(void) {\n"
        "    plat_cell(0, 0, '#');\n"
        "    while (1) { }\n"
        "}\n"
    )

    errors = sprite_usage_errors(project, {"main.c": source})

    assert len(errors) == 1


def test_the_library_itself_is_not_what_gets_scanned():
    """`sprite_usage_errors` takes the program's own sources, never the
    library Studio copies in beside them -- `resources/studio_lib/*/platform.c`
    both declares and calls `plat_sprite` internally, so scanning it would
    make the check pass unconditionally. This documents the contract at the
    call site: `build_project` below passes only `program_sources()`."""
    library = (
        Path(__file__).resolve().parents[1] / "resources" / "studio_lib" / "spectrum" / "platform.c"
    )
    assert "plat_sprite" in library.read_text(encoding="utf-8")  # sanity: it is there to scan
    # But a project's OWN sources are what sprite_usage_errors actually reads;
    # a program that never mentions plat_sprite itself must still be refused
    # even though the library beside it defines the function.


# ---------------------------------------------------------------------------
# Wired into build_project: cheap because the real toolchain is replaced.
# ---------------------------------------------------------------------------


def _fake_toolchain(monkeypatch: pytest.MonkeyPatch) -> list[list[str]]:
    """Stand in for zcc/make: succeeds instantly and writes a non-empty
    canonical artifact, without ever running a real compiler.

    Recording every invocation lets a test prove the sprite check runs
    *before* the toolchain for a refusal (`calls == []`) and does not block
    it when the program is innocent (`len(calls) == 1`).

    It writes `output.map` as well as `output.tap`, because a real zcc run
    writes both and `build_project` now reads the map to check the state
    contract. Leaving it out would make every program built here look like
    one that declared its state static, and fail these tests for a reason
    they are not about. The entries come from `REQUIRED_SYMBOLS` rather than
    a hand-written list so the fiction cannot drift from the contract the
    two programs above actually declare.
    """
    calls: list[list[str]] = []

    def fake_run(command, cwd, capture_output, text, check):
        calls.append(list(command))
        (Path(cwd) / "output.tap").write_bytes(b"\x00" * 64)
        (Path(cwd) / "output.map").write_text(
            "".join(
                f"_{name}{' ' * 8}= ${0x9F00 + index:04X} ; addr, public, , main\n"
                for index, name in enumerate(REQUIRED_SYMBOLS)
            ),
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(compiler_module.subprocess, "run", fake_run)
    return calls


def _project_with_program(tmp_path: Path, *, name: str, main_c: str, with_sprite: bool):
    project = blank_project(name, TargetPlatform.SPECTRUM)
    directory = ProjectStore(tmp_path).create(project)
    if with_sprite:
        project.assets = [_sprite_asset(directory)]
    program_dir = directory / project.program_dir
    program_dir.mkdir(parents=True, exist_ok=True)
    (program_dir / "main.c").write_text(main_c, encoding="utf-8")
    return project, directory


def test_a_program_that_never_draws_its_sprites_is_refused_without_compiling(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    calls = _fake_toolchain(monkeypatch)
    project, directory = _project_with_program(
        tmp_path, name="Refused", main_c=NO_SPRITE_MAIN, with_sprite=True
    )

    build = build_project(project, directory / "build")

    assert build.success is False
    assert build.report["quality_pass"] is False
    assert "plat_sprite" in build.report["stderr"]
    assert calls == []  # never reached the toolchain


def test_the_same_project_with_a_program_that_draws_builds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    calls = _fake_toolchain(monkeypatch)
    project, directory = _project_with_program(
        tmp_path, name="Accepted", main_c=DRAWS_SPRITE_MAIN, with_sprite=True
    )

    build = build_project(project, directory / "build")

    assert build.success is True, build.report.get("stderr") or build.report.get("stdout")
    assert len(calls) == 1  # the check let it through to the toolchain


def test_a_project_with_no_sprites_at_all_is_unaffected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    calls = _fake_toolchain(monkeypatch)
    project, directory = _project_with_program(
        tmp_path, name="Plain", main_c=NO_SPRITE_MAIN, with_sprite=False
    )

    build = build_project(project, directory / "build")

    assert build.success is True, build.report.get("stderr") or build.report.get("stdout")
    assert len(calls) == 1


# ---------------------------------------------------------------------------
# Reaching the repair loop: the refusal must be feedback, not a crash.
# ---------------------------------------------------------------------------


def test_the_refusal_reaches_the_repair_loop_as_actionable_feedback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """`generator.write_program` must see this refusal exactly the way it
    sees a real compiler diagnostic: as `feedback` text for the next
    attempt. If `sprite_usage_errors` were wired in as a raised exception
    instead (the way `validate_sprite_budget` and the missing-asset check
    already are for project-level, not per-attempt, failures), it would
    propagate out of `write_program` uncaught -- see the loop's `verify(...)`
    call, which is not wrapped in `try/except` the way `writer.write(...)`
    is -- and end the whole repair loop on attempt one instead of spending
    the remaining attempts.
    """
    _fake_toolchain(monkeypatch)
    project = blank_project("Repaired", TargetPlatform.SPECTRUM)
    directory = ProjectStore(tmp_path).create(project)
    project.assets = [_sprite_asset(directory)]

    attempts = {"n": 0}

    class StubWriter:
        def write(self, project, feedback=None):
            attempts["n"] += 1
            if attempts["n"] == 1:
                assert feedback is None
                body = NO_SPRITE_MAIN
            else:
                assert feedback and "plat_sprite" in feedback, feedback
                body = DRAWS_SPRITE_MAIN
            return ProgramSources(
                summary="stub", files=[ProgramFile(name="main.c", body=body)]
            )

    def verify(project, directory):
        render_project(project, directory / "build")
        build = build_project(project, directory / "build")
        return {"build": build.report, "acceptance": None, "probes": build.report.get("probes")}

    result = write_program(project, directory, StubWriter(), verify, attempts=3)

    assert attempts["n"] == 2
    assert result.attempts[0].build_passed is False
    assert "plat_sprite" in result.attempts[0].feedback
    assert result.attempts[1].build_passed is True
    assert result.accepted is True


# ---------------------------------------------------------------------------
# The same rule for terrain artwork, which is where it was actually noticed.
# ---------------------------------------------------------------------------

DRAWS_TILE_MAIN = (
    '#include "platform.h"\n'
    '#include "tiles.h"\n\n' + CONTRACT_STATE + "\n"
    "void main(void) {\n"
    "    plat_init();\n"
    "    plat_tile(0, 0, TILE_FLOOR);\n"
    "    while (1) { }\n"
    "}\n"
)


def _tile_asset(directory: Path, asset_id: str = "brickwork") -> AssetSpec:
    assets_dir = directory / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    pixels = image.load()
    for y in range(8):
        for x in range(8):
            if (x + y) % 2 == 0:
                pixels[x, y] = (255, 0, 0, 255)
    filename = f"{asset_id}.png"
    image.save(assets_dir / filename)
    return AssetSpec(
        id=asset_id, kind="tileset", source=f"assets/{filename}", width=8, height=8, frames=1
    )


def test_a_program_that_draws_its_terrain_as_letters_is_refused_without_compiling(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """The defect a finished Arkanoid shipped with: bricks packed as artwork,
    bricks drawn as the character 'B', every gate green."""
    calls = _fake_toolchain(monkeypatch)
    project, directory = _project_with_program(
        tmp_path, name="TextTerrain", main_c=NO_SPRITE_MAIN, with_sprite=False
    )
    project.assets = [_tile_asset(directory)]
    project.tiles[0].art = "brickwork"

    build = build_project(project, directory / "build")

    assert build.success is False
    assert build.report["quality_pass"] is False
    assert "plat_tile" in build.report["stderr"]
    assert calls == []  # never reached the toolchain


def test_the_same_project_with_a_program_that_draws_its_tiles_builds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    calls = _fake_toolchain(monkeypatch)
    project, directory = _project_with_program(
        tmp_path, name="ArtTerrain", main_c=DRAWS_TILE_MAIN, with_sprite=False
    )
    project.assets = [_tile_asset(directory)]
    project.tiles[0].art = "brickwork"

    build = build_project(project, directory / "build")

    assert build.success is True, build.report.get("stderr") or build.report.get("stdout")
    assert len(calls) == 1
