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
    """A ceiling-hung punching bag with pendulum physics.
    When hit, swings proportional to attack intensity."""

    def __init__(self, x, ceiling_y):
        self.anchor_x  = x
        self.anchor_y  = ceiling_y  # rope attach point
        self.rope_len  = 120              # px
        self.angle     = 0.0             # radians from vertical
        self.ang_vel   = 0.0
        self.ang_damp  = 0.88            # damping per frame
        self.gravity_k = 0.018           # pendulum gravity constant

        self.bag_w = 50
        self.bag_h = 100

        # Hit flash timer
        self.hit_flash = 0.0
        # Damage numbers
        self.damage_numbers = []

    @property
    def bag_cx(self):
        return self.anchor_x + math.sin(self.angle) * self.rope_len

    @property
    def bag_cy(self):
        return self.anchor_y + math.cos(self.angle) * self.rope_len

    def hit(self, attack_type, damage):
        """Apply impulse to the bag based on attack intensity."""
        impulse_map = {
            "light":        0.08,
            "heavy":        0.18,
            "special":      0.22,
            "super":        0.35,
            "air":          0.12,
            "dash":         0.16,
            "counter":      0.14,
            "slam":         0.28,
            "sweep":        0.10,
        }
        impulse = impulse_map.get(attack_type, 0.10)
        self.ang_vel += impulse * (1 if self.bag_cx < self.anchor_x else -1) + impulse
        self.hit_flash = 0.15
        # Add damage number
        self.damage_numbers.append({
            "val": damage, "x": self.bag_cx + random.randint(-20, 20),
            "y": self.bag_cy - 40, "vy": -80, "life": 1.2, "crit": attack_type in ("super","slam","heavy")
        })

    def update(self, dt_time):
        # Pendulum physics: ang_acc = -gravity_k * sin(angle)
        ang_acc = -self.gravity_k * math.sin(self.angle)
        self.ang_vel += ang_acc
        self.ang_vel *= self.ang_damp
        self.angle   += self.ang_vel

        # Limit swing angle
        max_swing = math.radians(60)
        if abs(self.angle) > max_swing:
            self.angle   = math.copysign(max_swing, self.angle)
            self.ang_vel *= -0.4

        if self.hit_flash > 0:
            self.hit_flash -= dt_time

        for d in self.damage_numbers:
            d["y"]   += d["vy"] * dt_time
            d["life"] -= dt_time
        self.damage_numbers = [d for d in self.damage_numbers if d["life"] > 0]

    def is_hit_by(self, fighter):
        """Check if fighter can hit the bag."""
        bx = self.bag_cx
        dist = abs(fighter.rect.centerx - bx)
        return dist < 120 and abs(fighter.rect.bottom - self.bag_cy) < 100

    def draw(self, surface):
        bx = int(self.bag_cx)
        by = int(self.bag_cy)
        ax = int(self.anchor_x)
        ay = int(self.anchor_y)

        # Ceiling mount bracket
        pygame.draw.rect(surface, (40, 30, 20), (ax - 12, ay - 18, 24, 20))
        pygame.draw.rect(surface, (80, 60, 35), (ax - 12, ay - 18, 24, 20), 2)

        # Rope
        rope_mid = (ax + (bx - ax) // 3 + random.randint(-1, 1),
                    ay + (by - ay) // 3)
        pygame.draw.line(surface, (100, 75, 45), (ax, ay), rope_mid, 2)
        pygame.draw.line(surface, (100, 75, 45), rope_mid,
                         (bx, by - self.bag_h // 2), 2)

        # Bag shadow
        sh = pygame.Surface((self.bag_w + 10, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 80), (0, 0, self.bag_w + 10, 10))
        surface.blit(sh, (bx - (self.bag_w + 10) // 2, GROUND_Y - 4))

        # Bag body color with hit flash
        if self.hit_flash > 0:
            bag_col  = (40, 15, 10)
            tape_col = (200, 90, 30)
        else:
            bag_col  = (15, 10, 8)
            tape_col = (30, 22, 15)

        # Draw rounded bag body
        bag_rect = pygame.Rect(bx - self.bag_w // 2, by - self.bag_h // 2,
                               self.bag_w, self.bag_h)
        pygame.draw.rect(surface, bag_col, bag_rect, border_radius=12)
        pygame.draw.rect(surface, (100, 70, 40), bag_rect, 2, border_radius=12)

        # Seam lines removed

        # Tape strips (horizontal bands)
        for ty in [by - self.bag_h // 4, by, by + self.bag_h // 4]:
            tape_rect = pygame.Rect(bx - self.bag_w // 2, ty - 4,
                                    self.bag_w, 8)
            pygame.draw.rect(surface, tape_col, tape_rect)
            pygame.draw.rect(surface, (110, 80, 45), tape_rect, 1)

        # Chain at top
        for i in range(3):
            cy_ = ay + i * 6
            pygame.draw.circle(surface, (80, 80, 80),
                                (ax, cy_), 3 - i // 2)

        # Damage numbers
        for d in self.damage_numbers:
            alpha = int(255 * min(1.0, d["life"]))
            col   = CRIMSON if d["crit"] else (230, 200, 150)
            size  = 30 if d["crit"] else 22
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

        # Get actual keybinds
        if hasattr(self.save_manager, "get_controls"):
            self.controls = self.save_manager.get_controls(1)
        else:
            self.controls = DEFAULT_P1_KEYS

        self.active_char_id = "warrior"
        self.player   = Fighter(self.active_char_id, 1, 350, GROUND_Y)
        self.renderer = FighterRenderer()

        sw = screen.get_width()
        # Bag placed center-right
        self.bag = PunchingBag(sw // 2 + 100, GROUND_Y - 200)

        self.last_attack_type = "light"

    def set_character(self, char_id):
        self.active_char_id = char_id
        sw = self.screen.get_width()
        self.player = Fighter(self.active_char_id, 1, 350, GROUND_Y)
        self.bag.damage_numbers.clear()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"

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
            for i, tab in enumerate(self.tabs):
                rect = pygame.Rect(sw // 2 - 300 + i * 200, 20, 180, 40)
                if rect.collidepoint(mx, my):
                    self.active_tab = tab

            # Character selector (shown on FIGHTER INFO and ROSTER tabs)
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
        # Check if bag is in range
        if self.bag.is_hit_by(self.player):
            char_data = get_character(self.active_char_id)
            move = char_data["moves"].get(atk_name)
            if move:
                dmg = move.get("damage", 10)
                self.bag.hit(atk_name, dmg)
        # Play animation
        state_map = {
            "light": "attack_light", "heavy": "attack_heavy",
            "special": "special", "super": "super",
            "dash": "dash", "counter": "counter",
            "slam": "slam", "sweep": "sweep",
        }
        self.player.state = state_map.get(atk_name, "attack_light")
        self.player.state_timer = 0.4

    def update(self, dt_time):
        self._dt = dt_time   # store for draw()
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

    def draw(self):
        dt_time = getattr(self, "_dt", 0.016)
        sw, sh = self.screen.get_width(), self.screen.get_height()

        # Background — dojo with warm amber sunset tones (flat 2D)
        bg = load_background("dojo", sw, sh)
        if bg:
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill((30, 15, 8))

        # Dark overlay for readability
        ov = pygame.Surface((sw, sh), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 100))
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

        if self.active_tab == "TRAINING":
            self.draw_training()
        elif self.active_tab == "FIGHTER INFO":
            self.draw_fighter_info()
        elif self.active_tab == "FULL ROSTER":
            self.draw_roster()

    def draw_training(self):
        sw, sh = self.screen.get_width(), self.screen.get_height()

        # Draw bag
        self.bag.draw(self.screen)

        # Draw player (fixed scale — ignore jump height changes visually)
        self.renderer.draw(self.screen, self.player)

        # Ceiling rope anchor ceiling line (decorative)
        pygame.draw.line(self.screen, (80, 60, 35),
                         (self.bag.anchor_x - 30, 90),
                         (self.bag.anchor_x + 30, 90), 6)

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

        # Character selector strip at top
        self._draw_char_strip(80)

        # Portrait panel
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

        # Stats panel
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
                # bar
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

        # Move list panel
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

        # Show selected char info briefly below
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
