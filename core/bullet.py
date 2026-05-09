# ─────────────────────────────────────────────
#  core/bullet.py  –  Bullet movement & collision
# ─────────────────────────────────────────────
from settings import BULLET_SPEED, BRICK, STEEL, WATER, EAGLE, EMPTY


# Direction vectors
DIR_VECTORS = {
    'UP':    (0, -1),
    'DOWN':  (0,  1),
    'LEFT':  (-1, 0),
    'RIGHT': (1,  0),
}


class Bullet:
    def __init__(self, x, y, direction, owner):
        # x, y      – tile position (floats for sub-tile movement tracking)
        # direction – 'UP' | 'DOWN' | 'LEFT' | 'RIGHT'
        # owner     – reference to the tank that fired this bullet
        self.x = float(x)
        self.y = float(y)
        self.direction = direction
        self.owner = owner
        self.alive = True
        self.speed = BULLET_SPEED
        dx, dy = DIR_VECTORS[direction]
        self.dx = dx * self.speed
        self.dy = dy * self.speed

    def update(self, grid, all_tanks):
        # Advance bullet position and check collisions. 
        # Uses a 'tile-stepping' algorithm: instead of jumping across tiles,
        # he bullet iterates through every integer coordinate it crosses to 
        # ensure it never 'ghosts' through walls or tanks.
        if not self.alive:
            return []

        events = []
        old_tx, old_ty = int(self.x), int(self.y)
        
        # Advance sub-tile coordinates
        self.x += self.dx
        self.y += self.dy
        
        new_tx, new_ty = int(self.x), int(self.y)

        # Generate list of tiles to check (from current to new)
        tiles_to_check = []
        if old_tx == new_tx: # Vertical
            step = 1 if new_ty > old_ty else -1
            for ty in range(old_ty, new_ty + step, step):
                tiles_to_check.append((old_tx, ty))
        else: # Horizontal
            step = 1 if new_tx > old_tx else -1
            for tx in range(old_tx, new_tx + step, step):
                tiles_to_check.append((tx, old_ty))

        for tx, ty in tiles_to_check:
            if not grid.in_bounds(tx, ty):
                self.alive = False
                return events

            # 1. Check Tank Collisions
            for tank in all_tanks:
                if tank.alive and tank.x == tx and tank.y == ty:
                    if tank is not self.owner:
                        tank.take_hit()
                        self.alive = False
                        events.append({'type': 'tank_hit', 'tank': tank})
                        return events

            # 2. Check Terrain Collisions
            tile = grid.get(tx, ty)
            if tile == BRICK:
                grid.destroy_brick(tx, ty)
                self.alive = False
                events.append({'type': 'brick_destroyed', 'x': tx, 'y': ty})
                return events
            elif tile == STEEL or tile == WATER:
                self.alive = False
                events.append({'type': 'blocked', 'x': tx, 'y': ty})
                return events
            elif tile == EAGLE:
                self.alive = False
                events.append({'type': 'eagle_hit'})
                return events

        return events

    def tile_pos(self):
        return int(round(self.x)), int(round(self.y))

    def __repr__(self):
        return f"Bullet({self.x:.1f},{self.y:.1f} {self.direction})"
