"""File paths for the proposal artwork used by the game."""

from pathlib import Path

ARTWORK_DIR = Path(__file__).resolve().parent.parent / "assets" / "game_art"
ARTWORK_FILES = {
    name: ARTWORK_DIR / f"{name}.png"
    for name in ("field", "defender", "bear", "runner", "title")
}
