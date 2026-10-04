"""Unit tests for Phase 01: project bootstrap.

Runs with a dummy SDL video driver (set inside Game(headless=True)) so
no real window is required to run these tests.
"""

import pygame
import pytest

from main import Game


@pytest.fixture()
def game():
    g = Game(headless=True)
    yield g
    pygame.quit()


def test_window_size_matches_settings(game):
    assert game.screen.get_size() == (
        game.settings["screen_width"],
        game.settings["screen_height"],
    )


def test_fps_setting_loaded(game):
    assert game.settings["fps"] == 60


def test_handle_events_returns_true_with_no_events(game):
    pygame.event.clear()
    assert game.handle_events() is True


def test_handle_events_returns_false_on_quit(game):
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    assert game.handle_events() is False


def test_update_does_not_raise(game):
    game.update(dt=1 / 60)  # one 60 FPS frame; should simply not error.


def test_draw_does_not_raise(game):
    game.draw()  # Should render the placeholder background without error.
