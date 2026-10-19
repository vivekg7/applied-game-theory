import pytest

from agt.games.tictactoe import TicTacToeState


def play(*actions: int) -> TicTacToeState:
    state = TicTacToeState()
    for action in actions:
        state = state.apply(action)
    return state


def test_initial_state():
    state = TicTacToeState()
    assert state.current_player == 0
    assert state.legal_actions() == list(range(9))
    assert not state.is_terminal()


def test_apply_does_not_mutate():
    state = TicTacToeState()
    child = state.apply(4)
    assert state.board == (None,) * 9
    assert child.board[4] == 0
    assert child.current_player == 1


@pytest.mark.parametrize(
    "actions, winner",
    [
        ((0, 3, 1, 4, 2), 0),  # X top row
        ((0, 1, 3, 4, 8, 7), 1),  # O middle column
        ((0, 1, 4, 2, 8), 0),  # X main diagonal
        ((0, 2, 1, 4, 3, 6), 1),  # O anti-diagonal
    ],
)
def test_wins(actions, winner):
    state = play(*actions)
    assert state.is_terminal()
    assert state.current_player is None
    assert state.legal_actions() == []
    assert state.returns() == ((1.0, -1.0) if winner == 0 else (-1.0, 1.0))


def test_draw():
    # X O X / X O O / O X X
    state = play(0, 1, 2, 4, 3, 5, 7, 6, 8)
    assert state.is_terminal()
    assert state.winner is None
    assert state.returns() == (0.0, 0.0)


def test_win_on_last_move_is_a_win_not_a_draw():
    # X O X / O X O / O X X: X completes the diagonal on the ninth move.
    state = play(0, 1, 2, 3, 4, 5, 7, 6, 8)
    assert None not in state.board
    assert state.returns() == (1.0, -1.0)


@pytest.mark.parametrize("action", [-1, 9, 4])
def test_illegal_actions_raise(action):
    state = play(4)
    with pytest.raises(ValueError):
        state.apply(action)


def test_cannot_move_after_game_over():
    with pytest.raises(ValueError):
        play(0, 3, 1, 4, 2).apply(5)


def test_returns_undefined_before_end():
    with pytest.raises(ValueError):
        TicTacToeState().returns()


def test_full_game_tree_matches_known_counts():
    """The complete tree has 549,946 nodes and 255,168 distinct games.

    These are well-known published figures, so matching them is strong evidence
    the rules (in particular, stopping at the first win) are implemented right.
    """
    nodes = terminals = 0
    x_wins = o_wins = 0
    stack = [TicTacToeState()]
    while stack:
        state = stack.pop()
        nodes += 1
        if state.is_terminal():
            terminals += 1
            x_wins += state.winner == 0
            o_wins += state.winner == 1
        else:
            stack.extend(state.apply(a) for a in state.legal_actions())
    assert nodes == 549_946
    assert terminals == 255_168
    assert x_wins == 131_184
    assert o_wins == 77_904
