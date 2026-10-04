"""Unit tests for Phase 03: Platform base class (static brick variant)."""

import pytest

from game.platform import Platform


@pytest.fixture()
def platform():
    return Platform(x=100, y=200)


def test_rect_matches_position_and_size(platform):
    r = platform.rect
    assert r.x == 100
    assert r.y == 200
    assert r.width == Platform.WIDTH
    assert r.height == Platform.HEIGHT


def test_is_solid_is_always_true_for_brick(platform):
    assert platform.is_solid() is True


def test_update_does_not_move_static_platform(platform):
    platform.update(dt=1.0)
    assert platform.x == 100
    assert platform.y == 200


def test_sprite_key_is_platform_brick(platform):
    assert platform.sprite_key() == "platform_brick"
