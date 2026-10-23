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

# NPCs e criaturas que não ficaram iguais à protagonista (os outros saíram com os chifres e o
# cabelo dela e foram descartados)
NPCS = {
    "fazendeiro": (130, 135, 92, 142),
    "anciã": (250, 145, 80, 132),
    "menino": (360, 168, 66, 108),
    "ladino": (1194, 362, 86, 146),
    "cavaleiro_negro": (1325, 333, 158, 180),
    "diabrete": (48, 618, 108, 108),
    "espirito": (205, 580, 90, 148),
    "goblin": (385, 588, 110, 138),
    "ogro": (528, 555, 186, 172),
    "lobo": (760, 610, 190, 110),
    "lich": (962, 538, 152, 190),
    "mumia": (1185, 583, 90, 140),
    "minotauro": (1334, 568, 182, 158),
    "alquimista": (612, 810, 170, 158),
    "vidente": (834, 830, 200, 140),
    "funileiro": (1060, 808, 110, 160),
    "gato": (1360, 905, 70, 60),
}


def is_bg(c):
    r, g, b = c[0], c[1], c[2]
    mx, mn = max(r, g, b), min(r, g, b)
    if mn > 222:
        return True                               # fundo branco
    if mx - mn < 20 and mn > 60:
        return True                               # sombra e poeira cinzentas
    return False


def cut(sheet, rect):
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
            imgs.append(pygame.transform.flip(img, True, False))     # olha para a esquerda
        hero[name] = imgs
    wave = hero.pop("wave")[0]
    pygame.image.save(wave, os.path.join(EFE, "onda_roxa.png"))
    pack(hero, os.path.join(PERS, "feiticeira_modelos.png"), 112, 72)

    npc_src = pygame.image.load(os.path.join(FONTES, "npcs_modelos.webp")).convert()
    npcs = {}
    for name, rect in NPCS.items():
        img = shrink(cut(npc_src, rect), SCALE)
        # cada NPC mantém as próprias cores; só tira meio-tons de borda
        img = snap(img, palette_quant(img))
        npcs[name] = [pygame.transform.flip(img, True, False)]
    pack(npcs, os.path.join(PERS, "npcs.png"), 96, 96)
    print("ok:", {k: len(v) for k, v in hero.items()}, len(npcs), "NPCs")


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
