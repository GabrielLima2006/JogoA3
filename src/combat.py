"""Golpes, hitboxes, projéteis e regras de dano."""

import itertools
import math

import pygame

from .config import Colors, Combat, Enemies, Energy, Projectile as PCfg, World
from .physics import rects_overlap
from .world import BREAKABLE

_attack_ids = itertools.count(1)


class Attack:
    """Instância de um golpe em andamento: preparação -> ativo -> recuperação."""

    def __init__(self, spec, facing, aim=None):
        self.spec = spec
        self.facing = facing
        self.aim = aim or (facing, 0)   # (dx, dy): frente, cima, baixo ou diagonal
        self.pogoed = False
        self.t = 0.0
        self.id = next(_attack_ids)
        self.hit_ids = set()       # cada inimigo só leva dano uma vez por golpe
        self.lunged = False

    @property
    def phase(self):
        s = self.spec
        if self.t < s.windup:
            return "windup"
        if self.t < s.windup + s.active:
            return "active"
        if self.t < s.total:
            return "recovery"
        return "done"

    @property
    def phase_progress(self):
        s = self.spec
        ph = self.phase
        if ph == "windup":
            return self.t / s.windup if s.windup else 1.0
        if ph == "active":
            return (self.t - s.windup) / s.active
        if ph == "recovery":
            return (self.t - s.windup - s.active) / s.recovery
        return 1.0

    def update(self, dt):
        self.t += dt

    def hitbox(self, body):
        s = self.spec
        dx, dy = self.aim
        if dy == 0:
            y = body.cy + s.hit_offset_y - s.hit_h / 2
            if dx > 0:
                x = body.right + s.hit_offset_x
            else:
                x = body.left - s.hit_offset_x - s.hit_w
            return (x, y, s.hit_w, s.hit_h)
        if dx == 0:
            # vertical: a hitbox "deitada" vira de pé
            w, h = s.hit_h + 8, s.hit_w
            y = body.top - h - s.hit_offset_x if dy < 0 else body.bottom + s.hit_offset_x
            return (body.cx - w / 2, y, w, h)
        # diagonal: quadrado encostado na quina do corpo
        size = (s.hit_w + s.hit_h) / 2
        cx = body.cx + dx * (body.w / 2 + size * 0.3)
        cy = body.cy + dy * (body.h / 2 + size * 0.3)
        return (cx - size / 2, cy - size / 2, size, size)


def resolve_player_attack(player, enemies, projectiles, ctx):
    atk = player.attack
    if atk is None or atk.phase != "active":
        return
    box = atk.hitbox(player)
    spec = atk.spec
    adx, ady = atk.aim
    landed = False
    for enemy in enemies:
        if not enemy.alive or enemy.uid in atk.hit_ids:
            continue
        if rects_overlap(box, enemy.rect_tuple()):
            atk.hit_ids.add(enemy.uid)
            hx = (max(box[0], enemy.left) + min(box[0] + box[2], enemy.right)) / 2
            hy = (max(box[1], enemy.top) + min(box[1] + box[3], enemy.bottom)) / 2
            direction = adx if adx else (1 if enemy.cx >= player.cx else -1)
            if enemy.blocks(spec, adx):
                # defendido: faísca metálica e o jogador é empurrado
                player.vx = -direction * Enemies.SHIELD_BLOCK_RECOIL
                ctx.effects.burst(hx, hy, 12, (220, 230, 255), speed=(100, 300), gravity=300)
                ctx.effects.add_hitstop(0.05)
                ctx.audio.play("block")
                continue
            knock_up = max(spec.knock_up, 300.0) if ady < 0 else (0.0 if ady > 0 else spec.knock_up)
            enemy.take_hit(spec.damage, direction, spec.knockback, knock_up, spec.stun, ctx)
            if ady and not enemy.gravity:
                enemy.vy = ady * spec.knockback * 0.8 * enemy.knockback_resist
            player.gain_energy(Energy.PER_HIT_HEAVY if spec.name == "heavy" else Energy.PER_HIT_QUICK)
            landed = True
            if spec.name == "heavy":
                ctx.effects.burst(hx, hy, 22, Colors.HEAVY_SLASH, speed=(120, 420), gravity=500,
                                  angle=math.atan2(ady, adx), spread=math.pi * 1.1)
                ctx.effects.ring(hx, hy, 34, 0.22, Colors.HEAVY_SLASH, 4)
                ctx.audio.play("heavy_hit")
            else:
                ctx.effects.burst(hx, hy, 10, Colors.QUICK_SLASH, speed=(80, 260), gravity=400,
                                  angle=math.atan2(ady, adx), spread=math.pi * 0.9)
                ctx.audio.play("hit")
    if Combat.PLAYER_PROJECTILE_PARRY:
        for p in projectiles.items:
            if p.alive and p.hostile and rects_overlap(box, p.rect_tuple()):
                p.alive = False
                ctx.effects.burst(p.x, p.y, 8, Colors.PROJECTILE, speed=(60, 200))
                landed = True
    # paredes quebráveis
    room = ctx.room
    T = World.TILE
    for ty in range(int(box[1] // T), int((box[1] + box[3]) // T) + 1):
        for tx in range(int(box[0] // T), int((box[0] + box[2]) // T) + 1):
            if room.tile(tx, ty) == BREAKABLE and (tx, ty) not in room.broken:
                ctx.break_tile(tx, ty)
                landed = True
    # golpe para baixo quica em inimigos, projéteis, paredes quebráveis e espinhos
    if ady > 0 and not atk.pogoed:
        spikes = room.spike_rects(box[0], box[1], box[0] + box[2], box[1] + box[3], water=False)
        if landed or any(rects_overlap(box, r) for r in spikes):
            atk.pogoed = True
            player.pogo(ctx)
    if landed:
        ctx.effects.add_hitstop(spec.hitstop)
        if spec.shake:
            ctx.effects.add_shake(spec.shake)
        player.on_attack_landed(spec)


class ProjectileObj:
    def __init__(self, x, y, vx, vy, damage, hostile=True):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.damage = damage
        self.hostile = hostile
        self.life = PCfg.LIFETIME
        self.alive = True
        self.r = PCfg.RADIUS

    def rect_tuple(self):
        return (self.x - self.r, self.y - self.r, self.r * 2, self.r * 2)


class ProjectileSystem:
    def __init__(self):
        self.items = []

    def clear(self):
        self.items.clear()

    def spawn(self, x, y, dir_x, dir_y, speed=PCfg.SPEED, damage=PCfg.DAMAGE, hostile=True):
        if len(self.items) >= PCfg.MAX_ACTIVE:
            return None
        n = math.hypot(dir_x, dir_y) or 1.0
        p = ProjectileObj(x, y, dir_x / n * speed, dir_y / n * speed, damage, hostile)
        self.items.append(p)
        return p

    def update(self, dt, room, player, ctx):
        T = World.TILE
        for p in self.items:
            if not p.alive:
                continue
            p.life -= dt
            if p.life <= 0:
                p.alive = False
                continue
            # sub-passos para não atravessar paredes finas
            dist = math.hypot(p.vx, p.vy) * dt
            steps = max(1, int(dist / 6) + 1)
            for _ in range(steps):
                p.x += p.vx * dt / steps
                p.y += p.vy * dt / steps
                if room.is_solid(int(p.x // T), int(p.y // T)):
                    p.alive = False
                    ctx.effects.burst(p.x - p.vx * dt / steps, p.y - p.vy * dt / steps, 8,
                                      Colors.PROJECTILE, speed=(40, 160), gravity=300)
                    ctx.audio.play("impact")
                    break
            if not p.alive:
                continue
            if not (-64 <= p.x <= room.width + 64 and -64 <= p.y <= room.height + 64):
                p.alive = False
                continue
            # jogador invulnerável (ex.: durante o dash) é atravessado pelo projétil
            if p.hostile and player.alive and rects_overlap(p.rect_tuple(), player.rect_tuple()):
                if player.take_hit(p.damage, p.x, ctx):
                    p.alive = False
                    ctx.effects.burst(p.x, p.y, 10, Colors.PROJECTILE, speed=(60, 200))
        self.items = [p for p in self.items if p.alive]

    def draw(self, surf, cam_x, cam_y):
        for p in self.items:
            pos = (int(p.x - cam_x), int(p.y - cam_y))
            pygame.draw.circle(surf, (255, 210, 150), pos, p.r)
            pygame.draw.circle(surf, Colors.PROJECTILE, pos, p.r, 2)
