# phases are as follows:
# -1: setup board
# 0: reinforce
# 1: invade
# 2: maneuver
# 3: draw

import math
import random

from app.services.game_data import TERRITORIES, PHASES
from app.services.phases import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.phases.phase import Phase


class Game:
    def __init__(self, game_id, players, desired_territories=None):
        self.game_id = game_id
        self.players = players
        self.current_player_index = 0
        self.current_phase = -1
        self.prev_phase = None
        # territory: {player, num_armies}
        self.state: dict[str, dict[str, int]] = {}
        # player: [territory cards]
        self.player_cards: dict[str, list[str]] = {}
        self.territory_card_stack = []
        self.current_num_armies = 0
        self.game_over = False

        self.phases: dict[int, Phase] = {
            -2: MoveArmies(self),
            0: Reinforce(self),
            1: Invade(self),
            2: Maneuver(self),
            3: Draw(self)
        }

        for player in self.players:
            self.player_cards[player] = []

        self.ter_from = []
        self.ter_to = []

        self.setup_board(desired_territories)

    def get_state(self):
        return self.state

    def get_current_phase(self):
        return PHASES.get(self.current_phase)

    def get_current_player(self):
        return self.players[self.current_player_index]

    def get_num_armies_on_territory(self, territory):
        if self.state.get(territory) == None:
            print(territory)
        return self.state.get(territory).get("num_armies")

    def get_string_armies_on_territory(self, territory):
        armies = str(self.get_num_armies_on_territory(territory))

        if self.current_phase == 0:
            if territory in self.ter_to:
                armies += f"+{self.ter_to.count(territory)}"

        return armies

    def get_player_cards(self, player):
        return self.player_cards.get(player)

    def get_current_num_armies(self):
        return self.current_num_armies

    def get_game_status(self):
        return self.game_over

    def get_ter_from(self):
        return self.ter_from

    def get_ter_to(self):
        return self.ter_to

    def pop_ter_to(self):
        self.ter_to.pop(0)

    def append_ter_to(self, territory):
        self.ter_to.append(territory)

    def append_ter_from(self, territory):
        self.ter_from.append(territory)

    def add_army_to_ter(self, territory):
        self.state[territory]["num_armies"] += 1
        self.current_num_armies -= 1

    def remove_army_from_ter(self, territory):
        self.state[territory]["num_armies"] -= 1

    # multiple referencing num_armies, used in moving
    def add_armies_to_ter(self, territory):
        self.state[territory]["num_armies"] += self.num_armies

    def remove_armies_from_ter(self, territory):
        self.state[territory]["num_armies"] -= self.num_armies

    def set_player_on_territory(self, player, territory):
        self.state.get(territory)["player"] = player

    def set_phase_to_move(self):
        self.prev_phase = self.current_phase
        self.current_phase = -2

    def return_phase_from_move(self):
        self.current_phase = self.prev_phase

    def reset_ter_to(self):
        self.ter_to = []

    def reset_ter_from(self):
        self.ter_from = []

    def pop_ter_stack(self):
        return self.territory_card_stack.pop(0)

    def end_game(self):
        self.game_over = True

    def add_ter_card(self, player, territory):
        self.player_cards[player].append(territory)

    def setup_board(self, desired_territories=None):
        cur_index = 0
        # look into a better way to organize these directories
        territories = list(TERRITORIES.keys())
        random.shuffle(territories)

        # distribute territories randomly, assign 2 armies to each
        for territory in territories:
            self.state[territory] = {
                "player": self.players[cur_index], "num_armies": 2}
            cur_index = (cur_index + 1) % len(self.players)

        # adding in potential to set territories, for testing purposes
        if desired_territories != None:
            for ter in desired_territories:
                self.state[ter["territory"]]["player"] = ter["player"]

        # append the end game card at the latter half of the deck
        midpoint = len(territories) // 2
        front_half = territories[:midpoint]
        last_half = territories[midpoint:]
        last_half.append("END GAME")
        random.shuffle(front_half)
        random.shuffle(last_half)

        front_half.extend(last_half)
        self.territory_card_stack = front_half

        self.next_move()

    # handle move:
    # handles a move when a player clicks on a territory
    def handle_move(self, player, data):
        if player == self.players[self.current_player_index]:
            return self.phases.get(self.current_phase).handle_move(player, data)

    def execute_move(self, args=None):
        return self.phases.get(self.current_phase).execute_move(args)

    def can_execute_move(self, player):
        return self.get_current_player() == player and self.phases.get(self.current_phase).can_execute_move()

    def set_num_armies(self, num_armies):
        self.num_armies = num_armies

    # next move:
    # progressed the game onto the next phase. if the user's turn is over, reset phases and move to next player.
    def next_move(self):
        if self.current_phase < 3:
            self.current_phase += 1
        else:
            self.current_phase = 0
            self.current_player_index = (
                self.current_player_index + 1) % len(self.players)
        self.reset_phase()

    # setup phase:
    # sets up a given phase
    def reset_phase(self):
        if self.current_phase == 0:
            self.current_num_armies = self.calc_num_armies()
        self.ter_to = []
        self.ter_from = []

    def calc_num_armies(self):
        cur_player = self.players[self.current_player_index]
        armies = 0

        for ter in self.state:
            if self.state.get(ter)["player"] == cur_player:
                armies += 1
                if TERRITORIES.get(ter)["is_castle"]:
                    armies += 1

        return max(3, math.floor(armies / 3))

    def get_player_on_territory(self, territory):
        return self.state.get(territory)["player"]
