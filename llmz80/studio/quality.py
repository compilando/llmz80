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


#: The check that refuses a brief with nothing to implement. Named because
#: three places ask about this one check by name -- the report builds it, the
#: refusal sentence is looked up under it, and `make.py` asks whether skipping
#: `diseño` has left the design in exactly this state -- and a slug spelled
#: out four times is a slug that will be misspelled once.
MECHANICS_CHECK = "design_states_the_mechanics_its_brief_asks_for"


#: Why each design check refuses, in words the person who wrote the design can
#: act on. `failures` carries check *names* -- slugs, which are what a report
#: reader and a test want, and which say nothing to somebody told their game
#: will not be written -- so anything that puts a refusal in front of a person
#: looks the sentence up here. Kept beside `checks` so a check added without a
#: sentence is visibly missing one.
DESIGN_REFUSALS = {
    "audio_is_supported_by_target": (
        "this design asks for sound the target machine cannot produce; see "
        "audio_gaps for which effects, and drop or replace them"
    ),
    "budget_fits_target": (
        "this design reserves more binary or static data than the target "
        "machine has; lower the budgets until they fit"
    ),
    MECHANICS_CHECK: (
        "this design carries a brief but states no mechanics, so nothing tells "
        "the writer how the game is won, lost or played and the program would "
        "be whatever the model infers; write the rules the brief asks for into "
        "the design's `mechanics` list in game.yml, one sentence per rule"
    ),
}


def design_refusals(report: dict[str, Any]) -> list[str]:
    """A design report's failures as sentences, in the order it lists them.

    A refusal is only worth raising if the person who reads it can act on
    it, and a check name is a variable, not a sentence: telling the designer
    of `studio-projects/zampabolas` that his design failed
    `design_states_the_mechanics_its_brief_asks_for` would have left him no
    better off than the silence that let it through did.
    """
    return [DESIGN_REFUSALS.get(name, name) for name in report["failures"]]


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


def design_quality_report(project: GameProject) -> dict[str, Any]:
    pack = target_registry().get(project.target.platform.value)
    gaps = audio_gaps(project)
    checks = {
        "audio_is_supported_by_target": not gaps,
        "budget_fits_target": (
            project.budgets.binary_bytes <= pack.binary_budget
            and project.budgets.static_data_bytes <= pack.data_budget
        ),
        MECHANICS_CHECK: bool(project.mechanics) or not project.metadata.brief.strip(),
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "schema_version": 7,
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
