import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from game_manager import GameManager
from game_state import GameState

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production should be replaced with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

game_manager = GameManager()


@app.post("/api/games/create")
async def create_game():
    """Create a new game and return its ID"""
    game_id = game_manager.create_game()
    return {"game_id": game_id}


@app.get("/api/games/{game_id}")
async def get_game_status(game_id: str):
    """Get the current status of a game"""
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    return {
        "player_count": len(game.players),
        "board": game.board,
        "current_player": game.current_player,
        "winner": game.winner
    }


@app.websocket("/ws/game/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await websocket.accept()

    game = game_manager.get_game(game_id)
    if not game:
        await websocket.close(code=4000, reason="Game not found")
        return

    if len(game.players) >= 2:
        await websocket.close(code=4001, reason="Game is full")
        return

    player_symbol = 'X' if len(game.players) == 0 else 'O'
    game.players[player_symbol] = websocket

    try:
        await websocket.send_json({
            "type": "player_joined",
            "is_your_turn": player_symbol == game.current_player,
            "symbol": player_symbol,
            "player_count": len(game.players)
        })

        if len(game.players) == 2:
            await broadcast_game_state(game)

        while True:
            data = await websocket.receive_json()
            await handle_message(data, game, player_symbol)

    except WebSocketDisconnect:
        game_manager.remove_player_from_game(game_id, player_symbol)
        if len(game.players) > 0:
            # Notify remaining player
            remaining_player = next(iter(game.players.values()))
            await remaining_player.send_json({
                "type": "opponent_disconnected",
                "message": "Opponent has disconnected. Waiting for them to rejoin..."
            })


@app.on_event("startup")
async def startup_event():
    """Clean up old games periodically"""
    game_manager.cleanup_old_games()


async def handle_message(data, game: GameState, player_symbol: str):
    if data["type"] == "new_game":
        game.reset_game()
        await broadcast_game_state(game)
    elif data["type"] == "move" and len(game.players) == 2:
        position = data["position"]
        if game.make_move(position, player_symbol):
            await broadcast_game_state(game)
            if game.winner:
                await broadcast_game_over(game)


async def broadcast_game_state(game: GameState):
    for symbol, ws in game.players.items():
        await ws.send_json({
            "type": "game_state",
            "board": game.board,
            "current_player": game.current_player,
            "is_your_turn": symbol == game.current_player,
            "player_count": len(game.players)
        })


async def broadcast_game_over(game: GameState):
    winner_message = "Draw!" if game.winner == "draw" else f"{game.winner} wins!"
    for ws in game.players.values():
        await ws.send_json({
            "type": "game_over",
            "winner": winner_message
        })


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
