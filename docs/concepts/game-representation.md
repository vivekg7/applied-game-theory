# Representing a game

Before any algorithm can play a game, we have to answer a question: what _is_
a game, to a computer? This page covers the representation in
`src/agt/core.py` and the vocabulary used in the rest of the repo.

## Classifying games

Each property below decides which algorithms are valid for a game. Picking an
algorithm starts with classifying the game.

| Property                | Question                                       | Tic-tac-toe | Poker             |
| ----------------------- | ---------------------------------------------- | ----------- | ----------------- |
| Sequential/simultaneous | Do players take turns or move at once?         | Sequential  | Sequential        |
| Perfect information     | Does everyone see the whole state?             | Yes         | No (hidden cards) |
| Deterministic           | Is it free of chance (dice, shuffles)?         | Yes         | No (deals)        |
| Zero-sum                | Is one player's gain exactly the other's loss? | Yes         | Yes               |
| Number of players       |                                                | 2           | 2+                |

**Minimax and alpha-beta** assume a sequential, deterministic, two-player,
zero-sum game with perfect information. Change any one of these and the
assumption that "my opponent minimizes my score" either stops being the right
model or stops being computable. The later phases are mostly about what to do
when each property changes:

- Chance → expectimax and MCTS.
- Hidden information → belief states and CFR.
- General-sum → Nash equilibria, which need not be unique and are not "optimal".
- Simultaneous moves → mixed strategies.

## The game tree (extensive form)

A sequential game is a tree:

- Each **node** is a state.
- Each **edge** is an action taken by the player to move at that node.
- Each **leaf** (terminal state) carries a **payoff** for every player.

This is the _extensive form_. Game theory also has the _normal form_, a payoff
matrix where players choose whole strategies at once. That is what Phase 2
uses.

Tic-tac-toe's tree has **549,946 nodes** and **255,168 leaves** (distinct
games). Of those games, X wins 131,184, O wins 77,904, and 46,080 are draws.
`tests/test_tictactoe.py` walks the whole tree and checks these numbers.
Matching them is strong evidence that the rules are right, and in particular
that a game stops at the first win.

The tree is far larger than the number of distinct _positions_ (5,478), because
the same position is reached by different move orders. These repeated positions
are called _transpositions_. Remembering them is the idea behind transposition
tables in Phase 1.

## The interface

```python
class State[A](Protocol):
    num_players: int
    current_player: int | None    # None once the game is over
    def legal_actions(self) -> list[A]
    def apply(self, action: A) -> State[A]   # returns a NEW state
    def is_terminal(self) -> bool
    def returns(self) -> tuple[float, ...]   # payoff per player, terminal only
```

These methods map directly onto the tree. `legal_actions` gives a node's edges,
`apply` follows an edge to a child, and `returns` reads a leaf's payoffs. Any
search algorithm is a strategy for deciding which parts of this tree to look at.

The design has three main choices:

- **Immutable states.** `apply` never mutates. A search can try every child of
  a node without undoing moves. The cost is copying the board on every move,
  which is negligible for small games. If profiling ever shows it matters,
  make/unmake-move is the classic optimization.
- **Returns are a tuple, one entry per player,** rather than a single "score
  for X". This keeps the interface honest for non-zero-sum and multi-player
  games. Zero-sum two-player code can still use `returns()[player]`.
- **Agents only see the `State` interface.** The same random agent plays every
  game, and the same minimax will too. Game-specific knowledge, such as an
  evaluation function, is passed into an agent instead of being built into it.

## What the interface can't represent yet

- **Chance nodes**, such as dealing cards or rolling dice. These need a
  "chance player" whose actions have probabilities.
- **Hidden information**: each player needs an _observation_ of the state and
  an _information set_, the set of states they cannot tell apart.
- **Simultaneous moves.**

These will be added when the first game that needs them arrives (Kuhn poker in
Phase 3), rather than guessed at now.

## Measuring agents fairly

`agt.arena.play_series` always swaps seats between games. Moving first matters.
Between two random players, X wins about 58% of tic-tac-toe games and O wins
about 29%. An agent that always played X would look much stronger than it is.
Swapping seats is the first of many controls the experiments need.

Try it:

```sh
uv run agt match tictactoe random random -n 10000
```

The score is close to 0.5, even though the first mover wins about twice as
often.
