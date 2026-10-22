"""Dados das salas (provisórios). Coordenadas em tiles: (coluna, linha).

Progressão:
  Zona Cavernas (A, C, D, E, E2): só pulo e ataques. O Guardião protege o Dash.
  Vila (B): banco, loja, ferreiro. Fosso de 9 tiles = exige Dash para ir aos Jardins.
            Plataforma 6 tiles acima = exige Pulo duplo para ir às Alturas.
  Jardins (F, G, H, I): exigem Dash. No fim (I) está o Pulo duplo.
  Alturas (K, L, M): exigem Pulo duplo + Dash. Segredos, minérios e amuletos.
"""


class Grid:
    """Ajudante para desenhar salas: começa com paredes na borda e interior vazio."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.g = [["." for _ in range(w)] for _ in range(h)]
        self.rect(0, 0, w - 1, 0)
        self.rect(0, h - 1, w - 1, h - 1)
        self.rect(0, 0, 0, h - 1)
        self.rect(w - 1, 0, w - 1, h - 1)

    def rect(self, x0, y0, x1, y1, ch="#"):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.g[y][x] = ch
        return self

    def clear(self, x0, y0, x1, y1):
        return self.rect(x0, y0, x1, y1, ".")

    def hline(self, x0, x1, y, ch):
        return self.rect(x0, y, x1, y, ch)

    def put(self, x, y, ch):
        self.g[y][x] = ch
        return self

    def door(self, side, a, b, digit):
        for i in range(a, b + 1):
            if side == "W":
                self.g[i][0] = digit
            elif side == "E":
                self.g[i][self.w - 1] = digit
            elif side == "N":
                self.g[0][i] = digit
            else:
                self.g[self.h - 1][i] = digit
        return self

    def rows(self):
        return ["".join(r) for r in self.g]


# ---------------------------------------------------------------------------
# Zona 1 — Cavernas
# ---------------------------------------------------------------------------

def room_a():
    g = Grid(45, 20)
    g.rect(1, 1, 43, 4)                          # teto
    g.rect(1, 17, 43, 18)                        # chão
    g.rect(12, 15, 15, 16)                       # degrau de 2
    g.clear(22, 17, 25, 18).hline(22, 25, 19, "^")   # fosso pequeno (pulável)
    g.rect(30, 14, 34, 14)                       # beirada 3 acima
    g.put(32, 13, "*")
    g.put(3, 16, "P")
    g.put(19, 16, "g").put(39, 16, "g")
    g.door("E", 13, 16, "1")
    return g.rows()


def room_b():
    g = Grid(64, 26)
    g.rect(1, 1, 62, 8)                          # teto de rocha
    g.clear(3, 0, 8, 8).door("N", 3, 8, "4")     # poço esquerdo -> Túneis
    g.clear(40, 0, 45, 8).door("N", 40, 45, "5")  # poço direito -> Alturas
    g.rect(1, 24, 62, 25)                        # chão
    g.clear(48, 24, 56, 24).hline(48, 56, 25, "^")   # fosso de 9: exige dash
    g.door("W", 20, 23, "1").door("E", 20, 23, "3")
    # escada esquerda (pulos simples)
    g.hline(4, 8, 21, "-").hline(10, 14, 18, "-").hline(4, 8, 15, "-").hline(6, 10, 12, "-")
    g.hline(3, 6, 9, "-").hline(6, 8, 6, "-").hline(3, 5, 3, "-")
    # escada direita: o último degrau fica 6 acima -> exige pulo duplo
    g.hline(32, 36, 21, "-").hline(38, 42, 18, "-").hline(33, 39, 15, "-")
    g.hline(43, 45, 9, "-").hline(40, 42, 6, "-").hline(43, 45, 3, "-")
    g.put(18, 23, "$").put(26, 23, "B").put(44, 23, "R")
    return g.rows()


def room_c():
    g = Grid(56, 22)
    g.rect(1, 1, 54, 6)                          # teto
    g.clear(48, 21, 53, 21).door("S", 48, 53, "4")   # chão fino com buraco (vem da Vila)
    g.door("W", 17, 20, "6")
    g.rect(36, 18, 39, 20)                       # bloco de 3
    g.hline(22, 27, 18, "-").hline(14, 19, 15, "-")
    g.rect(1, 12, 12, 12)                        # beirada alta + chão do esconderijo
    g.rect(1, 7, 9, 8)                           # teto do esconderijo
    g.rect(9, 9, 9, 11, "X")                     # parede quebrável
    g.put(4, 11, "*").put(6, 11, "*").put(11, 11, "*")
    g.put(28, 11, "f").put(20, 20, "c").put(46, 20, "g")
    return g.rows()


def room_d():
    g = Grid(34, 30)
    g.rect(1, 1, 32, 4)
    g.rect(1, 27, 32, 28)
    g.rect(21, 10, 32, 10)                       # beirada de entrada
    g.door("E", 6, 9, "6").door("W", 23, 26, "7")
    g.hline(13, 17, 12, "-").hline(17, 23, 15, "-").hline(7, 13, 18, "-")
    g.hline(17, 23, 21, "-").hline(7, 13, 24, "-")
    g.rect(1, 15, 5, 15)                         # nicho lateral
    g.put(3, 14, "*")
    g.put(30, 26, "B").put(18, 26, "s").put(10, 23, "j")
    return g.rows()


def room_e():
    g = Grid(40, 20)
    g.rect(1, 1, 38, 3)
    g.rect(1, 17, 38, 18)
    g.door("E", 13, 16, "7").door("W", 13, 16, "8")
    g.rect(38, 13, 38, 16, "|")                  # fecha atrás do jogador durante a luta
    g.rect(1, 13, 1, 16, "=")                    # abre quando o chefe cai
    g.hline(8, 13, 14, "-").hline(26, 31, 14, "-")
    g.put(12, 16, "G")
    return g.rows()


def room_e2():
    g = Grid(24, 17)
    g.rect(1, 1, 22, 4)
    g.rect(1, 15, 22, 15)
    g.door("E", 11, 14, "8")
    g.rect(6, 13, 9, 14)                         # pedestal
    g.put(7, 12, "*")
    return g.rows()


# ---------------------------------------------------------------------------
# Zona 2 — Jardins (exige dash)
# ---------------------------------------------------------------------------

def room_f():
    g = Grid(44, 28)
    g.rect(1, 1, 42, 3)
    g.rect(1, 26, 42, 26)
    g.rect(1, 11, 8, 25)                         # bloco de entrada
    g.door("W", 7, 10, "1").door("E", 22, 25, "2")
    g.rect(12, 14, 15, 14).rect(21, 17, 24, 17).rect(30, 20, 33, 20).rect(38, 23, 41, 23)
    g.hline(9, 37, 25, "^")
    g.put(20, 9, "f").put(34, 13, "f")
    return g.rows()


def room_g():
    g = Grid(64, 20)
    g.rect(1, 1, 62, 3)
    g.rect(1, 17, 62, 18)
    g.rect(16, 4, 40, 13)                        # teto baixo: corredor de 3 tiles
    g.clear(20, 17, 24, 18).hline(20, 24, 19, "^")
    g.clear(31, 17, 35, 18).hline(31, 35, 19, "^")
    g.hline(44, 48, 11, "-")                     # 6 acima: volte com pulo duplo
    g.put(46, 10, "*")
    g.put(6, 16, "B")
    g.put(28, 16, "s").put(52, 7, "f").put(56, 16, "j")
    g.door("W", 13, 16, "1").door("E", 13, 16, "2")
    return g.rows()


def room_h():
    g = Grid(32, 44)
    g.rect(1, 1, 30, 4)
    g.clear(12, 0, 17, 4).door("N", 12, 17, "2")
    g.door("W", 39, 42, "1")
    for i, y in enumerate(range(40, 9, -3)):
        if i % 2 == 0:
            g.hline(6, 11, y, "-")
        else:
            g.hline(18, 23, y, "-")
    g.hline(12, 17, 7, "-").hline(15, 17, 4, "-")
    # esconderijo à direita
    g.rect(24, 37, 30, 37)
    g.rect(25, 32, 30, 32)
    g.rect(25, 33, 25, 36, "X")
    g.put(27, 36, "*").put(29, 36, "*")
    g.put(14, 30, "f").put(14, 15, "f").put(30, 20, "t")
    return g.rows()


def room_i():
    g = Grid(24, 18)
    g.rect(1, 1, 22, 6)
    g.clear(9, 17, 14, 17).door("S", 9, 14, "1")
    g.rect(17, 15, 20, 16)
    g.put(18, 14, "*")
    return g.rows()


# ---------------------------------------------------------------------------
# Zona 3 — Alturas (exige pulo duplo + dash)
# ---------------------------------------------------------------------------

def room_k():
    g = Grid(40, 40)
    g.clear(17, 39, 22, 39).door("S", 17, 22, "1")
    g.door("W", 2, 5, "2").door("E", 2, 5, "3")
    g.rect(1, 6, 6, 6).rect(33, 6, 38, 6)
    g.rect(4, 34, 9, 34).rect(16, 29, 21, 29).rect(28, 24, 33, 24)
    g.rect(16, 19, 21, 19).rect(4, 14, 9, 14).rect(16, 9, 21, 9)
    g.hline(25, 38, 38, "^")
    g.rect(35, 19, 38, 19)
    g.put(36, 18, "*")
    g.put(38, 12, "t").put(10, 22, "f").put(26, 12, "f")
    return g.rows()


def room_l():
    g = Grid(26, 16)
    g.rect(1, 1, 24, 5)
    g.rect(1, 13, 24, 14)
    g.door("E", 9, 12, "1")
    g.rect(6, 6, 6, 9)
    g.rect(6, 10, 6, 12, "X")
    g.put(3, 12, "*").put(12, 12, "*")
    g.put(18, 12, "s")
    return g.rows()


def room_m():
    g = Grid(36, 18)
    g.rect(1, 1, 34, 4)
    g.rect(1, 13, 34, 16)
    g.door("W", 9, 12, "1")
    g.clear(8, 13, 25, 15).hline(8, 25, 16, "^")
    g.rect(11, 11, 13, 11).rect(17, 9, 19, 9).rect(22, 11, 23, 11)
    g.put(16, 6, "f")
    g.put(28, 12, "*").put(31, 12, "*").put(33, 12, "*")
    return g.rows()


ROOM_DEFS = [
    {"id": "A", "name": "Entrada", "zone": "cavernas", "rows": room_a(), "items": [("coins", 25)]},
    {"id": "B", "name": "Vila", "zone": "vila", "rows": room_b()},
    {"id": "C", "name": "Túneis", "zone": "cavernas", "rows": room_c(),
     "items": [("fragment", None), ("charm", "lamina"), ("coins", 30)]},
    {"id": "D", "name": "Galeria", "zone": "cavernas", "rows": room_d(), "items": [("charm", "coletor")]},
    {"id": "E", "name": "Arena do Guardião", "zone": "arena", "rows": room_e()},
    {"id": "E2", "name": "Santuário do Dash", "zone": "arena", "rows": room_e2(), "items": [("ability", "dash")]},
    {"id": "F", "name": "Descida", "zone": "jardins", "rows": room_f()},
    {"id": "G", "name": "Jardim", "zone": "jardins", "rows": room_g(), "items": [("fragment", None)]},
    {"id": "H", "name": "Ninho", "zone": "jardins", "rows": room_h(),
     "items": [("charm", "vigor"), ("ore", None)]},
    {"id": "I", "name": "Santuário do Pulo", "zone": "jardins", "rows": room_i(),
     "items": [("ability", "double_jump")]},
    {"id": "K", "name": "Picos", "zone": "alturas", "rows": room_k(), "items": [("fragment", None)]},
    {"id": "L", "name": "Câmara", "zone": "alturas", "rows": room_l(),
     "items": [("ore", None), ("charm", "forca")]},
    {"id": "M", "name": "Mirante", "zone": "alturas", "rows": room_m(),
     "items": [("charm", "vento"), ("ore", None), ("coins", 80)]},
]

ROOM_LINKS = [
    (("A", "1"), ("B", "1")),
    (("B", "4"), ("C", "4")),
    (("B", "5"), ("K", "1")),
    (("B", "3"), ("F", "1")),
    (("C", "6"), ("D", "6")),
    (("D", "7"), ("E", "7")),
    (("E", "8"), ("E2", "8")),
    (("F", "2"), ("G", "1")),
    (("G", "2"), ("H", "1")),
    (("H", "2"), ("I", "1")),
    (("K", "2"), ("L", "1")),
    (("K", "3"), ("M", "1")),
]

START_ROOM = "A"
