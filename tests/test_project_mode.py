import shutil
import subprocess

import pytest
from PIL import Image

from llmz80.core.project_mode import create_project_layout, pack_cpc, pack_spectrum
from llmz80.core.toolchain import prepare_amstrad_cpc_build_project, resolve_cpct_path


def test_spectrum_bitmap_packing_is_deterministic():
    image = Image.new("1", (8, 1))
    image.putpixel((0, 0), 1)
    image.putpixel((7, 0), 1)
    data, width, height = pack_spectrum(image)
    assert data == bytes([0x81])
    assert (width, height) == (1, 1)


def test_cpc_mode_packers_have_expected_layout():
    mode0 = Image.new("L", (2, 1))
    mode0.putdata([255, 0])
    data0, width0, _ = pack_cpc(mode0, 0)
    assert data0 == bytes([0xAA])
    mode1 = Image.new("L", (4, 1))
    mode1.putdata([255, 0, 0, 0])
    data1, width1, _ = pack_cpc(mode1, 1)
    assert data1 == bytes([0x88])
    assert (width0, width1) == (1, 1)


def test_owned_project_layout_contains_only_fixed_structure(tmp_path):
    asset = tmp_path / "hero.png"
    Image.new("1", (8, 8), 1).save(asset)
    output = tmp_path / "run"
    output.mkdir()
    manifest = create_project_layout(output, "spectrum", "void main(void){}", [asset])
    assert (output / "src/main.c").exists()
    assert (output / "src/llmz80_runtime.h").exists()
    assert (output / "src/assets.c").exists()
    assert manifest["assets"][0]["symbol"] == "asset_hero"


def test_missing_asset_fails_before_conversion(tmp_path):
    try:
        create_project_layout(tmp_path, "spectrum", "void main(void){}", [tmp_path / "missing.png"])
    except FileNotFoundError as exc:
        assert "missing.png" in str(exc)
    else:
        raise AssertionError("missing asset was accepted")


@pytest.mark.skipif(shutil.which("zcc") is None, reason="Z88DK is not installed")
def test_spectrum_project_fixture_compiles(tmp_path):
    image = tmp_path / "dot.png"
    Image.new("1", (8, 8), 1).save(image)
    code = '#include <arch/zx.h>\n#include "assets.h"\nvoid main(void){zx_cls(7);while(1){}}\n'
    create_project_layout(tmp_path, "spectrum", code, [image])
    result = subprocess.run(
        [
            "zcc",
            "+zx",
            "-vn",
            "-O3",
            "-clib=sdcc_iy",
            "src/main.c",
            "src/assets.c",
            "-o",
            "output",
            "-create-app",
            "-subtype=default",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "output.tap").stat().st_size > 0


@pytest.mark.skipif(shutil.which("make") is None, reason="make is not installed")
def test_cpc_project_fixture_compiles(tmp_path):
    cpct_path = resolve_cpct_path()
    if cpct_path is None:
        pytest.skip("CPCtelera is not installed")
    image = tmp_path / "dot.png"
    Image.new("L", (4, 2), 255).save(image)
    code = (
        '#include <cpctelera.h>\n#include "assets.h"\n'
        "void main(void){cpct_disableFirmware();cpct_setVideoMode(1);"
        "cpct_drawSprite((void*)asset_dot,CPCT_VMEM_START,ASSET_DOT_WIDTH_BYTES,"
        "ASSET_DOT_HEIGHT);while(1){}}\n"
    )
    create_project_layout(tmp_path, "amstrad_cpc", code, [image])
    assert prepare_amstrad_cpc_build_project(tmp_path, cpct_path)
    result = subprocess.run(
        ["make", f"CPCT_PATH={cpct_path}/"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert any(path.stat().st_size > 0 for path in tmp_path.glob("*.dsk"))
