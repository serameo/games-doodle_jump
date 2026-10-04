# Doodle Jump - Phase 02: Player Entity

**Version:** v0.2.0
**Status:** Done - confirmed working on your machine
**Currently doing:** Complete - ready to start Phase 03

---

## Goal

A `Player` with position, gravity-driven falling, and an auto-jump that
triggers on "landing." Real platform collision does not exist yet (that's
Phase 03), so `main.py` uses a temporary floor at the bottom of the
screen purely to demonstrate the physics end to end - you should see the
player fall, hit the temporary floor, and auto-jump repeatedly.

---

## Tasks

- [x] `game/player.py` - `Player` class:
  - `update(dt)` - applies gravity, advances position (delta-time based)
  - `jump(boosted=False)` - sets upward velocity; `boosted` applies the
    spring multiplier (x1.5, per Confirmed Decision #6)
  - `land(platform_top_y, boosted=False)` - snaps feet to a platform top
    and immediately auto-jumps (this is the hook Phase 03 will call from
    real platform collision detection)
  - `is_falling()` / `is_rising()` helpers
  - `rect` property (pygame.Rect) for future collision/drawing use
- [x] `config/settings.json` - added `gravity`, `jump_velocity`,
      `spring_multiplier` (Confirmed Decision #6: 2000 px/s^2, -900 px/s,
      x1.5)
- [x] `main.py` updated:
  - creates a `Player` at the top-center of the screen
  - `update()` now takes `dt` (real elapsed seconds since last frame,
    computed from `clock.tick()`), so physics is frame-rate independent
  - temporary demo floor: when the player's feet reach the bottom of the
    screen while falling, `land()` is called - proves gravity + jump work
  - draws the player as a placeholder orange rectangle
- [x] `tests/test_player.py` - 11 unit tests: initial state, free fall
      (velocity and position over time), normal jump, spring-boosted jump,
      landing (position snap + auto-jump), boosted landing, falling/rising
      state checks, rect sync
- [x] `tests/test_main.py` - updated `test_update_does_not_raise` to pass
      `dt` now that `Game.update()` requires it

## Files changed this phase

```
doodle_jump/
|-- main.py                 (updated: Player wired into the loop, dt-based update)
|-- config/settings.json    (updated: + gravity, jump_velocity, spring_multiplier)
|-- game/
|   |-- settings.py         (updated: new defaults for the above)
|   `-- player.py           (new)
`-- tests/
    |-- test_main.py        (updated: update(dt=...))
    `-- test_player.py      (new)
```

---

## How to run

```
python main.py     # window opens; the orange square should fall, hit the
                    # bottom, and auto-jump repeatedly - close via the X button
pytest              # runs all unit tests, headless, no window needed
```

## Test status

I could not execute `pytest` or run the window myself in this sandbox
(same limitation as Phase 01: no network access, `pygame`/`pytest` not
pre-installed here, so I could not verify by running them). The code and
tests have been written and reviewed carefully, following the same
pattern that worked for Phase 01. **Please run both commands above and
paste the result here** - especially watch that the square visibly falls
and bounces (auto-jumps) rather than just sitting still or falling
through the bottom.

---

## Decisions carried into this phase

From `doodle_jump_plans.md` (Confirmed Decision #6):
- Gravity: 2000 px/s^2
- Jump velocity: -900 px/s (upward)
- Spring multiplier: x1.5

These are stored in `config/settings.json`, so they can be re-tuned by
feel later without touching `player.py`.

---

## Open Questions

None currently.

---

## Next Phase

Phase 03: Platform base class + static brick platform. This will replace
the temporary demo floor in `main.py` with real platform objects and
proper collision detection. Will not start until you confirm Phase 02
runs correctly on your machine.

---

## Addendum (post-Phase-05): horizontal movement added

**Reported by you:** after Phase 05, the player would sometimes jump up
and never come back down.

**Root cause (part 1 of 2 - the other is in the Phase 03 addendum):**
the original spec never described how the player moves left/right, so
`Player.x` never changed. Combined with platforms spawning at random x
positions (Phase 04), the player would eventually miss every platform
above it and fall forever with no way back.

**Decision (Confirmed Decision #10):** keyboard left/right arrow keys,
300 px/s, with classic screen-wrap (exiting one side reappears on the
other).

**Changes:**
- `config/settings.json` / `game/settings.py` - added
  `player_horizontal_speed: 300.0`
- `game/player.py` - added `move(direction, dt)` and
  `wrap_around(screen_width)`
- `main.py` - `Game.read_horizontal_input()` reads `K_LEFT`/`K_RIGHT`
  each frame and calls `player.move()` + `player.wrap_around()` before
  the vertical physics update
- `tests/test_player.py` - 6 new tests for `move()` and `wrap_around()`
