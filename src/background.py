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

# figurantes (sala -> [(modelo, coluna, linha do chão, alcance em px)])
WALKERS = {
    "conves": [("gato", 52, 18, 140), ("bardo", 40, 18, 40), ("aldea", 60, 18, 90)],
    "cabine": [("estudioso", 22, 14, 50)],
    "praia": [("fazendeiro", 8, 18, 120), ("menino", 28, 18, 90), ("aldea", 50, 12, 70)],
    "floresta": [("anciã", 14, 37, 60), ("curandeira", 6, 37, 40)],
    "ruinas": [("velho", 4, 17, 0)],
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
                        out.append(("lantern", tx * T + 16, (ty + 1) * T))
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
        for name, tx, ty, span in WALKERS.get(room.id, ()):
            out.append(("walker", tx * T + 16, ty * T, name, span))
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
        if self.theme == "deck":
            self.next_flash -= dt
            self.flash = max(0.0, self.flash - dt)
            if self.next_flash <= 0:
                self.flash = 0.25
                self.next_flash = self.rng.uniform(6, 12)

    # --- desenho ---
    def draw(self, surf, cam_x, cam_y, time):
        th = self.theme
        if th in SKY:
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

    def _layers(self, surf, cam_x, cam_y, time):
        """Paisagem em camadas (parallax) para o convés, a ilha e as ruínas."""
        th = self.theme
        drift = time * 6

        def band(img, par, y, speed=0.0):
            x0 = -((cam_x * par + time * speed) % img.get_width())
            for x in (x0, x0 + img.get_width()):
                if x < W:
                    surf.blit(img, (x, y))

        band(pz.clouds(5, (44, 52, 86, 140)), 0.04, 30 - cam_y * 0.02, 4)
        band(pz.mountains(11, (36, 44, 74), 260, 1.1, snow=(150, 160, 200)), 0.08, H - 330 - cam_y * 0.04)
        if th != "deck":
            c = pz.castle(4, (30, 34, 60), (250, 200, 110))
            cx = W * 0.62 - (cam_x * 0.1) % (W * 1.6)
            surf.blit(c, (cx, H - 380 - cam_y * 0.05))
        band(pz.mist((70, 80, 120), 60), 0.12, H - 260 - cam_y * 0.06, 10)
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
        pygame.draw.rect(surf, (46, 32, 26), (0, y - 34, W, 7))
        pygame.draw.line(surf, (82, 60, 44), (0, y - 34), (W, y - 34), 2)
        off = int(-cam_x) % 24
        for x in range(off - 24, W + 24, 24):
            pygame.draw.rect(surf, (40, 28, 22), (x, y - 28, 6, 28))

    # --- partículas de ambiente ---
    MOTES = {"island": ("firefly", "leaf"), "ruins": ("firefly", "dust"), "temple": ("dust", "ember"),
             "hull": ("dust",), "bilge": ("drip", "dust")}

    def _update_motes(self, dt, cam):
        kinds = self.MOTES.get(self.theme)
        if not kinds or cam is None:
            return
        cx, cy = cam
        while len(self.motes) < 46:
            kind = self.rng.choice(kinds)
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

    def _draw_walker(self, surf, x, y, item, cam_x, cam_y, time):
        """Figurante que anda devagar de um lado para o outro (só cenário)."""
        from .creatures import draw_model
        name, span = item[3], item[4]
        period = max(4.0, span / 18)
        k = (time / period) % 2.0
        pos = k if k < 1 else 2 - k
        ease = 0.5 - 0.5 * math.cos(pos * math.pi)
        wx = x - span / 2 + span * ease
        facing = 1 if k < 1 else -1
        moving = span > 0 and 0.06 < pos < 0.94
        sx, sy = wx - cam_x, y - cam_y
        if -100 < sx < W + 100 and -100 < sy < H + 100:
            draw_model(surf, name, sx, sy, time + x * 0.01, facing, moving)

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
