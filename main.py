"""Entry point for the Doodle Jump game.

Phase 01 (project bootstrap): opens a window sized per config/settings.json
and closes cleanly on the window's close button.

Phase 02 (player entity) added a Player with gravity and jump physics.

Phase 03 (platforms) replaced the Phase 02 temporary demo floor with real
static "brick" Platform objects and a fixed demo layout.

Phase 04 (platform spawner) replaces that fixed layout with real random
generation via PlatformSpawner: a starting platform under the player,
then a column of platforms generated upward, each one guaranteed
reachable from the last (Confirmed Decision #8). Endless generation as
the player climbs (recycling/removing off-screen platforms) is handled
together with the camera in Phase 07 - for now the column is generated
once, tall enough to climb through for a while during manual testing.

Phase 05 (special platforms) adds ice, spring, and moving up/down and
left/right platform types (rules 2.2).

Post-Phase-05 fix: added left/right keyboard movement for the player
(the original spec never covered horizontal control) and fixed a
collision-tunneling bug where a fast-falling player could skip through a
thin platform within a single frame. See the addenda in
docs/doodle_jump_phase02.md and docs/doodle_jump_phase03.md.

Phase 07 (Camera, implemented ahead of Phase 06 at your request - see
the note in doodle_jump_plans.md) keeps the player vertically centered
on screen (rules 2.5). All physics/collision stays in world coordinates;
only draw() converts world y to screen y via Camera.to_screen_y().

Phase 06 (map file loading, resumed after Phase 07) replaces the fixed
Phase 04/05 demo layout: platforms and collectibles are now loaded from
maps/map01.txt, then maps/map02.txt, and so on (rules 2.4), via
MapLoader. Once map files are exhausted, the Phase 04 random spawner
takes over and continues the column upward, per rules 2.4's fallback
rule.

Phase 08 (scoring) adds real pickup: touching a coin/diamond removes it
and adds to a running score (rules 2.3), shown in the top-left corner.
The random spawner's fallback column now also generates its own
coins/diamonds every 5th/10th floor (map-placed ones were already
handled by Phase 06).

Phase 09 (difficulty scaling) makes the camera auto-scroll upward on its
own, continuously, at a speed that increases 2% per 30 points scored
(capped) - see game/difficulty.py and the revised game/camera.py. This
replaces Phase 07's "always centered, both directions" camera with a
one-directional "ratchet" camera (see docs/doodle_jump_phase09.md).

Phase 10 (game over flow) detects the player's feet dropping below the
bottom edge of the visible screen with no platform underneath them
(rules 2.1, now meaningful thanks to Phase 09's ratchet camera never
following a fall back down) and shows a menu: Continue (retry this
run), New Game, or Quit - see game/game_state.py and
docs/doodle_jump_phase10.md. World-building was refactored out of
__init__ into _build_world()/_new_run() so both the initial run and
"Continue"/"New Game" share the same setup code.

Phase 10 addendum (added after your review): a title-screen main menu
is now shown before gameplay starts (Start Game / Quit), and the
game-over menu's "Quit" now returns to this title screen instead of
closing the app outright - see the addendum in
docs/doodle_jump_phase10.md. Also added: a Wall (rules 2.2) is now
landable, and the first time the player lands on one it starts falling
straight down under acceleration (reusing config/settings.json's
"gravity") - see game/special_platforms.py's Wall class.

Phase 11 (polish) replaces every placeholder colored rectangle with the
real sprite art you provided, pre-sliced to each entity's existing
pixel size by tools/generate_sprites.py (see game/sprites.py and
docs/doodle_jump_phase11.md). draw() now looks up each entity's
sprite_key() in self.sprites and blits the image; if a key is somehow
missing, it falls back to the original colored rectangle rather than
crashing.
"""

import copy
import os

import pygame

from game.camera import Camera
from game.collision import find_landing_platform
from game.difficulty import current_scroll_speed
from game.game_state import GameState, has_fallen_off_screen
from game.map_loader import MapLoader
from game.platform import Platform
from game.platform_spawner import PlatformSpawner
from game.player import Player
from game.score import Score, collect_collectibles
from game.settings import load_settings
from game.sprites import load_sprites

MAPS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maps")


class Game:
    """Owns the pygame window and the main loop."""

    def __init__(self, headless: bool = False) -> None:
        if headless:
            # Used by automated tests: no real window is created/shown.
            os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

        pygame.init()
        self.settings = load_settings()
        self.screen = pygame.display.set_mode(
            (self.settings["screen_width"], self.settings["screen_height"])
        )
        pygame.display.set_caption("Doodle Jump")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 36)
        # Phase 10: extra fonts for the menu screens.
        self.title_font = pygame.font.Font(None, 56)
        self.menu_font = pygame.font.Font(None, 28)

        # Phase 11: real sprite art, keyed by sprite_key() (see
        # game/sprites.py). draw() falls back to the original colored
        # rectangles for any key not found here.
        self.sprites = load_sprites()

        # Phase 10: which screen is active - the title screen, gameplay,
        # or the game-over menu (rules 2.1). GameState starts in its
        # MAIN_MENU status, so the title screen is what's shown first.
        self.game_state = GameState()

        # Builds player/platforms/collectibles/score/camera so a world
        # already exists behind the title screen, ready for "Start
        # Game." Does not touch self.game_state - see _new_run().
        self._new_run(regenerate_world=True)

    def _build_world(self):
        """Build a fresh (platforms, collectibles) pair from scratch:
        the starting platform, then every available map file in order
        (Phase 06), then the Phase 04 random fallback column (with its
        own coins/diamonds every 5th/10th floor, Phase 08) once map
        files are exhausted (rules 2.4).

        Used at startup and whenever the player starts a brand-new game
        (from the title screen or the game-over menu), which needs an
        entirely fresh (re-randomized) layout.
        """
        # A starting platform right under the player, so there's always
        # an immediate, guaranteed-reachable first landing.
        starting_platform = Platform(
            x=self.settings["screen_width"] / 2 - Platform.WIDTH / 2,
            y=250,
        )
        platforms = [starting_platform]
        collectibles = []

        map_loader = MapLoader(
            maps_dir=MAPS_DIR,
            screen_width=self.settings["screen_width"],
            ice_melt_seconds=self.settings["ice_melt_seconds"],
            wall_fall_acceleration=self.settings["gravity"],
            ice_broken_visible_seconds=self.settings["ice_broken_visible_seconds"],
        )
        current_top_y = starting_platform.y
        while map_loader.has_next_map():
            new_platforms, new_collectibles, current_top_y = map_loader.load_next(
                start_y=current_top_y
            )
            platforms += new_platforms
            collectibles += new_collectibles

        self.spawner = PlatformSpawner(screen_width=self.settings["screen_width"])
        fallback_platforms = self.spawner.generate_column(
            start_y=current_top_y,
            top_y=current_top_y - 800,  # extra height for manual testing
        )
        platforms += fallback_platforms
        collectibles += self.spawner.generate_collectibles(fallback_platforms)

        return platforms, collectibles

    def _new_run(self, regenerate_world: bool) -> None:
        """Reset the player, score, and camera for a fresh run.

        regenerate_world=True rebuilds platforms/collectibles from
        scratch, including a freshly randomized fallback column (used at
        startup, and for "Start a new game"). regenerate_world=False
        instead restores the pristine snapshot captured the last time
        the world was built - putting melted ice, picked-up coins, moved
        platforms, and fallen walls back exactly as they started (Phase
        10's "Continue": retry the same run).

        Does not change self.game_state - callers decide what screen
        should be showing afterward (see handle_events()).
        """
        self.player = Player(
            x=self.settings["screen_width"] / 2 - Player.WIDTH / 2,
            y=100,
            settings=self.settings,
        )

        if regenerate_world:
            self.platforms, self.collectibles = self._build_world()
            # Deep-copied so a later "Continue" can restore this exact
            # layout even after ice melts, coins get picked up, or a
            # wall starts falling.
            self._pristine_platforms = copy.deepcopy(self.platforms)
            self._pristine_collectibles = copy.deepcopy(self.collectibles)
        else:
            self.platforms = copy.deepcopy(self._pristine_platforms)
            self.collectibles = copy.deepcopy(self._pristine_collectibles)

        # Phase 08: running score, incremented as collectibles are picked up.
        self.score = Score()

        # Phase 07/09: camera keeps the player on screen while advancing
        # its own continuous auto-scroll (rules 2.5 + 2.1; speed set by
        # game/difficulty.py, based on the current score).
        self.camera = Camera(
            screen_height=self.settings["screen_height"],
            player_height=Player.HEIGHT,
        )
        initial_scroll_speed = current_scroll_speed(self.score.value, self.settings)
        self.camera.update(
            dt=0.0, player_y=self.player.y, scroll_speed=initial_scroll_speed
        )

    def handle_events(self) -> bool:
        """Process pending events. Returns False when the game should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type != pygame.KEYDOWN:
                continue

            if self.game_state.is_main_menu():
                # Phase 10 addendum: the title screen.
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._new_run(regenerate_world=True)  # Start Game
                    self.game_state.resume_playing()
                elif event.key == pygame.K_q:
                    return False  # Quit the application
            elif self.game_state.is_game_over():
                # Phase 10: the game-over menu (rules 2.1).
                if event.key == pygame.K_c:
                    self._new_run(regenerate_world=False)  # Continue
                    self.game_state.resume_playing()
                elif event.key == pygame.K_n:
                    self._new_run(regenerate_world=True)  # Start a new game
                    self.game_state.resume_playing()
                elif event.key == pygame.K_q:
                    # Phase 10 addendum: back to the title screen, not a
                    # full application quit.
                    self.game_state.show_main_menu()
        return True

    def read_horizontal_input(self) -> int:
        """Read the left/right arrow key state. Returns -1, 0, or +1."""
        keys = pygame.key.get_pressed()
        direction = 0
        if keys[pygame.K_LEFT]:
            direction -= 1
        if keys[pygame.K_RIGHT]:
            direction += 1
        return direction

    def update(self, dt: float) -> None:
        if not self.game_state.is_playing():
            # Frozen behind the title screen or the game-over menu until
            # the player picks an option (handled in handle_events()).
            return

        direction = self.read_horizontal_input()
        self.player.move(direction, dt)
        self.player.wrap_around(self.settings["screen_width"])

        self.player.update(dt)
        for platform in self.platforms:
            platform.update(dt)

        landing_platform = find_landing_platform(self.player, self.platforms)
        if landing_platform is not None:
            landing_platform.on_landed()
            self.player.land(
                landing_platform.rect.top,
                boosted=landing_platform.boosts_jump(),
            )
        elif has_fallen_off_screen(
            self.player, self.camera, self.settings["screen_height"]
        ):
            # Phase 10: no platform caught the player this frame, and
            # their feet are now below the bottom edge of the visible
            # screen (rules 2.1). Stop here - no point updating
            # collectibles/camera for a frame that's about to freeze.
            self.game_state.trigger_game_over()
            return

        self.collectibles = collect_collectibles(
            self.player, self.collectibles, self.score
        )

        # Phase 09: scroll speed increases with score (capped), then the
        # ratchet camera applies it - see game/difficulty.py and the
        # revised game/camera.py.
        scroll_speed = current_scroll_speed(self.score.value, self.settings)
        self.camera.update(dt=dt, player_y=self.player.y, scroll_speed=scroll_speed)

    def _blit_sprite_or_rect(
        self, sprite_key, screen_rect: pygame.Rect, color: tuple
    ) -> None:
        """Phase 11: draw the named sprite at screen_rect if we have it
        loaded; otherwise fall back to the original colored rectangle
        placeholder (e.g. if assets/sprites/final/ is missing a file)."""
        sprite = self.sprites.get(sprite_key) if sprite_key else None
        if sprite is not None:
            self.screen.blit(sprite, screen_rect)
        else:
            pygame.draw.rect(self.screen, color, screen_rect)

    def draw(self) -> None:
        if self.game_state.is_main_menu():
            self._draw_main_menu()
            pygame.display.flip()
            return

        # Sky-blue background, behind the platform/player/collectible art.
        self.screen.fill((135, 206, 235))

        for platform in self.platforms:
            if platform.is_visible():
                screen_rect = pygame.Rect(
                    int(platform.x),
                    int(self.camera.to_screen_y(platform.y)),
                    platform.WIDTH,
                    platform.HEIGHT,
                )
                self._blit_sprite_or_rect(
                    platform.sprite_key(), screen_rect, platform.COLOR
                )

        for collectible in self.collectibles:
            screen_rect = pygame.Rect(
                int(collectible.x),
                int(self.camera.to_screen_y(collectible.y)),
                collectible.WIDTH,
                collectible.HEIGHT,
            )
            self._blit_sprite_or_rect(
                collectible.sprite_key(), screen_rect, collectible.COLOR
            )

        player_screen_rect = pygame.Rect(
            int(self.player.x),
            int(self.camera.to_screen_y(self.player.y)),
            Player.WIDTH,
            Player.HEIGHT,
        )
        self._blit_sprite_or_rect(
            self.player.sprite_key(), player_screen_rect, (255, 140, 0)
        )

        # Phase 08: running score, top-left corner.
        score_surface = self.font.render(
            f"Score: {self.score.value}", True, (0, 0, 0)
        )
        self.screen.blit(score_surface, (10, 10))

        if self.game_state.is_game_over():
            self._draw_game_over_menu()

        pygame.display.flip()

    def _draw_main_menu(self) -> None:
        """Phase 10 addendum: the title screen shown before gameplay
        starts, and returned to via the game-over menu's "Quit"."""
        self.screen.fill((135, 206, 235))

        center_x = self.settings["screen_width"] / 2
        lines = [
            (self.title_font, "DOODLE JUMP", (255, 255, 255)),
            (self.menu_font, "Enter - Start Game", (20, 20, 20)),
            (self.menu_font, "Q - Quit", (20, 20, 20)),
        ]

        y = self.settings["screen_height"] / 2 - 60
        for font, text, color in lines:
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect(center=(center_x, y))
            self.screen.blit(text_surface, text_rect)
            y += text_surface.get_height() + 20

    def _draw_game_over_menu(self) -> None:
        """Phase 10: a translucent overlay with the game-over menu
        (rules 2.1), drawn on top of the frozen gameplay frame."""
        overlay = pygame.Surface(
            (self.settings["screen_width"], self.settings["screen_height"])
        )
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        center_x = self.settings["screen_width"] / 2
        lines = [
            (self.title_font, "GAME OVER", (255, 255, 255)),
            (self.font, f"Score: {self.score.value}", (255, 255, 255)),
            (self.menu_font, "C - Continue (retry this run)", (220, 220, 220)),
            (self.menu_font, "N - New Game", (220, 220, 220)),
            (self.menu_font, "Q - Back to Title", (220, 220, 220)),
        ]

        y = self.settings["screen_height"] / 2 - 110
        for font, text, color in lines:
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect(center=(center_x, y))
            self.screen.blit(text_surface, text_rect)
            y += text_surface.get_height() + 16

    def run(self) -> None:
        while self.running:
            dt_ms = self.clock.tick(self.settings["fps"])
            dt = dt_ms / 1000.0
            self.running = self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()


def main() -> None:
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
