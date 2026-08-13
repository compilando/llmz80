"""Application services shared by the TUI and headless commands."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import logging
import re
import shutil
import tempfile

from llmz80.core.state_contract import STATE_PLAYING
from llmz80.quality.emulator_smoke import smoke_test, write_smoke_report
from PIL import Image

from .compiler import BuildResult, SourceResult, build_project, render_project
from .feel import animation_report
from .models import AssetSpec, EntitySpec, GameProject, GenreId, ProjectScope, TargetPlatform
from .packs import create_default_project
from .planner import ProjectProposal, proposal_diff
from .reference import GameReference, ReferenceResearcher, load_reference, save_reference
from .reference_design import ReferenceDesigner, propose_and_apply
from .sprite_artist import SpriteArtist
from .spriting import SPRITE_SIZE
from .store import ProjectStore
from .quality import studio_quality_report
from .acceptance import runtime_script
from .generator import write_program
from .release import export_release
import json

logger = logging.getLogger(__name__)


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

    def add_asset(
        self, project: GameProject, directory: Path, source: Path, *, frames: int = 1
    ) -> AssetSpec:
        """Copy `source` into the project's `assets/`, derive its id from the
        filename, validate it against the design, and save the project.

        `frames` defaults to 1 -- a still image, the only kind every caller
        before `draw_sprites` ever imported. `draw_sprites` is the first
        caller that stages a multi-pose sheet, and passes the real count
        through so the registered `AssetSpec` (which has carried `frames`
        since it gained the field) states it correctly instead of silently
        claiming every sheet is one still frame.
        """
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
            frames=frames,
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

    def draw_sprites(
        self,
        project: GameProject,
        directory: Path,
        artist: SpriteArtist,
        dossier: GameReference | None = None,
    ) -> list[AssetSpec]:
        """Draw the sheet each entity's sprite id is missing, and register it.

        One sheet is drawn per distinct `EntitySpec.sprite` id that has no
        matching sprite-kind asset yet -- several entities sharing a sprite id
        (three enemies all wearing "enemy") draw once, not once each, since
        `SpriteArtist.draw_frames` takes one representative entity and the
        result is worn by every entity whose `sprite` matches.

        Existing art is never touched here: a caller that wants an entity's
        sprite redrawn removes its asset first (`llmz80 project sprites` does
        this after asking), so from this method's view that id is "missing"
        like any other -- there is exactly one path that registers a sprite
        asset, `add_asset`, and this reuses it rather than writing a second
        one that also knows how to save the project and derive an id.

        `dossier`, when not given, is read the same way
        `propose_from_reference` reads one: a project with no researched game
        still needs art, and `SpriteArtist.draw_frames` already knows how to
        compose a prompt from the design alone when there is none.
        """
        if dossier is None:
            dossier = load_reference(directory)
        have = {asset.id for asset in project.assets if asset.kind == "sprite"}
        wanted: dict[str, EntitySpec] = {}
        for entity in project.entities:
            if entity.sprite not in have:
                wanted.setdefault(entity.sprite, entity)

        drawn: list[AssetSpec] = []
        for sprite_id, entity in wanted.items():
            # `add_asset` derives an asset's id from the file it is given, by
            # sanitising the filename stem into the same character set
            # `AssetSpec.id` requires. Staging the sheet under `sprite_id`
            # itself only round-trips to that same id if `sprite_id` was
            # already in that set -- true for every sprite this Studio has
            # ever generated (see `packs.py`), but `EntitySpec.sprite` carries
            # no such pattern constraint of its own, so a design that broke
            # that convention would otherwise register an asset silently
            # misnamed relative to the entity that is meant to wear it.
            if not re.fullmatch(r"[a-z][a-z0-9_]{1,31}", sprite_id):
                raise ValueError(
                    f"entity {entity.id!r} wears sprite id {sprite_id!r}, which is "
                    "not a valid asset identifier (expected lowercase letters, "
                    "digits and underscores, starting with a letter)"
                )
            try:
                frames = artist.draw_frames(project, entity, dossier)
            except ValueError as exc:
                # A `SpriteDrawFailure` (see `sprite_artist.py`) carries every
                # attempt's raw response even though none of them produced a
                # usable sprite -- exactly the run whose evidence is worth
                # keeping, since nothing else survives it (no asset is ever
                # registered). A caller's own artist raising a plain
                # `ValueError` carries no `.sheets`, and there is nothing to
                # save for those -- re-raising unconditionally either way is
                # what keeps this a transparent pass-through rather than a
                # second place that decides whether a draw failure is fatal.
                self._save_raw_sheets(directory, sprite_id, getattr(exc, "sheets", None))
                raise
            packed_sheet = Image.new("RGBA", (SPRITE_SIZE * len(frames), SPRITE_SIZE))
            for index, frame in enumerate(frames):
                packed_sheet.paste(frame, (index * SPRITE_SIZE, 0))
            with tempfile.TemporaryDirectory() as scratch:
                staged = Path(scratch) / f"{sprite_id}.png"
                packed_sheet.save(staged)
                asset = self.add_asset(project, directory, staged, frames=len(frames))
            self._save_raw_sheets(
                directory,
                sprite_id,
                getattr(frames, "sheets", None),
                winner=getattr(frames, "sheet", None),
            )
            have.add(sprite_id)
            drawn.append(asset)
        return drawn

    @staticmethod
    def _save_raw_sheets(
        directory: Path,
        sprite_id: str,
        sheets: list[Image.Image] | None,
        *,
        winner: Image.Image | None = None,
    ) -> None:
        """Keep what the model actually returned -- every attempt, not only
        one that worked -- beside the asset it did or did not produce.

        Nothing used to save any of this: only the cleaned, packed
        16x16-per-frame sheet ever reached disk, so a run like the one
        against *Abu Simbel Profanation* -- two sprites out of three coming
        back as dark art on a near-black background -- left nothing to look
        at afterwards except the ruined result. Saving only a winning
        attempt would still have that gap for the run that matters most: a
        sprite that exhausts every attempt and raises (`SpriteDrawFailure`,
        see `sprite_artist.py`) never reaches `add_asset` at all, so there
        would be no asset to save anything "beside". This is called from
        both branches -- the `except ValueError` above, before re-raising,
        and after a successful draw -- with whatever raw sheets exist either
        way, named from `sprite_id` directly rather than from an `AssetSpec`
        that may not exist yet.

        Every sheet in `sheets` (oldest first, one per attempt) is written to
        `assets/<sprite id>.raw.attempt-<n>.png`, `n` starting at 1, so the
        order they were drawn in is legible from the filename alone. When
        `winner` is given -- only on a successful draw -- it is additionally
        saved, unsuffixed, as `assets/<sprite id>.raw.png`: the one raw sheet
        worth finding without knowing which attempt number succeeded. Its
        absence is itself informative -- a sprite that only has numbered
        attempts on disk and no plain `.raw.png` is exactly the one that
        never produced a usable frame.

        `sheets` is `None` for a caller's own fake artist (several exist
        across the test suite) that carries no raw response at all -- there
        being nothing to save is not an error, so this simply returns.
        """
        if not sheets:
            return
        assets_dir = directory / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        for index, sheet in enumerate(sheets, start=1):
            sheet.save(assets_dir / f"{sprite_id}.raw.attempt-{index}.png")
        if winner is not None:
            winner.save(assets_dir / f"{sprite_id}.raw.png")

    def research_reference(
        self, project: GameProject, directory: Path, researcher: ReferenceResearcher
    ) -> GameReference:
        """Research the game the brief names and archive what was found.

        Archived whether or not the game was identified: knowing that a search
        already came up empty is worth as much as the dossier itself, and stops
        every later action paying for the same search again.
        """
        dossier = researcher.research(project.metadata.brief, project.target.platform.value)
        save_reference(dossier, directory)
        return dossier

    def reference(self, directory: Path) -> GameReference | None:
        return load_reference(directory)

    def propose_from_reference(
        self,
        project: GameProject,
        directory: Path,
        designer: ReferenceDesigner,
        dossier: GameReference | None = None,
        *,
        attempts: int = 3,
    ) -> tuple[ProjectProposal, str, GameProject, list[str]]:
        """Propose a design adaptation, repaired against `apply_proposal`
        until it is one a reviewer could accept as-is, returned with the diff
        a reviewer reads.

        Nothing is saved here -- `directory` is only where the dossier is
        read from -- but the returned project is already the one
        `planner.apply_proposal` built while validating the proposal, ready
        for a caller to persist once somebody has looked at the diff and
        agreed. The fourth item is the refusal reason from each attempt that
        did not apply, oldest first, so a caller can report what repair
        happened without this layer printing anything itself.
        """
        dossier = dossier or load_reference(directory)
        if dossier is None:
            raise ValueError("there is no researched game for this project yet")
        if not dossier.identified:
            raise ValueError(
                "no researched game was identified, so there is nothing to adapt to"
            )
        adaptation = propose_and_apply(project, dossier, designer, attempts=attempts)
        return (
            adaptation.proposal,
            proposal_diff(adaptation.proposal),
            adaptation.project,
            adaptation.refusals,
        )

    def build(self, project: GameProject, directory: Path) -> BuildResult:
        self.generate_sources(project, directory)
        return build_project(project, directory / "build")

    #: Direction to key, per control scheme, for the scripted collect sweep.
    SWEEP_KEYS = {
        "qaop_space": {"left": "o", "right": "p", "up": "q", "down": "a"},
        "cursor_space": {"left": "5", "right": "8", "up": "7", "down": "6"},
    }

    def scenario_script(self, project: GameProject) -> list[dict[str, Any]]:
        """Executable acceptance steps, with each input resolved to a real key.

        `ScenarioHold` documents `"none"` as waiting without touching the
        keyboard, and that is exactly what a step with no `"key"` entry does
        in `_run_zesarux` (`llmz80.quality.emulator_smoke`): it reads
        `step.get("key")`, and a key that is not one of `_SPECTRUM_ROWS` --
        which `None` never is -- presses nothing but still holds for the
        step's frames and reads the state contract. So a `"none"` hold is
        left with no `"key"` field rather than being resolved through
        `SWEEP_KEYS`, where it was never going to be found, and dropped.

        A direction (or `"action"`) the control scheme genuinely has no key
        for -- `"joystick"` has no `SWEEP_KEYS` entry at all -- still cannot
        be driven through the keyboard matrix this emulator scripts, so that
        step is dropped. But not without a trace: losing acceptance coverage
        because a design's control scheme lacks a mapping is exactly the
        kind of thing that hid this method's own bug, so it is logged rather
        than silently swallowed.
        """
        keys = dict(self.SWEEP_KEYS.get(project.controls.scheme) or {})
        keys["action"] = "space"
        steps = []
        for step in runtime_script(project):
            hold = step["hold"]
            if hold == "none":
                steps.append(dict(step))
                continue
            key = keys.get(hold)
            if key is None:
                logger.warning(
                    "dropping acceptance step %r: control scheme %r has no key "
                    "for hold %r",
                    step["id"], project.controls.scheme, hold,
                )
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
        animation = animation_report(report)
        report["animation"] = animation
        if (
            probes["quality_pass"] is False
            or acceptance["quality_pass"] is False
            or animation["quality_pass"] is False
        ):
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
