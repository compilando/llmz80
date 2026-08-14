# Suelo de calidad y motores externos — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cerrar el agujero por el que hoy sale aprobado un juego que nadie ha observado, y dejar montado el seam por el que entrarán motores externos vendorizados.

**Architecture:** Dos mitades independientes. La primera (tareas 1-10) endurece el aparato de verificación que ya existe: un guion de observación agnóstico de género alimenta las sondas de memoria, tres puertas nuevas juzgan esas lecturas (ritmo de frames, contenido invisible, cobertura del brief), y ni el release ni el bucle de escritura pueden volver a confundir una abstención con un aprobado. La segunda (tareas 11-12) introduce `EnginePack`: motores de terceros vendorizados a commit fijado, con licencia comprobada y con un `probe_map` que permite que todas las puertas anteriores sigan valiendo cuando el código del juego lo escriba otro.

**Tech Stack:** Python 3.10+, pydantic v2, pytest, z88dk/zcc, CPCtelera/SDCC, ZEsarUX (protocolo ZRCP), Caprice32.

**Decisiones tomadas (2026-08-14):** objetivo = pipeline de muchos juegos decentes · licencia GPL aceptable para lo generado · CPCtelera primero · el escritor libre de C se retira cuando dos motores externos funcionen · detalle ejecutable sólo para el horizonte 1.

---

## Contexto que el ejecutor necesita

El sistema genera juegos para ZX Spectrum 48K y Amstrad CPC. `game.yml` (schema v4, `llmz80/studio/models.py`) describe el diseño; una LLM escribe el programa entero en C (`llmz80/studio/generator.py`); se compila con la toolchain real y se ejecuta en un emulador headless (`llmz80/quality/emulator_smoke.py`).

**El defecto central que este plan ataca.** `llmz80/studio/generator.py:write_program` acepta un intento con:

```python
if (
    attempt.build_passed
    and attempt.acceptance_passed is not False
    and attempt.animation_passed is not False
):
```

`is not False` significa que una puerta que **se abstuvo** (`None`) cuenta como aprobada. Y hoy las tres puertas de comportamiento se abstienen siempre:

- `llmz80/studio/acceptance.py:runtime_script` devuelve `[]` a propósito (el examinador es trabajo futuro).
- `llmz80/studio/services.py:probe_report` devuelve `quality_pass: None` siempre.
- `llmz80/studio/services.py:runtime_test` llama a `smoke_test(..., script=[])`, así que `step_readings` sale vacío y `llmz80/studio/feel.py:animation_report` también se abstiene.

Resultado medido: `studio-projects/zampabolas/write_report.json` registra `accepted: true` en el intento 1 con `acceptance_passed: null` y `animation_passed: null`, para un programa de 163 líneas que dibuja un glifo `'o'` y termina la partida al pulsar ACTION.

**Lo que NO hay que tocar.** `runtime_script` sigue devolviendo `[]`. Derivar expectativas del diseño es el examinador del horizonte 2. Este plan produce **lecturas** y puertas que juzgan lo que es universalmente cierto de cualquier juego (el ritmo, la visibilidad, la animación), no lo que es cierto de un juego concreto.

---

## File Structure

**Se crean:**

| Fichero | Responsabilidad |
|---|---|
| `llmz80/studio/observation.py` | El guion que el emulador ejecuta para que haya algo que leer. No juzga nada |
| `llmz80/studio/pacing.py` | Juzga `g_worst_frame_cost` contra un techo de frames perdidos |
| `llmz80/studio/attributes.py` | Lee un volcado de pantalla y encuentra celdas cuyo contenido es invisible |
| `llmz80/studio/design_exam.py` | Examina si el diseño cubre lo que el brief pide |
| `llmz80/studio/engines.py` | `EnginePack`, registro de motores y puerta de licencia |
| `scripts/vendor_engine.py` | Clona un motor a commit fijado y escribe su manifiesto |
| `tests/test_studio_observation.py` | |
| `tests/test_studio_pacing.py` | |
| `tests/test_studio_attributes.py` | |
| `tests/test_studio_design_exam.py` | |
| `tests/test_studio_engines.py` | |

**Se modifican:**

| Fichero | Cambio |
|---|---|
| `llmz80/studio/quality.py` | `verification_level()`; la ausencia de mecánicas con brief pasa de aviso a fallo |
| `llmz80/studio/release.py` | Se niega a exportar lo que no fue observado |
| `llmz80/studio/services.py` | Pasa el guion; añade las puertas de ritmo y atributos |
| `llmz80/studio/generator.py` | El bucle exige las puertas nuevas; `repair_prompt` las traduce |
| `llmz80/studio/pipeline.py` | `write` se niega ante un diseño que no pasa su puerta; `adapt` examina el brief |
| `llmz80/core/state_contract.py` | `g_worst_frame_cost` pasa a requerido |
| `llmz80/studio/probes.py` | `contract_failures()` |
| `llmz80/studio/compiler.py` | Un símbolo requerido ausente rechaza el build |
| `llmz80/quality/emulator_smoke.py` | Vuelca los 6912 bytes de pantalla al final del guion |
| `.gitignore` | `vendor/` |

**Orden y dependencias:** 1→2. 3→4→6. 5→6. 9→10. 7→8. 11→12. Los cinco grupos son independientes entre sí y pueden ejecutarse en cualquier orden.

**Comandos del proyecto:** `make test` corre la suite. Un test suelto: `.venv/bin/python -m pytest tests/test_x.py::test_y -v`.

---

## Task 1: El nivel de verificación de un juego

Un juego pasa a llevar declarado **cómo de verificado está**, en vez de un booleano que no distingue «compiló» de «se le vio funcionar».

**Files:**
- Modify: `llmz80/studio/quality.py`
- Test: `tests/test_studio_quality.py`

- [ ] **Step 1: Write the failing test**

Añadir al final de `tests/test_studio_quality.py`:

```python
from llmz80.studio.quality import VERIFICATION_BUILT, VERIFICATION_OBSERVED, verification_level


def test_a_run_where_every_behaviour_gate_abstained_is_only_built():
    """Three gates that never watched cannot add up to a verified game: this is
    the exact shape `runtime_test` produces today for a v4 project."""
    runtime = {
        "quality_pass": True,
        "acceptance": {"quality_pass": None},
        "animation": {"quality_pass": None},
        "state_probe": {"quality_pass": None},
    }

    assert verification_level(runtime) == VERIFICATION_BUILT


def test_one_gate_that_actually_watched_and_passed_makes_it_observed():
    runtime = {
        "quality_pass": True,
        "acceptance": {"quality_pass": None},
        "animation": {"quality_pass": True},
        "state_probe": {"quality_pass": None},
    }

    assert verification_level(runtime) == VERIFICATION_OBSERVED


def test_a_gate_that_watched_and_refused_is_not_observed():
    runtime = {"animation": {"quality_pass": False}}

    assert verification_level(runtime) == VERIFICATION_BUILT


def test_no_runtime_at_all_is_only_built():
    assert verification_level(None) == VERIFICATION_BUILT


def test_the_quality_report_carries_the_level():
    from llmz80.studio.models import TargetPlatform
    from llmz80.studio.samples import blank_project

    project = blank_project("Levelled", TargetPlatform.SPECTRUM)
    report = studio_quality_report(
        project,
        build={"quality_pass": True},
        runtime={"quality_pass": True, "animation": {"quality_pass": True}},
    )

    assert report["verification"] == VERIFICATION_OBSERVED
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_studio_quality.py -v -k verification`
Expected: FAIL con `ImportError: cannot import name 'verification_level'`

- [ ] **Step 3: Write minimal implementation**

En `llmz80/studio/quality.py`, tras los imports:

```python
#: The game built and its artifact is valid, and that is the whole of what is
#: known about it. Every behaviour gate abstained.
VERIFICATION_BUILT = "built"

#: At least one behaviour gate actually watched the program run and approved
#: what it saw.
VERIFICATION_OBSERVED = "observed"

#: The gates whose verdict says something was watched. Read by name off the
#: runtime report so a gate added later (see `pacing`, `attributes`) counts
#: the moment it is wired in, without this function learning about it.
BEHAVIOUR_GATES = ("acceptance", "animation", "state_probe", "pacing", "attributes")


def verification_level(runtime: dict[str, Any] | None) -> str:
    """How much is actually known about this program's behaviour.

    Three verdicts are possible from a gate and they are not two: `True` (it
    watched and approved), `False` (it watched and refused) and `None` (it
    abstained -- no adapter, no script, nothing to judge). Folding `None` into
    `True` is the defect this function exists to make impossible: it is what
    let `studio-projects/zampabolas` be accepted on its first attempt with
    every behaviour gate unobserved.

    A single definite `True` is enough. Demanding all of them would make the
    level unreachable until the phase 2 examiner lands, and an unreachable
    level teaches people to pass `--force`.
    """
    if not runtime:
        return VERIFICATION_BUILT
    verdicts = [(runtime.get(name) or {}).get("quality_pass") for name in BEHAVIOUR_GATES]
    if any(verdict is False for verdict in verdicts):
        return VERIFICATION_BUILT
    return VERIFICATION_OBSERVED if any(verdict is True for verdict in verdicts) else VERIFICATION_BUILT
```

En `studio_quality_report`, añadir la clave al dict devuelto, justo antes de `"quality_pass"`:

```python
        "verification": verification_level(runtime),
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_studio_quality.py -v`
Expected: PASS (toda la clase, no sólo los nuevos)

- [ ] **Step 5: Commit**

```bash
git add llmz80/studio/quality.py tests/test_studio_quality.py
git commit -m "feat(studio): say how verified a game is instead of implying it"
```

---

## Task 2: El release exige haber observado el juego

**Files:**
- Modify: `llmz80/studio/release.py:14-24`
- Test: `tests/test_studio_release.py`

- [ ] **Step 1: Write the failing test**

Añadir a `tests/test_studio_release.py`:

```python
def test_a_game_nobody_observed_is_not_released(tmp_path):
    """The build passed and every behaviour gate abstained. That is a candidate,
    not a release, and the difference has to be enforced somewhere the operator
    cannot skip by accident."""
    from llmz80.studio.models import TargetPlatform
    from llmz80.studio.release import export_release
    from llmz80.studio.samples import blank_project

    project = blank_project("Unwatched", TargetPlatform.SPECTRUM)
    build = tmp_path / "build"
    build.mkdir()
    (tmp_path / "game.yml").write_text("schema_version: 4\n", encoding="utf-8")
    (build / "output.tap").write_bytes(b"\x13\x00tap")
    (build / "build_report.json").write_text("{}", encoding="utf-8")
    (build / "emulator_report.json").write_text("{}", encoding="utf-8")
    (build / "studio_quality_report.json").write_text(
        json.dumps({"quality_pass": True, "verification": "built"}), encoding="utf-8"
    )

    with pytest.raises(RuntimeError, match="was never observed"):
        export_release(project, tmp_path)
```

Asegurar que `json` y `pytest` están importados al principio del fichero de test.

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_studio_release.py -v -k observed`
Expected: FAIL — no se lanza `RuntimeError`, el zip se crea

- [ ] **Step 3: Write minimal implementation**

En `llmz80/studio/release.py`, tras la comprobación de `quality_pass`:

```python
    if not quality.get("quality_pass"):
        raise RuntimeError("release export requires every Studio quality gate to pass")
    if quality.get("verification") != VERIFICATION_OBSERVED:
        raise RuntimeError(
            "this game built and its gates all abstained, so it was never observed "
            "running: release refuses it. Run the runtime test on a target with a "
            "memory probe adapter, or fix whatever made every behaviour gate abstain"
        )
```

Y el import arriba:

```python
from .quality import VERIFICATION_OBSERVED
```

Añadir el nivel a las notas del release, en la construcción de `notes`:

```python
        f"Verification: {quality.get('verification')}\n"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_studio_release.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add llmz80/studio/release.py tests/test_studio_release.py
git commit -m "feat(studio): refuse to release a game nobody watched run"
```

---

## Task 3: El guion de observación

El emulador ya sabe ejecutar pasos con tecla, duración y lectura de memoria (`emulator_smoke.py:_run_zesarux`, líneas ~292-317). Nadie le da pasos. Esta tarea escribe los pasos; **no** dice qué debería pasar.

**Files:**
- Create: `llmz80/studio/observation.py`
- Test: `tests/test_studio_observation.py`

- [ ] **Step 1: Write the failing test**

Crear `tests/test_studio_observation.py`:

```python
"""The steps the emulator drives, which state no expectation about the game."""

from llmz80.studio.models import TargetPlatform
from llmz80.studio.observation import STEP_FRAMES, observation_script
from llmz80.studio.samples import blank_project


def test_every_binding_is_held_twice_and_then_let_go():
    """Twice because `feel.animation_report` compares consecutive readings, and
    one reading of a moving step has nothing to be compared against."""
    project = blank_project("Observed", TargetPlatform.SPECTRUM)

    script = observation_script(project)

    ids = [step["id"] for step in script]
    assert ids[-1] == "idle"
    assert ids.count("hold_left_a") == 1
    assert ids.count("hold_left_b") == 1
    assert len(ids) == len(set(ids))
    assert len(script) == 2 * len(project.controls.bindings) + 1


def test_a_direction_binding_holds_as_movement_and_anything_else_as_action():
    """`feel._classify` reads `hold`, so this is what decides whether a step
    counts as movement. A design coining its own name for a key gets `action`,
    which says nothing rather than something wrong."""
    project = blank_project("Classified", TargetPlatform.SPECTRUM)

    holds = {step["id"]: step["hold"] for step in observation_script(project)}

    assert holds["hold_left_a"] == "left"
    assert holds["hold_action_a"] == "action"
    assert holds["idle"] == "none"


def test_keys_are_named_the_way_the_emulator_knows_them():
    """`_run_zesarux` looks each step's key up in `_SPECTRUM_ROWS`, whose names
    are lowercase, and the 48K reaches its four directions through 5678."""
    from llmz80.quality.emulator_smoke import _SPECTRUM_ROWS

    project = blank_project("Keyed", TargetPlatform.SPECTRUM)

    for step in observation_script(project):
        if step["key"] is not None:
            assert step["key"] in _SPECTRUM_ROWS


def test_every_step_states_no_expectation():
    """Expectations belong to the phase 2 examiner. A step that predicted a
    value here would be judged by `acceptance_report` and could hand out a pass
    nobody earned."""
    project = blank_project("Silent", TargetPlatform.SPECTRUM)

    assert all(step["expect"] == {} for step in observation_script(project))
    assert all(step["frames"] == STEP_FRAMES for step in observation_script(project))


def test_a_target_the_harness_cannot_drive_gets_no_script():
    """`_run_caprice32` ignores its script entirely, so handing the CPC one
    would promise readings that never arrive."""
    project = blank_project("Silent CPC", TargetPlatform.AMSTRAD_CPC)

    assert observation_script(project) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_studio_observation.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'llmz80.studio.observation'`

- [ ] **Step 3: Write minimal implementation**

Crear `llmz80/studio/observation.py`:

```python
"""The steps the emulator drives so a program can be observed at all.

This is not the examiner and it must never become one. It states no
expectation about what the program should do: it holds each binding the design
declared, twice, then lets go, and the gates that read `step_readings` decide
what those readings mean. Keeping the two apart is what stops an
expectation-free script from being mistaken for a passed examination --
`acceptance.runtime_script` stays empty and `acceptance_report` keeps
abstaining, while `feel.animation_report` and `pacing.pacing_report` finally
get readings to judge.
"""

from __future__ import annotations

from typing import Any

from .models import GameProject, TargetPlatform

#: Design key label -> the name `emulator_smoke._SPECTRUM_ROWS` knows it by.
#: The four directions follow `codegen.KEY_CODES`: the 48K has no cursor keys,
#: and 5678 is what every game of the era used.
ZRCP_KEYS: dict[str, str] = {
    **{chr(code): chr(code).lower() for code in range(ord("A"), ord("Z") + 1)},
    **{str(digit): str(digit) for digit in range(10)},
    "SPACE": "space",
    "ENTER": "enter",
    "LEFT": "5",
    "DOWN": "6",
    "UP": "7",
    "RIGHT": "8",
}

#: Binding names that say the player is moving. A design coins its own binding
#: names (`jump`, `fire`, `pump`), so anything outside this set holds a key
#: that says nothing about movement -- which is what `feel._classify` calls
#: "action" and deliberately leaves out of its comparison.
DIRECTIONS = ("left", "right", "up", "down")

#: Frames each step holds its key. Fifty is one second at 50 Hz: long enough
#: that a program pacing itself on the frame clock has certainly moved.
STEP_FRAMES = 50


def observation_script(project: GameProject) -> list[dict[str, Any]]:
    """Hold each declared binding twice, then let go.

    Twice, because `feel.animation_report` compares consecutive readings and a
    single reading of a moving step can be compared against nothing. The
    trailing idle step is what lets it check the other half of its claim: that
    the animation frame holds still while the player does not move.

    Empty for any target the harness cannot drive. `_run_caprice32` ignores
    its `script` argument entirely, so a CPC script would promise readings
    that never arrive and make every gate look broken rather than absent.
    """
    if project.target.platform is not TargetPlatform.SPECTRUM:
        return []
    steps: list[dict[str, Any]] = []
    for name, label in project.controls.bindings.items():
        key = ZRCP_KEYS.get(label)
        if key is None:
            continue
        hold = name if name in DIRECTIONS else "action"
        for repeat in ("a", "b"):
            steps.append(
                {
                    "id": f"hold_{name}_{repeat}",
                    "hold": hold,
                    "key": key,
                    "frames": STEP_FRAMES,
                    "expect": {},
                }
            )
    if steps:
        steps.append(
            {"id": "idle", "hold": "none", "key": None, "frames": STEP_FRAMES, "expect": {}}
        )
    return steps
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_studio_observation.py -v`
Expected: PASS, 5 tests

- [ ] **Step 5: Commit**

```bash
git add llmz80/studio/observation.py tests/test_studio_observation.py
git commit -m "feat(studio): give the emulator steps to drive, and no expectations"
```

---

## Task 4: El emulador ejecuta el guion

**Files:**
- Modify: `llmz80/studio/services.py:424-468` (`runtime_test`), `llmz80/quality/emulator_smoke.py:248-254`
- Test: `tests/test_studio_services.py`, `tests/test_emulator_smoke.py`

**Añadido tras la revisión de la tarea 3.** El guion no cabe en la vida que el emulador se concede a sí mismo. `_run_zesarux` calcula su `--exit-after` así:

```python
    reads = 1 + len(steps) if steps else 2
    probe_cost = reads * len(addresses) * 0.2
    hold_cost = sum(int(step.get("frames", 50)) / 50.0 for step in steps)
    run_seconds = int(max(6, seconds) + probe_cost + hold_cost + 3)
```

Dos costes reales no están en esa cuenta. Una lectura ZRCP no cuesta 0.2 s sino ~0.32 (`_zrcp_query` duerme 0.12 fijo y luego lee hasta agotar un timeout de socket de 0.2), y cada paso manda dos `set-ui-io-ports` — pulsar y soltar — que cuestan otros ~0.64 s que nadie presupuesta, más ~3.7 s de conexión y capturas. Con los 11 pasos que produce `observation_script`:

| símbolos sondados | `--exit-after` | lo que el guion necesita | desfase |
|---|---|---|---|
| 2 (sólo los requeridos) | 24 s | ~29 s | +5 s |
| 5 | 32 s | ~40 s | +8 s |
| 8 (contrato completo) | 39 s | ~52 s | +13 s |

El emulador se cierra a mitad del guion, la siguiente orden ZRCP revienta con `BrokenPipeError` y la cola de `steps` no se llega a añadir — incluida la última, `idle`, que es justo la que `animation_report` necesita para la mitad de su afirmación. El síntoma que se ve es `scripted_input_sent: False` y un fallo de animación que no es del programa.

Bajar `STEP_FRAMES` no arregla nada: `hold_cost` sí está bien contado, así que recortarlo baja el presupuesto y el coste a la vez. Lo que falta es el coste por orden, que se multiplica por el número de pasos.

- [ ] **Step 0: Ensanchar el presupuesto antes de darle pasos que no caben**

En `llmz80/quality/emulator_smoke.py`, sustituir el bloque del cálculo:

```python
    steps = list(script or [])
    reads = 1 + len(steps) if steps else 2
    # A ZRCP read is not free and not 0.2s: `_zrcp_query` sleeps 0.12 outright
    # and then drains the socket until a 0.2 timeout expires. Budgeting the
    # optimistic figure is how a scripted run used to be cut off mid-script,
    # losing the tail of `steps` -- the idle step among them -- and surfacing
    # as a broken pipe rather than as the missing budget it was.
    probe_cost = reads * len(((probes or {}).get("addresses") or {})) * 0.35
    hold_cost = sum(int(step.get("frames", 50)) / 50.0 for step in steps)
    # Each step presses its key and lets it go, and both are ZRCP commands.
    command_cost = len(steps) * 0.7
    run_seconds = int(max(6, seconds) + probe_cost + hold_cost + command_cost + 5)
```

Test en `tests/test_emulator_smoke.py`, que fija la aritmética sin arrancar nada:

```python
def test_the_emulator_lifetime_covers_a_scripted_run():
    """A script whose steps outlive `--exit-after` loses its tail, and the tail
    is where the idle step -- half of what the animation gate claims -- lives."""
    from llmz80.quality.emulator_smoke import scripted_run_seconds

    script = [{"id": f"s{index}", "frames": 50} for index in range(11)]
    probes = {"addresses": {f"g_{index}": index for index in range(8)}}

    budget = scripted_run_seconds(seconds=3, steps=script, probes=probes)

    # 11 holds of one second, 12 reads of 8 symbols, 22 key commands.
    assert budget >= 11 + 12 * 8 * 0.35 + 11 * 0.7
```

Extraer el cálculo a `scripted_run_seconds(*, seconds, steps, probes)` en `emulator_smoke.py` y llamarla desde `_run_zesarux`: la aritmética es lo único comprobable sin un emulador, y hoy está enterrada en una función que arranca uno.

- [ ] **Step 1: Write the failing test**

Añadir a `tests/test_studio_services.py`:

```python
def test_the_runtime_test_drives_the_observation_script(tmp_path, monkeypatch):
    """`runtime_test` passed `script=[]`, so `step_readings` came back empty and
    every gate that reads it abstained. The pipeline was built and disconnected
    by a literal."""
    from llmz80.studio.compiler import BuildResult
    from llmz80.studio.models import TargetPlatform
    from llmz80.studio.observation import observation_script
    from llmz80.studio.samples import blank_project
    from llmz80.studio.services import StudioService

    project = blank_project("Driven", TargetPlatform.SPECTRUM)
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    monkeypatch.setattr(
        StudioService,
        "build",
        lambda self, p, d: BuildResult(
            output_dir=build_dir, success=True, artifact=None, report={"quality_pass": True}
        ),
    )
    captured: dict = {}

    def fake_smoke(output_dir, platform, full=False, seconds=3, probes=None, script=None):
        captured["script"] = script
        return {"quality_pass": True, "step_readings": []}

    monkeypatch.setattr("llmz80.studio.services.smoke_test", fake_smoke)

    StudioService.at(tmp_path).runtime_test(project, tmp_path)

    assert [step["id"] for step in captured["script"]] == [
        step["id"] for step in observation_script(project)
    ]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_studio_services.py -v -k observation_script`
Expected: FAIL — `captured["script"]` es `[]` y la lista esperada tiene 11 entradas

- [ ] **Step 3: Write minimal implementation**

En `llmz80/studio/services.py`, importar arriba:

```python
from .observation import observation_script
```

Y en `runtime_test` sustituir `script=[]`:

```python
        report = smoke_test(
            build.output_dir,
            project.target.platform.value,
            full=True,
            seconds=seconds,
            script=observation_script(project),
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_studio_services.py tests/test_studio_feel.py -v`
Expected: PASS

- [ ] **Step 5: Verificación real contra el emulador**

Run: `.venv/bin/python -m llmz80.cli project test studio-projects/my-retro-game`
Expected: `studio-projects/my-retro-game/build/emulator_report.json` contiene `step_readings` con 11 entradas, cada una con `hold` y `read`. Y `animation.quality_pass` deja de ser `null`.

Si `read` sale vacío en todas: las sondas no encontraron los símbolos; comprobar `build/probes.json`.

- [ ] **Step 6: Commit**

```bash
git add llmz80/studio/services.py tests/test_studio_services.py
git commit -m "feat(studio): connect the script the emulator harness was built for"
```

---

## Task 5: Un símbolo requerido ausente rechaza el build

Hoy `write_probe_report` calcula `missing_required` y nadie lo usa como puerta: `attempt.build_passed` sólo mira `build.quality_pass`. Un programa que declara `g_score` como `static` compila, es irreadable, y se acepta.

**Files:**
- Modify: `llmz80/core/state_contract.py:69-76`, `llmz80/studio/probes.py`, `llmz80/studio/compiler.py:485-487`
- Test: `tests/test_studio_probes.py`

- [ ] **Step 1: Write the failing test**

Añadir a `tests/test_studio_probes.py`:

```python
from llmz80.studio.probes import contract_failures


def test_a_missing_required_symbol_is_a_diagnostic_the_writer_can_act_on():
    failures = contract_failures({"missing_required": ["g_score", "g_state"]})

    assert len(failures) == 1
    assert "g_score" in failures[0]
    assert "g_state" in failures[0]
    assert "static" in failures[0]


def test_nothing_missing_is_no_diagnostic():
    assert contract_failures({"missing_required": []}) == []
    assert contract_failures({}) == []


def test_the_frame_cost_is_part_of_the_contract_every_program_must_honour():
    """A game that cannot report how badly it missed its frame cannot be judged
    on pacing, and pacing is the one performance claim the machine can make for
    any design whatsoever."""
    from llmz80.core.state_contract import REQUIRED_SYMBOLS

    assert "g_worst_frame_cost" in REQUIRED_SYMBOLS
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_studio_probes.py -v -k "contract_failures or frame_cost"`
Expected: FAIL con `ImportError: cannot import name 'contract_failures'`

- [ ] **Step 3: Write minimal implementation**

En `llmz80/core/state_contract.py`, cambiar el símbolo `g_worst_frame_cost` de opcional a requerido:

```python
    StateSymbol(
        "g_worst_frame_cost",
        1,
        True,
        "worst number of display frames a single game iteration missed since the "
        "game began; zero is ideal, and plat_wait_frame returns the count for you",
    ),
```

En `llmz80/studio/probes.py`, al final:

```python
def contract_failures(report: dict) -> list[str]:
    """Diagnostics for required symbols the linker map does not carry.

    Separated from `write_probe_report` so the build can refuse on them
    without the compiler having to be running to test the refusal. What used
    to happen instead: the report recorded the absence, `repair_prompt` told
    the writer about it, and the loop accepted the attempt anyway, because
    `attempt.build_passed` only ever read `build.quality_pass`.
    """
    missing = report.get("missing_required") or []
    if not missing:
        return []
    return [
        "these required contract symbols are absent from the linker map, which "
        "means they were declared static, declared inside a function, or "
        "optimised away because nothing reads them: " + ", ".join(missing)
    ]
```

En `llmz80/studio/compiler.py`, sustituir el bloque final que escribe las sondas:

```python
    if report["quality_pass"]:
        probes = write_probe_report(output_dir, platform)
        report["probes"] = probes
        failures = contract_failures(probes)
        if failures:
            report["quality_pass"] = False
            report["contract_errors"] = failures
            report["stderr"] = (report.get("stderr") or "") + "\n" + "\n".join(failures)
```

Y el import de `contract_failures` junto al de `write_probe_report`.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_studio_probes.py tests/test_studio_codegen.py -v`
Expected: PASS. `test_studio_codegen.py` cubre `render_state_header`, que ahora declara `g_worst_frame_cost` como `extern` en lugar de mencionarlo en el comentario de opcionales; si algún test afirma lo contrario, actualizarlo — el cambio es intencionado.

- [ ] **Step 5: Verificación real en ambas toolchains**

Run: `make audit-examples`
Expected: sin regresiones.

Run: `.venv/bin/python -m llmz80.cli project test studio-projects/my-retro-game`
Expected: build sigue pasando. `my-retro-game/program/main.c` ya declara `g_worst_frame_cost` (línea 10), así que este proyecto es la prueba de que la puerta no rechaza un programa correcto.

**Riesgo a comprobar aquí, no después:** en CPC las sondas se leen de `obj/*.noi`. Si un build CPC limpio devuelve `missing_required` con todos los símbolos, la puerta rompería toda la plataforma. Construir un proyecto CPC antes de dar la tarea por buena; si falla, la causa es que el `.noi` no se genera y hay que arreglar eso, no relajar la puerta.

- [ ] **Step 6: Commit**

```bash
git add llmz80/core/state_contract.py llmz80/studio/probes.py llmz80/studio/compiler.py tests/test_studio_probes.py
git commit -m "feat(studio): refuse a build whose state cannot be read"
```

---

## Task 6: La puerta de ritmo

`plat_wait_frame` ya devuelve cuántos frames se perdió el bucle (`resources/studio_lib/spectrum/platform.c:47-58`). El contrato ya nombra el símbolo donde vive el peor caso. Nadie lo lee. Esta tarea convierte una medición que ya existe en una puerta.

**Files:**
- Create: `llmz80/studio/pacing.py`
- Modify: `llmz80/studio/services.py` (`runtime_test`, `verify_program`), `llmz80/studio/generator.py` (`Attempt`, `repair_prompt`, `write_program`)
- Test: `tests/test_studio_pacing.py`

- [ ] **Step 1: Write the failing test**

Crear `tests/test_studio_pacing.py`:

```python
"""Judging frame pacing from what memory showed between steps."""

from llmz80.studio.pacing import MAX_MISSED_FRAMES, pacing_report


def _runtime(readings):
    return {"step_readings": [{"id": name, "read": read} for name, read in readings]}


def test_a_loop_that_keeps_pace_passes():
    report = pacing_report(_runtime([
        ("hold_left_a", {"g_worst_frame_cost": 0}),
        ("idle", {"g_worst_frame_cost": 0}),
    ]))

    assert report["quality_pass"] is True
    assert report["worst"] == 0


def test_one_missed_frame_is_tolerated():
    """The first drawn frame and the step where the harness writes its input
    both cost real time, and rejecting a game for them would reject every game."""
    report = pacing_report(_runtime([("hold_left_a", {"g_worst_frame_cost": MAX_MISSED_FRAMES})]))

    assert report["quality_pass"] is True


def test_a_loop_that_does_not_fit_in_its_frame_fails_and_says_where():
    report = pacing_report(_runtime([
        ("hold_left_a", {"g_worst_frame_cost": 1}),
        ("hold_right_b", {"g_worst_frame_cost": 7}),
    ]))

    assert report["quality_pass"] is False
    assert "7" in report["failures"][0]
    assert "hold_right_b" in report["failures"][0]


def test_a_run_that_never_reported_the_symbol_abstains():
    """Abstaining is not passing: a target with no probe adapter must not
    inherit a verdict it never earned."""
    report = pacing_report(_runtime([("idle", {"g_score": 10})]))

    assert report["quality_pass"] is None
    assert report["observed"] is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_studio_pacing.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'llmz80.studio.pacing'`

- [ ] **Step 3: Write minimal implementation**

Crear `llmz80/studio/pacing.py`:

```python
"""Judging frame pacing from what memory showed between steps.

This is the one performance claim that can be made about any design at all,
which is why it survives where the v3 gates did not: solvability and
difficulty assumed a kind of game, and "the loop fitted inside its frame"
assumes only that there is a loop and a frame.

Nothing here counts a T-state. `plat_wait_frame` already measures the cost in
the currency that matters -- whole display frames the previous iteration
overran by -- and the program keeps the worst it ever saw in
`g_worst_frame_cost`, which the linker map locates and ZRCP reads. Perfiling
T-states would need an instrumented emulator and would answer a question
nobody asked.
"""

from __future__ import annotations

from typing import Any

#: The one state-contract symbol this gate is about.
_SYMBOL = "g_worst_frame_cost"

#: Missed frames tolerated. One absorbs the cost of the first fully drawn
#: frame and of the step where the harness writes its input; two or more is a
#: game loop that does not fit inside its frame and will read as juddering.
MAX_MISSED_FRAMES = 1


def pacing_report(runtime: dict[str, Any]) -> dict[str, Any]:
    """Judge the worst frame overrun the program admitted to.

    Abstaining is not passing, exactly as in `feel.animation_report`: a run
    where no step ever reported the symbol returns `quality_pass: None`.
    """
    readings = [
        (reading.get("id"), (reading.get("read") or {})[_SYMBOL])
        for reading in runtime.get("step_readings") or []
        if _SYMBOL in (reading.get("read") or {})
    ]
    if not readings:
        return {
            "schema_version": 1,
            "observed": False,
            "reason": f"no step reported {_SYMBOL}; this target has no memory probe "
            "adapter, or the program never declared the symbol",
            "worst": None,
            "failures": [],
            "quality_pass": None,
        }
    worst_id, worst = max(readings, key=lambda item: item[1])
    failures: list[str] = []
    if worst > MAX_MISSED_FRAMES:
        failures.append(
            f"{_SYMBOL} reached {worst} at step {worst_id}: one iteration of the "
            f"game loop overran its display frame by {worst} frames, and at most "
            f"{MAX_MISSED_FRAMES} is accepted. Redraw only what changed, and move "
            "work that does not need to happen every frame out of the loop."
        )
    return {
        "schema_version": 1,
        "observed": True,
        "readings": [{"id": step_id, "read": value} for step_id, value in readings],
        "worst": worst,
        "failures": failures,
        "quality_pass": not failures,
    }
```

En `llmz80/studio/services.py`: importar `from .pacing import pacing_report`, y en `runtime_test`, tras la línea de `animation`:

```python
        pacing = pacing_report(report)
        report["pacing"] = pacing
        if (
            probes["quality_pass"] is False
            or acceptance["quality_pass"] is False
            or animation["quality_pass"] is False
            or pacing["quality_pass"] is False
        ):
            report["quality_pass"] = False
```

En `verify_program`, añadir `"pacing": None` al dict `evidence` inicial y, tras `evidence["animation"] = runtime.get("animation")`:

```python
        evidence["pacing"] = runtime.get("pacing")
```

En `llmz80/studio/generator.py`, añadir a `Attempt`:

```python
    #: `None` means the pacing gate abstained, exactly as `animation` does.
    pacing_passed: bool | None = None
```

En `repair_prompt`, ampliar la firma y añadir la sección:

```python
def repair_prompt(
    build: dict[str, Any] | None,
    acceptance: dict[str, Any] | None,
    probes: dict[str, Any] | None,
    animation: dict[str, Any] | None = None,
    pacing: dict[str, Any] | None = None,
) -> str:
```

y antes del `return`:

```python
    if pacing and pacing.get("quality_pass") is False:
        lines = ["THE GAME LOOP DID NOT FIT INSIDE ITS DISPLAY FRAME", ""]
        for reason in pacing.get("failures") or []:
            lines.append(f"  {reason}")
        lines.append("")
        lines.append(
            "plat_wait_frame returns how many whole frames the previous iteration "
            "overran by; keep the worst you ever see in g_worst_frame_cost. Memory "
            "was read directly, so these are facts about your program."
        )
        sections.append("\n".join(lines))
```

En `write_program`, dentro del bucle:

```python
        attempt.pacing_passed = (evidence.get("pacing") or {}).get("quality_pass")
```

y en la condición de aceptación y la llamada a `repair_prompt`:

```python
        if (
            attempt.build_passed
            and attempt.acceptance_passed is not False
            and attempt.animation_passed is not False
            and attempt.pacing_passed is not False
        ):
            result.accepted = True
            return result
        feedback = repair_prompt(build, acceptance, probes, animation, evidence.get("pacing"))
```

En `_attempt_line`, añadir el verdicto para que la línea de progreso no mienta:

```python
    pacing = _gate_verdict(attempt.pacing_passed)
    return (
        f"intento {attempt.number}: build {build}, "
        f"aceptación {acceptance}, animación {animation}, ritmo {pacing}"
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_studio_pacing.py tests/test_studio_generator.py tests/test_studio_services.py -v`
Expected: PASS

- [ ] **Step 5: Verificación real**

Run: `.venv/bin/python -m llmz80.cli project test studio-projects/my-retro-game`
Expected: `emulator_report.json` contiene `pacing` con `observed: true` y un `worst` numérico. Anotar el valor: es la primera medida de rendimiento que el sistema ha producido nunca.

- [ ] **Step 6: Commit**

```bash
git add llmz80/studio/pacing.py llmz80/studio/services.py llmz80/studio/generator.py tests/test_studio_pacing.py
git commit -m "feat(studio): judge the frame cost the platform library already measured"
```

---

## Task 7: Un diseño sin mecánicas y con brief no se escribe

`zampabolas` tiene un brief («Un juego como el zampabolas»), una ficha investigada con cinco mecánicas y tres fuentes, y `mechanics: []` en su `game.yml`. El programa que salió inventó su propia regla de derrota. Hoy eso es un aviso (`quality.py:design_notices`). Pasa a ser un fallo.

**Files:**
- Modify: `llmz80/studio/quality.py`, `llmz80/studio/pipeline.py` (`write`)
- Test: `tests/test_studio_quality.py`, `tests/test_studio_pipeline.py`

- [ ] **Step 1: Write the failing test**

Añadir a `tests/test_studio_quality.py`:

```python
def test_a_brief_with_no_mechanics_is_refused_not_merely_noticed():
    """The zampabolas case: a brief naming a real game, a dossier with five
    mechanics researched, and a design that states none of them. The program
    that came out invented its own losing condition."""
    from llmz80.studio.editing import rename_project
    from llmz80.studio.models import TargetPlatform
    from llmz80.studio.quality import design_quality_report
    from llmz80.studio.samples import blank_project

    project = rename_project(
        blank_project("Zampabolas", TargetPlatform.SPECTRUM),
        "Zampabolas",
        brief="Un juego como el zampabolas",
    )

    report = design_quality_report(project)

    assert report["quality_pass"] is False
    assert "design_states_the_mechanics_its_brief_asks_for" in report["failures"]


def test_a_design_with_no_brief_at_all_still_passes():
    """A fresh project has neither, and must stay buildable while its designer
    decides what it is."""
    from llmz80.studio.models import TargetPlatform
    from llmz80.studio.quality import design_quality_report
    from llmz80.studio.samples import blank_project

    assert design_quality_report(blank_project("Blank", TargetPlatform.SPECTRUM))["quality_pass"]
```

Añadir a `tests/test_studio_pipeline.py`:

```python
def test_writing_refuses_a_design_that_does_not_pass_its_own_gate(tmp_path):
    """The writer is not asked for a program the design gate already refused:
    an API call costs money and ninety seconds, and the answer is known."""
    import pytest

    from llmz80.studio.editing import rename_project
    from llmz80.studio.models import TargetPlatform
    from llmz80.studio.pipeline import write
    from llmz80.studio.services import StudioService

    service = StudioService.at(tmp_path)
    project, directory = service.create_project("Refused", TargetPlatform.SPECTRUM)
    project = rename_project(project, "Refused", brief="un juego como la abadía del crimen")
    service.save_project(project, directory)

    class NeverCalled:
        def write(self, project, feedback=None):
            raise AssertionError("the writer must not be asked")

    with pytest.raises(ValueError, match="not ready to be written"):
        write(service, project, directory, NeverCalled())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_studio_quality.py tests/test_studio_pipeline.py -v -k "brief or refuses"`
Expected: FAIL — el informe de diseño pasa, y `write` llama al escritor

- [ ] **Step 3: Write minimal implementation**

En `llmz80/studio/quality.py`, en `design_quality_report`, añadir al dict `checks`:

```python
        "design_states_the_mechanics_its_brief_asks_for": bool(project.mechanics)
        or not project.metadata.brief.strip(),
```

Y ajustar `design_notices` para que no repita como aviso lo que ahora es un fallo:

```python
def design_notices(project: GameProject) -> list[str]:
    """Advice for the designer. Never a refusal.

    A design with a brief and no mechanics is refused outright by
    `design_quality_report`, not noticed here: the brief is a statement that
    this game is meant to be something in particular, and writing it with
    nothing to implement produced `studio-projects/zampabolas`. A design with
    neither is a different case -- nobody has said what it should be yet --
    and that is what this notice is for.
    """
    notices = []
    if not project.mechanics and not project.metadata.brief.strip():
        notices.append(
            "this design states no mechanics and carries no brief, so nothing "
            "tells the writer how the game is won, lost or played; the program "
            "will be whatever the model infers from the screens alone"
        )
    return notices
```

En `llmz80/studio/pipeline.py`, al principio de `write`, antes de construir el escritor:

```python
    from .quality import design_quality_report

    report = design_quality_report(project)
    if not report["quality_pass"]:
        raise ValueError(
            "this design is not ready to be written:\n  " + "\n  ".join(report["failures"])
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_studio_quality.py tests/test_studio_pipeline.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add llmz80/studio/quality.py llmz80/studio/pipeline.py tests/test_studio_quality.py tests/test_studio_pipeline.py
git commit -m "feat(studio): refuse to write a game whose design says nothing"
```

---

## Task 8: El examinador de diseño

La tarea 7 detecta el caso extremo (cero mecánicas). Este examinador detecta el caso real: `my-retro-game`, cuyo brief pide *«va volando hacia la derecha, hay scroll»* y cuyo diseño es una pantalla fija de 20×14. Nada lo notó.

**Files:**
- Create: `llmz80/studio/design_exam.py`
- Modify: `llmz80/studio/pipeline.py` (`adapt`)
- Test: `tests/test_studio_design_exam.py`

- [ ] **Step 1: Write the failing test**

Crear `tests/test_studio_design_exam.py`:

```python
"""Does the design state what its own brief asked for."""

import pytest

from llmz80.studio.design_exam import (
    BriefCoverage,
    coverage_errors,
    examination_prompt,
)
from llmz80.studio.editing import rename_project
from llmz80.studio.models import TargetPlatform
from llmz80.studio.samples import blank_project


@pytest.fixture
def flying_project():
    return rename_project(
        blank_project("My Retro Game", TargetPlatform.SPECTRUM),
        "My Retro Game",
        brief="un avión de combate que vuela hacia la derecha. hay scroll y van "
        "apareciendo otros cazas, y se disparan entre ambos.",
    )


def test_the_prompt_carries_the_brief_and_what_the_design_actually_states(flying_project):
    prompt = examination_prompt(flying_project)

    assert "avión de combate" in prompt
    assert "20x14" in prompt


def test_an_uncovered_brief_becomes_an_error_naming_what_is_missing():
    coverage = BriefCoverage(
        covered=False,
        missing=["el brief pide scroll y el diseño declara una sola pantalla fija"],
        quoted="hay scroll",
    )

    errors = coverage_errors(coverage)

    assert len(errors) == 1
    assert "scroll" in errors[0]
    assert "hay scroll" in errors[0]


def test_a_covered_brief_is_no_error():
    assert coverage_errors(BriefCoverage(covered=True, missing=[], quoted="")) == []


def test_a_covered_verdict_that_still_lists_gaps_is_read_as_uncovered():
    """A model that says yes and then lists what is missing has contradicted
    itself, and the safe reading of a contradiction is the one that does not
    let a design through."""
    coverage = BriefCoverage(covered=True, missing=["no hay enemigos"], quoted="otros cazas")

    assert coverage_errors(coverage) != []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_studio_design_exam.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'llmz80.studio.design_exam'`

- [ ] **Step 3: Write minimal implementation**

Crear `llmz80/studio/design_exam.py`:

```python
"""Does the design state what its own brief asked for.

`quality.design_quality_report` catches the design that states nothing at all.
This catches the one that states something else: `studio-projects/my-retro-game`
carries a brief asking for a plane flying right with scroll and enemies, and a
design of one fixed 20x14 screen. The program implemented the design faithfully
and the brief was never mentioned again.

The verdict is a model's, so it is shaped to be checkable: a refusal must quote
the sentence of the brief it is about and name what the design fails to state.
A refusal that cannot do both is worthless to whoever has to fix the design.
"""

from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict

from .models import GameProject


class BriefCoverage(BaseModel):
    """One verdict on whether a design covers its brief."""

    model_config = ConfigDict(extra="forbid")

    covered: bool
    #: What the brief asks for and the design does not state, one sentence each.
    missing: list[str]
    #: The sentence of the brief this verdict is about, quoted verbatim, so a
    #: refusal can be checked against the brief rather than taken on faith.
    quoted: str


class DesignExaminer(Protocol):
    def examine(self, project: GameProject) -> BriefCoverage: ...


def _design_summary(project: GameProject) -> str:
    """What the design actually states, in the form the examiner must judge."""
    lines = [
        f"Screens: {len(project.screens)} "
        + ", ".join(f"{s.id} {s.width}x{s.height}" for s in project.screens),
        "Exits: "
        + (
            ", ".join(
                f"{screen.id} -{direction}-> {destination}"
                for screen in project.screens
                for direction, destination in screen.exits.items()
            )
            or "none"
        ),
        "Entities: " + ", ".join(f"{e.id} ({e.kind})" for e in project.entities),
        "Tiles: " + ", ".join(f"{t.id} '{t.char}'" for t in project.tiles),
        "Controls: " + ", ".join(f"{n}={k}" for n, k in project.controls.bindings.items()),
        "Mechanics:",
        *(f"  - {sentence}" for sentence in project.mechanics),
    ]
    return "\n".join(lines)


def examination_prompt(project: GameProject) -> str:
    """Everything the examiner is owed before it judges."""
    return f"""EXAMINE WHETHER THIS DESIGN STATES WHAT ITS BRIEF ASKED FOR

You are not judging whether the game is good, whether the brief is a good
idea, or whether the design would be fun. One question only: does the design
below state the things the brief asks for?

A brief sets mood as well as rules. Atmosphere ("a dark castle") is not
something a design must state. A concrete claim about how the game works --
that it scrolls, that enemies shoot back, that there are several rooms, that
the player jumps -- is.

THE BRIEF

{project.metadata.brief.strip()}

WHAT THE DESIGN STATES

{_design_summary(project)}

Answer with covered=true only if every concrete claim in the brief is stated
somewhere in the design. Otherwise list each gap in `missing` as one sentence
naming what the brief asks for and what the design says instead, and quote in
`quoted` the words of the brief your verdict is about, verbatim.
"""


def coverage_errors(coverage: BriefCoverage) -> list[str]:
    """The verdict as diagnostics, or nothing when the design covers its brief.

    A `covered=True` that still lists gaps is read as uncovered. A model that
    answers yes and then contradicts itself has told us it is unsure, and the
    reading that does not let a design through is the safe one.
    """
    if coverage.covered and not coverage.missing:
        return []
    gaps = "; ".join(coverage.missing) or "the examiner refused without naming a gap"
    return [f'the brief says "{coverage.quoted}" and the design does not deliver it: {gaps}']


class ResponsesDesignExaminer:
    """Examines the design with the OpenAI Responses API."""

    def __init__(self, client: Any, model: str = "gpt-5") -> None:
        self.client = client
        self.model = model

    def examine(self, project: GameProject) -> BriefCoverage:
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You examine game designs against the brief they came from. "
                        "You answer only about what is stated, never about taste."
                    ),
                },
                {"role": "user", "content": examination_prompt(project)},
            ],
            text_format=BriefCoverage,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("the model did not return a coverage verdict")
        return parsed
```

En `llmz80/studio/pipeline.py`, al final de `adapt`, antes de `service.save_project`:

```python
    if examiner is not None and updated.metadata.brief.strip():
        from .design_exam import coverage_errors

        errors = coverage_errors(examiner.examine(updated))
        for error in errors:
            say(f"El diseño no cubre su brief: {error}")
        if errors:
            raise Declined(
                "the adapted design does not state what the brief asked for:\n  "
                + "\n  ".join(errors)
            )
```

y añadir el parámetro `examiner: Any = None` a la firma de `adapt`, documentado: *un llamador sin examinador se queda como estaba; `llmz80 make` pasa uno.*

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_studio_design_exam.py tests/test_studio_pipeline.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add llmz80/studio/design_exam.py llmz80/studio/pipeline.py tests/test_studio_design_exam.py
git commit -m "feat(studio): notice when a design answers a different brief"
```

---

## Task 9: Volcar la pantalla del emulador

**Files:**
- Modify: `llmz80/quality/emulator_smoke.py` (`_run_zesarux`)
- Test: `tests/test_emulator_smoke.py`

- [ ] **Step 1: Write the failing test**

Añadir a `tests/test_emulator_smoke.py`:

```python
def test_a_screen_answer_becomes_the_bytes_the_machine_had():
    """ZRCP answers `read-memory` in hex pairs and then its own prompt; the
    prompt must not become pixels."""
    from llmz80.quality.emulator_smoke import _screen_from_answer

    answer = " ".join(f"{value % 256:02X}" for value in range(6912)) + "\ncommand@ deadbeef"

    screen = _screen_from_answer(answer)

    assert len(screen) == 6912
    assert screen[0] == 0
    assert screen[257] == 1


def test_a_truncated_screen_answer_is_no_screen_at_all():
    from llmz80.quality.emulator_smoke import _screen_from_answer

    assert _screen_from_answer("00 01 02") == b""
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_emulator_smoke.py -v -k screen`
Expected: FAIL con `ImportError: cannot import name '_screen_from_answer'`

- [ ] **Step 3: Write minimal implementation**

En `llmz80/quality/emulator_smoke.py`, junto a `_read_probes`:

```python
#: Bitmap plus attributes: 6144 + 768, the whole Spectrum display file.
SCREEN_BYTES = 6912

#: Where the display file starts on a 48K.
SCREEN_ORIGIN = 16384


def _screen_from_answer(answer: str) -> bytes:
    """The display file out of one ZRCP `read-memory` answer.

    Split on the prompt exactly as `_read_probes` does: ZRCP writes
    "command@ ..." after its payload, and its hex digits would otherwise be
    read as the last bytes of the screen.
    """
    digits = "".join(re.findall(r"[0-9A-Fa-f]{2}", answer.split("command@")[0]))[: SCREEN_BYTES * 2]
    if len(digits) < SCREEN_BYTES * 2:
        return b""
    return bytes(int(digits[index : index + 2], 16) for index in range(0, SCREEN_BYTES * 2, 2))


def _read_screen(connection: socket.socket) -> bytes:
    """Ask for the whole display file. Empty when the answer arrived short."""
    try:
        answer = _zrcp_query(connection, f"read-memory {SCREEN_ORIGIN} {SCREEN_BYTES}")
    except OSError:
        return b""
    return _screen_from_answer(answer)
```

En `_run_zesarux`, dentro del `if steps:` que captura `played.bmp`, tras `_wait_for_file(played)`:

```python
                screen = _read_screen(connection)
                if screen:
                    (capture_dir / "screen.bin").write_bytes(screen)
```

Y en el dict `result`, añadir:

```python
        "screen_dump": str(capture_dir / "screen.bin") if (capture_dir / "screen.bin").is_file() else None,
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_emulator_smoke.py -v`
Expected: PASS

- [ ] **Step 5: Verificación real**

Run: `.venv/bin/python -m llmz80.cli project test studio-projects/my-retro-game`
Expected: existe un `screen.bin` de exactamente 6912 bytes bajo `build/smoke_frames/spectrum_*/`.

Si sale vacío: la respuesta ZRCP llegó truncada. `_zrcp_query` espera 0.12 s y luego lee hasta timeout; para 13 KB de texto puede hacer falta subir ese `time.sleep` **sólo para esta consulta**. No subirlo globalmente: cada consulta de sonda paga ese tiempo y hay una por símbolo y paso.

- [ ] **Step 6: Commit**

```bash
git add llmz80/quality/emulator_smoke.py tests/test_emulator_smoke.py
git commit -m "feat(quality): keep the screen the machine actually had"
```

---

## Task 10: Contenido invisible

**Nota sobre el alcance, que importa:** esto **no** es un detector de colour clash. El clash real (dos colores necesarios en una celda) no es visible en el fichero de atributos: haría falta seguir qué sprite se solapa con qué fondo. Lo que sí es visible, barato y es un defecto siempre, es una celda con píxeles dibujados cuyo INK es igual a su PAPER: contenido que ningún jugador puede ver. Se llama por su nombre.

**Files:**
- Create: `llmz80/studio/attributes.py`
- Modify: `llmz80/studio/services.py` (`runtime_test`, `verify_program`)
- Test: `tests/test_studio_attributes.py`

- [ ] **Step 1: Write the failing test**

Crear `tests/test_studio_attributes.py`:

```python
"""Finding drawn pixels no player can see."""

from llmz80.studio.attributes import ATTRIBUTE_ORIGIN, cell_offset, invisible_cells


def _blank_screen() -> bytearray:
    """A screen with nothing drawn and white ink on black paper everywhere."""
    screen = bytearray(6912)
    for index in range(768):
        screen[ATTRIBUTE_ORIGIN + index] = 0x07
    return screen


def test_the_cell_offset_follows_the_thirds_the_hardware_has():
    """Row 8 starts the second third, which is 2048 bytes in, not 8 rows of 32."""
    assert cell_offset(0, 0) == 0
    assert cell_offset(1, 0) == 1
    assert cell_offset(0, 1) == 32
    assert cell_offset(0, 8) == 2048
    assert cell_offset(31, 23) == 2048 * 2 + 7 * 32 + 31


def test_pixels_drawn_in_a_cell_whose_ink_matches_its_paper_are_invisible():
    screen = _blank_screen()
    screen[cell_offset(4, 9)] = 0xFF
    screen[ATTRIBUTE_ORIGIN + 9 * 32 + 4] = 0x00  # INK_BLACK on PAPER_BLACK

    assert invisible_cells(bytes(screen)) == [(4, 9)]


def test_the_same_pixels_in_a_readable_cell_are_fine():
    screen = _blank_screen()
    screen[cell_offset(4, 9)] = 0xFF

    assert invisible_cells(bytes(screen)) == []


def test_an_empty_cell_is_not_invisible_content():
    """A black-on-black cell with nothing in it is just background."""
    screen = _blank_screen()
    screen[ATTRIBUTE_ORIGIN + 0] = 0x00

    assert invisible_cells(bytes(screen)) == []


def test_bright_does_not_separate_an_ink_from_its_own_paper():
    """BRIGHT applies to both halves of the attribute, so it cannot make an ink
    visible against a paper of the same colour."""
    screen = _blank_screen()
    screen[cell_offset(0, 0)] = 0xFF
    screen[ATTRIBUTE_ORIGIN + 0] = 0x40 | 0x02 | (0x02 << 3)  # bright red on red

    assert invisible_cells(bytes(screen)) == [(0, 0)]


def test_a_screen_of_the_wrong_size_is_no_screen():
    assert invisible_cells(b"") == []
    assert invisible_cells(bytes(100)) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_studio_attributes.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'llmz80.studio.attributes'`

- [ ] **Step 3: Write minimal implementation**

Crear `llmz80/studio/attributes.py`:

```python
"""Finding drawn pixels no player can see.

This is not a colour clash detector and must not be described as one. Clash --
two colours wanted in one 8x8 cell -- is not visible in the display file at
all: it needs to know which sprite overlapped which background, which is a
claim about the program, not about its output. What *is* visible in the
display file, costs one memory read, and is a defect in every design without
exception, is a cell carrying drawn pixels whose ink is the same colour as its
paper. The player sees nothing there.

It is the failure `sprite_artist.py` already fought once from the other side:
`spriting._FALLBACK_INK` exists because a correctly shaped sprite packed with
INK_BLACK on PAPER_BLACK draws a silhouette nobody can see. That was caught by
reading a fixture. This catches it on the real machine.
"""

from __future__ import annotations

from typing import Any

#: Bitmap first, then one attribute per character cell.
BITMAP_BYTES = 6144
ATTRIBUTE_ORIGIN = BITMAP_BYTES
SCREEN_BYTES = 6912

COLUMNS = 32
ROWS = 24


def cell_offset(col: int, row: int) -> int:
    """Byte offset of a cell's first pixel line inside the display file.

    The Spectrum's screen is three thirds of eight character rows, and within a
    third the eight pixel lines of a row are 256 bytes apart -- which is why
    `platform.c` writes `address[line << 8]` rather than adding a stride. The
    address bits are: third at 11, character row within the third at 5, column
    at 0, and the pixel line at 8.
    """
    third, row_in_third = divmod(row, 8)
    return (third << 11) | (row_in_third << 5) | col


def invisible_cells(screen: bytes) -> list[tuple[int, int]]:
    """Cells carrying drawn pixels whose ink cannot be told from their paper.

    BRIGHT is ignored on purpose: it applies to ink and paper together, so it
    can never separate a colour from itself. FLASH is ignored for the same
    reason -- it swaps the two, and swapping a colour with itself changes
    nothing.
    """
    if len(screen) != SCREEN_BYTES:
        return []
    found: list[tuple[int, int]] = []
    for row in range(ROWS):
        for col in range(COLUMNS):
            attribute = screen[ATTRIBUTE_ORIGIN + row * COLUMNS + col]
            if (attribute & 0x07) != ((attribute >> 3) & 0x07):
                continue
            base = cell_offset(col, row)
            if any(screen[base + (line << 8)] for line in range(8)):
                found.append((col, row))
    return found


def attribute_report(runtime: dict[str, Any]) -> dict[str, Any]:
    """Judge the screen the emulator kept, if it kept one.

    Abstains rather than passes when there is no dump, exactly as every other
    gate here does: a CPC run has no dump and must not inherit a verdict.
    """
    path = runtime.get("screen_dump")
    if not path:
        return {
            "schema_version": 1,
            "observed": False,
            "reason": "no screen dump was taken; this target has no ZRCP adapter",
            "invisible_cells": [],
            "failures": [],
            "quality_pass": None,
        }
    from pathlib import Path

    try:
        screen = Path(path).read_bytes()
    except OSError as exc:
        return {
            "schema_version": 1,
            "observed": False,
            "reason": f"the screen dump could not be read: {exc}",
            "invisible_cells": [],
            "failures": [],
            "quality_pass": None,
        }
    cells = invisible_cells(screen)
    failures = []
    if cells:
        shown = ", ".join(f"({col},{row})" for col, row in cells[:12])
        more = f" and {len(cells) - 12} more" if len(cells) > 12 else ""
        failures.append(
            f"{len(cells)} character cells carry drawn pixels whose ink is the same "
            f"colour as their paper, so nothing there can be seen: {shown}{more}. "
            "Set an attribute that contrasts with the paper wherever you draw."
        )
    return {
        "schema_version": 1,
        "observed": True,
        "invisible_cells": [list(cell) for cell in cells],
        "failures": failures,
        "quality_pass": not failures,
    }
```

En `llmz80/studio/services.py`, importar `from .attributes import attribute_report` y en `runtime_test`, junto a las demás puertas:

```python
        attributes = attribute_report(report)
        report["attributes"] = attributes
```

añadiendo `or attributes["quality_pass"] is False` a la condición que baja `report["quality_pass"]`.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_studio_attributes.py tests/test_studio_services.py -v`
Expected: PASS

- [ ] **Step 5: Calibrar contra los dos juegos que existen antes de fiarse de la puerta**

Run:
```bash
.venv/bin/python -m llmz80.cli project test studio-projects/my-retro-game
.venv/bin/python -m llmz80.cli project test studio-projects/zampabolas
```

Leer `attributes.invisible_cells` en cada `emulator_report.json` y anotar el número aquí:

- `my-retro-game`: ____ celdas
- `zampabolas`: ____ celdas

Si alguno da un puñado de celdas y la inspección de `played.bmp` muestra que el juego se ve bien, la captura está cogiendo un instante de transición: **no relajar el umbral**, mover la lectura del volcado a después del último paso del guion. Si dan cero, la puerta está calibrada y lista.

- [ ] **Step 6: Commit**

```bash
git add llmz80/studio/attributes.py llmz80/studio/services.py tests/test_studio_attributes.py
git commit -m "feat(studio): find the pixels the machine drew where nobody can see them"
```

---

## Task 11: `EnginePack` y la puerta de licencia

**Files:**
- Create: `llmz80/studio/engines.py`
- Test: `tests/test_studio_engines.py`

- [ ] **Step 1: Write the failing test**

Crear `tests/test_studio_engines.py`:

```python
"""Third-party engines: what they must declare before they can be used."""

from pathlib import Path

import pytest

from llmz80.studio.engines import (
    ALLOWED_LICENCES,
    EngineClass,
    EnginePack,
    engine_registry,
)
from llmz80.studio.models import TargetPlatform


def _pack(**overrides) -> EnginePack:
    fields = dict(
        id="cpctelera",
        name="CPCtelera",
        platform=TargetPlatform.AMSTRAD_CPC,
        engine_class=EngineClass.LIBRARY,
        repository="https://github.com/lronaldo/cpctelera",
        commit="0" * 40,
        licence="GPL-3.0-or-later",
        vendor_dir=Path("vendor/cpctelera"),
        probe_map={"g_score": "_g_score", "g_state": "_g_state", "g_worst_frame_cost": "_g_wfc"},
        capabilities=frozenset({"masked_sprites", "hardware_scroll", "ay_music"}),
    )
    fields.update(overrides)
    return EnginePack(**fields)


def test_gpl_is_accepted_because_the_project_accepted_what_it_means():
    assert _pack().licence_errors() == []
    assert "GPL-3.0-or-later" in ALLOWED_LICENCES


def test_an_unknown_licence_is_refused_by_name():
    errors = _pack(licence="ask-the-author").licence_errors()

    assert len(errors) == 1
    assert "ask-the-author" in errors[0]


def test_an_engine_that_cannot_be_probed_is_refused():
    """Every gate this project owns reads the state contract out of memory. An
    engine that does not say where its state lives silently switches all of
    them off."""
    errors = _pack(probe_map={"g_score": "_g_score"}).probe_errors()

    assert len(errors) == 1
    assert "g_state" in errors[0]
    assert "g_worst_frame_cost" in errors[0]


def test_a_commit_that_is_not_pinned_is_refused():
    """A branch name is not a version: the engine under it changes and the
    games built against it stop being reproducible."""
    assert _pack(commit="main").pin_errors() != []
    assert _pack().pin_errors() == []


def test_the_registry_keeps_one_pack_per_id():
    registry = engine_registry(load_external=False, packs=(_pack(),))

    assert registry.get("cpctelera").name == "CPCtelera"
    with pytest.raises(KeyError, match="unknown plugin"):
        registry.get("mk1")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_studio_engines.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'llmz80.studio.engines'`

- [ ] **Step 3: Write minimal implementation**

Crear `llmz80/studio/engines.py`:

```python
"""Third-party engines and libraries a project can be built with.

Studio does not write engines and is not going to. It vendors them: a checkout
pinned to one commit under `vendor/<id>/`, with its licence recorded, and one
`EnginePack` saying what it is, what it can do, and where its state lives.

`probe_map` is the field that makes everything else survive the change. The
state contract in `llmz80.core.state_contract` can be demanded of a program
*we* had written; it cannot be demanded of somebody else's engine, which names
its score whatever it named it. So each pack declares where its own state
lives and `probes.py` reads that instead. Without it, every gate this project
owns switches off the moment a game is built with an engine, and N engines
would need N sets of gates -- which is the arithmetic that kills a
multi-engine pipeline before it starts.

`engine_class` is not decoration: a `LIBRARY` still has the program written in
C by a model, so the output space stays unrestricted and the writing prompt
must teach its API. A `DSL` engine has the model emit data only and never a
line of code. Two different pipelines, and a gate that does not know which one
it is judging will judge one of them wrongly.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from importlib.metadata import entry_points
from pathlib import Path
from typing import Iterable, Mapping

from llmz80.core.state_contract import REQUIRED_SYMBOLS

from .models import TargetPlatform
from .registry import Registry

#: The entry-point group an installed package registers an `EnginePack` under.
ENGINE_PLUGIN_GROUP = "llmz80.engine_plugins"

#: Licences a vendored engine may carry. GPL is on the list because this
#: project decided (2026-08-14) that a generated game being a derivative work
#: of a GPL engine is a consequence it accepts. An unknown or bespoke licence
#: is not on it, and not because of its terms: a pipeline that publishes what
#: it builds cannot honour terms nobody has read.
ALLOWED_LICENCES = frozenset(
    {
        "MIT",
        "BSD-2-Clause",
        "BSD-3-Clause",
        "Zlib",
        "Apache-2.0",
        "LGPL-2.1-or-later",
        "LGPL-3.0-or-later",
        "GPL-2.0-only",
        "GPL-2.0-or-later",
        "GPL-3.0-only",
        "GPL-3.0-or-later",
        "CC0-1.0",
        "Unlicense",
    }
)


class EngineClass(str, Enum):
    #: The model writes C against the engine's API. Restricts nothing about
    #: what it can write.
    LIBRARY = "library"
    #: The model emits data the engine reads. Writes no code at all.
    DSL = "dsl"


@dataclass(frozen=True)
class EnginePack:
    id: str
    name: str
    platform: TargetPlatform
    engine_class: EngineClass
    repository: str
    #: A full 40-character git commit. A branch is not a version.
    commit: str
    #: SPDX identifier, read off the engine's own licence file by whoever
    #: vendored it.
    licence: str
    vendor_dir: Path
    #: Contract symbol -> the name or address this engine keeps it under.
    probe_map: Mapping[str, str]
    capabilities: frozenset[str]

    def licence_errors(self) -> list[str]:
        if self.licence in ALLOWED_LICENCES:
            return []
        return [
            f"{self.id} declares licence {self.licence!r}, which is not one this "
            "project has accepted. Read the engine's licence file, record its SPDX "
            "identifier, and add it to ALLOWED_LICENCES only if the games this "
            "pipeline publishes can honour it"
        ]

    def probe_errors(self) -> list[str]:
        missing = sorted(set(REQUIRED_SYMBOLS) - set(self.probe_map))
        if not missing:
            return []
        return [
            f"{self.id} does not say where these required contract symbols live, "
            "so every behaviour gate would abstain on any game built with it: "
            + ", ".join(missing)
        ]

    def pin_errors(self) -> list[str]:
        if len(self.commit) == 40 and all(c in "0123456789abcdef" for c in self.commit.lower()):
            return []
        return [
            f"{self.id} is pinned to {self.commit!r}, which is not a full commit "
            "hash: a game built against a moving reference cannot be rebuilt"
        ]

    def errors(self) -> list[str]:
        return [*self.licence_errors(), *self.probe_errors(), *self.pin_errors()]


def engine_registry(
    load_external: bool = True, packs: Iterable[EnginePack] = ()
) -> Registry[EnginePack]:
    """Every engine available, built-ins first.

    There are no built-ins yet on purpose: the first pack lands with the
    CPCtelera integration, and an empty registry is the honest statement that
    no engine is usable until one has been vendored and checked.
    """
    registry: Registry[EnginePack] = Registry(packs)
    if load_external:
        for point in entry_points(group=ENGINE_PLUGIN_GROUP):
            registry.register(point.load())
    return registry
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_studio_engines.py -v`
Expected: PASS, 6 tests

- [ ] **Step 5: Commit**

```bash
git add llmz80/studio/engines.py tests/test_studio_engines.py
git commit -m "feat(studio): describe an engine we did not write and could not judge without it"
```

---

## Task 12: Vendorizar un motor

**Files:**
- Create: `scripts/vendor_engine.py`
- Modify: `.gitignore`
- Test: `tests/test_studio_engines.py`

- [ ] **Step 1: Write the failing test**

Añadir a `tests/test_studio_engines.py`:

```python
def test_the_manifest_records_what_a_rebuild_would_need(tmp_path):
    from scripts.vendor_engine import write_manifest

    path = write_manifest(
        tmp_path,
        engine_id="cpctelera",
        repository="https://github.com/lronaldo/cpctelera",
        commit="a" * 40,
        licence="GPL-3.0-or-later",
    )

    import json

    manifest = json.loads(path.read_text(encoding="utf-8"))
    assert manifest["commit"] == "a" * 40
    assert manifest["licence"] == "GPL-3.0-or-later"
    assert manifest["repository"].endswith("cpctelera")


def test_vendoring_refuses_a_licence_nobody_read(tmp_path):
    import pytest

    from scripts.vendor_engine import write_manifest

    with pytest.raises(ValueError, match="not one this project has accepted"):
        write_manifest(
            tmp_path,
            engine_id="mystery",
            repository="https://example.invalid/mystery",
            commit="b" * 40,
            licence="UNKNOWN",
        )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_studio_engines.py -v -k manifest`
Expected: FAIL con `ModuleNotFoundError: No module named 'scripts.vendor_engine'`

Si el import de `scripts` no resuelve, crear `scripts/__init__.py` vacío.

- [ ] **Step 3: Write minimal implementation**

Crear `scripts/vendor_engine.py`:

```python
#!/usr/bin/env python3
"""Vendor a third-party engine at a pinned commit.

The checkout itself is not committed -- these repositories are large and
already have a home. What *is* committed is `vendor/<id>/ENGINE.json`, which
records the repository, the commit and the licence somebody read. That is
everything a rebuild needs, and it is auditable in a way a copied tree is not.

Usage:
    python scripts/vendor_engine.py cpctelera \\
        https://github.com/lronaldo/cpctelera <40-char-commit> GPL-3.0-or-later
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from llmz80.studio.engines import ALLOWED_LICENCES

VENDOR_ROOT = Path(__file__).resolve().parents[1] / "vendor"


def write_manifest(
    directory: Path, *, engine_id: str, repository: str, commit: str, licence: str
) -> Path:
    """Record what a rebuild needs, refusing a licence nobody has read.

    The refusal happens here rather than after the clone so a licence problem
    costs a second instead of a gigabyte.
    """
    if licence not in ALLOWED_LICENCES:
        raise ValueError(
            f"licence {licence!r} is not one this project has accepted. Read the "
            "engine's own licence file and record its SPDX identifier; if it is "
            "genuinely acceptable, add it to engines.ALLOWED_LICENCES in its own "
            "commit, with the reason"
        )
    if len(commit) != 40:
        raise ValueError(f"{commit!r} is not a full commit hash")
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "ENGINE.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "id": engine_id,
                "repository": repository,
                "commit": commit,
                "licence": licence,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def vendor(engine_id: str, repository: str, commit: str, licence: str) -> Path:
    directory = VENDOR_ROOT / engine_id
    write_manifest(
        directory, engine_id=engine_id, repository=repository, commit=commit, licence=licence
    )
    checkout = directory / "src"
    if not checkout.is_dir():
        subprocess.run(["git", "init", "-q", str(checkout)], check=True)
        subprocess.run(
            ["git", "-C", str(checkout), "remote", "add", "origin", repository], check=True
        )
    subprocess.run(
        ["git", "-C", str(checkout), "fetch", "--depth", "1", "origin", commit], check=True
    )
    subprocess.run(["git", "-C", str(checkout), "checkout", "-q", "FETCH_HEAD"], check=True)
    return checkout


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(__doc__)
        raise SystemExit(2)
    print(vendor(*sys.argv[1:5]))
```

Añadir a `.gitignore`:

```
vendor/*/src/
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_studio_engines.py -v`
Expected: PASS

- [ ] **Step 5: Vendorizar CPCtelera de verdad**

```bash
git ls-remote https://github.com/lronaldo/cpctelera HEAD
.venv/bin/python scripts/vendor_engine.py cpctelera \
    https://github.com/lronaldo/cpctelera <el-commit-de-arriba> <SPDX>
```

**Antes de ejecutar el segundo comando hay que leer el fichero de licencia del repositorio y anotar aquí su identificador SPDX real.** No adivinarlo: el comando lo rechazará si no está en la lista, que es exactamente lo que debe pasar.

- Licencia leída: ____________
- Commit fijado: ____________

Expected: `vendor/cpctelera/ENGINE.json` existe y está en el índice de git; `vendor/cpctelera/src/` existe y está ignorado.

- [ ] **Step 6: Commit**

```bash
git add scripts/vendor_engine.py scripts/__init__.py .gitignore vendor/cpctelera/ENGINE.json tests/test_studio_engines.py
git commit -m "feat(studio): vendor an engine at a pinned commit with its licence read"
```

---

## Verificación del horizonte 1 completo

- [ ] Run: `make test` — toda la suite en verde
- [ ] Run: `make lint` — sin errores críticos
- [ ] Run: `.venv/bin/python -m llmz80.cli project test studio-projects/my-retro-game`

Comprobar en `build/emulator_report.json` que **ninguna** de estas claves es `null`:
`animation.quality_pass`, `pacing.quality_pass`, `attributes.quality_pass`.

Y en `build/studio_quality_report.json`, que `verification` dice `observed`.

- [ ] Volver a generar `zampabolas` de cero y comprobar que **no** sale aceptado sin observación:

```bash
.venv/bin/python -m llmz80.cli make "un juego como el zampabolas" --platform spectrum
```

Expected: o bien el diseño se rechaza por no cubrir su brief (tarea 8), o bien el programa se escribe y **es observado**. Lo que no puede volver a pasar es un `accepted: true` con las tres puertas en `null`.

---

## Horizonte 2 (1-4 meses) — roadmap, sin detalle ejecutable

El detalle se escribirá cuando E1 exista, porque E1 va a cambiar los supuestos de todo lo demás.

| # | Ítem | Cierra | Esfuerzo | Depende de | Riesgo principal |
|---|---|---|---|---|---|
| **E1** | Integración de `EnginePack` en el pipeline: `game.yml` declara motor, `render_project` y `build_project` se enrutan por él, `probes.py` lee el `probe_map` en vez de los nombres del contrato | Gap 2, 3 | 3-4 sem | Tareas 11-12 | Diseñar el contrato con un solo motor a la vista. **No cerrarlo hasta tener dentro dos motores de clases distintas** |
| **E2** | CPCtelera operativo: build real, prompt de escritura con su API, sprites y scroll por sus rutinas | Gap 2 | 2-3 sem | E1 | Bajo. Ya hay 40+ ejemplos en `examples/amstrad_cpc*` |
| **E3** | Un motor con DSL en Spectrum (MK1/La Churrera o AGD). La LLM emite datos, no código | Gap 2, **3** | 5-7 sem | E1 | El emisor de datos es trabajo nuevo y el motor impone su formato. Es donde está el premio |
| **E4** | Enrutador: del brief al motor, con capacidad de **negarse** cuando ninguno cubre el caso | Gap 9 | 2 sem | E1 | Que elija mal en silencio. El motor y el motivo se escriben en `game.yml` |
| **M1** | El examinador: derivar de `mechanics` un guion con expectativas verificables, y declarar en voz alta lo que no puede verificar | Gap 1, 6, 9 | 4-6 sem | Tarea 4 | **El más alto del plan entero.** Los dos fracasos previos están documentados: v3 predijo un juego y rechazó tres, v4 se abstuvo y aceptó basura |
| **M2** | Agente jugador: completabilidad por entrada dirigida hasta `g_state == STATE_VICTORY` | Gap 1, 6 | 3-4 sem | M1 | Coste de emulación; un intento ya cuesta 121 s |
| **M5** | Presupuesto de memoria real: secciones de datos y BSS leídas del `.map`, no el tamaño del fichero | Gap 8 | 1 sem | — | Bajo |
| **R1** | **Retirada del escritor libre de C** (`generator.py`, `resources/studio_lib/`, `platform_notes.py`, ≈900 L) una vez E2 y E3 estén verdes | — | 1 sem | E2, E3 | Perder el único camino que hoy produce juegos. Condición de disparo: dos motores generando y pasando las puertas del horizonte 1 |

## Horizonte 3 (>4 meses)

| # | Ítem | Nota |
|---|---|---|
| E5 | Motores 3 y 4 (z88dk+sp1 en ZX, CPCRSLib en CPC) | Sólo si E1 aguantó dos motores sin torcerse |
| E6 | Arkos + AY en CPC: arreglar o rodear el error interno de SDCC que excluye `examples/amstrad_cpc/medium/arkosAudio` del RAG | Cierra el gap 5 en CPC sin escribir un driver |
| L1 | Spectrum 128K: `TargetPack` nuevo, bankswitching, `--machine 128k` en el harness | Menos urgente ahora: el AY llega antes por CPC |
| L4 | Crítico visual calibrado contra corpus de época | Sigue sin datos que lo calibren. Reevaluar cuando haya 100 juegos generados |

**Enterrados por las decisiones del 2026-08-14:** motor propio para un género (lo aportan los externos), motor ASM escrito a mano (3-6 meses de experto, incompatible con el objetivo de throughput), escape hatch ASM con revisión adversarial (no hay ASM que revisar), y limitar el catálogo a un género.

---

## Self-review

**Cobertura.** Q1→tareas 1-2. Q2→tareas 3-4. Q3→tareas 5-6. Q4→tareas 7-8. Q5→tareas 9-10 (con el alcance corregido y dicho: contenido invisible, no clash). Q6→tareas 11-12. Las cuatro decisiones del usuario están reflejadas: GPL en `ALLOWED_LICENCES`, CPCtelera como primer vendorizado, retirada del escritor libre como R1 con condición de disparo explícita, y detalle ejecutable sólo en el horizonte 1.

**Consistencia de tipos.** `verification_level(runtime)` lee `BEHAVIOUR_GATES`, que nombra `pacing` y `attributes` antes de que las tareas 6 y 10 las conecten; `.get()` devuelve `None` y cuentan como abstención hasta entonces — deliberado, y por eso la tarea 1 no hay que tocarla después. `pacing_report` y `attribute_report` devuelven la misma forma que `animation_report` (`observed`/`failures`/`quality_pass` con `None` para abstención), que es lo que hace que la tarea 1 funcione sin cambios. `contract_failures` toma el dict de `write_probe_report`, no un `Path`. El `hold` que emite `observation_script` usa exactamente los valores que `feel._classify` reconoce (`none`, las cuatro direcciones, `action`).

**Riesgos verificados dentro del propio plan, no diferidos:** la puerta de símbolos requeridos puede romper CPC (tarea 5, paso 5), el volcado ZRCP de 13 KB puede llegar truncado (tarea 9, paso 5), y el umbral de celdas invisibles se calibra contra los dos juegos existentes antes de fiarse de él (tarea 10, paso 5).
