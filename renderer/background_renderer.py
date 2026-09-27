"""
Background Renderer — Real image backgrounds with animated overlays
"""
import pygame
import math
import random
from settings import *
from core.asset_loader import load_background

STAGE_NAMES = ["dojo", "ruins", "rooftop", "volcano", "palace",
               "temple_new", "storm_castle", "night_market"]

class BackgroundRenderer:
    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h
        self._stage_index = 0
        self._bg = None
        self._particles = []
        self._t = 0.0
        # Ground line drawn over background
        self._ground_y = GROUND_Y

    def set_stage(self, index):
        self._stage_index = index % len(STAGE_NAMES)
        name = STAGE_NAMES[self._stage_index]
        self._bg = load_background(name, self.sw, self.sh)
        self._particles = []
        self._init_stage_particles(name)

    def _init_stage_particles(self, name):
        """Seed stage-specific ambient particles."""
        if name == "dojo":
            # Cherry blossom petals
            for _ in range(30):
                self._particles.append({
                    "type": "petal",
                    "x": random.uniform(0, self.sw),
                    "y": random.uniform(0, self.sh),
                    "vx": random.uniform(-0.5, -0.2),
                    "vy": random.uniform(0.3, 0.8),
                    "size": random.randint(3, 6),
                    "color": (255, 180, 200),
                    "rot": random.uniform(0, 360),
                    "rot_speed": random.uniform(-2, 2),
                })
        elif name == "ruins":
            # Ember sparks
            for _ in range(25):
                self._particles.append({
                    "type": "ember",
                    "x": random.uniform(0, self.sw),
                    "y": random.uniform(self.sh * 0.4, self.sh),
                    "vx": random.uniform(-0.3, 0.3),
                    "vy": random.uniform(-1.2, -0.4),
                    "size": random.randint(2, 5),
                    "color": random.choice([(255, 120, 0), (255, 200, 0), (255, 60, 0)]),
                })
        elif name == "rooftop":
            # Rain drops
            for _ in range(60):
                self._particles.append({
                    "type": "rain",
                    "x": random.uniform(0, self.sw),
                    "y": random.uniform(0, self.sh),
                    "vy": random.uniform(8, 14),
                    "len": random.randint(8, 16),
                })
        elif name == "volcano":
            # Lava embers
            for _ in range(35):
                self._particles.append({
                    "type": "lava",
                    "x": random.uniform(0, self.sw),
                    "y": random.uniform(self.sh * 0.6, self.sh),
                    "vx": random.uniform(-0.5, 0.5),
                    "vy": random.uniform(-2, -0.8),
                    "size": random.randint(3, 7),
                    "color": random.choice([(255, 80, 0), (255, 160, 0), (255, 40, 0)]),
                    "life": random.uniform(0, 2),
                })
        elif name == "palace":
            # Candle flicker motes
            for _ in range(20):
                self._particles.append({
                    "type": "mote",
                    "x": random.uniform(100, self.sw - 100),
                    "y": random.uniform(100, self.sh - 200),
                    "vx": random.uniform(-0.2, 0.2),
                    "vy": random.uniform(-0.5, -0.1),
                    "size": random.randint(2, 4),
                    "color": (255, 180, 80),
                    "alpha": random.randint(80, 200),
                })
        elif name == "temple_new":
            # Torch sparks + floating ash
            for _ in range(28):
                self._particles.append({
                    "type": "ember",
                    "x": random.uniform(0, self.sw),
                    "y": random.uniform(self.sh * 0.3, self.sh),
                    "vx": random.uniform(-0.4, 0.4),
                    "vy": random.uniform(-1.5, -0.5),
                    "size": random.randint(2, 5),
                    "color": random.choice([(255, 150, 30), (255, 220, 80), (200, 80, 0)]),
                    "life": random.uniform(0, 2),
                })
        elif name == "storm_castle":
            # Heavy rain + occasional lightning
            for _ in range(80):
                self._particles.append({
                    "type": "rain",
                    "x": random.uniform(0, self.sw),
                    "y": random.uniform(0, self.sh),
                    "vy": random.uniform(12, 20),
                    "len": random.randint(12, 22),
                })
        elif name == "night_market":
            # Light rain + red lantern glow motes
            for _ in range(40):
                self._particles.append({
                    "type": "rain",
                    "x": random.uniform(0, self.sw),
                    "y": random.uniform(0, self.sh),
                    "vy": random.uniform(6, 10),
                    "len": random.randint(8, 14),
                })
            for _ in range(15):
                self._particles.append({
                    "type": "mote",
                    "x": random.uniform(50, self.sw - 50),
                    "y": random.uniform(50, self.sh * 0.6),
                    "vx": random.uniform(-0.15, 0.15),
                    "vy": random.uniform(-0.3, -0.05),
                    "size": random.randint(3, 6),
                    "color": (255, 80, 60),
                    "alpha": random.randint(100, 200),
                })


    def draw(self, surface, dt):
        self._t += dt

        # Draw background image
        if self._bg:
            surface.blit(self._bg, (0, 0))
        else:
            surface.fill(DARK_BG)

        # Darken bottom to make ground readable
        darken = pygame.Surface((self.sw, 160), pygame.SRCALPHA)
        darken.fill((0, 0, 0, 80))
        surface.blit(darken, (0, self.sh - 160))

        # Ground line
        pygame.draw.line(surface, (40, 25, 10), (0, self._ground_y), (self.sw, self._ground_y), 3)
        # Ground shadow gradient
        for i in range(15):
            a = int(70 - i * 4)
            if a <= 0: break
            gs = pygame.Surface((self.sw, 2), pygame.SRCALPHA)
            gs.fill((0, 0, 0, a))
            surface.blit(gs, (0, self._ground_y + i * 2))

        # Ambient particles
        self._update_draw_particles(surface, dt)

    def _update_draw_particles(self, surface, dt):
        name = STAGE_NAMES[self._stage_index]

        for p in self._particles:
            ptype = p["type"]

            if ptype == "petal":
                p["x"] += p["vx"] * dt * 60
                p["y"] += p["vy"] * dt * 60
                p["rot"] += p["rot_speed"] * dt * 60
                if p["y"] > self.sh + 10:
                    p["y"] = -10
                    p["x"] = random.uniform(0, self.sw)
                ps = pygame.Surface((p["size"]*2, p["size"]*2), pygame.SRCALPHA)
                pygame.draw.ellipse(ps, (*p["color"], 180), (0, 0, p["size"]*2, p["size"]*2))
                rotated = pygame.transform.rotate(ps, p["rot"])
                surface.blit(rotated, (int(p["x"]), int(p["y"])))

            elif ptype in ("ember", "lava"):
                p["x"] += p["vx"] * dt * 60
                p["y"] += p["vy"] * dt * 60
                p["life"] = p.get("life", 0) + dt
                if p["y"] < self.sh * 0.2 or p["life"] > 3.0:
                    p["y"] = random.uniform(self.sh * 0.6, self.sh)
                    p["x"] = random.uniform(0, self.sw)
                    p["life"] = 0
                alpha = int(200 - (p.get("life", 0) / 3.0) * 160)
                ps = pygame.Surface((p["size"]*2, p["size"]*2), pygame.SRCALPHA)
                pygame.draw.circle(ps, (*p["color"], max(0, alpha)), (p["size"], p["size"]), p["size"])
                surface.blit(ps, (int(p["x"]) - p["size"], int(p["y"]) - p["size"]),
                             special_flags=pygame.BLEND_RGBA_ADD)

            elif ptype == "rain":
                p["y"] += p["vy"] * dt * 60
                if p["y"] > self.sh + 20:
                    p["y"] = -20
                    p["x"] = random.uniform(0, self.sw)
                pygame.draw.line(surface, (140, 160, 200),
                                 (int(p["x"]), int(p["y"])),
                                 (int(p["x"]) - 2, int(p["y"]) + p["len"]), 1)

            elif ptype == "mote":
                p["x"] += p["vx"] * dt * 60
                p["y"] += p["vy"] * dt * 60
                p["alpha"] = int(100 + math.sin(self._t * 3 + p["x"]) * 80)
                if p["y"] < 50:
                    p["y"] = random.uniform(100, self.sh - 200)
                    p["x"] = random.uniform(100, self.sw - 100)
                ps = pygame.Surface((p["size"]*2, p["size"]*2), pygame.SRCALPHA)
                pygame.draw.circle(ps, (*p["color"], p["alpha"]), (p["size"], p["size"]), p["size"])
                surface.blit(ps, (int(p["x"]), int(p["y"])), special_flags=pygame.BLEND_RGBA_ADD)
