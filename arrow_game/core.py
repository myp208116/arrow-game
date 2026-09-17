"""Pure game rules. Coordinates are (row, column), never (x, y)."""

from dataclasses import dataclass
from enum import Enum


class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)


@dataclass(frozen=True)
class Arrow:
    row: int
    col: int
    direction: Direction

    @property
    def position(self):
        return self.row, self.col


class Board:
    def __init__(self, rows, cols, arrows):
        if rows < 1 or cols < 1:
            raise ValueError("Board dimensions must be positive")
        self.rows, self.cols = rows, cols
        self.arrows = {}
        for arrow in arrows:
            if not self.inside(*arrow.position):
                raise ValueError("Arrow outside board")
            if arrow.position in self.arrows:
                raise ValueError("Two arrows occupy the same cell")
            if not isinstance(arrow.direction, Direction):
                raise ValueError("Invalid direction")
            self.arrows[arrow.position] = arrow

    def inside(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols

    def path(self, position):
        """Cells strictly in front of an arrow, stopping before the boundary."""
        arrow = self.arrows.get(position)
        if arrow is None:
            return ()
        dr, dc = arrow.direction.value
        row, col = arrow.row + dr, arrow.col + dc
        cells = []
        while self.inside(row, col):
            cells.append((row, col))
            row, col = row + dr, col + dc
        return tuple(cells)

    def blocker(self, position):
        return next((p for p in self.path(position) if p in self.arrows), None)

    def can_exit(self, position):
        return position in self.arrows and self.blocker(position) is None

    def available(self):
        return [p for p in sorted(self.arrows) if self.can_exit(p)]

    def copy(self):
        return Board(self.rows, self.cols, self.arrows.values())


def solve(board):
    """Return a legal removal order, or None if arrows are mutually blocked.

    Removing an arrow cannot add an obstacle, so any currently legal move is safe.
    The caller's board is never changed.
    """
    working = board.copy()
    order = []
    while working.arrows:
        moves = working.available()
        if not moves:
            return None
        for position in moves:
            del working.arrows[position]
            order.append(position)
    return order


class Game:
    """Logical state. The UI commits successful moves after their animation."""
    def __init__(self, board, lives=3):
        if lives < 1:
            raise ValueError("At least one life is required")
        self.initial = board.copy()
        self.max_lives = lives
        self.restart()

    def restart(self):
        self.board = self.initial.copy()
        self.lives = self.max_lives
        self.moves = 0
        self.hints = 0
        self.elapsed = 0.0
        self.status = "playing" if self.board.arrows else "won"

    def attempt(self, position):
        if self.status != "playing" or position not in self.board.arrows:
            return "ignored"
        self.moves += 1
        if self.board.can_exit(position):
            del self.board.arrows[position]
            if not self.board.arrows:
                self.status = "won"
            return "removed"
        self.lives -= 1
        if self.lives == 0:
            self.status = "lost"
        return "blocked"

    @property
    def stars(self):
        if self.status != "won":
            return 0
        penalties = self.max_lives - self.lives + self.hints
        return max(1, 3 - penalties)
