"""Gera as animações novas da feiticeira (golpes, pulo, queda, dash, dano, morte).

O pacote gratuito da personagem só traz "parada" e "andando". Este script cria os outros
quadros a partir das partes do sprite original (cabeça, cabelo, tronco e pernas):
tira a espada escura original, gira o tronco na cintura, faz o cabelo arrastar atrás
e desenha braço e lâmina pixel a pixel em cada pose.

Uso:  python tools/gerar_feiticeira.py
Saída: assets/img/personagens/feiticeira_acoes.png (quadros de 80x64, pé em (40, 63))
"""

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "img", "personagens", "feiticeira_andando.png")
OUT = os.path.join(ROOT, "assets", "img", "personagens", "feiticeira_acoes.png")

FW, FH = 80, 64           # quadro de saída
FOOT = (40, 63)           # onde fica o pé (âncora: última linha do quadro)
SRC_W, SRC_H = 45, 58     # quadro do sprite original
SRC_FOOT = (21, 57)
WAIST_Y = 40              # linha da cintura no quadro original

# paleta da personagem
SLEEVE = (28, 21, 77)
SLEEVE_HI = (3, 33, 188)
SLEEVE_DK = (21, 16, 55)
SKIN = (255, 140, 94)
SKIN_DK = (224, 94, 43)
HILT = (77, 47, 30)
GUARD = (255, 163, 3)
BLADE = (178, 178, 255)
BLADE_DK = (158, 160, 250)
BLADE_HI = (255, 255, 255)
HAIR = {(178, 178, 255), (158, 160, 250), (255, 255, 255), (255, 255, 204)}
WEAPON = {(47, 24, 80), (81, 55, 63)}
WEAPON_EDGE = {(166, 75, 10), (67, 21, 0)}

# linhas da folha: nome -> lista de poses
ANIMS = ["quick", "heavy", "up", "down", "jump", "fall", "dash", "hurt", "death", "land", "diag"]


def load_walk():
    sheet = pygame.image.load(SRC)
    cols = sheet.get_width() // SRC_W
    frames = []
    for i in range(cols * (sheet.get_height() // SRC_H)):
        x, y = (i % cols) * SRC_W, (i // cols) * SRC_H
        frames.append(sheet.subsurface((x, y, SRC_W, SRC_H)).copy())
    return frames


def strip_weapon(src):
    """Apaga a espada original (cores próprias) e o que encosta nela."""
    s = src.copy()
    w, h = s.get_size()
    weapon = set()
    for y in range(h):
        for x in range(w):
            c = s.get_at((x, y))
            if c.a and tuple(c)[:3] in WEAPON:
                weapon.add((x, y))
    edge = set()
    for x, y in weapon:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                p = (x + dx, y + dy)
                if 0 <= p[0] < w and 0 <= p[1] < h and p not in weapon:
                    c = s.get_at(p)
                    if c.a and tuple(c)[:3] in WEAPON_EDGE:
                        edge.add(p)
    for p in weapon | edge:
        s.set_at(p, (0, 0, 0, 0))
    return s


def trail_hair(src, dx, dy=0, top=36):
    """Cabelo arrasta para trás (dx > 0 = para a direita, que é atrás quando ela olha à esquerda)."""
    s = src.copy()
    w, h = s.get_size()
    out = pygame.Surface((w + abs(dx) + 2, h + abs(dy) + 2), pygame.SRCALPHA)
    out.blit(s, (0, 0))
    for y in range(min(top, h)):
        hair = [x for x in range(w) if s.get_at((x, y)).a and tuple(s.get_at((x, y)))[:3] in HAIR]
        if not hair:
            continue
        end = max(hair)
        if end < w // 2 - 2:
            continue
        edge = s.get_at((end, y))
        k = (y / top)                       # pontas de baixo arrastam mais
        n = round(dx * (0.4 + 0.6 * k))
        for i in range(1, n + 1):
            out.set_at((end + i, y), BLADE_DK if i == n else BLADE)
        if n:
            out.set_at((end + n + 1, y), (120, 110, 200))
        _ = edge
    if dy:
        moved = pygame.Surface(out.get_size(), pygame.SRCALPHA)
        moved.blit(out, (0, 0))
        out = moved
    return out


def split(src):
    upper = pygame.Surface(src.get_size(), pygame.SRCALPHA)
    lower = pygame.Surface(src.get_size(), pygame.SRCALPHA)
    upper.blit(src, (0, 0), (0, 0, src.get_width(), WAIST_Y))
    lower.blit(src, (0, WAIST_Y), (0, WAIST_Y, src.get_width(), src.get_height() - WAIST_Y))
    return upper, lower


def rotate_about(img, pivot, angle):
    """Gira em volta de `pivot` (ponto da imagem). Retorna (imagem, novo canto superior esquerdo)."""
    w, h = img.get_size()
    off = pygame.math.Vector2(w / 2 - pivot[0], h / 2 - pivot[1]).rotate(-angle)
    rot = pygame.transform.rotate(img, angle)
    r = rot.get_rect(center=(pivot[0] + off.x, pivot[1] + off.y))
    return rot, r.topleft


def draw_arm_and_blade(s, shoulder, angle_deg, blade_len=20, heavy=False, glow=False):
    """Braço da frente e lâmina. angle_deg: 0 = para a frente (esquerda), 90 = para cima."""
    a = math.radians(angle_deg)
    fx, fy = -math.cos(a), -math.sin(a)          # frente = esquerda
    sx, sy = shoulder
    hx, hy = sx + fx * 9, sy + fy * 9
    pygame.draw.line(s, SLEEVE_DK, (sx, sy + 1), (hx, hy + 1), 4)
    pygame.draw.line(s, SLEEVE, (sx, sy), (hx, hy), 3)
    pygame.draw.line(s, SLEEVE_HI, (sx, sy - 1), ((sx + hx) / 2, (sy + hy) / 2 - 1), 1)
    # cabo e guarda
    gx, gy = hx + fx * 2, hy + fy * 2
    pygame.draw.line(s, HILT, (hx - fx * 3, hy - fy * 3), (gx, gy), 2)
    px, py = -fy, fx
    pygame.draw.line(s, GUARD, (gx + px * 3, gy + py * 3), (gx - px * 3, gy - py * 3), 2)
    # lâmina
    L = blade_len + (6 if heavy else 0)
    tx, ty = gx + fx * L, gy + fy * L
    pygame.draw.line(s, BLADE_DK, (gx + px, gy + py), (tx, ty), 3)
    pygame.draw.line(s, BLADE, (gx, gy), (tx, ty), 2)
    pygame.draw.line(s, BLADE_HI, (gx - px * 0.5, gy - py * 0.5), (tx - fx, ty - fy), 1)
    if glow:
        pygame.draw.circle(s, (230, 230, 255), (round(tx), round(ty)), 2)
    # mão
    pygame.draw.circle(s, SKIN_DK, (round(hx), round(hy) + 1), 2)
    pygame.draw.circle(s, SKIN, (round(hx), round(hy)), 2)


def compose(base, lean=0.0, hair=0, arm=None, shift=(0, 0), whole_angle=0.0, sink=0, squash=1.0):
    """Monta um quadro: pernas fixas, tronco girado na cintura, cabelo arrastando e braço/lâmina."""
    src = strip_weapon(base)
    upper, lower = split(src)
    if hair:
        upper = trail_hair(upper, hair)
    frame = pygame.Surface((FW, FH), pygame.SRCALPHA)
    ox = FOOT[0] - SRC_FOOT[0] + shift[0]
    oy = FOOT[1] - SRC_FOOT[1] + shift[1] + sink
    frame.blit(lower, (ox, oy))
    pivot = (SRC_FOOT[0] + 1, WAIST_Y)
    rot, tl = rotate_about(upper, pivot, lean)    # lean > 0 gira para trás (anti-horário vira a cabeça à direita)
    frame.blit(rot, (ox + tl[0], oy + tl[1]))
    if arm is not None:
        ang, extra = arm[0], arm[1:]
        r = math.radians(lean)
        # ombro acompanha o giro do tronco
        sx0, sy0 = 17 - pivot[0], 25 - pivot[1]
        sx = sx0 * math.cos(r) + sy0 * math.sin(r)
        sy = -sx0 * math.sin(r) + sy0 * math.cos(r)
        draw_arm_and_blade(frame, (ox + pivot[0] + sx, oy + pivot[1] + sy), ang, *extra)
    if squash != 1.0:
        w2 = round(FW * (2 - squash))
        h2 = round(FH * squash)
        sq = pygame.transform.scale(frame, (w2, h2))
        frame = pygame.Surface((FW, FH), pygame.SRCALPHA)
        frame.blit(sq, (FOOT[0] - FOOT[0] * w2 / FW, FH - h2))
    if whole_angle:
        rot, tl = rotate_about(frame, FOOT, whole_angle)
        frame2 = pygame.Surface((FW, FH), pygame.SRCALPHA)
        frame2.blit(rot, tl)
        frame = frame2
    return frame


def build():
    pygame.init()
    pygame.display.set_mode((1, 1))
    walk = load_walk()
    stance, knee, legs_apart, stride = walk[5], walk[0], walk[3], walk[4]
    rows = {
        # golpe rápido: preparo (lâmina atrás), corte, finalização, volta
        "quick": [compose(stance, 8, 1, (150, 18)), compose(stance, -8, 3, (10, 20)),
                  compose(stance, -14, 4, (-25, 20)), compose(stance, -6, 2, (-50, 18))],
        # golpe pesado: lâmina sobe por cima da cabeça e desce com tudo
        "heavy": [compose(stance, 10, 0, (120, 18, True)), compose(stance, 14, 1, (105, 18, True, True)),
                  compose(stance, -10, 4, (30, 18, True, True), shift=(-2, 0)),
                  compose(stance, -18, 5, (-30, 18, True), shift=(-3, 0)),
                  compose(stance, -8, 2, (-55, 18, True), shift=(-2, 0))],
        "up": [compose(stance, 6, 0, (160, 18)), compose(stance, 10, 1, (95, 20)), compose(stance, 6, 1, (70, 18))],
        "down": [compose(knee, -6, 0, (-80, 20), shift=(0, -2)), compose(knee, -10, 1, (-95, 22), shift=(0, -2))],
        "jump": [compose(knee, 4, 1, (-120, 16), shift=(0, -2)), compose(knee, 2, 2, (-130, 16), shift=(0, -2))],
        "fall": [compose(legs_apart, -2, 3, (-140, 16)), compose(legs_apart, -4, 4, (-145, 16))],
        "dash": [compose(stride, -16, 6, (-165, 16), shift=(-2, 0)), compose(stride, -18, 7, (-170, 16), shift=(-3, 0))],
        "hurt": [compose(stance, 16, -1, (-130, 16), shift=(2, 0))],
        "death": [compose(stance, 16, 0, (-130, 16), shift=(2, 0)),
                  compose(stance, 20, 0, None, whole_angle=12, shift=(8, 0)),
                  compose(stance, 20, 0, None, whole_angle=35, shift=(14, 2)),
                  compose(stance, 20, 0, None, whole_angle=65, shift=(20, 6)),
                  compose(stance, 20, 0, None, whole_angle=88, shift=(22, 8))],
        "land": [compose(stance, -4, 0, (-130, 16), squash=0.9)],
        # diagonal para cima: lâmina sai de trás e corta em 45 graus
        "diag": [compose(stance, 6, 0, (170, 18)), compose(stance, -4, 2, (60, 21)), compose(stance, -8, 3, (40, 21)),
                 compose(stance, -2, 1, (15, 18))],
    }
    cols = max(len(v) for v in rows.values())
    sheet = pygame.Surface((FW * cols, FH * len(ANIMS)), pygame.SRCALPHA)
    for r, name in enumerate(ANIMS):
        for c, fr in enumerate(rows[name]):
            sheet.blit(fr, (c * FW, r * FH))
    pygame.image.save(sheet, OUT)
    print(f"{OUT}: {cols}x{len(ANIMS)} quadros")
    return sheet


if __name__ == "__main__":
    build()
    sys.exit(0)
