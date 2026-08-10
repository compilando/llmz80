import re
import unicodedata
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, Optional


REASONING_MODEL_PREFIXES = ("gpt-5", "o1", "o3", "o4")


_ERROR_SIGNAL_RE = re.compile(
    r"(error|fatal|undefined reference|undefined symbol|cannot find|no such file|"
    r"conflicting types|implicit declaration|warning|too few arguments|too many arguments)",
    re.IGNORECASE,
)
# Pure noise lines to drop unconditionally (no signal keywords inside).
_MAKE_NOISE_RE = re.compile(
    r"^(make(\[\d+\])?:\s+(Entering|Leaving)|Entering directory|Leaving directory|"
    r"gcc\s|sdcc\s-|Compiling .*\.c$)",
)


def filter_compiler_output(raw: str, max_lines: int = 40, keep_context: int = 1) -> str:
    """Strip compiler noise; keep error/warning lines plus N lines of context.

    SDCC/make emit lots of "Entering directory", build paths, and unrelated
    warnings that waste LLM tokens. This keeps only signal lines.
    """
    if not raw:
        return ""
    lines = raw.splitlines()
    keep_idx = set()
    for i, ln in enumerate(lines):
        if _ERROR_SIGNAL_RE.search(ln):
            for j in range(max(0, i - keep_context), min(len(lines), i + keep_context + 1)):
                keep_idx.add(j)
    # Drop pure make/ld noise even if kept by proximity
    out = []
    for i in sorted(keep_idx):
        ln = lines[i]
        if _MAKE_NOISE_RE.match(ln.strip()):
            continue
        out.append(ln)
    # Cap output size; favour LAST lines (final errors usually most useful)
    if len(out) > max_lines:
        out = out[-max_lines:]
    # Fallback: if filter stripped everything, return last N raw lines
    if not out:
        out = [ln for ln in lines if ln.strip()][-max_lines:]
    return "\n".join(out)


def hash_error_signature(error_text: str) -> str:
    """Stable signature for deduplicating errors across retry attempts.

    Extracts function names, error keywords, and file:line markers; ignores
    absolute build paths and timestamps that vary across runs.
    """
    if not error_text:
        return ""
    tokens = []
    for ln in error_text.splitlines():
        m = re.search(r"(error|undefined reference|conflicting types|implicit declaration):\s*(.+)", ln, re.IGNORECASE)
        if m:
            sig = m.group(2)
            # Normalise quoted identifiers and strip trailing punctuation
            sig = re.sub(r"['`\"]", "", sig).strip().rstrip('.')
            sig = re.sub(r"\s+", " ", sig)
            tokens.append(sig.lower()[:120])
    joined = "|".join(sorted(set(tokens)))
    return joined or error_text.strip().lower()[:200]


def is_reasoning_model(model: Optional[str]) -> bool:
    if not model:
        return False
    return model.lower().startswith(REASONING_MODEL_PREFIXES)


def build_completion_kwargs(
    model: str,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    reasoning_effort: Optional[str] = None,
) -> Dict:
    """Build kwargs for client.chat.completions.create adapting to model family.

    Reasoning models (gpt-5, o-series) require max_completion_tokens and reject
    temperature; classic chat models use max_tokens + temperature.
    """
    kwargs: Dict = {"model": model}
    if is_reasoning_model(model):
        if max_tokens is not None:
            kwargs["max_completion_tokens"] = max_tokens
        if reasoning_effort:
            kwargs["reasoning_effort"] = reasoning_effort
    else:
        if temperature is not None:
            kwargs["temperature"] = temperature
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
    return kwargs


def apply_deterministic_cpc_fixes(code: str) -> tuple[str, list[str]]:
    """Apply safe, local CPCtelera fixes before spending a compiler/LLM attempt."""
    fixes: list[str] = []
    fixed = code

    if re.search(r'\bcpct_[A-Za-z0-9_]+\s*\(', fixed) and not re.search(r'#include\s*<cpctelera\.h>', fixed):
        fixed = '#include <cpctelera.h>\n' + fixed
        fixes.append("Añadido #include <cpctelera.h>")

    main_match = re.search(r'\bvoid\s+main\s*\(\s*void\s*\)\s*\{', fixed)
    if main_match and re.search(r'\bcpct_(?:setVideoMode|scanKeyboard|setPalette|draw|clearScreen)', fixed):
        main_body = fixed[main_match.end():]
        if not re.search(r'\bcpct_disableFirmware\s*\(', main_body):
            insert_at = _find_main_first_statement_offset(fixed, main_match.end())
            fixed = fixed[:insert_at] + "    cpct_disableFirmware();\n" + fixed[insert_at:]
            fixes.append("Añadido cpct_disableFirmware() al inicio de main()")

    if re.search(r'\bcpct_isKeyPressed\s*\(', fixed) and not re.search(r'\bcpct_scanKeyboard(?:_f)?\s*\(', fixed):
        key_match = re.search(r'^[^\n]*\bcpct_isKeyPressed\s*\(', fixed, flags=re.MULTILINE)
        if key_match:
            line_start = key_match.start()
            fixed = fixed[:line_start] + "    cpct_scanKeyboard_f();\n" + fixed[line_start:]
            fixes.append("Añadido cpct_scanKeyboard_f() antes de cpct_isKeyPressed()")

    before_zx_cls = fixed
    fixed = re.sub(r'\bzx_cls\s*\(\s*\)\s*;', 'cpct_clearScreen(0x00);', fixed)
    if fixed != before_zx_cls:
        fixes.append("Sustituido zx_cls() por cpct_clearScreen(0x00)")

    before_drawchar = fixed
    pointer_variables = set(re.findall(
        r"\b(?:const\s+)?(?:u8|char|void)\s*\*\s*([A-Za-z_]\w*)\b", fixed
    ))

    def fix_drawchar_args(match: re.Match) -> str:
        first = match.group(2).strip()
        second = match.group(3).strip()
        first_is_literal = first.startswith(("'", '"'))
        second_is_pointer = second in pointer_variables
        first_is_pointer = first in pointer_variables
        if first_is_literal or (second_is_pointer and not first_is_pointer):
            return f"{match.group(1)}({second}, {first})"
        return match.group(0)

    fixed = re.sub(
        r'\b(cpct_drawCharM[012])\s*\(\s*([^,\n]+?)\s*,\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)',
        fix_drawchar_args,
        fixed,
    )
    if fixed != before_drawchar:
        fixes.append("Corregido orden de argumentos cpct_drawCharM*()")

    before_random = fixed
    fixed = re.sub(r'^\s*cpct_setRandom_lcg_u8\s*\(\s*\)\s*;\s*\n?', '', fixed, flags=re.MULTILINE)
    fixed = re.sub(r'\bcpct_getRandom_lcg_u8\s*\(\s*\)', 'cpct_getRandom_glfsr16_u8()', fixed)
    if fixed != before_random:
        fixes.append("Corregido uso de random LCG inexistente/sin entropía")

    before_ascii = fixed
    fixed = re.sub(r'\bcpct_getKeyASCII\s*\(\s*\)', 'cpct_getKeypressedAsASCII()', fixed)
    if fixed != before_ascii:
        fixes.append("Corregido cpct_getKeyASCII() por cpct_getKeypressedAsASCII()")

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
            rf'\bIN_KEY_SCANCODE_{upper}\b',
            f'IN_KEY_SCANCODE_{lower}',
            fixed,
        )
        if fixed != before:
            fixes.append(
                f"Corregido IN_KEY_SCANCODE_{upper} por IN_KEY_SCANCODE_{lower}"
            )

    fixed, cast_count = _cast_high_byte_constants(fixed, macro_type="uint8_t")
    if cast_count:
        fixes.append(f"Added explicit casts to {cast_count} high byte constants")

    return fixed, fixes


def _cast_high_byte_constants(code: str, macro_type: str) -> tuple[str, int]:
    """Silence SDCC warning 158 for checked 128..255 byte constants."""
    count = 0

    def cast_macro(match: re.Match) -> str:
        nonlocal count
        value = int(match.group("value"), 0)
        if not 128 <= value <= 255:
            return match.group(0)
        count += 1
        return f"{match.group('prefix')}(({macro_type}){match.group('value')}){match.group('suffix')}"

    fixed = re.sub(
        r"^(?P<prefix>\s*#define\s+[A-Za-z_]\w*\s+)"
        r"(?P<value>0[xX][0-9A-Fa-f]+|\d+)"
        r"(?P<suffix>\s*(?://[^\n]*|/\*[^\n]*\*/)?$)",
        cast_macro,
        code,
        flags=re.MULTILINE,
    )

    def cast_declaration(match: re.Match) -> str:
        nonlocal count
        value = int(match.group("value"), 0)
        if not 128 <= value <= 255:
            return match.group(0)
        count += 1
        return f"{match.group('prefix')}({match.group('type')}){match.group('value')}{match.group('suffix')}"

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

        def cast_assignment(match: re.Match) -> str:
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
        r'^\s*(?:const\s+|static\s+|volatile\s+)?'
        r'(?:u8|u16|u32|i8|i16|i32|char|int|unsigned|signed|long|short|GameState|\w+\s*\*)'
        r'[\w\s\*\[\],=+\-&|()<>.]*;\s*(?://.*)?$'
    )

    while offset < len(code):
        line_end = code.find('\n', offset)
        if line_end == -1:
            line_end = len(code)
        line = code[offset:line_end + (1 if line_end < len(code) else 0)]
        stripped = line.strip()
        if not stripped or stripped.startswith("//") or stripped.startswith("/*") or declaration_re.match(line):
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
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)  # Eliminar caracteres no deseados
    slug = re.sub(r'[-\s]+', '-', slug).strip('-')  # Reemplazar espacios/guiones por un solo guión
    slug = slug[:max_length]  # Truncar
    logging.debug(f"Slug creado: {slug}")
    return slug

def slugify(text: str, max_length: int = 40) -> str:
    """Compatibility alias for create_slug."""
    return create_slug(text, max_length)

def get_output_paths(prompt: str, platform: str, base_output_dir: Path, slug_max_length: int) -> Dict[str, Path]:
    """Genera rutas para archivos de salida basadas en timestamp y slug del prompt.
    
    Args:
        prompt: Prompt del usuario
        platform: Plataforma seleccionada
        base_output_dir: Directorio base para la salida
        slug_max_length: Longitud máxima para el slug
        
    Returns:
        Diccionario con las rutas generadas
    """
    logging.info("🗂️ Generando rutas de salida...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    slug = create_slug(prompt, slug_max_length)
    base_dir = base_output_dir / f"{timestamp}_{slug}"
    if base_dir.exists():
        suffix = 2
        while (base_output_dir / f"{timestamp}_{slug}-{suffix}").exists():
            suffix += 1
        base_dir = base_output_dir / f"{timestamp}_{slug}-{suffix}"

    paths = {
        'base': base_dir,
        'c_file': base_dir / 'main.c',
        'prompt_file': base_dir / 'prompt.txt',
        'platform_file': base_dir / 'platform.txt',  # Renombrado para claridad
        'obj_dir': base_dir / 'obj',  # Añadir explícitamente la ruta del dir obj
    }

    # Archivo de salida específico según la plataforma
    if platform == 'spectrum':
        paths['output_artifact'] = base_dir / 'output.tap'  # Nombre de ejemplo
    elif platform == 'amstrad_cpc':
        paths['output_artifact'] = base_dir / 'output.dsk'  # Nombre de ejemplo
    else:
        paths['output_artifact'] = base_dir / 'output.bin'  # Fallback genérico

    logging.debug(f"Rutas generadas: {paths}")
    return paths

def estimate_tokens(text: str) -> int:    
    """Estima de manera sencilla el número de tokens en un texto.
    
    Aproximación: 1 token ≈ 3.5 caracteres en inglés/código.
    
    Args:
        text: Texto cuya longitud en tokens se quiere estimar
        
    Returns:
        Número estimado de tokens
    """
    # Estimación conservadora: 1 token por cada 3.5 caracteres
    return int(len(str(text)) / 3.5)

def clean_api_response(raw_response: str) -> str:
    """Intenta extraer solo el código C de la respuesta de la API.
    
    Args:
        raw_response: Respuesta completa de la API
        
    Returns:
        Código C limpio
    """
    logging.debug("Limpiando respuesta de la API...")
    code = raw_response.strip()

    # Intento 1: Regex para bloques de código markdown (non-greedy)
    match = re.search(r'```\s*(?:c|C)?\s*\n?(.*?)```', code, re.DOTALL)
    if match:
        extracted_code = match.group(1).strip()
        logging.info("✅ Código extraído usando regex de markdown.")
        return extracted_code

    # If the model prefixed an explanation, start at the first preprocessor
    # directive.  Do not trim after main(): valid C may define functions later.
    include_match = re.search(r'^\s*#\s*include\b', code, re.MULTILINE)
    if include_match and include_match.start() > 0:
        logging.info("Eliminando texto previo al primer #include de la respuesta.")
        code = code[include_match.start():]

    cleaned_code = code.replace("```c", "").replace("```C", "").replace("```", "").strip()
    if len(cleaned_code) < 0.5 * len(raw_response):  # Umbral arbitrario
        logging.warning("⚠️ La limpieza básica redujo significativamente la longitud del contenido. El resultado podría estar incompleto.")
    elif not cleaned_code:
        logging.warning("⚠️ La limpieza resultó en código vacío.")

    return cleaned_code if cleaned_code else raw_response  # Devolver original si la limpieza falló gravemente 
