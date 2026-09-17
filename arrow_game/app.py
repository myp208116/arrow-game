"""Pygame interface. All visuals are drawn here; no external art is used."""
import math
import os
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame

from .core import Direction, Game
from .levels import load_levels

WIDTH, HEIGHT = 1120, 780
BG = "#F2F4ED"
INK = "#193C36"
MUTED = "#6A7E76"
GREEN = "#20775B"
MINT = "#DEEDDF"
WHITE = "#FFFFFF"
LINE = "#DCE3D8"
RED = "#BA5043"
GOLD = "#C49542"
COLORS = {Direction.UP: "#287961", Direction.DOWN: "#346A88",
          Direction.LEFT: "#BB8840", Direction.RIGHT: "#344F48"}


@dataclass
class Animation:
    position: tuple
    kind: str
    blocker: tuple | None
    elapsed: float = 0.0

    @property
    def duration(self):
        return 0.38 if self.kind == "fly" else 0.42


class App:
    def __init__(self):
        pygame.display.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("一箭又一箭 · 杜玉鹤 162404109")
        self.font_path = self.find_font()
        self.fonts = {}
        self.levels = load_levels()
        self.scene = "menu"
        self.level_index = 0
        self.game = None
        self.animation = None
        self.hint_position = None
        self.hint_time = 0
        self.feedback = "观察前方，再点一下。"
        self.feedback_kind = "normal"
        self.mouse = (-1, -1)
        self.running = True
        self.paused = False
        self.best = {}
        self.clock = pygame.time.Clock()

    @staticmethod
    def find_font():
        candidates = [Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts/msyh.ttc",
                      Path("/System/Library/Fonts/PingFang.ttc"),
                      Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")]
        for path in candidates:
            if path.is_file():
                return str(path)
        return pygame.font.match_font("microsoftyahei,pingfangsc,notosanscjk,simhei")

    def font(self, size, bold=False):
        key = size, bold
        if key not in self.fonts:
            font = pygame.font.Font(self.font_path, size)
            font.set_bold(bold)
            self.fonts[key] = font
        return self.fonts[key]

    def text(self, content, x, y, size=18, color=INK, bold=False, center=False):
        rendered = self.font(size, bold).render(str(content), True, color)
        rect = rendered.get_rect()
        if center:
            rect.midtop = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(rendered, rect)
        return rect

    def panel(self, rect, color=WHITE, radius=18, outline=None):
        pygame.draw.rect(self.screen, color, rect, border_radius=radius)
        if outline:
            pygame.draw.rect(self.screen, outline, rect, width=1, border_radius=radius)

    def arrow(self, center, direction, color, size=24):
        dr, dc = direction.value
        dx, dy = dc, dr
        px, py = -dy, dx
        cx, cy = center
        # Seven-point polygon, with a shaft and a clear triangular arrowhead.
        points = [(-0.75, -0.16), (0.08, -0.16), (0.08, -0.48),
                  (0.75, 0), (0.08, 0.48), (0.08, 0.16), (-0.75, 0.16)]
        vertices = [(cx + size * (a * dx + b * px), cy + size * (a * dy + b * py))
                    for a, b in points]
        pygame.draw.polygon(self.screen, color, vertices)
        pygame.draw.aalines(self.screen, color, True, vertices)

    def star(self, center, radius, color):
        points = []
        for i in range(10):
            angle = -math.pi / 2 + i * math.pi / 5
            r = radius if i % 2 == 0 else radius * .44
            points.append((center[0] + math.cos(angle) * r,
                           center[1] + math.sin(angle) * r))
        pygame.draw.polygon(self.screen, color, points)
        pygame.draw.aalines(self.screen, color, True, points)

    def button_specs(self):
        if self.scene == "menu":
            return [("start", pygame.Rect(64, 378, 242, 54), "开始第一关", True),
                    *[(f"level:{i}", pygame.Rect(64 + i * 338, 578, 316, 108),
                       level["name"], False) for i, level in enumerate(self.levels)]]
        if self.scene == "result":
            is_win = self.game.status == "won"
            has_next = self.level_index + 1 < len(self.levels)
            main = "next" if is_win and has_next else "restart"
            label = "进入下一关" if main == "next" else "再玩这一关"
            return [(main, pygame.Rect(376, 486, 368, 48), label, True),
                    ("menu", pygame.Rect(376, 550, 368, 40), "返回关卡选择", False)]
        if self.paused:
            return [("resume", pygame.Rect(432, 430, 256, 48), "继续游戏", True)]
        return [("restart", pygame.Rect(48, 704, 174, 44), "重新开始  R", False),
                ("menu", pygame.Rect(240, 704, 174, 44), "返回首页  Esc", False),
                ("hint", pygame.Rect(778, 584, 264, 52), "给我一个提示  H", True)]

    def draw_button(self, key, rect, label, primary):
        hovered = rect.collidepoint(self.mouse)
        color = ("#185E49" if hovered else GREEN) if primary else ("#E2EADA" if hovered else WHITE)
        self.panel(rect, color, 12, None if primary else LINE)
        self.text(label, rect.centerx, rect.y + (rect.h - 26) / 2,
                  18, WHITE if primary else INK, center=True)

    def start_level(self, index):
        self.level_index = index
        self.game = Game(self.levels[index]["board"])
        self.scene = "playing"
        self.animation = None
        self.hint_position = None
        self.hint_time = 0
        self.paused = False
        self.feedback = "观察前方，再点一下。"
        self.feedback_kind = "normal"

    def activate(self, key):
        if key == "start":
            self.start_level(0)
        elif key.startswith("level:"):
            self.start_level(int(key.split(":")[1]))
        elif key == "menu":
            self.scene = "menu"
            self.animation = None
            self.paused = False
        elif key == "restart":
            self.start_level(self.level_index)
        elif key == "next" and self.level_index + 1 < len(self.levels):
            self.start_level(self.level_index + 1)
        elif key == "resume":
            self.paused = False
        elif key == "hint" and self.scene == "playing" and not self.animation:
            moves = self.game.board.available()
            if moves:
                # Repeated presses while the same hint is visible count only once.
                if self.hint_time <= 0:
                    self.game.hints += 1
                self.hint_position = moves[0]
                self.hint_time = 3.0
                self.feedback = "金色标记的箭头可以先离开。"
                self.feedback_kind = "hint"

    def grid_geometry(self):
        board = self.game.board
        cell = 448 / max(board.rows, board.cols)
        rect = pygame.Rect(384 - board.cols * cell / 2,
                           414 - board.rows * cell / 2,
                           board.cols * cell, board.rows * cell)
        return rect, cell

    def cell_center(self, position):
        rect, cell = self.grid_geometry()
        row, col = position
        return rect.x + (col + .5) * cell, rect.y + (row + .5) * cell

    def cell_at(self, point):
        rect, cell = self.grid_geometry()
        if not rect.collidepoint(point):
            return None
        position = int((point[1] - rect.y) / cell), int((point[0] - rect.x) / cell)
        return position if self.game.board.inside(*position) else None

    def click_arrow(self, position):
        if self.scene != "playing" or self.paused or self.animation:
            return
        if position not in self.game.board.arrows:
            return
        blocker = self.game.board.blocker(position)
        self.animation = Animation(position, "fly" if blocker is None else "bump", blocker)
        self.hint_position = None
        self.hint_time = 0
        if blocker is not None:
            self.feedback = "前方被挡住了，换个顺序试试。"
            self.feedback_kind = "blocked"
        else:
            self.feedback = "路通了，这一箭顺利出发。"
            self.feedback_kind = "normal"

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.WINDOWFOCUSLOST and self.scene == "playing":
            self.paused = True
        elif event.type == pygame.MOUSEMOTION:
            self.mouse = event.pos
        elif event.type == pygame.KEYDOWN:
            if self.paused:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self.activate("resume")
            elif event.key == pygame.K_ESCAPE:
                self.activate("menu")
            elif event.key == pygame.K_r and self.scene in ("playing", "result"):
                self.activate("restart")
            elif event.key == pygame.K_h and self.scene == "playing":
                self.activate("hint")
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN) and self.scene == "menu":
                self.activate("start")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.mouse = event.pos
            for key, rect, _, _ in self.button_specs():
                if rect.collidepoint(event.pos):
                    self.activate(key)
                    return
            if self.scene == "playing" and not self.paused:
                self.click_arrow(self.cell_at(event.pos))

    def update(self, dt):
        if self.scene != "playing" or self.paused:
            return
        self.game.elapsed += dt
        self.hint_time = max(0, self.hint_time - dt)
        if self.hint_time == 0:
            self.hint_position = None
        if self.animation:
            self.animation.elapsed += dt
            if self.animation.elapsed >= self.animation.duration:
                self.game.attempt(self.animation.position)
                self.animation = None
                if self.game.status in ("won", "lost"):
                    self.scene = "result"
                    if self.game.status == "won":
                        self.best[self.level_index] = max(self.best.get(self.level_index, 0),
                                                          self.game.stars)

    def header(self):
        self.panel(pygame.Rect(48, 27, 44, 44), GREEN, 12)
        self.arrow((70, 49), Direction.RIGHT, WHITE, 26)
        self.text("一箭又一箭", 106, 25, 25, bold=True)
        self.text("ARROW AFTER ARROW", 107, 57, 10, MUTED)
        self.text("杜玉鹤  /  162404109", 848, 39, 16, MUTED)
        pygame.draw.line(self.screen, LINE, (48, 92), (1072, 92))

    def draw_menu(self):
        self.text("A LITTLE DIRECTION. A LITTLE PATIENCE.", 66, 153, 13, GREEN, True)
        self.text("顺着方向，", 61, 192, 53, bold=True)
        self.text("找到出口。", 61, 259, 53, bold=True)
        self.text("点击箭头，让它沿着自己的方向离开。", 65, 340, 19, MUTED)
        self.text("前方有阻挡？先为它腾出一条路。", 65, 450, 16, MUTED)
        self.panel(pygame.Rect(667, 135, 405, 370), "#E3EBDD", 26)
        demo = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.UP,
                Direction.LEFT, Direction.DOWN, Direction.RIGHT, Direction.RIGHT,
                Direction.DOWN, Direction.LEFT, Direction.UP, Direction.UP,
                Direction.RIGHT, Direction.UP, Direction.LEFT, Direction.RIGHT]
        for i, direction in enumerate(demo):
            row, col = divmod(i, 4)
            x, y = 708 + col * 86, 165 + row * 79
            color = WHITE if i != 7 else GREEN
            self.panel(pygame.Rect(x, y, 64, 62), color, 14)
            self.arrow((x + 32, y + 31), direction,
                       WHITE if i == 7 else COLORS[direction], 32)
        self.text("从一箭开始。", 869, 458, 15, MUTED, center=True)
        self.text("选择你的节奏", 64, 535, 20, bold=True)
        self.text("3 个关卡  ·  每关 3 次机会  ·  所有关卡均可直接选择", 566, 540, 14, MUTED)
        for key, rect, label, primary in self.button_specs():
            if not key.startswith("level:"):
                self.draw_button(key, rect, label, primary)
                continue
            index = int(key.split(":")[1])
            level = self.levels[index]
            self.panel(rect, "#E6EEE1" if rect.collidepoint(self.mouse) else WHITE, 16, LINE)
            self.text(f"0{index + 1}", rect.x + 22, rect.y + 18, 32, GREEN, True)
            self.text(label, rect.x + 86, rect.y + 19, 24, bold=True)
            self.text(f"{level['rows']} × {level['cols']}  /  {len(level['board'].arrows)} 枚箭头",
                      rect.x + 86, rect.y + 61, 15, MUTED)
            if index in self.best:
                self.star((rect.right - 28, rect.y + 34), 9, GOLD)
        self.text("鼠标点击操作   /   H 提示   /   R 重开   /   Esc 返回", 64, 722, 13, MUTED)
        self.text("SOFTWARE ENGINEERING  ·  02", 795, 722, 11, MUTED)

    def draw_board(self):
        self.panel(pygame.Rect(48, 158, 672, 520), WHITE, 20, LINE)
        grid, cell = self.grid_geometry()
        board = self.game.board
        hover = self.cell_at(self.mouse)
        for row in range(board.rows):
            for col in range(board.cols):
                x, y = self.cell_center((row, col))
                pygame.draw.circle(self.screen, "#DCE6DA", (x, y), 2)
        # Tiny labels make the saved solution sequence easy to follow.
        for col in range(board.cols):
            self.text(col + 1, grid.x + (col + .5) * cell, grid.y - 24, 11, MUTED, center=True)
        for row in range(board.rows):
            self.text(row + 1, grid.x - 21, grid.y + (row + .5) * cell - 8, 11, MUTED)
        self.screen.set_clip(pygame.Rect(55, 162, 658, 510))
        for position, arrow in board.arrows.items():
            x, y = self.cell_center(position)
            color = COLORS[arrow.direction]
            selected = self.animation and position == self.animation.position
            if hover == position and not self.animation and self.scene == "playing":
                self.panel(pygame.Rect(x - cell * .4, y - cell * .4, cell * .8, cell * .8),
                           "#EDF3E7", 12)
            if self.hint_position == position:
                self.panel(pygame.Rect(x - cell * .39, y - cell * .39, cell * .78, cell * .78),
                           "#FBEDC9", 12, GOLD)
            if self.animation and position == self.animation.blocker:
                self.panel(pygame.Rect(x - cell * .38, y - cell * .38, cell * .76, cell * .76),
                           "#F9E6DF", 12)
            if selected:
                progress = min(1, self.animation.elapsed / self.animation.duration)
                dr, dc = arrow.direction.value
                if self.animation.kind == "fly":
                    distance = 800 * progress ** 1.5
                    x, y = x + dc * distance, y + dr * distance
                    color = GREEN
                else:
                    offset = math.sin(progress * math.pi * 4) * (1 - progress) * cell * .16
                    x, y = x + dc * offset, y + dr * offset
                    color = RED
            self.arrow((x, y), arrow.direction, color, cell * .47)
        self.screen.set_clip(None)
        self.text("先观察，再出发。", 384, 649, 13, MUTED, center=True)

    def draw_playing(self):
        level = self.levels[self.level_index]
        self.text(f"第 {self.level_index + 1} 关  /  {level['name']}", 48, 108, 24, bold=True)
        self.text(level["subtitle"], 758, 117, 16, MUTED)
        self.draw_board()
        self.panel(pygame.Rect(748, 158, 324, 520), INK, 20)
        self.text("给每一箭，留一条路。", 778, 184, 21, WHITE, True)
        self.text("REMAINING", 779, 237, 11, "#AFC6B8")
        self.text(f"{len(self.game.board.arrows):02}", 776, 258, 66, WHITE, True)
        self.text(f"/ {len(self.game.initial.arrows)} 枚箭头", 879, 299, 16, "#B9CCBD")
        total = len(self.game.initial.arrows)
        self.panel(pygame.Rect(779, 350, 262, 5), "#35584B", 2)
        cleared = total - len(self.game.board.arrows)
        if cleared:
            self.panel(pygame.Rect(779, 350, 262 * cleared / total, 5), "#C8DA7C", 2)
        self.text("剩余机会", 779, 382, 16, "#B9CCBD")
        for i in range(3):
            x = 952 + i * 32
            pygame.draw.circle(self.screen, "#D6E597" if i < self.game.lives else "#426052", (x, 395), 10)
        minutes, seconds = divmod(int(self.game.elapsed), 60)
        self.text("本关用时", 779, 427, 16, "#B9CCBD")
        self.text(f"{minutes:02}:{seconds:02}", 966, 424, 22, WHITE)
        pygame.draw.line(self.screen, "#35584B", (779, 468), (1041, 468))
        self.text("前方畅通，才能离开。", 779, 489, 17, WHITE)
        self.text("碰撞会消耗 1 次机会。", 779, 520, 16, "#B9CCBD")
        self.text("提示不扣机会，会影响星级评价。", 779, 647, 12, "#B9CCBD")
        self.text(self.feedback, 462, 718, 16,
                  RED if self.feedback_kind == "blocked" else MUTED)
        if self.scene == "playing" and not self.paused:
            for spec in self.button_specs():
                self.draw_button(*spec)

    def dim(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((13, 38, 29, 145))
        self.screen.blit(overlay, (0, 0))

    def draw_result(self):
        self.dim()
        self.panel(pygame.Rect(330, 156, 460, 466), WHITE, 26)
        win = self.game.status == "won"
        self.text("LEVEL COMPLETE" if win else "TRY ANOTHER WAY", 560, 187, 13,
                  GREEN if win else RED, True, center=True)
        if win:
            for i in range(3):
                self.star((502 + i * 58, 256), 22, GOLD if i < self.game.stars else LINE)
        else:
            self.arrow((536, 257), Direction.RIGHT, RED, 35)
            self.arrow((584, 257), Direction.LEFT, RED, 35)
        final = self.level_index == len(self.levels) - 1
        title = ("最后一关，也通了。" if final else "这一关，畅通了。") if win else "换个顺序，再来。"
        self.text(title, 560, 305, 31, bold=True, center=True)
        subtitle = "回到首页，挑战更少的失误。" if win and final else (
            "留意箭头前方的每一格。" if not win else "接下来，让更多箭头找到出口。")
        self.text(subtitle, 560, 359, 16, MUTED, center=True)
        self.text(f"用时 {self.game.elapsed:.1f} 秒   ·   失误 {3 - self.game.lives} 次   ·   提示 {self.game.hints} 次",
                  560, 412, 15, MUTED, center=True)
        for spec in self.button_specs():
            self.draw_button(*spec)

    def render(self):
        self.screen.fill(BG)
        self.header()
        if self.scene == "menu":
            self.draw_menu()
        else:
            self.draw_playing()
            if self.scene == "result":
                self.draw_result()
            elif self.paused:
                self.dim()
                self.panel(pygame.Rect(342, 266, 436, 252), WHITE, 24)
                self.text("休息一下，方向还在。", 560, 303, 28, bold=True, center=True)
                self.text("已暂停计时，点击继续。", 560, 366, 17, MUTED, center=True)
                for spec in self.button_specs():
                    self.draw_button(*spec)
        pygame.display.flip()

    def run(self, max_frames=None):
        frames = 0
        while self.running:
            dt = min(self.clock.tick(60) / 1000.0, .05)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.render()
            frames += 1
            if max_frames and frames >= max_frames:
                break
        pygame.quit()
