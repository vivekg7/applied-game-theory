"""Alpha-beta pruning: minimax's answer, without searching subtrees that can't change it.

Same assumptions as minimax (two-player, zero-sum, perfect information), the
same full-depth search, and the same decisions, but it skips subtrees that
provably cannot affect the result. How much it skips depends on the order moves
are tried in; this version uses plain `legal_actions()` order so the effect of
move ordering can be measured separately (Experiment 001).

See docs/concepts/alpha-beta.md.
"""

from math import inf

from agt.agents.minimax import SearchStats
from agt.core import State


def alphabeta[A](
    state: State[A],
    maximizer: int,
    alpha: float = -inf,
    beta: float = inf,
    stats: SearchStats | None = None,
) -> float:
    """Minimax value of `state` for `maximizer`, searched within the window (alpha, beta).

    Invariants on entry, for the path from the root to `state`:
      alpha: the maximizer is already guaranteed at least this much elsewhere.
      beta:  the minimizer can already hold the maximizer to at most this elsewhere.

    So only values strictly between alpha and beta can change the decision
    higher up. The return value `v` is "fail-soft":
      alpha < v < beta  ->  v is the exact minimax value
      v <= alpha        ->  the true value is at most v   (an upper bound)
      v >= beta         ->  the true value is at least v  (a lower bound)
    With the default full window (-inf, inf), the result is always exact.
    """
    if stats is not None:
        stats.nodes += 1

    if state.is_terminal():
        return state.returns()[maximizer]

    if state.current_player == maximizer:
        value = -inf
        for action in state.legal_actions():
            value = max(value, alphabeta(state.apply(action), maximizer, alpha, beta, stats))
            if value >= beta:
                # Beta cutoff: this node is already worth >= beta to the maximizer,
                # but the minimizer has a way to hold them to beta elsewhere, so it
                # will never let play reach here. The remaining children can't matter.
                return value
            alpha = max(alpha, value)
        return value

    value = inf
    for action in state.legal_actions():
        value = min(value, alphabeta(state.apply(action), maximizer, alpha, beta, stats))
        if value <= alpha:
            # Alpha cutoff: the mirror image. The minimizer can already push this
            # node down to <= alpha, but the maximizer has alpha guaranteed elsewhere
            # and will avoid it.
            return value
        beta = min(beta, value)
    return value


class AlphaBetaAgent[A]:
    """Plays the move with the highest minimax value, found with alpha-beta.

    Picks exactly the move `MinimaxAgent` would, including its tie-break (the
    first best move in `legal_actions()` order). The root keeps alpha at the
    best value found so far: a later move that is only *as good* comes back as
    a bound <= alpha and is never preferred, and a strictly better one lies
    inside the window, so its value comes back exact.
    """

    def __init__(self) -> None:
        self.last_stats = SearchStats()

    @property
    def name(self) -> str:
        return "alphabeta"

    def act(self, state: State[A]) -> A:
        if state.num_players != 2:
            raise ValueError("alpha-beta assumes a two-player zero-sum game")
        me = state.current_player
        assert me is not None

        stats = SearchStats(nodes=1)  # the root
        best_action, best_value = None, -inf
        for action in state.legal_actions():
            value = alphabeta(state.apply(action), me, alpha=best_value, stats=stats)
            if value > best_value:
                best_action, best_value = action, value
        self.last_stats = stats
        return best_action
