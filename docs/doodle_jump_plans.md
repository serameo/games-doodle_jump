# Doodle Jump - Development Plan

**Status:** Draft v0.1 - awaiting review
**Language for game logic/comments:** English only
**Current stage:** Planning (pre-development)

---

## 1.1 Tools & Libraries

| Tool / Library | Purpose |
|---|---|
| Python 3.10+ | Language runtime |
| `pygame` | Rendering, input, game loop, window management |
| `pytest` | Unit testing framework |
| `venv` | Isolated environment |

### Installation steps
1. Install Python 3.10 or newer.
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate it:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies:
   ```
   pip install pygame pytest
   ```
5. (Optional) Freeze dependencies once confirmed:
   ```
   pip freeze > requirements.txt
   ```

---

## 1.2 File & Directory Structure

```
doodle_jump/
|-- main.py                  # Entry point - opens window, runs game loop
|-- game/
|   |-- __init__.py
|   |-- player.py            # Player entity: position, auto-jump, physics
|   |-- platform.py          # Platform base class + variants (brick, ice, spring, moving)
|   |-- platform_spawner.py  # Random platform generation logic
|   |-- camera.py            # Center-follow camera
|   |-- map_loader.py        # Reads map01.txt, map02.txt, ... then falls back to random
|   |-- score.py             # Coin/diamond scoring
|   `-- game_state.py        # Game over / restart / menu state machine
|-- maps/
|   |-- map01.txt
|   `-- map02.txt
|-- tests/
|   |-- test_player.py
|   |-- test_platform.py
|   |-- test_platform_spawner.py
|   |-- test_map_loader.py
|   |-- test_camera.py
|   `-- test_score.py
|-- assets/                  # Sprites/sounds (placeholder until added)
|-- docs/
|   |-- doodle_jump_plans.md
|   |-- doodle_jump_rules.md
|   `-- doodle_jump_phaseXX.md   # one per phase
`-- requirements.txt
```

---

## 1.3 Phase Breakdown

Each phase gets its own `doodle_jump_phaseXX.md` (English only), tracking: current version, status, tasks, open questions. No phase begins without confirmation on the previous one.

| Phase | Name | Goal |
|---|---|---|
| 01 | Project bootstrap | Runnable window (opens, displays blank screen, closes cleanly) |
| 02 | Player entity | Position, gravity, auto-jump on platform contact |
| 03 | Static platform | Brick platform (base class + static behavior) |
| 04 | Platform spawner | Random generation with guaranteed reachability |
| 05 | Special platforms | Ice (breakable/melts in 3s, tunable), moving up/down, moving left/right, spring (+50% jump) |
| 06 | Map file loading | Parse `map01.txt` bottom-to-top, fall back to random spawner when exhausted |
| 07 | Camera | Keep player centered on screen |
| 08 | Scoring | Coins (+1, every 5 floors) and diamonds (+3, every 10 floors) |
| 09 | Difficulty scaling | Scroll speed +2% per 30 points (tunable) |
| 10 | Game over flow | Detect fall below screen bound -> menu (retry / new game / quit) |
| 11 | Polish & tuning | Parameter tuning, integration tests, edge cases |

**Actual execution order note:** after Phase 05, manual testing was hard
to follow because there is no camera yet - the world only shows a thin
band near the start, so most platforms are drawn off-screen. At your
request, **Phase 07 (Camera) is implemented before Phase 06** (map file
loading), so manual testing has a properly scrolling view going forward.
Phase 06 resumes right after Phase 07 is confirmed.

---

## 1.4 Testing & Runnability Rule

Starting from **Phase 01**:
- The game must be runnable at the end of every phase (`python main.py`), even if it only opens and closes a window.
- Every new function/module ships with corresponding `pytest` unit tests.
- All code comments are written in English only.
- Any full file update is shown in its entirety, not as a diff/snippet.

---

## Confirmed Decisions

1. **Screen resolution:** 480x800 (portrait, standard mobile-like size)
2. **Difficulty scaling:** capped - scroll speed increases 2% per 30 points up to a max speed, then holds steady (exact cap value to be tuned during Phase 09)
3. **Ice platform melt timer:** configurable via a settings file (not hardcoded), default 3s
4. **Frame rate:** capped at 60 FPS
5. **Art style:** placeholder shapes (rectangles/circles) for Phases 01-10, real sprite art introduced during Phase 11 (Polish)
6. **Jump feel (Phase 02):** balanced, close to original Doodle Jump - gravity 2000 px/s^2, jump velocity -900 px/s (upward), spring platform multiplier x1.5 (the +50% from the rules). Values live in config/settings.json and can be re-tuned by feel later.
7. **Platform collision leniency (Phase 03):** lenient - any rectangle overlap between the player and a platform (while falling) counts as a landing, no minimum overlap percentage required.
8. **Platform vertical spacing (Phase 04):** medium margin, 140-190px between platforms (max jump height is ~202px with the Phase 02 physics, so this always leaves room to spare).
9. **Moving platform speed/range (Phase 05):** medium - 60 px/s, oscillating across an 80px range (typical Doodle-Jump-like pace, not too twitchy).
10. **Player horizontal control (post-Phase 05 fix):** keyboard left/right arrow keys, speed 300 px/s, with classic screen-wrap (exiting one side reappears on the other) - the original spec never covered this, and its absence combined with a collision-tunneling bug caused the player to eventually fall forever without landing. Documented as addenda in doodle_jump_phase02.md (movement) and doodle_jump_phase03.md (collision fix).
11. **Map grid size (Phase 06):** 8 columns per row (60px per cell, 480/8), row height 160px (within the same 140-190 reachable range as Confirmed Decision #8, so hand-authored map rows stay jumpable).
11. **Map grid size (Phase 06):** 8 columns per map row, so each column is screen_width/8 = 60px wide. Row height (vertical spacing between map rows) is 160px, reusing the reachable-gap logic from Confirmed Decision #8.

## Open Questions

None remaining - all decisions confirmed above.

---

**Next step:** upon your confirmation of this plan, I will create `doodle_jump_rules.md` (section 2 of the spec) and then `doodle_jump_phase01.md` to begin Phase 01 - each awaiting your review before moving forward, as specified.
