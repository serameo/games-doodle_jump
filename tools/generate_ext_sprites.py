"""Phase 11: one-time preprocessing script.

Slices game/../assets/sprites/doodle_jump_sprite_sheet.png (using the
matching .json frame data) into individual, pre-sized PNG files under
assets/sprites/final/ - one per sprite key the game actually draws.
This runs once (by Claude, while building this delivery) rather than at
game startup: the output PNGs are already exactly the right pixel size
for their entity's existing WIDTH/HEIGHT, so main.py just loads and
blits them directly - no slicing, rotating, or resizing logic needed in
the game itself, and no new runtime dependency (this script needs
Pillow; the game itself only needs pygame, same as before).

Steps per sprite:
1. Crop the named "frame" rectangle out of the atlas.
2. Auto-trim fully-transparent padding around the visible art (the
   atlas's raw crops include extra margin beyond the actual drawing).
3. Rotate 90 degrees where the source art is a tall vertical strip but
   the game needs a wide flat bar (ice, spring, the falling wall, and
   the vertical-moving bar) - your choice from the design discussion.
4. Resize (stretched, not letterboxed) to the exact target size.

Re-run this manually (`python tools/generate_sprites.py`) if the source
sprite sheet or its JSON ever changes.
"""

import json
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
SHEET_PATH = os.path.join(
    PROJECT_ROOT, "assets", "sprites", "doodle_jump_extended_sprite.png"
)
JSON_PATH = os.path.join(
    PROJECT_ROOT, "assets", "sprites", "doodle_jump_extended_sprite.json"
)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "assets", "sprites", "final")

# Existing in-game collision-box sizes (must not change - see
# game/player.py's Player.WIDTH/HEIGHT, game/platform.py's Platform.
# WIDTH/HEIGHT, game/collectible.py's Collectible.WIDTH/HEIGHT).
PLAYER_SIZE = (40, 40)
PLATFORM_SIZE = (70, 20)
COLLECTIBLE_SIZE = (20, 20)
BALLOON_SIZE = (145, 205)
HAWK_SIZE = (230, 190)
CLOUD_S_SIZE = (190, 150)
CLOUD_M_SIZE = (300, 200)
CLOUD_L_SIZE = (385, 225)
ROCKET_SIZE = (130,190)

# output_key -> (source frame name in the JSON, rotate_90, target size)
SPRITE_PLAN = {
    "cloud_small": ("cloud_small", False, CLOUD_S_SIZE),
    "cloud_medium": ("cloud_medium", False, CLOUD_M_SIZE),
    "cloud_large": ("cloud_large", False, CLOUD_L_SIZE),
    "hawk_left_fly1": ("left_hawk1", False, HAWK_SIZE),
    "hawk_left_fly2": ("left_hawk2", False, HAWK_SIZE),
    "hawk_right_fly1": ("right_hawk1", False, HAWK_SIZE),
    "hawk_right_fly2": ("right_hawk2", False, HAWK_SIZE),
    "balloon_red": ("red_balloon", False, BALLOON_SIZE),
    "balloon_red_dot": ("red_dot_balloon", False, BALLOON_SIZE),
    "balloon_red_stripe": ("red_stripe_balloon", False, BALLOON_SIZE),
    "balloon_red_vertical": ("red_vertical_balloon", False, BALLOON_SIZE),
    "balloon_red_diagonal": ("red_diagonal_balloon", False, BALLOON_SIZE),
    "balloon_red_checker": ("red_checker_balloon", False, BALLOON_SIZE),
    "rocket_red": ("red_rocket", False, ROCKET_SIZE),
    "rocket_green": ("green_rocket", False, ROCKET_SIZE),
    "rocket_blue": ("blue_rocket", False, ROCKET_SIZE),
    "rocket_yellow": ("yellow_rocket", False, ROCKET_SIZE),
    "rocket_purple": ("purple_rocket", False, ROCKET_SIZE),
    "rocket_orange": ("orange_rocket", False, ROCKET_SIZE),
}


def load_frame(sheet: Image.Image, frames: dict, name: str) -> Image.Image:
    box = frames[name]["frame"]
    return sheet.crop((box["x"], box["y"], box["x"] + box["w"], box["y"] + box["h"]))


def trim_transparent_padding(image: Image.Image) -> Image.Image:
    """Crop away fully-transparent margin around the visible art, so a
    generously-padded raw atlas crop doesn't get stretched along with
    its empty border."""
    bbox = image.getbbox()
    return image.crop(bbox) if bbox else image


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    sheet = Image.open(SHEET_PATH).convert("RGBA")
    with open(JSON_PATH) as f:
        frames = json.load(f)["frames"]

    for output_key, (frame_name, rotate, target_size) in SPRITE_PLAN.items():
        image = load_frame(sheet, frames, frame_name)
        image = trim_transparent_padding(image)
        if rotate:
            image = image.rotate(90, expand=True)
        image = image.resize(target_size, Image.LANCZOS)

        out_path = os.path.join(OUTPUT_DIR, f"{output_key}.png")
        image.save(out_path)
        print(f"wrote {out_path} ({target_size[0]}x{target_size[1]})")


if __name__ == "__main__":
    main()
