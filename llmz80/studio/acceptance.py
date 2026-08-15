"""The design, in the form whoever writes the program needs it, and the
expectations the examiner binds to the run that was already recorded.

What this module used to derive from the design -- a runnable acceptance
script -- assumed one kind of game: an actor stepping through a grid at a
fixed cadence, scoring one collectible at a time. That assumption is what made
any other kind of game fail verification (`studio-projects/archive-v3` keeps
three of them: `zampabolas` and `atic-atac-2000` burned all five write
attempts against it, `brick-wall` fell on its third), so the guessing is gone
for good. What replaced it, and stayed empty until now, was nothing at all:
`runtime_script` returned `[]`, `services.acceptance_report` abstained, and
`generator.write_program` read that abstention as a pass -- which is how a
program that draws one glyph and ends the game on a keypress was accepted on
its first attempt.

So this module now does the one thing between those two failures: it takes the
steps `observation.observation_script` will really run, asks an examiner which
readings of memory *that run* must produce, and states them as expectations
`services.acceptance_report` can judge. It still invents nothing on its own --
with no examiner it returns no steps and the gate abstains exactly as before.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from llmz80.core.state_contract import contract_prompt

from .models import AssetSpec, GameProject
from .observation import observation_script
from .runtime_exam import (
    RuntimeExam,
    RuntimeExaminer,
    UncheckableMechanic,
    dedupe,
    derived_assertions,
    examinable_symbols,
    usable_assertions,
)
from .spriting import is_blitter_sprite

#: How a step's expectation compares the reading against what it expects.
#:
#: Exact equality was the whole vocabulary until now, and it can say "g_state
#: is 1" and nothing else -- not "the score went up", which is the most
#: checkable claim a design makes and the one an examiner reaches for first.
#: The bounds are here rather than a general expression language because every
#: claim the observation script can actually witness is one of these five, and
#: an expression a model writes is an expression nobody can review.
EQUALS = "equals"
AT_LEAST = "at_least"
AT_MOST = "at_most"
CHANGED = "changed"
UNCHANGED = "unchanged"
COMPARISONS: tuple[str, ...] = (EQUALS, AT_LEAST, AT_MOST, CHANGED, UNCHANGED)


def blitter_sprites(project: GameProject) -> list[AssetSpec]:
    """Assets that `render_project` will really emit a SPRITE_<ID> for.

    Filtered through `is_blitter_sprite`, not just `asset.kind == "sprite"`:
    an asset shaped wrong for the blitter (not 16x16 per frame) still falls
    back to a plain `assets.c` import with no `SPRITE_<ID>` constant, and
    promising one here that `compiler.render_project` never defines is a
    prompt that lies to the writer -- it finds out three files and one
    compiler error later. See `is_blitter_sprite`'s own docstring for why
    that filter lives in `spriting.py` rather than being duplicated here.
    """
    return [asset for asset in project.assets if is_blitter_sprite(asset)]


def predicate(expectation: Any) -> dict[str, Any]:
    """One expectation, in the one shape the judge reads.

    A bare number is read as `equals` that number, so the shape that was on
    disk before this module learned to compare -- `{"g_state": 1}` -- still
    means what it always meant. Keeping it is not politeness towards old
    files: `services.acceptance_report`, `generator.repair_prompt` and every
    test fixture already speak it, and a flag day for a shape whose only
    producer is one function would have been changed noise in six modules.
    """
    if isinstance(expectation, dict):
        return expectation
    return {"compare": EQUALS, "value": expectation}


def _said(compare: str, target: Any, baseline: str | None) -> str:
    """The expectation as a sentence, because a writer reads it.

    `generator.repair_prompt` hands every mismatch straight to the model that
    has to fix the program, so `g_score: at_least 14` is worse than useless
    without saying where 14 came from -- the model would go looking for the
    number 14 in its own source.
    """
    where = f" (its reading at {baseline})" if baseline else ""
    if compare == EQUALS:
        return f"exactly {target}{where}"
    if compare == AT_LEAST:
        return f"at least {target}{where}"
    if compare == AT_MOST:
        return f"at most {target}{where}"
    if compare == CHANGED:
        return f"anything other than {target}{where}"
    return f"still {target}{where}"


def _satisfied(compare: str, actual: int, target: int) -> bool:
    if compare == AT_LEAST:
        return actual >= target
    if compare == AT_MOST:
        return actual <= target
    if compare == CHANGED:
        return actual != target
    return actual == target


def step_mismatches(step: dict[str, Any], readings: dict[str, dict[str, Any]]) -> list[str]:
    """Every expectation of `step` the readings did not satisfy, said in words.

    `readings` is the whole run, not this step's reading, because a comparison
    may name an earlier step: "the score at `hold_down_a` is at least what it
    was at `hold_left_a`" is a claim about two readings, and it is the claim
    that makes a rising score checkable at all.

    A symbol the step expects and the run never read is a mismatch, not a
    silent pass. That is the same rule `acceptance_report` applies to a step
    with no reading at all, and it exists because the opposite reading -- an
    absent number satisfying whatever was asked of it -- is how an unobserved
    run turns into an approved one.
    """
    read = readings.get(step["id"]) or {}
    mismatches: list[str] = []
    for name, expectation in sorted((step.get("expect") or {}).items()):
        rule = predicate(expectation)
        compare = rule.get("compare", EQUALS)
        baseline = rule.get("baseline")
        target = rule.get("value")
        if baseline is not None:
            target = (readings.get(baseline) or {}).get(name)
            if target is None:
                mismatches.append(
                    f"{name}: nothing was read at {baseline}, so there is nothing to compare against"
                )
                continue
        actual = read.get(name)
        if actual is None:
            mismatches.append(f"{name}: expected {_said(compare, target, baseline)}, read nothing")
            continue
        if not _satisfied(compare, actual, target):
            mismatches.append(f"{name}: expected {_said(compare, target, baseline)}, read {actual}")
    return mismatches


def _reason(project: GameProject, item: UncheckableMechanic) -> str:
    """One declined mechanic as a sentence a person can read on its own.

    The examiner answers with a number, and a report that printed the number
    would make whoever reads it go back to `game.yml` and count.
    """
    if 1 <= item.mechanic <= len(project.mechanics):
        return f'"{project.mechanics[item.mechanic - 1]}" -- {item.why}'
    return item.why


@dataclass
class RuntimeExamination:
    """What an examiner made of this design, ready for the gate to judge.

    Steps and unchecked mechanics travel together, which is why this replaced
    the bare `list[dict]` `runtime_script` used to be. The gate has to report
    both -- what was asserted and how much of the design nobody asserted
    anything about -- and the only alternative was calling the examiner twice
    or asking it once and reading its answer from two places.
    """

    steps: list[dict[str, Any]] = field(default_factory=list)
    #: The design's own sentences that no assertion is bound to, verbatim.
    #: Derived here from what the assertions cite rather than taken from the
    #: examiner's own list, so a model that forgets to declare a mechanic
    #: unverifiable cannot make the coverage look better than it is.
    unchecked: list[str] = field(default_factory=list)
    #: Why the examiner said it could not check them. Its words, unpoliced.
    reasons: list[str] = field(default_factory=list)
    #: Assertions that were thrown away before the run was judged, one
    #: sentence each -- see `runtime_exam.usable_assertions` for what makes an
    #: assertion unusable and why throwing it away beats failing the program.
    discarded: list[str] = field(default_factory=list)

    @property
    def asserted(self) -> bool:
        return any(step.get("expect") for step in self.steps)


def runtime_examination(
    project: GameProject,
    examiner: RuntimeExaminer | None = None,
    *,
    symbols: list[str] | None = None,
) -> RuntimeExamination:
    """Ask `examiner` what the observation script must show, if there is one.

    Without an examiner this returns nothing at all and the gate abstains,
    which is what an unexamined program honestly is -- the state this module
    was left in on purpose after the hardcoded script was withdrawn.

    The steps are `observation.observation_script`'s own, expectations filled
    in: the emulator drives that script and no other, so an examiner that
    invented its own steps would be predicting a run nobody performs. That is
    also why `symbols` is passed in from the run rather than taken from
    `state_contract`: the contract's optional symbols (lives, level,
    remaining) exist only in the designs that declared them, and an assertion
    about a symbol this program does not have would fail a correct game for a
    concept it never claimed to have.

    An examiner that raises is treated as no examiner at all. A gate that
    abstains costs an unobserved run; a gate that crashes costs the whole
    write attempt, and the model behind the examiner is the one part of this
    that is entitled to have a bad day.
    """
    steps = observation_script(project)
    if examiner is None or not steps:
        return RuntimeExamination()
    available = examinable_symbols(symbols or [])
    try:
        exam: RuntimeExam = examiner.examine(project, steps, available)
    except Exception as exc:  # noqa: BLE001 -- see docstring
        return RuntimeExamination(reasons=[f"the examiner failed and was ignored: {exc}"])
    # The claims nobody had to be asked for, added to whatever was answered.
    # They go through `usable_assertions` beside the examiner's own, because a
    # derivation is not exempt from the rules that make an assertion judgeable
    # -- and they go in *after* the examiner's, so that `dedupe` keeps the
    # attribution the examiner gave a claim they both make (see its docstring:
    # keeping the derived copy would cost `minero-observable` both its checked
    # mechanics). Only when an examiner ran at all: without one this function
    # returned nothing before now, the gate abstained, and turning that
    # abstention into a judged run is a decision for whoever supplies an
    # examiner, not a side effect of this module learning to derive.
    exam = RuntimeExam(
        assertions=dedupe(exam.assertions + derived_assertions(project, steps, available)),
        unverifiable=exam.unverifiable,
    )
    kept, discarded = usable_assertions(exam, steps, available)
    by_step: dict[str, dict[str, Any]] = {}
    for assertion in kept:
        rule: dict[str, Any] = {"compare": assertion.compare, "why": assertion.why}
        if assertion.baseline:
            rule["baseline"] = assertion.baseline
        else:
            rule["value"] = assertion.value
        by_step.setdefault(assertion.step, {})[assertion.symbol] = rule
    # A mechanic the examiner called unverifiable stays unchecked even when
    # an assertion cites it. The two answers contradict each other and the
    # honest reading of a contradiction is the one that claims less -- the
    # same rule `design_exam.coverage_errors` applies to a model that says
    # "covered" and then names a gap.
    declined = {item.mechanic for item in exam.unverifiable}
    cited = {assertion.mechanic for assertion in kept} - declined
    return RuntimeExamination(
        steps=[{**step, "expect": by_step.get(step["id"], {})} for step in steps],
        unchecked=[
            sentence
            for number, sentence in enumerate(project.mechanics, start=1)
            if number not in cited
        ],
        reasons=[_reason(project, item) for item in exam.unverifiable],
        discarded=discarded,
    )


def runtime_script(
    project: GameProject, examiner: RuntimeExaminer | None = None
) -> list[dict[str, Any]]:
    """The steps the acceptance gate judges, empty when nobody examined this.

    Thin over `runtime_examination` and kept because a caller that wants only
    the steps should not have to know what else an examination carries.
    """
    return runtime_examination(project, examiner).steps


def design_prompt(project: GameProject) -> str:
    """The design itself, in the vocabulary the design coined for it."""
    lines = ["DESIGN", ""]
    if project.metadata.brief.strip():
        lines.extend(["What this game should be:", "", project.metadata.brief.strip(), ""])
    lines += [
        f"Title: {project.metadata.title}",
        f"Target: {project.target.platform.value}, {project.target.video_mode.value}, "
        f"{project.target.frame_hz} Hz",
        f"Presentation: {project.presentation.style}",
        "",
    ]
    if project.mechanics:
        lines.append("Mechanics this game must have:")
        lines.extend(f"  - {sentence}" for sentence in project.mechanics)
        lines.append("")
    else:
        # A design is free to declare no rules at all, but silence here must
        # not read as permission to invent a win/lose condition to fit the
        # brief's mood -- that is exactly the kind of guess phase 2's
        # examiner cannot verify. Wording softens when a brief exists (it
        # sets atmosphere, not rules -- "an explorer crosses stone rooms"
        # still does not say how the game is won) but the instruction is
        # never dropped, only its tone.
        if project.metadata.brief.strip():
            lines.append(
                "This design states no mechanics beyond the brief above, and a brief "
                "sets mood, not rules -- it does not say how the game is won or lost. "
                "Implement only what is declared elsewhere below (terrain, actors, "
                "controls, screens, scenes); do not invent a win or lose condition to "
                "match the brief silently. Leave a comment in the code naming any rule "
                "you had to assume."
            )
        else:
            lines.append(
                "This design declares no mechanics at all. Implement only what is "
                "declared below (terrain, actors, controls, screens, scenes) and do "
                "not invent a win or lose condition silently. Leave a comment in the "
                "code naming any rule you had to assume to make the game playable."
            )
        lines.append("")

    lines.append("Controls. game_config.h defines one bit per binding:")
    for name, key in project.controls.bindings.items():
        lines.append(f"  INPUT_{name.upper():<12} key {key}")
    lines.append("")

    # Drawing terrain is unconditional -- every design has at least one tile
    # (TileSpec has min_length=1) -- so this instruction must not live inside
    # the `if sprites` branch below, the way the sprite-only half of drawing
    # does. A design with no sprites (the common case: a new project starts
    # with none) still needs to be told how its screen gets drawn at all.
    lines.append(
        "Terrain characters, as they appear in the screens below. Draw one with "
        "plat_cell(col, row, character):"
    )
    for tile in project.tiles:
        traits = f" [{', '.join(tile.traits)}]" if tile.traits else ""
        lines.append(f"  '{tile.char}' is {tile.id}{traits}")
    lines.append("")

    # "Actors" would presuppose every entity plays that role; `kind` is free
    # vocabulary a design coins for itself (a door, a switch, a collectible),
    # so the heading stays neutral about what any of them do.
    lines.append("Things in this game:")
    for entity in project.entities:
        # `count` is `structure.py`'s per-screen spawn budget, not "there are
        # this many" -- rendering it as "x3" reads as the latter, so it is
        # shown as an explicit cap, and only when it says anything a reader
        # couldn't assume (a count of 1 is the default and needs no caveat).
        cap = f", at most {entity.count} per screen" if entity.count > 1 else ""
        poses = f", poses {', '.join(entity.poses)}" if entity.poses else ""
        notes = f" -- {entity.notes}" if entity.notes else ""
        lines.append(f"  {entity.id}: {entity.kind}{cap}{poses}{notes}")
    lines.append("")

    if project.observables:
        # Said as an obligation, not as an inventory. game_state.h declares
        # these `extern` and nothing else in this prompt told the writer it
        # had to define them, so the sentence a writer could reasonably read
        # as "Studio provides these" is now the one that says the opposite --
        # and a program that leaves one undefined no longer links quietly:
        # `probes.contract_failures` fails the build on it, exactly as it does
        # for a missing required contract symbol.
        lines.append(
            "Extra state this design declares. game_state.h declares each of these "
            "extern; your program must define it exactly once at file scope and keep "
            "it accurate as the rule it names happens, because it is read straight "
            "out of memory to check that rule:"
        )
        for observable in project.observables:
            ctype = "unsigned int" if observable.width == 2 else "unsigned char"
            lines.append(f"  {ctype} {observable.symbol};  {observable.meaning}")
        lines.append("")

    # blitter_sprites(), not project.assets: only what it returns gets a real
    # SPRITE_<ID> constant in sprites.h (see its own docstring), so advertising
    # anything wider here would promise a constant the header never defines.
    sprites = blitter_sprites(project)
    if sprites:
        lines.append(
            "Sprites: draw one with plat_sprite(col, row, sprite, frame). This is not "
            "optional once a design has sprites: a program that packs sprites below but "
            "never calls plat_sprite fails verification (see compiler.py's "
            "check for it). Each sprite below is a SPRITE_<ID> constant and a frame "
            "count from sprites.h."
        )
        for asset in sprites:
            wearers = [entity.id for entity in project.entities if entity.sprite == asset.id]
            worn = f", worn by {', '.join(wearers)}" if wearers else ""
            frame_word = "frame" if asset.frames == 1 else "frames"
            lines.append(
                f"  {asset.id}: SPRITE_{asset.id.upper()}, {asset.frames} {frame_word}{worn}"
            )
        lines.append("")

    if project.audio.effects:
        lines.append(
            "Sound effects, played with plat_sound(SOUND_<NAME>) from game_config.h: "
            + ", ".join(project.audio.effects)
        )
        lines.append("")

    lines.append(f"The game starts on screen {project.initial_screen}.")
    for screen in project.screens:
        limit = (
            f", time limit {screen.time_limit_seconds}s"
            if screen.time_limit_seconds is not None
            else ""
        )
        lines.extend(
            ["", f'Screen {screen.id} "{screen.name}", ' f"{screen.width}x{screen.height}{limit}"]
        )
        lines.extend(f"    {row}" for row in screen.tiles)
        if screen.spawns:
            lines.append("  Starting positions (column, row):")
            for spawn in screen.spawns:
                lines.append(f"    {spawn.entity} at ({spawn.col}, {spawn.row})")
        for direction, destination in screen.exits.items():
            lines.append(f"  Exit {direction} -> {destination}")

    # Presentation flow is a separate graph from the screens above: every
    # design has at least two scenes (SceneSpec has min_length=2), and
    # contract_prompt() below already hands the writer four g_state values
    # (title/playing/game over/victory) to keep accurate -- without this
    # block nothing ever told it which scene is which or how they connect.
    lines.extend(["", f"Scenes: presentation flow, starting at {project.initial_scene}."])
    for scene in project.scenes:
        title = f' "{scene.title}"' if scene.title else ""
        lines.append(f"  {scene.id} ({scene.kind}){title}")
        if scene.next_scene:
            lines.append(f"    -> {scene.next_scene}")
        for option in scene.options:
            lines.append(f'    "{option.label}" -> {option.target_scene}')

    # This paragraph is written before the writer has seen platform.h itself:
    # `generator.writing_prompt` appends this design prompt first and
    # `library_interface()` -- the actual header text -- later in the same
    # message. It orients the writer to what is coming, it does not repeat it.
    lines.extend(
        [
            "",
            "Studio writes game_config.h with these constants, and game_state.h",
            "declaring the contract and this design's observables, into the same",
            "directory as your sources. A platform library is there too:",
            "platform.h documents what it offers.",
        ]
    )
    if sprites:
        lines.append(
            "Use as much of it as helps, except plat_sprite: this design's sprites "
            "make it mandatory, not optional (see above)."
        )
    else:
        lines.append("Use it or don't.")
    return "\n".join(lines)


def generation_prompt(project: GameProject) -> str:
    """Everything a generator is owed before it writes the program."""
    return "\n\n".join([contract_prompt(), design_prompt(project)])
