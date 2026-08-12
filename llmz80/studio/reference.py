"""What is known about the real game a brief names, and where it was read.

Studio's typologies give a design its shape; this gives it its identity. The
dossier is deliberately prose-heavy: a model writing a program reads sentences
better than it reads enum values, and a person correcting a wrong dossier edits
sentences more happily than fields.

Every claim carries its sources, and a dossier that claims to have identified a
game without any is refused. An unsupported claim about a real title is worse
than admitting the title was not found, because the rest of the pipeline treats
identification as licence to rewrite the design.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Literal, Protocol

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


class ReferenceSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str = Field(min_length=1, max_length=400)
    title: str = Field(min_length=1, max_length=200)
    retrieved_at: datetime


class GameReference(BaseModel):
    """One researched game, as the rest of Studio needs it."""

    model_config = ConfigDict(extra="forbid")

    identified: bool
    confidence: Literal["high", "medium", "low"]
    title: str = Field(default="", max_length=120)
    publisher: str = Field(default="", max_length=120)
    year: int | None = Field(default=None, ge=1975, le=1999)
    platforms: list[str] = Field(default_factory=list, max_length=8)
    mechanics: list[str] = Field(default_factory=list, max_length=20)
    screen_layout: str = Field(default="", max_length=600)
    pacing: str = Field(default="", max_length=600)
    visual_style: str = Field(default="", max_length=600)
    level_structure: str = Field(default="", max_length=600)
    sources: list[ReferenceSource] = Field(default_factory=list, max_length=10)

    @model_validator(mode="after")
    def validate_identification(self) -> "GameReference":
        if self.identified and not self.sources:
            raise ValueError(
                "an identified game must cite its sources; "
                "without them the dossier cannot be checked or corrected"
            )
        if self.identified and not self.title.strip():
            raise ValueError("an identified game must have a title")
        return self


#: Beside game.yml, and just as editable by hand.
REFERENCE_FILENAME = "reference.yml"


def save_reference(dossier: GameReference, directory: Path) -> Path:
    """Archive the dossier atomically, so a crash leaves the old one intact."""
    directory = Path(directory).expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / REFERENCE_FILENAME
    text = yaml.safe_dump(
        dossier.model_dump(mode="json"), allow_unicode=True, sort_keys=False, width=100
    )
    temporary = path.with_suffix(".yml.tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)
    return path


def load_reference(directory: Path) -> GameReference | None:
    """Read the archived dossier, or None when the project has none.

    A malformed file raises: a project that has a dossier and cannot read it is
    not the same as a project without one, and treating them alike would quietly
    rebuild a design from a blank. Only content failures are turned into that
    ValueError, though — bad YAML or a document that fails validation. A
    filesystem problem such as a permissions error is a different kind of
    failure with a different remedy, so it propagates as itself instead of
    being relabelled as a broken dossier.
    """
    path = Path(directory).expanduser().resolve() / REFERENCE_FILENAME
    if not path.exists():
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return GameReference.model_validate(data)
    except (yaml.YAMLError, ValidationError) as exc:
        raise ValueError(f"cannot read {path.name}: {exc}") from exc


#: What the researcher is told before it looks anything up. It is told to admit
#: failure explicitly because a model asked to describe a game it cannot find
#: will describe a plausible game instead, and a plausible game is exactly the
#: failure this whole stage exists to prevent.
RESEARCH_SYSTEM_PROMPT = """\
You research games published for 8-bit home computers in the 1980s, chiefly the
ZX Spectrum and the Amstrad CPC.

Search the web for the game the brief names. Report only what your sources
support, and cite every source you used.

If you cannot find the game, or you are not confident that what you found is the
same game the brief means, set identified to false and confidence to low, and
leave every other field at its default: nothing guessed, nothing invented, no
partial credit for a game you are not sure of. Do not describe a game you did
not find. A wrong dossier is worse than no dossier, because the rest of the
system will rebuild the design from it.

When you do identify the game, describe mechanics, pacing, screen layout and
visual style in short plain sentences that a programmer can act on, not in
marketing prose.
"""


def reference_prompt(dossier: GameReference | None) -> str:
    """The dossier as a prompt block, or nothing at all.

    An unidentified dossier yields nothing rather than a block saying so: the
    absence of a reference is already the default, and a paragraph explaining
    that there is no reference only spends attention.
    """
    if dossier is None or not dossier.identified:
        return ""
    lines = ["REFERENCE GAME", ""]
    # An identified game with an unknown publisher is a real case for this era
    # -- magazine type-ins, self-published titles -- so both known facts are
    # joined and either may be missing. A blank clause, or a bare ", 1985" or
    # empty "()", would be a wrong sentence rather than a shorter true one.
    year = str(dossier.year) if dossier.year else ""
    known = [part for part in (dossier.publisher, year) if part]
    on_publisher = f" ({', '.join(known)})" if known else ""
    on_platforms = f" for {', '.join(dossier.platforms)}" if dossier.platforms else ""
    lines.append(f"{dossier.title}{on_publisher}{on_platforms}.")
    lines.append(
        "Match this game's look, pacing and feel where the design allows it. "
        "The design below, not this dossier, is the authority on what the game is."
    )
    # Mechanics is a list rendered as its own bullets, so it is kept out of the
    # generic single-string loop below: that loop's "already multi-line, so
    # leave it alone" check would otherwise re-indent a lone bullet on top of
    # the indent it already has.
    if dossier.mechanics:
        lines.extend(["", "How it plays:"])
        lines.extend(f"  - {rule}" for rule in dossier.mechanics)
    for heading, value in (
        ("Screen layout", dossier.screen_layout),
        ("Pacing", dossier.pacing),
        ("Look", dossier.visual_style),
        ("Levels", dossier.level_structure),
    ):
        if value.strip():
            lines.extend(["", f"{heading}:", value if "\n" in value else f"  {value}"])
    lines.extend(["", f"Researched from: {', '.join(source.url for source in dossier.sources)}"])
    return "\n".join(lines)


class ReferenceResearcher(Protocol):
    def research(self, brief: str, target: str) -> GameReference: ...


class ResponsesReferenceResearcher:
    """Researches through the OpenAI Responses API with web search enabled."""

    def __init__(self, client: Any, model: str = "gpt-5") -> None:
        self.client = client
        self.model = model

    def research(self, brief: str, target: str) -> GameReference:
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": RESEARCH_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"TARGET PLATFORM: {target}\n\n"
                        f"WHAT THE DESIGNER ASKED FOR:\n{brief}"
                    ),
                },
            ],
            # The pinned SDK (openai==1.75.0) types this tool as
            # web_search_preview. The API also answers to the later
            # "web_search" name, but sending that makes the SDK mis-parse
            # its own request model and warn on every search. Move to the
            # newer name when the pin moves.
            tools=[{"type": "web_search_preview"}],
            text_format=GameReference,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("the model did not return a structured game reference")
        return parsed
