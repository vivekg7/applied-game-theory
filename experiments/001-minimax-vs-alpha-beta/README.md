# Experiment 001: Minimax vs. alpha-beta, and the effect of move ordering

**Field:** adversarial search.

## Question

On tic-tac-toe, how much work does alpha-beta save over minimax, does it always
make the same decision, and how much of the saving depends on the order in
which moves are tried?

## Hypothesis

Written before running anything.

- **Minimax** visits 549,946 nodes from the empty board under _every_
  ordering. It never prunes, so order can't matter.
- **Natural order** (cells 0–8) gives 18,297, already measured in
  [alpha-beta.md](../../docs/concepts/alpha-beta.md), and the same move as
  minimax at every position.
- **Reverse order** (8–0) gives _exactly_ 18,297 as well. Cell `i` ↦ `8 − i`
  is a 180° rotation of the board, a symmetry of the game, so searching in
  reverse order is the natural-order search of a rotated board.
- **Centre, then corners, then edges** prunes more than natural order: the
  centre and corners are the strong cells, so best moves come earlier.
- **Tactical** (wins first, then blocks, then centre/corners/edges) prunes
  more still: it puts forced moves first, which are often the only good ones.
- **Oracle best-first** (perfect ordering, cheating with the true values) is
  the lowest, but well above the `√549,946 ≈ 742` that the `b^(d/2)` rule of
  thumb suggests. That rule assumes a uniform tree, and tic-tac-toe's
  branching factor shrinks every move and many lines end early.
- **Oracle worst-first** is close to minimax but _below_ it. With perfect
  worst-first ordering a cutoff can only happen on the last child, which
  prunes nothing, except that values in tic-tac-toe are only −1, 0 and 1. Ties
  are everywhere, and a tie can reach the bound before the last child.
- **Random order** lands somewhere between natural and worst-first, with a
  wide spread across seeds.

## Setup

- **Game:** tic-tac-toe. Two sets of starting positions: the empty board, and
  each of the 4,520 reachable non-terminal positions in turn.
- **Agents:** `MinimaxAgent` and `AlphaBetaAgent`, unmodified, full depth. A
  node is one state visited, counted by `SearchStats`.
- **Orderings.** Alpha-beta isn't changed. Each ordering wraps the game state
  so that `legal_actions()` reports the same moves in a different order. Ties
  always keep natural order.

  | Ordering              | Moves tried first                                                                    |
  | --------------------- | ------------------------------------------------------------------------------------ |
  | natural               | cells 0–8, the order `TicTacToeState` reports                                        |
  | reverse               | cells 8–0                                                                            |
  | centre-corners-edges  | 4, then 0 2 6 8, then 1 3 5 7                                                        |
  | tactical              | a move that wins now, then one that blocks, then centre-corners-edges                |
  | oracle best-first     | highest true value for the mover. Uses the answer, so it isn't a real agent          |
  | oracle, tactical ties | as above, with ties broken by tactical (added after the first run)                   |
  | oracle worst-first    | lowest true value first: the worst case                                              |
  | random                | a fresh shuffle at every node. 200 seeds from the empty board, 20 over all positions |

- **Decisions.** "Same move" compares with minimax's move, i.e. the first best
  move in natural order. "Optimal" means the move has the best true value.
- Everything is deterministic except the random orderings, which are seeded.
  So only those get a confidence interval: a normal-approximation 95% interval
  for the mean over seeds.

## Results

Raw data: [`root.csv`](root.csv) (one row per search from the empty board) and
[`all_positions.csv`](all_positions.csv) (one row per ordering, summed over
positions). The tables are printed by `run.py`.

**From the empty board**

| Search    | Ordering              |                                 Nodes | % of minimax |   Move |
| --------- | --------------------- | ------------------------------------: | -----------: | -----: |
| minimax   | natural               |                               549,946 |      100.00% |      0 |
| minimax   | reverse               |                               549,946 |      100.00% |      8 |
| alphabeta | natural               |                                18,297 |        3.33% |      0 |
| alphabeta | reverse               |                                18,297 |        3.33% |      8 |
| alphabeta | centre-corners-edges  |                                 7,275 |        1.32% |      4 |
| alphabeta | tactical              |                                 2,096 |        0.38% |      4 |
| alphabeta | oracle best-first     |                                 2,312 |        0.42% |      0 |
| alphabeta | oracle, tactical ties |                                 1,774 |        0.32% |      4 |
| alphabeta | oracle worst-first    |                               198,837 |       36.16% |      0 |
| alphabeta | random, 200 seeds     | 14,661 ± 232 (min 10,829, max 19,260) |        2.67% | varies |

197 of 200 random orderings visit fewer nodes than natural order.

**Summed over all 4,520 non-terminal positions**

| Search    | Ordering              |     Total nodes | % of minimax | Same move as minimax | Optimal move |
| --------- | --------------------- | --------------: | -----------: | -------------------: | -----------: |
| minimax   | natural               |       2,125,535 |      100.00% |                4,520 |        4,520 |
| alphabeta | natural               |         274,507 |       12.91% |                4,520 |        4,520 |
| alphabeta | reverse               |         274,507 |       12.91% |                2,406 |        4,520 |
| alphabeta | centre-corners-edges  |         197,222 |        9.28% |                3,518 |        4,520 |
| alphabeta | tactical              |         102,985 |        4.85% |                3,372 |        4,520 |
| alphabeta | oracle best-first     |         112,630 |        5.30% |                4,520 |        4,520 |
| alphabeta | oracle, tactical ties |          95,769 |        4.51% |                3,372 |        4,520 |
| alphabeta | oracle worst-first    |       1,061,309 |       49.93% |                4,520 |        4,520 |
| alphabeta | random, 20 seeds      | 250,389 ± 1,323 |       11.78% |         3,187 (mean) |  4,520 (min) |

## Interpretation

**Decisions.** Alpha-beta made an optimal move at every one of the 4,520
positions under every ordering, including all 20 random seeds. It made
_minimax's exact_ move only when it tried moves in minimax's order (natural,
and oracle best-first, whose ties fall back to natural order). That's
expected: tic-tac-toe has many equally good moves, and both agents take the
first one they find. "Same decision" means the same value; the same move
needs the same tie-break too.

**Savings.** With no thought given to ordering, alpha-beta visits 3.3% of
minimax's nodes from the empty board, and 12.9% averaged over all positions.
The saving is likely smaller later in the game because the trees there are
shallow, so there is less below each cutoff to skip.

Hypotheses, checked one by one:

| Prediction                                   | Result                                                                               |
| -------------------------------------------- | ------------------------------------------------------------------------------------ |
| Minimax is the same under every ordering     | ✅ 549,946 under both                                                                |
| Reverse = natural exactly (180° symmetry)    | ✅ 18,297 from the root and 274,507 in total. Different moves, same work             |
| Centre-corners-edges beats natural           | ✅ 2.5× fewer nodes from the root                                                    |
| Tactical beats centre-corners-edges          | ✅ 3.5× fewer still                                                                  |
| The oracle is the lowest                     | ❌ Tactical (2,096) beat it (2,312). See below                                       |
| The oracle stays well above 742              | ✅ 1,774 at best, 2.4× the `b^(d/2)` estimate                                        |
| Worst-first is close to minimax              | ❌ 36% of minimax from the root, 50% overall: far more pruning than "close" suggests |
| Random lands between natural and worst-first | ❌ Random is _better_ than natural: 197 of 200 seeds beat it                         |

**Why a cheap heuristic beat the oracle.** "Best move first" isn't well
defined when moves tie, and in tic-tac-toe nearly everything ties. The oracle
can't tell a move that wins _now_ (a leaf, one node) from one that wins in
five moves (a whole subtree). Both are worth 1. A cutoff only needs _some_
move that reaches the bound, and the cheapest one is best. Tactical puts
immediate wins first, so its refutations are often a single node. To test
this, the oracle was rerun with ties broken by tactical: 1,774 nodes, the
lowest of all. So perfect ordering by _value_ is not minimal: what matters is
the cheapest move that proves the bound.

**Why worst-first still prunes.** Under worst-first ordering a node's value
only reaches the bound at its best child, normally the last one tried, so a
cutoff there would skip nothing. But when several children tie at the best
value, the first of them triggers the cutoff and the rest are skipped. With
only three possible values, ties like that are common. This is a likely
explanation, not a measured one: the experiment didn't count cutoffs by cause.

**Why natural order is worse than random.** Not established. One plausible
reason: a fixed order makes the _same_ choice at every node. If cell 1 (an
edge) is a poor first reply in one position, it tends to be poor in many, and
natural order tries it early everywhere. A random order makes independent
choices, so its mistakes don't line up. Testing this would mean comparing
natural order against a sample of other fixed orders of the cells.

**What this does _not_ establish.**

- These are node counts, not time. Ordering costs something at every node:
  tactical scans the lines for each move, and the oracle needs the game
  already solved. Neither cost is in the counts, and nothing was timed.
- Tic-tac-toe has only three values, and its branching factor falls from 9
  to 1. The tie effects above may matter much less in games with richer
  evaluations, like Connect Four with a heuristic score.
- The `b^d / b^(3d/4) / b^(d/2)` rule of thumb is for uniform trees. These
  measurements don't test it.

## Limitations

- One game, and a tiny one.
- Random orderings shuffle at every node independently, so a state visited
  twice may be searched in two different orders. A random _fixed_ permutation
  of cells is a different experiment.

## Reproduction

```sh
uv run python experiments/001-minimax-vs-alpha-beta/run.py   # about 20 s
```

## Next

- Move ordering returns as a real technique, not an oracle, with iterative
  deepening and transposition tables in Connect Four. There, the best move
  from a shallower search orders the deeper one.
- Is natural order unlucky, or is any fixed order worse than random? A sample
  of the 9! = 362,880 fixed cell orders would tell.
