# ─────────────────────────────────────────────
#  csp/constraints.py  –  All 5 CSP constraint checks
# ─────────────────────────────────────────────
from collections import deque
from settings import BRICK, STEEL, WATER, EMPTY, FOREST


def check_eagle_protection(grid, eagle_pos):
    # C1: Eagle must be surrounded by at least Brick or Steel on all
    # in-bounds 8 immediate neighbours.
    # Out-of-bounds tiles count as protected (border).
    ex, ey = eagle_pos
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if dx == 0 and dy == 0:
                continue
            nx, ny = ex + dx, ey + dy
            if not grid.in_bounds(nx, ny):
                continue
            tile = grid.get(nx, ny)
            if tile not in (BRICK, STEEL):
                return False
    return True


def check_reachability(grid, spawn_points, eagle_pos):
    # C2: A valid path must exist from every spawn point to the Eagle.
    # We use a BFS that treats BRICK as traversable (since tanks shoot).
    for spawn in spawn_points:
        if not _bfs_reachable_with_brick(grid, spawn, eagle_pos):
            return False
    return True


def _bfs_reachable_with_brick(grid, start, goal):
    # BFS reachability: empty, forest, and brick tiles are traversable.
    if start == goal:
        return True
    visited = {start}
    q = deque([start])
    while q:
        cx, cy = q.popleft()
        for nx, ny in grid.all_neighbours(cx, cy):
            if (nx, ny) == goal:
                return True
            if (nx, ny) in visited:
                continue
            tile = grid.get(nx, ny)
            if tile in (EMPTY, FOREST, BRICK):
                visited.add((nx, ny))
                q.append((nx, ny))
    return False


def _bfs_reachable(grid, start, goal):
    # Strict BFS reachability: only empty and forest.
    if start == goal:
        return True
    visited = {start}
    q = deque([start])
    while q:
        cx, cy = q.popleft()
        for nx, ny in grid.passable_neighbours(cx, cy):
            if (nx, ny) == goal:
                return True
            if (nx, ny) not in visited:
                visited.add((nx, ny))
                q.append((nx, ny))
    return False


def check_wall_density(tiles, size):
    # C4: No more than 40% of tiles can be wall types (BRICK + STEEL).
    wall_count = sum(
        1
        for row in tiles
        for tile in row
        if tile in (BRICK, STEEL)
    )
    total = size * size
    return (wall_count / total) <= 0.40


def check_water_blocking(grid, spawn_points, eagle_pos):
    # C5: Water tiles may not be the sole reason a path to Eagle is blocked.
    from core.grid import Grid

    temp = Grid(grid.size)
    temp_tiles = [
        [EMPTY if t == WATER else t for t in row]
        for row in grid.tiles
    ]
    temp.load_tiles(temp_tiles)

    for spawn in spawn_points:
        if not _bfs_reachable_with_brick(temp, spawn, eagle_pos):
            return False
    return True


def check_spawn_fairness(spawn_points, player_pos, min_dist=10):
    # C3: No spawn point within min_dist Manhattan distance of player start.
    px, py = player_pos
    for sx, sy in spawn_points:
        if abs(sx - px) + abs(sy - py) < min_dist:
            return False
    return True
