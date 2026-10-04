# Doodle Jump - Phase 05: Special Platform Types

**Version:** v0.5.0
**Status:** Implementation complete - awaiting your test run and review
**Currently doing:** Waiting for your confirmation before starting Phase 06

---

## Goal

Add the remaining platform types from rules 2.2: ice (breakable), spring
(jump boost), and the two moving platforms (up/down, left/right).

---

## Tasks

- [x] `game/platform.py` - added two hooks to the `Platform` base class
      so subclasses can plug in without changing shared code:
  - `on_landed()` - called once when the player lands here (brick: no-op)
  - `boosts_jump()` - whether landing here should apply the spring
    multiplier (brick: `False`)
- [x] `game/special_platforms.py` - new module:
  - `IcePlatform` - solid until landed on, then melts after
    `melt_seconds` (configurable, default from
    `settings["ice_melt_seconds"]` per Confirmed Decision #3);
    `is_solid()` becomes `False` once melted
  - `SpringPlatform` - `boosts_jump()` returns `True`, so `main.py`'s
    landing code applies the x1.5 multiplier from Phase 02
  - `MovingPlatform` - shared oscillation logic (medium speed/range per
    Confirmed Decision #9: 60 px/s, 80px range), reverses direction at
    each bound
  - `MovingVerticalPlatform` / `MovingHorizontalPlatform` - move along y
    or x respectively
- [x] `main.py` updated:
  - landing code now calls `landing_platform.on_landed()` and passes
    `boosted=landing_platform.boosts_jump()` into `player.land()`
  - `draw()` now skips platforms where `is_solid()` is `False`, so melted
    ice correctly disappears
  - **bug fix:** `draw()` was using `Platform.COLOR` (the base class
    color) for every platform regardless of type; changed to
    `platform.COLOR` so each subclass's own color is used
  - appended one hand-placed demo instance of each new type above the
    random column (same 160px reachable spacing) purely so you can see
    and test each behavior by eye - mixing special types into the random
    spawner itself comes later, alongside map loading in Phase 06
- [x] `tests/test_special_platforms.py` - 15 unit tests: base-class
      defaults, ice (starts solid, doesn't melt until landed on, stays
      solid before the timer elapses, melts once it elapses, configurable
      timer, doesn't un-melt on a second landing), spring (`boosts_jump`),
      moving vertical/horizontal (moves on the correct axis only, stays
      within range, reverses direction at the bound)

## Files changed this phase

```
doodle_jump/
|-- main.py                          (updated: on_landed/boosts_jump wiring, color bug fix, demo instances)
`-- game/
    |-- platform.py                   (updated: + on_landed(), boosts_jump())
    `-- special_platforms.py          (new)
`-- tests/
    `-- test_special_platforms.py     (new)
```

---

## How to run

```
python main.py     # keep climbing past the random brick column - you
                    # should reach a light-blue ice platform (melts a few
                    # seconds after you land, then disappears), a gold
                    # spring platform (noticeably higher/faster bounce),
                    # a platform sliding up/down, then one sliding
                    # left/right - close via the X button
pytest              # runs all unit tests, headless, no window needed
```

## Test status

Same sandbox limitation as previous phases - no network access, and
`pygame`/`pytest` are not pre-installed here, so I could not run these
myself. Code and tests were written and reviewed carefully. **Please run
both commands above and paste the result here** - especially check that:
- the ice platform visibly disappears a few seconds after landing on it
- the spring bounce is noticeably higher than a normal jump
- the two moving platforms are visibly sliding back and forth

---

## Decisions carried into this phase

From `doodle_jump_plans.md`:
- Confirmed Decision #3: ice melt timer configurable, default 3s
- Confirmed Decision #9: moving platforms at 60 px/s across an 80px range

---

## Open Questions

None currently.

---

## Addendum: bugs found during your manual testing, now fixed

You reported that after climbing for a while, the player would sometimes
jump up and never come back down. Root cause was two combined issues:

1. **No horizontal movement** (the original spec never covered player
   left/right control) - fixed by adding keyboard arrow-key movement
   with screen-wrap. Confirmed Decision #10. Full detail in the
   addendum to `docs/doodle_jump_phase02.md`.
2. **Collision tunneling** - a fast-falling player could skip clean
   through a thin platform within a single frame. Fixed with swept
   collision detection. Full detail in the addendum to
   `docs/doodle_jump_phase03.md`.

Also added, per your request: `tests/test_integration.py` - end-to-end
tests that exercise each special platform type (ice, spring, moving
up/down, moving left/right) through the real `Game` object rather than
isolated unit calls, plus a scripted playthrough that walks the player
up through every platform in the Phase 05 demo layout in sequence and
confirms it lands correctly on all of them without diverging.

**Please re-download, re-test, and specifically try holding the left/right
arrow keys this time** - that's the main thing that changed. Let me know
if the player still ever gets stuck.

---

## Next Phase

Phase 06: map file loading - parse `map01.txt` (and successors) bottom
to top per rules 2.4, using the symbol legend to place all platform
types (including these new special ones) and collectibles; falls back to
the Phase 04 random spawner once map files are exhausted. Will not start
until you confirm Phase 05 runs correctly on your machine.
