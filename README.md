# Sudoku Solver — Search Algorithms Comparison

A single-file Python implementation of a Sudoku solver using five classic search
algorithms — **BFS**, **DFS**, **UCS**, **Greedy Best-First Search**, and **A\*** —
built to compare how each performs on the same puzzle.

Each cell fill is treated as a search action. States are ranked/expanded differently
depending on the algorithm, and the next cell to fill is always chosen via the
**Minimum Remaining Values (MRV)** heuristic, with legal digits computed using
bitmask constraints for speed.

## Features

- All 5 algorithms implemented from a shared `solve()` function — only the frontier
  data structure and priority rule differ.
- Bitmask-based constraint checking (row/col/box as 9-bit integers) for fast
  candidate lookup.
- Reports **execution time**, **states explored**, **peak memory usage**, and
  **solution validity** for each algorithm.
- Input validation — malformed or conflicting puzzles fail cleanly instead of
  crashing.
- Zero dependencies — pure Python standard library.

## Algorithms

| Algorithm | Frontier | Priority |
|---|---|---|
| BFS | Queue (FIFO) | Insertion order |
| DFS | Stack (LIFO) | Insertion order |
| UCS | Priority queue | Path cost `g(n)` = moves made |
| Greedy Best-First | Priority queue | Heuristic `h(n)` = empty cells remaining |
| A\* | Priority queue | `g(n) + h(n)` |

`h(n)` (empty cells remaining) is admissible and consistent, since every move fills
exactly one cell.

## Requirements

- Python 3.8+
- No external packages

## Usage

```bash
python3 sudoku_search.py
```

Runs all five algorithms on a built-in hard puzzle and prints a comparison table
plus the solved grid.

### Using your own puzzle

```python
from sudoku_search import solve, parse, print_grid

puzzle = parse("530070000600195000098000060800060003400803001700020006060000280000419005000080079")
result = solve(puzzle, "astar")

if result["solution"]:
    print_grid(result["solution"])
```

Puzzle strings are 81 characters, row by row, left to right, top to bottom, with
`0` for blank cells.

## Sample Output

```
Puzzle:
8 0 0 0 0 0 0 0 0
0 0 3 6 0 0 0 0 0
0 7 0 0 9 0 2 0 0
0 5 0 0 0 7 0 0 0
0 0 0 0 4 5 7 0 0
0 0 0 1 0 0 0 3 0
0 0 1 0 0 0 0 6 8
0 0 8 5 0 0 0 1 0
0 9 0 0 0 0 4 0 0

Algorithm  Status       Time(s)   Explored   Memory(KB)
-------------------------------------------------------
bfs        solved        2.5585      18936        714.9
dfs        solved        1.1272       8895         42.8
ucs        solved        2.4697      18936        755.5
greedy     solved        1.2647      10102         71.3
astar      solved        2.3897      18936        693.8

Solution (bfs):
8 1 2 7 5 3 6 4 9
9 4 3 6 8 2 1 7 5
6 7 5 4 9 1 2 8 3
1 5 4 2 3 7 8 9 6
3 6 9 8 4 5 7 2 1
2 8 7 1 6 9 5 3 4
5 2 1 9 7 4 3 6 8
4 3 8 5 2 6 9 1 7
7 9 6 3 1 8 4 5 2
```

*(Timings vary by machine; the above is a reference run.)*

## Interpreting the results

- **BFS and UCS explore the same states** here because every move has a uniform
  cost of 1 — with uniform step costs, UCS degenerates into BFS.
- **DFS** is fastest and uses the least memory, since it only keeps one path in
  memory at a time, but it isn't guaranteed to find the shortest solution path.
- **Greedy** is fast because it always chases the state with the fewest empty cells,
  but can be misled since it ignores path cost.
- **A\*** explores the same states as BFS/UCS on this puzzle since `g(n)` grows
  uniformly, but in general it balances path cost and heuristic guidance.
- BFS/UCS/A\* keep the entire frontier in memory, so they use noticeably more
  memory than DFS or Greedy.

## Project Structure

```
sudoku_search.py   # solver, all 5 algorithms, CLI demo
README.md
```

## How It Works

1. The next cell to fill is chosen via MRV — the empty cell with the fewest legal
   candidates, computed from row/column/box bitmasks.
2. Each candidate digit for that cell generates one successor state.
3. States are pushed to the frontier and popped according to the active
   algorithm's rule (FIFO, LIFO, or priority).
4. Search ends when a state has no empty cells (solved) or the frontier is
   exhausted / an explored-state limit is hit (unsolvable or too complex).
