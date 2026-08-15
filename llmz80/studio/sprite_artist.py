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

A real run against *Abu Simbel Profanation* showed that "whatever comes
back" cannot be trusted at face value: two of three sprites came back as
dark grey art on a near-black background, despite the prompt demanding pure
white, and the pipeline as it stood then had no way to notice -- it keyed a
fixed white out of every frame regardless of what the frame actually showed,
so a dark frame keyed nothing out and packed as a solid 16x16 block. Three
things in this module exist because of that run: `_detect_background` reads
the real background off each frame's own border instead of assuming white
(see its docstring, and `_key_out_background`'s); `_judge_frames` catches a
solid or blank frame as evidence the generation failed, not as a sprite to
pack anyway (see its own docstring for the check this module tried and
dropped -- refusing four identical frames outright, which punished a
correctly-drawn static sprite like a `pellet` collectible); and
`SpriteArtist.draw_frames` retries a judged failure with feedback naming
what was wrong, up to `MAX_DRAW_ATTEMPTS` times, the way
`generator.write_program` and `reference_design.propose_and_apply` already
retry their own failures instead of accepting the first answer unconditionally.
A failed run's every attempt, not just a winning one, is kept on disk too --
see `services.StudioService._save_raw_sheet` -- because the run this module
exists for is exactly the one where nothing else survives to debug it.

Fixing that background defect let all three of that run's sprites reach
`_judge_frames` as real silhouettes, and all three passed it -- but passing
"not 0 or 256 opaque pixels" is not the same as looking right, and two of
the three did not. `_clean_image` crops tightly to whatever bounding box the
drawn pose actually occupies, and the code this module used to hand that
crop straight to `_scale_image(cleaned, SPRITE_SIZE, SPRITE_SIZE)`, which
stretches width and height independently until the crop fills the target
exactly -- whatever the crop's real proportions were. A creature with lots
of internal background inside its own bounding box (`enemy`) survives that
unrecognisably distorted either way, which is exactly why only it looked
right; a standing figure (`hero`) came out squashed into a near-solid blob,
and a small collectible (`pellet`) came out inflated to fill its frame edge
to edge, both indistinguishable from the "model drew a filled rectangle"
failure `_judge_frames` exists to catch, yet neither actually 0 or 256
opaque. `_fit_to_frame` is the fix: scale the crop by one factor derived
from both its own aspect ratio and the column it was cut from (see its
docstring for why both matter), and centre it, so proportions survive and
whatever space is left over is real background rather than distortion.

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
  `_clean_image` already accepts the background colour to isolate against as
  a parameter; this module supplies the colour it detected rather than the
  fixed white `_clean_image`'s own default happens to be, so fixing the "wrong
  background" defect never required touching `image_utils.py` at all.

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
from typing import Callable

import numpy as np
from PIL import Image

from generators.base import BaseImageGenerator
from image_utils import _clean_image, _scale_image
from llmz80.studio.models import EntitySpec, GameProject, TargetPlatform, VideoMode
from llmz80.studio.reference import GameReference
from llmz80.studio.sprite_sheet import split_frames
from llmz80.studio.spriting import ALPHA_THRESHOLD, SPRITE_SIZE

#: One sheet holds a walk/patrol cycle: four poses is enough for every current
#: entity kind (see `llmz80.studio.models.EntitySpec.kind`) without inflating
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

#: The background colour every `resources/sprite_prompt_*.txt` template asks
#: the model for -- see e.g. `sprite_prompt_spectrum.txt`'s "pure white
#: background (RGB 255,255,255)" and `sprite_prompt_generic.txt`'s "100%
#: solid white". Kept here as a record of what is *requested*, not as what
#: this module *trusts*: a real run showed the model does not always comply
#: (see the module docstring), so nothing below keys this fixed colour out
#: any more -- `_detect_background` reads the colour a frame actually has
#: instead. `BACKGROUND_TOLERANCE` is still a live constant: `_detect_background`
#: uses it to decide which border pixels count as "the same colour" as each
#: other, and `_key_out_background` uses it, on whatever colour detection
#: found, to decide which frame pixels match it.
BACKGROUND_COLOR = (255, 255, 255)
BACKGROUND_TOLERANCE = 10

#: How far a pixel may differ from the detected background before
#: `_binarize_against_background` still treats it as background, discounting
#: an anti-aliased halo rather than letting `_clean_image` count it as
#: figure. Deliberately not `BACKGROUND_TOLERANCE`: that constant is tuned
#: for exact-colour keying -- compression noise on an otherwise flat
#: background, the kind `tests/fixtures/sprite_sheet_running_figure.png`
#: (a compliant, hard-edged response) carries a little of even where the
#: prompt was obeyed -- and a real haloed response blows straight past it.
#: The *Abu Simbel Profanation* `hero` sheet (see the module docstring) is
#: the real failure this constant exists for: its detected background sits
#: at (70, 70, 71), only 71 units of maximum per-channel difference away
#: from the figure's pure black, and its halo -- a soft vignette, not a
#: crisp edge -- fills that entire gap gradually. A per-column histogram of
#: that difference shows why 40 and not some other number: counts climb
#: through the noise band under 15 (compression grain, same shape as the
#: compliant fixture's), rise again through a broad hump from roughly 16 to
#: 49 (thousands of halo pixels, the gradient itself), then fall to a sparse
#: trickle from 50 to 69 (a few dozen to a couple hundred pixels per value --
#: the halo's faint tail, already thin), before spiking at 70-71 into tens
#: of thousands of pixels (the figure's own solid interior, uniformly at
#: maximum contrast because it is drawn as flat, unblended black). 40 sits
#: inside the hump, past the noise band and short of the sparse tail --
#: comfortably past what compression grain or a `BACKGROUND_TOLERANCE`-sized
#: edge could produce, without reaching into the valley where real content
#: starts costing something.
#:
#: What a too-aggressive choice eats was checked directly, not assumed:
#: raising this past roughly 60 starts silently shortening the `hero`
#: sheet's second frame -- its cleaned crop drops from 561px tall to 403px,
#: losing the lower leg the same way a thin limb would be lost, because a
#: limb this pipeline never asked the model to draw with any less contrast
#: than its torso is, once drawn, exactly as far from the background as a
#: faint halo edge is. 40 leaves a wide margin below that break.
HALO_TOLERANCE = 40

#: How many times `SpriteArtist.draw_frames` will ask the model again after a
#: judged failure (see `_judge_frames`) before giving up. Set against its two
#: siblings, not picked in isolation: `generator.write_program` gets five
#: attempts because a failed build's diagnostics are concrete and cheap to
#: react to; `reference_design.propose_and_apply` gets three because a
#: refused proposal is validated locally, with no external call in the
#: repair itself. A judged sprite failure sits at the expensive end of that
#: spectrum -- every attempt is a full image generation, slower and pricier
#: than either sibling's retry step, and the feedback a judged failure can
#: give ("this frame is a solid block") is coarser than a compiler
#: diagnostic, so there is less reason to expect attempt five to do
#: meaningfully better than attempt three would not already have shown. Three
#: attempts -- one real chance to recover from a one-off bad draw, plus one
#: more in case the first repair overcorrects -- was chosen over five for
#: that reason: it costs at most two extra image generations per sprite
#: instead of four.
MAX_DRAW_ATTEMPTS = 3

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


def _technical_constraints() -> str:
    """The pipeline's non-negotiable requirements, stated last and stated as
    overriding anything a style description said above -- this is the fix
    for the defect a real run exposed: a reference dossier's own palette
    describes *that game's* screen, and when it sat last in the prompt (see
    the old `compose_prompt`, before this function existed) an image model
    read it as the final word and drew a dark sheet on a dark background.

    Every one of these lines is not a preference but a downstream contract:

    - Pure white background: still asked for, because a clean white
      background is easier for `_clean_image` to isolate a figure against
      than any other colour would be, and most responses do comply. It is no
      longer *trusted*, though: `_detect_background` reads whatever colour a
      frame's own border actually shows, white or not, so a response that
      ignores this line is judged and retried (see `_judge_frames`) rather
      than silently packed as a solid block -- see the module docstring for
      the run that made this necessary.
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

    The subject itself is named by `entity.kind` -- the design's own word for
    what this actor is ("a door", "a perseguidor character"), not one of a
    fixed handful of labels -- and, where the design bothered to write one,
    by `entity.notes`: prose about what this particular actor *does*
    ("opens once the player is holding the key") that a fixed vocabulary had
    no field for at all. Both come from the entity itself, so they apply
    whether or not a dossier was identified for this project.
    """
    template = (_RESOURCES / _template_filename(project)).read_text(encoding="utf-8")
    subject = f"{entity.sprite}, a {entity.kind} character"
    if entity.notes.strip():
        subject += f" ({entity.notes.strip()})"
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


def _detect_background(
    frame: Image.Image, tolerance: int = BACKGROUND_TOLERANCE
) -> tuple[int, int, int]:
    """The colour that actually dominates `frame`'s border pixels -- the
    honest evidence of what background the model drew, whatever it is: pure
    white as the prompt asks, or the dark grey a real run against *Abu
    Simbel Profanation* showed it can drift to instead (see the module
    docstring).

    Every `resources/sprite_prompt_*.txt` template asks for one full-canvas
    background and one figure roughly centred in it, so under a compliant
    response the border is background almost everywhere. This takes every
    pixel around all four edges, not just one corner or one edge, and votes:
    pixels are bucketed to the nearest multiple of `2 * tolerance + 1` (so
    near-identical background pixels -- the JPEG-grade noise real model
    output carries even on a flat background -- collapse into the same
    bucket instead of each being counted as its own, individually-rare
    colour), and the winning bucket's real pixels are averaged back out to a
    single RGB triple.

    A figure that only touches *part* of its frame's edge -- a foot reaching
    the bottom row, say -- still leaves the border majority-background, so
    the vote still finds the true background even then; see
    `test_a_sprite_touching_its_frame_edge_is_not_destroyed_by_background_detection`.
    What this cannot survive is a figure that covers *most* of the border:
    a sprite drawn edge-to-edge on all four sides would make its own colour
    the majority vote, and the two would swap -- the real background would
    be kept as opaque "figure", and the real figure would be keyed away as
    "background". No border-only method can tell that case apart from a
    frame that is genuinely all background; nothing here claims to.
    """
    rgb = np.asarray(frame.convert("RGB"), dtype=np.int16)
    border = np.concatenate([rgb[0, :], rgb[-1, :], rgb[:, 0], rgb[:, -1]], axis=0)
    bucket = max(1, tolerance * 2 + 1)
    quantised = (border // bucket) * bucket
    colours, counts = np.unique(quantised, axis=0, return_counts=True)
    dominant = colours[np.argmax(counts)]
    in_bucket = np.all(quantised == dominant, axis=1)
    real = border[in_bucket].mean(axis=0)
    return tuple(int(round(channel)) for channel in real)


def _key_out_background(
    frame: Image.Image,
    background_color: tuple[int, int, int],
    tolerance: int = BACKGROUND_TOLERANCE,
) -> Image.Image:
    """Turn `frame`'s background transparent, and leave its drawn pixels
    opaque.

    This is the fix for the defect that made every packed sprite a solid
    16x16 block: `gpt-image-1` draws a monochrome figure with no alpha
    channel at all, and `_clean_image`/`_scale_image` (which `draw_frames`
    already runs every frame through) preserve that -- they return RGB, not
    RGBA. `spriting.pack_spectrum` and `spriting.pack_cpc` both decide
    whether a pixel is drawn from *alpha* (`pixels[x, y][3] >=
    ALPHA_THRESHOLD`), so a plain `.convert("RGBA")` upstream of them (which
    is exactly what `spriting._checked` does) hands every pixel alpha 255
    regardless of whether it is figure or background -- both packers then
    read every pixel as opaque and pack the whole sprite as set.

    `background_color` is not defaulted to white any more, deliberately: a
    real run showed the model does not always draw the white background the
    prompt asks for, and a fixed assumption here silently packed that failure
    as a solid block instead of catching it (see the module docstring). Every
    caller in this module now passes whatever `_detect_background` found for
    this exact frame, so the two decisions -- "what is background" and "key
    it out" -- always agree with each other, and with what the frame actually
    shows rather than with what the prompt merely asked for.

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
      knows the background is what it detected it to be.

    - This module *is* well placed for it, because it is the one place that
      knows what colour to key, whether that came from the prompt's own
      request or (now) from `_detect_background` reading the frame itself.
      So this runs once, explicitly, right after `_fit_to_frame` reduces a
      frame to its final 16x16 size, converting the frame to RGBA and keying
      `background_color` out to alpha 0.

    Running after `_fit_to_frame` rather than before costs nothing:
    `_fit_to_frame`'s own resampling (`_scale_image`, nearest-neighbour) and
    its centring paste never blend two source pixels together, so every
    pixel of the fitted frame is still either exactly `background_color` or
    a genuine drawn pixel -- there is no antialiased middle ground for a
    tolerance-based threshold to get wrong.

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


def _fit_to_frame(
    cleaned: Image.Image,
    frame_size: int,
    background_color: tuple[int, int, int],
    *,
    reference_width: int,
) -> Image.Image:
    """Place `cleaned` -- `_clean_image`'s tight crop of the drawn pose,
    still at whatever size its own bounding box happened to be -- inside a
    `frame_size` x `frame_size` frame without distorting it.

    This is the fix for the defect a real run against *Abu Simbel
    Profanation* exposed: the code this replaced handed `cleaned` straight
    to `_scale_image(cleaned, SPRITE_SIZE, SPRITE_SIZE)`, which stretches
    both axes independently to fill the target exactly. A crop's proportions
    are whatever the drawn pose's really are -- a standing figure taller
    than it is wide, a small collectible far smaller than its own column --
    and stretching both axes to a fixed square destroys exactly that: a
    figure comes out squashed into a blob, and a small mark comes out
    inflated to a solid-looking block, indistinguishable from the "model
    drew a filled rectangle" failure `_judge_frames` exists to catch. See
    the module docstring for the three real sprites this showed up in.

    Two scale factors are computed, and the smaller wins:

    - `frame_size / max(width, height)`: the "contain" factor, mapping
      `cleaned`'s longer side onto `frame_size` exactly. Aspect ratio
      survives (both axes are scaled by the one factor), but taken alone
      this factor answers only "how big can this be without being cut off",
      never "how big should this be" -- a crop that is small purely because
      the pose it isolates is small, not because it was cropped tightly,
      would still be blown up until its longer side fills the frame, no
      different from the very stretch this function replaces for a crop
      that happens to be square.
    - `frame_size / reference_width`: how much a `reference_width`-wide
      *column* -- the caller's raw, unclean sheet slice `cleaned` was cut
      from, still at its own arithmetic width (`_sheet_columns` divides the
      sheet by `FRAMES_PER_SHEET` on width alone) -- would shrink to fit
      `frame_size`, applied to both of `cleaned`'s axes. This is the actual
      answer to "how big should this be": whatever fraction of one drawn
      frame's own width the object occupied, it keeps occupying once that
      frame is reduced to `frame_size`. A column's *height* is not used the
      same way, deliberately: every `resources/sprite_prompt_*.txt`
      template asks for frames laid out side by side at a fixed width, and
      `_sheet_columns` only ever divides on width, so a column's width is
      the one dimension this pipeline actually asked the model for and can
      trust; its height is however tall the model's whole response
      happened to be (`REQUEST_FRAME_SIZE * FRAMES_PER_SHEET` wide, but not
      reliably `REQUEST_FRAME_SIZE` tall -- a real response can, and for the
      run that exposed this defect did, come back as a square canvas far
      taller than the width its layout implies), so it carries no
      trustworthy notion of "how big was this meant to look".

    Taking the smaller factor is what keeps the two honest about each
    other's blind spot: the reference factor alone would let a crop that is
    genuinely taller than its own column is wide (a standing figure, cropped
    including the halo `_clean_image`'s tolerance mask picks up around it --
    see the module docstring) overflow past `frame_size` on that axis; the
    contain factor alone would blow a small collectible up to fill the frame
    just because nothing capped it from below. Whichever factor is smaller
    is the one guaranteed not to violate the other's constraint, so using
    it is not a compromise between two competing goals but the one number
    that actually satisfies both: never bigger than the frame allows, never
    bigger than what the object actually was relative to its own column.

    This is still a deliberately *kind-blind* rule: both factors look only
    at geometry -- `cleaned`'s own size and the column it came from -- never
    at `EntitySpec.kind`, so a `pellet` and a `hero` are sized by exactly
    the same arithmetic. A kind-aware alternative -- "small pickups stay
    small, tall characters fill more of the frame" -- was considered and
    rejected: it would need a second source of truth about how big each
    kind "ought" to look, alongside whatever the game's own design already
    implies, the same objection `_judge_frames`'s docstring raises against
    gating on kind at all.

    The result is centred on a `frame_size` x `frame_size` canvas of
    `background_color`, leaving whatever margin is left over -- on one axis
    if the contain factor won, on both if the reference factor did -- as
    real background, so `_key_out_background` keys it away like any other
    part of the frame. Nearest-neighbour throughout (`_scale_image`, already
    used everywhere else in this module), and the centring paste is
    exact-pixel, so nothing here can introduce the soft, blended edge
    `_technical_constraints` asks the model itself not to draw.
    """
    width, height = cleaned.size
    canvas = Image.new(cleaned.mode, (frame_size, frame_size), background_color)
    if width <= 0 or height <= 0:
        return canvas
    contain_scale = frame_size / max(width, height)
    reference_scale = frame_size / reference_width if reference_width > 0 else contain_scale
    scale = min(contain_scale, reference_scale)
    fitted_width = min(frame_size, max(1, round(width * scale)))
    fitted_height = min(frame_size, max(1, round(height * scale)))
    fitted = _scale_image(cleaned, fitted_width, fitted_height)
    offset = ((frame_size - fitted_width) // 2, (frame_size - fitted_height) // 2)
    canvas.paste(fitted, offset)
    return canvas


def _binarize_against_background(
    column: Image.Image,
    background_color: tuple[int, int, int],
    tolerance: int = HALO_TOLERANCE,
) -> Image.Image:
    """Snap every pixel of `column` within `tolerance` of `background_color`
    to that exact colour, before `_clean_image` ever sees the column --
    the fix for the defect that made the *Abu Simbel Profanation* run's
    `hero` sheet pack as a vertical bar instead of a figure (see the module
    docstring and `HALO_TOLERANCE`'s).

    `_clean_image` (see `image_utils.py`) keeps the single largest connected
    component whose pixels differ from `background_color` by more than its
    own, much smaller `tolerance` (`BACKGROUND_TOLERANCE`, tuned for
    near-exact colour matching -- see its own docstring), and crops to that
    component's bounding box. `_technical_constraints` asks the model for
    hard pixel edges and nothing behind the figure but flat background, so
    under a compliant response every pixel is either background or figure
    and that bounding box is the figure's true extent. A response that
    violates that -- a soft anti-aliasing halo, a vignette fading gradually
    from background toward the figure -- leaves a ring of pixels that are
    neither: too far from `background_color` for `_clean_image`'s tolerance
    to exclude, so they join the figure's connected component and drag its
    bounding box out to wherever the gradient happens to fade below that
    tolerance, which for a soft-enough halo can be most of the column.
    Fitting a bounding box that wide into `SPRITE_SIZE` leaves a bar, not a
    figure -- the pipeline doing exactly what `_fit_to_frame` promises with
    the wrong input, not a bug in fitting itself.

    This function is what makes that bounding box trustworthy again,
    without touching `_clean_image`'s own tolerance -- which stays at
    `BACKGROUND_TOLERANCE` everywhere else in this module, keyed against
    the *fixture* `test_a_sprite_touching_its_frame_edge_is_not_destroyed_by_background_detection`
    already depends on it protecting: a figure that only grazes its frame's
    edge. Snapping halo pixels to the exact background colour first, at the
    wider `HALO_TOLERANCE`, means `_clean_image` never has to be told to
    tolerate more -- every pixel it sees is already either exactly
    `background_color` (diff 0, always excluded, whatever its own tolerance
    is) or a pixel this function judged genuinely too far from background to
    be halo (necessarily further than `BACKGROUND_TOLERANCE` too, since
    `HALO_TOLERANCE` is the larger of the two), so the two tolerances never
    have to be reconciled against each other -- only `background_color`
    itself does the double duty, threaded through both calls the same way
    `_frame_from_column` already threads it through `_fit_to_frame` and
    `_key_out_background`.

    Run once, on the raw column, ahead of `_clean_image`: cleaning first and
    binarizing the crop after would already have let the halo inflate the
    bounding box `_clean_image` crops to, which is the one thing this
    function exists to prevent.
    """
    rgb = np.asarray(column.convert("RGB"))
    bg = np.asarray(background_color, dtype=np.int16)
    diff = np.abs(rgb.astype(np.int16) - bg)
    is_background = np.all(diff <= tolerance, axis=-1)
    binarized = rgb.copy()
    binarized[is_background] = np.asarray(background_color, dtype=np.uint8)
    return Image.fromarray(binarized, mode="RGB")


def _frame_from_column(column: Image.Image) -> Image.Image:
    """One raw sheet column, reduced to the real, final 16x16 RGBA frame.

    Detecting the background once per column (`_detect_background`) and
    threading that same colour through `_binarize_against_background` --
    which needs it to tell a soft halo from the figure it surrounds, before
    `_clean_image` ever sees either (see that function's docstring) --
    `_clean_image` -- which needs it to isolate the drawn pose -- `_fit_to_frame`
    -- which needs it to pad whatever margin is left once the pose is scaled
    without distortion -- and `_key_out_background` -- which needs it to key
    that pose's background to alpha 0 -- is what keeps all four decisions
    from disagreeing with each other, the way a caller passing a fixed white
    to one and something else to the others could. `column.width` is
    threaded through too, as `_fit_to_frame`'s `reference_width` -- see its
    docstring for why the column this pose was cut from, not just the
    pose's own crop, is what decides how big the pose should end up
    looking.
    """
    background = _detect_background(column, BACKGROUND_TOLERANCE)
    binarized = _binarize_against_background(column, background, HALO_TOLERANCE)
    cleaned = _clean_image(binarized, background_color=background, tolerance=BACKGROUND_TOLERANCE)
    fitted = _fit_to_frame(cleaned, SPRITE_SIZE, background, reference_width=column.width)
    return _key_out_background(fitted, background, BACKGROUND_TOLERANCE)


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
        frames: list[Image.Image] = (),
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


class SpriteArtist:
    """Draws one entity's sprite sheet, ready for `spriting.py`'s packer.

    The image model is injected, never constructed here -- see
    `generators/base.py` and, for the same pattern applied to the program
    writer, `llmz80.studio.generator.ResponsesProgramWriter`. This class only
    knows how to ask for art and how to turn whatever comes back into frames;
    it does not know or care which model answered.
    """

    def __init__(self, generator: BaseImageGenerator, *, attempts: int = MAX_DRAW_ATTEMPTS) -> None:
        self.generator = generator
        self.attempts = max(1, attempts)

    def draw_frames(
        self,
        project: GameProject,
        entity: EntitySpec,
        dossier: GameReference | None = None,
        *,
        on_progress: Progress = None,
    ) -> DrawnFrames:
        """One entity's sheet, cut into `FRAMES_PER_SHEET` frames of
        `spriting.SPRITE_SIZE` x `spriting.SPRITE_SIZE` pixels each, judged
        and, if the judgement fails, redrawn -- up to `self.attempts` times
        in total -- the way `generator.write_program` repairs a program that
        fails to build instead of shipping it anyway.

        Each attempt: ask the generator for a sheet (the composed prompt,
        with the previous attempt's judged feedback appended once there is
        one); split the raw response into its `FRAMES_PER_SHEET` columns
        first (`_sheet_columns`), on whatever size the model actually
        returned -- it is under no obligation to honour
        `REQUEST_WIDTH`/`REQUEST_HEIGHT`, and routinely does not; then clean,
        scale and key each column on its own (`_frame_from_column`).
        Cleaning per column rather than across the whole sheet is what keeps
        one pose's `_clean_image` result from crowding out the other three
        (see the module docstring).

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
        prompt = compose_prompt(project, entity, dossier)
        sheets: list[Image.Image] = []
        repairs: list[str] = []
        reason: str | None = None
        for attempt in range(1, self.attempts + 1):
            request = (
                prompt
                if reason is None
                else (prompt + "\n\nYOUR PREVIOUS SHEET WAS REJECTED\n\n" + reason)
            )
            _say(on_progress, f"{ident}: intento {attempt}, dibujando...")
            sheet = self.generator.generate_image(request)
            sheets.append(sheet)
            columns = _sheet_columns(sheet, FRAMES_PER_SHEET)
            frames = [_frame_from_column(column) for column in columns]
            reason = _judge_frames(frames)
            if reason is None:
                return DrawnFrames(
                    frames, sheet=sheet, sheets=sheets, attempts=attempt, repairs=repairs
                )
            repairs.append(reason)
            _say(on_progress, f"{ident}: intento {attempt} rechazado, {_reason_summary(reason)}")
        raise SpriteDrawFailure(
            f"the sprite sheet could not be drawn in {self.attempts} attempt"
            f"{'s' if self.attempts != 1 else ''}; the last reason was: " + reason,
            sheets=sheets,
            reasons=repairs,
        )
