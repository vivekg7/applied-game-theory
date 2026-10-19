# Minimax

**Field:** adversarial search, resting on a classical game-theory result.
Zermelo (1913) showed that a finite two-player game of perfect information,
with win/draw/loss outcomes, is _determined_: one side can force a win, or both can force a draw. The number
minimax computes is that outcome, the game's _value_. Von Neumann's minimax
theorem (1928) extends the idea to games needing mixed strategies (Phase 2).

**Code:** `src/agt/agents/minimax.py` · **Tests:** `tests/test_minimax.py`

## The idea

You can't know what your opponent will do, so assume the worst: they always
reply with the move that is worst for you. Under that assumption, a move's
value is well defined, and you pick the move with the highest one.

Fix one player as the **maximizer**. The value of a state for the maximizer is:

```
value(s) = returns(s)[maximizer]                if s is terminal
         = max over actions a of value(s.apply(a))   if the maximizer is to move
         = min over actions a of value(s.apply(a))   if the opponent is to move
```

The recursion bottoms out at the leaves. Each internal node takes the max or
the min of its children, depending on whose turn it is, so values flow up the
tree level by level.

## Assumptions

Each one matters, and each is broken by a later phase of the roadmap.

| Assumption                       | Why minimax needs it                                                                                                                                                                                              |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Two players, zero-sum**        | "The opponent minimizes my score" is only rational if my loss is their gain. In a general-sum game the opponent pursues their own payoff, not my loss, and one number per node isn't enough.                      |
| **Perfect information**          | Taking the max or min at a node means knowing exactly which node you are at. With hidden cards you don't; you only know an _information set_ of possible nodes.                                                   |
| **Deterministic**                | A chance node (a dice roll) is neither max nor min. It needs an _expectation_, which turns minimax into expectimax.                                                                                               |
| **The opponent plays perfectly** | This is a modelling choice rather than a requirement. It makes minimax _safe_: it guarantees at least the game value against anyone. It does **not** make it the best response to a weak or predictable opponent. |

## Worked example

X: `0`, O: `1`, X to move. O answered the corner with the edge next to it.

```
X | O | 2
---------
3 | 4 | 5
---------
6 | 7 | 8
```

Minimax returns **+1** for X. This position is lost for O under perfect play
(`test_known_positions`). One winning line: X takes 4, which threatens 8.
O must block 8, and X then plays 6, threatening both 3 (0-3-6) and 2 (2-4-6).
That is a _fork_, two threats at once, and O can block only one.

Minimax doesn't know what a fork is. It finds the win by checking every reply
to every move. All the "strategy" emerges from search plus correct leaf values.

## How it maps onto the code

```python
def minimax(state, maximizer, stats=None) -> float:
    if state.is_terminal():
        return state.returns()[maximizer]  # leaf: the payoff
    child_values = (minimax(state.apply(a), maximizer, stats) for a in state.legal_actions())
    if state.current_player == maximizer:
        return max(child_values)  # my move: best for me
    return min(child_values)  # their move: worst for me
```

`MinimaxAgent.act` runs this once per legal move and plays the highest. It
records `last_stats.nodes`, the number of states visited, which is the cost
measure that alpha-beta will be compared on.

This uses the explicit max/min form. Many engines use **negamax** instead: one
function where every player maximizes `-value(child)`. The two forms are
equivalent in zero-sum games. Explicit max/min is easier to read and closer to
the theory, so it is used first.

## What the tests establish

- **Tic-tac-toe is a draw.** The value of the empty board is 0, and so is the
  value of every one of the nine opening moves.
- **No pruning means the whole tree.** A search from the empty board visits
  exactly **549,946** nodes, the same number the rules test counts by brute
  force. Two independent walks agree.
- **Optimality is proven, not sampled.** `test_agent_never_loses_to_any_opponent`
  plays the agent against _every_ possible opponent strategy at once. At the
  agent's turns it follows the agent's move, and at the opponent's turns it
  branches on every legal move. No leaf is a loss, from either seat. This is a
  much stronger claim than "it beat a random agent 1000 times".
- **Known positions.** Values match standard tic-tac-toe theory. An edge
  reply to a corner or the centre loses, and corner-centre and centre-corner
  are draws.

A note on that last group: one expected value I first wrote into the tests was
wrong. I claimed X:0,8 / O:4,2 was a draw because X "just blocks" on 6, but
that block also forks 3 and 7, so X wins. Minimax was right and the test was
wrong. Hand-written "known" values need the same scepticism as code, which is
why the exhaustive checks matter more than the hand-picked positions.

## Measured behaviour

200 games against `RandomAgent(0)`, with seats swapped. These are
observations made while building the agent, not a formal experiment yet. The
totals (181 wins, 19 draws, 0 losses) reproduce with
`uv run agt match tictactoe minimax random -n 200 --seed -1` (the CLI seeds the
second agent with `seed + 1`). The split by seat and the delayed-win count below
come from the recorded games of that series.

| Minimax plays | Wins | Draws | Losses |
| ------------- | ---: | ----: | -----: |
| X (first)     |   98 |     2 |      0 |
| O (second)    |   83 |    17 |      0 |

**Cost.** Its first move as X visits all 549,946 nodes and takes about 0.5 s
in this Python. That is why every game where minimax plays X takes about half
a second, and why this approach can't scale to Connect Four, which has about
4.5 × 10¹² distinct positions and a far larger tree.

## What minimax doesn't do

Two behaviours look like bugs but follow from the definition.

1. **It doesn't hurry to win.** Every win is worth +1, whether it comes now or
   in five moves. In the 200 games above, minimax had an immediate win
   available 224 times and played something else 43 times (19%). It always
   still won, because it only delays when the win stays forced. A common fix is
   to score wins by depth, e.g. `+(10 - depth)`, so that a sooner win is worth
   more.
2. **It doesn't exploit weak opponents.** Every opening move is worth 0, so
   minimax always opens in cell 0, the first move in order. That is the
   tie-break, not a judgement. A move that sets more traps for a fallible
   opponent scores the same as one that sets none. Exploiting an opponent needs
   a _model_ of that opponent, which comes in later phases.

## Try it

Predict before you run:

- As O against `--opponent minimax`, can you draw? Is there anything you can
  do as X to make minimax lose?
- How many nodes will minimax visit for its first move as **O**, after X opens
  in the centre? Is that more or less than after a corner opening? Check with:

  ```sh
  uv run python -c "
  from agt.agents import MinimaxAgent; from agt.games import TicTacToeState
  for x in (4, 0, 1):
      a = MinimaxAgent(); a.act(TicTacToeState().apply(x)); print(x, a.last_stats.nodes)"
  ```

```sh
uv run agt play tictactoe --opponent minimax
uv run agt match tictactoe minimax random -n 100
```

## Next

[Alpha-beta pruning](alpha-beta.md) gives exactly the same decision while
skipping subtrees that can't affect it: 18,297 of these 549,946 nodes from the
empty board. Experiment 001 measures how much that depends on move ordering.
