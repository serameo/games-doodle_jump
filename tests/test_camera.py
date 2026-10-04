"""Unit tests for the Phase 09 "ratchet" Camera.

Phase 07's original camera always kept the player exactly centered, in
both directions. Phase 09 replaces that with:
1. A continuous auto-scroll (offset_y decreases every frame at
   scroll_speed px/sec, regardless of the player).
2. A ratchet follow: if the player has climbed above where that
   auto-scroll has reached, the camera snaps further up to keep them
   visible.
3. No reverse: once the camera has advanced to a point, it never moves
   back down to chase a falling player.
"""

import pytest

from game.camera import Camera


@pytest.fixture()
def camera():
    return Camera(screen_height=800, player_height=40)


def test_default_offset_is_zero_before_any_update():
    camera = Camera(screen_height=800, player_height=40)
    assert camera.offset_y == 0.0
    assert camera.to_screen_y(123) == 123


def test_update_snaps_to_center_the_player_on_first_call(camera):
    camera.update(dt=0.0, player_y=500, scroll_speed=0.0)
    assert camera.offset_y == pytest.approx(500 - 400 + 20)  # 120


def test_to_screen_y_centers_the_player_on_screen(camera):
    camera.update(dt=0.0, player_y=500, scroll_speed=0.0)
    player_screen_y = camera.to_screen_y(500)
    assert player_screen_y == pytest.approx(800 / 2 - 40 / 2)


def test_to_screen_y_preserves_relative_distance_to_player(camera):
    camera.update(dt=0.0, player_y=500, scroll_speed=0.0)
    platform_world_y = 400  # 100px above the player, in world space
    platform_screen_y = camera.to_screen_y(platform_world_y)
    player_screen_y = camera.to_screen_y(500)
    assert player_screen_y - platform_screen_y == pytest.approx(100)


def test_camera_ratchets_up_when_player_climbs_above_the_scrolled_point(camera):
    camera.update(dt=0.0, player_y=500, scroll_speed=0.0)
    offset_before = camera.offset_y
    camera.update(dt=0.0, player_y=300, scroll_speed=0.0)  # climbed 200px
    assert camera.offset_y == pytest.approx(offset_before - 200)
    assert camera.to_screen_y(300) == pytest.approx(800 / 2 - 40 / 2)


def test_camera_does_not_follow_the_player_back_down_when_falling(camera):
    camera.update(dt=0.0, player_y=300, scroll_speed=0.0)
    offset_before = camera.offset_y
    camera.update(dt=0.0, player_y=500, scroll_speed=0.0)  # fell 200px
    # Ratchet: offset must not move back down (increase) just because
    # the player fell - this is the key behavior change from Phase 07.
    assert camera.offset_y == pytest.approx(offset_before)
    # The player is now drawn below screen-center, not re-centered.
    assert camera.to_screen_y(500) > 800 / 2 - 40 / 2


def test_continuous_scroll_advances_the_offset_even_if_player_holds_still(camera):
    camera.update(dt=0.0, player_y=500, scroll_speed=0.0)
    offset_before = camera.offset_y
    camera.update(dt=1.0, player_y=500, scroll_speed=50.0)  # 1 second at 50 px/s
    assert camera.offset_y == pytest.approx(offset_before - 50.0)


def test_continuous_scroll_never_reverses_across_frames(camera):
    camera.update(dt=0.0, player_y=500, scroll_speed=0.0)
    offsets = [camera.offset_y]
    for _ in range(10):
        camera.update(dt=1 / 60, player_y=500, scroll_speed=30.0)
        offsets.append(camera.offset_y)
    # Every step should be <= the previous one (world coordinates: a
    # smaller offset means the camera has moved further up).
    assert all(b <= a for a, b in zip(offsets, offsets[1:]))


def test_player_climbing_faster_than_scroll_still_gets_followed(camera):
    camera.update(dt=0.0, player_y=500, scroll_speed=0.0)
    # A slow auto-scroll (10 px/s over 1s = 10px) but the player leaps
    # 300px upward in that same second - the ratchet-follow should win.
    camera.update(dt=1.0, player_y=200, scroll_speed=10.0)
    expected_offset = 200 - 400 + 20  # desired_offset for centering at y=200
    assert camera.offset_y == pytest.approx(expected_offset)
