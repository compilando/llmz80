"""Structured AI proposals; the model never writes C or replaces game.yml."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Callable, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from .editing import editing_status
from .llm import structured
from .models import GameProject


class ChangeValue(BaseModel):
    """What one `ProjectChange` writes into the document, in one of a handful
    of narrow shapes.

    The variants are the anyOf branches of `ProjectChange.value`. Each declares
    only the fields its own shape needs, which is the whole point: `value` used
    to be seven sibling `value_*` properties -- `value_text`, `value_number`,
    `value_rows`, `value_spawns`, `value_entity`, `value_tile`,
    `value_observable` -- because OpenAI strict structured output rejects a
    property with no concrete JSON type, so a single generic `value` was not
    available and each shape had to bring its own field.

    That shape cost more than the schema. Strict mode also requires *every*
    declared property, so after writing the one field it wanted the model had
    to emit the other six as `null` before it could close the object, and in
    the captured raw responses it stalled exactly there: runs of 1 to 762
    literal spaces between a value's closing quote and the
    `, "value_number": null` tail. Twice in fourteen replayed responses the
    stall arrived one token early and came out *inside* the string, as `},{` --
    a brace, a comma and a brace being ordinary string characters that the
    grammar masks between fields and permits within a value. That corruption
    reached three designs on disk (`minero-vigilado`'s entity `kind`,
    `minero-observable`'s and `un-minero-que-cava-tuneles-y-2`'s
    `presentation.style`) and the program writer, and is what `models.Prose`
    now refuses at the document edge.

    An anyOf of narrow objects removes the pressure instead of catching its
    output: the model writes one value and closes, with no siblings to pad
    towards. It was verified against the live API before being adopted --
    strict structured output accepts an anyOf of objects for a property, and
    gpt-5 picks the branch matching the field it is editing.

    Replaying both stages that emit a proposal, from the same inputs the
    corrupted designs had, says what it bought. Before: 7 of 30 responses
    carried `},{` inside a string value, and 15 of 30 carried a stall run --
    always in the same place, between a written value and the following
    `"value_number": null`, up to 131 characters of it. After: 0 of 40
    responses carried either, over more changes per response (244 against
    174). The only whitespace left in the sample is one response that chose
    to indent the whole document, which is a style and not a stall.

    Rejected alternatives:

      * A bare union of JSON types (`str | int | list[str] | ...`). Fewer
        tokens still, but it takes away the model's chance to *say* which
        shape it means, and a `/mechanics` change that should be rows arrives
        as a paragraph with nothing having declared the mismatch.
      * One ordered list per shape. It keeps every variant narrow but loses
        cross-type ordering, and `apply_proposal` applies changes in order:
        an `/entities/-` that appends an actor before an `/entities/2/notes`
        that edits one is not the same proposal in the other order. Restoring
        it means carrying an explicit sequence number in every change, which
        is more machinery than one anyOf.
    """

    model_config = ConfigDict(extra="forbid")

    def json_value(self) -> Any:
        """The plain JSON this variant writes into the document."""
        raise NotImplementedError


class TextValue(ChangeValue):
    """A string: `presentation.style`, a mechanic's sentence, an entity's
    notes, a control binding's key."""

    text: str

    def json_value(self) -> Any:
        return self.text


class NumberValue(ChangeValue):
    """A whole number: an entity's `count`, a screen's `time_limit_seconds`.

    The one variant worth asking whether it earns its place: across 174
    replayed changes under the old shape no stage ever set `value_number`, and
    every one of them still paid a `"value_number": null`. Kept because under
    an anyOf an unused branch costs nothing per response -- and because the
    model did reach for it 3 times in 244 changes once it was a peer of the
    other shapes rather than a null to step over.
    """

    number: int

    def json_value(self) -> Any:
        return self.number


class RowsValue(ChangeValue):
    """A list of strings: a screen's terrain rows, or the whole `mechanics`
    list, one sentence per rule.

    Kept apart from `SpawnsValue` rather than folded into one "list" variant,
    because they are lists of different things and a model that picks the
    wrong one would produce a screen made of spawns."""

    rows: list[str]

    def json_value(self) -> Any:
        return list(self.rows)


class SpawnValue(BaseModel):
    """Mirrors `SpawnSpec` in models.py: where one entity instance starts on
    one of the design's screens."""

    model_config = ConfigDict(extra="forbid")
    entity: str = Field(pattern=r"^[a-z][a-z0-9_]{1,31}$")
    col: int = Field(ge=0, le=39)
    row: int = Field(ge=0, le=24)


class SpawnsValue(ChangeValue):
    """A whole screen's spawn list."""

    spawns: list[SpawnValue]

    def json_value(self) -> Any:
        return [spawn.model_dump(mode="json") for spawn in self.spawns]


class EntityValue(ChangeValue):
    """One whole entity, in the shape `EntitySpec` validates.

    An entity is the first thing a proposal ever needed to *add* rather than
    edit -- the designer only ever touched `/entities/N/notes` of an entity
    that was already there -- and a design that states nothing has none.

    The defaults mirror `EntitySpec`'s own, so a drafter that names only an id
    and a kind gets exactly what a designer writing the same two fields by
    hand would get.
    """

    id: str
    kind: str
    sprite: str | None = None
    poses: list[str] = Field(default_factory=list)
    count: int = 1
    colour: str | None = None
    notes: str = ""

    def json_value(self) -> Any:
        return self.model_dump(mode="json")


class TileValue(ChangeValue):
    """One whole tile, in the shape `TileSpec` validates.

    Here for the same reason as `EntityValue`: a design that states nothing
    has two tiles, and terrain the brief asks for -- water, lava, a ladder --
    is a tile the design has to grow, not a field of one it already declares.
    """

    id: str
    char: str
    art: str | None = None
    #: What this terrain should look like, and so whether it is drawn at all
    #: (`TileSpec.wants_art`). Mirrored here because a mirror missing a field is
    #: a field no proposal can ever set: terrain artwork stayed unreachable
    #: while the one stage that could describe it wrote every design.
    art_note: str = ""
    colour: str | None = None
    traits: list[str] = Field(default_factory=list)

    def json_value(self) -> Any:
        return self.model_dump(mode="json")


class PaletteEntryValue(BaseModel):
    """Mirrors `PaletteEntry` in models.py: the design's own name for a colour,
    and the prose that says what the colour is."""

    model_config = ConfigDict(extra="forbid")
    id: str = Field(pattern=r"^[a-z][a-z0-9_]{1,31}$")
    colour: str


class PaletteValue(ChangeValue):
    """A whole `presentation.palette`.

    Its own variant because a design's colours are the one thing `colour` on a
    tile or an entity is allowed to name: `structure.py` refuses a document
    whose `tile.colour` names an entry the palette does not declare, so a
    proposal that cannot write the palette cannot use colour at all -- which is
    why every finished game came out monochrome while both the field and the
    machine's eight inks were there the whole time.

    Written whole rather than one entry at a time for the same reason
    `/mechanics` is: a design's colours are a short list decided together, and
    the twenty changes a proposal gets are better spent elsewhere.
    """

    palette: list[PaletteEntryValue]

    def json_value(self) -> Any:
        return [entry.model_dump(mode="json") for entry in self.palette]


class ObservableValue(ChangeValue):
    """One whole observable, in the shape `ObservableSpec` validates.

    Its own variant because an observable is neither an entity nor a tile: it
    is a C symbol, a width in bytes and a sentence saying what the number
    means.

    A design that declares one is the only way a gate can witness a rule the
    state contract has no word for. Nothing had ever declared one: `game.yml`
    could carry observables since schema v4 and no stage could propose them,
    so the four finished games in `studio-projects/` were judged entirely on
    `g_score`, `g_state` and their siblings, and not one of their own
    mechanics was checked.
    """

    symbol: str
    #: Bytes to read out of memory. Mirrors `ObservableSpec`'s own default
    #: rather than being required, so a drafter naming a counter it has not
    #: thought about the range of gets the one-byte reading a hand-written
    #: design would get.
    width: int = 1
    meaning: str

    def json_value(self) -> Any:
        return self.model_dump(mode="json")


#: The anyOf `ProjectChange.value` declares. Order matters only to readers:
#: every variant forbids the others' fields, so nothing here is ambiguous.
AnyChangeValue = (
    TextValue
    | NumberValue
    | RowsValue
    | SpawnsValue
    | EntityValue
    | TileValue
    | PaletteValue
    | ObservableValue
)


class ProjectChange(BaseModel):
    """One JSON-pointer edit.

    `value` carries a `ChangeValue` variant rather than the bare JSON it
    stands for: OpenAI's strict structured output requires every property to
    carry a concrete JSON Schema type, and `Any` has none. An anyOf of narrow
    objects is how one `value` property gets a type again -- see `ChangeValue`
    for what the seven sibling `value_*` fields it replaces were costing.
    """

    model_config = ConfigDict(extra="forbid")
    path: str = Field(pattern=r"^/[a-zA-Z0-9_/-]+$")
    operation: Literal["replace", "add", "remove"]
    reason: str = Field(min_length=1, max_length=240)
    #: Last of the four properties on purpose. Strict structured output emits
    #: them in declaration order, so nothing follows a value the model has
    #: just written and there is nowhere left to stall.
    value: AnyChangeValue | None = None

    @model_validator(mode="after")
    def validate_value_shape(self) -> "ProjectChange":
        if self.operation == "remove":
            if self.value is not None:
                raise ValueError(f"{self.path}: a remove must not carry a value")
        elif self.value is None:
            raise ValueError(f"{self.path}: {self.operation} needs a value")
        return self

    @property
    def applied_value(self) -> Any:
        """The plain JSON `apply_proposal` writes into the document.

        Named apart from `value` because `value` is now the declared variant,
        and every consumer -- the applier, the diff -- wants what the variant
        stands for rather than the wrapper carrying it.
        """
        return None if self.value is None else self.value.json_value()


class ProjectProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: str = Field(min_length=1, max_length=400)
    changes: list[ProjectChange] = Field(max_length=20)
    risks: list[str] = Field(default_factory=list, max_length=10)
    acceptance_updates: list[str] = Field(default_factory=list, max_length=10)
    #: Which of this design's own rules the proposal made checkable from
    #: outside, and why the rest were left uncheckable.
    #:
    #: On the proposal rather than in `game.yml`, because it is a sentence
    #: about a decision, not part of the design: a person reading the finished
    #: document should find the observables, not the deliberation that chose
    #: them. It is here rather than folded into `summary` because `drafting`
    #: reads it as a gate -- a draft that declares no observables and says
    #: nothing about why is sent back once -- and a gate cannot find its
    #: subject inside a free-form paragraph about everything else.
    #:
    #: Defaulted, so the two other producers of a `ProjectProposal` -- the
    #: designer adapting to a dossier, and the TUI's ad-hoc planner -- are not
    #: made to answer a question nobody asked them; strict structured output
    #: still puts the field in front of every one of them, which is the point
    #: for the one that is asked.
    observability: str = Field(default="", max_length=600)


class ResponsesProjectPlanner:
    def __init__(self, client: Any, model: str = "claude-opus-5") -> None:
        self.client = client
        self.model = model

    def propose(self, project: GameProject, request: str) -> ProjectProposal:
        return structured(
            self.client,
            self.model,
            system=(
                "You are a game designer for constrained Z80 computers. "
                "Propose small JSON-pointer changes to the supplied GameProject. "
                "Never emit C code and never silently relax budgets or acceptance tests. "
                "Each change carries its value in `value`, as an object naming "
                'the shape it is: {"text": ...} for strings such as '
                "presentation.style, a mechanic's sentence or an entity's notes, "
                '{"number": ...} for integers such as an entity\'s count, '
                '{"rows": [...]} for a screen\'s tiles (one string per row) or the '
                'whole mechanics list, {"spawns": [...]} for a screen\'s spawns, and '
                '{"palette": [...]} for the design\'s whole colour list. '
                "Leave `value` null for a remove, and set it for an add or a replace."
            ),
            user=f"REQUEST:\n{request}\n\nPROJECT:\n{project.model_dump_json(indent=2)}",
            schema=ProjectProposal,
            missing="the model did not return a structured project proposal",
        )


PROTECTED_PATHS = ("/schema_version", "/metadata/slug", "/target/platform", "/acceptance")


def proposal_diff(proposal: ProjectProposal) -> str:
    """Return a stable human-readable preview suitable for TUI approval."""
    lines = [proposal.summary]
    for change in proposal.changes:
        value = "" if change.operation == "remove" else f" = {change.applied_value!r}"
        lines.append(f"{change.operation.upper():7} {change.path}{value}\n         {change.reason}")
    if proposal.observability.strip():
        # Shown to whoever approves the diff, because "this design declares no
        # observables and here is why" is a decision a person may disagree
        # with, and the changes list cannot show a symbol that was considered
        # and not declared.
        lines.append("OBSERVABILITY")
        lines.append(proposal.observability.strip())
    if proposal.risks:
        lines.append("RISKS")
        lines.extend(f"- {risk}" for risk in proposal.risks)
    return "\n".join(lines)


def apply_proposal(
    project: GameProject,
    proposal: ProjectProposal,
    *,
    allow_budget_changes: bool = False,
    allow_unplayable: bool = False,
) -> GameProject:
    """Apply a reviewed proposal transactionally and revalidate the complete IR.

    `GameProject.model_validate` itself already refuses a screen that outgrows
    its target's playable grid (see `structure._fit_errors`), so a change that
    survives to `candidate` below is already a structurally valid document.
    What remains to check is whether the design still fits the target machine
    at all (`editing.editing_status`) -- the same check a person editing by
    hand gets to see live, one cell at a time, that a bulk change from a model
    does not, so it is refused here unless the caller opts in.
    """
    document = deepcopy(project.model_dump(mode="json"))
    for change in proposal.changes:
        if any(
            change.path == path or change.path.startswith(path + "/") for path in PROTECTED_PATHS
        ):
            raise ValueError(f"AI proposals cannot change protected path {change.path}")
        if change.path.startswith("/budgets/") and not allow_budget_changes:
            raise ValueError("budget changes require explicit approval")
        tokens = [_unescape(token) for token in change.path.lstrip("/").split("/")]
        if not tokens or any(token == "" for token in tokens):
            raise ValueError(f"invalid proposal path: {change.path}")
        parent: Any = document
        for token in tokens[:-1]:
            if isinstance(parent, list):
                parent = parent[_list_index(token, len(parent), allow_end=False)]
            elif isinstance(parent, dict) and token in parent:
                parent = parent[token]
            else:
                raise ValueError(f"proposal path does not exist: {change.path}")
        leaf = tokens[-1]
        if isinstance(parent, list):
            index = _list_index(leaf, len(parent), allow_end=change.operation == "add")
            if change.operation == "add":
                parent.insert(index, deepcopy(change.applied_value))
            elif change.operation == "replace":
                parent[index] = deepcopy(change.applied_value)
            else:
                parent.pop(index)
        elif isinstance(parent, dict):
            exists = leaf in parent
            if change.operation == "add":
                if exists:
                    raise ValueError(f"add target already exists: {change.path}")
                parent[leaf] = deepcopy(change.applied_value)
            elif change.operation == "replace":
                if not exists:
                    raise ValueError(f"replace target does not exist: {change.path}")
                parent[leaf] = deepcopy(change.applied_value)
            else:
                if not exists:
                    raise ValueError(f"remove target does not exist: {change.path}")
                del parent[leaf]
        else:
            raise ValueError(f"proposal parent is not a container: {change.path}")
    candidate = GameProject.model_validate(document)
    if not allow_unplayable:
        status = editing_status(candidate)
        if not status["ready"]:
            raise ValueError(
                "this proposal would leave the game unplayable: " + status["backend_error"]
            )
    return candidate


def _unescape(token: str) -> str:
    return token.replace("~1", "/").replace("~0", "~")


def _list_index(token: str, length: int, *, allow_end: bool) -> int:
    if token == "-" and allow_end:
        return length
    if not token.isdigit():
        raise ValueError(f"invalid list index: {token}")
    index = int(token)
    maximum = length if allow_end else length - 1
    if index < 0 or index > maximum:
        raise ValueError(f"list index out of range: {token}")
    return index


def repair_feedback(error: ValueError) -> str:
    """Turn a refusal from `apply_proposal` into an instruction the model can
    act on, the way `generator.repair_prompt` turns a failed build or a wrong
    reading into one.

    The two shapes `apply_proposal` raises deserve different handling. A
    `pydantic.ValidationError` names the exact fields that ended up outside
    their bounds once the changes were applied -- `presentation.style` too
    long, `entities.1.count` below its minimum -- so it is unpacked field by
    field rather than passed through as one opaque message. Everything else
    -- a protected path, a bad JSON pointer, the playability gate's refusal --
    already reads as a sentence a person wrote, so it is quoted whole and
    paired with what to do about it.

    Lives here, beside the function whose refusals it translates, rather than
    in `reference_design` where it was written: `drafting` needs the same
    translation, and neither stage should have to import the other to get it.
    """
    if isinstance(error, ValidationError):
        lines = [
            "THE PROPOSAL WAS REFUSED: THESE FIELDS ENDED UP OUTSIDE THEIR BOUNDS",
            "",
        ]
        for item in error.errors():
            path = "/" + "/".join(str(part) for part in item["loc"])
            lines.append(f"  {path}: {item['msg']}")
        lines.append("")
        lines.append(
            "Rewrite only the changes that set these fields so the result stays inside "
            "each bound. Leave every other change exactly as it was."
        )
        return "\n".join(lines)
    message = str(error)
    if message.startswith("this proposal would leave the game unplayable"):
        return (
            "THE PROPOSAL WAS REFUSED: IT WOULD LEAVE THE GAME UNPLAYABLE\n\n"
            + message
            + "\n\nPropose a screen that fits the target's playable grid instead -- a "
            "smaller width or height, or terrain that still fits the one already "
            "declared. Do not repeat the change that caused this."
        )
    return (
        "THE PROPOSAL WAS REFUSED\n\n"
        + message
        + "\n\nRemove or rework whichever change is responsible and propose again."
    )


@dataclass
class AppliedProposal:
    """What a repair loop produced: the proposal that finally applied, the
    project `apply_proposal` already built while checking it, and the refusal
    each earlier attempt drew, oldest first."""

    proposal: ProjectProposal
    project: GameProject
    refusals: list[str] = field(default_factory=list)


def propose_apply_repair(
    project: GameProject,
    propose: Callable[[str | None], ProjectProposal],
    review: Callable[[GameProject], tuple[str, str] | None],
    *,
    attempts: int = 3,
    allow_budget_changes: bool = False,
    allow_unplayable: bool = False,
    refusal: type[ValueError] = ValueError,
) -> AppliedProposal:
    """Ask for a proposal, apply it, and feed back whatever refused it.

    A mechanically refused proposal is repaired rather than discarded whole --
    the way `generator.write_program` repairs a program that failed to build
    rather than giving up on the first rejection.

    `apply_proposal` never mutates `project` or touches disk; it only builds
    and validates a candidate `GameProject` in memory. That means the loop can
    run to a validated result before anyone has agreed to anything, and the
    project this returns is exactly the one a caller would get by calling
    `apply_proposal` again with the same inputs -- so a caller who wants
    consent first can show the diff, ask, and on "yes" use the project already
    computed here instead of redoing the work.

    Applying cleanly is not the same as being any good, which is why `review`
    exists and is the second reason to try again. It sees the candidate and
    answers with the refusal to record and the feedback to send back, or None
    to accept. Both stages that run this loop -- `reference_design` adapting a
    design to a dossier, `drafting` writing one from a brief -- differ in
    exactly two things: what they hand their collaborator (hence `propose`
    being a closure over it rather than a fixed argument list) and what they
    will accept (hence `review`). Sharing the rest is what keeps a fix to the
    repair behaviour from having to be made twice.

    Raises `refusal` carrying the last refusal reason once attempts run out,
    so a user who burned several model calls learns what finally went wrong
    rather than getting a generic failure. Callers pass their own subclass of
    `ValueError` when they need it told apart from every other refusal a
    stage can raise.
    """
    refusals: list[str] = []
    feedback: str | None = None
    for _ in range(max(1, attempts)):
        proposal = propose(feedback)
        try:
            updated = apply_proposal(
                project,
                proposal,
                allow_budget_changes=allow_budget_changes,
                allow_unplayable=allow_unplayable,
            )
        except ValueError as exc:
            refusals.append(str(exc))
            feedback = repair_feedback(exc)
            continue
        verdict = review(updated)
        if verdict is not None:
            recorded, feedback = verdict
            refusals.append(recorded)
            continue
        return AppliedProposal(proposal=proposal, project=updated, refusals=refusals)
    raise refusal(
        f"the proposal could not be repaired in {attempts} attempt"
        f"{'s' if attempts != 1 else ''}; the last refusal was: " + refusals[-1]
    )
