"""Agents: anything that picks an action given a state. See `agt.core.Agent`."""

from collections.abc import Callable

from agt.agents.alphabeta import AlphaBetaAgent
from agt.agents.human import HumanAgent
from agt.agents.minimax import MinimaxAgent
from agt.agents.random_agent import RandomAgent
from agt.core import Agent

# Name -> factory taking a seed, used by the CLI and experiments to pick agents by name.
AGENTS: dict[str, Callable[[int | None], Agent]] = {
    "random": lambda seed: RandomAgent(seed),
    "minimax": lambda seed: MinimaxAgent(),
    "alphabeta": lambda seed: AlphaBetaAgent(),
    "human": lambda seed: HumanAgent(),
}

__all__ = ["AGENTS", "AlphaBetaAgent", "HumanAgent", "MinimaxAgent", "RandomAgent"]
