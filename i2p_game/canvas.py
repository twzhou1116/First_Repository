"""Pygame and Tkinter drawing adapters."""

from pathlib import Path
from .artwork import ARTWORK_FILES, SPRITE_DOWNSAMPLE, SPRITE_SIZES

class PygameCanvas:
    def __init__(self, pygame, screen):
        self.pg, self.screen = pygame, screen

        self.art = {
            name: pygame.image.load(str(path)).convert_alpha()
            for name, path in ARTWORK_FILES.items()
        }
        for name, size in SPRITE_SIZES.items():
            self.art[name] = pygame.transform.smoothscale(self.art[name], size)

        self.font_file = (
            Path(__file__).resolve().parent.parent
            / 'assets'
            / 'fonts'
            / 'NotoSansTC.ttf'
        )

        if not self.font_file.is_file():
            raise FileNotFoundError(
                f'找不到中文字型：{self.font_file}'
            )

        self.font_file = str(self.font_file)
        self.chinese = True
        self.fonts = {}

        # 測試字型能否正常渲染中文字
        test_font = pygame.font.Font(self.font_file, 20)
        test_surface = test_font.render(
            "清大大禮堂", True, (255, 255, 255)
        )
        print("Font test successful:", test_surface.get_size())

    def clear(self, color):
        self.screen.fill(color)

    def image(self, name, x, y):
        self.screen.blit(self.art[name], (int(x), int(y)))

    def sprite(self, name, x, foot_y):
        width, height = self.art[name].get_size()
        top = foot_y - height
        self.image(name, x - width / 2, top)
        return top

    def rect(self, x, y, width, height, color, outline=None, line_width=1):
        bounds = self.pg.Rect(int(x), int(y), int(width), int(height))
        self.pg.draw.rect(self.screen, color, bounds)
        if outline:
            self.pg.draw.rect(self.screen, outline, bounds, line_width)

    def circle(self, x, y, radius, color, outline=None, width=1):
        center = int(x), int(y)
        self.pg.draw.circle(self.screen, color, center, int(radius))
        if outline:
            self.pg.draw.circle(self.screen, outline, center, int(radius), width)

    def line(self, start, end, color, width=1):
        self.pg.draw.line(self.screen, color, start, end, width)

    def polygon(self, points, color, outline=None):
        self.pg.draw.polygon(self.screen, color, points)
        if outline:
            self.pg.draw.polygon(self.screen, outline, points, 1)

    def text(self, x, y, value, size, color, anchor):
        if size not in self.fonts:
            self.fonts[size] = self.pg.font.Font(self.font_file, size)

        surface = self.fonts[size].render(value, True, color)
        box = surface.get_rect()
        setattr(
            box,
            {'w': 'midleft', 'e': 'midright', 'center': 'center'}[anchor],
            (int(x), int(y))
        )
        self.screen.blit(surface, box)


class TkCanvas:
    def __init__(self, canvas, families):
        from tkinter import PhotoImage

        self.canvas = canvas
        self.art = {}
        for name, path in ARTWORK_FILES.items():
            image = PhotoImage(master=canvas, file=str(path))
            downsample = SPRITE_DOWNSAMPLE.get(name)
            if downsample:
                image = image.subsample(downsample, downsample)
            self.art[name] = image
        available = set(families)
        preferred = ('Microsoft JhengHei UI', 'Microsoft JhengHei', 'PingFang TC', 'Noto Sans CJK TC', 'WenQuanYi Zen Hei')
        self.family = next((name for name in preferred if name in available), None)
        self.chinese = self.family is not None
        if not self.family:
            self.family = 'TkDefaultFont'

    def clear(self, color):
        self.canvas.delete('all')
        self.canvas.configure(background=color)

    def image(self, name, x, y):
        self.canvas.create_image(x, y, image=self.art[name], anchor='nw')

    def sprite(self, name, x, foot_y):
        art = self.art[name]
        top = foot_y - art.height()
        self.image(name, x - art.width() / 2, top)
        return top

    def rect(self, x, y, width, height, color, outline=None, line_width=1):
        self.canvas.create_rectangle(x, y, x + width, y + height, fill=color, outline=outline or '', width=line_width)

    def circle(self, x, y, radius, color, outline=None, width=1):
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color,
                                outline=outline or '', width=width)

    def line(self, start, end, color, width=1):
        self.canvas.create_line(*start, *end, fill=color, width=width)

    def polygon(self, points, color, outline=None):
        coords = [coord for point in points for coord in point]
        self.canvas.create_polygon(*coords, fill=color, outline=outline or '')

    def text(self, x, y, value, size, color, anchor):
        self.canvas.create_text(x, y, text=value, anchor=anchor, fill=color, font=(self.family, -size))
