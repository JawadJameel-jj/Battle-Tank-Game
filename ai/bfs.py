# ─────────────────────────────────────────────
#  ai/bfs.py  –  Breadth-First Search
# ─────────────────────────────────────────────
from collections import deque
from settings import EMPTY, FOREST, BRICK


def bfs(grid, start, goal):
    # Standard BFS on the grid.

    # Treats EMPTY and FOREST as passable (cost = 1 each).
    # Does NOT shoot through walls — only follows open paths.

    # Parameters
    # ----------
    # grid  : Grid object
    # start : (x, y) tuple
    # goal  : (x, y) tuple

    # Returns
    # -------
    # List of (x, y) tiles from start (exclusive) to goal (inclusive),
    # or [] if no path exists.
    if start == goal:
        return []

    visited = {start}
    # The queue stores (current_position, path_taken_to_get_there)
    q = deque([(start, [])])

    while q:
        (cx, cy), path = q.popleft() # Pop next node to explore

        for nx, ny in grid.all_neighbours(cx, cy): # Check N, S, E, W
            if (nx, ny) in visited:
                continue
            
            tile = grid.get(nx, ny)
            # LOGIC: Bricks are treated as passable for searching purposes 
            # because the tank can shoot them down. Steel and Water block the path forever.
            if tile not in (EMPTY, FOREST, BRICK):
                continue

            visited.add((nx, ny))
            new_path = path + [(nx, ny)]

            # If we reached the target coordinate, return the sequence of moves
            if (nx, ny) == goal:
                return new_path

            q.append(((nx, ny), new_path))

    return []   # no path found


def bfs_next_step(grid, start, goal):
    # Convenience wrapper: returns only the immediate next tile to move to,
    # or None if no path exists.
    path = bfs(grid, start, goal)
    return path[0] if path else None
