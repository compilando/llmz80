from llmz80.studio.editing import set_audio
from llmz80.studio.models import GenreId, TargetPlatform
from llmz80.studio.packs import create_default_project
from llmz80.studio.quality import design_quality_report, studio_quality_report
from llmz80.studio.solvability import solvability_report


def _neighbours(cell):
    col, row = cell
    return [(col + 1, row), (col - 1, row), (col, row + 1), (col, row - 1)]


def _isolated_collectible(project):
    """A collectible whose neighbours hold no other spawn.

    Walling a cell that holds a spawn is refused by the model, so a test that
    seals a collectible in has to pick one with room around it.
    """
    occupied = {(s.col, s.row) for s in project.levels[0].spawns}
    roles = {e.id: e.role for e in project.entities}
    for spawn in project.levels[0].spawns:
        if roles.get(spawn.entity) != "collectible":
            continue
        cell = (spawn.col, spawn.row)
        if not any(n in occupied for n in _neighbours(cell)):
            return cell
    raise AssertionError("every collectible has a neighbour that is occupied")


def test_builtin_design_passes_commercial_design_gates():
    project = create_default_project("Quality", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)

    report = design_quality_report(project)

    assert report["quality_pass"] is True
    assert all(report["checks"].values())


def test_unachievable_score_is_rejected():
    project = create_default_project("Impossible", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    project.gameplay.win_score = 9999

    report = design_quality_report(project)

    assert report["quality_pass"] is False
    assert "win_score_is_achievable" in report["failures"]


def test_release_gate_requires_design_build_and_runtime_evidence():
    project = create_default_project("Release", TargetPlatform.AMSTRAD_CPC, GenreId.MAZE_CHASE)
    passed = {"quality_pass": True}

    assert studio_quality_report(project, build=passed, runtime=passed)["quality_pass"] is True
    assert studio_quality_report(project, build=passed)["quality_pass"] is False


def _wall_off(project, level_index, cells):
    """Return a copy whose terrain seals `cells` behind walls."""
    document = project.model_dump(mode="json")
    level = document["levels"][level_index]
    rows = [list(row) for row in level["tiles"]]
    for col, row in cells:
        rows[row][col] = "#"
    level["tiles"] = ["".join(row) for row in rows]
    return type(project).model_validate(document)


def test_default_projects_are_solvable():
    for platform in TargetPlatform:
        for genre in GenreId:
            project = create_default_project("Solvable", platform, genre)

            report = solvability_report(project)

            assert report.solvable, report.failures
            for level in report.levels:
                assert level.reachable_floor == level.total_floor
                assert level.minimum_steps > 0
                assert level.estimated_steps >= level.minimum_steps


def test_a_collectible_sealed_behind_walls_fails_the_design_gate():
    project = create_default_project("Sealed", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    target = _isolated_collectible(project)
    # Wall in every orthogonal neighbour of one collectible, leaving it stranded.
    sealed = _wall_off(project, 0, _neighbours(target))

    report = design_quality_report(sealed)

    assert report["checks"]["every_level_is_solvable"] is False
    assert "every_level_is_solvable" in report["failures"]
    assert any("seal off" in reason for reason in report["solvability_failures"])
    assert report["quality_pass"] is False


def _serpentine_level(project, entities_by_role):
    """A single-corridor level long enough to exhaust a minimum time limit."""
    width, height = 40, 25
    rows = []
    for row in range(height):
        if row % 2 == 0:
            rows.append("." * width)
        else:
            gap = width - 1 if (row // 2) % 2 == 0 else 0
            rows.append("".join("." if col == gap else "#" for col in range(width)))

    corridor = [(col, row) for row in range(0, height, 2) for col in range(width)]
    spawns = [{"entity": entities_by_role["player"], "col": 0, "row": 0}]
    # One spawn per declared instance, whatever the typology asked for.
    for offset, _ in enumerate(range(entities_by_role["enemy_count"])):
        spawns.append({"entity": entities_by_role["enemy"], "col": 5 + offset, "row": 0})
    # The last collectible sits at the far end of the corridor.
    picks = [corridor[-1]] + corridor[10:17]
    for col, row in picks:
        spawns.append({"entity": entities_by_role["collectible"], "col": col, "row": row})

    document = project.model_dump(mode="json")
    level = document["levels"][0]
    level["width"] = width
    level["height"] = height
    level["tiles"] = rows
    level["spawns"] = spawns
    return document


def test_an_impossible_time_limit_fails_the_design_gate():
    project = create_default_project("Rushed", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    by_role = {entity.role: entity.id for entity in project.entities}
    by_role["enemy_count"] = next(e.count for e in project.entities if e.role == "enemy")
    document = _serpentine_level(project, by_role)

    document["levels"][0]["time_limit_seconds"] = 999
    generous = type(project).model_validate(document)
    analysis = solvability_report(generous).levels[0]
    assert analysis.minimum_steps > 500, analysis.minimum_steps
    assert design_quality_report(generous)["checks"]["every_level_is_solvable"] is True

    # 10 seconds is 500 player steps at one cell per 50 Hz frame.
    document["levels"][0]["time_limit_seconds"] = 10
    rushed = type(project).model_validate(document)

    report = design_quality_report(rushed)

    assert report["checks"]["every_level_is_solvable"] is False
    assert any("allows 500 steps" in reason for reason in report["solvability_failures"])
    assert report["quality_pass"] is False


def test_passing_build_and_runtime_cannot_release_an_unsolvable_design():
    project = create_default_project("Sealed", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    target = _isolated_collectible(project)
    sealed = _wall_off(project, 0, _neighbours(target))

    report = studio_quality_report(
        sealed, build={"quality_pass": True}, runtime={"quality_pass": True}
    )

    assert report["gates"] == {"design": False, "build": True, "runtime": True}
    assert report["quality_pass"] is False


def test_spectrum_effects_are_supported_but_music_is_not():
    project = create_default_project("Beeper", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)

    assert design_quality_report(project)["checks"]["audio_is_supported_by_target"] is True

    with_music = set_audio(project, music=True)
    report = design_quality_report(with_music)

    assert report["checks"]["audio_is_supported_by_target"] is False
    assert any("cannot play music" in gap for gap in report["audio_gaps"])
    assert report["quality_pass"] is False


def test_cpc_projects_start_silent_and_refuse_effects_by_name():
    project = create_default_project("Silent", TargetPlatform.AMSTRAD_CPC, GenreId.MAZE_CHASE)

    assert project.audio.effects == []
    assert design_quality_report(project)["quality_pass"] is True

    noisy = set_audio(project, effects=["collect"])
    report = design_quality_report(noisy)

    assert report["checks"]["audio_is_supported_by_target"] is False
    assert any("cannot play sound effects" in gap for gap in report["audio_gaps"])


def _swap_level_content(project, i, j):
    """Return a copy with levels `i` and `j`'s terrain and spawns exchanged.

    A level's identity (id, name) stays put; only what makes it harder or
    easier -- its grid and spawns -- moves. Every level still places exactly
    `entity.count` of every entity (the swap just relocates which level holds
    which content), so `validate_contract` stays satisfied while the route
    lengths `difficulty_report` measures get scrambled out of order.
    """
    document = project.model_dump(mode="json")
    levels = document["levels"]
    for key in ("width", "height", "time_limit_seconds", "tiles", "spawns"):
        levels[i][key], levels[j][key] = levels[j][key], levels[i][key]
    return type(project).model_validate(document)


def test_a_design_whose_levels_do_not_escalate_fails_the_difficulty_gate():
    project = create_default_project("Flat", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    scrambled = _swap_level_content(project, 0, len(project.levels) - 1)

    report = design_quality_report(scrambled)

    assert report["checks"]["every_level_honors_the_difficulty_curve"] is False
    assert "every_level_honors_the_difficulty_curve" in report["failures"]
    assert report["difficulty_failures"]
    assert report["quality_pass"] is False


def test_freshly_created_projects_of_several_genres_honor_their_difficulty_curve():
    for genre in ("maze_chase", "single_screen_collect", "sokoban", "boss_arena"):
        for platform in TargetPlatform:
            project = create_default_project("Curve", platform, genre)

            report = design_quality_report(project)

            assert report["checks"]["every_level_honors_the_difficulty_curve"] is True, (
                genre,
                platform,
            )
            assert report["difficulty_failures"] == []


def test_the_difficulty_report_is_annexed_with_per_level_detail():
    project = create_default_project("Annex", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)

    report = design_quality_report(project)

    difficulty = report["difficulty"]
    assert difficulty["honored"] is True
    assert difficulty["curve"] == project.gameplay.difficulty_curve
    assert [level["level"] for level in difficulty["levels"]] == [
        level.id for level in project.levels
    ]
    assert all("estimated_steps" in level for level in difficulty["levels"])
