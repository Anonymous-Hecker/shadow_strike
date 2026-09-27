"""
Main Menu — Retro arcade style using turok.ttf font
"""
import pygame
import math
import random
from settings import *
from core.asset_loader import load_logo, load_background, get_font, draw_text


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
        for e in self._embers:
            e["x"] += e["vx"] * dt * 60
            e["y"] += e["vy"] * dt * 60
            if e["y"] < -10:
                e["y"] = self.sh + 10
                e["x"] = random.uniform(0, self.sw)
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
