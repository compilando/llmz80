"""Draw the sprites a project needs, in the style its dossier describes.

Everything downstream of this module already works: `spriting.py` packs frames
into the bytes each machine's blitter expects, `sprite_header.py` binds those
bytes into a generated `sprites.h`, and both machines blit them -- proven byte
for byte against real video memory. What has been missing is the art itself: a
project only had sprites if a human imported PNGs.

This module closes that gap. Given a project, one of its entities, and
optionally the dossier `llmz80.studio.reference` researched about a real
1980s game, it composes a prompt an image model can act on and turns whatever
comes back into frames `spriting.py` can pack.

Two things this module deliberately does *not* do, because getting them wrong
by guessing would be worse than not having them at all:

- It never asks an image model for a sprite's true, tiny size. Image models do
  not obey small requested dimensions -- asking for a 64x16 sheet reliably
  returns a large canvas (commonly 1024x1024) with a small sprite lost
  somewhere in the middle of it. So the prompt asks for a large sheet instead,
  and each pose in it is reduced with nearest-neighbour resampling, which keeps
  pixel art blocky rather than blurring it the way any smooth filter would.

- It depends on `image_utils._clean_image` and `image_utils._scale_image`
  (repository root) rather than reinventing them. Those two are private by
  convention, not by design: nothing about "find the drawn object against its
  background" or "resize with nearest-neighbour" is specific to the
  standalone `llm_sprites.py` script that has used them until now, and
  `llm_sprites.py` itself already imports them across that same boundary.
  This module does *not* import `image_utils.get_palette_for_platform` or
  `_process_image` -- `compiler.py` already documented, in `CPC_DEFAULT_PALETTE`,
  that the platform colour table those pull in has real gaps -- but no such
  problem exists for the two pixel-geometry helpers this module actually uses.

  `_clean_image` in particular keeps only the *single largest* connected
  non-background component and discards the rest -- exactly right for
  isolating one drawn pose against its background, and exactly wrong if it is
  run across the whole sheet at once: four separate, non-touching poses would
  collapse to whichever one happens to be largest, and the other three would
  come back blank. So this module always splits the sheet into its
  `FRAMES_PER_SHEET` columns *first*, by arithmetic, and only then hands each
  column to `_clean_image`/`_scale_image` on its own -- see `_sheet_columns`
  and `SpriteArtist.draw_frames`.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from generators.base import BaseImageGenerator
from image_utils import _clean_image, _scale_image
from llmz80.studio.models import EntitySpec, GameProject, TargetPlatform, VideoMode
from llmz80.studio.reference import GameReference
from llmz80.studio.sprite_sheet import split_frames
from llmz80.studio.spriting import SPRITE_SIZE

#: One sheet holds a walk/patrol cycle: four poses is enough for every current
#: entity role (see `llmz80.studio.models.EntitySpec.role`) without inflating
#: the static-data budget `spriting.py`'s packer already enforces.
FRAMES_PER_SHEET = 4

#: How big, per frame, to ask the model to draw before this module reduces the
#: result. Large enough that a model actually renders detail instead of a
#: blur; a plain multiple of the real 16px frame so the later nearest-neighbour
#: reduction lands on whole pixels.
REQUEST_FRAME_SIZE = 256
REQUEST_WIDTH = FRAMES_PER_SHEET * REQUEST_FRAME_SIZE
REQUEST_HEIGHT = REQUEST_FRAME_SIZE

#: The sheet's real, final size: `FRAMES_PER_SHEET` frames of
#: `spriting.SPRITE_SIZE` pixels each, side by side. Nothing in this module
#: resizes the whole sheet to this size in one step any more (see the module
#: docstring) -- it names the same total, reached one column at a time.
SHEET_WIDTH = FRAMES_PER_SHEET * SPRITE_SIZE
SHEET_HEIGHT = SPRITE_SIZE

#: The background colour and match tolerance every `resources/sprite_prompt_*.txt`
#: template asks the model for -- see e.g. `sprite_prompt_spectrum.txt`'s "pure
#: white background (RGB 255,255,255)" and `sprite_prompt_generic.txt`'s "100%
#: solid white". `image_utils._clean_image` already uses this exact pair
#: (they are its own defaults) to decide what counts as background when
#: isolating a pose from the sheet; `_key_out_background` below reuses the
#: same numbers for the same decision, so "background" means one thing
#: across both steps instead of two thresholds that could quietly drift
#: apart.
BACKGROUND_COLOR = (255, 255, 255)
BACKGROUND_TOLERANCE = 10

#: Prompt templates, one per target/mode, live beside the other Studio
#: resources (`resources/genres.yml`, `resources/studio_lib`, ...). Each
#: encodes real knowledge about what its machine can show -- monochrome on the
#: Spectrum, sixteen pens in CPC mode 0, four in mode 1 -- so this module reads
#: them rather than restating those constraints itself.
_RESOURCES = Path(__file__).resolve().parents[2] / "resources"


def _template_filename(project: GameProject) -> str:
    target = project.target
    if target.platform is TargetPlatform.SPECTRUM:
        return "sprite_prompt_spectrum.txt"
    if target.video_mode is VideoMode.CPC_MODE_0:
        return "sprite_prompt_amstrad_cpc_mode0.txt"
    return "sprite_prompt_amstrad_cpc_mode1.txt"


def _dossier_style_block(dossier: GameReference) -> str:
    """Only the visual half of an identified dossier, phrased so an image
    model reads it as inspiration for the *referenced* game's own screen --
    never as an instruction for the sheet being drawn right now.

    `reference_prompt` (see `reference.py`) renders far more than an image
    model has any use for: mechanics, pacing, screen layout and level
    structure are about how the *game* plays, not about one small sprite
    sheet's look, and its trailing "Researched from: <urls>" line exists for
    a person auditing the dossier, not for a model. Reusing that block here
    verbatim would put gameplay prose and a list of links at the very end of
    the prompt -- the position a model reads with the most weight -- crowding
    out the one thing that actually has to land there instead, the pipeline's
    own technical constraints (see `_technical_constraints`). This function
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
    design -- the entity's `role` and the design's `presentation.style`.
    """
    if dossier is not None and dossier.identified:
        return _dossier_style_block(dossier)
    return (
        "REFERENCE GAME\n\n"
        "No specific 1980s game has been identified for this project, so draw "
        f"from the design itself: this is a {entity.role} entity, and the "
        f'game\'s overall visual style is described as "{project.presentation.style}".'
    )


#: The heading `_technical_constraints` opens with. Named so the ordering
#: test can find it without duplicating the literal string, and so a future
#: edit to the wording cannot silently break the test that pins its position.
TECHNICAL_REQUIREMENTS_HEADING = "TECHNICAL REQUIREMENTS"


def _technical_constraints() -> str:
    """The pipeline's non-negotiable requirements, stated last and stated as
    overriding anything a style description said above -- this is the fix
    for the defect a real run exposed: a reference dossier's own palette
    describes *that game's* screen, and when it sat last in the prompt (see
    the old `compose_prompt`, before this function existed) an image model
    read it as the final word and drew a dark sheet on a dark background.

    Every one of these lines is not a preference but a downstream contract:

    - Pure white background: `image_utils._clean_image` isolates a frame's
      drawn pose by comparing against white, and this module's own
      `_key_out_background` keys that exact white to alpha 0 right
      afterwards (see its docstring). Art on any other background either
      gets treated as all-figure (nothing keyed out -- the solid-block
      defect this fixes) or has its real background wrongly keyed away.
    - No anti-aliasing: `_key_out_background` keys pixels by exact-colour
      tolerance, not by blending -- a soft edge leaves a halo of pixels that
      are neither background nor drawn figure.
    - Exactly `FRAMES_PER_SHEET` frames, one character each, side by side:
      `_sheet_columns` cuts the sheet into that many equal columns by
      arithmetic, before any cleaning happens (see the module docstring) --
      a different frame count or a second figure sharing a column corrupts
      every column split from it, not just the wrong one.

    The colour a referenced game's own dossier describes is deliberately
    left out of this list: Studio colours the sprite itself afterwards
    (`spriting.pack_spectrum`/`pack_cpc`), so the sheet drawn here only ever
    needs to be a clean silhouette, regardless of what any reference game's
    screen looked like.
    """
    return (
        f"{TECHNICAL_REQUIREMENTS_HEADING} (these apply no matter what any style note "
        "above says, and override it where the two disagree):\n\n"
        "- Pure white background (RGB 255,255,255), and nothing else behind the "
        "figure -- no gradient, no texture, no second colour of any kind.\n"
        "- No anti-aliasing: every edge is a hard, blocky pixel boundary; no "
        "soft, blended or intermediate-coloured pixels anywhere.\n"
        f"- Exactly {FRAMES_PER_SHEET} animation frames of the same character, side "
        "by side in a single row, and nothing drawn outside those frames.\n"
        "- Exactly one character per frame: no duplicate figure, no partial or "
        "cropped figure, no second character sharing a frame.\n\n"
        "A referenced game's own palette, above, describes that game on its own "
        "screen -- it does not describe this sheet. Draw the silhouette only, on "
        "the pure white background specified here; Studio colours the sprite "
        "itself afterwards."
    )


def compose_prompt(
    project: GameProject, entity: EntitySpec, dossier: GameReference | None = None
) -> str:
    """The prompt an image model is asked to draw one entity's sheet from.

    Four things are folded together, in this order: the target machine's
    real constraints (the matching `resources/sprite_prompt_*.txt`
    template), an explicit request for a `FRAMES_PER_SHEET`-frame sheet at
    the large size this module actually asks for (see the module docstring
    on why not the sprite's true size), whatever is known about how the game
    should look (`_style_context`), and, last, the pipeline's own technical
    constraints (`_technical_constraints`).

    That last position is deliberate, not incidental: an image model reads a
    long prompt with the most weight given to what it reads last, and the
    reference dossier's own palette/visual-style description used to sit
    there (see `_technical_constraints`'s docstring for the real run this
    broke). The style block dresses the sprite; the technical constraints
    that make the pipeline work at all -- a white background `_clean_image`
    and `_key_out_background` both depend on, no anti-aliasing, the exact
    frame layout `_sheet_columns` expects -- must win, so they are what the
    model reads last.
    """
    template = (_RESOURCES / _template_filename(project)).read_text(encoding="utf-8")
    subject = f"{entity.sprite}, a {entity.role} character"
    body = template.format(prompt=subject, width=REQUEST_WIDTH, height=REQUEST_HEIGHT)
    sheet = (
        f"Lay the art out as a sprite sheet of exactly {FRAMES_PER_SHEET} animation "
        f"frames of this same character, side by side in a single row, each frame "
        f"{REQUEST_FRAME_SIZE}x{REQUEST_FRAME_SIZE} pixels, so the whole sheet "
        f"image is {REQUEST_WIDTH}x{REQUEST_HEIGHT} pixels."
    )
    return "\n\n".join(
        [body, sheet, _style_context(project, entity, dossier), _technical_constraints()]
    )


def _key_out_background(
    frame: Image.Image,
    background_color: tuple[int, int, int] = BACKGROUND_COLOR,
    tolerance: int = BACKGROUND_TOLERANCE,
) -> Image.Image:
    """Turn a frame's white background transparent, and leave its drawn
    pixels opaque.

    This is the fix for the defect that made every packed sprite a solid
    16x16 block: `gpt-image-1` draws a monochrome figure as black-on-white,
    with no alpha channel at all, and `_clean_image`/`_scale_image` (which
    `draw_frames` already runs every frame through) preserve that -- they
    return RGB, not RGBA. `spriting.pack_spectrum` and `spriting.pack_cpc`
    both decide whether a pixel is drawn from *alpha*
    (`pixels[x, y][3] >= ALPHA_THRESHOLD`), so a plain `.convert("RGBA")`
    upstream of them (which is exactly what `spriting._checked` does) hands
    every pixel alpha 255 regardless of whether it is figure or background --
    both packers then read every pixel as opaque and pack the whole sprite as
    set.

    Three places could have carried this fix instead, and each was rejected:

    - `image_utils._clean_image`/`_process_image` (repository root) are
      shared with the standalone `llm_sprites.py` script, which is not part
      of Studio and has its own downstream pipeline (`_process_image`
      re-converts to RGB and quantises against a platform palette). Changing
      what those return would change a contract a script outside this
      module's ownership relies on, to fix a problem that is specific to how
      *this* module's prompts are written.

    - `spriting.pack_spectrum`/`pack_cpc` could fall back to luminance when a
      frame carries no real alpha (`_checked`'s `.convert("RGBA")` makes every
      pixel opaque either way, so "no real alpha" cannot even be detected
      there any more -- but even fixed to look earlier, in `draw_frames`, a
      luminance fallback is *implicit*: it would silently do the wrong thing
      for art that legitimately has a white foreground on a non-white
      background, and `spriting.py` has no way to know which case it is
      looking at. Only the caller that wrote the prompt -- this module --
      knows the background is guaranteed white.

    - This module *is* well placed for it, because it is the one place that
      knows, by construction (see every `resources/sprite_prompt_*.txt`
      template), that the background it asked the model to draw is pure
      white. So this runs once, explicitly, right after `_scale_image`
      reduces a frame to its final 16x16 size, converting the frame to RGBA
      and keying `background_color` out to alpha 0 -- using the exact
      colour/tolerance pair `_clean_image` itself already uses to tell figure
      from background (see `BACKGROUND_COLOR`/`BACKGROUND_TOLERANCE` above),
      so the two decisions cannot disagree.

    Running after `_scale_image` rather than before costs nothing: the
    nearest-neighbour resampling both use never blends two source pixels
    together, so every pixel of the scaled frame is still either exactly
    `background_color` or a genuine drawn pixel -- there is no antialiased
    middle ground for a tolerance-based threshold to get wrong.

    The resulting RGBA frames are what keeps the fix intact all the way to
    packed bytes: `services.draw_sprites` tiles them into a sheet with
    `Image.paste` (which copies an RGBA source's alpha channel verbatim, no
    mask needed), the sheet is saved as a PNG (a format that stores alpha
    losslessly), and `compiler.render_project` re-opens that PNG and asks for
    `"RGBA"` again -- a no-op on a file that already carries the real alpha
    this function put there. Every one of those steps would have discarded an
    implicit, un-stored decision; only real alpha, set once and carried in
    the pixels themselves, survives the round trip through disk.
    """
    rgba = np.asarray(frame.convert("RGBA")).copy()
    rgb = rgba[..., :3].astype(np.int16)
    bg = np.asarray(background_color, dtype=np.int16)
    is_background = np.all(np.abs(rgb - bg) <= tolerance, axis=-1)
    rgba[..., 3] = np.where(is_background, 0, 255)
    return Image.fromarray(rgba, mode="RGBA")


def _sheet_columns(sheet: Image.Image, frames: int) -> list[Image.Image]:
    """Split a raw, arbitrarily-sized sheet into `frames` equal columns, by
    arithmetic, on whatever width the model actually returned -- before any
    cleaning or scaling touches it. Splitting first, rather than cleaning the
    whole sheet and splitting the result, is what keeps four separate,
    non-touching poses from being collapsed into one: `_clean_image` (used
    per column by the caller) keeps only the single largest connected
    component, which is exactly right once each pose is on its own, and
    exactly wrong across a sheet of several.

    `split_frames` (see `sprite_sheet.py`) requires a width that divides
    evenly by `frames`; a model's response is under no obligation to provide
    one. A width that does not divide is cropped down to the largest width
    that does -- the discarded sliver is at most `frames - 1` pixels of a
    canvas hundreds of pixels wide, so it only ever trims padding, never a
    real pose. A sheet narrower than `frames` pixels -- possible only from a
    pathological or test response, never a real model at the sizes this
    module requests -- cannot even give each frame one pixel of its own column,
    so it is widened first (nearest-neighbour, like every other resize here)
    instead of being cropped to nothing.
    """
    usable_width = (sheet.width // frames) * frames
    if usable_width == 0:
        sheet = _scale_image(sheet, frames, sheet.height)
    elif usable_width != sheet.width:
        sheet = sheet.crop((0, 0, usable_width, sheet.height))
    return split_frames(sheet, frames)


class SpriteArtist:
    """Draws one entity's sprite sheet, ready for `spriting.py`'s packer.

    The image model is injected, never constructed here -- see
    `generators/base.py` and, for the same pattern applied to the program
    writer, `llmz80.studio.generator.ResponsesProgramWriter`. This class only
    knows how to ask for art and how to turn whatever comes back into frames;
    it does not know or care which model answered.
    """

    def __init__(self, generator: BaseImageGenerator) -> None:
        self.generator = generator

    def draw_frames(
        self, project: GameProject, entity: EntitySpec, dossier: GameReference | None = None
    ) -> list[Image.Image]:
        """One entity's sheet, cut into `FRAMES_PER_SHEET` frames of
        `spriting.SPRITE_SIZE` x `spriting.SPRITE_SIZE` pixels each.

        The raw response is split into its `FRAMES_PER_SHEET` columns first
        (`_sheet_columns`), on whatever size the model actually returned --
        it is under no obligation to honour `REQUEST_WIDTH`/`REQUEST_HEIGHT`,
        and routinely does not. Only then is each column, on its own, trimmed
        to its drawn pose (`_clean_image`) and forced down to
        `SPRITE_SIZE` x `SPRITE_SIZE` with nearest-neighbour resampling
        (`_scale_image`). Cleaning per column rather than across the whole
        sheet is what keeps one pose's `_clean_image` result from crowding
        out the other three (see the module docstring); forcing each column's
        exact final size, rather than trusting whatever the model sent, is
        what keeps a wrongly-sized response from ever producing a frame that
        is not exactly 16x16.

        The last step, `_key_out_background`, is what keeps the drawn
        silhouette from being lost between here and `spriting.py`'s packers:
        see its docstring for why keying the white background out to real
        alpha belongs here rather than in `image_utils.py` or `spriting.py`.
        """
        prompt = compose_prompt(project, entity, dossier)
        sheet = self.generator.generate_image(prompt)
        columns = _sheet_columns(sheet, FRAMES_PER_SHEET)
        return [
            _key_out_background(_scale_image(_clean_image(column), SPRITE_SIZE, SPRITE_SIZE))
            for column in columns
        ]
