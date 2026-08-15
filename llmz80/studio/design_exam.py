"""Does the design state what its own brief asked for.

`quality.design_quality_report` catches the design that states nothing at all.
This catches the one that states something else: `studio-projects/my-retro-game`
carries a brief asking for a plane flying right with scroll and enemies, and a
design of one fixed 20x14 screen. The program implemented the design faithfully
and the brief was never mentioned again.

The verdict is a model's, so it is shaped to be checkable: a refusal must quote
the sentence of the brief it is about and name what the design fails to state.
A refusal that cannot do both is worthless to whoever has to fix the design.

This is not a gate that only ever says no. `reference_design.propose_and_apply`
runs it inside its repair loop, so the first thing a missed brief buys is
another attempt with the gap named -- see that module. A refusal reaching a
person means the designer was told what was missing and still did not state it.
"""

from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict

from .models import GameProject


class BriefCoverage(BaseModel):
    """One verdict on whether a design covers its brief."""

    model_config = ConfigDict(extra="forbid")

    covered: bool
    #: What the brief asks for and the design does not state, one sentence each.
    missing: list[str]
    #: The sentence of the brief this verdict is about, quoted verbatim, so a
    #: refusal can be checked against the brief rather than taken on faith.
    quoted: str


class DesignExaminer(Protocol):
    def examine(self, project: GameProject) -> BriefCoverage: ...


def _screens_line(project: GameProject) -> str:
    parts = []
    for screen in project.screens:
        described = f"{screen.id} {screen.width}x{screen.height}"
        # A time limit is a concrete claim a brief can make ("hay que llegar
        # antes de que se acabe el tiempo"), so it travels with the screen it
        # belongs to rather than being left out as scenery.
        if screen.time_limit_seconds is not None:
            described += f" ({screen.time_limit_seconds}s limit)"
        parts.append(described)
    return f"Screens: {len(project.screens)} " + ", ".join(parts)


def _entities_line(project: GameProject) -> str:
    """Every actor with its count and its notes.

    The notes are here because of `my-retro-game`: its single `actor` carries a
    paragraph about fuel, missiles, bombs and landing on a carrier -- gameplay
    the design genuinely states, in a field the writer genuinely reads. A
    summary that hid it would have the examiner report gaps that are not gaps,
    and a false refusal costs an attempt the design needed for a real one.
    `count` is here for the same reason in the other direction: "van
    apareciendo otros cazas" is answered by how many of what there are.
    """
    described = []
    for entity in project.entities:
        line = f"  - {entity.id} ({entity.kind}) x{entity.count}"
        if entity.notes:
            line += f": {entity.notes}"
        described.append(line)
    return "\n".join(["Entities:", *described])


def design_summary(project: GameProject) -> str:
    """What the design actually states, in the form the examiner must judge.

    Everything a brief can ask for and this document can answer, and nothing
    else. `budgets` and `observables` are deliberately absent: budgets are what
    the machine imposes, not what anybody asked for, and observables are the
    symbols the runtime examiner reads. Showing either would invite a verdict
    about a field no brief was ever written about.

    Public, and named without an underscore, because `drafting` renders the
    same document for the drafter that has to make it answer its brief. One
    question from two sides deserves one rendering: two would drift until the
    drafter was told something the examiner never judged.
    """
    presentation = project.presentation
    audio = project.audio
    lines = [
        _screens_line(project),
        "Exits: "
        + (
            ", ".join(
                f"{screen.id} -{direction}-> {destination}"
                for screen in project.screens
                for direction, destination in screen.exits.items()
            )
            or "none"
        ),
        _entities_line(project),
        "Tiles: " + ", ".join(f"{t.id} '{t.char}'" for t in project.tiles),
        "Controls: " + ", ".join(f"{n}={k}" for n, k in project.controls.bindings.items()),
        "Scenes: " + ", ".join(f"{scene.id} ({scene.kind})" for scene in project.scenes),
        f"Presentation: style {presentation.style!r}, "
        f"score {'shown' if presentation.show_score else 'hidden'}, "
        f"lives {'shown' if presentation.show_lives else 'hidden'}",
        "Audio: "
        + ("music" if audio.music else "no music")
        + ", effects: "
        + (", ".join(audio.effects) or "none"),
    ]
    if project.mechanics:
        lines.append("Mechanics:")
        lines.extend(f"  - {sentence}" for sentence in project.mechanics)
    else:
        # Said out loud rather than left as a bare heading.
        # `studio-projects/zampabolas` and `studio-projects/my-retro-game`
        # both reached the writer with `mechanics: []`, and an empty heading
        # reads as a list that was cut off, not as a design that declares
        # nothing about what it does.
        lines.append("Mechanics: none stated")
    return "\n".join(lines)


def examination_prompt(project: GameProject) -> str:
    """Everything the examiner is owed before it judges."""
    return f"""EXAMINE WHETHER THIS DESIGN STATES WHAT ITS BRIEF ASKED FOR

You are not judging whether the game is good, whether the brief is a good
idea, or whether the design would be fun. One question only: does the design
below state the things the brief asks for?

A brief sets mood as well as rules. Atmosphere ("a dark castle") is not
something a design must state. A concrete claim about how the game works --
that it scrolls, that enemies shoot back, that there are several rooms, that
the player jumps -- is.

THE BRIEF

{project.metadata.brief.strip()}

WHAT THE DESIGN STATES

{design_summary(project)}

Answer with covered=true only if every concrete claim in the brief is stated
somewhere in the design. Otherwise list each gap in `missing` as one sentence
naming what the brief asks for and what the design says instead, and quote in
`quoted` the words of the brief your verdict is about, verbatim.
"""


def coverage_errors(coverage: BriefCoverage) -> list[str]:
    """The verdict as diagnostics, or nothing when the design covers its brief.

    A `covered=True` that still lists gaps is read as uncovered. A model that
    answers yes and then contradicts itself has told us it is unsure, and the
    reading that does not let a design through is the safe one.
    """
    if coverage.covered and not coverage.missing:
        return []
    gaps = "; ".join(coverage.missing) or "the examiner refused without naming a gap"
    return [f'the brief says "{coverage.quoted}" and the design does not deliver it: {gaps}']


class ResponsesDesignExaminer:
    """Examines the design with the OpenAI Responses API."""

    def __init__(self, client: Any, model: str = "gpt-5") -> None:
        self.client = client
        self.model = model

    def examine(self, project: GameProject) -> BriefCoverage:
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You examine game designs against the brief they came from. "
                        "You answer only about what is stated, never about taste."
                    ),
                },
                {"role": "user", "content": examination_prompt(project)},
            ],
            text_format=BriefCoverage,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("the model did not return a coverage verdict")
        return parsed
