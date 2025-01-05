from typing import Dict, Optional


class GameState:
    def __init__(self):
        self.reset_game()
        self.players: Dict[str, str] = {}

    def reset_game(self):
        self.board = [''] * 9
        self.current_player = 'X'
        self.winner: Optional[str] = None

    def make_move(self, position: int, symbol: str) -> bool:
        if 0 <= position < 9 and self.board[position] == '' and symbol == self.current_player:
            self.board[position] = symbol
            self.check_winner()
            self.current_player = 'O' if symbol == 'X' else 'X'
            return True
        return False

    def check_winner(self):
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]  # Diagonals
        ]

        for combo in winning_combinations:
            if (self.board[combo[0]] != '' and
                    self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]]):
                self.winner = self.board[combo[0]]
                return

        if '' not in self.board:
            self.winner = 'draw'
