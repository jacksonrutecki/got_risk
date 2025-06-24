from app.services.phases.phase import Phase


class MoveArmies(Phase):
    def __init__(self, game):
        super().__init__(game)

    def handle_move(self, player, num_armies):
        self.game.set_num_armies(num_armies)

    def execute_move(self, args=None):
        for ter in self.game.get_ter_from():
            self.game.remove_armies_from_ter(ter)

        for ter in self.game.get_ter_to():
            self.game.add_armies_to_ter(ter)

        self.game.return_phase_from_move()
        self.game.reset_ter_from()
        self.game.reset_ter_to()

    def can_execute_move(self):
        return True

    def get_phase_info(self):
        return ""
