# ─────────────────────────────────────────────
#  tanks/armor_tank.py  –  Model-Based Reflex Agent + A*
# ─────────────────────────────────────────────

# Agent type : Model-Based Reflex Agent
# Search     : A* (cost-aware; brick=3, steel=∞)
# Goal       : Reach and destroy the Eagle; retreat when badly damaged

# Internal state
# --------------
#   hit_count (0–3) : tracks how many times this tank has been hit
#   state           : 'attack' | 'retreat' | 'cover'

# Rule set
# --------
# Rule 1 (0–2 hits, state=attack): Navigate to Eagle via A*.
#                                   If player in LOS → shoot.
# Rule 2 (3rd hit, state=retreat) : Abandon A* path. BFS to nearest STEEL tile.
# Rule 3 (state=cover)            : Wait 2 s behind cover, then re-run A*.

from tanks.base_tank import BaseTank
from ai.astar import astar_next_step
from ai.bfs import bfs_next_step
from settings import *


COVER_WAIT = 60    # ~2 s at 30 FPS


class ArmorTank(BaseTank):
    MAX_HP     = 4
    MOVE_SPEED = SPEED_MEDIUM
    FIRE_RATE  = FIRE_MEDIUM
    TANK_COLOR = (180, 60, 60)   # dark red

    def __init__(self, x, y):
        super().__init__(x, y, direction='DOWN')
        self.hit_count    = 0
        self.state        = 'attack'    # 'attack' | 'retreat' | 'cover'
        self._cover_timer = 0
        self._cover_pos   = None
        self._eagle_pos   = EAGLE_POS

    # ── Override take_hit to track hit_count ──────────────────

    def take_hit(self):
        self.hit_count += 1
        result = super().take_hit()
        # Trigger retreat on 3rd hit (at 1 HP remaining)
        if self.hit_count >= 3 and self.alive:
            self.state = 'retreat'
        return result

    def notify_map_change(self, grid):
        # Invalidate A* path cache when map changes (A* recomputes next tick).
        pass

    # ── AI decision ──────────────────────────────────────────

    def decide(self, grid, player, all_tanks, eagle_pos=None):
        if eagle_pos:
            self._eagle_pos = eagle_pos

        if self.state == 'attack':
            return self._attack(grid, player, all_tanks)
        elif self.state == 'retreat':
            self._retreat(grid, all_tanks)
        elif self.state == 'cover':
            self._cover_wait(grid, all_tanks)
        return []

    # ── Attack behaviour ─────────────────────────────────────

    def _attack(self, grid, player, all_tanks):
        bullets = []

        # Shoot player if in line of sight
        if self.has_los_to(player.x, player.y, grid):
            self.direction = self.direction_to(player.x, player.y)
            b = self.try_shoot()
            if b:
                bullets.append(b)

        # A* navigation toward Eagle
        next_tile = astar_next_step(grid, (self.x, self.y), self._eagle_pos)

        if next_tile:
            tx, ty = next_tile
            if tx < self.x:   move_dir = 'LEFT'
            elif tx > self.x: move_dir = 'RIGHT'
            elif ty < self.y: move_dir = 'UP'
            else:             move_dir = 'DOWN'

            if self.try_move(move_dir, grid, all_tanks):
                self.ready_to_move()

        return bullets

    # ── Retreat behaviour ─────────────────────────────────────

    def _retreat(self, grid, all_tanks):
        # Find nearest STEEL tile for cover
        if self._cover_pos is None:
            self._cover_pos = grid.find_nearest(self.x, self.y, STEEL)

        if self._cover_pos is None:
            # No steel on map — just resume attacking
            self.state = 'attack'
            return

        cx, cy = self._cover_pos
        target = _adjacent_to(cx, cy, grid)
        if target is None:
            self.state = 'attack'
            return

        next_tile = bfs_next_step(grid, (self.x, self.y), target)
        if next_tile:
            tx, ty = next_tile
            if tx < self.x:   move_dir = 'LEFT'
            elif tx > self.x: move_dir = 'RIGHT'
            elif ty < self.y: move_dir = 'UP'
            else:             move_dir = 'DOWN'

            if self.try_move(move_dir, grid, all_tanks):
                self.ready_to_move()

        # Arrived at cover?
        if (self.x, self.y) == target:
            self.state = 'cover'
            self._cover_timer = COVER_WAIT

    # ── Cover-wait behaviour ──────────────────────────────────

    def _cover_wait(self, grid, all_tanks):
        self._cover_timer -= 1
        if self._cover_timer <= 0:
            # Resume attack with fresh A* path
            self.state = 'attack'
            self._cover_pos = None


# ── Utility ───────────────────────────────────────────────────

def _adjacent_to(sx, sy, grid):
    # Return the first passable tile adjacent to (sx, sy).
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = sx + dx, sy + dy
        if grid.is_passable(nx, ny):
            return (nx, ny)
    return None
