"""Real-toolchain proof that the Spectrum and CPC blitters draw the packed sprite.

Companion to `tests/test_toolchain_integration.py`: same skip-when-absent
pattern, but aimed at `plat_sprite` specifically. For each target, two claims
are checked separately, because a compile is not a drawing:

1. A Studio project carrying a real 16x16 sprite asset builds through the
   normal `render_project` -> `build_project` path and produces a bootable
   artifact (TAP on Spectrum, DSK on CPC).
2. The artifact, run under a real emulator, shows the sprite actually landed
   on screen. What "shows" means differs by target, and deliberately so:

   - Spectrum, booted under ZEsarUX: the exact bytes the emulator's screen
     memory holds at the sprite's cells match `spriting.pack_spectrum`'s
     packed data, combined with a known non-zero background through the
     blitter's own `(screen & mask) | data` formula. The packer's byte order
     is already verified independently (see `spriting.py`'s module
     docstring), so an exact match here pins any addressing or masking bug
     on the C blitter, not on the packer.
   - CPC, booted under Caprice32: `docs/STUDIO_ROADMAP.md` records that this
     install's Caprice32 does not resolve `CAP32_SNAPSHOT` as an autocmd --
     passing it types the literal characters into the emulated machine
     instead of dumping a snapshot -- so CPC memory cannot be read back the
     way Spectrum memory can. The strongest evidence this machine affords is
     a screenshot: build the sprite program and an otherwise identical
     control that never calls `plat_sprite`, and check their post-boot
     screens differ, with the sprite build alone showing real drawn area.
     That is weaker than the Spectrum's exact-byte match -- it shows
     something changed where the sprite should be, not that the packed
     bytes landed unmangled -- and that asymmetry is a known, already
     documented property of this project, not something glossed over here.

The Spectrum sprite is placed at character row 7/8 on purpose: row 7 is the
last row of the Spectrum screen's first third and row 8 is the first row of
the second, so the two-cell-tall sprite's second half is where a wrong
address computation (naive offset arithmetic instead of a fresh
`zx_cxy2saddr` call) would show up. The CPC screen has no equivalent third
boundary to target -- `cpct_drawSpriteMasked.asm` crosses its own internal
8-pixel-line block boundary unconditionally, on every character row, not at
one particular row -- so the CPC sprite's placement is unremarkable by
comparison; see the guard comment on `plat_sprite` in
`resources/studio_lib/cpc/platform.c` for that arithmetic.
"""

from __future__ import annotations

import shutil
import socket
import subprocess
import time
from pathlib import Path

import pytest
from PIL import Image

from llm_z80 import resolve_cpct_path
from llmz80.quality.emulator_smoke import smoke_test
from llmz80.studio import compiler as compiler_module
from llmz80.studio.models import AssetSpec, TargetPlatform
from llmz80.core.state_contract import SYMBOLS_BY_NAME, REQUIRED_SYMBOLS, required_declarations
from llmz80.studio.services import StudioService
from llmz80.studio.spriting import pack_spectrum

#: Real model-output sprite sheets, copied in from a genuine end-to-end Studio
#: run (`studio-projects/profanacion/assets/*.png`; see module docstring
#: below for why three sprites, not one). Copied into the repo rather than
#: read from that directory, which is a scratch project and not a fixture.
FIXTURES = Path(__file__).parent / "fixtures"

zcc_missing = pytest.mark.skipif(shutil.which("zcc") is None, reason="z88dk is not installed")
zesarux_missing = pytest.mark.skipif(
    shutil.which("zesarux") is None, reason="ZEsarUX is not installed"
)
make_missing = pytest.mark.skipif(shutil.which("make") is None, reason="make is not installed")
cpct_missing = pytest.mark.skipif(resolve_cpct_path() is None, reason="CPCtelera is not installed")
cap32_missing = pytest.mark.skipif(
    shutil.which("cap32") is None and shutil.which("caprice32") is None,
    reason="no Caprice32 binary (cap32/caprice32) is installed",
)

#: Character cell the sprite is drawn at. Row 7/8 straddles the display
#: file's first/second third on purpose (see module docstring).
SPRITE_COL = 2
SPRITE_ROW = 7
#: Non-zero fill the test program writes under the sprite before drawing it,
#: so the blitter's mask/data combine is actually exercised rather than the
#: trivial (screen & mask) | data == data case a zero background gives.
BACKGROUND_BYTE = 0xAA

#: The required half of the observable state contract, which `build_project`
#: now refuses a build for not carrying into the linker map. These programs
#: exist to prove the sprite blitter links and draws, not to be games, but
#: they are built through the real `StudioService.build`, so they have to
#: honour the contract like anything else that goes through it. Assigned in
#: `main` as well as defined, because a global no translation unit ever reads
#: is exactly what the gate's diagnostic warns can be optimised away.
#: Both are derived from the contract rather than spelled out, so a symbol
#: added to it does not break these seven real-toolchain tests with a linker
#: diagnostic that points at the toolchain instead of at the stale fixture.
CONTRACT_STATE = required_declarations()
#: Assignments for the symbols this fixture defines, which is not every
#: required one: the platform library defines and keeps `g_worst_frame_cost`
#: itself, so a program that assigns it would be writing over the library's
#: own measurement even where the linker allowed the definition.
CONTRACT_INIT = "".join(
    f"    {name} = 0;\n"
    for name in REQUIRED_SYMBOLS
    if not SYMBOLS_BY_NAME[name].provided_by_library
)


def _sprite_image() -> Image.Image:
    """A 16x16 RGBA sprite that is neither all-opaque nor all-transparent."""
    image = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    pixels = image.load()
    for y in range(16):
        for x in range(16):
            opaque = ((x + y) % 3 == 0) or (4 <= x <= 11 and 4 <= y <= 11 and (x + y) % 2 == 0)
            pixels[x, y] = (255, 255, 255, 255) if opaque else (0, 0, 0, 0)
    return image


def _build_sprite_project(tmp_path: Path):
    """Render and build a Spectrum project whose program draws one sprite."""
    workspace = tmp_path / "projects"
    service = StudioService.at(workspace)
    project, directory = service.create_project("SpriteProbe", TargetPlatform.SPECTRUM)

    sprite_path = tmp_path / "hero.png"
    _sprite_image().save(sprite_path)
    service.add_asset(project, directory, sprite_path)

    program_dir = directory / project.program_dir
    program_dir.mkdir(parents=True, exist_ok=True)
    (program_dir / "main.c").write_text(
        f"""#include <arch/zx.h>
#include "platform.h"

{CONTRACT_STATE}
void main(void) {{
    unsigned char half, line;
    plat_init();
{CONTRACT_INIT}
    /* Pre-fill the sprite's cells with a known non-zero pattern so the
     * blitter's (screen & mask) | data formula is actually exercised. */
    for (half = 0; half < 2; ++half) {{
        unsigned char *base = (unsigned char *)zx_cxy2saddr({SPRITE_COL}, {SPRITE_ROW} + half);
        for (line = 0; line < 8; ++line) {{
            unsigned char *at = base + ((unsigned int)line << 8);
            at[0] = 0x{BACKGROUND_BYTE:02X};
            at[1] = 0x{BACKGROUND_BYTE:02X};
        }}
    }}
    plat_sprite({SPRITE_COL}, {SPRITE_ROW}, 0, 0);
    while (1) {{ }}
}}
""",
        encoding="utf-8",
    )

    build = service.build(project, directory)
    return build


@zcc_missing
def test_spectrum_sprite_project_compiles_and_links(tmp_path: Path):
    build = _build_sprite_project(tmp_path)

    assert build.success, build.report.get("stderr") or build.report.get("stdout")
    assert build.artifact is not None
    assert build.artifact.is_file()
    assert build.artifact.stat().st_size > 0
    sprites_h = (build.output_dir / "src" / "sprites.h").read_text(encoding="utf-8")
    assert "#define SPRITE_COUNT 1" in sprites_h


def _screen_address(col: int, row: int, line: int) -> int:
    """Same non-linear formula `zx_cxy2saddr` + the `line << 8` stride use."""
    third, subrow = divmod(row, 8)
    return 0x4000 + third * 2048 + subrow * 32 + col + (line << 8)


def _free_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def _connect_zrcp(port: int, deadline: float) -> socket.socket:
    last_error: OSError | None = None
    while time.monotonic() < deadline:
        try:
            connection = socket.create_connection(("127.0.0.1", port), timeout=0.3)
            connection.settimeout(0.2)
            return connection
        except OSError as exc:
            last_error = exc
            time.sleep(0.05)
    raise OSError(f"ZEsarUX remote protocol did not start: {last_error}")


def _zrcp_query(connection: socket.socket, command: str) -> str:
    connection.sendall((command + "\n").encode("utf-8"))
    time.sleep(0.12)
    chunks: list[bytes] = []
    try:
        while True:
            data = connection.recv(65536)
            if not data:
                break
            chunks.append(data)
    except (TimeoutError, socket.timeout):
        pass
    return b"".join(chunks).decode("utf-8", errors="ignore")


@zcc_missing
@zesarux_missing
def test_spectrum_blitter_draws_the_exact_packed_bytes(tmp_path: Path):
    build = _build_sprite_project(tmp_path)
    assert build.success, build.report.get("stderr") or build.report.get("stdout")
    artifact = build.artifact
    assert artifact is not None and artifact.is_file()

    expected_data = pack_spectrum([_sprite_image()]).data
    assert len(expected_data) == 32  # 16 lines * 2 bytes/line, one frame
    expected_screen = bytes((BACKGROUND_BYTE | byte) & 0xFF for byte in expected_data)

    port = _free_local_port()
    command = [
        "zesarux",
        "--noconfigfile",
        "--machine",
        "48k",
        "--vo",
        "null",
        "--ao",
        "null",
        "--fastautoload",
        "--quickexit",
        "--enable-remoteprotocol",
        "--remoteprotocol-port",
        str(port),
        "--exit-after",
        "16",
        str(artifact),
    ]
    process = subprocess.Popen(
        command,
        cwd=artifact.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        connection = _connect_zrcp(port, time.monotonic() + 3.0)
        with connection:
            # Give the tap time to autoload and the program time to run.
            time.sleep(3.5)
            # The ZRCP connection banner's own trailing prompt otherwise
            # corrupts the parse of whichever query is sent first.
            _zrcp_query(connection, "get-version")

            actual = bytearray()
            for half in range(2):
                for line in range(8):
                    address = _screen_address(SPRITE_COL, SPRITE_ROW + half, line)
                    answer = _zrcp_query(connection, f"read-memory {address} 2")
                    digits = "".join(
                        ch for ch in answer.split("command@")[0] if ch in "0123456789abcdefABCDEF"
                    )[:4]
                    assert len(digits) == 4, f"no memory read back for {address:#06x}: {answer!r}"
                    actual.append(int(digits[0:2], 16))
                    actual.append(int(digits[2:4], 16))
    finally:
        process.terminate()
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate(timeout=5)

    assert bytes(actual) == expected_screen


#: Character cell the CPC sprite is drawn at: well inside the mode-1 default
#: grid (40x25, see codegen.TARGET_GRID) and away from every edge, so this
#: exercises the ordinary case rather than the plat_sprite bounds guard.
CPC_SPRITE_COL = 18
CPC_SPRITE_ROW = 10


def _build_cpc_project(tmp_path: Path, *, draw_sprite: bool):
    """Render and build a CPC project that either draws one sprite, or is an
    otherwise identical control that does not.

    With `draw_sprite=False` no sprite asset is added at all -- the same
    "existing project, no assets, SPRITE_COUNT 0" shape every pre-Task-7
    project already builds as -- so the only possible source of a screen
    difference between the two builds is `plat_sprite` actually drawing.
    """
    workspace = tmp_path / f"projects_{draw_sprite}"
    service = StudioService.at(workspace)
    project, directory = service.create_project("CpcSpriteProbe", TargetPlatform.AMSTRAD_CPC)

    if draw_sprite:
        sprite_path = tmp_path / "cpc_hero.png"
        _sprite_image().save(sprite_path)
        service.add_asset(project, directory, sprite_path)

    program_dir = directory / project.program_dir
    program_dir.mkdir(parents=True, exist_ok=True)
    draw_call = (
        f"    plat_sprite({CPC_SPRITE_COL}, {CPC_SPRITE_ROW}, 0, 0);\n" if draw_sprite else ""
    )
    (program_dir / "main.c").write_text(
        f"""#include <cpctelera.h>
#include "platform.h"

{CONTRACT_STATE}
void main(void) {{
    plat_init();
    plat_clear();
{CONTRACT_INIT}{draw_call}    while (1) {{ }}
}}
""",
        encoding="utf-8",
    )

    return service.build(project, directory)


@make_missing
@cpct_missing
def test_cpc_sprite_project_compiles_and_links(tmp_path: Path):
    build = _build_cpc_project(tmp_path, draw_sprite=True)

    assert build.success, build.report.get("stderr") or build.report.get("stdout")
    assert build.artifact is not None
    assert build.artifact.is_file()
    assert build.artifact.stat().st_size > 0
    sprites_h = (build.output_dir / "src" / "sprites.h").read_text(encoding="utf-8")
    assert "#define SPRITE_COUNT 1" in sprites_h
    # The default CPC video mode is mode 1 (see samples.blank_project); its
    # cells pack four pixels per byte, so a 16-pixel-wide sprite is 4 bytes
    # wide.
    assert "#define SPRITE_BYTES_WIDE 4" in sprites_h


@make_missing
@cpct_missing
def test_cpc_sprite_project_with_no_assets_still_builds(tmp_path: Path):
    """The control build from the runtime test below, checked on its own:
    a project with no sprite assets gets SPRITE_COUNT 0 and must still build
    and link cleanly, exactly as it did before plat_sprite had a body."""
    build = _build_cpc_project(tmp_path, draw_sprite=False)

    assert build.success, build.report.get("stderr") or build.report.get("stdout")
    sprites_h = (build.output_dir / "src" / "sprites.h").read_text(encoding="utf-8")
    assert "#define SPRITE_COUNT 0" in sprites_h


@make_missing
@cpct_missing
@cap32_missing
def test_cpc_blitter_visibly_draws_where_the_control_build_does_not(tmp_path: Path):
    """See the module docstring for why a screenshot, not exact memory bytes,
    is the ceiling for CPC evidence here.

    `llmz80.quality.emulator_smoke.smoke_test` already knows how to run
    Caprice32 headlessly and capture screenshots at fixed points in the
    boot sequence (`_run_caprice32`): index 0 is taken before the program
    runs, index 1 right after it has run but before any scripted input --
    exactly the moment `plat_sprite` has already drawn and nothing later
    could have changed the screen since. Reusing that machinery, rather than
    re-implementing screenshot timing here, is what keeps this test's timing
    identical to what the project's own runtime gate already relies on.
    """
    sprite_build = _build_cpc_project(tmp_path, draw_sprite=True)
    control_build = _build_cpc_project(tmp_path, draw_sprite=False)
    assert sprite_build.success, sprite_build.report.get("stderr") or sprite_build.report.get(
        "stdout"
    )
    assert control_build.success, control_build.report.get("stderr") or control_build.report.get(
        "stdout"
    )

    sprite_report = smoke_test(sprite_build.output_dir, "amstrad_cpc", full=True, seconds=3)
    control_report = smoke_test(control_build.output_dir, "amstrad_cpc", full=True, seconds=3)

    assert not sprite_report.get("emulator_error"), sprite_report.get("emulator_error")
    assert not control_report.get("emulator_error"), control_report.get("emulator_error")
    sprite_frames = sprite_report["frames"]
    control_frames = control_report["frames"]
    assert len(sprite_frames) >= 2, sprite_report
    assert len(control_frames) >= 2, control_report

    sprite_after_boot = sprite_frames[1]
    control_after_boot = control_frames[1]

    # The two builds' post-boot screens must differ, and specifically because
    # the sprite build shows meaningfully more non-background pixels than the
    # control's flat cleared screen -- not merely differ by some incidental
    # emulator artifact.
    assert sprite_after_boot["sha256"] != control_after_boot["sha256"]
    # This reading is bimodal, and 0.98 sits in the empty gap between its two
    # modes rather than being a tolerance around one of them. Measured over 18
    # runs of this same command: every run whose program actually got as far
    # as `plat_clear` read exactly 1.0 -- a genuinely flat screen has one
    # colour and no spread to allow for -- and every run whose program never
    # ran read 0.950 to 0.972, because the screen was still Caprice32's BASIC
    # text with `Bad command` on it after the autotyped `run"program.bin"`
    # arrived corrupted (see `emulator_smoke._run_caprice32` on the host
    # gamepad). So a failure here does not mean the ceiling is too tight; it
    # means the emulated machine never ran the program, and the comparison
    # below is about to be between two BASIC screens. Lowering the number to
    # accept 0.95 would make this test pass without either build having drawn
    # anything, which is the one outcome it exists to rule out.
    assert control_after_boot["dominant_fraction"] > 0.98, (
        f"the control screen is not flat ({control_after_boot['dominant_fraction']}), so the "
        f"program never ran and nothing below is comparing drawn screens: "
        f"{control_after_boot['path']}"
    )
    assert sprite_after_boot["non_dominant_pixels"] > control_after_boot["non_dominant_pixels"] + 30


# ---------------------------------------------------------------------------
# The link, not just the compile: a project with several sprites whose own
# main.c includes sprites.h, exactly like a real end-to-end Studio run's
# program does when it wants to choose which sprite plat_sprite draws.
#
# The single-sprite tests above never exercise this: their main.c only
# includes platform.h, so sprites.h is only ever pulled into one translation
# unit (platform.c itself). A real generated program that also includes
# sprites.h -- the natural thing to do once SPRITE_HERO/SPRITE_ENEMY/etc are
# needed in the caller's own code -- pulls the same header into a second
# translation unit, main.c. Before the header/source split in
# `sprite_header.py`, that made both translation units define
# `sprite_data[]`, `sprite_mask[]`, `sprite_frame_offset[][]`,
# `sprite_frames[]` and `sprite_attribute[]`, and the linker refused with
# `error: duplicate definition: main_c::_sprite_data` and four siblings.
# ---------------------------------------------------------------------------


def _add_sprite_fixture(directory: Path, asset_id: str, fixture_name: str, *, frames: int = 4):
    """Copy a real fixture sheet into the project's assets/ under `asset_id`."""
    assets_dir = directory / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{asset_id}.png"
    shutil.copy2(FIXTURES / fixture_name, assets_dir / filename)
    with Image.open(assets_dir / filename) as image:
        width, height = image.size
    return AssetSpec(
        id=asset_id, source=f"assets/{filename}", width=width, height=height, frames=frames
    )


def _build_multi_sprite_project(tmp_path: Path, platform: TargetPlatform):
    """Three real sprites (from a genuine Studio end-to-end run -- see
    `tests/fixtures/sprite_sheet_profanacion_*.png`), in a project whose own
    main.c includes sprites.h and picks a sprite by its SPRITE_<ID> constant,
    the same way the real generated program that hit this bug did.
    """
    workspace = tmp_path / f"projects_{platform.value}"
    service = StudioService.at(workspace)
    project, directory = service.create_project("MultiSprite", platform)
    project.assets = [
        _add_sprite_fixture(directory, "hero", "sprite_sheet_profanacion_hero.png"),
        _add_sprite_fixture(directory, "enemy", "sprite_sheet_profanacion_enemy.png"),
        _add_sprite_fixture(directory, "pellet", "sprite_sheet_profanacion_pellet.png"),
    ]

    program_dir = directory / project.program_dir
    program_dir.mkdir(parents=True, exist_ok=True)
    arch_include = (
        "#include <arch/zx.h>\n"
        if platform is TargetPlatform.SPECTRUM
        else "#include <cpctelera.h>\n"
    )
    (program_dir / "main.c").write_text(
        f"""{arch_include}#include "platform.h"
#include "sprites.h"

{CONTRACT_STATE}
void main(void) {{
    plat_init();
{CONTRACT_INIT}    plat_sprite(2, 7, SPRITE_HERO, 0);
    plat_sprite(4, 7, SPRITE_ENEMY, 0);
    plat_sprite(6, 7, SPRITE_PELLET, 0);
    while (1) {{ }}
}}
""",
        encoding="utf-8",
    )
    return service.build(project, directory)


@zcc_missing
def test_spectrum_multi_sprite_project_with_main_including_sprites_h_links(tmp_path: Path):
    """The link proof for Spectrum: three sprites, main.c and platform.c both
    including sprites.h, built and linked through the real z88dk toolchain."""
    build = _build_multi_sprite_project(tmp_path, TargetPlatform.SPECTRUM)

    assert build.success, build.report.get("stderr") or build.report.get("stdout")
    assert build.artifact is not None and build.artifact.is_file()
    assert build.artifact.stat().st_size > 0
    assert (build.output_dir / "src" / "sprites.c").is_file()
    sprites_h = (build.output_dir / "src" / "sprites.h").read_text(encoding="utf-8")
    assert "#define SPRITE_COUNT 3" in sprites_h


@make_missing
@cpct_missing
def test_cpc_multi_sprite_project_with_main_including_sprites_h_links(tmp_path: Path):
    """The link proof for CPC: same three-sprite project, built through the
    real CPCtelera/SDCC toolchain via `make`. `sprites.c` reaches the build
    the same way every other file in src/ does -- build_config.mk globs
    `$(SRCDIR)/*.c` -- so nothing here has to tell CPCtelera about it by name.
    """
    build = _build_multi_sprite_project(tmp_path, TargetPlatform.AMSTRAD_CPC)

    assert build.success, build.report.get("stderr") or build.report.get("stdout")
    assert build.artifact is not None and build.artifact.is_file()
    assert build.artifact.stat().st_size > 0
    assert (build.output_dir / "src" / "sprites.c").is_file()
    sprites_h = (build.output_dir / "src" / "sprites.h").read_text(encoding="utf-8")
    assert "#define SPRITE_COUNT 3" in sprites_h


def _pre_split_render_sprite_header(sprites):
    """The header exactly as `render_sprite_header` rendered it before the
    header/source split -- definitions and all, `static` byte arrays aside.
    Reproduced here (not imported) so this test does not depend on the buggy
    code still existing anywhere in the module under test; it exists only to
    prove the real toolchain rejects this shape, on purpose, when it comes
    back.
    """
    from llmz80.studio.sprite_header import _checked_id, _c_byte_array

    ids = [_checked_id(sprite_id) for sprite_id in sprites]
    count = len(ids)
    width_bytes_values = {packed.width_bytes for packed in sprites.values()}
    bytes_wide = next(iter(width_bytes_values), 2)

    lines = [
        "#ifndef LLMZ80_SPRITES_H",
        "#define LLMZ80_SPRITES_H",
        "",
    ]
    for index, sprite_id in enumerate(ids):
        lines.append(f"#define SPRITE_{sprite_id.upper()} {index}")
    lines.append(f"#define SPRITE_COUNT {count}")
    lines.append(f"#define SPRITE_BYTES_WIDE {bytes_wide}")
    lines.append("")
    if count == 0:
        lines.append("#endif")
        return "\n".join(lines) + "\n"

    max_frames = max(packed.frames for packed in sprites.values())
    lines.append("#if SPRITE_COUNT > 0")
    lines.append("")
    for sprite_id, packed in sprites.items():
        lines.append(_c_byte_array(f"sprite_{sprite_id}_data", packed.data))
        if packed.mask:
            lines.append(_c_byte_array(f"sprite_{sprite_id}_mask", packed.mask))
        lines.append("")
    data_pointers = ", ".join(f"sprite_{sprite_id}_data" for sprite_id in ids)
    lines.append(f"const unsigned char *const sprite_data[] = {{ {data_pointers} }};")
    mask_pointers = ", ".join(
        f"sprite_{sprite_id}_data" if not sprites[sprite_id].mask else f"sprite_{sprite_id}_mask"
        for sprite_id in ids
    )
    lines.append(f"const unsigned char *const sprite_mask[] = {{ {mask_pointers} }};")
    lines.append("")
    offset_rows = []
    for sprite_id in ids:
        packed = sprites[sprite_id]
        real = [frame * packed.bytes_per_frame for frame in range(packed.frames)]
        padded = real + [real[-1]] * (max_frames - len(real))
        offset_rows.append("{" + ", ".join(str(value) for value in padded) + "}")
    lines.append(
        f"const unsigned int sprite_frame_offset[][{max_frames}] = {{\n    "
        + ",\n    ".join(offset_rows)
        + "\n};"
    )
    lines.append("")
    frame_counts = ", ".join(str(sprites[sprite_id].frames) for sprite_id in ids)
    lines.append(f"const unsigned char sprite_frames[] = {{{frame_counts}}};")
    lines.append("")
    attribute_bytes = ", ".join(str(sprites[sprite_id].attribute) for sprite_id in ids)
    lines.append(f"const unsigned char sprite_attribute[] = {{{attribute_bytes}}};")
    lines.append("")
    lines.append("#endif /* SPRITE_COUNT */")
    lines.append("")
    lines.append("#endif /* LLMZ80_SPRITES_H */")
    return "\n".join(lines) + "\n"


@zcc_missing
def test_a_reintroduced_definition_in_the_header_fails_the_real_link(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """The regression proof: put a definition back in sprites.h (as if
    someone "simplified" the split away) and watch the real linker refuse to
    link, the same way it refused the real failed run this whole test module
    exists to guard against. If this test ever passes, the guard is gone.
    """
    monkeypatch.setattr(compiler_module, "render_sprite_header", _pre_split_render_sprite_header)
    # Also revert sprites.c to a no-op include, matching the pre-fix repo
    # exactly: one file (sprites.h) carrying the definitions, pulled into two
    # translation units (platform.c and this test's main.c). Leaving the real
    # render_sprite_source in place would instead fail earlier, while
    # compiling sprites.c itself (it would redefine what the reverted header
    # already defines) -- a real failure too, but not the cross-file linker
    # error `error: duplicate definition: main_c::_sprite_data` the actual
    # failed run hit, which is what this test reproduces on purpose.
    monkeypatch.setattr(
        compiler_module, "render_sprite_source", lambda sprites: '#include "sprites.h"\n'
    )

    build = _build_multi_sprite_project(tmp_path, TargetPlatform.SPECTRUM)

    assert not build.success
    diagnostics = (build.report.get("stdout") or "") + (build.report.get("stderr") or "")
    assert "duplicate definition" in diagnostics
    assert "_sprite_data" in diagnostics
