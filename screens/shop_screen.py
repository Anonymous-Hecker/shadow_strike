import pygame
import math
from settings import *
from core.asset_loader import get_font, draw_text as dt, load_background

class ShopScreen:
    def __init__(self, screen, audio, save_manager):
        self.screen = screen
        self.audio  = audio
        self.save   = save_manager
        self.sw     = screen.get_width()
        self.sh     = screen.get_height()
        self._t     = 0.0
        self._action = None
        self._tab    = 0   # 0=Weapons, 1=Armors
        self._cursor = 0
        self._msg    = ""
        self._msg_timer = 0.0

    def _current_items(self):
        return WEAPONS if self._tab == 0 else ARMORS

    def _current_item(self):
        items = self._current_items()
        return items[self._cursor % len(items)] if items else None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._action = "back"
            elif event.key in (pygame.K_UP, pygame.K_w):
                self._cursor = max(0, self._cursor - 1)
                self.audio.play_sfx("select")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                items = self._current_items()
                self._cursor = min(len(items) - 1, self._cursor + 1)
                self.audio.play_sfx("select")
            elif event.key == pygame.K_TAB:
                self._tab = 1 - self._tab
                self._cursor = 0
                self.audio.play_sfx("select")
            elif event.key in (pygame.K_RETURN, pygame.K_b):
                self._try_buy_or_equip()
            elif event.key == pygame.K_e:
                self._try_equip()

    def _try_buy_or_equip(self):
        item = self._current_item()
        if not item: return
        level = self.save.get("level", 1)
        item_type = "weapon" if self._tab == 0 else "armor"
        owned = self.save.get(f"owned_{item_type}s", [])
        
        if item["id"] in owned:
            self._try_equip()
        else:
            if level < item.get("unlock_level", 1):
                self._show_msg(f"Requires Level {item['unlock_level']}!")
                return
            if item["cost"] == 0 or self.save.spend_coins(item["cost"]):
                self.save.unlock_item(item["id"], item_type)
                self.save.equip_item(item["id"], item_type)
                self.audio.play_sfx("purchase")
                self._show_msg(f"Bought & Equipped {item['name']}!")
            else:
                self._show_msg("Not enough coins!")

    def _try_equip(self):
        item = self._current_item()
        if not item: return
        item_type = "weapon" if self._tab == 0 else "armor"
        owned = self.save.get(f"owned_{item_type}s", [])
        if item["id"] in owned:
            self.save.equip_item(item["id"], item_type)
            self.audio.play_sfx("confirm")
            self._show_msg(f"Equipped {item['name']}!")
        else:
            self._show_msg("Buy this item first!")

    def _show_msg(self, text):
        self._msg = text
        self._msg_timer = 2.0

    def update(self, dt_time):
        self._t += dt_time
        if self._msg_timer > 0:
            self._msg_timer -= dt_time
            if self._msg_timer <= 0:
                self._msg = ""
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
        overlay.fill((0, 0, 0, 210))
        self.screen.blit(overlay, (0, 0))

        dt(self.screen, "ARMORY", 50, GOLD, sw//2, 20, center=True)
        coins = self.save.get("coins", 0)
        dt(self.screen, f"COINS: {coins}", 30, GOLD, sw - 150, 30)

        # Tabs
        tab_w = 200
        for i, label in enumerate(["WEAPONS", "ARMORS"]):
            r = pygame.Rect(sw//2 - 210 + i * 220, 90, tab_w, 45)
            is_active = (i == self._tab)
            fill_c = (80, 60, 10) if is_active else (20, 10, 10)
            bord_c = GOLD if is_active else PANEL_EDGE
            pygame.draw.rect(self.screen, fill_c, r)
            pygame.draw.rect(self.screen, bord_c, r, 2)
            dt(self.screen, label, 26, OFF_WHITE, r.x + r.w//2, r.y + 10, center=True)

        items = self._current_items()
        level = self.save.get("level", 1)
        item_type = "weapon" if self._tab == 0 else "armor"
        owned = self.save.get(f"owned_{item_type}s", [])
        equipped = self.save.get(f"equipped_{item_type}", "")

        # Items list
        list_y = 150
        for j, item in enumerate(items):
            r = pygame.Rect(sw//2 - 350, list_y + j * 70, 700, 60)
            is_sel = (j == self._cursor)
            is_owned = item["id"] in owned
            is_equip = item["id"] == equipped
            locked = item.get("unlock_level", 1) > level
            item_col = item.get("color", (180, 180, 180))
            
            pulse = int(math.sin(t * 4) * 3) if is_sel else 0
            rx = r.x
            ry = r.y + pulse
            
            if is_equip:
                pygame.draw.rect(self.screen, (40, 60, 40), (rx, ry, r.w, r.h))
                pygame.draw.rect(self.screen, (80, 180, 80), (rx, ry, r.w, r.h), 2)
            elif is_sel:
                pygame.draw.rect(self.screen, (80, 20, 20), (rx, ry, r.w, r.h))
                pygame.draw.rect(self.screen, GOLD, (rx, ry, r.w, r.h), 2)
            else:
                pygame.draw.rect(self.screen, (20, 10, 10), (rx, ry, r.w, r.h))
                pygame.draw.rect(self.screen, PANEL_EDGE, (rx, ry, r.w, r.h), 1)

            # Draw item icon — procedural weapon/armor shape
            icon_rect = pygame.Rect(rx + 10, ry + 8, 40, 44)
            icon_col = item_col if not locked else (50, 50, 50)
            icon_bg = pygame.Surface((40, 44), pygame.SRCALPHA)
            icon_bg.fill((0, 0, 0, 100))
            pygame.draw.rect(icon_bg, icon_col, (0, 0, 40, 44), 1, border_radius=4)
            self.screen.blit(icon_bg, (icon_rect.x, icon_rect.y))
            icx, icy = icon_rect.centerx, icon_rect.centery
            if self._tab == 0:
                # Weapon icon — sword blade shape
                pygame.draw.line(self.screen, icon_col, (icx, icy - 16), (icx, icy + 12), 3)
                pygame.draw.line(self.screen, icon_col, (icx - 8, icy - 4), (icx + 8, icy - 4), 3)
                pygame.draw.polygon(self.screen, icon_col, [(icx - 3, icy + 12), (icx + 3, icy + 12), (icx, icy + 18)])
                pygame.draw.circle(self.screen, icon_col, (icx, icy - 17), 3)
            else:
                # Armor icon — shield shape
                pts = [(icx, icy - 16), (icx + 14, icy - 8), (icx + 12, icy + 6), (icx, icy + 16), (icx - 12, icy + 6), (icx - 14, icy - 8)]
                pygame.draw.polygon(self.screen, icon_col, pts, 2)
                pygame.draw.line(self.screen, icon_col, (icx, icy - 12), (icx, icy + 10), 2)
                pygame.draw.line(self.screen, icon_col, (icx - 8, icy - 2), (icx + 8, icy - 2), 2)
            
            name_col = WHITE if is_owned else ((200,150,50) if not locked else (80,80,80))
            dt(self.screen, item["name"], 24, name_col, rx + 60, ry + 5)
            dt(self.screen, item.get("perk", ""), 18, (160, 160, 180), rx + 60, ry + 32)
            
            if locked:
                dt(self.screen, f"Lv.{item['unlock_level']}", 24, (200, 140, 50), rx + r.w - 80, ry + 15)
            elif is_equip:
                dt(self.screen, "EQUIPPED", 24, GOLD, rx + r.w - 120, ry + 15)
            elif is_owned:
                dt(self.screen, "[E] Equip", 24, CYAN, rx + r.w - 120, ry + 15)
            else:
                dt(self.screen, f"Cost: {item['cost']}", 24, GOLD if not locked else (80,80,60), rx + r.w - 120, ry + 15)

        # Bottom buttons
        buy_r  = pygame.Rect(sw//2 + 100, sh - 70, 200, 45)
        equip_r= pygame.Rect(sw//2 - 300, sh - 70, 200, 45)
        pygame.draw.rect(self.screen, (60, 20, 20), buy_r)
        pygame.draw.rect(self.screen, GOLD, buy_r, 2)
        pygame.draw.rect(self.screen, (20, 40, 60), equip_r)
        pygame.draw.rect(self.screen, CYAN, equip_r, 2)
        
        dt(self.screen, "BUY / CONFIRM", 24, WHITE, buy_r.x + buy_r.w//2, buy_r.y + 10, center=True)
        dt(self.screen, "[E] EQUIP", 24, WHITE, equip_r.x + equip_r.w//2, equip_r.y + 10, center=True)

        if self._msg:
            alpha = min(255, int(self._msg_timer * 200))
            msg_s = get_font(32).render(self._msg, True, YELLOW)
            msg_s.set_alpha(alpha)
            self.screen.blit(msg_s, (sw//2 - msg_s.get_width()//2, sh - 130))

        dt(self.screen, "Up/Down=Nav  Enter=Buy  E=Equip  Tab=Switch  ESC=Back", 20, (120,120,120), sw//2, sh - 25, center=True)
