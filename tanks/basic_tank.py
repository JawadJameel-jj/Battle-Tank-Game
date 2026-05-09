# ─────────────────────────────────────────────
#  tanks/basic_tank.py  –  Simple Reflex Agent + BFS
# ─────────────────────────────────────────────
# AI SUMMARY
# ----------
# Agent Type : Model-Based Reflex Agent
# Search     : A* (Cost-Aware Search)
# Behavior   : Smartest non-boss enemy. Uses retreat logic when HP is low.
#              Prefers empty paths but will blast through bricks if efficient.
import random
from tanks.base_tank import BaseTank
from ai.bfs import bfs_next_step
from settings import *


class BasicTank(BaseTank):
    MAX_HP     = 1
    MOVE_SPEED = SPEED_SLOW
    FIRE_RATE  = FIRE_SLOW
    TANK_COLOR = (200, 160, 60)   # tan/gold

    def __init__(self, x, y):
        super().__init__(x, y, direction='DOWN')
        self._path_cache   = None    # cached next-step tile
        self._replan_timer = 0       # ticks until next forced replan
        self._eagle_pos    = EAGLE_POS  # updated on first decide()

    # ── BFS path management ───────────────────────────────────

    def _replan(self, grid):
        next_step = bfs_next_step(grid, (self.x, self.y), self._eagle_pos)
        self._path_cache   = next_step
        self._replan_timer = BFS_REPLAN_INTERVAL

    def notify_map_change(self, grid):
        # Called by the game when a nearby wall is destroyed.
        self._replan(grid)

    # ── Reflex rules ─────────────────────────────────────────

    def decide(self, grid, player, all_tanks, eagle_pos=None):
        if eagle_pos:
            self._eagle_pos = eagle_pos

        bullets = []
        self._replan_timer -= 1

        # Rule 1: shoot player if in line of sight
        if self.has_los_to(player.x, player.y, grid):
            self.direction = self.direction_to(player.x, player.y)
            b = self.try_shoot()
            if b:
                bullets.append(b)

        # Replan if timer expired or cache invalid
        if self._replan_timer <= 0 or self._path_cache is None:
            self._replan(grid)

        next_tile = self._path_cache

        if next_tile:
            tx, ty = next_tile
            if tx < self.x:   move_dir = 'LEFT'
            elif tx > self.x: move_dir = 'RIGHT'
            elif ty < self.y: move_dir = 'UP'
            else:             move_dir = 'DOWN'

            # Rule 2: follow BFS path
            if self.try_move(move_dir, grid, all_tanks):
                self.ready_to_move()
                self._path_cache = None   # invalidate; will replan next tick
        else:
            # Rule 4: no path found → random free direction
            dirs = ['UP', 'DOWN', 'LEFT', 'RIGHT']
            random.shuffle(dirs)
            for d in dirs:
                if self.try_move(d, grid, all_tanks):
                    self.ready_to_move()
                    break

        return bullets
