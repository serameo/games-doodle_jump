"""Unit tests for Phase 03: player-platform collision (lenient overlap).

Per Confirmed Decision #7, any rectangle overlap while falling counts as
a landing - no minimum overlap percentage.
"""

import pytest

from game.collision import find_landing_platform
from game.platform import Platform
from game.player import Player
from game.settings import load_settings


@pytest.fixture()
def settings():
    return load_settings()


@pytest.fixture()
def player(settings):
    # Positioned so its rect is (100, 190, 40, 40) -> bottom edge at y=230.
    return Player(x=100, y=190, settings=settings)


class _NonSolidPlatform(Platform):
    """Test double for a platform that should never be landed on."""

    def is_solid(self) -> bool:
        return False


def test_returns_platform_when_falling_and_overlapping(player):
    player.velocity_y = 100  # falling
    platform = Platform(x=90, y=225)  # overlaps player's rect slightly
    assert find_landing_platform(player, [platform]) is platform


def test_returns_none_when_no_overlap(player):
    player.velocity_y = 100  # falling
    platform = Platform(x=90, y=500)  # far below, no overlap
    assert find_landing_platform(player, [platform]) is None


def test_returns_none_when_rising(player):
    player.velocity_y = -100  # rising - should pass through platforms
    platform = Platform(x=90, y=225)  # would overlap if falling
    assert find_landing_platform(player, [platform]) is None


def test_returns_none_when_platform_not_solid(player):
    player.velocity_y = 100  # falling
    platform = _NonSolidPlatform(x=90, y=225)  # overlapping but not solid
    assert find_landing_platform(player, [platform]) is None


def test_returns_none_with_no_platforms(player):
    player.velocity_y = 100
    assert find_landing_platform(player, []) is None


def test_slight_overlap_is_enough(player):
    """Confirmed Decision #7: lenient collision - even a 1px overlap counts."""
    player.velocity_y = 100
    # Player rect bottom is at y=230; place platform so only its very top
    # edge overlaps the player's very bottom edge.
    platform = Platform(x=100, y=229)
    assert find_landing_platform(player, [platform]) is platform


def test_swept_detection_catches_fast_falls_that_would_tunnel(player):
    """Regression test for the tunneling bug: a large single-frame move
    that jumps clean over a thin platform must still be caught, because
    it's detected by crossing the platform's top between frames, not by
    overlapping at the final position alone."""
    # Platform sits well below the player's current position.
    platform = Platform(x=100, y=500)  # top at y=500, bottom at y=520

    # Simulate one very large frame: previous_y stays at 190 (unchanged,
    # as if this is the first frame after a slow start), but the player
    # jumps straight past the platform's 20px band to y=600 - so at the
    # end position there is no overlap at all with the platform.
    player.previous_y = 190
    player.y = 600
    player.velocity_y = 100  # falling

    assert find_landing_platform(player, [platform]) is platform


def test_no_swept_detection_when_platform_missed_entirely(player):
    """A big jump that never crosses the platform's y-band at all should
    still correctly report no landing."""
    platform = Platform(x=100, y=500)
    player.previous_y = 190
    player.y = 300  # big move, but doesn't reach anywhere near y=500-520
    player.velocity_y = 100

    assert find_landing_platform(player, [platform]) is None
