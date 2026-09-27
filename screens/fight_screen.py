"""
Fight Screen — Core battle arena: physics, combat, HUD, particles, projectiles
"""
import pygame
import math
import random
from settings import *
from entities.player import PlayerFighter
from entities.ai_fighter import AIFighter
from entities.projectile import Projectile
from renderer.background_renderer import BackgroundRenderer
from renderer.fighter_renderer import FighterRenderer
from ui.hud import HUD
from ui.particle_system import ParticleSystem
from core.asset_loader import get_font, draw_text as dt_text


class FightScreen:
    def __init__(self, screen, audio, save_manager,
                 p1_char, p2_char_or_cpu,
                 game_mode="2p", ai_difficulty=AI_BALANCED,
                 stage_index=None):
        self.screen  = screen
        self.audio   = audio
        self.save    = save_manager
        self.sw      = screen.get_width()
        self.sh      = screen.get_height()
        self.mode    = game_mode
        self._action = None
        self._t      = 0.0

        # Stage
        self.stage_index = stage_index if stage_index is not None else random.randint(0, 4)

        # Gear from save
        equipped_weapon_id = self.save.get("equipped_weapon", "iron_blade")
        equipped_armor_id  = self.save.get("equipped_armor",  "cloth_wrap")
        weapon_data = next((w for w in WEAPONS if w["id"] == equipped_weapon_id), WEAPONS[0])
        armor_data  = next((a for a in ARMORS  if a["id"] == equipped_armor_id),  ARMORS[0])

        # Spawn positions
        p1_x = self.sw // 4
        p2_x = self.sw * 3 // 4

        # Create P1
        p1_controls = self.save.get_controls(1)
        self.p1 = PlayerFighter(p1_char["id"], 1, p1_x, GROUND_Y, p1_controls, weapon_data, armor_data)

        # Create P2 (human or AI)
        if game_mode == "2p":
            p2_controls = self.save.get_controls(2)
            self.p2 = PlayerFighter(p2_char_or_cpu["id"], 2, p2_x, GROUND_Y, p2_controls)
        else:
            # CPU — no gear
            self.p2 = AIFighter(p2_char_or_cpu["id"], 2, p2_x, GROUND_Y, ai_difficulty)

        # Round state
        self.round_num    = 1
        self.max_rounds   = MAX_ROUNDS
        self.round_timer  = float(ROUND_TIME)
        self._round_phase = "start"   # "start", "fight", "end", "match_over"
        self._phase_timer = 0.0
        self._winner      = None
        self._round_winner = None

        # Match stats
        self._total_coins   = 0
        self._combo_count   = 0
        self._crit_count    = 0
        self._max_combo     = 0

        # Active projectiles
        self.projectiles = []

        # Systems
        self.bg_renderer  = BackgroundRenderer(self.sw, self.sh)
        self.bg_renderer.set_stage(self.stage_index)
        self.fighter_renderer = FighterRenderer()
        self.hud      = HUD(self.sw, self.sh)
        self.particles = ParticleSystem()

        # Critical label display
        self._crit_label = ""
        self._crit_color = WHITE
        self._crit_timer = 0.0

        # Pause
        self._paused = False

        self.font_big   = get_font(80)
        self.font_mid   = get_font(36)
        self.font_small = get_font(20)

        self._start_round()

    def _start_round(self):
        # Reset fighters to start positions
        p1_x = self.sw // 4
        p2_x = self.sw * 3 // 4
        self.p1.rect.center = (p1_x, GROUND_Y - FIGHTER_HEIGHT // 2)
        self.p2.rect.center = (p2_x, GROUND_Y - FIGHTER_HEIGHT // 2)
        self.p1.reset_for_round()
        self.p2.reset_for_round()
        self.p1.face_opponent(self.p2)
        self.p2.face_opponent(self.p1)
        self.round_timer  = float(ROUND_TIME)
        self._round_phase = "start"
        self._phase_timer = 0.0
        self.projectiles  = []
        self.particles._particles  = []
        self.particles._text_parts = []
        self.audio.play_sfx("round_start")
        self.hud.trigger_round_flash()

    def handle_event(self, event):
        if self._paused:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._paused = False
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._paused = True
            return
        if self._round_phase == "fight":
            self.p1.handle_event(event)
            if self.mode == "2p":
                self.p2.handle_event(event)

    def update(self, dt):
        if self._paused:
            return None
        self._t += dt
        real_dt = dt * self.particles.time_scale

        if self._round_phase == "start":
            self._phase_timer += dt
            if self._phase_timer >= 2.0:
                self._round_phase = "fight"
                self._phase_timer  = 0.0
            return None

        if self._round_phase == "fight":
            self._update_fight(real_dt, dt)

        elif self._round_phase == "end":
            self._phase_timer += dt
            if self._phase_timer >= 3.0:
                self._next_round_or_end()

        elif self._round_phase == "match_over":
            self._phase_timer += dt
            if self._phase_timer >= 0.5:
                return ("victory", self._winner, self._total_coins,
                        self._max_combo, self._crit_count)

        self.particles.update(dt)
        self.hud.update(dt, self.p1.hp_ratio, self.p2.hp_ratio,
                        self.p1.stamina_ratio, self.p2.stamina_ratio)
        if self._crit_timer > 0:
            self._crit_timer -= dt
            if self._crit_timer <= 0:
                self._crit_label = ""

        result = self._action
        self._action = None
        return result

    def _update_fight(self, real_dt, dt):
        # Timer
        self.round_timer -= dt
        if self.round_timer <= 0:
            self.round_timer = 0
            self._end_round_by_time()
            return

        # P1 input
        p1_results = self.p1.process_input(real_dt, [self.p2])
        self._process_hit_results(self.p1, p1_results, real_dt)

        # P2 input (human or AI)
        if self.mode == "2p":
            p2_results = self.p2.process_input(real_dt, [self.p1])
        else:
            p2_results = self.p2.process_ai(real_dt, [self.p1])
        self._process_hit_results(self.p2, p2_results, real_dt)

        # Update fighters
        self.p1.update(real_dt, self.sw)
        self.p2.update(real_dt, self.sw)

        # Spawn projectiles
        for proj_data in self.p1.projectiles_to_spawn:
            self.projectiles.append(Projectile(**proj_data))
            self.audio.play_sfx("magic")
        for proj_data in self.p2.projectiles_to_spawn:
            self.projectiles.append(Projectile(**proj_data))
            self.audio.play_sfx("magic")

        # Update projectiles
        for proj in self.projectiles:
            proj.update(real_dt, self.sw)
            target_map = {self.p1: self.p2, self.p2: self.p1}
            targets = [f for f in [self.p1, self.p2] if f is not proj.owner]
            hit = proj.check_hit(targets)
            if hit:
                hit._take_hit(proj.damage, False)
                if proj.effect:
                    proj._apply_move_effect = lambda e, eff: None  # already applied
                self.particles.emit_magic_explosion(int(proj.x), int(proj.y),
                                                    proj.color, 15)
                self.particles.show_damage(int(proj.x), int(proj.y), proj.damage, False)
                self.audio.play_sfx("magic_hit")
        self.projectiles = [p for p in self.projectiles if p.alive]

        # Idle state check
        self.p1.face_opponent(self.p2)
        self.p2.face_opponent(self.p1)

        # Check KO
        if self.p1.is_dead or self.p2.is_dead:
            self._end_round_by_ko()

    def _process_hit_results(self, attacker, results, dt):
        if not results["hit_enemies"]:
            return
        dmg      = results["damage"]
        is_crit  = results["is_crit"]
        parts    = results["particles"]

        # Play SFX
        if is_crit:
            self.audio.play_sfx("critical")
            self.particles.trigger_slow_mo(0.2)
            self._crit_label = attacker.char_data.get("critical_trait", "CRITICAL!")
            self._crit_color = CRIT_COLORS.get(self._crit_label, YELLOW)
            self._crit_timer = 1.5
            self._crit_count += 1
        else:
            self.audio.play_sfx("punch")

        # Emit particles
        for ptype, px, py in parts:
            if ptype == "hit":
                self.particles.emit_hit_sparks(px, py)
                self.particles.show_damage(px, py, dmg, is_crit)
            elif ptype == "magic":
                self.particles.emit_magic_explosion(px, py, attacker.char_data.get("aura_color", PURPLE))
                self.particles.show_damage(px, py, dmg, is_crit)

        # Combo tracking
        combo = attacker.combo_count
        if combo > self._max_combo:
            self._max_combo = combo
        if combo >= 3:
            self.audio.play_sfx(f"combo_{min(8, combo)}")
            self.particles.show_combo(attacker.rect.centerx, attacker.rect.top - 40, combo)

        # Earn coins
        coins = COINS_PER_COMBO * max(0, combo - 2) + (5 if is_crit else 0)
        if coins > 0:
            self._total_coins += coins
            self.particles.show_coin(attacker.rect.centerx, attacker.rect.top - 80, coins)
            self.audio.play_sfx("coin")

        self._combo_count += combo

    def _end_round_by_ko(self):
        if self.p1.is_dead:
            self._round_winner = self.p2
            self.p2.rounds_won += 1
        else:
            self._round_winner = self.p1
            self.p1.rounds_won += 1
        self._round_phase = "end"
        self._phase_timer = 0.0
        self.audio.play_sfx("ko")
        self.particles.emit_confetti(self._round_winner.rect.centerx, self._round_winner.rect.top)
        self.particles.show_text(self.sw // 2, self.sh // 2 - 60, "K.O.!", YELLOW, big=True)

    def _end_round_by_time(self):
        # Whoever has more HP wins
        if self.p1.hp > self.p2.hp:
            self._round_winner = self.p1
            self.p1.rounds_won += 1
        elif self.p2.hp > self.p1.hp:
            self._round_winner = self.p2
            self.p2.rounds_won += 1
        else:
            self._round_winner = None  # Draw
        self._round_phase = "end"
        self._phase_timer = 0.0
        self.audio.play_sfx("ko")
        if self._round_winner:
            self.particles.emit_confetti(self._round_winner.rect.centerx,
                                         self._round_winner.rect.top)
        self.particles.show_text(self.sw // 2, self.sh // 2 - 60, "TIME!", WHITE, big=True)

    def _next_round_or_end(self):
        rounds_needed = (self.max_rounds + 1) // 2
        if self.p1.rounds_won >= rounds_needed:
            self._winner = self.p1
            self._round_phase = "match_over"
            self._phase_timer = 0.0
            self._add_coins_and_record(won=(self._winner is self.p1))
        elif self.p2.rounds_won >= rounds_needed:
            self._winner = self.p2
            self._round_phase = "match_over"
            self._phase_timer = 0.0
            self._add_coins_and_record(won=(self._winner is self.p1))
        else:
            self.round_num += 1
            self._start_round()

    def _add_coins_and_record(self, won):
        self._total_coins += COINS_PER_WIN if won else 0
        # Perfect round bonus
        if won and self.p1.hp == self.p1.max_hp:
            self._total_coins += COINS_PERFECT
        self.save.add_coins(self._total_coins)
        self.audio.play_sfx("victory")

    def draw(self):
        dt_approx = 1 / 60
        self.bg_renderer.draw(self.screen, dt_approx)

        # Draw projectiles
        for proj in self.projectiles:
            proj.draw(self.screen)

        # Draw fighters
        aura1 = self.p1.aura_intensity
        aura2 = self.p2.aura_intensity
        self.fighter_renderer.draw(self.screen, self.p1, aura1)
        self.fighter_renderer.draw(self.screen, self.p2, aura2)

        # Particles
        self.particles.draw(self.screen)

        # HUD
        self.hud.draw(
            self.screen,
            self.p1.char_data["name"], self.p2.char_data["name"],
            self.p1.hp, self.p1.max_hp, self.p2.hp, self.p2.max_hp,
            self.p1.stamina, self.p1.max_stamina, self.p2.stamina, self.p2.max_stamina,
            self.round_timer, self.p1.rounds_won, self.p2.rounds_won, self.max_rounds,
            combo_count=self.p1.combo_count,
            p1_coins=self.save.get("coins", 0),
            gamer_id=self.save.get("gamer_id", ""),
            crit_label=self._crit_label,
            crit_color=self._crit_color,
        )

        # Screen flash
        self.particles.draw_screen_flash(self.screen, self.sw, self.sh)

        # Round start banner
        if self._round_phase == "start":
            self.hud.draw_round_start(self.screen, self.round_num, self._phase_timer)

        # Round end KO banner
        if self._round_phase == "end":
            self.hud.draw_ko(self.screen, "K.O.!", self._t)

        # Paused overlay
        if self._paused:
            self._draw_pause()

    def _draw_pause(self):
        ov = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 150))
        self.screen.blit(ov, (0, 0))
        dt_text(self.screen, "PAUSED", 80, WHITE,
                self.sw // 2, self.sh // 2 - 65, shadow=True, center=True)
        dt_text(self.screen, "ESC  TO  RESUME", 24, (160, 150, 120),
                self.sw // 2, self.sh // 2 + 30, shadow=True, center=True)
        dt_text(self.screen, "CONTROLS:  A/D MOVE   W JUMP   J LIGHT   K HEAVY   L SPECIAL   U SUPER",
                18, (100, 85, 55), self.sw // 2, self.sh // 2 + 70, shadow=False, center=True)
