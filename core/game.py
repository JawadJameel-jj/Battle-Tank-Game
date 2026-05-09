# ─────────────────────────────────────────────
#  core/game.py  –  Main Game class & game loop
# ─────────────────────────────────────────────
import pygame
from settings import *
from core.grid import Grid
from core.spawner import Spawner
from csp.map_generator import generate_map
from tanks.player_tank import PlayerTank
from tanks.basic_tank import BasicTank
from tanks.fast_tank import FastTank
from tanks.armor_tank import ArmorTank
from tanks.boss_tank import BossTank
from rendering.renderer import Renderer
from rendering.hud import HUD


# ── Level definitions ─────────────────────────────────────────

LEVEL_POOLS = {
    1: (['basic'] * 8 + ['fast'] * 4 + ['basic'] * 6 + ['fast'] * 2),  # 20 total
    2: (['fast'] * 4 + ['armor'] * 3 + ['fast'] * 3 + ['armor'] * 5 + ['fast'] * 5),  # 20 total
    'boss': ['boss'],
}


def make_tank(tank_type, x, y):
    return {
        'basic': BasicTank,
        'fast':  FastTank,
        'armor': ArmorTank,
        'boss':  BossTank,
    }[tank_type](x, y)


class Game:

    # The Game class is the heart of the engine. It manages the lifecycle of the application:
    # 1. Loading levels and generating procedural maps.
    # 2. Managing entity lists (player, enemies, bullets).
    # 3. Running the high-level 30FPS game loop.
    # 4. Mediating between Physics (Grid/Bullet) and Visuals (Renderer/HUD).

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Battle City — AI Lab Project")
        self.clock = pygame.time.Clock()

        # Initialize visual subsystems
        self.renderer = Renderer(self.screen)
        self.hud = HUD(self.screen)

        self.current_level = 1
        self._load_level(self.current_level)

    # ── Level loading ─────────────────────────────────────────

    def _load_level(self, level):
        # Resets the game state for a specific level.
        # Uses LEVEL_CONFIGS to fetch grid size and spawn positions.
        self.level = level
        cfg = LEVEL_CONFIGS.get(level, LEVEL_CONFIGS[1])
        grid_size    = cfg['grid_size']
        eagle_pos    = cfg['eagle_pos']
        spawn_points = cfg['spawn_points']
        player_spawn = cfg['player_spawn']

        self.eagle_pos    = eagle_pos
        self.spawn_points = spawn_points

        # 1. Generate a valid map using the CSP Generator
        self.grid = Grid(grid_size)
        tiles = generate_map(cfg)
        self.grid.load_tiles(tiles)

        # 2. Setup the Player
        self.player = PlayerTank(*player_spawn)
        self.enemies = []
        self.bullets = []

        # 3. Setup the Spawner with the level's specifically defined tank pool
        pool = LEVEL_POOLS.get(level, LEVEL_POOLS[1])
        max_active = 1 if level == 'boss' else 4
        self.spawner = Spawner(pool, max_active, spawn_points)

        # Immediately queue first enemies
        for _ in range(min(max_active, len(pool))):
            self.spawner.notify_kill()

        self.game_over   = False
        self.victory     = False
        self.paused      = False
        self.boss_report = {}

        # Update HUD panel position (boss level has smaller grid)
        panel_x = grid_size * TILE_SIZE
        self.hud.update_panel_x(panel_x)
        self.renderer.update_grid_pixel_w(panel_x)

    # ── Main run loop ─────────────────────────────────────────

    def run(self):
        while True:
            self._handle_events()

            if not self.game_over and not self.victory and not self.paused:
                self._update()

            self._render()
            self.clock.tick(FPS)

    # ── Event handling ────────────────────────────────────────

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); raise SystemExit
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                if (self.game_over or self.victory) and event.key == pygame.K_r:
                    self._load_level(self.current_level)
                if self.victory and event.key == pygame.K_n:
                    self._next_level()

    # ── Game update (one tick) ────────────────────────────────

    def _update(self):
        all_tanks = [self.player] + self.enemies

        # 1. Player decides (reads keyboard)
        new_bullets = self.player.update(self.grid, self.player, all_tanks)
        self.bullets.extend(new_bullets)

        # 2. Enemy AI decisions
        for enemy in self.enemies:
            if enemy.alive:
                new_b = enemy.update(self.grid, self.player, all_tanks,
                                     eagle_pos=self.eagle_pos)
                self.bullets.extend(new_b)
                # Store boss minimax stats for HUD
                if isinstance(enemy, BossTank):
                    self.boss_report = {**enemy.last_report, 'phase': enemy.phase}

        # 3. Update bullets
        for b in self.bullets:
            events = b.update(self.grid, all_tanks)
            for ev in events:
                if ev['type'] == 'eagle_hit':
                    self.game_over = True
                    return
                if ev['type'] == 'brick_destroyed':
                    # Notify tanks with cached paths
                    bx, by = ev['x'], ev['y']
                    for t in self.enemies:
                        if hasattr(t, 'notify_map_change'):
                            t.notify_map_change(self.grid)

        # 4. Bullet-vs-bullet collision (still handled at end of frame)
        self._check_bullet_bullet_collisions()

        # 5. Remove dead bullets
        self.bullets = [b for b in self.bullets if b.alive]

        # 7. Remove dead enemies, award score
        for enemy in self.enemies:
            if not enemy.alive:
                self.player.score += 100
                self.spawner.notify_kill()
        self.enemies = [e for e in self.enemies if e.alive]

        # 8. Spawn new enemies
        spawn_list = self.spawner.update(self.enemies, self.player.x, self.player.y)
        for sx, sy, tank_type in spawn_list:
            self.enemies.append(make_tank(tank_type, sx, sy))

        # 9. Win/lose checks
        if not self.player.alive:
            if self.player.lives > 0:
                self.player.respawn(*self._current_player_spawn())
            else:
                self.game_over = True

        all_defeated = (len(self.enemies) == 0 and self.spawner.all_spawned())
        if all_defeated:
            self.victory = True

    def _current_player_spawn(self):
        return LEVEL_CONFIGS[self.level]['player_spawn']

    # ── Collision helpers ─────────────────────────────────────

    def _check_bullet_tank_collisions(self):
        for b in self.bullets:
            if not b.alive:
                continue
            bx, by = b.tile_pos()

            # Bullet hitting player
            if b.owner is not self.player:
                if self.player.alive and self.player.x == bx and self.player.y == by:
                    self.player.take_hit()
                    b.alive = False

            # Bullet hitting enemies
            for enemy in self.enemies:
                if b.owner is enemy:
                    continue
                if enemy.alive and enemy.x == bx and enemy.y == by:
                    enemy.take_hit()
                    b.alive = False
                    break

    def _check_bullet_bullet_collisions(self):
        # Bullets from opposing sides that meet in the same tile cancel out.
        alive = [b for b in self.bullets if b.alive]
        for i in range(len(alive)):
            for j in range(i + 1, len(alive)):
                a, b = alive[i], alive[j]
                if not a.alive or not b.alive:
                    continue
                a_is_player = (a.owner is self.player)
                b_is_player = (b.owner is self.player)
                if a_is_player != b_is_player:
                    ax, ay = a.tile_pos()
                    bx, by = b.tile_pos()
                    if ax == bx and ay == by:
                        a.alive = False
                        b.alive = False

    # ── Rendering ─────────────────────────────────────────────

    def _render(self):
        self.screen.fill(BLACK)
        self.renderer.draw(self.grid, self.player, self.enemies, self.bullets, {})

        enemies_left = len(self.enemies) + self.spawner.remaining()
        boss_rep = self.boss_report if self.level == 'boss' else None
        self.hud.draw(self.player, enemies_left, self.level, boss_rep)

        if self.game_over:
            self.hud.draw_message("GAME OVER  (R to restart)", RED)
        elif self.victory:
            if self.level == 'boss':
                self.hud.draw_message("YOU WIN! (R to restart)", GREEN)
            else:
                self.hud.draw_message("LEVEL CLEAR!  N=Next  R=Retry", GREEN)

        if self.paused:
            self.hud.draw_message("PAUSED  (P to resume)", YELLOW)

        pygame.display.flip()

    # ── Level progression ─────────────────────────────────────

    def _next_level(self):
        if self.current_level == 1:
            self.current_level = 2
        elif self.current_level == 2:
            self.current_level = 'boss'
        self._load_level(self.current_level)
