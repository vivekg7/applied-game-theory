import pytest

from agt.agents import MinimaxAgent, RandomAgent
from agt.agents.minimax import SearchStats, minimax
from agt.arena import play_series
from agt.games import TicTacToeState


def play(*actions: int) -> TicTacToeState:
    state = TicTacToeState()
    for action in actions:
        state = state.apply(action)
    return state


def test_empty_board_is_a_draw():
    """The classic result: tic-tac-toe is a draw under perfect play."""
    assert minimax(TicTacToeState(), maximizer=0) == 0
    assert minimax(TicTacToeState(), maximizer=1) == 0


def test_full_search_visits_every_node_of_the_tree():
    # Plain minimax has no pruning, so it must visit exactly the 549,946 nodes
    # that test_tictactoe counts by brute force.
    stats = SearchStats()
    minimax(TicTacToeState(), maximizer=0, stats=stats)
    assert stats.nodes == 549_946


def test_every_opening_move_is_a_draw():
    root = TicTacToeState()
    assert [minimax(root.apply(a), maximizer=0) for a in range(9)] == [0] * 9


@pytest.mark.parametrize(
    "actions, x_value",
    [
        ((0, 1), 1),  # X corner, O adjacent edge: X forces a win
        ((0, 4), 0),  # X corner, O centre: the correct reply, draw
        ((4, 1), 1),  # X centre, O edge: X forces a win
        ((4, 0), 0),  # X centre, O corner: the correct reply, draw
        ((0, 3, 1, 4), 1),  # X to move with an immediate win on 2
        ((0, 4, 8, 2), 1),  # X's forced block on 6 also forks 3 and 7: X wins
    ],
)
def test_known_positions(actions, x_value):
    state = play(*actions)
    assert minimax(state, maximizer=0) == x_value
    assert minimax(state, maximizer=1) == -x_value  # zero-sum: one number suffices


def test_terminal_value_is_the_payoff():
    assert minimax(play(0, 3, 1, 4, 2), maximizer=0) == 1


def test_agent_takes_an_immediate_win():
    # X has 0,1 and can win on 2; it must not play elsewhere.
    assert MinimaxAgent().act(play(0, 3, 1, 4)) == 2


def test_agent_blocks_an_immediate_threat():
    # O has 4 and 2 (threatening 6 via the anti-diagonal); X must block.
    assert MinimaxAgent().act(play(0, 4, 8, 2)) == 6


def test_agent_reports_search_cost():
    agent = MinimaxAgent()
    agent.act(TicTacToeState())
    assert agent.last_stats.nodes == 549_946


def _outcomes_against_every_opponent(agent_seat: int) -> set[float]:
    """Play the minimax agent against *every possible* opponent strategy at once.

    At the agent's turns follow its single chosen move; at the opponent's turns
    branch on every legal move. The leaves are all games the agent can end up in,
    whatever the opponent does.
    """
    agent = MinimaxAgent()
    outcomes: set[float] = set()
    stack = [TicTacToeState()]
    while stack:
        state = stack.pop()
        if state.is_terminal():
            outcomes.add(state.returns()[agent_seat])
        elif state.current_player == agent_seat:
            stack.append(state.apply(agent.act(state)))
        else:
            stack.extend(state.apply(a) for a in state.legal_actions())
    return outcomes


@pytest.mark.parametrize("seat", [0, 1])
def test_agent_never_loses_to_any_opponent(seat):
    """Exhaustive proof of optimality, not a sampled win rate."""
    assert -1.0 not in _outcomes_against_every_opponent(seat)


def test_minimax_vs_minimax_is_a_draw():
    result = play_series(TicTacToeState(), MinimaxAgent(), MinimaxAgent(), games=1)
    assert result.draws == 1


def test_agent_rejects_non_two_player_games():
    class ThreePlayer:
        num_players = 3
        current_player = 0

    with pytest.raises(ValueError):
        MinimaxAgent().act(ThreePlayer())


def test_beats_random():
    # A smoke test through the arena; optimality itself is proven exhaustively above.
    # Kept small because each game where minimax plays X costs a full-tree search.
    result = play_series(TicTacToeState(), MinimaxAgent(), RandomAgent(0), games=4)
    assert result.b_wins == 0
    assert result.a_wins >= 2
