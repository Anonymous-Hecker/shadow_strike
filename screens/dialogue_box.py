"""
DialogueBox - Champion Island style RPG dialogue box.

Features:
  - Dark rounded panel with an aura-coloured border and name tab
  - Typewriter letter-by-letter animation with a typewriter tick SFX
  - 1-2 choice buttons when a message has 'choices'
  - Blinking "click for next" hint
  - Click the box to skip typing / advance / pick a choice
  - Dynamic tag substitution: {level} {wins} {losses} {coins} {gamer_id}
"""
import pygame
import math
from core.asset_loader import get_font, draw_text as _dt


class DialogueBox:
    BOX_W         = 430          # panel width
    BOX_H         = 124          # text panel height (below the name tab)
    MARGIN_X      = 16
    MARGIN_BOTTOM = 50
    PAD           = 14
    TAB_H         = 28
    CHOICE_H      = 34
    TICK_INTERVAL = 0.032        # seconds per revealed character
    BLINK_SPEED   = 1.4          # blink cycles per second
    TICK_VOLUME   = 0.18

    def __init__(self, screen, audio, char_name, aura_color, messages, save_data):
        self.screen    = screen
        self.audio     = audio
        self.char_name = char_name.upper()
        self.aura      = tuple(aura_color)[:3]
        self.messages  = messages
        self.save_data = save_data

        self._t        = 0.0
        self._msg_idx  = 0
        self._load_message(0)

    # -- Internals ----------------------------------------------------------
    def _resolve(self, text):
        sd = self.save_data
        for tag, key, default in (("{level}", "level", 1), ("{wins}", "wins", 0),
                                  ("{losses}", "losses", 0), ("{coins}", "coins", 0),
                                  ("{gamer_id}", "gamer_id", "Warrior"),
                                  ("{matches_played}", "matches_played", 0)):
            text = text.replace(tag, str(sd.get(key, default)))
        return text

    def _msg(self):
        return self.messages[self._msg_idx % len(self.messages)]

    def _choices(self):
        return self._msg().get("choices", [])

    def _load_message(self, idx):
        self._msg_idx    = idx % len(self.messages)
        self._full_text  = self._resolve(self._msg()["text"])
        self._char_idx   = 0
        self._tick_timer = 0.0
        self._done       = False
        self._choice_idx = -1
        self._response   = None
        self._resp_chars = 0
        self._resp_timer = 0.0

    def _advance(self):
        self._load_message(self._msg_idx + 1)

    def _typing_response(self):
        return self._response is not None and self._resp_chars < len(self._response)

    def _tick_sound(self, ch):
        if ch not in (" ", "\n"):
            self.audio.play_sfx("typewriter_tick", volume=self.TICK_VOLUME)

    # -- Public API ---------------------------------------------------------
    def refresh_char(self, char_name, aura_color, messages, save_data):
        """Switch speaker (player picked another favourite character)."""
        self.char_name = char_name.upper()
        self.aura      = tuple(aura_color)[:3]
        self.messages  = messages
        self.save_data = save_data
        self._load_message(0)

    def handle_click(self, pos):
        """Returns True if the click was consumed by the dialogue box."""
        rect = self._full_rect()
        if not rect.collidepoint(pos):
            return False

        choices = self._choices()

        # 1. Response is being typed -> finish it instantly
        if self._typing_response():
            self._resp_chars = len(self._response)
            return True
        # 2. Response fully shown -> next message
        if self._response is not None:
            self._advance()
            return True
        # 3. Main text still typing -> finish it instantly
        if not self._done:
            self._char_idx = len(self._full_text)
            self._done = True
            return True
        # 4. Choices waiting -> only a click on a button counts
        if choices:
            for i, r in enumerate(self._choice_rects(rect, choices)):
                if r.collidepoint(pos):
                    self._choice_idx = i
                    self._response   = self._resolve(choices[i]["response"])
                    self._resp_chars = 0
                    self._resp_timer = 0.0
                    self.audio.play_sfx("confirm")
                    return True
            return True
        # 5. Plain message -> next
        self._advance()
        return True

    # -- Update -------------------------------------------------------------
    def update(self, dt):
        self._t += dt

        if self._typing_response():
            self._resp_timer += dt
            while self._resp_timer >= self.TICK_INTERVAL and self._resp_chars < len(self._response):
                self._resp_timer -= self.TICK_INTERVAL
                self._resp_chars += 1
                self._tick_sound(self._response[self._resp_chars - 1])
            return

        if not self._done:
            self._tick_timer += dt
            while self._tick_timer >= self.TICK_INTERVAL and self._char_idx < len(self._full_text):
                self._tick_timer -= self.TICK_INTERVAL
                self._char_idx += 1
                self._tick_sound(self._full_text[self._char_idx - 1])
            if self._char_idx >= len(self._full_text):
                self._done = True

    # -- Layout -------------------------------------------------------------
    def _full_rect(self):
        """Panel rect; grows upward when the message has choices."""
        sh = self.screen.get_height()
        extra = (self.CHOICE_H + self.PAD) if self._choices() else 0
        h = self.TAB_H + self.BOX_H + extra
        return pygame.Rect(self.MARGIN_X, sh - self.MARGIN_BOTTOM - h, self.BOX_W, h)

    def _choice_rects(self, rect, choices):
        n = len(choices)
        gap = 10
        w = (rect.width - self.PAD * 2 - gap * (n - 1)) // n
        y = rect.bottom - self.CHOICE_H - self.PAD
        return [pygame.Rect(rect.x + self.PAD + i * (w + gap), y, w, self.CHOICE_H)
                for i in range(n)]

    # -- Draw ---------------------------------------------------------------
    def draw(self):
        rect    = self._full_rect()
        choices = self._choices()
        r, g, b = self.aura

        # Drop shadow
        sh = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 90), sh.get_rect(), border_radius=16)
        self.screen.blit(sh, (rect.x - 4, rect.y + 4))

        # Panel
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, (8, 6, 14, 225), panel.get_rect(), border_radius=14)
        pygame.draw.rect(panel, (r, g, b, 200), panel.get_rect(), 2, border_radius=14)
        pygame.draw.line(panel, (255, 255, 255, 35), (14, 3), (rect.width - 14, 3), 1)
        self.screen.blit(panel, rect.topleft)

        # Name tab (sits on the top edge)
        font_tab = get_font(16)
        tab_w = max(90, font_tab.size(self.char_name)[0] + 28)
        tab = pygame.Surface((tab_w, self.TAB_H), pygame.SRCALPHA)
        pygame.draw.rect(tab, (r, g, b, 235), tab.get_rect(), border_radius=8)
        self.screen.blit(tab, (rect.x + self.PAD, rect.y - self.TAB_H // 2))
        _dt(self.screen, self.char_name, 16, (255, 255, 255),
            rect.x + self.PAD + tab_w // 2, rect.y - self.TAB_H // 2 + 5,
            center=True, shadow=True)

        # Text
        if self._response is not None:
            full, count = self._response, self._resp_chars
            colour = (255, 235, 170)       # responses a touch warmer
        else:
            full, count = self._full_text, self._char_idx
            colour = (230, 225, 240)
        self._draw_wrapped(full, rect.x + self.PAD, rect.y + self.TAB_H // 2 + 10,
                           rect.width - self.PAD * 2, colour, count)

        # Choice buttons
        if choices and self._done and self._response is None:
            mx, my = pygame.mouse.get_pos()
            for rc, ch in zip(self._choice_rects(rect, choices), choices):
                hover = rc.collidepoint(mx, my)
                btn = pygame.Surface(rc.size, pygame.SRCALPHA)
                if hover:
                    pygame.draw.rect(btn, (r, g, b, 210), btn.get_rect(), border_radius=8)
                    tc = (255, 255, 255)
                else:
                    pygame.draw.rect(btn, (20, 15, 30, 210), btn.get_rect(), border_radius=8)
                    pygame.draw.rect(btn, (r, g, b, 140), btn.get_rect(), 1, border_radius=8)
                    tc = (205, 195, 215)
                self.screen.blit(btn, rc.topleft)
                _dt(self.screen, ch["label"], 16, tc, rc.centerx, rc.y + 8,
                    center=True, shadow=False)

        # "click for next" hint + blinking arrow
        waiting_choice = bool(choices) and self._response is None
        ready = (self._done and self._response is None and not choices) or \
                (self._response is not None and not self._typing_response())
        if ready and not waiting_choice:
            a = int(140 + 115 * math.sin(self._t * self.BLINK_SPEED * 2 * math.pi))
            hint = get_font(13).render("click for next", True, (190, 180, 205))
            hint.set_alpha(max(0, min(255, a)))
            hx = rect.right - self.PAD - hint.get_width() - 14
            hy = rect.bottom - self.PAD - hint.get_height() + 2
            self.screen.blit(hint, (hx, hy))
            # little down-pointing triangle
            ax, ay = rect.right - self.PAD - 6, hy + hint.get_height() // 2
            tri = pygame.Surface((12, 10), pygame.SRCALPHA)
            pygame.draw.polygon(tri, (r, g, b, max(0, min(255, a))),
                                [(0, 1), (11, 1), (6, 9)])
            self.screen.blit(tri, (ax - 6, ay - 5 + int(math.sin(self._t * 6) * 1.5)))

    def _draw_wrapped(self, text, x, y, max_w, colour, count, line_h=22):
        """Wrap the FULL text first, then reveal `count` characters, so words
        never jump between lines while the typewriter is running."""
        font = get_font(16)
        lines, line = [], ""
        for word in text.split(" "):
            test = (line + " " + word) if line else word
            if font.size(test)[0] <= max_w or not line:
                line = test
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)

        left, cy = count, y
        for ln in lines:
            if left <= 0:
                break
            self.screen.blit(font.render(ln[:left], True, colour), (x, cy))
            left -= len(ln) + 1          # +1 for the space eaten by wrapping
            cy += line_h
