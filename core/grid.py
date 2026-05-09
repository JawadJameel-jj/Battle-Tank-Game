# ─────────────────────────────────────────────
#  core/grid.py  –  26x26 tile map
# ─────────────────────────────────────────────
from settings import *


class Grid:
    # """
    # Holds the 26x26 (or custom-size) tile map.
    # Provides helpers used by pathfinding and collision code.
    # """

    def __init__(self, size=GRID_SIZE):
        self.size = size
        # 2-D list of tile types; default all EMPTY
        self.tiles = [[EMPTY] * size for _ in range(size)]

    # ── basic access ──────────────────────────────────────────

    def get(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.tiles[y][x]
        return STEEL   # treat out-of-bounds as impassable

    def set(self, x, y, tile_type):
        if 0 <= x < self.size and 0 <= y < self.size:
            self.tiles[y][x] = tile_type

    def in_bounds(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size

    # ── passability helpers ───────────────────────────────────

    def is_passable(self, x, y):
        # Determines if a tank can occupy this tile. 
        # Only returns True for EMPTY or FOREST. 
        # Note: Bricks are NOT passable even though AI can path through them,
        # because the tank must shoot the brick before moving onto the tile.
        t = self.get(x, y)
        return t in (EMPTY, FOREST)

    def is_shootable(self, x, y):
        # Does a bullet stop or trigger an effect at this tile?
        t = self.get(x, y)
        return t in (BRICK, STEEL, WATER, EAGLE)

    def is_destructible(self, x, y):
        return self.get(x, y) == BRICK

    # ── map mutation ─────────────────────────────────────────

    def destroy_brick(self, x, y):
        # Permanently modifies the map by clearing a brick tile.
        if self.get(x, y) == BRICK:
            self.set(x, y, EMPTY)
            return True
        return False

    # ── neighbours for search algorithms ─────────────────────

    def passable_neighbours(self, x, y):
        # Returns standard open neighbours (Empty/Forest only).
        neighbours = []
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if self.in_bounds(nx, ny) and self.is_passable(nx, ny):
                neighbours.append((nx, ny))
        return neighbours

    def all_neighbours(self, x, y):
        # Returns all 4 cardinal neighbours regardless of terrain.
        # Used by improved AI (BFS/A*) to find paths that include walls.
        result = []
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if self.in_bounds(nx, ny):
                result.append((nx, ny))
        return result

    # ── utility ───────────────────────────────────────────────

    def copy_tiles(self):
        # Return a deep copy of the tile array (for Minimax simulation).
        return [row[:] for row in self.tiles]

    def load_tiles(self, tile_array):
        # Load a 2-D list into this grid (used by CSP generator).
        self.tiles = [row[:] for row in tile_array]

    def find_nearest(self, x, y, tile_type):
        # BFS to find nearest tile of a given type. Returns (nx,ny) or None.
        from collections import deque
        visited = {(x, y)}
        q = deque([(x, y)])
        while q:
            cx, cy = q.popleft()
            if self.get(cx, cy) == tile_type:
                return (cx, cy)
            for nx, ny in self.all_neighbours(cx, cy):
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    q.append((nx, ny))
        return None

    def __repr__(self):
        symbols = {EMPTY: '.', BRICK: '#', STEEL: 'X', WATER: '~', FOREST: 'T', EAGLE: 'E'}
        rows = []
        for row in self.tiles:
            rows.append(''.join(symbols.get(t, '?') for t in row))
        return '\n'.join(rows)
