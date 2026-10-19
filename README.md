# applied-game-theory

Learning game theory, adversarial search, strategic agents and multi-agent
learning by building them and measuring what happens.

The repo is three things at once:

- **A learning path.** Concepts run from minimax to equilibrium computation and
  multi-agent learning, in [ROADMAP.md](ROADMAP.md).
- **A research notebook.** Every experiment in [`experiments/`](experiments/)
  states a question and a hypothesis, then records what the measurements
  actually showed.
- **A small platform.** Games, agents and the match runner share one interface,
  so a new algorithm can play every existing game, and a new game can be played
  by every existing agent.

"Game theory" is used broadly here. Alpha-beta pruning is adversarial search,
not game theory in the economist's sense. The repo covers both fields and where
they meet, and the docs say which is which.

## Layout

```
src/agt/
  core.py        State and Agent interfaces: the contract everything else uses
  games/         game rules, one State implementation per game
  agents/        anything that picks a move: random, human, search, learned...
  arena.py       play a game or a seat-swapping series between agents
  cli.py         `agt play` / `agt match`
tests/           correctness tests, including exhaustive ground truth where feasible
docs/concepts/   the theory: what each idea is, its assumptions, why it works
experiments/     numbered experiments: question, method, results, interpretation
```

Each concept has three layers: the **theory** (`docs/concepts/`), the
**implementation** (`src/agt/` plus tests) and the **evidence** (`experiments/`).
More advanced algorithms get a fourth layer, **failure analysis**: the cases
where they lose or where an assumption breaks.

## Setup

Requires [uv](https://docs.astral.sh/uv/). uv reads the Python version (3.15)
from `.python-version` and installs the pinned dependencies from `uv.lock`.

```sh
uv sync                                       # create .venv and install everything
uv run pytest                                 # run the tests
uv run agt play tictactoe                     # play against the random agent
uv run agt play tictactoe --opponent minimax  # ...or against perfect play
uv run agt play tictactoe --second            # ...letting it move first
uv run agt match tictactoe random random -n 10000
```

Before committing, run `uv run ruff format && uv run ruff check --fix`.

## Status

| Phase | Topic                                     | Theory | Code | Evidence |
| ----- | ----------------------------------------- | :----: | :--: | :------: |
| 0     | Game interface, tic-tac-toe, match runner |   ✅   |  ✅  |    —     |
| 1     | Minimax                                   |   ✅   |  ✅  |    —     |
| 1     | Alpha-beta                                |        |      |          |

See [ROADMAP.md](ROADMAP.md) for everything that comes after.

## References

- [MIT 6.7980: Topics in Multiagent Learning](https://www.mit.edu/~6.7980/):
  regret minimization, equilibrium computation, modern multi-agent learning.
- [MIT 14.12: Economic Applications of Game Theory](https://ocw.mit.edu/courses/14-12-economic-applications-of-game-theory-fall-2025/):
  classical foundations.
- [OpenSpiel](https://openspiel.readthedocs.io/): reference games and algorithms
  to cross-check our own implementations against.
- [PettingZoo](https://pettingzoo.farama.org/): standard multi-agent RL
  environment API, for the learning phases.
- Russell & Norvig, _Artificial Intelligence: A Modern Approach_, chapter on
  adversarial search: minimax, alpha-beta and MCTS.

## License

GPL-3.0. See [LICENSE](LICENSE).
