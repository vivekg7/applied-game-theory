import pytest

from agt.agents import RandomAgent
from agt.arena import play_game, play_series
from agt.games import TicTacToeState


class ScriptedAgent:
    """Plays a fixed list of moves, for tests that need an exact game."""

    def __init__(self, name: str, moves: list[int]) -> None:
        self.name = name
        self._moves = iter(moves)

    def act(self, state):
        return next(self._moves)


class FirstLegalAgent:
    """Always plays the lowest-numbered legal action."""

    def __init__(self, name: str) -> None:
        self.name = name

    def act(self, state):
        return state.legal_actions()[0]


def test_play_game_records_actions_and_returns():
    x = ScriptedAgent("x", [0, 1, 2])
    o = ScriptedAgent("o", [3, 4])
    record = play_game(TicTacToeState(), [x, o])
    assert record.players == ("x", "o")
    assert record.actions == (0, 3, 1, 4, 2)
    assert record.returns == (1.0, -1.0)


def test_play_game_rejects_wrong_number_of_agents():
    with pytest.raises(ValueError):
        play_game(TicTacToeState(), [RandomAgent(0)])


def test_series_swaps_seats():
    # Lowest-free-cell play always ends in an X win (X takes 0, 2, 4, 6), so an
    # identical pair of agents splits a series evenly only if seats alternate.
    result = play_series(TicTacToeState(), FirstLegalAgent("a"), FirstLegalAgent("b"), games=10)
    assert [g.players for g in result.games[:2]] == [("a", "b"), ("b", "a")]
    assert (result.a_wins, result.b_wins, result.draws) == (5, 5, 0)


def test_series_is_reproducible_with_seeds():
    def run():
        result = play_series(TicTacToeState(), RandomAgent(7), RandomAgent(8), games=50)
        return [g.actions for g in result.games]

    assert run() == run()


def test_random_vs_random_scores_about_half():
    """Sanity check on the scoring: with seats swapped, two random agents score about 0.5."""
    result = play_series(TicTacToeState(), RandomAgent(0), RandomAgent(1), games=2000)
    assert result.total == 2000
    assert 0.45 < result.a_score < 0.55
