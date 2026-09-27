"""
Save Manager — Persistent save/load via JSON
"""
import json
import os
from settings import *

SAVE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "save_data.json")

DEFAULT_SAVE = {
    "gamer_id":       "Shadow Warrior",
    "coins":          0,
    "level":          1,
    "xp":             0,
    "xp_to_next":     100,
    "wins":           0,
    "losses":         0,
    "matches_played": 0,
    "owned_weapons":  ["iron_blade"],
    "owned_armors":   ["cloth_wrap"],
    "equipped_weapon":"iron_blade",
    "equipped_armor": "cloth_wrap",
    "p1_keys": {k: v for k, v in DEFAULT_P1_KEYS.items()},
    "p2_keys": {k: v for k, v in DEFAULT_P2_KEYS.items()},
    "sfx_volume":     0.8,
    "music_volume":   0.6,
    "favorite_char":  "general",
    "total_combos":   0,
    "total_crits":    0,
}

XP_TABLE = [100, 200, 350, 550, 800, 1100, 1500, 2000, 2600, 3300,
            4100, 5000, 6000, 7200, 8500, 10000, 11700, 13600, 15700, 99999]


class SaveManager:
    def __init__(self):
        self.data = {}
        self.load()

    def load(self):
        if os.path.exists(SAVE_PATH):
            try:
                with open(SAVE_PATH, "r") as f:
                    loaded = json.load(f)
                self.data = {**DEFAULT_SAVE, **loaded}
            except Exception:
                self.data = dict(DEFAULT_SAVE)
        else:
            self.data = dict(DEFAULT_SAVE)

    def save(self):
        try:
            with open(SAVE_PATH, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"[SaveManager] Error saving: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def add_coins(self, amount):
        self.data["coins"] = max(0, self.data["coins"] + amount)
        self.save()

    def spend_coins(self, amount):
        if self.data["coins"] >= amount:
            self.data["coins"] -= amount
            self.save()
            return True
        return False

    def add_xp(self, xp_amount):
        self.data["xp"] += xp_amount
        leveled_up = False
        while self.data["level"] <= 20:
            needed = XP_TABLE[min(self.data["level"] - 1, len(XP_TABLE) - 1)]
            if self.data["xp"] >= needed:
                self.data["xp"] -= needed
                self.data["level"] += 1
                self.data["xp_to_next"] = XP_TABLE[min(self.data["level"] - 1, len(XP_TABLE) - 1)]
                leveled_up = True
            else:
                break
        self.save()
        return leveled_up

    def unlock_item(self, item_id, item_type):
        key = f"owned_{item_type}s"
        if item_id not in self.data.get(key, []):
            self.data.setdefault(key, []).append(item_id)
            self.save()

    def equip_item(self, item_id, item_type):
        self.data[f"equipped_{item_type}"] = item_id
        self.save()

    def record_match(self, won, combo_count=0, crit_count=0):
        self.data["matches_played"] += 1
        if won:
            self.data["wins"] += 1
        else:
            self.data["losses"] += 1
        self.data["total_combos"] += combo_count
        self.data["total_crits"]  += crit_count
        # Award XP
        xp = 30 if won else 10
        xp += combo_count * 2 + crit_count * 3
        leveled_up = self.add_xp(xp)
        # Award coins
        coins = COINS_PER_WIN if won else 0
        coins += combo_count * 3 + crit_count * 5
        self.add_coins(coins)
        self.save()
        return leveled_up

    def set_key_binding(self, player, action, key_code):
        p_key = "p1_keys" if player == 1 else "p2_keys"
        self.data[p_key][action] = key_code
        self.save()

    def get_controls(self, player):
        p_key = "p1_keys" if player == 1 else "p2_keys"
        raw = self.data.get(p_key, {})
        default = DEFAULT_P1_KEYS if player == 1 else DEFAULT_P2_KEYS
        return {k: raw.get(k, default[k]) for k in default}
