"""Unit tests for Phase 09: difficulty scaling (scroll speed).

Confirmed Decision #2 (docs/doodle_jump_plans.md): scroll speed
increases 2% per 30 points scored, capped at a maximum multiplier, then
holds steady.
"""

import pytest

from game.difficulty import current_scroll_speed, scroll_speed_multiplier


def test_multiplier_is_one_below_the_first_interval():
    assert scroll_speed_multiplier(0, 30, 0.02, 2.0) == pytest.approx(1.0)
    assert scroll_speed_multiplier(29, 30, 0.02, 2.0) == pytest.approx(1.0)


def test_multiplier_increases_by_two_percent_at_thirty_points():
    assert scroll_speed_multiplier(30, 30, 0.02, 2.0) == pytest.approx(1.02)


def test_multiplier_stacks_across_multiple_intervals():
    assert scroll_speed_multiplier(90, 30, 0.02, 2.0) == pytest.approx(1.06)
    assert scroll_speed_multiplier(150, 30, 0.02, 2.0) == pytest.approx(1.10)


def test_multiplier_is_capped_at_the_configured_maximum():
    # 100 intervals of 2% would be 3.0x uncapped - must clamp to 2.0x.
    assert scroll_speed_multiplier(3000, 30, 0.02, 2.0) == pytest.approx(2.0)


def test_multiplier_holds_steady_once_capped():
    at_cap = scroll_speed_multiplier(3000, 30, 0.02, 2.0)
    well_past_cap = scroll_speed_multiplier(30000, 30, 0.02, 2.0)
    assert at_cap == pytest.approx(well_past_cap)


def test_current_scroll_speed_applies_the_multiplier_to_the_base_speed():
    settings = {
        "base_scroll_speed": 30.0,
        "score_interval": 30,
        "speed_increase_per_interval": 0.02,
        "max_speed_multiplier": 2.0,
    }
    assert current_scroll_speed(0, settings) == pytest.approx(30.0)
    assert current_scroll_speed(30, settings) == pytest.approx(30.0 * 1.02)


def test_current_scroll_speed_is_capped_at_max_speed_multiplier_times_base():
    settings = {
        "base_scroll_speed": 30.0,
        "score_interval": 30,
        "speed_increase_per_interval": 0.02,
        "max_speed_multiplier": 2.0,
    }
    assert current_scroll_speed(100000, settings) == pytest.approx(60.0)
