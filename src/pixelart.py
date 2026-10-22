"""Pixel art desenhada no código (personagens que os pacotes não têm).

Cada desenho é feito em tamanho real com formas simples e recebe um contorno
escuro de 1 pixel, o que dá o acabamento de sprite. As poses são guardadas em
cache, então desenhar a cada quadro é barato.
"""

import math

import pygame

OUTLINE = (18, 12, 22)
SKIN = (238, 192, 158)
SKIN_DARK = (196, 146, 118)
_cache = {}


def outline(surf, color=OUTLINE):
    """Adiciona contorno de 1 px em volta dos pixels opacos."""
    w, h = surf.get_size()
    mask = pygame.mask.from_surface(surf, 1)
    out = surf.copy()
    edge = pygame.Surface((w, h), pygame.SRCALPHA)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        m = mask.to_surface(setcolor=color + (255,), unsetcolor=(0, 0, 0, 0))
        edge.blit(m, (dx, dy))
    edge.blit(mask.to_surface(setcolor=(0, 0, 0, 0), unsetcolor=(0, 0, 0, 0)), (0, 0))
    final = pygame.Surface((w, h), pygame.SRCALPHA)
    final.blit(edge, (0, 0))
    final.blit(out, (0, 0))
    return final


def _canvas(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def cached(key, builder):
    s = _cache.get(key)
    if s is None:
        s = builder()
        if len(_cache) > 1500:
            _cache.clear()
        _cache[key] = s
    return s


def shade(c, d):
    return tuple(max(0, min(255, v + d)) for v in c)


# ---------------------------------------------------------------------------
# Humanos da tripulação (NPCs e base da irmã pirata)
# ---------------------------------------------------------------------------

STYLES = {
    #               casaco          calça          cabelo          extra
    "cozinheira": ((236, 236, 228), (120, 90, 70), (130, 70, 40), "chef"),
    "grumete": ((70, 110, 170), (90, 70, 50), (200, 150, 70), "bone"),
    "imediato": ((60, 66, 110), (40, 40, 52), (40, 34, 30), "tricornio"),
    "irma": ((150, 40, 50), (50, 40, 50), (30, 24, 28), "bandana"),
    "amigo": ((70, 120, 90), (60, 52, 46), (110, 80, 50), "cachecol"),
    "capita": ((40, 44, 70), (36, 34, 44), (90, 50, 30), "capita"),
    "mercador": ((150, 110, 60), (80, 60, 40), (60, 40, 30), "chapeu"),
}


def human(style, pose="idle", phase=0.0, facing=1):
    """Humano de ~48 px de altura. pose: idle, walk, attack, shoot, hurt."""
    q = round(phase * 8) / 8
    key = ("human", style, pose, q, facing)
    return cached(key, lambda: _human(style, pose, q, facing))


def _human(style, pose, phase, facing):
    coat, pants, hair, extra = STYLES[style]
    s = _canvas(40, 56)
    cx = 20
    bob = round(math.sin(phase * math.tau) * 1) if pose == "idle" else 0
    leg = math.sin(phase * math.tau) * 4 if pose == "walk" else 0
    top = 14 + bob
    # pernas e botas
    for side, off in ((-1, leg), (1, -leg)):
        lx = cx + side * 4 + off * 0.5
        pygame.draw.rect(s, pants, (lx - 2, top + 22, 5, 14))
        pygame.draw.rect(s, (40, 30, 28), (lx - 3 + (1 if facing > 0 else -1), top + 34, 7, 4))
    # corpo/casaco
    pygame.draw.rect(s, coat, (cx - 8, top + 6, 16, 19), border_radius=3)
    pygame.draw.rect(s, shade(coat, -30), (cx - 8, top + 20, 16, 5))
    pygame.draw.line(s, shade(coat, 30), (cx - 7, top + 7), (cx - 7, top + 18))
    pygame.draw.rect(s, (60, 40, 30), (cx - 8, top + 18, 16, 2))            # cinto
    # braços
    arm = coat
    if pose == "attack":
        ang = -0.9 + phase * 2.2
        hx, hy = cx + facing * (6 + math.cos(ang) * 11), top + 11 + math.sin(ang) * 11
        pygame.draw.line(s, arm, (cx + facing * 6, top + 9), (hx, hy), 4)
        # alfanje
        bx, by = hx + facing * math.cos(ang - 0.5) * 14, hy + math.sin(ang - 0.5) * 14
        pygame.draw.line(s, (220, 226, 236), (hx, hy), (bx, by), 2)
        pygame.draw.circle(s, (210, 170, 70), (int(hx), int(hy)), 2)
    elif pose == "shoot":
        pygame.draw.line(s, arm, (cx + facing * 6, top + 9), (cx + facing * 17, top + 10), 4)
        pygame.draw.rect(s, (60, 50, 50), (cx + facing * 15 - (0 if facing > 0 else 8), top + 7, 9, 4))
    else:
        swing = math.sin(phase * math.tau) * 2 if pose == "walk" else 0
        pygame.draw.line(s, arm, (cx - 8, top + 9), (cx - 9 - swing, top + 20), 4)
        pygame.draw.line(s, arm, (cx + 8, top + 9), (cx + 9 + swing, top + 20), 4)
    pygame.draw.circle(s, SKIN, (cx - 9, top + 21), 2)
    pygame.draw.circle(s, SKIN, (cx + 9, top + 21), 2)
    # cabeça
    pygame.draw.rect(s, SKIN, (cx - 6, top - 6, 12, 12), border_radius=4)
    pygame.draw.rect(s, SKIN_DARK, (cx - 6, top + 3, 12, 3))
    ex = cx + facing * 2
    pygame.draw.rect(s, (30, 24, 34), (ex - 1 + facing, top - 2, 2, 3))
    pygame.draw.rect(s, (30, 24, 34), (ex - 5 + facing * 3, top - 2, 2, 3))
    pygame.draw.rect(s, hair, (cx - 7, top - 8, 14, 5))
    pygame.draw.rect(s, hair, (cx - 7 - (2 if facing > 0 else -10), top - 6, 4, 9))
    if extra == "chef":
        pygame.draw.rect(s, (250, 250, 250), (cx - 6, top - 16, 12, 9), border_radius=4)
        pygame.draw.rect(s, (250, 250, 250), (cx - 7, top - 9, 14, 3))
        pygame.draw.rect(s, (250, 250, 250), (cx - 8, top + 8, 16, 14))       # avental
    elif extra == "bone":
        pygame.draw.rect(s, (60, 80, 140), (cx - 7, top - 10, 14, 5), border_radius=2)
        pygame.draw.rect(s, (60, 80, 140), (cx + facing * 4, top - 7, 7 * facing or 7, 2))
    elif extra == "tricornio":
        pygame.draw.polygon(s, (30, 30, 40), [(cx - 11, top - 6), (cx + 11, top - 6), (cx, top - 16)])
        pygame.draw.line(s, (210, 180, 90), (cx - 10, top - 6), (cx + 10, top - 6), 1)
        pygame.draw.rect(s, (220, 190, 90), (cx - 1, top + 9, 2, 10))           # botões
    elif extra == "bandana":
        pygame.draw.rect(s, (180, 30, 40), (cx - 7, top - 9, 14, 4))
        pygame.draw.polygon(s, (180, 30, 40), [(cx - facing * 7, top - 8), (cx - facing * 14, top - 3),
                                               (cx - facing * 8, top - 2)])
        pygame.draw.circle(s, (230, 200, 80), (cx + facing * 6, top + 1), 1)
        # chapéu de pirata
        pygame.draw.polygon(s, (24, 20, 26), [(cx - 12, top - 8), (cx + 12, top - 8), (cx + 6, top - 15), (cx - 6, top - 15)])
        pygame.draw.circle(s, (240, 240, 240), (cx, top - 12), 2)
    elif extra == "cachecol":
        pygame.draw.rect(s, (110, 70, 140), (cx - 9, top + 5, 18, 4))
        pygame.draw.rect(s, (110, 70, 140), (cx - facing * 7, top + 7, 4, 11))
    elif extra == "capita":
        pygame.draw.polygon(s, (24, 22, 32), [(cx - 12, top - 6), (cx + 12, top - 6), (cx, top - 15)])
        pygame.draw.rect(s, (220, 190, 90), (cx - 8, top + 7, 3, 3))
    elif extra == "chapeu":
        pygame.draw.ellipse(s, (90, 60, 30), (cx - 12, top - 10, 24, 6))
        pygame.draw.rect(s, (90, 60, 30), (cx - 6, top - 15, 12, 7))
    if pose == "hurt":
        s.fill((255, 120, 120, 0), special_flags=pygame.BLEND_RGBA_MAX)
    return outline(s)


def corpse():
    """A capitã caída sobre a mesa."""
    def build():
        s = _canvas(56, 20)
        pygame.draw.rect(s, (40, 44, 70), (10, 6, 34, 10), border_radius=3)
        pygame.draw.circle(s, SKIN, (8, 11), 6)
        pygame.draw.polygon(s, (24, 22, 32), [(0, 6), (16, 6), (8, -2)])
        pygame.draw.rect(s, (110, 60, 120), (6, 14, 4, 2))           # lábios arroxeados
        pygame.draw.rect(s, (36, 34, 44), (44, 10, 10, 6))
        return outline(s)
    return cached(("corpse",), build)


# ---------------------------------------------------------------------------
# Bichos: rato e gaivota
# ---------------------------------------------------------------------------

def rat(phase, facing, scale=1, cap=False, glow=False):
    q = round(phase * 6) / 6
    return cached(("rat", q, facing, scale, cap, glow), lambda: _rat(q, facing, scale, cap, glow))


def _rat(phase, facing, scale, cap, glow):
    s = _canvas(40, 26)
    body = (128, 120, 126)
    leg = math.sin(phase * math.tau) * 2
    pygame.draw.ellipse(s, body, (6, 8, 26, 14))
    pygame.draw.ellipse(s, shade(body, 24), (9, 9, 18, 6))
    pygame.draw.ellipse(s, body, (24, 9, 13, 10))                     # cabeça
    pygame.draw.polygon(s, shade(body, 10), [(35, 13), (40, 15), (35, 17)])
    pygame.draw.circle(s, (240, 150, 160), (39, 15), 1)
    pygame.draw.circle(s, (200, 140, 150), (28, 8), 3)                 # orelha
    pygame.draw.rect(s, (255, 60, 60) if glow else (20, 16, 20), (31, 12, 2, 2))
    pygame.draw.lines(s, (200, 150, 160), False, [(7, 15), (2, 12), (0, 16)], 1)  # rabo
    for x, off in ((12, leg), (26, -leg)):
        pygame.draw.rect(s, shade(body, -40), (x + off, 20, 3, 4))
    if cap:
        pygame.draw.rect(s, (50, 70, 130), (24, 4, 12, 4), border_radius=2)
        pygame.draw.rect(s, (50, 70, 130), (34, 6, 5, 2))
    s = outline(s)
    if facing < 0:
        s = pygame.transform.flip(s, True, False)
    if scale != 1:
        s = pygame.transform.scale(s, (s.get_width() * scale, s.get_height() * scale))
    return s


def gull(phase, facing):
    q = round(phase * 6) / 6
    return cached(("gull", q, facing), lambda: _gull(q, facing))


def _gull(phase, facing):
    s = _canvas(36, 24)
    wing = math.sin(phase * math.tau) * 7
    pygame.draw.polygon(s, (230, 232, 238), [(18, 13), (4, 12 - wing), (10, 14)])
    pygame.draw.polygon(s, (200, 204, 214), [(18, 13), (32, 12 - wing), (26, 14)])
    pygame.draw.ellipse(s, (244, 244, 248), (11, 10, 16, 8))
    pygame.draw.circle(s, (244, 244, 248), (27, 11), 4)
    pygame.draw.polygon(s, (240, 170, 50), [(30, 10), (35, 12), (30, 13)])
    pygame.draw.rect(s, (20, 16, 20), (28, 9, 2, 2))
    pygame.draw.polygon(s, (90, 96, 110), [(11, 13), (6, 11), (7, 16)])
    s = outline(s)
    return pygame.transform.flip(s, True, False) if facing < 0 else s


# ---------------------------------------------------------------------------
# Chefes desenhados no código
# ---------------------------------------------------------------------------

def sorcerer(pose, phase, facing):
    """O Feiticeiro da Maré: capuz, manto que ondula, cajado com orbe."""
    q = round(phase * 10) / 10
    return cached(("sorc", pose, q, facing), lambda: _sorcerer(pose, q, facing))


def _sorcerer(pose, phase, facing):
    s = _canvas(70, 96)
    cx = 35
    robe = (46, 36, 84)
    trim = (120, 220, 210)
    wave = math.sin(phase * math.tau)
    # manto
    pts = [(cx - 10, 26), (cx + 10, 26), (cx + 18 + wave * 3, 84), (cx + 8, 90 + wave * 2),
           (cx, 86), (cx - 8, 90 - wave * 2), (cx - 18 - wave * 3, 84)]
    pygame.draw.polygon(s, robe, pts)
    pygame.draw.polygon(s, shade(robe, 22), [(cx - 6, 30), (cx + 2, 30), (cx - 2, 82)])
    pygame.draw.lines(s, trim, False, [(cx - 18 - wave * 3, 84), (cx - 8, 90 - wave * 2), (cx, 86),
                                       (cx + 8, 90 + wave * 2), (cx + 18 + wave * 3, 84)], 2)
    # capuz
    pygame.draw.ellipse(s, robe, (cx - 13, 6, 26, 28))
    pygame.draw.ellipse(s, (10, 8, 18), (cx - 8, 13, 16, 17))
    eye = (120, 255, 230) if pose != "hurt" else (255, 255, 255)
    pygame.draw.rect(s, eye, (cx - 5 + facing * 2, 20, 3, 2))
    pygame.draw.rect(s, eye, (cx + 2 + facing * 2, 20, 3, 2))
    # cachecol (o mesmo do amigo de infância)
    pygame.draw.rect(s, (110, 70, 140), (cx - 10, 30, 20, 5))
    # braços e cajado
    if pose == "cast":
        hx, hy = cx + facing * 22, 18 - phase * 6
        pygame.draw.line(s, robe, (cx + facing * 8, 36), (hx, hy), 5)
        pygame.draw.circle(s, (180, 255, 240), (int(hx), int(hy - 4)), 5)
        pygame.draw.circle(s, (255, 255, 255), (int(hx), int(hy - 4)), 2)
    else:
        pygame.draw.line(s, (90, 70, 50), (cx + facing * 16, 20), (cx + facing * 16, 88), 3)
        pygame.draw.circle(s, trim, (cx + facing * 16, 18), 5)
        pygame.draw.line(s, robe, (cx + facing * 8, 36), (cx + facing * 15, 46), 5)
    if pose == "hurt":
        s.fill((255, 160, 200, 0), special_flags=pygame.BLEND_RGBA_MAX)
    return outline(s)


def cannon(facing, flash=False):
    def build():
        s = _canvas(40, 28)
        pygame.draw.rect(s, (70, 50, 34), (6, 16, 24, 8), border_radius=2)
        pygame.draw.circle(s, (40, 30, 24), (10, 24), 4)
        pygame.draw.circle(s, (40, 30, 24), (26, 24), 4)
        pygame.draw.rect(s, (54, 58, 66), (10, 8, 26, 10), border_radius=3)
        pygame.draw.rect(s, (36, 38, 46), (34, 7, 5, 12))
        if flash:
            pygame.draw.circle(s, (255, 200, 90), (38, 13), 5)
        s2 = outline(s)
        return pygame.transform.flip(s2, True, False) if facing < 0 else s2
    return cached(("cannon", facing, flash), build)


def crate(broken=False):
    def build():
        s = _canvas(30, 28)
        wood = (150, 104, 60)
        pygame.draw.rect(s, wood, (1, 1, 28, 26))
        pygame.draw.rect(s, shade(wood, -40), (1, 1, 28, 26), 2)
        pygame.draw.line(s, shade(wood, -40), (2, 2), (27, 25), 3)
        pygame.draw.line(s, shade(wood, 30), (3, 3), (26, 3))
        for x, y in ((4, 4), (25, 4), (4, 23), (25, 23)):
            s.set_at((x, y), (70, 70, 80))
        return outline(s)
    return cached(("crate", broken), build)
