"""
Asset Loader — Loads fonts, backgrounds, and sprite sheets.

SPRITE SYSTEM (key design decisions):
- Uses set_colorkey on exact corner pixel, NOT threshold-based removal
  → Preserves dark-armored characters (warrior/ninja) which near-black backgrounds
  → Simple, reliable, no pixel destruction
- Scales to TARGET_SPRITE_W (fixed width), not height
  → Jump frames are taller but same width → no size explosion on jump
- Falls back to idle frame for empty/tiny cells
- Per-character bg type config (no guessing)
"""
import pygame
import os

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
FONT_PATH  = os.path.join(ASSETS_DIR, "ui", "turok.ttf")

_cache   = {}
_fonts   = {}
_sprites = {}   # (char_id, target_w) -> dict of state->pair


def _path(*parts):
    return os.path.join(ASSETS_DIR, *parts)


# ─── Fonts ────────────────────────────────────────────────────────────────────
def get_font(size):
    if size in _fonts:
        return _fonts[size]
    if os.path.exists(FONT_PATH):
        font = pygame.font.Font(FONT_PATH, size)
    else:
        try:
            font = pygame.font.SysFont("impact", size, bold=True)
        except Exception:
            font = pygame.font.Font(None, size)
    _fonts[size] = font
    return font


def draw_text(surface, text, size, color, x, y,
              shadow=True, shadow_color=(0, 0, 0), center=False,
              outline=False, outline_color=(0, 0, 0)):
    """Render crisp retro text with shadow or outline."""
    font = get_font(size)
    if outline:
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2),
                        (-1, -1), (1, -1), (-1, 1), (1, 1)]:
            os_ = font.render(text, True, outline_color)
            if center:
                surface.blit(os_, (x - os_.get_width() // 2 + dx, y + dy))
            else:
                surface.blit(os_, (x + dx, y + dy))
    elif shadow:
        ss = font.render(text, True, shadow_color)
        if center:
            surface.blit(ss, (x - ss.get_width() // 2 + 3, y + 3))
        else:
            surface.blit(ss, (x + 3, y + 3))
    ts = font.render(text, True, color)
    if center:
        surface.blit(ts, (x - ts.get_width() // 2, y))
    else:
        surface.blit(ts, (x, y))
    return ts


# ─── Images ───────────────────────────────────────────────────────────────────
def load_image(rel_path, scale=None):
    key = (rel_path, scale)
    if key in _cache:
        return _cache[key]
    full = _path(rel_path)
    if not os.path.exists(full):
        return None
    img = pygame.image.load(full).convert_alpha()
    if scale:
        img = pygame.transform.scale(img, scale)
    _cache[key] = img
    return img


def load_background(name, screen_w, screen_h):
    key = ("bg", name, screen_w, screen_h)
    if key in _cache:
        return _cache[key]
    full = _path("backgrounds", f"{name}.png")
    if not os.path.exists(full):
        surf = pygame.Surface((screen_w, screen_h))
        surf.fill((12, 5, 5))
        return surf
    img = pygame.image.load(full).convert()
    img = pygame.transform.scale(img, (screen_w, screen_h))
    _cache[key] = img
    return img


def load_logo(w, h):
    key = ("logo", w, h)
    if key in _cache:
        return _cache[key]
    full = _path("ui", "logo.png")
    if not os.path.exists(full):
        return None
    img = pygame.image.load(full).convert_alpha()
    img = pygame.transform.scale(img, (w, h))
    _cache[key] = img
    return img


# ─── Sprite Sheet Slicing ─────────────────────────────────────────────────────
# All generated sprites are 1024×1024 with 8 poses in a 4-col × 2-row grid.
# Row 1: idle, walk, light_attack, heavy_attack
# Row 2: jump, special, block, hurt

_QUAD_STATES_8 = {
    "idle":         (0, 0),
    "walk":         (1, 0),
    "attack_light": (2, 0),
    "attack_heavy": (3, 0),
    "jump":         (0, 1),
    "special":      (1, 1),
    "block":        (2, 1),
    "hurt":         (3, 1),
    "dead":         (3, 1),
    "air":          (0, 1),
    "dash":         (2, 0),
    "counter":      (1, 1),
    "slam":         (3, 0),
    "super":        (1, 1),
    "sweep":        (2, 1),
}

# Per-character background type.
# CRITICAL: warrior/ninja/berserker have very dark armor on black bg.
# Threshold-based removal would destroy the character. Use "black" = exact colorkey.
# White-bg sprites use "white" = exact colorkey on corner color.
_CHAR_BG_TYPE = {
    "warrior":   "black",
    "berserker": "white",
    "ninja":     "black",
    "shadow":    "white",
    "rogue":     "white",
    "mage":      "black",
    "phantom":   "black",
    "guardian":  "white",
    "monk":      "mixed",
    "samurai":   "black",
}

# Scale to width, not height — prevents jump-frame from appearing huge
# Jump frames are taller (stretched up) but same character width
TARGET_SPRITE_W = 160


def _detect_bg_type(surface):
    """Sample corners to detect if background is light or dark."""
    w, h = surface.get_size()
    corners = [
        surface.get_at((0, 0)),
        surface.get_at((w - 1, 0)),
        surface.get_at((0, h - 1)),
        surface.get_at((w - 1, h - 1)),
    ]
    avg = sum(c[0] + c[1] + c[2] for c in corners) / (3 * 4)
    return "white" if avg > 180 else "black"


def _remove_background(surface, bg_type, char_id=None):
    """Remove background using connected-component flood-fill from edges.

    Uses per-cell corner colors and tight tolerance.
    For problem characters, uses per-character tolerance overrides.
    """
    import numpy as np
    from scipy import ndimage

    w, h = surface.get_size()
    rgb   = pygame.surfarray.pixels3d(surface).copy()
    alpha = np.full((w, h), 255, dtype=np.uint8)

    # Per-character tolerance overrides (tested empirically)
    _CHAR_TOL = {
        "warrior": 30,    # dark armor on near-black bg, needs wider tolerance
        "shadow":  30,    # mixed bg with gray gradient
        "ninja":   22,    # dark but more contrast
        "samurai": 25,    # dark bg, medium armor
        "mage":    22,
        "phantom": 22,
    }

    def _
            alpha_arr[labeled == lbl] = 0

    # Get per-cell corner colors
    tl = rgb[0, 0].copy()
    tr = rgb[w-1, 0].copy()
    bl = rgb[0, h-1].copy()
    br = rgb[w-1, h-1].copy()

    if bg_type == "mixed" or char_id == "shadow":
        # Two passes for each unique corner color group
        tol = _CHAR_TOL.get(char_id, 22)
        _flood_remove(rgb, alpha, tl.astype(np.int16), tol)
        if np.abs(tl.astype(np.int16) - br.astype(np.int16)).max() > 30:
            _flood_remove(rgb, alpha, br.astype(np.int16), tol)
    else:
        corners = np.array([tl, tr, bl, br])
        bg_color = np.mean(corners, axis=0).astype(np.int16)
        tol = _CHAR_TOL.get(char_id, 22 if bg_type == "white" else 18)
        _flood_remove(rgb, alpha, bg_color, tol)

    result = pygame.Surface((w, h), pygame.SRCALPHA)
    px = pygame.surfarray.pixels3d(result)
    pa = pygame.surfarray.pixels_alpha(result)
    px[:] = rgb
    pa[:] = alpha
    del px, pa
    return result





def _auto_crop_alpha(surface):
    """Crop away fully transparent border pixels. Returns None if cell is empty."""
    try:
        import numpy as np
        alpha = pygame.surfarray.pixels_alpha(surface)  # (w, h)
        cols_mask = alpha.max(axis=1) > 10
        rows_mask = alpha.max(axis=0) > 10
        del alpha

        if not cols_mask.any() or not rows_mask.any():
            return None  # Empty cell

        col_indices = cols_mask.nonzero()[0]
        row_indices = rows_mask.nonzero()[0]
        min_x, max_x = int(col_indices[0]), int(col_indices[-1]) + 1
        min_y, max_y = int(row_indices[0]), int(row_indices[-1]) + 1

        pad = 2
        ww, hh = surface.get_size()
        min_x = max(0, min_x - pad)
        min_y = max(0, min_y - pad)
        max_x = min(ww, max_x + pad)
        max_y = min(hh, max_y + pad)

        cw, ch = max_x - min_x, max_y - min_y
        if cw < 8 or ch < 8:
            return None  # Too small → empty

        return surface.subsurface(pygame.Rect(min_x, min_y, cw, ch)).copy()
    except Exception:
        return surface


def load_character_sprite(char_id, target_w=TARGET_SPRITE_W):
    """
    Load and slice a character's 4×2 sprite sheet.
    Returns dict: {state_name: (base_surface, flipped_surface), ...}
    """
    cache_key = (char_id, target_w)
    if cache_key in _sprites:
        return _sprites[cache_key]

    

    raw = pygame.image.load(full).convert_alpha()
    iw, ih = raw.get_size()
    cols, rows = 4, 2
    cell_w = iw // cols
    cell_h = ih // rows

    bg_type = _CHAR_BG_TYPE.get(char_id, "auto")
    if bg_type == "auto":
        bg_type = _detect_bg_type(raw)

    cells = {}
    idle_pair = None

    for state, (cx, cy) in _QUAD_STATES_8.items():
        cell_key = (cx, cy)
        if cell_key in cells:
            continue

        rect = pygame.Rect(cx * cell_w, cy * cell_h, cell_w, cell_h)
        cell_surf = raw.subsurface(rect).copy()
        cell_surf = _remove_background(cell_surf, bg_type, char_id=char_id)
        cropped   = _auto_crop_alpha(cell_surf)

        if cropped is None:
            cells[cell_key] = None
            continue

        # Scale to fixed width, keep aspect ratio
        cw, ch = cropped.get_size()
        scale   = target_w / cw
        new_h   = max(1, int(ch * scale))
        scaled  = pygame.transform.smoothscale(cropped, (target_w, new_h))
        flipped = pygame.transform.flip(scaled, True, False)
        pair    = (scaled, flipped)
        cells[cell_key] = pair

        if cell_key == (0, 0):  # idle cell
            idle_pair = pair

    # Build state dict; use idle as fallback for empty cells
    result = {}
    for state, (cx, cy) in _QUAD_STATES_8.items():
        val = cells.get((cx, cy))
        result[state] = val if val is not None else idle_pair

    _sprites[cache_key] = result
    return result


def get_sprite(char_id, facing=1, state="idle"):
    """Get the correctly-oriented sprite for a character in a given state."""
    frames = load_character_sprite(char_id)
    if not frames:
        return None
    pair = frames.get(state)
    if pair is None:
        for fallback in ("idle", "walk", "attack_light"):
            pair = frames.get(fallback)
            if pair:
                break
    if pair is None:
        return None
    base, flipped = pair
    return base if facing >= 0 else flipped


def get_idle_sprite(char_id, target_w=None):
    """Get just the idle frame for display in menus/selectors."""
    tw = target_w or TARGET_SPRITE_W
    frames = load_character_sprite(char_id, tw)
    if not frames:
        return None
    pair = frames.get("idle")
    return pair[0] if pair else None


def clear_cache():
    _cache.clear()
    _sprites.clear()
    _fonts.clear()
