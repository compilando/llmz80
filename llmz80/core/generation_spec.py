"""Deterministic prompt-to-spec planning for constrained Z80 targets."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


ARCHETYPE_RULES = (
    (
        "maze_collect_game",
        (
            "comecocos", "come cocos", "pacman", "pac-man", "pac man",
            "maze chase", "pellet maze",
        ),
    ),
    ("platform_movement", ("plataform", "platform", "salta", "jump", "gravedad", "gravity")),
    ("collect_game", ("recoge", "recoger", "collect", "moneda", "coin", "objeto", "object")),
    ("board_game", ("tablero", "board", "tres en raya", "tic tac toe", "laberinto", "maze")),
    ("scrolling_scene", ("scroll", "desplaza", "estrellas", "star field")),
    ("arcade", ("pong", "pelota", "ball", "disparo", "shoot")),
    ("animation", ("anima", "mueve", "moves", "salta", "jumps", "rebota", "bounce", "parpade", "blink")),
)

GAME_TERMS = ("juego", "game", "jugable", "playable")
EXPLICIT_STATIC_TERMS = (
    "pantalla estatica", "pantalla estática", "static screen", "static display",
    "demo estatica", "demo estática", "static demo", "mockup",
)

MAZE_COLLECT_CAPABILITIES = {
    "animation", "collision", "collect", "end_state", "frame_pacing", "hud",
    "input", "score", "sprite", "tiles",
}

CAPABILITY_RULES = {
    "input": (
        "tecla", "keyboard", "control", "jugable", "playable", "jugador", "player",
        "pulsa", "press", "iniciar", "start",
    ),
    "sprite": ("sprite", "personaje", "character", "pulga", "flea", "nave", "ship"),
    "collision": ("colisi", "collision", "rebota", "bounce", "recoge", "collect", "plataform"),
    "hud": ("marcador", "score", "vidas", "lives", "contador", "counter"),
    "score": ("puntuaci", "score", "marcador", "moneda", "coin"),
    "text": ("texto", "text", "título", "title", "instrucciones", "instructions", "menú", "menu"),
    "state": ("reinicio", "reset", "menú", "menu", "pantalla final", "win screen", "meta", "exit"),
    "end_state": ("gan", "win", "fin", "end", "meta", "exit", "salida"),
    "animation": ("anima", "mueve", "moves", "salta", "jumps", "rebota", "blink", "parpade"),
    "gravity": ("gravedad", "gravity", "salta", "jump"),
    "palette": ("color", "colour", "paleta", "palette"),
    "tiles": ("tile", "tiles", "mapa", "map", "laberinto", "maze"),
    "collect": ("recoge", "recoger", "collect", "moneda", "coin", "punto", "pellet"),
}


@dataclass(frozen=True)
class GenerationSpec:
    schema_version: int
    platform: str
    language: str
    request: str
    archetype: str
    capabilities: tuple[str, ...]
    controls: tuple[str, ...]
    states: tuple[str, ...]
    presentation: dict[str, object]
    timing: dict[str, object]
    budgets: dict[str, int]
    assumptions: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        value = asdict(self)
        for key in ("capabilities", "controls", "states", "assumptions"):
            value[key] = list(value[key])
        return value

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2, sort_keys=True)

    def save(self, path: Path) -> None:
        path.write_text(self.to_json() + "\n", encoding="utf-8")


def _contains(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def create_generation_spec(prompt: str, platform: str) -> GenerationSpec:
    if platform not in {"spectrum", "amstrad_cpc"}:
        raise ValueError(f"unsupported platform: {platform}")
    request = " ".join(prompt.split())
    if not request:
        raise ValueError("prompt cannot be empty")
    text = request.casefold()
    spanish_markers = re.findall(r"\b(?:una?|el|la|que|con|por|para|juego|pantalla)\b", text)
    language = "es" if spanish_markers or any(char in text for char in "áéíóúñ") else "en"

    archetype = "static_display"
    for candidate, terms in ARCHETYPE_RULES:
        if _contains(text, terms):
            archetype = candidate
            break
    if (
        archetype == "static_display"
        and _contains(text, GAME_TERMS)
        and not _contains(text, EXPLICIT_STATIC_TERMS)
    ):
        # A request for a game must never silently degrade into a drawing.
        archetype = "arcade"

    capabilities = {name for name, terms in CAPABILITY_RULES.items() if _contains(text, terms)}
    if archetype == "maze_collect_game":
        capabilities.update(MAZE_COLLECT_CAPABILITIES)
    if archetype not in {"static_display", "board_game"}:
        capabilities.update({"animation", "frame_pacing"})
    if archetype in {
        "maze_collect_game", "collect_game", "platform_movement", "arcade", "board_game"
    }:
        capabilities.add("input")

    controls: list[str] = []
    if "input" in capabilities:
        controls = ["left", "right", "action"]
        if archetype in {"board_game", "maze_collect_game"}:
            controls = ["left", "right", "up", "down", "action"]

    states = ["running"]
    if "end_state" in capabilities or archetype in {
        "maze_collect_game", "collect_game", "board_game", "arcade"
    }:
        states.append("finished")
    if "state" in capabilities:
        states.insert(0, "title")

    is_cpc = platform == "amstrad_cpc"
    mode = 0 if is_cpc and _contains(text, ("modo 0", "mode 0", "multicolor", "multicolour")) else 1
    presentation = {
        "video_mode": mode if is_cpc else "spectrum_bitmap",
        "screen_width": 160 if is_cpc and mode == 0 else (320 if is_cpc else 256),
        "screen_height": 200 if is_cpc else 192,
        "hud_required": bool({"hud", "score"} & capabilities),
    }
    timing = {
        "frame_hz": 50,
        "frame_sync_required": "animation" in capabilities,
        "input_edges_required": "input" in capabilities and (
            archetype in {"board_game", "static_display"}
            or _contains(text, ("pulsa", "press", "iniciar", "start"))
        ),
    }
    budgets = {
        "program_binary_bytes": 32768 if is_cpc else 24576,
        "static_data_bytes": 12288 if is_cpc else 8192,
        "stack_reserve_bytes": 1024,
    }
    assumptions = (
        "Use the simplest complete implementation.",
        "Keep all coordinates within the selected video mode.",
        "Use platform runtime primitives before custom busy loops or pixel code.",
    )
    return GenerationSpec(
        schema_version=1,
        platform=platform,
        language=language,
        request=request,
        archetype=archetype,
        capabilities=tuple(sorted(capabilities)),
        controls=tuple(controls),
        states=tuple(states),
        presentation=presentation,
        timing=timing,
        budgets=budgets,
        assumptions=assumptions,
    )
