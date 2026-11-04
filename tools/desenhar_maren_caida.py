"""Capitã Maren caída de costas (vista lateral), desenhada pixel a pixel com a paleta de maren.png.

Uso: python tools/desenhar_maren_caida.py  ->  assets/img/personagens/maren_caida.png

Cabeça à esquerda com o rosto para cima, chapéu caído ao lado, braço sobre o peito, casaco
escorrendo até o chão e botas com a ponta para cima. A última linha opaca é o apoio no chão.
"""

import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "img", "personagens", "maren_caida.png")

# paleta tirada de maren.png
O = (5, 2, 21)            # contorno
C = (34, 35, 61)          # casaco escuro / chapéu
c = (59, 71, 90)          # casaco médio
L = (76, 92, 108)         # casaco claro
S = (247, 192, 156)       # pele
s = (216, 126, 98)        # pele na sombra
G = (235, 201, 88)        # dourado
g = (183, 121, 53)        # dourado escuro
R = (207, 65, 60)         # bandana
r = (130, 36, 61)         # bandana na sombra
W = (227, 228, 234)       # cabelo
w = (156, 153, 176)       # cabelo na sombra
B = (126, 67, 53)         # bota
b = (80, 36, 48)          # bota escura
P = (49, 24, 47)          # calça
T = (248, 249, 250)       # camisa
M = (108, 28, 59)         # lábios arroxeados

WID, HEI = 66, 22
FLOOR = 19                # linha do chão (última linha preenchida antes do contorno)


def desenhar():
    px = {}

    def put(x, y, cor):
        if 0 <= x < WID and 0 <= y <= FLOOR:
            px[(x, y)] = cor

    # chapéu de três pontas caído de lado, aba no chão (x 1..12)
    for x in range(1, 13):
        topo = 14 if 3 <= x <= 10 else 16
        if 5 <= x <= 8:
            topo = 13
        for y in range(topo, FLOOR + 1):
            put(x, y, C if y < 17 else c)
        put(x, 17, G if 2 <= x <= 11 else C)          # galão dourado da aba
    put(6, 14, c); put(7, 14, c)

    # cabelo branco espalhado no chão, atrás da cabeça
    for x in range(11, 22):
        for y in range(15, FLOOR + 1):
            put(x, y, w if y == FLOOR else W)
    # cabeça (círculo) com o rosto para cima
    cx, cy, rad = 18, 13, 5.2
    for x in range(12, 25):
        for y in range(6, FLOOR + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= rad * rad:
                if y >= 14 or x <= 14:
                    put(x, y, w if y >= 17 or x == 12 else W)       # nuca e cabelo
                else:
                    put(x, y, S if y < 12 else s)
    # bandana vermelha na testa (lado do chapéu)
    for y in range(9, 16):
        put(14, y, R)
        put(15, y, R if y < 13 else r)
    put(13, 13, r); put(13, 14, r)
    # perfil: nariz para cima, olho fechado, lábios
    put(18, 7, S); put(19, 7, S); put(18, 6, S)
    put(16, 9, O); put(17, 9, O)              # olho fechado
    put(21, 9, M); put(22, 10, s)             # boca e queixo

    # tronco: o peito sobe, a barriga desce até o quadril
    for x in range(25, 49):
        topo = round(7 + 3 * ((x - 30) / 18) ** 2) if x >= 30 else round(7 + (30 - x) * 0.45)
        for y in range(topo, FLOOR + 1):
            prof = y - topo
            put(x, y, L if prof <= 1 else (c if prof <= 5 else C))
        if x <= 34:
            put(x, topo, G)                       # galão da lapela
    # aba do casaco escorrendo no chão depois do quadril
    for x in range(44, 53):
        for y in range(FLOOR - 2, FLOOR + 1):
            put(x, y, C)
    # pescoço e gola branca da camisa entre a cabeça e o casaco
    for y in range(10, 17):
        put(23, y, S if y < 12 else T)
        put(24, y, T if y < 15 else C)
    put(25, 9, T); put(25, 10, T); put(26, 9, T)

    # alça dourada atravessada no peito
    for i in range(9):
        put(27 + i, 9 + i // 2, g)
    # braço sobre a barriga: manga clara com linha de contorno em cima, punho dourado e mão
    for i in range(10):
        x, y = 28 + i, 13 - (i * 4) // 10
        put(x, y - 1, O)
        put(x, y, L)
        put(x, y + 1, c)
        put(x, y + 2, O if i > 1 else c)
    put(38, 9, G); put(38, 10, G); put(38, 11, G)
    for x, y in ((39, 9), (40, 9), (39, 10), (40, 10), (41, 10), (39, 11)):
        put(x, y, S)
    put(41, 9, s); put(40, 11, s)

    # pernas (calça) do quadril às botas
    for x in range(48, 56):
        for y in range(12, FLOOR - 2):
            put(x, y, P)
    # botas com a ponta para cima
    for x in range(55, 61):
        for y in range(11, FLOOR - 1):
            put(x, y, B if y < 16 else b)
    for x in range(58, 62):
        for y in range(6, 12):
            put(x, y, B if x < 61 else b)          # pé erguido; sola escura atrás
    put(55, 11, G); put(56, 11, G)                # dobra do cano

    # contorno de 1 px por fora de tudo (sem descer abaixo do chão)
    img = pygame.Surface((WID, FLOOR + 2), pygame.SRCALPHA)
    for (x, y), cor in px.items():
        img.set_at((x, y), cor + (255,))
    for (x, y) in list(px):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) not in px and 0 <= nx < WID and 0 <= ny <= FLOOR + 1:
                img.set_at((nx, ny), O + (255,))
    return img.subsurface(img.get_bounding_rect()).copy()


def main():
    pygame.init()
    img = desenhar()
    pygame.image.save(img, OUT)
    print("salvo", OUT, img.get_size())


if __name__ == "__main__":
    main()
