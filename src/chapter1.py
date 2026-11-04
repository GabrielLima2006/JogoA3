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
Páginas do diário da Capitã Maren (3) escondidas: com as três, o final verdadeiro.
"""

from .rooms import Grid


def room_cabine():
    g = Grid(30, 17)
    g.rect(1, 1, 28, 3)
    g.rect(1, 14, 28, 15)
    g.door("E", 10, 13, "1")
    g.hline(3, 8, 11, "-")                    # cama (3 acima do chão)
    g.hline(10, 15, 8, "-")                   # prateleira de livros: sobe pela cama
    g.rect(21, 12, 23, 13)                    # escrivaninha
    g.put(13, 7, "*")                         # moedas guardadas na prateleira
    g.put(12, 13, "B").put(17, 13, "P").put(26, 13, "k")
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
    g.hline(11, 15, 7, "-")                   # verga do traquete: pulo + dash a partir do 3º degrau
    # mastro da mezena: caixotes e vergas até um cesto que só a Levitação alcança
    g.rect(44, 16, 45, 17).rect(54, 17, 55, 17)         # caixotes
    g.hline(47, 51, 14, "-").hline(53, 57, 11, "-").hline(59, 64, 8, "-")
    g.hline(51, 55, 3, "-")                   # cesto da mezena: 5 acima (volte com o pulo duplo)
    g.put(53, 2, "*").put(13, 6, "*").put(62, 7, "k")
    g.put(8, 17, "N").put(30, 17, "N")                  # capitã (corpo) e o amigo
    g.put(13, 17, "$").put(62, 17, "R")
    return g.rows()


# ---------------------------------------------------------------------------
# Área 1 — Porão (sem habilidades)
# ---------------------------------------------------------------------------

def room_porao1():
    g = Grid(56, 30)
    g.rect(1, 1, 54, 2)
    g.clear(20, 0, 22, 2).door("N", 20, 22, "1")
    g.rect(1, 20, 54, 21)                     # piso do porão
    g.door("E", 16, 19, "2")
    # escada de carga de volta ao convés
    g.hline(24, 27, 17, "-").hline(17, 20, 14, "-").hline(24, 27, 11, "-").hline(17, 20, 8, "-")
    g.hline(21, 22, 5, "-").hline(20, 21, 3, "-")
    g.hline(8, 13, 7, "-")                    # prateleira alta ao lado da escada (caixas com moedas)
    g.rect(3, 18, 4, 19)                      # barris
    g.rect(41, 17, 42, 19)                    # pilha de caixotes no caminho
    g.clear(30, 20, 33, 21)                   # buraco no piso: cai na sentina
    g.clear(10, 21, 12, 21).hline(10, 12, 20, "-")      # alçapão de mão única (volta da sentina)
    # sentina: canal com tábuas podres, o amuleto no fundo e um esconderijo atrás da madeira rachada
    g.rect(1, 27, 54, 28)
    g.rect(14, 28, 25, 28, "~")
    g.hline(14, 18, 27, "C").hline(21, 25, 27, "C")    # tábuas (o meio, 19-20, é viga firme)
    g.hline(10, 12, 24, "-").hline(10, 12, 22, "-")    # degraus até o alçapão
    g.rect(44, 22, 44, 24).rect(44, 25, 44, 26, "X")
    g.put(3, 26, "*").put(50, 26, "*")
    g.put(8, 26, "j").put(38, 26, "g")
    g.put(9, 6, "k").put(12, 6, "k").put(7, 19, "k")
    g.put(26, 19, "g").put(47, 19, "g").put(51, 19, "k")    # nenhum rato no chão estreito entre o buraco e os caixotes
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
    # vigas do teto: a volta por cima, de leste para oeste
    g.hline(41, 46, 9, "-").hline(32, 37, 8, "C").hline(23, 28, 8, "-").hline(14, 19, 8, "-")
    # nicho sobre a entrada, fechado por madeira rachada: a carta 1
    g.rect(1, 8, 13, 9)
    g.rect(12, 3, 12, 5).rect(12, 6, 12, 7, "X")
    g.put(4, 7, "*").put(55, 9, "*").put(39, 16, "*")
    g.put(4, 19, "B")
    g.put(16, 7, "g").put(46, 13, "f")       # rato na viga firme (não logo depois das tábuas); gaivota no chão leste
    g.put(58, 19, "g").put(60, 19, "k").put(54, 19, "j")      # gosma longe do pouso da ilha B
    return g.rows()


def room_toca():
    g = Grid(40, 18)
    g.rect(1, 1, 38, 2)
    g.rect(1, 15, 38, 16)
    g.door("W", 11, 14, "1")
    g.rect(1, 11, 1, 14, "|")
    g.hline(6, 10, 12, "-").hline(29, 33, 12, "-").hline(17, 22, 10, "-")
    g.rect(19, 13, 20, 14)                    # barris no meio: a investida do rei bate e ele fica tonto
    g.put(28, 14, "G")
    return g.rows()


# ---------------------------------------------------------------------------
# Área 2 — Cordame (precisa da Levitação)
# ---------------------------------------------------------------------------

def room_cordame1():
    g = Grid(40, 40)
    g.clear(17, 39, 20, 39).door("S", 17, 20, "1")
    g.door("E", 1, 3, "2")
    g.hline(14, 23, 36, "-")                  # pouso sobre a escotilha
    g.rect(19, 14, 21, 31)                    # mastro
    g.rect(19, 23, 19, 24, "X").clear(20, 23, 20, 24)   # oco no mastro (rachado do lado oeste)
    # subida oeste: enfrechates (o caminho principal)
    g.hline(9, 14, 33, "-").hline(2, 7, 30, "-").hline(9, 13, 27, "C").hline(14, 18, 25, "-")
    g.hline(3, 8, 22, "-").hline(10, 15, 19, "-").hline(3, 7, 16, "-")
    g.hline(8, 31, 13, "-")                   # verga grande, por cima do mastro
    # lado leste (opcional): gaivotas, tábuas e a plataforma que balança até o amuleto
    g.hline(25, 30, 33, "-").hline(32, 37, 30, "-").hline(26, 30, 27, "C").hline(33, 37, 25, "-")
    g.hline(27, 33, 18, "-")
    # topo: até a saída das vergas
    g.hline(3, 8, 10, "-").hline(10, 15, 7, "-").hline(18, 22, 6, "C").hline(25, 28, 5, "-")
    g.rect(31, 4, 38, 4)
    g.put(20, 24, "*").put(36, 24, "*")
    g.put(24, 12, "g")
    g.put(36, 21, "f").put(26, 21, "f").put(13, 11, "f")      # gaivota acima do amuleto, não do pouso leste 2
    return g.rows()


def room_cordame2():
    g = Grid(60, 20)
    g.door("W", 12, 14, "1").door("E", 11, 14, "2")
    g.rect(1, 15, 10, 16)
    g.rect(1, 18, 58, 18, "~")                # o mar lá embaixo
    g.rect(48, 15, 58, 16)
    # rota do meio: verga, topo do mastro de proa, tábuas e a plataforma que vai e volta
    g.hline(13, 17, 13, "-")
    g.rect(21, 11, 23, 18)
    g.hline(27, 31, 11, "C").hline(32, 33, 11, "-")    # tábuas e um pedaço firme para esperar a plataforma
    # rota baixa, rente ao mar: destroços boiando (o amuleto do vento)
    g.rect(25, 16, 26, 17).rect(30, 16, 31, 17).rect(35, 16, 36, 17).rect(39, 16, 41, 17)
    # rota alta: corda e o cesto escondido no alto, à esquerda (carta 2)
    g.hline(14, 18, 8, "-").hline(3, 7, 5, "-")
    g.put(4, 4, "*").put(40, 15, "*")
    g.put(3, 14, "B").put(56, 14, "t")       # canhão no fundo: alcança só o fim da plataforma móvel
    g.put(16, 4, "f").put(43, 14, "f")       # gaivota guarda a rota alta, não as tábuas
    return g.rows()


def room_gavea():
    g = Grid(36, 20)
    g.rect(1, 17, 34, 18)
    g.door("W", 13, 16, "1")
    g.rect(1, 13, 1, 16, "|")
    g.hline(5, 9, 14, "-").hline(26, 30, 14, "-").hline(14, 21, 10, "-")
    g.rect(11, 16, 11, 16).rect(24, 16, 24, 16)    # barris amarrados: abrigo contra o vento do Aldric
    g.put(27, 16, "G")
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
    g.hline(25, 29, 13, "-")                  # copa do coqueiro: 5 acima (pulo duplo)
    # gruta dentro do penhasco, atrás da rocha rachada
    g.clear(37, 15, 53, 17).rect(36, 16, 36, 17, "X")
    # ninho no alto (opcional): do coqueiro, galhos até caixas esquecidas por contrabandistas
    g.hline(16, 20, 8, "-").hline(7, 11, 5, "-")
    g.put(8, 4, "k").put(10, 4, "k")
    g.put(27, 12, "*").put(51, 17, "*")
    g.put(4, 17, "B").put(45, 17, "k")
    g.put(10, 17, "j").put(31, 17, "g").put(33, 17, "k")
    g.put(48, 11, "c").put(54, 11, "g").put(44, 6, "f")       # goblin, lobo e diabrete no alto
    return g.rows()


def room_floresta():
    g = Grid(48, 40)
    g.rect(1, 37, 46, 38)
    g.door("W", 33, 36, "1").door("E", 2, 5, "2")
    g.hline(20, 46, 36, "^")                  # raízes com espinhos
    g.rect(19, 36, 19, 36)                    # tronco caído: a patrulha do lobo para aqui
    # caminho rápido (leste): galhos, tábuas e a plataforma que sobe
    g.hline(6, 11, 34, "-").hline(14, 19, 31, "-").hline(23, 28, 29, "C").hline(32, 37, 26, "-")
    g.hline(43, 46, 32, "-").hline(37, 39, 29, "-")    # galho baixo sobre os espinhos (amuleto)
    # caminho longo (oeste): galhos até a árvore oca
    g.hline(24, 29, 22, "-").hline(14, 19, 19, "-").hline(5, 10, 16, "-")
    g.rect(2, 8, 7, 13).clear(3, 9, 6, 12).rect(7, 11, 7, 12, "X")   # árvore oca (carta 3)
    g.hline(8, 12, 13, "-")
    g.hline(15, 20, 10, "-").hline(24, 29, 8, "-").hline(32, 35, 7, "-")
    g.hline(22, 26, 3, "-")                   # copa alta (fragmento)
    g.rect(38, 6, 46, 6)
    g.put(24, 2, "*").put(4, 12, "*").put(45, 31, "*")
    g.put(27, 21, "j").put(30, 16, "f").put(12, 22, "f")      # gosma no caminho longo, não no galho 2
    g.put(3, 36, "B").put(9, 36, "j").put(14, 36, "g")
    return g.rows()


def room_ruinas():
    g = Grid(40, 20)
    g.rect(1, 17, 38, 18)
    g.door("W", 13, 16, "1").door("E", 13, 16, "2")
    g.rect(1, 13, 1, 16, "|")
    g.rect(38, 13, 38, 16, "=")
    # arcos de pedra: abrigo do canhonaço da Selka (a bala explode em cima deles)
    g.rect(8, 12, 12, 12).rect(27, 12, 31, 12)
    g.hline(16, 23, 8, "-")
    g.put(30, 16, "G")
    return g.rows()


def room_templo():
    g = Grid(60, 22)
    g.rect(1, 18, 58, 20)
    g.door("W", 14, 17, "1").door("E", 14, 17, "2")
    g.hline(10, 46, 17, "^")
    g.rect(46, 17, 46, 17)                    # meio-fio: quem anda no chão leste não cai nos espinhos
    # travessia: pilares, pedras soltas e a plataforma que vai e volta
    g.rect(12, 15, 13, 17).hline(17, 19, 14, "C")
    g.rect(20, 14, 21, 14)                    # pedra firme: espera a plataforma sem a pedra ceder
    g.rect(34, 14, 35, 17).rect(40, 15, 41, 17)
    # galeria alta do lich e a câmara selada (amuleto)
    g.hline(30, 45, 9, "-").hline(18, 25, 8, "-")
    g.rect(5, 4, 17, 9).clear(7, 5, 16, 7).rect(17, 6, 17, 7, "X")
    g.put(9, 7, "*")
    g.put(3, 17, "B")
    g.put(52, 17, "c").put(56, 17, "s")
    g.put(38, 8, "t").put(28, 5, "f")                          # lich na galeria e espírito
    return g.rows()


def room_altar():
    g = Grid(44, 22)
    g.rect(1, 19, 42, 20)
    g.door("W", 15, 18, "1")
    g.rect(1, 15, 1, 18, "|")
    # plataformas sob as três posições do Caelum (para testar qual é a verdadeira) e acima da maré
    g.hline(6, 13, 16, "-").hline(30, 37, 16, "-").hline(18, 25, 11, "-")
    g.rect(20, 16, 23, 18)                    # altar: refúgio quando a maré sobe
    g.put(30, 18, "G")
    return g.rows()


ROOM_DEFS = [
    {"id": "cabine", "name": "Cabine de Nyra", "zone": "interior", "rows": room_cabine(), "items": [("coins", 15)]},
    {"id": "conves", "name": "Convés da Gaivota Rubra", "zone": "convés", "rows": room_conves(), "npcs": ["capita", "amigo"],
     "key": "atracado", "items": [("fragment", None), ("coins", 25)]},
    {"id": "porao1", "name": "Porão", "zone": "porão", "rows": room_porao1(),
     "items": [("charm", "lamina"), ("coins", 30)]},
    {"id": "porao2", "name": "Porão Alagado", "zone": "porão", "rows": room_porao2(),
     "items": [("letter", "carta1"), ("fragment", None), ("food", "peixe")],
     "movers": [{"x0": 18, "y0": 16, "x1": 26, "y1": 16, "w": 3, "speed": 90},
                {"x0": 47, "y0": 19, "x1": 47, "y1": 10, "w": 3, "speed": 70}]},
    {"id": "toca", "name": "Toca dos Ratos", "zone": "porão", "rows": room_toca(), "boss": "rei_rato"},
    {"id": "cordame1", "name": "Cordame", "zone": "convés", "rows": room_cordame1(),
     "items": [("coins", 25), ("charm", "coletor")],
     "movers": [{"x0": 23, "y0": 22, "x1": 30, "y1": 22, "w": 3, "speed": 90}]},
    {"id": "cordame2", "name": "Vergas", "zone": "convés", "rows": room_cordame2(),
     "items": [("letter", "carta2"), ("charm", "vento")],
     "movers": [{"x0": 36, "y0": 10, "x1": 43, "y1": 10, "w": 3, "speed": 95}]},
    {"id": "gavea", "name": "Cesto da Gávea", "zone": "convés", "rows": room_gavea(), "boss": "cavaleiro"},
    {"id": "praia", "name": "Praia de Velmora", "zone": "ilha", "rows": room_praia(),
     "items": [("food", "torta"), ("coins", 40)]},
    {"id": "floresta", "name": "Bosque dos Vaga-lumes", "zone": "ilha", "rows": room_floresta(),
     "items": [("fragment", None), ("letter", "carta3"), ("charm", "vigor")],
     "movers": [{"x0": 41, "y0": 25, "x1": 41, "y1": 11, "w": 3, "speed": 70}]},
    {"id": "ruinas", "name": "Ruínas de Velmora", "zone": "ruínas", "rows": room_ruinas(), "boss": "irma"},
    {"id": "templo", "name": "Templo da Maré", "zone": "templo", "rows": room_templo(), "items": [("charm", "forca")],
     "movers": [{"x0": 23, "y0": 13, "x1": 30, "y1": 13, "w": 3, "speed": 110}]},
    {"id": "altar", "name": "Altar da Maré", "zone": "templo", "rows": room_altar(), "boss": "feiticeiro"},
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
    "capita": {"name": "Capitã Maren", "style": "corpo", "prompt": "Examinar", "color": (40, 44, 70), "height": 18},
    "amigo": {"name": "Caelum", "style": "amigo", "color": (70, 120, 90), "height": 44},
}

DIALOGS = {
    "capita": {
        "first": [
            "A Capitã Maren está caída no convés. Os lábios estão arroxeados: veneno.",
            "Na mão dela, um bilhete amassado: \"O tônico... o Tico... no porão.\"",
        ],
        "repeat": ["Nyra promete a si mesma: vai descobrir quem fez isso."],
    },
    "amigo": {
        "first": [
            "Nyra?! Dez anos e você ainda esconde esses chifres debaixo do capuz.",
            "Sou eu, Caelum. Da academia, lembra? Viajo como passageiro, que nem você.",
            "Vi o Tico, o grumete, descer correndo pela escotilha. Os ratos lá embaixo estão... estranhos.",
            "Vai lá, feiticeira. Eu cuido do convés.",
        ],
        "repeat": ["O porão fica pela escotilha, perto do mastro. Cuidado com a água."],
    },
}

FLAG_MESSAGES = {
    "atracado": ("A Gaivota Rubra atracou", "A prancha do convés agora leva à ilha de Velmora."),
}

LETTERS = {
    "carta1": ("Diário da Capitã Maren (1/3)",
               "\"Gente do porto de Aurel some toda lua cheia. Todos embarcaram rumo a Velmora.\""),
    "carta2": ("Diário da Capitã Maren (2/3)",
               "\"Estão vivos, presos no Templo da Maré. Alguém quer acordar o que dorme lá embaixo.\""),
    "carta3": ("Diário da Capitã Maren (3/3)",
               "\"É Caelum, o mago banido da academia. Diz que levou a culpa de outra pessoa.\""),
}

# id -> classe em bosses.py, recompensa, falas de apresentação e de derrota
BOSSES = {
    "rei_rato": {
        "reward": ("ability", "double_jump"),
        "speaker": "grumete",
        "intro": "O tônico... disseram que ia acalmar a capitã! E agora os ratos me obedecem!",
        "after": [
            "Eu só queria não ser expulso do navio...",
            "Um homem de cachecol roxo me deu o tônico. Disse que era remédio.",
        ],
    },
    "cavaleiro": {
        "reward": ("fragment", None),
        "flag": "atracado",
        "speaker": "imediato",
        "intro": "Ele me prometeu a Gaivota Rubra! A armadura e o vento são o preço, e eu pago!",
        "after": [
            "A ambição me cegou. O navio está atracando em Velmora...",
            "O feiticeiro está no Templo da Maré. Os desaparecidos também.",
        ],
    },
    "irma": {
        "reward": None,
        "speaker": "irma",
        "intro": "Ele prendeu meu filho no templo. Os canhões da minha irmã vão te parar!",
        "after": [
            "Escondi o diário da Maren para proteger o meu menino...",
            "Vá, Nyra. Salve todos. E pare o Caelum... ele era seu amigo.",
        ],
    },
    "feiticeiro": {
        "reward": None,
        "speaker": "amigo",
        "intro": "Na academia, a ilusão que explodiu era sua. Eu levei a culpa e você ficou calada. "
                 "Agora a Maré vai engolir Aurel!",
        "after": [],
    },
}

ENDING_TRUE = [
    "Caelum cai de joelhos. A Maré se recolhe e as correntes do templo se partem.",
    "Os desaparecidos voltam para a Gaivota Rubra, vivos. A Capitã Maren acorda.",
    "Com o diário da capitã, Aurel ouve a história inteira: Tico, Aldric e Selka foram enganados.",
    "E Nyra, pela primeira vez, conta a verdade sobre a academia. Caelum não estava sozinho na culpa.",
    "Sem ilusões nem capuz, a feiticeira de chifres volta para casa.",
    "FINAL VERDADEIRO",
]
ENDING_NORMAL = [
    "Caelum cai de joelhos. A Maré se recolhe e as correntes do templo se partem.",
    "Os desaparecidos voltam para a Gaivota Rubra, vivos.",
    "Mas sem o diário da capitã, ninguém em Aurel acredita na história inteira...",
    "(Encontre as 3 páginas do diário para ver o final verdadeiro.)",
    "FIM",
]
