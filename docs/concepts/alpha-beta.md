# Alpha-beta pruning

**Field:** adversarial search. It is an exact optimization of
[minimax](minimax.md). It doesn't change what minimax computes, only how much
of the tree it has to look at.

**Code:** `src/agt/agents/alphabeta.py` · **Tests:** `tests/test_alphabeta.py`

## The idea

Minimax looks at every node. Most of that work is wasted. Once you know a move
is worse than one you already have, you don't need to know _how much_ worse.

Suppose X has already found a move worth a draw (0). X now considers another
move, and the first reply O finds to it also holds X to a draw. O, the
minimizer, can then hold X to _at most_ 0 at that node, whatever the other
replies are. X already has 0 guaranteed elsewhere, so this move can't be
better. The remaining replies are skipped. That is a **cutoff**.

Alpha-beta tracks two bounds along the current path:

- **alpha**: the value the maximizer is already guaranteed elsewhere on the
  path. It only rises, at max nodes.
- **beta**: the value the minimizer can already hold the maximizer to
  elsewhere on the path. It only falls, at min nodes.

Only values strictly between alpha and beta can still change the decision at
the root. A node whose value is certain to fall outside the window `(α, β)`
can be abandoned:

- At a **max** node, once the value reaches `≥ β`, the minimizer above will
  avoid this node. This is a _beta cutoff_.
- At a **min** node, once the value drops to `≤ α`, the maximizer above will
  avoid it. This is an _alpha cutoff_.

## Why it is exact

At the root the window is `(-∞, ∞)`, so the root value is always computed
exactly. A pruned subtree is one whose exact value can't matter: some ancestor
already has an alternative that is at least as good for whoever would choose
there. The subtree only gets a _bound_, but a bound is enough to know it loses
that comparison.

The function's contract is **fail-soft**. For a returned value `v`:

| `v` compared with the window | What `v` means                |
| ---------------------------- | ----------------------------- |
| `α < v < β`                  | exact minimax value           |
| `v ≤ α`                      | upper bound: true value `≤ v` |
| `v ≥ β`                      | lower bound: true value `≥ v` |

The _fail-hard_ variant clamps `v` into `[α, β]`. It gives the same decisions,
but the bounds are less informative. Fail-soft bounds become useful later, with
transposition tables, where a stored bound can cause a cutoff on its own.

## Worked example: the opening in tic-tac-toe

The agent tries X's nine openings in order 0–8. Each opening is searched with
`alpha` set to the best value found so far:

| X opens | Minimax nodes | Alpha-beta nodes | What happened                                          |
| ------: | ------------: | ---------------: | ------------------------------------------------------ |
|       0 |        59,705 |            2,338 | Searched first, so alpha = −∞. Pruning only inside     |
|       1 |        63,905 |            1,244 | O's first reply (0) is already a draw, ≤ α = 0: cutoff |
|       2 |        59,705 |            2,428 | O's first reply (0) loses for O, so O keeps looking    |
|       3 |        63,905 |              626 | Cutoff after O's first reply, as for 1                 |
|       4 |        55,505 |              610 | Cutoff after O's first reply, as for 1                 |
|       5 |        63,905 |            1,699 |                                                        |
|       6 |        59,705 |            2,993 |                                                        |
|       7 |        63,905 |            3,393 |                                                        |
|       8 |        59,705 |            2,965 |                                                        |
|   total |   **549,946** |       **18,297** | the root, plus the nine subtrees                       |

To regenerate the table:

```sh
uv run python -c "
from math import inf
from agt.agents.alphabeta import alphabeta
from agt.agents.minimax import SearchStats, minimax
from agt.games import TicTacToeState
root, best = TicTacToeState(), -inf
for a in root.legal_actions():
    ab, mm = SearchStats(), SearchStats()
    v = alphabeta(root.apply(a), 0, alpha=best, stats=ab)
    minimax(root.apply(a), 0, mm)
    print(a, mm.nodes, ab.nodes)
    best = max(best, v)"
```

Alpha-beta visits **3.3%** of the nodes and picks the same move. Look at row 1:
once O's reply in cell 0 is known to hold X to a draw, O's seven other replies,
and everything below them, are never generated.

Rows like 2 show the cost of bad ordering. O's first reply is a losing one, so
no cutoff happens until O stumbles onto a drawing reply later in the list. Had
the strongest reply been tried first, the cutoff would have come immediately.

## Move ordering decides how much is pruned

Alpha-beta prunes most when the **best move is tried first** at every node.
For a tree with branching factor `b` and depth `d`:

| Ordering             | Nodes visited (roughly) | Effect                          |
| -------------------- | ----------------------- | ------------------------------- |
| Worst (best last)    | `b^d`                   | no better than minimax          |
| Random               | about `b^(3d/4)`        |                                 |
| Perfect (best first) | about `b^(d/2)`         | search twice as deep, same time |

"Search twice as deep in the same time" is why alpha-beta matters in
practice. A good move ordering, such as captures first in chess or centre
columns first in Connect Four, is worth more than most clever tricks. Of
course, if you could always order perfectly you would already know the best
move, so real engines use cheap guesses: heuristics, the best move from a
previous shallower search, or "killer moves".

This implementation deliberately uses plain `legal_actions()` order (cells
0–8). Measuring how much better ordering helps is **Experiment 001**.

## How it maps onto the code

```python
if state.current_player == maximizer:
    value = -inf
    for action in state.legal_actions():
        value = max(value, alphabeta(child, maximizer, alpha, beta, stats))
        if value >= beta:
            return value  # beta cutoff
        alpha = max(alpha, value)  # maximizer's guarantee improves
    return value
# ...and the min node is the mirror image, cutting at value <= alpha
```

At the root, `AlphaBetaAgent.act` passes `alpha = best value so far` into each
move's search, which is where the row-1 cutoffs above come from. A later move
that is only _as good_ as the best returns a bound `≤ α` and is never
preferred. So the agent makes **exactly the same choice as `MinimaxAgent`**,
including the tie-break that takes the first best move.

## What the tests establish

- **Same values.** With a full window, alpha-beta equals minimax at all 5,478
  reachable positions, for both players.
- **Correct bounds.** With random narrow windows, results respect the
  fail-soft contract above.
- **Same moves.** The agent picks minimax's move at every non-terminal
  position.
- **The pruning itself is pinned.** From the empty board alpha-beta visits
  exactly 18,297 nodes. This matters because the tests were checked by
  deliberately planting bugs ("mutations"). One planted bug, never raising
  alpha at max nodes, still produced correct values and moves. It just pruned
  less. Only the exact node count catches that kind of silent regression.

## Try it

Predict, then check in Experiment 001:

- Which cell would you try **first** at the root to maximize pruning? And at
  every node below it?
- If moves were tried in the _reverse_ order (8 down to 0), would the count go
  up or down?
- Could a "perfect" ordering get the root search down to near
  `√549,946 ≈ 742` nodes, as `b^(d/2)` suggests? Why might tic-tac-toe not
  follow the formula closely? Hint: games end early, and the branching factor
  shrinks as the board fills.

```sh
uv run agt match tictactoe alphabeta minimax -n 2   # always a draw
uv run agt play tictactoe --opponent alphabeta      # plays the same moves as minimax
```
