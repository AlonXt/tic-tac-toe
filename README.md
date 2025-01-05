# Tic-Tac-Toe Game

This project is a real-time Tic-Tac-Toe game with a FastAPI backend and a React frontend, allowing two players to compete against each other.

## Project Structure

- **Backend**: FastAPI handles game logic, player moves, and game state.
- **Frontend**: React displays the game board and manages user input.
- **WebSockets**: Enables real-time communication between server and clients.

## How to Run the Project Locally

### Backend

1. Navigate to the `backend` directory.
2. Create a `.venv` using python3
3. Install dependencies: `pip install -r requirements.txt`
4. Run the server: `uvicorn main:app --reload`

### Frontend

1. Navigate to the `frontend` directory.
2. Install dependencies: `npm install`
3. Start the React app: `npm start`

## Playing the Game

1. Open two browser windows.
2. In each window, go to `http://localhost:3000`.
3. Players take turns clicking on squares to place their symbol (X or O).
4. The game updates in real-time for both players.

## Game Logic

- The game board is a 3x3 grid.
- Players take turns to place their symbol (X or O) on the board.
- The game checks for a win condition after each move.
- The first player to align three of their symbols in a row, column, or diagonal wins.

## Entities

1. **GameState**:
   - Represents the current state of a single Tic-Tac-Toe game.
   - Manages the game board, current player, and win conditions.
   - Contains methods to reset the game, make moves, and check for winners.

2. **GameManager**:
   - Manages multiple game instances. in this case was tested only on one game.
   - Responsible for creating new games and keeping track of active games.
   - Provides methods to retrieve or reset game states based on game IDs.

3. **WebSocketManager** (implicit in the main file):
   - Handles WebSocket connections for real-time communication between the server and clients.
   - Listens for player actions (like moves and new game requests) and broadcasts game state updates to all connected players.

## Game Flow

- When a player connects, a new `GameState` is created or retrieved by the `GameManager`.
- Players take turns making moves, which are processed by the `GameState`.
- After each move, the game checks for if a winning series was created and updates the game state.
- The updated game state is sent to all players via WebSockets, ensuring real-time updates.


Enjoy playing!