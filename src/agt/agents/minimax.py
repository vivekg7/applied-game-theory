"""Minimax: optimal play in two-player, zero-sum, perfect-information games.

The textbook form, with no pruning and no depth limit: it searches the whole
tree below the current state. That's only feasible for tiny games like
tic-tac-toe, and that is the point. This version is the reference that faster
searches (alpha-beta, transposition tables) must agree with.

See docs/concepts/minimax.md.
"""

from dataclasses import dataclass

from agt.core import State


@dataclass
class SearchStats:
    """Work done by one search, so algorithms can be compared on cost, not just result."""

    nodes: int = 0  # states visited, including the root and every leaf


def minimax[A](state: State[A], maximizer: int, stats: SearchStats | None = None) -> float:
    """The game-theoretic value of `state` for `maximizer`, assuming both sides play perfectly.

    "Perfectly" means: `maximizer` picks the child with the highest value, and the
    opponent picks the child with the *lowest* value for `maximizer`. In a
    zero-sum game, minimizing your opponent's payoff is exactly the same as
    maximizing your own, which is why one number per node is enough.
    """
    if stats is not None:
        stats.nodes += 1

    if state.is_terminal():
        return state.returns()[maximizer]

    child_values = (minimax(state.apply(a), maximizer, stats) for a in state.legal_actions())
    if state.current_player == maximizer:
        return max(child_values)
    return min(child_values)


class MinimaxAgent[A]:
    """Plays the move with the highest minimax value.

    Ties go to the first move in `legal_actions()` order, so the agent is
    deterministic. Minimax only sees *values* under perfect play, so it can't
    tell a draw where the opponent has many chances to blunder from a draw
    where they have none. Against a weak opponent, that tie-break is the only
    thing deciding between "safe" moves.
    """

    def __init__(self) -> None:
        self.last_stats = SearchStats()

    @property
    def name(self) -> str:
        return "minimax"

    def act(self, state: State[A]) -> A:
        if state.num_players != 2:
            raise ValueError("minimax assumes a two-player zero-sum game")
        me = state.current_player
        assert me is not None

        stats = SearchStats(nodes=1)  # the root
        best_action, best_value = None, float("-inf")
        for action in state.legal_actions():
            value = minimax(state.apply(action), me, stats)
            if value > best_value:  # strict: keep the first of equally good moves
                best_action, best_value = action, value
        self.last_stats = stats
        return best_action
