"""Partículas, rastros de dash, tremor de tela e hitstop."""

import math
import random

import pygame

from .config import Effects as FX


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "size", "color", "gravity", "drag", "shape")

    def __init__(self, x, y, vx, vy, life, size, color, gravity=0.0, drag=0.0, shape="square"):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.life = self.max_life = life
        self.size = size
        self.color = color
        self.gravity = gravity
        self.drag = drag
        self.shape = shape


class Ghost:
    """Silhueta que fica para trás durante o dash."""
    __slots__ = ("rect", "life", "max_life", "color")

    def __init__(self, rect, life, color):
        self.rect = rect
        self.life = self.max_life = life
        self.color = color


class Ring:
    __slots__ = ("x", "y", "radius", "max_radius", "life", "max_life", "color", "width")

    def __init__(self, x, y, max_radius, life, color, width=3):
        self.x, self.y = x, y
        self.radius = 2
        self.max_radius = max_radius
        self.life = self.max_life = life
        self.color = color
        self.width = width


class EffectSystem:
    def __init__(self):
        self.particles = []
        self.ghosts = []
        self.rings = []
        self.shake = 0.0
        self.hitstop = 0.0
        self.screen_flash = 0.0
        self.screen_flash_color = (255, 255, 255)

    def clear(self):
        self.particles.clear()
        self.ghosts.clear()
        self.rings.clear()
        self.shake = 0.0
        self.hitstop = 0.0
        self.screen_flash = 0.0

    # --- disparadores ---
    def add_shake(self, amount):
        if FX.ENABLE_SHAKE:
            self.shake = min(14.0, max(self.shake, amount))

    def add_hitstop(self, duration):
        if FX.ENABLE_HITSTOP:
            self.hitstop = max(self.hitstop, duration)

    def flash(self, duration, color):
        self.screen_flash = duration
        self.screen_flash_color = color

    def _add(self, p):
        if len(self.particles) < FX.MAX_PARTICLES:
            self.particles.append(p)

    def burst(self, x, y, count, color, speed=(60, 220), life=(0.2, 0.45), size=(2, 4),
              gravity=600.0, angle=None, spread=math.pi * 2, drag=2.0):
        for _ in range(count):
            a = random.uniform(0, math.tau) if angle is None else angle + random.uniform(-spread / 2, spread / 2)
            s = random.uniform(*speed)
            self._add(Particle(x, y, math.cos(a) * s, math.sin(a) * s, random.uniform(*life),
                               random.uniform(*size), color, gravity, drag))

    def dust(self, x, y, count=6, direction=0, color=(170, 170, 190)):
        for _ in range(count):
            vx = random.uniform(-90, 90) + direction * random.uniform(40, 120)
            vy = random.uniform(-70, -10)
            self._add(Particle(x + random.uniform(-6, 6), y, vx, vy, random.uniform(0.18, 0.35),
                               random.uniform(2, 4), color, 200.0, 4.0))

    def ghost(self, rect, color):
        self.ghosts.append(Ghost(pygame.Rect(rect), 0.16, color))

    def ring(self, x, y, radius, life, color, width=3):
        self.rings.append(Ring(x, y, radius, life, color, width))

    # --- atualização ---
    def update_timers(self, dt):
        """Tremor e flash correm mesmo durante o hitstop."""
        self.shake = max(0.0, self.shake - FX.SHAKE_DECAY * dt)
        self.screen_flash = max(0.0, self.screen_flash - dt)

    def update(self, dt):
        alive = []
        for p in self.particles:
            p.life -= dt
            if p.life <= 0:
                continue
            p.vy += p.gravity * dt
            damp = max(0.0, 1.0 - p.drag * dt)
            p.vx *= damp
            p.vy *= damp
            p.x += p.vx * dt
            p.y += p.vy * dt
            alive.append(p)
        self.particles = alive
        for g in self.ghosts:
            g.life -= dt
        self.ghosts = [g for g in self.ghosts if g.life > 0]
        for r in self.rings:
            r.life -= dt
            k = 1.0 - r.life / r.max_life
            r.radius = 2 + (r.max_radius - 2) * (1 - (1 - k) ** 2)
        self.rings = [r for r in self.rings if r.life > 0]

    def shake_offset(self):
        if self.shake <= 0:
            return 0, 0
        return (random.uniform(-self.shake, self.shake), random.uniform(-self.shake, self.shake))

    # --- desenho ---
    def draw_world(self, surf, cam_x, cam_y):
        for g in self.ghosts:
            k = g.life / g.max_life
            s = pygame.Surface((g.rect.w, g.rect.h), pygame.SRCALPHA)
            s.fill((*g.color, int(120 * k)))
            surf.blit(s, (g.rect.x - cam_x, g.rect.y - cam_y))
        for r in self.rings:
            k = r.life / r.max_life
            col = tuple(int(c * (0.4 + 0.6 * k)) for c in r.color)
            pygame.draw.circle(surf, col, (int(r.x - cam_x), int(r.y - cam_y)), int(r.radius),
                               max(1, int(r.width * k + 0.5)))
        for p in self.particles:
            k = p.life / p.max_life
            size = max(1, int(p.size * (0.4 + 0.6 * k) + 0.5))
            pygame.draw.rect(surf, p.color, (int(p.x - cam_x - size / 2), int(p.y - cam_y - size / 2), size, size))

    def draw_overlay(self, surf):
        if self.screen_flash > 0:
            s = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            s.fill((*self.screen_flash_color, int(min(1.0, self.screen_flash / 0.12) * 70)))
            surf.blit(s, (0, 0))
