"""
Game — Main state machine orchestrating all screens
"""
import sys
import pygame
from settings import *
from core.save_manager import SaveManager
from core.audio_manager import AudioManager

from screens.main_menu import MainMenuScreen
from screens.character_select import CharacterSelectScreen
from screens.fight_screen import FightScreen
from screens.victory_screen import VictoryScreen
from screens.dojo_screen import DojoScreen
from screens.shop_screen import ShopScreen
from screens.settings_screen import SettingsScreen
from screens.profile_screen import ProfileScreen
from screens.skill_tree_screen import SkillTreeScreen


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption(TITLE)
        pygame.display.set_icon(self._make_icon())
        self.clock  = pygame.time.Clock()
        self.running = True
        self._fullscreen = False

        self.save  = SaveManager()
        self.audio = AudioManager()
        self.audio.set_sfx_volume(self.save.get("sfx_volume", 0.8))
        self.audio.set_music_volume(self.save.get("music_volume", 0.6))

        # Fight context (set before entering fight)
        self._fight_ctx = {}

        self._current_screen = None
        self._go_to_main_menu()

    def _make_icon(self):
        icon = pygame.Surface((32, 32), pygame.SRCALPHA)
        icon.fill((0, 0, 0, 0))
        pygame.draw.circle(icon, (140, 60, 255), (16, 16), 14)
        pygame.draw.circle(icon, (0, 0, 0), (16, 16), 10)
        pygame.draw.circle(icon, (200, 80, 255), (20, 13), 4)
        return icon

    def _go_to_main_menu(self):
        self.audio.stop_music()
        self._current_screen = MainMenuScreen(self.screen, self.audio, self.save)
        self._state = STATE_MAIN_MENU

    def _go_to_char_select(self):
        self._current_screen = CharacterSelectScreen(self.screen, self.audio, self.save)
        self._state = STATE_CHAR_SELECT

    def _go_to_fight(self, p1_char, p2_char_or_cpu, mode, ai_diff):
        self.audio.stop_music()
        self._current_screen = FightScreen(
            self.screen, self.audio, self.save,
            p1_char, p2_char_or_cpu, mode, ai_diff
        )
        self._state = STATE_FIGHT

    def _go_to_victory(self, winner, coins, combo, crits):
        self._current_screen = VictoryScreen(self.screen, self.audio, self.save,
                                              winner, coins, combo, crits)
        self._state = STATE_VICTORY

    def _go_to_dojo(self):
        self._current_screen = DojoScreen(self.screen, self.audio, self.save)
        self._state = STATE_DOJO

    def _go_to_shop(self):
        self._current_screen = ShopScreen(self.screen, self.audio, self.save)
        self._state = STATE_SHOP

    def _go_to_settings(self):
        self._current_screen = SettingsScreen(self.screen, self.audio, self.save)
        self._state = STATE_SETTINGS

    def _go_to_profile(self):
        self._current_screen = ProfileScreen(self.screen, self.audio, self.save)
        self._state = STATE_PROFILE

    def _go_to_skill_tree(self):
        self._current_screen = SkillTreeScreen(self.screen, self.audio, self.save)
        self._state = "skill_tree"

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)  # Cap delta to prevent spiral of death

            # Events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self._toggle_fullscreen()
                    continue
                if event.type == pygame.VIDEORESIZE:
                    # Window was resized — update screen ref and rebuild
                    self.screen = pygame.display.get_surface()
                    self._rebuild_current_screen()
                    continue
                self._current_screen.handle_event(event)

            # Update
            result = self._current_screen.update(dt)

            # Handle screen transitions
            self._handle_result(result)

            # Draw
            self._current_screen.draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _toggle_fullscreen(self):
        """Toggle fullscreen mode on F11."""
        self._fullscreen = not self._fullscreen
        if self._fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE
            )
        # Rebuild current screen with new surface
        self._rebuild_current_screen()

    def _rebuild_current_screen(self):
        """Recreate the current screen after a display mode change."""
        state = self._state
        if state == STATE_MAIN_MENU:
            self._go_to_main_menu()
        elif state == STATE_CHAR_SELECT:
            self._go_to_char_select()
        elif state == STATE_DOJO:
            self._go_to_dojo()
        elif state == STATE_SHOP:
            self._go_to_shop()
        elif state == STATE_SETTINGS:
            self._go_to_settings()
        elif state == STATE_PROFILE:
            self._go_to_profile()

    def _handle_result(self, result):
        if result is None:
            return

        state = self._state

        # ── Main Menu ─────────────────────────────────────────────────────────
        if state == STATE_MAIN_MENU:
            if result == "PLAY":
                self._go_to_char_select()
            elif result == "DOJO":
                self._go_to_dojo()
            elif result == "SKILLS":
                self._go_to_skill_tree()
            elif result in ("SHOP", "ARMORY"):
                self._go_to_shop()
            elif result == "PROFILE":
                self._go_to_profile()
            elif result == "SETTINGS":
                self._go_to_settings()
            elif result == "QUIT":
                self.running = False


        # ── Character Select ──────────────────────────────────────────────────
        elif state == STATE_CHAR_SELECT:
            if isinstance(result, tuple) and result[0] == "start_fight":
                _, p1_char, p2_char, mode, ai_diff = result
                # For 1P mode, pick a random opponent if none given
                if mode == "1p" and p2_char is None:
                    from characters.character_data import CHARACTERS
                    import random
                    p2_char = random.choice([c for c in CHARACTERS if c["id"] != p1_char["id"]])
                # Save favorite char
                self.save.set("favorite_char", p1_char["id"])
                self._go_to_fight(p1_char, p2_char, mode, ai_diff)
            elif result == "back":
                self._go_to_main_menu()

        # ── Fight ─────────────────────────────────────────────────────────────
        elif state == STATE_FIGHT:
            if isinstance(result, tuple) and result[0] == "victory":
                _, winner, coins, combo, crits = result
                self._go_to_victory(winner, coins, combo, crits)

        # ── Victory ───────────────────────────────────────────────────────────
        elif state == STATE_VICTORY:
            if result == "main_menu":
                self._go_to_main_menu()

        # ── Dojo ──────────────────────────────────────────────────────────────
        elif state == STATE_DOJO:
            if result == "back":
                self._go_to_main_menu()

        # ── Shop ──────────────────────────────────────────────────────────────
        elif state == STATE_SHOP:
            if result == "back":
                self._go_to_main_menu()

        # ── Settings ──────────────────────────────────────────────────────────
        elif state == STATE_SETTINGS:
            if result == "back":
                self._go_to_main_menu()

        # ── Profile ───────────────────────────────────────────────────────────
        elif state == STATE_PROFILE:
            if result == "back":
                self._go_to_main_menu()

        # ── Skill Tree ────────────────────────────────────────────────────────
        elif self._state == "skill_tree":
            if result == "back":
                self._go_to_main_menu()
