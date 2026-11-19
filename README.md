# Auditorium Defense

A small bilingual defense game set at the NTHU Auditorium. The game supports Pygame, with Tkinter as a fallback when Pygame is not installed.

## Run

```bash
python auditorium_defense.py
```

You can also run `python main.py`. The traditional Chinese interface uses the font bundled at `assets/fonts/NotoSansTC.ttf`.

## Project layout

- `i2p_game/config.py`: screen layout, colors, waves, enemies, towers, and upgrades
- `i2p_game/models.py`: game data objects
- `i2p_game/game.py`: simulation and game rules
- `i2p_game/interface.py`: screens, controls, and input handling
- `i2p_game/canvas.py`: Pygame and Tkinter drawing backends
- `i2p_game/artwork.py`: artwork file paths
- `assets/game_art/`: PNG artwork used by the game
- `i2p_game/launcher.py`: application startup and event loops
