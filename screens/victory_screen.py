import pygame
import math
from settings import *
from core.asset_loader import get_font, draw_text as dt, load_background, get_idle_sprite
from ui.particle_system import ParticleSystem

class VictoryScreen:
    def __init__(self, screen, audio, save_manager, winner, total_coins, max_combo, crit_count):
        self.screen  = screen
        self.audio   = audio
        self.save    = save_manager
        self.sw      = screen.get_width()
        self.sh      = screen.get_height()
        self._t      = 0.0
        self._action = None

        self.winner       = winner
        self.total_coins  = total_coins
        self.max_combo    = max_combo
        self.crit_count   = crit_count
        
        # Calculate breakdown based on typical logic
        self.win_bonus = COINS_PER_WIN if (winner and winner.player_num == 1) else 0
        self.combo_bonus = max_combo * COINS_PER_COMBO
        self.crit_bonus = crit_count * 5 # Assuming 5 coins per crit as a rough guess

        # Record match
        p1_won = (winner is not None and winner.player_num == 1)
        xp_earned = 30 if p1_won else 10
        xp_earned += max_combo * 2 + crit_count * 3
        leveled_up = self.save.record_match(p1_won, max_combo, crit_count)
        
        if leveled_up:
            self.audio.play_sfx("level_up")
        else:
            self.audio.play_sfx("victory")

        self._leveled_up = leveled_up
        self._new_level  = self.save.get("level", 1)
        self._xp_earned  = xp_earned
        self._p1_won     = p1_won

        self.particles = ParticleSystem()
        self._confetti_spawned = False
        self._selected_btn = 0
        
        # Determine next unlock
        self.next_unlock = None
        for w in WEAPONS:
            if w["unlock_level"] > self._new_level:
                self.next_unlock = w
                break
        if not self.next_unlock:
            for a in ARMORS:
                if a["unlock_level"] > self._new_level:
                	self.next_unlock = a
                	break

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w, pygame.K_LEFT, pygame.K_a):
                self._selected_btn = 0
                self.audio.play_sfx("select")
            elif event.key in (pygame.K_DOWN, pygame.K_s, pygame.K_RIGHT, pygame.K_d):
                self._selected_btn = 1
                self.audio.play_sfx("select")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.audio.play_sfx("confirm")
                self._action = "char_select" if self._selected_btn == 1 else "main_menu"
            elif event.key == pygame.K_ESCAPE:
                self.audio.play_sfx("confirm")
                self._action = "main_menu"

    def update(self, dt):
        self._t += dt
        if not self._confetti_spawned and self._t > 0.5 and self._p1_won:
            self._confetti_spawned = True
            self.particles.emit_confetti(self.sw // 2, self.sh // 4, 60)
        self.particles.update(dt)
        result = self._action
        self._action = None
        return result

    def draw(self):
        t = self._t
        sw, sh = self.sw, self.sh

        # Background
        bg = load_background("volcano", sw, sh)
        self.screen.blit(bg, (0, 0))
        
        # Dark overlay
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        self.particles.draw(self.screen)

        # Winner Sprite
        if self.winner:
            sprite = get_idle_sprite(self.winner.char_id, target_w=350)
            if sprite:
                self.screen.blit(sprite, (sw // 4 - sprite.get_width() // 2, sh // 2 - sprite.get_height() // 2 + 50))
            
            char_name = self.winner.char_data['name']
            if self._p1_won:
                dt(self.screen, f"{char_name} WINS!", 70, GOLD, sw // 4, sh // 2 - 200, center=True, shadow=True)
            else:
                dt(self.screen, f"{char_name} DEFEATS YOU", 70, CRIMSON, sw // 4, sh // 2 - 200, center=True, shadow=True)
        else:
            dt(self.screen, "DRAW", 70, OFF_WHITE, sw // 4, sh // 2 - 200, center=True, shadow=True)

        # Stats panel
        panel_x = sw // 2 + 50
        panel_y = 150
        panel_w = 500
        panel_h = 420

        bg_panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        bg_panel.fill((10, 5, 5, 200))
        pygame.draw.rect(bg_panel, GOLD, (0, 0, panel_w, panel_h), 2)
        self.screen.blit(bg_panel, (panel_x, panel_y))
        
        dt(self.screen, "REWARDS", 40, OFF_WHITE, panel_x + panel_w // 2, panel_y + 20, center=True)
        
        y = panel_y + 90
        dt(self.screen, f"Win Bonus: +{self.win_bonus} coins", 26, GOLD, panel_x + 30, y)
        y += 45
        dt(self.screen, f"Combo Bonus ({self.max_combo}-Hit Max): +{self.combo_bonus} coins", 26, GOLD, panel_x + 30, y)
        y += 45
        dt(self.screen, f"Critical Hits ({self.crit_count}): +{self.crit_bonus} coins", 26, GOLD, panel_x + 30, y)
        y += 45
        pygame.draw.line(self.screen, PANEL_EDGE, (panel_x + 30, y), (panel_x + panel_w - 30, y), 2)
        y += 20
        dt(self.screen, f"Total Coins Earned: {self.total_coins}", 32, YELLOW, panel_x + 30, y)
        y += 50
        dt(self.screen, f"XP Earned: +{self._xp_earned}", 32, CYAN, panel_x + 30, y)
        
        y += 70
        if self.next_unlock:
            teaser = f"Next Unlock: {self.next_unlock['name']} ({self.next_unlock['cost']} coins)"
            dt(self.screen, teaser, 22, (180, 180, 180), panel_x + panel_w // 2, y, center=True)

        # Level-up banner
        if self._leveled_up and t > 1.0:
            pulse = 1.0 + math.sin(t * 5) * 0.1
            size = int(40 * pulse)
            dt(self.screen, f"LEVEL UP! Now Level {self._new_level}!", size, CYAN, sw // 2, 80, center=True)

        # Buttons
        btn_y = sh - 100
        btn_w = 220
        btn_h = 50
        btn_gap = 40
        start_x = sw // 2 - (btn_w * 2 + btn_gap) // 2
        
        labels = ["CONTINUE", "REMATCH"]
        for i, label in enumerate(labels):
            bx = start_x + i * (btn_w + btn_gap)
            rect = pygame.Rect(bx, btn_y, btn_w, btn_h)
            is_sel = (i == self._selected_btn)
            
            fill_col = (60, 20, 20) if is_sel else (20, 10, 10)
            border_col = GOLD if is_sel else PANEL_EDGE
            pygame.draw.rect(self.screen, fill_col, rect)
            pygame.draw.rect(self.screen, border_col, rect, 2)
            
            dt(self.screen, label, 30, WHITE, bx + btn_w // 2, btn_y + 10, center=True)

        self.particles.draw_screen_flash(self.screen, sw, sh)

