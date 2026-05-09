# ─────────────────────────────────────────────
#  tanks/boss_tank.py  –  Adversarial Agent + Minimax + Alpha-Beta
# ─────────────────────────────────────────────
# AI SUMMARY
# ----------
# Agent Type : Adversarial Agent (Alpha-Beta Minimax)
# Behavior   : Strategically anticipates player moves and defends itself.
# Transitions: Changes speed and fire-rate based on remaining HP (3 phases).
from tanks.base_tank import BaseTank
from ai.minimax import get_boss_action
from settings import *


class BossTank(BaseTank):
    MAX_HP     = 10
    MOVE_SPEED = SPEED_SLOW    # updated per phase
    FIRE_RATE  = FIRE_SLOW     # updated per phase
    TANK_COLOR = (200, 30, 180)  # purple/magenta

    def __init__(self, x, y):
        super().__init__(x, y, direction='DOWN')
        self.phase = 1
        self.minimax_depth = 2
        self.last_report = {}    # stores node-count stats for HUD

    # ── Phase management ─────────────────────────────────────

    def _update_phase(self):
        if self.hp >= 7:
            phase = 1
        elif self.hp >= 3:
            phase = 2
        else:
            phase = 3

        if phase != self.phase:
            self.phase = phase
            cfg = list(BOSS_PHASES.values())[phase - 1]
            self.MOVE_SPEED    = cfg['speed']
            self.FIRE_RATE     = cfg['fire']
            self.minimax_depth = cfg['depth']

    def take_hit(self):
        result = super().take_hit()
        self._update_phase()
        return result

    # ── Minimax decision ─────────────────────────────────────

    def decide(self, grid, player, all_tanks, eagle_pos=None):
        bullets = []

        state = {
            'bx': self.x,  'by': self.y,
            'px': player.x, 'py': player.y,
            'boss_hp': self.hp,
            'player_hp': player.lives,
            'grid': grid,
        }

        action, report = get_boss_action(state, self.minimax_depth)
        self.last_report = report

        if action == 'SHOOT':
            b = self.try_shoot()
            if b:
                bullets.append(b)
        else:
            if self.try_move(action, grid, all_tanks):
                self.ready_to_move()

        return bullets
