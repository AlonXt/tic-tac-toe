import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
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


@app.websocket("/ws/game")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    game = game_manager.get_or_create_game("game1")
    player_symbol = 'X' if len(game.players) == 0 else 'O'
    game.players[player_symbol] = websocket

    await websocket.send_json({
        "type": "player_joined",
        "is_your_turn": player_symbol == game.current_player,
        "symbol": player_symbol
    })

    try:
        if len(game.players) == 2:
            await broadcast_game_state(game)

        while True:
            data = await websocket.receive_json()
            await handle_message(data, game, player_symbol)

    except WebSocketDisconnect:
        game.players.pop(player_symbol, None)
        if len(game.players) == 0:
            game_manager.games.pop("game1", None)


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
            "is_your_turn": symbol == game.current_player
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
