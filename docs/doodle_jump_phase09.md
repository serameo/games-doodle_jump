# Doodle Jump - Phase 09: Difficulty Scaling

**Version:** v0.9.0
**Status:** Done - confirmed working on your machine (tests passed)
**Currently doing:** Complete - starting Phase 10

---

## Goal

Scroll speed increases as the player scores more (Confirmed Decision
#2): +2% per 30 points, capped at a maximum multiplier, then holding
steady.

---

## Design decision made this phase (see conversation, not previously in
## the docs)

Before writing any code, one thing needed resolving: Phase 07's camera
always keeps the player exactly centered, in both directions (climbing
*and* falling). With that behavior, a "scroll speed" number has nothing
to act on - the player is always exactly centered no matter how fast
the scroll is set, so increasing it would change a number with zero
gameplay effect.

**You confirmed:** switch to a "ratchet" camera now - it only ever
scrolls upward, never re-follows the player down - so scroll speed
creates real pressure, matching the original Doodle Jump and rules
2.1's Overview ("the screen scrolls downward slowly and
continuously... If the player's feet fall below the game-over boundary
while not supported by any platform, the game ends"). This directly
supersedes the always-centered choice from Phase 07; see the addendum
added to `docs/doodle_jump_phase07.md`.

---

## How it works now

Each frame, the camera:
1. Advances upward on its own by `scroll_speed * dt` (the continuous
   auto-scroll - happens regardless of what the player does).
2. Also snaps further up if the player has climbed above where that
   auto-scroll has reached (so a fast climber is never scrolled off the
   top of the screen).
3. Never moves back down - if the player falls, the camera holds its
   position. Falling far enough below wherever the camera has already
   advanced to will eventually put the player below the bottom edge of
   the visible screen. Detecting that and ending the game is Phase 10's
   job, not this phase's - this phase only makes the pressure real.

`scroll_speed` itself comes from the new `game/difficulty.py`:
`scroll_speed = base_scroll_speed * multiplier`, where `multiplier`
starts at 1.0 and gets +2% for every full 30 points scored, capped at
2.0x (all four numbers - `base_scroll_speed`, `score_interval`,
`speed_increase_per_interval`, `max_speed_multiplier` - are read from
`config/settings.json`, same convention as every other tunable value in
this project).

---

## Tasks

- [x] `game/difficulty.py` - new module:
  - `scroll_speed_multiplier(score_value, score_interval,
    speed_increase_per_interval, max_speed_multiplier)` - the capped
    multiplier for a given score
  - `current_scroll_speed(score_value, settings)` - applies that
    multiplier to `settings["base_scroll_speed"]`
- [x] `game/camera.py` - reworked per the design decision above:
  - `Camera.update(dt, player_y, scroll_speed)` (signature changed from
    Phase 07's `update(player_y)`) - continuous auto-scroll + ratchet
    follow-up, never reverses
  - the very first call still snaps exactly to center the player (same
    as Phase 07), so starting behavior is unchanged; the ratchet only
    applies from the second call onward
- [x] `config/settings.json` / `game/settings.py` - added
      `base_scroll_speed` (default 30.0 px/s - "slowly" per rules 2.1,
      relative to the ~900 px/s jump velocity and 300 px/s horizontal
      speed already in use)
- [x] `main.py` updated:
  - computes `current_scroll_speed(self.score.value, self.settings)`
    each frame and passes it into `camera.update(dt, player.y,
    scroll_speed)`
  - same at startup, for the initial camera snap
- [x] `tests/test_camera.py` - rewritten for the new signature and
      ratchet behavior: initial snap-to-center, ratchet-up while
      climbing, no-reverse while falling, continuous scroll advances
      the offset on its own, continuous scroll never reverses across
      frames, a fast climb still wins over a slow auto-scroll
- [x] `tests/test_difficulty.py` - 7 unit tests: multiplier is 1.0 below
      the first interval, +2% exactly at 30 points, stacks correctly
      across multiple intervals, caps at the configured maximum, holds
      steady well past the cap, `current_scroll_speed` applies the
      multiplier to the base speed correctly, and stays capped at
      max-multiplier-times-base for very high scores
- [x] `tests/test_integration.py`:
  - updated `test_camera_keeps_player_on_screen_while_climbing` to pass
    `scroll_speed=0`, isolating the ratchet-follow behavior it already
    tested from the new auto-scroll
  - 3 new end-to-end tests: the camera keeps auto-scrolling over real
    frames even when the player holds still, scroll speed measurably
    increases after crossing a 30-point interval, and falling after a
    climb does not pull the camera back down (only the expected
    auto-scroll amount changes the offset)

## Files changed this phase

```
doodle_jump/
|-- main.py                        (updated: scroll speed wired into camera.update())
|-- config/
|   `-- settings.json                (updated: + base_scroll_speed)
`-- game/
    |-- difficulty.py                (new)
    |-- camera.py                    (reworked: ratchet + auto-scroll, see above)
    `-- settings.py                  (updated: + base_scroll_speed default)
`-- docs/
    `-- doodle_jump_phase07.md       (updated: addendum documenting the camera change)
`-- tests/
    |-- test_camera.py               (rewritten for new Camera API/behavior)
    |-- test_difficulty.py           (new)
    `-- test_integration.py          (updated: 1 test adjusted, 3 new end-to-end tests)
```

---

## How to run

```
python main.py     # climb for a while and then stand still on a
                    # platform without climbing further - you should see
                    # the platforms and background slowly drift downward
                    # on their own even while you're not moving; collect
                    # coins/diamonds to push your score past 30, 60, 90...
                    # and the drift should get slightly faster each time
                    # - close via the X button
pytest              # runs all unit tests, headless, no window needed
```

## Test status

Confirmed by you: both `python main.py` and `pytest` run correctly on
your machine.

---

## Decisions carried into this phase

1. **Camera: ratchet instead of always-centered** (see "Design decision
   made this phase" above) - supersedes the Phase 07 choice; recorded
   as an addendum in `docs/doodle_jump_phase07.md`.
2. **`base_scroll_speed` = 30.0 px/s** - not previously in
   `config/settings.json`; the rules only specified the *scaling*
   (+2%/30 points, capped at 2.0x), not a starting speed. Chosen to be
   slow relative to the existing jump/horizontal speeds, matching rules
   2.1's "slowly." Flag it if you'd like a different starting value -
   it's a one-line change in `config/settings.json`, no code changes
   needed.

No other new Confirmed Decisions were needed - the interval (30 points),
step size (2%), and cap (2.0x) were already specified in Confirmed
Decision #2 and already present in `config/settings.json` from earlier
phases.

---

## Open Questions

None currently, beyond the `base_scroll_speed` value flagged above if
you'd like it tuned.

---

## Next Phase

Phase 10: game over flow - detect the player's feet falling below the
screen's bottom edge (now meaningful, since the camera no longer
follows a falling player down) while unsupported by any platform, then
present a menu: retry / new game / quit. Starting now, per your
confirmation above.
