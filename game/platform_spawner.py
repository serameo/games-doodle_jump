"""Random platform generation.

Per rules 2.2 and Confirmed Decision #8: every newly generated platform
must always be reachable by a jump from the platform generated just
before it. This is guaranteed by keeping the vertical gap between
consecutive platforms within [MIN_GAP, MAX_GAP] = [140, 190] px, which
stays comfortably under the ~202px max jump height from the Phase 02
physics (gravity 2000 px/s^2, jump velocity -900 px/s).
"""

import random

from game.collectible import Coin, Diamond
from game.platform import Platform


class PlatformSpawner:
    """Generates a vertical column of platforms, one above the next."""

    MIN_GAP = 140.0
    MAX_GAP = 190.0

    # Rules 2.3: a coin every 5 floors, a diamond every 10 floors. This
    # only applies to the randomly-generated column (hand-authored maps
    # place their own coins/diamonds explicitly via symbols).
    COIN_EVERY_N_FLOORS = 5
    DIAMOND_EVERY_N_FLOORS = 10

    def __init__(self, screen_width: float, rng: random.Random | None = None) -> None:
        self.screen_width = screen_width
        # Accepting an rng lets tests pass a seeded Random() for
        # deterministic, repeatable results.
        self.rng = rng if rng is not None else random.Random()

    def next_platform(self, previous_y: float) -> Platform:
        """Generate one platform above previous_y with a reachable gap."""
        gap = self.rng.uniform(self.MIN_GAP, self.MAX_GAP)
        new_y = previous_y - gap
        max_x = self.screen_width - Platform.WIDTH
        new_x = self.rng.uniform(0, max_x)
        return Platform(x=new_x, y=new_y)

    def generate_column(self, start_y: float, top_y: float) -> list:
        """Generate platforms starting above start_y, continuing upward
        until a platform's y reaches or passes top_y.

        Each platform is generated relative to the previous one, so the
        whole column is guaranteed reachable end to end.
        """
        platforms = []
        current_y = start_y
        while current_y > top_y:
            platform = self.next_platform(current_y)
            platforms.append(platform)
            current_y = platform.y
        return platforms

    def generate_collectibles(self, platforms: list) -> list:
        """Attach coins/diamonds to a generated column per rules 2.3:
        each platform in the list counts as one floor climbed; every
        5th floor gets a coin, every 10th floor also gets a diamond
        (10 is a multiple of 5, so both appear together there)."""
        collectibles = []
        for floor_index, platform in enumerate(platforms, start=1):
            item_x = platform.x + (Platform.WIDTH - Coin.WIDTH) / 2
            item_y = platform.y - 30  # float just above the platform
            if floor_index % self.COIN_EVERY_N_FLOORS == 0:
                collectibles.append(Coin(x=item_x, y=item_y))
            if floor_index % self.DIAMOND_EVERY_N_FLOORS == 0:
                collectibles.append(Diamond(x=item_x, y=item_y))
        return collectibles
