import pygame
import math
from settings import *
from core.asset_loader import get_font, draw_text as dt, load_background

class SettingsScreen:
    def __init__(self, screen, audio, save_manager):
        self.screen = screen
        self.audio  = audio
        self.save   = save_manager
        self.sw     = screen.get_width()
        self.sh     = screen.get_height()
        self._t     = 0.0
        self._action = None
        self._tab    = 0   # 0=Profile, 1=P1 Controls, 2=P2 Controls, 3=Audio

        self._gamer_id_editing = False
        self._gamer_id_text    = self.save.get("gamer_id", "Shadow Warrior")
        self._rebinding        = None
        self._rebind_timer     = 0.0

        self._p1_keys = dict(self.save.get_controls(1))
        self._p2_keys = dict(self.save.get_controls(2))

        self._sfx_vol   = self.save.get("sfx_volume", 0.8)
        self._music_vol = self.save.get("music_volume", 0.6)

        self._selected_row = 0
        self._action_labels = ["left", "right", "up", "light", "heavy", "special", "super", "block", "dash", "counter", "slam"]

    def handle_event(self, event):
        if self._rebinding:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._rebinding = None
                    return
                player, action = self._rebinding
                keys = self._p1_keys if player == 1 else self._p2_keys
                keys[action] = event.key
                self.save.set_key_binding(player, action, event.key)
                self._rebinding = None
                self.audio.play_sfx("confirm")
            return

        if self._gamer_id_editing:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    self._gamer_id_editing = False
                    self.save.set("gamer_id", self._gamer_id_text)
                    self.audio.play_sfx("confirm")
                elif event.key == pygame.K_BACKSPACE:
                    self._gamer_id_text = self._gamer_id_text[:-1]
                else:
                    if len(self._gamer_id_text) < 20 and event.unicode.isprintable():
                        self._gamer_id_text += event.unicode
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._action = "back"
            elif event.key == pygame.K_TAB:
                self._tab = (self._tab + 1) % 4
                self._selected_row = 0
                self.audio.play_sfx("select")
            elif event.key in (pygame.K_UP, pygame.K_w):
                self._selected_row = max(0, self._selected_row - 1)
                self.audio.play_sfx("select")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                max_row = self._get_max_row()
                self._selected_row = min(max_row, self._selected_row + 1)
                self.audio.play_sfx("select")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activate_selected()
            elif event.key == pygame.K_LEFT:
                self._adjust_slider(-0.1)
            elif event.key == pygame.K_RIGHT:
                self._adjust_slider(0.1)

    def _get_max_row(self):
        if self._tab == 0: return 0
        if self._tab in (1, 2): return len(self._action_labels) - 1
        if self._tab == 3: return 1
        return 0

    def _activate_selected(self):
        if self._tab == 0:
            self._gamer_id_editing = True
        elif self._tab == 1:
            action = self._action_labels[self._selected_row]
            self._rebinding = (1, action)
            self._rebind_timer = 3.0
        elif self._tab == 2:
            action = self._action_labels[self._selected_row]
            self._rebinding = (2, action)
            self._rebind_timer = 3.0

    def _adjust_slider(self, delta):
        if self._tab == 3:
            if self._selected_row == 0:
                self._sfx_vol = max(0.0, min(1.0, self._sfx_vol + delta))
                self.audio.set_sfx_volume(self._sfx_vol)
                self.save.set("sfx_volume", self._sfx_vol)
                self.audio.play_sfx("select")
            elif self._selected_row == 1:
                self._music_vol = max(0.0, min(1.0, self._music_vol + delta))
                self.audio.set_music_volume(self._music_vol)
                self.save.set("music_volume", self._music_vol)

    def update(self, dt):
        self._t += dt
        if self._rebind_timer > 0:
            self._rebind_timer -= dt
            if self._rebind_timer <= 0:
                self._rebinding = None
        result = self._action
        self._action = None
        return result

    def draw(self):
        t = self._t
        sw, sh = self.sw, self.sh

        # Background
        bg = load_background("dojo", sw, sh)
        self.screen.blit(bg, (0, 0))
        
        # Dark overlay
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        dt(self.screen, "SETTINGS", 50, GOLD, sw // 2, 20, center=True)

        # Tabs
        tab_labels = ["PROFILE", "P1 CONTROLS", "P2 CONTROLS", "AUDIO"]
        tab_w = 220
        total_w = len(tab_labels) * tab_w
        start_x = sw // 2 - total_w // 2

        for i, label in enumerate(tab_labels):
            r = pygame.Rect(start_x + i * tab_w, 90, tab_w - 10, 45)
            is_active = (i == self._tab)
            fill_c = (80, 20, 20) if is_active else (20, 10, 10)
            bord_c = GOLD if is_active else PANEL_EDGE
            
            pygame.draw.rect(self.screen, fill_c, r)
            pygame.draw.rect(self.screen, bord_c, r, 2)
            dt(self.screen, label, 24, OFF_WHITE, r.x + r.w // 2, r.y + 10, center=True)

        if self._rebinding:
            ov = pygame.Surface((sw, sh), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 180))
            self.screen.blit(ov, (0,0))
            r_player, r_action = self._rebinding
            dt(self.screen, f"Press a key for: {r_action.upper()} (P{r_player})", 40, YELLOW, sw//2, sh//2 - 40, center=True)
            dt(self.screen, "ESC to cancel", 24, (180, 180, 180), sw//2, sh//2 + 20, center=True)
            return

        if self._tab == 0:
            self._draw_profile(t)
        elif self._tab == 1:
            self._draw_controls(1, self._p1_keys)
        elif self._tab == 2:
            self._draw_controls(2, self._p2_keys)
        elif self._tab == 3:
            self._draw_audio()

        dt(self.screen, "Up/Down=Nav  Enter=Select/Rebind  Tab=Switch  Left/Right=Adjust  ESC=Back", 20, (120, 120, 120), sw//2, sh - 30, center=True)

    def _draw_profile(self, t):
        sw, sh = self.sw, self.sh
        cx = sw // 2
        y  = 180
        dt(self.screen, "GAMER ID:", 30, OFF_WHITE, cx - 250, y)

        box = pygame.Rect(cx - 50, y - 5, 300, 42)
        border_col = CYAN if self._gamer_id_editing else PANEL_EDGE
        pygame.draw.rect(self.screen, (20, 10, 10), box)
        pygame.draw.rect(self.screen, border_col, box, 2)
        
        display_text = self._gamer_id_text
        if self._gamer_id_editing and int(t * 2) % 2 == 0:
            display_text += "|"
        dt(self.screen, display_text, 24, WHITE, box.x + 10, box.y + 8)

        y += 65
        hint = "Type your GamerID - Enter/ESC to confirm" if self._gamer_id_editing else "Press Enter to edit your GamerID"
        dt(self.screen, hint, 20, CYAN if self._gamer_id_editing else (140, 140, 160), cx, y, center=True)

        y += 60
        stats = [
            ("Level", str(self.save.get("level", 1))),
            ("Coins", str(self.save.get("coins", 0))),
            ("Wins",  str(self.save.get("wins", 0))),
            ("Losses",str(self.save.get("losses", 0))),
        ]
        for label, val in stats:
            dt(self.screen, f"{label}:", 26, (160, 160, 180), cx - 150, y)
            dt(self.screen, val, 26, WHITE, cx + 50, y)
            y += 40

    def _draw_controls(self, player, keys):
        sw = self.sw
        header_col = HP_COLOR_P1 if player == 1 else HP_COLOR_P2
        dt(self.screen, f"PLAYER {player} CONTROLS", 32, header_col, sw//2, 160, center=True)

        for i, action in enumerate(self._action_labels):
            col = i % 2
            row = i // 2
            x = sw // 2 - 350 + col * 380
            y = 220 + row * 60
            
            is_sel = (i == self._selected_row) and (self._tab == player)
            row_rect = pygame.Rect(x, y, 320, 50)
            
            fill_c = (80, 20, 20) if is_sel else (20, 10, 10)
            bord_c = GOLD if is_sel else PANEL_EDGE
            
            pygame.draw.rect(self.screen, fill_c, row_rect)
            pygame.draw.rect(self.screen, bord_c, row_rect, 2)

            dt(self.screen, action.upper(), 24, WHITE, x + 20, y + 12)
            key_code = keys.get(action, 0)
            key_name = pygame.key.name(key_code).upper()
            dt(self.screen, f"[{key_name}]", 24, CYAN if is_sel else (160, 160, 200), x + 200, y + 12)

    def _draw_audio(self):
        sw = self.sw
        dt(self.screen, "AUDIO SETTINGS", 32, WHITE, sw//2, 160, center=True)

        sliders = [("SFX Volume", self._sfx_vol, ORANGE), ("Music Volume", self._music_vol, CYAN)]
        for i, (label, val, col) in enumerate(sliders):
            y = 240 + i * 100
            is_sel = (i == self._selected_row)
            dt(self.screen, label, 28, WHITE, sw//2 - 300, y)

            bar_x = sw//2 - 100
            bar_w = 400
            bar_h = 24
            
            pygame.draw.rect(self.screen, (20, 10, 10), (bar_x, y + 2, bar_w, bar_h))
            fill_w = max(0, int(bar_w * val))
            pygame.draw.rect(self.screen, col, (bar_x, y + 2, fill_w, bar_h))
            pygame.draw.rect(self.screen, WHITE if is_sel else PANEL_EDGE, (bar_x, y + 2, bar_w, bar_h), 2)
            
            hx = bar_x + fill_w
            pygame.draw.circle(self.screen, WHITE, (hx, y + 2 + bar_h//2), 14)
            pygame.draw.circle(self.screen, col, (hx, y + 2 + bar_h//2), 10)

            dt(self.screen, f"{int(val * 100)}%", 24, WHITE, bar_x + bar_w + 20, y + 4)
