"""Structured AI proposals; the model never writes C or replaces game.yml."""

from __future__ import annotations

from typing import Any, Callable, Literal
from copy import deepcopy
from dataclasses import dataclass, field

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from .editing import editing_status
from .models import GameProject


class SpawnValue(BaseModel):
    """Mirrors `SpawnSpec` in models.py: where one entity instance starts on
    one of the design's screens."""

    model_config = ConfigDict(extra="forbid")
    entity: str = Field(pattern=r"^[a-z][a-z0-9_]{1,31}$")
    col: int = Field(ge=0, le=39)
    row: int = Field(ge=0, le=24)


class EntityValue(BaseModel):
    """One whole entity, in the shape `EntitySpec` validates.

    Flat and with every field concrete, for the reason `ProjectChange`'s own
    docstring gives: structured outputs reject a property with no JSON type,
    which is why there is no generic `value` and why `SpawnValue` exists. An
    entity is the first thing a proposal ever needed to *add* rather than
    edit -- the designer only ever touched `/entities/N/notes` of an entity
    that was already there -- and a design that states nothing has none.

    The defaults mirror `EntitySpec`'s own, so a drafter that names only an id
    and a kind gets exactly what a designer writing the same two fields by
    hand would get.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    kind: str
    sprite: str | None = None
    poses: list[str] = Field(default_factory=list)
    count: int = 1
    colour: str | None = None
    notes: str = ""


class TileValue(BaseModel):
    """One whole tile, in the shape `TileSpec` validates.

    Here for the same reason as `EntityValue`: a design that states nothing
    has two tiles, and terrain the brief asks for -- water, lava, a ladder --
    is a tile the design has to grow, not a field of one it already declares.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    char: str
    art: str | None = None
    colour: str | None = None
    traits: list[str] = Field(default_factory=list)


class ObservableValue(BaseModel):
    """One whole observable, in the shape `ObservableSpec` validates.

    Its own field for the reason `ProjectChange`'s docstring gives -- strict
    structured output rejects a property with no concrete JSON type, so there
    is no generic `value` to put it in -- and its own *shape* because an
    observable is neither an entity nor a tile: it is a C symbol, a width in
    bytes and a sentence saying what the number means.

    A design that declares one is the only way a gate can witness a rule the
    state contract has no word for. Nothing had ever declared one: `game.yml`
    could carry observables since schema v4 and no stage could propose them,
    so the four finished games in `studio-projects/` were judged entirely on
    `g_score`, `g_state` and their siblings, and not one of their own
    mechanics was checked.
    """

    model_config = ConfigDict(extra="forbid")

    symbol: str
    #: Bytes to read out of memory. Mirrors `ObservableSpec`'s own default
    #: rather than being required, so a drafter naming a counter it has not
    #: thought about the range of gets the one-byte reading a hand-written
    #: design would get.
    width: int = 1
    meaning: str


class ProjectChange(BaseModel):
    """One JSON-pointer edit.

    `value` is not a field: OpenAI's strict structured output requires every
    property to carry a concrete JSON Schema type, and `Any` has none. Each
    shape a design edit actually needs gets its own optional field instead, and
    `value` becomes a read-only property over whichever one is set, so callers
    keep reading a single thing.
    """

    model_config = ConfigDict(extra="forbid")
    path: str = Field(pattern=r"^/[a-zA-Z0-9_/-]+$")
    operation: Literal["replace", "add", "remove"]
    reason: str = Field(min_length=1, max_length=240)
    value_text: str | None = None
    value_number: int | None = None
    value_rows: list[str] | None = None  # a screen's tiles
    value_spawns: list[SpawnValue] | None = None  # a screen's spawns
    value_entity: EntityValue | None = None  # a whole entity
    value_tile: TileValue | None = None  # a whole tile
    value_observable: ObservableValue | None = None  # a whole observable

    @model_validator(mode="after")
    def validate_value_shape(self) -> "ProjectChange":
        variants = [
            v
            for v in (
                self.value_text,
                self.value_number,
                self.value_rows,
                self.value_spawns,
                self.value_entity,
                self.value_tile,
                self.value_observable,
            )
            if v is not None
        ]
        if self.operation == "remove":
            if variants:
                raise ValueError(f"{self.path}: a remove must not carry a value")
        elif len(variants) != 1:
            raise ValueError(
                f"{self.path}: {self.operation} needs exactly one value_* field set, "
                f"found {len(variants)}"
            )
        return self

    @property
    def value(self) -> Any:
        if self.value_text is not None:
            return self.value_text
        if self.value_number is not None:
            return self.value_number
        if self.value_rows is not None:
            return self.value_rows
        if self.value_spawns is not None:
            return [spawn.model_dump(mode="json") for spawn in self.value_spawns]
        if self.value_entity is not None:
            return self.value_entity.model_dump(mode="json")
        if self.value_tile is not None:
            return self.value_tile.model_dump(mode="json")
        if self.value_observable is not None:
            return self.value_observable.model_dump(mode="json")
        return None


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
    def __init__(self, client: Any, model: str = "gpt-5") -> None:
        self.client = client
        self.model = model

    def propose(self, project: GameProject, request: str) -> ProjectProposal:
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a game designer for constrained Z80 computers. "
                        "Propose small JSON-pointer changes to the supplied GameProject. "
                        "Never emit C code and never silently relax budgets or acceptance tests. "
                        "Each change carries its value in exactly one of value_text, "
                        "value_number, value_rows or value_spawns, matching the field being "
                        "changed: value_text for strings such as presentation.style, a "
                        "mechanic's sentence or an entity's notes, value_number for integers "
                        "such as an entity's count, value_rows for a screen's tiles (one string "
                        "per row), and value_spawns for a screen's spawns. Leave all four unset "
                        "for a remove, and set exactly one of them for an add or a replace."
                    ),
                },
                {
                    "role": "user",
                    "content": f"REQUEST:\n{request}\n\nPROJECT:\n{project.model_dump_json(indent=2)}",
                },
            ],
            text_format=ProjectProposal,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("the model did not return a structured project proposal")
        return parsed


PROTECTED_PATHS = ("/schema_version", "/metadata/slug", "/target/platform", "/acceptance")


def proposal_diff(proposal: ProjectProposal) -> str:
    """Return a stable human-readable preview suitable for TUI approval."""
    lines = [proposal.summary]
    for change in proposal.changes:
        value = "" if change.operation == "remove" else f" = {change.value!r}"
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
                parent.insert(index, deepcopy(change.value))
            elif change.operation == "replace":
                parent[index] = deepcopy(change.value)
            else:
                parent.pop(index)
        elif isinstance(parent, dict):
            exists = leaf in parent
            if change.operation == "add":
                if exists:
                    raise ValueError(f"add target already exists: {change.path}")
                parent[leaf] = deepcopy(change.value)
            elif change.operation == "replace":
                if not exists:
                    raise ValueError(f"replace target does not exist: {change.path}")
                parent[leaf] = deepcopy(change.value)
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
