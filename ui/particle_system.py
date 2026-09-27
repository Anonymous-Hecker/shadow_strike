"""
Particle System — Visual effects: sparks, magic, coins, crits, explosions
"""
import pygame
import math
import random
from settings import *


class Particle:
    def __init__(self, x, y, vx, vy, color, size, lifetime, fade=True, gravity=0.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.max_life = lifetime
        self.life = lifetime
        self.fade = fade
        self.gravity = gravity
        self.alive = True

    def update(self, dt):
        self.x  += self.vx * dt * 60
        self.y  += self.vy * dt * 60
        self.vy += self.gravity * dt * 60
        self.life -= dt
        if self.life <= 0:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        ratio = self.life / self.max_life
        alpha = int(255 * ratio) if self.fade else 255
        size  = max(1, int(self.size * ratio))
        if alpha < 10:
            return
        p_surf = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(p_surf, (*self.color, alpha), (size + 1, size + 1), size)
        surface.blit(p_surf, (int(self.x) - size - 1, int(self.y) - size - 1),
                     special_flags=pygame.BLEND_RGBA_ADD)


class TextParticle:
    """Floating damage/combo text."""
    def __init__(self, x, y, text, color, font, size_scale=1.0):
        self.x = float(x)
        self.y = float(y)
        self.text = text
        self.color = color
        self.font = font
        self.life = 1.2
        self.max_life = 1.2
        self.vy = -1.5
        self.alive = True
        self.size_scale = size_scale

    def update(self, dt):
        self.y   += self.vy * dt * 60
        self.vy  += 0.02 * dt * 60
        self.life -= dt
        if self.life <= 0:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        ratio = self.life / self.max_life
        alpha = int(255 * min(1.0, ratio * 2))
        scale = 0.6 + ratio * 0.4 * self.size_scale
        if alpha < 10:
            return
        rendered = self.font.render(self.text, True, self.color)
        w  = int(rendered.get_width()  * scale)
        h  = int(rendered.get_height() * scale)
        if w < 1 or h < 1:
            return
        scaled = pygame.transform.scale(rendered, (w, h))
        s_alpha = pygame.Surface((w, h), pygame.SRCALPHA)
        s_alpha.blit(scaled, (0, 0))
        s_alpha.set_alpha(alpha)
        surface.blit(s_alpha, (int(self.x) - w // 2, int(self.y) - h // 2))


class ParticleSystem:
    def __init__(self):
        self._particles  = []
        self._text_parts = []
        try:
            self._font_big   = pygame.font.SysFont("impact", 42, bold=True)
            self._font_mid   = pygame.font.SysFont("impact", 28, bold=True)
            self._font_small = pygame.font.SysFont("impact", 20, bold=True)
        except Exception:
            self._font_big   = pygame.font.Font(None, 42)
            self._font_mid   = pygame.font.Font(None, 28)
            self._font_small = pygame.font.Font(None, 20)
        self._screen_flash      = 0.0
        self._screen_flash_col  = (255, 0, 0)
        self._slow_mo_timer     = 0.0

    # ─── Emitters ─────────────────────────────────────────────────────────────

    def emit_hit_sparks(self, x, y, count=12):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 8)
            size  = random.randint(3, 7)
            life  = random.uniform(0.3, 0.7)
            col   = random.choice([(255, 200, 50), (255, 120, 0), (255, 60, 0)])
            self._particles.append(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed - 2,
                col, size, life, gravity=0.2
            ))

    def emit_magic_explosion(self, x, y, color=(140, 60, 255), count=20):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 6)
            size  = random.randint(4, 10)
            life  = random.uniform(0.5, 1.0)
            col_var = tuple(min(255, c + random.randint(-30, 30)) for c in color)
            self._particles.append(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed - 1,
                col_var, size, life, gravity=0.05
            ))
        # Center flash
        self._screen_flash = 0.15
        self._screen_flash_col = color

    def emit_fire(self, x, y, count=8):
        for _ in range(count):
            vx = random.uniform(-1.5, 1.5)
            vy = random.uniform(-4, -1)
            size = random.randint(4, 9)
            life = random.uniform(0.4, 0.9)
            col = random.choice([(255, 60, 0), (255, 120, 0), (255, 200, 0)])
            self._particles.append(Particle(
                x + random.randint(-15, 15), y,
                vx, vy, col, size, life, gravity=-0.05
            ))

    def emit_coin(self, x, y, count=8):
        for _ in range(count):
            angle = random.uniform(-math.pi, 0)
            speed = random.uniform(2, 5)
            size  = random.randint(3, 6)
            life  = random.uniform(0.5, 0.9)
            self._particles.append(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                GOLD, size, life, gravity=0.15
            ))

    def emit_blood(self, x, y, count=8):
        for _ in range(count):
            angle = random.uniform(math.pi * 0.7, math.pi * 1.3)
            speed = random.uniform(1, 5)
            size  = random.randint(2, 5)
            life  = random.uniform(0.3, 0.7)
            self._particles.append(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed - 2,
                (180, 0, 0), size, life, gravity=0.2
            ))

    def emit_lightning(self, x, y, count=6):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(3, 9)
            size  = random.randint(2, 5)
            life  = random.uniform(0.2, 0.5)
            col   = random.choice([(80, 160, 255), (180, 220, 255), (255, 255, 255)])
            self._particles.append(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                col, size, life, gravity=0.0
            ))

    def emit_confetti(self, x, y, count=40):
        cols = [RED, GREEN, BLUE, YELLOW, PURPLE, CYAN, ORANGE, PINK]
        for _ in range(count):
            vx = random.uniform(-5, 5)
            vy = random.uniform(-8, -2)
            size = random.randint(4, 8)
            life = random.uniform(1.0, 2.0)
            self._particles.append(Particle(
                x + random.randint(-200, 200), y,
                vx, vy,
                random.choice(cols), size, life, gravity=0.1, fade=True
            ))

    def emit_smoke(self, x, y, count=5):
        for _ in range(count):
            vx = random.uniform(-1, 1)
            vy = random.uniform(-2, -0.5)
            size = random.randint(8, 18)
            life = random.uniform(0.8, 1.5)
            col = random.choice([(80, 80, 100), (60, 60, 80), (100, 100, 120)])
            self._particles.append(Particle(
                x + random.randint(-20, 20), y,
                vx, vy, col, size, life, gravity=-0.02
            ))

    def emit_poison(self, x, y, count=8):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 4)
            size  = random.randint(3, 7)
            life  = random.uniform(0.5, 1.0)
            col   = (60 + random.randint(-20,20), 200 + random.randint(-20,20), 60)
            self._particles.append(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed - 1,
                col, size, life, gravity=0.05
            ))

    # ─── Text Effects ─────────────────────────────────────────────────────────

    def show_damage(self, x, y, amount, is_crit=False):
        text = f"{amount}"
        if is_crit:
            text = f"CRIT! {amount}"
        color = YELLOW if is_crit else WHITE
        font  = self._font_big if is_crit else self._font_mid
        self._text_parts.append(TextParticle(x, y - 40, text, color, font,
                                             size_scale=1.5 if is_crit else 1.0))
        if is_crit:
            self.trigger_screen_flash((255, 200, 0))

    def show_combo(self, x, y, count):
        text = f"{count} HIT COMBO!"
        if count >= 8:
            text = f"💀 {count} HIT DEVASTATION!"
        col = (255, min(255, 100 + count * 15), 0)
        self._text_parts.append(TextParticle(x, y - 80, text, col, self._font_big,
                                             size_scale=1.0 + count * 0.05))

    def show_critical_label(self, x, y, crit_name, color):
        self._text_parts.append(TextParticle(x, y - 120, crit_name.upper(),
                                             color, self._font_big, size_scale=1.3))
        self.trigger_screen_flash(color)

    def show_coin(self, x, y, amount):
        text = f"+{amount} 💰"
        self._text_parts.append(TextParticle(x, y, text, GOLD, self._font_small))
        self.emit_coin(x, y)

    def show_text(self, x, y, text, color=WHITE, big=False):
        font = self._font_big if big else self._font_mid
        self._text_parts.append(TextParticle(x, y, text, color, font))

    # ─── Screen Effects ────────────────────────────────────────────────────────

    def trigger_screen_flash(self, color=(255, 255, 255), intensity=0.4):
        self._screen_flash     = intensity
        self._screen_flash_col = color

    def trigger_slow_mo(self, duration=0.3):
        self._slow_mo_timer = duration

    @property
    def time_scale(self):
        return 0.2 if self._slow_mo_timer > 0 else 1.0

    # ─── Update & Draw ────────────────────────────────────────────────────────

    def update(self, dt):
        if self._slow_mo_timer > 0:
            self._slow_mo_timer = max(0, self._slow_mo_timer - dt)
        if self._screen_flash > 0:
            self._screen_flash = max(0, self._screen_flash - dt * 4)

        for p in self._particles:
            p.update(dt)
        for tp in self._text_parts:
            tp.update(dt)

        self._particles  = [p  for p  in self._particles  if p.alive]
        self._text_parts = [tp for tp in self._text_parts if tp.alive]

    def draw(self, surface):
        for p in self._particles:
            p.draw(surface)
        for tp in self._text_parts:
            tp.draw(surface)

    def draw_screen_flash(self, surface, sw, sh):
        if self._screen_flash > 0.01:
            alpha = int(self._screen_flash * 180)
            flash = pygame.Surface((sw, sh), pygame.SRCALPHA)
            flash.fill((*self._screen_flash_col, alpha))
            surface.blit(flash, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
