"""
Dojo Screen — Training hub, character info, stat upgrades (Shadow Fight 2 style)
"""
import pygame
import math
from settings import *
from characters.character_data import CHARACTERS, CLASS_ORDER, CLASS_COLORS


class DojoScreen:
    def __init__(self, screen, audio, save_manager):
        self.screen = screen
        self.audio  = audio
        self.save   = save_manager
        self.sw     = screen.get_width()
        self.sh     = screen.get_height()
        self._t     = 0.0
        self._action = None
        self._tab   = 0   # 0=Info, 1=Train, 2=Roster
        self._tabs  = ["FIGHTER INFO", "TRAINING", "FULL ROSTER"]
        self._dummy_angle = 0.0
        self._dummy_hit_flash = 0.0
        self._punch_timer = 0.0
        self._selected_char = 0

        try:
            self.font_title = pygame.font.SysFont("impact", 50, bold=True)
            self.font_mid   = pygame.font.SysFont("impact", 28, bold=True)
            self.font_small = pygame.font.SysFont("impact", 20, bold=True)
            self.font_tiny  = pygame.font.SysFont("impact", 15, bold=True)
        except Exception:
            self.font_title = pygame.font.Font(None, 50)
            self.font_mid   = pygame.font.Font(None, 28)
            self.font_small = pygame.font.Font(None, 20)
            self.font_tiny  = pygame.font.Font(None, 15)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._action = "back"
            elif event.key == pygame.K_TAB:
                self._tab = (self._tab + 1) % len(self._tabs)
                self.audio.play_sfx("select")
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                if self._tab == 2:
                    self._selected_char = max(0, self._selected_char - 1)
                    self.audio.play_sfx("select")
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                if self._tab == 2:
                    self._selected_char = min(len(CHARACTERS) - 1, self._selected_char + 1)
                    self.audio.play_sfx("select")
            elif event.key == pygame.K_SPACE:
                if self._tab == 1:
                    self._punch_timer = 0.3
                    self._dummy_hit_flash = 0.4
                    self.audio.play_sfx("punch")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i, tab in enumerate(self._tabs):
                r = self._tab_rect(i)
                if r.collidepoint(mx, my):
                    self._tab = i
                    self.audio.play_sfx("select")
            # Back button
            back_r = pygame.Rect(10, 10, 100, 40)
            if back_r.collidepoint(mx, my):
                self._action = "back"

    def _tab_rect(self, i):
        total_w = len(self._tabs) * 220
        start_x = self.sw // 2 - total_w // 2
        return pygame.Rect(start_x + i * 220 + 5, 70, 210, 40)

    def update(self, dt):
        self._t += dt
        self._dummy_angle += dt * 1.5
        if self._dummy_hit_flash > 0:
            self._dummy_hit_flash -= dt
        if self._punch_timer > 0:
            self._punch_timer -= dt
        result = self._action
        self._action = None
        return result

    def draw(self):
        t = self._t
        sw, sh = self.sw, self.sh

        # Background
        for y in range(sh):
            ratio = y / sh
            pygame.draw.line(self.screen, (int(8+ratio*10), int(5+ratio*5), int(15+ratio*20)), (0,y),(sw,y))

        # Wooden dojo floor
        pygame.draw.rect(self.screen, (55, 32, 12), (0, sh-120, sw, 120))
        for x in range(0, sw, 100):
            pygame.draw.line(self.screen, (40, 22, 8), (x, sh-120), (x, sh), 2)
        pygame.draw.line(self.screen, (80, 50, 20), (0, sh-120), (sw, sh-120), 3)

        # Back button
        back_r = pygame.Rect(10, 10, 100, 40)
        pygame.draw.rect(self.screen, (40, 20, 80), back_r, border_radius=8)
        pygame.draw.rect(self.screen, PANEL_EDGE, back_r, 2, border_radius=8)
        b_txt = self.font_small.render("◄ BACK", True, WHITE)
        self.screen.blit(b_txt, (back_r.x + back_r.w//2 - b_txt.get_width()//2,
                                  back_r.y + back_r.h//2 - b_txt.get_height()//2))

        # Title
        title = self.font_title.render("DOJO", True, (255, 180, 0))
        self.screen.blit(title, (sw//2 - title.get_width()//2, 10))

        # Player info
        gamer_id = self.save.get("gamer_id", "Shadow Warrior")
        level    = self.save.get("level", 1)
        coins    = self.save.get("coins", 0)
        xp       = self.save.get("xp", 0)
        xp_next  = self.save.get("xp_to_next", 100)
        info_txt = self.font_tiny.render(
            f"🎮 {gamer_id}   Lv.{level}   💰 {coins}   XP: {xp}/{xp_next}", True, (180, 180, 220))
        self.screen.blit(info_txt, (sw//2 - info_txt.get_width()//2, 55))

        # Tabs
        for i, tab in enumerate(self._tabs):
            r = self._tab_rect(i)
            is_active = (i == self._tab)
            bg_s = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            if is_active:
                pygame.draw.rect(bg_s, (140, 80, 0, 200), (0,0,r.w,r.h), border_radius=8)
                pygame.draw.rect(bg_s, (255, 180, 0), (0,0,r.w,r.h), 2, border_radius=8)
            else:
                pygame.draw.rect(bg_s, (30, 20, 5, 140), (0,0,r.w,r.h), border_radius=6)
                pygame.draw.rect(bg_s, PANEL_EDGE, (0,0,r.w,r.h), 1, border_radius=6)
            self.screen.blit(bg_s, (r.x, r.y))
            t_s = self.font_tiny.render(tab, True, WHITE if is_active else (140,140,140))
            self.screen.blit(t_s, (r.x + r.w//2 - t_s.get_width()//2, r.y + r.h//2 - t_s.get_height()//2))

        if self._tab == 0:
            self._draw_fighter_info(t)
        elif self._tab == 1:
            self._draw_training(t)
        elif self._tab == 2:
            self._draw_roster(t)

    def _draw_fighter_info(self, t):
        sw, sh = self.sw, self.sh
        equipped_weapon = self.save.get("equipped_weapon", "iron_blade")
        equipped_armor  = self.save.get("equipped_armor",  "cloth_wrap")
        level           = self.save.get("level", 1)
        wins            = self.save.get("wins", 0)
        losses          = self.save.get("losses", 0)
        combos          = self.save.get("total_combos", 0)
        crits           = self.save.get("total_crits", 0)
        fav_char_id     = self.save.get("favorite_char", "general")

        from characters.character_data import get_character
        char = get_character(fav_char_id)
        aura = char.get("aura_color", (150, 100, 200))

        panel_x = sw // 2 - 300
        panel_y = 130
        panel_w = 600
        panel_h = 420
        bg = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        bg.fill((0,0,0,160))
        pygame.draw.rect(bg, PANEL_EDGE, (0,0,panel_w,panel_h), 2, border_radius=14)
        self.screen.blit(bg, (panel_x, panel_y))

        # Fighter display (mini silhouette)
        fighter_cx = panel_x + 130
        fighter_cy = panel_y + 200
        self._draw_mini_fighter_dojo(fighter_cx, fighter_cy, aura, t)

        # Stats on right side
        rx = panel_x + 230
        ry = panel_y + 20
        char_name = self.font_mid.render(char["name"], True, WHITE)
        self.screen.blit(char_name, (rx, ry))
        ry += 35

        cls_col = CLASS_COLORS.get(char["class"], WHITE)
        cls_txt = self.font_small.render(f"Class: {char['class']}", True, cls_col)
        self.screen.blit(cls_txt, (rx, ry))
        ry += 28

        trait_col = CRIT_COLORS.get(char.get("critical_trait"), WHITE)
        trait_txt = self.font_small.render(f"Trait: {char.get('critical_trait','')}", True, trait_col)
        self.screen.blit(trait_txt, (rx, ry))
        ry += 38

        info_rows = [
            (f"Level", str(level), (100, 200, 255)),
            (f"Wins", str(wins), (80, 220, 80)),
            (f"Losses", str(losses), (220, 80, 80)),
            (f"Total Combos", str(combos), ORANGE),
            (f"Critical Hits", str(crits), YELLOW),
            (f"Equipped Weapon", equipped_weapon.replace("_"," ").title(), (200, 160, 80)),
            (f"Equipped Armor",  equipped_armor.replace("_"," ").title(),  (120, 160, 200)),
        ]
        for label, val, col in info_rows:
            l_s = self.font_tiny.render(label + ":", True, (140,140,160))
            v_s = self.font_tiny.render(val, True, col)
            self.screen.blit(l_s, (rx, ry))
            self.screen.blit(v_s, (rx + 200, ry))
            ry += 26

    def _draw_mini_fighter_dojo(self, cx, cy, aura_col, t):
        col = (15, 15, 25)
        bob = int(math.sin(t * 2) * 4)
        # Glow
        glow = pygame.Surface((120, 200), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (*aura_col, 40), (0, 0, 120, 200))
        self.screen.blit(glow, (cx-60, cy-140+bob), special_flags=pygame.BLEND_RGBA_ADD)
        # Body
        pygame.draw.ellipse(self.screen, col, (cx-28, cy-95+bob, 56, 70))
        pygame.draw.circle(self.screen, col, (cx, cy-110+bob), 22)
        pygame.draw.circle(self.screen, aura_col, (cx+8, cy-113+bob), 5)
        pygame.draw.circle(self.screen, WHITE,    (cx+8, cy-113+bob), 2)
        pygame.draw.line(self.screen, col, (cx-8, cy-28+bob),  (cx-16, cy+14+bob), 8)
        pygame.draw.line(self.screen, col, (cx+8, cy-28+bob),  (cx+16, cy+14+bob), 8)
        pygame.draw.line(self.screen, col, (cx+24, cy-58+bob), (cx+46, cy-30+bob), 7)
        pygame.draw.line(self.screen, col, (cx-24, cy-58+bob), (cx-40, cy-38+bob), 6)

    def _draw_training(self, t):
        sw, sh = self.sw, self.sh
        # Training dummy
        dummy_x = sw // 2
        dummy_y = sh - 170
        hit_col = (200, 50, 50) if self._dummy_hit_flash > 0 else (120, 80, 40)
        pygame.draw.circle(self.screen, hit_col, (dummy_x, dummy_y - 55), 25)
        pygame.draw.rect(self.screen, hit_col, (dummy_x - 18, dummy_y - 35, 36, 65))
        pygame.draw.line(self.screen, hit_col, (dummy_x, dummy_y - 10), (dummy_x - 35, dummy_y + 5), 10)
        pygame.draw.line(self.screen, hit_col, (dummy_x, dummy_y - 10), (dummy_x + 35, dummy_y + 5), 10)
        pygame.draw.line(self.screen, (80, 50, 20), (dummy_x, dummy_y + 30), (dummy_x - 12, dummy_y + 70), 9)
        pygame.draw.line(self.screen, (80, 50, 20), (dummy_x, dummy_y + 30), (dummy_x + 12, dummy_y + 70), 9)
        # Base pole
        pygame.draw.rect(self.screen, (60, 40, 15), (dummy_x - 8, dummy_y + 68, 16, 30))
        pygame.draw.rect(self.screen, (40, 28, 10), (dummy_x - 30, dummy_y + 92, 60, 10))

        # Move list
        mx = sw // 2 - 420
        my = 130
        guide_bg = pygame.Surface((400, 350), pygame.SRCALPHA)
        guide_bg.fill((0,0,0,160))
        pygame.draw.rect(guide_bg, PANEL_EDGE, (0,0,400,350), 2, border_radius=10)
        self.screen.blit(guide_bg, (mx, my))

        title_s = self.font_small.render("MOVE LIST (Player 1)", True, YELLOW)
        self.screen.blit(title_s, (mx+10, my+10))
        moves = [
            ("A / D",        "Move Left / Right"),
            ("W",            "Jump"),
            ("J",            "Light Attack"),
            ("K",            "Heavy Attack"),
            ("L",            "Special Attack"),
            ("U",            "Super Move"),
            (";",            "Block (Hold)"),
            ("J + in air",   "Air Attack"),
        ]
        y = my + 40
        for key, action in moves:
            k_s = self.font_tiny.render(key, True, CYAN)
            a_s = self.font_tiny.render(action, True, WHITE)
            self.screen.blit(k_s, (mx+15, y))
            self.screen.blit(a_s, (mx+150, y))
            y += 26

        hint = self.font_small.render("Press SPACE to hit the dummy!", True, (200, 200, 80))
        self.screen.blit(hint, (sw//2 - hint.get_width()//2, sh - 140))

        # P2 move list
        mx2 = sw // 2 + 20
        guide_bg2 = pygame.Surface((400, 350), pygame.SRCALPHA)
        guide_bg2.fill((0,0,0,160))
        pygame.draw.rect(guide_bg2, PANEL_EDGE, (0,0,400,350), 2, border_radius=10)
        self.screen.blit(guide_bg2, (mx2, my))
        title_s2 = self.font_small.render("MOVE LIST (Player 2)", True, HP_COLOR_P2)
        self.screen.blit(title_s2, (mx2+10, my+10))
        moves2 = [
            ("← →",         "Move Left / Right"),
            ("↑",            "Jump"),
            ("Num 1",        "Light Attack"),
            ("Num 2",        "Heavy Attack"),
            ("Num 3",        "Special Attack"),
            ("Num +",        "Super Move"),
            ("Num 0",        "Block (Hold)"),
            ("Num 1 + air",  "Air Attack"),
        ]
        y = my + 40
        for key, action in moves2:
            k_s = self.font_tiny.render(key, True, CYAN)
            a_s = self.font_tiny.render(action, True, WHITE)
            self.screen.blit(k_s, (mx2+15, y))
            self.screen.blit(a_s, (mx2+150, y))
            y += 26

    def _draw_roster(self, t):
        sw, sh = self.sw, self.sh
        level = self.save.get("level", 1)

        card_w, card_h = 100, 140
        cols = 5
        rows = 2
        gap  = 20
        total_w = cols * (card_w + gap) - gap
        start_x = sw // 2 - total_w // 2
        start_y = 130

        for i, char in enumerate(CHARACTERS):
            row = i // cols
            col = i % cols
            x = start_x + col * (card_w + gap)
            y = start_y + row * (card_h + gap)
            is_sel  = (i == self._selected_char)
            locked  = char.get("unlock_level", 1) > level
            aura    = char.get("aura_color", (100,100,200))
            cls_col = CLASS_COLORS.get(char["class"], WHITE)
            pulse   = int(math.sin(t * 4) * 4) if is_sel else 0

            bg_s = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            if is_sel:
                pygame.draw.rect(bg_s, (*aura, 100), (0,0,card_w,card_h), border_radius=10)
                pygame.draw.rect(bg_s, aura, (0,0,card_w,card_h), 2, border_radius=10)
            else:
                pygame.draw.rect(bg_s, (20,15,35,160), (0,0,card_w,card_h), border_radius=8)
                pygame.draw.rect(bg_s, PANEL_EDGE, (0,0,card_w,card_h), 1, border_radius=8)
            self.screen.blit(bg_s, (x, y + pulse))

            # Mini fighter
            self._draw_mini_fighter_dojo(x + card_w//2, y + card_h//2 + 10 + pulse,
                                          aura if not locked else (40,40,60), t)

            name_s = self.font_tiny.render(char["name"].replace("The ",""), True,
                                           WHITE if not locked else (60,60,60))
            self.screen.blit(name_s, (x + card_w//2 - name_s.get_width()//2,
                                       y + card_h - 28 + pulse))

            if locked:
                lock_s = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                lock_s.fill((0,0,0,130))
                self.screen.blit(lock_s, (x, y + pulse))
                lv_s = self.font_tiny.render(f"Lv{char['unlock_level']}", True, (200,150,50))
                self.screen.blit(lv_s, (x + card_w//2 - lv_s.get_width()//2, y + 55 + pulse))

        # Selected char info
        if 0 <= self._selected_char < len(CHARACTERS):
            char = CHARACTERS[self._selected_char]
            info_y = start_y + rows * (card_h + gap) + 10
            info_s = self.font_small.render(
                f"{char['name']}   |   {char['class']}   |   {char.get('critical_trait','')}",
                True, WHITE)
            self.screen.blit(info_s, (sw//2 - info_s.get_width()//2, info_y))
            lore_s = self.font_tiny.render(char.get("lore","")[:80] + "...", True, (140,140,160))
            self.screen.blit(lore_s, (sw//2 - lore_s.get_width()//2, info_y + 28))

        hint = self.font_tiny.render("← → Navigate Roster   TAB Switch Tabs   ESC Back", True, (80,80,120))
        self.screen.blit(hint, (sw//2 - hint.get_width()//2, sh - 30))
