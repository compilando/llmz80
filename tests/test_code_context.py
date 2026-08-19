"""Tests for compile-aware example context extraction."""

from llmz80.core.code_context import (
    build_embedding_text,
    build_example_context,
    discover_support_files,
    is_self_contained_c_context,
)


def test_build_example_context_includes_support_files_and_makefile(tmp_path):
    examples_dir = tmp_path / "examples" / "amstrad_cpc"
    project_dir = examples_dir / "easy" / "sprites"
    src_dir = project_dir / "src"
    src_dir.mkdir(parents=True)

    main_c = src_dir / "main.c"
    main_c.write_text(
        '#include <cpctelera.h>\n#include "sprites.h"\n\nvoid main(void) {}\n',
        encoding="utf-8",
    )
    (src_dir / "sprites.h").write_text("extern const unsigned char sprite[];\n", encoding="utf-8")
    (src_dir / "sprites.c").write_text(
        "const unsigned char sprite[] = { 0x00 };\n", encoding="utf-8"
    )
    (project_dir / "Makefile").write_text("include cfg/build_config.mk\n", encoding="utf-8")

    context = build_example_context(main_c, examples_dir, max_size=20000)

    assert "// FILE: easy/sprites/src/main.c" in context
    assert "// SUPPORT FILE: easy/sprites/src/sprites.h" in context
    assert "// SUPPORT FILE: easy/sprites/src/sprites.c" in context
    assert "// BUILD FILE: easy/sprites/Makefile" in context


def test_build_embedding_text_mentions_descriptions_and_support_files(tmp_path):
    source = """// Description: Draws a sprite
// Descripcion: Dibuja un sprite
#include "sprites.h"
void main(void) {}
"""
    support = [tmp_path / "sprites.h"]

    text = build_embedding_text("easy/sprites/src/main.c", source, support)

    assert "Draws a sprite" in text
    assert "Dibuja un sprite" in text
    assert "local includes: sprites.h" in text
    assert "support files: sprites.h" in text


def test_discover_support_files_finds_local_include(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    main_c = src_dir / "main.c"
    header = src_dir / "player.h"
    main_c.write_text('#include "player.h"\nvoid main(void) {}\n', encoding="utf-8")
    header.write_text("void draw_player(void);\n", encoding="utf-8")

    support_files = discover_support_files(main_c, tmp_path)

    assert header.resolve() in support_files


def test_is_self_contained_c_context_rejects_local_include():
    assert not is_self_contained_c_context('#include "sprites.h"\nvoid main(void) {}\n')


def test_is_self_contained_c_context_rejects_expanded_support_file():
    context = """// FILE: easy/sprites/src/main.c
#include <cpctelera.h>
void main(void) {}

// SUPPORT FILE: easy/sprites/src/sprites.h
extern const unsigned char sprite[];
"""

    assert not is_self_contained_c_context(context)


def test_is_self_contained_c_context_accepts_single_file_cpctelera():
    assert is_self_contained_c_context("#include <cpctelera.h>\nvoid main(void) {}\n")
