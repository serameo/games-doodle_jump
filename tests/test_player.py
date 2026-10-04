"""Unit tests for Phase 02: Player entity (position, gravity, jumping).

Uses pygame.Rect only (no display needed), so no headless flag is
required here - but we still guard init in case pygame needs it.
"""

import pygame
import pytest

from game.player import Player
from game.settings import load_settings


@pytest.fixture()
def settings():
    return load_settings()


@pytest.fixture()
def player(settings):
    return Player(x=100, y=100, settings=settings)


def test_initial_state_has_no_velocity(player):
    assert player.velocity_y == 0.0
    assert player.x == 100
    assert player.y == 100


def test_free_fall_increases_velocity_over_time(player):
    player.update(dt=0.1)
    expected_velocity = player.gravity * 0.1
    assert player.velocity_y == pytest.approx(expected_velocity)


def test_free_fall_moves_player_downward(player):
    start_y = player.y
    player.update(dt=0.1)
    assert player.y > start_y


def test_jump_sets_upward_velocity(player):
    player.jump()
    assert player.velocity_y == player.jump_velocity
    assert player.is_rising()


def test_jump_with_spring_multiplier_is_stronger(player):
    player.jump(boosted=False)
    normal_velocity = player.velocity_y

    player.jump(boosted=True)
    boosted_velocity = player.velocity_y

    # jump_velocity is negative (upward); a stronger jump is more negative.
    assert boosted_velocity < normal_velocity
    assert boosted_velocity == pytest.approx(player.jump_velocity * player.spring_multiplier)


def test_land_snaps_position_to_platform_top(player):
    platform_top_y = 400
    player.land(platform_top_y)
    assert player.y == platform_top_y - Player.HEIGHT


def test_land_triggers_auto_jump(player):
    player.velocity_y = 500  # was falling
    player.land(platform_top_y=400)
    assert player.is_rising()
    assert player.velocity_y == player.jump_velocity


def test_land_with_spring_boosts_jump(player):
    player.land(platform_top_y=400, boosted=True)
    assert player.velocity_y == pytest.approx(player.jump_velocity * player.spring_multiplier)


def test_is_falling_true_when_moving_down(player):
    player.velocity_y = 100
    assert player.is_falling() is True
    assert player.is_rising() is False


def test_is_rising_true_when_moving_up(player):
    player.velocity_y = -100
    assert player.is_rising() is True
    assert player.is_falling() is False


def test_rect_matches_position_and_size(player):
    r = player.rect
    assert r.x == int(player.x)
    assert r.y == int(player.y)
    assert r.width == Player.WIDTH
    assert r.height == Player.HEIGHT


def test_move_right_increases_x(player):
    start_x = player.x
    player.move(direction=1, dt=0.1)
    assert player.x == pytest.approx(start_x + player.horizontal_speed * 0.1)


def test_move_left_decreases_x(player):
    start_x = player.x
    player.move(direction=-1, dt=0.1)
    assert player.x == pytest.approx(start_x - player.horizontal_speed * 0.1)


def test_move_with_zero_direction_does_not_move(player):
    start_x = player.x
    player.move(direction=0, dt=0.1)
    assert player.x == start_x


def test_wrap_around_when_fully_off_left_edge(player):
    player.x = -Player.WIDTH - 1
    player.wrap_around(screen_width=480)
    assert player.x == 480


def test_wrap_around_when_fully_off_right_edge(player):
    player.x = 481
    player.wrap_around(screen_width=480)
    assert player.x == -Player.WIDTH


def test_wrap_around_does_nothing_when_on_screen(player):
    player.x = 200
    player.wrap_around(screen_width=480)
    assert player.x == 200


# --- Phase 11: sprite_key() -----------------------------------------------


def test_sprite_key_defaults_to_facing_right_and_standing(player):
    assert player.sprite_key() == "player_right_stand"


def test_sprite_key_is_jump_up_while_rising(player):
    player.velocity_y = -100
    assert player.sprite_key() == "player_right_jump_up"


def test_sprite_key_is_fall_down_while_falling(player):
    player.velocity_y = 100
    assert player.sprite_key() == "player_right_fall_down"


def test_sprite_key_is_run_while_moving_horizontally_with_no_vertical_velocity(
    player,
):
    player.move(direction=-1, dt=0.016)
    assert player.sprite_key() == "player_left_run"


def test_sprite_key_facing_persists_after_stopping(player):
    player.move(direction=-1, dt=0.016)
    player.move(direction=0, dt=0.016)  # stop moving, but still facing left
    assert player.sprite_key() == "player_left_stand"


def test_sprite_key_defaults_to_facing_right_before_any_movement(player):
    assert player.facing_right is True


def test_sprite_key_vertical_motion_takes_priority_over_run(player):
    """Per your confirmation: since the player is almost always
    airborne (continuous auto-jump), jump-up/fall-down should win over
    run/stand even if a horizontal key happens to be held too."""
    player.move(direction=1, dt=0.016)
    player.velocity_y = -50
    assert player.sprite_key() == "player_right_jump_up"
