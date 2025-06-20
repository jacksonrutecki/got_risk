# phases are as follows:
# -1: setup board
# 0: reinforce
# 1: invade
# 2: maneuver
# 3: draw

import json
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
            3: self.handle_draw
        }

        self.executes = {
            -2: self.execute_move_armies,
            0: self.execute_reinforce,
            1: self.execute_invade,
            2: self.execute_maneuver,
            3: self.execute_draw
        }

        self.ter_from = None
        self.ter_to = None

        self.setup_board(desired_territories)

    def get_state(self):
        return self.state

    def get_current_phase(self):
        return PHASES.get(self.current_phase)

    def get_current_player(self):
        return self.players[self.current_player_index]

    def get_num_armies_on_territory(self, territory):
        return self.state.get(territory).get("num_armies")

    def get_player_cards(self, player):
        return self.player_cards.get(player)

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
            print(self.current_phase)
            self.handles.get(self.current_phase)(player, data)

    def execute_move(self, args=None):
        self.executes.get(self.current_phase)(args)

    def handle_move_armies(self, player, num_armies):
        self.num_armies = num_armies

    def execute_move_armies(self, args=None):
        self.state.get(self.ter_from)["num_armies"] -= self.num_armies
        self.state.get(self.ter_to)["num_armies"] += self.num_armies

        self.current_phase = 1
        self.ter_from = None
        self.ter_to = None

    def handle_reinforce(self, player, territory):
        if self.current_num_armies > 0:
            if self.__get_player_on_territory__(territory) == player:
                self.ter_to = territory
            else:
                print(f"{player} does not have control of {territory}!")
        else:
            print(f"{player} is out of armies!")

    def execute_reinforce(self, args=None):
        self.state[self.ter_to]["num_armies"] += 1
        self.current_num_armies -= 1

        self.ter_to = None

    def handle_invade(self, player, territory):
        ter_player = self.state.get(territory)

        if ter_player["player"] == player:
            self.ter_from = territory
        else:
            self.ter_to = territory

    def execute_invade(self, args=None):
        if self.ter_to in TERRITORIES.get(self.ter_from)["neighbors"]:
            attack_armies = self.state.get(self.ter_from)["num_armies"]
            defend_armies = self.state.get(self.ter_to)["num_armies"]

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
                        self.state.get(self.ter_to)["num_armies"] -= 1
                    else:
                        self.state.get(self.ter_from)["num_armies"] -= 1

                if self.state.get(self.ter_to)["num_armies"] == 0:
                    self.state.get(self.ter_to)[
                        "player"] = self.players[self.current_player_index]
                    self.current_phase = -2
        else:
            print("not a valid attack")
            self.attack_from = None
            self.attack_to = None

    def handle_maneuver(self, player, territory):
        if self.ter_from is None:
            self.ter_from = territory
        elif self.ter_to is None:
            self.ter_to = territory
        else:
            self.ter_from = territory
            self.ter_to = None

    def execute_maneuver(self, args=None):
        self.current_phase = -2

    def handle_draw(self, player, data):
        return ()

    def execute_draw(self, args=None):
        if args != None:
            territory = self.territory_card_stack.pop(0)
        else:
            territroy = args

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
        self.ter_to = None
        self.ter_from = None
        self.setup_phase()

    # setup phase:
    # sets up a given phase
    def setup_phase(self):
        if self.current_phase == 0:
            self.current_num_armies = self.__calc_num_armies__()
        elif self.current_phase == 1:
            print(self.current_phase)
        elif self.current_phase == 2:
            print(self.current_phase)
        elif self.current_phase == 3:
            print(self.current_phase)
        else:
            print(f"invalid phase: {self.current_phase}")

    def __calc_num_armies__(self):
        cur_player = self.players[self.current_player_index]
        armies = 0

        for ter in self.state:
            if self.state.get(ter)["player"] == cur_player:
                armies += 1
                if TERRITORIES.get(ter)["is_castle"]:
                    armies += 1

        return max(3, armies)

    def __get_player_on_territory__(self, territory):
        return self.state.get(territory)["player"]
