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
from llmz80.studio.models import GenreId, TargetPlatform
from llmz80.studio.services import StudioService
from llmz80.studio.spriting import pack_spectrum

zcc_missing = pytest.mark.skipif(shutil.which("zcc") is None, reason="z88dk is not installed")
zesarux_missing = pytest.mark.skipif(
    shutil.which("zesarux") is None, reason="ZEsarUX is not installed"
)
make_missing = pytest.mark.skipif(shutil.which("make") is None, reason="make is not installed")
cpct_missing = pytest.mark.skipif(
    resolve_cpct_path() is None, reason="CPCtelera is not installed"
)
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


def _sprite_image() -> Image.Image:
    """A 16x16 RGBA sprite that is neither all-opaque nor all-transparent."""
    image = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    pixels = image.load()
    for y in range(16):
        for x in range(16):
            opaque = ((x + y) % 3 == 0) or (
                4 <= x <= 11 and 4 <= y <= 11 and (x + y) % 2 == 0
            )
            pixels[x, y] = (255, 255, 255, 255) if opaque else (0, 0, 0, 0)
    return image


def _build_sprite_project(tmp_path: Path):
    """Render and build a Spectrum project whose program draws one sprite."""
    workspace = tmp_path / "projects"
    service = StudioService.at(workspace)
    project, directory = service.create_project(
        "SpriteProbe", TargetPlatform.SPECTRUM, GenreId.SINGLE_SCREEN_COLLECT
    )

    sprite_path = tmp_path / "hero.png"
    _sprite_image().save(sprite_path)
    service.add_asset(project, directory, sprite_path)

    program_dir = directory / project.program_dir
    program_dir.mkdir(parents=True, exist_ok=True)
    (program_dir / "main.c").write_text(
        f"""#include <arch/zx.h>
#include "platform.h"

void main(void) {{
    unsigned char half, line;
    plat_init();
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
        "zesarux", "--noconfigfile", "--machine", "48k",
        "--vo", "null", "--ao", "null",
        "--fastautoload", "--quickexit",
        "--enable-remoteprotocol", "--remoteprotocol-port", str(port),
        "--exit-after", "16", str(artifact),
    ]
    process = subprocess.Popen(
        command, cwd=artifact.parent, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
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
    project, directory = service.create_project(
        "CpcSpriteProbe", TargetPlatform.AMSTRAD_CPC, GenreId.SINGLE_SCREEN_COLLECT
    )

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

void main(void) {{
    plat_init();
    plat_clear();
{draw_call}    while (1) {{ }}
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
    # The default CPC video mode is mode 1 (see packs.py); its cells pack
    # four pixels per byte, so a 16-pixel-wide sprite is 4 bytes wide.
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
    assert control_build.success, control_build.report.get(
        "stderr"
    ) or control_build.report.get("stdout")

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
    assert control_after_boot["dominant_fraction"] > 0.98
    assert sprite_after_boot["non_dominant_pixels"] > control_after_boot["non_dominant_pixels"] + 30
