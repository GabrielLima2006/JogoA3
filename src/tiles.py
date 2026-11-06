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


def _detalhe(s, theme, i):
    """Variação rara do topo de madeira: limo verde escorrendo (porão), chapa de ferro
    rebitada ou tábua remendada (convés e interior). Só abaixo da linha de cima,
    que é a borda de pisar e fica igual."""
    rnd = random.Random(300 + i)
    if theme == "bilge":
        for _ in range(5):                                   # limo pingando da borda
            x = rnd.randrange(1, T - 2)
            comp = rnd.randint(3, 9)
            pygame.draw.line(s, (58, 86, 54), (x, 4), (x, 4 + comp))
            s.set_at((x, 4 + comp), (88, 120, 70))
        pygame.draw.line(s, (70, 104, 60), (0, 4), (T - 1, 4))
    elif i == 0:                                             # chapa de ferro com rebites
        r = pygame.Rect(rnd.randint(4, 12), 7, 14, 10)
        pygame.draw.rect(s, (52, 54, 62), r)
        pygame.draw.rect(s, (30, 30, 36), r, 1)
        pygame.draw.line(s, (96, 98, 110), (r.x + 1, r.y + 1), (r.right - 2, r.y + 1))
        for cx, cy in ((r.x + 2, r.y + 3), (r.right - 3, r.y + 3), (r.x + 2, r.bottom - 3), (r.right - 3, r.bottom - 3)):
            s.set_at((cx, cy), (150, 150, 160))
    else:                                                    # tábua remendada mais clara
        y = 4 + 8 * rnd.randint(0, 2)
        x0 = rnd.randint(2, 12)
        pygame.draw.rect(s, (140, 96, 58) if theme == "deck" else (104, 70, 46), (x0, y + 1, 14, 6))
        pygame.draw.rect(s, (84, 54, 34), (x0, y + 1, 14, 6), 1)
        for nx in (x0 + 2, x0 + 11):
            s.set_at((nx, y + 3), (70, 70, 80))
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


# recortes do tileset (x, y) de 32x32, escolhidos por tema; veja tools/capturar.py para conferir
ISLAND_CROPS = {
    "island": {
        "top": [(32, 0), (64, 0), (96, 0), (672, 0), (384, 0), (416, 0), (576, 0), (448, 0)],
        "fill": [(640, 64), (672, 64), (640, 128), (672, 128), (704, 64), (704, 128)],
        "back": (34, 28, 24),
    },
    "ruins": {
        "top": [(928, 0), (832, 0), (960, 0), (864, 0), (896, 0), (768, 0)],
        # pedra cinza com algumas pedras de musgo (as mesmas do templo, para ligar as duas áreas)
        "fill": [(864, 64), (896, 64), (832, 64), (928, 64), (864, 128), (832, 128), (384, 288), (416, 320)],
        "back": (46, 46, 58),
    },
    "temple": {
        "top": [(32, 256), (64, 256), (96, 256), (128, 256), (256, 256), (288, 256)],
        "fill": [(224, 320), (256, 320), (288, 320), (256, 288), (288, 288), (224, 288)],
        "back": (20, 26, 30),
    },
}


def _backed(crop, back, from_row=0):
    """Recorte com fundo opaco a partir de `from_row` (fecha furos do tileset sem tirar o ar de cima)."""
    if crop is None:
        return None
    s = pygame.Surface((T, T), pygame.SRCALPHA)
    s.fill(back, (0, from_row, T, T - from_row))
    s.blit(crop, (0, 0))
    return s


def _darken(surf, k):
    d = surf.copy()
    d.fill((k, k, k, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return d


def _island_tiles(theme):
    spec = ISLAND_CROPS[theme]
    back = spec["back"]
    tops = [_backed(sprites.crop(ISLAND, (x, y, T, T)), back, 14) for x, y in spec["top"]]
    fills = [_backed(sprites.crop(ISLAND, (x, y, T, T)), back) for x, y in spec["fill"]]
    return tops, fills


def pick(group, tx, ty):
    """Variação do bloco na posição (tx, ty): espalhada por hash, sem listras repetidas."""
    h = (tx * 73856093 ^ ty * 19349663 ^ 0x5BD1E995) & 0xFFFFFFFF
    h = (h ^ (h >> 13)) * 0x5BD1E995 & 0xFFFFFFFF
    return group[(h ^ (h >> 15)) % len(group)]


def solid_tile(ts, room, tx, ty):
    """Bloco sólido certo para a posição: topo (ar em cima), recheio ou fundo (longe da superfície).

    Os blocos a 3 ou mais tiles de qualquer abertura ficam mais escuros, o que dá profundidade
    às paredes grossas."""
    def solid(a, b):
        return room.tile(a, b) in ("#", None, "X")
    aberto = (not solid(tx, ty - 1), not solid(tx - 1, ty), not solid(tx + 1, ty), not solid(tx, ty + 1))
    if aberto[0]:
        base = pick(ts["top"], tx, ty)
    else:
        deep = all(solid(tx + dx, ty + dy) for dx in (-2, 0, 2) for dy in (-2, 0, 2))
        base = pick(ts["deep"] if deep else ts["fill"], tx, ty)
    if not any(aberto[1:]):
        return base
    return _bordas(base, aberto)


_bordas_cache = {}


def _bordas(base, aberto):
    """Luz e sombra nas faces expostas (luz vem de cima, à esquerda) e cantos de fora gastos,
    para a parede não parecer uma grade de quadrados iguais."""
    key = (id(base), aberto)
    img = _bordas_cache.get(key)
    if img is not None:
        return img
    cima, esq, dir_, baixo = aberto
    img = base.copy()
    w, h = img.get_size()
    if baixo:                                    # face de baixo: sombra de 4 px e linha escura
        sombra = pygame.Surface((w, 4), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 70))
        img.blit(sombra, (0, h - 4))
        pygame.draw.line(img, (12, 8, 16), (0, h - 1), (w - 1, h - 1))
    if dir_:                                     # lado da sombra
        sombra = pygame.Surface((3, h), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 60))
        img.blit(sombra, (w - 3, 0))
        pygame.draw.line(img, (12, 8, 16), (w - 1, 0), (w - 1, h - 1))
    if esq:                                      # lado da luz: filete claro e contorno
        luz = pygame.Surface((1, h), pygame.SRCALPHA)
        luz.fill((255, 240, 210, 40))
        img.blit(luz, (1, 0))
        pygame.draw.line(img, (12, 8, 16), (0, 0), (0, h - 1))
    # cantos de fora: tira 1 px (e 2 no canto de baixo) para arredondar
    for canto, (cx, cy) in (((cima and esq), (0, 0)), ((cima and dir_), (w - 1, 0)),
                            ((baixo and esq), (0, h - 1)), ((baixo and dir_), (w - 1, h - 1))):
        if canto:
            img.set_at((cx, cy), (0, 0, 0, 0))
            if cy == h - 1:
                img.set_at((cx + (1 if cx == 0 else -1), cy), (0, 0, 0, 0))
                img.set_at((cx, cy - 1), (0, 0, 0, 0))
    if len(_bordas_cache) > 4000:
        _bordas_cache.clear()
    _bordas_cache[key] = img
    return img


def tileset(theme):
    """Dicionário com listas de variações: top, fill, deep, oneway, spike, crumble."""
    if theme in _cache:
        return _cache[theme]
    if theme in WOOD:
        pal = WOOD[theme]
        tops = [_wood_tile(pal, 100 + i, top=True) for i in range(6)]
        tops = tops * 3 + [_detalhe(_wood_tile(pal, 120 + i, top=True), theme, i) for i in range(3)]   # detalhe raro
        fills = [_wood_tile(tuple(_shade(c, -14) for c in pal[:3]) + (pal[3],), 200 + i, vertical=True)
                 for i in range(6)]
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
    deep = [_darken(f, 150) for f in fills]
    ts = {"top": tops, "fill": fills, "deep": deep, "oneway": oneway, "spike": _spike(theme), "crumble": crumble}
    _cache[theme] = ts
    return ts


def theme_of(zone):
    return ZONE_THEME.get(zone, "hull")
