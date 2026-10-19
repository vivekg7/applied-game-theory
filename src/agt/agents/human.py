"""A human player at the terminal, so you can play against any agent yourself."""

from agt.core import State


class HumanAgent:
    """Reads an action index from stdin. Assumes integer actions, as every game so far uses."""

    @property
    def name(self) -> str:
        return "human"

    def act(self, state: State[int]) -> int:
        legal = state.legal_actions()
        while True:
            raw = input(f"Your move {legal}: ").strip()
            try:
                action = int(raw)
            except ValueError:
                action = None
            if action in legal:
                return action
            print(f"{raw!r} is not a legal move.")
