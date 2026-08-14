# Diseño: el TUI pasa de tablero de mandos a wizard guiado

Fecha: 2026-08-14. Rama base: `main` (tras la fusión de `ir-v4-fase-1`).

## Problema

`llmz80/studio/tui.py` es un tablero de mandos: diez atajos `ctrl+<letra>`, cada uno
disparando una etapa del pipeline, y ninguna indicación de cuál toca. Quien lo abre
por primera vez tiene que saber de antemano que `ctrl+f` investiga antes que `ctrl+a`
adapta, que `ctrl+d` dibuja antes de que `ctrl+w` escriba, y que `ctrl+t` —no `ctrl+b`—
es lo único que produce el informe de calidad. La información existe: `screen.stage_line`
calcula las seis etapas y `screen.next_step` dice cuál merece la pena hacer ahora. Pero
sólo pinta una tira de estado; no conduce nada.

Y lo que el pipeline cuenta de sí mismo es demasiado poco. `tui.py` tiene trece
`self.notify` y un `_log` que escribe una línea por trabajo, **al terminarlo**. Escribir
un programa tarda minutos y llama a una API de pago; dibujar sprites reintenta cuando el
modelo devuelve un fotograma sólido. Durante todo ese rato la pantalla no dice nada,
porque los servicios devuelven su informe al final y no hay forma de que cuenten nada
antes. Al cerrar la aplicación se pierde hasta esa línea final: no queda rastro de qué se
hizo, cuándo, cuánto tardó ni qué costó.

## Objetivo

Que una persona que no conoce el pipeline pueda abrir Studio, ver qué paso toca, pulsar
Enter y entender en todo momento qué está pasando — y que al día siguiente pueda leer qué
pasó.

Fuera de alcance: que el editor de mapa dibuje el tercer tile (hoy pinta muro y suelo con
dos glifos fijos, así que una escalera es invisible); y las operaciones de edición que v4
hace expresables pero Studio aún no sabe escribir (`add_tile`, `set_exit`, `set_binding`,
`set_mechanics`). Ambas cosas están anotadas en el plan de la fase 1 y son trabajo aparte.

## Decisiones tomadas

| Decisión | Elegido | Descartado y por qué |
| --- | --- | --- |
| Rigidez | Lineal estricto: un paso cada vez, en orden | Wizard que aconseja pero no bloquea (vuelve a ser un menú); lineal con tecla de salto genérica (la excepción se acota mejor por paso, ver abajo) |
| Edición | Submodo dentro del paso 2: Enter entra al editor, Esc guarda y vuelve | Que el wizard sólo valide y se edite el YAML fuera; preguntar campo a campo (mucha interfaz nueva, y encaja mal con editar un mapa) |
| Log | Se pinta **y** se añade a `<proyecto>/studio.log` | Sólo en pantalla (cuando algo falla tras veinte minutos no queda rastro); un log global en `local/logs` (mezcla la historia de proyectos distintos) |
| Guardado | Al salir del editor, y al avanzar de paso | Guardar en cada cambio (una revisión por celda pintada); preguntar al salir (devuelve la decisión que el wizard existe para quitar) |
| Estructura | `wizard.py` puro + `journal.py` + `tui.py` como renderizador | Todo dentro de `tui.py` (1077 líneas ya, y el flujo dejaría de ser probable sin Textual); una `Screen` de Textual por paso (ata el flujo al framework) |

## Arquitectura

```
screen.stage_line / next_step        (existe: qué está hecho)
        |
   wizard.py        máquina de estados pura: qué paso es, qué le falta,
        |           qué hace Enter, si se puede avanzar
        |
   tui.py           renderizador: pinta paso, tira de etapas, diario, teclas
        |
   journal.py       formatea una línea, la añade a studio.log, y la devuelve
        |
   services.py      gana on_progress en los tres trabajos largos
```

`wizard.py` no duplica el conocimiento de qué está hecho: lo lee de `stage_line`, que ya
lo deriva del diseño en memoria y de lo que el pipeline dejó en disco. El wizard sólo
añade el orden, el texto de cada paso y la regla de avance.

## `wizard.py`

```python
@dataclass(frozen=True)
class Step:
    number: int              # 0..6; 0 es elegir o crear proyecto
    name: str                # "sprites"
    summary: str             # "Dibujar el arte de 2 entidades sin sprite"
    action_label: str        # "dibujar"
    costs_api: bool          # para avisar antes de gastar dinero
    state: StepState         # done | pending | failed | skipped
    detail: str              # por qué falló, o qué falta
    editable: bool           # sólo el paso 2
    skippable: bool          # sólo los pasos 1 y 3


def steps(project: GameProject | None, directory: Path | None) -> list[Step]
def current(project: GameProject | None, directory: Path | None) -> Step
```

`current` es el primer paso que no está hecho ni omitido — que es exactamente lo que
`screen.next_step` ya calcula, incluida su regla de que un fallo temprano gana a un
pendiente posterior.

`StepState` añade `skipped` a los tres estados de `screen.StageState`. Los pasos 1
(referencia) y 3 (sprites) son opcionales por naturaleza: un juego puede no estar basado
en ninguno real, y uno sin sprites se dibuja con caracteres. Exigirles "hecho" para
avanzar sería inventar un requisito que el pipeline no tiene. Omitir queda escrito en el
diario, así que la decisión es visible.

## `journal.py`

```python
KIND = Literal["ABRIR", "ETAPA", "INICIO", "..", "FIN", "AVISO", "ERROR", "GUARDAR", "OMITIR"]

@dataclass
class Journal:
    path: Path                                   # <proyecto>/studio.log

    def write(self, kind: KIND, text: str) -> str: ...
    def start(self, text: str) -> Token: ...     # escribe INICIO, recuerda el instante
    def note(self, text: str) -> str: ...        # una línea ".."
    def finish(self, token: Token, ok: bool, text: str) -> str: ...   # FIN con duración
```

Cada método **escribe la línea en el fichero y la devuelve formateada**. Que sea la misma
cadena es lo que garantiza que pantalla y fichero no diverjan; si el TUI compusiera la
suya por su cuenta, tarde o temprano dirían cosas distintas del mismo suceso.

`finish` calcula la duración desde su `start`, que es lo que convierte el diario en algo
que se puede leer para saber qué costó tiempo.

Ejemplo de `studio.log`:

```
2026-08-14 09:14:02  ABRIR    proyecto fase-uno (spectrum, v4)
2026-08-14 09:14:02  ETAPA    2 diseño: ok — 2 pantallas, 2 entidades, 3 tiles
2026-08-14 09:14:02  AVISO    el diseño no declara mecánicas
2026-08-14 09:14:05  INICIO   3 sprites — 2 entidades sin arte (API)
2026-08-14 09:14:31  ..       hero: 4 poses empaquetadas, 512 B
2026-08-14 09:15:02  ..       momia: reintento 1, fotograma sólido
2026-08-14 09:15:29  FIN      3 sprites — ok en 84 s, 2 hojas, 1024 B
```

El fichero se abre en modo añadir, así que reabrir un proyecto conserva la historia de las
sesiones anteriores. `studio-projects/` está en `.gitignore`, de modo que el diario no
entra en el repositorio.

## Los pasos

| | Paso | Enter hace | API | Omitible |
| --- | --- | --- | --- | --- |
| 0 | Proyecto | elegir uno del workspace, o crear otro | no | no |
| 1 | Referencia | busca el juego real y archiva la ficha citada | sí | sí |
| 2 | Diseño | entra al editor; Esc guarda y vuelve | no | no |
| 3 | Sprites | dibuja el arte que falte | sí | sí |
| 4 | Programa | escribe el juego en C y lo repara contra el compilador | sí | no |
| 5 | Gates | compila, ejecuta en el emulador y pasa las puertas | no | no |
| 6 | Release | empaqueta el zip con su evidencia | no | no |

El paso 0 es lo que hoy son `ctrl+n` y `ctrl+o`, convertido en pantalla de entrada: sin
proyecto no hay wizard que conducir. Es también donde vive la creación, que llama a
`samples.blank_project`.

`stage_line` sólo conoce las seis etapas del pipeline, así que `wizard.steps` sintetiza
el paso 0 por su cuenta: está `done` en cuanto hay un proyecto abierto y `pending`
mientras no lo haya. Es el único paso cuyo estado el wizard decide en vez de leer, y lo
hace porque "tengo un proyecto abierto" no es evidencia que nadie deje en disco.

## Progreso durante los trabajos largos

Las líneas `..` del diario no se pueden tener con la interfaz actual: los servicios
devuelven su informe cuando terminan. Los tres trabajos largos ganan un parámetro
opcional:

```python
def draw_sprites(self, project, directory, artist, *, on_progress=None) -> list[AssetSpec]
def write_program(self, project, directory, writer, *, on_progress=None) -> dict
def runtime_test(self, project, directory, *, seconds=3, on_progress=None) -> dict
```

`on_progress` es `Callable[[str], None] | None`, y por defecto no hacen nada — ni la CLI
ni los tests existentes cambian. Lo llaman cuando pasa algo digno de contar: una hoja
empaquetada, un reintento del artista con lo que se le reprochó, un intento del escritor
con su veredicto de build.

Es interfaz nueva en `services.py`, y es la única forma honesta de cumplir lo pedido: sin
ella, "informar de lo que pasa en cada paso" sólo puede informar cuando el paso terminó.

## Teclas

Desaparecen las diez: `ctrl+n`, `ctrl+o`, `ctrl+s`, `ctrl+f`, `ctrl+a`, `ctrl+d`,
`ctrl+w`, `ctrl+b`, `ctrl+t`, `ctrl+r`.

| Tecla | En el wizard | En el editor |
| --- | --- | --- |
| `Enter` | ejecuta la acción del paso; si ya está hecho, avanza | — |
| `R` | repite un paso ya hecho, preguntando antes de sobrescribir | — |
| `Esc` | retrocede un paso, para mirarlo | guarda y vuelve al wizard |
| `↑↓←→` | elige proyecto en el paso 0 | mueve el cursor |
| `Espacio` | — | pinta la celda |
| `Tab` | — | cambia el tile con el que se pinta |
| `S` | omite el paso, sólo en los pasos 1 y 3 | — |
| `Q` | salir | — |

Ninguna tecla hace cosas distintas según el contexto salvo las flechas, que son
"moverse" en los dos.

`R` existe porque `Enter` sobre un paso hecho avanza, y sin él no habría forma de
rehacer nada: volver con `Esc` a un paso terminado dejaría al usuario mirándolo sin
poder tocarlo. Reutiliza la confirmación de sobrescritura que `research_reference` y
`draw_sprites` ya piden hoy antes de pisar lo que había.

## Fallos

Un paso que falla **no avanza**: escribe `ERROR` con su razón en el diario, se queda donde
está y muestra el detalle. Que las puertas rechacen el programa es un resultado del paso 5,
no una excepción: se registra y se ofrece reintentar. Una excepción de verdad —la API
cae, el disco se llena— se registra igual y no tumba la aplicación, como ya hace `_run`.

## Pruebas

- `wizard.py`, como datos y sin Textual: cuál es el paso actual en un proyecto recién
  creado, tras archivar la ficha, con el diseño roto, con todo hecho; que omitir un paso
  omitible avanza y omitir uno que no lo es se refusa.
- `journal.py`: el formato de cada tipo, que `finish` calcula la duración, que añadir no
  pierde líneas previas, y que la cadena devuelta es idéntica a la escrita.
- `services.py`: que `on_progress` recibe una línea por hoja empaquetada y por intento del
  escritor, y que omitirlo no cambia nada.
- `tui.py`, con el `run_test` de Textual como hoy: que Enter ejecuta la acción del paso
  actual, que Esc en el editor guarda, y —el test que fija la decisión— que **ninguna de
  las diez teclas `ctrl` sigue atada**.

## Evidencia de aceptación

Abrir Studio sobre un workspace vacío y, sin conocer el pipeline ni consultar
documentación, llegar hasta un `game.yml` válido usando sólo Enter, Esc y las flechas. Y
que `studio.log` cuente después qué pasó, con sus inicios, sus finales y sus duraciones.
