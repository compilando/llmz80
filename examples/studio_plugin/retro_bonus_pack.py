"""Small third-party genre-pack example for the Studio extension SDK."""

from llmz80.studio.packs import GenrePack


PACK = GenrePack(
    id="dodge_arena",
    name="Dodge arena",
    description="Survive increasingly dense waves in a single-screen arena.",
    capabilities=("input", "collision", "enemy_ai", "lives", "levels", "menus"),
)
