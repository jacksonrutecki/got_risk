# phases are as follows:
# -1: setup board
# 0: reinforce
# 1: invade
# 2: maneuver
# 3: draw

import json
import math
import random

PHASES = {
    -2: "Move Armies",
    -1: "Board Setup",
    0: "Reinforce",
    1: "Invade",
    2: "Maneuver",
    3: "Draw"
}

with open("data/territories.json", "r") as f:
    TERRITORIES = json.load(f)


class Game:
    def __init__(self, game_id, players, desired_territories=None):
        self.game_id = game_id
        self.players = players
        self.current_player_index = 0
        self.current_phase = -1
        self.state = {}  # territory: {player, num_armies}
        self.player_cards = {}  # player: [territory cards]
        self.territory_card_stack = []
        self.current_num_armies = 0
        self.game_over = False

        self.handles = {
            -2: self.handle_move_armies,
            0: self.handle_reinforce,
            1: self.handle_invade,
            2: self.handle_maneuver,
            3: lambda x, y: None
        }

        self.executes = {
            -2: self.execute_move_armies,
            0: self.execute_reinforce,
            1: self.execute_invade,
            2: self.execute_maneuver,
            3: self.execute_draw
        }

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
            self.handles.get(self.current_phase)(player, data)

    def execute_move(self, args=None):
        self.executes.get(self.current_phase)(args)

    def handle_move_armies(self, player, num_armies):
        self.num_armies = num_armies

    def execute_move_armies(self, args=None):
        for ter in self.ter_from:
            self.state.get(ter)["num_armies"] -= self.num_armies

        for ter in self.ter_to:
            self.state.get(ter)["num_armies"] += self.num_armies

        self.current_phase = 1
        self.ter_from = []
        self.ter_to = []

    def handle_reinforce(self, player, territory):
        # ensure player has armies
        if self.current_num_armies > 0:
            # ensure player owns territory
            if self.__get_player_on_territory__(territory) == player:
                # if the player has selected more territories than they have armies, remove
                # the first selected and replace it with most recently selected
                if self.current_num_armies == len(self.ter_to):
                    self.ter_to.pop(0)
                self.ter_to.append(territory)
            else:
                print(f"{player} does not have control of {territory}!")
        else:
            print(f"{player} is out of armies!")

    def execute_reinforce(self, args=None):
        for ter in self.ter_to:
            self.state[ter]["num_armies"] += 1
            self.current_num_armies -= 1

        self.ter_to = []

    def handle_invade(self, player, territory):
        ter_player = self.state.get(territory)["player"]

        # case 1: no territories are selected:
        if len(self.ter_from) == 0 and len(self.ter_to) == 0:
            if ter_player == player:
                self.ter_from.append(territory)
            else:
                self.ter_to.append(territory)

        # case 2: both territories are selected:
        elif len(self.ter_from) == 1 and len(self.ter_to) == 1:
            # if the player owns the territory
            if ter_player == player:
                # if the selected territory is not neighbors with the old attacked territory
                if self.ter_to[0] not in TERRITORIES.get(territory)["neighbors"]:
                    # wipe it
                    self.ter_to = []
                self.ter_from.append(territory)
            # if the player does not own the territory
            else:
                # if the selected territory is not neighbors with the old attacked from territory
                if self.ter_from[0] not in TERRITORIES.get(territory)["neighbors"]:
                    # wipe it
                    self.ter_from = []
                self.ter_to.append(territory)

        # case 3: one territory from ter_from is selected:
        elif len(self.ter_from) == 1:
            # if the player does not own the territory
            if ter_player != player:
                if self.ter_from[0] not in TERRITORIES.get(territory)["neighbors"]:
                    self.ter_from = []
            self.ter_to.append(territory)

        # case 4: one territory from ter_to is selected:
        elif len(self.ter_to) == 1:
            # if the player owns the territory
            if ter_player == player:
                if self.ter_to[0] not in TERRITORIES.get(territory)["neighbors"]:
                    self.ter_to = []
            self.ter_from.append(territory)

    def execute_invade(self, args=None):
        if len(self.ter_to) > 1 or len(self.ter_from) > 1:
            ValueError(
                "ter_to and ter_from should both only have lengths of 1 at this point")

        attack_armies = self.state.get(self.ter_from[0])["num_armies"]
        defend_armies = self.state.get(self.ter_to[0])["num_armies"]

        if attack_armies > 1:
            # adding in a potential to not have rolls be randomized, for testing
            if args == None:
                num_attack_die = min(attack_armies, 3)
                num_defend_die = min(defend_armies, 2)

                attack_rolls = [random.randint(1, 6)
                                for _ in range(num_attack_die)]
                defend_rolls = [random.randint(1, 6)
                                for _ in range(num_defend_die)]
            else:
                attack_rolls = args[0]
                defend_rolls = args[1]

            while len(attack_rolls) != 0 and len(defend_rolls) != 0:
                max_attack_roll = attack_rolls.pop(
                    attack_rolls.index(max(attack_rolls)))
                max_defend_roll = defend_rolls.pop(
                    defend_rolls.index(max(defend_rolls)))

                if max_attack_roll > max_defend_roll:
                    self.state.get(self.ter_to[0])["num_armies"] -= 1
                else:
                    self.state.get(self.ter_from[0])["num_armies"] -= 1

            if self.state.get(self.ter_to[0])["num_armies"] == 0:
                self.state.get(self.ter_to[0])[
                    "player"] = self.players[self.current_player_index]
                self.current_phase = -2

    def handle_maneuver(self, player, territory):
        if self.state.get(territory)["player"] == player:
            if len(self.ter_from) == 0:
                self.ter_from.append(territory)
            elif len(self.ter_to) == 0 and territory in TERRITORIES.get(self.ter_from[0])["neighbors"]:
                self.ter_to.append(territory)
            else:
                self.ter_from.append(territory)
                self.ter_to = []

    def execute_maneuver(self, args=None):
        self.current_phase = -2

    def execute_draw(self, args=None):
        if args == None:
            territory = self.territory_card_stack.pop(0)
        else:
            territory = args

        if territory == "END GAME":
            self.game_over = True

        if self.get_current_player() not in self.player_cards:
            self.player_cards[self.get_current_player()] = []

        self.player_cards[self.get_current_player()].append(territory)

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
            self.current_num_armies = self.__calc_num_armies__()
        self.ter_to = []
        self.ter_from = []

    def __calc_num_armies__(self):
        cur_player = self.players[self.current_player_index]
        armies = 0

        for ter in self.state:
            if self.state.get(ter)["player"] == cur_player:
                armies += 1
                if TERRITORIES.get(ter)["is_castle"]:
                    armies += 1

        return max(3, math.floor(armies / 3))

    def __get_player_on_territory__(self, territory):
        return self.state.get(territory)["player"]
