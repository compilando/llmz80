"""The examiner that lets the acceptance gate judge a program, and its limits.

Every reading in this file was recorded by a real emulator run of a real game
in `studio-projects/`, pasted here because that directory is not in the
repository and a gate this often wrong deserves to be pinned against runs that
actually happened rather than against numbers invented to make it pass.
"""

from __future__ import annotations

from typing import Any, get_args

from llmz80.core.state_contract import STATE_TITLE
from llmz80.studio.acceptance import (
    AT_LEAST,
    AT_MOST,
    CHANGED,
    COMPARISONS,
    EQUALS,
    runtime_examination,
    step_mismatches,
)
from llmz80.studio.models import GameProject, TargetPlatform
from llmz80.studio.observation import observation_script
from llmz80.studio.runtime_exam import (
    RepeatedExaminer,
    RuntimeAssertion,
    RuntimeExam,
    UncheckableMechanic,
    merge_exams,
    usable_assertions,
)
from llmz80.studio.samples import blank_project
from llmz80.studio.services import StudioService

#: `studio-projects/un-minero-que-cava-tuneles-y-2/build/emulator_report.json`.
#: The miner digs, scores, reaches the exit on the seventh step (g_state 3) and
#: is back on its title screen by the eighth, with four steps still to run.
MINER_READINGS: list[tuple[str, dict[str, int]]] = [
    ("hold_action_a", {"g_anim_frame": 0, "g_lives": 3, "g_score": 0, "g_state": 1}),
    ("hold_action_b", {"g_anim_frame": 0, "g_lives": 3, "g_score": 0, "g_state": 1}),
    ("hold_left_a", {"g_anim_frame": 1, "g_lives": 3, "g_score": 0, "g_state": 1}),
    ("hold_right_a", {"g_anim_frame": 2, "g_lives": 3, "g_score": 14, "g_state": 1}),
    ("hold_up_a", {"g_anim_frame": 3, "g_lives": 3, "g_score": 15, "g_state": 1}),
    ("hold_down_a", {"g_anim_frame": 2, "g_lives": 3, "g_score": 24, "g_state": 1}),
    ("hold_left_b", {"g_anim_frame": 0, "g_lives": 3, "g_score": 525, "g_state": 3}),
    ("hold_right_b", {"g_anim_frame": 0, "g_lives": 3, "g_score": 525, "g_state": 0}),
    ("hold_up_b", {"g_anim_frame": 0, "g_lives": 3, "g_score": 525, "g_state": 0}),
    ("hold_down_b", {"g_anim_frame": 0, "g_lives": 3, "g_score": 525, "g_state": 0}),
    ("idle", {"g_anim_frame": 0, "g_lives": 3, "g_score": 525, "g_state": 0}),
]

#: `studio-projects/rana-recheck/build/emulator_report.json`. The frog is
#: driven in all four directions for a second each and never reaches the far
#: side of the road, so its score stays 0 for the whole run. That is the
#: correct behaviour of a correct program, and an examiner that asserted the
#: score rises would be rejecting a finished game.
FROG_READINGS: list[tuple[str, dict[str, int]]] = [
    (step, {"g_anim_frame": frame, "g_score": 0, "g_state": 1})
    for step, frame in [
        ("hold_action_a", 0),
        ("hold_action_b", 0),
        ("hold_left_a", 1),
        ("hold_right_a", 2),
        ("hold_up_a", 3),
        ("hold_down_a", 0),
        ("hold_left_b", 1),
        ("hold_right_b", 2),
        ("hold_up_b", 3),
        ("hold_down_b", 0),
        ("idle", 0),
    ]
]


def _service() -> StudioService:
    """The gate with no workspace behind it: `acceptance_report` reads only the
    runtime report it is handed, so a store would be scenery."""
    return StudioService(store=None)  # type: ignore[arg-type]


def _runtime(readings: list[tuple[str, dict[str, int]]]) -> dict[str, Any]:
    return {"step_readings": [{"id": step, "read": read} for step, read in readings]}


def _project(*mechanics: str) -> GameProject:
    """A Spectrum design whose bindings give the observation script the exact
    step ids the recorded runs above were driven with."""
    document = blank_project("Examined", TargetPlatform.SPECTRUM).model_dump(mode="json")
    document["mechanics"] = list(mechanics)
    return GameProject.model_validate(document)


class ScriptedExaminer:
    """Answers with assertions decided here, so no test makes an API call."""

    def __init__(self, exam: RuntimeExam) -> None:
        self.exam = exam
        self.calls = 0

    def examine(self, project, steps, symbols) -> RuntimeExam:
        self.calls += 1
        return self.exam


def _exam(
    *assertions: RuntimeAssertion, unverifiable: list[UncheckableMechanic] | None = None
) -> RuntimeExam:
    return RuntimeExam(assertions=list(assertions), unverifiable=unverifiable or [])


def test_a_score_that_rises_across_the_run_is_a_claim_the_gate_can_actually_judge():
    """Exact equality, the whole vocabulary this gate had until now, cannot say
    "the score went up": it can only name a number nobody can predict. Judged
    against the miner's own recorded readings, where it went 0, 14, 24."""
    report = _service().acceptance_report(
        _project("Digging dirt scores a point for every cell dug away."),
        _runtime(MINER_READINGS),
        ScriptedExaminer(
            _exam(
                RuntimeAssertion(
                    step="hold_down_a",
                    symbol="g_score",
                    compare=AT_LEAST,
                    baseline="hold_left_a",
                    mechanic=1,
                    why="every dug cell scores, and the miner digs while a direction is held",
                )
            )
        ),
    )

    assert report["quality_pass"] is True
    judged = {step["id"]: step for step in report["scenarios"]}
    assert judged["hold_down_a"]["expect"]["g_score"]["baseline"] == "hold_left_a"
    assert judged["hold_down_a"]["mismatches"] == []


def test_a_game_whose_score_never_moves_is_not_failed_for_a_rule_nobody_could_check():
    """The frog's score stays 0 because the harness cannot walk it to the far
    kerb. Its scoring mechanic must come back as unchecked, not as a failure:
    rejecting a finished game for a claim the run cannot witness is the exact
    mistake that cost three games all their write attempts."""
    goal = "Al entrar en una casilla de meta, ganas la partida."
    report = _service().acceptance_report(
        _project(goal, "La rana no puede salir de la pantalla."),
        _runtime(FROG_READINGS),
        ScriptedExaminer(
            _exam(
                RuntimeAssertion(
                    step="hold_left_a",
                    symbol="g_state",
                    compare=EQUALS,
                    value=1,
                    mechanic=0,
                    why="the action key has been held twice, so the title screen is behind us",
                ),
                unverifiable=[
                    UncheckableMechanic(mechanic=1, why="nobody can steer the frog to the goal")
                ],
            )
        ),
    )

    assert report["quality_pass"] is True
    assert report["unchecked_mechanics"] == [goal, "La rana no puede salir de la pantalla."]
    assert report["mechanics_total"] == 2
    assert report["unverifiable"] == [f'"{goal}" -- nobody can steer the frog to the goal']


def test_an_assertion_the_run_cannot_honour_is_thrown_away_instead_of_failed():
    """A step nobody runs, a symbol nothing reads, a baseline that comes later:
    no program on earth satisfies these, so judging them would fail every game
    equally and say "your program is wrong" about the examiner's own mistake."""
    steps = [{"id": "hold_left_a"}, {"id": "hold_right_a"}]
    exam = _exam(
        RuntimeAssertion(
            step="hold_jump_a", symbol="g_state", compare=EQUALS, value=1, mechanic=1, why="x"
        ),
        RuntimeAssertion(
            step="hold_left_a", symbol="g_lives", compare=AT_MOST, value=3, mechanic=1, why="x"
        ),
        RuntimeAssertion(
            step="hold_left_a",
            symbol="g_score",
            compare=AT_LEAST,
            baseline="hold_right_a",
            mechanic=1,
            why="x",
        ),
        RuntimeAssertion(
            step="hold_right_a", symbol="g_state", compare=EQUALS, mechanic=1, why="x"
        ),
    )

    kept, discarded = usable_assertions(exam, steps, ["g_score", "g_state"])

    assert kept == []
    assert [reason.split(":")[1].strip() for reason in discarded] == [
        "no step of this run is called 'hold_jump_a'",
        "this program does not expose g_lives",
        "its baseline hold_right_a does not run before it",
        "it names neither a value nor a baseline",
    ]


def test_a_symbol_that_was_expected_and_never_read_fails_its_step():
    """The abstention rule, at the level of one number: an absent reading that
    satisfied whatever was asked of it is how an unobserved run turns into an
    approved one."""
    step = {"id": "idle", "expect": {"g_state": {"compare": EQUALS, "value": 1}}}

    mismatches = step_mismatches(step, {"idle": {"g_score": 0}})

    assert mismatches == ["g_state: expected exactly 1, read nothing"]


def test_the_gate_abstains_when_neither_the_examiner_nor_the_design_offers_anything():
    """An examination that asserts nothing is not an examination that passed.
    Reading it as a pass is what let a program that draws one glyph and quits
    on a keypress be accepted on its first attempt. Nothing is derivable here
    either: this run never read `g_state`, so not even the title claim can be
    made."""
    stateless = [(step, {"g_score": read["g_score"]}) for step, read in FROG_READINGS]
    report = _service().acceptance_report(
        _project("Ganas al llegar a la meta."),
        _runtime(stateless),
        ScriptedExaminer(
            _exam(unverifiable=[UncheckableMechanic(mechanic=1, why="nobody reaches the goal")])
        ),
    )

    assert report["quality_pass"] is None
    assert report["observed"] is False
    assert report["reason"] == "the examiner found nothing this run could check"


def test_an_examiner_that_finds_nothing_still_leaves_the_title_claim_behind():
    """Three examinations in twenty of the five finished designs came back with
    no usable assertion at all, and the gate abstained on a run it had watched.
    The one claim two press-and-release cycles of the action key always prove
    is derived rather than asked for, so the run is judged even then."""
    report = _service().acceptance_report(
        _project("Ganas al llegar a la meta."),
        _runtime(FROG_READINGS),
        ScriptedExaminer(
            _exam(unverifiable=[UncheckableMechanic(mechanic=1, why="nobody reaches the goal")])
        ),
    )

    assert report["quality_pass"] is True
    judged = {step["id"]: step for step in report["scenarios"]}
    assert judged["hold_action_b"]["expect"]["g_state"] == {
        "compare": CHANGED,
        "value": STATE_TITLE,
        "why": judged["hold_action_b"]["expect"]["g_state"]["why"],
    }
    # Still nobody's mechanic: which sentence a symbol witnesses is a reading
    # of prose, and a derivation that guessed it would be the hardcoded gate
    # coming back through the door this module closed.
    assert report["unchecked_mechanics"] == ["Ganas al llegar a la meta."]


def test_an_examiner_that_breaks_leaves_the_gate_abstaining():
    """A model having a bad day must cost an unobserved run, not the write
    attempt it was called from."""

    class Broken:
        def examine(self, project, steps, symbols):
            raise RuntimeError("the model returned nothing")

    examination = runtime_examination(_project("Algo."), Broken(), symbols=["g_state"])

    assert examination.steps == []
    assert examination.asserted is False
    assert "the model returned nothing" in examination.reasons[0]


def test_one_design_is_examined_once_however_many_attempts_it_takes():
    """`write_program` verifies up to five attempts against the same design.
    Asking again each time would pay five times for one answer and could judge
    a repair against an exam the attempt before it never sat."""
    service = _service()
    project = _project("Cavar puntúa.")
    examiner = ScriptedExaminer(
        _exam(
            RuntimeAssertion(
                step="hold_left_a", symbol="g_state", compare=EQUALS, value=1, mechanic=0, why="x"
            )
        )
    )

    for _ in range(3):
        service.acceptance_report(project, _runtime(MINER_READINGS), examiner)

    assert examiner.calls == 1


def test_a_mechanic_the_examiner_called_unverifiable_stays_unchecked_even_if_it_asserted_one():
    """Recorded from the first real run of this prompt against
    `studio-projects/fase-uno-cpc`: the examiner declared its first mechanic
    unverifiable and bound an assertion to it in the same answer. A report that
    believed the assertion would claim more of the design was checked than the
    examiner itself believed."""
    gravity = "El explorador salta con SPACE y la gravedad lo devuelve a la cornisa."
    report = _service().acceptance_report(
        _project(gravity),
        _runtime(MINER_READINGS),
        ScriptedExaminer(
            _exam(
                RuntimeAssertion(
                    step="hold_action_a",
                    symbol="g_state",
                    compare=EQUALS,
                    value=1,
                    mechanic=1,
                    why="the action key starts the game",
                ),
                unverifiable=[
                    UncheckableMechanic(mechanic=1, why="nothing reads where the explorer is")
                ],
            )
        ),
    )

    assert report["quality_pass"] is True
    assert report["unchecked_mechanics"] == [gravity]


def test_every_comparison_the_examiner_may_answer_is_one_the_judge_implements():
    """The examiner's `compare` is a `Literal` because a JSON schema needs one,
    and `acceptance.COMPARISONS` is what judges it: two statements of the same
    fact, pinned the way `observation.SPECTRUM_KEYS` is pinned against
    `codegen.KEY_CODES`. A comparison the model may answer and the judge does
    not implement would be judged as equality without saying so."""
    answerable = get_args(RuntimeAssertion.model_fields["compare"].annotation)

    assert set(answerable) == set(COMPARISONS)


def test_the_examiner_is_offered_the_designs_own_symbols_in_the_designs_own_words():
    """A design's observable is the only symbol in the menu that can witness a
    rule of *this* game -- the other six are the same numbers in every game
    there is. Left unexplained it reads as "no stated meaning", which is a
    symbol no examiner will bind an assertion to, and the run goes on being
    judged entirely on g_score."""
    from llmz80.studio.runtime_exam import examination_prompt

    document = _project("Cavar tierra la convierte en suelo.").model_dump(mode="json")
    document["observables"] = [
        {"symbol": "g_dug", "width": 2, "meaning": "celdas de tierra excavadas; solo sube"}
    ]
    project = GameProject.model_validate(document)

    prompt = examination_prompt(project, observation_script(project), ["g_dug", "g_score"])

    assert "g_dug: celdas de tierra excavadas; solo sube (declared by this design)" in prompt
    assert "declared by this design" in prompt
    assert "g_score: current score" in prompt


#: `studio-projects/minero-observable/build/emulator_report.json`, the first
#: run in which a design's own observables were located and read: `g_dug`
#: counts dirt cells removed and `g_bat_turns` the times a bat turned round,
#: and the design's own words say each only ever rises.
OBSERVABLE_MINER_READINGS: list[tuple[str, dict[str, int]]] = [
    ("hold_action_a", {"g_bat_turns": 2, "g_dug": 0, "g_lives": 3, "g_score": 0, "g_state": 1}),
    ("hold_action_b", {"g_bat_turns": 11, "g_dug": 0, "g_lives": 3, "g_score": 0, "g_state": 1}),
    ("hold_left_a", {"g_bat_turns": 20, "g_dug": 0, "g_lives": 3, "g_score": 0, "g_state": 1}),
    ("hold_right_a", {"g_bat_turns": 27, "g_dug": 6, "g_lives": 3, "g_score": 10, "g_state": 1}),
    ("hold_up_a", {"g_bat_turns": 35, "g_dug": 15, "g_lives": 3, "g_score": 15, "g_state": 1}),
    ("hold_down_a", {"g_bat_turns": 45, "g_dug": 21, "g_lives": 2, "g_score": 24, "g_state": 1}),
    ("hold_left_b", {"g_bat_turns": 54, "g_dug": 28, "g_lives": 2, "g_score": 28, "g_state": 1}),
    ("hold_right_b", {"g_bat_turns": 62, "g_dug": 37, "g_lives": 2, "g_score": 41, "g_state": 3}),
    ("hold_up_b", {"g_bat_turns": 64, "g_dug": 41, "g_lives": 2, "g_score": 91, "g_state": 3}),
    ("hold_down_b", {"g_bat_turns": 64, "g_dug": 41, "g_lives": 2, "g_score": 91, "g_state": 3}),
    ("idle", {"g_bat_turns": 64, "g_dug": 41, "g_lives": 2, "g_score": 91, "g_state": 3}),
]


def _digger(*mechanics: str) -> GameProject:
    """`minero-observable`'s design, down to the sentence it wrote for `g_dug`."""
    document = _project(*mechanics).model_dump(mode="json")
    document["observables"] = [
        {
            "symbol": "g_dug",
            "width": 2,
            "meaning": "celdas de tierra excavadas desde el comienzo de la partida; solo sube",
        }
    ]
    return GameProject.model_validate(document)


def _assertion(step: str, symbol: str, compare: str, mechanic: int = 0, **target: Any):
    return RuntimeAssertion(
        step=step, symbol=symbol, compare=compare, mechanic=mechanic, why="x", **target
    )


def test_a_game_that_is_back_on_its_title_screen_in_two_seconds_fails_the_derived_claim():
    """`studio-projects/un-minero-que-cava-tuneles-y` spent its three lives and
    returned to its title while nothing but the action key was held. It was
    refused by the other gates and redesigned, and the examiner asserted
    nothing at all about it -- which is the run the derived title claim exists
    for."""
    burnt_out = [
        ("hold_action_a", {"g_score": 0, "g_state": 1}),
        ("hold_action_b", {"g_score": 0, "g_state": 0}),
        ("hold_left_a", {"g_score": 0, "g_state": 0}),
    ]
    report = _service().acceptance_report(
        _project("Perder las tres vidas termina la partida."),
        _runtime(burnt_out),
        ScriptedExaminer(_exam()),
    )

    assert report["quality_pass"] is False
    assert report["failures"] == ["hold_action_b"]


def test_a_claim_only_one_of_the_passes_made_is_still_kept_by_the_merge():
    """The union is the whole mechanism. Four examinations of one design left
    5, 5, 5 and 6 of its seven mechanics unchecked, so the pass that found a
    rule must not be outvoted by the two that did not think of it."""
    merged = merge_exams(
        [
            _exam(_assertion("hold_down_a", "g_score", AT_LEAST, 3, baseline="hold_left_a")),
            _exam(),
            _exam(_assertion("hold_action_b", "g_lives", AT_MOST, 4, baseline="hold_action_a")),
        ]
    )

    assert {(a.symbol, a.mechanic) for a in merged.assertions} == {("g_score", 3), ("g_lives", 4)}


def test_a_literal_number_about_a_counter_is_judged_only_when_two_passes_agree_on_it():
    """The union multiplies the chance of a single pass's bad claim being
    judged, and the one shape that can fail a correct program is a guess about
    how far the run got: `g_score at_least 1` fails the frog, whose score
    correctly never moves because nobody can walk it to the far kerb. A claim
    about `g_state` is not that shape -- its four values are the four screens
    -- and it is the claim this blind run is best at, so it stands alone."""
    lonely = _assertion("hold_left_a", "g_score", AT_LEAST, 1, value=1)
    shared = _assertion("hold_action_a", "g_state", EQUALS, 2, value=1)

    merged = merge_exams([_exam(lonely, shared), _exam(shared), _exam()])

    assert [(a.symbol, a.value) for a in merged.assertions] == [("g_state", 1)]


def test_a_counter_the_design_says_only_rises_is_asserted_without_asking_a_model():
    """`minero-observable` declares `g_dug` "solo sube" in its own words, which
    is a checkable claim the design has already made. Deriving it stops the
    coverage of a design's own observables depending on whether the examiner
    remembered the paragraph telling it to say so."""
    report = _service().acceptance_report(
        _digger("Cavar tierra la convierte en suelo."),
        _runtime(OBSERVABLE_MINER_READINGS),
        ScriptedExaminer(_exam()),
    )

    judged = {step["id"]: step for step in report["scenarios"]}
    assert judged["hold_action_b"]["expect"]["g_dug"]["compare"] == AT_LEAST
    assert judged["hold_action_b"]["expect"]["g_dug"]["baseline"] == "hold_action_a"
    assert report["quality_pass"] is True


def test_the_examiners_attribution_survives_a_derived_claim_that_says_the_same_thing():
    """Both the examiner and the derivation assert that `g_dug` has not fallen
    between the first two steps, but only the examiner can say which of the
    design's sentences that witnesses. Keeping the derived copy instead would
    take `minero-observable` from two of its seven mechanics checked back to
    none -- the coverage this whole change exists to hold steady."""
    digging = "Moverse contra la tierra la excava y la convierte en suelo."
    report = _service().acceptance_report(
        _digger(digging),
        _runtime(OBSERVABLE_MINER_READINGS),
        ScriptedExaminer(
            _exam(_assertion("hold_action_b", "g_dug", AT_LEAST, 1, baseline="hold_action_a"))
        ),
    )

    assert report["unchecked_mechanics"] == []
    assert report["quality_pass"] is True


def test_a_pass_that_declines_a_mechanic_it_also_asserted_loses_only_the_attribution():
    """`fase-uno-cpc`'s first examination declared a mechanic unverifiable and
    bound an assertion to it in the same answer, and the honest reading of a
    contradiction is the one claiming less. Across separate sittings there is
    no contradiction to resolve, so the pass that had no such doubt still
    attributes the claim -- and the claim itself is judged either way."""
    contradicted = _exam(
        _assertion("hold_action_a", "g_state", EQUALS, 1, value=1),
        unverifiable=[UncheckableMechanic(mechanic=1, why="nothing reads where the explorer is")],
    )
    confident = _exam(_assertion("hold_action_b", "g_state", EQUALS, 1, value=1))

    alone = merge_exams([contradicted, contradicted])
    together = merge_exams([contradicted, confident])

    assert [a.mechanic for a in alone.assertions] == [0]
    assert [item.mechanic for item in alone.unverifiable] == [1]
    assert sorted(a.mechanic for a in together.assertions) == [0, 1]
    assert together.unverifiable == []


def test_one_pass_surviving_is_enough_and_none_surviving_leaves_the_gate_abstaining():
    """A model having a bad day must cost an unobserved run rather than the
    write attempt it was called from, and that promise cannot be weakened by
    asking it three times: two failures out of three still leave an exam."""

    class Flaky:
        def __init__(self, answers):
            self.answers = list(answers)

        def examine(self, project, steps, symbols):
            answer = self.answers.pop()
            if isinstance(answer, Exception):
                raise answer
            return answer

    good = _exam(_assertion("hold_action_a", "g_state", EQUALS, 1, value=1))
    survived = RepeatedExaminer(Flaky([RuntimeError("no"), good, RuntimeError("no")]), passes=3)
    doomed = RepeatedExaminer(Flaky([RuntimeError("every pass failed")] * 2), passes=2)

    assert survived.examine(_project(), observation_script(_project()), ["g_state"]) == good
    examination = runtime_examination(_project("Algo."), doomed, symbols=["g_state"])
    assert examination.asserted is False
    assert "every pass failed" in examination.reasons[0]


def test_the_step_menu_names_a_step_by_the_id_an_assertion_must_use():
    """The menu used to number its lines, and the first examination of a design
    with observables of its own answered with `step="1. hold_action_a"` for
    every assertion it made. All five were discarded as naming steps that do
    not run, and a program whose two declared observables were being read
    correctly out of memory was judged by nothing at all."""
    from llmz80.studio.runtime_exam import _step_menu

    lines = _step_menu(observation_script(_project())).splitlines()

    assert lines[0].strip().startswith("hold_action_a --")
    assert not any(line.strip()[0].isdigit() for line in lines)
