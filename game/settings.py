"""Loads tunable game settings from config/settings.json.

Values such as screen size, frame rate, and the ice-platform melt timer
are kept in an external settings file (rather than hardcoded constants)
so gameplay can be tuned without touching source code. See Confirmed
Decisions in docs/doodle_jump_plans.md.
"""

import json
import os

_SETTINGS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config",
    "settings.json",
)

# Fallback values used if config/settings.json is missing or incomplete.
_DEFAULTS = {
    "screen_width": 480,
    "screen_height": 800,
    "fps": 60,
    "ice_melt_seconds": 3.0,
    "ice_broken_visible_seconds": 0.3,
    "max_speed_multiplier": 2.0,
    "speed_increase_per_interval": 0.02,
    "score_interval": 30,
    "base_scroll_speed": 30.0,
    "gravity": 2000.0,
    "jump_velocity": -900.0,
    "spring_multiplier": 1.5,
    "player_horizontal_speed": 300.0,
}


def load_settings() -> dict:
    """Return settings merged from config/settings.json over the defaults."""
    settings = dict(_DEFAULTS)
    if os.path.exists(_SETTINGS_PATH):
        with open(_SETTINGS_PATH, "r", encoding="utf-8") as settings_file:
            settings.update(json.load(settings_file))
    return settings
