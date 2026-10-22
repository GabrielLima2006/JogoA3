"""Capítulo 1 — Jantar no molhado em veneno: salas do navio, personagens e diálogos.

Mapa (portas pelos dígitos na borda; ver world.py):

                       [Gávea]
                          │ mastro
    [Tombadilho]──────[Convés]──────[Proa + cabine]
                          │ escotilha
    [Cabine capitã]═D═[Salão]──[Cozinha]──[Alojamento]
                                   │ alçapão
                                [Porão]

D = porta trancada (chave no bolso da capitã).
"""

from .rooms import Grid


# ---------------------------------------------------------------------------
# Convés (zona aberta, céu de tempestade)
# ---------------------------------------------------------------------------

def room_conves():
    g = Grid(50, 18)
    g.rect(1, 15, 48, 16)                                   # tábuas do convés
    g.door("W", 11, 14, "1").door("E", 11, 14, "2")
    g.door("N", 23, 26, "3")                                # topo do mastro -> gávea
    g.clear(8, 15, 10, 17).door("S", 8, 10, "4")            # escotilha -> salão
    # cordame do mastro (subida com pulos simples)
    g.hline(20, 23, 12, "-").hline(25, 28, 9, "-").hline(20, 23, 6, "-").hline(24, 27, 3, "-")
    g.rect(36, 13, 37, 14)                                  # caixotes
    g.rect(41, 14, 41, 14)
    return g.rows()


def room_tombadilho():
    g = Grid(30, 18)
    g.rect(1, 15, 28, 16)
    g.door("E", 11, 14, "1")
    g.rect(1, 12, 10, 14)                                   # tombadilho elevado (leme)
    g.put(6, 11, "N")                                       # imediato
    return g.rows()


def room_proa():
    g = Grid(40, 18)
    g.rect(1, 15, 38, 16)
    g.door("W", 11, 14, "1")
    g.rect(24, 5, 38, 5)                                    # teto da cabine
    g.rect(24, 6, 24, 12)                                   # parede (porta nas linhas 13-14)
    g.put(12, 14, "N")                                      # melhor amigo
    g.put(28, 14, "P").put(31, 14, "B").put(36, 14, "*")    # início, cama (salvar), baú de truques
    return g.rows()


def room_gavea():
    g = Grid(24, 30)
    g.clear(10, 29, 13, 29).door("S", 10, 13, "1")
    for i, y in enumerate(range(26, 7, -3)):
        if i % 2 == 0:
            g.hline(5, 9, y, "-")
        else:
            g.hline(13, 17, y, "-")
    g.hline(8, 16, 5, "-")                                  # cesto (mão única: atravessa por baixo)
    g.put(12, 4, "N")                                       # meia-irmã
    g.put(19, 15, "f").put(4, 11, "f")                      # gaivotas
    return g.rows()


# ---------------------------------------------------------------------------
# Interior
# ---------------------------------------------------------------------------

def room_salao():
    g = Grid(36, 18)
    g.rect(1, 1, 34, 2)
    g.clear(16, 0, 18, 2).door("N", 16, 18, "1")            # escotilha -> convés
    g.rect(1, 15, 34, 16)
    g.door("W", 11, 14, "2").door("E", 11, 14, "3")
    g.rect(1, 11, 1, 14, "D")                               # porta da cabine da capitã
    # escada até a escotilha
    g.hline(19, 22, 12, "-").hline(13, 16, 9, "-").hline(19, 22, 6, "-").hline(16, 17, 4, "-")
    g.rect(7, 14, 12, 14)                                   # mesa do jantar
    g.put(10, 13, "N")                                      # a capitã
    return g.rows()


def room_cabine_capita():
    g = Grid(26, 18)
    g.rect(1, 15, 24, 16)
    g.door("E", 11, 14, "1")
    g.rect(5, 13, 9, 14)                                    # escrivaninha
    g.hline(14, 19, 12, "-")                                # cama
    return g.rows()


def room_cozinha():
    g = Grid(34, 17)
    g.rect(1, 15, 32, 15)                                   # assoalho fino
    g.door("W", 11, 14, "1").door("E", 11, 14, "2")
    g.clear(24, 15, 26, 16).door("S", 24, 26, "3")          # alçapão -> porão
    g.rect(3, 13, 6, 14)                                    # fogão
    g.hline(9, 13, 11, "-")                                 # prateleira
    g.put(15, 14, "N")                                      # cozinheira
    return g.rows()


def room_alojamento():
    g = Grid(34, 17)
    g.rect(1, 15, 32, 15)
    g.door("W", 11, 14, "1")
    g.hline(5, 9, 12, "-").hline(13, 17, 12, "-").hline(21, 25, 12, "-")    # redes
    g.hline(9, 13, 9, "-").hline(17, 21, 9, "-")
    g.rect(30, 13, 31, 14)                                  # baú
    g.put(27, 14, "N")                                      # grumete
    return g.rows()


def room_porao():
    g = Grid(50, 20)
    g.rect(1, 1, 48, 3)
    g.clear(6, 0, 8, 3).door("N", 6, 8, "1")                # alçapão -> cozinha
    g.rect(1, 16, 48, 18)
    g.clear(20, 16, 28, 18).rect(20, 17, 28, 19, "~")       # trecho alagado de 9: exige Passo ilusório
    g.hline(9, 12, 13, "-").hline(3, 6, 10, "-").hline(9, 12, 7, "-").hline(6, 7, 4, "-")
    g.rect(40, 14, 41, 15)                                  # sacos
    g.put(15, 15, "g").put(36, 15, "g").put(45, 15, "g")    # ratos
    return g.rows()


ROOM_DEFS = [
    {"id": "conves", "name": "Convés principal", "zone": "convés", "rows": room_conves()},
    {"id": "tombadilho", "name": "Tombadilho", "zone": "convés", "rows": room_tombadilho(), "npcs": ["imediato"]},
    {"id": "proa", "name": "Proa", "zone": "convés", "rows": room_proa(), "npcs": ["amigo"],
     "items": [("ability", "dash")]},
    {"id": "gavea", "name": "Cesto da gávea", "zone": "convés", "rows": room_gavea(), "npcs": ["irma"]},
    {"id": "salao", "name": "Salão de jantar", "zone": "interior", "rows": room_salao(), "npcs": ["capita"],
     "key": "chave_cabine"},
    {"id": "cabine", "name": "Cabine da capitã", "zone": "interior", "rows": room_cabine_capita()},
    {"id": "cozinha", "name": "Cozinha", "zone": "interior", "rows": room_cozinha(), "npcs": ["cozinheira"]},
    {"id": "alojamento", "name": "Alojamento", "zone": "interior", "rows": room_alojamento(), "npcs": ["grumete"]},
    {"id": "porao", "name": "Porão", "zone": "porão", "rows": room_porao()},
]

ROOM_LINKS = [
    (("conves", "1"), ("tombadilho", "1")),
    (("conves", "2"), ("proa", "1")),
    (("conves", "3"), ("gavea", "1")),
    (("conves", "4"), ("salao", "1")),
    (("salao", "2"), ("cabine", "1")),
    (("salao", "3"), ("cozinha", "1")),
    (("cozinha", "2"), ("alojamento", "1")),
    (("cozinha", "3"), ("porao", "1")),
]

START_ROOM = "proa"


# ---------------------------------------------------------------------------
# Personagens e diálogos
# ---------------------------------------------------------------------------
# Os textos aceitam as formas do protagonista: {feiticeiro}, {o}, {bom}, {passageiro}.

CHARACTERS = {
    "capita": {"name": "A capitã", "color": (170, 120, 110), "height": 40, "style": "corpo",
               "prompt": "Examinar"},
    "cozinheira": {"name": "Cozinheira", "color": (235, 190, 150), "height": 44, "style": "chef"},
    "grumete": {"name": "Grumete", "color": (205, 170, 115), "height": 32, "style": "boné"},
    "imediato": {"name": "Imediato", "color": (140, 150, 190), "height": 48, "style": "casaco"},
    "irma": {"name": "Meia-irmã da capitã", "color": (205, 95, 85), "height": 42, "style": "bandana"},
    "amigo": {"name": "Melhor amigo de infância", "color": (120, 185, 140), "height": 44, "style": "cachecol"},
}

DIALOGS = {
    "capita": {
        "first": [
            "A capitã está caída sobre a mesa. Os lábios estão arroxeados e a mão ainda segura a colher.",
            "O prato dela está pela metade. Os outros pratos da mesa estão vazios.",
            "No bolso do casaco, você encontra uma chave de latão com o brasão do navio.",
        ],
        "repeat": ["Ninguém tocou no prato desde o jantar."],
        "on_first": "chave_cabine",
    },
    "cozinheira": {
        "first": [
            "Não me olhe assim! Eu cozinho para este navio há onze anos.",
            "Tudo saiu da mesma panela. Todo mundo comeu o mesmo ensopado e ninguém mais passou mal.",
            "Eu só cozinho, {feiticeiro}. Quem leva os pratos ao salão é a tripulação.",
        ],
        "repeat": ["Ainda aqui? A panela está limpa, pode olhar se quiser."],
    },
    "grumete": {
        "first": [
            "E-eu? Eu nem entrei no salão! Estava lavando o convés a noite toda.",
            "A capitã... ela era boa comigo. Às vezes.",
            "Me deixa em paz, tá? Eu não fiz nada.",
        ],
        "repeat": ["Já falei! Eu estava lavando o convés!"],
    },
    "imediato": {
        "first": [
            "Eu estava no leme a noite toda. Alguém tem que manter este navio inteiro com essa tempestade.",
            "E vou te dizer uma coisa, {feiticeiro}: quem ganha com isso é a irmã. O navio agora é dela.",
        ],
        "repeat": ["Vá investigar. Eu tenho um navio para segurar."],
    },
    "irma": {
        "first": [
            "Subiu até aqui só para me acusar?",
            "Não ganho nada com a morte dela. Nada.",
            "Agora me deixa olhar o mar. O vento está mudando.",
        ],
        "repeat": ["O vento está mudando. Isso nunca é bom sinal."],
    },
    "amigo": {
        "first": [
            "Quanto tempo! Nunca pensei que fosse te reencontrar num navio, e logo numa noite dessas.",
            "Se eu fosse você, ficaria de olho na irmã da capitã. Vi as duas discutindo mais cedo.",
            "Ah, e o seu baú de truques está ali na cabine. Acho que você vai precisar dele.",
        ],
        "repeat": ["Cuidado lá embaixo. A água está entrando no porão."],
    },
}

FLAG_MESSAGES = {
    "chave_cabine": ("Chave da cabine", "A porta da cabine da capitã, no salão, agora abre."),
}
