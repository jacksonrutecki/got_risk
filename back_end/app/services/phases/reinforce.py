from app.services.phases.phase import Phase


class Reinforce(Phase):
    def __init__(self, game):
        super().__init__(game)

    def handle_move(self, player, territory):
        # ensure player has armies
        if self.game.get_current_num_armies() > 0:
            # ensure player owns territory
            if self.game.get_player_on_territory(territory) == player:
                # if the player has selected more territories than they have armies, remove
                # the first selected and replace it with most recently selected
                if self.game.get_current_num_armies() == len(self.game.get_ter_to()):
                    self.game.pop_ter_to()
                self.game.append_ter_to(territory)
            else:
                print(f"{player} does not have control of {territory}!")
        else:
            print(f"{player} is out of armies!")

    def execute_move(self, args=None):
        for ter in self.game.get_ter_to():
            self.game.add_army_to_ter(ter)

        self.game.reset_ter_to()

    def can_execute_move(self):
        return len(self.game.get_ter_to()) > 0 and self.game.get_current_num_armies() > 0

    def get_phase_info(self):
        return f"Armies to place:{self.game.get_current_num_armies()}"
