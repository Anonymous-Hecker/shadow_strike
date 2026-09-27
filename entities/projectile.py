"""
Projectile — Magic bolts, flame waves, poison bombs
"""
import pygame
import math
import random
from settings import *


class Projectile:
    def __init__(self, x, y, vx, vy, damage, color, owner, proj_type="magic", effect=None):
        self.x      = float(x)
        self.y      = float(y)
        self.vx     = vx
        self.vy     = vy
        self.damage = damage
        self.color  = color
        self.owner  = owner
        self.type   = proj_type
        self.effect = effect
        self.alive  = True
        self.radius = 12
        self.trail  = []
        self._age   = 0.0

        # Type-specific visual
        self._ring_phase = 0.0

    @property
    def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)

    def update(self, dt, arena_w):
        self.x    += self.vx * dt * 60
        self.y    += self.vy * dt * 60
        self._age += dt
        self._ring_phase += dt * 10

        # Trail
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 8:
            self.trail.pop(0)

        # Out of bounds
        if self.x < 0 or self.x > arena_w or self.y < -100 or self.y > GROUND_Y + 200:
            self.alive = False

        # Lifetime cap
        if self._age > 3.0:
            self.alive = False

    def check_hit(self, fighters):
        """Return fighter hit, if any."""
        for fighter in fighters:
            if fighter is self.owner:
                continue
            if fighter.state == "dead":
                continue
            if self.rect.colliderect(fighter.rect):
                self.alive = False
                return fighter
        return None

    def draw(self, surface):
        if not self.alive:
            return
        t = self._age
        # Trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(60 * (i / max(1, len(self.trail))))
            size  = max(1, int(self.radius * 0.5 * (i / max(1, len(self.trail)))))
            ts    = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(ts, (*self.color, alpha), (size + 1, size + 1), size)
            surface.blit(ts, (tx - size - 1, ty - size - 1), special_flags=pygame.BLEND_RGBA_ADD)

        # Main projectile body
        pulse = int(math.sin(self._ring_phase) * 3)
        r = self.radius + pulse

        glow = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, 60), (r * 2, r * 2), r * 2)
        pygame.draw.circle(glow, (*self.color, 120), (r * 2, r * 2), r)
        surface.blit(glow, (int(self.x) - r * 2, int(self.y) - r * 2), special_flags=pygame.BLEND_RGBA_ADD)

        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), r)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), max(2, r // 3))

        # Type-specific
        if self.type == "fire":
            for _ in range(2):
                fx = int(self.x) + random.randint(-r, r)
                fy = int(self.y) + random.randint(-r, r)
                pygame.draw.circle(surface, (255, 200, 0), (fx, fy), 3)
        elif self.type == "magic":
            # Orbiting spark
            for i in range(2):
                angle = self._ring_phase + i * math.pi
                sx = int(self.x + math.cos(angle) * r)
                sy = int(self.y + math.sin(angle) * r)
                pygame.draw.circle(surface, WHITE, (sx, sy), 3)
