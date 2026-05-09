# ─────────────────────────────────────────────
#  core/spawner.py  –  Enemy spawn management
# ─────────────────────────────────────────────
import random
from settings import SPAWN_MIN_DIST


def manhattan(ax, ay, bx, by):
    return abs(ax - bx) + abs(ay - by)


class Spawner:
    # """
    # Manages a pool of enemy tank descriptors for one level.
    # Trickles them onto the map respecting the fairness constraint.
    # """

    def __init__(self, tank_pool, max_active=4, spawn_points=None):
        # """
        # tank_pool    – list of tank-type strings in spawn order
        # max_active   – max enemies on map at once (3–4 per spec)
        # spawn_points – list of (x,y) tuples; uses default if None
        # """
        from settings import SPAWN_POINTS as DEFAULT_SPAWNS
        self.pool = list(tank_pool)
        self.index = 0
        self.max_active = max_active
        self.spawn_points = spawn_points if spawn_points else DEFAULT_SPAWNS
        self.spawn_queue = []       # [delay_ticks, tank_type]
        self.spawn_delay = 60       # ticks after a kill before next spawn
        self._spawn_rotation = 0    # cycles through spawn_points

    def notify_kill(self):
        # Call this every time an enemy is destroyed.
        if self.index < len(self.pool):
            tank_type = self.pool[self.index]
            self.index += 1
            self.spawn_queue.append([self.spawn_delay, tank_type])

    def update(self, active_enemies, player_x, player_y):
        # Call once per tick.
        # Returns list of (spawn_x, spawn_y, tank_type) for tanks ready to spawn.
        spawns = []

        # Tick down pending spawns
        for entry in self.spawn_queue:
            entry[0] -= 1

        ready = [e for e in self.spawn_queue if e[0] <= 0]
        self.spawn_queue = [e for e in self.spawn_queue if e[0] > 0]

        for _, tank_type in ready:
            if len(active_enemies) >= self.max_active:
                # Re-queue with a small delay
                self.spawn_queue.append([30, tank_type])
                continue

            pos = self._pick_spawn_point(player_x, player_y)
            if pos:
                spawns.append((pos[0], pos[1], tank_type))

        return spawns

    def _pick_spawn_point(self, px, py):
        # Rotate through spawn points; enforce fairness constraint (C3).
        for _ in range(len(self.spawn_points)):
            sp = self.spawn_points[self._spawn_rotation % len(self.spawn_points)]
            self._spawn_rotation += 1
            if manhattan(sp[0], sp[1], px, py) >= SPAWN_MIN_DIST:
                return sp
        # Fallback: pick any spawn point
        return random.choice(self.spawn_points)

    def all_spawned(self):
        return self.index >= len(self.pool) and len(self.spawn_queue) == 0

    def remaining(self):
        return len(self.pool) - self.index + len(self.spawn_queue)
