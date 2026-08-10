"""Owned multi-file layouts and deterministic retro image conversion."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Iterable

from PIL import Image

from .runtime_contracts import runtime_header_path


ROOT = Path(__file__).resolve().parents[2]


def _identifier(path: Path) -> str:
    name = re.sub(r"[^A-Za-z0-9_]", "_", path.stem).strip("_") or "asset"
    return f"asset_{name.lower()}"


def pack_spectrum(image: Image.Image) -> tuple[bytes, int, int]:
    mono = image.convert("L")
    width, height = mono.size
    if width == 0 or height == 0 or width % 8:
        raise ValueError("Spectrum assets must have non-zero dimensions and width divisible by 8")
    pixels = mono.load()
    output = bytearray()
    for y in range(height):
        for x_byte in range(0, width, 8):
            value = 0
            for bit in range(8):
                if pixels[x_byte + bit, y] >= 128:
                    value |= 0x80 >> bit
            output.append(value)
    return bytes(output), width // 8, height


def _mode0_byte(left: int, right: int) -> int:
    return (
        ((left & 1) << 7) | ((right & 1) << 6)
        | ((left & 2) << 2) | ((right & 2) << 1)
        | ((left & 4) << 3) | ((right & 4) << 2)
        | ((left & 8) >> 2) | ((right & 8) >> 3)
    )


def _mode1_byte(values: list[int]) -> int:
    p0, p1, p2, p3 = values
    return ((p0 & 1) << 7) | ((p1 & 1) << 6) | ((p2 & 1) << 5) | ((p3 & 1) << 4) | ((p0 & 2) << 2) | ((p1 & 2) << 1) | (p2 & 2) | ((p3 & 2) >> 1)


def pack_cpc(image: Image.Image, mode: int) -> tuple[bytes, int, int]:
    if mode not in {0, 1}:
        raise ValueError("CPC asset mode must be 0 or 1")
    colours = 16 if mode == 0 else 4
    indexed = image.convert("L")
    width, height = indexed.size
    pixels_per_byte = 2 if mode == 0 else 4
    if width == 0 or height == 0 or width % pixels_per_byte:
        raise ValueError(f"CPC mode {mode} asset width must be divisible by {pixels_per_byte}")
    pixels = indexed.load()
    output = bytearray()
    for y in range(height):
        for x in range(0, width, pixels_per_byte):
            values = [min(colours - 1, pixels[x + offset, y] * colours // 256)
                      for offset in range(pixels_per_byte)]
            output.append(_mode0_byte(*values) if mode == 0 else _mode1_byte(values))
    return bytes(output), width // pixels_per_byte, height


def convert_assets(asset_paths: Iterable[Path], platform: str, output_dir: Path, cpc_mode: int = 1) -> list[dict]:
    records = []
    definitions = []
    declarations = []
    for path in asset_paths:
        if not path.is_file():
            raise FileNotFoundError(f"asset does not exist: {path}")
        with Image.open(path) as image:
            data, width_bytes, height = (
                pack_spectrum(image) if platform == "spectrum" else pack_cpc(image, cpc_mode)
            )
        symbol = _identifier(path)
        values = ", ".join(f"0x{byte:02X}" for byte in data)
        definitions.append(f"const unsigned char {symbol}[{len(data)}] = {{{values}}};")
        declarations.extend([
            f"extern const unsigned char {symbol}[{len(data)}];",
            f"#define {symbol.upper()}_WIDTH_BYTES {width_bytes}",
            f"#define {symbol.upper()}_HEIGHT {height}",
        ])
        records.append({"source": str(path), "symbol": symbol, "size_bytes": len(data),
                        "width_bytes": width_bytes, "height": height})
    if records:
        (output_dir / "assets.h").write_text(
            "#ifndef LLMZ80_ASSETS_H\n#define LLMZ80_ASSETS_H\n\n"
            + "\n".join(declarations) + "\n\n#endif\n", encoding="utf-8")
        (output_dir / "assets.c").write_text(
            '#include "assets.h"\n\n' + "\n\n".join(definitions) + "\n", encoding="utf-8")
    return records


def create_project_layout(output_dir: Path, platform: str, code: str,
                          assets: Iterable[Path] = (), cpc_mode: int = 1) -> dict:
    src = output_dir / "src"
    src.mkdir(parents=True, exist_ok=True)
    (output_dir / "obj").mkdir(exist_ok=True)
    # Root main.c remains the correction-loop source of truth; src/main.c is
    # synchronised before every build.
    (output_dir / "main.c").write_text(code, encoding="utf-8")
    (src / "main.c").write_text(code, encoding="utf-8")
    shutil.copy2(runtime_header_path(platform), src / "llmz80_runtime.h")
    records = convert_assets(assets, platform, src, cpc_mode=cpc_mode)
    template = (
        ROOT / "examples/spectrum/common/Makefile.template"
        if platform == "spectrum" else ROOT / "templates/amstrad_cpc/Makefile"
    )
    if template.exists():
        shutil.copy2(template, output_dir / "Makefile")
    manifest = {
        "schema_version": 1, "mode": "project", "platform": platform,
        "owned_files": sorted(str(path.relative_to(output_dir)) for path in src.iterdir()),
        "assets": records,
    }
    (output_dir / "project_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest
