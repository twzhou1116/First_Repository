"""Application entry points for Pygame and Tkinter."""

from .config import BG, HEIGHT, WIDTH
from .interface import Interface
from .canvas import PygameCanvas, TkCanvas
from time import perf_counter
import os

KEY_NAMES = {
    'return': 'enter',
    'kp_enter': 'enter',
    'kp enter': 'enter',
    'kp_1': '1',
    'kp_2': '2',
    'kp_3': '3',
    '[1]': '1',
    '[2]': '2',
    '[3]': '3',
}


def normalize_key(name):
    name = name.lower()
    return KEY_NAMES.get(name, name)


def run_pygame(pygame):
    pygame.display.init()
    pygame.font.init()
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('大禮堂防衛戰 | Auditorium Defense')
        clock = pygame.time.Clock()
        interface = Interface(PygameCanvas(pygame, screen))
        while True:
            dt = clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    interface.key_down(normalize_key(pygame.key.name(event.key)))
                elif event.type == pygame.KEYUP:
                    interface.key_up(normalize_key(pygame.key.name(event.key)))
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    interface.click(*event.pos)
                elif event.type == pygame.WINDOWFOCUSLOST:
                    interface.focus_lost()
            interface.pointer = pygame.mouse.get_pos()
            pressed = pygame.key.get_pressed()
            movement_keys = set()
            if pressed[pygame.K_a] or pressed[pygame.K_LEFT]:
                movement_keys.add('a')
            if pressed[pygame.K_d] or pressed[pygame.K_RIGHT]:
                movement_keys.add('d')
            if pressed[pygame.K_w] or pressed[pygame.K_UP]:
                movement_keys.add('w')
            if pressed[pygame.K_s] or pressed[pygame.K_DOWN]:
                movement_keys.add('s')
            interface.tick(dt, movement_keys)
            interface.draw()
            pygame.display.flip()
    finally:
        pygame.quit()


def run_tkinter():
    import tkinter as tk
    from tkinter import font

    root = tk.Tk()
    root.title('大禮堂防衛戰 | Auditorium Defense')
    root.resizable(False, False)
    widget = tk.Canvas(root, width=WIDTH, height=HEIGHT, highlightthickness=0, background=BG)
    widget.pack()
    interface = Interface(TkCanvas(widget, font.families(root)))
    root.bind('<KeyPress>', lambda event: interface.key_down(normalize_key(event.keysym)))
    root.bind('<KeyRelease>', lambda event: interface.key_up(normalize_key(event.keysym)))
    root.bind('<FocusOut>', lambda event: interface.focus_lost())
    widget.bind('<Button-1>', lambda event: interface.click(event.x, event.y))
    widget.bind('<Motion>', lambda event: setattr(interface, 'pointer', (event.x, event.y)))
    widget.bind('<Leave>', lambda event: setattr(interface, 'pointer', (-1, -1)))
    previous = perf_counter()

    def frame():
        nonlocal previous
        now = perf_counter()
        interface.tick(now - previous)
        interface.draw()
        previous = now
        root.after(16, frame)

    frame()
    root.mainloop()


def main():
    os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
    try:
        import pygame
    except ModuleNotFoundError as error:
        if error.name != 'pygame':
            raise
        run_tkinter()
    else:
        run_pygame(pygame)
