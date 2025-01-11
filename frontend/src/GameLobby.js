import React, { useState } from 'react';

const GameLobby = () => {
  const [isCreating, setIsCreating] = useState(false);
  const [gameLink, setGameLink] = useState('');

  const createGame = async () => {
    setIsCreating(true);
    try {
      const response = await fetch('http://localhost:8000/api/games/create', {
        method: 'POST',
      });
      const data = await response.json();
      const gameUrl = `${window.location.origin}?id=${data.game_id}`;
      setGameLink(gameUrl);
    } catch (error) {
      console.error('Error creating game:', error);
    } finally {
      setIsCreating(false);
    }
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(gameLink);
      alert('Game link copied to clipboard!');
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      alert('Failed to copy to clipboard. Please copy the link manually.');
    }
  };

  const startGame = () => {
    window.location.href = gameLink;
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <div className="p-8 bg-white rounded-lg shadow-md">
        <h1 className="text-3xl font-bold mb-6 text-center">Tic-Tac-Toe</h1>
        
        {!gameLink ? (
          <button
            onClick={createGame}
            disabled={isCreating}
            className="w-full py-3 px-6 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-400"
          >
            {isCreating ? 'Creating game...' : 'Create New Game'}
          </button>
        ) : (
          <div className="space-y-4">
            <p className="text-sm text-gray-600">Share this link with your opponent:</p>
            <div className="flex gap-2">
              <input
                type="text"
                value={gameLink}
                readOnly
                className="flex-1 p-2 border rounded"
              />
              <button
                onClick={copyToClipboard}
                className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
              >
                Copy
              </button>
            </div>
            <button
              onClick={startGame}
              className="w-full py-3 px-6 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Start Game
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default GameLobby;