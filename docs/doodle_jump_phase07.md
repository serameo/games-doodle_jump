# Doodle Jump - Phase 07: Camera

**Version:** v0.7.0
**Status:** Done - confirmed working on your machine (camera follows both up and down correctly)
**Currently doing:** Complete - resuming Phase 06 next

---

## Note on phase order

This phase was moved ahead of Phase 06 (map file loading) at your
request, after you correctly noticed that only 2 platforms were visible
on screen even though `main.py` creates several more. That wasn't a bug
- without a camera, the game only ever showed the fixed 800px-tall band
of world coordinates from y=0 to y=800, so most platforms (and
eventually the player itself, once it climbs high enough) were drawn
off-screen even though they existed and worked correctly. See the
"Actual execution order note" in `doodle_jump_plans.md`. Phase 06 resumes
right after this phase is confirmed.

---

## Goal

Keep the player vertically centered on screen at all times (rules 2.5),
so the visible window scrolls with the player instead of showing a fixed
slice of world coordinates.

---

## Tasks

- [x] `game/camera.py` - `Camera` class:
  - `update(player_y)` - recomputes a vertical offset so the player ends
    up centered on screen
  - `to_screen_y(world_y)` - converts any world y-coordinate into a
    screen y-coordinate using that offset
  - physics and collision are untouched - they keep working entirely in
    world coordinates; only rendering goes through the camera
- [x] `main.py` updated:
  - creates a `Camera` sized to the screen and player height
  - `update()` now calls `camera.update(player.y)` every frame, after
    physics/collision are resolved
  - `draw()` now converts every platform's and the player's world y into
    a screen y via `camera.to_screen_y(...)` before building the rect to
    draw - x is unaffected (horizontal wrap already keeps it on screen)
- [x] `tests/test_camera.py` - 6 unit tests: offset calculation, player
      correctly centered, relative distances between world objects are
      preserved after conversion, camera follows both climbing and
      falling, default offset before any update
- [x] `tests/test_integration.py` - 1 new end-to-end test: runs the
      scripted playthrough from the Phase 05 patch again, this time also
      checking that the player's on-screen (camera-converted) position
      stays within the visible window at every platform, not just that
      its world position is correct

## Files changed this phase

```
doodle_jump/
|-- main.py                    (updated: Camera created and applied in update()/draw())
`-- game/
    `-- camera.py                (new)
`-- tests/
    |-- test_camera.py           (new)
    `-- test_integration.py      (updated: + camera-aware scripted playthrough check)
```

---

## How to run

```
python main.py     # the player should now stay roughly centered on
                    # screen; as it climbs, platforms below scroll off
                    # the bottom and new ones scroll into view from the
                    # top - close via the X button
pytest              # runs all unit tests, headless, no window needed
```

## Test status

Same sandbox limitation as previous phases - no network access, and
`pygame`/`pytest` are not pre-installed here, so I could not run these
myself. Code and tests were written and reviewed carefully. **Please run
both commands above and paste the result here** - especially check that
you can now see the ice/spring/moving platforms from Phase 05 as you
climb, and that the player never visually leaves the screen.

---

## Decisions carried into this phase

- Camera always keeps the player centered (both scrolling up while
  climbing and down while falling), per a literal reading of rules 2.5
  ("stay centered on screen always"). This differs from some Doodle Jump
  clones that only scroll upward (ratchet); flag it if you'd prefer that
  one-directional behavior instead and I'll switch it.

---

## Open Questions

None currently, aside from the always-vs-ratchet camera note above if
you want to revisit it.

---

## Next Phase

Resume Phase 06: map file loading - parse `map01.txt` (and successors)
bottom to top per rules 2.4, using the symbol legend to place all
platform types (including the Phase 05 special ones) and collectibles;
falls back to the Phase 04 random spawner once map files are exhausted.
Will not start until you confirm Phase 07 runs correctly on your
machine.

---

## Addendum (Phase 09): camera changed from always-centered to "ratchet"

**Why:** implementing Phase 09's scroll-speed difficulty scaling exposed
a problem with the "always centered, both directions" behavior chosen
above: if the camera always recenters on the player regardless of
score, then an increasing scroll speed has nothing to act on - the
player can never fall behind or get closer to the bottom edge no matter
how fast the scroll is set. This directly revisits the open note left
in this document.

**Change:** the camera now only ever scrolls upward. Each frame it
advances on its own at the current scroll speed (px/sec, scaling with
score per Confirmed Decision #2), and separately snaps further up if
the player has climbed above where that auto-scroll has reached. It
never moves back down to chase a falling player. See
`docs/doodle_jump_phase09.md` for full details and
`game/camera.py`/`game/difficulty.py` for the implementation.

**Impact on this phase's tests:** `tests/test_camera.py` was rewritten
for the new `update(dt, player_y, scroll_speed)` signature and ratchet
behavior; `tests/test_integration.py`'s
`test_camera_keeps_player_on_screen_while_climbing` was updated to pass
`scroll_speed=0` so it keeps testing only the ratchet-follow behavior it
originally covered.
