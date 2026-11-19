"""File paths for the proposal artwork used by the game."""

from pathlib import Path

ASSET_DIR = Path(__file__).resolve().parent.parent / "assets"
ARTWORK_DIR = ASSET_DIR / "game_art"
IMAGE_DIR = ASSET_DIR / "images"
ARTWORK_FILES = {
    "field": ARTWORK_DIR / "field.png",
    "defender": IMAGE_DIR / "NaiFrog.png",
    "bear": IMAGE_DIR / "Bear.png",
    "runner": ARTWORK_DIR / "runner.png",
    "title": ARTWORK_DIR / "title.png",
}

SPRITE_SIZES = {
    "bear": (44, 64),
    "defender": (33, 66),
}

SPRITE_DOWNSAMPLE = {
    "bear": 11,
    "defender": 11,
}
