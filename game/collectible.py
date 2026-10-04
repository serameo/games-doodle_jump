"""Collectibles (rules 2.3 scoring, rules 2.4 map symbols): coins and
diamonds.

Placed by the Phase 06 map loader. They are inert for now - present in
the world and drawn, but pickup/scoring logic itself is implemented in
Phase 08 (Scoring).
"""

import pygame


class Collectible:
    WIDTH = 20
    HEIGHT = 20
    COLOR = (255, 255, 255)
    VALUE = 0
    SPRITE_KEY = None  # Phase 11: key into assets/sprites/final/

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.WIDTH, self.HEIGHT)

    def sprite_key(self) -> str:
        return self.SPRITE_KEY


class Coin(Collectible):
    """Symbol 'c'/'C' - worth 1 point (rules 2.3)."""

    COLOR = (255, 223, 0)  # yellow/gold; used only if sprites fail to load
    VALUE = 1
    SPRITE_KEY = "collectible_coin"


class Diamond(Collectible):
    """Symbol 'd'/'D' - worth 3 points (rules 2.3)."""

    COLOR = (0, 220, 220)  # cyan; used only if sprites fail to load
    VALUE = 3
    SPRITE_KEY = "collectible_diamond"
