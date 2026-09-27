"""
AI Fighter — CPU-controlled fighter with 5 difficulty personalities
"""
import random
import math
import pygame
from entities.fighter import Fighter
from settings import *


class AIFighter(Fighter):
    """
    AI behavior trees with 5 difficulty levels:
    0=Passive, 1=Defensive, 2=Balanced, 3=Aggressive, 4=Elite
    """

    # Personality parameters per difficulty
    PERSONALITIES = {
        AI_PASSIVE: {
            "attack_chance":  0.15,
            "block_chance":   0.10,
            "jump_chance":    0.05,
            "special_chance": 0.05,
            "reaction_time":  0.8,
            "combo_prob":     0.1,
            "chase_speed":    0.5,
            "aggro_distance": 200,
        },
        AI_DEFENSIVE: {
            "attack_chance":  0.30,
            "block_chance":   0.40,
            "jump_chance":    0.08,
            "special_chance": 0.15,
            "reaction_time":  0.5,
            "combo_prob":     0.2,
            "chase_speed":    0.7,
            "aggro_distance": 180,
        },
        AI_BALANCED: {
            "attack_chance":  0.50,
            "block_chance":   0.25,
            "jump_chance":    0.12,
            "special_chance": 0.25,
            "reaction_time":  0.3,
            "combo_prob":     0.4,
            "chase_speed":    0.9,
            "aggro_distance": 220,
        },
        AI_AGGRESSIVE: {
            "attack_chance":  0.75,
            "block_chance":   0.10,
            "jump_chance":    0.15,
            "special_chance": 0.35,
            "reaction_time":  0.15,
            "combo_prob":     0.6,
            "chase_speed":    1.1,
            "aggro_distance": 280,
        },
        AI_ELITE: {
            "attack_chance":  0.90,
            "block_chance":   0.35,
            "jump_chance":    0.20,
            "special_chance": 0.50,
            "reaction_time":  0.05,
            "combo_prob":     0.85,
            "chase_speed":    1.2,
            "aggro_distance": 320,
        },
    }

    def __init__(self, char_id, player_num, x, y, difficulty=AI_BALANCED, weapon_data=None, armor_data=None):
        super().__init__(char_id, player_num, x, y, weapon_data, armor_data)
        self.difficulty   = difficulty
        self.personality  = self.PERSONALITIES[difficulty]
        self._action_timer = 0.0
        self._current_action = "idle"
        self._combo_chain  = []
        self._combo_index  = 0
        self._think_timer  = 0.0

    def process_ai(self, dt, enemies):
        """Main AI decision loop. Called each frame."""
        results = {
            "hit_enemies": [],
            "damage": 0,
            "is_crit": False,
            "particles": [],
        }

        if self.state == "dead" or not enemies:
            return results

        target = enemies[0]
        p = self.personality

        self._action_timer -= dt
        self._think_timer  -= dt

        # Always face opponent
        self.face_opponent(target)

        dx   = target.rect.centerx - self.rect.centerx
        dist = abs(dx)

        # ── Reaction-delayed decision making ─────────────────────────────────
        if self._think_timer <= 0:
            self._think_timer = p["reaction_time"] + random.uniform(-0.05, 0.1)
            self._decide(target, dist, p)

        # ── Execute current action ────────────────────────────────────────────
        if self._current_action == "approach":
            if dx > 0:
                self.move_right()
            else:
                self.move_left()

        elif self._current_action == "retreat":
            if dx > 0:
                self.move_left()
            else:
                self.move_right()

        elif self._current_action == "block":
            self.block()

        elif self._current_action == "idle":
            self.stop_x()
            self.release_block()

        elif self._current_action == "jump":
            self.jump()
            self._current_action = "approach"

        elif self._current_action == "attack":
            self.stop_x()
            self.release_block()
            if self._action_timer <= 0 and self.state not in ("attack_light","attack_heavy","special","super","hurt"):
                atk = self._pick_attack(dist)
                hits, dmg, crit, parts = self.attack(atk, enemies)
                results["hit_enemies"] += hits
                results["damage"]      += dmg
                results["is_crit"]     = results["is_crit"] or crit
                results["particles"]   += parts
                self._action_timer = 0.4 + random.uniform(0, 0.3) / max(1, self.difficulty)

                # Combo continuation
                if random.random() < p["combo_prob"] and hits:
                    self._current_action = "attack"
                    self._action_timer   = 0.25

        return results

    def _decide(self, target, dist, p):
        """High-level behavior decision."""
        # If being comboed, block or retreat
        if target.combo_count >= 3 and random.random() < p["block_chance"] * 1.5:
            self._current_action = "block"
            self._action_timer   = 0.5
            return

        # If target is using super, jump away
        if target.state == "super" and random.random() < 0.7:
            self._current_action = "jump"
            return

        # If low HP and aggressive, maybe go rage mode (handled by trait)
        # Strategic logic
        if dist < p["aggro_distance"]:
            # In range — attack or block
            roll = random.random()
            if roll < p["attack_chance"]:
                self._current_action = "attack"
                self._action_timer   = random.uniform(0.1, 0.3)
            elif roll < p["attack_chance"] + p["block_chance"]:
                self._current_action = "block"
                self._action_timer   = random.uniform(0.3, 0.8)
            elif roll < p["attack_chance"] + p["block_chance"] + p["jump_chance"]:
                self._current_action = "jump"
            else:
                self._current_action = "approach"
        else:
            # Out of range — approach or circle
            if random.random() < p["chase_speed"]:
                self._current_action = "approach"
            else:
                self._current_action = "idle"

        # Elite AI: retreat when low HP
        if self.difficulty == AI_ELITE and self.hp_ratio < 0.25:
            if random.random() < 0.4:
                self._current_action = "retreat"
                self._action_timer   = 0.6

    def _pick_attack(self, dist):
        p = self.personality
        moves = self.char_data["moves"]

        # Can we use super?
        if self.super_cd <= 0 and self.stamina >= 60:
            if random.random() < p["special_chance"] * 0.5:
                return "super"

        # Special attack?
        if self.special_cd <= 0 and "special" in moves:
            if random.random() < p["special_chance"]:
                return "special"

        # Heavy vs light
        if random.random() < 0.35:
            return "heavy"
        return "light"

    def reset_for_round(self):
        super().reset_for_round()
        self._action_timer   = 0
        self._think_timer    = 0
        self._current_action = "idle"
