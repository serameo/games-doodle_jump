"""Unit tests for Phase 04: PlatformSpawner (random, reachable generation)."""

import random

import pytest

from game.collectible import Coin, Diamond
from game.platform import Platform
from game.platform_spawner import PlatformSpawner


@pytest.fixture()
def spawner():
    # Seeded RNG so results are deterministic and repeatable across runs.
    return PlatformSpawner(screen_width=480, rng=random.Random(42))


def test_next_platform_gap_within_reachable_range(spawner):
    for _ in range(200):
        platform = spawner.next_platform(previous_y=1000)
        gap = 1000 - platform.y
        assert PlatformSpawner.MIN_GAP <= gap <= PlatformSpawner.MAX_GAP


def test_next_platform_is_above_previous(spawner):
    platform = spawner.next_platform(previous_y=1000)
    assert platform.y < 1000


def test_next_platform_x_within_screen_bounds(spawner):
    for _ in range(200):
        platform = spawner.next_platform(previous_y=1000)
        assert 0 <= platform.x <= spawner.screen_width - Platform.WIDTH


def test_generate_column_stops_at_or_above_top_y(spawner):
    platforms = spawner.generate_column(start_y=1000, top_y=500)
    assert len(platforms) > 0
    assert platforms[-1].y <= 500


def test_generate_column_each_gap_is_reachable(spawner):
    platforms = spawner.generate_column(start_y=1000, top_y=200)
    previous_y = 1000
    for platform in platforms:
        gap = previous_y - platform.y
        assert PlatformSpawner.MIN_GAP <= gap <= PlatformSpawner.MAX_GAP
        previous_y = platform.y


def test_generate_column_is_deterministic_with_same_seed():
    spawner_a = PlatformSpawner(screen_width=480, rng=random.Random(7))
    spawner_b = PlatformSpawner(screen_width=480, rng=random.Random(7))

    result_a = spawner_a.generate_column(start_y=1000, top_y=400)
    result_b = spawner_b.generate_column(start_y=1000, top_y=400)

    assert [(p.x, p.y) for p in result_a] == [(p.x, p.y) for p in result_b]


def test_generate_column_empty_when_start_already_above_top(spawner):
    assert spawner.generate_column(start_y=100, top_y=500) == []


def test_generate_collectibles_places_coin_every_5th_floor(spawner):
    platforms = spawner.generate_column(start_y=2000, top_y=0)
    collectibles = spawner.generate_collectibles(platforms)

    coin_count = sum(1 for c in collectibles if isinstance(c, Coin))
    expected_coin_count = len(platforms) // 5
    assert coin_count == expected_coin_count


def test_generate_collectibles_places_diamond_every_10th_floor(spawner):
    platforms = spawner.generate_column(start_y=3000, top_y=0)
    collectibles = spawner.generate_collectibles(platforms)

    diamond_count = sum(1 for c in collectibles if isinstance(c, Diamond))
    expected_diamond_count = len(platforms) // 10
    assert diamond_count == expected_diamond_count


def test_generate_collectibles_none_for_short_column(spawner):
    # Fewer than 5 platforms: no coin or diamond should be generated.
    platforms = spawner.generate_column(start_y=1000, top_y=850)
    assert len(platforms) < 5
    collectibles = spawner.generate_collectibles(platforms)
    assert collectibles == []


def test_generate_collectibles_10th_floor_gets_both_coin_and_diamond(spawner):
    # Force exactly 10 platforms by chaining next_platform manually.
    platforms = []
    current_y = 5000
    for _ in range(10):
        platform = spawner.next_platform(current_y)
        platforms.append(platform)
        current_y = platform.y

    collectibles = spawner.generate_collectibles(platforms)
    types_at_10th_floor_position = [type(c) for c in collectibles]
    assert Coin in types_at_10th_floor_position
    assert Diamond in types_at_10th_floor_position
