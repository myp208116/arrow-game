"""Use the real Pygame event handler and renderer with an off-screen display."""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import unittest
import pygame
from arrow_game.app import App
from arrow_game.core import solve


class InterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = App()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.app.start_level(0)

    def click(self, point):
        self.app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                pos=point, button=1))

    def button(self, key):
        rect = next(rect for name, rect, *_ in self.app.button_specs() if name == key)
        self.click(rect.center)

    def test_menu_and_all_level_select_buttons(self):
        for index in range(3):
            self.app.activate("menu")
            self.app.render()
            self.button(f"level:{index}")
            self.assertEqual(self.app.scene, "playing")
            self.assertEqual(self.app.level_index, index)
            self.app.render()

    def test_animation_locks_extra_clicks_and_commits_once(self):
        position = self.app.game.board.available()[0]
        self.click(self.app.cell_center(position))
        for _ in range(20):
            self.click(self.app.cell_center(position))
        self.assertEqual(self.app.game.moves, 0)
        self.assertIn(position, self.app.game.board.arrows)
        self.app.update(.2)
        self.app.render()
        self.app.update(.2)
        self.assertEqual(self.app.game.moves, 1)
        self.assertNotIn(position, self.app.game.board.arrows)

    def test_collision_animation_and_fail_restart(self):
        position = next(p for p in self.app.game.board.arrows
                        if not self.app.game.board.can_exit(p))
        for lives in (2, 1, 0):
            self.click(self.app.cell_center(position))
            self.app.update(.2)
            self.assertEqual(self.app.animation.kind, "bump")
            self.app.render()
            self.app.update(.23)
            self.assertEqual(self.app.game.lives, lives)
            self.assertIn(position, self.app.game.board.arrows)
        self.assertEqual(self.app.scene, "result")
        self.app.render()
        self.button("restart")
        self.assertEqual((self.app.scene, self.app.game.lives), ("playing", 3))

    def test_restart_during_animation_cancels_pending_move(self):
        position = self.app.game.board.available()[0]
        self.click(self.app.cell_center(position))
        self.app.update(.1)
        self.button("restart")
        self.app.update(1)
        self.assertEqual(self.app.game.moves, 0)
        self.assertIn(position, self.app.game.board.arrows)
        self.assertIsNone(self.app.animation)

    def test_full_campaign_through_mouse_events_and_buttons(self):
        for index in range(3):
            self.assertEqual(self.app.level_index, index)
            for position in solve(self.app.game.board):
                self.click(self.app.cell_center(position))
                self.app.update(.4)
            self.assertEqual(self.app.scene, "result")
            self.assertEqual(self.app.game.status, "won")
            self.app.render()
            keys = {key for key, *_ in self.app.button_specs()}
            if index < 2:
                self.assertIn("next", keys)
                self.button("next")
                self.assertEqual(self.app.game.lives, 3)
            else:
                self.assertNotIn("next", keys)
                self.button("menu")
                self.assertEqual(self.app.scene, "menu")

    def test_empty_grid_margin_and_right_click(self):
        game = self.app.game
        self.click((50, 500))
        self.click((1100, 700))
        p = game.board.available()[0]
        self.app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                pos=self.app.cell_center(p), button=3))
        self.assertIsNone(self.app.animation)
        self.assertEqual(game.lives, 3)

    def test_focus_pause_freezes_time_and_animation(self):
        p = self.app.game.board.available()[0]
        self.click(self.app.cell_center(p))
        self.app.handle_event(pygame.event.Event(pygame.WINDOWFOCUSLOST))
        self.app.update(20)
        self.app.render()
        self.assertEqual(self.app.game.elapsed, 0)
        self.assertEqual(self.app.animation.elapsed, 0)
        self.button("resume")
        self.app.update(.4)
        self.assertNotIn(p, self.app.game.board.arrows)

    def test_hint_points_to_legal_move_without_changing_board(self):
        before = self.app.game.board.arrows.copy()
        self.button("hint")
        self.button("hint")
        self.assertTrue(self.app.game.board.can_exit(self.app.hint_position))
        self.assertEqual(self.app.game.hints, 1)
        self.assertEqual(self.app.game.board.arrows, before)
        self.assertEqual(self.app.game.lives, 3)
        self.app.update(3.1)
        self.assertIsNone(self.app.hint_position)

    def test_escape_discards_old_animation(self):
        self.click(self.app.cell_center(self.app.game.board.available()[0]))
        self.app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        self.assertEqual(self.app.scene, "menu")
        self.assertIsNone(self.app.animation)
        self.button("start")
        self.assertEqual(self.app.game.moves, 0)


if __name__ == "__main__":
    unittest.main()
