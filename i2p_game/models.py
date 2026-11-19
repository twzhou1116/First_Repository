"""Small data objects used by the game and interface."""

from dataclasses import dataclass
from typing import Callable

class Enemy:
    kind: int
    x: float
    y: float
    hp: int
    max_hp: int
    base_wait: float = 0.0
    slowed: float = 0.0


class Tower:
    kind: int
    upgraded: bool = False
    wait: float = 0.0


class Drop:
    x: float
    y: float
    energy: bool = False


class Shot:
    origin: tuple
    target: tuple
    color: str
    remaining: float = 0.12


class Button:
    bounds: tuple
    action: Callable[[], None]
