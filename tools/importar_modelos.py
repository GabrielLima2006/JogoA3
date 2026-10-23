"""Importa os modelos desenhados pela equipe (folhas com fundo branco) para sprites do jogo.

Para cada quadro: recorta, tira o fundo branco e as sombras cinzentas, reduz para a escala do
sprite da feiticeira, encaixa as cores na paleta dela (para tudo ficar no mesmo estilo) e vira
para a esquerda (o sprite original da protagonista olha para a esquerda).

Uso:  python tools/importar_modelos.py
Entrada: assets/fontes/feiticeira_modelos.webp, assets/fontes/npcs_modelos.webp
Saída:   assets/img/personagens/feiticeira_modelos.png (+ .json com âncoras)
         assets/img/personagens/npcs.png (+ .json)
         assets/img/efeitos/onda_roxa.png
"""

import json
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTES = os.path.join(ROOT, "assets", "fontes")
PERS = os.path.join(ROOT, "assets", "img", "personagens")
EFE = os.path.join(ROOT, "assets", "img", "efeitos")

SCALE = 0.47            # 117 px de altura na folha -> ~55 px no jogo (altura da feiticeira parada)

# quadros da protagonista na folha (x, y, w, h), já separados à mão onde os efeitos encostam
HERO = {
    "combo": [(20, 118, 88, 121), (125, 118, 92, 121), (222, 118, 146, 121), (393, 118, 84, 121),
              (520, 118, 94, 121)],
    "heavy": [(658, 130, 140, 115), (828, 126, 134, 118), (968, 126, 150, 118), (1434, 126, 86, 120)],
    "wave": [(1125, 150, 270, 70)],
    "dash": [(19, 360, 124, 94), (206, 364, 139, 90), (403, 364, 110, 90), (556, 357, 133, 97),
             (735, 357, 117, 93), (921, 356, 113, 99)],
    "jump": [(28, 592, 88, 108), (166, 565, 92, 128), (313, 556, 95, 136), (465, 556, 101, 136),
             (610, 598, 94, 104), (740, 600, 88, 102)],
    "roll": [(36, 834, 96, 106), (194, 849, 92, 90), (330, 845, 115, 96), (478, 862, 150, 79),
             (656, 836, 90, 105), (814, 819, 82, 121), (945, 818, 87, 123)],
}

# grupos em que o desenho do rosto não bate com a direção do golpe: usa a direção do golpe
ATTACK_FACES_RIGHT = {"heavy": True, "wave": True, "roll": True}

# NPCs e criaturas que não ficaram iguais à protagonista (os outros saíram com os chifres e o
# cabelo dela e foram descartados)
NPCS = {
    # nome: (recorte, cor nova do cabelo ou None). Quem tem cor nova saiu na folha com o cabelo
    # lavanda e os chifres da protagonista: o importador troca o cabelo e apaga os chifres.
    "aldea": ((35, 135, 69, 139), (150, 80, 50)),
    "fazendeiro": ((135, 137, 81, 137), None),
    "anciã": ((253, 151, 73, 123), None),
    "menino": ((364, 167, 57, 107), None),
    "comerciante": ((493, 122, 130, 152), (120, 80, 50)),
    "ferreiro": ((683, 122, 135, 152), (60, 50, 50)),
    "curandeira": ((920, 123, 120, 151), (90, 150, 80)),
    "guarda": ((1158, 122, 112, 152), (200, 150, 70)),
    "anciao": ((1375, 130, 89, 143), (220, 220, 220)),
    "cavaleiro_escudo": ((33, 330, 170, 175), (190, 120, 60)),
    "lanceiro": ((250, 330, 117, 175), (60, 42, 34)),
    "guerreiro": ((419, 339, 174, 166), (110, 110, 120)),
    "arqueira": ((638, 364, 114, 141), (40, 34, 48)),
    "espadachim": ((790, 359, 134, 146), (40, 40, 60)),
    "porta_estandarte": ((979, 330, 171, 175), (230, 200, 120)),
    "ladino": ((1197, 369, 81, 136), None),
    "cavaleiro_negro": ((1326, 335, 162, 174), None),
    "diabrete": ((43, 600, 115, 123), None),
    "espirito": ((200, 551, 98, 172), None),
    "goblin": ((387, 593, 103, 130), None),
    "ogro": ((532, 557, 180, 166), None),
    "lobo": ((764, 613, 185, 110), None),
    "lich": ((968, 540, 144, 183), None),
    "mumia": ((1188, 585, 81, 135), None),
    "minotauro": ((1337, 569, 174, 154), None),
    "bardo": ((41, 790, 150, 176), (70, 50, 90)),
    "mago_azul": ((235, 790, 143, 176), None),
    "estudioso": ((440, 811, 122, 152), (70, 50, 40)),
    "alquimista": ((613, 814, 168, 152), None),
    "vidente": ((834, 838, 193, 128), None),
    "funileiro": ((1068, 812, 97, 152), None),
    "velho": ((1238, 826, 118, 138), (180, 180, 180)),
    "gato": ((1360, 900, 70, 64), None),
}


def is_bg(c):
    r, g, b = c[0], c[1], c[2]
    mx, mn = max(r, g, b), min(r, g, b)
    if mn > 222:
        return True                               # fundo branco
    if mx - mn < 20 and mn > 60:
        return True                               # sombra e poeira cinzentas
    return False


def grow(sheet, rect, limit=60):
    """Aumenta o recorte enquanto a borda ainda encosta no desenho (evita modelo cortado)."""
    x, y, w, h = rect
    W, H = sheet.get_size()

    def busy(pts):
        return any(not is_bg(sheet.get_at(p)) for p in pts)
    for _ in range(limit):
        changed = False
        if x > 0 and busy([(x, yy) for yy in range(y, y + h)]):
            x, w, changed = x - 1, w + 1, True
        if x + w < W and busy([(x + w - 1, yy) for yy in range(y, y + h)]):
            w, changed = w + 1, True
        if y > 0 and busy([(xx, y) for xx in range(x, x + w)]):
            y, h, changed = y - 1, h + 1, True
        if y + h < H and busy([(xx, y + h - 1) for xx in range(x, x + w)]):
            h, changed = h + 1, True
        if not changed:
            break
    return (x, y, w, h)


def _is_shadow(sub, comp):
    """Mancha de sombra: quase sem cor (cinza)."""
    pts = comp.outline(every=2) or [(0, 0)]
    sat = bright = 0
    for p in pts:
        c = sub.get_at(p)
        sat += max(c.r, c.g, c.b) - min(c.r, c.g, c.b)
        bright += (c.r + c.g + c.b) / 3
    n = len(pts)
    r = comp.get_bounding_rects()[0]
    flat = r.h < 30 and r.h < r.w * 0.4                 # sombra é uma elipse achatada no chão
    return flat and sat / n < 22 and bright / n > 35


def cut(sheet, rect):
    rect = grow(sheet, rect)
    sub = sheet.subsurface(pygame.Rect(rect).clip(sheet.get_rect())).copy().convert_alpha()
    w, h = sub.get_size()
    for y in range(h):
        for x in range(w):
            if is_bg(sub.get_at((x, y))):
                sub.set_at((x, y), (0, 0, 0, 0))
    # some com pontinhos soltos (resto de outros quadros, letras)
    mask = pygame.mask.from_surface(sub)
    comps = mask.connected_components(minimum=40)
    keep = pygame.mask.Mask((w, h))
    for c in comps:
        r = c.get_bounding_rects()[0]
        text = r.h < 24 and r.w < 30 and c.count() < 220      # letras da folha
        if not _is_shadow(sub, c) and not text:
            keep.draw(c, (0, 0))
    clean = keep.to_surface(setsurface=sub, unsetcolor=(0, 0, 0, 0))
    r = keep.get_bounding_rects()
    if r:
        box = r[0].unionall(r[1:])
        clean = clean.subsurface(box).copy()
    return clean


def palette_of(paths):
    cols = set()
    for p in paths:
        s = pygame.image.load(p)
        for y in range(s.get_height()):
            for x in range(s.get_width()):
                c = s.get_at((x, y))
                if c.a:
                    cols.add((c.r, c.g, c.b))
    return sorted(cols)


def snap(surf, pal):
    out = surf.copy()
    cache = {}
    for y in range(out.get_height()):
        for x in range(out.get_width()):
            c = out.get_at((x, y))
            if c.a < 110:
                out.set_at((x, y), (0, 0, 0, 0))
                continue
            k = (c.r >> 2, c.g >> 2, c.b >> 2)
            if k not in cache:
                cache[k] = min(pal, key=lambda p: (p[0] - c.r) ** 2 * 3 + (p[1] - c.g) ** 2 * 4 + (p[2] - c.b) ** 2 * 2)
            out.set_at((x, y), cache[k] + (255,))
    return out


def shrink(surf, scale):
    w, h = surf.get_size()
    return pygame.transform.smoothscale(surf, (max(1, round(w * scale)), max(1, round(h * scale))))


def looks_right(img):
    """O rosto (pele) fica do lado para onde a personagem olha; o cabelo fica atrás."""
    w, h = img.get_size()
    skin, hair = [], []
    for y in range(int(h * 0.45)):
        for x in range(w):
            c = img.get_at((x, y))
            if not c.a:
                continue
            if c.r > 200 and 90 < c.g < 175 and c.b < 130:
                skin.append(x)
            elif c.b > 200 and c.r > 140:
                hair.append(x)
    if not skin or not hair:
        return False
    return sum(skin) / len(skin) > sum(hair) / len(hair)


def body_center(surf):
    """x do centro do corpo: média das colunas com pixels nas linhas de baixo (pés e pernas)."""
    w, h = surf.get_size()
    xs = [x for y in range(int(h * 0.55), h) for x in range(w) if surf.get_at((x, y)).a]
    return sum(xs) / len(xs) if xs else w / 2


def pack(frames, path, fw, fh, anchor_y_bottom=True):
    """Coloca os quadros numa folha (uma linha por grupo) com o pé em (fw/2, fh-1)."""
    meta = {"frame": [fw, fh], "anchor": [fw // 2, fh - 1], "rows": {}}
    rows = list(frames.items())
    cols = max(len(v) for _, v in rows)
    sheet = pygame.Surface((fw * cols, fh * len(rows)), pygame.SRCALPHA)
    for r, (name, items) in enumerate(rows):
        meta["rows"][name] = [r, len(items)]
        for c, img in enumerate(items):
            cx = body_center(img)
            x = c * fw + round(fw / 2 - cx)
            y = r * fh + (fh - img.get_height())
            sheet.blit(img, (x, y), None)
    pygame.image.save(sheet, path)
    with open(os.path.splitext(path)[0] + ".json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    return sheet


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    pal = palette_of([os.path.join(PERS, "feiticeira_parada.png"), os.path.join(PERS, "feiticeira_andando.png")])
    # brilhos dos golpes: lilás e branco extras
    pal += [(120, 60, 200), (90, 40, 160), (200, 170, 255), (60, 20, 110)]
    hero_src = pygame.image.load(os.path.join(FONTES, "feiticeira_modelos.webp")).convert()
    hero = {}
    for name, rects in HERO.items():
        imgs = []
        for rect in rects:
            img = snap(shrink(cut(hero_src, rect), SCALE), pal)
            # no golpe forte e na rolagem quem manda é a direção do movimento/corte, não o rosto
            right = ATTACK_FACES_RIGHT[name] if name in ATTACK_FACES_RIGHT else looks_right(img)
            if right:
                img = pygame.transform.flip(img, True, False)          # todos olham para a esquerda
            imgs.append(img)
        hero[name] = imgs
    wave = hero.pop("wave")[0]
    pygame.image.save(wave, os.path.join(EFE, "onda_roxa.png"))
    pack(hero, os.path.join(PERS, "feiticeira_modelos.png"), 112, 72)

    npc_src = pygame.image.load(os.path.join(FONTES, "npcs_modelos.webp")).convert()
    npcs = {}
    for name, (rect, hair) in NPCS.items():
        img = cut(npc_src, rect)
        if hair:
            img = fix_borrowed_look(img, hair)
        img = shrink(img, SCALE)
        # cada NPC mantém as próprias cores; só tira meio-tons de borda
        img = snap(img, palette_quant(img))
        npcs[name] = [pygame.transform.flip(img, True, False)]
    pack(npcs, os.path.join(PERS, "npcs.png"), 128, 96)
    print("ok:", {k: len(v) for k, v in hero.items()}, len(npcs), "NPCs")


def _is_lavender(c):
    return c.b > 150 and c.r > 110 and c.b > c.r + 25 and c.b > c.g + 20


def _is_horn(c):
    return c.r > c.b + 35 and c.r >= c.g and c.r > 70


def fix_borrowed_look(img, hair):
    """Tira o cabelo lavanda e os chifres copiados da protagonista (cor nova, chifres apagados)."""
    out = img.copy()
    w, h = out.get_size()
    is_hair = [[False] * w for _ in range(h)]
    hair_rows = []
    for y in range(h):
        for x in range(w):
            c = out.get_at((x, y))
            if c.a and _is_lavender(c):
                is_hair[y][x] = True
                hair_rows.append(y)
                k = (0.3 * c.r + 0.59 * c.g + 0.11 * c.b) / 200.0
                out.set_at((x, y), tuple(max(0, min(255, int(v * k * 1.05))) for v in hair) + (255,))
    if not hair_rows:
        return out
    top = min(hair_rows)
    zone = top + max(8, int((max(hair_rows) - top) * 0.3))
    outline = tuple(max(0, v // 4) for v in hair) + (255,)
    for x in range(w):
        first = next((y for y in range(top, zone) if is_hair[y][x]), None)
        limit = first if first is not None else zone
        for y in range(0, limit):
            c = out.get_at((x, y))
            if c.a and (first is not None or _is_horn(c) or max(c.r, c.g, c.b) < 90):
                out.set_at((x, y), (0, 0, 0, 0))
        if first is not None and first > 0:
            out.set_at((x, first - 1), outline)
    # chifres que passavam por dentro do cabelo: troca pelo cabelo vizinho
    for y in range(top, zone):
        for x in range(1, w - 1):
            c = out.get_at((x, y))
            if c.a and _is_horn(c) and not is_hair[y][x]:
                left = out.get_at((x - 1, y))
                out.set_at((x, y), left if left.a else (0, 0, 0, 0))
    return out


def palette_quant(img, levels=24):
    """Paleta reduzida do próprio NPC (cores mais frequentes)."""
    from collections import Counter
    cnt = Counter()
    for y in range(img.get_height()):
        for x in range(img.get_width()):
            c = img.get_at((x, y))
            if c.a > 110:
                cnt[(c.r // 16 * 16 + 8, c.g // 16 * 16 + 8, c.b // 16 * 16 + 8)] += 1
    return [c for c, _ in cnt.most_common(levels)] or [(0, 0, 0)]


if __name__ == "__main__":
    main()
