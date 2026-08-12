# Sprites en pantalla — Plan de implementación (2 de 3)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Que un juego generado dibuje sprites de verdad — empaquetados desde imágenes, con máscara y fotogramas de animación — en lugar de las cuatro formas de celda que la librería de plataforma lleva cableadas, y que esos sprites los pueda generar la IA con el estilo que dicte la ficha de referencia.

**Architecture:** Tres capas separadas por artefactos en disco. `spriting.py` convierte imágenes en bytes y máscara para cada target, sin saber de dónde salió la imagen. La librería de plataforma gana `plat_sprite`, que dibuja esos bytes y no sabe quién los generó. `sprite_artist.py` produce las imágenes desde la ficha, y es la única pieza que llama a una API. Cada capa se prueba sola: la primera con PNG fijos, la segunda con un programa mínimo compilado y capturado en el emulador, la tercera con un generador falso.

**Tech Stack:** Python 3.10+, pydantic v2, Pillow, numpy, z88dk/SDCC para Spectrum, CPCtelera/SDCC para Amstrad CPC, ZEsarUX y Caprice32 para captura, OpenAI Images API.

**Plan hermano:** 3 de 3, gates de game feel y TUI de mando. Este plan no depende de él, pero la gate de animación del plan 3 sí depende de éste.

---

## Hechos verificados del código actual

Comprobados antes de escribir el plan; no los des por supuestos, pero tampoco los re-investigues.

- `resources/studio_lib/common/platform.h` declara `plat_cell(col, row, kind)` con cinco `CELL_*`. No existe nada parecido a un sprite.
- Spectrum, `resources/studio_lib/spectrum/platform.c`: `put_glyph` escribe 8 bytes en `zx_cxy2saddr(col,row)`, con la línea `L` en `address[L << 8]`, y un byte de atributo en `zx_cxy2aaddr(col,row)`. Las cuatro formas son constantes de 8 bytes.
- CPC, `resources/studio_lib/cpc/platform.c`: `CELL_BYTES` es 4 en modo 0 y 2 en modo 1, y `plat_cell` pinta con `cpct_drawSolidBox`. La celda mide 8 píxeles de ancho en ambos modos.
- CPCtelera instalada en `~/cpctelera` ofrece exactamente:
  `extern void cpct_drawSpriteMasked(void *sprite, void* memory, u8 width, u8 height) __z88dk_callee;`
- `llmz80/studio/compiler.py:render_project` normaliza los assets del proyecto a `build/generated_assets/` rellenando el ancho a un múltiplo de píxeles por byte, y pasa las rutas a `create_project_layout`. **Ningún C generado los referencia jamás.** Ese es el eslabón que este plan suelda.
- `AssetSpec` en `llmz80/studio/models.py` tiene `id`, `kind`, `source`, `width`, `height`. No tiene fotogramas.
- `EntitySpec.sprite` es un `str` libre; los proyectos existentes lo rellenan con `hero`, `enemy`, `pellet` sin que nada los resuelva.
- `image_utils.py` ya trae `_clean_image`, `_scale_image` y `_process_image`, este último cuantiza a la paleta de la plataforma sin dithering.
- `generators/base.py` define `BaseImageGenerator.generate_image(prompt) -> PIL.Image`, con implementaciones OpenAI, Vertex y Gemini.
- `resources/sprite_prompt_spectrum.txt` y `resources/sprite_prompt_amstrad_cpc_mode{0,1,2}.txt` existen y usan marcadores `{prompt}`, `{width}`, `{height}`.
- El presupuesto de datos estáticos vive en `BudgetSpec.static_data_bytes`, mínimo 1024.

## Estructura de archivos

| Archivo | Responsabilidad |
|---|---|
| `llmz80/studio/spriting.py` (crear) | Imagen → bytes y máscara por target. Sin red, sin C, sin proyecto |
| `llmz80/studio/sprite_sheet.py` (crear) | Partir una hoja de fotogramas en imágenes sueltas. Separado porque cambia con el formato de la hoja, no con el target |
| `llmz80/studio/sprite_header.py` (crear) | Bytes empaquetados → `sprites.h`. Separado porque es generación de C, no de píxeles |
| `llmz80/studio/sprite_artist.py` (crear) | Ficha de referencia + rol → prompt → imagen. La única pieza que llama a una API |
| `resources/studio_lib/common/platform.h` (modificar) | Declara `plat_sprite` |
| `resources/studio_lib/spectrum/platform.c` (modificar) | Blit enmascarado 16×16 con atributo |
| `resources/studio_lib/cpc/platform.c` (modificar) | Blit vía `cpct_drawSpriteMasked` |
| `llmz80/studio/models.py` (modificar) | `AssetSpec` gana fotogramas; validación entidad↔asset |
| `llmz80/studio/compiler.py` (modificar) | Emite `sprites.h` en el build |
| `llmz80/studio/services.py`, `llmz80/cli.py` (modificar) | Operación compartida y comando |

---

### Task 1: Un asset sabe cuántos fotogramas tiene

**Files:**
- Modify: `llmz80/studio/models.py` (`AssetSpec`, y la validación de `GameProject`)
- Test: `tests/test_studio_models.py`

- [ ] **Step 1: Escribir los tests que fallan**

Añadir a `tests/test_studio_models.py`:

```python
def test_an_asset_declares_its_frames():
    asset = AssetSpec(id="hero", source="assets/hero.png", width=64, height=16, frames=4)

    assert asset.frames == 4
    assert asset.frame_width == 16


def test_an_asset_sheet_must_divide_into_whole_frames():
    """A sheet 65 wide cannot hold 4 frames; the split would silently lose a column."""
    with pytest.raises(ValidationError, match="frames"):
        AssetSpec(id="hero", source="assets/hero.png", width=65, height=16, frames=4)


def test_an_entity_may_name_a_sprite_that_no_asset_provides():
    """Designs predating any artwork must keep loading; the library falls back to shapes."""
    project = create_default_project("Fallback", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)

    assert project.assets == []
    assert any(entity.sprite for entity in project.entities)
```

- [ ] **Step 2: Ejecutar y verificar que fallan**

Run: `.venv/bin/python -m pytest tests/test_studio_models.py -q`
Expected: FAIL, `AssetSpec` no acepta `frames`

- [ ] **Step 3: Implementar**

En `AssetSpec`:

```python
    #: Frames laid out left to right in one sheet. One means a still image.
    frames: int = Field(default=1, ge=1, le=8)

    @property
    def frame_width(self) -> int:
        return self.width // self.frames

    @model_validator(mode="after")
    def validate_frames(self) -> "AssetSpec":
        if self.width % self.frames:
            raise ValueError(
                f"{self.id}: a sheet {self.width} wide cannot hold {self.frames} whole frames"
            )
        return self
```

No añadir todavía ninguna regla que exija que cada entidad tenga asset: los proyectos existentes no lo tienen y deben seguir cargando.

- [ ] **Step 4: Ejecutar y verificar que pasan**

Run: `.venv/bin/python -m pytest tests -q`
Expected: PASS. Usa el intérprete del venv; el `python` del sistema no tiene `pytest-asyncio`.

- [ ] **Step 5: Commit**

```bash
git add llmz80/studio/models.py tests/test_studio_models.py
git commit -m "feat(studio): let an asset declare its animation frames"
```

---

### Task 2: Partir una hoja de fotogramas

**Files:**
- Create: `llmz80/studio/sprite_sheet.py`
- Test: `tests/test_sprite_sheet.py`

Una sola imagen con los fotogramas en fila conserva la identidad del personaje entre ellos; una llamada por fotograma la pierde. Partirla debe ser determinista, por coordenadas, nunca por detección.

- [ ] **Step 1: Escribir los tests que fallan**

Crear `tests/test_sprite_sheet.py`:

```python
"""Splitting a frame sheet, by arithmetic rather than by detection."""

import pytest
from PIL import Image

from llmz80.studio.sprite_sheet import split_frames


def _sheet(frames: int, size: int = 16) -> Image.Image:
    """One sheet whose frames are solid grey levels, so order is checkable."""
    sheet = Image.new("RGBA", (size * frames, size), (0, 0, 0, 0))
    for index in range(frames):
        block = Image.new("RGBA", (size, size), (index * 40, index * 40, index * 40, 255))
        sheet.paste(block, (index * size, 0))
    return sheet


def test_a_sheet_splits_left_to_right():
    frames = split_frames(_sheet(4), 4)

    assert len(frames) == 4
    assert [frame.size for frame in frames] == [(16, 16)] * 4
    assert [frame.getpixel((0, 0))[0] for frame in frames] == [0, 40, 80, 120]


def test_a_sheet_that_does_not_divide_is_refused():
    with pytest.raises(ValueError, match="divide"):
        split_frames(_sheet(4, size=15), 4)


def test_one_frame_returns_the_image_itself():
    frames = split_frames(_sheet(1), 1)

    assert len(frames) == 1
    assert frames[0].size == (16, 16)
```

- [ ] **Step 2: Ejecutar y verificar que fallan**

Run: `.venv/bin/python -m pytest tests/test_sprite_sheet.py -q`
Expected: FAIL, `ModuleNotFoundError`

- [ ] **Step 3: Implementar**

Crear `llmz80/studio/sprite_sheet.py`:

```python
"""Cut a sheet of animation frames into single images.

A sheet exists because a model asked for one pose at a time draws a different
character each time. Cutting it is arithmetic on purpose: anything that inferred
frame boundaries from the pixels would drift the moment a pose reached the edge
of its cell.
"""

from __future__ import annotations

from PIL import Image


def split_frames(sheet: Image.Image, frames: int) -> list[Image.Image]:
    """Split a sheet into `frames` equal images, left to right."""
    if frames < 1:
        raise ValueError("a sheet holds at least one frame")
    if sheet.width % frames:
        raise ValueError(
            f"a sheet {sheet.width} wide does not divide into {frames} whole frames"
        )
    width = sheet.width // frames
    return [
        sheet.crop((index * width, 0, (index + 1) * width, sheet.height))
        for index in range(frames)
    ]
```

- [ ] **Step 4: Ejecutar y verificar que pasan**

Run: `.venv/bin/python -m pytest tests/test_sprite_sheet.py -q`
Expected: PASS, 3 tests

- [ ] **Step 5: Commit**

```bash
git add llmz80/studio/sprite_sheet.py tests/test_sprite_sheet.py
git commit -m "feat(studio): cut a frame sheet by arithmetic, not by guessing"
```

---

### Task 3: Empaquetar un sprite para el ZX Spectrum

**Files:**
- Create: `llmz80/studio/spriting.py`
- Test: `tests/test_spriting.py`

El Spectrum guarda un bit por píxel y un atributo de color por celda de 8×8. Un sprite de 16×16 son, por fila, dos bytes de datos y dos de máscara; dieciséis filas; más cuatro atributos.

Convenio de máscara, fijado aquí y respetado por el blitter: **un bit a 1 en la máscara conserva el fondo**. El blit es `pantalla = (pantalla & máscara) | datos`.

- [ ] **Step 1: Escribir los tests que fallan**

Crear `tests/test_spriting.py`:

```python
"""Packing an image into the bytes a Z80 can blit."""

import pytest
from PIL import Image

from llmz80.studio.spriting import PackedSprite, pack_spectrum


def _square(size: int = 16) -> Image.Image:
    """An opaque 8x8 block in the top-left quarter of a transparent 16x16 frame."""
    frame = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    for y in range(8):
        for x in range(8):
            frame.putpixel((x, y), (255, 255, 255, 255))
    return frame


def test_a_spectrum_frame_packs_two_bytes_per_row():
    packed = pack_spectrum([_square()])

    assert isinstance(packed, PackedSprite)
    assert packed.width_bytes == 2
    assert packed.height == 16
    assert len(packed.data) == 2 * 16
    assert len(packed.mask) == 2 * 16


def test_opaque_pixels_become_set_bits_and_a_clear_mask():
    packed = pack_spectrum([_square()])

    assert packed.data[0] == 0xFF   # first row, left byte: eight opaque pixels
    assert packed.mask[0] == 0x00   # nothing of the background survives there
    assert packed.data[1] == 0x00   # right byte is transparent
    assert packed.mask[1] == 0xFF   # so the background is kept whole


def test_transparent_rows_keep_the_background_everywhere():
    packed = pack_spectrum([_square()])
    row_nine = 9 * 2

    assert packed.data[row_nine] == 0x00
    assert packed.mask[row_nine] == 0xFF


def test_frames_are_concatenated_in_order():
    packed = pack_spectrum([_square(), Image.new("RGBA", (16, 16), (0, 0, 0, 0))])

    assert packed.frames == 2
    assert len(packed.data) == 2 * 16 * 2
    assert packed.data[0] == 0xFF
    assert packed.data[2 * 16] == 0x00   # second frame starts fully transparent


def test_a_frame_that_is_not_sixteen_by_sixteen_is_refused():
    with pytest.raises(ValueError, match="16x16"):
        pack_spectrum([Image.new("RGBA", (8, 8), (0, 0, 0, 0))])
```

- [ ] **Step 2: Ejecutar y verificar que fallan**

Run: `.venv/bin/python -m pytest tests/test_spriting.py -q`
Expected: FAIL, `ModuleNotFoundError`

- [ ] **Step 3: Implementar**

Crear `llmz80/studio/spriting.py`:

```python
"""Turn frames into the bytes each machine's blitter expects.

This module knows about pixels and about two machines, and about nothing else:
not where the image came from, not which entity wears it, not how the C that
draws it is written. That is what lets the same packer serve an imported PNG, a
model-generated sheet and a fixture in a test.

Mask convention, fixed here and honoured by every blitter: a set bit in the mask
keeps the background. A blit is `screen = (screen & mask) | data`.
"""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image

#: Every sprite is one 16x16 block, two character cells square. Fixing the size
#: keeps the blitter branchless and the budget arithmetic honest; a design that
#: needs something else needs a second sprite kind, not a variable-size one.
SPRITE_SIZE = 16

#: A pixel counts as drawn when it is this opaque. Generated art carries soft
#: edges no matter how firmly the prompt forbids them, and a threshold is a
#: decision made once here rather than differently in each caller.
ALPHA_THRESHOLD = 128


@dataclass(frozen=True)
class PackedSprite:
    """One sprite's frames, ready to be written into a header."""

    data: bytes
    mask: bytes
    width_bytes: int
    height: int
    frames: int

    @property
    def bytes_per_frame(self) -> int:
        return self.width_bytes * self.height


def _checked(frames: list[Image.Image]) -> list[Image.Image]:
    if not frames:
        raise ValueError("a sprite needs at least one frame")
    bad = [frame.size for frame in frames if frame.size != (SPRITE_SIZE, SPRITE_SIZE)]
    if bad:
        raise ValueError(f"every frame must be 16x16; found {bad}")
    return [frame.convert("RGBA") for frame in frames]


def pack_spectrum(frames: list[Image.Image]) -> PackedSprite:
    """Pack frames as one bit per pixel, two bytes to a row."""
    data = bytearray()
    mask = bytearray()
    for frame in _checked(frames):
        pixels = frame.load()
        for y in range(SPRITE_SIZE):
            for byte in range(2):
                bits = 0
                holes = 0
                for bit in range(8):
                    x = byte * 8 + bit
                    drawn = pixels[x, y][3] >= ALPHA_THRESHOLD
                    if drawn:
                        bits |= 0x80 >> bit
                    else:
                        holes |= 0x80 >> bit
                data.append(bits)
                mask.append(holes)
    return PackedSprite(bytes(data), bytes(mask), 2, SPRITE_SIZE, len(frames))
```

- [ ] **Step 4: Ejecutar y verificar que pasan**

Run: `.venv/bin/python -m pytest tests/test_spriting.py -q`
Expected: PASS, 5 tests

- [ ] **Step 5: Commit**

```bash
git add llmz80/studio/spriting.py tests/test_spriting.py
git commit -m "feat(studio): pack a sprite into Spectrum bitmap and mask"
```

---

### Task 4: Empaquetar un sprite para el Amstrad CPC

**Files:**
- Modify: `llmz80/studio/spriting.py`
- Test: `tests/test_spriting.py`

CPCtelera ofrece `cpct_drawSpriteMasked(void *sprite, void* memory, u8 width, u8 height)`, que espera **máscara y color intercalados**: por cada byte de pantalla, primero el byte de máscara y después el de color.

**Antes de escribir nada, verifica el convenio de la máscara** en la CPCtelera instalada, en `~/cpctelera/cpctelera/src/sprites/`. Lee la documentación de `cpct_drawSpriteMasked` y comprueba si un bit a 1 conserva el fondo o lo borra. El convenio del Spectrum lo fijamos nosotros; éste lo fija la librería, y equivocarse produce sprites en negativo que compilan y pasan cualquier test de bytes. Registra en un comentario lo que encuentres y dónde lo leíste.

Un sprite de 16 píxeles de ancho ocupa 8 bytes en modo 0 (2 px/byte) y 4 en modo 1 (4 px/byte).

- [ ] **Step 1: Escribir los tests que fallan**

Añadir a `tests/test_spriting.py`:

```python
def test_a_mode_zero_frame_is_eight_bytes_wide_with_the_mask_interleaved():
    packed = pack_cpc([_square()], mode=0, palette=[(255, 255, 255)])

    assert packed.width_bytes == 8
    # Interleaved: one mask byte and one colour byte per screen byte.
    assert len(packed.data) == 2 * 8 * 16


def test_a_mode_one_frame_is_four_bytes_wide():
    packed = pack_cpc([_square()], mode=1, palette=[(255, 255, 255)])

    assert packed.width_bytes == 4
    assert len(packed.data) == 2 * 4 * 16


def test_an_unsupported_mode_is_refused():
    with pytest.raises(ValueError, match="mode"):
        pack_cpc([_square()], mode=2, palette=[(255, 255, 255)])
```

Ampliar el import con `pack_cpc`.

- [ ] **Step 2: Ejecutar y verificar que fallan**

Run: `.venv/bin/python -m pytest tests/test_spriting.py -q`
Expected: FAIL, `ImportError: cannot import name 'pack_cpc'`

- [ ] **Step 3: Implementar**

Añadir a `llmz80/studio/spriting.py` una función `pack_cpc(frames, *, mode, palette)` que:

- refuse cualquier modo que no sea 0 o 1, nombrando el modo recibido;
- calcule los píxeles por byte, 2 en modo 0 y 4 en modo 1, y de ahí el ancho en bytes;
- mapee cada píxel opaco a la pluma más cercana de `palette` — usa distancia euclídea en RGB, que es lo que `image_utils._process_image` ya hace implícitamente al cuantizar;
- construya el byte de color con la codificación de píxeles del modo. **Ésta es la parte que hay que sacar de la documentación de CPCtelera, no de la memoria**: el modo 0 del CPC entrelaza los bits de las dos plumas de un byte de forma no obvia. `~/cpctelera/cpctelera/src/sprites/pixel_macros.h` es el sitio donde mirar. Cita en un comentario la macro concreta en la que te apoyas;
- intercale máscara y color en el orden que `cpct_drawSpriteMasked` espera, con el convenio que hayas verificado.

Devuelve un `PackedSprite` con `mask` vacío, porque en este target la máscara ya viaja dentro de `data`. Documenta esa asimetría en el docstring en lugar de dejarla implícita.

- [ ] **Step 4: Ejecutar y verificar que pasan**

Run: `.venv/bin/python -m pytest tests -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add llmz80/studio/spriting.py tests/test_spriting.py
git commit -m "feat(studio): pack a sprite for CPCtelera's masked blitter"
```

---

### Task 5: Escribir `sprites.h`

**Files:**
- Create: `llmz80/studio/sprite_header.py`
- Test: `tests/test_sprite_header.py`

- [ ] **Step 1: Escribir los tests que fallan**

Crear `tests/test_sprite_header.py`:

```python
"""The generated header, judged as text a compiler will read."""

from llmz80.studio.spriting import PackedSprite
from llmz80.studio.sprite_header import render_sprite_header


def _packed(frames: int = 2) -> PackedSprite:
    return PackedSprite(bytes(2 * 16 * frames), bytes(2 * 16 * frames), 2, 16, frames)


def test_the_header_names_every_sprite_and_its_frames():
    text = render_sprite_header({"hero": _packed(2), "enemy": _packed(1)})

    assert "#define SPRITE_HERO 0" in text
    assert "#define SPRITE_ENEMY 1" in text
    assert "#define SPRITE_COUNT 2" in text
    assert "sprite_frames[]" in text


def test_the_header_compiles_as_declarations_only_once():
    text = render_sprite_header({"hero": _packed(1)})

    assert text.count("#ifndef LLMZ80_SPRITES_H") == 1
    assert "#endif" in text


def test_an_empty_set_still_produces_a_valid_header():
    """A project with no artwork must still compile; the library falls back to shapes."""
    text = render_sprite_header({})

    assert "#define SPRITE_COUNT 0" in text
```

- [ ] **Step 2: Ejecutar y verificar que fallan**

Run: `.venv/bin/python -m pytest tests/test_sprite_header.py -q`
Expected: FAIL, `ModuleNotFoundError`

- [ ] **Step 3: Implementar**

Crear `llmz80/studio/sprite_header.py` con `render_sprite_header(sprites: dict[str, PackedSprite]) -> str`.

**Los símbolos que emite son un contrato con los blitters de Tasks 6 y 7.** Emite
exactamente estos nombres, porque el C de esas tareas ya los usa:

| Símbolo | Qué es |
|---|---|
| `SPRITE_<ID>` | Índice de cada sprite, desde cero, en el orden del diccionario |
| `SPRITE_COUNT` | Cuántos hay; cero desactiva el blitter entero |
| `SPRITE_BYTES_WIDE` | Ancho de un fotograma en bytes: 2 en Spectrum, 8 en CPC modo 0, 4 en modo 1 |
| `sprite_data[]` | Puntero a los bytes de cada sprite, indexado por `SPRITE_<ID>` |
| `sprite_mask[]` | Igual para la máscara. En CPC apunta a `sprite_data` porque la máscara viaja intercalada |
| `sprite_frame_offset[][]` | Desplazamiento en bytes del fotograma `f` del sprite `s`, **ya calculado** |
| `sprite_frames[]` | Cuántos fotogramas tiene cada sprite, para animar sin cablear constantes |
| `sprite_attribute[]` | Byte de atributo por sprite. Sólo Spectrum; en CPC emítelo igualmente a cero para que un mismo programa compile en ambos |

Los bytes van como arrays `const unsigned char`. `sprite_frame_offset` está
precalculado por una razón dura, no por comodidad: `docs/STUDIO_ROADMAP.md`
documenta que el programa no puede usar multiplicación de 16 bits, porque SDCC la
resuelve desde módulos con la ABI que el enlace de CPCtelera rechaza. Multiplicar
`frame * bytes_per_frame` dentro del juego rompe el build en modo release y de
una forma que no se parece en nada a su causa.

Recuerda la restricción ya documentada en `docs/STUDIO_ROADMAP.md`: el código no puede usar división, módulo ni multiplicación de 16 bits, porque SDCC los resuelve desde módulos con la ABI equivocada para el enlace de CPCtelera. Indexar fotogramas debe hacerse por suma acumulada o por tabla, nunca multiplicando dentro del programa. Emite la tabla ya calculada.

- [ ] **Step 4: Ejecutar y verificar que pasan**

Run: `.venv/bin/python -m pytest tests/test_sprite_header.py -q`
Expected: PASS, 3 tests

- [ ] **Step 5: Commit**

```bash
git add llmz80/studio/sprite_header.py tests/test_sprite_header.py
git commit -m "feat(studio): generate the sprite header a program includes"
```

---

### Task 6: El blitter del Spectrum

**Files:**
- Modify: `resources/studio_lib/common/platform.h`, `resources/studio_lib/spectrum/platform.c`
- Test: `tests/test_toolchain_integration.py`

- [ ] **Step 1: Declarar la operación**

En `platform.h`, junto a `plat_cell`:

```c
/* Draws one 16x16 masked sprite whose top-left corner sits at character cell
 * (col, row), so it covers two cells each way. Sprites come from sprites.h,
 * which Studio generates beside your sources; SPRITE_COUNT is zero when the
 * design carries no artwork, and then this does nothing. */
void plat_sprite(unsigned char col, unsigned char row, unsigned char sprite,
                 unsigned char frame);
```

- [ ] **Step 2: Implementar en Spectrum**

En `resources/studio_lib/spectrum/platform.c`. La aritmética de pantalla ya está resuelta por el código existente y debe reutilizarse, no reinventarse: `zx_cxy2saddr(col, row)` da la dirección de la línea 0 de esa celda, y la línea `L` de la misma celda está en `address[L << 8]`. Un sprite de 16 filas cruza dos filas de celda, así que hacen falta dos direcciones base, una por fila de celdas.

```c
void plat_sprite(unsigned char col, unsigned char row, unsigned char sprite,
                 unsigned char frame) {
#if SPRITE_COUNT
    const unsigned char *data;
    const unsigned char *mask;
    unsigned char half;
    unsigned char line;
    if (sprite >= SPRITE_COUNT) return;
    if (col > 30 || row > 22) return;
    /* Frame offsets come precomputed from the header: multiplying here would
     * pull in SDCC's 16-bit routines, which the CPCtelera link rejects and
     * which cost more than a table lookup anyway. */
    data = sprite_data[sprite] + sprite_frame_offset[sprite][frame];
    mask = sprite_mask[sprite] + sprite_frame_offset[sprite][frame];
    for (half = 0; half < 2; ++half) {
        unsigned char *base = (unsigned char *)zx_cxy2saddr(col, row + half);
        for (line = 0; line < 8; ++line) {
            unsigned char *at = base + ((unsigned int)line << 8);
            at[0] = (unsigned char)((at[0] & *mask++) | *data++);
            at[1] = (unsigned char)((at[1] & *mask++) | *data++);
        }
    }
    /* One attribute per covered cell. A single ink per sprite is what the
     * machine affords and what the era used; per-cell colour would need the
     * packer to carry an attribute plane. */
    *(unsigned char *)zx_cxy2aaddr(col, row) = sprite_attribute[sprite];
    *(unsigned char *)zx_cxy2aaddr(col + 1, row) = sprite_attribute[sprite];
    *(unsigned char *)zx_cxy2aaddr(col, row + 1) = sprite_attribute[sprite];
    *(unsigned char *)zx_cxy2aaddr(col + 1, row + 1) = sprite_attribute[sprite];
#else
    (void)col; (void)row; (void)sprite; (void)frame;
#endif
}
```

Añade `#include "sprites.h"` al principio del archivo. `render_project` debe escribir siempre `sprites.h`, aunque esté vacío, o la librería no compilará en un proyecto sin arte — eso es Task 8.

- [ ] **Step 3: Probar que compila y dibuja**

Este es el único paso del plan que necesita la toolchain real. `tests/test_toolchain_integration.py` ya salta cuando falta; sigue ese patrón exacto para no romper CI.

Escribe un test que construya un proyecto con un asset conocido, lo compile con z88dk y compare la captura del emulador contra la de un build idéntico sin el sprite. Que difieran demuestra que algo se dibujó; que el número de píxeles encendidos coincida con los bits a 1 del sprite empaquetado demuestra que se dibujó *eso*. `llmz80/quality/emulator_smoke.py` ya sabe capturar; léelo antes de inventar nada.

Si la comparación exacta de píxeles resulta impracticable con el capturador que hay, dilo en el informe y asegura al menos la diferencia — pero dilo, no lo escondas.

- [ ] **Step 4: Commit**

```bash
git add resources/studio_lib tests/test_toolchain_integration.py
git commit -m "feat(spectrum): blit masked sprites instead of single glyphs"
```

---

### Task 7: El blitter del CPC

**Files:**
- Modify: `resources/studio_lib/cpc/platform.c`
- Test: `tests/test_toolchain_integration.py`

- [ ] **Step 1: Implementar**

El trabajo real lo hace CPCtelera. `cpct_getScreenPtr(CPCT_VMEM_START, x_bytes, y_line)` toma la x en **bytes** y la y en **líneas de píxel**, mientras `plat_cell` la llama con `col * CELL_BYTES` y `row * 8` — mismo convenio, reutilízalo.

```c
void plat_sprite(unsigned char col, unsigned char row, unsigned char sprite,
                 unsigned char frame) {
#if SPRITE_COUNT
    u8 *screen;
    const u8 *bytes;
    if (sprite >= SPRITE_COUNT) return;
    screen = cpct_getScreenPtr(CPCT_VMEM_START, (u8)(col * CELL_BYTES), (u8)(row * 8));
    bytes = sprite_data[sprite] + sprite_frame_offset[sprite][frame];
    /* SPRITE_BYTES_WIDE is 8 in mode 0 and 4 in mode 1: sixteen pixels across,
     * at the mode's pixels per byte. The mask travels interleaved inside the
     * data, which is what cpct_drawSpriteMasked expects. */
    cpct_drawSpriteMasked((void *)bytes, screen, SPRITE_BYTES_WIDE, 16);
#else
    (void)col; (void)row; (void)sprite; (void)frame;
#endif
}
```

Comprueba, y no supongas, si `cpct_drawSpriteMasked` requiere que el sprite esté alineado o que el destino no cruce ciertos límites de memoria de vídeo. El CPC divide la pantalla en ocho bloques y un sprite de 16 líneas puede cruzar uno; si la función no lo gestiona, hay que decirlo en un comentario y acotar dónde puede dibujarse. Esa es la clase de fallo que sólo aparece en la mitad inferior de la pantalla.

- [ ] **Step 2: Probar en la toolchain real**

Mismo enfoque que en Spectrum, con las sondas de memoria del CPC ya sabidas rotas: allí sólo puedes comparar capturas de pantalla, no leer memoria. Léelo en `docs/STUDIO_ROADMAP.md` antes de intentar lo contrario.

- [ ] **Step 3: Commit**

```bash
git add resources/studio_lib/cpc/platform.c tests/test_toolchain_integration.py
git commit -m "feat(cpc): blit masked sprites through CPCtelera"
```

---

### Task 8: Los sprites llegan al build

**Files:**
- Modify: `llmz80/studio/compiler.py`
- Test: `tests/test_studio_compiler.py`

- [ ] **Step 1: Escribir los tests que fallan**

```python
def test_a_project_without_assets_still_gets_a_header(tmp_path):
    """The platform library includes sprites.h unconditionally."""
    project = create_default_project("Bare", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    result = render_project(project, tmp_path / "build")

    header = (result.output_dir / "src" / "sprites.h").read_text(encoding="utf-8")
    assert "#define SPRITE_COUNT 0" in header


def test_an_imported_asset_reaches_the_header(tmp_path):
    from PIL import Image

    service = StudioService.at(tmp_path)
    project, directory = service.create_project(
        "Art", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE
    )
    sheet = tmp_path / "hero.png"
    Image.new("RGBA", (64, 16), (255, 255, 255, 255)).save(sheet)
    service.add_asset(project, directory, sheet)

    result = render_project(project, directory / "build")

    header = (result.output_dir / "src" / "sprites.h").read_text(encoding="utf-8")
    assert "#define SPRITE_COUNT 1" in header
    assert "#define SPRITE_HERO 0" in header
    assert "sprite_frame_offset" in header
```

`add_asset` deriva el identificador del nombre del archivo, así que `hero.png`
produce el sprite `hero`. Comprueba en `services.py` si `add_asset` acepta ya el
número de fotogramas; si no, esta tarea es donde hay que dárselo, y decirlo en el
informe en lugar de dejar todo asset con un fotograma.

- [ ] **Step 2: Implementar**

En `render_project`, después de normalizar los assets y antes de copiar la librería, empaqueta cada asset de tipo `sprite` con el packer del target y escribe `src/sprites.h` con `render_sprite_header`. El presupuesto de datos estáticos ya existe: si los sprites lo superan, falla el build con un mensaje que diga cuántos bytes pesan y cuál es el techo, en lugar de producir un binario que no cabe.

- [ ] **Step 3 y 4: Verificar y commit**

Run: `.venv/bin/python -m pytest tests -q`

```bash
git add llmz80/studio/compiler.py tests/test_studio_compiler.py
git commit -m "feat(studio): pack the project's sprites into every build"
```

---

### Task 9: Decirle al escritor que existen

**Files:**
- Modify: `llmz80/studio/acceptance.py` (`design_prompt`), `llmz80/studio/generator.py`
- Test: `tests/test_studio_generator.py`

Un blitter que el escritor no conoce no dibuja nada. `writing_prompt` ya le enseña `platform.h` entero desde el plan 1, así que `plat_sprite` aparecerá solo — pero no aparecerá **qué sprites tiene este diseño**.

Añade al prompt del diseño la lista de sprites disponibles con su identificador de C, sus fotogramas y qué entidad lleva cada uno, y una frase que diga que los actores se dibujan con `plat_sprite` y el terreno con `plat_cell`. Cuando el proyecto no tiene arte, no digas nada: el prompt ya es largo y una sección que dice "no hay sprites" sólo gasta atención, exactamente como se decidió para la ficha de referencia.

- [ ] **Commit**

```bash
git commit -m "feat(studio): tell the writer which sprites it may draw"
```

---

### Task 10: Generar el arte desde la ficha

**Files:**
- Create: `llmz80/studio/sprite_artist.py`
- Test: `tests/test_sprite_artist.py`

- [ ] **Step 1: Escribir los tests que fallan**

Con un generador falso que devuelve una imagen fija, prueba que:

- el prompt lleva el `visual_style` y el `publisher` de la ficha cuando existe;
- el prompt lleva las restricciones reales del target: monocromo en Spectrum, 16 plumas en modo 0, 4 en modo 1;
- el prompt pide una hoja de cuatro fotogramas con las dimensiones correctas;
- sin ficha, el prompt se construye igual con el rol y el estilo del diseño, porque un proyecto sin juego identificado también necesita arte;
- el resultado se guarda en `assets/` y se registra como `AssetSpec` con sus fotogramas.

- [ ] **Step 2: Implementar**

`sprite_artist.py` compone el prompt desde `resources/sprite_prompt_*.txt`, la ficha y el rol, llama a un `BaseImageGenerator` inyectado — el interfaz ya existe en `generators/base.py`, con implementación OpenAI en `generators/openai_generator.py` — y pasa el resultado por `sprite_sheet.split_frames` y por la cuantización de `image_utils`.

Reutiliza `image_utils._clean_image`, `_scale_image` y `_process_image`. Son funciones privadas por convención, no por diseño: si prefieres promoverlas a públicas antes de depender de ellas desde un módulo nuevo, hazlo en un commit aparte y dilo.

El modelo de imagen no obedece dimensiones pequeñas: pide una hoja grande y reduce con `NEAREST`, que es lo que `_scale_image` ya hace. No intentes que el generador devuelva 64×16.

- [ ] **Step 3: Commit**

```bash
git commit -m "feat(studio): draw a project's sprites in the reference's style"
```

---

### Task 11: Comando y revisión

**Files:**
- Modify: `llmz80/studio/services.py`, `llmz80/cli.py`
- Test: `tests/test_studio_cli.py`

`StudioService.draw_sprites(project, directory, artist)` genera el arte que falta y lo registra. `llmz80 project sprites PATH` lo invoca, avisa de que gasta dinero antes de gastarlo — como hacen `write`, `reference` y `adapt` — y muestra cada sprite como pixel art en el terminal con `image_utils.display_sprite` para que se pueda mirar antes de compilar.

Pregunta antes de sobrescribir arte que ya existe, por el mismo motivo que `reference` pregunta antes de pisar una ficha corregida a mano.

- [ ] **Commit**

```bash
git commit -m "feat(cli): draw and review a project's sprites"
```

---

### Task 12: Documentar

**Files:**
- Modify: `README.md`, `docs/STUDIO_ROADMAP.md`

El roadmap tiene, en "Still open", este punto:

> Imported assets are normalised and packed, but the engine draws built-in cell shapes and never references them. Masked sprite blitting is required before assets reach the screen.

Bórralo sólo si de verdad quedó cerrado, y comprueba antes si algún otro punto de esa lista lo quedó también. Añade la fila S12 con la evidencia que exista, no con la que esperabas. Si el blitter del CPC quedó acotado a parte de la pantalla, o la comparación de píxeles no llegó a hacerse, eso va en la columna de evidencia.

- [ ] **Commit**

```bash
git commit -m "docs: record that sprites now reach the screen"
```

---

## Verificación final del plan

- [ ] `.venv/bin/python -m pytest tests` pasa entero
- [ ] Un proyecto sin arte sigue compilando y jugándose igual que antes
- [ ] `llmz80 project sprites` produce arte reconocible en el terminal
- [ ] El `.tap` resultante enseña sprites de 16×16 animados donde antes había un glifo de 8×8
- [ ] Superar el presupuesto de datos estáticos falla el build con el número exacto, no con un binario roto
