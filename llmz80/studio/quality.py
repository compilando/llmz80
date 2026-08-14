"""Project-level quality gates above compiler and emulator evidence.

What a design must satisfy is now only what the machine imposes: audio it can
produce, budgets it can hold, and a structure that refers to itself (already
enforced when the document validates). Solvability, difficulty curve and
terrain structure were retired with the template: all three assumed four-way
grid movement with no jump, so on anything else they reported confidently and
wrongly. What they were reaching for -- can this actually be played -- belongs
to the examiner and the emulator, which can answer it for any design.

`notices` is the other half of that restraint: things worth telling the person
who wrote the design, which are none of Studio's business to refuse.

`verification_level` is the one thing here that reads runtime evidence rather
than the design, and it lives here because it is a verdict about the report
this module writes, not about a run: `studio_quality_report` is what has to
state how much of the game was ever watched, and a level computed in
`services.py` beside the gates it reads would have to be carried back here
anyway. `feel.py` and its siblings answer "was this run good"; this answers
"did anyone look at all", which is the question the report claiming a pass is
the one obliged to answer.
"""

from __future__ import annotations

from typing import Any

from .models import GameProject
from .registry import audio_gaps, target_registry

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
    if any(verdict is True for verdict in verdicts):
        return VERIFICATION_OBSERVED
    return VERIFICATION_BUILT


def design_notices(project: GameProject) -> list[str]:
    """Advice for the designer. Never a refusal.

    A design with no stated mechanics still builds and still runs; what it
    cannot do is tell the writer what the game is, so the program that comes
    back is whatever the model guessed. Saying so is useful. Refusing would be
    Studio deciding a game must have rules it can read, which is the kind of
    judgement v4 exists to stop making.
    """
    notices = []
    if not project.mechanics:
        notices.append(
            "this design states no mechanics, so nothing tells the writer how the "
            "game is won, lost or played; the program will be whatever the model "
            "infers from the screens and the brief"
        )
    return notices


def design_quality_report(project: GameProject) -> dict[str, Any]:
    pack = target_registry().get(project.target.platform.value)
    gaps = audio_gaps(project)
    checks = {
        "audio_is_supported_by_target": not gaps,
        "budget_fits_target": (
            project.budgets.binary_bytes <= pack.binary_budget
            and project.budgets.static_data_bytes <= pack.data_budget
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "schema_version": 6,
        "checks": checks,
        "failures": failures,
        "notices": design_notices(project),
        "audio_gaps": gaps,
        "quality_pass": not failures,
    }


def studio_quality_report(
    project: GameProject,
    *,
    build: dict[str, Any] | None = None,
    runtime: dict[str, Any] | None = None,
) -> dict[str, Any]:
    design = design_quality_report(project)
    gates = {
        "design": design["quality_pass"],
        "build": bool(build and build.get("quality_pass")),
        "runtime": bool(runtime and runtime.get("quality_pass")),
    }
    return {
        "schema_version": 2,
        "project": project.metadata.slug,
        "target": project.target.platform.value,
        "gates": gates,
        "design": design,
        "build_report": "build_report.json" if build else None,
        "runtime_report": "emulator_report.json" if runtime else None,
        "verification": verification_level(runtime),
        "quality_pass": all(gates.values()),
    }
