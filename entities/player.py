"""
Player Fighter — Human-controlled fighter with rebindable keys
"""
from entities.fighter import Fighter
from settings import *


class PlayerFighter(Fighter):
    """Fighter controlled by a human player via keyboard."""

    def __init__(self, char_id, player_num, x, y, controls, weapon_data=None, armor_data=None):
        super().__init__(char_id, player_num, x, y, weapon_data, armor_data)
        self.controls = controls  # dict of action->key_code
        self._held = set()        # currently held keys
        self._pressed = set()     # keys pressed this frame

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self._pressed.add(event.key)
            self._held.add(event.key)
        elif event.type == pygame.KEYUP:
            self._held.discard(event.key)

    def process_input(self, dt, enemies):
        """Call once per frame after events are processed."""
        c = self.controls
        results = {
            "hit_enemies": [],
            "damage": 0,
            "is_crit": False,
            "particles": [],
        }

        if self.state in ("dead", "super", "hurt"):
            self._pressed.clear()
            return results

        # Movement
        left_held  = c["left"]  in self._held
        right_held = c["right"] in self._held

        if left_held and not right_held:
            self.move_left()
        elif right_held and not left_held:
            self.move_right()
        else:
            self.stop_x()

        # Jump
        if c["up"] in self._pressed:
            self.jump()

        # Block (hold)
        if c["block"] in self._held:
            if self.state not in ("attack_light","attack_heavy","special","super"):
                self.block()
        else:
            self.release_block()

        # Air attack
        if not self.on_ground and self.attack_cd <= 0:
            if c["light"] in self._pressed or c["heavy"] in self._pressed:
                hits, dmg, crit, parts = self.attack("air", enemies)
                results["hit_enemies"] += hits
                results["damage"]      += dmg
                results["is_crit"]     = results["is_crit"] or crit
                results["particles"]   += parts

        # Ground attacks
        if self.on_ground and self.state not in ("attack_light","attack_heavy","special","super","hurt","block"):
            if c["light"] in self._pressed and self.attack_cd <= 0:
                hits, dmg, crit, parts = self.attack("light", enemies)
                results["hit_enemies"] += hits
                results["damage"]      += dmg
                results["is_crit"]     = results["is_crit"] or crit
                results["particles"]   += parts

            elif c["heavy"] in self._pressed and self.attack_cd <= 0:
                hits, dmg, crit, parts = self.attack("heavy", enemies)
                results["hit_enemies"] += hits
                results["damage"]      += dmg
                results["is_crit"]     = results["is_crit"] or crit
                results["particles"]   += parts

            elif c["special"] in self._pressed and self.special_cd <= 0:
                hits, dmg, crit, parts = self.attack("special", enemies)
                results["hit_enemies"] += hits
                results["damage"]      += dmg
                results["is_crit"]     = results["is_crit"] or crit
                results["particles"]   += parts

            elif c["super"] in self._pressed and self.super_cd <= 0:
                if self.stamina >= 60:
                    hits, dmg, crit, parts = self.attack("super", enemies)
                    results["hit_enemies"] += hits
                    results["damage"]      += dmg
                    results["is_crit"]     = results["is_crit"] or crit
                    results["particles"]   += parts

            elif c.get("dash") in self._pressed and self.attack_cd <= 0:
                hits, dmg, crit, parts = self.attack("dash", enemies)
                # Dash lunge forward
                self.vel_x = self.facing * self.speed * 3
                results["hit_enemies"] += hits
                results["damage"]      += dmg
                results["is_crit"]     = results["is_crit"] or crit
                results["particles"]   += parts

            elif c.get("counter") in self._pressed and self.attack_cd <= 0:
                hits, dmg, crit, parts = self.attack("counter", enemies)
                results["hit_enemies"] += hits
                results["damage"]      += dmg
                results["is_crit"]     = results["is_crit"] or crit
                results["particles"]   += parts

            elif c.get("slam") in self._pressed and self.attack_cd <= 0:
                hits, dmg, crit, parts = self.attack("slam", enemies)
                results["hit_enemies"] += hits
                results["damage"]      += dmg
                results["is_crit"]     = results["is_crit"] or crit
                results["particles"]   += parts

            elif c.get("sweep") in self._pressed and getattr(self, "sweep_cd", 0) <= 0:
                hits, dmg, crit, parts = self.attack("sweep", enemies)
                if hits:
                    self.sweep_cd = 4.0  # 4-second cooldown
                results["hit_enemies"] += hits
                results["damage"]      += dmg
                results["is_crit"]     = results["is_crit"] or crit
                results["particles"]   += parts

        self._pressed.clear()
        return results
