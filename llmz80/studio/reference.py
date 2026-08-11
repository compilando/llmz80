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
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


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
