"""Phase 11: loads the pre-sliced sprite PNGs (see tools/generate_sprites.py
and assets/sprites/final/) into pygame Surfaces, keyed by sprite name.

Each PNG under assets/sprites/final/ is already exactly the pixel size
its entity draws at (Player.WIDTH/HEIGHT, Platform.WIDTH/HEIGHT,
Collectible.WIDTH/HEIGHT) - this module just loads them, with
convert_alpha() so blitting respects their transparency and is fast.

If a file is missing (e.g. someone deletes assets/sprites/), the
corresponding key is simply left out of the returned dict; main.py's
draw() falls back to the original colored-rectangle placeholder for
anything not found, so a partial or missing sprite folder degrades
gracefully rather than crashing the game.
"""

import os

import pygame

SPRITES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets",
    "sprites",
    "final",
)


def load_sprites(sprites_dir: str = SPRITES_DIR) -> dict:
    """Load every *.png in sprites_dir into a {stem: Surface} dict."""
    sprites = {}
    if not os.path.isdir(sprites_dir):
        return sprites

    for filename in os.listdir(sprites_dir):
        if not filename.endswith(".png"):
            continue
        key = filename[: -len(".png")]
        path = os.path.join(sprites_dir, filename)
        sprites[key] = pygame.image.load(path).convert_alpha()

    return sprites
