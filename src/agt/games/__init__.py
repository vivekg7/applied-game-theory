"""Game rules. Each game is a `State` implementation; see `agt.core`."""

from agt.games.tictactoe import TicTacToeState

# Name -> initial state, used by the CLI and experiments to pick a game by name.
GAMES = {
    "tictactoe": TicTacToeState,
}

__all__ = ["GAMES", "TicTacToeState"]
