# Anthropic y sprites por rejilla — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sacar a OpenAI del flujo vivo de Studio. El texto pasa a Claude; los sprites dejan de venir de un modelo de imagen y los dibuja Claude como rejilla de índices de paleta; los embeddings dejan de ser una llamada de red.

**Architecture:** Tres migraciones que no se bloquean entre sí. (1) Los ocho sitios que hoy llaman `client.responses.parse(text_format=...)` tienen exactamente la misma forma, así que se sustituyen por un único adaptador `structured` sobre `client.messages.parse(output_format=...)` y cada llamada queda en una línea. (2) `SpriteArtist` gana un seam nuevo — `SheetSource` — con dos implementaciones: la actual (modelo de imagen, 1024px, recorte y keying) y una nueva que pide a Claude una rejilla de 16×16 índices de paleta y la convierte en frames exactos. El bucle de reintento con feedback y `_judge_frames` son agnósticos y se quedan tal cual. (3) `EmbeddingsManager` cambia el backend a `fastembed`, que ya viene con `qdrant-client`.

**Tech Stack:** Python 3.10+, `anthropic` (SDK oficial), pydantic v2, Pillow, fastembed, qdrant-client, pytest.

**Decisiones tomadas (2026-08-16):** modelo de texto = `claude-opus-5` · sprites = Claude dibuja la rejilla, sin modelo de imagen · embeddings = fastembed local · alcance = sólo `llmz80/studio/*` + `llmz80/cli.py`; `llm_z80.py` y `llmz80/api/generator.py` se quedan en OpenAI.

---

## Contexto que el ejecutor necesita

### Lo que hoy toca OpenAI en Studio

Ocho llamadas, **todas con la misma forma**:

```python
response = self.client.responses.parse(
    model=self.model,                                  # "gpt-5"
    input=[{"role": "system", "content": SYSTEM},
           {"role": "user",   "content": content}],
    text_format=SomePydanticModel,
)
result = response.output_parsed
```

| Fichero | Línea | `text_format` |
|---|---|---|
| `studio/drafting.py` | 269 | `ProjectProposal` |
| `studio/reference_design.py` | 110 | `ProjectProposal` |
| `studio/planner.py` | 283 | `ProjectProposal` |
| `studio/design_exam.py` | 223 | `BriefCoverage` |
| `studio/design_exam.py` | 376 | `DesignCoherence` |
| `studio/generator.py` | 262 | `ProgramSources` |
| `studio/runtime_exam.py` | 689 | `RuntimeExam` |
| `studio/reference.py` | 179 | `GameReference` + `tools=[{"type": "web_search_preview"}]` |

Sólo `reference.py` se sale del molde, por la búsqueda web.

El cliente se construye en un sitio, `llmz80/cli.py:38` `_openai_client_and_model()`, y el generador de imágenes se cablea en `llmz80/studio/pipeline.py:358-367`.

### Correspondencia con la API de Anthropic

```python
response = client.messages.parse(
    model="claude-opus-5",
    max_tokens=16000,
    system=SYSTEM,                                     # parámetro propio, no un mensaje
    messages=[{"role": "user", "content": content}],
    output_format=SomePydanticModel,
)
result = response.parsed_output
```

Tres diferencias que importan:

- El prompt de sistema es el parámetro `system`, no el primer elemento de `input`.
- `max_tokens` es **obligatorio**. `generator.py` escribe programas de C enteros: dale holgura (16000 no-streaming; si algún sitio corta, ver la nota de streaming abajo).
- El resultado está en `.parsed_output`, no en `.output_parsed`.

`config.yml` tiene `temperature: 0.3`. En Claude Opus 5 `temperature` **está eliminado y devuelve 400** — hay que borrar la clave, no ignorarla. `reasoning_effort: medium` tampoco existe: el equivalente es `output_config={"effort": ...}` y su valor por defecto ya es `high`, así que la traducción correcta es no pasar nada.

**Punto a verificar antes de escribir el adaptador:** si `messages.parse()` acepta `output_format=` y `output_config=` a la vez, o si chocan (uno rellena `output_config.format`). Si chocan, y hace falta fijar `effort`, la salida es `messages.create()` con `output_config={"format": {...}, "effort": ...}` y parseo manual. Mientras no haga falta tocar `effort`, no hay problema.

Búsqueda web en `reference.py:196`: `{"type": "web_search_preview"}` → `{"type": "web_search_20260209", "name": "web_search"}`. El comentario que hay ahí explicando por qué se usa `web_search_preview` y no `web_search` es sobre el SDK de OpenAI; se borra, no se traduce.

### Por qué los sprites cambian de enfoque

`sprite_artist.py` son 965 líneas casi todas dedicadas a rescatar 16×16 píxeles de un PNG de 1024×1024 que un modelo de foto devolvió con antialiasing, halo y fondo que no es el que se pidió. `_detect_background`, `_key_out_background`, `HALO_TOLERANCE = 40` y su docstring de veinte líneas sobre histogramas por columna, `_clean_image`, `_fit_to_frame`, `_scale_image`: todo eso es reparación de daño causado por el formato de salida.

Claude puede emitir directamente la rejilla. Un sprite de Spectrum es 16×16 monocromo; uno de CPC son 16×16 índices sobre una paleta de 4 entradas (`studio/compiler.py:50` `CPC_DEFAULT_PALETTE`). Eso son 256 caracteres por frame, cuatro frames por hoja. Con `output_format` la forma está garantizada por el esquema, y **el antialiasing es imposible por construcción**: no hay canal donde meterlo.

Lo que se conserva porque es agnóstico del proveedor:

- `_judge_frames` (rechaza el frame en blanco y el bloque sólido) y su bucle de reintento con feedback en `draw_frames`.
- `MAX_DRAW_ATTEMPTS = 3`.
- `services.StudioService._save_raw_sheet` — la rejilla se renderiza a PNG para que un fallo siga dejando evidencia en disco.
- Todo lo de `spriting.py` aguas abajo: `pack_spectrum` y `pack_cpc` reciben `list[Image.Image]` de 16×16 RGBA y no se enteran de nada.

### Contrato de la rejilla

Un carácter por píxel:

- `.` = transparente (alpha 0; `spriting.ALPHA_THRESHOLD = 128` decide).
- `0`–`f` = índice de pen, opaco, con el RGB de la paleta de la plataforma.

Pens legales por objetivo, que el validador **rechaza** si se incumplen:

| Objetivo | Pens | Paleta |
|---|---|---|
| Spectrum | sólo `0` | monocromo; `pack_spectrum` deriva el atributo del RGB opaco dominante |
| CPC mode 0 | `0`–`f` | 16 pens **pero** `compiler.py:297` empaqueta con `CPC_DEFAULT_PALETTE`, que tiene 4 entradas — **verificar** antes de permitir más de `0`–`3` |
| CPC mode 1 | `0`–`3` | `CPC_DEFAULT_PALETTE` |
| CPC mode 2 | `0`–`1` | `CPC_DEFAULT_PALETTE[:2]` |

Un pen fuera de rango es un fallo de validación que alimenta el reintento con feedback, igual que hoy hace `_judge_frames`.

---

## Tareas

### Fase 1 — Cliente Anthropic y las ocho llamadas

- [ ] **1. Añadir la dependencia.** `anthropic` en `requirements.txt` y en `pyproject.toml`. `openai==1.75.0` **se queda**: `llm_z80.py` y `llmz80/api/generator.py` siguen usándola (fuera de alcance).

- [ ] **2. Escribir `llmz80/studio/llm.py` con el adaptador `structured`.** Firma: `structured(client, model, *, system, user, schema, max_tokens=16000)` → instancia de `schema`. Encapsula `messages.parse`, la traducción system-como-parámetro y `.parsed_output`. Ocho sitios comparten esta función; el fake de los tests pasa a ser uno solo en vez de cinco. Test primero: un cliente falso que registra los kwargs y devuelve un `parsed_output` fijo.

- [ ] **3. Migrar `cli.py:38` `_openai_client_and_model()`.** Renombrar a `_llm_client_and_model()`; `from anthropic import Anthropic`; leer `config.yml` de la sección `anthropic` con defecto `claude-opus-5`. La clave sale de `ANTHROPIC_API_KEY` — ver tarea 4. Mantener el import local a la función, tal como está hoy y por la razón que dice su docstring.

- [ ] **4. `llmz80/utils/config.py:load_api_key()`.** Hoy exige `OPENAI_API_KEY`. Necesita leer `ANTHROPIC_API_KEY` para Studio sin romper a los llamadores legacy que siguen queriendo la de OpenAI. Parámetro `provider` con defecto explícito, o una función hermana `load_anthropic_api_key()` — lo segundo es menos invasivo. Actualizar `.env.example`.

- [ ] **5. Migrar las siete llamadas sin búsqueda web** a `structured` (tabla de arriba, todas menos `reference.py`). Cada una queda en una llamada de una línea con su `schema`. Los prompts de sistema no se tocan: son buenos y están afinados.

- [ ] **6. Migrar `reference.py:179`,** que además lleva búsqueda web. No pasa por `structured` (o `structured` gana un parámetro `tools=`, a elección del ejecutor): `tools=[{"type": "web_search_20260209", "name": "web_search"}]`. Borrar el comentario sobre `web_search_preview`. **Verificar** que la búsqueda web y `output_format` conviven en la misma petición; si no, la salida es dos turnos (buscar, luego estructurar).

- [ ] **7. `config.yml`.** Sección `anthropic:` con `model: claude-opus-5`. **Borrar `temperature`** (da 400 en Opus 5) y `reasoning_effort` (no existe; el defecto ya es `high`). La sección `openai:` se queda con `embedding_model` y `image_model` hasta que las fases 2 y 3 los retiren.

- [ ] **8. Actualizar los tests de estructura.** `tests/test_studio_drafting.py`, `test_studio_generator.py`, `test_studio_cli.py`, `test_studio_reference_design.py`, `test_studio_reference.py` inspeccionan `client.responses.calls[...]["input"][1]["content"]`. Con `structured` el fake es uno y la aserción pasa a mirar `messages`/`system`. `tests/conftest.py:mock_openai_client` y `temp_config_dir` también.

- [ ] **9. Texto de usuario.** `cli.py:15,25,28,29,417` dicen "calls the OpenAI API". `studio/reference.py:172` y `reference_design.py:88` dicen "OpenAI Responses API" en sus docstrings.

- [ ] **10. Verificar de punta a punta.** `pytest`, luego una ejecución real de `llmz80 project draft` sobre un brief pequeño. Registrar aquí la salida.

### Fase 2 — Sprites por rejilla

- [ ] **11. Introducir el seam `SheetSource` en `sprite_artist.py`.** Protocolo con un método que, dado el prompt compuesto, devuelva `list[Image.Image]` de `FRAMES_PER_SHEET` frames RGBA exactos de `SPRITE_SIZE`×`SPRITE_SIZE`, más la hoja cruda para `_save_raw_sheet`. `draw_frames` pasa a llamar al source en vez de a `self.generator.generate_image` + `_sheet_columns` + `_frame_from_column`. **Refactor puro: sin cambio de comportamiento.** La ruta actual se envuelve en `ImageModelSheetSource` y los tests existentes de `sprite_artist` siguen pasando sin tocarse.

- [ ] **12. Definir el esquema de la rejilla** en `sprite_artist.py` o un módulo hermano. `SpriteSheet` con `frames: list[SpriteFrame]`, `SpriteFrame` con `rows: list[str]`. Validadores pydantic: exactamente `FRAMES_PER_SHEET` frames, exactamente `SPRITE_SIZE` filas, cada fila exactamente `SPRITE_SIZE` caracteres, cada carácter en el alfabeto legal de la plataforma. Test primero, con los casos malos: fila corta, pen ilegal, número de frames erróneo.

- [ ] **13. Escribir la conversión rejilla → frames.** Pura, sin red: `(SpriteSheet, paleta) -> list[Image.Image]`. `.` sale con alpha 0, un índice sale opaco con el RGB de la paleta. Test contra una rejilla escrita a mano, comprobando píxeles concretos y que `spriting.pack_spectrum` / `pack_cpc` aceptan el resultado.

- [ ] **14. Resolver la paleta por plataforma y modo.** Una función que dada `TargetPlatform` y `VideoMode` devuelva alfabeto legal + lista de RGB. **Verificar primero** el desajuste señalado arriba: `compiler.py:297` empaqueta el CPC con `CPC_DEFAULT_PALETTE` (4 entradas) sea cual sea el modo, así que permitir `0`–`f` en mode 0 produciría índices que el packer no puede resolver. Decidir con el código en la mano, no de memoria, y dejar constancia de la decisión aquí.

- [ ] **15. Escribir `ClaudeGridSheetSource`.** Llama a `structured` (fase 1) con `output_format=SpriteSheet`, convierte con la tarea 13 y renderiza la rejilla a un PNG ampliado por vecino más próximo para `sheets`, de forma que `_save_raw_sheet` siga dejando evidencia legible de cada intento fallido.

- [ ] **16. Reescribir las plantillas de prompt.** `resources/sprite_prompt_{spectrum,amstrad_cpc_mode0,amstrad_cpc_mode1,amstrad_cpc_mode2,generic}.txt` piden hoy "a image", "pure white background (RGB 255,255,255)", "NO anti-aliasing". Nada de eso aplica: ahora se pide una rejilla de caracteres. Cada plantilla conserva su conocimiento real de la máquina (monocromo en Spectrum, pens por modo en CPC) y describe el alfabeto y las dimensiones. La instrucción "no antialiasing" se borra: ya no es posible.

- [ ] **17. Cablear `pipeline.py:358-367`** para construir `SpriteArtist(ClaudeGridSheetSource(...))` en vez de `SpriteArtist(OpenAIImageGenerator(...))`.

- [ ] **18. Retirar el código muerto.** Con `ImageModelSheetSource` ya sin llamadores en Studio, `_detect_background`, `_key_out_background`, `_binarize_against_background`, `_fit_to_frame`, `HALO_TOLERANCE`, `BACKGROUND_COLOR`, `BACKGROUND_TOLERANCE`, `REQUEST_FRAME_SIZE` y compañía quedan huérfanos. **Comprobar antes de borrar** si `llm_sprites.py` o `generate_sprite.sh` (legacy, fuera de alcance) los importan. `generators/openai_generator.py` y `tests/test_openai_image_generator.py`: borrar sólo si nadie fuera de Studio los usa — `llm_sprites.py` construye `OpenAIImageGenerator` sin argumento `model`, así que probablemente se quedan.

- [ ] **19. Prueba real.** Generar sprites de un proyecto de `studio-projects/` con las dos plataformas y mirar los PNG. **Éste es el punto de decisión del enfoque D:** si la calidad espacial de Claude a 16×16 no da la talla, el respaldo acordado es una API nativa de pixel art (PixelLab / Retro Diffusion) detrás del mismo `SheetSource`, y las tareas 11-14 siguen valiendo enteras. Registrar aquí el veredicto con las imágenes.

### Fase 3 — Embeddings locales

- [ ] **20. Cambiar el backend de `llmz80/core/embeddings.py:54,114`** de `client.embeddings.create` a `fastembed` (ya viene con `qdrant-client==1.18.0`; confirmar que la versión instalada lo trae). Modelo por defecto: `BAAI/bge-small-en-v1.5`, 384 dimensiones.

- [ ] **21. Consecuencia: reindexar.** Las dimensiones cambian de 1536 a 384, así que las colecciones de Qdrant existentes y la caché de `local/embeddings` quedan inválidas. `scripts/init_qdrant.py` e `init_embeddings.py` tienen que recrear la colección, no añadir a la vieja. `init_embeddings.py:8` importa `OpenAI` directamente.

- [ ] **22. `config.yml`:** mover `embedding_model` fuera de la sección `openai:` a una `embeddings:` propia. Actualizar `utils/config.py:DEFAULT_EMBEDDING_MODEL`.

- [ ] **23. Verificar** que la ruta RAG de `api/generator.py` sigue funcionando o degrada limpiamente. El README dice que el camino principal es el catálogo local determinista y que Qdrant sólo lo amplía, así que un fallo aquí no debe romper una generación.

### Fase 4 — Cierre

- [ ] **24. README y CHANGELOG.** El badge de OpenAI GPT-5, "Usa modelos OpenAI configurables", y la mención del modelo de imagen en el comentario de `config.yml`.

- [ ] **25. Barrido final.** `grep -rn "openai\|OpenAI\|gpt-" llmz80/ resources/ config.yml` no debe devolver nada en la ruta de Studio. Lo que quede en `llm_z80.py`, `llmz80/api/`, `init_embeddings.py` y `generators/openai_generator.py` es legacy y está fuera de alcance por decisión.

---

## Riesgos anotados

**El enfoque D no está validado.** La tarea 19 es una puerta real, no un trámite. Nadie ha comprobado todavía si Claude dibuja un sprite reconocible de 16×16 a base de caracteres. El plan está construido para que un "no" ahí cueste sólo la tarea 15 y las plantillas: el seam, el esquema, la conversión y la paleta valen igual con una API de pixel art detrás.

**El desajuste de paleta del CPC (tarea 14) es anterior a este plan.** `pack_cpc` acepta un parámetro `palette` pero `compiler.py` siempre le pasa las mismas 4 entradas, incluso en mode 0, que admite 16. Este plan no lo arregla; lo que hace es no empeorarlo permitiendo pens que el packer no sabe resolver.

**Fase 1 y fase 3 son independientes.** Fase 2 depende de la 1 sólo por `structured`. Se pueden ejecutar en ese orden o en paralelo por ramas distintas.

---

## Estado de ejecución — 2026-08-16

**Fases 1, 3 y 4 completas. Fase 2 completa salvo la tarea 19, que no puedo
ejecutar yo.** Suite: 948 pasan, 0 fallan.

### Verificaciones que el plan dejó abiertas, ahora resueltas

- **`output_format` + `output_config` no chocan.** `messages.parse` *fusiona*
  el primero dentro del segundo (`anthropic` 0.122.0,
  `resources/messages/messages.py:1275-1283`), así que `effort` se puede
  añadir después sin reescribir nada. El adaptador no lo pasa porque el
  defecto ya es el valor alto.
  *Corregido 2026-08-17: `structured()` ya no llama a `parse` sino a `stream`
  (un `max_tokens` grande no se puede pedir sin streaming), y la fusión
  equivalente en ese camino está en `messages.py:1156`. La cita de arriba
  sigue siendo correcta para `parse`; no es el camino que Studio toma.*
- **Búsqueda web y `output_format` conviven** en la misma llamada: `parse`
  acepta `tools` y `system` junto al esquema. Que el servidor lo acepte en
  vivo sigue sin comprobarse: hace falta una clave.
- **`VideoMode` sólo tiene tres miembros**, no cuatro. No existe
  `CPC_MODE_2` pese a que hay un `resources/sprite_prompt_amstrad_cpc_mode2.txt`
  huérfano. La tabla de la tarea 14 estaba mal.
- **Los pens legales del CPC son `0`–`3` en los dos modos**, no `0`–`f`:
  `compiler.py:297` empaqueta ambos con `CPC_DEFAULT_PALETTE`, que tiene
  cuatro entradas. Ofrecer dieciséis habría dejado al modelo elegir un pen
  que el packer no sabe resolver.
- **`fastembed` NO viene con `qdrant-client`.** El plan decía que sí. Es una
  dependencia aparte, ya añadida a `requirements.txt` y `pyproject.toml`.

### Desviaciones deliberadas del plan

- **La tarea 18 (retirar código muerto) no se ha hecho, a propósito.**
  `_detect_background`, `_key_out_background`, `HALO_TOLERANCE`,
  `_fit_to_frame` y compañía siguen vivos bajo `ImageModelSheetSource`, y las
  plantillas `sprite_prompt_*.txt` siguen intactas. Borrarlos antes de que la
  tarea 19 diga que el enfoque D vale convertiría un "no" en una
  reconstrucción. Se borran cuando la puerta pase, no antes.
- **La tarea 16 añade plantillas nuevas (`resources/sprite_grid_*.txt`) en vez
  de reescribir las viejas**, por la misma razón.
- **El seam creció**: `SheetSource` tiene `compose` además de `draw`, porque
  los dos caminos quieren prompts genuinamente distintos y el artista no debe
  saber con qué clase de modelo habla.

### Defecto encontrado y corregido durante la migración

Renombrar `_openai_client_and_model` dejó a `pipeline.py` pasándole la clave
de **Anthropic** a la API de imágenes de **OpenAI**. Vivió unos minutos entre
dos commits que no existen; la rama entera se sustituyó después por
`ClaudeGridSheetSource`.

### Lo que queda

- [ ] **Tarea 19: la puerta.** No hay `ANTHROPIC_API_KEY` en el entorno ni en
      `.env`, así que no he podido dibujar un solo sprite de verdad. Corre
      `ANTHROPIC_API_KEY=... python scripts/draw_sprite_probe.py`, abre los
      PNG de `local/sprite_probe/` y decide. **Nadie ha comprobado todavía si
      Claude dibuja algo reconocible a 16x16.** Todo lo demás está construido
      para que un "no" cueste una clase.
- [ ] **Reindexar Qdrant y `local/embeddings`.** Los vectores pasan de 1536 a
      384; lo viejo no se migra, se recrea.
- [ ] Una ejecución real de `llmz80 project draft` contra la API, por el mismo
      motivo que la tarea 19: nada de esto ha hablado con el servidor.
