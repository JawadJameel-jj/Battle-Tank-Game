# ─────────────────────────────────────────────
#  tanks/player_tank.py  –  Human-controlled tank
# ─────────────────────────────────────────────
import pygame
from tanks.base_tank import BaseTank
from settings import *


class PlayerTank(BaseTank):
    MAX_HP     = 1
    MOVE_SPEED = SPEED_MEDIUM
    FIRE_RATE  = 20             # fairly responsive
    TANK_COLOR = GREEN

    def __init__(self, x, y):
        super().__init__(x, y, direction='UP')
        self.lives = 5
        self.score = 0
        self._spawn_x = x
        self._spawn_y = y

    def decide(self, grid, player, all_tanks, eagle_pos=None):
        # Read keyboard and act.
        keys = pygame.key.get_pressed()
        bullets = []

        moved = False
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            if self.try_move('UP', grid, all_tanks):
                moved = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            if self.try_move('DOWN', grid, all_tanks):
                moved = True
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if self.try_move('LEFT', grid, all_tanks):
                moved = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if self.try_move('RIGHT', grid, all_tanks):
                moved = True

        if moved:
            self.ready_to_move()

        if keys[pygame.K_SPACE]:
            b = self.try_shoot()
            if b:
                bullets.append(b)

        return bullets

    def respawn(self, spawn_x=None, spawn_y=None):
        # Called after the player loses a life.
        self.lives -= 1
        self.hp = self.MAX_HP
        self.alive = True
        self.x = spawn_x if spawn_x is not None else self._spawn_x
        self.y = spawn_y if spawn_y is not None else self._spawn_y
        self.direction = 'UP'
        self.bullet = None
        self._fire_timer = 0
        self._move_timer = 0
