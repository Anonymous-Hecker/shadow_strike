"""
Fighter Renderer — Uses per-state sprite frames.
No round aura. Only subtle flame behind fighter during Rage/Aggressive activation.
"""
import pygame
import math
import random
from settings import *
from core.asset_loader import get_sprite


class FighterRenderer:
    def __init__(self):
        self._bob = {}
        self._flame_particles = {}  # pid -> list of flame particles
        self._prev_state = {}       # pid -> previous state name
        self._transition = {}       # pid -> transition timer (0.0 to 1.0)
        self._TRANS_SPEED = 8.0     # how fast transitions happen (higher = faster)

    def draw(self, surface, fighter, aura_intensity=0.0):
        pid = fighter.player_num
        t   = pygame.time.get_ticks() / 1000.0

        # Track state transitions for smooth blending
        curr_state = fighter.state
        prev = self._prev_state.get(pid, curr_state)
        if curr_state != prev:
            self._prev_state[pid] = curr_state
            self._transition[pid] = 0.0  # start transition
        else:
            # Advance transition toward 1.0
            trans = self._transition.get(pid, 1.0)
            if trans < 1.0:
                trans = min(1.0, trans + self._TRANS_SPEED / 60.0)
                self._transition[pid] = trans

        # Bob animation — different per state
        if fighter.state == "walk":
            # Shuffle-step bob: faster, more pronounced to simulate footsteps
            self._bob[pid] = abs(math.sin(t * 8.0 + pid)) * 5
        elif fighter.state in ("idle", "block"):
            # Idle breathing: gentle slow bob
            self._bob[pid] = math.sin(t * 2.5 + pid * 1.5) * 2
        elif fighter.state == "jump":
            self._bob[pid] = 0
        else:
            self._bob[pid] = math.sin(t * 10 + pid) * 2

        bob = self._bob.get(pid, 0)

        sprite = get_sprite(fighter.char_id, fighter.facing, fighter.state)

        if sprite:
            self._draw_sprite(surface, fighter, sprite, bob, t)
        else:
            self._draw_silhouette(surface, fighter, bob, t)

        # Rage flame — ONLY when rage is active
        if fighter.rage_active:
            self._draw_rage_flame(surface, fighter, t)

        # Status effect tags
        self._draw_status(surface, fighter, t)

    def _draw_sprite(self, surface, fighter, sprite, bob, t):
        pid = fighter.player_num
        sw = sprite.get_width()
        sh = sprite.get_height()
        x  = fighter.rect.centerx - sw // 2
        y  = fighter.rect.bottom - sh + int(bob)

        # Smooth transition: scale pop on state change
        trans = self._transition.get(pid, 1.0)
        if trans < 1.0:
            # Slight scale-up then settle effect
            ease = 1.0 + 0.08 * math.sin(trans * math.pi)  # peaks at 0.5
            new_sw = int(sw * ease)
            new_sh = int(sh * ease)
            sprite = pygame.transform.smoothscale(sprite, (new_sw, new_sh))
            x = fighter.rect.centerx - new_sw // 2
            y = fighter.rect.bottom - new_sh + int(bob)
            sw, sh = new_sw, new_sh

        # Drop shadow on ground
        shadow = pygame.Surface((sw, 14), pygame.SRCALPHA)
        shadow_w = max(20, sw - 30)
        pygame.draw.ellipse(shadow, (0, 0, 0, 90),
                            ((sw - shadow_w) // 2, 2, shadow_w, 10))
        surface.blit(shadow, (x, fighter.rect.bottom - 8))

        # Block shield visual
        if fighter.is_blocking:
            shield_x = x + (sw + 4 if fighter.facing == 1 else -20)
            shield_y = y + sh // 4
            sh_surf = pygame.Surface((18, 50), pygame.SRCALPHA)
            pygame.draw.rect(sh_surf, (50, 120, 210, 170),
                             (0, 0, 18, 50), border_radius=4)
            pygame.draw.rect(sh_surf, (120, 180, 255, 200),
                             (0, 0, 18, 50), 2, border_radius=4)
            surface.blit(sh_surf, (shield_x, shield_y))

        # Draw the actual sprite with state-appropriate tinting
        if fighter.state == "hurt":
            flash = sprite.copy()
            flash.fill((200, 40, 40, 0), special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(flash, (x, y))
        elif fighter.state in ("attack_light", "attack_heavy", "special",
                                "super", "dash", "counter", "slam"):
            atk = sprite.copy()
            atk.fill((30, 30, 30, 0), special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(atk, (x, y))
        else:
            surface.blit(sprite, (x, y))


    def _draw_silhouette(self, surface, fighter, bob, t):
        """Shadow Fight 2 style silhouette — proper human proportions."""
        cx = fighter.rect.centerx
        cy = fighter.rect.bottom + int(bob)
        f  = fighter.facing
        col = (12, 8, 8)

        # Drop shadow
        shadow = pygame.Surface((70, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 85), (0, 2, 70, 10))
        surface.blit(shadow, (cx - 35, cy - 8))

        # Head
        pygame.draw.circle(surface, col, (cx, cy - 115), 16)

        # Neck
        pygame.draw.line(surface, col, (cx, cy - 99), (cx, cy - 90), 6)

        # Torso
        points_torso = [
            (cx - 16, cy - 90), (cx + 16, cy - 90),
            (cx + 12, cy - 45), (cx - 12, cy - 45),
        ]
        pygame.draw.polygon(surface, col, points_torso)

        # Legs
        if fighter.state == "walk":
            swing = math.sin(t * 8) * 10
            pygame.draw.line(surface, col, (cx - 6, cy - 45),
                             (cx - 10 + int(swing), cy - 4), 8)
            pygame.draw.line(surface, col, (cx + 6, cy - 45),
                             (cx + 10 - int(swing), cy - 4), 8)
        elif fighter.state == "jump":
            pygame.draw.line(surface, col, (cx - 6, cy - 45), (cx - 18, cy - 15), 8)
            pygame.draw.line(surface, col, (cx + 6, cy - 45), (cx + 18, cy - 15), 8)
        else:
            pygame.draw.line(surface, col, (cx - 6, cy - 45), (cx - 12, cy - 4), 8)
            pygame.draw.line(surface, col, (cx + 6, cy - 45), (cx + 12, cy - 4), 8)

        # Arms
        aura = fighter.char_data.get("aura_color", (160, 30, 30))
        if fighter.state in ("attack_light", "attack_heavy", "dash",
                              "counter", "slam", "special", "super"):
            # Striking arm extended
            pygame.draw.line(surface, col, (cx + f * 14, cy - 82),
                             (cx + f * 50, cy - 60), 7)
            pygame.draw.line(surface, col, (cx - f * 12, cy - 82),
                             (cx - f * 28, cy - 92), 6)
            # Weapon glow at tip
            tip_x = cx + f * 52
            tip_y = cy - 58
            glow = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*aura, 160), (8, 8), 7)
            surface.blit(glow, (tip_x - 8, tip_y - 8),
                         special_flags=pygame.BLEND_RGBA_ADD)
            pygame.draw.line(surface, aura,
                             (cx + f * 38, cy - 64), (tip_x, tip_y), 3)
        elif fighter.state == "block":
            pygame.draw.line(surface, col, (cx + f * 14, cy - 82),
                             (cx + f * 32, cy - 56), 7)
            pygame.draw.line(surface, col, (cx - f * 12, cy - 82),
                             (cx + f * 22, cy - 66), 7)
        elif fighter.state == "hurt":
            pygame.draw.line(surface, col, (cx + f * 14, cy - 82),
                             (cx - f * 10, cy - 60), 6)
            pygame.draw.line(surface, col, (cx - f * 12, cy - 82),
                             (cx - f * 30, cy - 72), 6)
        else:
            # Idle arms
            arm_swing = math.sin(t * 3.5) * 4
            pygame.draw.line(surface, col, (cx + 14, cy - 82),
                             (cx + 30, cy - 62 + int(arm_swing)), 7)
            pygame.draw.line(surface, col, (cx - 12, cy - 82),
                             (cx - 26, cy - 66 - int(arm_swing)), 6)

        # Glowing eyes
        eye_x = cx + f * 5
        pygame.draw.circle(surface, aura, (eye_x, cy - 117), 3)
        pygame.draw.circle(surface, (255, 255, 255), (eye_x, cy - 117), 1)

    def _draw_rage_flame(self, surface, fighter, t):
        """Subtle colored flame rising behind character — NOT a circle."""
        cx = fighter.rect.centerx
        bot = fighter.rect.bottom
        aura = fighter.char_data.get("aura_color", (255, 60, 0))
        pid = fighter.player_num

        # Maintain persistent flame particles
        if pid not in self._flame_particles:
            self._flame_particles[pid] = []

        particles = self._flame_particles[pid]

        # Spawn new flame wisps
        if len(particles) < 12:
            particles.append({
                "x": cx + random.uniform(-20, 20),
                "y": bot - random.uniform(10, 40),
                "vx": random.uniform(-0.3, 0.3),
                "vy": random.uniform(-2.5, -1.2),
                "life": random.uniform(0.4, 1.0),
                "max_life": 1.0,
                "size": random.randint(6, 14),
            })

        # Update and draw
        alive = []
        for p in particles:
            p["life"] -= 1 / 60
            if p["life"] <= 0:
                continue
            p["x"] += p["vx"] * 60 / 60
            p["y"] += p["vy"] * 60 / 60
            p["vx"] += random.uniform(-0.1, 0.1)

            ratio = max(0, p["life"] / p["max_life"])
            alpha = int(ratio * 120)
            size  = max(1, int(p["size"] * ratio))

            flame = pygame.Surface((size * 2, size * 3), pygame.SRCALPHA)
            # Flame shape: tall ellipse tapering upward
            pygame.draw.ellipse(flame, (*aura, alpha),
                                (0, 0, size * 2, size * 3))
            surface.blit(flame, (int(p["x"]) - size,
                                  int(p["y"]) - size * 2),
                         special_flags=pygame.BLEND_RGBA_ADD)
            alive.append(p)

        self._flame_particles[pid] = alive

    def _draw_status(self, surface, fighter, t):
        """Status effect tags + shield bar."""
        effects = fighter.status_effects
        if effects:
            icon_map = {
                "burn":   ((255, 100, 0),  "BRN"),
                "bleed":  ((180,   0, 0),  "BLD"),
                "slow":   (( 80, 140, 255), "SLW"),
                "poison": (( 50, 200, 50),  "PSN"),
            }
            from core.asset_loader import get_font
            font = get_font(12)
            ix = fighter.rect.left
            iy = fighter.rect.top - 20
            for eff, (col, lbl) in icon_map.items():
                if eff in effects:
                    bg = pygame.Surface((28, 14), pygame.SRCALPHA)
                    bg.fill((*col, 130))
                    surface.blit(bg, (ix, iy))
                    ts = font.render(lbl, True, (255, 255, 255))
                    surface.blit(ts, (ix + 2, iy + 1))
                    ix += 30

        if fighter.shield_hp > 0:
            cx = fighter.rect.centerx
            gy = fighter.rect.top - 10
            ratio = min(1.0, fighter.shield_hp / 30)
            pygame.draw.rect(surface, (12, 35, 70),
                             (cx - 24, gy, 48, 6), border_radius=3)
            pygame.draw.rect(surface, (55, 140, 255),
                             (cx - 24, gy, int(48 * ratio), 6), border_radius=3)
