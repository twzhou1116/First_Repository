"""Input handling and game screen drawing."""

from .config import BASE, BG, BLUE, BORDER, DEFENSES, ENEMY_KINDS, ENTRANCES, FIELD, GOLD, GREEN, MAX_BASE_HP, MUTED, PADS, PANEL, PURPLE, RED, SIDE, TEXT, UPGRADES, WAVES
from .models import Button
from .game import Game
from .geometry import distance, inside

class Interface:
    def __init__(self, canvas):
        self.canvas = canvas
        self.game = Game()
        self.keys = set()
        self.buttons = []
        self.pointer = (-1, -1)
        self.before_pause = 'combat'
        self.drawn_phase = None
        self.focus_paused = False

    def word(self, chinese, english):
        return chinese if self.canvas.chinese else english

    def text(self, x, y, value, size=18, color=TEXT, anchor='w'):
        self.canvas.text(x, y, value, size, color, anchor)

    def label(self, x, y, chinese, english, size=18, color=TEXT, anchor='w'):
        self.text(x, y, self.word(chinese, english), size, color, anchor)

    def button(self, x, y, width, height, title, action, accent=BLUE, primary=False):
        bounds = (x, y, width, height)
        hover = inside(*self.pointer, bounds)
        fill = accent if primary else ('#294355' if hover else '#203345')
        self.canvas.rect(*bounds, fill, outline=accent if hover or primary else BORDER)
        self.text(x + width / 2, y + height / 2, self.word(*title), 16,
                  BG if primary else TEXT, 'center')
        self.buttons.append(Button(bounds, action))

    def start(self):
        self.keys.clear()
        self.focus_paused = False
        self.game.reset()

    def title(self):
        self.keys.clear()
        self.game.phase = 'title'

    def help(self):
        self.game.phase = 'help'

    def pause(self):
        if self.game.phase in ('combat', 'prepare'):
            self.before_pause = self.game.phase
            self.game.phase = 'pause'
            self.focus_paused = False

    def focus_lost(self):
        if self.game.phase in ('combat', 'prepare'):
            self.before_pause = self.game.phase
            self.game.phase = 'pause'
            self.focus_paused = True
        self.keys.clear()

    def resume(self):
        self.game.phase = self.before_pause
        self.focus_paused = False

    def focus_gained(self):
        if self.focus_paused:
            self.resume()

    def key_down(self, key):
        if key in self.keys:
            return
        self.keys.add(key)
        phase = self.game.phase
        if phase == 'title':
            if key in ('enter', 'space'):
                self.start()
            elif key == 'h':
                self.help()
        elif phase == 'help' and key in ('escape', 'enter'):
            self.title()
        elif phase in ('combat', 'prepare'):
            if key == 'escape':
                self.pause()
            elif phase == 'prepare':
                if key == 'enter':
                    self.game.advance_wave()
                elif key == 'r':
                    self.game.repair()
                elif key == 'u':
                    self.game.upgrade_tower()
                elif key == 'tab':
                    self.game.selected_pad = (self.game.selected_pad + 1) % len(PADS)
                elif key in ('1', '2', '3'):
                    self.game.build(int(key) - 1)
        elif phase == 'upgrade' and key in ('1', '2', '3'):
            self.game.choose_upgrade(int(key) - 1)
        elif phase == 'pause':
            if key in ('escape', 'enter'):
                self.resume()
            elif key == 'r':
                self.start()
        elif phase in ('win', 'loss'):
            if key in ('r', 'enter'):
                self.start()
            elif key == 'escape':
                self.title()

    def key_up(self, key):
        self.keys.discard(key)

    def click(self, x, y):
        if self.drawn_phase != self.game.phase:
            return
        for button in reversed(self.buttons):
            if inside(x, y, button.bounds):
                button.action()
                return
        if self.game.phase == 'prepare':
            for index, (px, py) in enumerate(PADS):
                if distance(x, y, px, py) <= 30:
                    self.game.selected_pad = index
                    return

    def tick(self, dt, movement_keys=None):
        keys = self.keys
        if movement_keys is not None:
            keys = self.keys | set(movement_keys)
        dx = int(bool(keys & {'right', 'd'})) - int(bool(keys & {'left', 'a'}))
        dy = int(bool(keys & {'down', 's'})) - int(bool(keys & {'up', 'w'}))
        self.game.update(min(dt, 0.05), dx, dy)

    def draw_field(self):
        draw = self.canvas
        draw.rect(*FIELD, '#132931', outline='#38535d')
        draw.image('field', FIELD[0] + 1, FIELD[1] + 1)
        for entry in ENTRANCES:
            draw.line(entry, BASE, '#506662', width=2)
            draw.circle(*entry, 8, '#422e36', outline='#9e5455')
        draw.circle(*BASE, 108, '#1c373a')
        draw.circle(*BASE, 75, '#203e43', outline='#4b7275', width=2)
        draw.rect(365, 344, 120, 63, '#314958', outline='#556f7c')
        draw.rect(365, 389, 120, 16, '#6f8895')
        for x in (376, 395, 445, 464):
            draw.rect(x, 349, 9, 39, '#a0bbc4')
        draw.rect(413, 359, 25, 30, '#172a38')
        draw.polygon(((356, 346), (425, 316), (494, 346)), '#a67364', outline='#d4a28a')
        draw.rect(361, 405, 128, 6, '#8ba3ad')
        draw.rect(356, 411, 138, 5, '#526c7b')
        self.label(425, 434, '清大大禮堂', 'NTHU AUDITORIUM', 13, '#c8e4e6', 'center')
        for index, (x, y) in enumerate(PADS):
            tower = self.game.towers[index]
            selected = self.game.phase == 'prepare' and index == self.game.selected_pad
            draw.circle(x, y, 26, '#233d45', outline=BLUE if selected else '#54727c', width=2)
            if tower is None:
                self.text(x, y, str(index + 1), 17, BLUE if selected else MUTED, 'center')
            else:
                defense = DEFENSES[tower.kind]
                draw.rect(x - 11, y - 9, 22, 20, defense.color, outline=TEXT if tower.upgraded else None)
                draw.line((x, y), (x + 12, y - 13), defense.color, width=6)
                if tower.upgraded:
                    draw.circle(x, y + 16, 3, TEXT)

    def draw_entities(self):
        draw, game = self.canvas, self.game
        for drop in game.drops:
            x, y = drop.x, drop.y
            if drop.energy:
                draw.polygon(((x, y - 6), (x + 5, y), (x, y + 6), (x - 5, y)), PURPLE)
            else:
                draw.rect(x - 4, y - 4, 8, 8, GOLD, outline='#ffe3aa')
        for enemy in game.enemies:
            kind = ENEMY_KINDS[enemy.kind]
            x, y, radius = enemy.x, enemy.y, kind.radius
            if enemy.slowed:
                draw.circle(x, y, radius + 4, '#427085', outline=BLUE)
            draw.circle(x, y, radius, '#63323c', outline=kind.color, width=2)
            art = 'bear' if enemy.kind == 0 else 'runner'
            sprite_top = draw.sprite(art, x, y + 6)
            if enemy.hp < enemy.max_hp:
                self.bar(x - 13, sprite_top - 5, 26, 3, enemy.hp / enemy.max_hp, RED)
        for shot in game.shots:
            draw.line(shot.origin, shot.target, shot.color, width=2)
            draw.circle(*shot.target, 4, shot.color)
        x, y = game.player_x, game.player_y
        if game.hurt_wait <= 0 or int(game.hurt_wait * 24) % 2 == 0:
            draw.circle(x, y, 15, '#224e68', outline=BLUE, width=2)
            draw.sprite('defender', x, y + 7)

    def bar(self, x, y, width, height, fraction, color):
        self.canvas.rect(x, y, width, height, '#0b1923')
        filled = int(width * min(1.0, max(0.0, fraction)))
        if filled:
            self.canvas.rect(x, y, filled, height, color)

    def draw_hud(self):
        draw, game = self.canvas, self.game
        draw.rect(20, 18, 1112, 72, PANEL, outline=BORDER)
        self.label(37, 42, '大禮堂防衛戰', 'AUDITORIUM DEFENSE', 22)
        self.label(38, 68, '國立清華大學', 'NATIONAL TSING HUA UNIVERSITY', 12, MUTED)
        self.label(338, 39, '守衛生命', 'DEFENDER HP', 14, BLUE)
        self.text(510, 39, f'{game.player_hp} / {game.max_player_hp}', 15, TEXT, 'e')
        self.bar(338, 59, 172, 8, game.player_hp / game.max_player_hp, BLUE)
        self.label(548, 39, '禮堂耐久', 'AUDITORIUM HP', 14, GREEN)
        self.text(742, 39, f'{game.base_hp} / {MAX_BASE_HP}', 15, TEXT, 'e')
        self.bar(548, 59, 194, 8, game.base_hp / MAX_BASE_HP, GREEN)
        self.label(783, 39, '波次', 'WAVE', 14, MUTED)
        self.text(783, 65, f'{game.wave + 1} / {len(WAVES)}', 20)
        self.label(907, 39, '零件', 'PARTS', 14, GOLD)
        self.text(907, 65, str(game.parts), 20, GOLD)
        self.label(1019, 39, '能量', 'ENERGY', 14, PURPLE)
        self.text(1019, 65, str(game.energy), 20, PURPLE)

    def draw_side(self):
        draw, game = self.canvas, self.game
        draw.rect(*SIDE, PANEL, outline=BORDER)
        self.label(868, 135, '戰況', 'STATUS', 15, MUTED)
        if game.phase == 'prepare' or (game.phase == 'pause' and self.before_pause == 'prepare'):
            self.draw_preparation()
            return
        left = len(WAVES[game.wave]) - game.spawned + len(game.enemies)
        self.label(868, 172, f'第 {game.wave + 1} 波', f'Wave {game.wave + 1}', 28)
        self.label(868, 218, f'剩餘敵人   {left}', f'Enemies remaining   {left}', 17)
        self.label(868, 253, f'已擊倒   {game.kills}', f'Defeated   {game.kills}', 17)
        draw.line((869, 285), (1112, 285), BORDER)
        self.label(868, 318, f'等級 {game.level}', f'Level {game.level}', 20, GREEN)
        self.text(1111, 319, f'{game.xp} / {game.next_xp} XP', 15, MUTED, 'e')
        self.bar(868, 348, 244, 9, game.xp / game.next_xp, GREEN)
        self.label(868, 399, '靠近敵人時自動攻擊', 'Attacks trigger near enemies', 16, MUTED)
        self.label(868, 430, '走到掉落物旁即可拾取', 'Walk over drops to collect them', 16, MUTED)
        self.label(868, 492, '方向鍵 / WASD 移動', 'Arrow keys / WASD to move', 16)
        self.label(868, 525, 'Esc 暫停', 'Esc to pause', 16)

    def draw_preparation(self):
        game = self.game
        self.label(868, 170, '波次間備戰', 'Preparation', 27)
        self.label(868, 201, '點地圖或按 Tab 選擇建造點', 'Click a pad or use Tab to select', 14, MUTED)
        tower = game.towers[game.selected_pad]
        pad_status = self.word('空地', 'Empty') if tower is None else self.word(*DEFENSES[tower.kind].name)
        if tower is not None and tower.upgraded:
            pad_status += ' Lv.2'
        self.label(868, 233, f'建造點 {game.selected_pad + 1}   {pad_status}',
                   f'Pad {game.selected_pad + 1}   {pad_status}', 16, BLUE)
        for index, defense in enumerate(DEFENSES):
            y = 255 + index * 66
            cost = defense.cost
            zh, en = defense.name
            self.button(868, y, 246, 36, (f'{index + 1}  {zh}   {cost[0]} 零件 / {cost[1]} 能量',
                                           f'{index + 1}  {en}   {cost[0]}P / {cost[1]}E'),
                        lambda kind=index: game.build(kind), defense.color)
            self.label(878, y + 49, *defense.description, 13, MUTED)
        self.button(868, 458, 246, 37, ('R  修理禮堂   4 零件', 'R  Repair auditorium   4P'), game.repair)
        self.button(868, 503, 246, 37, ('U  升級選取的塔   5 零件 / 2 能量', 'U  Upgrade selected tower   5P / 2E'),
                    game.upgrade_tower)
        self.button(868, 575, 246, 45, ('Enter  開始下一波', 'Enter  Start next wave'), game.advance_wave, GREEN, True)

    def overlay(self, x, y, width, height):
        self.buttons.clear()
        self.canvas.rect(x + 7, y + 8, width, height, '#09121b')
        self.canvas.rect(x, y, width, height, '#172a3a', outline='#52788b', line_width=2)

    def draw_title(self):
        self.overlay(308, 171, 536, 365)
        self.label(576, 195, '國立清華大學', 'NATIONAL TSING HUA UNIVERSITY', 15, BLUE, 'center')
        self.canvas.image('title', 328, 213)
        self.label(576, 369, '大禮堂防衛戰', 'Auditorium Defense', 42, TEXT, 'center')
        self.label(576, 413, '收集資源、配置防禦塔，守住三波敵襲。',
                   'Collect resources and protect the base for three waves.', 17, MUTED, 'center')
        self.button(378, 438, 190, 48, ('Enter  開始遊戲', 'Enter  Start'), self.start, BLUE, True)
        self.button(584, 438, 190, 48, ('H  操作說明', 'H  Controls'), self.help)

    def draw_help(self):
        self.overlay(289, 168, 574, 382)
        self.label(326, 217, '操作說明', 'How to play', 30)
        rows = (
            ('方向鍵或 WASD 移動，附近有敵人時自動攻擊。', 'Move with the arrow keys or WASD. Attacks are automatic.'),
            ('走近零件和能量即可拾取。升級用 1、2、3 三選一。', 'Walk over drops to collect them. Pick an upgrade with 1–3.'),
            ('波次間按 Tab 選建造點，按 1、2、3 選塔種。', 'Between waves, Tab selects a pad and 1–3 builds a tower.'),
            ('按 R 修禮堂、按 U 升級塔、按 Enter 開始下一波。', 'R repairs, U upgrades the tower, and Enter starts a wave.'),
            ('守衛和禮堂都撐過第三波，就能獲勝。', 'Win by keeping the defender and auditorium alive for three waves.'),
        )
        for index, row in enumerate(rows):
            self.label(326, 270 + index * 36, *row, 16, MUTED)
        self.button(469, 468, 215, 44, ('Esc  回標題', 'Esc  Back to title'), self.title)

    def draw_upgrade(self):
        self.overlay(230, 252, 692, 222)
        self.label(576, 294, '角色升級', 'Level up', 29, GREEN, 'center')
        self.label(576, 335, '選擇一項強化後繼續戰鬥', 'Choose an upgrade to resume combat', 16, MUTED, 'center')
        for index, (title, details, color) in enumerate(UPGRADES):
            x = 251 + 221 * index
            self.button(x, 370, 208, 40, (f'{index + 1}  {title[0]}', f'{index + 1}  {title[1]}'),
                        lambda choice=index: self.game.choose_upgrade(choice), color)
            self.label(x + 104, 434, *details, 15, color, 'center')

    def draw_result(self, victory):
        game = self.game
        self.overlay(307, 213, 538, 294)
        if victory:
            self.label(576, 271, '防守成功', 'Auditorium secured', 35, GREEN, 'center')
            self.label(576, 321, '成功守住第三波的最後一名敵人。', 'All three waves defeated.', 17, MUTED, 'center')
        else:
            self.label(576, 271, '防守失敗', 'Defense failed', 35, RED, 'center')
            self.label(576, 321, *game.loss_reason, 17, MUTED, 'center')
        elapsed = int(game.elapsed)
        self.label(576, 372, f'擊倒 {game.kills} 隻    戰鬥時間 {elapsed // 60}:{elapsed % 60:02d}',
                   f'{game.kills} defeated    Combat time {elapsed // 60}:{elapsed % 60:02d}', 17, TEXT, 'center')
        self.button(368, 425, 200, 46, ('R  再玩一局', 'R  Play again'), self.start, BLUE, True)
        self.button(584, 425, 200, 46, ('Esc  回標題', 'Esc  Back to title'), self.title)

    def draw(self):
        game = self.game
        self.drawn_phase = game.phase
        self.buttons.clear()
        self.canvas.clear(BG)
        self.draw_field()
        self.draw_entities()
        self.draw_hud()
        self.draw_side()
        if game.notice_left > 0 and game.phase in ('combat', 'prepare'):
            self.label(23, 690, *game.notice, 16, GOLD)
        elif game.phase in ('combat', 'prepare'):
            self.label(23, 690, '藍圈標記守衛，紅圈和橘圈標記敵人。',
                       'Blue ring marks the defender. Red and orange rings mark enemies.', 14, MUTED)
        if game.phase == 'title':
            self.draw_title()
        elif game.phase == 'help':
            self.draw_help()
        elif game.phase == 'upgrade':
            self.draw_upgrade()
        elif game.phase == 'pause':
            self.overlay(311, 249, 530, 226)
            self.label(576, 307, '已暫停', 'Paused', 34, TEXT, 'center')
            self.button(341, 389, 150, 44, ('Enter  繼續', 'Enter  Resume'), self.resume, BLUE, True)
            self.button(501, 389, 150, 44, ('R  重新開始', 'R  Restart'), self.start)
            self.button(661, 389, 150, 44, ('回標題', 'Title'), self.title)
        elif game.phase in ('win', 'loss'):
            self.draw_result(game.phase == 'win')
