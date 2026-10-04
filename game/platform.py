"""Platform base class.

This phase implements the static "brick" behavior only. Other platform
types from the rules (ice, spring, moving up/down, moving left/right) are
added as subclasses starting Phase 05, overriding update() and/or
is_solid() as needed - the base class is written to make that easy.
"""

import pygame


class Platform:
    """A static, always-solid platform (the 'brick' type, symbol '=')."""

    WIDTH = 70
    HEIGHT = 20
    COLOR = (139, 69, 19)  # brick brown; used only if sprites fail to load
    SPRITE_KEY = "platform_brick"  # Phase 11: key into assets/sprites/final/

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.WIDTH, self.HEIGHT)

    def update(self, dt: float) -> None:
        """Static platforms do not move. Moving platforms (Phase 05)
        override this to animate x/y over time."""
        pass

    def is_solid(self) -> bool:
        """Whether the player can currently land on this platform.

        Always True for brick. Ice platforms (Phase 05) will return False
        once fully melted.
        """
        return True

    def on_landed(self) -> None:
        """Called once when the player lands on this platform.

        Brick does nothing. Ice platforms (Phase 05) use this hook to
        start their melt timer.
        """
        pass

    def boosts_jump(self) -> bool:
        """Whether landing on this platform should apply the spring
        multiplier to the player's auto-jump. False for every type
        except spring (Phase 05)."""
        return False

    def is_visible(self) -> bool:
        """Whether this platform should currently be drawn.

        Defaults to True. Distinct from is_solid(): a Wall (Phase 06) is
        visible but never solid (not a landing surface); melted ice
        (Phase 05) is neither visible nor solid.
        """
        return True

    def sprite_key(self) -> str:
        """Phase 11: which pre-sliced sprite (see assets/sprites/final/
        and game/sprites.py) should represent this platform right now.

        Defaults to the SPRITE_KEY class attribute, which is enough for
        every type except IcePlatform, whose sprite depends on how far
        along it's melted - see its own override in
        game/special_platforms.py.
        """
        return self.SPRITE_KEY
