"""Difficulty scaling (Phase 09; Confirmed Decision #2 in
docs/doodle_jump_plans.md): scroll speed increases 2% for every 30
points scored, capped at a maximum multiplier, then holds steady.

All tunable numbers come from config/settings.json, same convention as
every other tunable value in this project (gravity, jump velocity,
ice-melt timer, and so on):

- base_scroll_speed: scroll speed in px/sec before any score-based
  scaling (rules 2.1 Overview: "the screen scrolls downward slowly and
  continuously" - this is that baseline).
- score_interval: points needed to trigger one more speed-increase step
  (30, per Confirmed Decision #2).
- speed_increase_per_interval: fractional increase applied per interval
  (0.02 = 2%, per Confirmed Decision #2).
- max_speed_multiplier: hard cap on the multiplier (2.0), after which
  scroll speed holds steady regardless of further score.
"""


def scroll_speed_multiplier(
    score_value: int,
    score_interval: int,
    speed_increase_per_interval: float,
    max_speed_multiplier: float,
) -> float:
    """1.0 plus speed_increase_per_interval for every full score_interval
    points scored so far, capped at max_speed_multiplier.

    E.g. with the default 30-point interval and 2% step: 0-29 points ->
    1.0x, 30-59 -> 1.02x, 60-89 -> 1.04x, and so on, never exceeding
    max_speed_multiplier.
    """
    if score_interval <= 0:
        # Degenerate config - treat every point as a fresh interval
        # rather than dividing by zero.
        return max_speed_multiplier

    intervals_reached = score_value // score_interval
    multiplier = 1.0 + intervals_reached * speed_increase_per_interval
    return min(multiplier, max_speed_multiplier)


def current_scroll_speed(score_value: int, settings: dict) -> float:
    """The actual scroll speed in px/sec for the given score, combining
    settings["base_scroll_speed"] with the current multiplier."""
    multiplier = scroll_speed_multiplier(
        score_value,
        settings["score_interval"],
        settings["speed_increase_per_interval"],
        settings["max_speed_multiplier"],
    )
    return settings["base_scroll_speed"] * multiplier
