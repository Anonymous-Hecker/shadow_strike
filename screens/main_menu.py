"""
Main Menu — Shadow Strike
COMMIT 1: Show only player's selected/favourite character. Dark atmosphere bg.
"""
import pygame
import math
import random
from settings import *
from core.asset_loader import load_logo, load_background, get_font, draw_text, get_sprite
from characters.character_data import get_character, CHARACTERS


# ── Fallback animated silhouette (used when sprite sheet is missing) ──────────
def _draw_menu_silhouette(surface, cx, ground_y, t, state="idle", aura=(160, 30, 30)):
    col = (15, 12, 12)
    bob = int(math.sin(t * 2.5) * 4)
    base_y = ground_y + bob

    # Ground shadow
    sh = pygame.Surface((80, 14), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 80), (0, 2, 80, 10))
    surface.blit(sh, (cx - 40, ground_y - 6))

    # Head
    pygame.draw.circle(surface, col, (cx, base_y - 180), 22)
    # Neck
    pygame.draw.line(surface, col, (cx, base_y - 158), (cx, base_y - 145), 9)
    # Torso
    pts = [(cx - 22, base_y - 145), (cx + 22, base_y - 145),
           (cx + 18, base_y - 70), (cx - 18, base_y - 70)]
    pygame.draw.polygon(surface, col, pts)

    # Legs
    if state in ("attack_light", "attack_heavy"):
        pygame.draw.line(surface, col, (cx - 8, base_y - 70), (cx - 28, base_y - 10), 12)
        pygame.draw.line(surface, col, (cx + 8, base_y - 70), (cx + 20, base_y - 10), 12)
    else:
        swing = math.sin(t * 4) * 12
        pygame.draw.line(surface, col, (cx - 8, base_y - 70),
                         (cx - 18 + int(swing), base_y - 10), 12)
        pygame.draw.line(surface, col, (cx + 8, base_y - 70),
                         (cx + 18 - int(swing), base_y - 10), 12)

    # Arms
    if state in ("attack_light", "attack_heavy", "special"):
        pygame.draw.line(surface, col, (cx + 20, base_y - 138), (cx + 70, base_y - 110), 10)
        pygame.draw.line(surface, col, (cx - 18, base_y - 138), (cx - 38, base_y - 155), 9)
        # Weapon tip glow
        tip_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(tip_surf, (*aura, 160), (10, 10), 9)
        surface.blit(tip_surf, (cx + 62, base_y - 118),
                     special_flags=pygame.BLEND_RGBA_ADD)
    else:
        arm_sw = math.sin(t * 3) * 5
        pygame.draw.line(surface, col, (cx + 20, base_y - 138),
                         (cx + 42, base_y - 115 + int(arm_sw)), 10)
        pygame.draw.line(surface, col, (cx - 18, base_y - 138),
                         (cx - 36, base_y - 118 - int(arm_sw)), 9)

    # Glowing eyes
    pygame.draw.circle(surface, aura, (cx + 6, base_y - 183), 4)
    pygame.draw.circle(surface, (255, 255, 255), (cx + 6, base_y - 183), 1)


# ── Main Menu ─────────────────────────────────────────────────────────────────
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

        # ── Rotating backgrounds: palace → temple → volcano ─────────────────
        _bg_names = ["palace", "temple_new", "volcano"]
        self._bgs  = [load_background(n, self.sw, self.sh) for n in _bg_names]
        self._bg_idx      = 0          # current bg index
        self._bg_timer    = 0.0        # time on current bg
        self._bg_switch   = 25.0       # seconds per background
        self._bg_fade     = 0.0        # 0.0 = current, 1.0 = next (crossfade progress)
        self._bg_fading   = False      # True while crossfading

        self._logo = load_logo(620, 190)
        self.audio.play_music()

        # ── Particle system: falling ash/petals, not orange embers ───────────
        self._particles = []
        self._init_particles()

        # ── Showcase: ONLY the player's favourite/selected character ──────────
        fav = self.save.get("favorite_char", None)
        # Validate: must be a real character id
        valid_ids = {c["id"] for c in CHARACTERS}
        if fav not in valid_ids:
            fav = CHARACTERS[0]["id"]   # default to first character
        self._char_id = fav

        # Grab the character's aura colour for theming
        try:
            cdata = get_character(self._char_id)
            self._aura = tuple(cdata.get("aura_color", (160, 30, 30)))
            self._char_name = cdata["name"].upper()
        except Exception:
            self._aura = (160, 30, 30)
            self._char_name = self._char_id.upper()

        # Animated pose cycling
        self._anim_states = ["idle", "idle", "attack_light", "idle",
                             "attack_heavy", "idle", "special", "idle"]
        self._anim_idx   = 0
        self._anim_timer = 0.0
        self._anim_hold  = [1.4, 0.6, 0.35, 0.5, 0.45, 0.7, 0.55, 0.9]

    # ── Particles ─────────────────────────────────────────────────────────────
    def _init_particles(self):
        for _ in range(55):
            self._particles.append(self._new_particle())

    def _new_particle(self):
        return {
            "x":     random.uniform(0, self.sw),
            "y":     random.uniform(-self.sh, self.sh),
            "vx":    random.uniform(-0.3, 0.3),
            "vy":    random.uniform(0.3, 1.0),          # falling downward
            "size":  random.randint(1, 3),
            "alpha": random.randint(60, 160),
            # subtle grey/white ash particles — no orange
            "color": random.choice([
                (200, 200, 210),
                (180, 175, 195),
                (160, 160, 175),
                (220, 215, 225),
            ]),
            "wobble": random.uniform(0, math.pi * 2),
        }

    # ── Events ────────────────────────────────────────────────────────────────
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

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self, dt):
        self._t += dt

        # Particles
        for p in self._particles:
            p["x"]      += p["vx"] * dt * 60 + math.sin(self._t + p["wobble"]) * 0.3
            p["y"]      += p["vy"] * dt * 60
            if p["y"] > self.sh + 10:
                self._particles[self._particles.index(p)] = self._new_particle()
                self._particles[-1]["y"] = -10

        # Background rotation + crossfade
        self._bg_timer += dt
        if self._bg_fading:
            self._bg_fade += dt * 1.5          # crossfade speed (lower = slower)
            if self._bg_fade >= 1.0:
                self._bg_fade   = 0.0
                self._bg_fading = False
                self._bg_idx    = (self._bg_idx + 1) % len(self._bgs)
                self._bg_timer  = 0.0
        elif self._bg_timer >= self._bg_switch:
            self._bg_fading = True
            self._bg_fade   = 0.0

        # Pose cycling
        self._anim_timer += dt
        hold = self._anim_hold[self._anim_idx % len(self._anim_hold)]
        if self._anim_timer >= hold:
            self._anim_timer = 0.0
            self._anim_idx   = (self._anim_idx + 1) % len(self._anim_states)

        # Refresh char each frame in case player changed selection elsewhere
        fav = self.save.get("favorite_char", None)
        valid_ids = {c["id"] for c in CHARACTERS}
        if fav in valid_ids and fav != self._char_id:
            self._char_id = fav
            try:
                cdata = get_character(self._char_id)
                self._aura      = tuple(cdata.get("aura_color", (160, 30, 30)))
                self._char_name = cdata["name"].upper()
            except Exception:
                self._aura      = (160, 30, 30)
                self._char_name = self._char_id.upper()

        result = self._action
        self._action = None
        return result

    # ── Draw helpers ──────────────────────────────────────────────────────────
    def _draw_menu_icon(self, option, x, y, col):
        s = self.screen
        if option == "PLAY":
            pygame.draw.line(s, col, (x-6, y-8), (x+6, y+8), 3)
            pygame.draw.line(s, col, (x+6, y-8), (x-6, y+8), 3)
            pygame.draw.circle(s, col, (x, y), 3)
        elif option == "DOJO":
            pygame.draw.line(s, col, (x-8, y-8), (x+8, y-8), 3)
            pygame.draw.line(s, col, (x-6, y+8), (x-6, y-8), 2)
            pygame.draw.line(s, col, (x+6, y+8), (x+6, y-8), 2)
            pygame.draw.line(s, col, (x-10, y-6), (x+10, y-6), 2)
        elif option == "SKILLS":
            pygame.draw.line(s, col, (x, y-8), (x, y+8), 2)
            pygame.draw.line(s, col, (x-6, y-2), (x+6, y-2), 2)
            pygame.draw.line(s, col, (x-4, y+4), (x+4, y-6), 2)
            pygame.draw.line(s, col, (x+4, y+4), (x-4, y-6), 2)
        elif option == "ARMORY":
            pygame.draw.line(s, col, (x+3, y-10), (x+3, y+8), 3)
            pygame.draw.line(s, col, (x-2, y-4), (x+8, y-4), 2)
            pts = [(x-8, y-6), (x-2, y-8), (x-2, y+6), (x-8, y+4)]
            pygame.draw.polygon(s, col, pts, 2)
        elif option == "PROFILE":
            pygame.draw.circle(s, col, (x, y-5), 4, 2)
            pygame.draw.line(s, col, (x, y-1), (x, y+6), 2)
            pygame.draw.line(s, col, (x-5, y+3), (x+5, y+3), 2)
        elif option == "SETTINGS":
            pygame.draw.circle(s, col, (x, y), 6, 2)
            pygame.draw.circle(s, col, (x, y), 2)
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                ex = x + int(8 * math.cos(rad))
                ey = y + int(8 * math.sin(rad))
                pygame.draw.circle(s, col, (ex, ey), 2)
        elif option == "QUIT":
            pygame.draw.line(s, col, (x-6, y-6), (x+6, y+6), 3)
            pygame.draw.line(s, col, (x+6, y-6), (x-6, y+6), 3)

    def _draw_showcase_fighter(self, t):
        """Draw only the player's selected character on the right side."""
        sw, sh = self.sw, self.sh
        anim_state = self._anim_states[self._anim_idx % len(self._anim_states)]

        # facing left so character looks into the menu
        sprite = get_sprite(self._char_id, facing=-1, state=anim_state)

        fighter_x      = sw - 190
        fighter_ground = sh - 95

        if sprite:
            target_h = int(sh * 0.58)
            ratio    = target_h / max(1, sprite.get_height())
            target_w = int(sprite.get_width() * ratio)
            big      = pygame.transform.smoothscale(sprite, (target_w, target_h))

            bob = math.sin(t * 2.0) * 5

            # Thin vertical aura beam behind character — uses char's own colour
            beam_w = max(30, target_w // 3)
            beam_h = target_h + 30
            beam   = pygame.Surface((beam_w, beam_h), pygame.SRCALPHA)
            for bi in range(beam_w // 2):
                a = max(0, int(40 * (1 - bi / (beam_w / 2))))
                pygame.draw.rect(beam, (*self._aura, a),
                                 (bi, 0, beam_w - bi * 2, beam_h))
            self.screen.blit(beam,
                             (fighter_x - beam_w // 2,
                              fighter_ground - beam_h + 10),
                             special_flags=pygame.BLEND_RGBA_ADD)

            # Small ellipse shadow on ground
            ped = pygame.Surface((target_w + 20, 18), pygame.SRCALPHA)
            pygame.draw.ellipse(ped, (0, 0, 0, 100), (0, 0, target_w + 20, 18))
            self.screen.blit(ped,
                             (fighter_x - (target_w + 20) // 2,
                              fighter_ground - 6))

            sx = fighter_x - target_w // 2
            sy = int(fighter_ground - target_h + bob)
            self.screen.blit(big, (sx, sy))

            # Name tag — just text, no card/panel
            draw_text(self.screen, self._char_name, 20,
                      (*self._aura[:3],),
                      fighter_x, fighter_ground + 6,
                      center=True, shadow=True)
        else:
            # Fallback silhouette
            _draw_menu_silhouette(self.screen, fighter_x, fighter_ground,
                                  t, anim_state, self._aura)
            draw_text(self.screen, self._char_name, 20,
                      (*self._aura[:3],),
                      fighter_x, fighter_ground + 6,
                      center=True, shadow=True)

    # ── Main draw ─────────────────────────────────────────────────────────────
    def draw(self):
        t  = self._t
        sw, sh = self.sw, self.sh

        # ── 1. Background (crossfading between 3 bgs) ───────────────────────
        cur_bg  = self._bgs[self._bg_idx]
        next_bg = self._bgs[(self._bg_idx + 1) % len(self._bgs)]
        if cur_bg:
            self.screen.blit(cur_bg, (0, 0))
        else:
            self.screen.fill((8, 6, 12))
        if self._bg_fading and next_bg:
            fade_surf = next_bg.copy()
            fade_surf.set_alpha(int(self._bg_fade * 255))
            self.screen.blit(fade_surf, (0, 0))

        # Heavy dark vignette — makes it feel cinematic, not garish
        vignette = pygame.Surface((sw, sh), pygame.SRCALPHA)
        # Bottom-up dark gradient
        for yi in range(sh):
            ratio = yi / sh
            a = int(ratio * 200)
            pygame.draw.line(vignette, (0, 0, 0, a), (0, yi), (sw, yi))
        # Left dark band (behind menus)
        for xi in range(sw // 2):
            ratio = 1 - xi / (sw // 2)
            a = int(ratio * 120)
            pygame.draw.line(vignette, (0, 0, 0, a), (xi, 0), (xi, sh))
        self.screen.blit(vignette, (0, 0))

        # ── 2. Falling ash/petal particles ────────────────────────────────────
        for p in self._particles:
            ps = pygame.Surface((p["size"] * 2, p["size"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(ps, (*p["color"], p["alpha"]),
                               (p["size"], p["size"]), p["size"])
            self.screen.blit(ps, (int(p["x"]), int(p["y"])))

        # ── 3. Logo ───────────────────────────────────────────────────────────
        logo_y = 28
        if self._logo:
            pulse = math.sin(t * 1.4) * 3
            lx = sw // 2 - self._logo.get_width() // 2
            # Subtle dark glow — not orange
            gw = self._logo.get_width() + 40
            gh = self._logo.get_height() + 20
            glow = pygame.Surface((gw, gh), pygame.SRCALPHA)
            ga   = int(30 + math.sin(t * 2) * 10)
            pygame.draw.ellipse(glow, (80, 20, 20, ga), (0, 0, gw, gh))
            self.screen.blit(glow, (lx - 20, logo_y - 10),
                             special_flags=pygame.BLEND_RGBA_ADD)
            self.screen.blit(self._logo, (lx, logo_y + int(pulse)))
        else:
            draw_text(self.screen, "SHADOW STRIKE", 90, (200, 20, 20),
                      sw // 2, logo_y + 50,
                      shadow=True, shadow_color=(0, 0, 0), center=True)

        # ── 4. Player info bar — drawn BEFORE fighter so sprite is on top ─────
        gid   = self.save.get("gamer_id", "WARRIOR")
        level = self.save.get("level", 1)
        coins = self.save.get("coins", 0)
        bar   = pygame.Surface((sw, 34), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 170))
        pygame.draw.line(bar, (80, 50, 15), (0, 33), (sw, 33), 1)
        self.screen.blit(bar, (0, 258))
        draw_text(self.screen,
                  f"{gid.upper()}    LV. {level}    COINS: {coins}",
                  20, (200, 160, 80), sw // 2, 265,
                  shadow=False, center=True)

        # ── 5. Showcase fighter — drawn AFTER info bar so it stands in front ──
        self._draw_showcase_fighter(t)

        # ── 6. Menu items ─────────────────────────────────────────────────────
        for i, opt in enumerate(self._options):
            rect    = self._opt_rect(i)
            is_sel  = (i == self._selected)
            pulse_y = int(math.sin(t * 5) * 2) if is_sel else 0

            bg = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            if is_sel:
                pygame.draw.rect(bg, (130, 10, 10, 220),
                                 (0, 0, rect.w, rect.h), border_radius=4)
                pygame.draw.rect(bg, GOLD,
                                 (0, 0, rect.w, rect.h), 2, border_radius=4)
            else:
                pygame.draw.rect(bg, (8, 5, 5, 180),
                                 (0, 0, rect.w, rect.h), border_radius=4)
                pygame.draw.rect(bg, (70, 45, 15),
                                 (0, 0, rect.w, rect.h), 1, border_radius=4)
            self.screen.blit(bg, (rect.x, rect.y + pulse_y))

            icon_x = rect.x + 14
            icon_y = rect.y + 18 + pulse_y
            icon_col = GOLD if is_sel else (180, 150, 100)
            self._draw_menu_icon(opt, icon_x, icon_y, icon_col)

            col = GOLD if is_sel else (210, 190, 150)
            draw_text(self.screen, opt, 34, col,
                      rect.x + 42, rect.y + 10 + pulse_y,
                      shadow=True, shadow_color=(0, 0, 0))

        # ── 7. Bottom hint ────────────────────────────────────────────────────
        draw_text(self.screen,
                  "W/S  NAVIGATE      ENTER  SELECT      F11  FULLSCREEN      ESC  QUIT",
                  16, (100, 75, 45), sw // 2, sh - 26,
                  shadow=False, center=True)
        draw_text(self.screen, "SHADOW STRIKE  v1.0",
                  14, (55, 38, 18), sw - 4, sh - 22, shadow=False)
