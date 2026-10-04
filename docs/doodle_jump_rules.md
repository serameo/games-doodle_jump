# Doodle Jump - Game Rules

**Status:** Draft v0.1 - awaiting review
**Language:** English only (comments and code identifiers)

---

## Overview

The screen scrolls downward slowly and continuously. Scroll speed increases as
the player's score increases: for every 30 points scored, scroll speed
increases by 2%, up to a capped maximum speed (see `doodle_jump_plans.md`,
Confirmed Decisions #2 - exact cap value to be tuned in Phase 09).

The player must stay above the bottom edge of the screen, either standing on
a platform or airborne mid-jump. If the player's feet fall below the
game-over boundary while not supported by any platform, the game ends.

---

## 2.1 Player Rules

- The player jumps automatically every time their feet touch a platform (no
  manual jump input required).
- While moving upward, the player can pass through platforms from below
  (platforms do not block upward movement).
- While falling, the player lands and immediately re-jumps the instant their
  feet touch a platform.
- If the player falls below the screen with no platform underneath them, the
  game ends. The player is then presented with a menu to:
  - Continue (retry same run), or
  - Start a new game, or
  - Quit to the main menu.

---

## 2.2 Platforms

| Type | Symbol | Behavior |
|---|---|---|
| Brick | `=` | Static, always solid. |
| Ice | `~` | Starts solid. Once the player stands on it, it begins melting. After the configured melt timer elapses (default 3s, see settings file per Confirmed Decision #3), it disappears completely. |
| Moving up/down | `^` | Slides vertically between two bounds. |
| Moving left/right | `>` | Slides horizontally between two bounds. |
| Spring | `@` | Boosts the player's next jump height by +50%. |
| Wall | `!` | Static, blocks horizontal movement (does not act as a landing platform). |

### Platform generation rule
When platforms are randomly generated (rather than read from a map file),
each new platform must always be reachable by a jump from the platform
generated immediately before it. The player must never face a gap that is
impossible to clear.

---

## 2.3 Score

- Collecting a coin (`c` / `C`): +1 point. Coins spawn every 5 floors.
- Collecting a diamond (`d` / `D`): +3 points. Diamonds spawn every 10 floors.

---

## 2.4 Map Format

Maps are read from plain text files, starting with `map01.txt`, then
`map02.txt`, and so on. Once all map files have been consumed, the game
switches to fully random platform generation for the rest of the run (see
2.2, Platform generation rule).

Each map file is read from the **bottom row to the top row**.

### Symbol legend

| Symbol | Meaning |
|---|---|
| `!` | Wall (static) |
| `=` | Brick platform |
| ` ` or `.` | Empty space (no platform) |
| `@` | Spring platform |
| `^` | Moving up/down platform |
| `>` | Moving left/right platform |
| `~` | Ice platform |
| `c` or `C` | Coin |
| `d` or `D` | Diamond |

---

## 2.5 Camera

The camera stays centered on the player at all times, scrolling vertically
as the player climbs and as the screen auto-scrolls downward.

---

## Related Settings (cross-reference to Confirmed Decisions)

These values are configurable rather than hardcoded, per the decisions
recorded in `doodle_jump_plans.md`:

- Screen resolution: 480x800 (portrait)
- Scroll speed increase: +2% per 30 points, capped at a max speed (exact cap TBD in Phase 09)
- Ice platform melt timer: default 3s, adjustable via settings file
- Frame rate: capped at 60 FPS
- Visuals: placeholder shapes through Phase 10, real sprites introduced in Phase 11

---

## Open Questions

None yet - flag anything unclear here as it comes up during implementation.

---

**Next step:** upon your confirmation of these rules, I will create
`doodle_jump_phase01.md` to begin Phase 01 (project bootstrap: a runnable
window that opens and closes cleanly), and wait for review before writing
any code.
