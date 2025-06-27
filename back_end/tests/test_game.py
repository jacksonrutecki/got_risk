from app.services.game import Game
import unittest


class test_game(unittest.TestCase):
    def test_game_init(self):
        test_game = Game("id", ["jackson"])

        self.assertEqual(test_game.get_current_phase(), "Reinforce")
        self.assertEqual(test_game.get_current_player(), "jackson")
        self.assertEqual(
            test_game.get_num_armies_on_territory("stoney_shore"), 2)

    def test_handle_move_wrong_playername(self):
        test_game = Game("id", ["jackson"])
        test_game.handle_move("not_jackson", "stoney_shore")

        self.assertEqual(test_game.get_current_phase(), "Reinforce")
        self.assertEqual(test_game.get_current_player(), "jackson")
        self.assertEqual(
            test_game.get_num_armies_on_territory("stoney_shore"), 2)

    def test_handle_move_wrong_territory(self):
        test_game = Game("id", ["jackson"])
        test_game.handle_move("jackson", "barrowlands")

        self.assertEqual(test_game.get_current_phase(), "Reinforce")
        self.assertEqual(test_game.get_current_player(), "jackson")
        self.assertEqual(
            test_game.get_num_armies_on_territory("stoney_shore"), 2)

    def test_next_move(self):
        test_game = Game("id", ["jackson"])
        test_game.next_move()
        self.assertEqual(test_game.get_current_phase(), "Invade")
        self.assertEqual(test_game.get_current_player(), "jackson")

    def test_setting_board(self):
        test_game = Game("id", ["jackson1", "jackson2"], [{"territory": "stoney_shore", "player": "jackson1"},
                                                          {"territory": "barrowlands", "player": "jackson2"}])

        self.assertEqual(test_game.get_current_player(), "jackson1")
        self.assertEqual(test_game.get_player_on_territory(
            "stoney_shore"), "jackson1")
        self.assertEqual(test_game.get_player_on_territory(
            "barrowlands"), "jackson2")

    def test_next_move(self):
        test_game = Game("id", ["jackson1", "jackson2"], [{"territory": "stoney_shore", "player": "jackson1"},
                                                          {"territory": "barrowlands", "player": "jackson2"}])

        self.assertEqual(test_game.get_current_player(), "jackson1")

        test_game.next_move()
        test_game.next_move()
        test_game.next_move()
        test_game.next_move()

        self.assertEqual(test_game.get_current_player(), "jackson2")

    def test_can_execute_move(self):
        test_game = Game("id", ["jackson"])

        self.assertEqual(test_game.can_execute_move("jackson"), False)
        test_game.handle_move("jackson", "stoney_shore")
        self.assertEqual(test_game.can_execute_move("jackson"), True)


class test_reinforce(unittest.TestCase):
    def test_reinforcing(self):
        test_game = Game("id", ["jackson"])

        self.assertEqual(
            test_game.get_num_armies_on_territory("stoney_shore"), 2)
        test_game.handle_move("jackson", "stoney_shore")
        self.assertEqual(
            test_game.get_num_armies_on_territory("stoney_shore"), 2)
        test_game.execute_move()
        self.assertEqual(
            test_game.get_num_armies_on_territory("stoney_shore"), 3)

    def test_reinforce_double(self):
        test_game = Game("id", ["jackson"])

        self.assertEqual(test_game.calc_num_armies(), 8)
        self.assertEqual(test_game.get_current_num_armies(), 8)

        test_game.handle_move("jackson", "stoney_shore")
        test_game.handle_move("jackson", "barrowlands")
        test_game.handle_move("jackson", "stoney_shore")
        test_game.handle_move("jackson", "barrowlands")
        test_game.execute_move()

        self.assertEqual(test_game.get_current_num_armies(), 4)
        self.assertEqual(
            test_game.get_num_armies_on_territory("barrowlands"), 4)
        self.assertEqual(
            test_game.get_num_armies_on_territory("stoney_shore"), 4)


class test_invade(unittest.TestCase):
    def test_full_invade(self):
        test_game = Game("id", ["jackson1", "jackson2"], [{"territory": "stoney_shore", "player": "jackson1"},
                                                          {"territory": "barrowlands", "player": "jackson2"}])

        test_game.handle_move("jackson1", "stoney_shore")
        test_game.execute_move()
        test_game.next_move()

        self.assertEqual(test_game.get_current_phase(), "Invade")

        test_game.handle_move("jackson1", "stoney_shore")
        test_game.handle_move("jackson1", "barrowlands")
        test_game.execute_move([[6, 6, 6], [1, 1]])

        self.assertEqual(
            test_game.get_num_armies_on_territory("stoney_shore"), 3)
        self.assertEqual(
            test_game.get_num_armies_on_territory("barrowlands"), 0)
        self.assertEqual(test_game.get_current_phase(), "Move Armies")

        test_game.handle_move("jackson1", 2)
        test_game.execute_move()
        self.assertEqual(
            test_game.get_num_armies_on_territory("stoney_shore"), 1)
        self.assertEqual(
            test_game.get_num_armies_on_territory("barrowlands"), 2)
        self.assertEqual(test_game.get_player_on_territory(
            "barrowlands"), "jackson1")
        self.assertEqual(test_game.get_current_phase(), "Invade")

    def test_failed_invade(self):
        test_game = Game("id", ["jackson1", "jackson2"], [{"territory": "stoney_shore", "player": "jackson1"},
                                                          {"territory": "barrowlands", "player": "jackson2"}])

        test_game.handle_move("jackson1", "stoney_shore")
        test_game.execute_move()
        test_game.next_move()

        self.assertEqual(test_game.get_current_phase(), "Invade")

        test_game.handle_move("jackson1", "stoney_shore")
        test_game.handle_move("jackson1", "barrowlands")
        test_game.execute_move([[1, 1, 1], [1, 1]])

        self.assertEqual(
            test_game.get_num_armies_on_territory("stoney_shore"), 1)
        self.assertEqual(
            test_game.get_num_armies_on_territory("barrowlands"), 2)
        self.assertEqual(test_game.get_current_phase(), "Invade")

    def test_partial_invade(self):
        test_game = Game("id", ["jackson1", "jackson2"], [{"territory": "stoney_shore", "player": "jackson1"},
                                                          {"territory": "barrowlands", "player": "jackson2"}])

        test_game.handle_move("jackson1", "stoney_shore")
        test_game.execute_move()
        test_game.next_move()

        self.assertEqual(test_game.get_current_phase(), "Invade")

        test_game.handle_move("jackson1", "stoney_shore")
        test_game.handle_move("jackson1", "barrowlands")
        test_game.execute_move([[2, 1, 1], [1, 1]])

        self.assertEqual(
            test_game.get_num_armies_on_territory("stoney_shore"), 2)
        self.assertEqual(
            test_game.get_num_armies_on_territory("barrowlands"), 1)
        self.assertEqual(test_game.get_current_phase(), "Invade")

    def test_invade_case1_full(self):
        test_game = Game("id", ["jackson1", "jackson2"], [{"territory": "stoney_shore", "player": "jackson1"},
                                                          {"territory": "barrowlands", "player": "jackson2"}])

        test_game.next_move()
        test_game.handle_move("jackson1", "barrowlands")
        test_game.handle_move("jackson1", "stoney_shore")
        test_game.execute_move([[6, 6, 6], [1, 1]])

        self.assertEqual(
            test_game.get_num_armies_on_territory("stoney_shore"), 2)
        self.assertEqual(
            test_game.get_num_armies_on_territory("barrowlands"), 0)
        self.assertEqual(test_game.get_current_phase(), "Move Armies")

    def test_invade_case2_full(self):
        test_game = Game("id", ["jackson1", "jackson2"], [{"territory": "stoney_shore", "player": "jackson1"},
                                                          {"territory": "barrowlands", "player": "jackson2"}])

        test_game.next_move()
        test_game.handle_move("jackson1", "barrowlands")
        test_game.handle_move("jackson1", "stoney_shore")

        test_game.handle_move("jackson1", "barrowlands")
        test_game.handle_move("jackson1", "stoney_shore")
        test_game.execute_move([[6, 6, 6], [1, 1]])

        self.assertEqual(
            test_game.get_num_armies_on_territory("stoney_shore"), 2)
        self.assertEqual(
            test_game.get_num_armies_on_territory("barrowlands"), 0)
        self.assertEqual(test_game.get_current_phase(), "Move Armies")

    def test_invade_wrong_ter_selected(self):
        test_game = Game("id", ["jackson"])

        test_game.next_move()
        test_game.handle_move("jackson", "barrowlands")
        test_game.handle_move("jackson", "stoney_shore")

        self.assertEqual(test_game.get_ter_from(), ["stoney_shore"])
        self.assertEqual(test_game.get_ter_to(), [])


class test_maneuver(unittest.TestCase):
    def test_maneuever(self):
        test_game = Game("id", ["jackson"])

        test_game.handle_move("jackson", "stoney_shore")
        test_game.execute_move()
        test_game.next_move()
        test_game.next_move()

        test_game.handle_move("jackson", "stoney_shore")
        test_game.handle_move("jackson", "barrowlands")
        test_game.execute_move()
        test_game.handle_move("jackson", 2)
        test_game.execute_move()

        self.assertEqual(
            test_game.get_num_armies_on_territory("stoney_shore"), 1)
        self.assertEqual(
            test_game.get_num_armies_on_territory("barrowlands"), 4)


class test_draw(unittest.TestCase):
    def test_draw(self):
        test_game = Game("id", ["jackson"])

        test_game.next_move()
        test_game.next_move()
        test_game.next_move()

        test_game.handle_move("jackson", None)
        test_game.execute_move("stoney_shore")

        self.assertEqual(test_game.get_player_cards(
            "jackson"), ["stoney_shore"])


if __name__ == "__main__":
    unittest.main()
