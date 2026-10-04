"""Unit tests for Phase 08: Score tracking and collectible pickup."""

import pytest

from game.collectible import Coin, Diamond
from game.player import Player
from game.score import Score, collect_collectibles
from game.settings import load_settings


def test_score_starts_at_zero():
    assert Score().value == 0


def test_score_add_increments_value():
    score = Score()
    score.add(1)
    score.add(3)
    assert score.value == 4


@pytest.fixture()
def player():
    return Player(x=100, y=100, settings=load_settings())


def test_collect_collectibles_awards_points_for_overlap(player):
    score = Score()
    coin = Coin(x=100, y=100)  # exactly overlapping the player
    remaining = collect_collectibles(player, [coin], score)

    assert score.value == 1
    assert remaining == []


def test_collect_collectibles_leaves_non_overlapping_items(player):
    score = Score()
    far_coin = Coin(x=1000, y=1000)  # nowhere near the player
    remaining = collect_collectibles(player, [far_coin], score)

    assert score.value == 0
    assert remaining == [far_coin]


def test_collect_collectibles_diamond_worth_three(player):
    score = Score()
    diamond = Diamond(x=100, y=100)
    collect_collectibles(player, [diamond], score)
    assert score.value == 3


def test_collect_collectibles_mixed_overlap(player):
    score = Score()
    picked_up = Coin(x=100, y=100)
    left_behind = Coin(x=1000, y=1000)
    remaining = collect_collectibles(player, [picked_up, left_behind], score)

    assert score.value == 1
    assert remaining == [left_behind]
