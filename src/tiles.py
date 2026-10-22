"""Blocos do cenário (32x32) por tema.

Navio: madeira em pixel art feita aqui no código (tábuas, juntas, pregos, veio).
Ilha e templo: recortes do tileset "forgotten forest" (assets/img/tiles/ilha.png).
Cada tema tem: topo (bloco com ar em cima), recheio, plataforma de mão única.
"""

import random

import pygame

from . import sprites

T = 32
ISLAND = "tiles/ilha.png"

# tema de cada zona da sala
ZONE_THEME = {
    "convés": "deck", "interior": "hull", "porão": "bilge",
    "ilha": "island", "ruínas": "ruins", "templo": "temple",
    # mundo de testes (cavernas) usa madeira escura também
    "cavernas": "hull", "vila": "hull", "arena": "bilge", "jardins": "island", "alturas": "ruins",
}

WOOD = {
    #         base           escuro         claro           prego
    "deck": ((132, 88, 52), (78, 48, 30), (176, 126, 78), (60, 60, 70)),
    "hull": ((96, 62, 40), (54, 34, 24), (138, 96, 62), (52, 52, 60)),
    "bilge": ((70, 54, 44), (38, 30, 28), (104, 84, 66), (40, 46, 50)),
}

_cache = {}


def _shade(c, d):
    return tuple(max(0, min(255, v + d)) for v in c)


def _wood_tile(palette, seed, top=False, vertical=False):
    base, dark, light, nail = palette
    rnd = random.Random(seed)
    s = pygame.Surface((T, T))
    plank = 8
    for row in range(T // plank):
        tone = rnd.randint(-10, 10)
        col = _shade(base, tone)
        y0 = row * plank
        pygame.draw.rect(s, col, (0, y0, T, plank))
        # veio da madeira
        for _ in range(4):
            gx, gy = rnd.randrange(T), y0 + rnd.randrange(1, plank - 1)
            pygame.draw.line(s, _shade(col, -16), (gx, gy), (min(T - 1, gx + rnd.randint(3, 9)), gy))
        # brilho no topo da tábua e junta embaixo
        pygame.draw.line(s, _shade(col, 18), (0, y0), (T - 1, y0))
        pygame.draw.line(s, dark, (0, y0 + plank - 1), (T - 1, y0 + plank - 1))
        # emenda vertical com pregos
        jx = rnd.randrange(6, T - 6)
        pygame.draw.line(s, dark, (jx, y0), (jx, y0 + plank - 2))
        for nx in (jx - 2, jx + 2):
            s.set_at((nx, y0 + 3), nail)
    if vertical:
        s = pygame.transform.rotate(s, 90)
    if top:
        pygame.draw.rect(s, light, (0, 0, T, 2))
        pygame.draw.line(s, _shade(light, 25), (0, 0), (T - 1, 0))
        pygame.draw.line(s, dark, (0, 3), (T - 1, 3))
    return s


def _oneway_wood(palette):
    base, dark, light, nail = palette
    s = pygame.Surface((T, T), pygame.SRCALPHA)
    pygame.draw.rect(s, base, (0, 0, T, 8))
    pygame.draw.line(s, light, (0, 0), (T - 1, 0))
    pygame.draw.line(s, dark, (0, 7), (T - 1, 7))
    for x in (5, T - 6):
        pygame.draw.line(s, (150, 130, 90), (x, 8), (x, 12))      # corda
        s.set_at((x, 3), nail)
    return s


def _spike(theme):
    s = pygame.Surface((T, T), pygame.SRCALPHA)
    metal = (190, 196, 210) if theme in ("deck", "hull", "bilge") else (200, 190, 170)
    dark = (90, 96, 112)
    for i in range(4):
        bx = i * 8
        pygame.draw.polygon(s, dark, [(bx, T), (bx + 4, 12), (bx + 8, T)])
        pygame.draw.polygon(s, metal, [(bx + 1, T), (bx + 4, 14), (bx + 4, T)])
        s.set_at((bx + 4, 12), (255, 255, 255))
    pygame.draw.rect(s, dark, (0, T - 3, T, 3))
    return s


def _crumble(palette):
    base, dark, light, _ = palette
    s = pygame.Surface((T, T), pygame.SRCALPHA)
    pygame.draw.rect(s, _shade(base, 12), (1, 0, T - 2, 12), border_radius=2)
    pygame.draw.line(s, light, (2, 0), (T - 3, 0))
    pygame.draw.line(s, dark, (1, 11), (T - 2, 11))
    # rachaduras
    for pts in (((8, 0), (11, 5), (9, 11)), ((22, 0), (20, 6), (24, 11))):
        pygame.draw.lines(s, dark, False, pts)
    return s


def _island_tiles(theme):
    if theme == "island":
        top = sprites.crop(ISLAND, (384, 0, 32, 32))
        dirt = sprites.crop(ISLAND, (384, 16, 32, 16))
        fill = pygame.Surface((T, T), pygame.SRCALPHA)
        if dirt is not None:
            fill.blit(dirt, (0, 0))
            fill.blit(pygame.transform.flip(dirt, True, False), (0, 16))
        return [top], [fill]
    if theme == "ruins":
        return [sprites.crop(ISLAND, (768, 0, 32, 32))], [sprites.crop(ISLAND, (800, 96, 32, 32)),
                                                          sprites.crop(ISLAND, (864, 160, 32, 32))]
    # templo
    return [sprites.crop(ISLAND, (32, 256, 32, 32))], [sprites.crop(ISLAND, (0, 320, 32, 32)),
                                                       sprites.crop(ISLAND, (224, 288, 32, 32))]


def tileset(theme):
    """Dicionário com listas de variações: top, fill, oneway, spike, crumble."""
    if theme in _cache:
        return _cache[theme]
    if theme in WOOD:
        pal = WOOD[theme]
        tops = [_wood_tile(pal, 100 + i, top=True) for i in range(4)]
        fills = [_wood_tile(tuple(_shade(c, -14) for c in pal[:3]) + (pal[3],), 200 + i, vertical=True)
                 for i in range(4)]
        oneway = _oneway_wood(pal)
        crumble = _crumble(pal)
    else:
        tops, fills = _island_tiles(theme)
        tops = [t for t in tops if t is not None] or [_wood_tile(WOOD["hull"], 1, top=True)]
        fills = [f for f in fills if f is not None] or [_wood_tile(WOOD["hull"], 2)]
        plank = sprites.crop(ISLAND, (512, 190, 32, 14))
        oneway = pygame.Surface((T, T), pygame.SRCALPHA)
        if plank is not None:
            oneway.blit(plank, (0, 0))
        crumble = _crumble(WOOD["deck"])
    ts = {"top": tops, "fill": fills, "oneway": oneway, "spike": _spike(theme), "crumble": crumble}
    _cache[theme] = ts
    return ts


def theme_of(zone):
    return ZONE_THEME.get(zone, "hull")
