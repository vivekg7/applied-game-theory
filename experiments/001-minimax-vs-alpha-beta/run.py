"""Experiment 001: minimax vs. alpha-beta on tic-tac-toe, and the effect of move ordering.

Alpha-beta itself is not modified. To change the order moves are tried in, the
game state is wrapped in `Reordered`, which reports the same legal actions in a
different order. The search sees an ordinary `State`, so whatever changes in
the node counts is caused by the ordering alone.

Writes root.csv and all_positions.csv next to this file and prints the
Markdown tables used in README.md.

    uv run python experiments/001-minimax-vs-alpha-beta/run.py
"""

import csv
import random
import statistics
from collections.abc import Callable
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from agt.agents import AlphaBetaAgent, MinimaxAgent
from agt.games.tictactoe import LINES, TicTacToeState

OUT = Path(__file__).parent
RANDOM_SEEDS_ROOT = 200  # random orderings from the empty board: cheap, so many seeds
RANDOM_SEEDS_ALL = 20  # random orderings over every position: a full pass each, so fewer

type Order = Callable[[TicTacToeState], list[int]]


@dataclass(frozen=True)
class Reordered:
    """A tic-tac-toe state that reports its legal actions in a chosen order.

    Everything else is delegated, so to a search algorithm it is the same game.
    """

    inner: TicTacToeState
    order: Order

    @property
    def num_players(self) -> int:
        return self.inner.num_players

    @property
    def current_player(self) -> int | None:
        return self.inner.current_player

    def legal_actions(self) -> list[int]:
        return self.order(self.inner)

    def apply(self, action: int) -> Reordered:
        return Reordered(self.inner.apply(action), self.order)

    def is_terminal(self) -> bool:
        return self.inner.is_terminal()

    def returns(self) -> tuple[float, float]:
        return self.inner.returns()


# --- Ground truth ------------------------------------------------------------


@cache
def true_value(state: TicTacToeState) -> float:
    """Minimax value for X (player 0), memoized. Only the oracle orderings use it."""
    if state.is_terminal():
        return state.returns()[0]
    values = [true_value(state.apply(a)) for a in state.legal_actions()]
    return max(values) if state.current_player == 0 else min(values)


def value_for_mover(state: TicTacToeState, action: int) -> float:
    v = true_value(state.apply(action))
    return v if state.current_player == 0 else -v


def all_nonterminal_positions() -> list[TicTacToeState]:
    seen: dict[TicTacToeState, None] = {}  # insertion-ordered, so runs are repeatable
    stack = [TicTacToeState()]
    while stack:
        state = stack.pop()
        if state not in seen:
            seen[state] = None
            stack.extend(state.apply(a) for a in state.legal_actions())
    return [s for s in seen if not s.is_terminal()]


# --- Orderings ---------------------------------------------------------------
# Each takes a state and returns a permutation of state.legal_actions().
# Python's sort is stable, so ties always keep natural (0-8) order.

STATIC_PRIORITY = [4, 0, 2, 6, 8, 1, 3, 5, 7]  # centre, corners, edges
RANK = {cell: i for i, cell in enumerate(STATIC_PRIORITY)}


def natural(s: TicTacToeState) -> list[int]:
    return s.legal_actions()


def reverse(s: TicTacToeState) -> list[int]:
    return s.legal_actions()[::-1]


def centre_corners_edges(s: TicTacToeState) -> list[int]:
    return sorted(s.legal_actions(), key=RANK.__getitem__)


def _completes_line(board: tuple, cell: int, player: int) -> bool:
    """Would `player` marking `cell` complete a line?"""
    return any(
        cell in line and all(board[c] == player for c in line if c != cell) for line in LINES
    )


def tactical(s: TicTacToeState) -> list[int]:
    """A cheap, fair heuristic: win now, else block, else centre/corners/edges."""
    me = s.to_move

    def key(cell: int) -> tuple[int, int]:
        if _completes_line(s.board, cell, me):
            return (0, RANK[cell])
        if _completes_line(s.board, cell, 1 - me):
            return (1, RANK[cell])
        return (2, RANK[cell])

    return sorted(s.legal_actions(), key=key)


def oracle_best_first(s: TicTacToeState) -> list[int]:
    """Best move first, by true value. Uses the answer, so no real agent could do this.

    Not the cheapest ordering, though: see "oracle, tactical ties" in README.md.
    """
    return sorted(s.legal_actions(), key=lambda a: -value_for_mover(s, a))


def oracle_then_tactical(s: TicTacToeState) -> list[int]:
    """Perfect ordering by value, but ties broken by the tactical heuristic.

    Value alone can't tell "win now" from "win in five moves": both are worth 1.
    Among equally good moves, the cheapest one to search proves the same bound.
    """
    rank = {a: i for i, a in enumerate(tactical(s))}
    return sorted(s.legal_actions(), key=lambda a: (-value_for_mover(s, a), rank[a]))


def oracle_worst_first(s: TicTacToeState) -> list[int]:
    return sorted(s.legal_actions(), key=lambda a: value_for_mover(s, a))


def random_order(seed: int) -> Order:
    rng = random.Random(seed)

    def order(s: TicTacToeState) -> list[int]:
        actions = s.legal_actions()
        rng.shuffle(actions)
        return actions

    return order


DETERMINISTIC: dict[str, Order] = {
    "natural": natural,
    "reverse": reverse,
    "centre-corners-edges": centre_corners_edges,
    "tactical": tactical,
    "oracle best-first": oracle_best_first,
    "oracle, tactical ties": oracle_then_tactical,
    "oracle worst-first": oracle_worst_first,
}


# --- Measurements -------------------------------------------------------------


def alphabeta_nodes(state: TicTacToeState, order: Order) -> tuple[int, int]:
    """Nodes AlphaBetaAgent visits to choose a move at `state`, and the move."""
    agent = AlphaBetaAgent()
    move = agent.act(Reordered(state, order))
    return agent.last_stats.nodes, move


def minimax_nodes(state: TicTacToeState, order: Order) -> tuple[int, int]:
    agent = MinimaxAgent()
    move = agent.act(Reordered(state, order))
    return agent.last_stats.nodes, move


def mean_ci(xs: list[int]) -> tuple[float, float]:
    """Mean and the half-width of a normal-approximation 95% confidence interval for it.

    Only random orderings need this: every other number here is deterministic.
    """
    return statistics.fmean(xs), 1.96 * statistics.stdev(xs) / len(xs) ** 0.5


def over_all_positions(positions: list[TicTacToeState], order: Order) -> dict:
    total = same_move = optimal = 0
    for s in positions:
        nodes, move = alphabeta_nodes(s, order)
        total += nodes
        # Natural-order alpha-beta should pick exactly minimax's (natural-order) move.
        reference = natural(s)
        best = max(value_for_mover(s, a) for a in reference)
        minimax_move = next(a for a in reference if value_for_mover(s, a) == best)
        same_move += move == minimax_move
        optimal += value_for_mover(s, move) == best
    return {"total_nodes": total, "same_move_as_minimax": same_move, "optimal_moves": optimal}


def main() -> None:
    root = TicTacToeState()
    positions = all_nonterminal_positions()

    # 1. From the empty board. Minimax under two orderings, to show order can't affect it.
    root_rows = []
    for name, order in {"natural": natural, "reverse": reverse}.items():
        nodes, move = minimax_nodes(root, order)
        root_rows.append(dict(search="minimax", ordering=name, seed="", nodes=nodes, move=move))
    for name, order in DETERMINISTIC.items():
        nodes, move = alphabeta_nodes(root, order)
        root_rows.append(dict(search="alphabeta", ordering=name, seed="", nodes=nodes, move=move))
    for seed in range(RANDOM_SEEDS_ROOT):
        nodes, move = alphabeta_nodes(root, random_order(seed))
        root_rows.append(
            dict(search="alphabeta", ordering="random", seed=seed, nodes=nodes, move=move)
        )

    # 2. From every non-terminal position, summed. Minimax plays the reference moves.
    n = len(positions)
    minimax_total = sum(minimax_nodes(s, natural)[0] for s in positions)
    all_rows = [
        dict(
            search="minimax",
            ordering="natural",
            seed="",
            total_nodes=minimax_total,
            same_move_as_minimax=n,
            optimal_moves=n,
        )
    ]
    for name, order in DETERMINISTIC.items():
        all_rows.append(
            dict(search="alphabeta", ordering=name, seed="", **over_all_positions(positions, order))
        )
    for seed in range(RANDOM_SEEDS_ALL):
        all_rows.append(
            dict(
                search="alphabeta",
                ordering="random",
                seed=seed,
                **over_all_positions(positions, random_order(seed)),
            )
        )

    write_csv(OUT / "root.csv", root_rows)
    write_csv(OUT / "all_positions.csv", all_rows)
    print_tables(root_rows, all_rows, n)


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def print_tables(root_rows: list[dict], all_rows: list[dict], n_positions: int) -> None:
    minimax_root = root_rows[0]["nodes"]
    print("From the empty board\n")
    print("| Search | Ordering | Nodes | % of minimax | Move |")
    print("| --- | --- | ---: | ---: | ---: |")
    for r in root_rows:
        if r["ordering"] != "random":
            pct = 100 * r["nodes"] / minimax_root
            print(
                f"| {r['search']} | {r['ordering']} | {r['nodes']:,} | {pct:.2f}% | {r['move']} |"
            )
    randoms = [r["nodes"] for r in root_rows if r["ordering"] == "random"]
    mean, half = mean_ci(randoms)
    print(
        f"| alphabeta | random, {len(randoms)} seeds | {mean:,.0f} ± {half:,.0f} "
        f"(min {min(randoms):,}, max {max(randoms):,}) | {100 * mean / minimax_root:.2f}% | "
        f"varies |"
    )
    natural_root = next(
        r["nodes"] for r in root_rows if (r["search"], r["ordering"]) == ("alphabeta", "natural")
    )
    beaten_by = sum(nodes < natural_root for nodes in randoms)
    print(f"\n{beaten_by} of {len(randoms)} random orderings visit fewer nodes than natural order.")

    minimax_all = all_rows[0]["total_nodes"]
    print(f"\nSummed over all {n_positions:,} non-terminal positions\n")
    print(
        "| Search | Ordering | Total nodes | % of minimax | Same move as minimax | Optimal move |"
    )
    print("| --- | --- | ---: | ---: | ---: | ---: |")
    for r in all_rows:
        if r["ordering"] != "random":
            pct = 100 * r["total_nodes"] / minimax_all
            print(
                f"| {r['search']} | {r['ordering']} | {r['total_nodes']:,} | {pct:.2f}% | "
                f"{r['same_move_as_minimax']:,} | {r['optimal_moves']:,} |"
            )
    randoms = [r for r in all_rows if r["ordering"] == "random"]
    mean, half = mean_ci([r["total_nodes"] for r in randoms])
    same = statistics.fmean(r["same_move_as_minimax"] for r in randoms)
    optimal = min(r["optimal_moves"] for r in randoms)
    print(
        f"| alphabeta | random, {len(randoms)} seeds | {mean:,.0f} ± {half:,.0f} | "
        f"{100 * mean / minimax_all:.2f}% | {same:,.0f} (mean) | {optimal:,} (min) |"
    )


if __name__ == "__main__":
    main()
