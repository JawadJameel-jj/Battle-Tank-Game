# ─────────────────────────────────────────────
#  ai/astar.py  –  A* Search Algorithm
# ─────────────────────────────────────────────
import heapq
from settings import EMPTY, FOREST, BRICK, STEEL, WATER, ASTAR_COST


def manhattan(ax, ay, bx, by):
    return abs(ax - bx) + abs(ay - by)


def astar(grid, start, goal, allow_brick_shoot=True):
    # A* pathfinding with tile cost awareness.
    #
    # Terrain costs (from settings.ASTAR_COST):
    #     EMPTY  = 1   (normal movement)
    #     FOREST = 1   (same as empty)
    #     BRICK  = 3   (shoot + wait penalty)
    #     STEEL  = inf (absolute barrier)
    #     WATER  = inf (absolute barrier for tanks)
    #
    # Returns List of (x, y) tiles from start to goal.
    
    if start == goal:
        return []

    # Priority queue stores: (total_estimated_cost, current_g_cost, current_node, path)
    # Using Manhattan distance as the heuristic (H).
    pq = [(manhattan(*start, *goal), 0, start, [])]
    visited = {start: 0}

    while pq:
        _, g, current, path = heapq.heappop(pq)

        if current == goal:
            return path

        for nx, ny in grid.all_neighbours(*current):
            tile = grid.get(nx, ny)
            cost = ASTAR_COST.get(tile, float('inf'))

            # Bricks are only traversable if we plan to shoot them down
            if tile == BRICK and not allow_brick_shoot:
                cost = float('inf')

            if cost == float('inf'):
                continue

            new_g = g + cost
            # Only explore this neighbour if we found a cheaper way to get there
            if nx not in visited or ny not in visited[nx] if isinstance(visited, dict) else (nx, ny) not in visited or new_g < visited[(nx, ny)]:
                # Note: using (nx, ny) as key for simplicity
                if (nx, ny) not in visited or new_g < visited[(nx, ny)]:
                    visited[(nx, ny)] = new_g
                    h = manhattan(nx, ny, *goal)
                    heapq.heappush(pq, (new_g + h, new_g, (nx, ny), path + [(nx, ny)]))

    return []


def astar_next_step(grid, start, goal):
    # Helper for tanks: returns just the next (x, y) tile in the A* path.
    path = astar(grid, start, goal)
    return path[0] if path else None
