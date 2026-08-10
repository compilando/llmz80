"""
Validadores pre-compilación para detectar errores comunes antes de compilar.
Esto ahorra tiempo y tokens de API al detectar errores obvios.
"""

import logging
import os
import re
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from .semantic_validation import SemanticValidator

logger = logging.getLogger(__name__)


class ValidationResult:
    """Resultado de una validación."""
    
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        """
        Args:
            is_valid: Si el código pasó la validación
            errors: Lista de errores críticos encontrados
            warnings: Lista de advertencias (no bloquean compilación)
        """
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def __bool__(self):
        """Permite usar ValidationResult en contextos booleanos."""
        return self.is_valid
    
    def __str__(self):
        """Representación en string del resultado."""
        if self.is_valid:
            msg = "✅ Validación exitosa"
            if self.warnings:
                msg += f" ({len(self.warnings)} advertencias)"
            return msg
        else:
            return f"❌ Validación fallida: {len(self.errors)} errores"


class BaseValidator:
    """Clase base para validadores."""
    
    def __init__(self, platform: str):
        """
        Args:
            platform: Plataforma objetivo (spectrum, amstrad_cpc)
        """
        self.platform = platform.lower()
        
    def validate(self, code: str) -> ValidationResult:
        """
        Valida el código.
        
        Args:
            code: Código C a validar
            
        Returns:
            ValidationResult con los resultados de la validación
        """
        raise NotImplementedError("Subclasses must implement validate()")


class SyntaxValidator(BaseValidator):
    """Valida sintaxis básica de C."""

    def __init__(self, platform: str, allowed_local_includes: Optional[set[str]] = None):
        super().__init__(platform)
        self.allowed_local_includes = allowed_local_includes or set()

    @staticmethod
    def _strip_comments(code: str) -> str:
        """Remove C comments while preserving strings/chars and newlines."""
        result = []
        i = 0
        in_str = None
        while i < len(code):
            c = code[i]
            nxt = code[i + 1] if i + 1 < len(code) else ""
            if in_str:
                result.append(c)
                if c == "\\" and i + 1 < len(code):
                    result.append(code[i + 1])
                    i += 2
                    continue
                if c == in_str:
                    in_str = None
                i += 1
                continue
            if c in ('"', "'"):
                in_str = c
                result.append(c)
                i += 1
                continue
            if c == "/" and nxt == "/":
                while i < len(code) and code[i] != "\n":
                    i += 1
                if i < len(code):
                    result.append("\n")
                    i += 1
                continue
            if c == "/" and nxt == "*":
                i += 2
                while i + 1 < len(code) and not (code[i] == "*" and code[i + 1] == "/"):
                    result.append("\n" if code[i] == "\n" else " ")
                    i += 1
                i += 2
                continue
            result.append(c)
            i += 1
        return "".join(result)
    
    def validate(self, code: str) -> ValidationResult:
        """Valida sintaxis básica."""
        errors = []
        warnings = []
        
        # Verificar que el código no esté vacío
        if not code.strip():
            errors.append("El código está vacío")
            return ValidationResult(False, errors)
        
        code_without_comments = self._strip_comments(code)

        # Contar llaves
        open_braces = code_without_comments.count('{')
        close_braces = code_without_comments.count('}')
        if open_braces != close_braces:
            errors.append(f"Llaves desbalanceadas: {open_braces} '{{' vs {close_braces} '}}'")
        
        # Contar paréntesis
        open_parens = code_without_comments.count('(')
        close_parens = code_without_comments.count(')')
        if open_parens != close_parens:
            errors.append(f"Paréntesis desbalanceados: {open_parens} '(' vs {close_parens} ')'")
        
        # Verificar que tenga función main
        if not re.search(r'\bmain\s*\(', code):
            errors.append("No se encontró función main()")
        
        # Buscar includes comunes faltantes
        has_includes = bool(re.search(r'#include\s*[<"]', code))
        if not has_includes:
            warnings.append("No se encontraron directivas #include (puede ser intencional)")

        local_includes = re.findall(r'#include\s+"([^"]+)"', code)
        for include_name in local_includes:
            if include_name in self.allowed_local_includes:
                continue
            errors.append(
                f"Include local prohibido en modo main.c autocontenido: #include \"{include_name}\". "
                "Embebe los datos en main.c o cambia explícitamente a modo proyecto multiarchivo."
            )
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)


class SpectrumValidator(BaseValidator):
    """Validador específico para ZX Spectrum (Z88DK)."""
    
    # Funciones comunes de Z88DK
    Z88DK_FUNCTIONS = [
        'zx_border', 'zx_cls',
        'in_inkey', 'in_key_pressed', 'in_wait_key', 'in_wait_nokey',
        'bit_beep', 'bit_fx', 'bit_synth',
        'sprintf', 'printf', 'putchar', 'getchar'
    ]
    
    # Headers comunes
    COMMON_HEADERS = [
        'arch/zx.h', 'input.h', 'sound.h', 'graphics.h',
        'stdio.h', 'stdlib.h', 'string.h'
    ]
    
    def validate(self, code: str) -> ValidationResult:
        """Valida código específico para ZX Spectrum."""
        errors = []
        warnings = []
        
        # Verificar si usa funciones Z88DK sin incluir headers
        used_z88dk_functions = []
        for func in self.Z88DK_FUNCTIONS:
            if re.search(rf'\b{func}\s*\(', code):
                used_z88dk_functions.append(func)
        
        if used_z88dk_functions:
            # Verificar si tiene los includes necesarios
            has_arch_zx_h = bool(re.search(r'#include\s*[<"]arch/zx\.h[>"]', code))
            has_input_h = bool(re.search(r'#include\s*[<"]input\.h[>"]', code))
            has_sound_h = bool(re.search(r'#include\s*[<"]sound\.h[>"]', code))
            
            # Funciones que requieren arch/zx.h
            zx_funcs = ['zx_border', 'zx_cls']
            if any(f in used_z88dk_functions for f in zx_funcs) and not has_arch_zx_h:
                errors.append("Usa funciones de arch/zx.h pero falta #include <arch/zx.h>")
            
            # Funciones que requieren input.h
            input_funcs = ['in_inkey', 'in_key_pressed', 'in_wait_key', 'in_wait_nokey']
            if any(f in used_z88dk_functions for f in input_funcs) and not has_input_h:
                errors.append("Usa funciones de input.h pero falta #include <input.h>")
            
            # Funciones que requieren sound.h
            sound_funcs = ['bit_beep', 'bit_fx', 'bit_synth']
            if any(f in used_z88dk_functions for f in sound_funcs) and not has_sound_h:
                errors.append("Usa funciones de sound.h pero falta #include <sound.h>")

        for invented_graphics_func in ('zx_plot', 'zx_point'):
            if re.search(rf'\b{invented_graphics_func}\s*\(', code):
                errors.append(
                    f"'{invented_graphics_func}()' no existe para este target Z88DK; "
                    "usa el helper plot()/unplot() probado de los ejemplos Spectrum"
                )

        for letter in ('Q', 'A', 'O', 'P'):
            bad_symbol = f"IN_KEY_SCANCODE_{letter}"
            if re.search(rf'\b{bad_symbol}\b', code):
                errors.append(
                    f"Scancode inexistente '{bad_symbol}'; las letras QAOP usan "
                    f"IN_KEY_SCANCODE_{letter.lower()} (sufijo minúsculo)"
                )

        if re.search(r'\bcpct_[A-Za-z0-9_]+\s*\(', code):
            errors.append("Usa funciones CPCtelera cpct_* en un programa ZX Spectrum")
        
        # Detectar uso de funciones estándar que pueden no estar disponibles
        problematic_functions = [
            'malloc', 'free', 'calloc', 'realloc',  # Memoria dinámica problemática
            'fprintf', 'fscanf', 'fopen', 'fclose',  # I/O de archivos no disponible
            'system', 'exit'  # Funciones de sistema
        ]
        
        for func in problematic_functions:
            if re.search(rf'\b{func}\s*\(', code):
                warnings.append(f"Función '{func}' puede no estar disponible o ser problemática en Z88DK")
        
        # Verificar arrays muy grandes (ZX Spectrum tiene 32KB RAM)
        array_declarations = re.findall(r'\b\w+\s+\w+\s*\[\s*(\d+)\s*\]', code)
        for size_str in array_declarations:
            try:
                size = int(size_str)
                if size > 8192:  # Arrays > 8KB son sospechosos
                    warnings.append(f"Array muy grande declarado [{size}] - ZX Spectrum tiene memoria limitada")
            except ValueError:
                pass
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)


class AmstradCPCValidator(BaseValidator):
    """Validador específico para Amstrad CPC (CPCtelera)."""

    CPCT_HEADER_FUNCTION_RE = re.compile(r'\b(cpct_[A-Za-z0-9_]+)\s*\(')

    # Funciones comunes de CPCtelera
    CPCTELERA_FUNCTIONS = [
        'cpct_disableFirmware', 'cpct_setVideoMode', 'cpct_clearScreen',
        'cpct_clearScreen_f8', 'cpct_clearScreen_f64',
        'cpct_drawSprite', 'cpct_drawSpriteMasked', 'cpct_drawSpriteBlended', 'cpct_drawSolidBox',
        'cpct_setPalette', 'cpct_setPALColour', 'cpct_getHWColour',
        'cpct_scanKeyboard', 'cpct_scanKeyboard_f', 'cpct_isKeyPressed',
        'cpct_isAnyKeyPressed', 'cpct_isAnyKeyPressed_f', 'cpct_getKeypressedAsASCII',
        'cpct_getScreenPtr', 'cpct_setDrawCharM0', 'cpct_setDrawCharM1',
        'cpct_setDrawCharM2', 'cpct_drawStringM0', 'cpct_drawStringM1',
        'cpct_drawStringM2', 'cpct_drawCharM0', 'cpct_drawCharM1', 'cpct_drawCharM2',
        'cpct_px2byteM0', 'cpct_px2byteM1',
        'cpct_memset', 'cpct_memset_f8', 'cpct_memset_f64', 'cpct_memcpy',
        'cpct_hflipSpriteM0', 'cpct_hflipSpriteM1',
        'cpct_vflipSprite',
        'cpct_akp_musicInit', 'cpct_akp_musicPlay', 'cpct_akp_stop',
        'cpct_akp_SFXInit', 'cpct_akp_SFXPlay', 'cpct_akp_SFXStopAll',
        'cpct_setSeed_lcg_u8', 'cpct_getRandom_lcg_u8',
        'cpct_setSeed_glfsr16', 'cpct_setTaps_glfsr16',
        'cpct_getRandom_glfsr16_u8', 'cpct_getRandom_glfsr16_u16',
        'cpct_getRandom_mxor_u8', 'cpct_getRandom_mxor_u16',
        'cpct_setSeed_mxor', 'cpct_restoreState_mxor_u8', 'cpct_restoreState_mxor_u16',
        'cpct_waitVSYNC', 'cpct_wait_cycles', 'cpct_waitHalts'
    ]

    # Expected arg counts for the highest-confidence CPCtelera signatures.
    # Used to catch wrong-arity calls before SDCC ever sees them.
    # Functions with optional/variant signatures are intentionally omitted.
    CPCTELERA_ARITY = {
        'cpct_disableFirmware': 0,
        'cpct_setVideoMode': 1,
        'cpct_clearScreen': 1,
        'cpct_clearScreen_f8': 1,
        'cpct_clearScreen_f64': 1,
        'cpct_scanKeyboard': 0,
        'cpct_scanKeyboard_f': 0,
        'cpct_isKeyPressed': 1,
        'cpct_isAnyKeyPressed': 0,
        'cpct_isAnyKeyPressed_f': 0,
        'cpct_getKeypressedAsASCII': 0,
        'cpct_getScreenPtr': 3,
        'cpct_getHWColour': 1,
        'cpct_setPALColour': 2,
        'cpct_setPalette': 2,
        'cpct_drawSprite': 4,
        'cpct_drawSpriteMasked': 4,
        'cpct_drawSpriteBlended': 4,
        'cpct_drawSolidBox': 4,
        'cpct_setDrawCharM0': 2,
        'cpct_setDrawCharM1': 2,
        'cpct_setDrawCharM2': 2,
        'cpct_drawStringM0': 2,
        'cpct_drawStringM1': 2,
        'cpct_drawStringM2': 2,
        'cpct_drawCharM0': 2,
        'cpct_drawCharM1': 2,
        'cpct_drawCharM2': 2,
        'cpct_px2byteM0': 2,
        'cpct_px2byteM1': 4,
        'cpct_memset': 3,
        'cpct_memset_f8': 3,
        'cpct_memset_f64': 3,
        'cpct_memcpy': 3,
        'cpct_hflipSpriteM0': 3,
        'cpct_hflipSpriteM1': 3,
        'cpct_vflipSprite': 4,
        'cpct_akp_musicInit': 1,
        'cpct_akp_musicPlay': 0,
        'cpct_akp_stop': 0,
        'cpct_akp_SFXInit': 1,
        'cpct_akp_SFXPlay': 6,
        'cpct_akp_SFXStopAll': 0,
        'cpct_setSeed_lcg_u8': 1,
        'cpct_getRandom_lcg_u8': 1,
        'cpct_setSeed_glfsr16': 1,
        'cpct_getRandom_glfsr16_u16': 0,
        'cpct_getRandom_glfsr16_u8': 0,
        'cpct_getRandom_mxor_u8': 0,
        'cpct_getRandom_mxor_u16': 0,
        'cpct_setSeed_mxor': 1,
        'cpct_restoreState_mxor_u8': 0,
        'cpct_restoreState_mxor_u16': 0,
        'cpct_waitVSYNC': 0,
        'cpct_wait_cycles': 1,
        'cpct_waitHalts': 1,
    }

    # Funciones Z88DK que NO deben usarse en CPCtelera
    FORBIDDEN_Z88DK_FUNCTIONS = [
        'zx_border', 'zx_cls', 'zx_print', 'in_inkey'
    ]

    FORBIDDEN_STANDARD_FUNCTIONS = [
        'printf', 'puts', 'putchar',
        'malloc', 'free', 'calloc', 'realloc',
        'fopen', 'fclose', 'fprintf', 'fscanf',
        'system', 'exit',
    ]

    def __init__(self, platform: str):
        super().__init__(platform)
        self.header_cpct_symbols = self._load_cpctelera_header_symbols()

    def _load_cpctelera_header_symbols(self) -> set[str]:
        """Best-effort extraction across the complete installed CPCtelera API.

        ``cpctelera.h`` is only an umbrella of includes, so scanning that file
        alone yielded zero symbols and made the validator reject valid advanced
        APIs demonstrated by the example library.
        """
        cpct_path = os.environ.get("CPCT_PATH", "/home/oscar/cpctelera/cpctelera/")
        cpct_dir = Path(cpct_path)
        candidates = [
            cpct_dir / "src" / "cpctelera.h",
            cpct_dir / "cpctelera" / "src" / "cpctelera.h",
        ]
        for umbrella in candidates:
            if not umbrella.exists():
                continue
            symbols: set[str] = set()
            for header in umbrella.parent.rglob("*.h"):
                try:
                    content = header.read_text(encoding="utf-8", errors="ignore")
                except Exception as exc:
                    logger.debug(f"No se pudo leer {header}: {exc}")
                    continue
                symbols.update(self.CPCT_HEADER_FUNCTION_RE.findall(content))
            if symbols:
                logger.debug(
                    f"Cargados {len(symbols)} símbolos CPCtelera desde {umbrella.parent}"
                )
                return symbols
        return set()

    @staticmethod
    def _count_call_args(code: str, call_start: int) -> Optional[int]:
        """Count top-level args in a C call whose '(' begins at call_start.

        Handles nested parens, string/char literals, escape sequences.
        Returns None if unbalanced.
        """
        depth = 0
        args = 0
        seen_token = False
        in_str = None  # '"' or "'" or None
        prev = ''
        i = call_start
        while i < len(code):
            c = code[i]
            if in_str:
                if c == in_str and prev != '\\':
                    in_str = None
            elif c in ('"', "'"):
                in_str = c
                if depth == 1:
                    seen_token = True
            elif c == '(':
                if depth == 1:
                    seen_token = True
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    if seen_token:
                        args += 1
                    return args
            elif c == ',' and depth == 1:
                args += 1
                seen_token = False
            elif depth == 1 and not c.isspace():
                seen_token = True
            prev = c
            i += 1
        return None  # unbalanced

    @staticmethod
    def _extract_main_body(code: str) -> str:
        """Return the body of main(), best-effort, for execution-order checks."""
        match = re.search(r'\bmain\s*\([^)]*\)\s*\{', code)
        if not match:
            return ""
        start = match.end()
        depth = 1
        i = start
        in_str = None
        prev = ''
        while i < len(code):
            c = code[i]
            if in_str:
                if c == in_str and prev != '\\':
                    in_str = None
            elif c in ('"', "'"):
                in_str = c
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return code[start:i]
            prev = c
            i += 1
        return code[start:]

    @staticmethod
    def _strip_leading_declarations(code: str) -> str:
        """Remove leading declarations/comments/blank lines from a function body."""
        declaration_re = re.compile(
            r'^\s*(?:const\s+|static\s+|volatile\s+)?'
            r'(?:u8|u16|u32|i8|i16|i32|char|int|unsigned|signed|long|short|\w+\s*\*)'
            r'[\w\s\*\[\],=+\-&|()<>.]*;\s*$'
        )
        offset = 0
        while offset < len(code):
            line_end = code.find("\n", offset)
            if line_end == -1:
                line_end = len(code)
            line = code[offset:line_end]
            stripped = line.strip()
            if not stripped or declaration_re.match(line):
                offset = line_end + (1 if line_end < len(code) else 0)
                continue
            return code[offset:]
        return ""

    @staticmethod
    def _extract_first_call_arg(code: str, call_start: int) -> Optional[str]:
        """Extract the first top-level argument in a C call."""
        depth = 0
        in_str = None
        prev = ''
        arg_start = None
        i = call_start
        while i < len(code):
            c = code[i]
            if in_str:
                if c == in_str and prev != '\\':
                    in_str = None
            elif c in ('"', "'"):
                in_str = c
                if arg_start is None:
                    arg_start = i
            elif c == '(':
                depth += 1
                if depth == 1:
                    arg_start = i + 1
            elif c == ')':
                if depth == 1 and arg_start is not None:
                    return code[arg_start:i].strip()
                depth -= 1
            elif c == ',' and depth == 1 and arg_start is not None:
                return code[arg_start:i].strip()
            elif depth == 1 and arg_start is None and not c.isspace():
                arg_start = i
            prev = c
            i += 1
        return None
    
    def validate(self, code: str) -> ValidationResult:
        """Valida código específico para Amstrad CPC."""
        errors = []
        warnings = []
        
        # Verificar include de cpctelera.h
        has_cpctelera_h = bool(re.search(r'#include\s*[<"]cpctelera\.h[>"]', code))
        
        # Verificar si usa funciones CPCtelera
        used_cpctelera_functions = []
        for func in self.CPCTELERA_FUNCTIONS:
            if re.search(rf'\b{func}\s*\(', code):
                used_cpctelera_functions.append(func)
        
        if used_cpctelera_functions and not has_cpctelera_h:
            errors.append("Usa funciones de CPCtelera pero falta #include <cpctelera.h>")

        used_cpct_symbols = sorted(set(re.findall(r'\b(cpct_[A-Za-z0-9_]+)\s*\(', code)))
        known_cpct_symbols = set(self.CPCTELERA_FUNCTIONS) | self.header_cpct_symbols
        for func in used_cpct_symbols:
            if func not in known_cpct_symbols:
                errors.append(
                    f"Función CPCtelera '{func}' no está en la lista segura del validador; "
                    "no inventes APIs CPCtelera y verifica la firma contra <cpctelera.h>"
                )

        # === ARITY CHECK ===
        # Walk every call site and compare arg count vs known signature.
        # Mismatches are hard errors — SDCC will reject them anyway, but catching
        # them here avoids burning a compile+correction cycle.
        for m in re.finditer(r'\b(cpct_[A-Za-z0-9_]+)\s*\(', code):
            func = m.group(1)
            expected = self.CPCTELERA_ARITY.get(func)
            if expected is None:
                continue
            paren_pos = code.find('(', m.start())
            actual = self._count_call_args(code, paren_pos)
            if actual is None:
                warnings.append(f"Llamada a {func}(...) con paréntesis desbalanceados")
                continue
            if actual != expected:
                # Find line number for actionable error
                line_no = code.count('\n', 0, m.start()) + 1
                errors.append(
                    f"Línea {line_no}: {func}() invocada con {actual} argumentos, "
                    f"se esperan {expected}"
                )
        
        # Verificar que NO use funciones Z88DK (error común)
        for func in self.FORBIDDEN_Z88DK_FUNCTIONS:
            if re.search(rf'\b{func}\s*\(', code):
                errors.append(f"Usa función Z88DK '{func}' - debe usar equivalente CPCtelera")

        for func in self.FORBIDDEN_STANDARD_FUNCTIONS:
            if re.search(rf'\b{func}\s*\(', code):
                errors.append(f"Usa función no permitida en CPCtelera '{func}'")

        if re.search(r'\b(float|double)\b', code):
            errors.append("Usa float/double; usa aritmética entera o fixed-point para Z80/CPCtelera")
        
        # Verificar cpct_disableFirmware() si usa funciones de hardware
        hardware_funcs = ['cpct_setVideoMode', 'cpct_scanKeyboard', 'cpct_setPalette']
        if any(re.search(rf'\b{func}\s*\(', code) for func in hardware_funcs):
            if not re.search(r'\bcpct_disableFirmware\s*\(', code):
                errors.append("Usa funciones de hardware pero no llama cpct_disableFirmware()")

        main_body = self._extract_main_body(code)
        if main_body and re.search(r'\bcpct_disableFirmware\s*\(', main_body):
            main_body_no_comments = SyntaxValidator._strip_comments(main_body)
            main_body_no_comments = self._strip_leading_declarations(main_body_no_comments)
            first_call = re.search(r'\b([A-Za-z_][A-Za-z0-9_]*)\s*\(', main_body_no_comments)
            if first_call and first_call.group(1) != 'cpct_disableFirmware':
                errors.append("cpct_disableFirmware() debe ser la primera llamada ejecutable en main()")

        for m in re.finditer(r'\b(cpct_drawCharM[012])\s*\(', code):
            paren_pos = code.find('(', m.start())
            first_arg = self._extract_first_call_arg(code, paren_pos)
            if first_arg and (
                first_arg.startswith("'")
                or first_arg.startswith('"')
                or re.fullmatch(r'\d+', first_arg)
                or first_arg in {"ch", "ascii", "character", "char_code"}
            ):
                line_no = code.count('\n', 0, m.start()) + 1
                errors.append(
                    f"Línea {line_no}: {m.group(1)}() debe recibir memoria como primer argumento "
                    "(cpct_drawCharM1(pvmem, 'X'))"
                )
        
        # Verificar modo de video configurado
        if re.search(r'\bcpct_drawSprite\s*\(', code):
            if not re.search(r'\bcpct_setVideoMode\s*\(', code):
                errors.append("Dibuja sprites pero no configura modo de video con cpct_setVideoMode()")

        if re.search(r'\bcpct_isKeyPressed\s*\(', code):
            scan_match = re.search(r'\bcpct_scanKeyboard(?:_f)?\s*\(', code)
            key_match = re.search(r'\bcpct_isKeyPressed\s*\(', code)
            if not scan_match:
                errors.append("Usa cpct_isKeyPressed() sin llamar antes a cpct_scanKeyboard() o cpct_scanKeyboard_f()")
            elif key_match and scan_match.start() > key_match.start():
                errors.append("cpct_scanKeyboard() debe ejecutarse antes de cpct_isKeyPressed()")

        mode_match = re.search(r'\bcpct_setVideoMode\s*\(\s*([012])\s*\)', code)
        if mode_match:
            mode = mode_match.group(1)
            wrong_mode_calls = []
            for called_mode in ('0', '1', '2'):
                if called_mode == mode:
                    continue
                if re.search(rf'\bcpct_(?:drawString|drawChar|setDrawChar)M{called_mode}\s*\(', code):
                    wrong_mode_calls.append(f"M{called_mode}")
            if wrong_mode_calls:
                errors.append(
                    f"Usa funciones de texto {', '.join(sorted(set(wrong_mode_calls)))} "
                    f"pero el modo configurado es {mode}"
                )
        
        # Verificar arrays grandes (CPC tiene 16KB-128KB dependiendo modelo)
        array_declarations = re.findall(r'\b\w+\s+\w+\s*\[\s*(\d+)\s*\]', code)
        for size_str in array_declarations:
            try:
                size = int(size_str)
                if size > 16384:  # Arrays > 16KB son sospechosos
                    warnings.append(f"Array muy grande declarado [{size}] - considerar limitaciones de RAM")
            except ValueError:
                pass
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)


class CodeValidator:
    """Validador principal que coordina todas las validaciones."""
    
    def __init__(self, platform: str, spec: Optional[Dict] = None, output_mode: str = "single"):
        """
        Args:
            platform: Plataforma objetivo (spectrum, amstrad_cpc)
        """
        self.platform = platform.lower()
        
        # Inicializar validadores
        allowed = {"assets.h", "llmz80_runtime.h"} if output_mode == "project" else set()
        self.syntax_validator = SyntaxValidator(platform, allowed_local_includes=allowed)
        
        if platform == 'spectrum':
            self.platform_validator = SpectrumValidator(platform)
        elif platform == 'amstrad_cpc':
            self.platform_validator = AmstradCPCValidator(platform)
        else:
            raise ValueError(f"Platform not supported: {platform}")
        self.semantic_validator = SemanticValidator(platform, spec)
        self.last_semantic_report: Dict = {}
    
    def validate(self, code: str) -> ValidationResult:
        """
        Ejecuta todas las validaciones.
        
        Args:
            code: Código C a validar
            
        Returns:
            ValidationResult con todos los errores y advertencias combinados
        """
        all_errors = []
        all_warnings = []
        
        # Validación de sintaxis
        logger.info("🔍 Ejecutando validación de sintaxis...")
        syntax_result = self.syntax_validator.validate(code)
        all_errors.extend(syntax_result.errors)
        all_warnings.extend(syntax_result.warnings)
        
        if syntax_result.errors:
            logger.warning(f"⚠️ Errores de sintaxis encontrados: {len(syntax_result.errors)}")
        
        # Validación específica de plataforma
        logger.info(f"🔍 Ejecutando validación específica para {self.platform}...")
        platform_result = self.platform_validator.validate(code)
        all_errors.extend(platform_result.errors)
        all_warnings.extend(platform_result.warnings)
        
        if platform_result.errors:
            logger.warning(f"⚠️ Errores de plataforma encontrados: {len(platform_result.errors)}")

        self.last_semantic_report = self.semantic_validator.validate(code)
        all_errors.extend(self.last_semantic_report["errors"])
        all_warnings.extend(self.last_semantic_report["warnings"])
        
        # Resultado final
        is_valid = len(all_errors) == 0
        
        if is_valid:
            logger.info(f"✅ Validación exitosa ({len(all_warnings)} advertencias)")
        else:
            logger.error(f"❌ Validación fallida: {len(all_errors)} errores, {len(all_warnings)} advertencias")
        
        return ValidationResult(is_valid, all_errors, all_warnings)
    
    def validate_and_report(self, code: str) -> Tuple[bool, str]:
        """
        Valida y genera un reporte legible.
        
        Args:
            code: Código C a validar
            
        Returns:
            Tupla de (es_válido, reporte_texto)
        """
        result = self.validate(code)
        
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("REPORTE DE VALIDACIÓN PRE-COMPILACIÓN")
        report_lines.append("=" * 60)
        
        if result.is_valid:
            report_lines.append("✅ RESULTADO: CÓDIGO VÁLIDO")
        else:
            report_lines.append("❌ RESULTADO: ERRORES DETECTADOS")
        
        report_lines.append("")
        
        if result.errors:
            report_lines.append(f"ERRORES CRÍTICOS ({len(result.errors)}):")
            for i, error in enumerate(result.errors, 1):
                report_lines.append(f"  {i}. {error}")
            report_lines.append("")
        
        if result.warnings:
            report_lines.append(f"ADVERTENCIAS ({len(result.warnings)}):")
            for i, warning in enumerate(result.warnings, 1):
                report_lines.append(f"  {i}. {warning}")
            report_lines.append("")
        
        if result.is_valid and not result.warnings:
            report_lines.append("✨ No se detectaron problemas. El código está listo para compilar.")
        elif result.is_valid and result.warnings:
            report_lines.append("⚠️ El código es válido pero tiene advertencias.")
            report_lines.append("   Puede compilar, pero revise las advertencias.")
        else:
            report_lines.append("❌ Corrija los errores antes de intentar compilar.")
        
        report_lines.append("=" * 60)
        
        return result.is_valid, "\n".join(report_lines)
