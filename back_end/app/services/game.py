# phases are as follows:
# -1: setup board
# 0: reinforce
# 1: invade
# 2: maneuver
# 3: draw

import json
import random


class Game:
    def __init__(self, game_id, players):
        self.game_id = game_id
        self.players = players
        self.current_player_index = 0
        self.current_phase = -1
        self.state = {}  # territory: {player, num_armies}
        self.territory_card_stack = []

        self.setup_board()

    def get_state(self):
        return self.state

    def get_current_phase(self):
        return self.current_phase

    def get_current_player(self):
        return self.players[self.current_player_index]

    def setup_board(self):
        cur_index = 0
        with open("../data/territories.json", "r") as f:
            territories = list(json.load(f).keys())
            random.shuffle(territories)

            # distribute territories randomly, assign 2 armies to each
            for territory in territories:
                self.state[territory] = {"player": cur_index, "num_armies": 2}
                cur_index = (cur_index + 1) % len(self.players)

            # append the end game card at the latter half of the deck
            midpoint = len(territories) // 2
            front_half = territories[:midpoint]
            last_half = territories[midpoint:]
            last_half.append("END GAME")
            random.shuffle(front_half)
            random.shuffle(last_half)

            front_half.extend(last_half)
            self.territory_card_stack = front_half

            self.current_phase += 1

    def handle_move(self, player):
        if player == self.players[self.current_player_index]:
            print(self.current_phase)
        else:
            return ()

    def next_move(self):
        if self.current_phase < 3:
            self.current_phase += 1
        else:
            self.current_phase = 0
            self.current_player_index = (
                self.current_player_index + 1) % len(self.players)
