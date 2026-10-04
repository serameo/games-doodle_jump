"""Special platform types (rules 2.2): ice, spring, moving, and wall
platforms.

Each subclass overrides only the Platform base-class hooks it needs:
- IcePlatform: is_solid() + update() + on_landed() + sprite_key()
  (melts after contact; sprite_key() cycles solid -> cracking -> broken)
- SpringPlatform: boosts_jump() (SPRITE_KEY class attribute)
- MovingVerticalPlatform / MovingHorizontalPlatform: update() (oscillate;
  SPRITE_KEY class attribute)
- Wall: is_solid() + on_landed() + update() (falls after first contact -
  see the class docstring for how this revises rules 2.2; SPRITE_KEY
  class attribute)

Phase 11: sprite_key() picks which of the pre-sliced PNGs under
assets/sprites/final/ main.py's draw() should blit for this platform.
Most types just return a fixed SPRITE_KEY class attribute (see
Platform.sprite_key() in game/platform.py); IcePlatform overrides the
method since its sprite depends on how far along it's melted.
"""

from game.platform import Platform


class IcePlatform(Platform):
    """Breakable ice (symbol '~').

    Starts solid. The moment the player lands on it, it begins melting;
    once melt_seconds has elapsed it disappears (is_solid() becomes
    False). melt_seconds is configurable per Confirmed Decision #3
    (config/settings.json's "ice_melt_seconds", default 3.0).

    Phase 11 addition: the sprite sheet provides three distinct visuals
    (solid / cracking / broken), so sprite_key() now cycles through them
    as the melt timer progresses - solid for the first half of
    melt_seconds, cracking for the second half, then broken. Once
    melted, the shattered "broken" art lingers for a short, purely
    cosmetic grace period (ice_broken_visible_seconds, default 0.3s)
    before is_visible() finally goes False - is_solid() already went
    False the instant melt_seconds elapsed, so this doesn't change
    when the platform stops being landable, only how long its shatter
    animation stays on screen afterward.
    """

    COLOR = (173, 216, 230)  # light blue; used only if sprites fail to load

    def __init__(
        self, x: float, y: float, melt_seconds: float, broken_visible_seconds: float
    ) -> None:
        super().__init__(x, y)
        self.melt_seconds = melt_seconds
        self.broken_visible_seconds = broken_visible_seconds
        self.melting = False
        self.timer = 0.0
        self.melted = False
        self.broken_timer = 0.0

    def on_landed(self) -> None:
        """Start the melt timer the first time the player lands here."""
        if not self.melting and not self.melted:
            self.melting = True
            self.timer = 0.0

    def update(self, dt: float) -> None:
        if self.melting and not self.melted:
            self.timer += dt
            if self.timer >= self.melt_seconds:
                self.melted = True
        elif self.melted:
            self.broken_timer += dt

    def is_solid(self) -> bool:
        return not self.melted

    def is_visible(self) -> bool:
        if not self.melted:
            return True
        return self.broken_timer < self.broken_visible_seconds

    def sprite_key(self) -> str:
        if self.melted:
            return "platform_ice_broken"
        if self.melting and self.timer >= self.melt_seconds / 2:
            return "platform_ice_cracking"
        return "platform_ice_solid"


class SpringPlatform(Platform):
    """Spring platform (symbol '@'): boosts the next jump by +50%."""

    COLOR = (255, 215, 0)  # gold; used only if sprites fail to load
    SPRITE_KEY = "platform_spring"

    def boosts_jump(self) -> bool:
        return True


class MovingPlatform(Platform):
    """Shared oscillation logic for the two moving platform types.

    Moves back and forth around its starting point (the "origin") within
    a fixed range, reversing direction at each bound. Speed and range are
    medium/typical values per Confirmed Decision #9.
    """

    SPEED = 60.0  # px/s
    RANGE = 80.0  # px, total distance covered (origin +/- RANGE/2)

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y)
        self.origin_x = x
        self.origin_y = y
        self.direction = 1  # +1 or -1
        self.offset = 0.0  # current signed distance from the origin

    def _advance_offset(self, dt: float) -> None:
        self.offset += self.direction * self.SPEED * dt
        half_range = self.RANGE / 2
        if self.offset > half_range:
            self.offset = half_range
            self.direction = -1
        elif self.offset < -half_range:
            self.offset = -half_range
            self.direction = 1


class MovingVerticalPlatform(MovingPlatform):
    """Slides up/down (symbol '^')."""

    COLOR = (100, 149, 237)  # cornflower blue; used only if sprites fail to load
    SPRITE_KEY = "platform_moving_vertical"

    def update(self, dt: float) -> None:
        self._advance_offset(dt)
        self.y = self.origin_y + self.offset


class MovingHorizontalPlatform(MovingPlatform):
    """Slides left/right (symbol '>')."""

    COLOR = (60, 179, 113)  # medium sea green; used only if sprites fail to load
    SPRITE_KEY = "platform_moving_horizontal"

    def update(self, dt: float) -> None:
        self._advance_offset(dt)
        self.x = self.origin_x + self.offset


class Wall(Platform):
    """Wall (symbol '!').

    Originally (rules 2.2) a static, non-landable obstacle that only
    blocks horizontal movement. Revised per your request: the wall is
    now landable like any other platform, but the first time the player
    lands on it, it starts falling straight down under acceleration -
    reusing config/settings.json's "gravity" (2000 px/s^2 by default),
    so it falls at the same rate the player themselves would. It never
    stops falling once triggered.

    Known limitation carried over from before: rules 2.2 also says
    walls "block horizontal movement," but the player has no horizontal
    obstacle collision at all yet (see the Phase 05 addendum) - this
    class still doesn't implement that part, only the new falling
    behavior.
    """

    COLOR = (105, 105, 105)  # dim gray; used only if sprites fail to load
    SPRITE_KEY = "platform_wall"

    def __init__(self, x: float, y: float, fall_acceleration: float) -> None:
        super().__init__(x, y)
        self.fall_acceleration = fall_acceleration
        self.falling = False
        self.fall_velocity = 0.0

    def on_landed(self) -> None:
        """Start falling the first time the player lands here."""
        if not self.falling:
            self.falling = True
            self.fall_velocity = 0.0

    def update(self, dt: float) -> None:
        if self.falling:
            self.fall_velocity += self.fall_acceleration * dt
            self.y += self.fall_velocity * dt

    def is_solid(self) -> bool:
        return True
