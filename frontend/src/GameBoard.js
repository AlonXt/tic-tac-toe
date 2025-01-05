import React, { useState, useEffect } from 'react';
import Square from './Square';

const GameBoard = () => {
  const [gameState, setGameState] = useState({
    board: Array(9).fill(''),
    currentPlayer: 'X',
    isMyTurn: false,
    isGameOver: false,
    gameStatus: 'Waiting for opponent...'
  });
  const [ws, setWs] = useState(null);

  const handleWebSocketMessage = (event, mounted) => {
    if (!mounted) return;
    console.log('Received message:', event.data);
    const data = JSON.parse(event.data);
    
    const messageHandlers = {
      game_state: () => {
        setGameState(prev => ({
          ...prev,
          board: data.board,
          currentPlayer: data.current_player,
          isMyTurn: data.is_your_turn,
          gameStatus: data.is_your_turn ? 'Your turn!' : "Opponent's turn!",
          isGameOver: false
        }));
      },
      player_joined: () => {
        setGameState(prev => ({
          ...prev,
          isMyTurn: data.is_your_turn,
          gameStatus: `Game started! ${data.is_your_turn ? 'Your turn!' : "Opponent's turn!"}`
        }));
      },
      game_over: () => {
        setGameState(prev => ({
          ...prev,
          isGameOver: true,
          gameStatus: data.winner ? `Game Over! ${data.winner}` : 'Game Over! Draw!'
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
    let websocket = null;
    let retryCount = 0;
    const maxRetries = 3;
    let mounted = true;

    const connectWebSocket = () => {
      if (!mounted) return;
      try {
        if (websocket?.readyState === WebSocket.OPEN) return;

        websocket = new WebSocket('ws://localhost:8000/ws/game');
        
        websocket.onopen = () => {
          if (!mounted) {
            websocket.close();
            return;
          }
          console.log('WebSocket connected successfully');
          setGameState(prev => ({
            ...prev,
            gameStatus: 'Connected! Waiting for opponent...'
          }));
          setWs(websocket);
        };
        
        websocket.onmessage = (event) => handleWebSocketMessage(event, mounted);
        
        websocket.onerror = (error) => {
          if (!mounted) return;
          console.error('WebSocket error:', error);
          setGameState(prev => ({
            ...prev,
            gameStatus: 'Connection error. Retrying...'
          }));
        };
        
        websocket.onclose = () => {
          if (!mounted) return;
          console.log('WebSocket closed');
          setGameState(prev => ({
            ...prev,
            gameStatus: 'Connection lost. Retrying...'
          }));
          
          if (retryCount < maxRetries) {
            retryCount++;
            setTimeout(connectWebSocket, 2000);
          } else {
            setGameState(prev => ({
              ...prev,
              gameStatus: 'Could not connect to game server. Please refresh the page.'
            }));
          }
        };
      } catch (error) {
        if (!mounted) return;
        console.error('WebSocket connection error:', error);
        setGameState(prev => ({
          ...prev,
          gameStatus: 'Failed to connect to game server.'
        }));
      }
    };

    connectWebSocket();

    return () => {
      mounted = false;
      if (websocket) {
        websocket.close();
      }
    };
  }, []);

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

  const renderSquare = (index) => (
    <Square
      value={gameState.board[index]}
      onClick={() => handleSquareClick(index)}
    />
  );

  const renderBoard = () => (
    <table>
      <tbody>
        {[0, 3, 6].map(rowStart => (
          <tr key={rowStart}>
            {[0, 1, 2].map(colOffset => (
              <td key={colOffset}>
                {renderSquare(rowStart + colOffset)}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );

  return (
    <div className="game-container">
      <h2 className="game-status">{gameState.gameStatus}</h2>
      <div className="game-board">
        {renderBoard()}
      </div>
      {gameState.isGameOver && (
        <button 
          className="new-game-button" 
          onClick={startNewGame}
        >
          Start New Game
        </button>
      )}
    </div>
  );
};

export default GameBoard;