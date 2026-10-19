"""Running matches between agents.

A single win rate is easy to misread, so a series always swaps seats: in most
games moving first is an advantage (tic-tac-toe X wins far more often between
random players), and an agent that only ever plays first would look stronger
than it is.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field

from agt.core import Agent, State


@dataclass(frozen=True)
class GameRecord:
    """Everything needed to replay and score one game."""

    players: tuple[str, ...]  # agent name in each seat
    actions: tuple[object, ...]
    returns: tuple[float, ...]


def play_game[A](initial: State[A], agents: Sequence[Agent[A]]) -> GameRecord:
    """Play one game to the end, `agents[i]` taking seat `i`."""
    if len(agents) != initial.num_players:
        raise ValueError(f"game needs {initial.num_players} agents, got {len(agents)}")
    state = initial
    actions: list[A] = []
    while not state.is_terminal():
        player = state.current_player
        assert player is not None
        action = agents[player].act(state)
        actions.append(action)
        state = state.apply(action)
    return GameRecord(
        players=tuple(agent.name for agent in agents),
        actions=tuple(actions),
        returns=state.returns(),
    )


@dataclass
class SeriesResult:
    """Outcomes from the point of view of agent A in a two-player series."""

    a_name: str
    b_name: str
    a_wins: int = 0
    b_wins: int = 0
    draws: int = 0
    games: list[GameRecord] = field(default_factory=list, repr=False)

    @property
    def total(self) -> int:
        return self.a_wins + self.b_wins + self.draws

    @property
    def a_score(self) -> float:
        """A's average score with a win as 1, a draw as 0.5 and a loss as 0."""
        return (self.a_wins + 0.5 * self.draws) / self.total if self.total else 0.0

    def __str__(self) -> str:
        return (
            f"{self.a_name} vs {self.b_name} over {self.total} games: "
            f"{self.a_wins} wins, {self.draws} draws, {self.b_wins} losses "
            f"(score {self.a_score:.3f})"
        )


def play_series[A](
    initial: State[A], agent_a: Agent[A], agent_b: Agent[A], games: int
) -> SeriesResult:
    """Play `games` two-player games, A taking seat 0 in even games and seat 1 in odd ones."""
    result = SeriesResult(agent_a.name, agent_b.name)
    for i in range(games):
        a_seat = i % 2
        seats = (agent_a, agent_b) if a_seat == 0 else (agent_b, agent_a)
        record = play_game(initial, seats)
        result.games.append(record)
        a_return, b_return = record.returns[a_seat], record.returns[1 - a_seat]
        if a_return > b_return:
            result.a_wins += 1
        elif b_return > a_return:
            result.b_wins += 1
        else:
            result.draws += 1
    return result
