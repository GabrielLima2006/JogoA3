"""Chefes do jogo e os perigos que eles criam (bombas, raios, ondas).

Cada chefe:
  - dorme até o jogador chegar perto (a luta fecha o portão da arena);
  - avisa antes de cada ataque (pisca, muda de pose) para ser justo;
  - tem uma janela para ser punido (fica tonto, recupera, pousa);
  - abaixo de 50% de vida entra na fase 2 (mais rápido e com ataques extras).
"""

import math
import random

import pygame

from . import pixelart, sprites
from .config import Physics as PH
from .creatures import Rat, TideSlime
from .enemies import Enemy, approach, wall_ahead
from .physics import move_and_collide, rects_overlap


class Boss(Enemy):
    is_boss = True
    knockback_resist = 0.0
    contact_damage = 1
    name = "Chefe"
    title = ""
    drop = "guardian"

    def __init__(self, foot_x, foot_y, w, h):
        super().__init__(foot_x, foot_y, w, h)
        self.state = "sleep"
        self.timer = 0.0
        self.history = []
        self.anim_t = 0.0
        self.airborne = False
        self.invulnerable = False

    @property
    def awake(self):
        return self.state != "sleep"

    def wake(self):
        if self.state == "sleep":
            self.state = "idle"
            self.timer = 1.0

    @property
    def phase2(self):
        return self.hp <= self.max_hp * 0.5

    def take_hit(self, damage, direction, knockback, knock_up, stun, ctx):
        if self.invulnerable or not self.awake:
            return
        super().take_hit(damage, direction, 0, 0, 0, ctx)

    def choose(self, options, weights):
        if len(self.history) >= 2 and self.history[-1] == self.history[-2] and self.history[-1] in options:
            i = options.index(self.history[-1])
            options = options[:i] + options[i + 1:]
            weights = weights[:i] + weights[i + 1:]
        pick = random.choices(options, weights)[0]
        self.history = (self.history + [pick])[-3:]
        return pick

    def update(self, dt, room, player, ctx):
        self.anim_t += dt
        super().update(dt, room, player, ctx)

    def draw_hp(self, surf, cam_x, cam_y):
        pass   # a barra do chefe fica na interface

    def telegraphing(self):
        return self.state.endswith("_tele") and int(self.timer * 18) % 2 == 0

    def _stars(self, surf, cam_x, cam_y):
        t = self.anim_t * 8
        for i in range(3):
            a = t + i * 2.1
            pygame.draw.circle(surf, (255, 240, 140),
                               (int(self.cx - cam_x + math.cos(a) * 18), int(self.top - 10 - cam_y + math.sin(a) * 4)), 3)


# ---------------------------------------------------------------------------
# Perigos criados pelos chefes
# ---------------------------------------------------------------------------

class Bomb:
    """Bomba arremessada em arco; explode ao tocar o chão (área de dano)."""
    RADIUS = 64

    def __init__(self, x, y, vx, vy):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.alive = True
        self.fuse = 2.5

    def update(self, dt, room, player, ctx):
        self.vy += PH.GRAVITY * 0.8 * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.fuse -= dt
        T = 32
        if room.is_solid(int(self.x // T), int((self.y + 8) // T)) or self.fuse <= 0 or self.y > room.height:
            self.explode(player, ctx)
        return self.alive

    def explode(self, player, ctx):
        self.alive = False
        ctx.effects.sprite("explosao", self.x, self.y - 10, fps=20, scale=2)
        ctx.effects.add_shake(7)
        ctx.audio.play("heavy_hit")
        if player.alive and math.hypot(player.cx - self.x, player.cy - self.y) < self.RADIUS:
            player.take_hit(1, self.x, ctx)

    def draw(self, surf, cam_x, cam_y, time):
        pos = (int(self.x - cam_x), int(self.y - cam_y))
        pygame.draw.circle(surf, (30, 30, 36), pos, 9)
        pygame.draw.circle(surf, (90, 90, 110), (pos[0] - 3, pos[1] - 3), 3)
        if int(time * 12) % 2 == 0:
            pygame.draw.circle(surf, (255, 200, 80), (pos[0] + 6, pos[1] - 9), 3)


class Lightning:
    """Raio: marca o chão por um instante (aviso) e depois cai na coluna."""

    def __init__(self, x, floor_y, warn=0.8):
        self.x, self.floor_y = x, floor_y
        self.warn = warn
        self.strike = 0.35
        self.alive = True
        self.hit_done = False

    def update(self, dt, room, player, ctx):
        if self.warn > 0:
            self.warn -= dt
            if self.warn <= 0:
                ctx.effects.sprite("raio", self.x, self.floor_y - 64, fps=22, scale=2)
                ctx.effects.add_shake(5)
                ctx.audio.play("boss")
            return True
        self.strike -= dt
        rect = (self.x - 22, self.floor_y - 260, 44, 260)
        if not self.hit_done and player.alive and rects_overlap(rect, player.rect_tuple()):
            self.hit_done = player.take_hit(1, self.x, ctx)
        if self.strike <= 0:
            self.alive = False
        return self.alive

    def draw(self, surf, cam_x, cam_y, time):
        if self.warn > 0:
            k = 1 - self.warn / 0.8
            r = pygame.Rect(0, 0, 44, 8)
            r.midbottom = (int(self.x - cam_x), int(self.floor_y - cam_y))
            col = (200, 120, 255) if int(time * 20) % 2 else (255, 255, 255)
            pygame.draw.rect(surf, col, r, border_radius=3)
            pygame.draw.line(surf, (160, 90, 220), (r.centerx, r.top - 6 - 60 * (1 - k)), (r.centerx, r.top - 6), 2)


class Wave:
    """Onda da maré que atravessa a arena rente ao chão: pule por cima."""

    def __init__(self, x, floor_y, direction, speed=300, height=46):
        self.x, self.floor_y, self.dir, self.speed, self.h = x, floor_y, direction, speed, height
        self.alive = True
        self.hit = False

    def update(self, dt, room, player, ctx):
        self.x += self.dir * self.speed * dt
        rect = (self.x - 30, self.floor_y - self.h, 60, self.h)
        if not self.hit and player.alive and rects_overlap(rect, player.rect_tuple()):
            self.hit = player.take_hit(1, self.x - self.dir * 40, ctx)
        if self.x < -60 or self.x > room.width + 60:
            self.alive = False
        return self.alive

    def draw(self, surf, cam_x, cam_y, time):
        x, fy = self.x - cam_x, self.floor_y - cam_y
        pts = []
        for i in range(13):
            k = i / 12
            px = x - 34 + 68 * k
            py = fy - self.h * math.sin(k * math.pi) * (0.85 + 0.15 * math.sin(time * 10 + i))
            pts.append((px, py))
        pygame.draw.polygon(surf, (40, 110, 170), pts + [(x + 34, fy), (x - 34, fy)])
        pygame.draw.lines(surf, (190, 230, 250), False, pts, 3)


class Flood:
    """A água da arena sobe, fica um tempo e baixa. Quem estiver com os pés na água leva dano;
    as plataformas altas ficam secas. Desenhada na frente do jogador."""
    front = True

    def __init__(self, room_width, floor_y, height=72, rise=0.9, hold=2.6, tick=0.7):
        self.w, self.floor_y, self.max_h = room_width, floor_y, height
        self.rise, self.hold, self.t, self.tick, self.cool = rise, hold, 0.0, tick, 0.0
        self.alive = True

    @property
    def level(self):
        t, r, h = self.t, self.rise, self.hold
        if t < r:
            k = t / r
        elif t < r + h:
            k = 1.0
        else:
            k = max(0.0, 1 - (t - r - h) / r)
        return self.max_h * (1 - (1 - k) ** 2)

    def update(self, dt, room, player, ctx):
        self.t += dt
        self.cool = max(0.0, self.cool - dt)
        surface = self.floor_y - self.level
        if self.level > 10 and player.alive and player.bottom > surface + 6 and self.cool <= 0:
            if player.take_hit(1, player.cx - player.facing * 10, ctx):
                self.cool = self.tick
                ctx.effects.burst(player.cx, surface, 10, (150, 210, 240), speed=(60, 200))
        if self.t > self.rise * 2 + self.hold:
            self.alive = False
        return self.alive

    def draw(self, surf, cam_x, cam_y, time):
        lvl = self.level
        if lvl < 2:
            # aviso: bolhas subindo do chão
            for i in range(12):
                x = (i * 97 + int(time * 40)) % self.w
                pygame.draw.circle(surf, (150, 210, 240), (int(x - cam_x), int(self.floor_y - 6 - cam_y)), 2)
            return
        top = self.floor_y - lvl
        water = pygame.Surface((self.w, int(lvl) + 4), pygame.SRCALPHA)
        water.fill((30, 90, 150, 120))
        pts = [(x, 4 + math.sin(x * 0.05 + time * 4) * 3) for x in range(0, self.w + 16, 16)]
        water.fill((0, 0, 0, 0), (0, 0, self.w, 8))
        pygame.draw.polygon(water, (30, 90, 150, 120), pts + [(self.w, 8), (0, 8)])
        pygame.draw.lines(water, (190, 230, 250, 230), False, pts, 2)
        surf.blit(water, (-cam_x, top - 4 - cam_y))


class Gust:
    """Rajada de vento: avisa com riscos no ar e depois empurra o jogador na horizontal."""

    def __init__(self, direction, warn=0.7, duration=2.0, force=250):
        self.dir, self.warn, self.duration, self.force = direction, warn, duration, force
        self.t = 0.0
        self.alive = True
        self.streaks = [(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0.6, 1.4)) for _ in range(40)]

    def update(self, dt, room, player, ctx):
        self.t += dt
        if self.t > self.warn and player.alive:
            k = min(1.0, (self.t - self.warn) / 0.3)
            if player.dashing:
                k *= 0.3          # o dash corta o vento
            grounded = player.on_ground
            move_and_collide(player, self.dir * self.force * k * dt, 0, room)
            player.on_ground = grounded      # empurrar de lado não tira do chão
        if self.t > self.warn + self.duration:
            self.alive = False
        return self.alive

    def draw(self, surf, cam_x, cam_y, time):
        w, h = surf.get_size()
        strong = self.t > self.warn
        col = (210, 230, 255) if strong else (140, 160, 200)
        for fx, fy, sp in self.streaks:
            x = (fx * w + self.dir * time * 900 * sp) % w
            y = fy * h
            ln = 40 if strong else 14
            pygame.draw.line(surf, col, (x, y), (x - self.dir * ln, y), 1)


class CannonShot:
    """Canhonaço do navio: marca o chão e, depois do aviso, uma bala cai do céu e explode."""

    def __init__(self, x, floor_y, warn=1.0):
        self.x, self.floor_y, self.warn = x, floor_y, warn
        self.alive = True

    def update(self, dt, room, player, ctx):
        self.warn -= dt
        if self.warn <= 0:
            ctx.hazards.append(Bomb(self.x, self.floor_y - 460, 0, 900))
            ctx.audio.play("shoot")
            self.alive = False
        return self.alive

    def draw(self, surf, cam_x, cam_y, time):
        x, y = int(self.x - cam_x), int(self.floor_y - cam_y)
        col = (255, 80, 80) if int(time * 16) % 2 else (255, 220, 120)
        r = 14 + int(6 * max(0.0, self.warn))
        pygame.draw.line(surf, col, (x - r, y - 4), (x + r, y - 4), 3)
        pygame.draw.line(surf, col, (x - 8, y - 12), (x + 8, y + 4), 3)
        pygame.draw.line(surf, col, (x + 8, y - 12), (x - 8, y + 4), 3)


# ---------------------------------------------------------------------------
# 1. O Grumete — Rei dos Ratos
# ---------------------------------------------------------------------------

class RatKing(Boss):
    name = "Tico"
    title = "Rei dos Ratos"
    color = (150, 140, 146)
    max_hp = 70

    def __init__(self, foot_x, foot_y):
        super().__init__(foot_x, foot_y, 60, 34)
        self.charge_dir = 1
        self.floor_y = foot_y

    def think(self, dt, room, player, ctx):
        sp = 1.3 if self.phase2 else 1.0
        dx = player.cx - self.cx
        st = self.state
        if st == "sleep":
            self.vx = 0.0
            return
        if st == "idle":
            self.vx = approach(self.vx, 0.0, 1800 * dt)
            self.direction = 1 if dx > 0 else -1
            self.timer -= dt * sp
            if self.timer <= 0 and self.on_ground:
                minions = sum(1 for e in ctx.enemies if isinstance(e, Rat) and e.alive)
                flooding = any(isinstance(h, Flood) for h in ctx.hazards)
                opts, w = ["charge", "flood", "summon", "leap"], [3, 0 if flooding else 3, 2 if minions < 3 else 0,
                                                                  2 if self.phase2 else 0]
                pick = self.choose(opts, w)
                self.state = pick + "_tele"
                self.timer = {"charge": 0.55, "flood": 0.7, "leap": 0.4, "summon": 0.5}[pick] / sp
        elif st == "charge_tele":
            self.vx = approach(self.vx, -self.direction * 50, 1500 * dt)
            self.timer -= dt
            if self.timer <= 0:
                self.state = "charge"
                self.charge_dir = self.direction
                ctx.audio.play("dash")
        elif st == "charge":
            self.vx = self.charge_dir * 430 * sp
            if wall_ahead(self, room, self.charge_dir):
                self.state = "stunned"
                self.timer = 1.1
                self.vx = -self.charge_dir * 140
                self.vy = -260
                ctx.effects.add_shake(9)
                ctx.effects.sprite("fumaca_marrom", self.cx + self.charge_dir * 30, self.cy, fps=18, scale=2)
                ctx.audio.play("impact")
        elif st == "stunned":
            self.vx = approach(self.vx, 0.0, 600 * dt)
            self.timer -= dt
            if self.timer <= 0:
                self.state = "idle"
                self.timer = random.uniform(0.5, 0.8)
        elif st == "leap_tele":
            self.vx = 0.0
            self.squash = min(self.squash, 0.7)
            self.timer -= dt
            if self.timer <= 0:
                self.vy = -820
                self.vx = max(-420.0, min(420.0, dx / 0.75))
                self.state = "leap"
                self.airborne = False
        elif st == "leap":
            if not self.on_ground:
                self.airborne = True
            elif self.airborne:
                self.vx = 0.0
                self.squash = 0.55
                for d in (-1, 1):
                    ctx.projectiles.spawn(self.cx + d * 34, self.bottom - 10, d, 0, speed=280 * sp, look="espinho")
                ctx.effects.add_shake(9)
                ctx.effects.sprite("fumaca_marrom", self.cx, self.bottom - 12, fps=16, scale=2)
                ctx.audio.play("impact")
                self.state = "idle"
                self.timer = random.uniform(0.6, 0.9)
        elif st == "flood_tele":
            # bate o pé e chama a água do porão
            self.vx = 0.0
            self.squash = min(self.squash, 0.8)
            self.timer -= dt
            if self.timer <= 0:
                ctx.hazards.append(Flood(room.width, self.floor_y, height=78 if self.phase2 else 70))
                ctx.effects.add_shake(6)
                ctx.audio.play("boss")
                self.state = "idle"
                self.timer = 1.0
        elif st == "summon_tele":
            self.vx = 0.0
            self.timer -= dt
            if self.timer <= 0:
                for d in (-1, 1):
                    r = Rat(self.cx + d * 50, self.bottom)
                    r.direction = d
                    ctx.spawn_enemy(r)
                ctx.effects.sprite("fumaca_marrom", self.cx, self.bottom - 16, fps=16, scale=2)
                ctx.audio.play("shoot")
                self.state = "idle"
                self.timer = 0.9

    def draw(self, surf, cam_x, cam_y):
        phase = (self.x * 0.03) % 1.0 if abs(self.vx) > 30 else (self.anim_t * 0.8) % 1.0
        img = pixelart.rat(phase, self.direction, scale=2, cap=True, glow=self.awake)
        w = int(img.get_width() * (2 - self.squash))
        h = int(img.get_height() * self.squash)
        img = pygame.transform.scale(sprites.variant(img, False, self.flash > 0 or self.telegraphing()), (w, h))
        surf.blit(img, img.get_rect(midbottom=(round(self.cx - cam_x), round(self.bottom - cam_y + 6))))
        if self.state == "stunned":
            self._stars(surf, cam_x, cam_y)


# ---------------------------------------------------------------------------
# 2. O Imediato — Cavaleiro Rubro (sprite cavaleiro_rubro.png, 2x)
# ---------------------------------------------------------------------------

KNIGHT = "chefes/cavaleiro_rubro.png"
K_ANIMS = {
    "idle": (list(range(0, 6)), 8), "run": (list(range(6, 14)), 14), "jump": ([14, 15], 8),
    "fall": ([16, 17], 8), "crouch": ([20], 1), "raise": ([21, 22], 8), "slash": ([23, 24], 14),
    "recover": ([25, 26], 6), "transform": (list(range(27, 36)), 8), "death": (list(range(36, 49)), 12),
}


class RedKnight(Boss):
    name = "Aldric"
    title = "Cavaleiro Rubro"
    color = (230, 40, 100)
    max_hp = 110

    def __init__(self, foot_x, foot_y):
        super().__init__(foot_x, foot_y, 46, 104)
        self.powered = False
        self.slash_dir = 1
        self.slashes_left = 0

    def think(self, dt, room, player, ctx):
        sp = 1.35 if self.powered else 1.0
        dx = player.cx - self.cx
        st = self.state
        if st == "sleep":
            self.vx = 0.0
            return
        if self.phase2 and not self.powered and st in ("idle", "recover") and self.on_ground:
            self.state = "transform"
            self.timer = 1.2
            self.invulnerable = True
            ctx.effects.add_shake(8)
            ctx.audio.play("boss")
            return
        if st == "transform":
            self.vx = 0.0
            self.timer -= dt
            if int(self.timer * 10) % 3 == 0:
                ctx.effects.burst(self.cx, self.top + 20, 2, (255, 60, 120), speed=(40, 160), gravity=-200)
            if self.timer <= 0:
                self.powered = True
                self.invulnerable = False
                self.state = "idle"
                self.timer = 0.4
            return
        if st == "idle":
            self.direction = 1 if dx > 0 else -1
            # anda devagar na direção do jogador
            target = self.direction * 90 * sp if abs(dx) > 140 else 0.0
            self.vx = approach(self.vx, target, 900 * dt)
            self.timer -= dt * sp
            if self.timer <= 0 and self.on_ground:
                windy = any(isinstance(h, Gust) for h in ctx.hazards)
                pick = self.choose(["slash", "leap", "gust"], [3 if abs(dx) < 380 else 1, 2, 0 if windy else 2])
                if pick == "gust":
                    # ergue a espada e chama o vento do alto do mastro, empurrando para longe dele
                    self.state = "idle"
                    self.timer = 1.4 / sp
                    ctx.hazards.append(Gust(1 if dx > 0 else -1, force=280 if self.powered else 230))
                    ctx.audio.play("dash")
                elif pick == "slash":
                    self.state = "slash_tele"
                    self.timer = 0.5 / sp
                    self.slashes_left = 2 if self.powered else 1
                else:
                    self.state = "leap_tele"
                    self.timer = 0.4 / sp
        elif st == "slash_tele":
            self.vx = approach(self.vx, 0.0, 2000 * dt)
            self.direction = 1 if dx > 0 else -1
            self.timer -= dt
            if self.timer <= 0:
                self.state = "slash"
                self.slash_dir = self.direction
                self.timer = 0.32
                ctx.audio.play("attack_heavy")
                if self.powered:
                    ctx.projectiles.spawn(self.cx + self.slash_dir * 40, self.cy, self.slash_dir, 0, speed=360,
                                          look="espinho")
        elif st == "slash":
            self.vx = self.slash_dir * 620 * sp if not wall_ahead(self, room, self.slash_dir) else 0.0
            self.timer -= dt
            if self.timer <= 0:
                self.slashes_left -= 1
                if self.slashes_left > 0:
                    self.state = "slash_tele"
                    self.timer = 0.25
                else:
                    self.state = "recover"
                    self.timer = 0.7 / sp
        elif st == "recover":
            self.vx = approach(self.vx, 0.0, 1600 * dt)
            self.timer -= dt
            if self.timer <= 0:
                self.state = "idle"
                self.timer = random.uniform(0.5, 0.8)
        elif st == "leap_tele":
            self.vx = 0.0
            self.timer -= dt
            if self.timer <= 0:
                self.vy = -980
                self.vx = max(-460.0, min(460.0, dx / 0.85))
                self.state = "leap"
                self.airborne = False
                ctx.audio.play("jump")
        elif st == "leap":
            if not self.on_ground:
                self.airborne = True
            elif self.airborne:
                self.vx = 0.0
                n = 2 if not self.powered else 3
                for i in range(n):
                    for d in (-1, 1):
                        p = ctx.projectiles.spawn(self.cx + d * (30 + i * 4), self.bottom - 14, d, 0,
                                                  speed=(260 + i * 70) * sp, look="espinho")
                ctx.effects.add_shake(11)
                ctx.effects.sprite("fumaca_marrom", self.cx, self.bottom - 14, fps=16, scale=3)
                ctx.audio.play("boss")
                self.state = "recover"
                self.timer = 0.6

    def anim(self):
        st = self.state
        if st == "transform":
            return "transform", 1.2 - self.timer
        if st in ("slash_tele",):
            return "raise", self.anim_t
        if st == "slash":
            return "slash", 0.32 - self.timer
        if st == "recover":
            return "recover", self.anim_t
        if st == "leap_tele":
            return "crouch", 0
        if st == "leap" or not self.on_ground:
            return ("jump" if self.vy < 0 else "fall"), self.anim_t
        if abs(self.vx) > 30:
            return "run", self.anim_t
        return "idle", self.anim_t

    def draw(self, surf, cam_x, cam_y):
        frames = sprites.grid(KNIGHT, 80, 80)
        if not frames:
            return super().draw(surf, cam_x, cam_y)
        name, t = self.anim()
        idxs, fps = K_ANIMS[name]
        i = idxs[min(len(idxs) - 1, int(t * fps))] if name in ("transform", "slash") else idxs[int(t * fps) % len(idxs)]
        frame = frames[i]
        tint = (255, 150, 190, 255) if self.powered and not self.flash else None
        white = self.flash > 0 or self.telegraphing()
        sprites.blit_anchor(surf, frame, self.cx - cam_x, self.bottom - cam_y, (38, 79),
                            flip=self.direction < 0, white=white, scale=2, tint=tint)
        if self.powered and int(self.anim_t * 10) % 2 == 0:
            pygame.draw.circle(surf, (255, 40, 110), (int(self.cx - cam_x), int(self.top - cam_y + 10)), 3)


# ---------------------------------------------------------------------------
# 3. A Irmã da Capitã — Lâmina da Tempestade (pixel art própria, 2x)
# ---------------------------------------------------------------------------

class PirateSister(Boss):
    name = "Selka"
    title = "Canhoneira da Tempestade"
    color = (190, 50, 60)
    max_hp = 120

    def __init__(self, foot_x, foot_y):
        super().__init__(foot_x, foot_y, 36, 80)
        self.shots_left = 0
        self.shot_timer = 0.0
        self.lunges_left = 0
        self.lunge_dir = 1

    def think(self, dt, room, player, ctx):
        sp = 1.25 if self.phase2 else 1.0
        dx = player.cx - self.cx
        st = self.state
        if st == "sleep":
            self.vx = 0.0
            return
        if st == "idle":
            self.direction = 1 if dx > 0 else -1
            # mantém distância média: recua se o jogador chega muito perto
            if abs(dx) < 110 and self.on_ground:
                self.vy = -700
                self.vx = -self.direction * 300
                self.state = "hop"
                return
            self.vx = approach(self.vx, self.direction * 70 if abs(dx) > 300 else 0.0, 900 * dt)
            self.timer -= dt * sp
            if self.timer <= 0 and self.on_ground:
                pick = self.choose(["pistol", "lunge", "cannon"], [3, 3 if abs(dx) < 420 else 1, 2])
                self.state = pick + "_tele"
                self.timer = {"pistol": 0.45, "lunge": 0.38, "cannon": 0.5}[pick] / sp
                if pick == "lunge":
                    self.lunges_left = 2 if self.phase2 else 1
        elif st == "hop":
            if self.on_ground and self.vy >= 0:
                self.state = "idle"
                self.timer = 0.3
        elif st == "pistol_tele":
            self.vx = 0.0
            self.direction = 1 if dx > 0 else -1
            self.timer -= dt
            if self.timer <= 0:
                self.state = "pistol"
                self.shots_left = 5 if self.phase2 else 3
                self.shot_timer = 0.0
        elif st == "pistol":
            self.shot_timer -= dt
            if self.shot_timer <= 0 and self.shots_left > 0:
                self.shots_left -= 1
                self.shot_timer = 0.17
                ang = math.atan2(player.cy - (self.top + 30), dx) + random.uniform(-0.08, 0.08)
                ctx.projectiles.spawn(self.cx + self.direction * 30, self.top + 30, math.cos(ang), math.sin(ang),
                                      speed=360, look="bala")
                ctx.effects.burst(self.cx + self.direction * 34, self.top + 30, 6, (255, 220, 120),
                                  speed=(60, 160), gravity=0)
                ctx.audio.play("shoot")
            if self.shots_left <= 0 and self.shot_timer <= 0:
                self.state = "idle"
                self.timer = random.uniform(0.6, 0.9)
        elif st == "lunge_tele":
            self.vx = 0.0
            self.direction = 1 if dx > 0 else -1
            self.timer -= dt
            if self.timer <= 0:
                self.state = "lunge"
                self.lunge_dir = self.direction
                self.timer = 0.3
                ctx.audio.play("dash")
        elif st == "lunge":
            self.vx = self.lunge_dir * 660 * sp if not wall_ahead(self, room, self.lunge_dir) else 0.0
            if int(self.timer * 60) % 3 == 0:
                img = sprites.variant(pixelart.human("irma", "attack", 0.7, self.direction), False, False, 2,
                                      tint=(255, 120, 130, 255))
                r = img.get_rect(midbottom=(round(self.cx), round(self.bottom + 2)))
                ctx.effects.ghost(r, (230, 120, 120), img)
            self.timer -= dt
            if self.timer <= 0:
                self.lunges_left -= 1
                if self.lunges_left > 0:
                    self.state = "lunge_tele"
                    self.timer = 0.22
                else:
                    self.state = "recover"
                    self.timer = 0.6
        elif st == "recover":
            self.vx = approach(self.vx, 0.0, 1800 * dt)
            self.timer -= dt
            if self.timer <= 0:
                self.state = "idle"
                self.timer = 0.4
        elif st == "cannon_tele":
            # ergue a pistola e dá o sinal: o navio da irmã dispara sobre as marcas
            self.vx = 0.0
            self.timer -= dt
            if self.timer <= 0:
                n = 5 if self.phase2 else 3
                start = player.cx - (n - 1) / 2 * 110
                for i in range(n):
                    x = max(40, min(room.width - 40, start + i * 110))
                    ctx.hazards.append(CannonShot(x, self.bottom, warn=0.9 + i * 0.18))
                ctx.audio.play("attack_quick")
                self.state = "idle"
                self.timer = random.uniform(1.0, 1.3)

    def draw(self, surf, cam_x, cam_y):
        st = self.state
        if st in ("pistol", "pistol_tele"):
            pose, ph = "shoot", 0
        elif st in ("lunge", "lunge_tele"):
            pose, ph = "attack", 0.0 if st == "lunge_tele" else 0.7
        elif abs(self.vx) > 30:
            pose, ph = "walk", (self.x * 0.02) % 1.0
        else:
            pose, ph = "idle", (self.anim_t * 0.8) % 1.0
        img = pixelart.human("irma", pose, ph, self.direction)
        white = self.flash > 0 or self.telegraphing()
        v = sprites.variant(img, False, white, 2)
        surf.blit(v, v.get_rect(midbottom=(round(self.cx - cam_x), round(self.bottom - cam_y + 2))))


# ---------------------------------------------------------------------------
# 4. O Melhor Amigo — Feiticeiro da Maré (chefe final)
# ---------------------------------------------------------------------------

class Sorcerer(Boss):
    name = "Caelum"
    title = "Feiticeiro da Maré"
    color = (120, 220, 210)
    max_hp = 160
    gravity = False

    def __init__(self, foot_x, foot_y):
        super().__init__(foot_x, foot_y - 120, 36, 80)
        self.floor_y = foot_y
        self.anchors = []
        self.anchor_i = 1
        self.alpha = 255
        self.vy = 0.0

    def setup(self, room):
        w = room.width
        base = self.floor_y - 150
        self.anchors = [(w * 0.22, base), (w * 0.5, base - 70), (w * 0.78, base)]

    def think(self, dt, room, player, ctx):
        if not self.anchors:
            self.setup(room)
        sp = 1.3 if self.phase2 else 1.0
        dx = player.cx - self.cx
        self.direction = 1 if dx > 0 else -1
        st = self.state
        if st == "sleep":
            return
        ax, ay = self.anchors[self.anchor_i]
        bob = math.sin(self.anim_t * 2.2) * 10
        if st not in ("tele_out",):
            self.vx = (ax - self.cx) * 3
            self.vy = (ay + bob - self.cy) * 3
        if st == "idle":
            self.timer -= dt * sp
            if self.timer <= 0:
                decoys = sum(1 for e in ctx.enemies if isinstance(e, Illusion) and e.alive)
                flooding = any(isinstance(h, Flood) for h in ctx.hazards)
                opts, w = ["skulls", "lightning", "teleport", "illusion"], [3, 3, 2, 0 if decoys else 3]
                if self.phase2:
                    opts += ["wave", "summon", "tide"]
                    w += [2, 1 if sum(1 for e in ctx.enemies if isinstance(e, TideSlime)) < 2 else 0,
                          0 if flooding else 2]
                pick = self.choose(opts, w)
                if pick == "teleport":
                    self.state = "tele_out"
                    self.timer = 0.35
                    ctx.effects.sprite("fumaca_caveira", self.cx, self.cy, fps=16, scale=2)
                else:
                    self.state = pick + "_tele"
                    self.timer = {"skulls": 0.55, "lightning": 0.45, "wave": 0.5, "summon": 0.5,
                                  "illusion": 0.6, "tide": 0.7}[pick] / sp
        elif st == "tele_out":
            self.vx = self.vy = 0.0
            self.timer -= dt
            self.alpha = int(255 * max(0.0, self.timer / 0.35))
            if self.timer <= 0:
                choices = [i for i in range(len(self.anchors)) if i != self.anchor_i]
                self.anchor_i = random.choice(choices)
                nx, ny = self.anchors[self.anchor_i]
                self.x, self.y = nx - self.w / 2, ny - self.h / 2
                self.alpha = 255
                self.state = "idle"
                self.timer = 0.5
                ctx.effects.sprite("raio_explosao", self.cx, self.cy, fps=18, scale=2)
        elif st == "skulls_tele":
            self.timer -= dt
            if self.timer <= 0:
                n = 5 if self.phase2 else 3
                base = math.atan2(player.cy - self.cy, dx)
                for i in range(n):
                    a = base + (i - (n - 1) / 2) * 0.35
                    ctx.projectiles.spawn(self.cx, self.cy, math.cos(a), math.sin(a), speed=170, look="caveira",
                                          homing=1.5)
                ctx.audio.play("shoot")
                self.state = "idle"
                self.timer = random.uniform(0.8, 1.1)
        elif st == "lightning_tele":
            self.timer -= dt
            if self.timer <= 0:
                n = 5 if self.phase2 else 3
                for i in range(n):
                    x = player.cx + (i - (n - 1) / 2) * 110
                    if 20 < x < room.width - 20:
                        ctx.hazards.append(Lightning(x, self.floor_y, warn=0.8 + i * 0.05))
                self.state = "idle"
                self.timer = random.uniform(1.0, 1.3)
        elif st == "wave_tele":
            self.timer -= dt
            if self.timer <= 0:
                side = -1 if player.cx > room.width / 2 else 1
                start = 40 if side > 0 else room.width - 40
                ctx.hazards.append(Wave(start, self.floor_y, side, speed=320))
                ctx.audio.play("boss")
                self.state = "idle"
                self.timer = 1.2
        elif st == "illusion_tele":
            # cria cópias de si nas outras âncoras; acertar o verdadeiro desfaz as ilusões
            self.timer -= dt
            if self.timer <= 0:
                for i, (ax2, ay2) in enumerate(self.anchors):
                    if i != self.anchor_i:
                        ctx.spawn_enemy(Illusion(ax2, ay2 + 40, self))
                        ctx.effects.sprite("fumaca_caveira", ax2, ay2, fps=16, scale=2)
                ctx.audio.play("boss")
                self.state = "idle"
                self.timer = 1.0
        elif st == "tide_tele":
            self.timer -= dt
            if self.timer <= 0:
                ctx.hazards.append(Flood(room.width, self.floor_y, height=70, hold=3.0))
                ctx.effects.add_shake(7)
                ctx.audio.play("boss")
                self.state = "idle"
                self.timer = 1.0
        elif st == "summon_tele":
            self.timer -= dt
            if self.timer <= 0:
                for d in (-1, 1):
                    sx = max(60, min(room.width - 60, player.cx + d * 220))
                    ctx.spawn_enemy(TideSlime(sx, self.floor_y))
                    ctx.effects.sprite("fumaca_caveira", sx, self.floor_y - 20, fps=16)
                self.state = "idle"
                self.timer = 1.0

    def take_hit(self, damage, direction, knockback, knock_up, stun, ctx):
        was = self.hp
        super().take_hit(damage, direction, knockback, knock_up, stun, ctx)
        if self.hp < was:                       # acertou o verdadeiro: as ilusões se desfazem
            for e in ctx.enemies:
                if isinstance(e, Illusion) and e.alive:
                    e.vanish(ctx)

    def draw(self, surf, cam_x, cam_y):
        from .creatures import draw_model
        lean = 12 if self.state.endswith("_tele") else 0
        draw_model(surf, "mago_azul", self.cx - cam_x, self.bottom - cam_y, self.anim_t, self.direction,
                   white=self.flash > 0 or self.telegraphing(), lean=lean, float_amp=3.0, scale=1.25,
                   alpha=self.alpha)
        # brilho da maré nas mãos e sombra no chão (as ilusões não têm sombra)
        k = 0.5 + 0.5 * math.sin(self.anim_t * 5)
        pygame.draw.circle(surf, (int(90 + 120 * k), 220, 230), (round(self.cx - cam_x + self.direction * 20),
                                                                 round(self.cy - cam_y + 4)), 4)
        shadow = pygame.Rect(0, 0, 50, 8)
        shadow.center = (round(self.cx - cam_x), round(self.floor_y - cam_y - 2))
        pygame.draw.ellipse(surf, (20, 60, 70), shadow)


class Illusion(Enemy):
    """Cópia de Caelum: atira caveiras, some com um golpe. Não tem sombra no chão (a dica)."""
    gravity = False
    max_hp = 1
    contact_damage = 1
    knockback_resist = 0.0
    color = (120, 220, 210)

    def __init__(self, x, foot_y, master):
        super().__init__(x, foot_y, 36, 80)
        self.master = master
        self.cool = random.uniform(1.0, 1.8)
        self.t = 0.0

    def think(self, dt, room, player, ctx):
        self.t += dt
        self.vx = self.vy = 0.0
        self.direction = 1 if player.cx > self.cx else -1
        self.cool -= dt
        if self.cool <= 0:
            self.cool = 2.4
            a = math.atan2(player.cy - self.cy, player.cx - self.cx)
            ctx.projectiles.spawn(self.cx, self.cy, math.cos(a), math.sin(a), speed=150, look="caveira", homing=0.8)
        if not self.master.alive:
            self.alive = False

    def vanish(self, ctx):
        self.alive = False
        ctx.effects.sprite("fumaca_caveira", self.cx, self.cy, fps=18, scale=2)

    def draw(self, surf, cam_x, cam_y):
        from .creatures import draw_model
        draw_model(surf, "mago_azul", self.cx - cam_x, self.bottom - cam_y, self.t, self.direction,
                   white=self.flash > 0, float_amp=3.0, scale=1.25, alpha=200 + int(40 * math.sin(self.t * 9)))


BOSS_CLASSES = {"rei_rato": RatKing, "cavaleiro": RedKnight, "irma": PirateSister, "feiticeiro": Sorcerer}
