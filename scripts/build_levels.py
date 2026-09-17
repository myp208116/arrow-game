"""Regenerate our original, deterministic level data and solution evidence."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from arrow_game.core import Direction, solve
from arrow_game.levels import generate

specs = [(5, 12, 19, "初见", "先找朝向边缘的箭头"),
         (6, 24, 43, "交错", "让一条路，为另一条路让行"),
         (7, 38, 82, "回响", "耐心观察，拆开层层阻挡")]
levels, evidence = [], []
for size, count, seed, name, subtitle in specs:
    # Prefer a layout with fewer initial exits while retaining all four directions.
    candidates = [(s, generate(size, size, count, s)) for s in range(seed, seed + 40)]
    candidates = [(s, b) for s, b in candidates
                  if {a.direction for a in b.arrows.values()} == set(Direction)]
    seed, board = min(candidates, key=lambda pair: len(pair[1].available()))
    levels.append(dict(name=name, subtitle=subtitle, rows=size, cols=size, seed=seed,
                       arrows=[[a.row, a.col, a.direction.name]
                               for a in board.arrows.values()]))
    evidence.append(dict(level=name, arrows=count, initial_exits=len(board.available()),
                         solution_1_based=[[r + 1, c + 1] for r, c in solve(board)]))
(ROOT / "arrow_game/levels.json").write_text(
    json.dumps(levels, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "docs/solutions.json").write_text(
    json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(evidence, ensure_ascii=False, indent=2))
