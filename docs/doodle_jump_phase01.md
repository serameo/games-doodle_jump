# Doodle Jump - Phase 01: Project Bootstrap

**Version:** v0.1.0
**Status:** Done - confirmed working on your machine (window opens/closes correctly, all 6 pytest tests pass after the pytest.ini fix)
**Currently doing:** Complete - ready to start Phase 02

---

## Goal

A runnable window that opens and closes cleanly. No gameplay logic yet -
this phase only proves the project skeleton, settings loading, and the
main loop work end to end.

---

## Tasks

- [x] Project structure: `game/`, `tests/`, `config/`, `docs/`, `maps/`, `assets/`
- [x] `game/settings.py` - loads tunable values from `config/settings.json`
      (screen size, FPS, ice melt timer, speed-cap placeholders)
- [x] `config/settings.json` - the actual tunable values (see below)
- [x] `main.py` - `Game` class: opens a 480x800 window, loop capped at 60 FPS,
      closes cleanly on the window's close (QUIT) event
- [x] `tests/test_main.py` - 6 unit tests (window size, FPS setting, quit
      handling both ways, `update()`, `draw()`), run headless via a dummy
      SDL video driver so no real window is needed to test
- [x] `requirements.txt`

## Files added this phase

```
doodle_jump/
|-- main.py
|-- requirements.txt
|-- config/
|   `-- settings.json
|-- game/
|   |-- __init__.py
|   `-- settings.py
|-- tests/
|   `-- test_main.py
|-- docs/
|   |-- doodle_jump_plans.md
|   |-- doodle_jump_rules.md
|   `-- doodle_jump_phase01.md   (this file)
|-- maps/        (empty, populated from Phase 06)
`-- assets/      (empty, populated in Phase 11)
```

---

## How to run (on your machine)

```
pip install -r requirements.txt
python main.py     # opens the window - close it via the window's close button
pytest              # runs the unit tests, headless, no window needed
```

## Test status - IMPORTANT

I was not able to actually execute `pytest` or run the window in this
sandbox: this container has no network access, and `pygame`/`pytest` are
not pre-installed here, so I could not `pip install` them to verify. The
code has been written and reviewed carefully, but **please run the two
commands above on your machine and let me know the result** - especially
`pytest` - before we treat Phase 01 as fully done. If anything fails, paste
the error here and I will fix it before moving on.

### Bug found (round 1) - fixed

`python main.py` ran correctly. `pytest` failed to collect
`tests/test_main.py` with `ModuleNotFoundError: No module named 'main'`.

**Cause:** `tests/` has no `__init__.py`, so pytest's default import mode
only adds the `tests/` folder itself to `sys.path`, not the project root
where `main.py` lives - so `from main import Game` cannot resolve.

**Fix:** added `pytest.ini` at the project root:

```ini
[pytest]
pythonpath = .
```

This is a built-in pytest option (pytest >= 7) that adds the project root
to `sys.path` before collecting tests, without needing any `__init__.py`
files or changing the test imports.

**Confirmed:** re-run on your machine - `python main.py` opens/closes
correctly, and all 6 tests in `pytest` pass. Phase 01 is complete.

---

## Decisions carried into this phase

From `doodle_jump_plans.md` (Confirmed Decisions):
- Screen: 480x800, portrait
- Frame rate: capped at 60 FPS
- Ice melt timer: default 3s, already present in `config/settings.json`
  even though ice platforms themselves aren't implemented until Phase 05
- Max speed multiplier: placeholder value in settings, real tuning happens
  in Phase 09
- Art: placeholder background fill color is used; no sprites yet (per
  decision to defer real art to Phase 11)

---

## Open Questions

None currently.

---

## Next Phase

Phase 02: Player entity - position, gravity, and automatic jump on
platform contact. Will not start until you confirm Phase 01 runs
correctly on your machine.
