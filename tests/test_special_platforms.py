"""Unit tests for Phase 05: ice, spring, and moving platforms; also
Wall's falling behavior (added in a Phase 10 addendum)."""

import pytest

from game.platform import Platform
from game.special_platforms import (
    IcePlatform,
    MovingHorizontalPlatform,
    MovingVerticalPlatform,
    SpringPlatform,
    Wall,
)


# --- Base class defaults -----------------------------------------------

def test_brick_platform_does_not_boost_jump():
    assert Platform(x=0, y=0).boosts_jump() is False


def test_brick_platform_on_landed_does_nothing():
    platform = Platform(x=0, y=0)
    platform.on_landed()  # should simply not error, no state to check


def test_brick_platform_is_visible_by_default():
    assert Platform(x=0, y=0).is_visible() is True


# --- Wall (Phase 06; falling behavior added in a Phase 10 addendum) ----

@pytest.fixture()
def wall():
    return Wall(x=0, y=0, fall_acceleration=2000.0)


def test_wall_is_solid(wall):
    """Revised from the original rules 2.2 behavior: the wall is now a
    normal landable platform (see the Wall class docstring)."""
    assert wall.is_solid() is True


def test_wall_is_visible(wall):
    assert wall.is_visible() is True


def test_wall_does_not_fall_before_being_landed_on(wall):
    assert wall.falling is False
    wall.update(dt=1.0)
    assert wall.y == 0
    assert wall.falling is False


def test_wall_starts_falling_on_landed(wall):
    wall.on_landed()
    assert wall.falling is True
    assert wall.y == 0  # starts falling from the next update(), not instantly


def test_wall_accelerates_downward_after_landing(wall):
    wall.on_landed()
    wall.update(dt=1.0)
    # v = a*t = 2000 * 1.0 = 2000; y += v*dt = 0 + 2000*1.0 = 2000
    assert wall.fall_velocity == pytest.approx(2000.0)
    assert wall.y == pytest.approx(2000.0)


def test_wall_keeps_accelerating_across_multiple_frames(wall):
    wall.on_landed()
    wall.update(dt=0.5)
    velocity_after_first_frame = wall.fall_velocity
    wall.update(dt=0.5)
    assert wall.fall_velocity > velocity_after_first_frame


def test_wall_landing_again_after_falling_does_not_reset_velocity(wall):
    wall.on_landed()
    wall.update(dt=1.0)
    velocity_before = wall.fall_velocity
    wall.on_landed()  # should not restart the fall from zero
    assert wall.fall_velocity == pytest.approx(velocity_before)


def test_wall_fall_acceleration_is_configurable():
    slow_wall = Wall(x=0, y=0, fall_acceleration=10.0)
    slow_wall.on_landed()
    slow_wall.update(dt=1.0)
    assert slow_wall.fall_velocity == pytest.approx(10.0)


def test_wall_sprite_key(wall):
    assert wall.sprite_key() == "platform_wall"


# --- Ice platform --------------------------------------------------------

@pytest.fixture()
def ice_platform():
    return IcePlatform(x=0, y=0, melt_seconds=3.0, broken_visible_seconds=0.3)


def test_ice_starts_solid_and_not_melting(ice_platform):
    assert ice_platform.is_solid() is True
    assert ice_platform.melting is False


def test_ice_does_not_melt_before_being_landed_on(ice_platform):
    ice_platform.update(dt=10.0)  # no on_landed() call yet
    assert ice_platform.is_solid() is True


def test_ice_starts_melting_on_landed(ice_platform):
    ice_platform.on_landed()
    assert ice_platform.melting is True
    assert ice_platform.is_solid() is True  # not melted yet, just started


def test_ice_stays_solid_before_timer_elapses(ice_platform):
    ice_platform.on_landed()
    ice_platform.update(dt=2.9)
    assert ice_platform.is_solid() is True


def test_ice_melts_once_timer_elapses(ice_platform):
    ice_platform.on_landed()
    ice_platform.update(dt=3.0)
    assert ice_platform.is_solid() is False


def test_ice_stays_visible_during_the_broken_grace_period(ice_platform):
    """Phase 11 addition: is_solid() goes False the instant melt_seconds
    elapses (no gameplay change), but is_visible() stays True a little
    longer so the shattered "broken" art has a moment to show."""
    ice_platform.on_landed()
    ice_platform.update(dt=3.0)
    assert ice_platform.is_solid() is False
    assert ice_platform.is_visible() is True


def test_ice_becomes_invisible_after_the_broken_grace_period_elapses(ice_platform):
    ice_platform.on_landed()
    ice_platform.update(dt=3.0)  # melts
    ice_platform.update(dt=0.3)  # grace period elapses
    assert ice_platform.is_visible() is False


def test_ice_broken_grace_period_is_configurable():
    ice = IcePlatform(x=0, y=0, melt_seconds=3.0, broken_visible_seconds=1.0)
    ice.on_landed()
    ice.update(dt=3.0)
    ice.update(dt=0.5)
    assert ice.is_visible() is True  # still within the longer grace period
    ice.update(dt=0.5)
    assert ice.is_visible() is False


def test_ice_melt_timer_is_configurable():
    fast_melting_ice = IcePlatform(
        x=0, y=0, melt_seconds=0.5, broken_visible_seconds=0.3
    )
    fast_melting_ice.on_landed()
    fast_melting_ice.update(dt=0.5)
    assert fast_melting_ice.is_solid() is False


def test_ice_landing_again_after_melted_does_not_reset(ice_platform):
    ice_platform.on_landed()
    ice_platform.update(dt=3.0)
    assert ice_platform.is_solid() is False
    ice_platform.on_landed()  # should not un-melt it
    assert ice_platform.is_solid() is False


def test_ice_sprite_key_is_solid_before_landing(ice_platform):
    assert ice_platform.sprite_key() == "platform_ice_solid"


def test_ice_sprite_key_stays_solid_for_first_half_of_melt(ice_platform):
    ice_platform.on_landed()
    ice_platform.update(dt=1.4)  # < half of 3.0
    assert ice_platform.sprite_key() == "platform_ice_solid"


def test_ice_sprite_key_is_cracking_past_the_halfway_point(ice_platform):
    ice_platform.on_landed()
    ice_platform.update(dt=1.6)  # >= half of 3.0
    assert ice_platform.sprite_key() == "platform_ice_cracking"


def test_ice_sprite_key_is_broken_once_melted(ice_platform):
    ice_platform.on_landed()
    ice_platform.update(dt=3.0)
    assert ice_platform.sprite_key() == "platform_ice_broken"


# --- Spring platform -------------------------------------------------------

def test_spring_platform_boosts_jump():
    assert SpringPlatform(x=0, y=0).boosts_jump() is True


def test_spring_platform_sprite_key():
    assert SpringPlatform(x=0, y=0).sprite_key() == "platform_spring"


# --- Moving platforms --------------------------------------------------

def test_moving_vertical_platform_moves_along_y_only():
    platform = MovingVerticalPlatform(x=100, y=200)
    platform.update(dt=0.1)
    assert platform.x == 100
    assert platform.y != 200


def test_moving_vertical_platform_stays_within_range():
    platform = MovingVerticalPlatform(x=100, y=200)
    for _ in range(1000):
        platform.update(dt=0.05)
    half_range = MovingVerticalPlatform.RANGE / 2
    assert 200 - half_range <= platform.y <= 200 + half_range


def test_moving_vertical_platform_reverses_direction_at_bound():
    platform = MovingVerticalPlatform(x=100, y=200)
    # Push far enough in one big step to hit (and clamp at) the bound.
    platform.update(dt=10.0)
    assert platform.direction == -1
    assert platform.offset == pytest.approx(MovingVerticalPlatform.RANGE / 2)


def test_moving_vertical_platform_sprite_key():
    assert (
        MovingVerticalPlatform(x=0, y=0).sprite_key() == "platform_moving_vertical"
    )


def test_moving_horizontal_platform_moves_along_x_only():
    platform = MovingHorizontalPlatform(x=100, y=200)
    platform.update(dt=0.1)
    assert platform.y == 200
    assert platform.x != 100


def test_moving_horizontal_platform_stays_within_range():
    platform = MovingHorizontalPlatform(x=100, y=200)
    for _ in range(1000):
        platform.update(dt=0.05)
    half_range = MovingHorizontalPlatform.RANGE / 2
    assert 100 - half_range <= platform.x <= 100 + half_range


def test_moving_horizontal_platform_sprite_key():
    assert (
        MovingHorizontalPlatform(x=0, y=0).sprite_key()
        == "platform_moving_horizontal"
    )
