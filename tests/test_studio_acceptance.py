"""What the runtime gate judges, and what it refuses to judge."""

from llmz80.studio.acceptance import design_prompt, generation_prompt, runtime_script
from llmz80.studio.models import GameProject, TargetPlatform
from llmz80.studio.samples import blank_project


def test_a_project_nobody_examined_gets_no_script_at_all():
    """No examiner, no steps, and `acceptance_report` abstains on the empty
    list -- the state this gate was deliberately left in when the hardcoded
    script was withdrawn, and the one it must fall back to."""
    assert runtime_script(blank_project("Quiet", TargetPlatform.SPECTRUM)) == []


def test_the_design_prompt_shows_the_declared_vocabulary():
    project = blank_project("Vocabulary", TargetPlatform.SPECTRUM)
    document = project.model_dump(mode="json")
    document["metadata"]["brief"] = "un explorador cruza salas de piedra"
    document["mechanics"] = ["SPACE salta y la gravedad devuelve al suelo"]
    document["entities"][0]["notes"] = "el que mueve el jugador"
    prompt = design_prompt(GameProject.model_validate(document))
    assert "un explorador cruza salas de piedra" in prompt
    assert "SPACE salta" in prompt
    assert "el que mueve el jugador" in prompt
    assert "actor" in prompt


def test_the_design_prompt_shows_the_tile_alphabet_the_design_coined():
    prompt = design_prompt(blank_project("Tiles", TargetPlatform.SPECTRUM))
    assert "'#' is wall" in prompt
    assert "'.' is floor" in prompt


def test_the_design_prompt_shows_a_tiles_traits_and_omits_them_when_there_are_none():
    prompt = design_prompt(blank_project("Traits", TargetPlatform.SPECTRUM))
    assert "'#' is wall [solid]" in prompt
    assert "'.' is floor [" not in prompt


def test_the_design_prompt_names_the_full_binding_lines():
    prompt = design_prompt(blank_project("Keys", TargetPlatform.SPECTRUM))
    # The line as a whole, not just a substring of it: a line containing only
    # "INPUT_LEFT" (with the key dropped) would also satisfy "O" in prompt,
    # since O turns up inside INPUT_DOWN and INPUT_ACTION too.
    assert f"  INPUT_{'LEFT':<12} key O" in prompt


def test_terrain_drawing_is_told_even_without_any_sprites():
    # The common case: a project starts with no sprites at all. Before this
    # was fixed, the plat_cell instruction lived inside `if sprites:` and a
    # design with none of them was never told how to draw its own screen.
    project = blank_project("Bare", TargetPlatform.SPECTRUM)
    assert project.assets == []

    prompt = design_prompt(project)

    assert "plat_cell" in prompt
    assert "plat_sprite" not in prompt


def test_the_design_prompt_lists_screens_and_where_they_lead():
    project = blank_project("Rooms", TargetPlatform.SPECTRUM)
    document = project.model_dump(mode="json")
    second = dict(document["screens"][0])
    second.update(id="screen_2", name="SCREEN 2", spawns=[], exits={"left": "screen_1"})
    document["screens"] = [dict(document["screens"][0], exits={"right": "screen_2"}), second]
    prompt = design_prompt(GameProject.model_validate(document))
    assert "screen_1" in prompt and "screen_2" in prompt
    assert "right -> screen_2" in prompt


def test_the_design_prompt_shows_a_screens_time_limit_only_when_declared():
    project = blank_project("Clock", TargetPlatform.SPECTRUM)
    document = project.model_dump(mode="json")
    document["screens"][0]["time_limit_seconds"] = 60
    timed = design_prompt(GameProject.model_validate(document))
    untimed = design_prompt(project)

    assert "time limit 60s" in timed
    assert "time limit" not in untimed


def test_the_design_prompt_shows_starting_positions_from_screen_spawns():
    prompt = design_prompt(blank_project("Spawns", TargetPlatform.SPECTRUM))

    assert "Starting positions (column, row):" in prompt
    assert "actor at (10, 7)" in prompt


def test_an_entitys_count_reads_as_a_per_screen_cap_not_a_headcount():
    project = blank_project("Cap", TargetPlatform.SPECTRUM)
    document = project.model_dump(mode="json")
    document["entities"][0]["count"] = 3
    capped = design_prompt(GameProject.model_validate(document))
    default = design_prompt(project)

    # "x3" would read as "there are three"; EntitySpec.count is the most a
    # screen may place, so it must say so explicitly.
    assert "at most 3 per screen" in capped
    # A count of 1 (the default) needs no caveat and must not print one.
    assert "at most 1 per screen" not in default
    assert "at most" not in default


def test_the_design_prompt_shows_an_entitys_poses_when_it_has_any():
    project = blank_project("Poses", TargetPlatform.SPECTRUM)
    document = project.model_dump(mode="json")
    document["entities"][0]["poses"] = ["walk", "jump"]
    prompt = design_prompt(GameProject.model_validate(document))

    assert "poses walk, jump" in prompt


def test_a_project_without_assets_gets_no_sprite_section():
    project = blank_project("NoArt", TargetPlatform.SPECTRUM)
    assert project.assets == []

    prompt = design_prompt(project)

    assert "SPRITE_" not in prompt
    assert "Use it or don't." in prompt


def test_a_project_with_a_blitter_sprite_makes_plat_sprite_mandatory():
    project = blank_project("Art", TargetPlatform.SPECTRUM)
    document = project.model_dump(mode="json")
    document["assets"] = [
        {
            "id": "hero",
            "kind": "sprite",
            "source": "assets/hero.png",
            "width": 32,
            "height": 16,
            "frames": 2,
        }
    ]
    document["entities"][0]["sprite"] = "hero"
    prompt = design_prompt(GameProject.model_validate(document))

    assert "SPRITE_HERO" in prompt
    assert "2 frames" in prompt
    assert "plat_cell" in prompt
    assert "plat_sprite" in prompt
    # The closing paragraph must not hand back the permission the compiler's
    # own gate revokes (compiler.py rejects a program with sprites that
    # never calls plat_sprite).
    assert "Use it or don't." not in prompt
    assert "mandatory" in prompt


def test_a_sprites_frame_count_of_one_reads_as_singular():
    project = blank_project("OneFrame", TargetPlatform.SPECTRUM)
    document = project.model_dump(mode="json")
    document["assets"] = [
        {
            "id": "hero",
            "kind": "sprite",
            "source": "assets/hero.png",
            "width": 16,
            "height": 16,
            "frames": 1,
        }
    ]
    document["entities"][0]["sprite"] = "hero"
    prompt = design_prompt(GameProject.model_validate(document))

    assert "1 frame," in prompt
    assert "1 frames" not in prompt


def test_the_design_prompt_makes_an_observable_the_programs_obligation():
    """game_state.h declares a design's observables `extern` and nothing else
    in this prompt ever said who defines them, which reads as "Studio provides
    these". A program that leaves one undefined now fails its build."""
    project = blank_project("State", TargetPlatform.SPECTRUM)
    document = project.model_dump(mode="json")
    document["observables"] = [{"symbol": "g_keys", "meaning": "keys collected so far"}]
    prompt = design_prompt(GameProject.model_validate(document))

    assert "unsigned char g_keys;  keys collected so far" in prompt
    assert "your program must define it exactly once at file scope" in prompt


def test_the_design_prompt_shows_audio_effects():
    project = blank_project("Sound", TargetPlatform.SPECTRUM)
    document = project.model_dump(mode="json")
    document["audio"] = {"music": False, "effects": ["jump", "coin"]}
    prompt = design_prompt(GameProject.model_validate(document))

    assert "plat_sound" in prompt
    assert "jump" in prompt and "coin" in prompt


def test_the_design_prompt_lists_the_scene_graph_and_where_it_starts():
    # blank_project already ships a real scene graph (title -> game ->
    # game_over -> title), so no fixture needs to be built for this.
    prompt = design_prompt(blank_project("Flow", TargetPlatform.SPECTRUM))

    assert "starting at title" in prompt
    assert "title (title)" in prompt
    assert '"START" -> game' in prompt
    assert "game (gameplay)" in prompt
    assert "-> game_over" in prompt


def test_a_design_with_no_mechanics_and_no_brief_is_told_not_to_invent_rules():
    project = blank_project("Silent", TargetPlatform.SPECTRUM)
    assert project.mechanics == []
    assert project.metadata.brief == ""

    prompt = design_prompt(project)

    assert "declares no mechanics at all" in prompt
    assert "do not invent a win or lose condition" in prompt


def test_a_brief_softens_the_no_mechanics_warning_without_dropping_it():
    project = blank_project("Moody", TargetPlatform.SPECTRUM)
    document = project.model_dump(mode="json")
    document["metadata"]["brief"] = "un explorador cruza salas de piedra"
    prompt = design_prompt(GameProject.model_validate(document))

    # Not the no-brief wording...
    assert "declares no mechanics at all" not in prompt
    # ...but the instruction is still there, softened, not dropped.
    assert "sets mood, not rules" in prompt
    assert "do not invent a win or lose condition" in prompt


def test_declared_mechanics_suppress_the_no_mechanics_warning():
    project = blank_project("Ruled", TargetPlatform.SPECTRUM)
    document = project.model_dump(mode="json")
    document["mechanics"] = ["SPACE salta"]
    prompt = design_prompt(GameProject.model_validate(document))

    assert "do not invent a win or lose condition" not in prompt
    assert "SPACE salta" in prompt


def test_the_generation_prompt_carries_the_state_contract_and_the_design():
    project = blank_project("Contract", TargetPlatform.SPECTRUM)
    prompt = generation_prompt(project)

    assert "OBSERVABLE STATE CONTRACT" in prompt
    assert "g_score" in prompt
    # A generation_prompt that dropped half the design would still pass a
    # contract-only assertion; this pins the design side too.
    assert "Terrain characters" in prompt
    assert project.metadata.title in prompt


def test_the_pellet_derivation_is_gone():
    import llmz80.studio.acceptance as acceptance

    for name in (
        "derive_scenarios",
        "sweep_frames",
        "chase_catch_frames",
        "FRAMES_PER_CELL",
        "with_executable_scenarios",
    ):
        assert not hasattr(acceptance, name), f"{name} survives"


def _with_tile_art(project: GameProject) -> GameProject:
    """The design with 8x8 artwork registered for its first tile."""
    document = project.model_dump(mode="json")
    document["assets"] = [
        {
            "id": "brickwork",
            "kind": "tileset",
            "source": "assets/brickwork.png",
            "width": 8,
            "height": 8,
            "frames": 1,
        }
    ]
    document["tiles"][0]["id"] = "ladrillo"
    document["tiles"][0]["art"] = "brickwork"
    document["screens"][0]["tiles"] = [
        row.replace(project.tiles[0].char, document["tiles"][0]["char"])
        for row in document["screens"][0]["tiles"]
    ]
    return GameProject.model_validate(document)


def test_a_tile_with_artwork_is_advertised_as_its_own_constant():
    prompt = design_prompt(_with_tile_art(blank_project("Terrain", TargetPlatform.SPECTRUM)))

    assert "TILE_LADRILLO" in prompt
    assert "plat_tile" in prompt


def test_terrain_artwork_makes_plat_tile_mandatory_not_optional():
    """Same rule sprites already carry, for the same reason: `compiler.
    tile_usage_errors` refuses a program that packs terrain art and draws its
    terrain with a letter anyway, so the prompt must not read as a choice."""
    prompt = design_prompt(_with_tile_art(blank_project("Terrain", TargetPlatform.SPECTRUM)))

    assert "Use it or don't." not in prompt
    assert "mandatory" in prompt


def test_a_design_whose_tiles_are_all_characters_is_never_told_about_plat_tile():
    project = blank_project("Bare", TargetPlatform.SPECTRUM)

    prompt = design_prompt(project)

    assert "plat_tile" not in prompt
    assert "TILE_" not in prompt


def test_the_prompt_states_the_footprint_a_sprite_covers():
    """The real defect this closes: a finished program drew its 16x16 bat at
    two adjacent columns, so the same sprite overlapped itself by eight
    pixels and the bat came out looking like a dumbbell. Nothing in the
    prompt had said a sprite is two cells wide."""
    project = blank_project("Art", TargetPlatform.SPECTRUM)
    document = project.model_dump(mode="json")
    document["assets"] = [
        {
            "id": "hero",
            "kind": "sprite",
            "source": "assets/hero.png",
            "width": 16,
            "height": 16,
            "frames": 1,
        }
    ]
    document["entities"][0]["sprite"] = "hero"

    prompt = design_prompt(GameProject.model_validate(document))

    assert "2x2 character cells" in prompt
    assert "at least two columns and two rows apart" in prompt


def test_a_declared_colour_is_offered_to_the_writer_by_name():
    """`plat_ink(COLOUR_<ID>)` is how a program colours the cells and text it
    draws itself; a palette nobody is told about is a palette nobody uses."""
    from llmz80.studio.models import PaletteEntry

    project = blank_project("Coloured", TargetPlatform.SPECTRUM)
    project.presentation.palette = [PaletteEntry(id="ladrillo_cyan", colour="cian")]

    prompt = design_prompt(project)

    assert "COLOUR_LADRILLO_CYAN" in prompt
    assert "plat_ink" in prompt


def test_a_design_with_no_palette_is_told_nothing_about_colour():
    project = blank_project("Plain", TargetPlatform.SPECTRUM)
    assert project.presentation.palette == []

    prompt = design_prompt(project)

    assert "COLOUR_" not in prompt


def test_terrain_artwork_comes_with_the_warning_that_redrawing_it_costs_frames():
    """Terrain art made a cheap mistake expensive. A screen of brickwork is a
    hundred cells, each one eight bytes and an attribute, and a program that
    repaints all of it every frame overruns its display frame -- which is what
    the pacing gate then reads back out of the machine, four frames late, with
    no idea that the terrain was the reason. Cheaper to say it here than to
    spend an attempt of the repair loop learning it."""
    project = _with_tile_art(blank_project("Terrain", TargetPlatform.SPECTRUM))

    prompt = design_prompt(project)

    assert "Draw each cell once" in prompt
    assert "when that cell changes" in prompt
    assert "overruns the display frame" in prompt


def test_a_design_that_animates_is_told_the_frame_has_to_move():
    """`g_anim_frame` is in the state contract with its rule attached, and the
    runtime gate reads it directly -- but the contract states what the symbol
    means, not that drawing an actor is the moment to advance it. Three
    attempts of one run failed this gate with the sprite drawn correctly and
    the counter never touched."""
    project = blank_project("Art", TargetPlatform.SPECTRUM)
    document = project.model_dump(mode="json")
    document["assets"] = [
        {
            "id": "hero",
            "kind": "sprite",
            "source": "assets/hero.png",
            "width": 64,
            "height": 16,
            "frames": 4,
        }
    ]
    document["entities"][0]["sprite"] = "hero"

    prompt = design_prompt(GameProject.model_validate(document))

    assert "g_anim_frame" in prompt


def test_the_writer_is_told_to_restart_the_frame_measurement_after_startup_work():
    """Ten program attempts across two runs were failed by the pacing gate for
    a gap left by work before the game loop -- painting a screen, waiting on a
    title -- which `plat_wait_frame` charges to the loop's first iteration and
    keeps as a maximum for the rest of the session. `plat_frame_baseline` ends
    that, but only if the program calls it, so the prompt has to say when."""
    project = blank_project("Paced", TargetPlatform.SPECTRUM)

    prompt = design_prompt(project)

    assert "plat_frame_baseline" in prompt
