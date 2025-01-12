from fastapi import APIRouter, HTTPException, WebSocket
from typing import Dict

from game_manager import GameManager
from websocket_handler import WebSocketHandler

router = APIRouter(prefix="/api")
ws_router = APIRouter()

class GameRoutes:
    def __init__(self, game_manager: GameManager):
        self.game_manager = game_manager
        self.ws_handler = WebSocketHandler(game_manager)
        self._setup_routes()

    def _setup_routes(self):
        @router.post("/games/create")
        async def create_game():
            """Create a new game and return its ID"""
            game_id = self.game_manager.create_game()
            return {"game_id": game_id}

        @router.get("/games/{game_id}")
        async def get_game_status(game_id: str):
            """Get the current status of a game"""
            game = self.game_manager.get_game(game_id)
            if not game:
                raise HTTPException(status_code=404, detail="Game not found")

            return {
                "player_count": len(game.players),
                "board": game.board,
                "current_player": game.current_player,
                "winner": game.winner
            }

        @router.get("/games")
        async def get_all_games():
            """Get all active games"""
            try:
                games_data = {}
                for game_id, game in self.game_manager.games.items():
                    games_data[game_id] = {
                        "board": game.board,
                        "current_player": game.current_player,
                        "winner": game.winner,
                        "player_count": len(game.players),
                        "created_at": self.game_manager.game_creation_times.get(game_id).isoformat() 
                            if game_id in self.game_manager.game_creation_times else None
                    }
                return {"games": games_data}
            
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @ws_router.websocket("/ws/game/{game_id}")
        async def websocket_endpoint(websocket: WebSocket, game_id: str):
            await self.ws_handler.handle_connection(websocket, game_id)