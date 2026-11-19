"""Wave progression, combat, economy, and upgrade rules."""
from math import hypot

from .config import BASE, BASE_RADIUS, BLUE, DEFENSES, ENEMY_KINDS, ENTRANCES, FIELD, MAX_BASE_HP, PADS, REPAIR_COST, REPAIR_HP, SPAWN_INTERVALS, STARTING_PLAYER_HP, UPGRADE_COST, WAVES
from .models import Drop, Enemy, Shot, Tower
from .geometry import distance

class Game:
    def __init__(self):
        self.reset()
        self.phase = 'title'

    def reset(self):
        self.phase = 'combat'
        self.wave = 0
        self.spawned = 0
        self.spawn_wait = 0.75
        self.player_x, self.player_y = 425.0, 467.0
        self.player_hp = self.max_player_hp = STARTING_PLAYER_HP
        self.base_hp = MAX_BASE_HP
        self.player_speed, self.damage, self.reach = 240, 24, 153
        self.attack_wait = self.hurt_wait = 0.0
        self.parts = self.energy = self.kills = self.xp = 0
        self.level, self.next_xp = 1, 5
        self.elapsed = 0.0
        self.selected_pad = 0
        self.enemies = []
        self.drops = []
        self.shots = []
        self.towers = [None] * len(PADS)
        self.notice = ('', '')
        self.notice_left = 0.0
        self.loss_reason = ('', '')

    def message(self, chinese, english):
        self.notice = chinese, english
        self.notice_left = 2.6

    def advance_wave(self):
        if self.phase == 'prepare' and self.wave + 1 < len(WAVES):
            self.wave += 1
            self.spawned = 0
            self.spawn_wait = 0.75
            self.phase = 'combat'
            self.notice_left = 0.0

    def can_afford(self, cost):
        return self.parts >= cost[0] and self.energy >= cost[1]

    def spend(self, cost):
        if not self.can_afford(cost):
            self.message('資源不足', 'Insufficient resources')
            return False
        self.parts -= cost[0]
        self.energy -= cost[1]
        return True

    def repair(self):
        if self.phase != 'prepare':
            return
        if self.base_hp == MAX_BASE_HP:
            self.message('禮堂耐久已滿', 'Auditorium durability is full')
            return
        if self.spend((REPAIR_COST, 0)):
            restored = min(REPAIR_HP, MAX_BASE_HP - self.base_hp)
            self.base_hp += restored
            self.message(f'禮堂耐久 +{restored}', f'Auditorium +{restored} HP')

    def build(self, kind):
        if self.phase != 'prepare':
            return
        if self.towers[self.selected_pad] is not None:
            self.message('這個建造點已有防禦塔', 'A tower already occupies this pad')
            return
        defense = DEFENSES[kind]
        if self.spend(defense.cost):
            self.towers[self.selected_pad] = Tower(kind)
            self.message(f'已建造{defense.name[0]}', f'{defense.name[1]} built')

    def upgrade_tower(self):
        if self.phase != 'prepare':
            return
        tower = self.towers[self.selected_pad]
        if tower is None:
            self.message('請先在這裡建塔', 'Build a tower on this pad first')
        elif tower.upgraded:
            self.message('這座塔已達最高等級', 'This tower is fully upgraded')
        elif self.spend(UPGRADE_COST):
            tower.upgraded = True
            self.message('砲塔攻擊與射程提升', 'Tower damage and range increased')

    def choose_upgrade(self, choice):
        if self.phase != 'upgrade':
            return
        self.xp -= self.next_xp
        self.level += 1
        self.next_xp += 3
        if choice == 0:
            self.damage += 8
        elif choice == 1:
            self.max_player_hp += 25
            self.player_hp += 25
        else:
            self.player_speed += 30
        if self.xp < self.next_xp:
            self.phase = 'combat'

    def move_player(self, dx, dy, dt):
        length = hypot(dx, dy)
        if length:
            self.player_x += self.player_speed * dx / length * dt
            self.player_y += self.player_speed * dy / length * dt
        left, top, width, height = FIELD
        self.player_x = max(left + 18, min(left + width - 18, self.player_x))
        self.player_y = max(top + 18, min(top + height - 18, self.player_y))

    def collect_drops(self):
        remaining = []
        for drop in self.drops:
            if distance(self.player_x, self.player_y, drop.x, drop.y) <= 30:
                if drop.energy:
                    self.energy += 1
                else:
                    self.parts += 1
            else:
                remaining.append(drop)
        self.drops = remaining

    def spawn_enemy(self):
        kind = WAVES[self.wave][self.spawned]
        x, y = ENTRANCES[(self.spawned + 2 * self.wave) % len(ENTRANCES)]
        hp = ENEMY_KINDS[kind].hp + 6 * self.wave
        self.enemies.append(Enemy(kind, x, y, hp, hp))
        self.spawned += 1

    def move_enemies(self, dt):
        for enemy in self.enemies:
            kind = ENEMY_KINDS[enemy.kind]
            enemy.slowed = max(0.0, enemy.slowed - dt)
            dx, dy = BASE[0] - enemy.x, BASE[1] - enemy.y
            length = hypot(dx, dy)
            room = length - BASE_RADIUS - kind.radius
            if room > 0.01:
                speed = kind.speed * (1 + 0.08 * self.wave)
                if enemy.slowed:
                    speed *= 0.54
                travel = min(room, speed * dt)
                enemy.x += dx * travel / length
                enemy.y += dy * travel / length
            else:
                enemy.base_wait -= dt
                if enemy.base_wait <= 0:
                    self.base_hp = max(0, self.base_hp - kind.base_damage)
                    enemy.base_wait = 0.9
            if self.hurt_wait <= 0 and distance(enemy.x, enemy.y, self.player_x, self.player_y) < kind.radius + 13:
                self.player_hp = max(0, self.player_hp - kind.player_damage)
                self.hurt_wait = 0.62

    def target_at(self, x, y, reach):
        nearest = None
        for enemy in self.enemies:
            gap = distance(x, y, enemy.x, enemy.y)
            if enemy.hp > 0 and gap <= reach:
                reach, nearest = gap, enemy
        return nearest

    def attack(self, dt):
        self.attack_wait -= dt
        if self.attack_wait <= 0:
            target = self.target_at(self.player_x, self.player_y, self.reach)
            if target is not None:
                target.hp -= self.damage
                self.shots.append(Shot((self.player_x, self.player_y), (target.x, target.y), BLUE))
                self.attack_wait = 0.37
        for pad, tower in zip(PADS, self.towers):
            if tower is None:
                continue
            tower.wait -= dt
            if tower.wait > 0:
                continue
            kind = DEFENSES[tower.kind]
            reach = kind.reach + (22 if tower.upgraded else 0)
            target = self.target_at(*pad, reach)
            if target is None:
                continue
            damage = kind.damage * 3 // 2 if tower.upgraded else kind.damage
            target.hp -= damage
            if tower.kind == 1:
                target.slowed = 1.08
            elif tower.kind == 2:
                for enemy in self.enemies:
                    if enemy is not target and enemy.hp > 0 and distance(enemy.x, enemy.y, target.x, target.y) <= 67:
                        enemy.hp -= damage
                        self.shots.append(Shot((target.x, target.y), (enemy.x, enemy.y), kind.color))
            self.shots.append(Shot(pad, (target.x, target.y), kind.color))
            tower.wait = kind.interval

    def remove_defeated(self):
        survivors = []
        for enemy in self.enemies:
            if enemy.hp > 0:
                survivors.append(enemy)
                continue
            self.kills += 1
            self.xp += 1
            self.drops.append(Drop(enemy.x - 8, enemy.y))
            if self.kills % 2 == 0:
                self.drops.append(Drop(enemy.x + 8, enemy.y, energy=True))
        self.enemies = survivors

    def update(self, dt, dx, dy):
        if self.phase not in ('combat', 'prepare'):
            return
        self.notice_left -= dt
        self.move_player(dx, dy, dt)
        self.collect_drops()
        for shot in self.shots:
            shot.remaining -= dt
        self.shots = [shot for shot in self.shots if shot.remaining > 0]
        if self.phase == 'prepare':
            return
        self.elapsed += dt
        self.hurt_wait = max(0.0, self.hurt_wait - dt)
        self.spawn_wait -= dt
        if self.spawn_wait <= 0 and self.spawned < len(WAVES[self.wave]):
            self.spawn_enemy()
            self.spawn_wait = SPAWN_INTERVALS[self.wave]
        self.move_enemies(dt)
        if self.player_hp == 0 or self.base_hp == 0:
            self.phase = 'loss'
            self.loss_reason = ('禮堂耐久已歸零', 'The auditorium fell') if self.base_hp == 0 else (
                '守衛的生命已歸零', 'The defender fell')
            return
        self.attack(dt)
        self.remove_defeated()
        self.collect_drops()
        if self.xp >= self.next_xp:
            self.phase = 'upgrade'
        elif self.spawned == len(WAVES[self.wave]) and not self.enemies:
            if self.wave + 1 == len(WAVES):
                self.phase = 'win'
            else:
                self.phase = 'prepare'
                self.message('可以拾取零件與能量，再決定如何備戰', 'Pick up drops, then repair or build')
