# ─────────────────────────────────────────────
#  tanks/base_tank.py  –  Shared tank base class
# ─────────────────────────────────────────────
from settings import *
from core.bullet import Bullet


class BaseTank:
    # ABSTRACT BASE CLASS: 
    # This class defines the shared properties of all tanks (HP, speed, shooting).

    # Override in subclasses
    MAX_HP       = 1
    MOVE_SPEED   = SPEED_SLOW     # ticks between moves
    FIRE_RATE    = FIRE_SLOW      # ticks between shots
    TANK_COLOR   = WHITE

    def __init__(self, x, y, direction='UP'):
        self.x = x
        self.y = y
        self.direction = direction   # 'UP'|'DOWN'|'LEFT'|'RIGHT'
        self.hp = self.MAX_HP
        self.alive = True

        self._move_timer = 0         # counts down to next allowed move
        self._fire_timer = 0         # counts down to next allowed shot
        self.bullet = None           # only one bullet at a time

    # ── HP / damage ───────────────────────────────────────────

    def take_hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.alive = False
        return self.alive

    # ── Movement ──────────────────────────────────────────────

    def try_move(self, direction, grid, all_tanks):
        # Moves the tank 1 tile in specified direction if the tile is passable 
        # and no other tanks occupy it. Returns True on success.
        deltas = {'UP': (0,-1), 'DOWN': (0,1), 'LEFT': (-1,0), 'RIGHT': (1,0)}
        self.direction = direction
        dx, dy = deltas[direction]
        nx, ny = self.x + dx, self.y + dy

        # Terrain check
        if not grid.is_passable(nx, ny):
            return False

        # Other tank collision
        for tank in all_tanks:
            if tank is not self and tank.alive and tank.x == nx and tank.y == ny:
                return False

        self.x, self.y = nx, ny
        return True

    # ── Shooting ──────────────────────────────────────────────

    def try_shoot(self):
        # Fire a bullet in current direction if fire timer allows.
        if self._fire_timer > 0:
            return None
        if self.bullet and self.bullet.alive:
            return None   # already a bullet in flight

        self._fire_timer = self.FIRE_RATE
        # Spawn bullet at tank's current tile center.
        # It will move into the next tile during its first update.
        self.bullet = Bullet(self.x, self.y, self.direction, owner=self)
        return self.bullet

    # ── Timer ticks ───────────────────────────────────────────

    def tick_timers(self):
        if self._move_timer > 0:
            self._move_timer -= 1
        if self._fire_timer > 0:
            self._fire_timer -= 1

    def can_move(self):
        return self._move_timer == 0

    def ready_to_move(self):
        # Reset move timer after a successful move.
        self._move_timer = self.MOVE_SPEED

    # ── Line-of-sight helper ──────────────────────────────────

    def has_los_to(self, tx, ty, grid):
        # LINE OF SIGHT (LOS) check:
        # Returns True if there are no solid walls (Steel/Water/Brick) 
        # between this tank and the target coordinate.
        if self.x == tx:
            for y in range(min(self.y, ty) + 1, max(self.y, ty)):
                if grid.get(self.x, y) in (BRICK, STEEL, WATER):
                    return False
            return True
        if self.y == ty:
            for x in range(min(self.x, tx) + 1, max(self.x, tx)):
                if grid.get(x, self.y) in (BRICK, STEEL, WATER):
                    return False
            return True
        return False

    # ── Direction helper ─────────────────────────────────────

    def direction_to(self, tx, ty):
        # Return the cardinal direction from this tank toward (tx, ty).
        dx = tx - self.x
        dy = ty - self.y
        if abs(dx) >= abs(dy):
            return 'RIGHT' if dx > 0 else 'LEFT'
        return 'DOWN' if dy > 0 else 'UP'

    # ── AI hook (override in subclasses) ─────────────────────

    def decide(self, grid, player, all_tanks, eagle_pos=None):
        # TO BE IMPLEMENTED BY SUBCLASSES: 
        # This is where the AI logic (A*, BFS, etc.) lives.
        # Called once per tick BEFORE movement.
        # Should call self.try_move() and/or self.try_shoot().
        # Returns a list of new Bullet objects fired this tick (may be empty).
        # eagle_pos – (x, y) of the Eagle tile for this level (passed by Game).
        raise NotImplementedError

    def update(self, grid, player, all_tanks, eagle_pos=None):
        # Full per-tick update: timers -> reflex -> decide -> return bullets.
        self.tick_timers()
        if not self.alive:
            return []
        
        bullets = []

        # 1. CONTINUOUS REFLEX CHECK (Runs 30 times a second; AI only)
        # This makes the tank react INSTANTLY to things directly in front.
        if self is not player:
            dx, dy = {'UP':(0,-1), 'DOWN':(0,1), 'LEFT':(-1,0), 'RIGHT':(1,0)}[self.direction]
            fx, fy = self.x + dx, self.y + dy
            
            target_tile = grid.get(fx, fy)
            target_is_player = (player.alive and player.x == fx and player.y == fy)
            
            # If there is a BRICK wall, the EAGLE, or the PLAYER in front, shoot immediately.
            if target_tile in (BRICK, EAGLE) or target_is_player:
                b = self.try_shoot()
                if b: bullets.append(b)

        # 2. AI MOVEMENT DECISION (Only runs when move timer is 0)
        # This handles the complex pathfinding (BFS, A*, etc.)
        if self.can_move():
            decision_bullets = self.decide(grid, player, all_tanks, eagle_pos=eagle_pos)
            if decision_bullets:
                bullets.extend(decision_bullets)
        
        return bullets

    def __repr__(self):
        return f"{self.__class__.__name__}({self.x},{self.y} hp={self.hp})"
