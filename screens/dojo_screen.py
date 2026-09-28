import pygame
import math
import random
from settings import *
from core.asset_loader import get_font, draw_text as dt, load_background, get_idle_sprite, get_sprite
from characters.character_data import CHARACTERS, get_character
from entities.fighter import Fighter
from renderer.fighter_renderer import FighterRenderer


# ─── Physics Punching Bag ─────────────────────────────────────────────────────
class PunchingBag:
    """A ceiling-hung punching bag with real pendulum physics.
    Pure black silhouette, no textures. Swings proportionally to hit power."""

    def __init__(self, x, ceiling_y):
        self.anchor_x  = x
        self.anchor_y  = ceiling_y
        self.rope_len  = 160              # px — longer rope, more visible swing
        self.angle     = 0.0             # radians from vertical
        self.ang_vel   = 0.0
        self.ang_damp  = 0.92            # realistic damping
        self.gravity_k = 0.015           # pendulum gravity constant

        # Big, clear bag dimensions
        self.bag_w = 80
        self.bag_h = 160

        self.hit_flash   = 0.0
        self.flash_color = (255, 80, 0)
        self.damage_numbers = []
        self.impact_rings   = []         # ring shockwave on hit

    @property
    def bag_cx(self):
        return self.anchor_x + math.sin(self.angle) * self.rope_len

    @property
    def bag_cy(self):
        # Center of bag
        return self.anchor_y + math.cos(self.angle) * self.rope_len

    def hit(self, attack_type, damage):
        """Apply impulse to the bag based on attack intensity."""
        impulse_map = {
            "light":    0.06,
            "heavy":    0.16,
            "special":  0.20,
            "super":    0.30,
            "air":      0.10,
            "dash":     0.14,
            "counter":  0.12,
            "slam":     0.26,
            "sweep":    0.08,
        }
        impulse = impulse_map.get(attack_type, 0.10)
        # Always push away from player (left = push right, right = push left)
        direction = 1 if self.bag_cx >= self.anchor_x else -1
        self.ang_vel += impulse * direction

        # Flash colour based on attack type
        if attack_type in ("super", "slam"):
            self.flash_color = (255, 40, 0)
            self.hit_flash = 0.25
        elif attack_type in ("heavy", "special"):
            self.flash_color = (255, 130, 0)
            self.hit_flash = 0.18
        else:
            self.flash_color = (255, 220, 0)
            self.hit_flash = 0.12

        # Damage number
        self.damage_numbers.append({
            "val": damage,
            "x": self.bag_cx + random.randint(-25, 25),
            "y": self.bag_cy - 60,
            "vy": -100,
            "life": 1.4,
            "crit": attack_type in ("super", "slam", "heavy"),
        })
        # Impact ring shockwave
        self.impact_rings.append({"r": 10, "alpha": 200, "cx": self.bag_cx, "cy": self.bag_cy})

    def update(self, dt_time):
        # Real pendulum: ang_acc = -(g/L) * sin(θ) — simplified with gravity_k
        ang_acc = -self.gravity_k * math.sin(self.angle)
        self.ang_vel += ang_acc
        self.ang_vel *= self.ang_damp
        self.angle   += self.ang_vel

        # Limit swing angle to ±70 degrees
        max_swing = math.radians(70)
        if abs(self.angle) > max_swing:
            self.angle   = math.copysign(max_swing, self.angle)
            self.ang_vel *= -0.35   # bounce back

        if self.hit_flash > 0:
            self.hit_flash -= dt_time

        for d in self.damage_numbers:
            d["y"]   += d["vy"] * dt_time
            d["life"] -= dt_time
        self.damage_numbers = [d for d in self.damage_numbers if d["life"] > 0]

        for ring in self.impact_rings:
            ring["r"]     += 3
            ring["alpha"] -= 12
        self.impact_rings = [r for r in self.impact_rings if r["alpha"] > 0]

    def is_hit_by(self, fighter):
        """Check if fighter can hit the bag (generous hitbox)."""
        dist = abs(fighter.rect.centerx - self.bag_cx)
        return dist < 150 and abs(fighter.rect.bottom - self.bag_cy) < 130

    def draw(self, surface):
        bx = int(self.bag_cx)
        by = int(self.bag_cy)
        ax = int(self.anchor_x)
        ay = int(self.anchor_y)

        # Ceiling bracket
        pygame.draw.rect(surface, (30, 22, 12), (ax - 16, ay - 22, 32, 24))
        pygame.draw.rect(surface, (80, 60, 30), (ax - 16, ay - 22, 32, 24), 2)

        # Heavy chain (3 links visible)
        chain_top_y = ay
        chain_bot_y = by - self.bag_h // 2
        for i in range(4):
            t = i / 3
            cx_ = int(ax + (bx - ax) * t)
            cy_ = int(chain_top_y + (chain_bot_y - chain_top_y) * t)
            pygame.draw.circle(surface, (50, 50, 55), (cx_, cy_), 4)
            pygame.draw.circle(surface, (100, 100, 110), (cx_, cy_), 4, 1)

        # Impact rings (shockwave)
        for ring in self.impact_rings:
            r_surf = pygame.Surface((ring["r"] * 2 + 4, ring["r"] * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(r_surf, (255, 180, 0, int(ring["alpha"])),
                               (ring["r"] + 2, ring["r"] + 2), ring["r"], 2)
            surface.blit(r_surf, (int(ring["cx"]) - ring["r"] - 2,
                                   int(ring["cy"]) - ring["r"] - 2),
                         special_flags=pygame.BLEND_RGBA_ADD)

        # Ground shadow (ellipse under bag)
        sh_w = max(20, int(self.bag_w * (1 - abs(self.angle) / math.radians(70) * 0.3)))
        sh = pygame.Surface((sh_w + 20, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 90), (0, 0, sh_w + 20, 12))
        surface.blit(sh, (bx - (sh_w + 20) // 2, GROUND_Y - 5))

        # === Pure black silhouette bag ===
        bag_rect = pygame.Rect(bx - self.bag_w // 2, by - self.bag_h // 2,
                               self.bag_w, self.bag_h)

        if self.hit_flash > 0:
            # Flash: draw a colored glow halo first
            halo = pygame.Surface((self.bag_w + 40, self.bag_h + 40), pygame.SRCALPHA)
            fa   = int(200 * (self.hit_flash / 0.25))
            pygame.draw.rect(halo, (*self.flash_color, fa),
                             (0, 0, self.bag_w + 40, self.bag_h + 40), border_radius=20)
            surface.blit(halo, (bag_rect.x - 20, bag_rect.y - 20),
                         special_flags=pygame.BLEND_RGBA_ADD)

        # Pure matte black body
        pygame.draw.rect(surface, (8, 6, 6), bag_rect, border_radius=18)
        # Slight rim highlight so it reads against dark bg
        pygame.draw.rect(surface, (45, 38, 35), bag_rect, 2, border_radius=18)

        # Subtle top cap (where chain attaches)
        cap_rect = pygame.Rect(bx - self.bag_w // 2 + 6, by - self.bag_h // 2 - 10,
                               self.bag_w - 12, 18)
        pygame.draw.ellipse(surface, (18, 14, 12), cap_rect)
        pygame.draw.ellipse(surface, (55, 42, 30), cap_rect, 2)

        # Damage numbers
        for d in self.damage_numbers:
            col  = CRIMSON if d["crit"] else (255, 210, 80)
            size = 32 if d["crit"] else 24
            dt(surface, str(d["val"]), size, col,
               int(d["x"]), int(d["y"]), center=True, shadow=True)


# ─── Dojo Screen ──────────────────────────────────────────────────────────────
class DojoScreen:
    def __init__(self, screen, audio, save_manager):
        self.screen      = screen
        self.audio       = audio
        self.save_manager = save_manager

        self.tabs       = ["FIGHTER INFO", "TRAINING", "FULL ROSTER"]
        self.active_tab = "TRAINING"

        if hasattr(self.save_manager, "get_controls"):
            self.controls = self.save_manager.get_controls(1)
        else:
            self.controls = DEFAULT_P1_KEYS

        self.active_char_id = "warrior"
        self.player   = Fighter(self.active_char_id, 1, 350, GROUND_Y)
        self.renderer = FighterRenderer()

        sw = screen.get_width()
        sh = screen.get_height()
        # Bag positioned right side, hanging from ceiling at ~20% from top
        bag_anchor_x = sw - 220
        bag_anchor_y = int(sh * 0.18)
        self.bag = PunchingBag(bag_anchor_x, bag_anchor_y)

        self.last_attack_type = "light"

    def set_character(self, char_id):
        self.active_char_id = char_id
        self.player = Fighter(self.active_char_id, 1, 350, GROUND_Y)
        self.bag.damage_numbers.clear()
        self.bag.impact_rings.clear()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._action = "back"   # stored — returned by update()
                return

            if self.active_tab == "TRAINING":
                for atk_name in ["light", "heavy", "special", "super",
                                  "dash", "counter", "slam", "sweep"]:
                    if event.key == self.controls.get(atk_name):
                        self._do_attack(atk_name)
                        return

                if event.key == self.controls.get("up"):
                    self.player.jump()
                elif event.key == self.controls.get("block"):
                    self.player.block()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            sw = self.screen.get_width()
            # Back button click
            if pygame.Rect(14, 14, 110, 36).collidepoint(mx, my):
                self._action = "back"
                return
            for i, tab in enumerate(self.tabs):
                rect = pygame.Rect(sw // 2 - 300 + i * 200, 20, 180, 40)
                if rect.collidepoint(mx, my):
                    self.active_tab = tab

            if self.active_tab in ("FIGHTER INFO", "FULL ROSTER"):
                for i, char in enumerate(CHARACTERS):
                    cx = 70 + (i % 5) * 220
                    cy = 130 + (i // 5) * 70
                    rect = pygame.Rect(cx, cy, 200, 55)
                    if rect.collidepoint(mx, my):
                        self.set_character(char["id"])
                        return

        elif event.type == pygame.KEYUP:
            if event.key == self.controls.get("block"):
                self.player.release_block()

        return None

    def _do_attack(self, atk_name):
        self.last_attack_type = atk_name
        if self.bag.is_hit_by(self.player):
            char_data = get_character(self.active_char_id)
            move = char_data["moves"].get(atk_name)
            if move:
                dmg = move.get("damage", 10)
                self.bag.hit(atk_name, dmg)
        state_map = {
            "light": "attack_light", "heavy": "attack_heavy",
            "special": "special",    "super": "super",
            "dash": "dash",          "counter": "counter",
            "slam": "slam",          "sweep": "sweep",
        }
        self.player.state       = state_map.get(atk_name, "attack_light")
        self.player.state_timer = 0.4

    def update(self, dt_time):
        self._dt = dt_time
        keys = pygame.key.get_pressed()
        if self.active_tab == "TRAINING":
            c = self.controls
            if keys[c.get("left", pygame.K_a)]:
                self.player.move_left()
            elif keys[c.get("right", pygame.K_d)]:
                self.player.move_right()
            else:
                self.player.stop_x()

            self.player.update(dt_time, self.screen.get_width())
            self.bag.update(dt_time)

        # Return and clear any pending action (ESC → back)
        action = getattr(self, "_action", None)
        self._action = None
        return action

    def draw(self):
        dt_time = getattr(self, "_dt", 0.016)
        sw, sh = self.screen.get_width(), self.screen.get_height()

        bg = load_background("dojo", sw, sh)
        if bg:
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill((30, 15, 8))

        # Subtle dark overlay for readability
        ov = pygame.Surface((sw, sh), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 80))
        self.screen.blit(ov, (0, 0))

        # Ground line
        pygame.draw.line(self.screen, (120, 90, 55), (0, GROUND_Y), (sw, GROUND_Y), 3)
        ground_surf = pygame.Surface((sw, sh - GROUND_Y), pygame.SRCALPHA)
        ground_surf.fill((20, 12, 5, 140))
        self.screen.blit(ground_surf, (0, GROUND_Y))

        # Tabs
        for i, tab in enumerate(self.tabs):
            rect = pygame.Rect(sw // 2 - 300 + i * 200, 20, 180, 40)
            color = GOLD if self.active_tab == tab else PANEL_EDGE
            pygame.draw.rect(self.screen, (15, 8, 4), rect)
            pygame.draw.rect(self.screen, color, rect, 2)
            dt(self.screen, tab, 20, color if self.active_tab == tab else OFF_WHITE,
               rect.centerx, rect.centery - 10, center=True)

        # ── BACK button (top-left, always visible) ────────────────────────────
        back_rect = pygame.Rect(14, 14, 110, 36)
        pygame.draw.rect(self.screen, (35, 12, 6), back_rect, border_radius=6)
        pygame.draw.rect(self.screen, GOLD, back_rect, 2, border_radius=6)
        dt(self.screen, "◀  BACK", 20, GOLD,
           back_rect.centerx, back_rect.y + 8, center=True)


        if self.active_tab == "TRAINING":
            self.draw_training()
        elif self.active_tab == "FIGHTER INFO":
            self.draw_fighter_info()
        elif self.active_tab == "FULL ROSTER":
            self.draw_roster()

    def draw_training(self):
        sw, sh = self.screen.get_width(), self.screen.get_height()

        # Draw bag FIRST (behind player)
        self.bag.draw(self.screen)

        # Draw player
        self.renderer.draw(self.screen, self.player)

        # ── Move List Panel ──────────────────────────────────────────────────
        panel_rect = pygame.Rect(sw - 280, 80, 260, 390)
        panel_surf = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        panel_surf.fill((10, 5, 3, 210))
        self.screen.blit(panel_surf, panel_rect.topleft)
        pygame.draw.rect(self.screen, GOLD, panel_rect, 2)

        dt(self.screen, "MOVE LIST", 22, GOLD,
           panel_rect.centerx, panel_rect.y + 8, center=True)

        moves = [
            ("MOVE LEFT",  "left"),  ("MOVE RIGHT", "right"),
            ("JUMP",       "up"),    ("BLOCK",       "block"),
            ("LIGHT ATK",  "light"), ("HEAVY ATK",   "heavy"),
            ("SPECIAL",    "special"),("SUPER",       "super"),
            ("DASH STRIKE","dash"),  ("COUNTER",     "counter"),
            ("SLAM",       "slam"),  ("SWEEP",       "sweep"),
        ]
        for i, (name, key) in enumerate(moves):
            val      = self.controls.get(key, pygame.K_UNKNOWN)
            key_name = pygame.key.name(val).upper() if val else "?"
            text     = f"{key_name:<6} {name}"
            col      = GOLD if key in ("sweep", "super", "special") else OFF_WHITE
            dt(self.screen, text, 17, col,
               panel_rect.x + 12, panel_rect.y + 42 + i * 28)

        # ── Combo hints ──────────────────────────────────────────────────────
        k_l = pygame.key.name(self.controls.get("light",  pygame.K_j)).upper()
        k_h = pygame.key.name(self.controls.get("heavy",  pygame.K_k)).upper()
        k_d = pygame.key.name(self.controls.get("dash",   pygame.K_f)).upper()
        k_s = pygame.key.name(self.controls.get("sweep",  pygame.K_n)).upper()

        combo_rect = pygame.Rect(30, sh - 95, sw - 310, 82)
        cs = pygame.Surface(combo_rect.size, pygame.SRCALPHA)
        cs.fill((10, 5, 3, 200))
        self.screen.blit(cs, combo_rect.topleft)
        pygame.draw.rect(self.screen, GOLD, combo_rect, 2)

        dt(self.screen, "COMBOS", 20, GOLD,
           combo_rect.centerx, combo_rect.y + 4, center=True)
        combos = [
            f"{k_l} > {k_l} > {k_h}  =  Triple Slash",
            f"{k_d} + {k_l}  =  Dash Strike",
            f"{k_s}  =  Sweep (Disarm+Stun 1.5s)",
        ]
        for i, c_text in enumerate(combos):
            dt(self.screen, c_text, 17, OFF_WHITE,
               combo_rect.x + 15 + (i * (combo_rect.width // 3)),
               combo_rect.y + 32)

    def draw_fighter_info(self):
        sw, sh = self.screen.get_width(), self.screen.get_height()
        char = get_character(self.active_char_id)

        self._draw_char_strip(80)

        portrait_x, portrait_y = 60, 170
        portrait_w, portrait_h = 220, 350

        p_surf = pygame.Surface((portrait_w, portrait_h), pygame.SRCALPHA)
        p_surf.fill((15, 8, 4, 200))
        self.screen.blit(p_surf, (portrait_x, portrait_y))
        pygame.draw.rect(self.screen, GOLD,
                         (portrait_x, portrait_y, portrait_w, portrait_h), 2)

        sprite = get_idle_sprite(self.active_char_id, target_w=140)
        if sprite:
            sx = portrait_x + portrait_w // 2 - sprite.get_width() // 2
            sy = portrait_y + portrait_h - sprite.get_height() - 10
            self.screen.blit(sprite, (sx, sy))

        dt(self.screen, char["name"].upper(), 26, GOLD,
           portrait_x + portrait_w // 2, portrait_y + 10, center=True)

        stats_x = portrait_x + portrait_w + 30
        stats = [
            ("HP",        char["stats"]["hp"]),
            ("STAMINA",   char["stats"]["stamina"]),
            ("SPEED",     char["stats"]["speed"]),
            ("STRENGTH",  char["stats"]["damage"]),
            ("DEFENSE",   char["stats"]["defense"]),
            ("CLASS",     char["class"].upper()),
            ("TRAIT",     char.get("critical_trait", "none").upper()),
        ]
        for i, (label, val) in enumerate(stats):
            y = portrait_y + 10 + i * 42
            dt(self.screen, label, 18, GOLD, stats_x, y)
            if isinstance(val, int):
                bar_rect = pygame.Rect(stats_x + 120, y + 4, 200, 18)
                pygame.draw.rect(self.screen, (40, 20, 10), bar_rect)
                fill = min(200, int(200 * val / 200))
                pygame.draw.rect(self.screen, CRIMSON,
                                 (bar_rect.x, bar_rect.y, fill, 18))
                pygame.draw.rect(self.screen, GOLD, bar_rect, 1)
                dt(self.screen, str(val), 16, OFF_WHITE,
                   bar_rect.right + 6, y + 2)
            else:
                dt(self.screen, str(val), 18, OFF_WHITE, stats_x + 120, y)

        moves_x = stats_x + 360
        dt(self.screen, "MOVES", 22, GOLD, moves_x, portrait_y + 10)
        for j, (m_name, m_data) in enumerate(char["moves"].items()):
            if j > 10:
                break
            y = portrait_y + 45 + j * 38
            label = m_name.upper().replace("_", " ")
            dt(self.screen, label, 17, GOLD, moves_x, y)
            dt(self.screen, f"DMG:{m_data['damage']}  RNG:{m_data['range']}",
               15, OFF_WHITE, moves_x + 140, y)

    def draw_roster(self):
        sw = self.screen.get_width()
        dt(self.screen, "SELECT CHARACTER", 26, GOLD, sw // 2, 80, center=True)
        self._draw_char_strip(120)

        char = get_character(self.active_char_id)
        sprite = get_idle_sprite(self.active_char_id, target_w=120)
        if sprite:
            sx = sw // 2 - sprite.get_width() // 2
            self.screen.blit(sprite, (sx, 230))

        dt(self.screen, char["name"].upper(), 36, GOLD,
           sw // 2, 430, center=True, shadow=True)
        dt(self.screen, f"CLASS: {char['class'].upper()}  |  HP: {char['stats']['hp']}  |  SPD: {char['stats']['speed']}",
           22, OFF_WHITE, sw // 2, 475, center=True)

    def _draw_char_strip(self, y_top):
        sw = self.screen.get_width()
        for i, char in enumerate(CHARACTERS):
            row, col = divmod(i, 5)
            cx = (sw // 2 - 2 * 220) + col * 220
            cy = y_top + row * 65
            is_sel = char["id"] == self.active_char_id

            rect = pygame.Rect(cx, cy, 200, 55)
            col_bg = (40, 18, 8) if is_sel else (18, 8, 4)
            pygame.draw.rect(self.screen, col_bg, rect, border_radius=6)
            pygame.draw.rect(self.screen, GOLD if is_sel else PANEL_EDGE,
                             rect, 2, border_radius=6)
            dt(self.screen, char["name"].upper(), 19,
               GOLD if is_sel else OFF_WHITE, cx + 10, cy + 8)
            dt(self.screen, char["class"].upper(), 15,
               CRIMSON if is_sel else (100, 80, 60), cx + 10, cy + 30)
