"""
HUD — Street Fighter / Shadow Fight style HUD with turok.ttf
"""
import pygame
import math
from settings import *
from core.asset_loader import get_font, draw_text as dt


class HUD:
    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h

        # Animated display values
        self._p1_hp_disp   = 1.0
        self._p2_hp_disp   = 1.0
        self._p1_hp_ghost  = 1.0
        self._p2_hp_ghost  = 1.0
        self._p1_st_disp   = 1.0
        self._p2_st_disp   = 1.0
        self._round_flash  = 0.0

    def update(self, dt, p1_hp_r, p2_hp_r, p1_st_r, p2_st_r):
        spd = dt * 6
        self._p1_hp_ghost += (self._p1_hp_disp - self._p1_hp_ghost) * dt * 1.8
        self._p2_hp_ghost += (self._p2_hp_disp - self._p2_hp_ghost) * dt * 1.8
        self._p1_hp_disp  += (p1_hp_r - self._p1_hp_disp)  * spd * 6
        self._p2_hp_disp  += (p2_hp_r - self._p2_hp_disp)  * spd * 6
        self._p1_st_disp  += (p1_st_r - self._p1_st_disp)  * spd * 9
        self._p2_st_disp  += (p2_st_r - self._p2_st_disp)  * spd * 9
        if self._round_flash > 0:
            self._round_flash = max(0.0, self._round_flash - dt * 3)

    def trigger_round_flash(self):
        self._round_flash = 1.0

    # ── Main Draw ──────────────────────────────────────────────────────────────
    def draw(self, surface, p1_name, p2_name,
             p1_hp, p1_max_hp, p2_hp, p2_max_hp,
             p1_stam, p1_max_stam, p2_stam, p2_max_stam,
             time_left, p1_rounds, p2_rounds, max_rounds,
             combo_count=0, p1_coins=0, gamer_id="",
             crit_label="", crit_color=(255, 210, 0)):

        t  = pygame.time.get_ticks() / 1000.0
        sw = self.sw

        # ── Top panel ─────────────────────────────────────────────────────────
        panel_h = 90
        panel = pygame.Surface((sw, panel_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 210))
        pygame.draw.line(panel, (100, 60, 15), (0, panel_h-1), (sw, panel_h-1), 2)
        surface.blit(panel, (0, 0))

        bar_margin = 115
        bar_w      = sw // 2 - bar_margin - 8
        bar_h      = 28
        bar_top    = 8
        stam_h     = 10

        # ── P1 HP bar (left, grows right) ─────────────────────────────────────
        px1 = bar_margin
        self._draw_hp_bar(surface, px1, bar_top, bar_w, bar_h,
                          self._p1_hp_ghost, self._p1_hp_disp, HP_COLOR_P1, False)
        self._draw_stam_bar(surface, px1, bar_top + bar_h + 4, bar_w, stam_h,
                            self._p1_st_disp, False)
        # P1 Name + HP
        dt(surface, p1_name, 22, OFF_WHITE, px1, bar_top + bar_h + 18, shadow=True)
        hp1_s = f"{max(0, int(p1_hp))}"
        dt(surface, hp1_s, 18, (180, 140, 80),
           px1 + bar_w - get_font(18).size(hp1_s)[0], bar_top + bar_h + 19, shadow=False)

        # ── P2 HP bar (right, grows left) ─────────────────────────────────────
        px2 = sw - bar_margin - bar_w
        self._draw_hp_bar(surface, px2, bar_top, bar_w, bar_h,
                          self._p2_hp_ghost, self._p2_hp_disp, HP_COLOR_P2, True)
        self._draw_stam_bar(surface, px2, bar_top + bar_h + 4, bar_w, stam_h,
                            self._p2_st_disp, True)
        # P2 Name + HP (right-aligned)
        n2w = get_font(22).size(p2_name)[0]
        dt(surface, p2_name, 22, OFF_WHITE, px2 + bar_w - n2w, bar_top + bar_h + 18, shadow=True)
        hp2_s = f"{max(0, int(p2_hp))}"
        dt(surface, hp2_s, 18, (180, 140, 80), px2, bar_top + bar_h + 19, shadow=False)

        # ── Timer center ──────────────────────────────────────────────────────
        self._draw_timer(surface, time_left, t)

        # ── Round dots ────────────────────────────────────────────────────────
        self._draw_round_dots(surface, p1_rounds, p2_rounds, max_rounds)

        # ── Coins + GamerID ───────────────────────────────────────────────────
        dt(surface, f"COINS: {p1_coins}", 16, AMBER, bar_margin, 74, shadow=True)
        if gamer_id:
            gid_w = get_font(16).size(gamer_id.upper())[0]
            dt(surface, gamer_id.upper(), 16, (90, 70, 40),
               sw // 2 - gid_w // 2, 74, shadow=False)

        # ── Combo banner ──────────────────────────────────────────────────────
        if combo_count >= 2:
            self._draw_combo(surface, combo_count, t)

        # ── Crit label ────────────────────────────────────────────────────────
        if crit_label:
            self._draw_crit(surface, crit_label, crit_color, t)

        # ── Round flash ───────────────────────────────────────────────────────
        if self._round_flash > 0.01:
            fl = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
            fl.fill((255, 255, 255, int(self._round_flash * 90)))
            surface.blit(fl, (0, 0))

    def _draw_hp_bar(self, surface, x, y, w, h, ghost_r, ratio, color, flipped):
        # BG
        pygame.draw.rect(surface, (18, 6, 6), (x, y, w, h))
        # Ghost (damage trail)
        if ghost_r > ratio + 0.01:
            gw = max(0, int(w * ghost_r))
            ghost_col = (160, 80, 0)
            if not flipped:
                pygame.draw.rect(surface, ghost_col, (x, y, gw, h))
            else:
                pygame.draw.rect(surface, ghost_col, (x + w - gw, y, gw, h))
        # Main fill
        bw = max(0, int(w * ratio))
        if bw > 0:
            fill = self._hp_col(ratio, color)
            if not flipped:
                pygame.draw.rect(surface, fill, (x, y, bw, h))
                # Shine
                shine = pygame.Surface((bw, h // 3), pygame.SRCALPHA)
                shine.fill((255, 255, 255, 28))
                surface.blit(shine, (x, y))
            else:
                pygame.draw.rect(surface, fill, (x + w - bw, y, bw, h))
                shine = pygame.Surface((bw, h // 3), pygame.SRCALPHA)
                shine.fill((255, 255, 255, 28))
                surface.blit(shine, (x + w - bw, y))
        # Border
        pygame.draw.rect(surface, (90, 60, 20), (x, y, w, h), 2)

    def _draw_stam_bar(self, surface, x, y, w, h, ratio, flipped):
        pygame.draw.rect(surface, (6, 22, 12), (x, y, w, h))
        sw2 = max(0, int(w * ratio))
        if sw2 > 0:
            if not flipped:
                pygame.draw.rect(surface, STAMINA_COLOR, (x, y, sw2, h))
            else:
                pygame.draw.rect(surface, STAMINA_COLOR, (x + w - sw2, y, sw2, h))
        pygame.draw.rect(surface, (15, 50, 28), (x, y, w, h), 1)

    def _draw_timer(self, surface, time_left, t):
        cx  = self.sw // 2
        bw  = 84
        bh  = 66
        box = pygame.Surface((bw, bh), pygame.SRCALPHA)
        box.fill((0, 0, 0, 230))
        pygame.draw.rect(box, (90, 55, 15), (0, 0, bw, bh), 2, border_radius=4)
        surface.blit(box, (cx - bw//2, 2))

        secs = max(0, int(time_left))
        urgent = secs <= 10
        col    = CRIMSON if urgent else OFF_WHITE
        size   = 58 if urgent else 56
        pulse  = 1.0 + math.sin(t * 9) * 0.08 if urgent else 1.0

        font = get_font(size)
        ts   = font.render(str(secs), True, col)
        w = int(ts.get_width() * pulse)
        h = int(ts.get_height() * pulse)
        if w > 0 and h > 0:
            scaled = pygame.transform.scale(ts, (w, h))
            # Shadow
            shadow = font.render(str(secs), True, (0, 0, 0))
            surface.blit(shadow, (cx - shadow.get_width()//2 + 2, 6))
            surface.blit(scaled, (cx - w//2, 5))

    def _draw_round_dots(self, surface, p1r, p2r, max_r):
        dot_r = 7
        gap   = 20
        # P1 dots left
        x1_start = 115
        for i in range(max_r):
            col = HP_COLOR_P1 if i < p1r else (30, 12, 12)
            pygame.draw.circle(surface, col, (x1_start + i*gap, 80), dot_r)
            pygame.draw.circle(surface, (90, 60, 20), (x1_start + i*gap, 80), dot_r, 1)
        # P2 dots right
        x2_start = self.sw - 115 - (max_r-1)*gap
        for i in range(max_r):
            col = HP_COLOR_P2 if i < p2r else (12, 12, 30)
            pygame.draw.circle(surface, col, (x2_start + i*gap, 80), dot_r)
            pygame.draw.circle(surface, (90, 60, 20), (x2_start + i*gap, 80), dot_r, 1)

    def _draw_combo(self, surface, count, t):
        sw  = self.sw
        col = (255, min(255, 60 + count * 20), 0)
        size = 40
        pulse = 1.0 + math.sin(t * 8) * 0.07
        font  = get_font(size)
        ts    = font.render(f"{count} HIT", True, col)
        w  = int(ts.get_width() * pulse)
        h  = int(ts.get_height() * pulse)
        if w > 0 and h > 0:
            sc = pygame.transform.scale(ts, (w, h))
            shadow = font.render(f"{count} HIT", True, (0, 0, 0))
            surface.blit(shadow, (sw - shadow.get_width() - 14, 97))
            surface.blit(sc, (sw - w - 12, 95))
        sub = get_font(17).render("COMBO!", True, col)
        surface.blit(sub, (sw - sub.get_width() - 12, 95 + h + 2))

    def _draw_crit(self, surface, label, color, t):
        sw  = self.sw
        pulse = 1.0 + math.sin(t * 7) * 0.09
        font  = get_font(32)
        ts    = font.render(label.upper(), True, color)
        w  = int(ts.get_width() * pulse)
        h  = int(ts.get_height() * pulse)
        if w <= 0 or h <= 0: return
        sc = pygame.transform.scale(ts, (w, h))
        shadow = font.render(label.upper(), True, (0, 0, 0))
        surface.blit(shadow, (sw//2 - shadow.get_width()//2 + 2, 100))
        surface.blit(sc, (sw//2 - w//2, 98))

    @staticmethod
    def _hp_col(ratio, base):
        if ratio > 0.50: return base
        if ratio > 0.25:
            f = (ratio - 0.25) / 0.25
            return (int(220 + (base[0]-220)*f), int(70 * f), int(base[2]*f*0.5))
        return (180, 12, 12)

    # ── Overlays ──────────────────────────────────────────────────────────────
    def draw_ko(self, surface, text="K.O.", t=0.0):
        sw, sh = self.sw, self.sh
        pulse  = 1.0 + math.sin(t * 5) * 0.06
        font   = get_font(92)
        ts     = font.render(text, True, GOLD)
        w = int(ts.get_width() * pulse)
        h = int(ts.get_height() * pulse)
        if w <= 0 or h <= 0: return
        sc = pygame.transform.scale(ts, (w, h))
        shadow = font.render(text, True, (60, 20, 0))
        surface.blit(shadow, (sw//2 - shadow.get_width()//2 + 5, sh//2 - shadow.get_height()//2 + 5))
        surface.blit(sc, (sw//2 - w//2, sh//2 - h//2))

    def draw_round_start(self, surface, round_num, t=0.0):
        sw, sh = self.sw, self.sh
        a = min(255, int(t * 512))
        if a <= 0: return
        rs = get_font(30).render(f"ROUND  {round_num}", True, OFF_WHITE)
        rs.set_alpha(a)
        surface.blit(rs, (sw//2 - rs.get_width()//2, sh//2 - 55))
        if t > 0.4:
            fa = min(255, int((t - 0.4) * 640))
            fs = get_font(95).render("FIGHT!", True, CRIMSON)
            sh2 = get_font(95).render("FIGHT!", True, (0,0,0))
            sh2.set_alpha(fa)
            fs.set_alpha(fa)
            surface.blit(sh2, (sw//2 - sh2.get_width()//2 + 4, sh//2 - sh2.get_height()//2 + 4))
            surface.blit(fs, (sw//2 - fs.get_width()//2, sh//2 - fs.get_height()//2))
