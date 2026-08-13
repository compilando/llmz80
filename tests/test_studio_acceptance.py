import pytest

from llmz80.core.state_contract import (
    REQUIRED_SYMBOLS,
    STATE_PLAYING,
    STATE_CONTRACT,
    contract_prompt,
)
from llmz80.studio.acceptance import (
    derive_scenarios,
    design_prompt,
    generation_prompt,
    runtime_script,
    scenarios_prompt,
    with_executable_scenarios,
)
from llmz80.studio import editing
from llmz80.studio.editing import set_entity_behaviour
from llmz80.studio.feel import animation_report
from llmz80.studio.models import AcceptanceScenario, TargetPlatform
from llmz80.studio.samples import blank_project
from llmz80.studio.services import StudioService


@pytest.fixture
def project():
    return blank_project("Contract", TargetPlatform.SPECTRUM)


def test_the_contract_prompt_names_every_symbol_and_its_type():
    prompt = contract_prompt()

    for symbol in STATE_CONTRACT:
        assert symbol.name in prompt
        assert symbol.meaning in prompt
    assert "unsigned int g_score;" in prompt
    assert "unsigned char g_lives;" in prompt
    # The two rules that cost real build failures to learn.
    assert "static" in prompt
    assert "data segment" in prompt


def test_required_symbols_are_the_ones_a_playable_design_cannot_omit():
    assert set(REQUIRED_SYMBOLS) == {"g_score", "g_lives", "g_level", "g_state"}


def test_default_projects_ship_runnable_acceptance(project):
    # The default maze_chase pack's enemy behaviour is "chase" (see
    # resources/genres.yml), so all three core criteria are runnable, not
    # just the first two.
    executable = [scenario for scenario in project.acceptance if scenario.executable]

    assert [scenario.id for scenario in executable] == [
        "start_game",
        "collect_scores",
        "enemy_costs_life",
    ]
    start = executable[0]
    assert start.hold == "action"
    assert start.expect["g_state"] == STATE_PLAYING
    collect = executable[1]
    assert collect.expect["g_score"] == project.gameplay.score_per_collectible
    assert collect.expect["g_remaining"] == 7
    enemy = executable[2]
    assert enemy.hold == "none"
    assert enemy.expect["g_lives"] == project.gameplay.lives - 1
    assert enemy.expect["g_state"] == STATE_PLAYING


def test_a_criterion_the_design_cannot_predict_stays_prose(project):
    # Chase is predictable and is covered by
    # test_a_chasing_enemy_makes_losing_a_life_executable; guard is not a
    # chaser and stays unpredictable exactly like a patrol.
    edited = editing.set_entity_behaviour(project, "enemy", "guard")

    enemy = next(s for s in derive_scenarios(edited) if s.id == "enemy_costs_life")

    assert enemy.executable is False
    assert enemy.then  # the prose is still there for a reader


def test_a_chasing_enemy_makes_losing_a_life_executable():
    project = blank_project("Chase", TargetPlatform.SPECTRUM)

    scenario = next(s for s in derive_scenarios(project) if s.id == "enemy_costs_life")

    assert scenario.executable
    assert scenario.hold == "none"
    assert scenario.expect["g_lives"] == project.gameplay.lives - 1
    assert scenario.expect["g_state"] == STATE_PLAYING


def test_a_design_with_no_chasing_enemy_leaves_it_as_prose():
    """A patrolling enemy's position depends on where it wandered; that is not predictable."""
    project = blank_project("Patrol", TargetPlatform.SPECTRUM)
    project = editing.set_entity_behaviour(project, "enemy", "patrol_h")

    scenario = next(s for s in derive_scenarios(project) if s.id == "enemy_costs_life")

    assert not scenario.executable


def test_the_script_keeps_the_designs_order(project):
    steps = runtime_script(project)

    # The two animation-probe steps always land last -- see
    # test_the_animation_probes_come_after_every_core_step below for why
    # that position is asserted, not assumed.
    assert [step["id"] for step in steps] == [
        "start_game",
        "collect_scores",
        "enemy_costs_life",
        "anim_probe_move",
        "anim_probe_idle",
    ]
    assert steps[0]["frames"] > 0


def test_the_script_enforces_scoring_before_dying_even_if_the_design_lists_it_first():
    """`enemy_costs_life` costs a life; `collect_scores` assumes none has been

    lost yet. `runtime_script` accumulates in one boot without resetting, so
    if a design listed the criteria in the other order the emulator would
    check "no life lost" only after one already was. This is the actual
    enforcement point, not the pack's authoring order.
    """
    project = blank_project("Reordered", TargetPlatform.SPECTRUM)
    document = project.model_dump(mode="json")
    document["acceptance"] = list(reversed(document["acceptance"]))
    reordered = type(project).model_validate(document)

    steps = runtime_script(reordered)

    assert [step["id"] for step in steps] == [
        "start_game",
        "collect_scores",
        "enemy_costs_life",
        "anim_probe_move",
        "anim_probe_idle",
    ]


def test_the_animation_probes_come_after_every_core_step(project):
    """The probes move the player and then wait; if they ran before
    `collect_scores` or `enemy_costs_life`, they would change the state
    those steps' `expect` values assume (score, remaining, lives). Asserted
    from the script's actual order and from `collect_scores`'s own expected
    values surviving untouched, not merely from where the code that builds
    the script happens to append them.
    """
    steps = runtime_script(project)

    ids = [step["id"] for step in steps]
    assert ids.index("anim_probe_move") > ids.index("enemy_costs_life")
    assert ids.index("anim_probe_idle") > ids.index("anim_probe_move")

    collect_alone = next(s for s in derive_scenarios(project) if s.id == "collect_scores")
    collect_in_script = next(step for step in steps if step["id"] == "collect_scores")
    assert collect_in_script["expect"] == collect_alone.expect
    assert collect_in_script["hold"] == collect_alone.hold
    assert collect_in_script["frames"] == collect_alone.frames


def test_a_design_without_a_chasing_enemy_still_gets_two_moving_and_one_waiting_step():
    """The animation gate needs two readings it can classify "moving" and at
    least one it can classify "idle" (see `feel.animation_report`). Before
    the probe steps existed, only a chasing enemy's `enemy_costs_life` ever
    supplied a waiting step, and `collect_scores` alone is a single moving
    reading with nothing to compare it to -- so a design whose enemies patrol,
    bounce, or guard (or that has no enemy at all) could never pass the gate,
    however well it animated. This is the actual fix for that: the probes are
    unconditional, not dependent on any enemy's behaviour.
    """
    project = blank_project("Patrol", TargetPlatform.SPECTRUM)
    patrol = with_executable_scenarios(editing.set_entity_behaviour(project, "enemy", "patrol_h"))
    # enemy_costs_life stays prose for a patrol -- confirms this design really
    # is the case the old script could never satisfy.
    assert not next(s for s in patrol.acceptance if s.id == "enemy_costs_life").executable

    steps = runtime_script(patrol)

    moving = [step for step in steps if step["hold"] in {"left", "right", "up", "down"}]
    waiting = [step for step in steps if step["hold"] == "none"]
    assert len(moving) >= 2
    assert len(waiting) >= 1


def test_the_prompt_states_the_checks_and_the_controls(project):
    prompt = scenarios_prompt(project)

    assert "hold action for 30 frames" in prompt
    assert "g_score == 10" in prompt
    assert "action = SPACE" in prompt
    assert prompt in generation_prompt(project)


def test_the_prompt_tells_the_writer_how_the_animation_frame_is_judged(project):
    # The contract sentence (in contract_prompt) says the symbol must advance
    # while moving and hold still while idle; this checks the acceptance
    # section separately says *how that gets checked*: readings compared
    # between steps, not repeating the contract's own wording.
    prompt = scenarios_prompt(project)

    assert "g_anim_frame" in prompt
    assert "changed" in prompt or "differ" in prompt
    assert "stayed the same" in prompt or "unchanged" in prompt
    # The contract sentence itself belongs in contract_prompt, not here.
    assert "currently drawn with" not in prompt


def test_the_animation_expectation_does_not_depend_on_target(project):
    # feel.py's animation gate only ever gets a memory reading through the
    # Spectrum's zesarux adapter today (the CPC adapter captures screenshots,
    # not memory), but that is a fact about which checker is wired up, not
    # about what a correct CPC program looks like -- so the instruction must
    # not vanish for a CPC target.
    cpc_project = blank_project("Contract", TargetPlatform.AMSTRAD_CPC)

    assert "g_anim_frame" in scenarios_prompt(cpc_project)


def test_a_none_hold_reads_as_waiting_not_as_a_keypress(project):
    scenario = next(s for s in project.acceptance if s.id == "enemy_costs_life")
    assert scenario.hold == "none"  # the default maze_chase pack chases

    prompt = scenarios_prompt(project)

    assert "hold none" not in prompt
    assert "without pressing anything" in prompt


def test_a_design_with_no_chasing_enemy_still_gets_a_waiting_step_in_the_prompt(project):
    """Before the animation probes existed, a patrol enemy left the script
    with no waiting step at all, and the prompt said so explicitly. Now the
    probes supply one unconditionally, so the writer is told about it exactly
    as it would be for a chaser -- this is the prompt-visible half of the fix
    for the defect a real run exposed (see acceptance.py's
    `_animation_probe_steps`).
    """
    patrol = editing.set_entity_behaviour(project, "enemy", "patrol_h")
    patrol = with_executable_scenarios(patrol)

    prompt = scenarios_prompt(patrol)

    assert "without pressing anything" in prompt
    # start_game, collect_scores, anim_probe_move, anim_probe_idle: four steps.
    assert "  4." in prompt
    assert "  5." not in prompt


def test_the_animation_gate_reaches_a_verdict_for_a_design_with_no_chaser():
    """The whole point of the probe steps: given plausible readings, the gate
    that used to abstain for lack of evidence (see the docstring above) now
    reaches a definite verdict, for a design that has no chasing enemy at
    all -- exactly the shape the real run's project (`platform_single_screen`,
    patrolling enemies) had.
    """
    project = blank_project("Patrol", TargetPlatform.SPECTRUM)
    patrol = with_executable_scenarios(editing.set_entity_behaviour(project, "enemy", "patrol_h"))
    steps = runtime_script(patrol)

    # A frame that genuinely advances while moving and holds while idle.
    value = 0
    readings = []
    for step in steps:
        if step["hold"] in {"left", "right", "up", "down"}:
            value += 1
        readings.append({"id": step["id"], "hold": step["hold"], "read": {"g_anim_frame": value}})

    report = animation_report({"step_readings": readings})

    assert report["observed"] is True
    assert report["quality_pass"] is True
    assert report["failures"] == []


def test_a_design_without_runnable_criteria_produces_no_script(project):
    document = project.model_dump(mode="json")
    for scenario in document["acceptance"]:
        scenario["hold"] = None
        scenario["expect"] = {}
    bare = type(project).model_validate(document)

    assert runtime_script(bare) == []
    assert scenarios_prompt(bare) == ""


def test_deriving_scenarios_is_idempotent(project):
    again = with_executable_scenarios(project)

    assert [s.model_dump() for s in again.acceptance] == [
        s.model_dump() for s in project.acceptance
    ]


def test_a_step_whose_reading_contradicts_the_design_fails(tmp_path, project):
    service = StudioService.at(tmp_path)
    runtime = {
        "step_readings": [
            {"id": "start_game", "read": {"g_state": 1, "g_level": 1, "g_score": 0}},
            {"id": "collect_scores", "read": {"g_score": 0, "g_remaining": 8}},
            {
                "id": "enemy_costs_life",
                "read": {"g_lives": project.gameplay.lives - 1, "g_state": STATE_PLAYING},
            },
        ]
    }

    report = service.acceptance_report(project, runtime)

    assert report["quality_pass"] is False
    assert report["failures"] == ["collect_scores"]
    failed = next(item for item in report["scenarios"] if item["id"] == "collect_scores")
    assert "g_score: expected 10, read 0" in failed["mismatches"]


def test_every_step_matching_passes(tmp_path, project):
    service = StudioService.at(tmp_path)
    runtime = {
        "step_readings": [
            {"id": step["id"], "read": dict(step["expect"])}
            for step in runtime_script(project)
        ]
    }

    report = service.acceptance_report(project, runtime)

    assert report["quality_pass"] is True
    assert report["failures"] == []


def test_a_target_without_readings_abstains(tmp_path, project):
    service = StudioService.at(tmp_path)

    report = service.acceptance_report(project, {"step_readings": []})

    assert report["observed"] is False
    assert report["quality_pass"] is None
    assert "no memory probe adapter" in report["reason"]


def test_a_scenario_expecting_an_unknown_symbol_is_refused():
    with pytest.raises(ValueError, match="outside the state contract"):
        AcceptanceScenario(
            id="bogus",
            given="a",
            when="b",
            then="c",
            hold="down",
            expect={"g_not_a_symbol": 1},
        )


def test_the_design_prompt_carries_the_map_and_the_entities(project):
    prompt = design_prompt(project)

    assert "Level level_1" in prompt
    assert "####################" in prompt
    assert "'#' is wall, '.' is floor" in prompt
    for entity in project.entities:
        assert f"{entity.id}: {entity.role} x{entity.count}" in prompt
    assert "player at (" in prompt
    assert f"Points per collectible: {project.gameplay.score_per_collectible}" in prompt


def test_the_generation_prompt_is_contract_design_and_acceptance(project):
    prompt = generation_prompt(project)

    assert prompt.index("OBSERVABLE STATE CONTRACT") < prompt.index("DESIGN")
    assert prompt.index("DESIGN") < prompt.index("RUNTIME ACCEPTANCE")


def test_a_designed_behaviour_reaches_the_prompt(project):
    edited = set_entity_behaviour(project, "enemy", "bounce")

    assert "moves bounce" in design_prompt(edited)
    assert "moves bounce" not in design_prompt(project)


def test_sweep_frames_follow_the_declared_speed(project):
    from llmz80.studio.acceptance import frames_per_cell, sweep_frames

    assert frames_per_cell(1) == 4
    assert frames_per_cell(4) == 1
    slow = sweep_frames(project, {"distance": 10})
    fast = sweep_frames(
        type(project).model_validate(
            {
                **project.model_dump(mode="json"),
                "entities": [
                    {**e, "speed": 4} if e["role"] == "player" else e
                    for e in project.model_dump(mode="json")["entities"]
                ],
            }
        ),
        {"distance": 10},
    )
    assert slow > fast


def test_the_prompt_states_the_movement_pace(project):
    prompt = design_prompt(project)

    assert "one cell every 4 frames" in prompt
    assert "Speed is a pace, not a distance" in prompt


def _with_assets(project, assets: list[dict]):
    document = project.model_dump(mode="json")
    document["assets"] = assets
    return type(project).model_validate(document)


def test_a_project_without_assets_gets_no_sprite_section(project):
    assert project.assets == []

    prompt = design_prompt(project)

    assert "SPRITE_" not in prompt
    assert "plat_sprite" not in prompt


def test_a_project_with_sprite_assets_gets_the_sprite_section(project):
    # "hero" is the id the player entity's `sprite` field already names (see
    # packs.py); a 32x16 sheet at two frames of 16x16 each is exactly what the
    # blitter packs, so this asset earns a SPRITE_<ID> constant.
    with_art = _with_assets(
        project,
        [{"id": "hero", "kind": "sprite", "source": "assets/hero.png", "width": 32, "height": 16, "frames": 2}],
    )

    prompt = design_prompt(with_art)

    assert "SPRITE_HERO" in prompt
    assert "2 frames" in prompt
    assert "plat_sprite" in prompt
    assert "plat_cell" in prompt


def test_the_prompt_states_which_entity_wears_a_matching_sprite(project):
    player = next(entity for entity in project.entities if entity.role == "player")
    assert player.sprite == "hero"
    with_art = _with_assets(
        project,
        [{"id": "hero", "kind": "sprite", "source": "assets/hero.png", "width": 16, "height": 16, "frames": 1}],
    )

    prompt = design_prompt(with_art)

    # The sprite's own line names the entity that wears it, not just its
    # existence: check the two appear together, not merely both in the prompt.
    hero_lines = [line for line in prompt.splitlines() if "SPRITE_HERO" in line]
    assert len(hero_lines) == 1
    assert player.id in hero_lines[0]


def test_a_sprite_no_entity_names_claims_no_wearer(project):
    # No entity in the default project has sprite == "cape", so the prompt must
    # not invent a binding for it -- an unsupported claim here is worse than
    # silence, per the same rule the reference dossier follows.
    assert not any(entity.sprite == "cape" for entity in project.entities)
    with_art = _with_assets(
        project,
        [{"id": "cape", "kind": "sprite", "source": "assets/cape.png", "width": 16, "height": 16, "frames": 1}],
    )

    prompt = design_prompt(with_art)

    cape_lines = [line for line in prompt.splitlines() if "SPRITE_CAPE" in line]
    assert len(cape_lines) == 1
    assert "worn by" not in cape_lines[0]
    for entity in with_art.entities:
        assert entity.id not in cape_lines[0]


def test_an_asset_shaped_wrong_for_the_blitter_is_left_out(project):
    # Only a sprite-kind asset whose frames are exactly the blitter's 16x16 gets
    # packed into sprites.h (see compiler.py); anything else falls back to a
    # plain asset import and has no SPRITE_<ID>, so the prompt must not claim one.
    with_art = _with_assets(
        project,
        [
            {
                "id": "banner",
                "kind": "sprite",
                "source": "assets/banner.png",
                "width": 32,
                "height": 32,
                "frames": 1,
            },
            {
                "id": "backdrop",
                "kind": "screen",
                "source": "assets/backdrop.png",
                "width": 16,
                "height": 16,
                "frames": 1,
            },
        ],
    )

    prompt = design_prompt(with_art)

    assert "SPRITE_BANNER" not in prompt
    assert "SPRITE_BACKDROP" not in prompt
