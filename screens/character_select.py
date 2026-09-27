"""
Character Select Screen — Retro fighting game style with real sprite previews
Uses turok.ttf via asset_loader.get_font() / draw_text()
"""
import pygame
import math
from settings import *
from characters.character_data import CHARACTERS, CLASS_ORDER, get_characters_by_class
from core.asset_loader import load_character_sprite, load_background, get_font, draw_text as dt, get_idle_sprite


class CharacterSelectScreen:
    def __init__(self, screen, audio, save_manager):
        self.screen = screen
        self.audio  = audio
        self.save   = save_manager
        self.sw     = screen.get_width()
        self.sh     = screen.get_height()
        self._t     = 0.0

        self._phase         = "mode_pick"
        self._game_mode     = None
        self._ai_difficulty = AI_BALANCED
        self._p1_char       = None
        self._p2_char       = None
        self._cursor        = 0
        self._class_i       = 0
        self._action        = None

        # Preload all sprites
        for c in CHARACTERS:
            load_character_sprite(c["sprite_id"])

        self._bg = load_background("dojo", self.sw, self.sh)
        self._class_chars = {cls: get_characters_by_class(cls) for cls in CLASS_ORDER}

    # ── Font helpers (turok.ttf) ───────────────────────────────────────────────
    def _f(self, size):
        return get_font(size)

    def _t_render(self, text, size, col):
        return get_font(size).render(text, True, col)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _current_chars(self):
        return self._class_chars[CLASS_ORDER[self._class_i]]

    def _current_char(self):
        chars = self._current_chars()
        return chars[self._cursor % len(chars)] if chars else None

    def _tab_rect(self, i):
        tab_w = self.sw // len(CLASS_ORDER)
        return pygame.Rect(i * tab_w + 4, 65, tab_w - 8, 38)

    def _card_rect(self, j, total):
        card_w = 160
        gap    = 18
        total_w = total * (card_w + gap) - gap
        sx = min(self.sw // 2 - total_w // 2, self.sw - 290 - total_w)
        return pygame.Rect(sx + j * (card_w + gap), 118, card_w, 248)

    # ── Events ────────────────────────────────────────────────────────────────
    def handle_event(self, event):
        if self._phase == "mode_pick":
            self._handle_mode_pick(event)
        elif self._phase in ("p1_pick", "p2_pick"):
            self._handle_char_pick(event)
        elif self._phase == "ai_diff":
            self._handle_ai_diff(event)

    def _handle_mode_pick(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_KP1):
                self._game_mode = "1p"; self._phase = "p1_pick"; self.audio.play_sfx("confirm")
            elif event.key in (pygame.K_2, pygame.K_KP2):
                self._game_mode = "2p"; self._phase = "p1_pick"; self.audio.play_sfx("confirm")
            elif event.key == pygame.K_ESCAPE:
                self._action = "back"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            r1 = pygame.Rect(self.sw//2 - 290, self.sh//2 - 90, 260, 90)
            r2 = pygame.Rect(self.sw//2 +  30, self.sh//2 - 90, 260, 90)
            if r1.collidepoint(event.pos):
                self._game_mode = "1p"; self._phase = "p1_pick"; self.audio.play_sfx("confirm")
            elif r2.collidepoint(event.pos):
                self._game_mode = "2p"; self._phase = "p1_pick"; self.audio.play_sfx("confirm")
            if pygame.Rect(10, 10, 90, 36).collidepoint(event.pos):
                self._action = "back"

    def _handle_char_pick(self, event):
        chars = self._current_chars()
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self._cursor = max(0, self._cursor - 1); self.audio.play_sfx("select")
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._cursor = min(len(chars)-1, self._cursor+1); self.audio.play_sfx("select")
            elif event.key in (pygame.K_TAB, pygame.K_q):
                self._class_i = (self._class_i + 1) % len(CLASS_ORDER)
                self._cursor = 0; self.audio.play_sfx("select")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._confirm_char(self._current_char())
            elif event.key == pygame.K_ESCAPE:
                if self._phase == "p2_pick":
                    self._phase = "p1_pick"; self._p1_char = None; self._cursor = 0
                else:
                    self._phase = "mode_pick"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i in range(len(CLASS_ORDER)):
                if self._tab_rect(i).collidepoint(event.pos):
                    self._class_i = i; self._cursor = 0; self.audio.play_sfx("select")
            for j, c in enumerate(chars):
                if self._card_rect(j, len(chars)).collidepoint(event.pos):
                    self._cursor = j; self._confirm_char(c)
            if pygame.Rect(10, 10, 90, 36).collidepoint(event.pos):
                self._phase = "mode_pick"

    def _handle_ai_diff(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self._ai_difficulty = max(0, self._ai_difficulty - 1); self.audio.play_sfx("select")
            elif event.key == pygame.K_RIGHT:
                self._ai_difficulty = min(4, self._ai_difficulty + 1); self.audio.play_sfx("select")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.audio.play_sfx("confirm")
                self._action = ("start_fight", self._p1_char, self._p2_char,
                                self._game_mode, self._ai_difficulty)
            elif event.key == pygame.K_ESCAPE:
                self._phase = "p1_pick"; self._p2_char = None

    def _confirm_char(self, char):
        if not char: return
        level = self.save.get("level", 1)
        if char.get("unlock_level", 1) > level:
            return  # locked
        if self._phase == "p1_pick":
            self._p1_char = char
            self.audio.play_sfx("confirm")
            if self._game_mode == "2p":
                self._phase = "p2_pick"; self._cursor = 0; self._class_i = 0
            else:
                self._p2_char = None; self._phase = "ai_diff"
        elif self._phase == "p2_pick":
            self._p2_char = char
            self.audio.play_sfx("confirm")
            self._action = ("start_fight", self._p1_char, self._p2_char,
                            self._game_mode, self._ai_difficulty)

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self, dt_val):
        self._t += dt_val
        result = self._action
        self._action = None
        return result

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self):
        if self._bg:
            self.screen.blit(self._bg, (0, 0))
        else:
            self.screen.fill(DARK_BG)
        ov = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 115))
        self.screen.blit(ov, (0, 0))

        if self._phase == "mode_pick":
            self._draw_mode_pick()
        elif self._phase in ("p1_pick", "p2_pick"):
            self._draw_char_pick()
        elif self._phase == "ai_diff":
            self._draw_ai_diff()

    def _draw_back_btn(self):
        r = pygame.Rect(10, 10, 90, 36)
        pygame.draw.rect(self.screen, (60, 20, 20), r, border_radius=4)
        pygame.draw.rect(self.screen, (100, 60, 30), r, 1, border_radius=4)
        dt(self.screen, "< BACK", 16, OFF_WHITE,
           r.x + r.w//2, r.y + r.h//2 - 8, shadow=True, center=True)

    def _draw_mode_pick(self):
        sw, sh = self.sw, self.sh
        t = self._t
        self._draw_back_btn()
        dt(self.screen, "SELECT MODE", 48, GOLD, sw//2, sh//2 - 200, shadow=True, center=True)
        pygame.draw.line(self.screen, DARK_GOLD, (sw//2 - 280, sh//2 - 148),
                         (sw//2 + 280, sh//2 - 148), 2)

        modes = [
            ("1 PLAYER",  "VS  COMPUTER",  HP_COLOR_P1, pygame.Rect(sw//2-290, sh//2-90, 260, 90)),
            ("2 PLAYERS", "LOCAL  VERSUS", HP_COLOR_P2, pygame.Rect(sw//2+30,  sh//2-90, 260, 90)),
        ]
        for label, sub, col, rect in modes:
            pulse = int(math.sin(t * 2.5) * 3)
            bg = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            pygame.draw.rect(bg, (*col, 55), (0, 0, rect.w, rect.h), border_radius=6)
            pygame.draw.rect(bg, col, (0, 0, rect.w, rect.h), 2, border_radius=6)
            self.screen.blit(bg, (rect.x, rect.y + pulse))
            dt(self.screen, label, 28, WHITE, rect.x + rect.w//2, rect.y + 18 + pulse,
               shadow=True, center=True)
            dt(self.screen, sub, 15, (180, 170, 150), rect.x + rect.w//2, rect.y + 55 + pulse,
               shadow=False, center=True)

        dt(self.screen, "Press 1 or 2  -  or click a mode", 15, (90, 70, 45),
           sw//2, sh - 40, shadow=False, center=True)

    def _draw_char_pick(self):
        sw, sh = self.sw, self.sh
        t = self._t
        self._draw_back_btn()

        # Header bar
        bar = pygame.Surface((sw, 62), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 175))
        self.screen.blit(bar, (0, 0))
        header_txt = "PLAYER 1  -  SELECT FIGHTER" if self._phase == "p1_pick" else "PLAYER 2  -  SELECT FIGHTER"
        header_col = HP_COLOR_P1 if self._phase == "p1_pick" else HP_COLOR_P2
        dt(self.screen, header_txt, 26, header_col, sw//2, 15, shadow=True, center=True)

        # Class tabs
        for i, cls in enumerate(CLASS_ORDER):
            r = self._tab_rect(i)
            active  = (i == self._class_i)
            cls_col = CLASS_COLORS[cls]
            bg = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            if active:
                pygame.draw.rect(bg, (*cls_col, 210), (0, 0, r.w, r.h))
                pygame.draw.rect(bg, GOLD, (0, 0, r.w, r.h), 2)
            else:
                pygame.draw.rect(bg, (18, 12, 12, 185), (0, 0, r.w, r.h))
                pygame.draw.rect(bg, (65, 42, 18), (0, 0, r.w, r.h), 1)
            self.screen.blit(bg, (r.x, r.y))
            icon = CLASS_ICONS.get(cls, "")
            tab_col = WHITE if active else (120, 100, 75)
            dt(self.screen, f"{icon} {cls.upper()}", 14, tab_col,
               r.x + r.w//2, r.y + r.h//2 - 7, shadow=True, center=True)

        # Character cards
        chars  = self._current_chars()
        level  = self.save.get("level", 1)

        for j, char in enumerate(chars):
            rect    = self._card_rect(j, len(chars))
            is_sel  = (j == self._cursor)
            locked  = char.get("unlock_level", 1) > level
            aura    = char.get("aura_color", (100, 80, 60))
            pulse_y = int(math.sin(t * 4) * 5) if is_sel else 0

            # Card BG
            card_bg = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            if is_sel:
                pygame.draw.rect(card_bg, (40, 20, 8, 225), (0, 0, rect.w, rect.h), border_radius=6)
                pygame.draw.rect(card_bg, aura, (0, 0, rect.w, rect.h), 2, border_radius=6)
                glow = pygame.Surface((rect.w + 24, rect.h + 24), pygame.SRCALPHA)
                pygame.draw.rect(glow, (*aura, 38), (0, 0, glow.get_width(), glow.get_height()), border_radius=8)
                self.screen.blit(glow, (rect.x-12, rect.y+pulse_y-12), special_flags=pygame.BLEND_RGBA_ADD)
            else:
                pygame.draw.rect(card_bg, (18, 10, 6, 205), (0, 0, rect.w, rect.h), border_radius=6)
                pygame.draw.rect(card_bg, (62, 42, 18), (0, 0, rect.w, rect.h), 1, border_radius=6)
            self.screen.blit(card_bg, (rect.x, rect.y + pulse_y))

            # Sprite — get_idle_sprite returns a single cropped idle frame
            base_surf = get_idle_sprite(char["sprite_id"], target_w=155)
            if base_surf:
                sw_s, sh_s = base_surf.get_size()
                max_w = rect.w - 12
                if sw_s > max_w:
                    ratio = max_w / sw_s
                    disp_w = max_w
                    disp_h = max(1, int(sh_s * ratio))
                    base_surf = pygame.transform.scale(base_surf, (disp_w, disp_h))
                else:
                    disp_w, disp_h = sw_s, sh_s
                sx = rect.x + rect.w // 2 - disp_w // 2
                sy = rect.y + 6 + pulse_y

                # Shadow bg behind sprite
                spr_bg = pygame.Surface((disp_w + 8, disp_h + 6), pygame.SRCALPHA)
                spr_bg.fill((0, 0, 0, 90))
                self.screen.blit(spr_bg, (sx - 4, sy - 3))

                if locked:
                    locked_s = base_surf.copy()
                    locked_s.set_alpha(60)
                    self.screen.blit(locked_s, (sx, sy))
                else:
                    self.screen.blit(base_surf, (sx, sy))
            else:
                placeholder = pygame.Surface((rect.w - 10, 155), pygame.SRCALPHA)
                placeholder.fill((*aura, 55) if not locked else (18, 14, 12, 80))
                self.screen.blit(placeholder, (rect.x + 5, rect.y + 5 + pulse_y))

            # Lock overlay
            if locked:
                lk = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                lk.fill((0, 0, 0, 125))
                self.screen.blit(lk, (rect.x, rect.y + pulse_y))
                dt(self.screen, f"LV {char['unlock_level']}", 20, AMBER,
                   rect.x + rect.w//2, rect.y + 88 + pulse_y, shadow=True, center=True)

            # Name + class
            name_col = GOLD if is_sel else (OFF_WHITE if not locked else (55, 48, 38))
            dt(self.screen, char["name"], 16, name_col,
               rect.x + rect.w//2, rect.y + rect.h - 44 + pulse_y, shadow=True, center=True)
            cls_c = CLASS_COLORS.get(char["class"], (100, 80, 60)) if not locked else (48, 42, 38)
            dt(self.screen, char["class"].upper(), 12, cls_c,
               rect.x + rect.w//2, rect.y + rect.h - 26 + pulse_y, shadow=False, center=True)

        # Stats panel on right
        sel = self._current_char()
        if sel:
            self._draw_stats_panel(sel, t)

        # Bottom bar
        bot_bar = pygame.Surface((sw, 42), pygame.SRCALPHA)
        bot_bar.fill((0, 0, 0, 170))
        self.screen.blit(bot_bar, (0, sh - 42))
        if self._p1_char:
            dt(self.screen, f"P1: {self._p1_char['name']}", 18, HP_COLOR_P1, 20, sh - 32, shadow=True)
        if self._p2_char:
            p2_label = f"P2: {self._p2_char['name']}"
            p2_w = get_font(18).size(p2_label)[0]
            dt(self.screen, p2_label, 18, HP_COLOR_P2, sw - p2_w - 20, sh - 32, shadow=True)
        dt(self.screen, "< >  SELECT    TAB  CLASS    ENTER  CONFIRM    ESC  BACK",
           14, (80, 62, 42), sw//2, sh - 26, shadow=False, center=True)

    def _draw_stats_panel(self, char, t):
        sw, sh = self.sw, self.sh
        px = sw - 270
        py = 118
        pw = 258
        ph = sh - 165

        bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 185))
        pygame.draw.rect(bg, (80, 50, 18), (0, 0, pw, ph), 2, border_radius=6)
        self.screen.blit(bg, (px, py))

        y = py + 12
        dt(self.screen, char["name"], 26, GOLD, px + pw//2, y, shadow=True, center=True)
        y += 36
        dt(self.screen, char["class"].upper(), 14,
           CLASS_COLORS.get(char["class"], WHITE), px + 10, y, shadow=False)
        trait_col = CRIT_COLORS.get(char.get("critical_trait",""), AMBER)
        dt(self.screen, f"  TRAIT: {char.get('critical_trait','')}", 13, trait_col,
           px + pw//2, y, shadow=False, center=True)
        y += 24
        pygame.draw.line(self.screen, (80, 50, 18), (px+8, y), (px+pw-8, y), 1)
        y += 10

        # Lore wrap
        font_lore = get_font(13)
        lore  = char.get("lore", "")
        words = lore.split()
        line  = ""
        for word in words:
            test = line + word + " "
            if font_lore.size(test)[0] > pw - 22:
                lsurf = font_lore.render(line.strip(), True, (145, 125, 95))
                self.screen.blit(lsurf, (px + 10, y))
                y += 16
                line = word + " "
            else:
                line = test
        if line.strip():
            self.screen.blit(font_lore.render(line.strip(), True, (145, 125, 95)), (px+10, y))
        y += 28
        pygame.draw.line(self.screen, (80, 50, 18), (px+8, y), (px+pw-8, y), 1)
        y += 10

        # Stat bars
        stats = char["stats"]
        bars = [
            ("HP",      stats["hp"],      200, HP_COLOR_P1),
            ("STAMINA", stats["stamina"], 200, STAMINA_COLOR),
            ("SPEED",   stats["speed"],    10, AMBER),
            ("DAMAGE",  stats["damage"],   26, CRIMSON),
            ("DEFENSE", stats["defense"],  22, STEEL_BLUE),
        ]
        for lbl, val, mx, col in bars:
            dt(self.screen, lbl, 13, (155, 135, 95), px + 10, y, shadow=False)
            bx = px + 82
            bw = pw - 98
            bh = 9
            pygame.draw.rect(self.screen, (22, 12, 8), (bx, y+2, bw, bh), border_radius=3)
            fw = max(1, int(bw * min(1.0, val / mx)))
            pygame.draw.rect(self.screen, col, (bx, y+2, fw, bh), border_radius=3)
            pygame.draw.rect(self.screen, (60, 40, 18), (bx, y+2, bw, bh), 1, border_radius=3)
            dt(self.screen, str(val), 13, OFF_WHITE, bx + bw + 4, y, shadow=False)
            y += 24

        # Move count indicator
        move_count = len(char.get("moves", {}))
        dt(self.screen, f"MOVES: {move_count}", 14, (120, 100, 70),
           px + pw//2, y + 4, shadow=False, center=True)

    def _draw_ai_diff(self):
        sw, sh = self.sw, self.sh
        t = self._t
        self._draw_back_btn()

        dt(self.screen, "SELECT DIFFICULTY", 48, GOLD, sw//2, 100, shadow=True, center=True)
        if self._p1_char:
            dt(self.screen, f"Your Fighter:  {self._p1_char['name']}", 26,
               HP_COLOR_P1, sw//2, 168, shadow=True, center=True)

        diff_cols = [(80,180,80),(80,180,180),(180,180,60),(220,120,30),(220,30,30)]
        names = list(AI_NAMES.values())
        descs = ["Easy - learns nothing", "Cautious - blocks often",
                 "Balanced - fights smart", "Relentless - rarely backs off",
                 "Godlike - reads everything"]

        for i, name in enumerate(names):
            is_sel = (i == self._ai_difficulty)
            rx = sw//2 - 240
            ry = 222 + i * 72
            rw, rh = 480, 62
            pulse = int(math.sin(t * 5) * 3) if is_sel else 0
            col = diff_cols[i]
            bg = pygame.Surface((rw, rh), pygame.SRCALPHA)
            if is_sel:
                pygame.draw.rect(bg, (*col, 78), (0, 0, rw, rh), border_radius=6)
                pygame.draw.rect(bg, col, (0, 0, rw, rh), 2, border_radius=6)
            else:
                pygame.draw.rect(bg, (18, 10, 6, 182), (0, 0, rw, rh), border_radius=6)
                pygame.draw.rect(bg, (62, 40, 18), (0, 0, rw, rh), 1, border_radius=6)
            self.screen.blit(bg, (rx, ry + pulse))
            name_col = WHITE if is_sel else (138, 118, 88)
            dt(self.screen, name, 26, name_col, rx + 20, ry + 10 + pulse, shadow=True)
            desc_col = (175, 155, 115) if is_sel else (78, 62, 42)
            dt(self.screen, descs[i], 14, desc_col, rx + 20, ry + 40 + pulse, shadow=False)
            if is_sel:
                dt(self.screen, "<", 26, col, rx + rw - 32, ry + 16 + pulse, shadow=True)

        dt(self.screen, "< >  CHANGE    ENTER  FIGHT    ESC  BACK",
           15, (80, 62, 42), sw//2, sh - 30, shadow=False, center=True)

