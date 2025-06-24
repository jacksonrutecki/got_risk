import random
from app.services.phases.phase import Phase
from app.services.game_data import TERRITORIES


class Invade(Phase):
    def __init__(self, game):
        super().__init__(game)

    def handle_move(self, player, territory):
        ter_player = self.game.get_player_on_territory(territory)

        # case 1: no territories are selected:
        if len(self.game.get_ter_from()) == 0 and len(self.game.get_ter_to()) == 0:
            if ter_player == player:
                self.game.append_ter_from(territory)
            else:
                self.game.append_ter_to(territory)

        # # case 2: both territories are selected:
        # elif len(self.game.get_ter_from()) == 1 and len(self.game.get_ter_to()) == 1:
        #     # if the player owns the territory
        #     if ter_player == player:
        #         # if the selected territory is not neighbors with the old attacked territory
        #         if self.game.get_ter_to()[0] not in TERRITORIES.get(territory)["neighbors"]:
        #             # wipe it
        #             self.game.reset_ter_to()
        #         self.game.append_ter_to(territory)
        #     # if the player does not own the territory
        #     else:
        #         # if the selected territory is not neighbors with the old attacked from territory
        #         if self.game.get_ter_from()[0] not in TERRITORIES.get(territory)["neighbors"]:
        #             # wipe it
        #             self.game.reset_ter_from()
        #         self.game.append_ter_to(territory)

        # case 3: one territory from ter_from is selected:
        elif len(self.game.get_ter_from()) == 1:
            # if the player does not own the territory
            if ter_player != player:
                if self.game.get_ter_from()[0] not in TERRITORIES.get(territory)["neighbors"]:
                    self.game.reset_ter_from()
                self.game.append_ter_to(territory)
            # if the player does own the territory
            else:
                self.game.reset_ter_from()
                self.game.append_ter_from(territory)

        # case 4: one territory from ter_to is selected:
        elif len(self.game.get_ter_to()) == 1:
            # if the player owns the territory
            if ter_player == player:
                if self.game.get_ter_to()[0] not in TERRITORIES.get(territory)["neighbors"]:
                    self.game.reset_ter_to()
                self.game.append_ter_from(territory)
            else:
                self.game.reset_ter_to()
                self.game.append_ter_to(territory)

    def execute_move(self, args=None):
        if len(self.game.get_ter_to()) > 1 or len(self.game.get_ter_from()) > 1:
            ValueError(
                "ter_to and ter_from should both only have lengths of 1 at this point")

        ter_from = self.game.get_ter_from()[0]
        ter_to = self.game.get_ter_to()[0]

        attack_armies = self.game.get_num_armies_on_territory(ter_from)
        defend_armies = self.game.get_num_armies_on_territory(ter_to)

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
                    self.game.remove_army_from_ter(ter_to)
                else:
                    self.game.remove_army_from_ter(ter_from)

            if self.game.get_num_armies_on_territory(ter_to) == 0:
                self.game.set_player_on_territory(
                    self.game.get_current_player(), ter_to)

                self.game.set_phase_to_move()

    def can_execute_move(self):
        return len(self.game.get_ter_to()) > 0 and len(self.game.get_ter_from()) > 0

    def get_phase_info(self):
        return f"Attacking: {self.game.get_ter_to()}\nAttacking from: {self.game.get_ter_from()}"
