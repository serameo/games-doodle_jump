"""Collision detection between the player and platforms.

Per Confirmed Decision #7 (docs/doodle_jump_plans.md), collision is
lenient: any rectangle overlap between the player and a solid platform,
while the player is falling, counts as a landing. There is no minimum
overlap percentage requirement.

Detection uses a swept check across the frame's vertical movement (via
player.previous_y), not just the position at the end of the frame. This
prevents "tunneling": a fast-falling player skipping past a thin
platform entirely within a single frame without any single instant where
the rects overlap. See the Phase 03 addendum in
docs/doodle_jump_phase03.md.
"""

from game.player import Player
from game.platform import Platform


def find_landing_platform(player: Player, platforms: list) -> Platform | None:
    """Return the first platform the player has landed on, or None.

    Only considered while the player is falling (per rules 2.1: the
    player passes through platforms while moving upward). Platforms that
    are not currently solid (e.g. fully melted ice) are skipped.
    """
    if not player.is_falling():
        return None

    player_rect = player.rect
    prev_bottom = player.previous_y + Player.HEIGHT
    curr_bottom = player.y + Player.HEIGHT

    for platform in platforms:
        if not platform.is_solid():
            continue

        platform_rect = platform.rect
        x_overlap = (
            player_rect.right > platform_rect.left
            and player_rect.left < platform_rect.right
        )
        if not x_overlap:
            continue

        overlapping_now = player_rect.colliderect(platform_rect)
        crossed_top_this_frame = prev_bottom <= platform_rect.top <= curr_bottom

        if overlapping_now or crossed_top_this_frame:
            return platform

    return None
