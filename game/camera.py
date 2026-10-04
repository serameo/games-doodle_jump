"""Camera (rules 2.5, plus rules 2.1's "the screen scrolls downward
slowly and continuously"; Phase 09 difficulty scaling).

Revised in Phase 09 - see docs/doodle_jump_phase09.md for the full
reasoning. Phase 07 originally kept the player exactly centered in both
directions (climbing and falling). That choice is replaced here with a
one-directional "ratchet" camera, which is required for scroll speed to
have any actual effect: with an always-recentering camera, the player
can never fall behind or get closer to the bottom edge, so scroll speed
would be a number that changes but produces no gameplay effect.

How it works now:
- Each frame, the camera advances upward in world space on its own, at
  the current scroll_speed (px/sec, from game/difficulty.py). This is
  the literal "screen scrolls downward" - everything drawn drifts
  toward the bottom of the screen over time, even if the player stands
  still.
- If the player has climbed above where that auto-scroll has reached,
  the camera also snaps up to keep the player on screen - a fast
  climber is never scrolled off the top.
- Falling is never followed. Once the camera has advanced to a given
  point, it never scrolls back down to chase a falling player. This is
  what makes falling dangerous: drop far enough below wherever the
  camera has already climbed to, and the player passes below the
  bottom edge of the visible screen (rules 2.1's game-over condition,
  wired up in Phase 10).

offset_y converts world_y to screen_y via to_screen_y(). Since a smaller
offset_y means the camera has moved further up, offset_y only ever
decreases or stays the same after the first update - it is never
allowed to increase.

Physics and collision are unaffected - they keep working entirely in
world coordinates; only draw() goes through the camera.
"""


class Camera:
    def __init__(self, screen_height: float, player_height: float) -> None:
        self.screen_height = screen_height
        self.player_height = player_height
        self.offset_y = 0.0
        self._initialized = False

    def update(self, dt: float, player_y: float, scroll_speed: float) -> None:
        """Advance the continuous auto-scroll by dt at scroll_speed, then
        ratchet further up if the player has climbed past that point.
        Never moves back down to follow a falling player.

        The very first call is a special case: offset_y starts at 0.0,
        which does not mean "the camera has already scrolled all the
        way up" - it just means no update has run yet. So the first
        call always snaps exactly to center the player, the same as
        Phase 07's original behavior; the ratchet only kicks in from
        the second call onward.
        """
        if not self._initialized:
            self.offset_y = (
                player_y - (self.screen_height / 2) + (self.player_height / 2)
            )
            self._initialized = True
            return

        self.offset_y -= scroll_speed * dt

        desired_offset = (
            player_y - (self.screen_height / 2) + (self.player_height / 2)
        )
        if desired_offset < self.offset_y:
            self.offset_y = desired_offset

    def to_screen_y(self, world_y: float) -> float:
        """Convert a world y-coordinate into a screen y-coordinate."""
        return world_y - self.offset_y
