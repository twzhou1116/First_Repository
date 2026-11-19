"""Shared game configuration and balance data."""

from dataclasses import dataclass

WIDTH, HEIGHT = 1152, 720


FIELD = (20, 108, 812, 555)


SIDE = (850, 108, 282, 555)


BASE = (425, 379)


BASE_RADIUS = 68


PADS = ((284, 374), (567, 374), (425, 516))


ENTRANCES = (
    (86, 178), (758, 583), (752, 172), (94, 591),
    (425, 142), (800, 371), (425, 628), (54, 371),
)


MAX_BASE_HP = 180


REPAIR_COST, REPAIR_HP = 4, 38


UPGRADE_COST = (5, 2)


STARTING_PLAYER_HP = 100


BG = '#0c1621'


PANEL = '#162534'


BORDER = '#2d4558'


TEXT = '#edf5fa'


MUTED = '#a8bdcd'


GREEN = '#8ee5ae'


BLUE = '#78d7ff'


GOLD = '#ffd181'


PURPLE = '#c9b3ff'


RED = '#ff8580'


@dataclass
class EnemyKind:
    hp: int
    speed: int
    base_damage: int
    player_damage: int
    radius: int
    color: str


ENEMY_KINDS = (
    EnemyKind(48, 51, 6, 9, 14, RED),
    EnemyKind(29, 84, 4, 7, 10, '#ffac66'),
)


WAVES = (
    (0,) * 8,
    (0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0),
    (1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1),
)


SPAWN_INTERVALS = (1.15, 0.94, 0.77)


@dataclass
class DefenseKind:
    name: tuple
    description: tuple
    cost: tuple
    reach: int
    damage: int
    interval: float
    color: str


DEFENSES = (
    DefenseKind(('哨戒塔', 'Sentry'), ('快速攻擊單一敵人', 'Rapid single-target shots'),
                (5, 2), 185, 18, 0.55, GOLD),
    DefenseKind(('冰霜塔', 'Frost tower'), ('傷害並減緩敵人', 'Damages and slows enemies'),
                (5, 3), 170, 12, 0.62, BLUE),
    DefenseKind(('脈衝塔', 'Pulse tower'), ('同時打擊附近敵群', 'Hits groups near the target'),
                (7, 3), 171, 22, 0.90, PURPLE),
)


UPGRADES = (
    (('攻擊強化', 'Power'), ('每次攻擊傷害 +8', 'Attack damage +8'), GOLD),
    (('生命強化', 'Vitality'), ('最大生命與目前生命 +25', 'Maximum and current HP +25'), GREEN),
    (('移動強化', 'Agility'), ('移動速度 +30', 'Movement speed +30'), BLUE),
)
