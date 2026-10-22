"""Elenco do jogo derivado do sprite da protagonista.

Todos os humanos (tripulação, irmã da capitã, capangas) usam os quadros da feiticeira
(parada, andando e as ações geradas por tools/gerar_feiticeira.py) com outra paleta por
região: cabelo, casaco, pele, botas, dourados e olhos. Assim todo mundo fica no mesmo
traço e com as mesmas animações. Cada um ganha cabelo curto ou comprido e um acessório
desenhado por cima (chapéu, bandana, cachecol...).
"""

import pygame

from . import sprites

# cores originais da feiticeira, por região
HAIR = [(178, 178, 255), (158, 160, 250), (255, 255, 255), (255, 255, 204), (151, 192, 255)]
COAT = [(28, 21, 77), (3, 33, 188), (21, 16, 55), (64, 34, 95), (50, 29, 112)]
SKIN = [(255, 140, 94), (224, 94, 43), (140, 35, 9)]
SHADOW = (173, 95, 173)          # sombra usada tanto na pele quanto no cabelo
BOOTS = [(136, 35, 35), (88, 3, 3), (255, 14, 0), (145, 88, 76), (169, 110, 103)]
TRIM = [(255, 163, 3), (166, 75, 10)]
EYES = [(43, 122, 76), (39, 113, 72), (0, 127, 38), (0, 110, 34)]
PINS = [(77, 47, 30), (67, 21, 0)]
PIN_TIPS = [(169, 110, 103), (145, 88, 76)]   # pontas dos grampos (a mesma cor aparece no cano da bota)
WEAPON = [(47, 24, 80), (81, 55, 63)]
WEAPON_EDGE = [(166, 75, 10), (67, 21, 0)]

BASE = {"hair": HAIR[0], "coat": COAT[0], "skin": SKIN[0], "boots": BOOTS[0], "trim": TRIM[0], "eyes": EYES[2]}

CANVAS = (80, 64)
FOOT = (40, 61)                   # 3 px livres abaixo do pé (mesmo contrato dos desenhos antigos)

# hair: cabelo · coat: casaco · skin: pele · boots: botas · trim: dourados · eyes: olhos
# short: corta o cabelo comprido na altura do pescoço · hat: acessório
CAST = {
    "cozinheira": {"hair": (150, 80, 50), "coat": (226, 222, 214), "skin": (240, 170, 130), "boots": (110, 70, 50),
                   "trim": (210, 60, 60), "eyes": (110, 70, 40), "short": False, "hat": "chef"},
    "grumete": {"hair": (235, 150, 60), "coat": (40, 90, 170), "skin": (250, 180, 140), "boots": (120, 80, 50),
                "trim": (230, 200, 90), "eyes": (60, 120, 200), "short": True, "hat": "bone", "size": (0.9, 0.86)},
    "imediato": {"hair": (60, 54, 70), "coat": (26, 30, 60), "skin": (220, 150, 110), "boots": (50, 40, 40),
                 "trim": (230, 190, 80), "eyes": (170, 40, 60), "short": True, "hat": "tricornio", "size": (1.0, 1.12)},
    "irma": {"hair": (52, 40, 64), "coat": (120, 20, 40), "skin": (250, 160, 120), "boots": (40, 30, 40),
             "trim": (240, 200, 90), "eyes": (200, 50, 70), "short": False, "hat": "pirata"},
    "amigo": {"hair": (140, 96, 64), "coat": (30, 80, 60), "skin": (240, 160, 120), "boots": (90, 60, 40),
              "trim": (160, 100, 200), "eyes": (70, 160, 110), "short": True, "hat": "cachecol"},
    "capita": {"hair": (220, 220, 236), "coat": (24, 28, 56), "skin": (250, 170, 130), "boots": (110, 30, 40),
               "trim": (230, 190, 80), "eyes": (90, 120, 220), "short": False, "hat": "capita"},
    "mercador": {"hair": (120, 110, 100), "coat": (110, 72, 34), "skin": (210, 140, 100), "boots": (80, 54, 36),
                 "trim": (110, 170, 90), "eyes": (100, 80, 50), "short": True, "hat": "chapeu", "size": (1.12, 1.0)},
    "capanga": {"hair": (70, 60, 76), "coat": (60, 56, 78), "skin": (230, 150, 110), "boots": (60, 44, 40),
                "trim": (200, 60, 60), "eyes": (200, 70, 70), "short": True, "hat": "lenco"},
    "escudeiro": {"hair": (170, 70, 40), "coat": (90, 40, 30), "skin": (220, 140, 100), "boots": (70, 50, 40),
                  "trim": (220, 190, 110), "eyes": (200, 120, 60), "short": True, "hat": "lenco_amarelo", "size": (1.08, 1.06)},
}

_cache = {}


def _lum(c):
    return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2] + 1


def _tone(new, orig, base):
    """Leva a variação de brilho (orig em relação a base) para a cor nova."""
    k = _lum(orig) / _lum(base)
    if k <= 1:
        return tuple(max(0, min(255, round(v * k))) for v in new)
    t = min(1.0, (k - 1) * 0.6)
    return tuple(max(0, min(255, round(v + (255 - v) * t))) for v in new)


def _palette(spec):
    m = {}
    for region, colors in (("hair", HAIR), ("coat", COAT), ("skin", SKIN), ("boots", BOOTS), ("trim", TRIM),
                           ("eyes", EYES)):
        for c in colors:
            m[c] = _tone(spec[region], c, BASE[region])
    return m


def _recolor(src, spec, short):
    """Troca as cores por região. Retorna (imagem, linha do pescoço)."""
    pal = _palette(spec)
    w, h = src.get_size()
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    px = [[tuple(src.get_at((x, y))) for x in range(w)] for y in range(h)]
    hair_set, skin_set = set(HAIR), set(SKIN)
    # altura do pescoço: primeira linha com bastante casaco
    neck = next((y for y in range(h) if sum(1 for x in range(w) if px[y][x][3] and px[y][x][:3] in COAT) >= 4),
                h // 2)
    weapon = {(x, y) for y in range(h) for x in range(w) if px[y][x][3] and px[y][x][:3] in WEAPON}
    near_weapon = {(x + dx, y + dy) for x, y in weapon for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
    cut = neck - 1
    hair_dark = _tone(spec["hair"], (120, 110, 200), BASE["hair"])
    skin_dark = _tone(spec["skin"], (190, 100, 80), BASE["skin"])
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[y][x]
            if not a:
                continue
            c = (r, g, b)
            if c in WEAPON or c in PINS or (c in PIN_TIPS and y < neck):
                continue
            if c in WEAPON_EDGE and (x, y) in near_weapon:
                continue
            if c in hair_set and short and y > cut:
                continue
            if c == SHADOW:
                hair_n = skin_n = 0
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if 0 <= x + dx < w and 0 <= y + dy < h:
                            q = px[y + dy][x + dx][:3]
                            hair_n += q in hair_set
                            skin_n += q in skin_set
                if hair_n > skin_n:
                    if short and y > cut:
                        continue
                    c = hair_dark
                else:
                    c = skin_dark
            else:
                c = pal.get(c, c)
            out.set_at((x, y), c + (a,))
    return out, neck


def _head(img):
    """Caixa do cabelo na metade de cima (para pôr o chapéu)."""
    w, h = img.get_size()
    pts = [(x, y) for y in range(h // 2) for x in range(w) if img.get_at((x, y)).a]
    if not pts:
        return pygame.Rect(w // 2 - 8, 0, 16, 16)
    xs = [p[0] for p in pts]
    top = min(p[1] for p in pts)
    row = [p[0] for p in pts if p[1] <= top + 8]
    return pygame.Rect(min(row), top, max(row) - min(row) + 1, 16) if row else pygame.Rect(min(xs), top, 16, 16)


def _hat(s, kind, head, spec, neck):
    x, y, w = head.x + 2, head.y + 3, head.w - 4
    cx = head.centerx
    trim = spec["trim"]
    if kind == "chef":
        pygame.draw.rect(s, (250, 250, 250), (cx - 7, y - 9, 14, 11), border_radius=5)
        pygame.draw.rect(s, (214, 214, 222), (cx - 8, y + 1, 16, 3))
        pygame.draw.rect(s, (30, 26, 40), (cx - 7, y - 9, 14, 11), 1, border_radius=5)
    elif kind == "bone":
        pygame.draw.ellipse(s, (40, 80, 160), (x, y - 2, w, 9))
        pygame.draw.rect(s, (30, 60, 130), (x - 6, y + 4, 10, 3))                  # aba para a frente
        pygame.draw.ellipse(s, (20, 30, 70), (x, y - 2, w, 9), 1)
    elif kind in ("tricornio", "capita", "pirata"):
        hat = (26, 24, 38)
        pygame.draw.polygon(s, hat, [(x - 4, y + 4), (x + w + 4, y + 4), (x + w - 3, y - 7), (x + 3, y - 7)])
        pygame.draw.line(s, trim, (x - 3, y + 4), (x + w + 3, y + 4))
        pygame.draw.polygon(s, (10, 8, 16), [(x - 4, y + 4), (x + w + 4, y + 4), (x + w - 3, y - 7), (x + 3, y - 7)], 1)
        if kind != "tricornio":
            pygame.draw.circle(s, (240, 240, 240), (cx, y - 2), 2)                # caveira
        if kind == "capita":
            pygame.draw.polygon(s, (200, 60, 70), [(x + w - 4, y - 6), (x + w + 4, y - 14), (x + w, y - 4)])
        if kind == "pirata":
            pygame.draw.rect(s, (190, 30, 50), (x, y + 5, w, 3))                    # bandana por baixo
    elif kind == "cachecol":
        neck += 1
        pygame.draw.rect(s, trim, (cx - 7, neck, 15, 4), border_radius=1)
        pygame.draw.rect(s, trim, (cx + 3, neck + 2, 4, 9))
        pygame.draw.rect(s, (30, 20, 40), (cx - 7, neck, 15, 4), 1, border_radius=1)
    elif kind == "chapeu":
        pygame.draw.ellipse(s, (96, 62, 30), (x - 6, y + 1, w + 12, 7))
        pygame.draw.rect(s, (96, 62, 30), (cx - 7, y - 7, 14, 9), border_radius=2)
        pygame.draw.rect(s, (160, 50, 50), (cx - 7, y - 1, 14, 2))
        pygame.draw.ellipse(s, (40, 26, 16), (x - 6, y + 1, w + 12, 7), 1)
    elif kind in ("lenco", "lenco_amarelo"):
        col = (200, 50, 50) if kind == "lenco" else (220, 180, 60)
        pygame.draw.rect(s, col, (x, y + 1, w, 5), border_radius=2)
        pygame.draw.polygon(s, col, [(x + w - 1, y + 2), (x + w + 6, y), (x + w + 5, y + 7)])   # nó atrás
        for i in range(x + 2, x + w - 1, 4):
            s.set_at((i, y + 3), (250, 240, 230))
        pygame.draw.rect(s, (40, 16, 20), (x, y + 1, w, 5), 1, border_radius=2)


def _source(pose, phase):
    if pose == "walk":
        frames = sprites.grid("personagens/feiticeira_andando.png", 45, 58)
        return frames[int(phase * len(frames)) % len(frames)] if frames else None, (21, 57)
    if pose in ("attack", "shoot", "hurt"):
        acts = sprites.grid("personagens/feiticeira_acoes.png", 80, 64)
        if not acts:
            return None, (0, 0)
        if pose == "attack":
            fr = acts[0:4][min(3, int(phase * 4))]
        elif pose == "shoot":
            fr = acts[1]
        else:
            fr = acts[7 * 5]
        return fr, (40, 63)
    frames = sprites.grid("personagens/feiticeira_parada.png", 46, 55)
    return frames[int(phase * len(frames)) % len(frames)] if frames else None, (21, 54)


def character(style, pose="idle", phase=0.0, facing=1):
    """Quadro do personagem `style` (olhando para `facing`), com o pé em FOOT no quadro 80x64."""
    q = round(phase * 24) / 24
    key = (style, pose, q, facing)
    img = _cache.get(key)
    if img is not None:
        return img
    spec = CAST[style]
    src, foot = _source(pose, q)
    out = pygame.Surface(CANVAS, pygame.SRCALPHA)
    if src is not None:
        body, neck = _recolor(src, spec, spec["short"])
        if spec.get("hat"):
            _hat(body, spec["hat"], _head(body), spec, neck)
        sx, sy = spec.get("size", (1.0, 1.0))
        if (sx, sy) != (1.0, 1.0):
            bw, bh = body.get_size()
            body = pygame.transform.scale(body, (round(bw * sx), round(bh * sy)))
            foot = (round(foot[0] * sx), round(foot[1] * sy))
        if pose == "hurt":
            body.fill((255, 120, 120, 0), special_flags=pygame.BLEND_RGBA_MAX)
        out.blit(body, (FOOT[0] - foot[0], FOOT[1] - foot[1]))
    if facing > 0:                                  # o sprite original olha para a esquerda
        out = pygame.transform.flip(out, True, False)
    if len(_cache) > 2000:
        _cache.clear()
    _cache[key] = out
    return out
