"""Unit tests for Phase 06: map file loading (rules 2.4)."""

from game.collectible import Coin, Diamond
from game.map_loader import MapLoader, ROW_HEIGHT, cell_width, load_map_file
from game.platform import Platform
from game.special_platforms import (
    IcePlatform,
    MovingHorizontalPlatform,
    MovingVerticalPlatform,
    SpringPlatform,
    Wall,
)


def test_cell_width_divides_screen_into_confirmed_8_columns():
    assert cell_width(480) == 60  # Confirmed Decision #11


def test_load_map_file_parses_every_symbol_type(tmp_path):
    content = "!......!\n..=..d..\n..^...>.\n.c....C.\n..~..@..\n..=..=..\n"
    map_path = tmp_path / "map01.txt"
    map_path.write_text(content, encoding="ascii")

    platforms, collectibles, _ = load_map_file(
        str(map_path),
        start_y=0,
        screen_width=480,
        ice_melt_seconds=3.0,
        wall_fall_acceleration=2000.0,
        ice_broken_visible_seconds=0.3,
    )

    platform_types = {type(p) for p in platforms}
    assert platform_types == {
        Platform,
        IcePlatform,
        SpringPlatform,
        MovingVerticalPlatform,
        MovingHorizontalPlatform,
        Wall,
    }

    collectible_types = {type(c) for c in collectibles}
    assert collectible_types == {Coin, Diamond}


def test_load_map_file_places_rows_bottom_first_going_upward(tmp_path):
    # Bottom row (last line in the file) should end up closest to
    # start_y; the top row (first line) should be further up (smaller y).
    content = "=.......\n=.......\n"  # top row, then bottom row
    map_path = tmp_path / "map01.txt"
    map_path.write_text(content, encoding="ascii")

    platforms, _, next_y = load_map_file(
        str(map_path),
        start_y=1000,
        screen_width=480,
        ice_melt_seconds=3.0,
        wall_fall_acceleration=2000.0,
        ice_broken_visible_seconds=0.3,
    )

    ys = sorted(p.y for p in platforms)
    assert ys[0] == 1000 - 2 * ROW_HEIGHT  # top row: furthest up
    assert ys[1] == 1000 - ROW_HEIGHT  # bottom row: closest to start
    assert next_y == 1000 - 2 * ROW_HEIGHT


def test_load_map_file_x_positions_match_the_column_grid(tmp_path):
    content = "=......=\n"  # column 0 and column 7
    map_path = tmp_path / "map01.txt"
    map_path.write_text(content, encoding="ascii")

    platforms, _, _ = load_map_file(
        str(map_path),
        start_y=1000,
        screen_width=480,
        ice_melt_seconds=3.0,
        wall_fall_acceleration=2000.0,
        ice_broken_visible_seconds=0.3,
    )

    xs = sorted(p.x for p in platforms)
    assert xs == [0, 7 * 60]


def test_load_map_file_ignores_blank_lines(tmp_path):
    content = "=.......\n\n=.......\n"
    map_path = tmp_path / "map01.txt"
    map_path.write_text(content, encoding="ascii")

    platforms, _, _ = load_map_file(
        str(map_path),
        start_y=1000,
        screen_width=480,
        ice_melt_seconds=3.0,
        wall_fall_acceleration=2000.0,
        ice_broken_visible_seconds=0.3,
    )
    assert len(platforms) == 2


def test_load_map_file_uses_configured_ice_melt_seconds(tmp_path):
    content = "~.......\n"
    map_path = tmp_path / "map01.txt"
    map_path.write_text(content, encoding="ascii")

    platforms, _, _ = load_map_file(
        str(map_path),
        start_y=1000,
        screen_width=480,
        ice_melt_seconds=1.5,
        wall_fall_acceleration=2000.0,
        ice_broken_visible_seconds=0.3,
    )
    assert platforms[0].melt_seconds == 1.5


def test_load_map_file_uses_configured_wall_fall_acceleration(tmp_path):
    content = "!.......\n"
    map_path = tmp_path / "map01.txt"
    map_path.write_text(content, encoding="ascii")

    platforms, _, _ = load_map_file(
        str(map_path),
        start_y=1000,
        screen_width=480,
        ice_melt_seconds=3.0,
        wall_fall_acceleration=1234.0,
        ice_broken_visible_seconds=0.3,
    )
    assert platforms[0].fall_acceleration == 1234.0
    assert platforms[0].falling is False  # not triggered until landed on


def test_load_map_file_uses_configured_ice_broken_visible_seconds(tmp_path):
    content = "~.......\n"
    map_path = tmp_path / "map01.txt"
    map_path.write_text(content, encoding="ascii")

    platforms, _, _ = load_map_file(
        str(map_path),
        start_y=1000,
        screen_width=480,
        ice_melt_seconds=3.0,
        wall_fall_acceleration=2000.0,
        ice_broken_visible_seconds=0.75,
    )
    assert platforms[0].broken_visible_seconds == 0.75


def test_map_loader_loads_files_in_numeric_order(tmp_path):
    (tmp_path / "map01.txt").write_text("=.......\n", encoding="ascii")
    (tmp_path / "map02.txt").write_text("=.......\n", encoding="ascii")

    loader = MapLoader(
        maps_dir=str(tmp_path),
        screen_width=480,
        ice_melt_seconds=3.0,
        wall_fall_acceleration=2000.0,
        ice_broken_visible_seconds=0.3,
    )

    assert loader.has_next_map() is True
    platforms_1, _, next_y_1 = loader.load_next(start_y=1000)
    assert len(platforms_1) == 1
    assert next_y_1 == 1000 - ROW_HEIGHT

    assert loader.has_next_map() is True
    platforms_2, _, next_y_2 = loader.load_next(start_y=next_y_1)
    assert len(platforms_2) == 1
    assert next_y_2 == next_y_1 - ROW_HEIGHT

    assert loader.has_next_map() is False


def test_map_loader_load_next_with_no_more_maps_returns_empty(tmp_path):
    loader = MapLoader(
        maps_dir=str(tmp_path),
        screen_width=480,
        ice_melt_seconds=3.0,
        wall_fall_acceleration=2000.0,
        ice_broken_visible_seconds=0.3,
    )
    platforms, collectibles, next_y = loader.load_next(start_y=500)
    assert platforms == []
    assert collectibles == []
    assert next_y == 500


def test_shipped_demo_map_files_parse_without_error():
    """Sanity check for the actual maps/map01.txt and map02.txt shipped
    with the project (not synthetic tmp_path files)."""
    from main import MAPS_DIR

    loader = MapLoader(
        maps_dir=MAPS_DIR,
        screen_width=480,
        ice_melt_seconds=3.0,
        wall_fall_acceleration=2000.0,
        ice_broken_visible_seconds=0.3,
    )

    assert loader.has_next_map() is True
    platforms_1, collectibles_1, next_y = loader.load_next(start_y=250)
    assert len(platforms_1) > 0
    assert len(collectibles_1) > 0

    assert loader.has_next_map() is True
    platforms_2, _, next_y_2 = loader.load_next(start_y=next_y)
    assert len(platforms_2) > 0

    assert loader.has_next_map() is False
