# Roadmap

Roughly 5–7 hours a week. Phases overlap on purpose: build a small version,
watch it fail, then learn the theory that explains the failure. Don't master
one phase before touching the next.

Each phase ends with a **milestone**: something that runs and measures a result.
A phase isn't done when the code compiles.

## Phase 0: Foundations of the platform ✅

- [x] `State` / `Agent` interfaces (`src/agt/core.py`)
- [x] Tic-tac-toe, checked against the known game-tree counts
- [x] Random and human agents
- [x] Match runner with seat swapping, `agt play` / `agt match` CLI

## Phase 1: Adversarial search (weeks 1–2)

- [x] Minimax over the full tic-tac-toe tree, to prove perfect play is a draw
- [ ] Alpha-beta pruning
- [ ] **Experiment 001**: minimax vs. alpha-beta. Count the nodes, check the
      decisions are identical, and measure the effect of move ordering
- [ ] Connect Four: too big to search fully, so it forces a depth limit
- [ ] Depth-limited search with an evaluation function
- [ ] Iterative deepening, transposition tables, move ordering
- [ ] **Experiment 002**: evaluation functions. Does a deeper search with a
      bad evaluation function lose to a shallower search with a good one?

Milestone: compare the strength and the cost of several search configurations.

## Phase 2: Strategic reasoning (weeks 3–4)

- [ ] Normal-form games: payoff matrices for rock-paper-scissors, matching
      pennies, prisoner's dilemma and coordination games
- [ ] Dominance, best responses, pure and mixed Nash equilibria
- [ ] Solving two-player zero-sum games with a linear program
- [ ] Repeated games: an iterated prisoner's dilemma tournament
- [ ] **Experiment**: why a deterministic strategy is exploitable and a mixed
      one isn't

Milestone: show why an unpredictable strategy can beat a deterministic one.

## Phase 3: Sampling and uncertainty (weeks 5–6)

- [ ] MCTS with UCT, on Connect Four
- [ ] **Experiment**: MCTS vs. alpha-beta with the same compute budget
- [ ] Extend the interface for chance nodes and hidden information
- [ ] Kuhn poker
- [ ] Belief states and Bayesian updating

Milestone: compare search-based agents fairly, with equal compute budgets.

## Phase 4: Learning agents (weeks 7–9)

- [ ] Tabular Q-learning with self-play
- [ ] Counterfactual regret minimization (CFR) on Kuhn poker
- [ ] Exploitability as a metric
- [ ] Cross-check against OpenSpiel (check it supports our Python version first)
- [ ] **Experiment**: does a learned strategy generalize beyond the opponents it
      trained against?

Milestone: a learned agent evaluated against opponents it never saw in training.

## Phase 5: Tournament laboratory (weeks 10–12)

- [ ] Round-robin tournaments and Elo or Bradley–Terry ratings
- [ ] Confidence intervals on every reported win rate
- [ ] Stored match results, replays and decision traces
- [ ] Regression tests: a new agent can't silently make an old result wrong
- [ ] Population-based evaluation: non-transitive strategies (A beats B, B
      beats C, C beats A)

Milestone: a new agent enters the arena and is evaluated without changing the
rest of the system.

## Later, maybe

- A web UI for replays and search-tree visualization
- Multi-player games: coalitions and betrayal
- Mechanism design
