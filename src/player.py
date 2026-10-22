"""Jogador: movimentação, pulo, pulo duplo, dash e ataques.

Regras de prioridade (documentadas também no README):
- Só um golpe por vez. Clique durante outro golpe fica no buffer por
  Combat.ATTACK_BUFFER s e sai assim que o golpe atual termina.
- Dash cancela golpe em preparação ou recuperação. Durante a fase ativa o
  dash fica no buffer e sai logo que ela termina.
- Golpes não começam durante o dash (ficam no buffer).
- Pulo cancela o dash (se houver pulo disponível).
- Pulo é permitido durante golpes; a direção do golpe fica travada.
"""

import copy
import math

import pygame

from .combat import Attack
from .config import (Colors, Combat, Game, Dash as D, Economy as EC, Effects as FX, Energy as EN,
                     Physics as PH, Player as P, Progression as PR)
from . import sprites
from .physics import Body, is_supported, move_and_collide, standing_only_on_oneway
from .skins import SKINS, frame_for, state_of
from .progress import Progress


def approach(value, target, delta):
    if value < target:
        return min(value + delta, target)
    return max(value - delta, target)


def _derive(spec, damage, reach):
    out = copy.copy(spec)
    out.damage = damage
    out.hit_w = round(spec.hit_w * reach)
    out.hit_h = round(spec.hit_h * (1 + (reach - 1) * 0.5))
    return out


class Player(Body):
    def __init__(self, x, y, progress=None):
        super().__init__(x - P.WIDTH / 2, y - P.HEIGHT, P.WIDTH, P.HEIGHT)
        self.progress = progress if progress is not None else Progress()
        self.hp = 0
        self.recompute_stats()
        self.reset_state()

    @property
    def abilities(self):
        return self.progress.abilities

    def recompute_stats(self):
        """Recalcula atributos a partir do progresso (arma, amuletos, fragmentos)."""
        pr = self.progress
        self.max_hp = pr.max_hp
        lvl = pr.weapon_level
        strong = 1.5 if pr.equipped("forca") else 1.0
        reach = 1.3 if pr.equipped("lamina") else 1.0
        self.quick_spec = _derive(Combat.QUICK, round((Combat.QUICK.damage + lvl * PR.QUICK_DAMAGE_PER_LEVEL) * strong), reach)
        self.heavy_spec = _derive(Combat.HEAVY, round((Combat.HEAVY.damage + lvl * PR.HEAVY_DAMAGE_PER_LEVEL) * strong), reach)
        wind = pr.equipped("vento")
        self.dash_speed = D.SPEED * (1.2 if wind else 1.0)
        self.dash_cooldown_time = D.COOLDOWN * (0.6 if wind else 1.0)
        self.heal_time = EN.HEAL_TIME * (0.6 if pr.equipped("foco") else 1.0)
        self.energy_mult = 1.5 if pr.equipped("coletor") else 1.0
        self.magnet = EC.CHARM_MAGNET if pr.equipped("ima") else EC.PICKUP_MAGNET
        self.hp = min(self.hp, self.max_hp)

    # ------------------------------------------------------------------
    def reset_state(self):
        """Zera tudo que não é posição. Usado no nascimento e no reaparecimento."""
        self.vx = self.vy = 0.0
        self.facing = 1
        self.hp = self.max_hp
        self.energy = 0.0
        self.heal_timer = 0.0
        self.heal_fx_timer = 0.0
        self.alive = True
        self.on_ground = False
        self.was_on_ground = False
        self.coyote = 0.0
        self.jump_buffer = 0.0
        self.jumps_used = 0
        self.jumping = False          # subida causada por pulo (pode ser cortada)
        self.jump_cut_done = False
        self.jump_time = 0.0
        self.dash_time = 0.0
        self.dash_cooldown = 0.0
        self.dash_dir = 1
        self.dash_buffer = 0.0
        self.air_dashes_used = 0
        self.ghost_timer = 0.0
        self.attack = None
        self.attack_buffer = None     # (spec, tempo restante)
        self.invuln = 0.0
        self.hurt_lock = 0.0
        self.hurt_flash = 0.0
        self.scale_x = self.scale_y = 1.0
        self.charge_fx_timer = 0.0
        self.landing_impact = 0.0
        self.drop_timer = 0.0
        self.anim_state = "idle"
        self.anim_time = 0.0
        self.land_timer = 0.0

    def place(self, foot_x, foot_y):
        self.x = foot_x - self.w / 2
        self.y = foot_y - self.h
        self.vx = self.vy = 0.0

    # ------------------------------------------------------------------
    @property
    def dashing(self):
        return self.dash_time > 0

    @property
    def invulnerable(self):
        return self.invuln > 0 or (D.INVULNERABLE and self.dashing) or not self.alive

    @property
    def can_air_jump(self):
        return "double_jump" in self.abilities and self.jumps_used < P.MAX_JUMPS

    @property
    def dash_ready(self):
        return ("dash" in self.abilities and self.dash_cooldown <= 0
                and (self.on_ground or self.air_dashes_used < D.AIR_DASHES))

    # ------------------------------------------------------------------
    def update(self, dt, inp, room, ctx):
        if not self.alive:
            self.anim_time += dt
            return
        self._tick_timers(dt)
        self._read_buffers(inp)

        move_x = inp.axis_x() if self.hurt_lock <= 0 else 0

        # --- dash ---
        if self.dash_buffer > 0 and self._can_start_dash():
            self._start_dash(move_x, ctx)

        # --- pulo (pode cancelar dash) ---
        if self.jump_buffer > 0 and self.hurt_lock <= 0:
            self._try_jump(ctx)

        # --- ataques ---
        if self.attack_buffer and self._can_start_attack():
            self._start_attack(self.attack_buffer[0], ctx, inp)

        # --- descer da plataforma de mão única (S) ---
        if (inp.was_pressed("down") and self.on_ground and not self.dashing and self.attack is None
                and standing_only_on_oneway(self, room)):
            self.drop_timer = P.DROP_THROUGH_TIME
            self.on_ground = False
            self.coyote = 0.0
            self.y += 1

        # --- cura (segurar F parado no chão) ---
        if inp.is_held("heal") and self._can_heal():
            move_x = 0
            self._heal_step(dt, ctx)
        else:
            self.heal_timer = 0.0

        # --- corte do pulo variável ---
        # (respeita um tempo mínimo para um toque rápido ainda gerar um pulinho útil)
        if self.jumping:
            self.jump_time += dt
            if (not inp.is_held("jump") and self.vy < 0 and not self.jump_cut_done
                    and self.jump_time >= P.MIN_JUMP_HOLD):
                self.vy *= P.JUMP_CUT_MULT
                self.jump_cut_done = True

        # --- velocidade ---
        if self.dashing:
            self.vx = self.dash_dir * self.dash_speed
            self.vy = 0.0
            self.ghost_timer -= dt
            if self.ghost_timer <= 0:
                self.ghost_timer = D.GHOST_INTERVAL
                self._dash_ghost(ctx)
        else:
            self._horizontal(dt, move_x)
            self._gravity(dt, inp)

        if self.attack is not None and not self.dashing:
            self._attack_motion()

        # --- facing ---
        if move_x and self.attack is None and not self.dashing:
            self.facing = move_x

        # --- movimento e colisão ---
        self.was_on_ground = self.on_ground
        impact_vy = self.vy
        dy = self.vy * dt
        move_and_collide(self, self.vx * dt, dy, room, oob_solid=False,
                         ignore_oneway=self.drop_timer > 0,
                         corner_correction=PH.CORNER_CORRECTION if self.vy < 0 else 0,
                         step_up=PH.STEP_UP)
        if dy == 0 and not self.on_ground:
            self.on_ground = is_supported(self, room)

        if self.hit_left or self.hit_right:
            if self.dashing:
                self._end_dash(keep_speed=False)
            self.vx = 0.0
        if self.hit_ceiling and self.vy < 0:
            self.vy = 0.0
            self.jumping = False

        if self.on_ground:
            if not self.was_on_ground:
                self._on_land(impact_vy, ctx)
            self.vy = 0.0
            self.coyote = P.COYOTE_TIME
            self.jumps_used = 0
            self.air_dashes_used = 0
            self.jumping = False

        # perdeu o coyote sem pular: o pulo "do chão" foi gasto
        if not self.on_ground and self.coyote <= 0 and self.jumps_used == 0:
            self.jumps_used = 1

        self._update_visuals(dt, ctx)

    # ------------------------------------------------------------------
    def _tick_timers(self, dt):
        self.drop_timer = max(0.0, self.drop_timer - dt)
        if not self.on_ground:
            self.coyote = max(0.0, self.coyote - dt)
        self.jump_buffer = max(0.0, self.jump_buffer - dt)
        self.dash_buffer = max(0.0, self.dash_buffer - dt)
        self.dash_cooldown = max(0.0, self.dash_cooldown - dt)
        self.invuln = max(0.0, self.invuln - dt)
        self.hurt_lock = max(0.0, self.hurt_lock - dt)
        self.hurt_flash = max(0.0, self.hurt_flash - dt)
        if self.dashing:
            self.dash_time -= dt
            if self.dash_time <= 0:
                self._end_dash(keep_speed=True)
        if self.attack_buffer and not self.dashing:
            # clique dado durante o dash espera o dash acabar
            spec, t = self.attack_buffer
            t -= dt
            self.attack_buffer = (spec, t) if t > 0 else None
        if self.attack is not None:
            self.attack.update(dt)
            if self.attack.phase == "done":
                self.attack = None

    def _read_buffers(self, inp):
        if inp.was_pressed("jump"):
            self.jump_buffer = P.JUMP_BUFFER
        if inp.was_pressed("dash"):
            self.dash_buffer = D.INPUT_BUFFER
        # um clique = um golpe; o último clique vence se houver dois no mesmo instante
        if inp.was_pressed("attack_quick"):
            self.attack_buffer = (self.quick_spec, Combat.ATTACK_BUFFER)
        if inp.was_pressed("attack_heavy"):
            self.attack_buffer = (self.heavy_spec, Combat.ATTACK_BUFFER)

    # --- movimento horizontal / gravidade ---
    def _horizontal(self, dt, move_x):
        mult = 1.0
        if self.attack is not None:
            spec = self.attack.spec
            mult = spec.ground_move_mult if self.on_ground else spec.air_move_mult
        target = move_x * P.RUN_SPEED * mult
        if self.hurt_lock > 0:
            self.vx = approach(self.vx, 0.0, P.AIR_DECEL * 0.5 * dt)
            return
        grounded = self.on_ground
        if move_x == 0:
            rate = P.GROUND_DECEL if grounded else P.AIR_DECEL
        elif self.vx * move_x < 0:
            rate = P.GROUND_TURN_ACCEL if grounded else P.AIR_TURN_ACCEL
        else:
            rate = P.GROUND_ACCEL if grounded else P.AIR_ACCEL
        # acima da velocidade alvo (fim de dash, recuo): desacelera sem cortar seco
        if abs(self.vx) > abs(target) and self.vx * move_x > 0:
            rate = P.GROUND_DECEL if grounded else P.AIR_DECEL * 0.6
        self.vx = approach(self.vx, target, rate * dt)

    def _gravity(self, dt, inp):
        g = PH.GRAVITY
        if self.jumping and inp.is_held("jump") and abs(self.vy) < PH.APEX_THRESHOLD:
            g *= PH.APEX_GRAVITY_MULT       # leve "flutuada" no ápice
        elif self.vy > 0:
            g *= PH.FALL_GRAVITY_MULT
        self.vy = min(self.vy + g * dt, PH.MAX_FALL_SPEED)

    # --- pulo ---
    def _try_jump(self, ctx):
        if self.on_ground or self.coyote > 0:
            if self.dashing:
                self._end_dash(keep_speed=True)
            self.vy = -P.JUMP_VELOCITY
            self.jumps_used = 1
            self.coyote = 0.0
            self.jump_buffer = 0.0
            self.jumping = True
            self.jump_cut_done = False
            self.jump_time = 0.0
            self.on_ground = False
            self.scale_x, self.scale_y = 0.78, 1.25
            ctx.effects.dust(self.cx, self.bottom, 7, 0)
            ctx.audio.play("jump")
        elif self.can_air_jump:
            if self.dashing:
                self._end_dash(keep_speed=True)
            self.vy = -P.DOUBLE_JUMP_VELOCITY
            self.jumps_used += 1
            self.jump_buffer = 0.0
            self.jumping = True
            self.jump_cut_done = False
            self.jump_time = 0.0
            self.scale_x, self.scale_y = 0.82, 1.2
            ctx.effects.ring(self.cx, self.bottom, 22, 0.22, Colors.PLAYER, 2)
            ctx.effects.burst(self.cx, self.bottom, 10, Colors.PLAYER, speed=(60, 160),
                              angle=math.pi / 2, spread=math.pi * 0.9, gravity=200)
            ctx.audio.play("double_jump")
        # senão: fica no buffer até aterrissar

    def _on_land(self, impact_vy, ctx):
        k = min(1.0, max(0.0, impact_vy) / PH.MAX_FALL_SPEED)
        self.scale_x = 1.0 + 0.32 * k + 0.05
        self.scale_y = 1.0 - 0.28 * k - 0.04
        if impact_vy > 200:
            ctx.effects.dust(self.cx, self.bottom, int(4 + 8 * k), 0)
            ctx.audio.play("land")
        self.landing_impact = k
        if impact_vy > 500:
            self.land_timer = 0.12

    # --- dash ---
    def _can_start_dash(self):
        if not self.dash_ready or self.hurt_lock > 0 or self.dashing:
            return False
        if self.attack is not None and self.attack.phase == "active":
            return False   # espera a fase ativa acabar (fica no buffer)
        return True

    def _start_dash(self, move_x, ctx):
        self.attack = None
        self.dash_dir = move_x if move_x else self.facing
        self.facing = self.dash_dir
        self.dash_time = D.DURATION
        self.dash_cooldown = D.DURATION + self.dash_cooldown_time
        self.dash_buffer = 0.0
        if not self.on_ground:
            self.air_dashes_used += 1
        self.jumping = False
        self.ghost_timer = 0.0
        self.scale_x, self.scale_y = 1.3, 0.8
        ctx.effects.dust(self.cx, self.bottom, 6, -self.dash_dir)
        ctx.effects.sprite("fumaca_dash", self.cx - self.dash_dir * 16, self.cy, fps=24, flip=self.dash_dir < 0)
        ctx.effects.burst(self.cx - self.dash_dir * 10, self.cy, 6, Colors.PLAYER_DASH,
                          speed=(80, 200), angle=math.pi if self.dash_dir > 0 else 0,
                          spread=0.8, gravity=0)
        ctx.audio.play("dash")

    def _end_dash(self, keep_speed):
        self.dash_time = 0.0
        self.vx = self.dash_dir * P.RUN_SPEED * D.END_SPEED_MULT if keep_speed else 0.0

    # --- ataques ---
    def _can_start_attack(self):
        return self.attack is None and not self.dashing and self.hurt_lock <= 0

    def _start_attack(self, spec, ctx, inp):
        # mira: W = cima, S no ar = baixo; A/D junto = diagonal; nada = frente
        mx = inp.axis_x()
        if inp.is_held("up"):
            aim = (mx, -1)
        elif inp.is_held("down") and not self.on_ground:
            aim = (mx, 1)
        else:
            aim = (self.facing, 0)
        if aim[0]:
            self.facing = aim[0]
        self.attack = Attack(spec, self.facing, aim)
        self.attack_buffer = None
        ctx.audio.play("attack_" + spec.name)

    def _attack_motion(self):
        atk = self.attack
        if atk.phase == "active" and not atk.lunged:
            atk.lunged = True
            if atk.spec.lunge and self.on_ground and atk.aim[1] == 0:
                self.vx = atk.facing * atk.spec.lunge

    def pogo(self, ctx):
        """Quique do golpe para baixo: devolve o pulo duplo e o dash aéreo."""
        self.vy = -Combat.POGO_VELOCITY
        self.jumping = False
        self.on_ground = False
        self.jumps_used = min(self.jumps_used, 1)
        self.air_dashes_used = 0
        self.scale_x, self.scale_y = 0.85, 1.15
        ctx.effects.burst(self.cx, self.bottom + 10, 8, Colors.QUICK_SLASH, speed=(60, 180),
                          angle=math.pi / 2, spread=math.pi * 0.8, gravity=300)

    def land_on_platform(self, ctx):
        """Apoia o jogador numa plataforma móvel (mesmas regras de pousar no chão)."""
        if not self.was_on_ground and not self.on_ground:
            self._on_land(max(0.0, self.vy), ctx)
        self.vy = 0.0
        self.on_ground = True
        self.coyote = P.COYOTE_TIME
        self.jumps_used = 0
        self.air_dashes_used = 0
        self.jumping = False

    # --- energia e cura ---
    def gain_energy(self, amount):
        self.energy = min(float(EN.MAX), self.energy + amount * self.energy_mult)

    def _can_heal(self):
        return (self.on_ground and self.attack is None and not self.dashing and self.hurt_lock <= 0
                and self.energy >= EN.HEAL_COST and self.hp < self.max_hp)

    def _heal_step(self, dt, ctx):
        self.heal_timer += dt
        self.heal_fx_timer -= dt
        if self.heal_fx_timer <= 0:
            self.heal_fx_timer = 0.03
            a = (self.heal_timer * 23) % math.tau
            r = 34
            ctx.effects.burst(self.cx + math.cos(a) * r, self.cy + math.sin(a) * r, 1, Colors.ENERGY,
                              speed=(10, 20), life=(0.15, 0.2), gravity=-60)
        if self.heal_timer >= self.heal_time:
            self.heal_timer = 0.0
            self.energy -= EN.HEAL_COST
            self.hp = min(self.max_hp, self.hp + EN.HEAL_AMOUNT)
            self.scale_x, self.scale_y = 1.2, 0.85
            ctx.effects.ring(self.cx, self.cy, 40, 0.3, Colors.ENERGY, 3)
            ctx.effects.burst(self.cx, self.cy, 16, Colors.ENERGY, speed=(60, 200), gravity=-100)
            ctx.audio.play("heal")

    @property
    def healing(self):
        return self.heal_timer > 0

    def on_attack_landed(self, spec):
        if (spec.self_recoil and self.on_ground and self.attack is not None
                and self.attack.aim[1] == 0):
            self.vx -= self.attack.facing * spec.self_recoil

    # --- dano ---
    def take_hit(self, damage, source_x, ctx):
        """Retorna True se o dano foi aplicado."""
        if self.invulnerable:
            return False
        self.hp -= damage
        self.invuln = P.HURT_INVULN
        self.hurt_lock = P.HURT_LOCK
        self.hurt_flash = 0.15
        self.heal_timer = 0.0
        self.attack = None
        self.attack_buffer = None
        if self.dashing:
            self._end_dash(keep_speed=False)
        direction = 1 if self.cx >= source_x else -1
        self.vx = direction * P.HURT_KNOCKBACK_X
        self.vy = -P.HURT_KNOCKBACK_Y
        self.jumping = False
        ctx.effects.add_hitstop(FX.HURT_HITSTOP)
        ctx.effects.add_shake(FX.HURT_SHAKE)
        ctx.effects.flash(0.15, (255, 60, 80))
        ctx.effects.burst(self.cx, self.cy, 14, (255, 90, 110), speed=(80, 260))
        ctx.audio.play("hurt")
        if self.hp <= 0:
            self.die(ctx)
        return True

    def die(self, ctx):
        self.hp = 0
        self.alive = False
        self.anim_state = "death"
        self.anim_time = 0.0
        ctx.effects.sprite("fumaca_caveira", self.cx, self.cy - 10, fps=14, scale=2)
        self.attack = None
        self.dash_time = 0.0
        self.vx = self.vy = 0.0
        ctx.effects.burst(self.cx, self.cy, 40, Colors.PLAYER, speed=(100, 420), life=(0.4, 0.9),
                          size=(3, 6), gravity=500)
        ctx.effects.ring(self.cx, self.cy, 60, 0.5, Colors.PLAYER, 4)
        ctx.effects.add_shake(9)
        ctx.audio.play("death")
        ctx.on_player_death()

    # --- visual ---
    def _update_visuals(self, dt, ctx):
        name = state_of(self)[0]
        if name != self.anim_state:
            self.anim_state = name
            self.anim_time = 0.0
        self.anim_time += dt
        self.land_timer = max(0.0, self.land_timer - dt)
        k = 1 - math.exp(-14 * dt)
        self.scale_x += (1.0 - self.scale_x) * k
        self.scale_y += (1.0 - self.scale_y) * k
        atk = self.attack
        if atk is not None and atk.spec.name == "heavy" and atk.phase == "windup":
            self.charge_fx_timer -= dt
            if self.charge_fx_timer <= 0:
                self.charge_fx_timer = 0.03
                ang = (pygame.time.get_ticks() * 0.02) % math.tau
                r = 26
                ctx.effects.burst(self.cx + math.cos(ang) * r, self.cy + math.sin(ang) * r, 1,
                                  Colors.PLAYER_HEAVY_CHARGE, speed=(10, 30), life=(0.15, 0.25),
                                  gravity=0)

    def draw(self, surf, cam_x, cam_y):
        skin = SKINS.get(self.progress.protagonist, SKINS["ele"])
        # piscar durante invulnerabilidade
        if self.alive and self.invuln > 0 and int(self.invuln * 20) % 2 == 0 and self.hurt_flash <= 0:
            return
        if not self.alive and self.anim_time > 1.2:
            return
        name, t = state_of(self)
        frame = frame_for(skin, name, t)
        if frame is None:
            return
        flip = (self.facing < 0) if skin.faces_right else (self.facing > 0)
        white = self.hurt_flash > 0 or (self.healing and int(self.heal_timer * 12) % 2 == 0)
        atk = self.attack
        tint = None
        if atk is not None and atk.spec.name == "heavy" and atk.phase == "windup":
            k = atk.phase_progress
            tint = (255, int(255 - 70 * k), int(255 - 150 * k), 255)
        elif self.dashing:
            tint = (190, 230, 255, 255)
        ax = skin.anchor_x(name)
        ay = frame.get_height() - 1
        fx = self.cx - cam_x
        fy = self.bottom - cam_y
        pose = None
        if self.alive:
            if skin.procedural_attacks:
                pose = self._attack_pose(atk) if atk is not None else self._motion_pose()
            elif skin.motion_lean and atk is None and name == "run":
                pose = self._motion_pose()
        if pose is not None:
            lean, shift, sx, sy = pose
            img = sprites.variant(frame, flip, white, 1, tint)
            w = max(1, round(frame.get_width() * sx * self.scale_x))
            h = max(1, round(frame.get_height() * sy * self.scale_y))
            img = pygame.transform.scale(img, (w, h))
            pivot_x = (frame.get_width() - 1 - ax if flip else ax) * w / frame.get_width()
            face = atk.facing if atk is not None else self.facing
            _blit_rotated(surf, img, (fx + shift * face, fy), (pivot_x, h - 1), -lean * face)
            if atk is not None:
                self._draw_cast_glow(surf, fx + shift * face, fy, atk)
        elif abs(self.scale_x - 1) > 0.03 or abs(self.scale_y - 1) > 0.03:
            # achatar/esticar (pulo e aterrissagem) mantendo os pés no chão
            w = max(1, int(frame.get_width() * self.scale_x))
            h = max(1, int(frame.get_height() * self.scale_y))
            img = sprites.variant(frame, flip, white, 1, tint)
            img = pygame.transform.scale(img, (w, h))
            ax2 = (frame.get_width() - 1 - ax if flip else ax) * self.scale_x
            surf.blit(img, (round(fx - ax2), round(fy - h + 1)))
        else:
            sprites.blit_anchor(surf, frame, fx, fy, (ax, ay), flip=flip, white=white, tint=tint)
        if atk is not None:
            self._draw_attack(surf, cam_x, cam_y, atk)

    def _attack_pose(self, atk):
        """Pose de golpe feita por código (para quem não tem quadros de ataque):
        inclina para trás no preparo, avança e inclina para a frente no golpe e volta na recuperação.
        Retorna (inclinação em graus, deslocamento para a frente em px, escala x, escala y)."""
        heavy = atk.spec.name == "heavy"
        k = atk.phase_progress
        dx, dy = atk.aim
        big = 1.5 if heavy else 1.0
        if dy < 0 and dx == 0:          # para cima: estica e joga o corpo para trás
            peak = (-6 * big, 0, 0.94, 1.10)
            back = (4 * big, -2, 1.04, 0.94)
        elif dy > 0:                    # para baixo no ar: mergulha para a frente
            peak = (28 * big, 4, 0.96, 1.04)
            back = (-6, -2, 1.0, 1.0)
        else:                           # para a frente (ou diagonal)
            peak = (14 * big - (6 if dy < 0 else 0), 8 * big, 1.08, 0.95)
            back = (-10 * big, -4 * big, 0.95, 1.05)
        if atk.phase == "windup":
            e = 1 - (1 - k) ** 2
            return tuple(b * e if i < 2 else 1 + (b - 1) * e for i, b in enumerate(back))
        if atk.phase == "active":
            e = min(1.0, k * 2.5)
            return tuple(b + (p - b) * e for b, p in zip(back, peak))
        e = (1 - k) ** 2                # recuperação: volta ao normal
        return tuple(p * e if i < 2 else 1 + (p - 1) * e for i, p in enumerate(peak))

    def _motion_pose(self):
        """Corpo reage ao movimento (para quem tem poucos quadros): inclina na corrida,
        estica no dash, joga para trás ao levar dano e acompanha a velocidade no ar."""
        speed = P.RUN_SPEED
        k = max(-1.0, min(1.0, self.vx / speed)) * self.facing   # >0: indo para onde olha
        if self.dashing:
            return (12, 2, 1.14, 0.9)
        if self.hurt_lock > 0:
            return (-12, -2, 1.0, 1.0)
        if not self.on_ground:
            return (7 * k + (3 if self.vy > 0 else -2), 0, 1.0, 1.0)
        if abs(self.vx) > 20:
            return (5 * k, 0, 1.0, 1.0)
        return None

    def _draw_cast_glow(self, surf, x, foot_y, atk):
        """Brilho de magia na mão durante o golpe."""
        if atk.phase != "active":
            return
        dx, dy = atk.aim
        if dx == 0 and dy == 0:
            dx = atk.facing
        hx = x + dx * 18
        hy = foot_y - 30 + dy * 16
        k = atk.phase_progress
        r = int((9 if atk.spec.name == "heavy" else 6) * (1.2 - k * 0.6))
        col = (255, 190, 110) if atk.spec.name == "heavy" else (170, 220, 255)
        pygame.draw.circle(surf, col, (round(hx), round(hy)), r + 2)
        pygame.draw.circle(surf, (255, 255, 255), (round(hx), round(hy)), max(1, r - 2))

    def _dash_ghost(self, ctx):
        """Rastro do dash: silhueta azulada do quadro atual, na posição de agora."""
        skin = SKINS.get(self.progress.protagonist, SKINS["ele"])
        frame = frame_for(skin, "dash", self.anim_time)
        if frame is None:
            ctx.effects.ghost(self.rect_tuple(), Colors.PLAYER_DASH)
            return
        flip = (self.facing < 0) if skin.faces_right else (self.facing > 0)
        img = sprites.variant(frame, flip, False, 1, (120, 200, 255, 255))
        ax = skin.anchor_x("dash")
        if flip:
            ax = frame.get_width() - 1 - ax
        rect = (self.cx - ax, self.bottom - frame.get_height() + 1, frame.get_width(), frame.get_height())
        ctx.effects.ghost(rect, Colors.PLAYER_DASH, img)

    def _draw_attack(self, surf, cam_x, cam_y, atk):
        spec = atk.spec
        heavy = spec.name == "heavy"
        bx, by, bw, bh = atk.hitbox(self)
        if atk.phase == "windup":
            if heavy:
                k = atk.phase_progress
                fr = sprites.effect("brilho")
                if fr:
                    img = fr[min(len(fr) - 1, int(k * len(fr)))]
                    sprites.blit_anchor(surf, img, self.cx - cam_x - atk.facing * 10, self.cy - cam_y - 6,
                                        (img.get_width() // 2, img.get_height() // 2))
            return
        if atk.phase != "active":
            return
        frames = sprites.grid("efeitos/cortes.png", 128, 128)
        if not frames:
            return
        seq = frames[4:8] if heavy else frames[0:4]
        img = seq[min(len(seq) - 1, int(atk.phase_progress * len(seq)))]
        dx, dy = atk.aim
        angle = 0 if dy == 0 else (-90 * dy if dx == 0 else -45 * dy)
        flip = (dx if dx else atk.facing) < 0
        scale = 1.35 if heavy else 1.0
        key = (id(img), flip, angle, scale, heavy)
        cache = _SMEAR_CACHE.get(key)
        if cache is None:
            v = pygame.transform.flip(img, flip, False)
            if heavy:
                v = v.copy()
                v.fill((255, 200, 120, 255), special_flags=pygame.BLEND_RGBA_MULT)
            if scale != 1:
                v = pygame.transform.scale(v, (int(v.get_width() * scale), int(v.get_height() * scale)))
            if angle:
                v = pygame.transform.rotate(v, angle if not flip else -angle)
            cache = _SMEAR_CACHE[key] = v
        rect = cache.get_rect(center=(round(bx + bw / 2 - cam_x), round(by + bh / 2 - cam_y)))
        surf.blit(cache, rect)


_SMEAR_CACHE = {}


def _blit_rotated(surf, img, pivot_screen, pivot_img, angle):
    """Gira `img` em volta de `pivot_img` (ponto da imagem) e cola esse ponto em `pivot_screen`."""
    if abs(angle) < 0.5:
        surf.blit(img, (round(pivot_screen[0] - pivot_img[0]), round(pivot_screen[1] - pivot_img[1])))
        return
    w, h = img.get_size()
    offset = pygame.math.Vector2(w / 2 - pivot_img[0], h / 2 - pivot_img[1]).rotate(-angle)
    rot = pygame.transform.rotate(img, angle)
    rect = rot.get_rect(center=(round(pivot_screen[0] + offset.x), round(pivot_screen[1] + offset.y)))
    surf.blit(rot, rect)
