"""The two interfaces everything else is built on: a game `State` and an `Agent`.

The rules of a game live entirely in its `State` type; agents only ever see a
state and choose one of its legal actions. Keeping the two apart is what lets
the same game be played by a random agent, a search algorithm, a learned policy
or a human, and lets an algorithm be reused across games.

Scope today: sequential, perfect-information, deterministic games for any
number of players. Chance nodes (dice, card deals) and hidden information
(poker) will extend this interface when the first game that needs them arrives,
rather than being designed in advance.
"""

from typing import Protocol


class State[A](Protocol):
    """An immutable snapshot of a game, generic over the action type `A`.

    `apply` returns a *new* state and never mutates `self`. Search algorithms
    rely on this: they can hold a parent state, try every child, and come back
    without having to undo moves.
    """

    @property
    def num_players(self) -> int: ...

    @property
    def current_player(self) -> int | None:
        """Index of the player to move, or `None` once the game is over."""
        ...

    def legal_actions(self) -> list[A]:
        """Actions available to `current_player`, in a fixed, deterministic order.

        Empty if and only if the state is terminal.
        """
        ...

    def apply(self, action: A) -> State[A]:
        """The state after `current_player` plays `action`. Raises on an illegal action."""
        ...

    def is_terminal(self) -> bool: ...

    def returns(self) -> tuple[float, ...]:
        """Final payoff for each player, indexed by player. Only valid when terminal.

        In a two-player zero-sum game these always sum to zero, e.g. (1, -1).
        """
        ...


class Agent[A](Protocol):
    """Anything that can pick an action in a state.

    Agents that use randomness own a seeded `random.Random`, so a match between
    two agents built with the same seeds replays identically.
    """

    @property
    def name(self) -> str: ...

    def act(self, state: State[A]) -> A: ...
