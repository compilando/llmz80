"""Project-level quality gates above compiler and emulator evidence."""

from __future__ import annotations

from typing import Any

from .difficulty import difficulty_report
from .models import GameProject, SceneKind
from .registry import audio_gaps
from .solvability import solvability_report
from .terrain_structure import structure_report


def design_quality_report(project: GameProject) -> dict[str, Any]:
    roles = {entity.role for entity in project.entities}
    scene_kinds = {scene.kind for scene in project.scenes}
    acceptance_ids = {scenario.id for scenario in project.acceptance}
    collectible_total = sum(
        entity.count for entity in project.entities if entity.role == "collectible"
    )
    achievable_score = (
        collectible_total * project.gameplay.score_per_collectible * project.gameplay.level_count
    )
    checks = {
        "complete_scene_flow": {
            SceneKind.TITLE,
            SceneKind.GAMEPLAY,
            SceneKind.GAME_OVER,
        }.issubset(scene_kinds),
        "core_roles": {"player", "enemy", "collectible"}.issubset(roles),
        "three_core_acceptance_scenarios": {
            "start_game",
            "collect_scores",
            "enemy_costs_life",
        }.issubset(acceptance_ids),
        "win_score_is_achievable": achievable_score >= project.gameplay.win_score,
        "levels_fit_target_grid": all(
            level.width <= 40 and level.height <= 25 for level in project.levels
        ),
        "entity_budget_respected": (
            sum(entity.count for entity in project.entities) <= project.budgets.max_entities
        ),
        "release_has_multiple_levels": (
            project.scope.value == "prototype" or project.gameplay.level_count >= 3
        ),
    }
    solvability = solvability_report(project)
    checks["every_level_is_solvable"] = solvability.solvable
    structure = structure_report(project)
    checks["every_level_has_genre_shaped_terrain"] = structure.structured
    difficulty = difficulty_report(project)
    checks["every_level_honors_the_difficulty_curve"] = difficulty.honored
    gaps = audio_gaps(project)
    checks["audio_is_supported_by_target"] = not gaps
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "schema_version": 5,
        "checks": checks,
        "failures": failures,
        "solvability_failures": solvability.failures,
        "terrain_structure_failures": structure.failures,
        "difficulty_failures": difficulty.failures,
        "audio_gaps": gaps,
        "achievable_score": achievable_score,
        "solvability": solvability.as_dict(),
        "terrain_structure": structure.as_dict(),
        "difficulty": difficulty.as_dict(),
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
        "schema_version": 1,
        "project": project.metadata.slug,
        "target": project.target.platform.value,
        "genre": project.genre,
        "gates": gates,
        "design": design,
        "build_report": "build_report.json" if build else None,
        "runtime_report": "emulator_report.json" if runtime else None,
        "quality_pass": all(gates.values()),
    }
