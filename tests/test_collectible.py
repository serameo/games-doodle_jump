"""Unit tests for Phase 06: Coin and Diamond collectibles; sprite_key()
added in Phase 11."""

from game.collectible import Coin, Diamond


def test_coin_has_value_1():
    assert Coin(x=10, y=20).VALUE == 1


def test_diamond_has_value_3():
    assert Diamond(x=10, y=20).VALUE == 3


def test_coin_rect_matches_position_and_size():
    coin = Coin(x=10, y=20)
    r = coin.rect
    assert r.x == 10
    assert r.y == 20
    assert r.width == Coin.WIDTH
    assert r.height == Coin.HEIGHT


def test_coin_sprite_key():
    assert Coin(x=0, y=0).sprite_key() == "collectible_coin"


def test_diamond_sprite_key():
    assert Diamond(x=0, y=0).sprite_key() == "collectible_diamond"
