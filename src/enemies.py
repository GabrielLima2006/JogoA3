"""Inimigos de teste: patrulheiro, perseguidor e torreta (projéteis)."""

import itertools
import math
import random

import pygame

from .config import Boss as BS, Colors, Enemies as E, Physics as PH
from .physics import Body, ground_ahead, line_of_sight, move_and_collide, wall_ahead

_uids = itertools.count(1)


def approach(value, target, delta):
    if value < target:
        return min(value + delta, target)
    return max(value - delta, target)


class Enemy(Body):
    color = (200, 200, 200)
    max_hp = 1
    drop = None
    is_boss = False
    contact_damage = 1
    gravity = True
    knockback_resist = 1.0

    def __init__(self, foot_x, foot_y, w, h):
        super().__init__(foot_x - w / 2, foot_y - h, w, h)
        self.uid = next(_uids)
        self.hp = self.max_hp
        self.alive = True
        self.flash = 0.0
        self.stun = 0.0
        self.direction = -1
        self.show_hp = 0.0
        self.squash = 1.0

    # --- dano ---
    def take_hit(self, damage, direction, knockback, knock_up, stun, ctx):
        if not self.alive:
            return
        self.hp -= damage
        self.flash = 0.12
        self.show_hp = 2.5
        self.stun = max(self.stun, stun)
        self.vx = direction * knockback * self.knockback_resist
        if knock_up and self.gravity:
            self.vy = -knock_up * self.knockback_resist
        self.squash = 0.7
        if self.hp <= 0:
            self.alive = False
            ctx.effects.sprite("explosao_grande" if self.is_boss else "explosao", self.cx, self.cy, fps=18,
                               scale=2 if self.is_boss else 1)
            ctx.effects.burst(self.cx, self.cy, 26, self.color, speed=(80, 340), life=(0.3, 0.7),
                              size=(3, 6), gravity=600)
            ctx.effects.ring(self.cx, self.cy, 40, 0.3, self.color, 3)
            ctx.effects.add_shake(3)
            ctx.audio.play("enemy_death")
            ctx.on_enemy_killed(self)

    def blocks(self, spec, direction):
        """Retorna True se o golpe foi defendido (sem dano)."""
        return False

    # --- atualização comum ---
    def update(self, dt, room, player, ctx):
        self.flash = max(0.0, self.flash - dt)
        self.show_hp = max(0.0, self.show_hp - dt)
        self.squash += (1.0 - self.squash) * (1 - math.exp(-12 * dt))
        if self.stun > 0:
            self.stun -= dt
            self.vx = approach(self.vx, 0.0, E.KNOCKBACK_FRICTION * dt)
        else:
            self.think(dt, room, player, ctx)
        if self.gravity:
            g = PH.GRAVITY * (PH.FALL_GRAVITY_MULT if self.vy > 0 else 1.0)
            self.vy = min(self.vy + g * dt, PH.MAX_FALL_SPEED)
        move_and_collide(self, self.vx * dt, self.vy * dt, room, oob_solid=True)
        if self.on_ground or self.hit_ceiling:
            self.vy = 0.0
        if self.hit_left or self.hit_right:
            self.vx = 0.0
        # caiu no espinho ou para fora da sala
        spikes = room.spike_rects(self.left, self.top, self.right, self.bottom)
        if self.top > room.height or any(_overlap(self.rect_tuple(), r) for r in spikes):
            self.hp = 0
            self.take_hit(0, 0, 0, 0, 0, ctx)

    def think(self, dt, room, player, ctx):
        pass

    # --- desenho ---
    def body_color(self):
        return (255, 255, 255) if self.flash > 0 else self.color

    def draw(self, surf, cam_x, cam_y):
        w = self.w * (2 - self.squash)
        h = self.h * self.squash
        r = pygame.Rect(round(self.cx - w / 2 - cam_x), round(self.bottom - h - cam_y), round(w), round(h))
        pygame.draw.rect(surf, self.body_color(), r, border_radius=3)
        eye_x = r.centerx + self.direction * r.w * 0.25
        pygame.draw.rect(surf, (25, 20, 30), (round(eye_x - 3), r.y + 6, 6, 5))
        if self.stun > 0.05:
            # estrelinhas de atordoamento
            t = pygame.time.get_ticks() * 0.008
            for i in range(3):
                a = t + i * 2.1
                pygame.draw.circle(surf, (255, 240, 140),
                                   (int(r.centerx + math.cos(a) * 12), int(r.y - 8 + math.sin(a) * 3)), 2)
        self.draw_hp(surf, cam_x, cam_y)

    def draw_hp(self, surf, cam_x, cam_y):
        if self.show_hp <= 0 or self.hp >= self.max_hp:
            return
        bw = max(26, self.w + 6)
        x = round(self.cx - bw / 2 - cam_x)
        y = round(self.top - 10 - cam_y)
        pygame.draw.rect(surf, (40, 30, 40), (x, y, bw, 5))
        pygame.draw.rect(surf, Colors.HP_FULL, (x, y, round(bw * max(0, self.hp) / self.max_hp), 5))


def _overlap(a, b):
    return a[0] < b[0] + b[2] and a[0] + a[2] > b[0] and a[1] < b[1] + b[3] and a[1] + a[3] > b[1]


class Patroller(Enemy):
    """Anda de um lado para o outro e vira em paredes e bordas."""
    color = Colors.PATROLLER
    drop = "patroller"
    max_hp = E.PATROLLER_HP
    contact_damage = E.PATROLLER_DAMAGE

    def __init__(self, foot_x, foot_y):
        super().__init__(foot_x, foot_y, *E.PATROLLER_SIZE)

    def think(self, dt, room, player, ctx):
        if self.on_ground:
            if wall_ahead(self, room, self.direction) or not ground_ahead(self, room, self.direction):
                self.direction *= -1
        self.vx = approach(self.vx, self.direction * E.PATROLLER_SPEED, 1200 * dt)


class Chaser(Enemy):
    """Patrulha devagar; ao ver o jogador, avisa com "!" e persegue.

    Persegue apenas no mesmo andar aproximado (CHASER_VERTICAL_RANGE) e com
    linha de visão. Fora dessas condições por CHASER_GIVE_UP_TIME, desiste.
    Nunca se joga de bordas: para na beirada.
    """
    color = Colors.CHASER
    drop = "chaser"
    max_hp = E.CHASER_HP
    contact_damage = E.CHASER_DAMAGE

    def __init__(self, foot_x, foot_y):
        super().__init__(foot_x, foot_y, *E.CHASER_SIZE)
        self.state = "patrol"
        self.timer = 0.0
        self.lost_timer = 0.0

    def _sees(self, player, room, max_range):
        if not player.alive:
            return False
        dx = player.cx - self.cx
        dy = player.cy - self.cy
        if abs(dx) > max_range or abs(dy) > E.CHASER_VERTICAL_RANGE:
            return False
        return line_of_sight(room, self.cx, self.cy - 6, player.cx, player.cy - 6)

    def think(self, dt, room, player, ctx):
        if self.state == "patrol":
            if self.on_ground and (wall_ahead(self, room, self.direction)
                                   or not ground_ahead(self, room, self.direction)):
                self.direction *= -1
            self.vx = approach(self.vx, self.direction * E.CHASER_PATROL_SPEED, 900 * dt)
            if self._sees(player, room, E.CHASER_DETECT_RANGE):
                self.state = "alert"
                self.timer = E.CHASER_ALERT_TIME
                self.direction = 1 if player.cx > self.cx else -1
                if self.on_ground:
                    self.vy = -220     # pulinho de susto: leitura clara do perigo
        elif self.state == "alert":
            self.vx = approach(self.vx, 0.0, 2000 * dt)
            self.timer -= dt
            if self.timer <= 0:
                self.state = "chase"
                self.lost_timer = 0.0
        elif self.state == "chase":
            if self._sees(player, room, E.CHASER_LOSE_RANGE):
                self.lost_timer = 0.0
            else:
                self.lost_timer += dt
                if self.lost_timer >= E.CHASER_GIVE_UP_TIME:
                    self.state = "patrol"
            dx = player.cx - self.cx
            if abs(dx) > 6:
                self.direction = 1 if dx > 0 else -1
            target = self.direction * E.CHASER_SPEED if abs(dx) > 6 else 0.0
            # não cai de bordas nem empurra paredes
            if self.on_ground and (not ground_ahead(self, room, self.direction)
                                   or wall_ahead(self, room, self.direction)):
                target = 0.0
            self.vx = approach(self.vx, target, E.CHASER_ACCEL * dt)

    def draw(self, surf, cam_x, cam_y):
        super().draw(surf, cam_x, cam_y)
        if self.state in ("alert", "chase") and self.alive:
            x = round(self.cx - cam_x)
            y = round(self.top - 22 - cam_y)
            col = Colors.CHASER_ALERT if self.state == "alert" else (255, 120, 90)
            pygame.draw.rect(surf, col, (x - 2, y, 4, 9))
            pygame.draw.rect(surf, col, (x - 2, y + 11, 4, 4))


class Turret(Enemy):
    """Fixa na parede/chão. Brilha antes de atirar (telegrafia)."""
    color = Colors.TURRET
    drop = "turret"
    max_hp = E.TURRET_HP
    contact_damage = 1
    gravity = False
    knockback_resist = 0.0

    def __init__(self, foot_x, foot_y):
        super().__init__(foot_x, foot_y, *E.TURRET_SIZE)
        self.cooldown = E.TURRET_COOLDOWN * 0.5
        self.telegraph = 0.0

    def think(self, dt, room, player, ctx):
        self.vx = self.vy = 0.0
        dx = player.cx - self.cx
        dy = player.cy - self.cy
        self.direction = 1 if dx > 0 else -1
        in_range = (player.alive and math.hypot(dx, dy) <= E.TURRET_RANGE
                    and line_of_sight(room, self.cx, self.cy, player.cx, player.cy))
        if self.telegraph > 0:
            self.telegraph -= dt
            if self.telegraph <= 0:
                if in_range:
                    ctx.projectiles.spawn(self.cx, self.cy, dx, dy)
                    ctx.audio.play("shoot")
                    ctx.effects.burst(self.cx, self.cy, 5, Colors.PROJECTILE, speed=(40, 120), gravity=0)
                self.cooldown = E.TURRET_COOLDOWN
            return
        self.cooldown -= dt
        if self.cooldown <= 0 and in_range:
            self.telegraph = E.TURRET_TELEGRAPH

    def body_color(self):
        if self.flash > 0:
            return (255, 255, 255)
        if self.telegraph > 0 and int(self.telegraph * 24) % 2 == 0:
            return Colors.PROJECTILE
        return self.color


class Flier(Enemy):
    """Voa parado balançando; ao ver o jogador, avisa e persegue pelo ar."""
    color = Colors.FLIER
    drop = "flier"
    max_hp = E.FLIER_HP
    gravity = False

    def __init__(self, foot_x, foot_y):
        super().__init__(foot_x, foot_y - 8, *E.FLIER_SIZE)
        self.state = "hover"
        self.timer = 0.0
        self.lost = 0.0
        self.t = (foot_x * 0.37) % 6.28

    def _sees(self, player, room, max_range):
        if not player.alive:
            return False
        if math.hypot(player.cx - self.cx, player.cy - self.cy) > max_range:
            return False
        return line_of_sight(room, self.cx, self.cy, player.cx, player.cy)

    def think(self, dt, room, player, ctx):
        self.t += dt
        if self.state == "hover":
            self.vx = approach(self.vx, 0.0, 300 * dt)
            self.vy = math.sin(self.t * 2.2) * 35
            if self._sees(player, room, E.FLIER_DETECT_RANGE):
                self.state = "alert"
                self.timer = E.FLIER_ALERT_TIME
        elif self.state == "alert":
            self.vx = approach(self.vx, 0.0, 800 * dt)
            self.vy = approach(self.vy, -40.0, 800 * dt)
            self.timer -= dt
            if self.timer <= 0:
                self.state = "chase"
                self.lost = 0.0
        else:
            dx = player.cx - self.cx
            dy = player.cy - 6 - self.cy
            d = math.hypot(dx, dy) or 1.0
            self.vx = approach(self.vx, dx / d * E.FLIER_SPEED, E.FLIER_ACCEL * dt)
            self.vy = approach(self.vy, dy / d * E.FLIER_SPEED, E.FLIER_ACCEL * dt)
            self.direction = 1 if dx > 0 else -1
            if self._sees(player, room, E.FLIER_LOSE_RANGE):
                self.lost = 0.0
            else:
                self.lost += dt
                if self.lost > 1.5:
                    self.state = "hover"

    def update(self, dt, room, player, ctx):
        super().update(dt, room, player, ctx)
        if self.stun > 0:
            self.vy = approach(self.vy, 0.0, E.KNOCKBACK_FRICTION * dt)

    def draw(self, surf, cam_x, cam_y):
        super().draw(surf, cam_x, cam_y)
        flap = math.sin(self.t * 18) * 6
        x, y = self.cx - cam_x, self.cy - cam_y
        col = self.body_color()
        pygame.draw.polygon(surf, col, [(x - 6, y), (x - 20, y - 6 - flap), (x - 14, y + 4)])
        pygame.draw.polygon(surf, col, [(x + 6, y), (x + 20, y - 6 - flap), (x + 14, y + 4)])
        if self.state == "alert":
            pygame.draw.rect(surf, Colors.CHASER_ALERT, (round(x - 2), round(self.top - 22 - cam_y), 4, 9))


class Jumper(Enemy):
    """Agacha (aviso) e salta na direção do jogador."""
    color = Colors.JUMPER
    drop = "jumper"
    max_hp = E.JUMPER_HP

    def __init__(self, foot_x, foot_y):
        super().__init__(foot_x, foot_y, *E.JUMPER_SIZE)
        self.state = "idle"
        self.timer = 0.0
        self.cooldown = 0.8

    def think(self, dt, room, player, ctx):
        dx = player.cx - self.cx
        in_range = player.alive and abs(dx) < E.JUMPER_RANGE and abs(player.cy - self.cy) < 200
        if self.state == "idle":
            self.vx = approach(self.vx, 0.0, 1400 * dt)
            if self.on_ground:
                self.cooldown -= dt
                if in_range:
                    self.direction = 1 if dx > 0 else -1
                if self.cooldown <= 0 and in_range:
                    self.state = "crouch"
                    self.timer = E.JUMPER_TELEGRAPH
        elif self.state == "crouch":
            self.vx = 0.0
            self.squash = min(self.squash, 0.72)
            self.timer -= dt
            if self.timer <= 0:
                self.vy = -E.JUMPER_JUMP_VY
                self.vx = self.direction * min(E.JUMPER_JUMP_VX, abs(dx) * 1.6 + 40)
                self.state = "air"
                self.timer = 0.12
        else:
            self.timer -= dt
            if self.on_ground and self.timer <= 0:
                self.state = "idle"
                self.cooldown = E.JUMPER_COOLDOWN
                self.squash = 0.75
                ctx.effects.dust(self.cx, self.bottom, 5)


class Shield(Enemy):
    """Escudo na frente bloqueia o ataque rápido. O pesado quebra a guarda."""
    color = Colors.SHIELD
    drop = "shield"
    max_hp = E.SHIELD_HP
    knockback_resist = 0.5

    def __init__(self, foot_x, foot_y):
        super().__init__(foot_x, foot_y, *E.SHIELD_SIZE)
        self.state = "walk"
        self.timer = 0.0
        self.guard_broken = False

    def blocks(self, spec, direction):
        from_front = direction == -self.direction
        if not from_front or self.guard_broken:
            return False
        if spec.name == "heavy":
            self.guard_broken = True
            self.stun = E.SHIELD_GUARD_BREAK
            self.state = "walk"
            return False
        return True

    def think(self, dt, room, player, ctx):
        self.guard_broken = False
        dx = player.cx - self.cx
        aware = player.alive and abs(dx) < E.SHIELD_RANGE and abs(player.cy - self.cy) < 110
        if self.state == "walk":
            if aware:
                self.direction = 1 if dx > 0 else -1
                target = self.direction * E.SHIELD_SPEED
                if abs(dx) < E.SHIELD_BASH_RANGE:
                    self.state = "windup"
                    self.timer = E.SHIELD_BASH_WINDUP
                    target = 0.0
            else:
                if self.on_ground and (wall_ahead(self, room, self.direction)
                                       or not ground_ahead(self, room, self.direction)):
                    self.direction *= -1
                target = self.direction * E.SHIELD_SPEED * 0.5
            if self.on_ground and (not ground_ahead(self, room, self.direction)
                                   or wall_ahead(self, room, self.direction)):
                target = 0.0
            self.vx = approach(self.vx, target, 900 * dt)
        elif self.state == "windup":
            self.vx = approach(self.vx, -self.direction * 30, 900 * dt)
            self.timer -= dt
            if self.timer <= 0:
                self.state = "bash"
                self.timer = E.SHIELD_BASH_TIME
        else:
            self.vx = self.direction * E.SHIELD_BASH_SPEED if ground_ahead(self, room, self.direction) else 0.0
            self.timer -= dt
            if self.timer <= 0:
                self.state = "walk"

    def body_color(self):
        if self.flash > 0:
            return (255, 255, 255)
        if self.state == "windup" and int(self.timer * 20) % 2 == 0:
            return (230, 230, 255)
        return self.color

    def draw(self, surf, cam_x, cam_y):
        super().draw(surf, cam_x, cam_y)
        if not self.guard_broken and self.stun <= 0:
            sx = self.cx + self.direction * (self.w / 2 + 2) - cam_x
            pygame.draw.rect(surf, (210, 220, 240), (round(sx - 4), round(self.top + 4 - cam_y), 8, self.h - 6),
                             border_radius=3)


class Guardian(Enemy):
    """Chefe: investida (bate na parede e fica tonto), salto com onda de choque e cuspe."""
    color = Colors.GUARDIAN
    drop = "guardian"
    max_hp = BS.HP
    contact_damage = BS.CONTACT_DAMAGE
    knockback_resist = 0.0
    is_boss = True

    def __init__(self, foot_x, foot_y):
        super().__init__(foot_x, foot_y, *BS.SIZE)
        self.state = "sleep"
        self.timer = 0.0
        self.history = []
        self.airborne = False
        self.charge_dir = 1

    @property
    def awake(self):
        return self.state != "sleep"

    def wake(self):
        if self.state == "sleep":
            self.state = "idle"
            self.timer = 0.9

    def take_hit(self, damage, direction, knockback, knock_up, stun, ctx):
        super().take_hit(damage, direction, 0, 0, 0, ctx)

    @property
    def phase2(self):
        return self.hp <= self.max_hp * BS.PHASE2_HP

    def _choose(self, player):
        options = ["charge", "leap", "spit"]
        if len(self.history) >= 2 and self.history[-1] == self.history[-2]:
            options.remove(self.history[-1])
        far = abs(player.cx - self.cx) > 260
        weights = [3 if far else 2, 2, 2 if far else 1]
        weights = [w for o, w in zip(["charge", "leap", "spit"], weights) if o in options]
        pick = random.choices(options, weights)[0]
        self.history = (self.history + [pick])[-3:]
        return pick

    def think(self, dt, room, player, ctx):
        sp = BS.PHASE2_SPEED if self.phase2 else 1.0
        dx = player.cx - self.cx
        st = self.state
        if st == "sleep":
            self.vx = 0.0
            return
        if st == "idle":
            self.vx = approach(self.vx, 0.0, 2000 * dt)
            self.direction = 1 if dx > 0 else -1
            self.timer -= dt * sp
            if self.timer <= 0 and self.on_ground:
                pick = self._choose(player)
                self.state = pick + "_tele"
                self.timer = {"charge": BS.CHARGE_TELEGRAPH, "leap": BS.LEAP_TELEGRAPH,
                              "spit": BS.SPIT_TELEGRAPH}[pick] / sp
        elif st == "charge_tele":
            self.vx = approach(self.vx, -self.direction * 40, 1500 * dt)
            self.timer -= dt
            if self.timer <= 0:
                self.state = "charge"
                self.charge_dir = self.direction
        elif st == "charge":
            self.vx = self.charge_dir * BS.CHARGE_SPEED * sp
            if wall_ahead(self, room, self.charge_dir):
                self.state = "stunned"
                self.timer = BS.WALL_STUN
                self.vx = -self.charge_dir * 120
                self.vy = -200
                ctx.effects.add_shake(8)
                ctx.effects.burst(self.cx + self.charge_dir * self.w / 2, self.cy, 18, (200, 200, 210),
                                  speed=(80, 260))
                ctx.audio.play("impact")
        elif st == "stunned":
            self.vx = approach(self.vx, 0.0, 600 * dt)
            self.timer -= dt
            if self.timer <= 0:
                self.state = "idle"
                self.timer = random.uniform(*BS.IDLE_TIME)
        elif st == "leap_tele":
            self.vx = 0.0
            self.squash = min(self.squash, 0.75)
            self.timer -= dt
            if self.timer <= 0:
                self.vy = -BS.LEAP_VY
                self.vx = max(-460.0, min(460.0, dx / 0.8))
                self.state = "leap"
                self.airborne = False
        elif st == "leap":
            if not self.on_ground:
                self.airborne = True
            elif self.airborne:
                self.vx = 0.0
                self.squash = 0.6
                y = self.bottom - 10
                for d in (-1, 1):
                    ctx.projectiles.spawn(self.cx + d * self.w / 2, y, d, 0, speed=BS.SHOCKWAVE_SPEED * sp)
                    if self.phase2:
                        ctx.projectiles.spawn(self.cx, self.top + 10, d, -0.6, speed=BS.SHOCKWAVE_SPEED * 0.9)
                ctx.effects.add_shake(9)
                ctx.effects.dust(self.cx, self.bottom, 16)
                ctx.audio.play("impact")
                self.state = "idle"
                self.timer = random.uniform(*BS.IDLE_TIME)
        elif st == "spit_tele":
            self.vx = 0.0
            self.direction = 1 if dx > 0 else -1
            self.timer -= dt
            if self.timer <= 0:
                base = math.atan2(player.cy - self.cy, dx)
                count = 5 if self.phase2 else 3
                for i in range(count):
                    a = base + (i - (count - 1) / 2) * 0.28
                    ctx.projectiles.spawn(self.cx + self.direction * 20, self.cy - 10, math.cos(a), math.sin(a))
                ctx.audio.play("shoot")
                self.state = "idle"
                self.timer = random.uniform(*BS.IDLE_TIME)

    def body_color(self):
        if self.flash > 0:
            return (255, 255, 255)
        if self.state.endswith("_tele") and int(self.timer * 18) % 2 == 0:
            return (255, 200, 120)
        if self.state == "stunned":
            return (150, 90, 90)
        if self.state == "sleep":
            return (110, 60, 60)
        return self.color

    def draw_hp(self, surf, cam_x, cam_y):
        pass   # a barra do chefe é desenhada na interface


ENEMY_TYPES = {"g": Patroller, "c": Chaser, "t": Turret, "f": Flier, "j": Jumper, "s": Shield, "G": Guardian}


def spawn_enemies(room, boss_defeated=False):
    out = []
    for spawn in room.spawns:
        kind, x, y = spawn[0], spawn[1], spawn[2]
        cls = ENEMY_TYPES.get(kind)
        if cls is None or (cls.is_boss and boss_defeated):
            continue
        out.append(cls(x, y))
    return out
