"""Camadas de paisagem desenhadas no código (parallax): montanhas, névoa, nuvens, castelo distante,
raios de luz, folhagem de primeiro plano e o interior do templo (arcos, colunas, correntes e runas).

Cada camada é gerada uma vez e guardada em cache; o fundo só desloca as imagens.
"""

import math
import random

import pygame

from .config import Display

W, H = Display.WIDTH, Display.HEIGHT
_cache = {}


def _cached(key, build):
    if key not in _cache:
        _cache[key] = build()
    return _cache[key]


def _shade(c, d):
    return tuple(max(0, min(255, v + d)) for v in c)


def mountains(seed, color, height, rough=1.0, width=W * 2, snow=None):
    """Cordilheira com picos irregulares e um lado mais claro (luz da lua)."""
    def build():
        rnd = random.Random(seed)
        s = pygame.Surface((width, height), pygame.SRCALPHA)
        pts = [(0, height)]
        x, y = 0, height * rnd.uniform(0.3, 0.6)
        peaks = []
        while x <= width:
            pts.append((x, y))
            if rnd.random() < 0.25:
                peaks.append((x, y))
            x += rnd.randint(18, 46)
            y = max(height * 0.08, min(height * 0.85, y + rnd.uniform(-60, 60) * rough))
        pts += [(width, pts[-1][1]), (width, height)]
        pygame.draw.polygon(s, color, pts)
        light = _shade(color, 16)
        for i in range(1, len(pts) - 3):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            if y1 > y0:          # encosta que desce para a direita recebe luz
                pygame.draw.polygon(s, light, [(x0, y0), (x1, y1), (x1, y1 + 30), (x0, y0 + 10)])
        if snow:
            for x0, y0 in peaks:
                pygame.draw.polygon(s, snow, [(x0 - 9, y0 + 12), (x0, y0), (x0 + 9, y0 + 12), (x0 + 3, y0 + 9),
                                              (x0 - 3, y0 + 13)])
        return s
    return _cached(("mont", seed, color, height, rough, width, snow), build)


def castle(seed, color, glow):
    """Silhueta de castelo/torre distante com janelas acesas."""
    def build():
        rnd = random.Random(seed)
        s = pygame.Surface((420, 260), pygame.SRCALPHA)
        base = 260
        x = 20
        while x < 400:
            w = rnd.randint(30, 60)
            h = rnd.randint(80, 200)
            pygame.draw.rect(s, color, (x, base - h, w, h))
            # ameias
            for k in range(x, x + w, 8):
                pygame.draw.rect(s, color, (k, base - h - 6, 5, 6))
            if rnd.random() < 0.5:   # telhado pontudo
                pygame.draw.polygon(s, color, [(x - 4, base - h), (x + w + 4, base - h), (x + w // 2, base - h - 50)])
            for _ in range(rnd.randint(1, 4)):
                wx = rnd.randint(x + 6, x + w - 10)
                wy = rnd.randint(base - h + 14, base - 30)
                pygame.draw.rect(s, glow, (wx, wy, 4, 7))
            x += w + rnd.randint(-10, 20)
        pygame.draw.rect(s, color, (0, base - 40, 420, 40))
        return s
    return _cached(("castle", seed, color, glow), build)


def clouds(seed, color, count=7, width=W * 2, height=220):
    def build():
        rnd = random.Random(seed)
        s = pygame.Surface((width, height), pygame.SRCALPHA)
        for _ in range(count):
            cx, cy = rnd.uniform(0, width), rnd.uniform(20, height - 40)
            for _ in range(rnd.randint(5, 9)):
                r = rnd.randint(14, 34)
                pygame.draw.circle(s, color, (int(cx + rnd.uniform(-60, 60)), int(cy + rnd.uniform(-10, 10))), r)
        return s
    return _cached(("clouds", seed, color, count, width, height), build)


def mist(color, alpha, height=90, width=W * 2):
    """Faixa de névoa com borda suave."""
    def build():
        s = pygame.Surface((width, height), pygame.SRCALPHA)
        for y in range(height):
            k = 1 - abs(y - height / 2) / (height / 2)
            a = int(alpha * k ** 1.5)
            pygame.draw.line(s, color + (a,), (0, y), (width, y))
        return s
    return _cached(("mist", color, alpha, height, width), build)


def light_rays(color, count=5, seed=1):
    """Fachos de luz diagonais (desenhados com BLEND_RGB_ADD)."""
    def build():
        rnd = random.Random(seed)
        s = pygame.Surface((W, H))
        s.fill((0, 0, 0))
        for _ in range(count):
            x = rnd.uniform(-100, W)
            w = rnd.uniform(30, 90)
            k = rnd.uniform(0.25, 0.55)
            col = tuple(int(c * k) for c in color)
            for i in range(6):
                f = (6 - i) / 6
                c2 = tuple(int(v * f * 0.35) for v in col)
                off = i * w / 10
                pygame.draw.polygon(s, c2, [(x + off, 0), (x + w - off, 0), (x + w - off + 260, H), (x + off + 260, H)])
        return s
    return _cached(("rays", color, count, seed), build)


def foliage(seed, color, width=W * 2, height=120):
    """Folhagem escura de primeiro plano (borda de baixo da tela)."""
    def build():
        rnd = random.Random(seed)
        s = pygame.Surface((width, height), pygame.SRCALPHA)
        x = 0
        while x < width:
            r = rnd.randint(18, 46)
            pygame.draw.circle(s, color, (x, height - rnd.randint(0, 30)), r)
            if rnd.random() < 0.3:   # folha comprida
                pygame.draw.polygon(s, color, [(x, height), (x + rnd.randint(-20, 20), height - rnd.randint(60, 110)),
                                               (x + 12, height)])
            x += rnd.randint(20, 50)
        pygame.draw.rect(s, color, (0, height - 20, width, 20))
        return s
    return _cached(("foliage", seed, color, width, height), build)


def canopy(seed, color, width=W * 2, height=90):
    """Galhos com cachos de folhas pendendo da borda de cima da tela (primeiro plano)."""
    def build():
        rnd = random.Random(seed)
        s = pygame.Surface((width, height), pygame.SRCALPHA)
        claro = tuple(min(255, c + 14) for c in color[:3]) + (255,)
        x = rnd.randint(0, 40)
        while x < width:
            # galho que desce e cachos de folhas compridas ao longo dele
            comp = rnd.randint(24, 70)
            dx = rnd.randint(-18, 18)
            pygame.draw.line(s, color, (x, 0), (x + dx, comp), 2)
            for k in range(rnd.randint(4, 8)):
                t = rnd.uniform(0.2, 1.0)
                fx, fy = x + dx * t, comp * t
                lado = rnd.choice((-1, 1))
                folha = [(fx, fy), (fx + lado * 9, fy + 3), (fx + lado * 12, fy + 9), (fx + lado * 4, fy + 6)]
                pygame.draw.polygon(s, claro if k % 3 == 0 else color, folha)
            x += rnd.randint(50, 140)
        return s
    return _cached(("canopy", seed, color, width, height), build)


def broken_column(seed, color, height):
    """Toco de coluna quebrada (silhueta) com ponta irregular e capitel caído ao lado."""
    def build():
        rnd = random.Random(seed)
        w = 34
        s = pygame.Surface((w + 30, height), pygame.SRCALPHA)
        pygame.draw.rect(s, color, (6, 10, w - 12, height - 10))
        pygame.draw.rect(s, color, (2, height - 10, w - 4, 10))          # base
        topo = [(6, 10)]
        for k in range(1, 6):
            topo.append((6 + k * (w - 12) / 5, rnd.randint(0, 12)))
        topo.append((w - 6, 10))
        pygame.draw.polygon(s, color, topo + [(w - 6, 14), (6, 14)])
        pygame.draw.rect(s, color, (w - 2, height - 12, 24, 12), border_radius=3)   # pedaço caído
        return s
    return _cached(("coluna", seed, color, height), build)


def temple_hall(seed, wall, pillar, rune):
    """Parede do fundo do templo: arcos, colunas, correntes e runas que brilham."""
    def build():
        rnd = random.Random(seed)
        s = pygame.Surface((W * 2, H), pygame.SRCALPHA)
        s.fill(wall + (255,))
        # tijolos grandes
        for y in range(0, H, 28):
            off = 0 if (y // 28) % 2 else 22
            for x in range(-44 + off, W * 2, 44):
                pygame.draw.rect(s, _shade(wall, -6), (x, y, 44, 28), 1)
                if rnd.random() < 0.15:
                    pygame.draw.line(s, _shade(wall, -14), (x + 6, y + 6), (x + 18, y + 20), 1)
        dark = _shade(wall, -18)
        for i, x in enumerate(range(60, W * 2, 260)):
            # arco
            pygame.draw.rect(s, dark, (x, 140, 150, H))
            pygame.draw.ellipse(s, dark, (x, 70, 150, 150))
            pygame.draw.ellipse(s, _shade(wall, 10), (x - 8, 62, 166, 166), 4)
            # colunas
            for px in (x - 34, x + 162):
                pygame.draw.rect(s, pillar, (px, 40, 22, H))
                pygame.draw.rect(s, _shade(pillar, 16), (px + 3, 40, 4, H))
                pygame.draw.rect(s, _shade(pillar, -20), (px - 4, 34, 30, 10))
            # runa que brilha dentro do arco
            cx, cy = x + 75, 150
            pygame.draw.circle(s, rune, (cx, cy), 18, 2)
            pygame.draw.line(s, rune, (cx, cy - 12), (cx, cy + 12), 2)
            pygame.draw.line(s, rune, (cx - 10, cy + 4), (cx + 10, cy - 4), 2)
            # correntes
            for chx in (x + 20, x + 130):
                for cy2 in range(0, rnd.randint(60, 140), 8):
                    pygame.draw.ellipse(s, _shade(pillar, -10), (chx - 2, cy2, 5, 8), 1)
        return s
    return _cached(("hall", seed, wall, pillar, rune), build)


def ruins_layer(seed, color):
    """Colunas quebradas e arcos em ruínas (silhueta)."""
    def build():
        rnd = random.Random(seed)
        s = pygame.Surface((W * 2, 300), pygame.SRCALPHA)
        x = 0
        while x < W * 2:
            h = rnd.randint(90, 260)
            w = rnd.randint(22, 34)
            pygame.draw.rect(s, color, (x, 300 - h, w, h))
            # topo quebrado
            pygame.draw.polygon(s, (0, 0, 0, 0), [(x, 300 - h), (x + w, 300 - h), (x + w, 300 - h + rnd.randint(4, 16))])
            if rnd.random() < 0.4:
                span = rnd.randint(80, 140)
                pygame.draw.arc(s, color, (x, 300 - h - 30, span, 90), 0, math.pi, 12)
            x += rnd.randint(70, 160)
        return s
    return _cached(("ruinslayer", seed, color), build)


def tile_layer(surf, x_off, y, period=None):
    """Desenha uma camada repetida na horizontal."""
    w = surf.get_width()
    x = -(x_off % w)
    while x < W:
        yield x, y
        x += w
