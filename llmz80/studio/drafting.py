"""Turn a brief into a design that states something.

The pipeline had a hole where this stage now is. `adapt` dresses a design in a
researched game's clothes and says so in its own prompt -- what the game *is*
is "settled and not yours to change" -- and `samples.blank_project` is one
actor, two tiles and no mechanics, with a docstring saying it has no
authority. Between the two, nobody ever decided what the game was:
`studio-projects/zampabolas` and `studio-projects/my-retro-game` both reached
the writer with `mechanics: []`, the second of them from a dossier that had
correctly identified *Harrier Attack!* from eight cited sources.

Drafting decides what the game is; adaptation decides what it looks like.
Keeping them apart is what leaves `adapt`'s prompt intact, and it is why this
stage runs *after* research rather than instead of it: when there is a
dossier the draft reads it, and when there is none it drafts from the brief
alone -- which is what unblocks an order that used to dead-end on a game
nobody recognised.

Like `reference_design`, this emits the `ProjectProposal` the assistant
already emits, so it inherits the diff, the protected paths and the
transactional validation of `apply_proposal` without writing any of them.
"""

from __future__ import annotations

from typing import Any, Protocol

from .design_exam import DesignCoherenceExaminer, coherence_errors, design_summary
from .models import GameProject
from .planner import AppliedProposal, ProjectProposal, propose_apply_repair
from .quality import design_quality_report, design_refusals
from .reference import GameReference
from .typologies import typology_hints

#: Everything the drafter is told. It is the mirror image of
#: `reference_design.DESIGN_SYSTEM_PROMPT`: that one is warned off the fields
#: that carry the design's identity, and this one is pointed at exactly those
#: fields, because deciding them is the whole job. What both share is the
#: warning off Studio's own guarantees -- a proposal touching a protected path
#: is refused on apply, and one that outgrows the target's playable grid is
#: refused by `GameProject`'s own validation, so spending changes there only
#: wastes the twenty a proposal is allowed.
DRAFT_SYSTEM_PROMPT = """\
You write the design of a game from the brief somebody wrote for it. The
design you are given is a blank: one actor, two tiles, one empty room. It
decides nothing and you are not contradicting anybody by replacing it.

Say what this game *is*: who is in it, what the player does, how it is won
and how it is lost. Nothing downstream infers these -- the program is
written from what the design states, so a rule you leave unstated is a rule
the game will not have.

Draft only what the brief asks for. Where the brief is silent about a
mechanic, do not invent one to fill the space; a smaller design that answers
the brief is right, and a bigger one that answers a different game is the
one failure this stage exists to avoid. Where a researched game is supplied,
it is evidence about what the brief means, not a second brief: take from it
what the brief already asked for.

Propose JSON-pointer changes to the supplied GameProject. You get at most 20
changes in total, so spend them on whole arrays and whole objects rather than
one row, cell or spawn at a time:
  /mechanics                what the game does, one sentence per rule,
                             in the design's own language        -> value_rows
  /entities/-               a whole new actor, appended          -> value_entity, add
  /entities/N/kind          what an actor already there is       -> value_text
  /entities/N/notes         what that actor does                 -> value_text
  /entities/N/count         how many of it there are             -> value_number
  /tiles/-                  a whole new kind of terrain          -> value_tile, add
  /screens/N/tiles          the room, as rows of the design's own
                             tile characters                     -> value_rows
  /screens/N/spawns         where each actor starts              -> value_spawns
  /controls/bindings/NAME   a key for an action the brief names and
                             the design has no key for           -> value_text, add

Each change carries its value in exactly one of those value_* fields --
never more than one, and none at all for a remove.

Out of bounds. Never propose a change to any of these:
  * /schema_version, /metadata/slug, /target/platform and /acceptance are
    protected and refused on apply; so is anything under /budgets, which the
    machine imposes and the design does not get to raise.
  * /metadata/title, /metadata/brief and the rest of /target are not refused
    for you, and are still not yours. A person wrote the title and the brief
    -- the brief is what this draft is measured against, so editing it would
    be marking your own exam -- and the video mode and frame rate were
    decided when the project was created.

Rules:
  * Every id -- an entity's, a tile's -- is lower case, starts with a letter
    and holds only letters, digits and underscores: `caza_enemigo`, never
    `Caza Enemigo`.
  * A binding's name follows that same rule, and the key it names must be one
    the machine can read: a single letter or digit, or SPACE, ENTER, UP,
    DOWN, LEFT or RIGHT. A design has at most eight bindings, and no two may
    share a key.
  * A tile's `char` is one printable character, and no two tiles may share
    one. It is what the screen rows are written in.
  * A screen's terrain rows must all match its declared width and height
    exactly, and use only tile characters the design declares under `/tiles`.
    Add the tile before you use its character.
  * Leave `sprite`, `art` and `colour` unset on everything you add. They name
    assets and palette entries this design does not declare yet, and naming
    one that does not exist is refused outright. The artwork comes later.
  * A spawn names an entity the design declares and sits inside the screen it
    is on; an entity's `count` is the most instances of it one screen may
    place.
  * Give each change a reason that says what in the brief motivates it.
"""


def needs_drafting(project: GameProject) -> bool:
    """Whether this design is one that should be drafted at all.

    Both halves matter, and for opposite reasons.

    No brief means nobody has said what this game should be. Drafting one
    anyway would mean inventing the brief, which is the exact failure the
    whole pipeline is built to prevent -- it is why `reference.py` makes a
    researcher admit it found nothing rather than describe a plausible game,
    and the same rule applies to a stage with even less to go on.

    Mechanics already stated mean the design is somebody's. Redrafting it
    would be the reinterpretation `adapt`'s own prompt refuses on the
    dossier's behalf, and refusing it there while doing it here would be a
    rule that only binds the stage that did not need it.

    A design with neither -- no brief and no mechanics -- is held back by the
    first half alone, and that is right: `quality.design_notices` already
    tells whoever created it that nothing says what the game does, and the
    remedy for that is a brief, not a draft.
    """
    return bool(project.metadata.brief.strip()) and not project.mechanics


class DesignDrafter(Protocol):
    def draft(
        self,
        project: GameProject,
        dossier: GameReference | None = None,
        feedback: str | None = None,
    ) -> ProjectProposal: ...


def drafting_prompt(project: GameProject, dossier: GameReference | None) -> str:
    """Everything the drafter is owed before it decides what this game is.

    What the design states today comes from `design_exam.design_summary`
    rather than a second summary written here. The examiner asks whether the
    design answers its brief and this stage has to make it answer it: that is
    one question from two sides, and two renderings of the same document
    would drift until the drafter was told something the examiner never
    judged.
    """
    # Named outright rather than left to the brief's own wording. Two runs of
    # the same brief drafted the same game in different languages, one Spanish
    # and one English, because nothing here said which -- and `mechanics` is
    # read by a person editing game.yml as well as by the model that writes
    # the program, so the design should not change tongue between runs.
    tongue = "Spanish" if project.metadata.language == "es" else "English"
    sections = [
        "WRITE THE DESIGN THIS BRIEF ASKS FOR",
        f"Write every sentence of the design in {tongue}: that is the language "
        "this project declares in its metadata.",
        "THE BRIEF\n\n" + project.metadata.brief.strip(),
        "WHAT THE DESIGN STATES TODAY\n\n" + design_summary(project),
    ]
    # An unidentified dossier has nothing in it to read: `reference.py` tells
    # the researcher to leave every other field at its default rather than
    # describe a game it is not sure of. Nothing validates that, so this is
    # not a guarantee -- it is a reason not to show a model a document of
    # blank fields, which invites it to treat the blanks as facts.
    if dossier is not None and dossier.identified:
        sections.append(
            "A REAL GAME WAS RESEARCHED FOR THIS BRIEF\n\n"
            "It is evidence about what the brief means. Take from it what the "
            "brief already asked for, and nothing else.\n\n" + dossier.model_dump_json(indent=2)
        )
    return "\n\n".join(sections)


class ResponsesDesignDrafter:
    """Drafts a design through the OpenAI Responses API.

    The same shape as `reference_design.ResponsesReferenceDesigner`, including
    the guard it opens with: that one refuses to adapt to a game nobody
    identified, and this one refuses to draft from a brief nobody wrote. Both
    are the one input their stage cannot invent, and both are refused here as
    well as in `needs_drafting` -- the stage's guard is what keeps the call
    from being made, and this one is what keeps a caller that reached past the
    stage from getting a design out of nothing.

    `typology_hints` travels with the request rather than inside
    `drafting_prompt`, for two reasons: it is what `ResponsesReferenceDesigner`
    does with the same block, and it reads `resources/genres.yml` off disk --
    a prompt builder that touches the filesystem is one a test cannot call
    without one.
    """

    def __init__(self, client: Any, model: str = "gpt-5") -> None:
        self.client = client
        self.model = model

    def draft(
        self,
        project: GameProject,
        dossier: GameReference | None = None,
        feedback: str | None = None,
    ) -> ProjectProposal:
        if not project.metadata.brief.strip():
            raise ValueError(
                "this project carries no brief, so there is nothing to draft a design from"
            )
        content = "\n\n".join([typology_hints(), drafting_prompt(project, dossier)])
        if feedback:
            content += "\n\nYOUR PREVIOUS DRAFT WAS REJECTED\n\n" + feedback
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": DRAFT_SYSTEM_PROMPT},
                {"role": "user", "content": content},
            ],
            text_format=ProjectProposal,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("the model did not return a structured project proposal")
        return parsed


class DraftRefused(ValueError):
    """The drafter could not produce a design that states anything.

    Its own class so `make` and the CLI can tell "the drafter did not manage
    it" from every other `ValueError` a stage can raise -- the distinction
    `pipeline.DesignRefused` already draws for a refused design.
    """


def gate_feedback(refusals: list[str]) -> str:
    """Turn the design gate's refusals into an instruction the drafter can act
    on.

    The sentences, not the check names: `quality.design_refusals` exists
    because telling somebody their design failed
    `design_states_the_mechanics_its_brief_asks_for` leaves them no better off
    than the silence that used to let it through.

    Deliberately not `reference_design.coverage_feedback`, which reads well
    and would be wrong here: it tells the model that adding entities is
    refused and it must work with the actors it has. That is true of the
    designer and false of the drafter, whose whole reason to exist is that
    `/entities/-` is open to it.
    """
    return "\n".join(
        [
            "THE DRAFT APPLIED BUT THE DESIGN STILL DOES NOT PASS ITS OWN GATE",
            "",
            *(f"  {refusal}" for refusal in refusals),
            "",
            "Propose again, fixing exactly these. `/mechanics` is where what the "
            "game does belongs -- one sentence per rule -- and it is the one the "
            "writer downstream refuses to work without.",
        ]
    )


def coherence_feedback(gaps: list[str]) -> str:
    """Turn the coherence examiner's gaps into an instruction the drafter can
    act on.

    Deliberately not `reference_design.coverage_feedback`, for the reason
    `gate_feedback` gives above: that text tells the model adding entities is
    refused and it must work with the actors it has, which is true of the
    designer and a lie to the drafter -- `/entities/-` and `/tiles/-` are open
    to it, and this gap is usually closed by exactly those paths. Being told
    the gap and then told the way to close it is forbidden would spend an
    attempt on nothing.

    The paths are named out loud rather than left to the system prompt, which
    the model has already read once and already followed into a design missing
    a car: `una-rana-que-cruza-una` names coches in three mechanics and
    declares one `actor`.
    """
    return "\n".join(
        [
            "THE DRAFT APPLIED BUT THE DESIGN DOES NOT DECLARE WHAT IT ASSUMES",
            "",
            *(f"  {gap}" for gap in gaps),
            "",
            "Propose again, declaring each of these. `/entities/-` appends a whole "
            "new actor and `/tiles/-` a whole new kind of terrain -- both are yours, "
            "and adding one is the ordinary way to close this. A tile you add must "
            "then appear in the screen rows that use its character, and an entity "
            "that starts somewhere needs its spawn under `/screens/N/spawns`.",
        ]
    )


def _coherence_gaps(project: GameProject, examiner: DesignCoherenceExaminer | None) -> list[str]:
    """What the examiner says this design assumes and never declares, or
    nothing.

    Nothing, and no model call, when there is no examiner -- every offline
    caller and every test that injects a drafter alone -- and when the design
    states no mechanics, since there is then nothing that could take anything
    for granted. The second case is not merely a saving: the design gate below
    already refuses a mechanics-less draft in words the drafter can act on,
    and paying a model to add "and it declares nothing" to that would tell it
    something it was about to be told anyway.
    """
    if examiner is None or not project.mechanics:
        return []
    return coherence_errors(examiner.examine(project))


def draft_and_apply(
    project: GameProject,
    drafter: DesignDrafter,
    dossier: GameReference | None = None,
    *,
    attempts: int = 3,
    examiner: DesignCoherenceExaminer | None = None,
) -> AppliedProposal:
    """Draft a design from the brief and validate it through `apply_proposal`.

    The loop is `planner.propose_apply_repair`, shared with
    `reference_design.propose_and_apply`. What is this stage's own is the two
    things below: the dossier is optional where the designer's is required --
    drafting from a brief alone is the case that unblocks a game nobody
    recognised -- and the acceptance test is the design gate rather than the
    examiner's coverage.

    The gate is the right acceptance test because it is the one that stops the
    pipeline later: `pipeline.write` refuses a design that carries a brief and
    states no mechanics before it pays a writer. A draft that would fail there
    is worth another attempt here, where the failure is still cheap and can be
    handed back as feedback.

    The whole gate is used, not only its mechanics check, and one of its three
    checks is not the drafter's to fix: `/budgets` is refused to a proposal
    outright. A design that arrives already over budget would spend every
    attempt being told something it cannot act on. That is written down rather
    than guarded against because there is no way in yet -- `blank_project`
    sets both budgets to exactly what its target allows and declares no audio,
    so only a hand edit gets a design here failing anything but its mechanics,
    and `pipeline.write` refuses that edit anyway.

    An `examiner` adds a second acceptance test beside the gate, and the one
    the gate cannot make: whether the design declares what its own mechanics
    take for granted. `studio-projects/una-rana-que-cruza-una` passed the gate
    with five mechanics, three of which name coches, and an entity roster of
    one untouched default `actor`. `design_exam`'s other examiner passed it
    too -- it reads the mechanics as evidence the brief is served, and the
    drafter wrote them, so the design certified itself. Feeding the gaps back
    is what makes the finding buy another attempt rather than a refusal.

    Raises `DraftRefused` once attempts run out, carrying what the design was
    still missing.
    """

    def review(updated: GameProject) -> tuple[str, str] | None:
        refusals = design_refusals(design_quality_report(updated))
        if refusals:
            return (
                "the draft applied but the design still does not pass its own gate: "
                + "; ".join(refusals),
                gate_feedback(refusals),
            )
        # Asked second, and only once the gate is happy, because it is the
        # one of the two that costs a model call. A draft that states no
        # mechanics has already been sent back by the line above, and it is
        # also the draft with nothing for this examiner to read.
        gaps = _coherence_gaps(updated, examiner)
        if gaps:
            return (
                "the draft applied but the design assumes things it never declares: "
                + "; ".join(gaps),
                coherence_feedback(gaps),
            )
        return None

    return propose_apply_repair(
        project,
        lambda feedback: drafter.draft(project, dossier, feedback),
        review,
        attempts=attempts,
        refusal=DraftRefused,
    )
