# Doodle Jump - Phase 08: Scoring

**Version:** v0.8.0
**Status:** Implementation complete - awaiting your test run and review
**Currently doing:** Waiting for your confirmation before starting Phase 09

---

## Goal

Real coin/diamond pickup (rules 2.3): touching a collectible removes it
and adds to a running score, shown on screen. The random spawner's
fallback column (Phase 04) now also places its own coins/diamonds every
5th/10th floor, since Phase 06's hand-authored maps only cover their own
explicit symbols.

---

## Tasks

- [x] `game/score.py` - new module:
  - `Score` - just holds/increments a running total
  - `collect_collectibles(player, collectibles, score)` - checks every
    collectible for overlap with the player (any overlap counts, no
    falling condition needed - you can grab one mid-air), adds its
    `VALUE` to the score, and returns the list of collectibles that
    remain (picked-up ones are dropped)
- [x] `game/platform_spawner.py` - added
      `generate_collectibles(platforms)`: treats each platform in a
      generated column as one "floor" and places a `Coin` every 5th
      floor and a `Diamond` every 10th (both appear together on floors
      that are multiples of 10), per rules 2.3
- [x] `main.py` updated:
  - `Game.update()` now calls `collect_collectibles(...)` every frame
    and replaces `self.collectibles` with what's left
  - the Phase 04 fallback column also gets
    `spawner.generate_collectibles(fallback_platforms)` appended
  - added `pygame.font.Font` and a "Score: N" overlay drawn in the
    top-left corner every frame
- [x] `tests/test_score.py` - 6 unit tests: starting value, `add()`,
      pickup awards points and removes the item, non-overlapping items
      are left alone, diamond value, mixed overlap/non-overlap in one
      call
- [x] `tests/test_platform_spawner.py` - 4 new tests: coin count matches
      `floors // 5`, diamond count matches `floors // 10`, a short
      column (<5 floors) generates nothing, and the 10th floor
      specifically gets both a coin and a diamond
- [x] `tests/test_integration.py` - 3 new end-to-end tests: picking up a
      real coin from the shipped map increases score by 1 and removes it
      from `game.collectibles`, picking up a diamond adds 3, and score
      accumulates correctly across multiple pickups in sequence

## Files changed this phase

```
doodle_jump/
|-- main.py                        (updated: Score + pickup wiring, on-screen display)
`-- game/
    |-- score.py                     (new)
    `-- platform_spawner.py          (updated: + generate_collectibles())
`-- tests/
    |-- test_score.py                (new)
    |-- test_platform_spawner.py     (updated: + collectible-generation tests)
    `-- test_integration.py          (updated: + pickup end-to-end tests)
```

---

## How to run

```
python main.py     # climb up and touch a coin or diamond - it should
                    # disappear and the "Score: N" text top-left should
                    # update immediately - close via the X button
pytest              # runs all unit tests, headless, no window needed
```

## Test status

Same sandbox limitation as previous phases - no network access, and
`pygame`/`pytest` are not pre-installed here, so I could not run these
myself. Code and tests were written and reviewed carefully. **Please run
both commands above and paste the result here** - especially check that
the score text is legible and updates the instant you touch a
coin/diamond, and that touched items actually disappear rather than
lingering on screen.

---

## Decisions carried into this phase

No new Confirmed Decisions were needed - rules 2.3 already specified the
point values (coin 1, diamond 3) and the "every 5/10 floors" spawn
frequency for randomly-generated platforms. Score display position
(top-left corner) and font were implementation details, not judged
significant enough to interrupt you for.

---

## Open Questions

None currently.

---

## Next Phase

Phase 09: difficulty scaling - scroll speed increases 2% per 30 points,
capped at a maximum (Confirmed Decision #2). Will not start until you
confirm Phase 08 runs correctly on your machine.
