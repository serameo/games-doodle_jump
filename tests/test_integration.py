"""End-to-end tests: exercise each special platform type through the
real Game object (main.py), not isolated unit calls on Platform classes
directly. This verifies the whole pipeline - input, physics, collision,
and per-platform hooks - works together the way it will when you
actually play, including regression coverage for two bugs found during
manual testing after Phase 05:

1. Collision tunneling: a fast-falling player could skip clean through a
   thin platform within a single frame (fixed via swept collision in
   game/collision.py).
2. No horizontal control: the player never moved on the x-axis, so it
   would eventually miss every platform and fall forever (fixed by
   adding keyboard-driven Player.move()/wrap_around(), wired into
   Game.update() in main.py).
"""

import pygame
import pytest

from main import Game
from game.collectible import Coin, Diamond
from game.special_platforms import (
    IcePlatform,
    MovingHorizontalPlatform,
    MovingVerticalPlatform,
    SpringPlatform,
    Wall,
)


@pytest.fixture()
def game():
    g = Game(headless=True)
    # Phase 10 addendum: Game now starts on the title screen. Skip past
    # it here so every existing gameplay test keeps testing gameplay,
    # not the title screen itself (which has its own tests below).
    g.game_state.resume_playing()
    return g


def _find(game, platform_type):
    return next(p for p in game.platforms if isinstance(p, platform_type))


def _drop_player_onto(game, platform, dt=1 / 60):
    """Position the player directly above a platform, falling, then run
    exactly one real Game.update() frame - exercising the full pipeline
    (input -> physics -> collision -> platform hook) at once."""
    game.player.x = platform.x
    game.player.y = platform.rect.top - game.player.HEIGHT
    game.player.previous_y = game.player.y
    game.player.velocity_y = 200  # falling
    game.update(dt)


def test_all_special_platform_types_exist_on_screen(game):
    """Sanity check that Phase 05's demo layout is actually present."""
    assert _find(game, IcePlatform) is not None
    assert _find(game, SpringPlatform) is not None
    assert _find(game, MovingVerticalPlatform) is not None
    assert _find(game, MovingHorizontalPlatform) is not None


def test_landing_on_ice_starts_melting_end_to_end(game):
    ice = _find(game, IcePlatform)
    assert ice.melting is False

    _drop_player_onto(game, ice)

    assert ice.melting is True
    assert ice.is_solid() is True  # just started, not melted yet
    assert game.player.is_rising() is True  # auto-jumped after landing


def test_ice_disappears_after_melt_time_end_to_end(game):
    ice = _find(game, IcePlatform)
    _drop_player_onto(game, ice)
    assert ice.is_solid() is True

    # Advance real game frames covering the full melt timer.
    total_time = 0.0
    dt = 1 / 60
    while total_time < ice.melt_seconds + 0.5:
        game.update(dt)
        total_time += dt

    assert ice.is_solid() is False


def test_landing_on_spring_gives_a_boosted_bounce_end_to_end(game):
    spring = _find(game, SpringPlatform)

    _drop_player_onto(game, spring)

    expected_boosted_velocity = game.player.jump_velocity * game.player.spring_multiplier
    assert game.player.velocity_y == pytest.approx(expected_boosted_velocity)


def test_landing_on_spring_bounces_higher_than_a_normal_platform(game):
    """Compare against the starting (brick) platform to show the boost
    actually makes a measurable difference, not just a nonzero one."""
    spring = _find(game, SpringPlatform)
    brick = game.platforms[0]  # the Phase 04 starting brick platform

    _drop_player_onto(game, spring)
    boosted_velocity = game.player.velocity_y

    _drop_player_onto(game, brick)
    normal_velocity = game.player.velocity_y

    # Both velocities are negative (upward); boosted is more negative.
    assert boosted_velocity < normal_velocity


def test_moving_vertical_platform_visibly_moves_over_real_frames(game):
    moving_v = _find(game, MovingVerticalPlatform)
    start_y = moving_v.y

    for _ in range(30):  # half a second at 60 FPS
        game.update(1 / 60)

    assert moving_v.y != start_y
    assert moving_v.x == moving_v.origin_x  # only moves vertically


def test_moving_horizontal_platform_visibly_moves_over_real_frames(game):
    moving_h = _find(game, MovingHorizontalPlatform)
    start_x = moving_h.x

    for _ in range(30):
        game.update(1 / 60)

    assert moving_h.x != start_x
    assert moving_h.y == moving_h.origin_y  # only moves horizontally


def test_player_can_still_land_on_a_moving_platform_end_to_end(game):
    moving_v = _find(game, MovingVerticalPlatform)

    _drop_player_onto(game, moving_v)

    assert game.player.is_rising() is True  # auto-jump triggered


def test_scripted_playthrough_lands_on_every_platform_without_diverging(game):
    """Regression test for the reported bug (player floats up and never
    comes back): walk the player up through every *landable* platform in
    order, aligning x with each one before it falls (simulating correct
    player input), and confirm it successfully lands on every single one
    - brick, ice, spring, and both moving types - via the real collision
    pipeline. Walls are excluded: they are intentionally never landable
    (rules 2.2 - see game/special_platforms.py's Wall docstring). If
    tunneling were still present, some of these landings would be missed
    and the player's y would run away instead of tracking each platform
    closely."""
    landable_platforms = [p for p in game.platforms if not isinstance(p, Wall)]
    platforms_bottom_to_top = sorted(
        landable_platforms, key=lambda p: p.y, reverse=True
    )

    for platform in platforms_bottom_to_top:
        _drop_player_onto(game, platform)
        assert game.player.is_rising() is True
        # The player should now be resting almost exactly on this
        # platform's top, not off somewhere far away.
        assert abs(game.player.y - (platform.rect.top - game.player.HEIGHT)) < 5


def test_player_wraps_instead_of_getting_stuck_off_screen(game):
    game.player.x = game.settings["screen_width"] + 100  # far off the right
    game.player.wrap_around(game.settings["screen_width"])
    assert game.player.x < game.settings["screen_width"]


def test_camera_keeps_player_on_screen_while_climbing(game):
    """Phase 07 regression coverage: as the player climbs through the
    demo layout via the scripted playthrough, the camera should keep
    translating world y into a screen y that stays within the visible
    window - proving world position and camera offset move together."""
    landable_platforms = [p for p in game.platforms if not isinstance(p, Wall)]
    platforms_bottom_to_top = sorted(
        landable_platforms, key=lambda p: p.y, reverse=True
    )
    screen_height = game.settings["screen_height"]

    for platform in platforms_bottom_to_top:
        _drop_player_onto(game, platform)
        # scroll_speed=0 isolates the ratchet-follow behavior being
        # tested here (climbing keeps the player on screen) from the
        # separate Phase 09 auto-scroll, which has its own tests below.
        game.camera.update(dt=1 / 60, player_y=game.player.y, scroll_speed=0)
        player_screen_y = game.camera.to_screen_y(game.player.y)
        assert 0 <= player_screen_y <= screen_height


def test_picking_up_a_coin_end_to_end_increases_score_and_removes_it(game):
    coin = next(c for c in game.collectibles if isinstance(c, Coin))
    starting_count = len(game.collectibles)

    game.player.x = coin.x
    game.player.y = coin.y
    game.player.previous_y = coin.y
    game.update(1 / 60)

    assert game.score.value == 1
    assert coin not in game.collectibles
    assert len(game.collectibles) == starting_count - 1


def test_picking_up_a_diamond_end_to_end_adds_three_points(game):
    diamond = next(c for c in game.collectibles if isinstance(c, Diamond))

    game.player.x = diamond.x
    game.player.y = diamond.y
    game.player.previous_y = diamond.y
    game.update(1 / 60)

    assert game.score.value == 3
    assert diamond not in game.collectibles


def test_score_accumulates_across_multiple_pickups(game):
    coin = next(c for c in game.collectibles if isinstance(c, Coin))
    game.player.x = coin.x
    game.player.y = coin.y
    game.player.previous_y = coin.y
    game.update(1 / 60)
    assert game.score.value == 1

    diamond = next(c for c in game.collectibles if isinstance(c, Diamond))
    game.player.x = diamond.x
    game.player.y = diamond.y
    game.player.previous_y = diamond.y
    game.update(1 / 60)
    assert game.score.value == 1 + 3


def test_camera_auto_scrolls_over_real_frames_even_if_player_holds_still(game):
    """Phase 09 end-to-end: the camera should keep advancing on its own,
    purely from real Game.update() frames ticking by, even with the
    player sitting motionless (not falling, not climbing)."""
    game.player.velocity_y = 0.0
    start_offset = game.camera.offset_y

    for _ in range(120):  # 2 seconds at 60 FPS
        game.player.previous_y = game.player.y  # freeze in place
        game.player.velocity_y = 0.0
        game.update(1 / 60)

    assert game.camera.offset_y < start_offset


def test_scroll_speed_increases_after_scoring_thirty_points_end_to_end(game):
    """Picking up enough coins/diamonds to cross a 30-point interval
    should measurably speed up the camera's auto-scroll, through the
    real Game object end to end."""
    from game.difficulty import current_scroll_speed

    speed_before = current_scroll_speed(game.score.value, game.settings)
    game.score.add(30)  # cross exactly one interval
    speed_after = current_scroll_speed(game.score.value, game.settings)

    assert speed_after > speed_before


def test_falling_after_climbing_does_not_pull_the_camera_back_down(game):
    """Phase 09 end-to-end regression: once the camera has ratcheted up
    to follow a climb, a subsequent fall must not drag it back down -
    this is what makes falling behind the scroll dangerous (Phase 10's
    game-over condition)."""
    landable_platforms = [p for p in game.platforms if not isinstance(p, Wall)]
    platforms_bottom_to_top = sorted(
        landable_platforms, key=lambda p: p.y, reverse=True
    )

    # Climb up through a few platforms to ratchet the camera upward.
    for platform in platforms_bottom_to_top[:3]:
        _drop_player_onto(game, platform)

    offset_after_climbing = game.camera.offset_y

    # Now simulate the player falling straight down, well below where
    # the camera has already scrolled to.
    game.player.previous_y = game.player.y
    game.player.y += 500
    game.player.velocity_y = 200  # falling
    dt = 1 / 60
    game.update(dt)

    # The only change allowed is the continuous auto-scroll itself
    # (independent of the player) - the fall must not additionally pull
    # the offset back down toward the player.
    from game.difficulty import current_scroll_speed

    scroll_speed = current_scroll_speed(game.score.value, game.settings)
    expected_offset = offset_after_climbing - scroll_speed * dt
    assert game.camera.offset_y == pytest.approx(expected_offset)


# --- Phase 10: game over flow ------------------------------------------


def _fall_off_screen(game):
    """Helper: force the player far below wherever the camera has
    already climbed to (well past every generated platform, which all
    sit at or above the starting platform's y=250), then run one real
    Game.update() frame - this is what should trigger Phase 10's
    game-over condition."""
    game.player.previous_y = game.player.y
    game.player.y += 5000
    game.player.velocity_y = 200  # falling
    game.update(1 / 60)


def test_falling_far_below_screen_triggers_game_over_end_to_end(game):
    assert game.game_state.is_game_over() is False
    _fall_off_screen(game)
    assert game.game_state.is_game_over() is True


def test_gameplay_freezes_once_game_over_end_to_end(game):
    _fall_off_screen(game)
    frozen_y = game.player.y
    frozen_score = game.score.value

    game.update(1 / 60)  # should be a no-op while the menu is up

    assert game.player.y == frozen_y
    assert game.score.value == frozen_score


def test_continue_resets_player_and_score_but_restores_the_same_layout(game):
    coin = next(c for c in game.collectibles if isinstance(c, Coin))
    game.player.x = coin.x
    game.player.y = coin.y
    game.player.previous_y = coin.y
    game.update(1 / 60)  # pick up the coin
    assert game.score.value == 1
    collectible_count_after_pickup = len(game.collectibles)

    _fall_off_screen(game)
    assert game.game_state.is_game_over() is True

    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_c))
    game.handle_events()

    assert game.game_state.is_game_over() is False
    assert game.score.value == 0
    assert game.player.y == pytest.approx(100)
    # The picked-up coin should be back - Continue restores the exact
    # same layout the run started with.
    assert len(game.collectibles) == collectible_count_after_pickup + 1


def test_new_game_resets_and_rebuilds_the_world_end_to_end(game):
    original_platform_count = len(game.platforms)
    original_fallback_xs = [p.x for p in game.platforms[-5:]]

    _fall_off_screen(game)
    assert game.game_state.is_game_over() is True

    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_n))
    game.handle_events()

    assert game.game_state.is_game_over() is False
    assert game.score.value == 0
    assert game.player.y == pytest.approx(100)
    assert len(game.platforms) == original_platform_count
    # A brand-new random fallback column should not exactly match the
    # very first one (astronomically unlikely to coincide by chance),
    # confirming the world was actually rebuilt, not just reset.
    new_fallback_xs = [p.x for p in game.platforms[-5:]]
    assert new_fallback_xs != original_fallback_xs


def test_quit_key_from_game_over_returns_to_title_screen_end_to_end(game):
    """Phase 10 addendum: game-over's 'Quit' now returns to the title
    screen rather than closing the application outright."""
    _fall_off_screen(game)
    assert game.game_state.is_game_over() is True

    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q))
    assert game.handle_events() is True  # app keeps running
    assert game.game_state.is_main_menu() is True
    assert game.game_state.is_game_over() is False


def test_menu_keys_are_ignored_while_still_playing(game):
    """Pressing C/N/Q should do nothing during normal gameplay - only
    once the game-over menu is showing."""
    assert game.game_state.is_game_over() is False
    original_player = game.player

    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_n))
    assert game.handle_events() is True
    assert game.player is original_player  # world was not rebuilt
    assert game.game_state.is_game_over() is False


# --- Phase 10 addendum: title-screen main menu --------------------------


def test_new_game_starts_on_the_title_screen():
    """Phase 10 addendum: a fresh Game() shows the title screen first -
    gameplay does not start automatically."""
    fresh_game = Game(headless=True)
    assert fresh_game.game_state.is_main_menu() is True
    assert fresh_game.game_state.is_playing() is False


def test_gameplay_is_frozen_while_on_the_title_screen():
    fresh_game = Game(headless=True)
    player_y_before = fresh_game.player.y

    fresh_game.update(1 / 60)

    assert fresh_game.player.y == player_y_before


def test_enter_key_starts_the_game_from_the_title_screen():
    fresh_game = Game(headless=True)
    assert fresh_game.game_state.is_main_menu() is True

    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    assert fresh_game.handle_events() is True

    assert fresh_game.game_state.is_playing() is True
    assert fresh_game.score.value == 0
    assert fresh_game.player.y == pytest.approx(100)


def test_quit_key_from_title_screen_stops_the_game():
    fresh_game = Game(headless=True)
    assert fresh_game.game_state.is_main_menu() is True

    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q))
    assert fresh_game.handle_events() is False


# --- Phase 11: sprite art -------------------------------------------------


EXPECTED_SPRITE_KEYS = {
    "player_right_stand",
    "player_right_run",
    "player_right_jump_up",
    "player_right_fall_down",
    "player_left_stand",
    "player_left_run",
    "player_left_jump_up",
    "player_left_fall_down",
    "collectible_coin",
    "collectible_diamond",
    "platform_brick",
    "platform_ice_solid",
    "platform_ice_cracking",
    "platform_ice_broken",
    "platform_spring",
    "platform_moving_horizontal",
    "platform_moving_vertical",
    "platform_wall",
}


def test_all_expected_sprites_are_loaded(game):
    """Every sprite key any entity can ever return should actually be
    loaded - this is what lets main.py trust sprite_key() lookups
    instead of silently falling back to a colored rectangle."""
    assert EXPECTED_SPRITE_KEYS.issubset(game.sprites.keys())


def test_loaded_sprites_match_their_entity_pixel_sizes(game):
    """Each pre-sliced sprite must exactly match the entity's existing
    collision-box size (the whole point of pre-slicing at build time
    instead of scaling at runtime)."""
    from game.player import Player
    from game.platform import Platform
    from game.collectible import Collectible

    for key in EXPECTED_SPRITE_KEYS:
        surface = game.sprites[key]
        if key.startswith("player_"):
            assert surface.get_size() == (Player.WIDTH, Player.HEIGHT)
        elif key.startswith("platform_"):
            assert surface.get_size() == (Platform.WIDTH, Platform.HEIGHT)
        elif key.startswith("collectible_"):
            assert surface.get_size() == (Collectible.WIDTH, Collectible.HEIGHT)


def test_every_platform_in_a_real_game_has_a_loaded_sprite(game):
    """End-to-end guard against a sprite_key() typo: every platform
    actually generated in a real run (maps + random fallback column)
    must resolve to a sprite that was actually loaded."""
    for platform in game.platforms:
        assert platform.sprite_key() in game.sprites


def test_every_collectible_in_a_real_game_has_a_loaded_sprite(game):
    for collectible in game.collectibles:
        assert collectible.sprite_key() in game.sprites


def test_player_sprite_key_has_a_loaded_sprite_in_every_state(game):
    for facing_right in (True, False):
        game.player.facing_right = facing_right
        for velocity_y, moving in (
            (-50, False),
            (50, False),
            (0, False),
            (0, True),
        ):
            game.player.velocity_y = velocity_y
            game.player.moving_horizontally = moving
            assert game.player.sprite_key() in game.sprites


def test_ice_platform_sprite_stays_loaded_through_the_full_melt_cycle(game):
    """End-to-end: as a real IcePlatform (from the shipped maps) melts
    over actual gameplay frames, every sprite it cycles through along
    the way must be one that was actually loaded."""
    from game.special_platforms import IcePlatform

    ice = next((p for p in game.platforms if isinstance(p, IcePlatform)), None)
    if ice is None:
        pytest.skip("no IcePlatform in the shipped maps' current layout")

    ice.on_landed()
    seen_keys = set()
    for _ in range(int(ice.melt_seconds / 0.05) + 10):
        seen_keys.add(ice.sprite_key())
        ice.update(dt=0.05)
    seen_keys.add(ice.sprite_key())

    assert seen_keys.issubset(game.sprites.keys())
    assert "platform_ice_broken" in seen_keys  # confirms it actually melted


def test_sprites_survive_continue_and_new_game(game):
    """Continue/New Game rebuild platforms/collectibles (Phase 10) - make
    sure the fresh objects still resolve to loaded sprites afterward."""
    game._new_run(regenerate_world=False)
    for platform in game.platforms:
        assert platform.sprite_key() in game.sprites

    game._new_run(regenerate_world=True)
    for platform in game.platforms:
        assert platform.sprite_key() in game.sprites
    for collectible in game.collectibles:
        assert collectible.sprite_key() in game.sprites
