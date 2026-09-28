"""
Main Menu — Retro arcade style using turok.ttf font
"""
import pygame
import math
import random
from settings import *
from core.asset_loader import load_logo, load_background, get_font, draw_text, get_sprite


def _draw_menu_silhouette(surface, cx, ground_y, t, state="idle"):
    """Animated Shadow Fight-style silhouette for the main menu showcase panel."""
    col = (15, 12, 12)
    # Bob
    bob = int(math.sin(t * 2.5) * 4)
    base_y = ground_y + bob

    # Shadow
    sh = pygame.Surface((80, 14), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 80), (0, 2, 80, 10))
    surface.blit(sh, (cx - 40, ground_y - 6))

    # Head
    pygame.draw.circle(surface, col, (cx, base_y - 180), 22)
    # Neck
    pygame.draw.line(surface, col, (cx, base_y - 158), (cx, base_y - 145), 9)
    # Torso
    pts = [(cx - 22, base_y - 145), (cx + 22, base_y - 145),
           (cx + 18, base_y - 70), (cx - 18, base_y - 70)]
    pygame.draw.polygon(surface, col, pts)

    # Legs
    if state in ("attack_light", "attack_heavy"):
        pygame.draw.line(surface, col, (cx - 8, base_y - 70), (cx - 28, base_y - 10), 12)
        pygame.draw.line(surface, col, (cx + 8, base_y - 70), (cx + 20, base_y - 10), 12)
    else:
        swing = math.sin(t * 4) * 12
        pygame.draw.line(surface, col, (cx - 8, base_y - 70), (cx - 18 + int(swing), base_y - 10), 12)
        pygame.draw.line(surface, col, (cx + 8, base_y - 70), (cx + 18 - int(swing), base_y - 10), 12)

    # Arms
    if state in ("attack_light", "attack_heavy", "special"):
        pygame.draw.line(surface, col, (cx + 20, base_y - 138), (cx + 70, base_y - 110), 10)
        pygame.draw.line(surface, col, (cx - 18, base_y - 138), (cx - 38, base_y - 155), 9)
    else:
        arm_sw = math.sin(t * 3) * 5
        pygame.draw.line(surface, col, (cx + 20, base_y - 138),
                         (cx + 42, base_y - 115 + int(arm_sw)), 10)
        pygame.draw.line(surface, col, (cx - 18, base_y - 138),
                         (cx - 36, base_y - 118 - int(arm_sw)), 9)


class MainMenuScreen:
    def __init__(self, screen, audio, save_manager):
        self.screen = screen
        self.audio  = audio
        self.save   = save_manager
        self.sw     = screen.get_width()
        self.sh     = screen.get_height()
        self._t     = 0.0
        self._selected = 0
        self._options  = ["PLAY", "DOJO", "SKILLS", "ARMORY", "PROFILE", "SETTINGS", "QUIT"]
        self._action   = None
        self._embers   = []
        self._init_embers()
        self._bg   = load_background("volcano", self.sw, self.sh)
        self._logo = load_logo(620, 190)
        self.audio.play_music()

        # Animated showcase fighter on the right side
        self._showcase_chars  = ["mage", "ninja", "samurai", "warrior", "phantom"]
        self._showcase_idx    = 0
        self._showcase_timer  = 0.0
        self._showcase_switch = 4.0   # seconds before switching character
        # Animated pose cycling
        self._anim_states = ["idle", "attack_light", "attack_heavy", "special", "idle", "idle"]
        self._anim_idx    = 0
        self._anim_timer  = 0.0
        self._anim_hold   = [1.2, 0.4, 0.5, 0.6, 0.8, 1.0]  # hold time for each pose

    def _init_embers(self):
        for _ in range(45):
            self._embers.append({
                "x": random.uniform(0, self.sw),
                "y": random.uniform(0, self.sh),
                "vx": random.uniform(-0.4, 0.4),
                "vy": random.uniform(-1.6, -0.5),
                "size": random.randint(2, 5),
                "color": random.choice([(255, 100, 0),(255, 190, 0),(200, 50, 0)]),
                "alpha": random.randint(120, 230),
            })

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self._selected = (self._selected - 1) % len(self._options)
                self.audio.play_sfx("select")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._selected = (self._selected + 1) % len(self._options)
                self.audio.play_sfx("select")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.audio.play_sfx("confirm")
                self._action = self._options[self._selected]
            elif event.key == pygame.K_ESCAPE:
                self._action = "QUIT"
        elif event.type == pygame.MOUSEMOTION:
            for i in range(len(self._options)):
                if self._opt_rect(i).collidepoint(event.pos):
                    if self._selected != i:
                        self._selected = i
                        self.audio.play_sfx("select")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i in range(len(self._options)):
                if self._opt_rect(i).collidepoint(event.pos):
                    self.audio.play_sfx("confirm")
                    self._action = self._options[i]

    def _opt_rect(self, i):
        return pygame.Rect(self.sw // 2 - 185, 290 + i * 52, 370, 44)

    def update(self, dt):
        self._t += dt

        # Advance embers
        for e in self._embers:
            e["x"] += e["vx"] * dt * 60
            e["y"] += e["vy"] * dt * 60
            if e["y"] < -10:
                e["y"] = self.sh + 10
                e["x"] = random.uniform(0, self.sw)

        # Advance showcase fighter animation
        self._anim_timer += dt
        hold = self._anim_hold[self._anim_idx % len(self._anim_hold)]
        if self._anim_timer >= hold:
            self._anim_timer = 0.0
            self._anim_idx   = (self._anim_idx + 1) % len(self._anim_states)

        # Switch character every N seconds
        self._showcase_timer += dt
        if self._showcase_timer >= self._showcase_switch:
            self._showcase_timer = 0.0
            self._showcase_idx   = (self._showcase_idx + 1) % len(self._showcase_chars)
            self._anim_idx       = 0
            self._anim_timer     = 0.0

        result = self._action
        self._action = None
        return result

    def _draw_menu_icon(self, option, x, y, col):
        """Draw a small procedural icon for each menu item."""
        s = self.screen
        if option == "PLAY":
            # Crossed swords
            pygame.draw.line(s, col, (x-6, y-8), (x+6, y+8), 3)
            pygame.draw.line(s, col, (x+6, y-8), (x-6, y+8), 3)
            pygame.draw.circle(s, col, (x, y), 3)
        elif option == "DOJO":
            # Torii gate shape
            pygame.draw.line(s, col, (x-8, y-8), (x+8, y-8), 3)
            pygame.draw.line(s, col, (x-6, y+8), (x-6, y-8), 2)
            pygame.draw.line(s, col, (x+6, y+8), (x+6, y-8), 2)
            pygame.draw.line(s, col, (x-10, y-6), (x+10, y-6), 2)
        elif option == "SKILLS":
            # Star/Tree shape
            pygame.draw.line(s, col, (x, y-8), (x, y+8), 2)
            pygame.draw.line(s, col, (x-6, y-2), (x+6, y-2), 2)
            pygame.draw.line(s, col, (x-4, y+4), (x+4, y-6), 2)
            pygame.draw.line(s, col, (x+4, y+4), (x-4, y-6), 2)
        elif option == "ARMORY":
            # Shield + sword
            pygame.draw.line(s, col, (x+3, y-10), (x+3, y+8), 3)
            pygame.draw.line(s, col, (x-2, y-4), (x+8, y-4), 2)
            pts = [(x-8, y-6), (x-2, y-8), (x-2, y+6), (x-8, y+4)]
            pygame.draw.polygon(s, col, pts, 2)
        elif option == "PROFILE":
            # Head + body figure
            pygame.draw.circle(s, col, (x, y-5), 4, 2)
            pygame.draw.line(s, col, (x, y-1), (x, y+6), 2)
            pygame.draw.line(s, col, (x-5, y+3), (x+5, y+3), 2)
        elif option == "SETTINGS":
            # Gear / cog shape
            pygame.draw.circle(s, col, (x, y), 6, 2)
            pygame.draw.circle(s, col, (x, y), 2)
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                ex = x + int(8 * math.cos(rad))
                ey = y + int(8 * math.sin(rad))
                pygame.draw.circle(s, col, (ex, ey), 2)
        elif option == "QUIT":
            # X mark
            pygame.draw.line(s, col, (x-6, y-6), (x+6, y+6), 3)
            pygame.draw.line(s, col, (x+6, y-6), (x-6, y+6), 3)

    def draw(self):
        t  = self._t
        sw, sh = self.sw, self.sh

        # Background
        if self._bg:
            self.screen.blit(self._bg, (0, 0))
        else:
            self.screen.fill((10, 3, 3))

        # Dark gradient overlay (top transparent, bottom dark)
        dark = pygame.Surface((sw, sh), pygame.SRCALPHA)
        for y in range(sh):
            ratio = y / sh
            a = int(ratio * 180)
            pygame.draw.line(dark, (0, 0, 0, a), (0, y), (sw, y))
        self.screen.blit(dark, (0, 0))

        # Embers
        for e in self._embers:
            es = pygame.Surface((e["size"]*2, e["size"]*2), pygame.SRCALPHA)
            pygame.draw.circle(es, (*e["color"], e["alpha"]),
                               (e["size"], e["size"]), e["size"])
            self.screen.blit(es, (int(e["x"]), int(e["y"])),
                             special_flags=pygame.BLEND_RGBA_ADD)

        # ── Animated showcase fighter (right side) ────────────────────────────
        char_id   = self._showcase_chars[self._showcase_idx]
        anim_state = self._anim_states[self._anim_idx % len(self._anim_states)]
        # facing left so it looks into the menu
        sprite = get_sprite(char_id, facing=-1, state=anim_state)

        fighter_x = sw - 200   # right edge x center
        fighter_ground_y = sh - 100

        if sprite:
            # Scale to a nice tall size
            target_h = int(sh * 0.55)
            ratio    = target_h / sprite.get_height()
            target_w = int(sprite.get_width() * ratio)
            big_sprite = pygame.transform.smoothscale(sprite, (target_w, target_h))

            # Subtle idle bob
            bob = math.sin(t * 2.2) * 5

            # Glow pedestal beneath
            ped_surf = pygame.Surface((target_w + 60, 30), pygame.SRCALPHA)
            pygame.draw.ellipse(ped_surf, (200, 80, 0, 55), (0, 0, target_w + 60, 30))
            self.screen.blit(ped_surf, (fighter_x - target_w // 2 - 30,
                                        fighter_ground_y - 8))

            # Vertical glow behind fighter
            glow_h = target_h + 40
            glow_w = target_w + 20
            glow = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)
            for gi in range(0, glow_w // 2, 4):
                a = max(0, 30 - gi * 2)
                pygame.draw.rect(glow, (220, 80, 0, a),
                                 (gi, 0, glow_w - gi * 2, glow_h), border_radius=20)
            self.screen.blit(glow, (fighter_x - glow_w // 2, fighter_ground_y - glow_h + 10),
                             special_flags=pygame.BLEND_RGBA_ADD)

            sx = fighter_x - target_w // 2
            sy = int(fighter_ground_y - target_h + bob)
            self.screen.blit(big_sprite, (sx, sy))

            # Character name tag below
            from characters.character_data import get_character
            try:
                cdata = get_character(char_id)
                name  = cdata["name"].upper()
            except Exception:
                name = char_id.upper()
            draw_text(self.screen, name, 22, (220, 170, 80),
                      fighter_x, fighter_ground_y + 8, center=True, shadow=True)

        else:
            # Fallback: animated silhouette
            _draw_menu_silhouette(self.screen, fighter_x, fighter_ground_y, t, anim_state)

        # Logo or text title
        logo_y = 28
        if self._logo:
            pulse = math.sin(t * 1.4) * 4
            lx = sw // 2 - self._logo.get_width() // 2
            # Warm glow behind logo
            gw = self._logo.get_width() + 60
            gh = self._logo.get_height() + 30
            glow = pygame.Surface((gw, gh), pygame.SRCALPHA)
            ga   = int(50 + math.sin(t * 2) * 15)
            pygame.draw.ellipse(glow, (180, 60, 0, ga), (0, 0, gw, gh))
            self.screen.blit(glow, (lx - 30, logo_y - 15), special_flags=pygame.BLEND_RGBA_ADD)
            self.screen.blit(self._logo, (lx, logo_y + int(pulse)))
        else:
            draw_text(self.screen, "SHADOW STRIKE", 90, (200, 20, 20),
                      sw // 2, logo_y + 50, shadow=True, shadow_color=(0,0,0), center=True)

        # Player info bar
        gid   = self.save.get("gamer_id", "WARRIOR")
        level = self.save.get("level", 1)
        coins = self.save.get("coins", 0)
        bar   = pygame.Surface((sw, 34), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 170))
        pygame.draw.line(bar, (80, 50, 15), (0, 33), (sw, 33), 1)
        self.screen.blit(bar, (0, 258))
        draw_text(self.screen, f"{gid.upper()}    LV. {level}    COINS: {coins}",
                  20, (200, 160, 80), sw // 2, 265,
                  shadow=False, center=True)

        # Menu items
        for i, opt in enumerate(self._options):
            rect   = self._opt_rect(i)
            is_sel = (i == self._selected)
            pulse_y = int(math.sin(t * 5) * 2) if is_sel else 0

            bg = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            if is_sel:
                pygame.draw.rect(bg, (130, 10, 10, 220), (0,0,rect.w,rect.h), border_radius=4)
                pygame.draw.rect(bg, GOLD, (0,0,rect.w,rect.h), 2, border_radius=4)
            else:
                pygame.draw.rect(bg, (8, 5, 5, 180), (0,0,rect.w,rect.h), border_radius=4)
                pygame.draw.rect(bg, (70, 45, 15), (0,0,rect.w,rect.h), 1, border_radius=4)
            self.screen.blit(bg, (rect.x, rect.y + pulse_y))

            # Draw per-item icon
            icon_x = rect.x + 14
            icon_y = rect.y + 18 + pulse_y
            icon_col = GOLD if is_sel else (180, 150, 100)
            self._draw_menu_icon(opt, icon_x, icon_y, icon_col)

            col   = GOLD if is_sel else (210, 190, 150)
            draw_text(self.screen, opt, 34, col,
                      rect.x + 42, rect.y + 10 + pulse_y, shadow=True, shadow_color=(0,0,0))

        # Bottom hint
        draw_text(self.screen, "W/S  NAVIGATE      ENTER  SELECT      F11  FULLSCREEN      ESC  QUIT",
                  16, (100, 75, 45), sw // 2, sh - 26, shadow=False, center=True)
        draw_text(self.screen, "SHADOW STRIKE  v1.0",
                  14, (55, 38, 18), sw - 4, sh - 22, shadow=False)
