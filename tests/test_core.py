import unittest

from arrow_game.core import Arrow, Board, Direction as D, Game, solve
from arrow_game.levels import generate, load_levels


class RuleTests(unittest.TestCase):
    def test_t01_clear_path_in_all_four_directions(self):
        for direction in D:
            with self.subTest(direction=direction):
                game = Game(Board(5, 5, [Arrow(2, 2, direction)]))
                self.assertEqual(game.attempt((2, 2)), "removed")
                self.assertEqual(len(game.board.arrows), 0)
                self.assertEqual(game.lives, 3)

    def test_t02_blocker_at_distance_in_all_directions(self):
        for direction in D:
            dr, dc = direction.value
            blocker = (2 + dr * 2, 2 + dc * 2)
            game = Game(Board(5, 5, [Arrow(2, 2, direction),
                                    Arrow(*blocker, D.UP)]))
            with self.subTest(direction=direction):
                self.assertEqual(game.board.blocker((2, 2)), blocker)
                self.assertEqual(game.attempt((2, 2)), "blocked")
                self.assertEqual(game.lives, 2)
                self.assertEqual(len(game.board.arrows), 2)

    def test_t03_all_outward_edges(self):
        for row, col, direction in [(0, 2, D.UP), (4, 2, D.DOWN),
                                     (2, 0, D.LEFT), (2, 4, D.RIGHT)]:
            game = Game(Board(5, 5, [Arrow(row, col, direction)]))
            self.assertEqual(game.board.path((row, col)), ())
            self.assertEqual(game.attempt((row, col)), "removed")

    def test_t04_complete_every_shipped_level(self):
        for level in load_levels():
            game = Game(level["board"])
            for position in solve(game.board):
                self.assertEqual(game.attempt(position), "removed")
            self.assertEqual(game.status, "won")
            self.assertEqual(game.lives, 3)

    def test_t05_loss_and_restart(self):
        game = Game(Board(1, 2, [Arrow(0, 0, D.RIGHT), Arrow(0, 1, D.LEFT)]))
        for _ in range(3):
            self.assertEqual(game.attempt((0, 0)), "blocked")
        self.assertEqual(game.status, "lost")
        self.assertEqual(game.attempt((0, 0)), "ignored")
        self.assertEqual(game.lives, 0)
        game.restart()
        self.assertEqual((game.status, game.lives, len(game.board.arrows)),
                         ("playing", 3, 2))

    def test_t06_restart_restores_exact_initial_layout(self):
        board = Board(1, 2, [Arrow(0, 0, D.RIGHT), Arrow(0, 1, D.RIGHT)])
        game = Game(board)
        game.attempt((0, 0))
        game.attempt((0, 1))
        game.elapsed, game.hints = 12.0, 1
        game.restart()
        self.assertEqual(game.board.arrows, board.arrows)
        self.assertEqual((game.lives, game.moves, game.elapsed, game.hints),
                         (3, 0, 0.0, 0))

    def test_behind_and_other_rows_do_not_block(self):
        board = Board(4, 5, [Arrow(2, 2, D.RIGHT), Arrow(2, 0, D.RIGHT),
                             Arrow(1, 3, D.DOWN)])
        self.assertTrue(board.can_exit((2, 2)))

    def test_nearest_blocker_is_reported(self):
        board = Board(1, 5, [Arrow(0, c, D.RIGHT) for c in (0, 2, 4)])
        self.assertEqual(board.blocker((0, 0)), (0, 2))

    def test_empty_and_outside_clicks_are_free(self):
        game = Game(Board(2, 3, [Arrow(1, 1, D.UP)]))
        for p in [(0, 0), (-1, 1), (10, 5)]:
            self.assertEqual(game.attempt(p), "ignored")
        self.assertEqual((game.lives, game.moves), (3, 0))

    def test_solver_detects_cycle_without_changing_board(self):
        board = Board(1, 2, [Arrow(0, 0, D.RIGHT), Arrow(0, 1, D.LEFT)])
        before = board.arrows.copy()
        self.assertIsNone(solve(board))
        self.assertEqual(board.arrows, before)

    def test_generator_is_solvable_and_reproducible(self):
        for rows, cols, count in [(1, 1, 1), (1, 8, 8), (8, 1, 8),
                                 (3, 7, 19), (7, 7, 49)]:
            for seed in range(25):
                board = generate(rows, cols, count, seed)
                self.assertEqual(len(solve(board)), count)
                self.assertEqual(board.arrows, generate(rows, cols, count, seed).arrows)

    def test_bad_data_is_rejected(self):
        with self.assertRaises(ValueError):
            Board(2, 2, [Arrow(-1, 0, D.UP)])
        with self.assertRaises(ValueError):
            Board(2, 2, [Arrow(0, 0, D.UP)] * 2)
        with self.assertRaises(ValueError):
            generate(2, 2, 5, 0)

    def test_win_is_terminal_and_stars_include_hints(self):
        game = Game(Board(1, 1, [Arrow(0, 0, D.RIGHT)]))
        game.hints = 1
        game.attempt((0, 0))
        self.assertEqual(game.stars, 2)
        self.assertEqual(game.attempt((0, 0)), "ignored")

    def test_shipped_levels_have_four_directions(self):
        for level in load_levels():
            self.assertEqual({a.direction for a in level["board"].arrows.values()}, set(D))


if __name__ == "__main__":
    unittest.main()
