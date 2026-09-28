"""
Fighter Entity — Base class for all fighters (player and AI)
"""
import pygame
import math
import random
from settings import *
from characters.character_data import get_character


class Fighter:
    """Core fighter class. Extended by Player and AIFighter."""

    def __init__(self, char_id, player_num, x, y, weapon_data=None, armor_data=None):
        self.char_id   = char_id
        self.player_num = player_num
        self.char_data = get_character(char_id)

        # Apply gear stats
        self.weapon = weapon_data
        self.armor  = armor_data
        self._apply_gear_stats()

        # Position & physics
        self.rect = pygame.Rect(x - FIGHTER_WIDTH // 2, y - FIGHTER_HEIGHT, FIGHTER_WIDTH, FIGHTER_HEIGHT)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.facing = 1 if player_num == 1 else -1  # 1=right, -1=left

        # Stats
        self.max_hp      = self.char_data["stats"]["hp"]
        self.hp          = float(self.max_hp)
        self.max_stamina = self.char_data["stats"]["stamina"]
        self.stamina     = float(self.max_stamina)
        self.speed       = self.char_data["stats"]["speed"] + self.speed_bonus
        self.base_damage = self.char_data["stats"]["damage"] + self.dmg_bonus
        self.defense     = self.char_data["stats"]["defense"] + self.def_bonus
        self.jump_power  = self.char_data["stats"]["jump_power"]

        # State machine
        self.state        = "idle"       # idle/walk/jump/air/attack_light/attack_heavy/special/super/block/hurt/dead
        self.prev_state   = "idle"
        self.state_timer  = 0.0
        self.is_blocking  = False
        self.is_invincible= False
        self.invincible_timer = 0.0

        # Combat tracking
        self.combo_count      = 0
        self.last_hit_time    = 0.0
        self.crit_count       = 0
        self.consecutive_hits = 0   # for AGGRESSIVE trait
        self.first_hit_done   = False
        self.rage_active      = False
        self.rage_timer       = 0.0
        self.shield_hp        = 0   # for Scholar barrier

        # Status effects {name: time_remaining}
        self.status_effects = {}

        # Aura intensity (0-1, based on gear quality)
        self.aura_intensity = self._calc_aura_intensity()
        self.weapon_color   = self._get_weapon_color()

        # Animation
        self.anim_frame  = 0
        self.anim_timer  = 0.0

        # Attack cooldowns
        self.attack_cd   = 0.0
        self.special_cd  = 0.0
        self.super_cd    = 0.0

        # Round tracking
        self.rounds_won  = 0

        # Projectiles spawned this frame
        self.projectiles_to_spawn = []

        # Movement — acceleration-based for shuffle-step feel
        self.walk_accel = 0.35      # how fast we ramp up
        self.walk_max   = self.speed * 0.6  # walk is slower than sprint
        self.move_dir   = 0         # -1, 0, +1 from input

    def _apply_gear_stats(self):
        """Apply weapon + armor stat bonuses."""
        self.dmg_bonus   = 0
        self.speed_bonus = 0
        self.def_bonus   = 0
        self.dodge_bonus = 0
        self.lifesteal   = 0
        self.crit_bonus  = 0
        self.pierce      = False
        self.reflect_pct = 0

        if self.weapon:
            self.dmg_bonus   += self.weapon.get("dmg_bonus", 0)
            self.speed_bonus += self.weapon.get("speed_bonus", 0)
            self.crit_bonus  += self.weapon.get("crit_bonus", 0)
            self.lifesteal   += self.weapon.get("lifesteal", 0)
            self.pierce       = self.weapon.get("pierce", False)
        if self.armor:
            self.def_bonus   += self.armor.get("dmg_reduce", 0)
            self.speed_bonus += self.armor.get("speed_bonus", 0)
            self.dodge_bonus += self.armor.get("dodge_bonus", 0)
            self.reflect_pct += self.armor.get("reflect", 0)

    def _calc_aura_intensity(self):
        intensity = 0.15  # base
        if self.weapon and self.weapon.get("id") != "iron_blade":
            intensity += 0.25
        if self.armor and self.armor.get("id") != "cloth_wrap":
            intensity += 0.20
        if self.weapon:
            intensity += min(0.4, self.weapon.get("cost", 0) / 8000)
        return min(1.0, intensity)

    def _get_weapon_color(self):
        if self.weapon:
            return self.weapon.get("color")
        return None

    # ─── Update ───────────────────────────────────────────────────────────────

    def update(self, dt, arena_w):
        """Update physics, state timers, status effects. Override in subclasses."""
        self._update_physics(dt, arena_w)
        self._update_state_timer(dt)
        self._update_status_effects(dt)
        self._update_stamina(dt)
        self._update_attack_cooldowns(dt)
        self._update_critical_traits(dt)
        self._update_invincibility(dt)
        self.projectiles_to_spawn = []

    def _update_physics(self, dt, arena_w):
        # Gravity
        if not self.on_ground:
            self.vel_y += GRAVITY * dt * 60

        # Horizontal movement — acceleration-based shuffle
        if self.state == "walk" and self.on_ground:
            # Accelerate toward target speed
            target_vx = self.move_dir * self.walk_max
            diff = target_vx - self.vel_x
            self.vel_x += diff * self.walk_accel
        elif self.on_ground and self.state not in ("dash", "slam"):
            # Friction / deceleration when not walking
            self.vel_x *= 0.75
            if abs(self.vel_x) < 0.1:
                self.vel_x = 0

        self.rect.x += int(self.vel_x * dt * 60)
        self.rect.y += int(self.vel_y * dt * 60)

        # Ground check
        ground = GROUND_Y
        if self.rect.bottom >= ground:
            self.rect.bottom = ground
            self.vel_y = 0
            if not self.on_ground:
                self.on_ground = True
                if self.state in ("jump", "air"):
                    self.state = "idle"

        # Arena bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > arena_w:
            self.rect.right = arena_w

    def _update_state_timer(self, dt):
        if self.state_timer > 0:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state_timer = 0
                if self.state in ("attack_light","attack_heavy","special","super","hurt",
                                  "dash","counter","slam"):
                    self.state = "idle"
                    self.is_blocking = False

    def _update_status_effects(self, dt):
        for eff in list(self.status_effects.keys()):
            self.status_effects[eff] -= dt
            if self.status_effects[eff] <= 0:
                del self.status_effects[eff]
                continue
            # Apply DoT
            if eff == "burn":
                self._take_raw_damage(8 * dt)
            elif eff == "poison":
                self._take_raw_damage(5 * dt)
            elif eff == "bleed":
                self._take_raw_damage(6 * dt)

    def _update_stamina(self, dt):
        if self.state == "block":
            self.stamina = max(0, self.stamina - 5 * dt)
        elif self.state in ("idle","walk"):
            regen = STAMINA_REGEN * dt * 60
            self.stamina = min(self.max_stamina, self.stamina + regen)

    def _update_attack_cooldowns(self, dt):
        if self.attack_cd > 0:  self.attack_cd  = max(0, self.attack_cd  - dt)
        if self.special_cd > 0: self.special_cd = max(0, self.special_cd - dt)
        if self.super_cd > 0:   self.super_cd   = max(0, self.super_cd   - dt)
        if getattr(self, "sweep_cd", 0) > 0:
            self.sweep_cd = max(0.0, self.sweep_cd - dt)
        if getattr(self, "disarmed_timer", 0) > 0:
            self.disarmed_timer = max(0.0, self.disarmed_timer - dt)

    def _update_critical_traits(self, dt):
        trait = self.char_data.get("critical_trait")
        # Rage mode timer
        if self.rage_active:
            self.rage_timer -= dt
            if self.rage_timer <= 0:
                self.rage_active = False

    def _update_invincibility(self, dt):
        if self.invincible_timer > 0:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.is_invincible = False

    # ─── Combat ───────────────────────────────────────────────────────────────

    def attack(self, attack_type, enemies):
        """
        Execute an attack. attack_type: 'light', 'heavy', 'special', 'super', 'air'
        Returns (hit_enemies, damage_dealt, is_crit, particles_info)
        """
        moves = self.char_data["moves"]
        move  = moves.get(attack_type if attack_type != "air" else "air",
                          moves.get("light"))

        # Stamina check
        cost = move.get("stamina_cost", 10)
        if self.stamina < cost:
            return [], 0, False, []

        self.stamina -= cost

        # Set attack state
        state_map = {
            "light": "attack_light", "heavy": "attack_heavy",
            "special": "special",     "super": "super", "air": "attack_light",
            "dash": "dash",           "counter": "counter", "slam": "slam",
        }
        self.state = state_map.get(attack_type, "attack_light")
        duration   = move["startup"] / 60.0 + 0.2
        self.state_timer = duration

        # Cooldown
        if attack_type in ("light","heavy","air"):
            self.attack_cd  = 0.25 if attack_type == "light" else 0.5
        elif attack_type == "special":
            self.special_cd = 2.0
        elif attack_type == "super":
            self.super_cd   = 8.0

        # Handle buff/heal moves
        if move.get("type") in ("buff",):
            return self._apply_buff(move)

        # Handle projectile moves
        if move.get("projectile"):
            self._spawn_projectile(move)
            return [], 0, False, [("magic", self.rect.centerx, self.rect.centery)]

        # Melee hit detection
        hit_results = []
        total_dmg   = 0
        any_crit    = False
        particles   = []

        for enemy in enemies:
            if self._can_hit(enemy, move["range"]):
                result = self._apply_hit(enemy, move)
                if result:
                    dmg, is_crit, eff = result
                    hit_results.append(enemy)
                    total_dmg += dmg
                    if is_crit:
                        any_crit = True
                    fx_type = "magic" if move["type"] in ("magic","fire","poison") else "hit"
                    particles.append((fx_type, enemy.rect.centerx, enemy.rect.centery - 30))

        if hit_results:
            self.combo_count += 1
            self.last_hit_time = pygame.time.get_ticks() / 1000.0
        else:
            if pygame.time.get_ticks() / 1000.0 - self.last_hit_time > 1.5:
                self.combo_count = 0

        return hit_results, total_dmg, any_crit, particles

    def _can_hit(self, enemy, attack_range):
        """Check if enemy is within attack range and in the correct direction."""
        if enemy is self or enemy.state == "dead":
            return False
        dx = enemy.rect.centerx - self.rect.centerx
        if self.facing != (1 if dx > 0 else -1):
            return False
        dist = abs(dx)
        return dist < attack_range

    def _apply_hit(self, enemy, move):
        """Apply damage to enemy, considering their block, dodge, armor, and our traits."""
        # Block check
        if enemy.is_blocking and not self.pierce:
            block_dmg = max(2, int(move["damage"] * 0.15))
            enemy.stamina -= 15
            enemy._take_raw_damage(block_dmg)
            return (block_dmg, False, None)

        # Dodge check
        if enemy.dodge_bonus > 0:
            if random.randint(0, 100) < enemy.dodge_bonus:
                return None  # Dodged!

        # Calculate damage
        raw_dmg = move["damage"] + self.base_damage // 3

        # Apply critical traits (attacker)
        raw_dmg, is_crit = self._apply_crit_traits(raw_dmg, move)

        # Apply defense reduction
        def_reduce = enemy.defense * 0.4
        final_dmg  = max(1, raw_dmg - int(def_reduce))

        # Apply armor magic bonus
        if move.get("type") in ("magic","fire","poison") and enemy.armor:
            if enemy.armor.get("special") == "magic_up":
                final_dmg = int(final_dmg * 0.7)

        # Lifesteal
        if self.lifesteal > 0:
            heal = int(final_dmg * self.lifesteal / 100)
            self.hp = min(self.max_hp, self.hp + heal)

        # Reflect
        if enemy.reflect_pct > 0:
            reflect_dmg = int(final_dmg * enemy.reflect_pct / 100)
            self._take_raw_damage(reflect_dmg)

        # Apply damage to enemy
        enemy._take_hit(final_dmg, is_crit)

        # Apply move effects
        effect = move.get("effect")
        self._apply_move_effect(enemy, effect)

        return (final_dmg, is_crit, effect)

    def _apply_crit_traits(self, damage, move):
        trait    = self.char_data.get("critical_trait")
        is_crit  = False

        if trait == CRIT_FIRST_STRIKE and not self.first_hit_done:
            damage   = int(damage * 1.5)
            is_crit  = True
            self.first_hit_done = True
            self.crit_count += 1

        elif trait == CRIT_HARD:
            self.consecutive_hits += 1
            if self.consecutive_hits % 3 == 0:
                damage  = int(damage * 1.4)
                is_crit = True
                self.crit_count += 1

        elif trait == CRIT_AGGRESSIVE:
            bonus = min(0.5, self.consecutive_hits * 0.1)
            damage = int(damage * (1.0 + bonus))
            self.consecutive_hits += 1
            if bonus > 0.1:
                is_crit = True
                self.crit_count += 1

        elif trait == CRIT_TEMPERAMENTAL:
            if self.hp / self.max_hp < 0.4:
                damage = int(damage * 1.2)
                is_crit = True
                self.crit_count += 1

        elif trait == CRIT_RAGE and self.rage_active:
            damage  = int(damage * 2.0)
            is_crit = True
            # Lifesteal in rage
            self.hp = min(self.max_hp, self.hp + int(damage * 0.1))
            self.crit_count += 1

        # Weapon crit bonus
        if self.crit_bonus > 0 and not is_crit:
            if random.randint(0, 100) < self.crit_bonus:
                damage  = int(damage * 1.3)
                is_crit = True

        return damage, is_crit

    def _apply_move_effect(self, enemy, effect):
        if not effect:
            return
        if effect == "stun":
            enemy.state_timer = max(enemy.state_timer, 0.8)
            enemy.state = "hurt"
        elif effect == "knockdown":
            enemy.vel_y = -8          # upward impulse
            enemy.vel_x = self.facing * 6
            enemy.on_ground = False   # BUG FIX: must set False so gravity applies!
            enemy.state = "jump"      # visual jump/fly state
        elif effect == "knockback":
            enemy.vel_x = self.facing * 10
            if enemy.on_ground:
                enemy.vel_y = -3     # slight upward so they look pushed
                enemy.on_ground = False
        elif effect == "sweep":        # NEW: disarm + stun
            enemy.state_timer = max(enemy.state_timer, 1.5)  # 1.5s stun
            enemy.state = "hurt"
            if not hasattr(enemy, "disarmed_timer"):
                enemy.disarmed_timer = 0.0
            enemy.disarmed_timer = 5.0  # disarmed for 5 seconds
        elif effect == "burn_dot":
            enemy.status_effects["burn"] = 3.0
        elif effect == "poison_dot":
            enemy.status_effects["poison"] = 4.0
        elif effect == "bleed":
            enemy.status_effects["bleed"] = 3.5
        elif effect == "slow":
            enemy.status_effects["slow"] = 2.0
        elif effect == "stamina_drain":
            enemy.stamina = max(0, enemy.stamina - 40)
        elif effect == "hp_regen":
            self.hp = min(self.max_hp, self.hp + 20)
        elif effect == "physical_shield":
            self.shield_hp = 30

    def _apply_buff(self, move):
        effect = move.get("effect")
        self._apply_move_effect(self, effect)
        return [], 0, False, []

    def _spawn_projectile(self, move):
        self.projectiles_to_spawn.append({
            "x":     self.rect.centerx + self.facing * 40,
            "y":     self.rect.centery - 30,
            "vx":    self.facing * 8,
            "vy":    0,
            "damage": move["damage"] + self.base_damage // 4,
            "color": self.char_data.get("aura_color", (200, 100, 255)),
            "owner": self,
            "type":  move.get("type", "magic"),
            "effect": move.get("effect"),
        })

    def _take_hit(self, damage, is_crit):
        self._take_raw_damage(damage)
        if self.state not in ("dead", "super"):
            self.state = "hurt"
            self.state_timer = 0.3
        self.consecutive_hits = 0  # reset aggressive stacking on getting hit
        self.combo_count = 0

    def _take_raw_damage(self, damage):
        # Shield absorbs first
        if self.shield_hp > 0:
            absorbed = min(self.shield_hp, damage)
            self.shield_hp -= absorbed
            damage -= absorbed
        self.hp = max(0, self.hp - damage)
        if self.hp <= 0 and self.state != "dead":
            # Check rage activation
            trait = self.char_data.get("critical_trait")
            if trait == CRIT_RAGE and not self.rage_active and self.hp <= 1:
                self.hp = 1
                self.rage_active = True
                self.rage_timer  = 15.0
            else:
                self.state = "dead"
                self.state_timer = 999

    # ─── Movement ─────────────────────────────────────────────────────────────

    def move_left(self):
        if self.state in ("dead","super","hurt"):
            return
        self.move_dir = -1
        # NOTE: do NOT set self.facing here — facing is controlled by
        # face_opponent() in the fight loop, so the fighter always faces enemy
        if self.on_ground and self.state not in ("attack_light","attack_heavy","special","super","dash","counter","slam","block"):
            self.state = "walk"

    def move_right(self):
        if self.state in ("dead","super","hurt"):
            return
        self.move_dir = 1
        # NOTE: do NOT set self.facing here — see move_left comment
        if self.on_ground and self.state not in ("attack_light","attack_heavy","special","super","dash","counter","slam","block"):
            self.state = "walk"

    def stop_x(self):
        self.move_dir = 0
        if self.state == "walk" and self.on_ground:
            self.state = "idle"

    def jump(self):
        if not self.on_ground or self.state in ("dead","hurt"):
            return
        if self.stamina < STAMINA_COST_JUMP:
            return
        self.stamina -= STAMINA_COST_JUMP
        self.vel_y = self.jump_power
        self.on_ground = False
        self.state = "jump"

    def block(self):
        if self.state in ("dead","hurt","attack_light","attack_heavy","special","super"):
            return
        self.is_blocking = True
        self.state = "block"

    def release_block(self):
        self.is_blocking = False
        if self.state == "block":
            self.state = "idle"

    def set_idle(self):
        if self.state not in ("dead","hurt","attack_light","attack_heavy","special","super","jump","air","block"):
            self.state = "idle"

    def face_opponent(self, opponent):
        dx = opponent.rect.centerx - self.rect.centerx
        if dx != 0:
            self.facing = 1 if dx > 0 else -1

    @property
    def is_dead(self):
        return self.hp <= 0 and self.state == "dead"

    @property
    def hp_ratio(self):
        return max(0.0, self.hp / self.max_hp)

    @property
    def stamina_ratio(self):
        return max(0.0, self.stamina / self.max_stamina)

    def reset_for_round(self):
        self.hp      = float(self.max_hp)
        self.stamina = float(self.max_stamina)
        self.state   = "idle"
        self.state_timer = 0
        self.combo_count = 0
        self.consecutive_hits = 0
        self.first_hit_done   = False
        self.rage_active      = False
        self.rage_timer       = 0
        self.shield_hp        = 0
        self.status_effects   = {}
        self.vel_x = 0
        self.vel_y = 0
        self.is_blocking = False
        self.projectiles_to_spawn = []
