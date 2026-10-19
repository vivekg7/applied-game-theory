"""Alpha-beta must agree with minimax everywhere, so most tests compare the two.

Ground truth comes from a memoized minimax over all 5,478 reachable tic-tac-toe
positions. Memoizing is safe here because a tic-tac-toe value depends only on
the board (whose turn it is follows from the board), and it keeps checking
every position fast.
"""

import random
from functools import cache
from math import inf

import pytest

from agt.agents import AlphaBetaAgent, MinimaxAgent
from agt.agents.alphabeta import alphabeta
from agt.agents.minimax import SearchStats, minimax
from agt.arena import play_series
from agt.games import TicTacToeState


@cache
def true_value(state: TicTacToeState) -> float:
    """Minimax value for X (player 0), memoized by state."""
    if state.is_terminal():
        return state.returns()[0]
    values = [true_value(state.apply(a)) for a in state.legal_actions()]
    return max(values) if state.current_player == 0 else min(values)


def all_positions() -> list[TicTacToeState]:
    seen: dict[TicTacToeState, None] = {}  # insertion-ordered, so the list is deterministic
    stack = [TicTacToeState()]
    while stack:
        state = stack.pop()
        if state not in seen:
            seen[state] = None
            stack.extend(state.apply(a) for a in state.legal_actions())
    return list(seen)


POSITIONS = all_positions()
NONTERMINAL = [s for s in POSITIONS if not s.is_terminal()]


def test_ground_truth_sanity():
    assert len(POSITIONS) == 5_478
    assert true_value(TicTacToeState()) == minimax(TicTacToeState(), maximizer=0) == 0


def test_full_window_value_matches_minimax_at_every_position():
    for state in POSITIONS:
        for player in (0, 1):
            expected = true_value(state) if player == 0 else -true_value(state)
            assert alphabeta(state, maximizer=player) == expected, (state, player)


def test_narrow_windows_return_correct_bounds():
    """The fail-soft contract: exact inside the window, a valid bound outside it."""
    rng = random.Random(0)
    edges = [-inf, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, inf]
    for state in rng.sample(POSITIONS, 1500):
        alpha, beta = sorted(rng.sample(edges, 2))
        v = alphabeta(state, maximizer=0, alpha=alpha, beta=beta)
        truth = true_value(state)
        if v <= alpha:
            assert truth <= v
        elif v >= beta:
            assert truth >= v
        else:
            assert truth == v


def _minimax_choice(state: TicTacToeState) -> int:
    """The move MinimaxAgent plays: the first action with the best value."""
    me = state.current_player
    sign = 1 if me == 0 else -1
    best = max(sign * true_value(state.apply(a)) for a in state.legal_actions())
    return next(a for a in state.legal_actions() if sign * true_value(state.apply(a)) == best)


def test_agent_picks_the_same_move_as_minimax_at_every_position():
    agent = AlphaBetaAgent()
    for state in NONTERMINAL:
        assert agent.act(state) == _minimax_choice(state), state


def test_agent_matches_the_real_minimax_agent_directly():
    # The test above uses a memoized stand-in for MinimaxAgent; check the stand-in
    # against the real agent on a spread of positions, including the root.
    sample = [TicTacToeState(), *random.Random(1).sample(NONTERMINAL, 40)]
    for state in sample:
        assert AlphaBetaAgent().act(state) == MinimaxAgent().act(state) == _minimax_choice(state)


def test_prunes_but_never_searches_more_than_minimax():
    for state in [TicTacToeState(), *random.Random(2).sample(NONTERMINAL, 40)]:
        ab, mm = SearchStats(), SearchStats()
        alphabeta(state, maximizer=0, stats=ab)
        minimax(state, maximizer=0, stats=mm)
        assert ab.nodes <= mm.nodes
    # From the empty board the saving is large, not marginal.
    ab = SearchStats()
    alphabeta(TicTacToeState(), maximizer=0, stats=ab)
    assert ab.nodes < 549_946 // 2


def test_exact_node_count_from_the_empty_board():
    """Pin the pruning, not just the answer.

    A bug that weakens pruning (e.g. never raising alpha) still returns correct
    values and moves, so only the node count can catch it. With moves tried in
    `legal_actions()` order the count is deterministic: 18,297 of minimax's 549,946.
    """
    agent = AlphaBetaAgent()
    agent.act(TicTacToeState())
    assert agent.last_stats.nodes == 18_297
    stats = SearchStats()
    alphabeta(TicTacToeState(), maximizer=0, stats=stats)
    assert stats.nodes == 18_297


def test_agent_rejects_non_two_player_games():
    class ThreePlayer:
        num_players = 3
        current_player = 0

    with pytest.raises(ValueError):
        AlphaBetaAgent().act(ThreePlayer())


def test_alphabeta_vs_minimax_is_a_draw():
    result = play_series(TicTacToeState(), AlphaBetaAgent(), MinimaxAgent(), games=2)
    assert result.draws == 2
