"""Draw the sprites a project needs, in the style its dossier describes.

Everything downstream of this module already works: `spriting.py` packs frames
into the bytes each machine's blitter expects, `sprite_header.py` binds those
bytes into a generated `sprites.h`, and both machines blit them -- proven byte
for byte against real video memory. What has been missing is the art itself: a
project only had sprites if a human imported PNGs.

This module closes that gap. Given a project, one of its entities, and
optionally the dossier `llmz80.studio.reference` researched about a real
1980s game, it composes a request a model can answer and turns the answer into
frames `spriting.py` can pack.

**How it asks matters more than what it asks for.** This module used to send
the request to an image model, get a 1024x1024 picture back, and try to
recover a 16x16 sprite from it -- reading each frame's real background off its
own border because the model would not honour the one it was asked for,
discounting an anti-aliased halo with a tolerance derived from a per-column
histogram, cropping to the drawn pose, rescaling by a factor that preserved
proportions. Around four hundred lines, none of them about drawing: all of it
repaired damage the *output format* caused. A real run against *Abu Simbel
Profanation* still got through it with two of three sprites unrecognisable.

The model now writes the sprite directly, as a grid of palette-index
characters -- see `sprite_grid.py`, and `ClaudeGridSheetSource` below. There
is no background to detect because there is no background, no halo to discount
because a blend cannot be written, no crop because the frame is already the
frame, and no illegal colour because the alphabet is the machine's own. Nine
sprites across the Spectrum and both CPC modes were drawn on the first attempt
with nothing rejected.

What survives from the old path is everything that was never about pictures:

- `_judge_frames` refuses a frame that packs to 0 or 256 of 256 opaque pixels
  -- a blank sprite or a solid block -- as evidence the drawing failed rather
  than as a sprite to pack anyway. See its own docstring for the check this
  module tried and dropped: refusing four identical frames outright, which
  punished a correctly-drawn static sprite like a `pellet` collectible.
- `SpriteArtist.draw_frames` retries a judged failure with feedback naming
  what was wrong, up to `MAX_DRAW_ATTEMPTS` times, the way
  `generator.write_program` and `reference_design.propose_and_apply` already
  retry their own failures instead of accepting the first answer.
- Every attempt of a failed run is kept, not just a winning one -- see
  `services.StudioService._save_raw_sheet` -- because the run this evidence
  exists for is exactly the one where nothing else survives to debug it.

`SheetSource` is the seam the two paths met at, and it is kept now that only
one of them is left: a source owns how to ask and how to read the answer,
`SpriteArtist` owns when to ask again and with what. If a future source draws
sprites some third way, none of the judging or retrying is written twice.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Protocol, Sequence

import numpy as np
from PIL import Image

from llmz80.studio.llm import structured
from llmz80.studio.models import EntitySpec, GameProject, TargetPlatform, TileSpec, VideoMode
from llmz80.studio.reference import GameReference
from llmz80.studio.sprite_grid import (
    TRANSPARENT,
    GridPalette,
    SpriteSheetGrid,
    frames_from_grid,
    grid_errors,
    palette_for,
    render_grid,
)
from llmz80.studio.spriting import ALPHA_THRESHOLD, SPRITE_SIZE, TILE_SIZE

#: How many poses a sheet holds when the design named none. One: a ball, a
#: bullet, a paddle, a block. Most things in most games do not animate.
#:
#: This was four, for every sprite in every design, and it cost a real run.
#: A Breakout for the CPC built, booted and played correctly and was refused
#: five times, three of them because `g_anim_frame` never advanced -- which
#: was true, and which the gate was right to say, because `sprite_frames[]`
#: read `{4, 4}` and the art really did carry four poses. The design had
#: declared `poses: []` for both its entities. A ball had been given a walk
#: cycle it has no use for and then failed for not walking.
POSES_WHEN_UNDECLARED = 1


def poses_wanted(entity: "EntitySpec") -> int:
    """How many poses this entity's sheet should hold.

    `EntitySpec.poses` has existed since schema v4, documented as "named poses
    the artwork carries: walk, jump, die", and nothing read it. This is what
    reads it. A design that names none gets one frame, which is what a thing
    that does not animate needs.
    """
    return len(entity.poses) or POSES_WHEN_UNDECLARED


def sheet_size(frames: int) -> tuple[int, int]:
    """The sheet's real, final size: `frames` frames side by side.

    Derived rather than kept as two constants, because `AssetSpec` refuses a
    sheet whose width is not a whole multiple of its frame count and the two
    numbers therefore have to come from one.
    """
    return SPRITE_SIZE * frames, SPRITE_SIZE


def animates(entities: "Iterable[EntitySpec]") -> bool:
    """Whether anything here has more than one pose to cycle.

    Takes the entities rather than the project, for the reason `probes._wanted`
    gives for taking a mapping rather than one: the question needs nothing else,
    and a narrow input is one a test can ask without building a whole valid
    document around it.

    One `g_anim_frame` serves the whole program, so one animated actor is
    enough to give `feel.animation_report` something to judge -- and a design
    where nothing animates gives it nothing, which is what it now abstains on
    rather than demanding a counter move for no visible reason.

    An entity carrying no sprite is not counted however many poses it names:
    poses on artwork that does not exist animate nothing.
    """
    return any(entity.sprite is not None and poses_wanted(entity) > 1 for entity in entities)


#: How many times `SpriteArtist.draw_frames` will ask the model again after a
#: judged failure (see `_judge_frames`) before giving up. Set against its two
#: siblings, not picked in isolation: `generator.write_program` gets five
#: attempts because a failed build's diagnostics are concrete and cheap to
#: react to; `reference_design.propose_and_apply` gets three because a
#: refused proposal is validated locally, with no external call in the
#: repair itself. A judged sprite failure sits between them: every attempt
#: costs a model call, and the feedback a judged failure gives ("this frame
#: is a solid block") is coarser than a compiler diagnostic, so there is
#: little reason to expect attempt five to do better than attempt three
#: would not already have shown. Three attempts -- one real chance to
#: recover from a one-off bad draw, plus one more in case the first repair
#: overcorrects.
MAX_DRAW_ATTEMPTS = 3

#: Prompt templates, one per target/mode, live beside the other Studio
#: resources (`resources/genres.yml`, `resources/studio_lib`, ...). Each
#: encodes real knowledge about what its machine can show -- monochrome on
#: the Spectrum, double-width pixels in CPC mode 0 -- so this module reads
#: them rather than restating those constraints itself.
_RESOURCES = Path(__file__).resolve().parents[2] / "resources"


def _dossier_style_block(dossier: GameReference) -> str:
    """Only the visual half of an identified dossier, phrased so it reads as
    inspiration for the *referenced* game's own screen -- never as an
    instruction for the sheet being drawn right now.

    `reference_prompt` (see `reference.py`) renders far more than is any use
    here: mechanics, pacing, screen layout and level
    structure are about how the *game* plays, not about one small sprite
    sheet's look, and its trailing "Researched from: <urls>" line exists for
    a person auditing the dossier, not for a model. Reusing that block here
    verbatim would put gameplay prose and a list of links at the very end of
    the prompt -- the position a model reads with the most weight -- crowding
    out the one thing that actually has to land there instead, the pipeline's
    own technical constraints (see `_grid_contract`). This function
    keeps only `title`/`publisher`/`year` (for context) and `visual_style`
    (the only field that is actually about how something looks), and states
    outright that the description is of the referenced game's own screen, not
    of this sheet. `reference_prompt` itself is untouched -- the program
    writer (`generator.py`) still relies on its full, source-cited form.
    """
    year = str(dossier.year) if dossier.year else ""
    known = [part for part in (dossier.publisher, year) if part]
    on_publisher = f" ({', '.join(known)})" if known else ""
    lines = [
        "REFERENCE GAME",
        "",
        f"This project is inspired by {dossier.title}{on_publisher}.",
    ]
    if dossier.visual_style.strip():
        lines.extend(["", "How that game looked on its own screen:", f"  {dossier.visual_style}"])
    lines.extend(
        [
            "",
            "That description is of the referenced game, on its own screen -- it "
            "does not describe the sheet you are drawing now. See TECHNICAL "
            "REQUIREMENTS below for what this sheet itself must look like; those "
            "requirements win over anything above.",
        ]
    )
    return "\n".join(lines)


def _style_context(project: GameProject, entity: EntitySpec, dossier: GameReference | None) -> str:
    """What is known about how this should look.

    An identified dossier renders through `_dossier_style_block`; an
    unidentified dossier and no dossier at all fall through to the same
    fallback here, which is correct: an unidentified dossier's `visual_style`
    and `publisher` are themselves blank (see `RESEARCH_SYSTEM_PROMPT`), so
    there would be nothing to carry either way. The fallback still has to
    describe *some* style, because a project with no identified game still
    needs art: it draws on the one thing every project always has, its own
    design -- the entity's `kind` and the design's `presentation.style`.
    """
    if dossier is not None and dossier.identified:
        return _dossier_style_block(dossier)
    return (
        "REFERENCE GAME\n\n"
        "No specific 1980s game has been identified for this project, so draw "
        f"from the design itself: this is a {entity.kind} entity, and the "
        f'game\'s overall visual style is described as "{project.presentation.style}".'
    )


#: The heading `_technical_constraints` opens with. Named so the ordering
#: test can find it without duplicating the literal string, and so a future
#: edit to the wording cannot silently break the test that pins its position.
TECHNICAL_REQUIREMENTS_HEADING = "TECHNICAL REQUIREMENTS"


def _grid_template_filename(project: GameProject) -> str:
    """The grid-path sibling of `_template_filename`.

    Separate files rather than a rewrite of the image-path templates: those
    are still what `ImageModelSheetSource` sends, and the two say genuinely
    different things -- one asks for a picture with a white background and
    no anti-aliasing, the other asks for characters, where a background and
    a blend are not expressible in the first place.
    """
    target = project.target
    if target.platform is TargetPlatform.SPECTRUM:
        return "sprite_grid_spectrum.txt"
    if target.video_mode is VideoMode.CPC_MODE_0:
        return "sprite_grid_amstrad_cpc_mode0.txt"
    return "sprite_grid_amstrad_cpc_mode1.txt"


#: Everything the sprite artist is told about its job, as opposed to about
#: this particular sprite. Deliberately short: the machine's own character
#: is in `resources/sprite_grid_*.txt` and the subject is in the user turn,
#: and repeating either here would only make the two disagree eventually.
GRID_SYSTEM_PROMPT = """\
You are a pixel artist for 8-bit home computers. You draw sprites directly,
as grids of characters, one character per pixel -- not as pictures of
sprites.

You are drawing at a size where every single pixel is a decision. A sprite
this small is read as a silhouette before it is read as anything else, so
the shape has to be recognisable with all detail stripped out. Detail that
does not survive at this size is not detail, it is noise.

Across the frames of one sheet you are drawing the same character, moving.
The frames should differ enough that a cycle through them reads as motion --
a leg forward then back, wings up then down -- and not so much that they
read as different characters.\
"""


def _grid_contract(palette: GridPalette, frames: int) -> str:
    """The one part of the request that is not negotiable, stated last.

    Same position and same reason as `_technical_constraints` on the image
    path -- what is read last carries most weight, and a reference game's
    style note must not be the final word. What differs is how much has to
    be said: on this path a wrong colour or a blended edge cannot be
    expressed, so the contract is only about shape and alphabet, and every
    line of it is checked by `sprite_grid.grid_errors` rather than hoped for.
    """
    pens = "\n".join(f"  '{index}' = RGB{pen}" for index, pen in enumerate(palette.pens))
    return (
        f"{TECHNICAL_REQUIREMENTS_HEADING} (these apply no matter what any style note "
        "above says, and override it where the two disagree):\n\n"
        f"- Exactly {frames} frame{'s' if frames != 1 else ''}.\n"
        f"- Each frame is exactly {SPRITE_SIZE} rows of exactly {SPRITE_SIZE} "
        "characters. Not one more, not one fewer, on any row of any frame.\n"
        f"- The only characters allowed are '{TRANSPARENT}' and "
        f"{', '.join(repr(character) for character in palette.alphabet)}.\n\n"
        "PENS:\n"
        f"  '{TRANSPARENT}' = transparent; the background shows through\n"
        f"{pens}\n\n"
        "No frame may be entirely transparent, and no frame may be entirely "
        "filled -- the first draws nothing and the second is a solid block, "
        "not a shape."
    )


def compose_grid_prompt(
    project: GameProject,
    entity: EntitySpec,
    dossier: GameReference | None,
    palette: GridPalette,
) -> str:
    """The request `ClaudeGridSheetSource` draws one entity's sheet from.

    The same four-part shape as `compose_prompt`, and for the same reasons
    (see its docstring): the machine, the sheet being asked for, what is
    known about how this should look, and last the contract that has to win.
    `_style_context` is shared between the two paths untouched -- what an
    entity is and what a referenced game looked like are facts about the
    subject, not about the output format.
    """
    template = (_RESOURCES / _grid_template_filename(project)).read_text(encoding="utf-8")
    subject = f"{entity.sprite}, a {entity.kind} character"
    if entity.notes.strip():
        subject += f" ({entity.notes.strip()})"
    body = template.format(prompt=subject, width=SPRITE_SIZE, height=SPRITE_SIZE)
    frames = poses_wanted(entity)
    # A single-pose subject is asked for a picture, not for a cycle. Saying
    # "one animation cycle" in front of a request for one frame is a
    # contradiction the model has to resolve by guessing, and what it guessed
    # was four.
    if frames == 1:
        sheet = (
            f"Draw this character once, {SPRITE_SIZE}x{SPRITE_SIZE} pixels. It does "
            "not animate: one pose is all the design asked for."
        )
    else:
        named = ", ".join(entity.poses)
        sheet = (
            f"Draw {frames} frames of this same character: one animation cycle, in "
            f"order, each frame {SPRITE_SIZE}x{SPRITE_SIZE} pixels. The design named "
            f"these poses, in this order: {named}."
        )
    return "\n\n".join(
        [body, sheet, _style_context(project, entity, dossier), _grid_contract(palette, frames)]
    )


class ClaudeGridSheetSource:
    """Asks the model for the sprite itself, as a grid of pen characters.

    What this does not have to do is the point of it. There is no background
    to detect because there is no background; no halo to discount because a
    blend cannot be written; no crop, because the frame is already the
    frame; no rescale, because it is already the right size; and no colour
    to quantize, because the only colours expressible are the ones the
    machine has. The failures those existed to repair are not caught here,
    they are unrepresentable.

    What is left is the failure a grid *can* have -- a row a character short,
    a frame missing, an empty pose -- and `sprite_grid.grid_errors` names it
    precisely enough for the next attempt to fix it, which is what
    `SpriteArtist.draw_frames` then does with it.
    """

    def __init__(self, client: object, model: str = "claude-opus-5") -> None:
        self.client = client
        self.model = model

    def compose(
        self, project: GameProject, entity: EntitySpec, dossier: GameReference | None
    ) -> str:
        return compose_grid_prompt(project, entity, dossier, palette_for(project))

    def draw(self, project: GameProject, request: str, *, frames: int) -> DrawnSheet:
        palette = palette_for(project)
        grid = structured(
            self.client,
            self.model,
            system=GRID_SYSTEM_PROMPT,
            user=request,
            schema=SpriteSheetGrid,
            missing="the model did not return a sprite sheet",
        )
        reason = grid_errors(grid, palette, frames_expected=frames)
        # Rendered whichever way the judgement went: a rejected sheet is
        # exactly the one somebody will want to look at, and `render_grid`
        # is built to survive the malformed input `frames_from_grid` refuses.
        sheet = render_grid(grid, palette)
        drawn = [] if reason is not None else frames_from_grid(grid, palette)
        return DrawnSheet(frames=drawn, sheet=sheet, reason=reason)


def _set_pixel_count(frame: Image.Image) -> int:
    """How many of `frame`'s pixels `spriting.py`'s packers would read as
    drawn -- the same alpha threshold `pack_spectrum`/`pack_cpc` use
    (`spriting.ALPHA_THRESHOLD`), so a frame `_judge_frames` calls valid is
    valid by the same rule the packer itself will apply to it.
    """
    alpha = np.asarray(frame.convert("RGBA"))[..., 3]
    return int(np.count_nonzero(alpha >= ALPHA_THRESHOLD))


def _solid_or_blank_feedback(bad: list[tuple[int, int]], total: int) -> str:
    lines = ["THE SHEET WAS REJECTED: THESE FRAMES ARE NOT A SPRITE", ""]
    for index, count in bad:
        kind = "a solid block" if count == total else "blank"
        lines.append(f"  frame {index + 1}: {kind} -- {count} of {total} pixels opaque")
    lines.append("")
    lines.append(
        "A pixel count of 0 or 256 means the whole frame was read as either all "
        "background or all figure -- not a drawn silhouette with a real edge. This "
        "happens when the background is not the unmistakably pure white asked for "
        "(a dark or grey background reads as figure everywhere), or when the figure "
        "leaves no background gap around it at all (reads as background everywhere)."
    )
    lines.append("")
    lines.append(
        "Redraw the sheet on an unmistakably pure white background (RGB 255,255,255) "
        "with nothing else behind the figure -- no shading, no texture, no near-white "
        "or near-black grey standing in for white -- and leave a visible gap of "
        "background around each figure."
    )
    return "\n".join(lines)


#: Told what is happening while it happens -- see `services.Progress` for the
#: same alias and the reason it exists. Defined again here, rather than
#: imported, because `services.py` imports *this* module (`SpriteArtist`);
#: importing back the other way would be a cycle.
Progress = Callable[[str], None] | None


def _say(on_progress: Progress, text: str) -> None:
    """Report `text` if anyone is listening, so callers stay free of the check."""
    if on_progress is not None:
        on_progress(text)


def _reason_summary(reason: str) -> str:
    """`_solid_or_blank_feedback` below writes a judged rejection as several
    paragraphs of redraw instructions for the model -- a heading, the
    per-frame evidence, and an explanation of the check and the fix. A
    progress line needs only the evidence: the "frame N: blank/solid block
    -- count of total pixels opaque" lines the block opens with, read out on
    one line instead of buried in a block meant for the next prompt.
    """
    frames = [line.strip() for line in reason.splitlines() if line.strip().startswith("frame ")]
    return "; ".join(frames) if frames else reason.strip().splitlines()[0]


def _judge_frames(frames: list[Image.Image]) -> str | None:
    """Whether `frames` are demonstrably not a sprite, and if so, feedback
    naming what was wrong and what to do about it -- the register
    `planner.repair_feedback` already uses for a refused design proposal: a
    heading naming the failure, the specific evidence, and an instruction
    for the next attempt.

    One failure is checked, and it is real: a frame that packs to 0 or
    `SPRITE_SIZE * SPRITE_SIZE` set pixels is a blank or a solid block, not a
    silhouette -- exactly what the *Abu Simbel Profanation* run's `enemy` and
    `pellet` sprites came back as (see the module docstring).

    An earlier version of this also refused a sheet whose four frames were
    all pixel-identical, on the theory that a repeated pose meant no
    animation was actually drawn. That check was wrong for a `pellet`-like
    collectible, and for any other static entity (a wall, an exit): a model
    drawing a non-animating thing identically four times drew it *correctly*,
    and the check cost three wasted image generations, then raised, on
    exactly the response that should have been accepted on the first one.
    Gating the check on `EntitySpec.kind` was considered and rejected too --
    it would need this function, or its caller, to carry a growing list of
    "which kinds animate", a second source of truth alongside whatever the
    game's own design already implies, to catch a failure mode nothing in a
    real run has ever actually shown. The 0/256 check above does not have
    that problem: it fires on concrete, load-bearing evidence -- a frame with
    no distinguishable figure at all -- not on a stylistic reading of how
    many poses a sprite sheet "ought" to have.
    """
    total = SPRITE_SIZE * SPRITE_SIZE
    counts = [_set_pixel_count(frame) for frame in frames]
    bad = [(index, count) for index, count in enumerate(counts) if count in (0, total)]
    if bad:
        return _solid_or_blank_feedback(bad, total)
    return None


class DrawnFrames(list):
    """What `SpriteArtist.draw_frames` returns on success: a
    `list[Image.Image]` in every way that matters to existing callers
    (`len()`, iteration, `spriting.pack_spectrum`/`pack_cpc`,
    `services.draw_sprites`'s tiling loop all only ever index, iterate or
    measure it), carrying four more things alongside the frames for the
    caller that wants them:

    - `sheet`: the raw, unprocessed image the generator returned for the
      attempt that finally passed `_judge_frames` -- the last entry of
      `sheets` below, named separately because it is the one every caller
      most wants.
    - `sheets`: the raw, unprocessed image from *every* attempt, oldest
      first, including the winner as its last entry. `services.py` saves
      each one beside the asset it produced (see
      `services.StudioService._save_raw_sheet`), so a failed earlier
      attempt is not lost just because a later one succeeded.
    - `attempts`: how many times the model was asked, 1 if the first
      response already passed -- `len(sheets)`, kept as its own field so a
      caller does not have to derive it.
    - `repairs`: the feedback text given after each earlier, judged-failed
      attempt, oldest first -- empty if `attempts == 1`.

    A plain `list` subclass, rather than a dataclass wrapping a list, is
    what lets every existing caller keep treating the result as frames and
    nothing else: `_FakeArtist`/`_FixtureArtist` fakes elsewhere in the test
    suite return a bare `list[Image.Image]` from their own `draw_frames`,
    and `services.draw_sprites` reads `getattr(frames, "sheet", None)`
    rather than assuming every artist provides one -- so this richer return
    type is additive, not a breaking change to the `draw_frames` contract
    those fakes implement.
    """

    def __init__(
        self,
        frames: Sequence[Image.Image] = (),
        *,
        sheet: Image.Image,
        sheets: list[Image.Image],
        attempts: int,
        repairs: list[str],
    ) -> None:
        super().__init__(frames)
        self.sheet = sheet
        self.sheets = sheets
        self.attempts = attempts
        self.repairs = repairs


class SpriteDrawFailure(ValueError):
    """Raised when `SpriteArtist.draw_frames` exhausts `self.attempts`
    without a judged-valid sheet.

    A plain `ValueError` subclass, deliberately: any caller that only reads
    `str(exc)` -- the CLI's blanket error handler, for instance -- sees
    exactly the same message a bare `ValueError` would have carried, and
    nothing about existing error handling has to change. What this adds is
    `sheets`: every attempt's raw, unprocessed response, oldest first, and
    `reasons`: the judged feedback for each of them, same length, same
    order. Losing is exactly the case `services.StudioService._save_raw_sheet`
    most needs evidence for -- the run that never produced a usable sprite is
    the one where, otherwise, nothing would be left on disk to look at
    afterwards -- so `services.draw_sprites` catches this specifically to
    save every attempt before letting it propagate.
    """

    def __init__(self, message: str, *, sheets: list[Image.Image], reasons: list[str]) -> None:
        super().__init__(message)
        self.sheets = sheets
        self.reasons = reasons


@dataclass(frozen=True)
class DrawnSheet:
    """One attempt's answer, however it was drawn.

    `frames` are already the size `spriting.py`'s packers demand; how they
    got there is the source's business. `sheet` is the raw answer kept for
    evidence (`services.StudioService._save_raw_sheet`) -- for an image model
    it is the picture that came back, and for a source that had no picture it
    is a rendering of whatever it did get, because a failed run with nothing
    on disk to look at is the run this evidence exists for.

    `reason` is a refusal the source itself can state -- an answer that was
    not a usable sheet in the source's own terms, phrased for the model that
    wrote it. `None` means the source has no objection, which is not the same
    as the frames being good: `_judge_frames` still rules on the pixels
    afterwards.
    """

    frames: list[Image.Image]
    sheet: Image.Image
    reason: str | None = None


class SheetSource(Protocol):
    """Where a sheet comes from.

    The seam exists because "ask a model for a picture and recover a sprite
    from it" and "ask a model for the sprite" are different jobs with the
    same shape, and everything around them -- judging the result, retrying
    with feedback, keeping every attempt -- is the same either way and worth
    keeping exactly once.

    A source owns *how to ask* as well as how to read the answer: the two
    paths want genuinely different prompts, one describing a picture and one
    describing a grid, and separating them here is what keeps `draw_frames`
    from having to know which kind of model it is talking to. What it does
    not own is *when* to ask again, or with what feedback -- that stays in
    `SpriteArtist`, once, for both.
    """

    def compose(
        self, project: GameProject, entity: EntitySpec, dossier: GameReference | None
    ) -> str: ...

    def draw(self, project: GameProject, request: str, *, frames: int) -> DrawnSheet: ...


class TileSource(Protocol):
    """Where a tile's 8x8 block comes from.

    `SheetSource` one class over, for terrain instead of an entity. Two
    protocols rather than one generic over the thing being drawn, because
    the prompts differ in what they describe and the return types differ in
    what they carry -- a tile has one pose and a sheet has a cycle.
    """

    def compose(
        self, project: GameProject, tile: TileSpec, dossier: GameReference | None
    ) -> str: ...

    def draw(self, project: GameProject, request: str) -> DrawnSheet: ...


class SpriteArtist:
    """Draws one entity's sprite sheet, ready for `spriting.py`'s packer.

    The source is injected, never constructed here -- the same pattern
    `llmz80.studio.generator.ResponsesProgramWriter` follows for the program
    writer. This class only knows how to ask for art, how to judge what comes
    back and how to ask again; it does not know or care which model answered,
    nor in what form.
    """

    def __init__(self, source: SheetSource, *, attempts: int = MAX_DRAW_ATTEMPTS) -> None:
        self.source = source
        self.attempts = max(1, attempts)

    def draw_frames(
        self,
        project: GameProject,
        entity: EntitySpec,
        dossier: GameReference | None = None,
        *,
        on_progress: Progress = None,
    ) -> DrawnFrames:
        """One entity's sheet, cut into one frame per pose the design named,
        `spriting.SPRITE_SIZE` x `spriting.SPRITE_SIZE` pixels each, judged
        and, if the judgement fails, redrawn -- up to `self.attempts` times
        in total -- the way `generator.write_program` repairs a program that
        fails to build instead of shipping it anyway.

        Each attempt: ask the source for a sheet, with the previous
        attempt's feedback appended to the request once there is one. The
        source composes its own request and reads its own answer, and may
        state a refusal of its own -- a grid with a short row can be named
        precisely, where `_judge_frames`, which only ever sees pixels, could
        say no more than "that frame is blank".

        `_judge_frames` then decides whether the result is demonstrably not a
        sprite -- a solid or blank frame. A pass returns immediately, as
        `DrawnFrames` (see its docstring for what it carries beyond the
        frames themselves). A judged failure feeds that feedback into the
        next attempt's prompt and tries again; once `self.attempts` is
        exhausted, `SpriteDrawFailure` is raised, carrying every attempt's
        raw sheet and judged reason -- the way
        `reference_design.propose_and_apply` raises the last refusal once
        its own attempts run out, but keeping the full history rather than
        only the last entry: a run that never produces a usable sprite is
        exactly the run whose evidence is worth keeping (see
        `services.StudioService._save_raw_sheet`).

        `on_progress`, when given, is told twice per attempt: once before
        `self.generator.generate_image` -- the long wait, an image-model call
        -- and once after `_judge_frames` has ruled on what came back, with
        the reason first-hand rather than reconstructed afterwards from
        `DrawnFrames.repairs`/`SpriteDrawFailure.reasons` the way
        `services.draw_sprites` used to have to.
        """
        ident = entity.sprite or entity.id
        prompt = self.source.compose(project, entity, dossier)
        # Asked once and threaded through every attempt: a retry that
        # requested a different number of frames from the prompt it was
        # repairing would be judged against a contract the model never saw.
        frames = poses_wanted(entity)
        sheets: list[Image.Image] = []
        repairs: list[str] = []
        reason: str | None = None
        for attempt in range(1, self.attempts + 1):
            request = (
                prompt
                if reason is None
                else (prompt + "\n\nYOUR PREVIOUS SHEET WAS REJECTED\n\n" + reason)
            )
            _say(on_progress, f"{ident}: attempt {attempt}, drawing...")
            drawn = self.source.draw(project, request, frames=frames)
            sheets.append(drawn.sheet)
            # A source that can state its own refusal is believed first: it
            # saw the answer in the form the model actually wrote it, so it
            # can say "row 6 is a character short" where `_judge_frames`, which
            # only ever sees pixels, could say no more than "that frame is
            # blank" -- and the difference is what the next attempt is told.
            reason = drawn.reason or _judge_frames(drawn.frames)
            if reason is None:
                return DrawnFrames(
                    drawn.frames,
                    sheet=drawn.sheet,
                    sheets=sheets,
                    attempts=attempt,
                    repairs=repairs,
                )
            repairs.append(reason)
            _say(on_progress, f"{ident}: attempt {attempt} refused, {_reason_summary(reason)}")
        raise SpriteDrawFailure(
            f"the sprite sheet could not be drawn in {self.attempts} attempt"
            f"{'s' if self.attempts != 1 else ''}; the last reason was: "
            + (reason or "not recorded"),
            sheets=sheets,
            reasons=repairs,
        )


# ---------------------------------------------------------------------------
# Terrain. Everything above draws an actor; the rest of this module draws the
# ground it stands on. Kept in the same file because it is the same craft and
# the same machinery -- one grid of pen characters per cell -- and separate
# from `SpriteArtist` because almost every decision differs: one frame instead
# of four, eight pixels instead of sixteen, a solid block is a correct answer
# rather than a failure, and the subject is a kind of terrain rather than a
# character in motion.
# ---------------------------------------------------------------------------

#: What a tile artist is told about its job. The sprite system prompt's advice
#: about silhouettes and animation cycles is actively wrong here: terrain does
#: not move, and it is read as a texture rather than as a shape.
TILE_SYSTEM_PROMPT = """\
You are a pixel artist for 8-bit home computers. You draw terrain directly, as
grids of characters, one character per pixel -- not as pictures of terrain.

You are drawing one character cell: the smallest unit of ground, wall or
scenery the machine has. It will be repeated across a screen, next to copies of
itself, so what you draw has to read as a texture rather than as a picture --
and its edges have to meet the copy beside it without a visible seam, unless a
seam is the point (mortar between bricks is a seam that belongs).

Unlike a sprite, a filled cell is a legitimate answer: a solid wall is solid.
A cell with nothing in it is not -- that is the empty space this design draws
as a character, and it would not have asked you for artwork.\
"""


def _tile_contract(palette: GridPalette) -> str:
    """The non-negotiable half of a tile request, stated last for the same
    reason `_grid_contract` states it last: what is read last carries most
    weight, and a reference game's style note must not be the final word.

    Every line is checked by `sprite_grid.grid_errors` at tile size rather
    than hoped for -- including the one rule that differs from a sprite's,
    that a solid cell is allowed.
    """
    pens = "\n".join(f"  '{index}' = RGB{pen}" for index, pen in enumerate(palette.pens))
    return (
        f"{TECHNICAL_REQUIREMENTS_HEADING} (these apply no matter what any style note "
        "above says, and override it where the two disagree):\n\n"
        "- Exactly 1 frame. Terrain does not animate.\n"
        f"- The frame is exactly {TILE_SIZE} rows of exactly {TILE_SIZE} characters. "
        "Not one more, not one fewer, on any row.\n"
        f"- The only characters allowed are '{TRANSPARENT}' and "
        f"{', '.join(repr(character) for character in palette.alphabet)}.\n\n"
        "PENS:\n"
        f"  '{TRANSPARENT}' = transparent; the paper shows through\n"
        f"{pens}\n\n"
        "A completely filled cell is allowed -- a solid wall is solid. A completely "
        "transparent one is not: it would draw nothing, and this design would not have "
        "asked for artwork it did not want to see."
    )


def compose_tile_prompt(
    project: GameProject,
    tile: TileSpec,
    dossier: GameReference | None,
    palette: GridPalette,
) -> str:
    """The request `ClaudeGridTileSource` draws one tile's cell from.

    The same four-part shape as `compose_grid_prompt` -- the machine, the thing
    being asked for, what is known about how it should look, and last the
    contract that has to win -- with the subject taken from the design's own
    words for this terrain (`TileSpec.art_note`) and its traits, which are the
    design's vocabulary and not Studio's (`solid` means whatever the program
    decides it means, and the artist reads it exactly as loosely as that).
    """
    template = (_RESOURCES / _grid_template_filename(project)).read_text(encoding="utf-8")
    subject = f"{tile.id}, terrain drawn as one character cell"
    if tile.art_note.strip():
        subject += f": {tile.art_note.strip()}"
    if tile.traits:
        subject += f" [{', '.join(tile.traits)}]"
    body = template.format(prompt=subject, width=TILE_SIZE, height=TILE_SIZE)
    ask = (
        f"Draw 1 frame: one {TILE_SIZE}x{TILE_SIZE} pixel cell of this terrain, which will "
        "be repeated across the screen beside copies of itself. Mind the edges where the "
        "copies meet."
    )
    style = _dossier_style_block(dossier) if dossier is not None else ""
    return "\n\n".join(part for part in [body, ask, style, _tile_contract(palette)] if part)


class ClaudeGridTileSource:
    """Asks the model for one tile's cell, as a grid of pen characters.

    `ClaudeGridSheetSource` for terrain: the same absence of things to repair
    (no background, no halo, no crop, no rescale, no illegal colour), checked
    at `spriting.TILE_SIZE` with `solid_allowed=True`. It answers with the same
    `DrawnSheet` the sprite source does, so the retry loop that consumes it
    does not have to know which kind of art it is repairing.
    """

    def __init__(self, client: object, model: str = "claude-opus-5") -> None:
        self.client = client
        self.model = model

    def compose(self, project: GameProject, tile: TileSpec, dossier: GameReference | None) -> str:
        return compose_tile_prompt(project, tile, dossier, palette_for(project))

    def draw(self, project: GameProject, request: str) -> DrawnSheet:
        palette = palette_for(project)
        grid = structured(
            self.client,
            self.model,
            system=TILE_SYSTEM_PROMPT,
            user=request,
            schema=SpriteSheetGrid,
            missing="the model did not return a tile",
        )
        reason = grid_errors(grid, palette, frames_expected=1, size=TILE_SIZE, solid_allowed=True)
        sheet = render_grid(grid, palette, size=TILE_SIZE)
        frames = [] if reason is not None else frames_from_grid(grid, palette, size=TILE_SIZE)
        return DrawnSheet(frames=frames, sheet=sheet, reason=reason)


class TileArtist:
    """Draws one tile's cell, retrying a refusal with the reason for it.

    `SpriteArtist`'s loop for terrain, and a separate class rather than a
    parameter on that one: what it narrates, what it judges and what it asks
    for all differ, and the shared part is fifteen lines of "ask, check, ask
    again with the reason". Bending `SpriteArtist` around a second kind of art
    would mean a `judge` parameter, a size parameter and a subject that is
    sometimes an entity and sometimes a tile -- three knobs to keep straight
    at every call site, to save a loop a reader can hold in their head.

    There is no pixel judge here, unlike `SpriteArtist`'s `_judge_frames`.
    That check exists to catch what an *image model* did to a sprite (a solid
    or blank frame recovered from a picture); on the grid path the same two
    failures are already named precisely by `sprite_grid.grid_errors`, in the
    grid's own terms, and the one of them that is legitimate for terrain -- a
    solid cell -- is allowed there rather than re-refused here.
    """

    def __init__(self, source: TileSource, *, attempts: int = MAX_DRAW_ATTEMPTS) -> None:
        self.source = source
        self.attempts = max(1, attempts)

    def draw_tile(
        self,
        project: GameProject,
        tile: TileSpec,
        dossier: GameReference | None = None,
        *,
        on_progress: Progress = None,
    ) -> DrawnFrames:
        prompt = self.source.compose(project, tile, dossier)
        sheets: list[Image.Image] = []
        repairs: list[str] = []
        reason: str | None = None
        for attempt in range(1, self.attempts + 1):
            request = (
                prompt
                if reason is None
                else (prompt + "\n\nYOUR PREVIOUS TILE WAS REJECTED\n\n" + reason)
            )
            _say(on_progress, f"{tile.id}: attempt {attempt}, drawing terrain...")
            drawn = self.source.draw(project, request)
            sheets.append(drawn.sheet)
            reason = drawn.reason
            if reason is None:
                return DrawnFrames(
                    drawn.frames,
                    sheet=drawn.sheet,
                    sheets=sheets,
                    attempts=attempt,
                    repairs=repairs,
                )
            repairs.append(reason)
            _say(
                on_progress,
                f"{tile.id}: attempt {attempt} refused, {_reason_summary(reason)}",
            )
        raise SpriteDrawFailure(
            f"the tile could not be drawn in {self.attempts} attempt"
            f"{'s' if self.attempts != 1 else ''}; the last reason was: "
            + (reason or "not recorded"),
            sheets=sheets,
            reasons=repairs,
        )
