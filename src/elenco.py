"""Elenco do jogo: tripulação, irmã da capitã, capangas e figurantes.

Todos saem de sprites de pacotes da internet, com outra paleta por região (cabelo, roupa, pele,
botas, detalhes e olhos) e um acessório desenhado por cima (chapéu, bandana, cachecol...):
- base "feiticeira" (padrão): sprite "sample idle & walk" (parada, andando) + ações de
  tools/gerar_feiticeira.py; papéis femininos;
- base "heroi": espadachim do Metroidvania Forge (heroi.png, com corrida e golpes); papéis masculinos.
Os modelos da equipe (npcs.png) ficam fora do elenco até chegarem as artes originais.
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
_EYE_COLORS = set(EYES)
PINS = [(77, 47, 30), (67, 21, 0)]
PIN_TIPS = [(169, 110, 103), (145, 88, 76)]   # pontas dos grampos (a mesma cor aparece no cano da bota)
WEAPON = [(47, 24, 80), (81, 55, 63)]
WEAPON_EDGE = [(166, 75, 10), (67, 21, 0)]

BASE = {"hair": HAIR[0], "coat": COAT[0], "skin": SKIN[0], "boots": BOOTS[0], "trim": TRIM[0], "eyes": EYES[2]}

CANVAS = (96, 80)
FOOT = (48, 77)                   # 3 px livres abaixo do pé (mesmo contrato dos desenhos antigos)
HAT_ROOM = 18                     # folga acima da cabeça para o chapéu não sair cortado
# lâmina das ações (tools/gerar_feiticeira.py): tons próprios, que viram aço nos outros personagens
BLADE = {(176, 180, 255): (214, 218, 228), (152, 156, 246): (150, 156, 172), (250, 250, 255): (250, 250, 255),
         (232, 232, 255): (240, 240, 250)}

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
    # figurantes e NPCs de serviço
    "ferreiro": {"hair": (60, 44, 36), "coat": (120, 90, 70), "skin": (210, 140, 100),
                 "boots": (60, 50, 44), "trim": (90, 70, 60), "eyes": (90, 70, 50), "short": True, "hat": "lenco",
                 "size": (1.08, 1.0)},
    "marinheiro": {"hair": (90, 60, 40), "coat": (220, 220, 230), "skin": (230, 160, 120),
                   "boots": (40, 60, 120), "trim": (40, 70, 150), "eyes": (60, 90, 160), "short": True, "hat": "bone"},
    "pescador": {"hair": (150, 150, 150), "coat": (90, 110, 80), "skin": (220, 150, 110),
                 "boots": (70, 60, 50), "trim": (200, 170, 80), "eyes": (80, 80, 60), "short": True, "hat": "chapeu"},
    "aldea": {"hair": (110, 60, 40), "coat": (150, 70, 60), "skin": (240, 170, 130), "boots": (90, 60, 40),
              "trim": (230, 220, 200), "eyes": (100, 70, 40), "short": False, "hat": "lenco_amarelo"},
    "curandeira": {"hair": (90, 150, 80), "coat": (220, 214, 190), "skin": (250, 180, 140), "boots": (110, 80, 50),
                   "trim": (90, 150, 80), "eyes": (70, 130, 70), "short": False},
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
    # cabelo curto: além de cortar no pescoço, tira o volume que sai muito para os lados da cabeça
    eyes = [(x, y) for y in range(h) for x in range(w) if px[y][x][3] and px[y][x][:3] in _EYE_COLORS]
    head_x = min(p[0] for p in eyes) + 6 if eyes else None
    brow = min(p[1] for p in eyes) - 8 if eyes else 0

    def trimmed(x, y):
        return short and (y > cut or (head_x is not None and y > brow and abs(x - head_x) > 11))
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
            if c in BLADE:                                   # lâmina das ações vira aço
                out.set_at((x, y), BLADE[c] + (a,))
                continue
            if c in hair_set and trimmed(x, y):
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
                    if trimmed(x, y):
                        continue
                    c = hair_dark
                else:
                    c = skin_dark
            else:
                c = pal.get(c, c)
            out.set_at((x, y), c + (a,))
    return out, neck


def _head(img):
    """Centro da cabeça (x) e linha da testa (y), a partir dos olhos.

    Os olhos acompanham o tronco girado dos golpes, então o chapéu fica sempre no lugar.
    Sem olhos visíveis, usa o topo do cabelo."""
    w, h = img.get_size()
    eyes = [(x, y) for y in range(h * 2 // 3) for x in range(w)
            if img.get_at((x, y)).a and tuple(img.get_at((x, y)))[:3] in _EYE_COLORS]
    if eyes:
        ex = min(p[0] for p in eyes)
        ey = min(p[1] for p in eyes)
        return ex + 6, ey - 6
    pts = [(x, y) for y in range(h // 2) for x in range(w) if img.get_at((x, y)).a]
    if not pts:
        return w // 2, 8
    top = min(p[1] for p in pts)
    row = [p[0] for p in pts if p[1] <= top + 8]
    return (min(row) + max(row)) // 2, top + 8


INK = (24, 18, 30)


def _hat(s, kind, head, spec, neck):
    """Acessório por cima do cabelo. `head` = (centro x, testa y); o rosto fica à esquerda."""
    cx, by = head
    trim = spec["trim"]
    if kind == "chef":
        crown = pygame.Rect(cx - 8, by - 13, 16, 12)
        pygame.draw.rect(s, (250, 250, 250), crown, border_radius=5)
        pygame.draw.rect(s, (226, 226, 234), (cx - 1, by - 12, 3, 10))            # dobra do pano
        pygame.draw.rect(s, INK, crown, 1, border_radius=5)
        pygame.draw.rect(s, (214, 214, 222), (cx - 9, by - 2, 18, 4))
        pygame.draw.rect(s, INK, (cx - 9, by - 2, 18, 4), 1)
    elif kind == "bone":
        cap = (40, 80, 160)
        pygame.draw.ellipse(s, cap, (cx - 10, by - 8, 20, 11))
        pygame.draw.ellipse(s, INK, (cx - 10, by - 8, 20, 11), 1)
        pygame.draw.line(s, (90, 130, 210), (cx - 5, by - 6), (cx + 2, by - 6))  # brilho
        pygame.draw.rect(s, (30, 60, 130), (cx - 16, by - 1, 10, 3))             # aba para a frente
        pygame.draw.rect(s, INK, (cx - 16, by - 1, 10, 3), 1)
    elif kind in ("tricornio", "capita", "pirata"):
        hat = (30, 26, 42)
        if kind == "pirata":                                                     # bandana por baixo
            tail = [(cx + 9, by), (cx + 15, by + 6), (cx + 11, by + 7)]
            pygame.draw.polygon(s, (190, 30, 50), tail)
            pygame.draw.polygon(s, INK, tail, 1)
            pygame.draw.rect(s, (190, 30, 50), (cx - 10, by - 1, 20, 4))
        pts = [(cx - 15, by), (cx - 10, by - 4), (cx - 7, by - 11), (cx + 7, by - 11), (cx + 10, by - 4),
               (cx + 15, by)]
        pygame.draw.polygon(s, hat, pts)
        pygame.draw.line(s, (62, 56, 84), (cx - 6, by - 10), (cx + 6, by - 10))   # brilho da copa
        pygame.draw.line(s, trim, (cx - 12, by - 1), (cx + 12, by - 1))
        pygame.draw.polygon(s, INK, pts, 1)
        if kind != "tricornio":                                                  # caveira
            pygame.draw.rect(s, (236, 236, 236), (cx - 2, by - 8, 4, 3))
            s.set_at((cx - 1, by - 5), (236, 236, 236))
            s.set_at((cx, by - 5), (236, 236, 236))
        if kind == "capita":                                                     # pluma para trás
            plume = [(cx + 6, by - 10), (cx + 16, by - 17), (cx + 12, by - 8)]
            pygame.draw.polygon(s, (200, 60, 70), plume)
            pygame.draw.polygon(s, INK, plume, 1)
    elif kind == "cachecol":
        neck += 1
        x0 = cx - 6
        pygame.draw.rect(s, trim, (x0 + 10, neck + 2, 4, 9))                      # ponta caída atrás
        pygame.draw.rect(s, INK, (x0 + 10, neck + 2, 4, 9), 1)
        pygame.draw.rect(s, trim, (x0, neck, 15, 4), border_radius=1)
        pygame.draw.rect(s, INK, (x0, neck, 15, 4), 1, border_radius=1)
    elif kind == "chapeu":
        felt = (96, 62, 30)
        pygame.draw.rect(s, felt, (cx - 8, by - 11, 16, 10), border_radius=3)
        pygame.draw.rect(s, INK, (cx - 8, by - 11, 16, 10), 1, border_radius=3)
        pygame.draw.ellipse(s, felt, (cx - 17, by - 3, 34, 6))
        pygame.draw.ellipse(s, INK, (cx - 17, by - 3, 34, 6), 1)
        pygame.draw.rect(s, (160, 50, 50), (cx - 7, by - 4, 14, 2))
    elif kind in ("lenco", "lenco_amarelo"):
        col = (200, 50, 50) if kind == "lenco" else (220, 180, 60)
        knot = [(cx + 8, by - 3), (cx + 15, by - 7), (cx + 14, by + 3)]          # nó atrás
        pygame.draw.polygon(s, col, knot)
        pygame.draw.polygon(s, INK, knot, 1)
        cloth = pygame.Rect(cx - 10, by - 9, 20, 11)
        pygame.draw.ellipse(s, col, cloth)
        pygame.draw.ellipse(s, INK, cloth, 1)
        pygame.draw.line(s, col, (cx - 9, by), (cx + 9, by))
        for i in range(cx - 6, cx + 7, 4):
            s.set_at((i, by - 4), (250, 240, 230))


def _source(pose, phase):
    if pose == "walk":
        frames = sprites.grid("personagens/feiticeira_andando.png", 45, 58)
        return frames[int(phase * len(frames)) % len(frames)] if frames else None, (21, 57)
    if pose in ("attack", "shoot", "hurt"):
        acts = sprites.grid("personagens/feiticeira_acoes.png", 96, 72)
        if not acts:
            return None, (0, 0)
        if pose == "attack":
            fr = acts[0:4][min(3, int(phase * 4))]
        elif pose == "shoot":
            fr = acts[1]
        else:
            fr = acts[7 * 5]
        return fr, (48, 71)
    frames = sprites.grid("personagens/feiticeira_parada.png", 46, 55)
    return frames[int(phase * len(frames)) % len(frames)] if frames else None, (21, 54)


# ---------------------------------------------------------------------------
# Segunda base: o espadachim do Metroidvania Forge (personagens/heroi.png, 80x80, olha para a
# direita). Serve para os papéis masculinos, com as cores trocadas por região como na feiticeira.
# ---------------------------------------------------------------------------

HERO_SHEET = "personagens/heroi.png"
HERO_FOOT = (41, 78)               # pé no quadro já virado para a esquerda
H_HAIR = [(233, 225, 207), (176, 164, 139), (141, 129, 106), (114, 104, 83), (88, 79, 61), (70, 58, 45),
          (255, 255, 255)]
H_ARMOR = [(167, 155, 144), (92, 92, 92), (132, 126, 135), (198, 188, 179), (244, 236, 219)]
H_PANTS = [(49, 47, 66), (76, 74, 92), (107, 104, 128)]
H_SCARF = [(57, 25, 19), (97, 26, 26), (154, 58, 58)]
H_SKIN = [(248, 189, 166), (227, 142, 116), (154, 65, 76), (255, 222, 193), (239, 211, 199)]
H_EYES = [(99, 155, 255), (71, 90, 198)]
H_BASE = {"hair": (176, 164, 139), "coat": (167, 155, 144), "boots": (76, 74, 92), "trim": (154, 58, 58),
          "skin": (248, 189, 166), "eyes": (99, 155, 255)}
_H_EYE_COLORS = set(H_EYES)


def _hero_source(pose, phase):
    """Quadro do espadachim para a pose (virado para a esquerda) e o pé."""
    f = sprites.grid(HERO_SHEET, 80, 80)
    if not f:
        return None
    if pose == "walk":
        idx = list(range(12, 16)) + list(range(16, 20))
        i = idx[int(phase * len(idx)) % len(idx)]
    elif pose == "attack":
        i = 32 + min(4, int(phase * 5))
    elif pose == "shoot":
        i = 34
    elif pose == "hurt":
        i = 30
    else:
        i = int(phase * 12) % 12
    return pygame.transform.flip(f[i], True, False)


def _hero_recolor(src, spec):
    m = {}
    for region, colors in (("hair", H_HAIR), ("coat", H_ARMOR), ("boots", H_PANTS), ("trim", H_SCARF),
                           ("skin", H_SKIN), ("eyes", H_EYES)):
        for c in colors:
            m[c] = _tone(spec[region], c, H_BASE[region])
    w, h = src.get_size()
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        for x in range(w):
            c = src.get_at((x, y))
            if c.a:
                rgb = tuple(c)[:3]
                out.set_at((x, y), m.get(rgb, rgb) + (c.a,))
    return out


def _hero_head(img):
    """Centro da cabeça e testa do espadachim (pelos olhos azuis)."""
    w, h = img.get_size()
    eyes = [(x, y) for y in range(h * 2 // 3) for x in range(w)
            if img.get_at((x, y)).a and tuple(img.get_at((x, y)))[:3] in _H_EYE_COLORS]
    if not eyes:
        return _head(img)
    return min(p[0] for p in eyes) + 3, min(p[1] for p in eyes) - 8


def _hero_body(spec, pose, phase):
    """Espadachim com as cores do papel e o acessório. Retorna (imagem, pé)."""
    src = _hero_source(pose, phase)
    if src is None:
        return None, None
    hair_cols = {_tone(spec["hair"], c, H_BASE["hair"]) for c in H_HAIR}
    body = _hero_recolor(src, spec)
    foot = HERO_FOOT
    if spec.get("hat"):
        padded = pygame.Surface((body.get_width() + 16, body.get_height() + HAT_ROOM), pygame.SRCALPHA)
        padded.blit(body, (8, HAT_ROOM))
        body, foot = padded, (foot[0] + 8, foot[1] + HAT_ROOM)
        head = _hero_head(body)
        if spec["hat"] != "cachecol":            # o cabelo espetado não pode furar o chapéu
            for y in range(0, head[1] - 9):
                for x in range(body.get_width()):
                    c = body.get_at((x, y))
                    if c.a and tuple(c)[:3] in hair_cols:
                        body.set_at((x, y), (0, 0, 0, 0))
        neck = head[1] + 14
        _hat(body, spec["hat"], head, spec, neck)
    return body, foot


def character(style, pose="idle", phase=0.0, facing=1):
    """Quadro do personagem `style` (olhando para `facing`), com o pé em FOOT no quadro 96x80.

    Base "feiticeira" (padrão) ou "heroi" (espadachim), as duas de pacotes da internet."""
    # Artes próprias geradas para os figurantes; mantêm o contrato de quadro do elenco.
    pixel_lab = {
        "px_comerciante": "comerciante", "px_ferreira": "ferreira", "px_curandeira": "curandeira",
        "px_pescador": "pescador", "px_estudioso": "estudioso", "px_bardo": "bardo",
        "px_anciao": "anciao", "px_ancia": "ancia", "px_aldea": "aldea", "px_grumete": "grumete",
    }
    if style in pixel_lab:
        # Folha animada (parado/andando/ataque) feita por tools/animar_pose.py, já na altura
        # combinada com a protagonista. Sem ela, cai na pose parada reduzida.
        quadro, pe = sprites.pose_anim(pixel_lab[style], "walk" if pose in ("walk", "run") else
                                       ("attack" if pose == "attack" else "idle"), phase)
        if quadro is not None:
            out = pygame.Surface(CANVAS, pygame.SRCALPHA)
            if facing < 0:
                quadro = pygame.transform.flip(quadro, True, False)
                pe = (quadro.get_width() - 1 - pe[0], pe[1])
            out.blit(quadro, (FOOT[0] - pe[0], FOOT[1] - pe[1]))
            return out
        src = sprites.image("personagens", f"npc_{pixel_lab[style]}.png")
        if src is not None:
            out = pygame.Surface(CANVAS, pygame.SRCALPHA)
            w, h = src.get_size()
            scale = min(58 / max(1, w), 62 / max(1, h))
            body = pygame.transform.scale(src, (max(1, round(w * scale)), max(1, round(h * scale))))
            # A vista `east` do PixelLab já olha para a direita.
            if facing < 0:
                body = pygame.transform.flip(body, True, False)
            out.blit(body, body.get_rect(midbottom=FOOT))
            return out
    q = round(phase * 24) / 24
    key = (style, pose, q, facing)
    img = _cache.get(key)
    if img is not None:
        return img
    spec = CAST[style]
    out = pygame.Surface(CANVAS, pygame.SRCALPHA)
    if spec.get("base") == "heroi":
        body, foot = _hero_body(spec, pose, q)
    else:
        body, foot = None, None
        src, foot = _source(pose, q)
        if src is not None:
            body, neck = _recolor(src, spec, spec["short"])
            if spec.get("hat"):
                padded = pygame.Surface((body.get_width() + 16, body.get_height() + HAT_ROOM), pygame.SRCALPHA)
                padded.blit(body, (8, HAT_ROOM))
                body, neck, foot = padded, neck + HAT_ROOM, (foot[0] + 8, foot[1] + HAT_ROOM)
                _hat(body, spec["hat"], _head(body), spec, neck)
    if body is not None:
        sx, sy = spec.get("size", (1.0, 1.0))
        if (sx, sy) != (1.0, 1.0):
            bw, bh = body.get_size()
            body = pygame.transform.scale(body, (round(bw * sx), round(bh * sy)))
            foot = (round(foot[0] * sx), round(foot[1] * sy))
        if pose == "hurt":
            body.fill((64, 12, 12, 0), special_flags=pygame.BLEND_RGB_ADD)      # avermelha sem apagar o traço
        out.blit(body, (FOOT[0] - foot[0], FOOT[1] - foot[1]))
    if facing > 0:                                  # as bases ficam viradas para a esquerda
        out = pygame.transform.flip(out, True, False)
    if len(_cache) > 2000:
        _cache.clear()
    _cache[key] = out
    return out
