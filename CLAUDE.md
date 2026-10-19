# CLAUDE.md

This is a **learning repository**. Its purpose is that the owner comes to
understand game theory, adversarial search and multi-agent learning. Working
code is a means to that, not the goal. See `README.md` for the layout and
`ROADMAP.md` for the learning path and what comes next.

## How we work here

- **Claude implements; the owner studies.** Claude writes the algorithms. The
  code must be written to be read and learned from:
  - Clarity beats speed. Prefer the textbook form of an algorithm. When an
    optimization is added, put it in a separate, named step and explain what
    it buys.
  - Comment the _why_ and the invariants, e.g. "alpha is the best value the
    maximizer is already guaranteed on this path", not the mechanics.
  - Each algorithm gets a matching `docs/concepts/<topic>.md`: the idea, its
    assumptions, when it applies and when it doesn't, a small worked example,
    and how it maps onto the code.
- **Explain as you go.** When delivering an algorithm, summarize the key idea
  and anything surprising, and suggest something the owner could try or predict
  before running an experiment.
- **One roadmap item at a time.** Don't scaffold future phases before they're
  needed: no empty directories, no placeholder modules. Tick items in
  `ROADMAP.md` and update the status table in `README.md` as they land.
- **Be honest about terminology.** Say whether a technique is adversarial
  search, classical game theory or learning, and don't oversell.

## Correctness

AI-written algorithms can be subtly wrong in a way that makes an agent look
strong when it isn't. So:

- Every game and algorithm has tests, including edge cases.
- Wherever possible, test against **exhaustive ground truth**. Small games like
  tic-tac-toe and Kuhn poker can be solved completely, so the tests should check
  against known values (game-tree counts, game value, equilibrium strategies),
  not just "it runs".
- An optimized algorithm must agree with its plain version. For example,
  alpha-beta must return the same value as minimax, and a test should check it.
- Determinism: anything random takes an explicit seed. The same seeds must give
  the same matches.

## Architecture

- Game rules live only in `State` implementations (`src/agt/games/`). Agents
  only see the `State` interface in `src/agt/core.py`. Never special-case a game
  inside an agent. If an agent needs game knowledge, such as an evaluation
  function, pass it in.
- `State` is immutable: `apply` returns a new state. Search code relies on this.
- Extend `core.py` only when a real game needs it, e.g. chance nodes for poker.
  Update its module docstring when you do.
- Register new games in `agt.games.GAMES` and new agents in `agt.agents.AGENTS`
  so the CLI and experiments can use them.
- Keep the simulator UI-free so it can run thousands of games headless.

## Experiments

- Each experiment is `experiments/NNN-short-name/`, with a `README.md` that
  follows `experiments/TEMPLATE.md` and a `run.py` that regenerates every number
  in it: `uv run python experiments/NNN-short-name/run.py`.
- Raw results go to CSV or JSON next to `run.py`, and plots are generated from
  that data by a script, never pasted in by hand.
- Benchmarks compare agents under equal conditions: the same positions, depth or
  compute budget, and swapped seats. Report a confidence interval, not a bare
  win rate.
- Keep **measured results** separate from **interpretation**. Say what the data
  does _not_ establish.

## Tooling

- Python 3.15, managed by uv. Use `uv add <pkg>` for runtime deps and
  `uv add --dev <pkg>` for tooling. Never use `pip install` directly.
- `uv run pytest` must pass and `uv run ruff format && uv run ruff check --fix`
  must be clean before any commit.
- Add a dependency only when an item actually needs it, e.g. NumPy for payoff
  matrices in Phase 2. Don't add one speculatively.
- `local/` is git-ignored and holds private notes. Don't reference it from
  committed files.
