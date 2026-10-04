"""Player entity: position, velocity, gravity, jumping, and horizontal
movement.

Physics is advanced using delta-time (seconds), not per-frame constants,
so behavior stays consistent regardless of frame rate.

previous_y is tracked so collision detection (game/collision.py) can use
a swept check across the frame's movement, not just the position at the
end of the frame - this avoids "tunneling" through thin platforms when
falling fast (see the Phase 03 addendum in docs/doodle_jump_phase03.md).
"""

import pygame


class Player:
    """A simple physics body: position and velocity affected by gravity,
    plus keyboard-driven horizontal movement with screen wrap-around."""

    WIDTH = 40
    HEIGHT = 40

    def __init__(self, x: float, y: float, settings: dict) -> None:
        self.x = x
        self.y = y
        self.previous_y = y
        self.velocity_y = 0.0
        self.gravity = settings["gravity"]
        self.jump_velocity = settings["jump_velocity"]
        self.spring_multiplier = settings["spring_multiplier"]
        self.horizontal_speed = settings["player_horizontal_speed"]
        # Phase 11: which way the player is facing/moving, for sprite
        # selection only - has no effect on physics or collision.
        self.facing_right = True
        self.moving_horizontally = False

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.WIDTH, self.HEIGHT)

    def update(self, dt: float) -> None:
        """Advance vertical physics by dt seconds (free fall unless
        jump()/land() ran). Remembers the pre-move y for swept collision."""
        self.previous_y = self.y
        self.velocity_y += self.gravity * dt
        self.y += self.velocity_y * dt

    def move(self, direction: int, dt: float) -> None:
        """Move horizontally. direction: -1 (left), 0 (none), +1 (right)."""
        self.x += direction * self.horizontal_speed * dt
        self.moving_horizontally = direction != 0
        if direction != 0:
            self.facing_right = direction > 0

    def wrap_around(self, screen_width: float) -> None:
        """Classic screen-wrap: fully exiting one side reappears on the
        other, so the player is never permanently unreachable off-screen
        horizontally."""
        if self.x + self.WIDTH < 0:
            self.x = screen_width
        elif self.x > screen_width:
            self.x = -self.WIDTH

    def jump(self, boosted: bool = False) -> None:
        """Set upward velocity. boosted=True applies the spring multiplier."""
        velocity = self.jump_velocity
        if boosted:
            velocity *= self.spring_multiplier
        self.velocity_y = velocity

    def land(self, platform_top_y: float, boosted: bool = False) -> None:
        """Snap the player's feet to a platform top, then auto-jump.

        Called by platform-collision code (Phase 03+) the moment the
        player's feet reach a platform's top while falling.
        """
        self.y = platform_top_y - self.HEIGHT
        self.jump(boosted=boosted)

    def is_falling(self) -> bool:
        return self.velocity_y > 0

    def is_rising(self) -> bool:
        return self.velocity_y < 0

    def sprite_key(self) -> str:
        """Phase 11: which of the 8 player sprites (see
        assets/sprites/final/ and game/sprites.py) to draw right now.

        Facing comes from the last horizontal direction moved (there's
        no separate "idle facing" concept - the player keeps facing
        whichever way they last moved). Vertical motion always takes
        priority over Stand/Run, since the continuous auto-jump means
        the player is almost always airborne - Stand/Run only ever
        surface for an instant where velocity_y is exactly zero (e.g.
        the very first spawn frame, before gravity has been applied).
        """
        facing = "right" if self.facing_right else "left"
        if self.is_rising():
            state = "jump_up"
        elif self.is_falling():
            state = "fall_down"
        elif self.moving_horizontally:
            state = "run"
        else:
            state = "stand"
        return f"player_{facing}_{state}"
