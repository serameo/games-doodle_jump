"""Unit tests for Phase 10: the game-over state machine (plus its
Phase 10 addendum title-screen state) and the fell-off-screen check
(rules 2.1)."""

import pytest

from game.camera import Camera
from game.game_state import GameState, GameStatus, has_fallen_off_screen
from game.player import Player

SETTINGS = {
    "gravity": 2000.0,
    "jump_velocity": -900.0,
    "spring_multiplier": 1.5,
    "player_horizontal_speed": 300.0,
}


def make_player(y: float) -> Player:
    return Player(x=0, y=y, settings=SETTINGS)


# --- GameState ---------------------------------------------------------


def test_starts_on_the_title_screen():
    """Phase 10 addendum: the title screen is shown first, before any
    gameplay or game-over state."""
    state = GameState()
    assert state.is_main_menu() is True
    assert state.is_playing() is False
    assert state.is_game_over() is False
    assert state.status is GameStatus.MAIN_MENU


def test_resume_playing_switches_to_playing():
    state = GameState()
    state.resume_playing()
    assert state.is_playing() is True
    assert state.is_main_menu() is False
    assert state.status is GameStatus.PLAYING


def test_trigger_game_over_switches_state():
    state = GameState()
    state.resume_playing()
    state.trigger_game_over()
    assert state.is_game_over() is True
    assert state.is_playing() is False
    assert state.status is GameStatus.GAME_OVER


def test_resume_playing_switches_back_from_game_over():
    state = GameState()
    state.resume_playing()
    state.trigger_game_over()
    state.resume_playing()
    assert state.is_game_over() is False
    assert state.is_playing() is True
    assert state.status is GameStatus.PLAYING


def test_show_main_menu_switches_back_from_game_over():
    """Phase 10 addendum: the game-over menu's 'Quit' returns to the
    title screen rather than exiting the application."""
    state = GameState()
    state.resume_playing()
    state.trigger_game_over()
    state.show_main_menu()
    assert state.is_main_menu() is True
    assert state.is_game_over() is False
    assert state.status is GameStatus.MAIN_MENU


# --- has_fallen_off_screen ----------------------------------------------


@pytest.fixture()
def camera():
    camera = Camera(screen_height=800, player_height=40)
    camera.update(dt=0.0, player_y=100, scroll_speed=0.0)  # centers on y=100
    return camera


def test_player_within_screen_has_not_fallen_off(camera):
    player = make_player(y=100)  # matches the camera's centered player
    assert has_fallen_off_screen(player, camera, screen_height=800) is False


def test_player_far_below_screen_has_fallen_off(camera):
    player = make_player(y=100 + 2000)  # way below the visible window
    assert has_fallen_off_screen(player, camera, screen_height=800) is True


def test_player_exactly_at_bottom_edge_has_not_fallen_off(camera):
    # Feet exactly on the bottom edge should not count as "below" it.
    screen_height = 800
    feet_world_y = camera.offset_y + screen_height  # feet land exactly on edge
    player = make_player(y=feet_world_y - Player.HEIGHT)
    assert has_fallen_off_screen(player, camera, screen_height) is False


def test_player_one_pixel_below_bottom_edge_has_fallen_off(camera):
    screen_height = 800
    feet_world_y = camera.offset_y + screen_height + 1
    player = make_player(y=feet_world_y - Player.HEIGHT)
    assert has_fallen_off_screen(player, camera, screen_height) is True
