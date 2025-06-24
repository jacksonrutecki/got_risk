from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.game import Game


class Phase:
    def __init__(self, game: "Game"):
        self.game = game

    def handle_move(self, player, data):
        return False

    def execute_move(self, args=None):
        return False

    def can_execute_move(self):
        return False

    def get_phase_info(self):
        return False
