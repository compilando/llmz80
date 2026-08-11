"""Application services shared by the TUI and headless commands."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import re
import shutil

from llmz80.core.state_contract import STATE_PLAYING
from llmz80.quality.emulator_smoke import smoke_test, write_smoke_report
from PIL import Image

from .compiler import BuildResult, SourceResult, build_project, render_project
from .models import AssetSpec, GameProject, GenreId, ProjectScope, TargetPlatform
from .packs import create_default_project
from .store import ProjectStore
from .quality import studio_quality_report
from .acceptance import runtime_script
from .generator import write_program
from .release import export_release
import json


@dataclass
class StudioService:
    store: ProjectStore

    @classmethod
    def at(cls, workspace: Path) -> "StudioService":
        return cls(ProjectStore(workspace))

    def create_project(
        self,
        title: str,
        platform: TargetPlatform,
        genre: GenreId,
        scope: ProjectScope = ProjectScope.COMPLETE,
    ) -> tuple[GameProject, Path]:
        project = create_default_project(title, platform, genre, scope)
        directory = self.store.create(project)
        return project, directory

    def open_project(self, location: Path) -> GameProject:
        return self.store.load(location)

    def save_project(self, project: GameProject, directory: Path) -> Path:
        return self.store.save(project, directory)

    def generate_sources(self, project: GameProject, directory: Path) -> SourceResult:
        self.store.save(project, directory)
        return render_project(project, directory / "build")

    def add_asset(self, project: GameProject, directory: Path, source: Path) -> AssetSpec:
        source = source.expanduser().resolve()
        if not source.is_file():
            raise FileNotFoundError(f"asset not found: {source}")
        if source.suffix.casefold() not in {".png", ".bmp", ".gif"}:
            raise ValueError("assets must be PNG, BMP or GIF images")
        with Image.open(source) as image:
            width, height = image.size
            image.verify()
        identifier = re.sub(r"[^a-z0-9]+", "_", source.stem.casefold()).strip("_")
        identifier = (identifier or "sprite")[:32]
        if not identifier[0].isalpha():
            identifier = ("asset_" + identifier)[:32]
        if any(asset.id == identifier for asset in project.assets):
            raise ValueError(f"asset id already exists: {identifier}")
        assets_dir = directory / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        destination = assets_dir / f"{identifier}{source.suffix.casefold()}"
        if destination.exists():
            raise FileExistsError(f"asset destination already exists: {destination}")
        shutil.copy2(source, destination)
        asset = AssetSpec(
            id=identifier,
            source=f"assets/{destination.name}",
            width=width,
            height=height,
        )
        candidate = GameProject.model_validate(
            {
                **project.model_dump(mode="json"),
                "assets": [
                    *project.model_dump(mode="json")["assets"],
                    asset.model_dump(mode="json"),
                ],
            }
        )
        project.assets = candidate.assets
        self.store.save(project, directory)
        return asset

    def build(self, project: GameProject, directory: Path) -> BuildResult:
        self.generate_sources(project, directory)
        return build_project(project, directory / "build")

    #: Direction to key, per control scheme, for the scripted collect sweep.
    SWEEP_KEYS = {
        "qaop_space": {"left": "o", "right": "p", "up": "q", "down": "a"},
        "cursor_space": {"left": "5", "right": "8", "up": "7", "down": "6"},
    }

    def scenario_script(self, project: GameProject) -> list[dict[str, Any]]:
        """Executable acceptance steps, with each input resolved to a real key."""
        keys = dict(self.SWEEP_KEYS.get(project.controls.scheme) or {})
        keys["action"] = "space"
        steps = []
        for step in runtime_script(project):
            key = keys.get(step["hold"])
            if key is None:
                continue
            steps.append({**step, "key": key})
        return steps

    def acceptance_report(
        self, project: GameProject, runtime: dict[str, Any]
    ) -> dict[str, Any]:
        """Judge each executable acceptance step against what memory showed.

        A step whose reading never arrived is reported as unobserved, never as
        satisfied, so a target without a probe adapter cannot inherit a pass.
        """
        readings = {
            reading.get("id"): reading.get("read") or {}
            for reading in runtime.get("step_readings") or []
        }
        steps = runtime_script(project)
        if not steps:
            return {
                "schema_version": 1,
                "observed": False,
                "reason": "this design states no executable acceptance scenario",
                "scenarios": [],
                "quality_pass": None,
            }
        if not any(readings.values()):
            return {
                "schema_version": 1,
                "observed": False,
                "reason": "this target has no memory probe adapter",
                "scenarios": [step["id"] for step in steps],
                "quality_pass": None,
            }
        results = []
        for step in steps:
            read = readings.get(step["id"], {})
            mismatches = [
                f"{name}: expected {value}, read {read.get(name)}"
                for name, value in sorted(step["expect"].items())
                if read.get(name) != value
            ]
            results.append(
                {
                    "id": step["id"],
                    "hold": step["hold"],
                    "frames": step["frames"],
                    "expect": step["expect"],
                    "read": read,
                    "mismatches": mismatches,
                    "passed": not mismatches and bool(read),
                }
            )
        return {
            "schema_version": 1,
            "observed": True,
            "scenarios": results,
            "failures": [item["id"] for item in results if not item["passed"]],
            "quality_pass": all(item["passed"] for item in results),
        }

    def expected_state(self, project: GameProject, collected: int = 0) -> dict[str, int]:
        """Engine state the design demands after the scripted input.

        With no sweep this is the state a freshly loaded level must show. After
        a sweep the same rules predict the exact score and remaining count.
        """
        total = sum(
            entity.count for entity in project.entities if entity.role == "collectible"
        )
        return {
            "g_level": 1,
            "g_state": STATE_PLAYING,
            "g_lives": project.gameplay.lives,
            "g_score": collected * project.gameplay.score_per_collectible,
            "g_remaining": total - collected,
            "g_worst_frame_cost": 0,
            # The high score tracks the run live, so on a first run it equals it.
            "g_hiscore": collected * project.gameplay.score_per_collectible,
        }

    def probe_report(
        self, project: GameProject, runtime: dict[str, Any], collected: int = 0
    ) -> dict[str, Any]:
        """Compare emulator memory reads against what the design asked for.

        Where no reading is available the gate abstains rather than passing: an
        unobserved rule is recorded as unobserved, never as satisfied.
        """
        observed = runtime.get("probe_after") or {}
        expected = self.expected_state(project, collected)
        if not observed:
            return {
                "schema_version": 1,
                "observed": False,
                "reason": "this target has no memory probe adapter",
                "checks": {},
                "mismatches": [],
                "quality_pass": None,
            }
        checks = {
            name: observed.get(name) == value
            for name, value in expected.items()
            if name in observed
        }
        mismatches = [
            f"{name}: expected {expected[name]}, read {observed.get(name)}"
            for name, passed in checks.items()
            if not passed
        ]
        return {
            "schema_version": 1,
            "observed": True,
            "expected": expected,
            "read": observed,
            "checks": checks,
            "mismatches": mismatches,
            "quality_pass": not mismatches,
        }

    def runtime_test(
        self, project: GameProject, directory: Path, *, seconds: int = 3
    ) -> dict[str, Any]:
        build = self.build(project, directory)
        if not build.success:
            raise RuntimeError("runtime test requires a quality-passing build")
        script = self.scenario_script(project)
        report = smoke_test(
            build.output_dir,
            project.target.platform.value,
            full=True,
            seconds=seconds,
            script=script,
        )
        # The end state the design predicts is whatever the last scoring step
        # was meant to leave behind.
        scoring = [step for step in script if step["expect"].get("g_score")]
        collected = (
            scoring[-1]["expect"]["g_score"] // max(1, project.gameplay.score_per_collectible)
            if scoring
            else 0
        )
        probes = self.probe_report(project, report, collected)
        report["state_probe"] = probes
        acceptance = self.acceptance_report(project, report)
        report["acceptance"] = acceptance
        if probes["quality_pass"] is False or acceptance["quality_pass"] is False:
            report["quality_pass"] = False
        write_smoke_report(report, build.output_dir / "emulator_report.json")
        combined = studio_quality_report(project, build=build.report, runtime=report)
        (build.output_dir / "studio_quality_report.json").write_text(
            json.dumps(combined, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return report

    def verify_program(self, project: GameProject, directory: Path) -> dict[str, Any]:
        """Build the project and, where the target allows it, watch it run.

        Returned as evidence rather than as a verdict: the repair loop needs the
        diagnostics, not a boolean.
        """
        evidence: dict[str, Any] = {"build": None, "acceptance": None, "probes": None}
        build = self.build(project, directory)
        evidence["build"] = build.report
        evidence["probes"] = build.report.get("probes")
        if not build.success:
            return evidence
        try:
            runtime = self.runtime_test(project, directory)
        except RuntimeError as exc:
            evidence["runtime_error"] = str(exc)
            return evidence
        evidence["runtime"] = runtime
        evidence["acceptance"] = runtime.get("acceptance")
        return evidence

    def write_program(
        self,
        project: GameProject,
        directory: Path,
        writer: Any,
        *,
        attempts: int = 5,
    ) -> dict[str, Any]:
        """Have a program written into the project and repaired until it passes."""
        result = write_program(project, directory, writer, self.verify_program, attempts=attempts)
        report = result.as_dict()
        (directory / "write_report.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return report

    def release(self, project: GameProject, directory: Path) -> Path:
        return export_release(project, directory)
