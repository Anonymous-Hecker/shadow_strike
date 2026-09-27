"""
Shadow Strike - Global Settings & Constants
RETRO FIGHTING GAME THEME — Dark dojo / arcade aesthetic
"""
import pygame

# ─── Display ──────────────────────────────────────────────────────────────────
SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 720
FPS           = 60
TITLE         = "SHADOW STRIKE"

# ─── Physics ──────────────────────────────────────────────────────────────────
GRAVITY        = 0.55
GROUND_Y       = 570
FIGHTER_WIDTH  = 80
FIGHTER_HEIGHT = 180

# ─── Combat ───────────────────────────────────────────────────────────────────
ROUND_TIME        = 99
MAX_ROUNDS        = 3
STAMINA_REGEN     = 0.25
STAMINA_COST_JUMP = 10

# ─── Economy ──────────────────────────────────────────────────────────────────
COINS_PER_COMBO = 3
COINS_PER_WIN   = 100
COINS_PERFECT   = 50

# ─── RETRO FIGHTING PALETTE ───────────────────────────────────────────────────
# Core colors — dark, gritty, cinematic
BLACK      = (0,   0,   0)
DARK_BG    = (8,   4,   4)       # near-black warm
PANEL_BG   = (12,  8,   8)
WHITE      = (255, 255, 255)
OFF_WHITE  = (230, 220, 200)     # aged parchment white

# Fighting game reds/golds
BLOOD_RED  = (180,  10,  10)
DARK_RED   = (100,   5,   5)
CRIMSON    = (200,  20,  30)
GOLD       = (220, 170,   0)
DARK_GOLD  = (140, 100,   0)
AMBER      = (255, 160,   0)
ORANGE     = (220,  90,   0)

# Accent / UI
STEEL_BLUE = ( 40,  80, 120)
ASH_GREY   = ( 60,  55,  55)
PANEL_EDGE = ( 80,  60,  40)     # weathered wood edge

# HP bar colors
HP_COLOR_P1   = (220,  30,  30)   # P1 = red
HP_COLOR_P2   = ( 30, 120, 220)   # P2 = blue
HP_BG         = ( 20,  10,  10)
HP_EMPTY      = ( 60,  20,  20)
STAMINA_COLOR = ( 40, 200, 120)

# Screen state colors
YELLOW = (255, 210,   0)
RED    = (220,  20,  20)
GREEN  = ( 30, 180,  50)
BLUE   = ( 30, 100, 220)
PURPLE = (120,  30, 200)
CYAN   = ( 40, 200, 200)
PINK   = (220,  60, 120)

# ─── Critical Traits ──────────────────────────────────────────────────────────
CRIT_FIRST_STRIKE  = "First Strike"
CRIT_HARD          = "Hard"
CRIT_AGGRESSIVE    = "Aggressive"
CRIT_TEMPERAMENTAL = "Temperamental"
CRIT_RAGE          = "Rage"

CRIT_COLORS = {
    CRIT_FIRST_STRIKE:  (255, 220,  60),
    CRIT_HARD:          (220,  60,  60),
    CRIT_AGGRESSIVE:    (255, 120,  20),
    CRIT_TEMPERAMENTAL: (200,  40, 200),
    CRIT_RAGE:          (255,  20,  20),
}

# ─── AI Difficulty Levels ─────────────────────────────────────────────────────
AI_PASSIVE    = 0
AI_DEFENSIVE  = 1
AI_BALANCED   = 2
AI_AGGRESSIVE = 3
AI_ELITE      = 4

AI_NAMES = {
    AI_PASSIVE:    "NOVICE",
    AI_DEFENSIVE:  "APPRENTICE",
    AI_BALANCED:   "WARRIOR",
    AI_AGGRESSIVE: "VETERAN",
    AI_ELITE:      "MASTER",
}

# ─── Game States ──────────────────────────────────────────────────────────────
STATE_MAIN_MENU   = "main_menu"
STATE_CHAR_SELECT = "char_select"
STATE_FIGHT       = "fight"
STATE_VICTORY     = "victory"
STATE_DOJO        = "dojo"
STATE_SHOP        = "shop"
STATE_SETTINGS    = "settings"
STATE_PROFILE     = "profile"

# ─── Character Classes ────────────────────────────────────────────────────────
CLASS_WARRIOR   = "Warrior"
CLASS_ROGUE     = "Rogue"
CLASS_MAGE      = "Mage"
CLASS_GUARDIAN  = "Guardian"
CLASS_SHADOW    = "Shadow"

CLASS_ORDER = [CLASS_WARRIOR, CLASS_ROGUE, CLASS_MAGE, CLASS_GUARDIAN, CLASS_SHADOW]

CLASS_COLORS = {
    CLASS_WARRIOR:  (180,  40,  40),
    CLASS_ROGUE:    (180, 120,  20),
    CLASS_MAGE:     ( 80,  40, 200),
    CLASS_GUARDIAN: ( 40, 100, 180),
    CLASS_SHADOW:   ( 60,  60,  60),
}

CLASS_ICONS = {
    CLASS_WARRIOR:  "W",
    CLASS_ROGUE:    "R",
    CLASS_MAGE:     "M",
    CLASS_GUARDIAN: "G",
    CLASS_SHADOW:   "S",
}

# ─── Weapons ──────────────────────────────────────────────────────────────────
WEAPONS = [
    {"id": "iron_blade",      "name": "Iron Blade",      "cost": 0,    "unlock_level": 1,
     "dmg_bonus": 0,  "speed_bonus": 0, "crit_bonus": 0, "lifesteal": 0,
     "color": (140, 140, 140), "perk": "Starter weapon — balanced & reliable",
     "pierce": False},
    {"id": "shadow_dagger",   "name": "Shadow Dagger",   "cost": 500,  "unlock_level": 2,
     "dmg_bonus": 3,  "speed_bonus": 1, "crit_bonus": 12, "lifesteal": 0,
     "color": ( 40,  40,  60), "perk": "+12% Critical Strike chance",
     "pierce": False},
    {"id": "flame_sword",     "name": "Flame Sword",     "cost": 1200, "unlock_level": 3,
     "dmg_bonus": 6,  "speed_bonus": 0, "crit_bonus": 5, "lifesteal": 0,
     "color": (220,  80,   0), "perk": "Burns enemies for 3s DoT",
     "pierce": False},
    {"id": "blood_katana",    "name": "Blood Katana",    "cost": 2200, "unlock_level": 5,
     "dmg_bonus": 8,  "speed_bonus": 2, "crit_bonus": 8, "lifesteal": 12,
     "color": (180,   0,  40), "perk": "12% Lifesteal on every hit",
     "pierce": False},
    {"id": "void_blade",      "name": "Void Blade",      "cost": 4000, "unlock_level": 7,
     "dmg_bonus": 12, "speed_bonus": 1, "crit_bonus": 15, "lifesteal": 8,
     "color": ( 80,   0, 180), "perk": "Pierces block — hits blocked enemies for 50%",
     "pierce": True},
    {"id": "dragon_spear",    "name": "Dragon Spear",    "cost": 6000, "unlock_level": 10,
     "dmg_bonus": 16, "speed_bonus": -1,"crit_bonus": 20, "lifesteal": 0,
     "color": (220, 140,   0), "perk": "+20% Crit & massive range boost",
     "pierce": False},
]

ARMORS = [
    {"id": "cloth_wrap",      "name": "Cloth Wraps",     "cost": 0,    "unlock_level": 1,
     "dmg_reduce": 0, "speed_bonus": 0, "dodge_bonus": 0, "reflect": 0,
     "color": (100,  80,  60), "perk": "Starter armor — no bonuses",
     "special": None},
    {"id": "leather_vest",    "name": "Leather Vest",    "cost": 400,  "unlock_level": 2,
     "dmg_reduce": 3, "speed_bonus": 1, "dodge_bonus": 5, "reflect": 0,
     "color": (100,  60,  30), "perk": "+5% Dodge chance, slight defence",
     "special": None},
    {"id": "shadow_cloak",    "name": "Shadow Cloak",    "cost": 1000, "unlock_level": 3,
     "dmg_reduce": 2, "speed_bonus": 2, "dodge_bonus": 15,"reflect": 0,
     "color": ( 20,  20,  40), "perk": "+15% Dodge — very fast & elusive",
     "special": None},
    {"id": "iron_mail",       "name": "Iron Mail",       "cost": 1800, "unlock_level": 4,
     "dmg_reduce": 8, "speed_bonus": -1,"dodge_bonus": 0, "reflect": 0,
     "color": ( 80,  90, 100), "perk": "High defence, reduces incoming damage",
     "special": None},
    {"id": "runic_robe",      "name": "Runic Robe",      "cost": 3000, "unlock_level": 6,
     "dmg_reduce": 4, "speed_bonus": 0, "dodge_bonus": 8, "reflect": 0,
     "color": ( 60,  20, 140), "perk": "Reduces magic damage by 30%",
     "special": "magic_up"},
    {"id": "titan_plate",     "name": "Titan Plate",     "cost": 5500, "unlock_level": 9,
     "dmg_reduce": 14,"speed_bonus": -2,"dodge_bonus": 0, "reflect": 15,
     "color": ( 50,  60,  80), "perk": "Reflects 15% damage back to attacker",
     "reflect": 15, "special": None},
]

# ─── Controls ─────────────────────────────────────────────────────────────────
DEFAULT_P1_KEYS = {
    "left":    pygame.K_a,
    "right":   pygame.K_d,
    "up":      pygame.K_w,
    "light":   pygame.K_j,
    "heavy":   pygame.K_k,
    "special": pygame.K_l,
    "super":   pygame.K_u,
    "block":   pygame.K_SEMICOLON,
    "dash":    pygame.K_f,       # Forward dash attack
    "counter": pygame.K_g,       # Counter / parry strike
    "slam":    pygame.K_h,       # Ground slam
    "sweep":   pygame.K_n,       # Sweep — disarms + stuns
}

DEFAULT_P2_KEYS = {
    "left":    pygame.K_LEFT,
    "right":   pygame.K_RIGHT,
    "up":      pygame.K_UP,
    "light":   pygame.K_KP1,
    "heavy":   pygame.K_KP2,
    "special": pygame.K_KP3,
    "super":   pygame.K_KP_PLUS,
    "block":   pygame.K_KP0,
    "dash":    pygame.K_KP4,
    "counter": pygame.K_KP5,
    "slam":    pygame.K_KP6,
    "sweep":   pygame.K_KP7,
}
