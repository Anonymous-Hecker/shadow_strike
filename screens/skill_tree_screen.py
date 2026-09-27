"""
Skill Tree Screen — Unlock special moves using coins/XP as you level up.

Moves are organized in 4 tiers unlocked by player level.
Each node shows: icon, name, cost, description, lock status.
"""
import pygame
import math
from settings import *
from core.asset_loader import get_font, draw_text as dt, load_background


# ─── Skill Tree Data ──────────────────────────────────────────────────────────
SKILL_TIERS = [
    {
        "tier": 1, "label": "NOVICE", "req_level": 1,
        "skills": [
            {
                "id": "dash_strike",
                "name": "DASH STRIKE",
                "desc": "Lunge forward and slash",
                "cost_coins": 0,
                "key": "F",
                "color": (180, 130, 50),
                "icon": "dash",
            },
            {
                "id": "sweep",
                "name": "SWEEP",
                "desc": "Disarm & stun enemy 1.5s",
                "cost_coins": 200,
                "key": "N",
                "color": (50, 140, 200),
                "icon": "sweep",
            },
        ]
    },
    {
        "tier": 2, "label": "ADEPT", "req_level": 3,
        "skills": [
            {
                "id": "counter",
                "name": "COUNTER STRIKE",
                "desc": "Parry and punish instantly",
                "cost_coins": 500,
                "key": "G",
                "color": (180, 60, 60),
                "icon": "counter",
            },
            {
                "id": "slam",
                "name": "GROUND SLAM",
                "desc": "Powerful knockdown smash",
                "cost_coins": 500,
                "key": "H",
                "color": (140, 80, 200),
                "icon": "slam",
            },
        ]
    },
    {
        "tier": 3, "label": "MASTER", "req_level": 5,
        "skills": [
            {
                "id": "special",
                "name": "SPECIAL MOVE",
                "desc": "Unique character ability",
                "cost_coins": 1200,
                "key": "L",
                "color": (60, 180, 120),
                "icon": "special",
            },
            {
                "id": "ultra_hit",
                "name": "ULTRA HIT",
                "desc": "Super move consuming stamina",
                "cost_coins": 1500,
                "key": "U",
                "color": (220, 160, 30),
                "icon": "super",
            },
        ]
    },
    {
        "tier": 4, "label": "SHADOW", "req_level": 8,
        "skills": [
            {
                "id": "shadow_step",
                "name": "SHADOW STEP",
                "desc": "Teleport behind the enemy",
                "cost_coins": 3000,
                "key": "F+J",
                "color": (80, 60, 160),
                "icon": "shadow",
            },
            {
                "id": "rage_form",
                "name": "RAGE FORM",
                "desc": "Double damage for 5 seconds",
                "cost_coins": 4000,
                "key": "AUTO",
                "color": (200, 40, 40),
                "icon": "rage",
            },
        ]
    },
]


def _draw_skill_icon(surface, icon_type, cx, cy, size, color, unlocked):
    """Draw a procedural icon for each skill type."""
    c = color if unlocked else (60, 50, 40)
    bg = (20, 12, 5) if unlocked else (12, 8, 4)

    pygame.draw.circle(surface, bg, (cx, cy), size)
    pygame.draw.circle(surface, c, (cx, cy), size, 2)

    if icon_type == "dash":
        # Arrow right
        pts = [(cx - size//2, cy), (cx + size//3, cy),
               (cx + size//3, cy - size//3), (cx + size*2//3, cy),
               (cx + size//3, cy + size//3), (cx + size//3, cy)]
        pygame.draw.polygon(surface, c, pts)
    elif icon_type == "sweep":
        # Sweeping arc
        pygame.draw.arc(surface, c,
                        (cx - size*2//3, cy - size//4, size*4//3, size//2),
                        math.radians(10), math.radians(170), 3)
        pygame.draw.line(surface, c, (cx - size//2, cy + size//6),
                         (cx + size//2, cy + size//6), 3)
    elif icon_type == "counter":
        # Two opposing arrows
        pygame.draw.line(surface, c, (cx - size//2, cy - size//4),
                         (cx + size//2, cy - size//4), 2)
        pygame.draw.line(surface, c, (cx + size//2, cy + size//4),
                         (cx - size//2, cy + size//4), 2)
        # Arrow heads
        pygame.draw.polygon(surface, c, [
            (cx + size//2, cy - size//4),
            (cx + size//2 - 8, cy - size//4 - 6),
            (cx + size//2 - 8, cy - size//4 + 6)
        ])
    elif icon_type == "slam":
        # Downward fist
        pygame.draw.rect(surface, c, (cx - 10, cy - size//2, 20, size//2), 2)
        pts = [(cx - size//2, cy), (cx + size//2, cy),
               (cx + size//3, cy + size//2), (cx - size//3, cy + size//2)]
        pygame.draw.polygon(surface, c, pts, 2)
    elif icon_type == "special":
        # Star
        for i in range(5):
            a = math.radians(-90 + i * 72)
            a2 = math.radians(-90 + i * 72 + 36)
            ox = cx + math.cos(a) * size * 2 // 3
            oy = cy + math.sin(a) * size * 2 // 3
            ix = cx + math.cos(a2) * size // 3
            iy = cy + math.sin(a2) * size // 3
            a3 = math.radians(-90 + (i+1) * 72)
            nx = cx + math.cos(a3) * size * 2 // 3
            ny = cy + math.sin(a3) * size * 2 // 3
            pygame.draw.line(surface, c, (int(ox), int(oy)), (int(ix), int(iy)), 2)
            pygame.draw.line(surface, c, (int(ix), int(iy)), (int(nx), int(ny)), 2)
    elif icon_type == "super":
        # Lightning bolt
        pts = [(cx + 8, cy - size*2//3), (cx - 4, cy - 4),
               (cx + 8, cy - 4), (cx - 8, cy + size*2//3),
               (cx + 4, cy + 4), (cx - 8, cy + 4)]
        pygame.draw.polygon(surface, c, pts)
    elif icon_type == "shadow":
        # Ghost/shadow shape
        pygame.draw.circle(surface, c, (cx, cy - size//4), size//2, 2)
        for i in range(3):
            bx = cx - size//2 + i * size//2
            pygame.draw.arc(surface, c,
                            (bx, cy, size//2, size//3),
                            math.radians(0), math.radians(180), 2)
    elif icon_type == "rage":
        # Flame
        for i in range(3):
            h = size * (3 - i) // 3
            w = size * (2 - i) // 3 + 4
            pygame.draw.ellipse(surface, c,
                                (cx - w // 2, cy - h + size//4, w, h), 2)

    if not unlocked:
        # Lock icon
        pygame.draw.rect(surface, (120, 90, 60),
                         (cx - 8, cy - 4, 16, 14), border_radius=2)
        pygame.draw.arc(surface, (120, 90, 60),
                        (cx - 6, cy - 12, 12, 14),
                        math.radians(0), math.radians(180), 2)


class SkillTreeScreen:
    def __init__(self, screen, audio, save_manager):
        self.screen = screen
        self.audio  = audio
        self.save   = save_manager

        # Load player level and unlocked skills
        self.player_level = self.save.get("level", 1)
        self.coins        = self.save.get("coins", 0)
        self.unlocked     = set(self.save.get("unlocked_skills", ["dash_strike"]))

        self.selected_skill = None   # currently hovered/selected
        self.anim_t = 0.0
        self.msg = ""
        self.msg_timer = 0.0

        self._node_rects = {}   # skill_id -> pygame.Rect

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._action = "back"

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for skill_id, rect in self._node_rects.items():
                if rect.collidepoint(mx, my):
                    self._try_unlock(skill_id)
                    return

        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            self.selected_skill = None
            for skill_id, rect in self._node_rects.items():
                if rect.inflate(10, 10).collidepoint(mx, my):
                    self.selected_skill = skill_id
                    break

        return None

    def _try_unlock(self, skill_id):
        # Find the skill data
        skill = self._find_skill(skill_id)
        if not skill:
            return

        # Find tier
        tier_data = self._find_tier(skill_id)
        if not tier_data:
            return

        if self.player_level < tier_data["req_level"]:
            self.msg = f"NEED LEVEL {tier_data['req_level']}"
            self.msg_timer = 2.0
            return

        if skill_id in self.unlocked:
            self.msg = "ALREADY UNLOCKED"
            self.msg_timer = 1.5
            return

        if self.coins < skill["cost_coins"]:
            self.msg = f"NEED {skill['cost_coins']} COINS"
            self.msg_timer = 2.0
            return

        # Unlock!
        self.coins -= skill["cost_coins"]
        self.unlocked.add(skill_id)
        self.save.set("coins", self.coins)
        self.save.set("unlocked_skills", list(self.unlocked))
        self.save.save()
        self.msg = f"{skill['name']} UNLOCKED!"
        self.msg_timer = 2.5

    def _find_skill(self, skill_id):
        for tier in SKILL_TIERS:
            for s in tier["skills"]:
                if s["id"] == skill_id:
                    return s
        return None

    def _find_tier(self, skill_id):
        for tier in SKILL_TIERS:
            for s in tier["skills"]:
                if s["id"] == skill_id:
                    return tier
        return None

    def update(self, dt_time):
        self.anim_t += dt_time
        if self.msg_timer > 0:
            self.msg_timer -= dt_time
        res = getattr(self, "_action", None)
        self._action = None
        return res

    def draw(self):
        sw, sh = self.screen.get_width(), self.screen.get_height()

        # Background
        bg = load_background("dojo", sw, sh)
        if bg:
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill(DARK_BG)

        ov = pygame.Surface((sw, sh), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        self.screen.blit(ov, (0, 0))

        # Title
        dt(self.screen, "SKILL TREE", 52, GOLD, sw // 2, 18, center=True,
           shadow=True, shadow_color=(80, 40, 0))
        dt(self.screen, f"COINS: {self.coins}   LEVEL: {self.player_level}",
           24, OFF_WHITE, sw // 2, 70, center=True)
        dt(self.screen, "ESC: BACK   |   CLICK NODE TO UNLOCK",
           18, (100, 80, 55), sw // 2, 100, center=True)

        self._node_rects.clear()

        # Tooltip data to draw later
        tooltip_to_draw = None

        # Draw tiers from left to right
        tier_count = len(SKILL_TIERS)
        tier_w = sw // (tier_count + 1)
        tier_start_x = tier_w

        for ti, tier in enumerate(SKILL_TIERS):
            tx = tier_start_x + ti * tier_w
            tier_unlocked = self.player_level >= tier["req_level"]

            # Tier column header
            header_col = GOLD if tier_unlocked else (80, 60, 40)
            dt(self.screen, tier["label"], 22, header_col, tx, 130, center=True)
            dt(self.screen, f"LV {tier['req_level']}+", 17,
               (150, 110, 60) if tier_unlocked else (70, 50, 30),
               tx, 155, center=True)

            # Vertical connector line
            if ti < tier_count - 1:
                next_tx = tier_start_x + (ti + 1) * tier_w
                pygame.draw.line(self.screen,
                                 GOLD if tier_unlocked else (50, 40, 25),
                                 (tx + 35, sh // 2), (next_tx - 35, sh // 2), 2)

            # Draw skill nodes in this tier
            skill_count = len(tier["skills"])
            node_r = 38
            node_spacing = 160
            node_y_start = sh // 2 - (skill_count - 1) * node_spacing // 2

            for si, skill in enumerate(tier["skills"]):
                ny = node_y_start + si * node_spacing
                is_unlocked = skill["id"] in self.unlocked
                is_selected = skill["id"] == self.selected_skill
                available   = tier_unlocked and self.coins >= skill["cost_coins"]

                # Node circle
                pulse = int(8 * abs(math.sin(self.anim_t * 2))) if is_selected else 0

                # Background ring
                ring_col = GOLD if is_selected else ((80, 200, 80) if is_unlocked else (80, 60, 40))
                pygame.draw.circle(self.screen, (15, 8, 4), (tx, ny), node_r + pulse + 4)
                pygame.draw.circle(self.screen, ring_col, (tx, ny), node_r + pulse, 3)

                # Icon
                _draw_skill_icon(self.screen, skill["icon"], tx, ny,
                                 node_r - 6, skill["color"], is_unlocked)

                # Store rect for click detection
                self._node_rects[skill["id"]] = pygame.Rect(
                    tx - node_r - 4, ny - node_r - 4,
                    (node_r + 4) * 2, (node_r + 4) * 2
                )

                # Skill name below node
                name_col = GOLD if is_unlocked else (OFF_WHITE if available else (80, 65, 50))
                dt(self.screen, skill["name"], 17, name_col,
                   tx, ny + node_r + 8, center=True)

                # Cost or UNLOCKED
                if is_unlocked:
                    dt(self.screen, "UNLOCKED", 15, (80, 200, 80),
                       tx, ny + node_r + 32, center=True)
                else:
                    cost_col = (200, 180, 80) if available else (120, 90, 60)
                    dt(self.screen, f"{skill['cost_coins']} coins",
                       15, cost_col, tx, ny + node_r + 32, center=True)

                # Key binding
                dt(self.screen, f"KEY: {skill['key']}", 14,
                   (100, 80, 55), tx, ny + node_r + 52, center=True)

                # Collect detail tooltip data
                if is_selected:
                    tooltip_to_draw = (skill, tier, tx, ny, sw, sh)

        # Draw tooltip on top
        if tooltip_to_draw:
            self._draw_tooltip(*tooltip_to_draw)

        # Message
        if self.msg and self.msg_timer > 0:
            alpha = min(255, int(255 * min(1.0, self.msg_timer)))
            msg_surf = get_font(34).render(self.msg, True, GOLD)
            msg_surf.set_alpha(alpha)
            self.screen.blit(msg_surf,
                             (sw // 2 - msg_surf.get_width() // 2, sh - 80))

    def _draw_tooltip(self, skill, tier, sx, sy, sw, sh):
        """Draw a detail panel near the selected node."""
        pw, ph = 260, 140
        px = min(sw - pw - 10, sx + 50)
        py = max(10, sy - ph // 2)

        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((20, 10, 5, 230))
        self.screen.blit(panel, (px, py))
        pygame.draw.rect(self.screen, GOLD, (px, py, pw, ph), 2)

        dt(self.screen, skill["name"], 20, GOLD, px + 10, py + 8)
        dt(self.screen, skill["desc"], 16, OFF_WHITE, px + 10, py + 38)
        dt(self.screen, f"Cost: {skill['cost_coins']} coins", 16,
           (200, 180, 80), px + 10, py + 65)
        dt(self.screen, f"Req. Level: {tier['req_level']}", 16,
           (150, 120, 70), px + 10, py + 90)
        status = "UNLOCKED" if skill["id"] in self.unlocked else (
            "CLICK TO UNLOCK" if self.player_level >= tier["req_level"] else "LOCKED"
        )
        status_col = (80, 200, 80) if skill["id"] in self.unlocked else (
            CRIMSON if self.player_level < tier["req_level"] else GOLD
        )
        dt(self.screen, status, 18, status_col, px + 10, py + 114)
