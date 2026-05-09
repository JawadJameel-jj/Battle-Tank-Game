# ─────────────────────────────────────────────
#  settings.py  –  Global constants
# ─────────────────────────────────────────────

# Grid
GRID_SIZE      = 26          # 26x26 tiles
TILE_SIZE      = 24          # pixels per tile
SCREEN_W       = GRID_SIZE * TILE_SIZE + 160   # +160 for HUD panel
SCREEN_H       = GRID_SIZE * TILE_SIZE
FPS            = 30

# Tile types
EMPTY  = 0
BRICK  = 1
STEEL  = 2
WATER  = 3
FOREST = 4
EAGLE  = 5

# Terrain colours (R,G,B)
TILE_COLORS = {
    EMPTY:  (30,  30,  30),
    BRICK:  (180, 80,  40),
    STEEL:  (120, 120, 140),
    WATER:  (40,  80,  180),
    FOREST: (30,  110, 40),
    EAGLE:  (220, 200, 50),
}

# A* terrain costs
ASTAR_COST = {
    EMPTY:  1,
    FOREST: 1,
    BRICK:  3,
    STEEL:  float('inf'),
    WATER:  float('inf'),
    EAGLE:  1,
}

# Fixed positions (for 26x26 normal levels)
EAGLE_POS        = (12, 24)
SPAWN_POINTS     = [(0, 0), (12, 0), (24, 0)]
PLAYER_SPAWN     = (4, 24)
SPAWN_MIN_DIST   = 10        # Manhattan distance safety

# Boss level fixed positions (for 16x16 boss arena)
BOSS_GRID_SIZE   = 16
BOSS_EAGLE_POS   = (7, 14)
BOSS_SPAWN_PTS   = [(0, 0), (7, 0), (14, 0)]
BOSS_PLAYER_SPAWN = (3, 13)

# Tank speed (ticks between moves; lower = faster)
SPEED_SLOW   = 8     # ~4 moves per sec at 30 FPS
SPEED_MEDIUM = 6     # ~5 moves per sec
SPEED_FAST   = 4     # ~7.5 moves per sec

# Fire rate (ticks between shots)
FIRE_SLOW   = 120    # ~4 s
FIRE_MEDIUM = 90     # ~3 s
FIRE_FAST   = 60     # ~2 s
FIRE_RAPID  = 30     # ~1 s

# Bullet speed (tiles per tick)
BULLET_SPEED = 1.0

# BFS replan interval (ticks)
BFS_REPLAN_INTERVAL = 150    # ~5 s at 30 FPS

# Boss phases
BOSS_PHASES = {
    # (min_hp, max_hp): (minimax_depth, speed, fire_rate)
    'phase1': {'hp_range': (7, 10), 'depth': 2, 'speed': SPEED_SLOW,   'fire': FIRE_SLOW},
    'phase2': {'hp_range': (3,  6), 'depth': 3, 'speed': SPEED_MEDIUM, 'fire': FIRE_FAST},
    'phase3': {'hp_range': (1,  2), 'depth': 4, 'speed': SPEED_FAST,   'fire': FIRE_RAPID},
}

# Colours
BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
RED    = (220, 50,  50)
GREEN  = (50,  200, 80)
YELLOW = (230, 210, 50)
GRAY   = (90,  90,  90)
ORANGE = (220, 130, 40)
CYAN   = (80,  200, 220)
PURPLE = (180, 60,  200)

# Level configs  (passed to CSP generator)
LEVEL_CONFIGS = {
    1: {
        'steel_density':  0.05,
        'brick_density':  0.30,
        'forest_density': 0.08,
        'water_density':  0.03,
        'grid_size':      GRID_SIZE,
        'eagle_pos':      EAGLE_POS,
        'spawn_points':   SPAWN_POINTS,
        'player_spawn':   PLAYER_SPAWN,
    },
    2: {
        'steel_density':  0.15,
        'brick_density':  0.20,
        'forest_density': 0.05,
        'water_density':  0.05,
        'grid_size':      GRID_SIZE,
        'eagle_pos':      EAGLE_POS,
        'spawn_points':   SPAWN_POINTS,
        'player_spawn':   PLAYER_SPAWN,
    },
    'boss': {
        'steel_density':  0.20,
        'brick_density':  0.15,
        'forest_density': 0.05,
        'water_density':  0.05,
        'grid_size':      BOSS_GRID_SIZE,
        'eagle_pos':      BOSS_EAGLE_POS,
        'spawn_points':   BOSS_SPAWN_PTS,
        'player_spawn':   BOSS_PLAYER_SPAWN,
    },
}
