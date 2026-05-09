# ─────────────────────────────────────────────
#  tanks/fast_tank.py  –  Goal-Based Agent + Greedy Best-First
# ─────────────────────────────────────────────

# Agent type : Goal-Based Agent
# Search     : Greedy Best-First (single-step, Manhattan heuristic)
# Goal       : Destroy the Eagle — player is completely ignored

# Rule set
# --------
# 1. Always move toward the neighbour tile with lowest Manhattan distance to Eagle.
# 2. IF next tile is BRICK → SHOOT to clear path. Do NOT detour.
# 3. Never engages the player.

# Known failure: can get stuck in local minima (walls on three sides).
# This is intentional — demonstrates why greedy ≠ optimal.

from tanks.base_tank import BaseTank
from ai.greedy import greedy_single_step
from settings import *


class FastTank(BaseTank):
    MAX_HP     = 1
    MOVE_SPEED = SPEED_FAST
    FIRE_RATE  = FIRE_FAST
    TANK_COLOR = (80, 200, 220)   # cyan

    def __init__(self, x, y):
        super().__init__(x, y, direction='DOWN')
        self._eagle_pos = EAGLE_POS

    def decide(self, grid, player, all_tanks, eagle_pos=None):
        if eagle_pos:
            self._eagle_pos = eagle_pos

        bullets = []
        
        # New Reflex Point: Defensive Fire
        # If player in LOS, turn and shoot them even if goal-based
        if self.has_los_to(player.x, player.y, grid):
            self.direction = self.direction_to(player.x, player.y)
            b = self.try_shoot()
            if b: bullets.append(b)

        gx, gy = self._eagle_pos
        # Greedy single-step: pick neighbour closest to Eagle
        next_tile = greedy_single_step(grid, self.x, self.y, gx, gy)

        if next_tile:
            tx, ty = next_tile

            if tx < self.x:   move_dir = 'LEFT'
            elif tx > self.x: move_dir = 'RIGHT'
            elif ty < self.y: move_dir = 'UP'
            else:             move_dir = 'DOWN'

            # Always try to move in that direction (reflex handles walls)
            if self.try_move(move_dir, grid, all_tanks):
                self.ready_to_move()
        else:
            # Completely stuck — try to shoot in current direction to break free
            b = self.try_shoot()
            if b:
                bullets.append(b)

        return bullets
