"""
Character Data — All 10 fighters mapped to their sprite IDs and stats
"""
from settings import *

# ── Character Definitions ─────────────────────────────────────────────────────
CHARACTERS = [
    # ── WARRIORS ──────────────────────────────────────────────────────────────
    {
        "id": "warrior", "name": "WARLORD", "class": CLASS_WARRIOR,
        "sprite_id": "warrior",
        "aura_color": (200, 30, 30),
        "critical_trait": CRIT_HARD,
        "unlock_level": 1,
        "lore": "A battle-hardened general who has never lost a duel.",
        "stats": {"hp": 180, "stamina": 120, "speed": 5, "damage": 20, "defense": 12, "jump_power": -12},
        "moves": {
            "light":   {"damage": 18, "range": 130, "startup": 8,  "stamina_cost": 8,  "type": "physical", "effect": None},
            "heavy":   {"damage": 32, "range": 140, "startup": 16, "stamina_cost": 16, "type": "physical", "effect": "knockdown"},
            "air":     {"damage": 20, "range": 120, "startup": 6,  "stamina_cost": 10, "type": "physical", "effect": None},
            "special": {"damage": 28, "range": 150, "startup": 12, "stamina_cost": 25, "type": "physical", "effect": "bleed", "projectile": False},
            "super":   {"damage": 60, "range": 160, "startup": 20, "stamina_cost": 60, "type": "physical", "effect": "knockdown"},
        },
    },
    {
        "id": "berserker", "name": "BERSERKER", "class": CLASS_WARRIOR,
        "sprite_id": "berserker",
        "aura_color": (255, 80, 0),
        "critical_trait": CRIT_RAGE,
        "unlock_level": 3,
        "lore": "When his HP drops below 30%, he enters an unstoppable rage.",
        "stats": {"hp": 200, "stamina": 100, "speed": 4, "damage": 24, "defense": 8,  "jump_power": -11},
        "moves": {
            "light":   {"damage": 22, "range": 130, "startup": 10, "stamina_cost": 10, "type": "physical", "effect": None},
            "heavy":   {"damage": 38, "range": 145, "startup": 18, "stamina_cost": 20, "type": "physical", "effect": "knockback"},
            "air":     {"damage": 24, "range": 120, "startup": 8,  "stamina_cost": 12, "type": "physical", "effect": "knockdown"},
            "special": {"damage": 34, "range": 155, "startup": 14, "stamina_cost": 28, "type": "physical", "effect": "stun"},
            "super":   {"damage": 75, "range": 170, "startup": 22, "stamina_cost": 60, "type": "physical", "effect": "knockdown"},
        },
    },

    # ── ROGUES ────────────────────────────────────────────────────────────────
    {
        "id": "rogue", "name": "SHADOWBLADE", "class": CLASS_ROGUE,
        "sprite_id": "rogue",
        "aura_color": (200, 150, 0),
        "critical_trait": CRIT_FIRST_STRIKE,
        "unlock_level": 1,
        "lore": "Strikes first, strikes hardest. Never gives an opponent a second chance.",
        "stats": {"hp": 140, "stamina": 160, "speed": 8, "damage": 16, "defense": 6, "jump_power": -13},
        "moves": {
            "light":   {"damage": 14, "range": 110, "startup": 5,  "stamina_cost": 6,  "type": "physical", "effect": None},
            "heavy":   {"damage": 24, "range": 120, "startup": 12, "stamina_cost": 14, "type": "physical", "effect": "bleed"},
            "air":     {"damage": 18, "range": 100, "startup": 4,  "stamina_cost": 8,  "type": "physical", "effect": None},
            "special": {"damage": 20, "range": 130, "startup": 8,  "stamina_cost": 20, "type": "physical", "effect": "stun", "projectile": False},
            "super":   {"damage": 50, "range": 140, "startup": 14, "stamina_cost": 55, "type": "physical", "effect": "bleed"},
        },
    },
    {
        "id": "ninja", "name": "KAGE", "class": CLASS_ROGUE,
        "sprite_id": "ninja",
        "aura_color": (40, 200, 80),
        "critical_trait": CRIT_AGGRESSIVE,
        "unlock_level": 4,
        "lore": "Each hit builds momentum. The longer the combo, the deadlier he becomes.",
        "stats": {"hp": 130, "stamina": 180, "speed": 9, "damage": 14, "defense": 5, "jump_power": -14},
        "moves": {
            "light":   {"damage": 12, "range": 105, "startup": 4,  "stamina_cost": 5,  "type": "physical", "effect": None},
            "heavy":   {"damage": 20, "range": 115, "startup": 10, "stamina_cost": 12, "type": "physical", "effect": "knockback"},
            "air":     {"damage": 16, "range": 100, "startup": 3,  "stamina_cost": 7,  "type": "physical", "effect": None},
            "special": {"damage": 18, "range": 200, "startup": 6,  "stamina_cost": 18, "type": "physical", "effect": None, "projectile": True},
            "super":   {"damage": 45, "range": 130, "startup": 12, "stamina_cost": 50, "type": "physical", "effect": "stun"},
        },
    },

    # ── MAGES ─────────────────────────────────────────────────────────────────
    {
        "id": "mage", "name": "VOID MAGE", "class": CLASS_MAGE,
        "sprite_id": "mage",
        "aura_color": (120, 40, 220),
        "critical_trait": CRIT_TEMPERAMENTAL,
        "unlock_level": 1,
        "lore": "When cornered and low on HP, desperation fuels devastating power.",
        "stats": {"hp": 120, "stamina": 200, "speed": 5, "damage": 22, "defense": 4, "jump_power": -12},
        "moves": {
            "light":   {"damage": 16, "range": 110, "startup": 7,  "stamina_cost": 7,  "type": "magic",    "effect": None},
            "heavy":   {"damage": 28, "range": 120, "startup": 14, "stamina_cost": 16, "type": "magic",    "effect": "slow"},
            "air":     {"damage": 20, "range": 115, "startup": 6,  "stamina_cost": 10, "type": "magic",    "effect": None},
            "special": {"damage": 35, "range": 320, "startup": 16, "stamina_cost": 30, "type": "magic",    "effect": "slow", "projectile": True},
            "super":   {"damage": 70, "range": 180, "startup": 24, "stamina_cost": 60, "type": "magic",    "effect": "stun"},
        },
    },
    {
        "id": "phantom", "name": "WRAITH", "class": CLASS_MAGE,
        "sprite_id": "phantom",
        "aura_color": (220, 60, 180),
        "critical_trait": CRIT_FIRST_STRIKE,
        "unlock_level": 6,
        "lore": "A ghost-like fighter who phases between dimensions to land devastating strikes.",
        "stats": {"hp": 110, "stamina": 180, "speed": 6, "damage": 26, "defense": 3, "jump_power": -13},
        "moves": {
            "light":   {"damage": 18, "range": 115, "startup": 6,  "stamina_cost": 8,  "type": "magic",    "effect": None},
            "heavy":   {"damage": 32, "range": 130, "startup": 14, "stamina_cost": 18, "type": "magic",    "effect": "stamina_drain"},
            "air":     {"damage": 22, "range": 110, "startup": 5,  "stamina_cost": 10, "type": "magic",    "effect": None},
            "special": {"damage": 30, "range": 280, "startup": 12, "stamina_cost": 25, "type": "magic",    "effect": "burn_dot", "projectile": True},
            "super":   {"damage": 65, "range": 170, "startup": 20, "stamina_cost": 55, "type": "magic",    "effect": "knockdown"},
        },
    },

    # ── GUARDIANS ─────────────────────────────────────────────────────────────
    {
        "id": "guardian", "name": "IRONCLAD", "class": CLASS_GUARDIAN,
        "sprite_id": "guardian",
        "aura_color": (40, 120, 220),
        "critical_trait": CRIT_HARD,
        "unlock_level": 1,
        "lore": "A towering fortress of steel. Every third strike is guaranteed to shatter.",
        "stats": {"hp": 220, "stamina": 140, "speed": 3, "damage": 18, "defense": 20, "jump_power": -10},
        "moves": {
            "light":   {"damage": 16, "range": 135, "startup": 12, "stamina_cost": 10, "type": "physical", "effect": None},
            "heavy":   {"damage": 30, "range": 150, "startup": 20, "stamina_cost": 22, "type": "physical", "effect": "stun"},
            "air":     {"damage": 18, "range": 120, "startup": 10, "stamina_cost": 12, "type": "physical", "effect": "knockdown"},
            "special": {"damage": 25, "range": 145, "startup": 16, "stamina_cost": 28, "type": "physical", "effect": "physical_shield"},
            "super":   {"damage": 55, "range": 160, "startup": 25, "stamina_cost": 60, "type": "physical", "effect": "knockdown"},
        },
    },
    {
        "id": "monk", "name": "IRON MONK", "class": CLASS_GUARDIAN,
        "sprite_id": "monk",
        "aura_color": (40, 210, 200),
        "critical_trait": CRIT_AGGRESSIVE,
        "unlock_level": 5,
        "lore": "Thirty years of discipline forged into iron fists and unbreakable will.",
        "stats": {"hp": 170, "stamina": 160, "speed": 6, "damage": 17, "defense": 15, "jump_power": -12},
        "moves": {
            "light":   {"damage": 15, "range": 120, "startup": 7,  "stamina_cost": 7,  "type": "physical", "effect": None},
            "heavy":   {"damage": 26, "range": 135, "startup": 15, "stamina_cost": 16, "type": "physical", "effect": "knockback"},
            "air":     {"damage": 19, "range": 115, "startup": 6,  "stamina_cost": 9,  "type": "physical", "effect": None},
            "special": {"damage": 22, "range": 140, "startup": 10, "stamina_cost": 22, "type": "physical", "effect": "hp_regen"},
            "super":   {"damage": 52, "range": 150, "startup": 18, "stamina_cost": 55, "type": "physical", "effect": "stun"},
        },
    },

    # ── SHADOWS ───────────────────────────────────────────────────────────────
    {
        "id": "shadow", "name": "THE SHADOW", "class": CLASS_SHADOW,
        "sprite_id": "shadow",
        "aura_color": (100, 100, 120),
        "critical_trait": CRIT_FIRST_STRIKE,
        "unlock_level": 1,
        "lore": "No one knows its true form. It strikes once, perfectly, then vanishes.",
        "stats": {"hp": 150, "stamina": 150, "speed": 7, "damage": 20, "defense": 8, "jump_power": -13},
        "moves": {
            "light":   {"damage": 17, "range": 120, "startup": 5,  "stamina_cost": 6,  "type": "physical", "effect": None},
            "heavy":   {"damage": 28, "range": 130, "startup": 12, "stamina_cost": 15, "type": "physical", "effect": "stun"},
            "air":     {"damage": 20, "range": 115, "startup": 4,  "stamina_cost": 8,  "type": "physical", "effect": None},
            "special": {"damage": 24, "range": 260, "startup": 8,  "stamina_cost": 22, "type": "physical", "effect": None, "projectile": True},
            "super":   {"damage": 58, "range": 150, "startup": 16, "stamina_cost": 55, "type": "physical", "effect": "knockdown"},
        },
    },
    {
        "id": "samurai", "name": "ONI BLADE", "class": CLASS_SHADOW,
        "sprite_id": "samurai",
        "aura_color": (220, 160, 0),
        "critical_trait": CRIT_TEMPERAMENTAL,
        "unlock_level": 7,
        "lore": "A cursed samurai whose blade grows stronger as his blood is spilled.",
        "stats": {"hp": 155, "stamina": 140, "speed": 7, "damage": 23, "defense": 10, "jump_power": -12},
        "moves": {
            "light":   {"damage": 20, "range": 135, "startup": 6,  "stamina_cost": 7,  "type": "physical", "effect": None},
            "heavy":   {"damage": 34, "range": 150, "startup": 14, "stamina_cost": 18, "type": "physical", "effect": "bleed"},
            "air":     {"damage": 22, "range": 130, "startup": 5,  "stamina_cost": 9,  "type": "physical", "effect": None},
            "special": {"damage": 30, "range": 155, "startup": 10, "stamina_cost": 24, "type": "physical", "effect": "bleed", "projectile": False},
            "super":   {"damage": 68, "range": 165, "startup": 18, "stamina_cost": 58, "type": "physical", "effect": "knockdown"},
            "dash":    {"damage": 26, "range": 200, "startup": 6,  "stamina_cost": 20, "type": "physical", "effect": None,        "is_dash": True},
            "counter": {"damage": 40, "range": 140, "startup": 4,  "stamina_cost": 30, "type": "physical", "effect": "stun",     "is_counter": True},
            "slam":    {"damage": 44, "range": 135, "startup": 16, "stamina_cost": 28, "type": "physical", "effect": "knockdown"},
        },
    },
]

# ── Add dash/counter/slam to every character that doesn't have them ────────────
_EXTRA_MOVES_TEMPLATE = {
    "warrior":   {
        "dash":    {"damage": 24, "range": 190, "startup": 7,  "stamina_cost": 20, "type": "physical", "effect": None,       "is_dash": True},
        "counter": {"damage": 36, "range": 135, "startup": 4,  "stamina_cost": 28, "type": "physical", "effect": "knockback","is_counter": True},
        "slam":    {"damage": 38, "range": 130, "startup": 14, "stamina_cost": 25, "type": "physical", "effect": "knockdown"},
        "sweep":   {"damage": 18, "range": 120, "startup": 8,  "stamina_cost": 20, "type": "physical", "effect": "sweep"},
    },
    "berserker": {
        "dash":    {"damage": 30, "range": 210, "startup": 6,  "stamina_cost": 22, "type": "physical", "effect": None,       "is_dash": True},
        "counter": {"damage": 44, "range": 140, "startup": 5,  "stamina_cost": 32, "type": "physical", "effect": "stun",    "is_counter": True},
        "slam":    {"damage": 48, "range": 140, "startup": 18, "stamina_cost": 28, "type": "physical", "effect": "knockdown"},
        "sweep":   {"damage": 22, "range": 130, "startup": 10, "stamina_cost": 24, "type": "physical", "effect": "sweep"},
    },
    "rogue": {
        "dash":    {"damage": 18, "range": 220, "startup": 4,  "stamina_cost": 14, "type": "physical", "effect": "bleed",    "is_dash": True},
        "counter": {"damage": 28, "range": 115, "startup": 3,  "stamina_cost": 22, "type": "physical", "effect": "bleed",   "is_counter": True},
        "slam":    {"damage": 24, "range": 110, "startup": 10, "stamina_cost": 18, "type": "physical", "effect": "stun"},
        "sweep":   {"damage": 16, "range": 125, "startup": 6,  "stamina_cost": 16, "type": "physical", "effect": "sweep"},
    },
    "ninja": {
        "dash":    {"damage": 16, "range": 240, "startup": 3,  "stamina_cost": 12, "type": "physical", "effect": None,       "is_dash": True},
        "counter": {"damage": 24, "range": 110, "startup": 2,  "stamina_cost": 18, "type": "physical", "effect": "stun",    "is_counter": True},
        "slam":    {"damage": 20, "range": 105, "startup": 8,  "stamina_cost": 14, "type": "physical", "effect": "knockback"},
        "sweep":   {"damage": 14, "range": 130, "startup": 5,  "stamina_cost": 14, "type": "physical", "effect": "sweep"},
    },
    "mage": {
        "dash":    {"damage": 20, "range": 180, "startup": 8,  "stamina_cost": 18, "type": "magic",    "effect": "slow",     "is_dash": True},
        "counter": {"damage": 32, "range": 120, "startup": 5,  "stamina_cost": 26, "type": "magic",    "effect": "stun",    "is_counter": True},
        "slam":    {"damage": 36, "range": 125, "startup": 14, "stamina_cost": 24, "type": "magic",    "effect": "slow"},
        "sweep":   {"damage": 20, "range": 115, "startup": 9,  "stamina_cost": 22, "type": "magic",    "effect": "sweep"},
    },
    "phantom": {
        "dash":    {"damage": 22, "range": 200, "startup": 6,  "stamina_cost": 16, "type": "magic",    "effect": None,       "is_dash": True},
        "counter": {"damage": 38, "range": 125, "startup": 4,  "stamina_cost": 28, "type": "magic",    "effect": "stamina_drain","is_counter": True},
        "slam":    {"damage": 34, "range": 120, "startup": 12, "stamina_cost": 22, "type": "magic",    "effect": "burn_dot"},
        "sweep":   {"damage": 18, "range": 120, "startup": 7,  "stamina_cost": 18, "type": "magic",    "effect": "sweep"},
    },
    "guardian": {
        "dash":    {"damage": 26, "range": 175, "startup": 10, "stamina_cost": 22, "type": "physical", "effect": "stun",     "is_dash": True},
        "counter": {"damage": 40, "range": 145, "startup": 6,  "stamina_cost": 32, "type": "physical", "effect": "knockdown","is_counter": True},
        "slam":    {"damage": 42, "range": 150, "startup": 20, "stamina_cost": 30, "type": "physical", "effect": "knockdown"},
        "sweep":   {"damage": 24, "range": 140, "startup": 11, "stamina_cost": 26, "type": "physical", "effect": "sweep"},
    },
    "monk": {
        "dash":    {"damage": 20, "range": 190, "startup": 7,  "stamina_cost": 18, "type": "physical", "effect": None,       "is_dash": True},
        "counter": {"damage": 34, "range": 130, "startup": 4,  "stamina_cost": 26, "type": "physical", "effect": "stun",    "is_counter": True},
        "slam":    {"damage": 30, "range": 130, "startup": 12, "stamina_cost": 22, "type": "physical", "effect": "knockback"},
        "sweep":   {"damage": 18, "range": 130, "startup": 7,  "stamina_cost": 18, "type": "physical", "effect": "sweep"},
    },
    "shadow": {
        "dash":    {"damage": 22, "range": 230, "startup": 5,  "stamina_cost": 16, "type": "physical", "effect": None,       "is_dash": True},
        "counter": {"damage": 34, "range": 125, "startup": 3,  "stamina_cost": 24, "type": "physical", "effect": "stun",    "is_counter": True},
        "slam":    {"damage": 30, "range": 120, "startup": 10, "stamina_cost": 20, "type": "physical", "effect": "knockdown"},
        "sweep":   {"damage": 16, "range": 128, "startup": 6,  "stamina_cost": 16, "type": "physical", "effect": "sweep"},
    },
    "samurai": {
        "dash":    {"damage": 26, "range": 200, "startup": 6,  "stamina_cost": 18, "type": "physical", "effect": None,       "is_dash": True},
        "counter": {"damage": 40, "range": 130, "startup": 4,  "stamina_cost": 28, "type": "physical", "effect": "knockback","is_counter": True},
        "slam":    {"damage": 44, "range": 135, "startup": 14, "stamina_cost": 26, "type": "physical", "effect": "knockdown"},
        "sweep":   {"damage": 22, "range": 125, "startup": 8,  "stamina_cost": 20, "type": "physical", "effect": "sweep"},
    },
}
for _c in CHARACTERS:
    if _c["id"] in _EXTRA_MOVES_TEMPLATE:
        for move_key, move_data in _EXTRA_MOVES_TEMPLATE[_c["id"]].items():
            if move_key not in _c["moves"]:
                _c["moves"][move_key] = move_data

# ── Lookups ───────────────────────────────────────────────────────────────────
_by_id    = {c["id"]: c for c in CHARACTERS}
_by_class = {cls: [c for c in CHARACTERS if c["class"] == cls] for cls in CLASS_ORDER}

def get_character(char_id):
    return _by_id.get(char_id, CHARACTERS[0])

def get_characters_by_class(cls):
    return _by_class.get(cls, [])
