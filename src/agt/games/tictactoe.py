"""Tic-tac-toe: the smallest game worth searching.

Small enough that its whole game tree fits in memory (549,946 nodes), so
algorithms can be checked against exhaustive ground truth: perfect play from
both sides is a draw, and alpha-beta must pick a move with the same minimax
value as plain minimax.

Cells are numbered 0-8, row by row::

    0 | 1 | 2
    3 | 4 | 5
    6 | 7 | 8

An action is the index of the cell to mark. Player 0 is X and moves first.
"""

from dataclasses import dataclass, field

type Cell = int | None  # owning player index, or None if empty

LINES: tuple[tuple[int, int, int], ...] = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
    (0, 4, 8), (2, 4, 6),             # diagonals
)  # fmt: skip

SYMBOLS = ("X", "O")


@dataclass(frozen=True, slots=True)
class TicTacToeState:
    board: tuple[Cell, ...] = (None,) * 9
    to_move: int = 0
    # Derived from `board`; computed once so repeated queries during search are cheap.
    winner: int | None = field(init=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "winner", _find_winner(self.board))

    @property
    def num_players(self) -> int:
        return 2

    @property
    def current_player(self) -> int | None:
        return None if self.is_terminal() else self.to_move

    def legal_actions(self) -> list[int]:
        if self.is_terminal():
            return []
        return [i for i, cell in enumerate(self.board) if cell is None]

    def apply(self, action: int) -> TicTacToeState:
        if self.is_terminal():
            raise ValueError("game is over")
        if not 0 <= action < 9 or self.board[action] is not None:
            raise ValueError(f"illegal action {action!r}")
        board = list(self.board)
        board[action] = self.to_move
        return TicTacToeState(tuple(board), 1 - self.to_move)

    def is_terminal(self) -> bool:
        return self.winner is not None or None not in self.board

    def returns(self) -> tuple[float, float]:
        if not self.is_terminal():
            raise ValueError("returns are only defined for terminal states")
        if self.winner is None:
            return (0.0, 0.0)
        return (1.0, -1.0) if self.winner == 0 else (-1.0, 1.0)

    def __str__(self) -> str:
        def show(i: int) -> str:
            cell = self.board[i]
            return str(i) if cell is None else SYMBOLS[cell]

        rows = (" | ".join(show(r * 3 + c) for c in range(3)) for r in range(3))
        return "\n---------\n".join(rows)


def _find_winner(board: tuple[Cell, ...]) -> int | None:
    for a, b, c in LINES:
        if board[a] is not None and board[a] == board[b] == board[c]:
            return board[a]
    return None
