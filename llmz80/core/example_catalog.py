"""Deterministic retrieval over compileable example entry points.

The vector index is an optional semantic accelerator.  This catalog is the
source of truth: it indexes programs (files containing ``main``), not every C
translation unit in the examples tree.  That distinction prevents sprite data
and support modules from being presented to the model as complete programs.
"""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from .code_context import build_example_context, extract_descriptions, find_nearest_makefile

MAIN_RE = re.compile(r"\b(?:void|int)\s+main\s*\(")
WORD_RE = re.compile(r"[a-z0-9_]+")
EXCLUDED_PARTS = {"build", "generated", "obj", "exp"}
EXCLUSION_MARKER = ".llmz80-rag-exclude"
STOP_WORDS = {
    "a",
    "al",
    "and",
    "around",
    "con",
    "create",
    "crea",
    "de",
    "del",
    "el",
    "en",
    "for",
    "la",
    "las",
    "los",
    "main",
    "mode",
    "modo",
    "program",
    "programa",
    "static",
    "the",
    "un",
    "una",
    "using",
    "void",
    "with",
    "y",
    "que",
    "por",
    "para",
    "pantalla",
}

# Bilingual intent vocabulary.  Expanding a small, explicit vocabulary is more
# predictable than falling back to random examples when embeddings are absent.
INTENT_GROUPS = (
    {"text", "texto", "string", "strings", "print", "printf", "hello", "hola", "menu"},
    {"keyboard", "teclado", "key", "keys", "tecla", "teclas", "input", "control", "qaop"},
    {
        "sprite",
        "sprites",
        "player",
        "jugador",
        "ship",
        "nave",
        "character",
        "personaje",
        "flea",
        "pulga",
    },
    {"graphic", "graphics", "grafico", "graficos", "draw", "dibuja", "pixel", "line", "screen"},
    {
        "game",
        "juego",
        "arcade",
        "tetris",
        "pong",
        "snake",
        "tic",
        "tac",
        "toe",
        "comecocos",
        "pacman",
        "pellet",
    },
    {"sound", "sonido", "music", "musica", "beep", "audio"},
    {"random", "aleatorio", "azar", "procedural"},
    {
        "tile",
        "tiles",
        "tilemap",
        "map",
        "mapa",
        "maze",
        "laberinto",
        "scroll",
        "scrolling",
        "comecocos",
        "pacman",
    },
    {"colour", "color", "colores", "palette", "paleta", "ink", "border", "borde"},
    {
        "animate",
        "animated",
        "animation",
        "animacion",
        "mueve",
        "move",
        "jump",
        "jumps",
        "salta",
        "rebota",
        "bounce",
    },
    {
        "collision",
        "colision",
        "collide",
        "rebota",
        "bounce",
        "bounds",
        "bordes",
        "wall",
        "walls",
        "muro",
        "muros",
        "comecocos",
        "pacman",
    },
    {
        "score",
        "puntuacion",
        "puntos",
        "marcador",
        "lives",
        "vidas",
        "hud",
        "counter",
        "contador",
        "comecocos",
        "pacman",
    },
    {
        "collect",
        "recoge",
        "recoger",
        "coin",
        "coins",
        "moneda",
        "monedas",
        "object",
        "objeto",
        "pellet",
        "pellets",
        "comecocos",
        "pacman",
    },
    {"platform", "platforms", "plataforma", "plataformas", "gravity", "gravedad"},
)

CAPABILITY_TOKENS = {
    "text": {"text", "texto", "print", "printf", "menu", "title"},
    "input": {
        "keyboard",
        "teclado",
        "key",
        "tecla",
        "input",
        "control",
        "qaop",
        "playable",
        "jugable",
        "comecocos",
        "pacman",
    },
    "sprite": {
        "sprite",
        "player",
        "jugador",
        "ship",
        "nave",
        "character",
        "personaje",
        "flea",
        "pulga",
        "comecocos",
        "pacman",
    },
    "animation": {
        "animate",
        "animated",
        "animation",
        "animacion",
        "move",
        "mueve",
        "jump",
        "salta",
        "scroll",
        "comecocos",
        "pacman",
    },
    "collision": {
        "collision",
        "colision",
        "collide",
        "bounce",
        "rebota",
        "platform",
        "plataforma",
        "wall",
        "muro",
        "comecocos",
        "pacman",
    },
    "collect": {"collect", "recoge", "coin", "moneda", "pellet", "comecocos", "pacman"},
    "hud": {
        "score",
        "puntuacion",
        "puntos",
        "marcador",
        "lives",
        "vidas",
        "hud",
        "counter",
        "contador",
        "comecocos",
        "pacman",
    },
    "score": {"score", "puntuacion", "puntos", "marcador", "comecocos", "pacman"},
    "sound": {"sound", "sonido", "music", "musica", "beep", "audio"},
    "tiles": {
        "tile",
        "tiles",
        "tilemap",
        "map",
        "mapa",
        "maze",
        "laberinto",
        "comecocos",
        "pacman",
    },
    "palette": {"colour", "color", "palette", "paleta", "ink"},
    "frame_pacing": {"vsync", "waitvsync", "intrinsic_halt", "frame"},
}


def _normalise(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.lower())
    return "".join(char for char in value if not unicodedata.combining(char))


def _tokens(value: str) -> set[str]:
    return set(WORD_RE.findall(_normalise(value))) - STOP_WORDS


def _expanded_query_tokens(query: str) -> set[str]:
    tokens = _tokens(query)
    if {"pac", "man"} <= tokens:
        tokens.add("pacman")
    if {"come", "cocos"} <= tokens:
        tokens.add("comecocos")
    expanded = set(tokens)
    for group in INTENT_GROUPS:
        if tokens & group:
            expanded.update(group)
    return expanded


def infer_capabilities(text: str) -> list[str]:
    tokens = _expanded_query_tokens(text)
    normalised = _normalise(text)
    capabilities = {name for name, terms in CAPABILITY_TOKENS.items() if tokens & terms}
    api_hints = {
        "cpct_drawsprite": "sprite",
        "zx_pxy2saddr": "sprite",
        "in_inkey": "input",
        "cpct_scankeyboard": "input",
        "cpct_waitvsync": "frame_pacing",
        "intrinsic_halt": "frame_pacing",
        "printf": "text",
        "cpct_drawstring": "text",
    }
    for hint, capability in api_hints.items():
        if hint in normalised:
            capabilities.add(capability)
    return sorted(capabilities)


class ExampleCatalog:
    """Discover and rank local, project-level examples for one platform."""

    def __init__(
        self,
        platform: str,
        examples_dir: Path | Iterable[Path],
        max_context_size: int = 50000,
    ):
        self.platform = platform
        if isinstance(examples_dir, Path):
            roots = [examples_dir]
        else:
            roots = list(examples_dir)
        self.example_roots = [root.resolve() for root in roots]
        self.examples_dir = self.example_roots[0]
        self.max_context_size = max_context_size
        self._entries: list[dict[str, Any]] | None = None

    def discover(self) -> list[dict[str, Any]]:
        """Return deterministic entry-point metadata without calling external services."""
        if self._entries is not None:
            return [dict(entry) for entry in self._entries]

        entries: list[dict[str, Any]] = []
        available_roots = [root for root in self.example_roots if root.is_dir()]
        if not available_roots:
            self._entries = entries
            return []

        multiple_roots = len(available_roots) > 1
        for root in available_roots:
            for file_path in sorted(root.rglob("*.c")):
                relative = file_path.relative_to(root)
                if set(relative.parts) & EXCLUDED_PARTS:
                    continue
                source = file_path.read_text(encoding="utf-8", errors="ignore")
                if not MAIN_RE.search(source):
                    continue
                if self._has_exclusion_marker(file_path, root):
                    continue

                # CPC examples are projects.  A main.c without a build definition is
                # not evidence that the code compiles under the repository contract.
                makefile = find_nearest_makefile(file_path, root)
                if self.platform == "amstrad_cpc" and makefile is None:
                    continue

                display_path = (
                    f"{root.name}/{relative}"
                    if multiple_roots and root != available_roots[0]
                    else str(relative)
                )
                desc_en, desc_es = extract_descriptions(source)
                project_name = relative.parent.name if relative.stem == "main" else relative.stem
                description = desc_en or desc_es or project_name.replace("_", " ")
                searchable = "\n".join((display_path, desc_en, desc_es, source[:12000]))
                capabilities = infer_capabilities(searchable)
                apis = sorted(set(re.findall(r"\b(?:cpct|zx|in|intrinsic)_[A-Za-z0-9_]+", source)))
                controls = [
                    name for name in ("qaop", "cursor", "space") if name in _normalise(source)
                ]
                entries.append(
                    {
                        "path": display_path,
                        "file_path": file_path,
                        "examples_dir": root,
                        "description": description,
                        "tokens": _tokens(searchable),
                        "source_size": len(source),
                        "has_makefile": makefile is not None,
                        "capabilities": capabilities,
                        "controls": controls,
                        "video_mode": (
                            "mode_0"
                            if "cpct_setVideoMode(0)" in source
                            else (
                                "mode_1"
                                if "cpct_setVideoMode(1)" in source
                                else (
                                    "spectrum_bitmap"
                                    if self.platform == "spectrum"
                                    else "unspecified"
                                )
                            )
                        ),
                        "apis": apis,
                        "has_assets": bool(
                            re.search(r"SUPPORT FILE|\.h[>\"]|cpct_drawSprite", source)
                        ),
                        "complexity": (
                            "small"
                            if len(source) < 4000
                            else "medium" if len(source) < 12000 else "large"
                        ),
                        "quality_tier": "certified",
                    }
                )

        self._entries = entries
        return [dict(entry) for entry in entries]

    @staticmethod
    def _has_exclusion_marker(file_path: Path, root: Path) -> bool:
        """Return True when a project explicitly opts out of retrieval."""
        current = file_path.parent
        while True:
            if (current / EXCLUSION_MARKER).exists():
                return True
            if current == root or current.parent == current:
                return False
            current = current.parent

    def search(self, query: str, limit: int = 8) -> list[dict[str, Any]]:
        """Rank entry points lexically, then return compile-aware contexts.

        Ranking uses IDF-weighted token overlap plus small stable bonuses for
        path/description matches.  It intentionally has no random component.
        """
        entries = self.discover()
        if not entries or limit <= 0:
            return []

        query_tokens = _expanded_query_tokens(query)
        query_capabilities = set(infer_capabilities(query))
        document_frequency: Counter[str] = Counter()
        for entry in entries:
            document_frequency.update(entry["tokens"])

        ranked = []
        query_normalised = _normalise(query)
        for entry in entries:
            overlap = query_tokens & entry["tokens"]
            score = sum(
                math.log((len(entries) + 1) / (document_frequency[token] + 1)) + 1.0
                for token in overlap
            )
            path_text = _normalise(entry["path"].replace("/", " ").replace("_", " "))
            description_text = _normalise(entry["description"])
            score += 1.5 * sum(1 for token in query_tokens if token in path_text)
            score += 2.0 * sum(1 for token in query_tokens if token in description_text)
            if query_normalised and query_normalised in description_text:
                score += 5.0
            score += 3.0 * len(query_capabilities & set(entry["capabilities"]))
            ranked.append((score, entry["path"], entry))

        ranked.sort(key=lambda item: (-item[0], item[1]))
        selected = [item[2] for item in ranked if item[0] > 0.0][:limit]

        # Always provide one minimal platform foundation.  This stabilises
        # headers/initialisation even for novel prompts with no lexical overlap.
        foundation = self._foundation_entry(entries)
        if foundation and foundation["path"] not in {entry["path"] for entry in selected}:
            if len(selected) >= limit:
                selected[-1] = foundation
            else:
                selected.append(foundation)

        results = []
        score_by_path = {item[1]: item[0] for item in ranked}
        for entry in selected:
            context = build_example_context(
                entry["file_path"], entry["examples_dir"], self.max_context_size
            )
            results.append(
                {
                    "path": entry["path"],
                    "content": context,
                    "description": entry["description"],
                    "score": float(
                        score_by_path.get(entry["path"], 0.0)
                        / (score_by_path.get(entry["path"], 0.0) + 10.0)
                    ),
                    "source": "local_catalog",
                    "capabilities": entry["capabilities"],
                    "controls": entry["controls"],
                    "video_mode": entry["video_mode"],
                    "apis": entry["apis"],
                    "has_assets": entry["has_assets"],
                    "complexity": entry["complexity"],
                    "quality_tier": entry["quality_tier"],
                }
            )
        return results

    def _foundation_entry(self, entries: Iterable[dict[str, Any]]) -> dict[str, Any] | None:
        preferred = "02_print.c" if self.platform == "spectrum" else "rag/base/src/main.c"
        for entry in entries:
            if entry["path"] == preferred:
                return entry
        return next(iter(entries), None)
