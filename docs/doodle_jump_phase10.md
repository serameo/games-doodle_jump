# Doodle Jump - Phase 10: Game Over Flow

**Version:** v0.10.0
**Status:** Implementation complete - awaiting your test run and review
**Currently doing:** Waiting for your confirmation before starting Phase 11

---

## Goal

Detect the player falling below the screen with no platform underneath
them (rules 2.1) and present a menu: Continue (retry same run), Start a
new game, or Quit.

This phase only becomes meaningful because of Phase 09's camera change:
with the old always-centered camera the player could never actually
fall below the visible screen, since the camera would just recenter on
them. The ratchet camera (never follows a fall back down) is what makes
"falling below the screen" a real, detectable event.

---

## How it works

`game/game_state.py` (new) holds:
- `GameState` / `GameStatus` - a two-state machine, `PLAYING` and
  `GAME_OVER`.
- `has_fallen_off_screen(player, camera, screen_height)` - true once the
  player's feet have dropped below the bottom edge of the *currently
  visible* screen (using `camera.to_screen_y()`), independent of the
  player's own coordinates in world space.

In `main.py`'s `Game.update()`, this check runs only in the branch where
`find_landing_platform()` found nothing this frame - i.e. exactly the
rules 2.1 condition "with no platform underneath them." When it fires,
`game_state.trigger_game_over()` is called and the frame returns early,
skipping collectibles/camera updates. Every subsequent call to
`update()` becomes a no-op while `game_state.is_game_over()`, freezing
gameplay behind the menu; `draw()` still renders the last frame, with a
translucent overlay and the three options on top.

`handle_events()` now also reads keyboard input while the menu is
showing: **C** (Continue), **N** (New Game), **Q** (Quit).

### Refactor: `_build_world()` / `_new_run()`

The world-building code that used to live directly in `Game.__init__()`
was pulled out into two reusable methods, since both the initial run and
the menu's Continue/New Game options need it:

- `_build_world()` - builds `(platforms, collectibles)` from scratch:
  the starting platform, every map file in order (Phase 06), then the
  Phase 04/08 random fallback column. Identical to what `__init__` did
  before, just extracted into its own method.
- `_new_run(regenerate_world)` - resets the player, score, and camera.
  - `regenerate_world=True` calls `_build_world()` for an entirely fresh
    layout (used at startup, and for "Start a new game"). A pristine
    deep-copy snapshot of the freshly built platforms/collectibles is
    also stored.
  - `regenerate_world=False` instead restores that pristine snapshot
    (deep-copied again, so mutating it during play never touches the
    stored original) - used for "Continue," so ice that melted and
    coins/diamonds that were picked up are all back exactly as they
    were at the start of the run.

`__init__` now just sets up the pygame window/fonts/`GameState`, then
calls `_new_run(regenerate_world=True)` once.

---

## Interpreting "Continue" / "Start a new game" / "Quit" (rules 2.1)

Rules 2.1 names these three options but doesn't spell out exactly what
each one resets, and there's no main-menu screen anywhere in this
project yet. Interpreted as follows - flag if you'd like something
different, each is a small change:

- **Continue = retry the exact same run.** Since map files always
  produce the same fixed layout and the random fallback column is only
  generated once per run, "the same run" is well-defined: restore that
  original layout (undoing melted ice, picked-up items, and any moved
  platforms' progress) and reset the player/score. This seemed like the
  most natural reading of "retry" for a game with mostly-static levels.
- **Start a new game = rebuild everything from scratch.** Map files
  still produce the same fixed content, but the random fallback column
  is regenerated with a fresh, unseeded RNG draw, so it won't match the
  previous run's random platforms.
- **Quit = close the application.** Rules 2.1 says "quit to the main
  menu," but no main menu exists in this project (not in the Phase
  Breakdown in `doodle_jump_plans.md`). Treated as exiting the window
  for now; if a main menu gets added in a later phase, this is a
  one-line change in `handle_events()`.

---

## Tasks

- [x] `game/game_state.py` - new module: `GameState`/`GameStatus`
      (two-state machine) and `has_fallen_off_screen()`
- [x] `main.py` restructured:
  - world-building extracted from `__init__` into `_build_world()`
  - `_new_run(regenerate_world)` added for (re)starting a run, shared by
    startup and the menu
  - `Game.update()` checks `has_fallen_off_screen()` when nothing caught
    the player this frame, and freezes (returns early) once
    `game_state.is_game_over()`
  - `Game.handle_events()` reads C/N/Q while the menu is showing
  - `Game.draw()` renders a translucent game-over overlay
    (`_draw_game_over_menu()`) with the final score and the three
    options, on top of the frozen gameplay frame
- [x] `tests/test_game_state.py` - 7 unit tests: `GameState` starts in
      `PLAYING`, `trigger_game_over()`/`resume_playing()` switch state
      correctly, and `has_fallen_off_screen()` for: comfortably on
      screen, far below screen, exactly on the bottom edge (not fallen),
      one pixel past it (fallen)
- [x] `tests/test_integration.py` - 6 new end-to-end tests: falling far
      below the screen triggers game over, gameplay freezes once game
      over (position/score don't change on further updates), Continue
      resets player/score but restores the exact same layout (picked-up
      coin reappears), New Game resets and produces a different random
      fallback layout, Q quits (`handle_events()` returns `False`), and
      menu keys are ignored during normal gameplay

## Files changed this phase

```
doodle_jump/
|-- main.py                        (restructured: _build_world()/_new_run(),
|                                    game-over check, menu input/drawing)
`-- game/
    `-- game_state.py                (new)
`-- tests/
    |-- test_game_state.py           (new)
    `-- test_integration.py          (updated: + 6 game-over end-to-end tests)
```

---

## How to run

```
python main.py     # you should now land on a title screen first -
                    # "DOODLE JUMP" with Enter to start and Q to quit;
                    # press Enter to begin playing, then let the player
                    # fall off a platform and keep falling past the
                    # bottom of the screen - a translucent "GAME OVER"
                    # menu should appear over the frozen scene, showing
                    # your final score and three options:
                    #   C - Continue (same layout, fresh player/score)
                    #   N - New Game (fresh random layout too)
                    #   Q - Back to Title (the title screen, not exit)
                    # try all of these and confirm each behaves as
                    # described - only Q from the title screen itself
                    # should actually close the window
                    #
                    # also find a wall ('!' on the map, dim gray) and
                    # jump onto the top of it - it should catch you like
                    # a normal platform (auto-jump as usual), then start
                    # sliding straight down and keep accelerating
pytest              # runs all unit tests, headless, no window needed
```

## Test status

Same sandbox limitation as previous phases - no network access, so
`pygame`/`pytest` could not be installed here and I could not run these
myself. I did verify the pure state-machine and boundary-check logic in
`game/game_state.py` directly with plain Python (using a minimal stub
standing in for the two pygame calls `Player` needs), confirming every
number in `tests/test_game_state.py` is correct. What I have *not* been
able to exercise is the full `pytest` run through the real
`Game`/pygame integration tests, or a real play session. **Please run
both commands above and paste the result here** - especially check that
falling off the bottom reliably shows the menu (not immediately, or
never), that Continue puts everything back the way it started
(including a coin you picked up), and that New Game actually looks
different from your last run.

---

## Decisions carried into this phase

No new Confirmed Decisions from `doodle_jump_plans.md` were needed. The
"Continue/New Game/Quit" interpretation above is an implementation
choice made to fill in what rules 2.1 left unspecified - flagged there
rather than as a formal Confirmed Decision, since it's easy to adjust
later if you'd prefer different semantics.

---

## Open Questions

- Is the "Continue = restore this run's original layout" interpretation
  what you had in mind, or did you want it to instead resume from
  wherever the player was standing right before the fall (i.e. much
  closer to a true "retry from checkpoint")? Easy to change if not.

---

## Addendum: title-screen main menu + falling walls

Added after your review of the original Phase 10 delivery, per your
request.

### Title-screen main menu

Answers the first Open Question above (yes to a real main menu):

- `GameState` gained a third status, `MAIN_MENU`, and now starts there
  instead of `PLAYING` - a title screen ("DOODLE JUMP" / "Enter - Start
  Game" / "Q - Quit") is shown before any gameplay begins.
- The game-over menu's "Quit" option now calls
  `game_state.show_main_menu()` instead of exiting the app - it returns
  to the title screen. Quitting from the title screen itself is what
  now closes the application.
- `Game.update()`'s freeze condition changed from `is_game_over()` to
  `not is_playing()`, so gameplay is frozen behind *either* menu.
- `Game._new_run()` no longer calls `game_state.resume_playing()`
  itself - that's now the caller's job in `handle_events()`, since
  different transitions need different follow-up (Start Game and New
  Game go straight to `PLAYING`; Quit-from-game-over goes to
  `MAIN_MENU` instead).
- New tests in `tests/test_game_state.py` (starts on the title screen,
  each transition) and `tests/test_integration.py` (title screen freezes
  gameplay, Enter starts the game, Quit from the title screen stops the
  game, Quit from game-over returns to the title screen instead of
  quitting).

### Falling walls

Revises rules 2.2's original Wall behavior ("does not act as a landing
platform") per your request:

- `Wall` is now solid (landable) like any other platform. The first
  time the player lands on one, `on_landed()` sets `falling = True`;
  from then on, `update()` accelerates it downward every frame
  (`fall_velocity += fall_acceleration * dt`, `y += fall_velocity *
  dt`) and it never stops.
- You chose to reuse the existing `gravity` setting
  (`config/settings.json`, 2000 px/s^2) for `fall_acceleration` rather
  than converting the "10 m/s^2" from real-world units - so a fallen
  wall now drops at the same rate the player themselves would fall.
- `game/map_loader.py` threads a new `wall_fall_acceleration` parameter
  through `MapLoader`/`load_map_file()` down to each `Wall` it places;
  `main.py`'s `_build_world()` passes `self.settings["gravity"]` for it.
- The known limitation noted in the original Wall docstring (walls still
  don't block horizontal movement - the player has no horizontal
  obstacle collision at all yet) still applies and is unrelated to this
  change.
- New tests in `tests/test_special_platforms.py` (solid now instead of
  non-solid, doesn't fall until landed on, accelerates correctly,
  landing again mid-fall doesn't reset velocity, configurable
  acceleration) and `tests/test_map_loader.py` (the configured
  acceleration reaches the placed `Wall`).

**Not addressed, flagging in case it matters:** once a wall starts
falling, nothing ever removes it from `self.platforms` - it just keeps
existing (and moving downward) for the rest of the run. For a short
play session this is harmless, but if you generate many maps with many
walls over a long session, the list could grow storage-wise from
`copy.deepcopy` calls on "Continue" needing to carry all of them
forward (not performance-relevant yet, just worth knowing about).

---

## Next Phase

Phase 11: polish & tuning - parameter tuning, integration tests, edge
cases, and replacing the placeholder rectangle/circle shapes with real
sprite art (Confirmed Decision #5). Will not start until you confirm
Phase 10 (including this addendum) runs correctly on your machine.
