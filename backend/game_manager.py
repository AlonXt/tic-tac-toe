from typing import Dict

from game_state import GameState


class GameManager:
    def __init__(self):
        self.games: Dict[str, GameState] = {}

    def get_or_create_game(self, game_id: str) -> GameState:
        if game_id not in self.games:
            self.games[game_id] = GameState()
        return self.games[game_id]

    def reset_game(self, game_id: str):
        if game_id in self.games:
            self.games[game_id].reset_game()
