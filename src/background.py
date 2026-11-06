"""Fundos com profundidade (parallax), decoração presa ao cenário e clima.

As decorações (lanternas, escotilhas, braseiros) são posicionadas a partir dos
tiles da sala e desenhadas em coordenadas do MUNDO: elas não acompanham a
câmera nem os pulos do jogador.
"""

import math
import random

import pygame

from . import paisagem as pz
from . import sprites
from .config import Display
from .tiles import ISLAND, T, theme_of

W, H = Display.WIDTH, Display.HEIGHT

SKY = {
    "deck": ((6, 8, 22), (34, 42, 74)),
    "island": ((8, 10, 24), (30, 44, 62)),
    "ruins": ((10, 10, 22), (40, 40, 64)),
}

_static = {}

# céus em camadas (Craftpix, "New free backgrounds"): nome do arquivo, escurecimento (noite)
SKY_PACKS = {
    "noite": 0.72, "tempestade": 0.8, "roxo": 0.6, "cinza": 0.62,
    "porsol": 0.8, "crepusculo": 0.62,      # pacotes 2 (fundo 2) e 4 (fundo 2); camadas 4 e 5 fundidas
}
SKY_OF_ROOM = {"cordame1": "tempestade", "cordame2": "tempestade", "gavea": "tempestade", "ruinas": "cinza",
               "praia": "porsol", "floresta": "crepusculo"}
SKY_OF_THEME = {"deck": "noite", "island": "roxo", "ruins": "cinza"}
SKY_PARALLAX = (0.0, 0.015, 0.035, 0.06)


def _sky_layers(name):
    """As 4 camadas do céu em 2x (pixel art sem borrar), escurecidas para a noite.
    No céu de tempestade, o raio desenhado na última camada vira uma camada à parte
    (só aparece quando o relâmpago pisca)."""
    key = ("sky", name)
    if key not in _static:
        k = SKY_PACKS[name]
        layers, bolt = [], None
        for i in range(1, 5):
            img = sprites.image("fundos", f"ceu_{name}_{i}.png")
            if img is None:
                layers = []
                break
            img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
            if name == "tempestade" and i == 4:
                bolt = pygame.Surface(img.get_size(), pygame.SRCALPHA)
                w, h = img.get_size()
                for y in range(h):
                    for x in range(w):
                        c = img.get_at((x, y))
                        if c.a and c.r + c.g + c.b > 520:
                            bolt.set_at((x, y), c)
                            img.set_at((x, y), (0, 0, 0, 0))
            if k != 1.0:
                v = int(255 * k)
                img.fill((v, v, v, 255), special_flags=pygame.BLEND_RGBA_MULT)
            layers.append(img)
        _static[key] = (layers, bolt)
    return _static[key]

# figurantes (sala -> [(modelo, coluna, linha do chão, alcance em px, atividade)])
# No máximo 2 por sala. Atividades: "parado" (encostado, respirando), "pesca" (vara e linha),
# "caixa" (anda devagar carregando um caixote) e "anda" (passeio lento com pausas nas pontas).
WALKERS = {
    "conves": [("bardo", 47, 18, 0, "pesca"), ("aldea", 60, 18, 56, "caixa")],
    "cabine": [("bardo", 22, 14, 0, "parado")],
    "praia": [("fazendeiro", 8, 18, 0, "parado"), ("velho", 28, 18, 40, "anda")],
    "floresta": [("anciã", 14, 37, 36, "anda")],
    "ruinas": [("velho", 4, 17, 0, "parado")],
}


def _gradient(top, bottom, h=H):
    key = ("grad", top, bottom, h)
    if key not in _static:
        s = pygame.Surface((W, h))
        for y in range(0, h, 4):
            k = y / h
            pygame.draw.rect(s, tuple(int(a + (b - a) * k) for a, b in zip(top, bottom)), (0, y, W, 4))
        _static[key] = s
    return _static[key]


def _wall_texture(theme):
    """Parede do fundo: madeira escura (SBS, CC0) ou tijolo do templo, escurecida."""
    key = ("wall", theme)
    if key not in _static:
        if theme == "temple":
            tile = sprites.crop(ISLAND, (0, 320, 32, 32))
            base = pygame.transform.scale(tile, (64, 64)) if tile is not None else pygame.Surface((64, 64))
        else:
            tex = sprites.image("fundos", "madeira_escura.png")
            base = pygame.transform.smoothscale(tex, (96, 96)) if tex is not None else pygame.Surface((96, 96))
        wall = pygame.Surface((base.get_width() * 4, base.get_height() * 4))
        for x in range(0, wall.get_width(), base.get_width()):
            for y in range(0, wall.get_height(), base.get_height()):
                wall.blit(base, (x, y))
        dark = {"hull": (70, 60, 56), "bilge": (48, 50, 52), "temple": (70, 80, 86)}.get(theme, (70, 60, 56))
        wall.fill(dark + (255,), special_flags=pygame.BLEND_RGB_MULT)
        _static[key] = wall
    return _static[key]


def _glow(radius, color):
    key = ("glow", radius, color)
    if key not in _static:
        # cor já multiplicada pela intensidade: desenhada com BLEND_RGB_ADD (soma de luz)
        s = pygame.Surface((radius * 2, radius * 2))
        s.fill((0, 0, 0))
        for r in range(radius, 0, -2):
            k = 0.32 * (1 - r / radius) ** 1.8
            pygame.draw.circle(s, tuple(int(c * k) for c in color), (radius, radius), r)
        _static[key] = s
    return _static[key]


def _prop(kind):
    """Caixote e barril (folha de objetos do Metroidvania Forge), um pouco escurecidos:
    são cenário de fundo, não plataformas."""
    key = ("prop", kind)
    if key not in _static:
        rect = {"crate": (53, 28, 40, 35), "barrel": (109, 38, 23, 25)}[kind]
        img = sprites.crop("objetos/caixas.png", rect)
        if img is not None:
            img = img.copy()
            img.fill((150, 140, 140, 255), special_flags=pygame.BLEND_RGBA_MULT)
        _static[key] = img
    return _static[key]


FLORA = {"bush": (640, 224, 32, 32), "tall": (672, 232, 31, 56), "sprout": (550, 231, 18, 25),
         "rock": (642, 196, 61, 26), "rock2": (704, 197, 32, 25)}


def _flora(kind, theme, flip):
    """Arbusto, broto e pedra do tileset da ilha, ou coluna quebrada de pedra; um pouco
    escurecidos e azulados para ficarem no plano de trás (não parecem plataformas)."""
    key = ("flora", kind, theme, flip)
    if key not in _static:
        if kind == "column":
            img = _column(len(theme) + flip, 54 + 18 * flip)
        else:
            img = sprites.crop(ISLAND, FLORA[kind])
            if img is not None and kind.startswith("rock"):
                img = pygame.transform.scale(img, (img.get_width() * 2 // 3, img.get_height() * 2 // 3))
        if img is not None:
            img = img.copy()
            tom = {"island": (150, 160, 170), "ruins": (140, 140, 156), "temple": (120, 140, 150)}[theme]
            img.fill(tom + (255,), special_flags=pygame.BLEND_RGBA_MULT)
            if flip:
                img = pygame.transform.flip(img, True, False)
        _static[key] = img
    return _static[key]


def _column(seed, alt):
    """Toco de coluna de pedra com blocos, luz à esquerda, topo partido e musgo."""
    rnd = random.Random(seed)
    w = 22
    s = pygame.Surface((w + 4, alt), pygame.SRCALPHA)
    pedra, escura, clara = (104, 104, 114), (58, 58, 70), (140, 140, 150)
    topo = [(2, 8)] + [(2 + k * (w - 2) / 5, rnd.randint(0, 9)) for k in range(1, 5)] + [(w, 6)]
    corpo = topo + [(w, alt - 6), (2, alt - 6)]
    pygame.draw.polygon(s, escura, [(x + 1, y + 1) for x, y in corpo])
    pygame.draw.polygon(s, pedra, corpo)
    pygame.draw.rect(s, escura, (w - 5, 8, 4, alt - 14))                 # lado da sombra
    pygame.draw.line(s, clara, (3, 9), (3, alt - 7))                      # lado da luz
    for y in range(18, alt - 8, 14):                                      # juntas dos blocos
        pygame.draw.line(s, escura, (2, y), (w, y))
    for x in (8, 14):                                                     # caneluras
        pygame.draw.line(s, (90, 90, 100), (x, 12), (x, alt - 8))
    pygame.draw.rect(s, escura, (0, alt - 7, w + 4, 7))                   # base
    pygame.draw.line(s, clara, (0, alt - 7), (w + 3, alt - 7))
    for _ in range(6):                                                    # musgo
        mx = rnd.randint(2, w - 2)
        pygame.draw.line(s, (70, 110, 64), (mx, alt - 8), (mx, alt - 8 - rnd.randint(2, 8)))
    return s


def _blit_mid(surf, img, sx, sy):
    surf.blit(img, img.get_rect(midbottom=(round(sx), round(sy))))


def _coil():
    """Rolo de corda deitado no chão: anéis empilhados com a ponta solta."""
    key = ("coil",)
    if key not in _static:
        s = pygame.Surface((26, 13), pygame.SRCALPHA)
        corda, escura, clara = (138, 108, 70), (60, 44, 30), (176, 146, 100)
        for w, y in ((24, 4), (20, 2), (14, 0)):
            r = pygame.Rect((26 - w) // 2, y, w, 9)
            pygame.draw.ellipse(s, escura, r.inflate(2, 2))
            pygame.draw.ellipse(s, corda, r)
            pygame.draw.ellipse(s, escura, r.inflate(-6, -4))
            pygame.draw.arc(s, clara, r, 0.4, 2.6, 1)
        pygame.draw.lines(s, escura, False, [(22, 9), (25, 11), (25, 12)], 2)
        img = s.copy()
        img.fill((150, 140, 140, 255), special_flags=pygame.BLEND_RGBA_MULT)   # fundo: mais escuro
        _static[key] = img
    return _static[key]


def _bucket():
    """Balde de madeira com aros de ferro."""
    key = ("bucket",)
    if key not in _static:
        s = pygame.Surface((14, 15), pygame.SRCALPHA)
        pygame.draw.arc(s, (70, 70, 80), (2, 0, 10, 8), 0, math.pi, 1)
        pygame.draw.polygon(s, (20, 14, 16), [(0, 3), (13, 3), (12, 14), (1, 14)])
        pygame.draw.polygon(s, (100, 68, 42), [(1, 4), (12, 4), (11, 13), (2, 13)])
        for y in (6, 11):
            pygame.draw.line(s, (64, 66, 76), (1, y), (12, y))
        pygame.draw.line(s, (136, 100, 64), (3, 4), (3, 12))
        _static[key] = s
    return _static[key]


def _net():
    """Rede de pesca pendurada em dois pregos, com boias de cortiça."""
    key = ("net",)
    if key not in _static:
        w, h = 46, 40
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        fio = (88, 80, 66, 190)
        topo = [(2 + k * (w - 4) / 8, 2 + 5 * math.sin(math.pi * k / 8)) for k in range(9)]
        fundo = [(w / 2 + (x - w / 2) * 0.45, h - 3) for x, _ in topo]
        for a, b in zip(topo, fundo):                 # fios caindo e juntando embaixo
            pygame.draw.line(s, fio, a, b)
        for k in range(1, 6):                          # carreiras de nós
            t = k / 6
            pts = [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t) for a, b in zip(topo, fundo)]
            pygame.draw.lines(s, fio, False, pts)
        pygame.draw.lines(s, (60, 46, 34), False, topo, 2)
        for x in (2, w - 3):
            pygame.draw.circle(s, (120, 120, 130), (x, 2), 2)
        for x, y in ((15, 18), (31, 25)):
            pygame.draw.ellipse(s, (40, 26, 20), (x - 4, y - 3, 9, 7))
            pygame.draw.ellipse(s, (176, 112, 58), (x - 3, y - 2, 7, 5))
        _static[key] = s
    return _static[key]


def _web(lado):
    """Teia de aranha no canto do teto; lado -1 = parede à esquerda."""
    key = ("web", lado)
    if key not in _static:
        n = 26
        s = pygame.Surface((n, n), pygame.SRCALPHA)
        cor = (170, 170, 180, 70)
        raios = [(n - 1, 0), (n - 1, n * 0.45), (n * 0.75, n * 0.75), (n * 0.45, n - 1), (0, n - 1)]
        for p in raios:
            pygame.draw.line(s, cor, (0, 0), p)
        for k in (0.35, 0.65, 0.95):
            pygame.draw.lines(s, cor, False, [(p[0] * k, p[1] * k) for p in raios])
        if lado > 0:
            s = pygame.transform.flip(s, True, False)
        _static[key] = s
    return _static[key]


def _pool(rx, ry, color):
    """Poça de luz achatada (somada à cena)."""
    key = ("pool", rx, ry, color)
    if key not in _static:
        _static[key] = pygame.transform.smoothscale(_glow(64, color), (rx * 2, ry * 2))
    return _static[key]


def _cone(alt, color):
    """Cone de luz da lanterna até o chão, mais forte perto da chama."""
    alt = max(8, int(alt) // 8 * 8)
    key = ("cone", alt, color)
    if key not in _static:
        w = 26 + alt // 2
        s = pygame.Surface((w, alt))
        for y in range(alt):
            k = (1 - y / alt) ** 1.8 * 0.3
            meia = 5 + (w / 2 - 5) * y / alt
            for f, m in ((0.45, 1.0), (0.75, 0.7), (1.0, 0.4)):     # miolo mais forte, borda suave
                pygame.draw.line(s, tuple(int(c * k * f) for c in color), (w / 2 - meia * m, y), (w / 2 + meia * m, y))
        _static[key] = s
    return _static[key]


def _shaft():
    """Feixe de luar entrando pela escotilha, descendo na diagonal."""
    key = ("shaft",)
    if key not in _static:
        comp, w = 150, 110
        s = pygame.Surface((w, comp))
        for y in range(comp):
            k = (1 - y / comp) ** 1.4 * 0.16
            x0 = 10 + y * 0.5
            meia = 7 + y * 0.12
            pygame.draw.line(s, (int(150 * k), int(170 * k), int(220 * k)), (x0 - meia, y), (x0 + meia, y))
        _static[key] = s
    return _static[key]


def _splash_frames():
    """Respingo (Super Pixel Effects, "burst splatter" verde) pintado de água e reduzido."""
    key = ("splash",)
    if key not in _static:
        out = []
        for fr in sprites.effect("respingo"):
            f = pygame.transform.scale(fr, (fr.get_width() // 2, fr.get_height() // 2))
            f.fill((120, 170, 255, 210), special_flags=pygame.BLEND_RGBA_MULT)
            out.append(f)
        _static[key] = out
    return _static[key]


def _vignette():
    """Bordas escurecidas: elipses concêntricas, cada uma sobrescreve o alfa do miolo."""
    key = ("vignette",)
    if key not in _static:
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        steps = 20
        for i in range(steps + 1):
            k = i / steps                       # 0 = borda, 1 = centro
            alpha = int(140 * (1 - k) ** 2)
            rect = pygame.Rect(0, 0, int(W * (1.5 - 0.6 * k)), int(H * (1.5 - 0.6 * k)))
            rect.center = (W // 2, H // 2)
            if i == 0:
                s.fill((0, 0, 0, alpha))
            pygame.draw.ellipse(s, (0, 0, 0, alpha), rect)
        _static[key] = s
    return _static[key]


def _tree_layer(seed, color, height):
    key = ("trees", seed, color, height)
    if key not in _static:
        sil = [sprites.crop(ISLAND, (720, 296, 96, 216)), sprites.crop(ISLAND, (776, 188, 152, 324))]
        s = pygame.Surface((W * 2, height), pygame.SRCALPHA)
        rnd = random.Random(seed)
        x = 0
        while x < W * 2:
            t = rnd.choice([t for t in sil if t is not None] or [None])
            if t is None:
                break
            k = rnd.uniform(0.6, 1.0)
            img = pygame.transform.scale(t, (int(t.get_width() * k), int(t.get_height() * k)))
            img.fill(color + (255,), special_flags=pygame.BLEND_RGBA_MULT)
            s.blit(img, (x, height - img.get_height()))
            x += int(img.get_width() * rnd.uniform(0.5, 0.9))
        _static[key] = s
    return _static[key]


class Background:
    def __init__(self, room):
        self.room = room
        self.theme = theme_of(room.zone)
        self.decor = self._place_decor()
        rnd = random.Random(hash(room.id) & 0xFFFF)
        self.stars = [(rnd.uniform(0, W), rnd.uniform(0, H * 0.6), rnd.random()) for _ in range(70)]
        self.rain = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0.7, 1.2)) for _ in range(90)]
        self.next_flash = rnd.uniform(4, 9)
        self.flash = 0.0
        self.rng = random.Random(len(room.id))   # aleatório próprio: não mexe no do jogo
        self.motes = []                  # partículas de ambiente (mundo): vaga-lumes, folhas, poeira, gotas
        self.time = 0.0

    # --- decoração presa ao cenário ---
    def _place_decor(self):
        room = self.room
        out = []
        solid = room.is_solid
        if self.theme in ("hull", "bilge"):
            for tx in range(3, room.cols - 3, 8):
                for ty in range(1, room.rows_count - 6):
                    if solid(tx, ty) and not solid(tx, ty + 1) and all(not solid(tx, ty + k) for k in range(1, 5)):
                        chao = next((k for k in range(ty + 1, min(room.rows_count, ty + 7))
                                     if solid(tx, k) or room.is_oneway(tx, k)), None)
                        out.append(("lantern", tx * T + 16, (ty + 1) * T, chao * T if chao else None))
                        break
            for tx in range(6, room.cols - 4, 11):
                for ty in range(room.rows_count - 6, 2, -1):
                    if all(not solid(tx + dx, ty + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                        out.append(("porthole", tx * T + 16, ty * T + 16))
                        break
        rnd = random.Random(sum(map(ord, room.id)))
        if self.theme in ("hull", "bilge", "deck"):
            tx = 3
            while tx < room.cols - 3:
                placed = False
                for ty in range(2, room.rows_count):
                    if room.tile(tx, ty) == "#" and room.tile(tx, ty - 1) == "." and room.tile(tx, ty - 2) == "."                             and room.tile(tx + 1, ty) == "#" and room.tile(tx + 1, ty - 1) == ".":
                        kind = rnd.choice(("crate", "barrel", "barrel", "stack"))
                        out.append((kind, tx * T + T, ty * T))
                        placed = True
                        break
                tx += rnd.randint(7, 12) if placed else 3
        if self.theme in ("hull", "bilge"):
            for tx in range(8, room.cols - 4, 14):
                out.insert(0, ("beam", tx * T + 16, 0))
            # teias nos cantos do teto (bloco em cima e de um lado, ar embaixo)
            usados = set()
            for ty in range(1, room.rows_count - 1):
                for tx in range(1, room.cols - 1):
                    if room.tile(tx, ty) != "." or not solid(tx, ty - 1) or (tx // 6, ty // 4) in usados:
                        continue
                    for lado in (-1, 1):
                        if solid(tx + lado, ty) and rnd.random() < 0.55:
                            out.append(("web", tx * T + (0 if lado < 0 else T), ty * T, lado))
                            usados.add((tx // 6, ty // 4))
                            break
            # rede de pesca pendurada na parede
            for tx in range(10, room.cols - 4, 17):
                for ty in range(room.rows_count - 3, 2, -1):
                    if room.tile(tx, ty) in ("#", "X") and all(room.tile(tx + dx, ty - dy) == "."
                                                              for dx in (-1, 0, 1) for dy in (1, 2, 3)):
                        out.append(("net", tx * T + 16, ty * T - 52))
                        break
        if self.theme in ("hull", "bilge", "deck"):
            # rolos de corda e baldes no chão, longe dos caixotes
            ocupados = [it[1] for it in out if it[0] in ("crate", "barrel", "stack")]
            tx = 5
            while tx < room.cols - 3:
                feito = False
                for ty in range(2, room.rows_count):
                    if (room.tile(tx, ty) == "#" and room.tile(tx, ty - 1) == "." and room.tile(tx, ty - 2) == "."
                            and all(abs(o - tx * T) > 70 for o in ocupados)):
                        out.append((rnd.choice(("coil", "coil", "bucket")), tx * T + 16, ty * T))
                        feito = True
                        break
                tx += rnd.randint(9, 15) if feito else 4
        if self.theme == "deck":
            floor = max((ty for ty in range(room.rows_count) if room.tile(1, ty) == "#" and room.tile(1, ty - 1) == "."),
                        default=room.rows_count - 4)
            out.insert(0, ("rail", 0, floor * T))
            out.insert(0, ("mast", 29 * T, floor * T))
        if self.theme in ("island", "ruins"):
            for tx in range(1, room.cols - 1):
                for ty in range(1, room.rows_count):
                    if room.tile(tx, ty) == "#" and room.tile(tx, ty - 1) == "." and rnd.random() < 0.35:
                        out.append(("tuft", tx * T + rnd.randint(4, 28), ty * T))
                    if (self.theme == "island" and room.tile(tx, ty) == "#" and room.tile(tx, ty + 1) == "."
                            and rnd.random() < 0.18):
                        out.append(("vine", tx * T + rnd.randint(6, 26), (ty + 1) * T))
        if self.theme in ("island", "ruins", "temple"):
            # plantas, pedras e colunas quebradas no chão (atrás da cena), espaçadas
            opcoes = {"island": ("bush", "bush", "tall", "sprout", "rock", "rock2"),
                      "ruins": ("column", "rock", "rock2", "sprout", "bush"),
                      "temple": ("column", "rock2", "rock")}[self.theme]
            tx = 2 + rnd.randint(0, 3)
            while tx < room.cols - 2:
                feito = False
                for ty in range(2, room.rows_count):
                    if (room.tile(tx, ty) == "#" and all(room.tile(tx + dx, ty - dy) == "."
                                                         for dx in (-1, 0, 1) for dy in (1, 2))):
                        out.append(("flora", tx * T + rnd.randint(4, 28), ty * T, rnd.choice(opcoes), rnd.random() < 0.5))
                        feito = True
                        break
                tx += rnd.randint(4, 8) if feito else 2
        for name, tx, ty, span, *atividade in WALKERS.get(room.id, ()):
            out.append(("walker", tx * T + 16, ty * T, name, span, atividade[0] if atividade else "anda"))
        if self.theme in ("temple", "ruins"):
            for tx in range(2, room.cols - 2, 7):
                for ty in range(room.rows_count - 2, 1, -1):
                    if solid(tx, ty) and not solid(tx, ty - 1) and not solid(tx, ty - 2) and room.tile(tx, ty - 1) == ".":
                        out.append(("brazier", tx * T + 16, ty * T))
                        break
        return out

    def update(self, dt, cam=None):
        self.time += dt
        self._update_motes(dt, cam)
        if self.theme == "deck" or SKY_OF_ROOM.get(self.room.id) == "tempestade":
            self.next_flash -= dt
            self.flash = max(0.0, self.flash - dt)
            if self.next_flash <= 0:
                self.flash = 0.25
                self.next_flash = self.rng.uniform(6, 12)

    # --- desenho ---
    def draw(self, surf, cam_x, cam_y, time):
        th = self.theme
        sky = SKY_OF_ROOM.get(self.room.id, SKY_OF_THEME.get(th))
        layers, bolt = _sky_layers(sky) if sky else ([], None)
        if th in SKY and layers:
            self._draw_sky(surf, layers, bolt, cam_x, cam_y, time)
            self._layers(surf, cam_x, cam_y, time, packed_sky=True)
        elif th in SKY:
            top, bottom = SKY[th]
            surf.blit(_gradient(top, bottom), (0, 0))
            for x, y, b in self.stars:
                sx = (x - cam_x * 0.03) % W
                c = int(120 + 90 * b * (0.6 + 0.4 * math.sin(time * 2 + x)))
                surf.set_at((int(sx), int(y)), (c, c, min(255, c + 30)))
            surf.blit(_glow(150, (120, 130, 190)), (W - 300, -60), special_flags=pygame.BLEND_RGB_ADD)
            pygame.draw.circle(surf, (226, 230, 240), (W - 150, 90), 34)
            pygame.draw.circle(surf, (200, 204, 220), (W - 162, 82), 8)
            pygame.draw.circle(surf, (205, 210, 226), (W - 138, 100), 5)
            self._layers(surf, cam_x, cam_y, time)
        elif th == "temple":
            hall = pz.temple_hall(7, (34, 40, 46), (54, 62, 70), (90, 220, 200))
            surf.blit(hall, (-(cam_x * 0.5) % W - W, -cam_y * 0.2 % 1))
            pulse = 0.6 + 0.4 * math.sin(time * 1.6)
            surf.blit(pz.light_rays((int(120 * pulse), int(200 * pulse), int(190 * pulse)), 4, 3), (0, 0),
                      special_flags=pygame.BLEND_RGB_ADD)
            surf.blit(pz.mist((40, 70, 80), 70, 140), (-(cam_x * 0.6 + time * 8) % W - W, H - 170 - cam_y * 0.05))
        else:
            surf.fill((10, 10, 14))
            wall = _wall_texture(th)
            ww, wh = wall.get_size()
            ox = -(cam_x * 0.8) % ww
            oy = -(cam_y * 0.8) % wh
            for x in range(-1, W // ww + 2):
                for y in range(-1, H // wh + 2):
                    surf.blit(wall, (x * ww + ox - ww, y * wh + oy - wh))
        self._draw_decor(surf, cam_x, cam_y, time)

    def _draw_sky(self, surf, layers, bolt, cam_x, cam_y, time):
        """Céu do pacote: camadas com parallax lento e nuvens andando com o vento."""
        lh = layers[0].get_height()
        y = -min(lh - H, max(0, cam_y * 0.03))
        for i, img in enumerate(layers):
            lw = img.get_width()
            x0 = -((cam_x * SKY_PARALLAX[i] + time * (2 + 3 * i) * (i > 0)) % lw)
            for x in (x0, x0 + lw):
                if x < W:
                    surf.blit(img, (x, y))
        if bolt is not None and self.flash > 0:
            x0 = -((cam_x * SKY_PARALLAX[3]) % bolt.get_width())
            surf.blit(bolt, (x0, y))

    def _layers(self, surf, cam_x, cam_y, time, packed_sky=False):
        """Paisagem em camadas (parallax) para o convés, a ilha e as ruínas.
        packed_sky: o céu do pacote já foi desenhado (sem as nuvens desenhadas por código)."""
        th = self.theme
        drift = time * 6

        def band(img, par, y, speed=0.0):
            x0 = -((cam_x * par + time * speed) % img.get_width())
            for x in (x0, x0 + img.get_width()):
                if x < W:
                    surf.blit(img, (x, y))

        if not packed_sky:
            band(pz.clouds(5, (44, 52, 86, 140)), 0.04, 30 - cam_y * 0.02, 4)
        band(pz.mountains(11, (36, 44, 74), 260, 1.1, snow=(150, 160, 200)), 0.08, H - 330 - cam_y * 0.04)
        if th != "deck":
            c = pz.castle(4, (30, 34, 60), (250, 200, 110))
            cx = W * 0.62 - (cam_x * 0.1) % (W * 1.6)
            surf.blit(c, (cx, H - 380 - cam_y * 0.05))
        band(pz.mist((70, 80, 120), 60), 0.12, H - 260 - cam_y * 0.06, 10)
        if not packed_sky:
            band(pz.clouds(9, (60, 68, 104, 120), 5, height=160), 0.1, 90 - cam_y * 0.03, 9)
        if th == "deck":
            self._draw_sea(surf, cam_x, cam_y, time)
            return
        band(pz.mountains(23, (26, 34, 56), 200, 0.8), 0.18, H - 240 - cam_y * 0.08)
        if th == "ruins":
            band(pz.ruins_layer(6, (24, 28, 46)), 0.3, H - 320 - cam_y * 0.12)
        far = _tree_layer(3, (40, 52, 80), 330)
        near = _tree_layer(9, (22, 30, 48), 420)
        surf.blit(far, (-(cam_x * 0.25) % W - W, H - far.get_height() + 40 - cam_y * 0.1))
        band(pz.mist((90, 110, 140), 45, 70), 0.35, H - 150 - cam_y * 0.12, 16 + drift * 0)
        surf.blit(near, (-(cam_x * 0.4) % W - W, H - near.get_height() + 80 - cam_y * 0.15))
        surf.blit(pz.light_rays((150, 170, 230), 5, 2), (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def _draw_sea(self, surf, cam_x, cam_y, time):
        horizon = self.room.height - cam_y - 40 + (cam_y * 0.0)
        horizon = min(H - 40, max(H * 0.55, horizon * 0.35 + H * 0.45))
        for layer, (col, amp, spd, par) in enumerate((((26, 46, 78), 5, 1.0, 0.1), ((18, 34, 60), 7, 1.4, 0.2))):
            pts = [(0, H)]
            y0 = horizon + layer * 26
            for x in range(0, W + 16, 16):
                pts.append((x, y0 + math.sin((x + cam_x * par) * 0.018 + time * spd + layer) * amp))
            pts.append((W, H))
            pygame.draw.polygon(surf, col, pts)

    def _draw_decor(self, surf, cam_x, cam_y, time):
        fire = sprites.effect("fogo")
        for item in self.decor:
            kind, x, y = item[0], item[1], item[2]
            sx, sy = x - cam_x, y - cam_y
            # peças grandes fazem o próprio recorte
            if kind == "walker":
                self._draw_walker(surf, x, y, item, cam_x, cam_y, time)
                continue
            if kind == "beam":
                self._draw_beam(surf, sx, time)
                continue
            if kind == "mast":
                self._draw_mast(surf, sx, sy, cam_y, time)
                continue
            if kind == "rail":
                self._draw_rail(surf, cam_x, sy)
                continue
            if not (-80 < sx < W + 80 and -120 < sy < H + 80):
                continue
            if kind in ("crate", "barrel", "stack"):
                crate, barrel = _prop("crate"), _prop("barrel")
                if crate is None or barrel is None:
                    continue
                if kind == "crate":
                    surf.blit(crate, crate.get_rect(midbottom=(int(sx), int(sy))))
                elif kind == "barrel":
                    surf.blit(barrel, barrel.get_rect(midbottom=(int(sx - 10), int(sy))))
                    surf.blit(barrel, barrel.get_rect(midbottom=(int(sx + 14), int(sy))))
                else:
                    r = crate.get_rect(midbottom=(int(sx), int(sy)))
                    surf.blit(crate, r)
                    surf.blit(barrel, barrel.get_rect(midbottom=(r.centerx, r.top + 2)))
                continue
            if kind == "tuft":
                sway = math.sin(time * 2 + x * 0.05) * 1.5
                for i, (dx, hgt, col) in enumerate(((-3, 6, (60, 110, 60)), (0, 9, (80, 140, 70)),
                                                    (3, 7, (50, 96, 54)))):
                    pygame.draw.line(surf, col, (sx + dx, sy), (sx + dx + sway * (i + 1) / 2, sy - hgt), 2)
                continue
            if kind == "vine":
                ln = 26 + int(x) % 30
                sway = math.sin(time * 1.3 + x * 0.03) * 3
                pts = [(sx + math.sin(k * 0.5) * 2 + sway * k / ln * 4, sy + k) for k in range(0, ln, 4)]
                if len(pts) > 1:
                    pygame.draw.lines(surf, (40, 80, 50), False, pts, 2)
                    for px, py in pts[1::2]:
                        pygame.draw.circle(surf, (70, 130, 70), (round(px + 2), round(py)), 2)
                continue
            if kind == "flora":
                img = _flora(item[3], self.theme, item[4])
                if img is not None:
                    _blit_mid(surf, img, sx, sy + 2)
                continue
            if kind == "coil":
                _blit_mid(surf, _coil(), sx, sy)
                continue
            if kind == "bucket":
                _blit_mid(surf, _bucket(), sx, sy)
                continue
            if kind == "net":
                img = _net()
                surf.blit(img, (round(sx - img.get_width() / 2), round(sy)))
                continue
            if kind == "web":
                img = _web(item[3])
                surf.blit(img, (round(sx - (0 if item[3] < 0 else img.get_width())), round(sy)))
                continue
            if kind == "lantern":
                pygame.draw.line(surf, (40, 34, 30), (sx, sy), (sx, sy + 18), 2)
                body = pygame.Rect(0, 0, 14, 18)
                body.midtop = (sx, sy + 18)
                pygame.draw.rect(surf, (52, 44, 38), body, border_radius=3)
                pygame.draw.rect(surf, (246, 196, 96), body.inflate(-6, -6), border_radius=2)
                flick = 1 + 0.08 * math.sin(time * 9 + x)
                surf.blit(_glow(int(70 * flick), (255, 170, 80)), (sx - int(70 * flick), body.centery - int(70 * flick)),
                          special_flags=pygame.BLEND_RGB_ADD)
            elif kind == "porthole":
                pygame.draw.circle(surf, (60, 46, 34), (int(sx), int(sy)), 17)
                pygame.draw.circle(surf, (24, 44, 74), (int(sx), int(sy)), 12)
                wave = math.sin(time * 1.5 + x * 0.01) * 3
                pygame.draw.circle(surf, (40, 72, 110), (int(sx), int(sy + 4 + wave)), 9)
                pygame.draw.circle(surf, (210, 216, 230), (int(sx - 4), int(sy - 5)), 3)
                pygame.draw.circle(surf, (120, 100, 70), (int(sx), int(sy)), 17, 3)
            elif kind == "brazier":
                stand = sprites.crop(ISLAND, (512, 290, 32, 30))
                if stand is not None:
                    surf.blit(stand, (sx - 16, sy - 30))
                if fire:
                    fr = fire[int(time * 14 + x) % len(fire)]
                    surf.blit(fr, fr.get_rect(midbottom=(int(sx), int(sy - 24))))
                surf.blit(_glow(80, (255, 150, 60)), (sx - 80, sy - 110), special_flags=pygame.BLEND_RGB_ADD)

    def _draw_beam(self, surf, sx, time):
        """Viga de sustentação do casco, presa ao cenário."""
        if not -40 < sx < W + 40:
            return
        x = int(sx)
        pygame.draw.rect(surf, (34, 24, 20), (x - 12, 0, 24, H))
        pygame.draw.rect(surf, (52, 38, 30), (x - 9, 0, 18, H))
        pygame.draw.line(surf, (70, 52, 40), (x - 6, 0), (x - 6, H), 2)
        for y in range(40, H, 160):
            pygame.draw.rect(surf, (90, 90, 100), (x - 10, y, 20, 6))
            pygame.draw.circle(surf, (140, 140, 150), (x - 5, y + 3), 2)
            pygame.draw.circle(surf, (140, 140, 150), (x + 5, y + 3), 2)

    def _draw_mast(self, surf, sx, sy, cam_y, time):
        """Mastro principal com velas rasgadas e cordas, atrás do cordame."""
        top = -cam_y - 200
        x = int(sx)
        if not -400 < x < W + 400:
            return
        sway = math.sin(time * 0.8) * 6
        for yard_y, half in ((sy - 330, 150), (sy - 520, 110)):
            # verga
            pygame.draw.line(surf, (40, 30, 26), (x - half, yard_y), (x + half, yard_y), 7)
            # vela (pano escuro que balança)
            pts = [(x - half + 8, yard_y + 4), (x + half - 8, yard_y + 4),
                   (x + half - 20 + sway, yard_y + 120), (x + sway * 1.5, yard_y + 138),
                   (x - half + 20 + sway, yard_y + 120)]
            pygame.draw.polygon(surf, (70, 72, 86), pts)
            pygame.draw.polygon(surf, (52, 54, 66), pts, 3)
            pygame.draw.line(surf, (58, 60, 74), (x - 30 + sway, yard_y + 30), (x - 10 + sway, yard_y + 110), 2)
        pygame.draw.rect(surf, (36, 26, 22), (x - 9, top, 18, sy - top))
        pygame.draw.line(surf, (64, 48, 38), (x - 4, top), (x - 4, sy), 3)
        # cordas do mastro até a amurada
        for dx in (-520, -300, 300, 520):
            pygame.draw.line(surf, (30, 26, 28), (x, sy - 560), (x + dx, sy - 22), 2)

    def _draw_rail(self, surf, cam_x, sy):
        """Amurada do convés (fundo)."""
        y = int(sy)
        if not -40 < y < H + 60:
            return
        # névoa do mar subindo atrás da amurada (bem leve, não esconde nada do jogo)
        neblina = pz.mist((140, 160, 205), 62, height=70)
        nx = -((cam_x * 0.5 + self.time * 8) % neblina.get_width())
        for x0 in (nx, nx + neblina.get_width()):
            if x0 < W:
                surf.blit(neblina, (x0, y - 70))
        pygame.draw.rect(surf, (46, 32, 26), (0, y - 34, W, 7))
        pygame.draw.line(surf, (82, 60, 44), (0, y - 34), (W, y - 34), 2)
        off = int(-cam_x) % 24
        for x in range(off - 24, W + 24, 24):
            pygame.draw.rect(surf, (40, 28, 22), (x, y - 28, 6, 28))
        # lanternas presas na amurada a cada 12 blocos, com luz quente que treme
        passo = 12 * T
        primeira = int(cam_x // passo) * passo + passo // 2
        for wx in range(primeira - passo, int(cam_x) + W + passo, passo):
            lx = int(wx - cam_x)
            pygame.draw.line(surf, (34, 26, 22), (lx, y - 34), (lx, y - 52), 2)
            corpo = pygame.Rect(0, 0, 10, 13)
            corpo.midtop = (lx, y - 52)
            pygame.draw.rect(surf, (40, 32, 28), corpo, border_radius=2)
            pygame.draw.rect(surf, (250, 200, 104), corpo.inflate(-4, -5), border_radius=1)
            treme = 1 + 0.07 * math.sin(self.time * 8 + wx)
            r = int(68 * treme)
            surf.blit(_glow(r, (255, 160, 70)), (lx - r, corpo.centery - r), special_flags=pygame.BLEND_RGB_ADD)

    # --- partículas de ambiente ---
    MOTES = {"island": ("firefly", "leaf"), "ruins": ("firefly", "dust"), "temple": ("dust", "ember"),
             "hull": ("dust",), "bilge": ("drip", "dust", "bubble"), "deck": ("rainsplash",)}

    def _agua(self):
        """Blocos de água da sala (posições no mundo), para as bolhas."""
        if not hasattr(self, "_agua_cache"):
            r = self.room
            self._agua_cache = [(tx * T, ty * T) for ty in range(r.rows_count) for tx in range(r.cols)
                                if r.tile(tx, ty) == "~"]
        return self._agua_cache

    def _update_motes(self, dt, cam):
        kinds = self.MOTES.get(self.theme)
        if not kinds or cam is None:
            return
        cx, cy = cam
        quota = 46 // len(kinds)                 # cada tipo tem sua cota (gotas caem rápido e somem)
        count = {k: 0 for k in kinds}
        for m in self.motes:
            if m[0] in count:
                count[m[0]] += 1
        while True:
            missing = [k for k in kinds if count[k] < quota]
            if not missing:
                break
            kind = self.rng.choice(missing)
            count[kind] += 1
            if kind == "rainsplash":
                # gota que bate no chão do convés: procura o primeiro chão exposto na coluna
                x = cx + self.rng.uniform(0, W)
                tx = int(x // T)
                chao = None
                for ty in range(max(1, int(cy // T)), min(self.room.rows_count, int((cy + H) // T) + 1)):
                    if self.room.tile(tx, ty) == "#" and self.room.tile(tx, ty - 1) == ".":
                        chao = ty * T
                        break
                if chao is None:
                    self.motes.append(["rainsplash", x, cy - 999, 0.0, 0.05])
                else:
                    self.motes.append(["rainsplash", x, chao, self.rng.uniform(-0.6, 0.0), 0.4])
                continue
            if kind == "bubble":
                # bolha que sobe de um bloco de água visível até a superfície
                agua = [p for p in self._agua() if cx - 20 < p[0] < cx + W + 20 and cy - 20 < p[1] < cy + H + 20]
                if not agua:
                    self.motes.append(["bubble", cx, cy - 999, 0.0, 0.05])
                    continue
                bx, by = self.rng.choice(agua)
                self.motes.append(["bubble", bx + self.rng.uniform(2, T - 2), by + self.rng.uniform(8, T),
                                   self.rng.uniform(0, 6.28), self.rng.uniform(1.5, 3.5)])
                continue
            x = cx + self.rng.uniform(-40, W + 40)
            y = cy + (self.rng.uniform(-20, 0) if kind in ("leaf", "drip") else self.rng.uniform(0, H))
            if kind == "ember":
                y = cy + H + 10
            self.motes.append([kind, x, y, self.rng.uniform(0, 6.28), self.rng.uniform(4, 9)])
        alive = []
        for m in self.motes:
            kind = m[0]
            m[3] += dt
            m[4] -= dt
            if kind == "firefly":
                m[1] += math.cos(m[3] * 0.9) * 14 * dt
                m[2] += math.sin(m[3] * 1.3) * 10 * dt
            elif kind == "leaf":
                m[1] += (18 + math.sin(m[3] * 2) * 30) * dt
                m[2] += 34 * dt
            elif kind == "dust":
                m[1] += math.sin(m[3] * 0.7) * 6 * dt
                m[2] -= 4 * dt
            elif kind == "ember":
                m[1] += math.sin(m[3] * 3) * 12 * dt
                m[2] -= 40 * dt
            elif kind == "drip":
                m[2] += 260 * dt
                tile = self.room.tile(int(m[1] // T), int(m[2] // T))
                above = self.room.tile(int(m[1] // T), int((m[2] - 260 * dt) // T))
                if tile in ("#", "~", "X") and above == ".":   # caiu do ar na água ou no chão: respinga
                    m[0], m[2], m[3], m[4] = "splash", (int(m[2] // T)) * T + (6 if tile == "~" else 0), 0.0, 0.5
            elif kind == "bubble":
                m[1] += math.sin(m[3] * 5) * 8 * dt
                m[2] -= 26 * dt
                if self.room.tile(int(m[1] // T), int((m[2] - 2) // T)) != "~":
                    m[4] = 0                                   # chegou na superfície: estoura
            elif kind in ("splash", "rainsplash"):
                pass
            inside = cx - 80 < m[1] < cx + W + 80 and cy - 80 < m[2] < cy + H + 80
            if m[4] > 0 and inside:
                alive.append(m)
        self.motes = alive

    def _draw_motes(self, surf, cam_x, cam_y):
        for kind, x, y, t, life in self.motes:
            sx, sy = round(x - cam_x), round(y - cam_y)
            if not (0 <= sx < W and 0 <= sy < H):
                continue
            fade = min(1.0, life / 1.5)
            if kind == "firefly":
                k = (0.5 + 0.5 * math.sin(t * 4)) * fade
                surf.blit(_glow(10, (int(200 * k), int(255 * k), int(120 * k))), (sx - 10, sy - 10),
                          special_flags=pygame.BLEND_RGB_ADD)
                surf.set_at((sx, sy), (240, 255, 170))
            elif kind == "leaf":
                c = (110, 150, 70) if int(x) % 2 else (150, 110, 60)
                w = 3 if math.sin(t * 5) > 0 else 1
                pygame.draw.rect(surf, c, (sx, sy, w, 2))
            elif kind == "dust":
                v = int(140 * fade)
                surf.set_at((sx, sy), (v, v, min(255, v + 20)))
            elif kind == "ember":
                surf.blit(_glow(6, (int(255 * fade), int(130 * fade), int(40 * fade))), (sx - 6, sy - 6),
                          special_flags=pygame.BLEND_RGB_ADD)
                surf.set_at((sx, sy), (255, 200, 120))
            elif kind == "drip":
                pygame.draw.line(surf, (110, 150, 200), (sx, sy), (sx, sy + 4), 1)
            elif kind == "bubble":
                r = 2 if int(x) % 3 else 1
                pygame.draw.circle(surf, (150, 190, 220), (sx, sy), r, 1)
            elif kind == "rainsplash":
                if t >= 0:                                    # coroa de 2 gotinhas que sobem e caem
                    h = int(6 * math.sin(min(1.0, t / 0.35) * math.pi))
                    cor = (150, 170, 215)
                    surf.set_at((sx - 2, sy - h), cor)
                    surf.set_at((sx + 2, sy - h), cor)
                    if t < 0.12:
                        pygame.draw.line(surf, cor, (sx - 3, sy - 1), (sx + 3, sy - 1))
            elif kind == "splash":
                frames = _splash_frames()
                if frames:
                    fr = frames[min(len(frames) - 1, int(t * 16))]
                    surf.blit(fr, fr.get_rect(midbottom=(sx, sy + 2)))

    def _draw_walker(self, surf, x, y, item, cam_x, cam_y, time):
        """Figurante de cenário: parado, pescando ou andando devagar (com pausas) de um lado para o outro."""
        from .creatures import draw_model
        name, span = item[3], item[4]
        atividade = item[5] if len(item) > 5 else "anda"
        wx, facing, moving = x, (-1 if (x // 7) % 2 else 1), False
        if span > 0 and atividade in ("anda", "caixa"):
            # ida (span/12 s), pausa de 3 s, volta, pausa: ~12 px/s, bem abaixo da protagonista
            ida = span / 12.0
            ciclo = 2 * (ida + 3.0)
            k = (time + x * 0.37) % ciclo
            if k < ida:
                pos, facing, moving = k / ida, 1, True
            elif k < ida + 3.0:
                pos, facing = 1.0, 1
            elif k < 2 * ida + 3.0:
                pos, facing, moving = 1 - (k - ida - 3.0) / ida, -1, True
            else:
                pos, facing = 0.0, -1
            wx = x - span / 2 + span * pos
        elif atividade == "pesca":
            facing = -1
        sx, sy = wx - cam_x, y - cam_y
        if not (-100 < sx < W + 100 and -100 < sy < H + 100):
            return
        # tempo do desenho mais lento: a passada acompanha a velocidade baixa
        draw_model(surf, name, sx, sy, time * (0.45 if moving else 1.0) + x * 0.01, facing, moving)
        if atividade == "pesca":
            mao = (round(sx + facing * 7), round(sy - 30))
            ponta = (round(sx + facing * 30), round(sy - 60))
            pygame.draw.line(surf, (96, 64, 40), mao, ponta, 2)                  # vara
            # a linha some atrás da amurada, como se caísse no mar
            boia_y = round(sy - 26 + math.sin(time * 2.2 + x) * 1.5)
            pygame.draw.line(surf, (200, 200, 210), ponta, (ponta[0], boia_y), 1)  # linha
        elif atividade == "caixa":
            caixa = pygame.Rect(0, 0, 12, 10)
            caixa.midbottom = (round(sx + facing * 7), round(sy - 22))
            pygame.draw.rect(surf, (20, 14, 22), caixa.inflate(2, 2))
            pygame.draw.rect(surf, (150, 104, 60), caixa)
            pygame.draw.line(surf, (104, 70, 40), caixa.topleft, (caixa.right - 1, caixa.bottom - 1))
            pygame.draw.line(surf, (190, 140, 84), (caixa.x, caixa.y), (caixa.right - 1, caixa.y))

    def _draw_foreground(self, surf, cam_x, cam_y, time):
        """Silhuetas na frente da jogadora, só nas bordas de cima da tela (não cobrem o jogo)."""
        if self.theme == "deck":
            # cordas do cordame penduradas, passando um pouco mais rápido que a câmera
            par = 1.25
            periodo = 700
            x0 = -((cam_x * par) % periodo)
            for base in (x0 - periodo, x0, x0 + periodo):
                for dx, comp, flecha in ((60, 260, 46), (390, 180, 30)):
                    a = base + dx
                    if a > W or a + comp < 0:
                        continue
                    balanco = math.sin(time * 0.9 + dx) * 3
                    pts = [(a + comp * k / 12, -6 + flecha * math.sin(math.pi * k / 12) + balanco * math.sin(math.pi * k / 12))
                           for k in range(13)]
                    pygame.draw.lines(surf, (12, 10, 16), False, pts, 3)
                    # ponta solta pendurada
                    px, py = pts[9]
                    pygame.draw.line(surf, (12, 10, 16), (px, py), (px + balanco, py + 34), 2)
        elif self.theme == "island":
            # copa de folhas pendendo no alto e névoa rasteira bem leve
            copa = pz.canopy(17, (16, 34, 28, 255))
            x0 = -((cam_x * 1.2) % copa.get_width())
            balanco = round(math.sin(time * 0.6) * 2)
            for x in (x0, x0 + copa.get_width()):
                if x < W:
                    surf.blit(copa, (x + balanco, -4))
            self._nevoa(surf, cam_x, (190, 220, 210), 26, H - 150)
        if self.theme == "ruins":
            # hera pendurada das bordas de cima, como na floresta, um pouco mais escura
            hera = pz.canopy(29, (10, 18, 20, 255))
            x0 = -((cam_x * 1.2) % hera.get_width())
            for x in (x0, x0 + hera.get_width()):
                if x < W:
                    surf.blit(hera, (x, -6))
        if self.theme == "temple":
            self._nevoa(surf, cam_x, (150, 120, 200), 30, H - 130)
        if self.theme in ("hull", "bilge", "temple"):
            # corda e corrente penduradas perto da câmera, só no alto da tela
            par = 1.3
            periodo = 610
            x0 = -((cam_x * par) % periodo)
            for a in (x0 - periodo, x0, x0 + periodo):
                if not -300 < a < W + 60:
                    continue
                balanco = math.sin(time * 0.7 + a * 0.01) * 2
                pts = [(a + 220 * k / 10, -4 + 26 * math.sin(math.pi * k / 10) + balanco * math.sin(math.pi * k / 10))
                       for k in range(11)]
                pygame.draw.lines(surf, (16, 11, 12), False, pts, 3)
                cx0 = a + 300                               # corrente: elos alternados
                for i in range(7):
                    y0 = i * 7
                    if i % 2:
                        pygame.draw.line(surf, (24, 22, 28), (cx0, y0), (cx0, y0 + 6), 2)
                    else:
                        pygame.draw.ellipse(surf, (24, 22, 28), (cx0 - 3, y0, 7, 8), 2)
                pygame.draw.circle(surf, (24, 22, 28), (int(cx0), 54), 5, 2)   # gancho

    def _draw_lights(self, surf, cam_x, cam_y, time):
        """Luz quente somada por cima da cena: cone e poça no chão embaixo das lanternas, feixe de
        luar das escotilhas e clarão dos braseiros. Fraca de propósito: não esconde nada do jogo."""
        add = pygame.BLEND_RGB_ADD
        for item in self.decor:
            kind, x, y = item[0], item[1], item[2]
            sx, sy = round(x - cam_x), round(y - cam_y)
            if not -200 < sx < W + 200:
                continue
            if kind == "lantern" and item[3] is not None:
                alt = min(150, item[3] - y - 30)
                fy = round(item[3] - cam_y)
                if alt > 20 and fy > -60 and sy < H + 40:
                    treme = int(time * 9 + x) % 3
                    cone = _cone(alt, (90, 60, 26))
                    surf.blit(cone, (sx - cone.get_width() // 2, sy + 30), special_flags=add)
                    poca = _pool(70 + treme * 2, 14, (150, 96, 40))
                    surf.blit(poca, poca.get_rect(center=(sx, fy)), special_flags=add)
            elif kind == "porthole" and -40 < sy < H + 200:
                surf.blit(_shaft(), (sx - 10, sy - 6), special_flags=add)
            elif kind == "brazier" and -60 < sy < H + 60:
                treme = int(time * 7 + x) % 3
                poca = _pool(84 + treme * 3, 16, (150, 80, 30))
                surf.blit(poca, poca.get_rect(center=(sx, sy)), special_flags=add)
        if self.theme == "deck":
            # poças das lanternas da amurada sobre o piso do convés
            rail = next((it for it in self.decor if it[0] == "rail"), None)
            if rail is not None:
                fy = round(rail[2] - cam_y)
                if -40 < fy < H + 40:
                    passo = 12 * T
                    primeira = int(cam_x // passo) * passo + passo // 2
                    for wx in range(primeira - passo, int(cam_x) + W + passo, passo):
                        treme = int(time * 8 + wx) % 3
                        poca = _pool(76 + treme * 2, 12, (130, 84, 36))
                        surf.blit(poca, poca.get_rect(center=(round(wx - cam_x), fy + 2)), special_flags=add)

    def _nevoa(self, surf, cam_x, cor, alpha, y):
        """Faixa de névoa que passa devagar, desenhada sobre a cena (bem transparente)."""
        faixa = pz.mist(cor, alpha, height=110)
        x0 = -((cam_x * 1.1 + self.time * 10) % faixa.get_width())
        for x in (x0, x0 + faixa.get_width()):
            if x < W:
                surf.blit(faixa, (x, y))

    def draw_front(self, surf, cam_x, cam_y, time):
        """Partículas, chuva no convés, clarão de relâmpago e vinheta em todas as salas."""
        self._draw_motes(surf, cam_x, cam_y)
        if self.theme in ("island", "ruins"):
            leaf = pz.foliage(31, (10, 16, 22, 255))
            x0 = -((cam_x * 1.25) % leaf.get_width())
            y = H - 46 + max(0, (self.room.height - cam_y - H) * 0.3)
            for x in (x0, x0 + leaf.get_width()):
                if x < W and y < H:
                    surf.blit(leaf, (x, y))
        self._draw_lights(surf, cam_x, cam_y, time)
        self._draw_foreground(surf, cam_x, cam_y, time)
        surf.blit(_vignette(), (0, 0))
        if self.theme != "deck":
            return
        for x, y, s in self.rain:
            rx = (x - cam_x * 0.6 + time * 120 * s) % W
            ry = (y + time * 620 * s) % H
            pygame.draw.line(surf, (120, 140, 180), (rx, ry), (rx - 4, ry + 12), 1)
        if self.flash > 0:
            veil = pygame.Surface((W, H), pygame.SRCALPHA)
            veil.fill((200, 210, 255, int(90 * self.flash / 0.25)))
            surf.blit(veil, (0, 0))
