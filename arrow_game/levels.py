"""Reproducible level generation with a constructive solvability guarantee."""

import json
import random
from pathlib import Path

from .core import Arrow, Board, Direction, solve


def generate(rows, cols, count, seed):
    if rows < 1 or cols < 1 or not 1 <= count <= rows * cols:
        raise ValueError("Invalid board size or arrow count")
    rng = random.Random(seed)
    remaining = set(rng.sample([(r, c) for r in range(rows)
                                for c in range(cols)], count))
    arrows = []
    # Select a position/direction that can leave the *remaining* occupied cells.
    # Remember this arrow and remove it from the temporary occupancy set.
    # Replaying the construction order is therefore a valid solution.
    while remaining:
        choices = []
        for row, col in sorted(remaining):
            for direction in Direction:
                dr, dc = direction.value
                r, c = row + dr, col + dc
                while 0 <= r < rows and 0 <= c < cols:
                    if (r, c) in remaining:
                        break
                    r, c = r + dr, c + dc
                else:
                    choices.append(Arrow(row, col, direction))
        arrow = rng.choice(choices)
        arrows.append(arrow)
        remaining.remove(arrow.position)
    return Board(rows, cols, arrows)


def load_levels(path=None):
    source = Path(path) if path else Path(__file__).with_name("levels.json")
    raw = json.loads(source.read_text(encoding="utf-8"))
    levels = []
    for item in raw:
        board = Board(item["rows"], item["cols"], [
            Arrow(r, c, Direction[d]) for r, c, d in item["arrows"]])
        if not board.arrows or solve(board) is None:
            raise ValueError(f"Unsolvable or empty level: {item['name']}")
        levels.append({**item, "board": board})
    if not levels:
        raise ValueError("No levels supplied")
    return levels
