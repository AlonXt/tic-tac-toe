from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Optional

from game_state import GameState
from game_manager import GameManager
from messaging_service import MessagingService

class WebSocketHandler:
    def __init__(self, game_manager: GameManager):
        self.game_manager = game_manager
        self.messaging_service = MessagingService()

    async def handle_connection(self, websocket: WebSocket, game_id: str):
        """Handle new WebSocket connections and manage the game session"""
        await websocket.accept()

        game = self.game_manager.get_game(game_id)
        if not game:
            await websocket.close(code=4000, reason="Game not found")
            return

        if len(game.players) >= 2:
            await websocket.close(code=4001, reason="Game is full")
            return

        player_symbol = 'X' if len(game.players) == 0 else 'O'
        game.players[player_symbol] = websocket

        try:
            await self.messaging_service.send_player_joined(
                websocket, 
                player_symbol, 
                game.current_player, 
                len(game.players)
            )

            if len(game.players) == 2:
                await self.messaging_service.broadcast_game_state(game)

            await self.handle_game_messages(websocket, game, player_symbol, game_id)

        except WebSocketDisconnect:
            await self.handle_disconnect(game_id, player_symbol, game)

    async def handle_game_messages(
        self, 
        websocket: WebSocket, 
        game: GameState, 
        player_symbol: str,
        game_id: str
    ):
        """Handle incoming game messages"""
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "new_game":
                game.reset_game()
                await self.messaging_service.broadcast_game_state(game)
            
            elif data["type"] == "move" and len(game.players) == 2:
                position = data["position"]
                if game.make_move(position, player_symbol):
                    await self.messaging_service.broadcast_game_state(game)
                    if game.winner:
                        await self.messaging_service.broadcast_game_over(game)

    async def handle_disconnect(self, game_id: str, player_symbol: str, game: GameState):
        """Handle player disconnection"""
        self.game_manager.remove_player_from_game(game_id, player_symbol)
        
        if len(game.players) > 0:
            # Notify remaining player
            remaining_player: WebSocket = next(iter(game.players.values()))
            await self.messaging_service.send_opponent_disconnected(remaining_player)