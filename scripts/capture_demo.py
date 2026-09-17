"""Capture actual game rendering using synthetic mouse events, not mock images.

This is automated demonstration evidence, not a claim of personal playtesting.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from PIL import Image
from arrow_game.app import App
from arrow_game.core import solve

output = ROOT / "docs/images"
output.mkdir(parents=True, exist_ok=True)
app = App()
frames, durations = [], []


def frame(duration=80):
    app.render()
    image = Image.frombytes("RGB", app.screen.get_size(), pygame.image.tobytes(app.screen, "RGB"))
    frames.append(image.resize((840, 585), Image.Resampling.LANCZOS).convert("P", palette=Image.Palette.ADAPTIVE, colors=96))
    durations.append(duration)


def shot(name):
    app.render()
    pygame.image.save(app.screen, str(output / f"{name}.png"))


def click(point):
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=point, button=1))


def button(key):
    rect = next(rect for name, rect, *_ in app.button_specs() if name == key)
    click(rect.center)


def animate(record=True):
    while app.animation:
        app.update(.07)
        if record:
            frame(70)


shot("01-start")
frame(1600)
button("start")
shot("02-game")
frame(1600)
blocked = next(p for p in app.game.board.arrows if not app.game.board.can_exit(p))
click(app.cell_center(blocked))
app.update(.12)
shot("03-collision")
frame(700)
animate()
frame(800)
button("hint")
shot("04-hint")
frame(1200)
for position in solve(app.game.board):
    click(app.cell_center(position))
    animate()
shot("05-win")
frame(2000)
button("next")
shot("06-level2")
frame(1300)
for position in solve(app.game.board):
    click(app.cell_center(position))
    animate(False)
button("next")
shot("07-level3")
for position in solve(app.game.board):
    click(app.cell_center(position))
    animate(False)
shot("08-final")
button("menu")
button("level:0")
blocked = next(p for p in app.game.board.arrows if not app.game.board.can_exit(p))
for _ in range(3):
    click(app.cell_center(blocked))
    animate()
shot("09-fail")
frame(1900)
button("restart")
frame(900)
frames[0].save(output / "demo.gif", save_all=True, append_images=frames[1:],
               duration=durations, loop=0, optimize=False, disposal=2)
pygame.quit()
print(f"Saved {len(frames)} real rendered frames and 9 screenshots to {output}")
