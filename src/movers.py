"""Plataformas móveis: vão e voltam entre dois pontos, carregando o jogador."""

import math

import pygame

from .config import World

T = World.TILE


class Mover:
    HEIGHT = 12

    def __init__(self, spec):
        self.x0, self.y0 = spec["x0"] * T, spec["y0"] * T
        self.x1, self.y1 = spec["x1"] * T, spec["y1"] * T
        self.w = spec.get("w", 3) * T
        self.h = self.HEIGHT
        self.speed = spec.get("speed", 90)
        dist = math.hypot(self.x1 - self.x0, self.y1 - self.y0) or 1.0
        self.period = 2 * dist / self.speed + 1.0      # ida + volta + 2 pausas de 0,5 s
        self.t = 0.0
        self.x, self.y = float(self.x0), float(self.y0)
        self.dx = self.dy = 0.0

    def _pos(self, t):
        # ida e volta; em cada ponta fica 0,5 s parado; saída e chegada suaves
        half = self.period / 2
        travel = half - 0.5
        tau = t % self.period
        leg = tau if tau < half else tau - half
        k = min(1.0, max(0.0, (leg - 0.25) / travel)) if travel > 0 else 1.0
        k = k * k * (3 - 2 * k)
        if tau >= half:
            k = 1.0 - k
        return self.x0 + (self.x1 - self.x0) * k, self.y0 + (self.y1 - self.y0) * k

    def update(self, dt):
        self.t += dt
        nx, ny = self._pos(self.t)
        self.dx, self.dy = nx - self.x, ny - self.y
        self.x, self.y = nx, ny

    def rect(self):
        return (self.x, self.y, self.w, self.h)

    def draw(self, surf, cam_x, cam_y, island=False):
        r = pygame.Rect(round(self.x - cam_x), round(self.y - cam_y), int(self.w), self.h)
        wood, dark, light = ((112, 84, 52), (60, 42, 28), (160, 124, 80)) if island else ((132, 92, 56), (70, 46, 30), (180, 132, 84))
        pygame.draw.rect(surf, wood, r, border_radius=3)
        pygame.draw.line(surf, light, (r.left + 2, r.top), (r.right - 3, r.top))
        pygame.draw.rect(surf, dark, r, 2, border_radius=3)
        for x in range(r.left + 10, r.right - 4, 24):
            pygame.draw.line(surf, dark, (x, r.top + 2), (x, r.bottom - 3))
        # cordas até o alto (polias)
        for x in (r.left + 6, r.right - 7):
            pygame.draw.line(surf, (150, 128, 90), (x, r.top), (x, r.top - 40), 1)
