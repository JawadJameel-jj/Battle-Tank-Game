# ─────────────────────────────────────────────
#  rendering/hud.py  –  Heads-Up Display
# ─────────────────────────────────────────────
import pygame
from settings import *


class HUD:
    def __init__(self, screen):
        self.screen = screen
        self.font_sm = pygame.font.SysFont('monospace', 13)
        self.font_md = pygame.font.SysFont('monospace', 15, bold=True)
        self.font_lg = pygame.font.SysFont('monospace', 20, bold=True)
        self.panel_x = GRID_SIZE * TILE_SIZE + 8

    def update_panel_x(self, grid_pixel_w):
        # Called by Game when a level with a different grid size is loaded.
        self.panel_x = grid_pixel_w + 8

    def draw(self, player, enemies_remaining, level, boss_report=None):
        px = self.panel_x
        panel_rect = pygame.Rect(px - 8, 0, SCREEN_W - px + 8, SCREEN_H)
        pygame.draw.rect(self.screen, (18, 18, 18), panel_rect)
        pygame.draw.line(self.screen, GRAY, (px - 8, 0), (px - 8, SCREEN_H), 2)

        y = 12

        # Title
        self._text("BATTLE CITY", px, y, self.font_lg, YELLOW)
        y += 30

        self._divider(y); y += 10

        # Level
        level_name = {1: 'Level 1', 2: 'Level 2', 'boss': '★ BOSS ★'}.get(level, str(level))
        lvl_color  = RED if level == 'boss' else WHITE
        self._text(f"LEVEL: {level_name}", px, y, self.font_md, lvl_color)
        y += 24

        self._divider(y); y += 10

        # Player stats
        self._text("PLAYER", px, y, self.font_md, GREEN)
        y += 20

        # Life icons
        life_icon = "♥ "
        lives_str  = life_icon * min(player.lives, 5)
        if player.lives > 5:
            lives_str += f"+{player.lives - 5}"
        self._text(lives_str, px, y, self.font_sm, RED)
        y += 18

        self._text(f"Lives : {player.lives}", px, y, self.font_sm, WHITE)
        y += 16
        self._text(f"Score : {player.score}", px, y, self.font_sm, WHITE)
        y += 24

        self._divider(y); y += 10

        # Enemy count
        self._text("ENEMIES", px, y, self.font_md, RED)
        y += 20
        self._text(f"Left  : {enemies_remaining}", px, y, self.font_sm, WHITE)
        y += 24

        # Boss Minimax stats (shown in boss level)
        if boss_report:
            self._divider(y); y += 10
            self._text("MINIMAX", px, y, self.font_md, ORANGE)
            y += 20

            phase_labels = {1: 'Aggressive', 2: 'Tactical', 3: 'Desperate'}
            phase_num  = boss_report.get('phase', 1)
            phase_name = phase_labels.get(phase_num, '?')
            phase_col  = {1: RED, 2: ORANGE, 3: YELLOW}.get(phase_num, WHITE)
            self._text(f"Phase : {phase_name}", px, y, self.font_sm, phase_col)
            y += 16

            self._text(f"Depth : {boss_report.get('depth', '?')}", px, y, self.font_sm, WHITE)
            y += 16
            self._text(f"Nodes : {boss_report.get('nodes_with_pruning', '?')}", px, y, self.font_sm, CYAN)
            y += 16
            self._text(f"NoPrune:{boss_report.get('nodes_without_pruning', '?')}", px, y, self.font_sm, GRAY)
            y += 16

            speedup = boss_report.get('speedup', '?')
            self._text(f"Speedup:{speedup}x", px, y, self.font_sm, YELLOW)
            y += 24

        # AI Legend
        self._divider(y); y += 10
        self._text("AI TYPES", px, y, self.font_md, GRAY)
        y += 18
        legend = [
            ((200, 160, 60), "Basic  = BFS"),
            ((80, 200, 220), "Fast   = Greedy"),
            ((180, 60,  60), "Armor  = A*"),
            ((200, 30, 180), "Boss   = Minimax"),
        ]
        for col, label in legend:
            pygame.draw.rect(self.screen, col, (px, y + 2, 8, 8))
            self._text(f"  {label}", px, y, self.font_sm, GRAY)
            y += 14

        # Controls reminder
        self._divider(y + 4); y += 14
        self._text("CONTROLS", px, y, self.font_md, GRAY)
        y += 18
        for line in ["WASD/Arrows", "  move tank", "SPACE  shoot",
                     "P      pause", "R      restart", "N      next lvl"]:
            self._text(line, px, y, self.font_sm, (70, 70, 70))
            y += 14

    def draw_message(self, text, color=YELLOW):
        # Draw a centered overlay message (win/lose/pause).
        surf = self.font_lg.render(text, True, color)
        grid_w = self.panel_x - 8
        rx = max(0, (grid_w - surf.get_width()) // 2)
        ry = SCREEN_H // 2 - 20
        bg = pygame.Rect(rx - 12, ry - 10, surf.get_width() + 24, surf.get_height() + 20)
        pygame.draw.rect(self.screen, (0, 0, 0, 200), bg)
        pygame.draw.rect(self.screen, color, bg, 2)
        self.screen.blit(surf, (rx, ry))

    # ── Helpers ──────────────────────────────────────────────

    def _text(self, msg, x, y, font, color):
        surf = font.render(msg, True, color)
        self.screen.blit(surf, (x, y))

    def _divider(self, y):
        pygame.draw.line(self.screen, (50, 50, 50),
                         (self.panel_x - 8, y),
                         (self.panel_x + 148, y), 1)
