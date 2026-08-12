"""Does a design's authored difficulty match the curve it declares?

`GameplaySpec.difficulty_curve` is a word a designer picks -- `flat`, `linear`
or `stepped` -- and until now nothing checked it against the levels
themselves. A design can declare `linear` and ship three interchangeable
levels; the designer sees a word, the player sees no curve. This module reads
what the IR can actually say about a level's difficulty and holds the
declared curve to it, the same way `solvability_report` holds a design to
"can this be finished" and `structure_report` holds it to "does the terrain
carry its typology's shape".

What the IR can say, and what it cannot
----------------------------------------
Two measurements are available per level, both already computed elsewhere:

* route length -- `solvability.analyse_level`'s `estimated_steps`, a greedy
  nearest-first walk collecting everything reachable. Longer is more game to
  play through, which is the closest thing to "harder" the IR can prove
  without simulating a play session.
* time budget -- `LevelSpec.time_limit_seconds`, optional. A tighter limit on
  the same amount of route is a real difficulty signal where a design sets
  one; compared only where both levels being compared set one, since the
  presence or absence of a limit is a design choice this module should not
  read a direction into.

Two things that look like difficulty knobs are not, in today's schema, and
this module does not pretend otherwise:

* Enemy *count* looks like it should vary per level -- `EntitySpec.count` is
  attached to the entity, not the level, but the per-level `spawns` list
  looked like the place a design could still put "more enemies later." It
  is not: `GameProject.validate_contract` requires every level to place
  *exactly* `entity.count` instances of *every* entity in the project, and
  `editing.set_entity_count` changes a count on every level identically.
  A level cannot carry more or fewer enemies than any other level for the
  same entity roster; the schema forbids it before this module ever runs.
  Enemy presence is therefore not a measurable difficulty signal here.
* `EntitySpec.speed` belongs to the entity, not the level, so "the same
  enemy moves faster on level 3" cannot be written down at all. There is
  nothing to measure.

Both are stated limitations, not gaps this module papers over with a guess.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import GameProject
from .solvability import analyse_level

#: Curve values that demand later levels are never easier *and* that
#: something measurably increases somewhere across the design. `stepped`
#: is not distinguished from `linear` here: both signals this module has
#: (route length, time budget) are plain scalars, so a discrete jump and a
#: smooth increase read identically from them. Distinguishing "smooth" from
#: "stepped" would need more levels' worth of shape than three typically
#: gives, and would be a guess this module is not in the business of making.
CURVES_REQUIRING_INCREASE = frozenset({"linear", "stepped"})


@dataclass(frozen=True)
class LevelDifficulty:
    level_id: str
    estimated_steps: int
    time_limit_seconds: int | None

    def as_dict(self) -> dict:
        return {
            "level": self.level_id,
            "estimated_steps": self.estimated_steps,
            "time_limit_seconds": self.time_limit_seconds,
        }


@dataclass(frozen=True)
class LevelDifficultyDelta:
    """How one level compares to the level immediately before it."""

    from_level: str
    to_level: str
    from_steps: int
    to_steps: int
    #: Only set when both levels declare a time limit; otherwise a design
    #: choice (setting or dropping a limit) is not read as harder or easier.
    from_time_limit: int | None
    to_time_limit: int | None

    @property
    def steps_changed(self) -> int:
        return self.to_steps - self.from_steps

    @property
    def time_limit_comparable(self) -> bool:
        return self.from_time_limit is not None and self.to_time_limit is not None

    @property
    def time_limit_changed(self) -> int | None:
        if not self.time_limit_comparable:
            return None
        return self.to_time_limit - self.from_time_limit

    @property
    def easier(self) -> bool:
        """Route shrinks, or a shared time limit loosens."""
        if self.steps_changed < 0:
            return True
        changed = self.time_limit_changed
        return changed is not None and changed > 0

    @property
    def harder(self) -> bool:
        """Route grows, or a shared time limit tightens."""
        if self.steps_changed > 0:
            return True
        changed = self.time_limit_changed
        return changed is not None and changed < 0

    def as_dict(self) -> dict:
        return {
            "from_level": self.from_level,
            "to_level": self.to_level,
            "from_steps": self.from_steps,
            "to_steps": self.to_steps,
            "from_time_limit_seconds": self.from_time_limit,
            "to_time_limit_seconds": self.to_time_limit,
            "easier": self.easier,
            "harder": self.harder,
        }


@dataclass
class DifficultyReport:
    curve: str
    levels: list[LevelDifficulty] = field(default_factory=list)
    deltas: list[LevelDifficultyDelta] = field(default_factory=list)

    @property
    def regressions(self) -> list[LevelDifficultyDelta]:
        return [delta for delta in self.deltas if delta.easier]

    @property
    def advances(self) -> list[LevelDifficultyDelta]:
        return [delta for delta in self.deltas if delta.harder]

    @property
    def honored(self) -> bool:
        """Whether the authored levels back up the declared curve.

        A single-level design has no pair to compare and passes vacuously --
        there is nothing in one level that could contradict any curve.
        """
        if self.regressions:
            return False
        if self.curve in CURVES_REQUIRING_INCREASE and self.deltas and not self.advances:
            return False
        return True

    @property
    def failures(self) -> list[str]:
        """Human-readable reasons, distinguishing "got easier" from "never got
        harder" -- a designer can act on either, but they call for different
        fixes, and collapsing them into one message would hide which."""
        reasons: list[str] = []
        for delta in self.regressions:
            parts = []
            if delta.steps_changed < 0:
                parts.append(
                    f"route shortens from {delta.from_steps} to {delta.to_steps} steps"
                )
            changed = delta.time_limit_changed
            if changed is not None and changed > 0:
                parts.append(
                    f"time limit loosens from {delta.from_time_limit}s to "
                    f"{delta.to_time_limit}s"
                )
            reasons.append(
                f"{delta.to_level} is easier than {delta.from_level}: " + "; ".join(parts)
            )
        if self.curve in CURVES_REQUIRING_INCREASE and self.deltas and not self.advances:
            steps = ", ".join(str(level.estimated_steps) for level in self.levels)
            reasons.append(
                f"declared '{self.curve}' but no level is ever harder than the one before "
                f"it -- route length across levels stays {steps} and no time limit tightens"
            )
        return reasons

    def as_dict(self) -> dict:
        return {
            "schema_version": 1,
            "curve": self.curve,
            "honored": self.honored,
            "failures": self.failures,
            "levels": [level.as_dict() for level in self.levels],
            "deltas": [delta.as_dict() for delta in self.deltas],
        }


def difficulty_report(project: GameProject) -> DifficultyReport:
    levels = [
        LevelDifficulty(
            level_id=level.id,
            estimated_steps=analyse_level(project, level).estimated_steps,
            time_limit_seconds=level.time_limit_seconds,
        )
        for level in project.levels
    ]
    deltas = [
        LevelDifficultyDelta(
            from_level=previous.level_id,
            to_level=current.level_id,
            from_steps=previous.estimated_steps,
            to_steps=current.estimated_steps,
            from_time_limit=previous.time_limit_seconds,
            to_time_limit=current.time_limit_seconds,
        )
        for previous, current in zip(levels, levels[1:])
    ]
    return DifficultyReport(curve=project.gameplay.difficulty_curve, levels=levels, deltas=deltas)
