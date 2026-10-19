"""Command line entry point: `uv run agt play ...` and `uv run agt match ...`."""

import argparse

from agt.agents import AGENTS
from agt.arena import play_game, play_series
from agt.games import GAMES


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="agt", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    play = sub.add_parser("play", help="play a game yourself against an agent")
    play.add_argument("game", choices=GAMES)
    play.add_argument("--opponent", choices=AGENTS, default="random")
    play.add_argument("--second", action="store_true", help="let the opponent move first")
    play.add_argument("--seed", type=int, default=None)

    match = sub.add_parser("match", help="run a series between two agents")
    match.add_argument("game", choices=GAMES)
    match.add_argument("agent_a", choices=AGENTS)
    match.add_argument("agent_b", choices=AGENTS)
    match.add_argument("-n", "--games", type=int, default=1000)
    match.add_argument("--seed", type=int, default=0)

    args = parser.parse_args(argv)
    initial = GAMES[args.game]()

    if args.command == "play":
        human = AGENTS["human"](None)
        opponent = AGENTS[args.opponent](args.seed)
        seats = [opponent, human] if args.second else [human, opponent]
        record = play_game(initial, [_Narrator(a) for a in seats])
        final = initial
        for action in record.actions:
            final = final.apply(action)
        print(f"\n{final}")
        outcome = record.returns[seats.index(human)]
        print("\nYou win!" if outcome > 0 else "\nYou lose." if outcome < 0 else "\nDraw.")
    else:
        # Distinct seeds so two copies of the same random agent don't mirror each other.
        a = AGENTS[args.agent_a](args.seed)
        b = AGENTS[args.agent_b](args.seed + 1)
        print(play_series(initial, a, b, args.games))


class _Narrator:
    """Wraps an agent so each position and chosen move is printed during `play`."""

    def __init__(self, agent) -> None:
        self._agent = agent
        self.name = agent.name

    def act(self, state):
        print(f"\n{state}\n")
        action = self._agent.act(state)
        if self.name != "human":
            print(f"{self.name} plays {action}")
        return action


if __name__ == "__main__":
    main()
