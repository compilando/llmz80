"""How many poses a sprite sheet holds, and who decides.

Found by generating a real game. A Breakout for the Amstrad CPC designed,
drew, built, booted and played -- the ball bounced, thirteen bricks broke, the
loop kept pace -- and was refused five times over, three of them for the same
reason:

    g_anim_frame never advanced across the moving steps

The gate was right. `sprite_frames[]` in the built header read `{4, 4}`, so the
art really did carry four poses and the program really never cycled them. The
defect was a step earlier: `FRAMES_PER_SHEET = 4` asked for four poses of every
sprite in every design, and this design had declared

    entities:
      - id: actor   poses: []
      - id: bola    poses: []

no poses at all. A ball and a paddle were given a walk cycle they have no use
for, and then a gate insisted they walk. `EntitySpec.poses` has existed since
schema v4, documented as "named poses the artwork carries", and nothing read it.

The second half matters as much as the first. Asking for one frame without
teaching the gate that one frame cannot animate would have made things worse:
the sprite would stop cycling and `g_anim_frame` would still be demanded to
change, which is a number moving for no visible reason.
"""

from __future__ import annotations

import pytest

from llmz80.studio.feel import animation_report
from llmz80.studio.models import EntitySpec, TargetPlatform
from llmz80.studio.samples import blank_project
from llmz80.studio.sprite_artist import poses_wanted


def _entity(**overrides) -> EntitySpec:
    fields = {"id": "bola", "kind": "ball", "sprite": "bola", "poses": []}
    fields.update(overrides)
    return EntitySpec(**fields)


class TestHowManyPoses:
    def test_a_design_that_names_none_gets_one(self):
        """A ball has one pose. Four was the number every sprite got, and it
        is what a Breakout was failed for three times."""
        assert poses_wanted(_entity(poses=[])) == 1

    def test_a_design_that_names_them_gets_that_many(self):
        assert poses_wanted(_entity(poses=["walk", "jump"])) == 2
        assert poses_wanted(_entity(poses=["walk", "jump", "die", "idle"])) == 4

    def test_the_schema_bound_is_respected(self):
        """`EntitySpec.poses` allows at most eight, and the sheet is that many
        16-pixel frames side by side."""
        assert poses_wanted(_entity(poses=[f"p{index}" for index in range(8)])) == 8


class TestThePromptAsksForWhatTheDesignDeclared:
    def test_a_still_entity_is_asked_for_one_frame_and_not_a_cycle(self):
        """The wording matters as much as the number: "one animation cycle" in
        front of a request for a single frame is a contradiction the model has
        to resolve by guessing."""
        from llmz80.studio.sprite_artist import compose_grid_prompt
        from llmz80.studio.sprite_grid import palette_for

        project = blank_project("Breakout", TargetPlatform.AMSTRAD_CPC)
        prompt = compose_grid_prompt(project, _entity(poses=[]), None, palette_for(project))

        assert "Exactly 1 frame" in prompt
        assert "animation cycle" not in prompt

    def test_an_animated_entity_is_asked_for_its_cycle(self):
        from llmz80.studio.sprite_artist import compose_grid_prompt
        from llmz80.studio.sprite_grid import palette_for

        project = blank_project("Runner", TargetPlatform.AMSTRAD_CPC)
        entity = _entity(id="minero", sprite="minero", poses=["walk_a", "walk_b", "walk_c"])

        prompt = compose_grid_prompt(project, entity, None, palette_for(project))

        assert "Exactly 3 frames" in prompt
        assert "animation cycle" in prompt

    def test_the_named_poses_reach_the_model(self):
        """A sheet asked for "3 frames" and nothing else gets three arbitrary
        poses; the design said which three."""
        from llmz80.studio.sprite_artist import compose_grid_prompt
        from llmz80.studio.sprite_grid import palette_for

        project = blank_project("Runner", TargetPlatform.AMSTRAD_CPC)
        entity = _entity(id="minero", sprite="minero", poses=["walk", "jump", "die"])

        prompt = compose_grid_prompt(project, entity, None, palette_for(project))

        for pose in ("walk", "jump", "die"):
            assert pose in prompt


class TestTheGateAbstainsWhenThereIsNothingToAnimate:
    """Half two. A single-pose design has no animation, so the gate has no
    claim to make -- and `quality_pass: None` is how everything here says that.
    """

    def _runtime(self, frames):
        return {
            "platform": "amstrad_cpc",
            "step_readings": [
                {"id": "hold_left_a", "hold": "left", "read": {"g_anim_frame": 0}},
                {"id": "hold_right_a", "hold": "right", "read": {"g_anim_frame": 0}},
                {"id": "idle", "hold": "none", "read": {"g_anim_frame": 0}},
            ],
        }

    def test_a_still_design_abstains_instead_of_failing(self):
        report = animation_report(self._runtime(1), animated=False)

        assert report["quality_pass"] is None
        assert report["observed"] is False
        assert "one pose" in report["reason"]

    def test_an_animated_design_is_still_judged(self):
        report = animation_report(self._runtime(4), animated=True)

        assert report["quality_pass"] is False

    def test_judging_is_still_the_default(self):
        """Every existing caller passes nothing, and every existing design is
        animated until its poses say otherwise."""
        report = animation_report(self._runtime(4))

        assert report["quality_pass"] is False

    def test_abstaining_is_not_passing(self):
        """The rule this whole floor is built on, restated where it would be
        cheapest to break: a gate that cannot judge must not hand out a pass.
        `generator.py` accepts an abstention, and `release` refuses a build
        whose gates all abstained, which is what keeps that safe."""
        report = animation_report(self._runtime(1), animated=False)

        assert report["quality_pass"] is not True


class TestTheDesignDecidesWhetherItAnimates:
    def test_a_design_whose_entities_name_no_poses_does_not_animate(self):
        from llmz80.studio.sprite_artist import animates

        assert not animates([_entity(id="bola", sprite="bola", poses=[])])

    def test_one_animated_entity_is_enough(self):
        """The gate reads one `g_anim_frame` for the whole program, so a design
        with any animated actor has something to judge."""
        from llmz80.studio.sprite_artist import animates

        assert animates(
            [
                _entity(id="bola", sprite="bola", poses=[]),
                _entity(id="minero", sprite="minero", poses=["walk", "jump"]),
            ]
        )

    def test_an_entity_with_no_sprite_does_not_count(self):
        """Poses on an entity that carries no artwork animate nothing."""
        from llmz80.studio.sprite_artist import animates

        assert not animates([_entity(id="ghost", sprite=None, poses=["walk", "jump"])])


@pytest.mark.parametrize("count", [1, 2, 4, 8])
def test_the_sheet_is_as_wide_as_the_poses_it_holds(count):
    """`AssetSpec.validate_frames` refuses a sheet whose width is not a whole
    multiple of its frame count, so the two have to be derived from one number.
    """
    from llmz80.studio.sprite_artist import sheet_size
    from llmz80.studio.spriting import SPRITE_SIZE

    assert sheet_size(count) == (SPRITE_SIZE * count, SPRITE_SIZE)


class TestTheDrafterCanDeclareThem:
    """Without this the fix is a regression: every design would name no poses,
    every sprite would be one frame, and nothing would ever animate again.
    `/entities/N/poses` was not in the drafting table at all.
    """

    def test_the_path_is_offered(self):
        from llmz80.studio.drafting import DRAFT_SYSTEM_PROMPT

        assert "/entities/N/poses" in DRAFT_SYSTEM_PROMPT

    def test_the_drafter_is_told_when_not_to(self):
        """A list offered without "leave it alone for a ball" is a list that
        gets filled in for everything, which is where this started."""
        from llmz80.studio.drafting import DRAFT_SYSTEM_PROMPT

        assert "a ball, a bullet, a block, a paddle" in DRAFT_SYSTEM_PROMPT

    def test_the_drafter_is_told_what_naming_one_commits_it_to(self):
        """Poses are not free: each is drawn, and the program is then required
        to cycle through them or fail the animation gate."""
        from llmz80.studio.drafting import DRAFT_SYSTEM_PROMPT

        assert "g_anim_frame" in DRAFT_SYSTEM_PROMPT

    def test_the_planner_can_write_the_list(self):
        from llmz80.studio.planner import ProjectChange, ProjectProposal, RowsValue, apply_proposal

        project = blank_project("Runner", TargetPlatform.AMSTRAD_CPC)
        assert project.entities[0].poses == []

        updated = apply_proposal(
            project,
            ProjectProposal(
                summary="the miner walks",
                changes=[
                    ProjectChange(
                        path="/entities/0/poses",
                        operation="replace",
                        reason="the miner has a walk cycle and the ball does not",
                        value=RowsValue(rows=["walk_a", "walk_b"]),
                    )
                ],
            ),
        )

        assert updated.entities[0].poses == ["walk_a", "walk_b"]
