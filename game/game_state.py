"""Game over / restart / new game / quit state machine (rules 2.1).

The player must stay above the bottom edge of the visible screen, either
standing on a platform or airborne mid-jump. Since Phase 09's camera is
a one-directional "ratchet" (it never follows a falling player back
down), falling behind wherever the camera has already climbed to is
what makes falling dangerous: eventually the player's feet cross below
the bottom edge of the screen with no platform underneath them, and the
game ends (rules 2.1).

The player is then presented with a menu (rules 2.1) to:
- Continue: retry the exact same run. Platforms/collectibles are reset
  to exactly how they looked at the start of this run - including
  putting back melted ice, picked-up coins/diamonds, and fallen walls -
  and the player and score reset too. See Game._new_run() in main.py.
- Start a new game: rebuild everything from scratch, including a freshly
  randomized fallback column (game/platform_spawner.py's RNG is
  unseeded by default, so a new game's random platforms differ from the
  previous run's).
- Quit: return to the title screen (MAIN_MENU) - see the Phase 10
  addendum in docs/doodle_jump_phase10.md. From the title screen itself,
  Quit exits the application.

A third status, MAIN_MENU, is the title screen shown before gameplay
starts and whenever the game-over menu's "Quit" is chosen.
"""

from enum import Enum

from game.player import Player


class GameStatus(Enum):
    MAIN_MENU = "main_menu"
    PLAYING = "playing"
    GAME_OVER = "game_over"


class GameState:
    """Tracks which screen is active: the title screen, gameplay, or the
    game-over menu. Starts on the title screen."""

    def __init__(self) -> None:
        self.status = GameStatus.MAIN_MENU

    def trigger_game_over(self) -> None:
        self.status = GameStatus.GAME_OVER

    def resume_playing(self) -> None:
        self.status = GameStatus.PLAYING

    def show_main_menu(self) -> None:
        self.status = GameStatus.MAIN_MENU

    def is_playing(self) -> bool:
        return self.status is GameStatus.PLAYING

    def is_game_over(self) -> bool:
        return self.status is GameStatus.GAME_OVER

    def is_main_menu(self) -> bool:
        return self.status is GameStatus.MAIN_MENU


def has_fallen_off_screen(player: Player, camera, screen_height: float) -> bool:
    """True once the player's feet have dropped below the bottom edge of
    the currently visible screen (rules 2.1's game-over condition).

    Intended to be checked only on a frame where the player did *not*
    just land on a platform (see Game.update() in main.py) - "with no
    platform underneath them" is already guaranteed by that ordering,
    since a successful landing snaps the player back onto a platform's
    top before this check ever runs.
    """
    feet_screen_y = camera.to_screen_y(player.y + Player.HEIGHT)
    return feet_screen_y > screen_height
