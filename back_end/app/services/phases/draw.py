from app.services.phases.phase import Phase
from app.services.game_data import TERRITORIES


class Draw(Phase):
    def __init__(self, game):
        super().__init__(game)

    def handle_move(self, player, territory):
        return False

    def execute_move(self, args=None):
        if args == None:
            territory = self.game.pop_ter_stack()
        else:
            territory = args

        if territory == "END GAME":
            self.game.end_game()

        self.game.add_ter_card(self.game.get_current_player(), territory)

    def can_execute_move(self):
        return True

    def get_phase_info(self):
        return ""
