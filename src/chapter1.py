"""O mundo do jogo: navio, porão, cordame, ilha e templo.

Mapa (portas pelos dígitos na borda; ver world.py):

                [Cordame 2]──[Gávea: CHEFE 2]
                     │
                [Cordame 1]
                     │ (precisa da Levitação)
   [Cabine]──[Convés (hub)]══D══[Praia]──[Floresta]──[Ruínas: CHEFE 3]──[Templo]──[Altar: FINAL]
                     │                        (D abre quando o navio atraca, depois do chefe 2)
                [Porão 1]──[Porão 2]──[Toca: CHEFE 1]

Habilidades: Passo ilusório (dash) desde o início · Levitação (pulo duplo, chefe 1).
Cartas da capitã (3) escondidas: com as três, o final verdadeiro.
"""

from .rooms import Grid


def room_cabine():
    g = Grid(30, 17)
    g.rect(1, 1, 28, 3)
    g.rect(1, 14, 28, 15)
    g.door("E", 10, 13, "1")
    g.hline(4, 8, 11, "-")                    # cama
    g.rect(21, 12, 23, 13)                    # escrivaninha
    g.put(12, 13, "B").put(17, 13, "P")
    return g.rows()


def room_conves():
    g = Grid(72, 22)
    g.rect(1, 18, 70, 20)
    g.door("W", 14, 17, "1").door("E", 14, 17, "4")
    g.rect(70, 14, 70, 17, "D")               # prancha: só abre quando o navio atraca
    g.clear(20, 18, 22, 21).door("S", 20, 22, "2")      # escotilha -> porão
    # cordame do mastro: o último degrau (5 tiles acima) exige a Levitação (pulo duplo)
    g.hline(24, 28, 15, "-").hline(19, 23, 12, "-").hline(24, 28, 9, "-")
    g.hline(28, 36, 4, "-").door("N", 33, 36, "3")
    g.rect(44, 16, 45, 17).rect(54, 17, 55, 17)         # caixotes
    g.put(8, 17, "N").put(30, 17, "N")                  # capitã (corpo) e o amigo
    g.put(13, 17, "$").put(62, 17, "R")
    return g.rows()


# ---------------------------------------------------------------------------
# Área 1 — Porão (sem habilidades)
# ---------------------------------------------------------------------------

def room_porao1():
    g = Grid(56, 24)
    g.rect(1, 1, 54, 2)
    g.clear(20, 0, 22, 2).door("N", 20, 22, "1")
    g.rect(1, 20, 54, 22)
    # escada de volta ao convés
    g.hline(24, 27, 17, "-").hline(17, 20, 14, "-").hline(24, 27, 11, "-").hline(17, 20, 8, "-")
    g.hline(21, 22, 5, "-").hline(20, 21, 3, "-")
    # poça e tábuas podres sobre a água
    g.clear(34, 20, 37, 22).rect(34, 21, 37, 22, "~")
    g.clear(45, 20, 50, 22).rect(45, 21, 50, 22, "~").hline(45, 50, 20, "C")
    g.door("E", 16, 19, "2")
    g.put(9, 19, "*").put(31, 19, "k").put(42, 19, "g").put(53, 19, "g")
    return g.rows()


def room_porao2():
    g = Grid(64, 24)
    g.rect(1, 1, 62, 2)
    g.door("W", 16, 19, "1").door("E", 16, 19, "2")
    g.rect(1, 20, 9, 22)
    g.rect(10, 21, 55, 22, "~")               # canal alagado
    g.rect(13, 18, 15, 22)                    # ilha A
    g.hline(30, 35, 16, "C")                  # tábuas que desabam
    g.rect(38, 17, 40, 22)                    # ilha B
    g.rect(44, 20, 62, 22)                    # chão leste
    g.hline(51, 57, 10, "-")                  # prateleira alta (plataforma que sobe)
    g.put(4, 19, "B")
    g.put(52, 9, "*").put(55, 9, "*").put(39, 16, "*")
    g.put(58, 19, "g").put(60, 19, "k").put(25, 15, "f")
    return g.rows()


def room_toca():
    g = Grid(40, 18)
    g.rect(1, 1, 38, 2)
    g.rect(1, 15, 38, 16)
    g.door("W", 11, 14, "1")
    g.rect(1, 11, 1, 14, "|")
    g.hline(7, 11, 12, "-").hline(28, 32, 12, "-")
    g.put(28, 14, "G")
    return g.rows()


# ---------------------------------------------------------------------------
# Área 2 — Cordame (precisa da Levitação)
# ---------------------------------------------------------------------------

def room_cordame1():
    g = Grid(40, 40)
    g.clear(17, 39, 20, 39).door("S", 17, 20, "1")
    g.hline(8, 13, 36, "-").hline(21, 25, 33, "-").hline(30, 35, 30, "-").hline(22, 26, 27, "C")
    g.hline(12, 17, 24, "-").hline(32, 37, 18, "-").hline(22, 26, 15, "-").hline(12, 16, 12, "-")
    g.hline(4, 8, 9, "-").hline(12, 15, 6, "-").hline(20, 24, 4, "-")
    g.rect(31, 4, 38, 4)
    g.door("E", 1, 3, "2")
    g.put(34, 29, "*")
    g.put(26, 29, "f").put(10, 17, "f").put(28, 8, "f")
    return g.rows()


def room_cordame2():
    g = Grid(60, 20)
    g.door("W", 12, 14, "1").door("E", 11, 14, "2")
    g.rect(1, 15, 10, 16)
    g.rect(1, 18, 58, 18, "~")                # o mar lá embaixo
    g.hline(13, 16, 13, "-")
    g.rect(24, 14, 26, 18)                    # topo de mastro
    g.hline(29, 34, 14, "C")
    g.rect(48, 15, 58, 16)
    g.hline(29, 32, 8, "-")                   # carta: só com pulo duplo (volte depois!)
    g.put(30, 7, "*").put(57, 14, "*")
    g.put(3, 14, "B").put(54, 14, "t")
    g.put(20, 8, "f").put(41, 7, "f")
    return g.rows()


def room_gavea():
    g = Grid(36, 20)
    g.rect(1, 17, 34, 18)
    g.door("W", 13, 16, "1")
    g.rect(1, 13, 1, 16, "|")
    g.hline(5, 9, 14, "-").hline(26, 30, 14, "-")
    g.put(26, 16, "G")
    return g.rows()


# ---------------------------------------------------------------------------
# Área 3 — Ilha (navio atracado; pulo duplo + dash)
# ---------------------------------------------------------------------------

def room_praia():
    g = Grid(60, 22)
    g.door("W", 14, 17, "1").door("E", 8, 11, "2")
    g.rect(1, 18, 14, 20)
    g.hline(15, 22, 20, "^")                  # vala de espinhos (8)
    g.rect(23, 18, 35, 20)
    g.rect(36, 12, 58, 20)                    # penhasco: 6 acima (pulo duplo)
    g.put(4, 17, "B").put(25, 17, "*")
    g.put(28, 17, "j").put(33, 17, "k").put(48, 11, "c")
    g.put(31, 17, "g").put(53, 11, "g").put(44, 6, "f")       # lobos e diabrete
    return g.rows()


def room_floresta():
    g = Grid(48, 40)
    g.rect(1, 37, 46, 38)
    g.door("W", 33, 36, "1").door("E", 2, 5, "2")
    g.hline(20, 46, 36, "^")
    g.hline(6, 11, 32, "-").hline(16, 20, 28, "-").hline(25, 30, 25, "C").hline(35, 40, 21, "-")
    g.hline(30, 35, 10, "-").hline(20, 24, 8, "-").hline(8, 13, 5, "-")
    g.rect(38, 6, 46, 6)
    g.put(10, 4, "*").put(44, 5, "*").put(38, 20, "*")
    g.put(18, 27, "j").put(30, 16, "f").put(9, 36, "j")
    g.put(14, 36, "g").put(12, 18, "f")                        # lobo no chão e diabrete no alto
    return g.rows()


def room_ruinas():
    g = Grid(40, 20)
    g.rect(1, 17, 38, 18)
    g.door("W", 13, 16, "1").door("E", 13, 16, "2")
    g.rect(1, 13, 1, 16, "|")
    g.rect(38, 13, 38, 16, "=")
    g.hline(6, 11, 12, "-").hline(28, 33, 12, "-").hline(16, 23, 8, "-")
    g.put(30, 16, "G")
    return g.rows()


def room_templo():
    g = Grid(60, 22)
    g.rect(1, 18, 58, 20)
    g.door("W", 14, 17, "1").door("E", 14, 17, "2")
    g.hline(10, 46, 17, "^")
    g.hline(11, 14, 15, "-").hline(19, 23, 14, "C").hline(38, 41, 15, "-")
    g.put(3, 17, "B").put(40, 14, "*")
    g.put(52, 17, "c").put(56, 17, "s")
    g.put(39, 14, "t").put(26, 8, "f")                         # lich na plataforma e espírito
    return g.rows()


def room_altar():
    g = Grid(44, 22)
    g.rect(1, 19, 42, 20)
    g.door("W", 15, 18, "1")
    g.rect(1, 15, 1, 18, "|")
    g.hline(6, 11, 14, "-").hline(32, 37, 14, "-").hline(17, 26, 10, "-")
    g.put(30, 18, "G")
    return g.rows()


ROOM_DEFS = [
    {"id": "cabine", "name": "Cabine", "zone": "interior", "rows": room_cabine()},
    {"id": "conves", "name": "Convés", "zone": "convés", "rows": room_conves(), "npcs": ["capita", "amigo"],
     "key": "atracado"},
    {"id": "porao1", "name": "Porão", "zone": "porão", "rows": room_porao1(), "items": [("charm", "lamina")]},
    {"id": "porao2", "name": "Porão Alagado", "zone": "porão", "rows": room_porao2(),
     "items": [("food", "peixe"), ("letter", "carta1"), ("fragment", None)],
     "movers": [{"x0": 18, "y0": 16, "x1": 26, "y1": 16, "w": 3, "speed": 90},
                {"x0": 47, "y0": 19, "x1": 47, "y1": 10, "w": 3, "speed": 70}]},
    {"id": "toca", "name": "Toca dos Ratos", "zone": "porão", "rows": room_toca(), "boss": "rei_rato"},
    {"id": "cordame1", "name": "Cordame", "zone": "convés", "rows": room_cordame1(), "items": [("charm", "coletor")],
     "movers": [{"x0": 19, "y0": 21, "x1": 28, "y1": 21, "w": 3, "speed": 100}]},
    {"id": "cordame2", "name": "Vergas", "zone": "convés", "rows": room_cordame2(),
     "items": [("letter", "carta2"), ("charm", "vento")],
     "movers": [{"x0": 36, "y0": 13, "x1": 44, "y1": 13, "w": 3, "speed": 95}]},
    {"id": "gavea", "name": "Cesto da Gávea", "zone": "convés", "rows": room_gavea(), "boss": "cavaleiro"},
    {"id": "praia", "name": "Praia da Ilha", "zone": "ilha", "rows": room_praia(), "items": [("food", "torta")]},
    {"id": "floresta", "name": "Floresta", "zone": "ilha", "rows": room_floresta(),
     "items": [("letter", "carta3"), ("charm", "vigor"), ("fragment", None)],
     "movers": [{"x0": 42, "y0": 20, "x1": 42, "y1": 10, "w": 3, "speed": 70}]},
    {"id": "ruinas", "name": "Ruínas", "zone": "ruínas", "rows": room_ruinas(), "boss": "irma"},
    {"id": "templo", "name": "Templo da Maré", "zone": "templo", "rows": room_templo(), "items": [("charm", "forca")],
     "movers": [{"x0": 26, "y0": 13, "x1": 34, "y1": 13, "w": 3, "speed": 110}]},
    {"id": "altar", "name": "Altar", "zone": "templo", "rows": room_altar(), "boss": "feiticeiro"},
]

ROOM_LINKS = [
    (("cabine", "1"), ("conves", "1")),
    (("conves", "2"), ("porao1", "1")),
    (("porao1", "2"), ("porao2", "1")),
    (("porao2", "2"), ("toca", "1")),
    (("conves", "3"), ("cordame1", "1")),
    (("cordame1", "2"), ("cordame2", "1")),
    (("cordame2", "2"), ("gavea", "1")),
    (("conves", "4"), ("praia", "1")),
    (("praia", "2"), ("floresta", "1")),
    (("floresta", "2"), ("ruinas", "1")),
    (("ruinas", "2"), ("templo", "1")),
    (("templo", "2"), ("altar", "1")),
]

START_ROOM = "cabine"
START_ABILITIES = ("dash",)   # o Passo ilusório é o truque da protagonista desde o início


# ---------------------------------------------------------------------------
# Personagens, chefes e textos
# ---------------------------------------------------------------------------

CHARACTERS = {
    "capita": {"name": "A capitã", "style": "corpo", "prompt": "Examinar", "color": (40, 44, 70), "height": 18},
    "amigo": {"name": "Melhor amigo de infância", "style": "amigo", "color": (70, 120, 90), "height": 44},
}

DIALOGS = {
    "capita": {
        "first": [
            "A capitã está caída no convés. Os lábios estão arroxeados: veneno.",
            "Na mão dela, um papel amassado: \"O tônico... o grumete... no porão.\"",
        ],
        "repeat": ["Você promete a si mesm{o}: vai descobrir quem fez isso."],
    },
    "amigo": {
        "first": [
            "Que noite! Quem diria que eu ia te reencontrar justo neste navio.",
            "Vi o grumete descer correndo pela escotilha. Os ratos lá embaixo estão... estranhos.",
            "Vai lá, {feiticeiro}. Eu cuido do convés.",
        ],
        "repeat": ["O porão fica pela escotilha, perto do mastro. Cuidado com a água."],
    },
}

FLAG_MESSAGES = {
    "atracado": ("O navio atracou", "A prancha do convés agora leva à ilha."),
}

LETTERS = {
    "carta1": ("Carta da capitã (1/3)", "\"Alguém está levando gente do porto. Desaparecidos, todos ligados a mim.\""),
    "carta2": ("Carta da capitã (2/3)", "\"Os sumidos estão vivos, presos no Templo da Maré, na ilha.\""),
    "carta3": ("Carta da capitã (3/3)",
               "\"Achei o culpado: meu velho amigo de infância. Ele nunca me perdoou por aquele dia.\""),
}

# id -> classe em bosses.py, recompensa, falas de apresentação e de derrota
BOSSES = {
    "rei_rato": {
        "reward": ("ability", "double_jump"),
        "speaker": "grumete",
        "intro": "O tônico... ele disse que ia acalmar a capitã! E agora... os ratos me obedecem!",
        "after": [
            "Eu só queria não ser expulso do navio...",
            "Um homem de cachecol roxo me deu o tônico. Disse que era remédio.",
        ],
    },
    "cavaleiro": {
        "reward": ("fragment", None),
        "flag": "atracado",
        "speaker": "imediato",
        "intro": "Ele me prometeu este navio! A armadura rubra é o preço, e eu pago!",
        "after": [
            "A ambição me cegou. O navio está atracando na ilha...",
            "O feiticeiro está no templo. Os desaparecidos também.",
        ],
    },
    "irma": {
        "reward": None,
        "speaker": "irma",
        "intro": "Ele tem alguém que eu amo preso no templo. Não posso deixar você passar!",
        "after": [
            "Escondi as cartas da minha irmã para proteger quem eu amo...",
            "Vá. Salve todos. E pare aquele monstro... que um dia foi seu amigo.",
        ],
    },
    "feiticeiro": {
        "reward": None,
        "speaker": "amigo",
        "intro": "Anos atrás eu levei a culpa no seu lugar, e você ficou calado. Agora vou tirar tudo de você!",
        "after": [],
    },
}

ENDING_TRUE = [
    "O feitiço da maré se desfaz. As correntes do templo caem.",
    "Os desaparecidos voltam para o navio, vivos.",
    "Com as cartas da capitã, a verdade é contada no porto: os cúmplices foram enganados,",
    "e o verdadeiro culpado é levado a julgamento.",
    "Você confessa o erro de anos atrás. Pela primeira vez, a mentira não é o seu truque.",
    "FINAL VERDADEIRO",
]
ENDING_NORMAL = [
    "O feitiço da maré se desfaz. As correntes do templo caem.",
    "Os desaparecidos voltam para o navio, vivos.",
    "Mas sem as cartas da capitã, ninguém no porto acredita na história inteira...",
    "(Encontre as 3 cartas escondidas para ver o final verdadeiro.)",
    "FIM",
]
