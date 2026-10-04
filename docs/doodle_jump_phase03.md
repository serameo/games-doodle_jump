# Doodle Jump - Phase 03: Platform Base Class + Static Brick Platform

**Version:** v0.3.0
**Status:** Done - confirmed working on your machine
**Currently doing:** Complete - ready to start Phase 04

---

## Goal

A `Platform` base class implementing the static "brick" behavior, plus
real collision detection between the player and platforms - replacing
the Phase 02 temporary demo floor. `main.py` now uses a small fixed set
of demo platforms so you can see falling/landing/auto-jump working
across multiple real platforms by eye.

---

## Tasks

- [x] `game/platform.py` - `Platform` base class:
  - `rect` property (pygame.Rect)
  - `update(dt)` - no-op for now (static); written so moving-platform
    subclasses in Phase 05 can override it
  - `is_solid()` - always True for brick; written so ice platforms
    (Phase 05) can return False once melted
- [x] `game/collision.py` - `find_landing_platform(player, platforms)`:
  - only considers landing while the player is falling (per rules 2.1 -
    the player passes through platforms on the way up)
  - skips platforms where `is_solid()` is False
  - uses lenient overlap: any rectangle intersection counts (Confirmed
    Decision #7), no minimum overlap percentage
- [x] `main.py` updated:
  - removed the Phase 02 temporary floor
  - added 4 fixed demo `Platform` objects, spaced within jump range, so
    you can see the player land on and bounce between real platforms
  - draws each platform as a brown rectangle
- [x] `tests/test_platform.py` - 3 unit tests: rect sync, `is_solid()`
      always True, `update()` doesn't move a static platform
- [x] `tests/test_collision.py` - 6 unit tests: lands when falling +
      overlapping, no landing with no overlap, no landing while rising
      (passes through), no landing on a non-solid platform, empty
      platform list, and a test specifically for the lenient
      "slight overlap still counts" rule (Decision #7)

## Files changed this phase

```
doodle_jump/
|-- main.py                    (updated: real Platform objects + collision, temp floor removed)
`-- game/
    |-- platform.py             (new)
    `-- collision.py            (new)
`-- tests/
    |-- test_platform.py        (new)
    `-- test_collision.py       (new)
```

---

## How to run

```
python main.py     # window opens; the orange player should fall onto the
                    # brown demo platforms and auto-jump between them -
                    # close via the X button
pytest              # runs all unit tests, headless, no window needed
```

## Test status

Same sandbox limitation as previous phases: no network access and
`pygame`/`pytest` are not pre-installed here, so I could not run these
myself. Code and tests were written and reviewed carefully, following the
pattern that has worked for Phase 01 and Phase 02. **Please run both
commands above and paste the result here** - especially check that the
player visibly lands on and bounces between the brown platforms (not just
falls straight through them).

---

## Decisions carried into this phase

From `doodle_jump_plans.md` (Confirmed Decision #7):
- Platform collision is lenient: any rectangle overlap while falling
  counts as landing, no minimum overlap percentage required.

---

## Open Questions

None currently.

---

## Next Phase

Phase 04: Platform spawner - random platform generation that guarantees
every new platform is reachable by a jump from the one before it (per
rules 2.2). This replaces the fixed demo platform list in `main.py` with
real procedural generation. Will not start until you confirm Phase 03
runs correctly on your machine.

---

## Addendum (post-Phase-05): collision-tunneling bug fixed

**Reported by you:** after Phase 05, the player would sometimes jump up
and never come back down.

**Root cause (part 2 of 2 - the other is in the Phase 02 addendum):**
`find_landing_platform()` only checked whether the player's rect
overlapped a platform's rect *at the end of the current frame*. As the
player fell faster and faster under gravity, its per-frame movement
could exceed a platform's 20px thickness, so it would skip clean over a
platform without any single frame where the rects actually overlapped -
"tunneling" straight through and free-falling from then on.

**Fix:** collision detection is now a swept check. `Player` remembers
`previous_y` from before each physics update; `find_landing_platform()`
checks whether the platform's top edge falls between the player's
previous and current bottom edge (in addition to the original
"overlapping right now" check), catching landings that would otherwise
be skipped between frames. This does not change Confirmed Decision #7
(lenient overlap) - it only fixes frames being skipped entirely.

**Changes:**
- `game/player.py` - added `previous_y`, set at the start of `update()`
- `game/collision.py` - `find_landing_platform()` now checks
  `overlapping_now OR crossed_top_this_frame`
- `tests/test_collision.py` - 2 new regression tests: a large single-step
  fall that would have tunneled is still caught; a large step that
  genuinely misses the platform's band still correctly reports no landing
- `tests/test_integration.py` (new) - end-to-end tests via the real
  `Game` object, including a scripted playthrough that lands on every
  platform (brick, ice, spring, both moving types) in the Phase 05 demo
  layout in sequence without diverging
