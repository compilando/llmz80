import json
import re
from pathlib import Path

import pytest
from PIL import Image

from llmz80.studio.acceptance import blitter_sprites
from llmz80.studio.compiler import build_project, render_project, validate_design_fits_target
from llmz80.studio.layout import relayout
from llmz80.studio.models import AssetSpec, GenreId, TargetPlatform
from llmz80.studio.packs import create_default_project
from llmz80.studio.services import StudioService
from llmz80.studio.spriting import pack_spectrum
from llmz80.studio.sprite_sheet import split_frames
from llmz80.studio.store import ProjectStore

REFERENCE = Path(__file__).resolve().parents[1] / "resources" / "studio_reference"


def _with_program(project, directory: Path, platform: TargetPlatform):
    """Give a project the reference program as its own source of record."""
    target = "spectrum" if platform is TargetPlatform.SPECTRUM else "amstrad_cpc"
    program = directory / project.program_dir
    program.mkdir(parents=True, exist_ok=True)
    for path in (REFERENCE / target / "src").iterdir():
        if path.suffix in {".c", ".h"}:
            (program / path.name).write_bytes(path.read_bytes())
    return project


def _sprite_sheet(frames: int) -> Image.Image:
    """A `frames`-wide 16x16-per-frame RGBA sheet, half opaque so it packs to
    non-trivial data and mask bytes rather than an all-one-value edge case.
    """
    image = Image.new("RGBA", (16 * frames, 16), (0, 0, 0, 0))
    pixels = image.load()
    for y in range(16):
        for x in range(16 * frames):
            if (x + y) % 2 == 0:
                pixels[x, y] = (255, 0, 0, 255)
    return image


def _add_sprite_asset(directory: Path, asset_id: str, frames: int) -> AssetSpec:
    """Write a real `frames`-frame 16x16 sprite sheet and its AssetSpec."""
    assets_dir = directory / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{asset_id}.png"
    _sprite_sheet(frames).save(assets_dir / filename)
    return AssetSpec(
        id=asset_id, source=f"assets/{filename}", width=16 * frames, height=16, frames=frames
    )


@pytest.mark.parametrize("platform", list(TargetPlatform))
def test_scaffolding_contributes_library_and_contracts_not_gameplay(
    tmp_path: Path, platform: TargetPlatform
):
    project = create_default_project("Scaffold", platform, GenreId.MAZE_CHASE)
    directory = ProjectStore(tmp_path).create(project)

    result = render_project(project, directory / "build")
    source = result.output_dir / "src"

    assert (source / "platform.c").is_file()
    assert (source / "platform.h").is_file()
    assert (source / "game_config.h").is_file()
    assert (source / "game_state.h").is_file()
    # Studio writes no gameplay of its own.
    assert not (source / "engine.c").exists()
    assert (result.output_dir / "CONTRACT.md").read_text().startswith("OBSERVABLE STATE CONTRACT")


def test_a_project_without_a_program_scaffolds_and_says_so(tmp_path: Path):
    project = create_default_project("Empty", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    directory = ProjectStore(tmp_path).create(project)

    result = render_project(project, directory / "build")

    manifest = json.loads((result.output_dir / "studio_manifest.json").read_text())
    assert manifest["program_present"] is False
    assert manifest["program"] == []
    assert manifest["generated"] is False


def test_the_projects_own_sources_reach_the_build(tmp_path: Path):
    project = create_default_project("Owned", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    directory = ProjectStore(tmp_path).create(project)
    _with_program(project, directory, TargetPlatform.SPECTRUM)

    result = render_project(project, directory / "build")

    manifest = json.loads((result.output_dir / "studio_manifest.json").read_text())
    assert manifest["program_present"] is True
    assert "engine.c" in manifest["program"]
    assert (result.output_dir / "src" / "engine.c").is_file()
    assert result.main_c.is_file()


def test_sprites_h_reaches_src_as_declarations_and_sprites_c_as_definitions(tmp_path: Path):
    """The link-time defect this module guards against (see
    tests/test_sprite_blitter_toolchain.py for the real-toolchain proof):
    sprites.h must declare the sprite tables `extern`, never define them,
    because it is included by both platform.c and the program's own main.c;
    the actual definitions belong in sprites.c, compiled exactly once.
    """
    project = create_default_project("SplitHeader", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    directory = ProjectStore(tmp_path).create(project)
    asset = _add_sprite_asset(directory, "hero", frames=1)
    project.assets = [asset]

    result = render_project(project, directory / "build")

    sprites_h = (result.output_dir / "src" / "sprites.h").read_text(encoding="utf-8")
    sprites_c = (result.output_dir / "src" / "sprites.c").read_text(encoding="utf-8")

    assert "extern const unsigned char *const sprite_data[];" in sprites_h
    assert "0x" not in sprites_h  # no packed byte ever lands in the header
    assert '#include "sprites.h"' in sprites_c
    assert "const unsigned char *const sprite_data[] = {" in sprites_c


def test_a_program_may_not_shadow_a_studio_generated_file(tmp_path: Path):
    """A program that writes its own sprites.h (or platform.c, or any other
    file Studio generates) must not have it silently override the generated
    one -- that is how `SPRITE_PELLET` and friends have gone missing before
    while the build still (mostly) succeeded. Refuse it loudly instead.
    """
    project = create_default_project("Shadow", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    directory = ProjectStore(tmp_path).create(project)
    program_dir = directory / project.program_dir
    program_dir.mkdir(parents=True, exist_ok=True)
    (program_dir / "main.c").write_text("int main(void) { return 0; }\n", encoding="utf-8")
    (program_dir / "sprites.h").write_text(
        "#ifndef LLMZ80_SPRITES_H\n#define LLMZ80_SPRITES_H\n#endif\n", encoding="utf-8"
    )

    with pytest.raises(ValueError, match="sprites.h"):
        render_project(project, directory / "build")


def test_a_removed_source_does_not_survive_the_next_scaffold(tmp_path: Path):
    project = create_default_project("Stale", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    directory = ProjectStore(tmp_path).create(project)
    _with_program(project, directory, TargetPlatform.SPECTRUM)
    render_project(project, directory / "build")
    (directory / project.program_dir / "engine.c").unlink()

    result = render_project(project, directory / "build")

    assert not (result.output_dir / "src" / "engine.c").exists()
    assert (result.output_dir / "src" / "platform.c").is_file()


def test_the_config_header_states_the_target_and_the_design(tmp_path: Path):
    project = create_default_project("Config", TargetPlatform.AMSTRAD_CPC, GenreId.MAZE_CHASE)
    project.gameplay.score_per_collectible = 25

    header = (
        render_project(project, tmp_path / "build").output_dir / "src" / "game_config.h"
    ).read_text()

    assert "#define SCORE_PER_COLLECTIBLE 25" in header
    assert "#define CPC_MODE 1" in header
    assert "#define PLAYFIELD_COLS 40" in header
    assert "#define HAS_FRAME_CLOCK 0" in header


def test_the_state_header_declares_the_whole_contract(tmp_path: Path):
    project = create_default_project("State", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)

    header = (
        render_project(project, tmp_path / "build").output_dir / "src" / "game_state.h"
    ).read_text()

    for symbol in ("g_score", "g_lives", "g_level", "g_state", "g_hiscore"):
        assert f" {symbol};" in header
    assert "extern unsigned int g_score;" in header


def test_a_level_larger_than_the_target_grid_is_refused(tmp_path: Path):
    project = create_default_project("Oversized", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    project = relayout(project, width=40)

    with pytest.raises(ValueError, match="offers 32x22 playable cells"):
        validate_design_fits_target(project)


def test_scaffolding_is_byte_identical_across_runs(tmp_path: Path):
    project = create_default_project("Determinism", TargetPlatform.AMSTRAD_CPC, GenreId.MAZE_CHASE)

    first = render_project(project, tmp_path / "build")
    snapshot = {
        path.relative_to(first.output_dir): path.read_bytes()
        for path in first.output_dir.rglob("*")
        if path.suffix in {".c", ".h", ".md"}
    }
    render_project(project, tmp_path / "build")

    for relative, content in snapshot.items():
        assert (first.output_dir / relative).read_bytes() == content, relative


@pytest.mark.parametrize("platform", list(TargetPlatform))
def test_imported_asset_is_owned_padded_and_target_packed(tmp_path: Path, platform: TargetPlatform):
    source = tmp_path / "odd sprite.png"
    Image.new("RGB", (7, 5), "white").save(source)
    workspace = tmp_path / "projects"
    service = StudioService.at(workspace)
    project, directory = service.create_project("Assets", platform, GenreId.SINGLE_SCREEN_COLLECT)

    asset = service.add_asset(project, directory, source)
    result = service.generate_sources(project, directory)

    assert asset.source.startswith("assets/")
    assert (directory / asset.source).is_file()
    assert (result.output_dir / "src" / "assets.c").is_file()
    header = (result.output_dir / "src" / "assets.h").read_text()
    expected_bytes = 1 if platform is TargetPlatform.SPECTRUM else 2
    assert f"WIDTH_BYTES {expected_bytes}" in header


def test_building_without_a_program_says_what_is_missing(tmp_path: Path):
    project = create_default_project("Empty", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    directory = ProjectStore(tmp_path).create(project)

    with pytest.raises(FileNotFoundError, match="no program yet"):
        build_project(project, directory / "build")


def test_sprites_that_fit_the_budget_build_as_before(tmp_path: Path):
    project = create_default_project("Trim", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    directory = ProjectStore(tmp_path).create(project)
    asset = _add_sprite_asset(directory, "hero", frames=1)
    project.assets = [asset]

    result = render_project(project, directory / "build")

    sprites_h = (result.output_dir / "src" / "sprites.h").read_text(encoding="utf-8")
    assert "#define SPRITE_COUNT 1" in sprites_h


def test_sprites_h_and_blitter_sprites_agree_on_every_asset(tmp_path: Path):
    """`compiler.render_project` (what actually gets packed into `sprites.h`)
    and `acceptance.blitter_sprites` (what `design_prompt` tells the writer to
    expect) must name exactly the same assets. Both now call the single
    `spriting.is_blitter_sprite`, so simply calling that function twice would
    prove nothing about agreement -- it would just prove a function returns
    the same thing twice. This instead drives each real code path (the
    compiler's file writer, the prompt's list builder) on a mix designed to
    exercise every way an asset can fail the rule -- wrong kind, wrong frame
    size -- and checks the *outputs* against each other: the constants the
    written header actually `#define`s, versus the ids `blitter_sprites`
    reports. A future edit that reintroduces a hand-copied filter in only one
    of the two places -- the exact regression this guards against -- would
    make one of them disagree with the header the other module wrote.
    """
    project = create_default_project("Mix", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    directory = ProjectStore(tmp_path).create(project)
    assets_dir = directory / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    fits = _add_sprite_asset(directory, "hero", frames=1)  # sprite kind, 16x16: qualifies

    Image.new("RGBA", (16, 32), (255, 0, 0, 255)).save(assets_dir / "banner.png")
    wrong_size = AssetSpec(
        id="banner", kind="sprite", source="assets/banner.png", width=16, height=32, frames=1
    )  # sprite kind, but not 16x16: disqualified by size

    Image.new("RGBA", (16, 16), (0, 255, 0, 255)).save(assets_dir / "tiles.png")
    wrong_kind = AssetSpec(
        id="tiles", kind="tileset", source="assets/tiles.png", width=16, height=16, frames=1
    )  # 16x16, but not sprite kind: disqualified by kind

    project.assets = [fits, wrong_size, wrong_kind]

    result = render_project(project, directory / "build")
    sprites_h = (result.output_dir / "src" / "sprites.h").read_text(encoding="utf-8")

    expected_ids = {asset.id for asset in blitter_sprites(project)}
    assert expected_ids == {"hero"}  # sanity: the fixture actually exercises all three cases

    for asset in project.assets:
        constant = f"SPRITE_{asset.id.upper()}"
        if asset.id in expected_ids:
            assert re.search(rf"#define {constant} \d+\b", sprites_h), (
                f"{constant} is missing from sprites.h though blitter_sprites promised it"
            )
        else:
            assert constant not in sprites_h, (
                f"{constant} is in sprites.h though blitter_sprites never promised it"
            )


def test_sprites_over_the_static_data_budget_are_refused(tmp_path: Path):
    project = create_default_project("Bulky", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    # A small budget keeps the failing case to two sprite assets instead of
    # dozens, while still exercising the real packer arithmetic end to end.
    project.budgets.static_data_bytes = 1024
    directory = ProjectStore(tmp_path).create(project)
    big = _add_sprite_asset(directory, "hero", frames=8)
    small = _add_sprite_asset(directory, "enemy2", frames=1)
    project.assets = [big, small]

    expected_total = sum(
        len(packed.data) + len(packed.mask)
        for packed in (
            pack_spectrum(split_frames(_sprite_sheet(8), 8)),
            pack_spectrum(split_frames(_sprite_sheet(1), 1)),
        )
    )
    expected_budget = project.budgets.static_data_bytes // 2
    assert expected_total > expected_budget  # the case is real over-budget, not contrived

    with pytest.raises(ValueError, match="packed sprites are") as excinfo:
        render_project(project, directory / "build")

    message = str(excinfo.value)
    assert f"{expected_total} bytes" in message
    assert f"{expected_budget} bytes" in message
