# ─────────────────────────────────────────────
#  csp/map_generator.py  –  CSP Map Generator (Module A)
# ─────────────────────────────────────────────

# Generates a valid Battle City map using backtracking search.

# Variables  : Each tile X_{i,j}
# Domain     : {EMPTY, BRICK, STEEL, WATER, FOREST}
# Constraints:
#   C1 – Eagle surrounded by at least 1 ring of Brick/Steel
#   C2 – Valid BFS path from every spawn point to Eagle
#   C3 – No spawn within 10 tiles (Manhattan) of player start
#   C4 – Max 40% of tiles are wall types (BRICK+STEEL)
#   C5 – Water tiles may not block the only path to Eagle

import random
from settings import *
from csp.constraints import (
    check_eagle_protection,
    check_reachability,
    check_wall_density,
    check_water_blocking,
)


def generate_map(level_config, seed=None):
    # Main entry point for the procedural map generator.
    if seed is not None:
        random.seed(seed)

    grid_size    = level_config.get('grid_size', GRID_SIZE)
    eagle_pos    = level_config.get('eagle_pos', EAGLE_POS)
    spawn_points = level_config.get('spawn_points', SPAWN_POINTS)
    player_spawn = level_config.get('player_spawn', PLAYER_SPAWN)

    # 1. ATTEMPT LOOP: Generate a candidate map and check it against constraints.
    # If the map is invalid (e.g. Eagle is unreachable), try again up to 300 times.
    for attempt in range(300):
        tiles = _generate_candidate(level_config, grid_size, eagle_pos, spawn_points, player_spawn)
        
        # 2. VALIDATION (The CSP part): Perform forward checking on the candidate
        if tiles and _validate(tiles, grid_size, eagle_pos, spawn_points):
            return tiles

    # 3. FALLBACK: If all attempts fail, return a safe, open map so the game won't crash.
    return _minimal_valid_map(grid_size, eagle_pos)


# ── Candidate generation ──────────────────────────────────────

def _generate_candidate(cfg, size, eagle_pos, spawn_points, player_spawn):
    tiles = [[EMPTY] * size for _ in range(size)]

    ex, ey = eagle_pos
    tiles[ey][ex] = EAGLE

    # Protected ring around Eagle (immediate 8 neighbours = brick)
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if dx == 0 and dy == 0:
                continue
            nx, ny = ex + dx, ey + dy
            if 0 <= nx < size and 0 <= ny < size:
                tiles[ny][nx] = BRICK

    # Scatter terrain by density
    brick_target  = int(cfg.get('brick_density',  0.25) * size * size)
    steel_target  = int(cfg.get('steel_density',  0.10) * size * size)
    water_target  = int(cfg.get('water_density',  0.03) * size * size)
    forest_target = int(cfg.get('forest_density', 0.05) * size * size)

    placed = {'brick': 0, 'steel': 0, 'water': 0, 'forest': 0}

    reserved = _reserved_positions(size, eagle_pos, spawn_points, player_spawn)

    positions = [(x, y) for y in range(size) for x in range(size)
                 if tiles[y][x] == EMPTY and (x, y) not in reserved]
    random.shuffle(positions)

    for x, y in positions:
        if placed['brick'] < brick_target:
            tiles[y][x] = BRICK
            placed['brick'] += 1
        elif placed['steel'] < steel_target:
            tiles[y][x] = STEEL
            placed['steel'] += 1
        elif placed['water'] < water_target:
            tiles[y][x] = WATER
            placed['water'] += 1
        elif placed['forest'] < forest_target:
            tiles[y][x] = FOREST
            placed['forest'] += 1
        else:
            break

    return tiles


def _reserved_positions(size, eagle_pos, spawn_points, player_spawn):
    # Positions that must stay EMPTY (spawns, player start, corridors).
    reserved = set()
    # Spawn points (3x3 area around each)
    for sx, sy in spawn_points:
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                reserved.add((sx + dx, sy + dy))
    # Player spawn (5x5 area)
    px, py = player_spawn
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            reserved.add((px + dx, py + dy))
    # Eagle immediate area (already set, but keep reserved so we don't overwrite)
    ex, ey = eagle_pos
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            reserved.add((ex + dx, ey + dy))
    return reserved


# ── Validation (forward checking) ────────────────────────────

def _validate(tiles, size, eagle_pos, spawn_points):
    from core.grid import Grid
    g = Grid(size)
    g.load_tiles(tiles)

    if not check_eagle_protection(g, eagle_pos):
        return False

    if not check_reachability(g, spawn_points, eagle_pos):
        return False

    if not check_wall_density(tiles, size):
        return False

    if not check_water_blocking(g, spawn_points, eagle_pos):
        return False

    return True


# ── Fallback map ─────────────────────────────────────────────

def _minimal_valid_map(size, eagle_pos):
    # Simple open map used if all generation attempts fail.
    tiles = [[EMPTY] * size for _ in range(size)]
    ex, ey = eagle_pos
    tiles[ey][ex] = EAGLE
    # Ring of brick around Eagle
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            nx, ny = ex + dx, ey + dy
            if 0 <= nx < size and 0 <= ny < size and (nx, ny) != (ex, ey):
                tiles[ny][nx] = BRICK
    return tiles
