import React, { useState, useEffect } from 'react';

const Square = ({ value, onClick }) => (
  <button 
    className={`square ${value}`}
    onClick={onClick}
  >
    {value}
  </button>
);

const GameBoard = () => {
  // Extract gameId from URL
  const gameId = new URLSearchParams(window.location.search).get('id');
  
  const [gameState, setGameState] = useState({
    board: Array(9).fill(''),
    currentPlayer: 'X',
    isMyTurn: false,
    isGameOver: false,
    gameStatus: 'Connecting to game...',
    symbol: null
  });
  const [ws, setWs] = useState(null);

  const handleWebSocketMessage = (event) => {
    console.log('Received message:', event.data);
    const data = JSON.parse(event.data);
    
    const messageHandlers = {
      game_state: () => {
        setGameState(prev => ({
          ...prev,
          board: data.board,
          currentPlayer: data.current_player,
          isMyTurn: data.is_your_turn,
          isGameOver: false,
          gameStatus: data.player_count === 2 
            ? (data.is_your_turn ? 'Your turn!' : "Opponent's turn!")
            : 'Waiting for opponent...'
        }));
      },
      player_joined: () => {
        setGameState(prev => ({
          ...prev,
          symbol: data.symbol,
          isMyTurn: data.is_your_turn,
          gameStatus: data.player_count === 2
            ? `Game started! ${data.is_your_turn ? 'Your turn!' : "Opponent's turn!"}`
            : 'Waiting for opponent...'
        }));
      },
      game_over: () => {
        setGameState(prev => ({
          ...prev,
          isGameOver: true,
          gameStatus: `Game Over! ${data.winner}`
        }));
      },
      opponent_disconnected: () => {
        setGameState(prev => ({
          ...prev,
          gameStatus: 'Opponent disconnected. Waiting for them to rejoin...'
        }));
      }
    };

    const handler = messageHandlers[data.type];
    if (handler) {
      handler();
    } else {
      console.log('Received unknown message type:', data.type);
    }
  };

  useEffect(() => {
    if (!gameId) {
      setGameState(prev => ({
        ...prev,
        gameStatus: 'Invalid game ID. Please check your URL.'
      }));
      return;
    }

    let websocket = null;
    let retryCount = 0;
    const maxRetries = 3;

    const connectWebSocket = () => {
      try {
        if (websocket?.readyState === WebSocket.OPEN) return;

        websocket = new WebSocket(`ws://localhost:8000/ws/game/${gameId}`);
        
        websocket.onopen = () => {
          console.log('WebSocket connected successfully');
          setGameState(prev => ({
            ...prev,
            gameStatus: 'Connected! Waiting for opponent...'
          }));
          setWs(websocket);
        };
        
        websocket.onmessage = handleWebSocketMessage;
        
        websocket.onerror = (error) => {
          console.error('WebSocket error:', error);
          setGameState(prev => ({
            ...prev,
            gameStatus: 'Connection error. Retrying...'
          }));
        };
        
        websocket.onclose = (event) => {
          console.log('WebSocket closed:', event.code, event.reason);
          setWs(null);
          
          if (event.code === 4000) {
            setGameState(prev => ({
              ...prev,
              gameStatus: 'Game not found.'
            }));
            return;
          }
          
          if (event.code === 4001) {
            setGameState(prev => ({
              ...prev,
              gameStatus: 'Game is full.'
            }));
            return;
          }
          
          if (retryCount < maxRetries) {
            retryCount++;
            setTimeout(connectWebSocket, 2000);
            setGameState(prev => ({
              ...prev,
              gameStatus: 'Connection lost. Retrying...'
            }));
          } else {
            setGameState(prev => ({
              ...prev,
              gameStatus: 'Could not connect to game server. Please refresh the page.'
            }));
          }
        };
      } catch (error) {
        console.error('WebSocket connection error:', error);
        setGameState(prev => ({
          ...prev,
          gameStatus: 'Failed to connect to game server.'
        }));
      }
    };

    connectWebSocket();

    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, [gameId]);

  const handleSquareClick = (index) => {
    const { isMyTurn, board, isGameOver } = gameState;
    if (!isMyTurn || board[index] || !ws || ws.readyState !== WebSocket.OPEN || isGameOver) {
      return;
    }

    ws.send(JSON.stringify({
      type: 'move',
      position: index
    }));
  };

  const startNewGame = () => {
    if (ws?.readyState === WebSocket.OPEN) {
      console.log('Requesting new game');
      ws.send(JSON.stringify({
        type: 'new_game'
      }));
    }
  };

  const createNewGame = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/games/create', {
        method: 'POST',
      });
      const data = await response.json();
      const gameUrl = `${window.location.origin}?id=${data.game_id}`;
      
      // Copy to clipboard
      await navigator.clipboard.writeText(gameUrl);
      alert('Game link copied to clipboard! Share it with your opponent.');
      
      // Redirect to the game
      window.location.href = gameUrl;
    } catch (error) {
      console.error('Error creating game:', error);
      alert('Failed to create game. Please try again.');
    }
  };

  const renderBoard = () => (
    <div className="board-container">
      <table>
        <tbody>
          {[0, 3, 6].map(rowStart => (
            <tr key={rowStart}>
              {[0, 1, 2].map(colOffset => (
                <td key={colOffset}>
                  <Square
                    value={gameState.board[rowStart + colOffset]}
                    onClick={() => handleSquareClick(rowStart + colOffset)}
                  />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  return (
    <div className="game-container">
      <h2 className="game-status">{gameState.gameStatus}</h2>
      
      {!gameId ? (
        <button
          onClick={createNewGame}
          className="new-game-button"
        >
          Create New Game
        </button>
      ) : (
        <>
          {renderBoard()}
          
          {gameState.isGameOver && (
            <button 
              onClick={startNewGame}
              className="new-game-button"
            >
              Start New Game
            </button>
          )}
        </>
      )}
    </div>
  );
};

export default GameBoard;