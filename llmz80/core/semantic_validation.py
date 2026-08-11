"""Semantic and resource checks that a C compiler cannot express."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any


FRAME_CALLS = ("intrinsic_halt", "cpct_waitVSYNC", "cpct_waitHalts")

INTEGER_RANGES = {
    "u8": (0, 255),
    "uint8_t": (0, 255),
    "unsigned char": (0, 255),
    "i8": (-128, 127),
    "int8_t": (-128, 127),
    "char": (-128, 127),
    "u16": (0, 65535),
    "uint16_t": (0, 65535),
    "unsigned": (0, 65535),
    "unsigned int": (0, 65535),
    "i16": (-32768, 32767),
    "int16_t": (-32768, 32767),
    "int": (-32768, 32767),
    "u32": (0, 4294967295),
    "uint32_t": (0, 4294967295),
    "i32": (-2147483648, 2147483647),
    "int32_t": (-2147483648, 2147483647),
    "long": (-2147483648, 2147483647),
}
_INTEGER_TYPE_PATTERN = "|".join(
    re.escape(name) for name in sorted(INTEGER_RANGES, key=len, reverse=True)
)
_CAST_RE = re.compile(rf"\(\s*(?:{_INTEGER_TYPE_PATTERN})\s*\)")


def _executable_code(code: str) -> str:
    """Remove comments and literals while preserving statement boundaries."""
    pattern = re.compile(
        r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*.*?\*/',
        re.DOTALL,
    )
    return pattern.sub(lambda match: "\n" * match.group(0).count("\n"), code)


def _constant_value(expression: str, constants: dict[str, int]) -> int | None:
    """Evaluate a side-effect-free integer expression using C-like operators."""
    expression = re.sub(r"/\*.*?\*/|//[^\n]*", "", expression, flags=re.DOTALL).strip()
    expression = _CAST_RE.sub("", expression)
    expression = re.sub(r"\b(0[xX][0-9A-Fa-f]+|\d+)[uUlL]+\b", r"\1", expression)
    try:
        root = ast.parse(expression, mode="eval")
    except (SyntaxError, ValueError):
        return None

    def visit(node: ast.AST) -> int:
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return int(node.value)
        if isinstance(node, ast.Name) and node.id in constants:
            return constants[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub, ast.Invert)):
            value = visit(node.operand)
            if isinstance(node.op, ast.UAdd):
                return value
            if isinstance(node.op, ast.USub):
                return -value
            return ~value
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, (ast.Div, ast.FloorDiv)):
                return int(left / right)
            if isinstance(node.op, ast.Mod):
                return left % right
            if isinstance(node.op, ast.LShift):
                return left << right
            if isinstance(node.op, ast.RShift):
                return left >> right
            if isinstance(node.op, ast.BitOr):
                return left | right
            if isinstance(node.op, ast.BitAnd):
                return left & right
            if isinstance(node.op, ast.BitXor):
                return left ^ right
        raise ValueError("not a constant integer expression")

    try:
        return visit(root)
    except (ValueError, ZeroDivisionError, OverflowError, TypeError):
        return None


def constant_range_errors(code: str) -> list[str]:
    """Find compile-time values that cannot be represented by their C target type."""
    constants: dict[str, int] = {}
    byte_typed_constants: set[str] = set()
    variable_types: dict[str, str] = {}
    assignments: list[tuple[str, str]] = []

    for name, expression in re.findall(r"^\s*#define\s+(\w+)\s+([^\n]+)$", code, re.MULTILINE):
        value = _constant_value(expression, constants)
        if value is not None:
            constants[name] = value
            if re.search(r"\(\s*(?:u8|uint8_t|unsigned\s+char)\s*\)", expression):
                byte_typed_constants.add(name)

    declaration_re = re.compile(
        rf"\b(?:static\s+)?(?P<const>const\s+)?(?P<type>{_INTEGER_TYPE_PATTERN})\s+"
        r"(?P<declarators>[^;{}]+);"
    )
    for declaration in declaration_re.finditer(code):
        type_name = re.sub(r"\s+", " ", declaration.group("type").strip())
        for declarator in declaration.group("declarators").split(","):
            declarator = declarator.strip()
            match = re.match(r"(?P<name>\w+)\s*(?:=\s*(?P<expression>.+))?$", declarator)
            if not match:
                continue
            name = match.group("name")
            expression = match.group("expression")
            variable_types[name] = type_name
            if expression:
                assignments.append((name, expression))
                if declaration.group("const"):
                    value = _constant_value(expression, constants)
                    if value is not None:
                        constants[name] = value
                        if type_name in {"u8", "uint8_t", "unsigned char"}:
                            byte_typed_constants.add(name)

    for name in variable_types:
        for match in re.finditer(rf"(?<![=!<>])\b{re.escape(name)}\s*=(?!=)\s*([^;]+);", code):
            assignments.append((name, match.group(1)))

    errors = []
    seen: set[tuple[str, int]] = set()
    for name, expression in assignments:
        value = _constant_value(expression, constants)
        if value is None:
            continue
        minimum, maximum = INTEGER_RANGES[variable_types[name]]
        key = (name, value)
        outside_range = value < minimum or value > maximum
        source_name = expression.strip()
        safe_byte_source = (
            re.fullmatch(r"[A-Za-z_]\w*", source_name) is not None
            and (
                variable_types.get(source_name) in {"u8", "uint8_t", "unsigned char"}
                or source_name in byte_typed_constants
            )
        )
        sdcc_u8_conversion = (
            variable_types[name] in {"u8", "uint8_t", "unsigned char"}
            and 128 <= value <= 255
            and not safe_byte_source
            and not re.search(r"\(\s*(?:u8|uint8_t|unsigned\s+char)\s*\)", expression)
        )
        if outside_range and key not in seen:
            seen.add(key)
            errors.append(
                f"Constant value {value} assigned to {variable_types[name]} {name} "
                f"is outside [{minimum}, {maximum}]"
            )
        elif sdcc_u8_conversion and key not in seen:
            seen.add(key)
            errors.append(
                f"Constant value {value} assigned implicitly to {variable_types[name]} {name} "
                "triggers SDCC warning 158; range-check it and use an explicit u8 cast"
            )
    return errors


def estimate_static_data(code: str) -> int:
    """Conservative byte estimate for fixed-size scalar arrays."""
    type_sizes = {"char": 1, "u8": 1, "i8": 1, "int": 2, "unsigned": 2, "u16": 2, "i16": 2, "long": 4, "u32": 4, "i32": 4}
    total = 0
    pattern = re.compile(
        r"\b(?:static\s+)?(?:const\s+)?"
        r"(unsigned\s+char|unsigned\s+int|char|u8|i8|int|unsigned|u16|i16|long|u32|i32)"
        r"\s+\w+\s*\[\s*(\d+)\s*\]"
    )
    for type_name, count in pattern.findall(code):
        canonical = {"unsigned char": "char", "unsigned int": "unsigned"}.get(type_name, type_name)
        total += type_sizes[canonical] * int(count)
    return total


def cpc_read_only_pointer_errors(code: str) -> list[str]:
    """Detect SDCC warning 357 before compiling CPCtelera sprite calls."""
    const_arrays = set(re.findall(
        r"\b(?:static\s+)?const\s+(?:u8|uint8_t|unsigned\s+char)\s+"
        r"([A-Za-z_]\w*)\s*\[",
        code,
    ))
    errors = []
    for symbol in sorted(const_arrays):
        if re.search(
            rf"\bcpct_drawSprite\s*\(\s*\(\s*void\s*\*\s*\)\s*{re.escape(symbol)}\b",
            code,
        ):
            errors.append(
                f"SDCC warning 357: const sprite {symbol} is cast to void*; "
                "pass the array directly to cpct_drawSprite"
            )
    return errors


def _maze_gameplay_errors(code: str) -> list[str]:
    """Require observable game mechanics for the maze-collect contract."""
    executable = _executable_code(code)
    checks = (
        (
            r"\b(?:maze|map|level|board|tile|wall|laberinto|muro)[A-Za-z0-9_]*\b",
            "Maze-collect game has no maze/tile/wall model",
        ),
        (
            r"\b(?:pellet|dot|coin|collect|food|pickup|punto|comida)[A-Za-z0-9_]*\b",
            "Maze-collect game has no collectible state",
        ),
        (
            r"\b(?:collis|can_move|is_wall|wall_at|blocked|walkable|tile_at)[A-Za-z0-9_]*\b",
            "Maze-collect game has no collision/wall test",
        ),
        (
            r"\b(?:score|points|puntuacion|puntos)[A-Za-z0-9_]*\b",
            "Maze-collect game has no score/HUD state",
        ),
    )
    errors = [message for pattern, message in checks if not re.search(pattern, executable, re.IGNORECASE)]
    if not re.search(
        r"\b(?:player|pac|iv)?_?[xy]\s*(?:\+\+|--|[+\-]?=)",
        executable,
        re.IGNORECASE,
    ):
        errors.append("Maze-collect game has no evident player position update")
    return errors


class SemanticValidator:
    def __init__(self, platform: str, spec: dict[str, Any] | None = None):
        self.platform = platform
        self.spec = spec or {}

    def validate(self, code: str) -> dict[str, Any]:
        errors: list[str] = constant_range_errors(code)
        warnings: list[str] = []
        capabilities = set(self.spec.get("capabilities", []))
        timing = self.spec.get("timing", {})
        states = set(self.spec.get("states", []))
        archetype = self.spec.get("archetype", "")

        if archetype == "maze_collect_game":
            errors.extend(_maze_gameplay_errors(code))

        if timing.get("frame_sync_required") or "animation" in capabilities:
            if not any(re.search(rf"\b{name}\s*\(", code) for name in FRAME_CALLS):
                errors.append("Animated program has no certified 50 Hz frame pacing call")
        if "input" in capabilities:
            input_calls = (
                ("cpct_isKeyPressed", "cpct_isAnyKeyPressed", "cpct_getKeypressedAsASCII")
                if self.platform == "amstrad_cpc"
                else ("in_key_pressed", "in_inkey", "joy_read")
            )
            if not any(re.search(rf"\b{name}\s*\(", code) for name in input_calls):
                errors.append("GenerationSpec requires input but no certified keyboard/joystick read is evident")
        if re.search(r"\b(?:delay|wait)\w*\s*\([^)]*\)", code, re.IGNORECASE) and not any(
            name in code for name in FRAME_CALLS
        ):
            warnings.append("Custom delay/busy-wait detected; use the certified frame primitive")

        if re.search(r"while\s*\([^)]*\)\s*\{[^{}]*cpct_clearScreen", code, re.DOTALL):
            errors.append("Full CPC screen clear inside the main loop exceeds the redraw budget")
        if re.search(r"while\s*\([^)]*\)\s*\{[^{}]*zx_cls", code, re.DOTALL):
            errors.append("Full Spectrum screen clear inside the main loop causes flicker and excess work")

        if "sprite" in capabilities and re.search(r"\b(?:cpct_drawSprite|llmz80_draw_sprite8)\s*\(", code):
            has_erase = bool(re.search(r"\b(?:erase|clear|old_[xy]|prev_[xy]|previous_[xy])\b", code, re.IGNORECASE))
            if "animation" in capabilities and not has_erase:
                warnings.append("Moving sprite has no evident erase/restore step and may leave trails")

        if re.search(r"\b(?:u8|unsigned\s+char)\s+\w+", code) and re.search(r"\b\w+\s*-=[^;]+", code):
            warnings.append("Unsigned subtraction may underflow; guard bounds before updating coordinates")

        if "finished" in states and not re.search(
            r"\b(?:finished|game_over|won|win|state|[A-Za-z_]\w*_state|"
            r"state_[A-Za-z_]\w*|ST_(?:FINISHED|WIN|WON|GAME_OVER)|STATE_)\b",
            code,
            re.IGNORECASE,
        ):
            errors.append("GenerationSpec requires a finished state but no end-state variable is evident")

        if self.platform == "amstrad_cpc":
            errors.extend(cpc_read_only_pointer_errors(code))
            executable = _executable_code(code)
            executable = re.sub(r"^\s*#.*$", "", executable, flags=re.MULTILINE)
            if re.search(r"(?<!/)/(?:=)?|%(?:=)?", executable):
                errors.append(
                    "Runtime division/modulo is incompatible with the CPCtelera sdcccall build; "
                    "use shifts, masks, lookup tables, or bounded subtraction"
                )
            for match in re.finditer(r"cpct_getScreenPtr\s*\([^,]+,\s*(\d+)\s*,\s*(\d+)", code):
                x, y = map(int, match.groups())
                if x > 79 or y > 199:
                    errors.append(f"CPC screen address is out of bounds: x-byte={x}, y={y}")
        else:
            for match in re.finditer(r"zx_pxy2saddr\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)", code):
                x, y = map(int, match.groups())
                if x > 255 or y > 191:
                    errors.append(f"Spectrum pixel coordinate is out of bounds: x={x}, y={y}")

        static_data = estimate_static_data(code)
        static_budget = int(self.spec.get("budgets", {}).get(
            "static_data_bytes", 12288 if self.platform == "amstrad_cpc" else 8192
        ))
        if static_data > static_budget:
            errors.append(f"Estimated static data {static_data} exceeds budget {static_budget} bytes")

        return {
            "schema_version": 1,
            "platform": self.platform,
            "errors": errors,
            "warnings": warnings,
            "resources": {"estimated_static_data_bytes": static_data, "static_data_budget_bytes": static_budget},
            "quality_pass": not errors,
        }

    def write_report(self, code: str, path: Path) -> dict[str, Any]:
        report = self.validate(code)
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return report
