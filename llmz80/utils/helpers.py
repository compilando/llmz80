"""Source fixups and slugs: what is left of the helpers after the legacy cut.

The OpenAI chat-completions plumbing, the compiler-output triage and the
`local/<timestamp>_<slug>/` run layout all went with `api/generator.py` and
`llm_z80.py`; nothing here calls a model or lays out a run any more.

The two `apply_deterministic_*_fixes` are kept deliberately even though no
live caller applies them. They encode SDCC and z88dk workarounds that
`tests/test_runtime_contracts.py` proves against a real toolchain -- the
warning-357 CPC fixture compiles cleanly only because of them -- and Studio's
own build does not apply them at all. That is a gap to close, not knowledge
to throw away.
"""

import logging
import re
import unicodedata


def apply_deterministic_cpc_fixes(code: str) -> tuple[str, list[str]]:
    """Apply safe, local CPCtelera fixes before spending a compiler/LLM attempt."""
    fixes: list[str] = []
    fixed = code

    if re.search(r"\bcpct_[A-Za-z0-9_]+\s*\(", fixed) and not re.search(
        r"#include\s*<cpctelera\.h>", fixed
    ):
        fixed = "#include <cpctelera.h>\n" + fixed
        fixes.append("Añadido #include <cpctelera.h>")

    main_match = re.search(r"\bvoid\s+main\s*\(\s*void\s*\)\s*\{", fixed)
    if main_match and re.search(
        r"\bcpct_(?:setVideoMode|scanKeyboard|setPalette|draw|clearScreen)", fixed
    ):
        main_body = fixed[main_match.end() :]
        if not re.search(r"\bcpct_disableFirmware\s*\(", main_body):
            insert_at = _find_main_first_statement_offset(fixed, main_match.end())
            fixed = fixed[:insert_at] + "    cpct_disableFirmware();\n" + fixed[insert_at:]
            fixes.append("Añadido cpct_disableFirmware() al inicio de main()")

    if re.search(r"\bcpct_isKeyPressed\s*\(", fixed) and not re.search(
        r"\bcpct_scanKeyboard(?:_f)?\s*\(", fixed
    ):
        key_match = re.search(r"^[^\n]*\bcpct_isKeyPressed\s*\(", fixed, flags=re.MULTILINE)
        if key_match:
            line_start = key_match.start()
            fixed = fixed[:line_start] + "    cpct_scanKeyboard_f();\n" + fixed[line_start:]
            fixes.append("Añadido cpct_scanKeyboard_f() antes de cpct_isKeyPressed()")

    before_zx_cls = fixed
    fixed = re.sub(r"\bzx_cls\s*\(\s*\)\s*;", "cpct_clearScreen(0x00);", fixed)
    if fixed != before_zx_cls:
        fixes.append("Sustituido zx_cls() por cpct_clearScreen(0x00)")

    before_drawchar = fixed
    pointer_variables = set(
        re.findall(r"\b(?:const\s+)?(?:u8|char|void)\s*\*\s*([A-Za-z_]\w*)\b", fixed)
    )

    def fix_drawchar_args(match: re.Match[str]) -> str:
        first = match.group(2).strip()
        second = match.group(3).strip()
        first_is_literal = first.startswith(("'", '"'))
        second_is_pointer = second in pointer_variables
        first_is_pointer = first in pointer_variables
        if first_is_literal or (second_is_pointer and not first_is_pointer):
            return f"{match.group(1)}({second}, {first})"
        return match.group(0)

    fixed = re.sub(
        r"\b(cpct_drawCharM[012])\s*\(\s*([^,\n]+?)\s*,\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)",
        fix_drawchar_args,
        fixed,
    )
    if fixed != before_drawchar:
        fixes.append("Corregido orden de argumentos cpct_drawCharM*()")

    before_random = fixed
    fixed = re.sub(r"^\s*cpct_setRandom_lcg_u8\s*\(\s*\)\s*;\s*\n?", "", fixed, flags=re.MULTILINE)
    fixed = re.sub(r"\bcpct_getRandom_lcg_u8\s*\(\s*\)", "cpct_getRandom_glfsr16_u8()", fixed)
    if fixed != before_random:
        fixes.append("Corregido uso de random LCG inexistente/sin entropía")

    before_ascii = fixed
    fixed = re.sub(r"\bcpct_getKeyASCII\s*\(\s*\)", "cpct_getKeypressedAsASCII()", fixed)
    if fixed != before_ascii:
        fixes.append("Corregido cpct_getKeyASCII() por cpct_getKeypressedAsASCII()")

    # CPCtelera's assembly sprite routine does not modify sprite data. SDCC
    # warning 357 is triggered when generated code discards a const array's
    # code-space qualifier with an explicit (void*) cast. Passing the array
    # directly is the compile-proven CPCtelera form used by certified examples.
    const_sprite_arrays = set(
        re.findall(
            r"\b(?:static\s+)?const\s+(?:u8|uint8_t|unsigned\s+char)\s+" r"([A-Za-z_]\w*)\s*\[",
            fixed,
        )
    )
    fixed_sprite_casts = 0
    for symbol in sorted(const_sprite_arrays):
        pattern = re.compile(
            rf"(\bcpct_drawSprite\s*\(\s*)\(\s*void\s*\*\s*\)\s*" rf"{re.escape(symbol)}\b"
        )
        fixed, count = pattern.subn(rf"\g<1>{symbol}", fixed)
        fixed_sprite_casts += count
    if fixed_sprite_casts:
        fixes.append(
            f"Eliminados {fixed_sprite_casts} casts void* de sprites const (SDCC warning 357)"
        )

    fixed, cast_count = _cast_high_byte_constants(fixed, macro_type="u8")
    if cast_count:
        fixes.append(f"Añadidos casts explícitos a {cast_count} constantes byte altas")

    return fixed, fixes


def apply_deterministic_spectrum_fixes(code: str) -> tuple[str, list[str]]:
    """Apply only semantics-preserving fixes verified against Z88DK headers."""
    fixed = code
    fixes: list[str] = []

    for upper, lower in (("Q", "q"), ("A", "a"), ("O", "o"), ("P", "p")):
        before = fixed
        fixed = re.sub(
            rf"\bIN_KEY_SCANCODE_{upper}\b",
            f"IN_KEY_SCANCODE_{lower}",
            fixed,
        )
        if fixed != before:
            fixes.append(f"Corregido IN_KEY_SCANCODE_{upper} por IN_KEY_SCANCODE_{lower}")

    fixed, cast_count = _cast_high_byte_constants(fixed, macro_type="uint8_t")
    if cast_count:
        fixes.append(f"Added explicit casts to {cast_count} high byte constants")

    return fixed, fixes


def _cast_high_byte_constants(code: str, macro_type: str) -> tuple[str, int]:
    """Silence SDCC warning 158 for checked 128..255 byte constants."""
    count = 0

    def cast_macro(match: re.Match[str]) -> str:
        nonlocal count
        value = int(match.group("value"), 0)
        if not 128 <= value <= 255:
            return match.group(0)
        count += 1
        return (
            f"{match.group('prefix')}(({macro_type}){match.group('value')}){match.group('suffix')}"
        )

    fixed = re.sub(
        r"^(?P<prefix>\s*#define\s+[A-Za-z_]\w*\s+)"
        r"(?P<value>0[xX][0-9A-Fa-f]+|\d+)"
        r"(?P<suffix>\s*(?://[^\n]*|/\*[^\n]*\*/)?$)",
        cast_macro,
        code,
        flags=re.MULTILINE,
    )

    def cast_declaration(match: re.Match[str]) -> str:
        nonlocal count
        value = int(match.group("value"), 0)
        if not 128 <= value <= 255:
            return match.group(0)
        count += 1
        return (
            f"{match.group('prefix')}({match.group('type')})"
            f"{match.group('value')}{match.group('suffix')}"
        )

    fixed = re.sub(
        r"(?P<prefix>\b(?P<type>u8|uint8_t|unsigned\s+char)\s+[A-Za-z_]\w*\s*=\s*)"
        r"(?P<value>0[xX][0-9A-Fa-f]+|\d+)(?P<suffix>\s*;)",
        cast_declaration,
        fixed,
    )

    byte_variables = {
        name: re.sub(r"\s+", " ", type_name)
        for type_name, name in re.findall(
            r"\b(u8|uint8_t|unsigned\s+char)\s+([A-Za-z_]\w*)\b", fixed
        )
    }
    if byte_variables:
        names = "|".join(re.escape(name) for name in sorted(byte_variables, key=len, reverse=True))

        def cast_assignment(match: re.Match[str]) -> str:
            nonlocal count
            value = int(match.group("value"), 0)
            if not 128 <= value <= 255:
                return match.group(0)
            count += 1
            type_name = byte_variables[match.group("name")]
            return (
                f"{match.group('prefix')}({type_name}){match.group('value')}"
                f"{match.group('suffix')}"
            )

        fixed = re.sub(
            rf"(?P<prefix>\b(?P<name>{names})\s*=\s*)"
            r"(?P<value>0[xX][0-9A-Fa-f]+|\d+)(?P<suffix>\s*;)",
            cast_assignment,
            fixed,
        )
    return fixed, count


def _find_main_first_statement_offset(code: str, main_body_start: int) -> int:
    """Find insertion offset after leading declarations in main()."""
    offset = main_body_start
    declaration_re = re.compile(
        r"^\s*(?:const\s+|static\s+|volatile\s+)?"
        r"(?:u8|u16|u32|i8|i16|i32|char|int|unsigned|signed|long|short|GameState|\w+\s*\*)"
        r"[\w\s\*\[\],=+\-&|()<>.]*;\s*(?://.*)?$"
    )

    while offset < len(code):
        line_end = code.find("\n", offset)
        if line_end == -1:
            line_end = len(code)
        line = code[offset : line_end + (1 if line_end < len(code) else 0)]
        stripped = line.strip()
        if (
            not stripped
            or stripped.startswith("//")
            or stripped.startswith("/*")
            or declaration_re.match(line)
        ):
            offset = line_end + (1 if line_end < len(code) else 0)
            continue
        return offset
    return main_body_start


def create_slug(text: str, max_length: int = 40) -> str:
    """Genera un slug URL-friendly a partir de un texto.

    Args:
        text: Texto a convertir en slug
        max_length: Longitud máxima del slug

    Returns:
        Slug generado
    """
    logging.debug(f"Creando slug desde texto: {text[:50]}...")
    slug = unicodedata.normalize("NFKD", text.lower())
    slug = slug.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)  # Eliminar caracteres no deseados
    slug = re.sub(r"[-\s]+", "-", slug).strip("-")  # Reemplazar espacios/guiones por un solo guión
    slug = slug[:max_length]  # Truncar
    logging.debug(f"Slug creado: {slug}")
    return slug


def slugify(text: str, max_length: int = 40) -> str:
    """Compatibility alias for create_slug."""
    return create_slug(text, max_length)
