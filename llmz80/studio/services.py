"""Application services shared by the TUI and headless commands."""

from __future__ import annotations

import json
import re
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from PIL import Image

from llmz80.quality.emulator_smoke import smoke_test, write_smoke_report

from .acceptance import RuntimeExamination, runtime_examination, step_mismatches
from .attributes import attribute_report
from .compiler import BuildResult, SourceResult, build_project, render_project
from .design_exam import DesignExaminer
from .feel import animation_report
from .generator import write_program
from .models import AssetSpec, EntitySpec, GameProject, TargetPlatform
from .observation import observation_script
from .pacing import pacing_report
from .planner import ProjectProposal, proposal_diff
from .quality import RUNTIME_GATES, studio_quality_report
from .reference import GameReference, ReferenceResearcher, load_reference, save_reference
from .reference_design import ReferenceDesigner, propose_and_apply
from .release import export_release
from .runtime_exam import RuntimeExaminer
from .samples import blank_project
from .sprite_artist import SpriteArtist
from .spriting import SPRITE_SIZE
from .store import ProjectStore

#: Told what is happening while it happens. The three long jobs below take
#: minutes and two of them spend money, and their reports only exist once they
#: are over -- so without this there is nothing to say during the wait, and a
#: screen that says nothing for eighty seconds reads as one that hung.
Progress = Callable[[str], None] | None


def _say(on_progress: Progress, text: str) -> None:
    """Report `text` if anyone is listening, so callers stay free of the check."""
    if on_progress is not None:
        on_progress(text)


@dataclass
class StudioService:
    store: ProjectStore
    #: Examinations already paid for, keyed by the design and the symbols the
    #: program exposes. See `examination`.
    _examinations: dict[tuple[str, tuple[str, ...]], RuntimeExamination] = field(
        default_factory=dict
    )

    @classmethod
    def at(cls, workspace: Path) -> "StudioService":
        return cls(ProjectStore(workspace))

    def create_project(self, title: str, platform: TargetPlatform) -> tuple[GameProject, Path]:
        project = blank_project(title, platform)
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
        self,
        project: GameProject,
        directory: Path,
        source: Path,
        *,
        frames: int = 1,
        kind: str = "sprite",
    ) -> AssetSpec:
        """Copy `source` into the project's `assets/`, derive its id from the
        filename, validate it against the design, and save the project.

        `frames` defaults to 1 -- a still image, the only kind every caller
        before `draw_sprites` ever imported. `draw_sprites` is the first
        caller that stages a multi-pose sheet, and passes the real count
        through so the registered `AssetSpec` (which has carried `frames`
        since it gained the field) states it correctly instead of silently
        claiming every sheet is one still frame.

        `kind` defaults to `sprite` because an actor's artwork is what every
        caller before terrain art imported. It is a parameter rather than
        something inferred from the image's size: an 8x8 image is tile art
        only if the design meant it as terrain, and `spriting.is_tile_art`
        asks `kind` exactly so a small sprite is not silently reclassified.
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
            kind=kind,
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

    def draw_tiles(
        self,
        project: GameProject,
        directory: Path,
        artist: object,
        dossier: GameReference | None = None,
        *,
        on_progress: Progress = None,
    ) -> list[AssetSpec]:
        """Draw the artwork every tile that asked for it is missing, and
        register it.

        `draw_sprites` for terrain, and the same shape for the same reasons:
        one asset per tile that wants art and has none, `add_asset` reused
        rather than a second path that also knows how to save a project, and
        existing art left alone (a caller that wants terrain redrawn removes
        the asset first, so from here that tile is simply missing art).

        Which tiles are drawn is the design's decision and not this method's:
        `TileSpec.wants_art` reads the note the designer wrote about how that
        terrain should look. Empty space leaves that blank and stays the
        character it carries -- drawing every declared tile would spend a
        model call producing a cell with nothing in it.

        The id an asset is registered under is the tile's own, so the
        generated `TILE_<ID>` matches the terrain vocabulary the writer reads
        in its prompt (see `acceptance.tile_art`). And like an entity's
        sprite, `tile.art` is filled in beside the asset that backs it rather
        than before: `structure.py` refuses a document naming an asset that
        does not exist, so the only reachable order is both at once.
        """
        if dossier is None:
            dossier = load_reference(directory)
        have = {asset.id for asset in project.assets if asset.kind == "tileset"}
        drawn: list[AssetSpec] = []
        for tile in project.tiles:
            if not tile.wants_art or tile.id in have:
                continue
            if not re.fullmatch(r"[a-z][a-z0-9_]{1,31}", tile.id):
                # `TileSpec.id` already matches this, so this is a guard
                # against the pattern changing under us rather than a case a
                # valid design can reach -- the same guard `draw_sprites`
                # keeps over `EntitySpec.sprite`, which really can carry
                # anything.
                raise ValueError(
                    f"tile {tile.id!r} is not a valid asset identifier (expected "
                    "lowercase letters, digits and underscores, starting with a letter)"
                )
            try:
                frames = artist.draw_tile(project, tile, dossier, on_progress=on_progress)
            except ValueError as exc:
                # Every attempt's raw cell is worth keeping for exactly the
                # run that produced no asset at all; see `draw_sprites`.
                self._save_raw_sheets(directory, tile.id, getattr(exc, "sheets", None))
                raise
            with tempfile.TemporaryDirectory() as scratch:
                staged = Path(scratch) / f"{tile.id}.png"
                frames[0].save(staged)
                asset = self.add_asset(project, directory, staged, kind="tileset")
            # Set after the asset exists and before the save below, so the
            # document that reaches disk has both halves or neither.
            tile.art = asset.id
            self.store.save(project, directory)
            self._save_raw_sheets(
                directory,
                tile.id,
                getattr(frames, "sheets", None),
                winner=getattr(frames, "sheet", None),
            )
            _say(
                on_progress,
                f"{tile.id}: terreno dibujado, {(directory / asset.source).stat().st_size} B",
            )
            drawn.append(asset)
        return drawn

    def draw_sprites(
        self,
        project: GameProject,
        directory: Path,
        artist: SpriteArtist,
        dossier: GameReference | None = None,
        *,
        on_progress: Progress = None,
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
            # `sprite` is optional on `EntitySpec` -- a fresh v4 project's
            # entity carries none until a designer assigns one (v3 always
            # had a genre pack do that for it). But `structure.py` refuses a
            # document where `entity.sprite` names an id no asset declares
            # (see its `test_an_entity_sprite_must_name_a_declared_asset`),
            # so there is no way to *pre*-assign one before the art exists --
            # any attempt to save that half-finished state would be rejected
            # the moment it round-trips through `GameProject.model_validate`.
            # The only way this ever balances is doing both at once: an
            # entity with no sprite yet wants its own id as its sprite id,
            # the same default a designer naming a new entity by hand would
            # reach for, and the loop below writes it onto `entity` in the
            # same breath `add_asset` registers the asset it now names.
            sprite_id = entity.sprite or entity.id
            if sprite_id not in have:
                wanted.setdefault(sprite_id, entity)

        drawn: list[AssetSpec] = []
        for sprite_id, entity in wanted.items():
            # `add_asset` derives an asset's id from the file it is given, by
            # sanitising the filename stem into the same character set
            # `AssetSpec.id` requires. Staging the sheet under `sprite_id`
            # itself only round-trips to that same id if `sprite_id` was
            # already in that set -- true of every sprite id a design is
            # expected to coin, but `EntitySpec.sprite` carries no such
            # pattern constraint of its own, so a design that broke
            # that convention would otherwise register an asset silently
            # misnamed relative to the entity that is meant to wear it.
            if not re.fullmatch(r"[a-z][a-z0-9_]{1,31}", sprite_id):
                raise ValueError(
                    f"entity {entity.id!r} wears sprite id {sprite_id!r}, which is "
                    "not a valid asset identifier (expected lowercase letters, "
                    "digits and underscores, starting with a letter)"
                )
            if entity.sprite is None:
                # Assigning it now, before the frames are even drawn, means
                # a `SpriteDrawFailure` below leaves `entity.sprite` set to
                # an id with no asset behind it -- exactly the state
                # `structure.py` refuses -- but nothing saves `project` on
                # that path (see the `except` clause immediately below), so
                # it never reaches disk; `add_asset`'s own save, a few lines
                # down, is the first (and only) point this project is
                # persisted, and by then the asset exists too.
                entity.sprite = sprite_id
            try:
                # `on_progress` is forwarded straight into the artist: the
                # real `SpriteArtist.draw_frames` owns the retry loop and
                # the judged rejection reason first-hand, so it narrates its
                # own attempts live rather than this method reconstructing
                # them afterwards from `DrawnFrames.repairs` /
                # `SpriteDrawFailure.reasons` once the call has returned.
                frames = artist.draw_frames(project, entity, dossier, on_progress=on_progress)
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
            packed_bytes = (directory / asset.source).stat().st_size
            _say(
                on_progress,
                f"{entity.id}: {len(frames)} poses empaquetadas, {packed_bytes} B",
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

    def identified_reference(
        self, directory: Path, dossier: GameReference | None = None
    ) -> GameReference:
        """The archived dossier, only when it named a game to adapt to.

        Split out of `propose_from_reference` so a caller can ask the question
        before it does anything expensive. `pipeline.adapt` does exactly that:
        it used to announce "this calls the Anthropic API" and build the client,
        and only then hit these two guards, so a project with no dossier was
        told money was about to go out and then handed an error -- which reads
        as a charge that failed rather than one that never happened. The
        alternative, copying the two conditions into the pipeline, would have
        left two sets of wording to drift apart; `cli.py` matches the first
        message exactly to decide whether to print its fix-it hint.
        """
        dossier = dossier or load_reference(directory)
        if dossier is None:
            raise ValueError("there is no researched game for this project yet")
        if not dossier.identified:
            raise ValueError("no researched game was identified, so there is nothing to adapt to")
        return dossier

    def propose_from_reference(
        self,
        project: GameProject,
        directory: Path,
        designer: ReferenceDesigner,
        dossier: GameReference | None = None,
        *,
        attempts: int = 3,
        examiner: DesignExaminer | None = None,
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

        With an `examiner`, an attempt that applies cleanly but leaves the
        design saying nothing about what the brief asked for is refused the
        same way and reported in the same list -- so a caller already saying
        each repair aloud needs no new code to say these.
        """
        dossier = self.identified_reference(directory, dossier)
        adaptation = propose_and_apply(
            project, dossier, designer, attempts=attempts, examiner=examiner
        )
        return (
            adaptation.proposal,
            proposal_diff(adaptation.proposal),
            adaptation.project,
            adaptation.refusals,
        )

    def build(self, project: GameProject, directory: Path) -> BuildResult:
        self.generate_sources(project, directory)
        return build_project(project, directory / "build")

    def acceptance_report(
        self,
        project: GameProject,
        runtime: dict[str, Any],
        examiner: RuntimeExaminer | None = None,
    ) -> dict[str, Any]:
        """Judge each examined acceptance step against what memory showed.

        A step whose reading never arrived is reported as unobserved, never as
        satisfied, so a target without a probe adapter cannot inherit a pass.
        The same rule decides the order of the two abstentions below: whether
        anything was read at all is settled *before* the examiner is asked,
        because asking a model what a run must show when no run was observed
        spends money to produce a verdict that could only abstain anyway.

        Which symbols the examiner may talk about comes from the readings
        rather than from the contract, so it cannot assert anything about a
        symbol this program does not have -- a design with no lives never
        declares `g_lives`, and a claim about one would fail the game for a
        concept it never had.

        The mechanics nobody checked are published here, not just counted.
        That list is the honest measure of how much of this design the gate
        said nothing about, and a pass that hides it reads as a full
        examination -- which is the shape of the failure that let an
        abstention be mistaken for approval in the first place.
        """
        readings = {
            reading.get("id"): reading.get("read") or {}
            for reading in runtime.get("step_readings") or []
        }
        if not any(readings.values()):
            return {
                "schema_version": 2,
                "observed": False,
                "reason": "this target has no memory probe adapter",
                "scenarios": [],
                "quality_pass": None,
            }
        symbols = sorted({name for read in readings.values() for name in read})
        examination = self.examination(project, examiner, symbols)
        common = {
            "mechanics_total": len(project.mechanics),
            "unchecked_mechanics": examination.unchecked,
            "unverifiable": examination.reasons,
            "discarded_assertions": examination.discarded,
        }
        if not examination.asserted:
            return {
                "schema_version": 2,
                "observed": False,
                "reason": (
                    "no examiner has derived what this design should do"
                    if not examination.steps
                    else "the examiner found nothing this run could check"
                ),
                "scenarios": [],
                "quality_pass": None,
                **common,
            }
        results = []
        for step in examination.steps:
            read = readings.get(step["id"], {})
            mismatches = step_mismatches(step, readings)
            # `bool(read)` guards against a step whose reading never arrived
            # inheriting a pass by vacuous truth -- but that guard only means
            # something for a step that actually predicts something. Most
            # steps predict nothing: the examiner binds its assertions to the
            # few steps that can witness them, and judging the rest by whether
            # a reading happened to arrive would fail a program over steps
            # this gate never made a claim about.
            passed = not mismatches and (bool(read) or not step["expect"])
            results.append(
                {
                    "id": step["id"],
                    "hold": step["hold"],
                    "frames": step["frames"],
                    "expect": step["expect"],
                    "read": read,
                    "mismatches": mismatches,
                    "passed": passed,
                }
            )
        return {
            "schema_version": 2,
            "observed": True,
            "scenarios": results,
            "failures": [item["id"] for item in results if not item["passed"]],
            "quality_pass": all(item["passed"] for item in results),
            **common,
        }

    def examination(
        self,
        project: GameProject,
        examiner: RuntimeExaminer | None,
        symbols: list[str],
    ) -> RuntimeExamination:
        """The examiner's verdict on this design, asked for at most once.

        `generator.write_program` verifies up to five attempts, and the design
        it examines is the same document every time -- only the program
        changes. Without this the same question would be paid for five times
        per game and answered slightly differently each time, so a repair
        could be judged against an exam the previous attempt never sat.
        Keyed by the symbols too, because a program that starts declaring
        `g_lives` on its third attempt is a different exam.
        """
        key = (project.model_dump_json(), tuple(symbols))
        if key not in self._examinations:
            self._examinations[key] = runtime_examination(project, examiner, symbols=symbols)
        return self._examinations[key]

    def probe_report(self, project: GameProject, runtime: dict[str, Any]) -> dict[str, Any]:
        """Report what memory said, without judging it.

        Judging needs an expectation, and the only expectation Studio could
        produce was the pellet-sweeper's. Until the examiner derives a real one
        from the design, this records the reading and abstains.
        """
        observed = runtime.get("probe_after") or {}
        return {
            "schema_version": 2,
            "observed": bool(observed),
            "reason": "no examiner has derived what this design should read",
            "read": observed,
            "checks": {},
            "mismatches": [],
            "quality_pass": None,
        }

    def runtime_test(
        self,
        project: GameProject,
        directory: Path,
        *,
        seconds: int = 3,
        on_progress: Progress = None,
        examiner: RuntimeExaminer | None = None,
    ) -> dict[str, Any]:
        """Build the project, then watch it run in the emulator.

        These are the two long waits this method spends: compiling the
        sources, then launching and driving the emulator for `seconds`. Today
        they are lived as one silent wait, so `on_progress` is told when each
        one starts.
        """
        _say(on_progress, "compilando el programa")
        build = self.build(project, directory)
        if not build.success:
            raise RuntimeError("runtime test requires a quality-passing build")
        _say(on_progress, "arrancando el emulador")
        report = smoke_test(
            build.output_dir,
            project.target.platform.value,
            full=True,
            seconds=seconds,
            script=observation_script(project),
        )
        probes = self.probe_report(project, report)
        report["state_probe"] = probes
        acceptance = self.acceptance_report(project, report, examiner)
        report["acceptance"] = acceptance
        animation = animation_report(report)
        report["animation"] = animation
        pacing = pacing_report(report)
        report["pacing"] = pacing
        attributes = attribute_report(report)
        report["attributes"] = attributes
        # Every gate in `RUNTIME_GATES`, read back off the report just written
        # rather than from the locals above: the set of gates that can refuse a
        # run is one list in `quality.py`, and a chain of `or`s here is a second
        # copy of it that drifts silently. Wider than `WITNESS_GATES`, which is
        # what `verification_level` reads: pacing and attributes cannot promote
        # a run to `observed`, but a definite refusal from either still fails
        # it.
        if any(report[name]["quality_pass"] is False for name in RUNTIME_GATES):
            report["quality_pass"] = False
        write_smoke_report(report, build.output_dir / "emulator_report.json")
        combined = studio_quality_report(project, build=build.report, runtime=report)
        (build.output_dir / "studio_quality_report.json").write_text(
            json.dumps(combined, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return report

    def verify_program(
        self,
        project: GameProject,
        directory: Path,
        *,
        on_progress: Progress = None,
        examiner: RuntimeExaminer | None = None,
    ) -> dict[str, Any]:
        """Build the project and, where the target allows it, watch it run.

        Returned as evidence rather than as a verdict: the repair loop needs the
        diagnostics, not a boolean.

        `on_progress` is forwarded to `runtime_test` unchanged, so its two
        long-wait lines (compiling, then starting the emulator) are told
        however this is called -- directly, or from inside
        `write_program`'s repair loop, which is the call `on_progress` used
        to never reach: `generator.write_program`'s own `verify` parameter
        is a fixed two-argument `Callable[[GameProject, Path], dict]`, so
        nothing this method itself does could widen what it is called with.
        """
        evidence: dict[str, Any] = {
            "build": None,
            "acceptance": None,
            "probes": None,
            "animation": None,
            "pacing": None,
            "attributes": None,
            "state_probe": None,
        }
        build = self.build(project, directory)
        evidence["build"] = build.report
        # The build-time symbol map, which is what `repair_prompt`'s missing
        # contract symbols are read from and stays under this name. The runtime
        # state-probe gate is a different verdict about a different thing and
        # goes in under `state_probe` below, so the two are never confused --
        # confusing them is why the runtime gate could fail a run that the
        # repair loop was accepting.
        evidence["probes"] = build.report.get("probes")
        if not build.success:
            # No emulator has run yet, so there is no animation, pacing or
            # attribute verdict -- a build failure is refused on the build
            # diagnostics alone.
            return evidence
        try:
            runtime = self.runtime_test(
                project, directory, on_progress=on_progress, examiner=examiner
            )
        except RuntimeError as exc:
            evidence["runtime_error"] = str(exc)
            return evidence
        evidence["runtime"] = runtime
        evidence["acceptance"] = runtime.get("acceptance")
        evidence["animation"] = runtime.get("animation")
        evidence["pacing"] = runtime.get("pacing")
        evidence["attributes"] = runtime.get("attributes")
        evidence["state_probe"] = runtime.get("state_probe")
        return evidence

    def write_program(
        self,
        project: GameProject,
        directory: Path,
        writer: Any,
        *,
        attempts: int = 5,
        on_progress: Progress = None,
        examiner: RuntimeExaminer | None = None,
    ) -> dict[str, Any]:
        """Have a program written into the project and repaired until it passes.

        `generator.write_program` now narrates its own loop -- one line
        before each attempt's LLM call, one with its verdict once `verify`
        has judged it -- so `on_progress` is simply forwarded to it; nothing
        here waits for the whole repair loop to finish before saying
        anything.

        The `verify` callable it is given is not `self.verify_program`
        directly but a closure over it that also carries `on_progress`.
        `generator.write_program`'s `verify` parameter is typed
        `Callable[[GameProject, Path], dict[str, Any]]` on purpose -- several
        tests (`test_studio_generator.py`) inject their own two-argument fake
        verifier straight into that loop, with no interest in progress at
        all, and widening the signature to three arguments would force every
        one of them (present and future) to accept and ignore a parameter
        only this one caller wants. The closure keeps that extra argument
        local to the caller that needs it instead of leaking it into a
        contract several unrelated tests already rely on.
        """

        def _verify(project: GameProject, directory: Path) -> dict[str, Any]:
            # The examiner rides in the same closure as `on_progress` and for
            # the same reason: `generator.write_program`'s `verify` is a fixed
            # two-argument callable that several tests inject their own
            # version of, and widening it would force every one of them to
            # accept an argument only this caller cares about.
            return self.verify_program(
                project, directory, on_progress=on_progress, examiner=examiner
            )

        result = write_program(
            project, directory, writer, _verify, attempts=attempts, on_progress=on_progress
        )
        report = result.as_dict()
        (directory / "write_report.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return report

    def release(self, project: GameProject, directory: Path) -> Path:
        return export_release(project, directory)
