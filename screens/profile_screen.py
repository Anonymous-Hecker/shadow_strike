"""
Profile Screen — Player stats, win/loss record, equipped gear
Uses turok.ttf via asset_loader.get_font() / draw_text()
"""
import pygame
import math
from settings import *
from core.asset_loader import get_font, draw_text as dt, load_background, get_idle_sprite


class ProfileScreen:
    def __init__(self, screen, audio, save_manager):
        self.screen = screen
        self.audio  = audio
        self.save   = save_manager
        self.sw     = screen.get_width()
        self.sh     = screen.get_height()
        self._t     = 0.0
        self._action = None
        self._bg    = load_background("dojo", self.sw, self.sh)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._action = "back"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if pygame.Rect(10, 10, 120, 40).collidepoint(*event.pos):
                self._action = "back"

    def update(self, dt_val):
        self._t += dt_val
        result = self._action
        self._action = None
        return result

    def draw(self):
        t = self._t
        sw, sh = self.sw, self.sh

        # Background
        if self._bg:
            self.screen.blit(self._bg, (0, 0))
        else:
            self.screen.fill(DARK_BG)

        # Dark overlay
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Back button
        back_r = pygame.Rect(10, 10, 120, 40)
        pygame.draw.rect(self.screen, (40, 15, 8, 220), back_r, border_radius=6)
        pygame.draw.rect(self.screen, GOLD, back_r, 2, border_radius=6)
        dt(self.screen, "< BACK", 20, GOLD, back_r.centerx, back_r.y + 10,
           shadow=True, center=True)

        # Title — Gamer ID
        gamer_id = self.save.get("gamer_id", "Shadow Warrior")
        dt(self.screen, gamer_id.upper(), 52, GOLD, sw // 2, 20,
           shadow=True, center=True, outline=True, outline_color=(40, 20, 0))

        # XP Bar
        level   = self.save.get("level", 1)
        xp      = self.save.get("xp", 0)
        xp_next = self.save.get("xp_to_next", 100)

        dt(self.screen, f"LEVEL {level}", 26, OFF_WHITE, sw // 2 - 250, 82, shadow=True)
        bar_x, bar_w, bar_h = sw // 2 - 80, 380, 18
        pygame.draw.rect(self.screen, (20, 10, 5), (bar_x, 88, bar_w, bar_h), border_radius=8)
        fill = max(0, int(bar_w * min(1.0, xp / max(1, xp_next))))
        pygame.draw.rect(self.screen, (0, 180, 220), (bar_x, 88, fill, bar_h), border_radius=8)
        pygame.draw.rect(self.screen, (80, 50, 20), (bar_x, 88, bar_w, bar_h), 2, border_radius=8)
        dt(self.screen, f"{xp}/{xp_next} XP", 14, OFF_WHITE, bar_x + bar_w + 10, 90, shadow=False)

        # Character portrait
        fav_char = self.save.get("favorite_char", "warrior")
        portrait = get_idle_sprite(fav_char, target_w=200)
        portrait_x = sw // 2 - 320
        portrait_y = 140
        if portrait:
            # Dark bg behind portrait
            pw, ph = portrait.get_size()
            pbg = pygame.Surface((pw + 20, ph + 20), pygame.SRCALPHA)
            pbg.fill((0, 0, 0, 120))
            pygame.draw.rect(pbg, GOLD, (0, 0, pw + 20, ph + 20), 2, border_radius=8)
            self.screen.blit(pbg, (portrait_x - 10, portrait_y - 10))
            self.screen.blit(portrait, (portrait_x, portrait_y))

        # Stats panel
        panel_x = sw // 2 - 120
        panel_y = 130
        panel_w = 480
        panel_h = 440
        bg = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        pygame.draw.rect(bg, GOLD, (0, 0, panel_w, panel_h), 2, border_radius=12)
        self.screen.blit(bg, (panel_x, panel_y))

        wins    = self.save.get("wins", 0)
        losses  = self.save.get("losses", 0)
        total   = max(1, wins + losses)
        wr      = int(wins / total * 100)
        coins   = self.save.get("coins", 0)
        combos  = self.save.get("total_combos", 0)
        crits   = self.save.get("total_crits", 0)
        matches = self.save.get("matches_played", 0)
        weapon  = self.save.get("equipped_weapon", "iron_blade").replace("_", " ").title()
        armor   = self.save.get("equipped_armor", "cloth_wrap").replace("_", " ").title()

        stats = [
            ("TOTAL WINS",       str(wins),    (80, 220, 80)),
            ("TOTAL LOSSES",     str(losses),  (220, 80, 80)),
            ("WIN RATE",         f"{wr}%",     (80, 200, 255)),
            ("MATCHES PLAYED",   str(matches), (180, 180, 220)),
            ("CURRENT COINS",    str(coins),   GOLD),
            ("TOTAL COMBOS",     str(combos),  ORANGE),
            ("CRITICAL HITS",    str(crits),   (255, 220, 60)),
            ("EQUIPPED WEAPON",  weapon,       (200, 160, 80)),
            ("EQUIPPED ARMOR",   armor,        (120, 160, 200)),
        ]

        y = panel_y + 20
        col_w = panel_w // 2
        for i, (label, val, col) in enumerate(stats):
            col_x = panel_x + 20 + (i % 2) * col_w
            row_y = y + (i // 2) * 52
            dt(self.screen, label, 16, (140, 130, 110), col_x, row_y, shadow=False)
            dt(self.screen, val, 26, col, col_x, row_y + 18, shadow=True)

        # Hint
        dt(self.screen, "ESC  BACK", 14, (80, 60, 40), sw // 2, sh - 24,
           shadow=False, center=True)

