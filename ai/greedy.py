# ─────────────────────────────────────────────
#  ai/greedy.py  –  Greedy Best-First Search
# ─────────────────────────────────────────────
import heapq
from settings import STEEL, WATER


def manhattan(ax, ay, bx, by):
    return abs(ax - bx) + abs(ay - by)


def greedy_next_step(grid, start, goal):
    # Greedy Best-First Search: always expands the node closest to goal
    # by Manhattan distance. No path cost considered.

    # Key property: may get stuck in local minima (surrounded by walls
    # with only an opening behind it). This is intentional — it visually
    # demonstrates WHY greedy search is suboptimal.

    # Returns the next (x, y) to move to, or None if completely stuck.
    if start == goal:
        return None

    sx, sy = start
    gx, gy = goal

    # Priority queue: (heuristic, (x, y), came_from_pos)
    heap = [(manhattan(sx, sy, gx, gy), start, None)]
    came_from = {start: None}

    while heap:
        h, (cx, cy), _ = heapq.heappop(heap)

        if (cx, cy) == goal:
            # Reconstruct path back to start
            path = []
            pos = (cx, cy)
            while came_from[pos] is not None:
                path.append(pos)
                pos = came_from[pos]
            path.reverse()
            return path[0] if path else None

        for nx, ny in grid.passable_neighbours(cx, cy):
            if (nx, ny) not in came_from:
                came_from[(nx, ny)] = (cx, cy)
                heapq.heappush(heap, (manhattan(nx, ny, gx, gy), (nx, ny), (cx, cy)))

    return None   # stuck — no passable path


def greedy_single_step(grid, x, y, gx, gy):
    # Ultra-simple single-step greedy: just pick the open neighbour
    # with the lowest Manhattan distance to goal.
    # This is what the Fast Tank actually uses each tick (no full search).
    best = None
    best_h = float('inf')
    for nx, ny in grid.all_neighbours(x, y):
        # Allow moving through EMPTY, FOREST, or BRICK
        if grid.get(nx, ny) in (STEEL, WATER):
            continue
            
        h = manhattan(nx, ny, gx, gy)
        if h < best_h:
            best_h = h
            best = (nx, ny)
    return best
