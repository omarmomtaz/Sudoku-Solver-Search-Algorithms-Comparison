import time, tracemalloc, heapq, sys
from collections import deque

FULL = 0b1111111110  # bits 1..9
POPCOUNT = [bin(i).count('1') for i in range(1024)]
BOX_OF = [(r // 3) * 3 + c // 3 for r in range(9) for c in range(9)]
ROW_OF = [pos // 9 for pos in range(81)]
COL_OF = [pos % 9 for pos in range(81)]

def masks(grid):
    row = [0] * 9
    col = [0] * 9
    box = [0] * 9
    for pos in range(81):
        v = grid[pos]
        if v:
            bit = 1 << v
            row[ROW_OF[pos]] |= bit
            col[COL_OF[pos]] |= bit
            box[BOX_OF[pos]] |= bit
    return row, col, box

def mrv_cell(grid, row, col, box):
    best_pos, best_free, best_count = -1, 0, 10
    for pos in range(81):
        if grid[pos] == 0:
            free = FULL & ~(row[ROW_OF[pos]] | col[COL_OF[pos]] | box[BOX_OF[pos]])
            cnt = POPCOUNT[free]
            if cnt < best_count:
                best_pos, best_free, best_count = pos, free, cnt
                if cnt == 0:
                    return best_pos, best_free
    return best_pos, best_free

def bits(mask):
    while mask:
        lsb = mask & -mask
        yield lsb.bit_length() - 1
        mask ^= lsb

def is_valid_input(grid):
    if len(grid) != 81 or any(v < 0 or v > 9 for v in grid):
        return False
    row, col, box = [0]*9, [0]*9, [0]*9
    for pos in range(81):
        v = grid[pos]
        if v == 0:
            continue
        bit = 1 << v
        r, c, b = ROW_OF[pos], COL_OF[pos], BOX_OF[pos]
        if row[r] & bit or col[c] & bit or box[b] & bit:
            return False
        row[r] |= bit; col[c] |= bit; box[b] |= bit
    return True

def solve(grid, strategy, limit=200_000):
    if not is_valid_input(grid):
        return {'solution': None, 'time': 0.0, 'explored': 0,
                'memory_kb': 0.0, 'strategy': strategy, 'error': 'invalid puzzle'}

    tracemalloc.start()
    start = time.perf_counter()
    explored = 0
    init_grid = tuple(grid)

    use_heap = strategy in ('ucs', 'greedy', 'astar')
    if strategy == 'bfs':
        frontier = deque([(init_grid, 0)])
        pop = frontier.popleft
    elif strategy == 'dfs':
        frontier = [(init_grid, 0)]
        pop = frontier.pop
    else:
        heap = []
        counter = 0

    def push_heap(g, cost, empties):
        nonlocal counter
        counter += 1
        if strategy == 'ucs':
            p = cost
        elif strategy == 'greedy':
            p = empties
        else:
            p = cost + empties
        heapq.heappush(heap, (p, counter, g, cost))

    if use_heap:
        push_heap(init_grid, 0, init_grid.count(0))

    while (heap if use_heap else frontier):
        if explored > limit:
            break
        if use_heap:
            _, _, grid_t, g = heapq.heappop(heap)
        else:
            grid_t, g = pop()

        explored += 1
        if 0 not in grid_t:
            elapsed = time.perf_counter() - start
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            return {'solution': grid_t, 'time': elapsed, 'explored': explored,
                    'memory_kb': peak / 1024, 'strategy': strategy}

        row, col, box = masks(grid_t)
        pos, free = mrv_cell(grid_t, row, col, box)
        if free == 0:
            continue
        for v in bits(free):
            new_grid = grid_t[:pos] + (v,) + grid_t[pos + 1:]
            new_cost = g + 1
            if use_heap:
                push_heap(new_grid, new_cost, new_grid.count(0))
            else:
                frontier.append((new_grid, new_cost))

    elapsed = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {'solution': None, 'time': elapsed, 'explored': explored,
            'memory_kb': peak / 1024, 'strategy': strategy}

def print_grid(grid):
    for r in range(9):
        print(' '.join(str(grid[r * 9 + c]) for c in range(9)))

def parse(s):
    return tuple(int(ch) for ch in s)

HARD = (
    "800000000"
    "003600000"
    "070090200"
    "050007000"
    "000045700"
    "000100030"
    "001000068"
    "008500010"
    "090000400"
)

if __name__ == '__main__':
    puzzle = parse(HARD)
    print("Puzzle:")
    print_grid(puzzle)
    print()

    algos = ['bfs', 'dfs', 'ucs', 'greedy', 'astar']
    results = []
    print(f"{'Algorithm':10s} {'Status':9s} {'Time(s)':>10s} {'Explored':>10s} {'Memory(KB)':>12s}")
    print('-' * 55)
    for algo in algos:
        r = solve(puzzle, algo)
        results.append(r)
        status = "solved" if r['solution'] else "unsolved"
        print(f"{algo:10s} {status:9s} {r['time']:10.4f} {r['explored']:10d} {r['memory_kb']:12.1f}")

    solved = next((r for r in results if r['solution']), None)
    if solved:
        print(f"\nSolution ({solved['strategy']}):")
        print_grid(solved['solution'])

    sys.exit(0)
