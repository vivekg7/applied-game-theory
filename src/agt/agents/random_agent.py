"""The baseline every other agent must beat: a uniformly random legal move."""

import random

from agt.core import State


class RandomAgent[A]:
    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    @property
    def name(self) -> str:
        return "random"

    def act(self, state: State[A]) -> A:
        return self._rng.choice(state.legal_actions())
