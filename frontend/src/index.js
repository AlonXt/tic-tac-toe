import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import GameBoard from './GameBoard';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <div className="App">
    <h1 className="game-title">Tic-Tac-Toe</h1>
    <GameBoard />
  </div>
);
