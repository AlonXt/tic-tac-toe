import React from 'react';
import GameBoard from './GameBoard';
import GameLobby from './GameLobby';

function App() {
  // Check if there's a game ID in the URL
  const hasGameId = new URLSearchParams(window.location.search).has('id');

  return (
    <div className="min-h-screen bg-gray-100">
      <h1 className="text-4xl font-bold text-center py-6 text-gray-800">Tic-Tac-Toe</h1>
      {hasGameId ? <GameBoard /> : <GameLobby />}
    </div>
  );
}

export default App;