from app.services.phases.phase import Phase
from app.services.game_data import TERRITORIES


class Maneuver(Phase):
    def __init__(self, game):
        super().__init__(game)

    def handle_move(self, player, territory):
        if self.game.get_player_on_territory(territory) == player:
            if len(self.game.get_ter_from()) == 0:
                self.game.append_ter_from(territory)
            elif len(self.game.get_ter_to()) == 0 and territory in TERRITORIES.get(self.game.get_ter_from()[0])["neighbors"]:
                self.game.append_ter_to(territory)
            else:
                self.game.append_ter_from(territory)
                self.game.reset_ter_to()

    def execute_move(self, args=None):
        self.game.set_phase_to_move()

    def can_execute_move(self):
        return len(self.game.get_ter_to()) > 0 and len(self.game.get_ter_from()) > 0

    def get_phase_info(self):
        return f"Maneuvering from: {self.game.get_ter_from()}\nManeuvering to: {self.game.get_ter_to()}"
