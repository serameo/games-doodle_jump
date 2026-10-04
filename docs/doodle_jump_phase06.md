# Doodle Jump - Phase 06: Map File Loading

**Version:** v0.6.0
**Status:** Done - confirmed working on your machine
**Currently doing:** Complete - moving to Phase 08 next (Phase 09/10/11 remain after that)

---

## Note on phase order

This phase was paused right after being started, so Phase 07 (Camera)
could be done first - see `doodle_jump_phase07.md` and the "Actual
execution order note" in `doodle_jump_plans.md`. This is that resumed
work, now built on top of the working camera.

---

## Goal

Replace the Phase 04/05 fixed demo layout with real map file loading per
rules 2.4: parse `maps/map01.txt`, then `maps/map02.txt`, and so on
(bottom row to top row), placing every platform type and both
collectibles from the symbol legend. Falls back to the Phase 04 random
spawner once map files are exhausted.

---

## Tasks

- [x] `game/collectible.py` - new module: `Collectible` base class plus
      `Coin` (symbol 'c'/'C', value 1) and `Diamond` (symbol 'd'/'D',
      value 3). Inert for now - placed and drawn, but pickup/scoring
      itself is Phase 08.
- [x] `game/special_platforms.py` - added `Wall` (symbol '!'): not
      solid (never a landing surface, per rules 2.2), but still visible
      - see the known-limitation note in its docstring about horizontal
      blocking not being implemented yet.
- [x] `game/platform.py` - added `is_visible()` hook, separate from
      `is_solid()` (a Wall is visible-but-not-solid; melted ice is
      neither).
- [x] `game/map_loader.py` - new module:
  - `cell_width(screen_width)` - 480 / 8 = 60px per column (Confirmed
    Decision #11)
  - `load_map_file(path, start_y, screen_width, ice_melt_seconds)` -
    parses one file bottom row to top row, placing each row
    `ROW_HEIGHT` (160px) above the last, returning
    `(platforms, collectibles, next_y)`
  - `MapLoader` - loads `map01.txt`, `map02.txt`, ... in order from a
    directory; `has_next_map()` / `load_next(start_y)`
- [x] `maps/map01.txt`, `maps/map02.txt` - demo map files exercising
      every symbol from rules 2.4 (wall, brick, ice, spring, both moving
      types, coin, diamond, empty)
- [x] `main.py` updated:
  - loads every available map file via `MapLoader` in a loop, each one
    continuing from the last one's returned `next_y`
  - once maps are exhausted, the Phase 04 `PlatformSpawner` continues
    the column upward (rules 2.4's fallback rule)
  - `draw()` now uses `is_visible()` (not `is_solid()`) to decide what
    to render, and also draws `self.collectibles`
- [x] `tests/test_map_loader.py` - 9 unit tests: column/cell math, every
      symbol type parses to the right class, row placement order and
      spacing, x position matches the column grid, blank lines are
      ignored, configurable ice melt timer flows through, multi-file
      sequencing, empty result once exhausted, and a sanity check that
      parses the actual shipped `maps/map01.txt` / `map02.txt`
- [x] `tests/test_collectible.py` - 3 unit tests: coin/diamond values,
      rect sync
- [x] `tests/test_special_platforms.py` - added Wall tests
      (`is_solid()` False, `is_visible()` True) and an ice-becomes-
      invisible-once-melted test
- [x] `tests/test_integration.py` - updated the scripted playthrough and
      camera tests to skip `Wall` (intentionally never landable)

## Files changed this phase

```
doodle_jump/
|-- main.py                        (updated: MapLoader replaces fixed demo layout)
|-- maps/
|   |-- map01.txt                   (new)
|   `-- map02.txt                   (new)
`-- game/
    |-- platform.py                  (updated: + is_visible())
    |-- special_platforms.py         (updated: + Wall, ice + is_visible())
    |-- collectible.py               (new)
    `-- map_loader.py                (new)
`-- tests/
    |-- test_map_loader.py           (new)
    |-- test_collectible.py          (new)
    |-- test_special_platforms.py    (updated: + Wall, ice visibility tests)
    `-- test_integration.py          (updated: exclude Wall from landing tests)
```

---

## How to run

```
python main.py     # climb up through map01's mix of platforms (wall,
                    # brick, moving up/down, coin, ice, spring, brick+
                    # diamond, in that bottom-to-top order), then map02's
                    # shorter layout, then the random column continues
                    # after that - close via the X button
pytest              # runs all unit tests, headless, no window needed
```

## Test status

Same sandbox limitation as previous phases - no network access, and
`pygame`/`pytest` are not pre-installed here, so I could not run these
myself. Code and tests were written and reviewed carefully. **Please run
both commands above and paste the result here** - especially check that:
- you can see coins (small gold squares) and a diamond (cyan square) as
  you climb - they don't do anything yet (no pickup/score), that's
  expected until Phase 08
- the two gray walls near the very start are visible but you simply
  fall through them if you try to land there (expected - see the Wall
  limitation note above)
- after map01 and map02 are climbed through, the game keeps generating
  new random platforms rather than running out

---

## Decisions carried into this phase

- Confirmed Decision #11: 8 columns (60px each), 160px row height.

---

## Known limitation flagged (not a decision needed right now, just FYI)

Walls block horizontal movement per rules 2.2, but the player currently
has no horizontal collision with anything - it can walk straight through
a Wall left/right. Only vertical landing is blocked. Let me know if you
want this implemented; it isn't covered by any of the 11 planned phases
as originally scoped.

---

## Open Questions

None currently.

---

## Next Phase

Phase 08: Scoring - coins (+1) and diamonds (+3), collected on contact
with the player and removed once picked up, with a running score
displayed. Will not start until you confirm Phase 06 runs correctly on
your machine.
