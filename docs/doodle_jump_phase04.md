# Doodle Jump - Phase 04: Platform Spawner

**Version:** v0.4.0
**Status:** Done - confirmed working on your machine
**Currently doing:** Complete - ready to start Phase 05

---

## Goal

Replace the Phase 03 fixed demo platform list with real random
generation, guaranteeing every platform is reachable from the one before
it (rules 2.2 + Confirmed Decision #8).

---

## Tasks

- [x] `game/platform_spawner.py` - `PlatformSpawner` class:
  - `next_platform(previous_y)` - generates one platform above
    `previous_y`, with a vertical gap randomly chosen from
    `[MIN_GAP, MAX_GAP] = [140, 190]` px (Confirmed Decision #8), and a
    random x position within the screen width
  - `generate_column(start_y, top_y)` - repeatedly calls
    `next_platform()` to build a column of platforms upward until
    reaching `top_y`; since each platform is placed relative to the one
    before it, the whole column is guaranteed reachable end to end
  - accepts an optional seeded `random.Random` so tests are deterministic
- [x] `main.py` updated:
  - one starting platform placed directly under the player
  - a full column generated upward from it via
    `spawner.generate_column(...)`, extending well above the visible
    screen so there's plenty to climb through during manual testing
  - (endless generation as the player keeps climbing, and recycling
    platforms that scroll off screen, is deferred to Phase 07 together
    with the camera - noted in the code comments)
- [x] `tests/test_platform_spawner.py` - 7 unit tests: gap always within
      the reachable range, each platform is above the previous one, x
      stays within screen bounds, `generate_column` stops at/above
      `top_y`, every gap in a generated column is reachable, generation
      is deterministic with a fixed seed, and an empty-result edge case

## Files changed this phase

```
doodle_jump/
|-- main.py                        (updated: random column replaces fixed demo platforms)
`-- game/
    `-- platform_spawner.py         (new)
`-- tests/
    `-- test_platform_spawner.py    (new)
```

---

## How to run

```
python main.py     # window opens; player should fall onto a starting
                    # platform, then keep auto-jumping through several
                    # randomly placed platforms going upward - close via
                    # the X button
pytest              # runs all unit tests, headless, no window needed
```

## Test status

Same sandbox limitation as previous phases - no network access, and
`pygame`/`pytest` are not pre-installed here, so I could not run these
myself. Code and tests were written and reviewed carefully. **Please run
both commands above and paste the result here** - especially check that
the player keeps landing on differently-positioned platforms as it climbs
(not always the same handful of spots), and that it never has to make an
impossible jump.

---

## Decisions carried into this phase

From `doodle_jump_plans.md` (Confirmed Decision #8):
- Vertical gap between generated platforms: 140-190px (medium margin,
  comfortably under the ~202px max jump height).

---

## Open Questions

None currently.

---

## Next Phase

Phase 05: special platform types - ice (breakable, melts after the
configured timer), moving up/down, moving left/right, and spring
(+50% jump boost). Will not start until you confirm Phase 04 runs
correctly on your machine.
