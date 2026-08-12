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
  and the result is reduced with nearest-neighbour resampling, which keeps
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
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from generators.base import BaseImageGenerator
from image_utils import _clean_image, _scale_image
from llmz80.studio.models import EntitySpec, GameProject, TargetPlatform, VideoMode
from llmz80.studio.reference import GameReference, reference_prompt
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
#: `spriting.SPRITE_SIZE` pixels each, side by side.
SHEET_WIDTH = FRAMES_PER_SHEET * SPRITE_SIZE
SHEET_HEIGHT = SPRITE_SIZE

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


def _style_context(project: GameProject, entity: EntitySpec, dossier: GameReference | None) -> str:
    """What is known about how this should look.

    `reference_prompt` (see `reference.py`) already renders an identified
    dossier's `publisher` and `visual_style`, among other fields, and already
    returns nothing for a dossier that was never identified -- so an
    unidentified dossier and no dossier at all fall through to the same
    fallback here, which is correct: an unidentified dossier's `visual_style`
    and `publisher` are themselves blank (see `RESEARCH_SYSTEM_PROMPT`), so
    there would be nothing to carry either way. The fallback still has to
    describe *some* style, because a project with no identified game still
    needs art: it draws on the one thing every project always has, its own
    design -- the entity's `role` and the design's `presentation.style`.
    """
    block = reference_prompt(dossier)
    if block:
        return block
    return (
        "REFERENCE GAME\n\n"
        "No specific 1980s game has been identified for this project, so draw "
        f"from the design itself: this is a {entity.role} entity, and the "
        f'game\'s overall visual style is described as "{project.presentation.style}".'
    )


def compose_prompt(
    project: GameProject, entity: EntitySpec, dossier: GameReference | None = None
) -> str:
    """The prompt an image model is asked to draw one entity's sheet from.

    Three things are folded together: the target machine's real constraints
    (the matching `resources/sprite_prompt_*.txt` template), an explicit
    request for a `FRAMES_PER_SHEET`-frame sheet at the large size this module
    actually asks for (see the module docstring on why not the sprite's true
    size), and whatever is known about how the game should look, from
    `_style_context`.
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
    return "\n\n".join([body, sheet, _style_context(project, entity, dossier)])


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

        Whatever size the model actually returns -- it is under no obligation
        to honour `REQUEST_WIDTH`/`REQUEST_HEIGHT`, and routinely does not --
        is first trimmed to its drawn content (`_clean_image`) and then forced
        down to the sheet's real, final size with nearest-neighbour
        resampling (`_scale_image`). Forcing the exact size here, rather than
        trusting whatever the model sent, is what keeps a wrongly-sized
        response from ever reaching `split_frames`: that final size is always
        `FRAMES_PER_SHEET * SPRITE_SIZE` wide, which always divides evenly.
        """
        prompt = compose_prompt(project, entity, dossier)
        sheet = self.generator.generate_image(prompt)
        cleaned = _clean_image(sheet)
        scaled = _scale_image(cleaned, SHEET_WIDTH, SHEET_HEIGHT)
        return split_frames(scaled, FRAMES_PER_SHEET)
