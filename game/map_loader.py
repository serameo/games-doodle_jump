"""Map file loading (rules 2.4).

Parses map01.txt, then map02.txt, and so on from the maps/ directory,
each one read bottom row to top row. Uses an 8-column grid (Confirmed
Decision #11: 60px per cell, 480/8) and a fixed 160px row height (within
the same 140-190 reachable range as the random spawner's Confirmed
Decision #8, so hand-authored rows stay jumpable). Falls back to the
Phase 04 random spawner once all map files are exhausted - that
fallback is handled by main.py, not this module.

wall_fall_acceleration is passed through to each Wall placed from a '!'
symbol - see game/special_platforms.py's Wall class for what it's used
for (added in a Phase 10 addendum; reuses config/settings.json's
"gravity").

ice_broken_visible_seconds is passed through to each IcePlatform placed
from a '~' symbol - see game/special_platforms.py's IcePlatform class
(added in Phase 11, config/settings.json's "ice_broken_visible_seconds").
"""

import os

from game.collectible import Coin, Diamond
from game.platform import Platform
from game.special_platforms import (
    IcePlatform,
    MovingHorizontalPlatform,
    MovingVerticalPlatform,
    SpringPlatform,
    Wall,
)

COLUMNS = 8
ROW_HEIGHT = 160.0


def cell_width(screen_width: float) -> float:
    return screen_width / COLUMNS


def load_map_file(
    path: str,
    start_y: float,
    screen_width: float,
    ice_melt_seconds: float,
    wall_fall_acceleration: float,
    ice_broken_visible_seconds: float,
):
    """Parse one map file into (platforms, collectibles, next_y).

    start_y is the y of the highest platform already placed below this
    map (e.g. the previous map file's last row, or the player's starting
    platform). The file's bottom row is placed ROW_HEIGHT above that, and
    each row above it continues ROW_HEIGHT further up. next_y is the y
    of this file's topmost row, for chaining into the next map file or
    the random spawner.
    """
    with open(path, "r", encoding="ascii") as map_file:
        lines = [line.rstrip("\n") for line in map_file if line.strip("\n") != ""]

    # The file is read bottom row to top row, so the *last* line is
    # processed first.
    rows_bottom_to_top = list(reversed(lines))

    width = cell_width(screen_width)
    platforms = []
    collectibles = []
    current_y = start_y

    for row in rows_bottom_to_top:
        current_y -= ROW_HEIGHT
        for col, symbol in enumerate(row[:COLUMNS]):
            x = col * width
            if symbol == "=":
                platforms.append(Platform(x=x, y=current_y))
            elif symbol == "~":
                platforms.append(
                    IcePlatform(
                        x=x,
                        y=current_y,
                        melt_seconds=ice_melt_seconds,
                        broken_visible_seconds=ice_broken_visible_seconds,
                    )
                )
            elif symbol == "@":
                platforms.append(SpringPlatform(x=x, y=current_y))
            elif symbol == "^":
                platforms.append(MovingVerticalPlatform(x=x, y=current_y))
            elif symbol == ">":
                platforms.append(MovingHorizontalPlatform(x=x, y=current_y))
            elif symbol == "!":
                platforms.append(
                    Wall(x=x, y=current_y, fall_acceleration=wall_fall_acceleration)
                )
            elif symbol in ("c", "C"):
                collectibles.append(Coin(x=x, y=current_y))
            elif symbol in ("d", "D"):
                collectibles.append(Diamond(x=x, y=current_y))
            # " " or "." -> empty, nothing placed. Any other/unknown
            # character is also silently treated as empty.

    return platforms, collectibles, current_y


class MapLoader:
    """Loads map01.txt, map02.txt, ... in order from a maps directory."""

    def __init__(
        self,
        maps_dir: str,
        screen_width: float,
        ice_melt_seconds: float,
        wall_fall_acceleration: float,
        ice_broken_visible_seconds: float,
    ) -> None:
        self.maps_dir = maps_dir
        self.screen_width = screen_width
        self.ice_melt_seconds = ice_melt_seconds
        self.wall_fall_acceleration = wall_fall_acceleration
        self.ice_broken_visible_seconds = ice_broken_visible_seconds
        self._next_index = 1

    def _next_path(self) -> str | None:
        path = os.path.join(self.maps_dir, f"map{self._next_index:02d}.txt")
        return path if os.path.exists(path) else None

    def has_next_map(self) -> bool:
        return self._next_path() is not None

    def load_next(self, start_y: float):
        """Load the next map file, or return an empty result if none
        remain (per rules 2.4: caller should fall back to the random
        spawner in that case)."""
        path = self._next_path()
        if path is None:
            return [], [], start_y

        platforms, collectibles, next_y = load_map_file(
            path,
            start_y,
            self.screen_width,
            self.ice_melt_seconds,
            self.wall_fall_acceleration,
            self.ice_broken_visible_seconds,
        )
        self._next_index += 1
        return platforms, collectibles, next_y
