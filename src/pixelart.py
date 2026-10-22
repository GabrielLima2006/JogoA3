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
    # mesmo padrão da protagonista: cabeça grande, cabelo volumoso com franja, olhos grandes
    # com brilho, roupa com três tons e botas destacadas.
    # casaco, detalhe, calça, botas, cabelo, olhos, cabelo comprido (0-3), extra
    "cozinheira": ((236, 232, 222), (200, 60, 60), (110, 84, 70), (120, 70, 50), (150, 80, 50), (90, 60, 40), 1, "chef"),
    "grumete": ((60, 110, 190), (230, 200, 90), (100, 80, 60), (150, 90, 50), (230, 150, 60), (60, 120, 200), 0, "bone"),
    "imediato": ((44, 52, 104), (220, 180, 80), (40, 40, 56), (60, 40, 40), (40, 34, 44), (160, 40, 60), 2, "tricornio"),
    "irma": ((170, 36, 56), (240, 200, 90), (50, 40, 60), (40, 30, 40), (34, 28, 44), (200, 50, 70), 3, "bandana"),
    "amigo": ((56, 120, 90), (130, 80, 170), (70, 60, 56), (90, 60, 40), (130, 90, 60), (70, 160, 110), 1, "cachecol"),
    "capita": ((36, 40, 80), (220, 180, 80), (36, 34, 50), (110, 40, 40), (200, 210, 230), (90, 120, 220), 3, "capita"),
    "mercador": ((160, 110, 60), (90, 150, 80), (80, 60, 44), (90, 60, 40), (100, 70, 50), (100, 80, 50), 0, "chapeu"),
    "capanga": ((70, 70, 96), (200, 60, 60), (60, 50, 60), (60, 44, 40), (60, 50, 60), (200, 70, 70), 0, "lenco"),
    "escudeiro": ((120, 60, 50), (210, 180, 110), (60, 50, 56), (70, 50, 40), (170, 60, 40), (200, 120, 60), 1, "lenco"),
}
OUTLINE_SOFT = (34, 20, 44)


def human(style, pose="idle", phase=0.0, facing=1):
    """Humano feito a partir do sprite da protagonista (ver elenco.py). pose: idle, walk, attack, shoot, hurt.
    Quadro 80x64 com o pé 3 px acima da borda de baixo, centralizado."""
    from . import elenco
    if style in elenco.CAST:
        return elenco.character(style, pose, phase, facing)
    q = round(phase * 8) / 8
    key = ("human", style, pose, q, facing)
    return cached(key, lambda: _human(style, pose, q, facing))


def _tones(c):
    return shade(c, 34), c, shade(c, -42)


def _human(style, pose, phase, facing):
    coat, trim, pants, boots, hair, eyes, hair_len, extra = STYLES[style]
    s = _canvas(48, 62)
    cx = 22
    feet = 58
    wave = math.sin(phase * math.tau)
    bob = round(wave) if pose == "idle" else (abs(round(wave)) if pose == "walk" else 0)
    leg = wave * 6 if pose == "walk" else 0
    hl, base, dk = _tones(coat)
    phl, pbase, pdk = _tones(pants)
    bhl, bbase, bdk = _tones(boots)
    hhl, hbase, hdk = _tones(hair)
    top = 10 + bob                                    # topo do cabelo

    # cabelo de trás (antes do corpo)
    if hair_len:
        ln = (8, 14, 20)[hair_len - 1]
        pygame.draw.rect(s, hdk, (cx - 10, top + 8, 9, ln + 8), border_radius=3)
        pygame.draw.rect(s, hbase, (cx - 9, top + 8, 6, ln + 6), border_radius=3)

    # pernas e botas (a de trás mais escura)
    for side, off, back in ((-1, leg, True), (1, -leg, False)):
        lx = round(cx + side * 3 + off * 0.6)
        pygame.draw.rect(s, pdk if back else pbase, (lx - 2, feet - 15, 5, 9))
        bc = bdk if back else bbase
        pygame.draw.rect(s, bc, (lx - 3, feet - 7, 7, 7), border_radius=2)
        pygame.draw.rect(s, bc, (lx - 2, feet - 3, 8, 3))                     # bico da bota
        if not back:
            pygame.draw.line(s, bhl, (lx - 2, feet - 6), (lx + 2, feet - 6))
        pygame.draw.line(s, OUTLINE_SOFT, (lx - 2, feet - 1), (lx + 5, feet - 1))   # sola

    body_top = top + 20
    # braço de trás
    back_swing = -wave * 3 if pose == "walk" else 0
    pygame.draw.line(s, dk, (cx - 4, body_top + 3), (cx - 6 + back_swing, body_top + 12), 4)
    # casaco que abre embaixo (como o manto da protagonista)
    flare = wave * 1.5 if pose == "walk" else 0
    pts = [(cx - 6, body_top), (cx + 6, body_top), (cx + 9 + flare, feet - 12), (cx - 10 - flare, feet - 12)]
    pygame.draw.polygon(s, base, pts)
    pygame.draw.polygon(s, dk, [(cx - 6, body_top), (cx - 2, body_top), (cx - 4, feet - 12),
                                (cx - 10 - flare, feet - 12)])
    pygame.draw.line(s, hl, (cx + 4, body_top + 1), (cx + 7 + flare, feet - 13))
    pygame.draw.line(s, trim, (cx + 1, body_top + 1), (cx + 2, feet - 13))     # abotoamento/faixa
    pygame.draw.rect(s, shade(trim, -30), (cx - 6, body_top + 9, 13, 2))         # cinto
    pygame.draw.rect(s, (230, 210, 120), (cx + 1, body_top + 9, 2, 2))           # fivela

    # braço da frente + mão
    if pose == "attack":
        ang = -1.2 + phase * 2.4
        hx, hy = cx + 3 + math.cos(ang) * 11, body_top + 4 + math.sin(ang) * 11
        pygame.draw.line(s, base, (cx + 3, body_top + 3), (hx, hy), 4)
        bx, by = hx + math.cos(ang - 0.4) * 15, hy + math.sin(ang - 0.4) * 15
        pygame.draw.line(s, (226, 232, 244), (hx, hy), (bx, by), 2)               # alfanje
        pygame.draw.line(s, (255, 255, 255), (hx, hy), ((hx + bx) / 2, (hy + by) / 2), 1)
        pygame.draw.circle(s, SKIN, (round(hx), round(hy)), 2)
        pygame.draw.circle(s, (220, 180, 70), (round(hx), round(hy)), 1)
    elif pose == "shoot":
        pygame.draw.line(s, base, (cx + 3, body_top + 3), (cx + 13, body_top + 4), 4)
        pygame.draw.rect(s, (70, 60, 64), (cx + 12, body_top + 1, 9, 4))
        pygame.draw.rect(s, (130, 90, 50), (cx + 12, body_top + 4, 3, 4))
        pygame.draw.circle(s, SKIN, (cx + 13, body_top + 4), 2)
    else:
        swing = wave * 3 if pose == "walk" else 0
        pygame.draw.line(s, base, (cx + 3, body_top + 3), (cx + 4 + swing, body_top + 12), 4)
        pygame.draw.circle(s, SKIN, (round(cx + 4 + swing), body_top + 13), 2)

    # cabeça grande: rosto, olhos com brilho, boca e bochecha
    face = pygame.Rect(cx - 7, top + 6, 15, 15)
    pygame.draw.rect(s, SKIN, face, border_radius=5)
    pygame.draw.rect(s, SKIN_DARK, (face.x, face.bottom - 4, 4, 3))
    for ex in (cx + 4, cx - 2):
        pygame.draw.rect(s, (30, 22, 40), (ex, top + 12, 3, 5))
        pygame.draw.rect(s, eyes, (ex, top + 14, 3, 3))
        s.set_at((ex, top + 12), (255, 255, 255))
    s.set_at((cx + 4, top + 19), (170, 80, 80))                                 # boca
    s.set_at((cx + 7, top + 18), (240, 150, 150))                               # bochecha

    # cabelo volumoso com franja em pontas
    pygame.draw.ellipse(s, hbase, (cx - 10, top, 21, 13))
    pygame.draw.rect(s, hbase, (cx - 10, top + 5, 6, 10))                       # lado (atrás da orelha)
    for i, x in enumerate(range(cx - 7, cx + 9, 4)):
        pygame.draw.polygon(s, hbase, [(x, top + 7), (x + 4, top + 7), (x + 2, top + 11 + (i % 2) * 2)])
    pygame.draw.arc(s, hhl, (cx - 6, top + 1, 14, 9), 0.6, 2.6, 2)               # brilho do cabelo
    pygame.draw.line(s, hdk, (cx - 10, top + 6), (cx - 8, top + 14))

    _accessory(s, extra, cx, top, body_top, trim)
    if pose == "hurt":
        s.fill((255, 120, 120, 0), special_flags=pygame.BLEND_RGBA_MAX)
    s = outline(s, OUTLINE_SOFT)
    return pygame.transform.flip(s, True, False) if facing < 0 else s


def _accessory(s, extra, cx, top, body_top, trim):
    if extra == "chef":
        pygame.draw.rect(s, (252, 252, 252), (cx - 7, top - 9, 15, 11), border_radius=5)
        pygame.draw.rect(s, (220, 220, 226), (cx - 8, top + 1, 17, 3))
        pygame.draw.rect(s, (250, 250, 250), (cx - 5, body_top + 2, 11, 15))      # avental
        pygame.draw.rect(s, trim, (cx - 7, body_top - 1, 15, 3))                   # lenço vermelho
    elif extra == "bone":
        pygame.draw.ellipse(s, (50, 90, 170), (cx - 9, top - 2, 19, 9))
        pygame.draw.rect(s, (40, 70, 140), (cx + 4, top + 4, 9, 3))                # aba
    elif extra in ("tricornio", "capita"):
        hat = (30, 28, 44) if extra == "tricornio" else (24, 22, 36)
        pygame.draw.polygon(s, hat, [(cx - 13, top + 4), (cx + 14, top + 4), (cx + 8, top - 6), (cx - 7, top - 6)])
        pygame.draw.line(s, trim, (cx - 12, top + 4), (cx + 13, top + 4), 1)
        if extra == "capita":
            pygame.draw.circle(s, (240, 240, 240), (cx, top - 1), 2)               # caveira do chapéu
            pygame.draw.polygon(s, (200, 60, 70), [(cx + 8, top - 5), (cx + 14, top - 12), (cx + 10, top - 4)])
    elif extra == "bandana":
        pygame.draw.rect(s, (190, 30, 50), (cx - 9, top + 2, 19, 4))
        pygame.draw.polygon(s, (190, 30, 50), [(cx - 9, top + 3), (cx - 16, top + 9), (cx - 10, top + 9)])
        pygame.draw.polygon(s, (24, 20, 30), [(cx - 13, top + 2), (cx + 14, top + 2), (cx + 7, top - 7),
                                              (cx - 6, top - 7)])
        pygame.draw.circle(s, (240, 240, 240), (cx + 1, top - 2), 2)
        pygame.draw.circle(s, (240, 210, 90), (cx - 6, top + 15), 1)              # brinco
    elif extra == "cachecol":
        pygame.draw.rect(s, trim, (cx - 7, body_top - 2, 15, 4), border_radius=1)
        pygame.draw.rect(s, trim, (cx - 7, body_top, 4, 9))
        pygame.draw.line(s, shade(trim, 40), (cx - 6, body_top - 1), (cx + 6, body_top - 1))
    elif extra == "chapeu":
        pygame.draw.ellipse(s, (100, 66, 34), (cx - 14, top + 1, 29, 7))
        pygame.draw.rect(s, (100, 66, 34), (cx - 7, top - 6, 15, 9), border_radius=2)
        pygame.draw.rect(s, (160, 50, 50), (cx - 7, top, 15, 2))
    elif extra == "lenco":
        pygame.draw.rect(s, trim, (cx - 9, top + 1, 19, 5), border_radius=2)
        pygame.draw.polygon(s, trim, [(cx - 9, top + 3), (cx - 15, top + 1), (cx - 14, top + 7)])
        for x in range(cx - 7, cx + 9, 4):
            s.set_at((x, top + 3), (250, 240, 230))


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
