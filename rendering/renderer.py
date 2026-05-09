# ─────────────────────────────────────────────
#  rendering/renderer.py  –  Pygame drawing
# ─────────────────────────────────────────────
import pygame
from settings import *


# Direction → rotation angle for tank sprite arrow
DIR_ANGLES = {'UP': 0, 'RIGHT': 90, 'DOWN': 180, 'LEFT': 270}


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font_sm = pygame.font.SysFont('monospace', 13)
        self.font_md = pygame.font.SysFont('monospace', 16, bold=True)
        self._grid_pixel_w = GRID_SIZE * TILE_SIZE  # width of grid area in pixels

    def update_grid_pixel_w(self, w):
        # Called by Game when a new level is loaded with a different grid size.
        self._grid_pixel_w = w

    # ── Master draw call ─────────────────────────────────────

    def draw(self, grid, player, enemies, bullets, game_state):
        # Clear only the grid area (HUD fills its own panel)
        pygame.draw.rect(self.screen, BLACK,
                         (0, 0, self._grid_pixel_w, SCREEN_H))
        self._draw_grid(grid)
        self._draw_tanks(player, enemies)
        self._draw_bullets(bullets)

    # ── Grid ─────────────────────────────────────────────────

    def _draw_grid(self, grid):
        for y in range(grid.size):
            for x in range(grid.size):
                tile = grid.get(x, y)
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                color = TILE_COLORS.get(tile, BLACK)
                pygame.draw.rect(self.screen, color, rect)

                # Draw brick mortar lines
                if tile == BRICK:
                    pygame.draw.rect(self.screen, (100, 40, 10), rect, 1)
                    mid = TILE_SIZE // 2
                    pygame.draw.line(self.screen, (100, 40, 10),
                                     (rect.x, rect.y + mid), (rect.right, rect.y + mid), 1)
                    pygame.draw.line(self.screen, (100, 40, 10),
                                     (rect.x + mid, rect.y), (rect.x + mid, rect.y + mid), 1)

                # Steel cross-hatch
                elif tile == STEEL:
                    pygame.draw.rect(self.screen, (80, 80, 100), rect, 1)
                    pygame.draw.line(self.screen, (80, 80, 100),
                                     (rect.x, rect.y), (rect.right, rect.bottom), 1)
                    pygame.draw.line(self.screen, (80, 80, 100),
                                     (rect.right, rect.y), (rect.x, rect.bottom), 1)

                # Water wave
                elif tile == WATER:
                    wave_y = rect.centery
                    pygame.draw.line(self.screen, (20, 50, 200),
                                     (rect.x, wave_y), (rect.right, wave_y), 1)
                    pygame.draw.line(self.screen, (40, 80, 220),
                                     (rect.x, wave_y - 2), (rect.centerx, wave_y - 2), 1)

                # Forest tree dots
                elif tile == FOREST:
                    pygame.draw.circle(self.screen, (20, 90, 30),
                                       (rect.centerx, rect.centery), TILE_SIZE // 3)

                # Eagle star
                elif tile == EAGLE:
                    self._draw_eagle(rect)

    def _draw_eagle(self, rect):
        # Draw a more visible eagle / star symbol.
        cx, cy = rect.centerx, rect.centery
        r = TILE_SIZE // 2 - 2
        # Outer 8-point star
        pts = []
        import math
        for i in range(8):
            angle = math.radians(i * 45 - 90)
            radius = r if i % 2 == 0 else r // 2
            pts.append((cx + radius * math.cos(angle),
                         cy + radius * math.sin(angle)))
        pygame.draw.polygon(self.screen, (255, 220, 30), pts)
        pygame.draw.polygon(self.screen, (200, 140, 0), pts, 1)

    # ── Tanks ─────────────────────────────────────────────────

    def _draw_tanks(self, player, enemies):
        if player.alive:
            self._draw_one_tank(player, player.TANK_COLOR)
        for tank in enemies:
            if tank.alive:
                color = tank.TANK_COLOR
                # Armor tank: flash lighter color when hit
                if hasattr(tank, 'hit_count') and tank.hit_count > 0:
                    import time
                    if int(time.time() * 6) % 2 == 0:
                        color = (255, 80, 80)
                self._draw_one_tank(tank, color)

    def _draw_one_tank(self, tank, color):
        x = tank.x * TILE_SIZE
        y = tank.y * TILE_SIZE
        size = TILE_SIZE

        # Tank body (rounded feel with inset)
        body = pygame.Rect(x + 2, y + 2, size - 4, size - 4)
        pygame.draw.rect(self.screen, color, body, border_radius=3)
        pygame.draw.rect(self.screen, WHITE, body, 1, border_radius=3)

        # Barrel (direction arrow)
        cx, cy = x + size // 2, y + size // 2
        barrel_len = size // 2
        d = tank.direction
        bx = cx + (barrel_len if d == 'RIGHT' else (-barrel_len if d == 'LEFT' else 0))
        by = cy + (barrel_len if d == 'DOWN'  else (-barrel_len if d == 'UP'    else 0))
        pygame.draw.line(self.screen, WHITE, (cx, cy), (bx, by), 3)

        # HP bar (shown for any multi-HP tank)
        if tank.MAX_HP > 1:
            hp_frac = tank.hp / tank.MAX_HP
            bar_w = size - 4
            pygame.draw.rect(self.screen, (80, 0, 0), (x + 2, y - 5, bar_w, 3))
            hp_color = GREEN if hp_frac > 0.5 else (ORANGE if hp_frac > 0.25 else RED)
            pygame.draw.rect(self.screen, hp_color, (x + 2, y - 5, int(bar_w * hp_frac), 3))

    # ── Bullets ──────────────────────────────────────────────

    def _draw_bullets(self, bullets):
        for b in bullets:
            if not b.alive:
                continue
            px = int(b.x * TILE_SIZE) + TILE_SIZE // 2 - 2
            py = int(b.y * TILE_SIZE) + TILE_SIZE // 2 - 2
            # Player bullets = yellow; enemy bullets = red
            color = YELLOW if b.owner.__class__.__name__ == 'PlayerTank' else RED
            pygame.draw.rect(self.screen, color, (px, py, 4, 4))
            # Small glow effect
            pygame.draw.rect(self.screen, WHITE, (px + 1, py + 1, 2, 2))
