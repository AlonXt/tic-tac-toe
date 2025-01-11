from typing import Dict, Optional
import uuid
from datetime import datetime, timedelta

from game_state import GameState

class GameManager:
    def __init__(self):
        self.games: Dict[str, GameState] = {}
        self.game_creation_times: Dict[str, datetime] = {}
        self.cleanup_interval = timedelta(hours=24)  # Clean up games after 24 hours

    def create_game(self) -> str:
        """Creates a new game with a unique ID"""
        game_id = str(uuid.uuid4())
        self.games[game_id] = GameState()
        self.game_creation_times[game_id] = datetime.now()
        return game_id

    def get_game(self, game_id: str) -> Optional[GameState]:
        """Get an existing game by ID"""
        return self.games.get(game_id)

    def cleanup_old_games(self):
        """Remove games that are older than cleanup_interval"""
        current_time = datetime.now()
        game_ids_to_remove = []
        
        for game_id, creation_time in self.game_creation_times.items():
            if current_time - creation_time > self.cleanup_interval:
                game_ids_to_remove.append(game_id)
        
        for game_id in game_ids_to_remove:
            self.games.pop(game_id, None)
            self.game_creation_times.pop(game_id, None)

    def remove_player_from_game(self, game_id: str, player_symbol: str):
        """Remove a player from a game without deleting the game"""
        if game := self.games.get(game_id):
            game.players.pop(player_symbol, None)