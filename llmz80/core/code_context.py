"""Utilities to build compile-aware RAG snippets from example projects."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Optional


DESCRIPTION_RE = re.compile(r"^//\s*(Description|Descripcion):\s*(.*)", re.IGNORECASE)
LOCAL_INCLUDE_RE = re.compile(r'^\s*#\s*include\s+"([^"]+)"', re.MULTILINE)

SUPPORT_EXTENSIONS = {".h", ".s", ".asm"}
MAX_SUPPORT_FILE_SIZE = 12000
MAX_MAKEFILE_SIZE = 8000
MAX_CONTEXT_SIZE = 50000


def extract_descriptions(source_code: str) -> tuple[str, str]:
    """Return English and Spanish descriptions from the first comment lines."""
    desc_en = ""
    desc_es = ""

    for line in source_code.splitlines()[:8]:
        match = DESCRIPTION_RE.match(line.strip())
        if not match:
            continue

        language = match.group(1).lower()
        description = match.group(2).strip()
        if language == "description":
            desc_en = description
        else:
            desc_es = description

    return desc_en, desc_es


def build_embedding_text(relative_path: str, source_code: str, support_files: Iterable[Path]) -> str:
    """Build a search document that includes behavior and compile-relevant signals."""
    desc_en, desc_es = extract_descriptions(source_code)
    parts = [relative_path.replace("/", " ").replace("_", " ")]

    if desc_en:
        parts.append(desc_en)
    if desc_es:
        parts.append(desc_es)

    includes = sorted(set(LOCAL_INCLUDE_RE.findall(source_code)))
    if includes:
        parts.append("local includes: " + ", ".join(includes))

    support_names = sorted(path.name for path in support_files)
    if support_names:
        parts.append("support files: " + ", ".join(support_names))

    parts.append(source_code[:4000])
    return "\n".join(part for part in parts if part)


def is_self_contained_c_context(source_code: str) -> bool:
    """Return True when a C snippet does not require local project files."""
    if LOCAL_INCLUDE_RE.search(source_code):
        return False
    if re.search(r"^\s*//\s+SUPPORT FILE:", source_code, re.MULTILINE):
        return False
    return True


def build_example_context(
    file_path: Path,
    examples_dir: Path,
    max_size: int = MAX_CONTEXT_SIZE,
) -> str:
    """Return source plus nearby files needed to understand how it compiles."""
    file_path = file_path.resolve()
    examples_dir = examples_dir.resolve()
    source_code = file_path.read_text(encoding="utf-8", errors="ignore")
    relative_path = file_path.relative_to(examples_dir)
    project_dir = file_path.parent.parent if file_path.parent.name == "src" else file_path.parent

    sections = [
        f"// FILE: {relative_path}",
        source_code,
    ]

    for support_file in discover_support_files(file_path, project_dir):
        content = support_file.read_text(encoding="utf-8", errors="ignore")
        if len(content) > MAX_SUPPORT_FILE_SIZE:
            content = content[:MAX_SUPPORT_FILE_SIZE] + "\n/* ... support file truncated ... */\n"
        sections.extend(
            [
                "",
                f"// SUPPORT FILE: {support_file.relative_to(examples_dir)}",
                content,
            ]
        )

    makefile = find_nearest_makefile(file_path, stop_dir=examples_dir)
    if makefile:
        content = makefile.read_text(encoding="utf-8", errors="ignore")
        if len(content) > MAX_MAKEFILE_SIZE:
            content = content[:MAX_MAKEFILE_SIZE] + "\n# ... Makefile truncated ...\n"
        sections.extend(
            [
                "",
                f"// BUILD FILE: {makefile.relative_to(examples_dir)}",
                "/*",
                content,
                "*/",
            ]
        )

    context = "\n".join(sections)
    if len(context) <= max_size:
        return context

    keep_head = int(max_size * 0.75)
    keep_tail = max_size - keep_head
    return (
        context[:keep_head]
        + "\n/* ... compile context truncated ... */\n"
        + context[-keep_tail:]
    )


def discover_support_files(file_path: Path, project_dir: Path) -> list[Path]:
    """Find local headers/assembly/C modules an example depends on."""
    source_code = file_path.read_text(encoding="utf-8", errors="ignore")
    support_files: set[Path] = set()

    for include_name in LOCAL_INCLUDE_RE.findall(source_code):
        candidate = (file_path.parent / include_name).resolve()
        if candidate.exists() and candidate.is_file():
            support_files.add(candidate)

    src_dir = project_dir / "src"
    search_roots = [src_dir] if src_dir.exists() else [file_path.parent]
    for root in search_roots:
        for candidate in root.rglob("*"):
            if not candidate.is_file() or candidate.resolve() == file_path.resolve():
                continue
            if candidate.suffix.lower() in SUPPORT_EXTENSIONS:
                support_files.add(candidate.resolve())
            elif candidate.suffix.lower() == ".c" and candidate.parent == file_path.parent:
                support_files.add(candidate.resolve())

    return sorted(support_files)


def find_nearest_makefile(file_path: Path, stop_dir: Path) -> Optional[Path]:
    """Find the closest Makefile for an example without walking outside examples_dir."""
    current = file_path.parent
    stop_dir = stop_dir.resolve()

    while True:
        makefile = current / "Makefile"
        if makefile.exists():
            return makefile
        if current.resolve() == stop_dir or current.parent == current:
            return None
        current = current.parent
