"""The eight methods that do a step of the pipeline, kept out of the widgets.

`StudioApp` is a screen: a widget tree, a set of keys, and the machinery that
runs a slow job without freezing the terminal. These are the other thing it
does -- what pressing `Enter` on a step actually means -- and they all have
the same shape: check there is a project, ask before overwriting anything on
disk, close over a `job()` that calls `StudioService`, and hand it to `_run`.
None of them touches a widget; the panel each one opens is asked for through
`_set_panel` and drawn by the screen.

A mixin rather than free functions, deliberately. They are still methods of
the application: every one of them reads the state below and calls back into
the screen, so making them functions would mean passing the application in as
an argument and would buy nothing. What it does buy, as a class of its own,
is that the pipeline can be read in one sitting without the CSS, the key
handling and the compose tree in between.

The contract with the host, which `StudioApp` provides:

* state -- `project`, `project_dir`, `service`, `passed`, `researcher`,
  `designer`, `artist`, `_pending_proposal`, `_drawn_sprites`;
* the screen -- `notify`, `_set_panel`, `_refresh`,
  `_show_pending_proposal`, `_show_drawn_sprites`;
* the job runner -- `_run`, `_progress`, and `_confirmed` for the steps that
  ask before replacing a dossier or existing art.

Nothing here imports `tui`: a mixin that knew its host would be a circle, and
the contract above is what it needs instead.
"""

from __future__ import annotations

from . import wizard


class PipelineSteps:
    """The `Enter` of each step. See the module docstring for what it needs
    from the application it is mixed into."""

    def _open_project_step(self) -> None:
        """Step 0: pick a project out of the workspace, or start one.

        A workspace with projects in it shows the picker, whose first entry
        starts a new project; an empty one shows the creation panel straight
        away, because there is only one sensible thing to do in an empty
        workspace and making someone press one more key to be told so wastes
        the time of exactly the person who has least idea what to press.
        That shortcut is a courtesy and not the only road: the picker offers
        creating too, or the second project would be unreachable from here.

        Both paths end in `action_open`/`action_create`, which point the
        diary at the project's own directory, write `OPEN` in it, and put
        `proyecto` in `passed`. That last part is what actually lets the
        wizard move: `wizard.current` returns the first step *not left
        behind*, so a project that is open but whose step nobody marked
        would leave the wizard standing on step 0 forever.
        """
        self._set_panel("open" if self.service.store.list_projects() else "create")

    def _research(self) -> None:
        """The `referencia` step: research the real game the brief names,
        archiving reference.yml.

        This searches the web and calls the OpenAI API, so it says so
        before doing either -- the check for an existing dossier happens
        first and costs nothing. Like `llmz80 project reference`, it asks
        before replacing a dossier that already exists, since that file is
        meant to be corrected by hand, not silently overwritten; and a
        dossier that exists but cannot be read (malformed YAML) is reported
        the same way, not crashed on.
        """
        if self.project is None or self.project_dir is None:
            self.notify("Create or open a project first", severity="warning")
            return
        step = wizard.current(self.project, self.project_dir, self.passed)
        try:
            existing = self.service.reference(self.project_dir)
        except ValueError as exc:
            self.notify(str(exc), severity="error")
            self.notify(
                "Fix or remove reference.yml before researching again.",
                severity="warning",
            )
            return
        if existing is not None and not self._confirmed(step.name):
            self.notify(
                "An archived dossier already exists: "
                f"{existing.title or '(unidentified)'}. Press Enter again to replace it.",
                severity="warning",
            )
            return

        project, directory = self.project, self.project_dir

        def job() -> tuple[bool, str]:
            researcher = self.researcher
            if researcher is None:
                from ..cli import _openai_client_and_model
                from .reference import ResponsesReferenceResearcher

                client, model = _openai_client_and_model()
                researcher = ResponsesReferenceResearcher(client, model=model)
            dossier = self.service.research_reference(project, directory, researcher)
            if not dossier.identified:
                # Not a failure: an archived "nothing was found" is a real
                # answer, and the step is done -- the design keeps its typology.
                return True, "No game was identified. The design keeps its typology."
            known = [part for part in (dossier.publisher, str(dossier.year or "")) if part]
            on_publisher = f" ({', '.join(known)})" if known else ""
            return True, (
                f"[green]{dossier.title}{on_publisher}[/green] · "
                f"{len(dossier.sources)} source(s). See the stage line for Reference."
            )

        self._run("Researching with the OpenAI API; this searches the web", job)

    def _edit_design(self) -> None:
        """Step 2: review and adjust the design, in the map editor.

        The map is the largest part of what reviewing a design means by
        hand, and it is the panel `Esc` now saves out of (`action_back`), so
        a wall painted here is on disk before the wizard moves on. The two
        smaller parts have their own letters on the shortcuts line -- `e`
        for the entity roster, `g` for title/brief/style -- and `A`, offered
        by this step's own summary once a dossier exists, adapts the whole
        design to the researched game in one reviewable diff.
        """
        self._set_panel("map")
        if self.project is not None:
            self._refresh()

    def _adapt(self) -> None:
        """Propose an adaptation to the researched game, and open the diff
        panel to review it.

        Nothing is applied here -- `propose_from_reference` only returns an
        already-validated candidate project, and `_show_pending_proposal`
        shows its diff (and whatever the repair loop had to overcome to
        reach it) for a person to accept with [y] or discard with [n] in
        the diff panel, the same restraint `llmz80 project adapt` applies
        before it ever calls `save_project`.
        """
        if self.project is None or self.project_dir is None:
            self.notify("Create or open a project first", severity="warning")
            return
        self._pending_proposal = None
        project, directory = self.project, self.project_dir

        def job() -> tuple[bool, str]:
            designer = self.designer
            if designer is None:
                from ..cli import _openai_client_and_model
                from .reference_design import ResponsesReferenceDesigner

                client, model = _openai_client_and_model()
                designer = ResponsesReferenceDesigner(client, model=model)
            proposal, diff, updated, refusals = self.service.propose_from_reference(
                project, directory, designer
            )
            self._pending_proposal = (diff, updated, refusals)
            lines = [
                f"Attempt {number} was refused, repairing: {reason}"
                for number, reason in enumerate(refusals, start=1)
            ]
            lines.append("[green]Proposal ready[/green] -- review it in the diff panel.")
            return True, "\n".join(lines)

        self._run(
            "Proposing an adaptation with the OpenAI API",
            job,
            on_finished=self._show_pending_proposal,
            # A proposal is not the design step finished: nothing is applied
            # until [y], and the person may well go on editing afterwards.
            leaves_behind=False,
        )

    def _draw_sprites(self) -> None:
        """The `sprites` step: draw the art this project is missing, and
        register each result as an asset.

        `draw_sprites` only ever fills a gap -- it never touches an entity
        that already wears a sprite-kind asset -- so the one place this can
        overwrite existing art is here, by evicting it first; like
        `llmz80 project sprites`, that only happens after asking, and this
        calls OpenAI's image API, so it says so before doing that too.
        """
        if self.project is None or self.project_dir is None:
            self.notify("Create or open a project first", severity="warning")
            return

        have = {asset.id for asset in self.project.assets if asset.kind == "sprite"}
        needed = sorted({entity.sprite or entity.id for entity in self.project.entities})
        existing = [sprite_id for sprite_id in needed if sprite_id in have]
        if existing and not self._confirmed("sprites"):
            self.notify(
                "Sprite art already exists for: "
                + ", ".join(existing)
                + ". Press Enter again to redraw it, overwriting the existing art.",
                severity="warning",
            )
            return
        if existing:
            for sprite_id in existing:
                asset = next(
                    a for a in self.project.assets if a.kind == "sprite" and a.id == sprite_id
                )
                (self.project_dir / asset.source).unlink(missing_ok=True)
            remaining = [
                a for a in self.project.assets if not (a.kind == "sprite" and a.id in existing)
            ]
            # `model_copy`, not `model_validate` or a plain assignment,
            # deliberately skips the structural check tying an entity's
            # sprite to a declared asset: for the instant between evicting
            # the old art here and `draw_sprites` registering its
            # replacement below, no asset declares this id at all, which
            # the full validator would refuse. That gap lives only in
            # memory and is never saved -- `draw_sprites`'s own `add_asset`
            # call is what next writes to disk, once a fresh asset closes it.
            self.project = self.project.model_copy(update={"assets": remaining})

        self._drawn_sprites = []
        project, directory = self.project, self.project_dir
        progress = self._progress()

        def job() -> tuple[bool, str]:
            artist = self.artist
            if artist is None:
                from generators.openai_generator import OpenAIImageGenerator

                from ..cli import _openai_client_and_model, _openai_image_model
                from .sprite_artist import SpriteArtist

                # `OpenAIImageGenerator` takes an API key, not a client --
                # `llmz80 project sprites` reads it off the client
                # `_openai_client_and_model` already built rather than
                # loading it a second time, and this does the same; the
                # image model comes from `_openai_image_model` for the same
                # reason `llmz80 project sprites` does.
                client, _model = _openai_client_and_model()
                artist = SpriteArtist(
                    OpenAIImageGenerator(api_key=client.api_key, model=_openai_image_model())
                )
            drawn = self.service.draw_sprites(project, directory, artist, on_progress=progress)
            self._drawn_sprites = drawn
            if not drawn:
                return True, "Every entity already has sprite art."
            return True, "[green]Drawn[/green] " + ", ".join(asset.id for asset in drawn)

        self._run(
            "Drawing sprites with OpenAI's image API",
            job,
            on_finished=self._show_drawn_sprites,
        )

    def _write(self) -> None:
        """The `programa` step: have the program written and repaired against
        the compiler. This spends money, so it says so first."""
        progress = self._progress()

        def job() -> tuple[bool, str]:
            from ..cli import _openai_client_and_model
            from .generator import ResponsesProgramWriter

            client, model = _openai_client_and_model()
            writer = ResponsesProgramWriter(client, model=model)
            report = self.service.write_program(
                self.project, self.project_dir, writer, on_progress=progress
            )
            lines = [
                f"  attempt {attempt['number']}: build={attempt['build_passed']} "
                f"acceptance={attempt['acceptance_passed']}"
                for attempt in report["attempts"]
            ]
            lines.append(
                "[green]Program accepted[/green]"
                if report["accepted"]
                else "[red]Not accepted[/red] " + report["last_error"]
            )
            return bool(report["accepted"]), "\n".join(lines)

        self._run("Writing the program with the OpenAI API", job)

    def _test(self) -> None:
        """The `gates` step: build, run in the emulator, and report the gates.

        There is no build-only step: `runtime_test` compiles before it runs,
        and it is the only thing that writes studio_quality_report.json --
        building alone was a shortcut, never a stage of the pipeline.
        """
        progress = self._progress()

        def work() -> tuple[bool, str]:
            report = self.service.runtime_test(self.project, self.project_dir, on_progress=progress)
            acceptance = report.get("acceptance") or {}
            lines = [
                (
                    "[green]Runtime passed[/green]"
                    if report["quality_pass"]
                    else "[red]Runtime rejected[/red]"
                )
            ]
            for scenario in acceptance.get("scenarios") or []:
                if isinstance(scenario, dict):
                    mark = "ok" if scenario["passed"] else "FAILED"
                    lines.append(f"  {scenario['id']}: {mark} {scenario['mismatches'] or ''}")
            return bool(report["quality_pass"]), "\n".join(lines)

        self._run("Building and running", work)

    def _release(self) -> None:
        def work() -> tuple[bool, str]:
            archive = self.service.release(self.project, self.project_dir)
            return True, f"[green]Released[/green] {archive}"

        self._run("Exporting", work)
