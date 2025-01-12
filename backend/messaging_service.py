from fastapi import WebSocket
from game_state import GameState

class MessagingService:
    async def broadcast_game_state(self, game: GameState):
        """Broadcast current game state to all players"""
        for symbol, ws in game.players.items():
            await ws.send_json({
                "type": "game_state",
                "board": game.board,
                "current_player": game.current_player,
                "is_your_turn": symbol == game.current_player,
                "player_count": len(game.players)
            })

    async def broadcast_game_over(self, game: GameState):
        """Broadcast game over message to all players"""
        winner_message = "Draw!" if game.winner == "draw" else f"{game.winner} wins!"
        for ws in game.players.values():
            await ws.send_json({
                "type": "game_over",
                "winner": winner_message
            })

    async def send_player_joined(
        self, 
        websocket: WebSocket, 
        player_symbol: str, 
        current_player: str,
        player_count: int
    ):
        """Send player joined message to the new player"""
        await websocket.send_json({
            "type": "player_joined",
            "is_your_turn": player_symbol == current_player,
            "symbol": player_symbol,
            "player_count": player_count
        })

    async def send_opponent_disconnected(self, websocket: WebSocket):
        """Send opponent disconnected message"""
        await websocket.send_json({
            "type": "opponent_disconnected",
            "message": "Opponent has disconnected. Waiting for them to rejoin..."
        })