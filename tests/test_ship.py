"""Testes do mundo do jogo (navio, porão, cordame, ilha, templo): estrutura, portas,
alcance dos saltos por habilidade, mecânicas de parkour, chefes, itens e finais."""

import random

from helpers import SIM_DT, Sim, T, check, in_room, stands_on, try_reach
from src import chapter1
from src.bosses import PirateSister, RatKing, RedKnight, Sorcerer
from src.config import Progression
from src.physics import tile_span
from src.progress import Progress
from src.states import BossIntroState, DialogState, EndingState, ResultsState


def game(abilities=(), protagonist="ela", name="jogo.json", flags=()):
    pr = Progress()
    pr.chapter = 1
    pr.abilities = set(abilities)
    pr.protagonist = protagonist
    pr.flags = set(flags)
    return Sim(progress=pr, save_name=name)


def test_start_abilities():
    s = game(name="inicio.json")
    check("o dash já vem desde o começo", "dash" in s.p.abilities and "double_jump" not in s.p.abilities)
    check("o primeiro chefe dá o pulo duplo", chapter1.BOSSES["rei_rato"]["reward"] == ("ability", "double_jump"))


def test_water_returns_to_checkpoint():
    s = game(name="agua.json")
    s.pr.bench = None
    s.goto("porao2", 14, 18)
    s.play.enemies = []
    mover = s.play.movers[0]
    s.p.place(mover.x + mover.w / 2, mover.y)          # em cima da plataforma móvel
    s.step()
    s.play.riding = None
    s.p.place(30 * T, 21 * T - 4)                      # cai na água do canal
    s.p.vy = 200
    entry = s.play.room_entry
    for _ in range(int(3.0 / SIM_DT)):
        s.step()
        if s.play.hazard_timer <= 0 and s.p.hp < s.p.max_hp and s.p.on_ground:
            break
    check("cair na água volta ao chão firme da mesma sala (sem loop)",
          s.play.room.id == "porao2" and s.p.alive and entry is not None and abs(s.p.cx - entry[0]) < 4,
          s.play.room.id)
    hp = s.p.hp
    s.run(2.0)
    check("depois de voltar não toma dano de novo", s.p.hp == hp and s.play.hazard_timer <= 0)


def test_structure():
    s = game()
    w = s.play.world
    rooms = [r for r in w.rooms.values() if not r.id.startswith("L")]
    overlaps = [o for o in w.overlaps() if not (o[0].startswith("L") or o[1].startswith("L"))]
    check("mundo tem 13 salas sem sobreposição", len(rooms) == 13 and not overlaps, str(overlaps))
    unlinked = [(r.id, d) for r in rooms for d in r.doors if (r.id, d) not in w.links]
    check("toda porta tem destino", not unlinked, str(unlinked))
    check("novo jogo começa na cabine", s.play.room.id == "cabine")
    bosses = sorted(r.boss for r in rooms if r.boss)
    check("4 chefes no mundo", bosses == sorted(chapter1.BOSSES), str(bosses))
    letters = [it for r in rooms for it in r.items if it[0] == "letter"]
    check("3 cartas escondidas", len(letters) == 3)


def _overlaps_solid(s):
    p = s.p
    room = s.play.room
    x0, x1 = tile_span(p.x, p.w)
    y0, y1 = tile_span(p.y, p.h)
    return any(room.is_solid(tx, ty) for ty in range(y0, y1 + 1) for tx in range(x0, x1 + 1))


def test_doors():
    s = game(("dash", "double_jump"), flags=("atracado",))
    for r in s.play.world.rooms.values():
        r.door_unlocked = r.key is not None
        r.boss_defeated = bool(r.boss)
    bad = []
    for (rid, digit), (tid, _) in sorted(s.play.world.links.items()):
        if rid.startswith("L"):
            continue
        room = s.play.world.rooms[rid]
        door = room.doors[digit]
        ok = False
        for settle in ("left", "right"):
            s.play.load_room(room)
            s.play.enemies, s.play.items, s.play.boss = [], [], None
            p = s.p
            p.reset_state()
            p.invuln = 99
            held = set()
            if door.side == "W":
                p.x, p.y = 2.0, (door.hi + 1) * T - p.h
                held = {"left"}
            elif door.side == "E":
                p.x, p.y = room.width - p.w - 2.0, (door.hi + 1) * T - p.h
                held = {"right"}
            else:
                p.x = (door.lo + door.hi + 1) / 2 * T - p.w / 2
                if door.side == "N":
                    p.y, p.vy = 4.0, -700.0
                else:
                    p.y, p.vy = room.height - p.h - 4.0, 300.0
            arrived = s.wait_until(lambda: s.play.room.id == tid, 1.5, held=held)
            if not arrived or _overlaps_solid(s):
                continue
            stable = s.wait_until(lambda: s.p.on_ground, 1.5, held=held or {settle})
            if stable and s.play.room.id == tid and s.play.hazard_timer <= 0:
                ok = True
                break
        if not ok:
            bad.append(f"{rid}:{digit}->{tid}")
    check("todas as passagens funcionam nos dois sentidos", not bad, ", ".join(bad))


PATHS_NONE = [
    ("Cabine: cama", "cabine", 10, 14, stands_on("cabine", 11, 3, 8)),
    ("Cabine: prateleira", "cabine", 6, 11, stands_on("cabine", 8, 10, 15)),
    ("Convés: cordame 1", "conves", 26, 18, stands_on("conves", 15, 24, 28)),
    ("Convés: cordame 2", "conves", 26, 15, stands_on("conves", 12, 19, 23)),
    ("Convés: cordame 3", "conves", 21, 12, stands_on("conves", 9, 24, 28)),
    ("Convés: caixote da mezena", "conves", 41, 18, stands_on("conves", 16, 44, 45)),
    ("Convés: mezena 1", "conves", 45, 16, stands_on("conves", 14, 47, 51)),
    ("Convés: mezena 2", "conves", 50, 14, stands_on("conves", 11, 53, 57)),
    ("Convés: mezena 3", "conves", 56, 11, stands_on("conves", 8, 59, 64)),
    ("Porão 1: volta 1", "porao1", 28, 20, stands_on("porao1", 17, 24, 27)),
    ("Porão 1: volta 2", "porao1", 25, 17, stands_on("porao1", 14, 17, 20)),
    ("Porão 1: volta 3", "porao1", 18, 14, stands_on("porao1", 11, 24, 27)),
    ("Porão 1: volta 4", "porao1", 25, 11, stands_on("porao1", 8, 17, 20)),
    ("Porão 1: volta 5", "porao1", 18, 8, stands_on("porao1", 5, 21, 22)),
    ("Porão 1: volta 6", "porao1", 21, 5, stands_on("porao1", 3, 20, 21)),
    ("Porão 1: sobe ao convés", "porao1", 20, 3, in_room("conves")),
    ("Porão 1: prateleira alta", "porao1", 18, 8, stands_on("porao1", 7, 8, 13)),
    ("Porão 1: pula o buraco", "porao1", 28, 20, stands_on("porao1", 20, 34, 40)),
    ("Porão 1: caixotes", "porao1", 38, 20, stands_on("porao1", 20, 43, 54)),
    ("Porão 1: volta dos caixotes", "porao1", 45, 20, stands_on("porao1", 20, 34, 40)),
    ("Porão 1: degrau 1 do alçapão", "porao1", 8, 27, stands_on("porao1", 24, 10, 12)),
    ("Porão 1: degrau 2 do alçapão", "porao1", 11, 24, stands_on("porao1", 22, 10, 12)),
    ("Porão 1: sai pelo alçapão", "porao1", 11, 22, stands_on("porao1", 20, 10, 12)),
    ("Porão 2: ilha A", "porao2", 7, 20, stands_on("porao2", 18, 13, 15)),
    ("Porão 2: tábuas até a ilha B", "porao2", 33, 16, stands_on("porao2", 17, 38, 40)),
    ("Porão 2: chão leste", "porao2", 39, 17, stands_on("porao2", 20, 44, 62)),
    ("Porão 2: volta do chão leste", "porao2", 45, 20, stands_on("porao2", 17, 38, 40)),
    ("Porão 2: prateleira até a viga", "porao2", 52, 10, stands_on("porao2", 9, 41, 46)),
    ("Porão 2: viga 2 (tábuas)", "porao2", 42, 9, stands_on("porao2", 8, 32, 37)),
    ("Porão 2: viga 3", "porao2", 33, 8, stands_on("porao2", 8, 23, 28)),
    ("Porão 2: viga 4", "porao2", 24, 8, stands_on("porao2", 8, 14, 19)),
    ("Porão 2: nicho da carta", "porao2", 15, 8, stands_on("porao2", 8, 13, 13)),
    ("Porão 2: tábua podre do desafio", "porao2", 56, 10, stands_on("porao2", 7, 58, 61)),
    ("Porão 2: jirau do fragmento (desafio)", "porao2", 60, 7, stands_on("porao2", 5, 50, 55)),
    ("Toca: plataforma", "toca", 4, 15, stands_on("toca", 12, 6, 10)),
    ("Toca: barris", "toca", 15, 15, stands_on("toca", 13, 19, 20)),
    ("Toca: plataforma do meio", "toca", 19, 13, stands_on("toca", 10, 17, 22)),
]

PATHS_DASH = [
    ("Convés: verga do traquete (pulo + dash)", "conves", 25, 9, stands_on("conves", 7, 11, 15)),
    ("Toca: plataforma ao meio (dash)", "toca", 9, 12, stands_on("toca", 10, 17, 22)),
]

PATHS_DJ = [
    ("Convés: mastro (pulo duplo)", "conves", 26, 9, stands_on("conves", 4, 28, 36)),
    ("Convés: sobe ao cordame", "conves", 34, 4, in_room("cordame1")),
    ("Convés: cesto da mezena (pulo duplo)", "conves", 60, 8, stands_on("conves", 3, 51, 55)),
    ("Cordame: pouso", "cordame1", 15, 39, stands_on("cordame1", 36, 14, 23)),
    ("Cordame: oeste 1", "cordame1", 15, 36, stands_on("cordame1", 33, 9, 14)),
    ("Cordame: oeste 2", "cordame1", 10, 33, stands_on("cordame1", 30, 2, 7)),
    ("Cordame: oeste 3 (tábuas)", "cordame1", 6, 30, stands_on("cordame1", 27, 9, 13)),
    ("Cordame: oeste 4 (oco do mastro)", "cordame1", 11, 27, stands_on("cordame1", 25, 14, 18)),
    ("Cordame: oeste 5", "cordame1", 15, 25, stands_on("cordame1", 22, 3, 8)),
    ("Cordame: oeste 6", "cordame1", 7, 22, stands_on("cordame1", 19, 10, 15)),
    ("Cordame: oeste 7", "cordame1", 11, 19, stands_on("cordame1", 16, 3, 7)),
    ("Cordame: verga grande", "cordame1", 6, 16, stands_on("cordame1", 13, 8, 31)),
    ("Cordame: leste 1", "cordame1", 22, 36, stands_on("cordame1", 33, 25, 30)),
    ("Cordame: leste 2", "cordame1", 29, 33, stands_on("cordame1", 30, 32, 37)),
    ("Cordame: leste 3 (tábuas)", "cordame1", 33, 30, stands_on("cordame1", 27, 26, 30)),
    ("Cordame: amuleto", "cordame1", 29, 27, stands_on("cordame1", 25, 33, 37)),
    ("Cordame: leste, volta à verga", "cordame1", 30, 18, stands_on("cordame1", 13, 8, 31)),
    ("Cordame: topo 1", "cordame1", 9, 13, stands_on("cordame1", 10, 3, 8)),
    ("Cordame: topo 2", "cordame1", 7, 10, stands_on("cordame1", 7, 10, 15)),
    ("Cordame: topo 3 (tábuas)", "cordame1", 14, 7, stands_on("cordame1", 6, 18, 22)),
    ("Cordame: topo 4", "cordame1", 21, 6, stands_on("cordame1", 5, 25, 28)),
    ("Cordame: ponta", "cordame1", 27, 5, stands_on("cordame1", 4, 31, 38)),
    ("Vergas: verga", "cordame2", 6, 15, stands_on("cordame2", 13, 13, 17)),
    ("Vergas: mastro de proa", "cordame2", 16, 13, stands_on("cordame2", 11, 21, 23)),
    ("Vergas: tábuas", "cordame2", 23, 11, stands_on("cordame2", 11, 27, 33)),
    ("Vergas: tábuas até o pedaço firme", "cordame2", 23, 11, stands_on("cordame2", 11, 32, 33)),
    ("Vergas: corda", "cordame2", 15, 13, stands_on("cordame2", 8, 14, 18)),
    ("Vergas: cesto da carta 2", "cordame2", 15, 8, stands_on("cordame2", 5, 3, 7)),
    ("Vergas: destroço 1", "cordame2", 23, 11, stands_on("cordame2", 16, 25, 26)),
    ("Vergas: destroço 2", "cordame2", 26, 16, stands_on("cordame2", 16, 30, 31)),
    ("Vergas: destroço 3", "cordame2", 31, 16, stands_on("cordame2", 16, 35, 36)),
    ("Vergas: destroço do amuleto", "cordame2", 36, 16, stands_on("cordame2", 16, 39, 41)),
    ("Vergas: do destroço à plataforma leste", "cordame2", 41, 16, stands_on("cordame2", 15, 48, 58)),
    ("Gávea: plataforma", "gavea", 14, 17, stands_on("gavea", 14, 5, 9)),
    ("Gávea: plataforma alta", "gavea", 8, 14, stands_on("gavea", 10, 14, 21)),
    ("Praia: vala de espinhos", "praia", 12, 18, stands_on("praia", 18, 24, 35)),
    ("Praia: coqueiro (pulo duplo)", "praia", 24, 18, stands_on("praia", 13, 25, 29)),
    ("Praia: penhasco (pulo duplo)", "praia", 33, 18, stands_on("praia", 12, 36, 58)),
    ("Praia: galho do ninho", "praia", 27, 13, stands_on("praia", 8, 16, 20)),
    ("Praia: ninho (desafio)", "praia", 18, 8, stands_on("praia", 5, 7, 11)),
    ("Floresta: 1", "floresta", 4, 37, stands_on("floresta", 34, 6, 11)),
    ("Floresta: 2", "floresta", 9, 34, stands_on("floresta", 31, 14, 19)),
    ("Floresta: 3 (tábuas)", "floresta", 17, 31, stands_on("floresta", 29, 23, 28)),
    ("Floresta: 4", "floresta", 26, 29, stands_on("floresta", 26, 32, 37)),
    ("Floresta: galho do amuleto", "floresta", 35, 26, stands_on("floresta", 32, 43, 46)),
    ("Floresta: volta do amuleto", "floresta", 44, 32, stands_on("floresta", 29, 37, 39)),
    ("Floresta: volta do amuleto 2", "floresta", 38, 29, stands_on("floresta", 26, 32, 37)),
    ("Floresta: oeste 1", "floresta", 34, 26, stands_on("floresta", 22, 24, 29)),
    ("Floresta: oeste 2", "floresta", 26, 22, stands_on("floresta", 19, 14, 19)),
    ("Floresta: oeste 3", "floresta", 16, 19, stands_on("floresta", 16, 5, 10)),
    ("Floresta: árvore oca", "floresta", 8, 16, stands_on("floresta", 13, 8, 12)),
    ("Floresta: copa 1", "floresta", 10, 13, stands_on("floresta", 10, 15, 20)),
    ("Floresta: copa 2", "floresta", 17, 10, stands_on("floresta", 8, 24, 29)),
    ("Floresta: copa 3", "floresta", 27, 8, stands_on("floresta", 7, 32, 35)),
    ("Floresta: saída", "floresta", 34, 7, stands_on("floresta", 6, 38, 46)),
    ("Floresta: fragmento", "floresta", 26, 8, stands_on("floresta", 3, 22, 26)),
    ("Ruínas: arco", "ruinas", 14, 17, stands_on("ruinas", 12, 8, 12)),
    ("Ruínas: plataforma alta", "ruinas", 11, 12, stands_on("ruinas", 8, 16, 23)),
    ("Templo: pilar A", "templo", 8, 18, stands_on("templo", 15, 12, 13)),
    ("Templo: pedras soltas", "templo", 13, 15, stands_on("templo", 14, 17, 20)),
    ("Templo: pilar A à pedra firme", "templo", 13, 15, stands_on("templo", 14, 20, 21)),
    ("Templo: pedra firme à câmara", "templo", 21, 14, stands_on("templo", 8, 18, 25)),
    ("Templo: pilar B ao C", "templo", 35, 14, stands_on("templo", 15, 40, 41)),
    ("Templo: saída", "templo", 41, 15, stands_on("templo", 18, 47, 58)),
    ("Templo: galeria", "templo", 35, 14, stands_on("templo", 9, 30, 45)),
    ("Templo: torre 1 (pedras soltas)", "templo", 44, 9, stands_on("templo", 6, 48, 52)),
    ("Templo: torre 2 (cofre)", "templo", 50, 6, stands_on("templo", 3, 54, 57)),
    ("Templo: câmara selada", "templo", 31, 9, stands_on("templo", 8, 18, 25)),
    ("Altar: plataforma", "altar", 3, 19, stands_on("altar", 16, 6, 13)),
    ("Altar: altar", "altar", 17, 19, stands_on("altar", 16, 20, 23)),
    ("Altar: plataforma alta", "altar", 22, 16, stands_on("altar", 11, 18, 25)),
]

GATES = [
    ("sem pulo duplo não chega ao cordame", ("dash",), "conves", 26, 9, stands_on("conves", 4, 28, 36)),
    ("sem pulo duplo não chega ao cesto da mezena", ("dash",), "conves", 60, 8, stands_on("conves", 3, 51, 55)),
    ("sem pulo duplo não sobe o penhasco da praia", ("dash",), "praia", 33, 18, stands_on("praia", 12, 36, 58)),
    ("sem pulo duplo não sobe o coqueiro", ("dash",), "praia", 24, 18, stands_on("praia", 13, 25, 29)),
]


def _run(abilities, paths, label):
    s = game(abilities, name=f"alc_{label}.json")
    for name, room, tx, row, target in paths:
        s.play.world.rooms[room].crumbled.clear()
        res = try_reach(s, room, tx, row, target)
        check(f"alcançável ({label}): {name}", res is not None, res or "nenhuma sequência funcionou")


def test_reach_none():
    _run((), PATHS_NONE, "sem habilidades")


def test_reach_dash():
    _run(("dash",), PATHS_DASH, "dash")


def test_reach_double():
    _run(("dash", "double_jump"), PATHS_DJ, "dash + pulo duplo")


def test_gates():
    for name, abilities, room, tx, row, target in GATES:
        s = game(abilities, name="bloq.json")
        res = try_reach(s, room, tx, row, target)
        check(f"bloqueio: {name}", res is None, res or "")
    s = game(("dash", "double_jump"), name="prancha.json")
    conves = s.play.world.rooms["conves"]
    check("prancha para a ilha trancada até o navio atracar", conves.is_solid(70, 16))


# Plataformas móveis: (nome, habilidades, sala, índice, ponta, partida, alvo).
# "ponta" diz onde a plataforma está no começo da tentativa ("x0" ou "x1", parada 0,5 s ali).
# Partida (coluna, linha) = jogadora em chão firme esperando; None = jogadora em cima da plataforma.
def _riding(idx):
    return lambda s: s.play.riding is s.play.movers[idx]


MOVER_PATHS = [
    ("Porão 2: ilha A à plataforma", ("dash",), "porao2", 0, "x0", (14, 18), _riding(0)),
    ("Porão 2: plataforma às tábuas", ("dash",), "porao2", 0, "x1", None, stands_on("porao2", 16, 30, 35)),
    ("Porão 2: chão leste ao elevador", ("dash",), "porao2", 1, "x0", (46, 20), _riding(1)),
    ("Porão 2: elevador à prateleira", ("dash",), "porao2", 1, "x1", None, stands_on("porao2", 10, 51, 57)),
    ("Cordame: amuleto à plataforma", ("dash", "double_jump"), "cordame1", 0, "x1", (34, 25), _riding(0)),
    ("Cordame: plataforma à verga leste", ("dash", "double_jump"), "cordame1", 0, "x1", None,
     stands_on("cordame1", 18, 27, 33)),
    ("Vergas: pedaço firme à plataforma", ("dash", "double_jump"), "cordame2", 0, "x0", (33, 11), _riding(0)),
    ("Vergas: plataforma ao lado leste", ("dash", "double_jump"), "cordame2", 0, "x1", None,
     stands_on("cordame2", 15, 48, 58)),
    ("Floresta: galho ao elevador", ("dash", "double_jump"), "floresta", 0, "x0", (36, 26), _riding(0)),
    ("Floresta: elevador ao galho da copa", ("dash", "double_jump"), "floresta", 0, "x1", None,
     stands_on("floresta", 7, 32, 35)),
    ("Templo: pedra firme à plataforma", ("dash", "double_jump"), "templo", 0, "x0", (21, 14), _riding(0)),
    ("Templo: plataforma ao pilar B", ("dash", "double_jump"), "templo", 0, "x1", None,
     stands_on("templo", 14, 34, 35)),
]


def _mover_goto(s, idx, end):
    """Troca o goto da simulação: depois de pôr a jogadora no lugar, deixa a plataforma
    parada na ponta pedida (e, sem partida, põe a jogadora em cima dela)."""
    original = s.goto

    def goto(room_id, tile_x, floor_row, enemies=False, items=True, on_mover=False):
        original(room_id, tile_x, floor_row, enemies=enemies, items=items)
        m = s.play.movers[idx]
        half = m.period / 2
        m.t = (half - 0.25) if end == "x1" else (m.period - 0.25)
        m.x, m.y = m._pos(m.t)
        m.dx = m.dy = 0.0
        if on_mover:
            s.p.place(m.x + m.w / 2, m.y)
            s.p.vy = 0.0
            s.play.riding = m
            s.p.land_on_platform(s.play)
    return original, goto


def test_reach_movers():
    for name, abilities, room, idx, end, start, target in MOVER_PATHS:
        s = game(abilities, name="alc_plataformas.json")
        original, goto = _mover_goto(s, idx, end)
        if start is None:
            s.goto = lambda r, x, y, enemies=False, items=True: goto(r, x, y, enemies, items, on_mover=True)
            # partida qualquer em chão firme: a jogadora é posta em cima da plataforma logo depois
            tx, row = {"porao2": (5, 20), "cordame1": (16, 36), "cordame2": (5, 15),
                       "floresta": (4, 37), "templo": (5, 18)}[room]
        else:
            s.goto = goto
            tx, row = start
        res = try_reach(s, room, tx, row, target)
        s.goto = original
        check(f"alcançável (plataforma móvel): {name}", res is not None, res or "nenhuma sequência funcionou")


# Pousos estreitos logo depois de buraco, água ou tábuas: (sala, linha do chão, coluna inicial, final).
# Nenhum inimigo começa neles, para a jogadora não cair em cima de um (ou levar empurrão para o perigo).
NARROW_LANDINGS = [
    ("porao1", 20, 34, 40),      # depois do buraco do piso
    ("porao2", 8, 23, 28),       # viga logo depois das tábuas do teto
    ("porao2", 16, 30, 35),      # tábuas depois da plataforma móvel
    ("cordame1", 30, 32, 37),    # leste 2
    ("floresta", 31, 14, 19),    # galho 2
    ("templo", 14, 20, 21),      # pedra firme sobre os espinhos
]


def test_fair_landings():
    rows = {d["id"]: d["rows"] for d in chapter1.ROOM_DEFS}
    bad = []
    for room, row, c0, c1 in NARROW_LANDINGS:
        for y in range(max(0, row - 3), row):
            for x in range(c0 - 1, c1 + 2):
                if rows[room][y][x] in "gcjsfa":
                    bad.append(f"{room} ({x},{y})")
    check("nenhum inimigo começa num pouso estreito depois de perigo", not bad, ", ".join(bad))


# Inimigos que andam: precisam de chão logo abaixo e espaço livre no tile e acima (altura até 34 px).
GROUND_ENEMIES = "gcjsatkG"
SUPPORT = "#-C=X|D"


def test_enemies_not_in_walls():
    bad = []
    for d in chapter1.ROOM_DEFS:
        rows = d["rows"]
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch in GROUND_ENEMIES:
                    above = rows[y - 1][x]
                    below = rows[y + 1][x] if y + 1 < len(rows) else "#"
                    if above in "#X|=D" or below not in SUPPORT:
                        bad.append(f"{d['id']} {ch}({x},{y})")
                elif ch == "f":
                    if any(rows[y + dy][x + dx] in "#X" for dy in (-1, 0) for dx in (-1, 0, 1)):
                        bad.append(f"{d['id']} f({x},{y})")
    check("nenhum inimigo começa dentro de parede ou no ar", not bad, ", ".join(bad))


def test_enemy_mix():
    """Do navio ao templo, cada área tem combinações: atirador junto de outro inimigo."""
    rows = {d["id"]: "".join(d["rows"]) for d in chapter1.ROOM_DEFS}
    combos = [r for r, txt in rows.items() if "a" in txt and any(c in txt for c in "gcsjf")]
    check("atiradores em combinação nas 4 áreas",
          all(r in combos for r in ("porao1", "porao2", "cordame1", "cordame2", "praia", "floresta", "templo")),
          ", ".join(combos))


def test_enemy_variety():
    """No navio, no máximo 2 do ladino (capanga `c` e pistoleiro `a` usam o mesmo modelo) por sala;
    toda sala com inimigos mistura pelo menos 3 tipos."""
    many, few = [], []
    for d in chapter1.ROOM_DEFS:
        txt = "".join(d["rows"])
        if d["zone"] in ("interior", "convés", "porão") and txt.count("c") + txt.count("a") > 2:
            many.append(d["id"])
        if txt.count("s") > 1:
            many.append(d["id"] + " (escudo)")
        kinds = {ch for ch in txt if ch in "gcjsatf"}
        if kinds and len(kinds) < 3:
            few.append(d["id"])
    check("sem enxame do ladino (até 2 por sala no navio) nem do escudo (1 por sala)", not many, ", ".join(many))
    check("salas com inimigos misturam 3 tipos ou mais", not few, ", ".join(few))


def test_crumble():
    s = game(name="tabua.json")
    s.goto("porao1", 12, 27)
    room = s.play.room
    s.p.place(16 * T + 16, 27 * T)
    s.step()
    s.run(0.2)
    check("tábua começa a ceder quando pisada", bool(s.play.crumble_timers) or bool(room.crumbled))
    s.run(0.5)
    check("tábua desaba depois de um instante", any(k[1] == 27 for k in room.crumbled))
    s.goto("porao1", 8, 27)
    s.run(3.5)
    check("tábua volta depois", not room.crumbled)
    for start, held, done in ((27, "left", lambda p: p.right <= 14 * T), (12, "right", lambda p: p.left >= 26 * T)):
        s2 = game(name="tabua2.json")
        s2.goto("porao1", start, 27)
        s2.play.enemies = []
        ok = s2.wait_until(lambda: done(s2.p), 2.5, held={held})
        check(f"correndo dá para atravessar as tábuas da sentina ({held})", ok and s2.p.hp == s2.p.max_hp)


def test_movers():
    s = game(name="plataforma.json")
    s.goto("porao2", 14, 18)
    mover = s.play.movers[0]
    s.wait_until(lambda: abs(mover.x - (18 * T)) < 4, 8.0)
    s.p.place(mover.x + mover.w / 2, mover.y - 20)
    s.p.vy = 100
    landed = s.wait_until(lambda: s.play.riding is mover, 0.5)
    check("jogador pousa na plataforma móvel", landed)
    x0, px0 = mover.x, s.p.x
    s.run(1.5)
    check("plataforma carrega o jogador", s.play.riding is mover and abs((s.p.x - px0) - (mover.x - x0)) < 3,
          f"plataforma {mover.x - x0:.0f} px, jogador {s.p.x - px0:.0f} px")
    s.step({"jump"}, {"jump"})
    s.run(0.1, held={"jump"})
    check("pular sai da plataforma", s.play.riding is None and s.p.vy < 0)


def test_bosses():
    random.seed(5)
    specs = [("toca", RatKing, ["charge", "leap", "summon"], "Rat"),
             ("gavea", RedKnight, ["slash", "leap"], "Gust"),
             ("ruinas", PirateSister, ["pistol", "lunge", "cannon"], "CannonShot"),
             ("altar", Sorcerer, ["skulls", "lightning", "tele_out", "illusion"], "Illusion")]
    for room, cls, attacks, signature in specs:
        s = game(("dash", "double_jump"), name=f"chefe_{room}.json")
        r = s.play.world.rooms[room]
        floor = {"toca": 15, "gavea": 17, "ruinas": 17, "altar": 19}[room]
        start = {"gavea": 14}.get(room, 6)            # na gávea, começa depois do barril
        s.goto(room, start, floor, enemies=True)
        boss = s.play.boss
        check(f"{cls.name}: chefe da sala certa", isinstance(boss, cls))
        s.p.invuln = 99
        woke = s.wait_until(lambda: boss.awake, 4.0, held={"right"})
        check(f"{cls.name}: acorda, fecha a arena e se apresenta", woke and r.fight_active)
        seen = set()
        made = set()
        for _ in range(int(30 / SIM_DT)):
            s.step()
            s.p.invuln = 99
            seen.add(boss.state.replace("_tele", ""))
            made |= {type(h).__name__ for h in s.play.hazards} | {type(e).__name__ for e in s.play.enemies}
            if all(a in seen for a in attacks) and signature in made:
                break
        check(f"{cls.name}: usa todos os ataques", all(a in seen for a in attacks), str(sorted(seen)))
        check(f"{cls.name}: mecânica própria ({signature})", signature in made, str(sorted(made)))
        check(f"{cls.name}: fica dentro da arena", -2 <= boss.x and boss.right <= r.width + 2)
        # derrota
        boss.hp = 1
        boss.invulnerable = False
        if isinstance(boss, RedKnight):
            boss.powered = True
        for _ in range(6):
            s.play.hazards.clear()                     # vento/canhonaço não atrapalham o golpe final
            boss.state = "idle"
            boss.timer = 5
            boss.vx = boss.vy = 0
            side = 1 if boss.cx < r.width / 2 else -1      # ataca pelo lado com espaço
            fx = boss.cx + side * 34
            s.p.place(fx, s.play._floor_below(fx, boss.top))
            s.p.facing = -side
            aim = {"up"} if not boss.gravity else set()
            if not boss.gravity:
                # o feiticeiro flutua: desce para alcance de um golpe para cima
                boss.y = s.p.top - boss.h - 6
                boss.x = s.p.cx - boss.w / 2
            s.step(aim, {"attack_quick"})
            s.run(0.3, held=aim)
            if not boss.alive:
                break
        check(f"{cls.name}: pode ser derrotado", not boss.alive and room in s.pr.bosses)
        ending = False
        for _ in range(int(2.0 / SIM_DT)):
            s.play.fixed_update(SIM_DT, s.inp)
            if isinstance(s.app.state, EndingState):
                ending = True
                break
        info = chapter1.BOSSES[r.boss]
        if r.boss == "feiticeiro":
            check("chefe final leva ao desfecho", ending)
        else:
            if info["reward"]:
                kind, arg = info["reward"]
                has = (any(i.kind == kind and i.arg == arg for i in s.play.items) or arg in s.pr.abilities
                       or f"{room}:boss" in s.pr.collected)          # já pegou: o jogador estava em cima
                check(f"{cls.name}: recompensa aparece na arena", has)
            if info.get("flag"):
                check(f"{cls.name}: libera {info['flag']}", info["flag"] in s.pr.flags)


def test_items_and_letters():
    s = game(("dash", "double_jump"), name="itens.json")
    s.goto("porao2", 9, 8)
    got = s.wait_until(lambda: "carta1" in s.pr.letters, 1.5, held={"left"})
    check("pegar a carta registra o texto", got)
    s.goto("praia", 25, 13)
    s.p.hp = 2
    s.wait_until(lambda: "praia:1" in s.pr.collected, 1.0, held={"right"})
    check("comida recupera 2 corações", s.p.hp == 4)
    saved = Progress.load(s.save_path)
    check("cartas ficam salvas", saved is not None and "carta1" in saved.letters)


def test_secrets():
    s = game(("dash", "double_jump"), name="segredos.json")
    rooms = [r for r in s.play.world.rooms.values() if not r.id.startswith("L")]
    cracked = sorted(r.id for r in rooms if r.tiles_of({"X"}))
    check("paredes rachadas escondem segredos em várias salas", len(cracked) >= 5, ", ".join(cracked))
    frags = sum(1 for r in rooms for it in r.items if it[0] == "fragment")
    frags += sum(1 for b in chapter1.BOSSES.values() if b["reward"] and b["reward"][0] == "fragment")
    check("fragmentos espalhados fecham um coração inteiro", frags == Progression.FRAGMENTS_PER_HP, str(frags))
    s.goto("porao2", 13, 8)
    s.p.facing = -1
    s.step(set(), {"attack_quick"})
    s.run(0.4)
    check("golpe abre a madeira rachada do nicho da carta 1", bool(s.play.room.broken))
    ok = s.wait_until(lambda: "carta1" in s.pr.letters, 2.0, held={"left"})
    check("atrás da madeira rachada está a carta 1", ok)


# Paredes rachadas: (sala, coluna e linha do chão do lado de fora, direção da parede, chave do item atrás)
SECRETS = [
    ("porao1", 42, 27, "right", "porao1:1"),      # esconderijo da sentina
    ("porao2", 13, 8, "left", "porao2:1"),        # nicho da carta 1
    ("cordame1", 17, 25, "right", "cordame1:0"),  # oco do mastro
    ("praia", 34, 18, "right", "praia:2"),        # gruta do penhasco
    ("floresta", 9, 13, "left", "floresta:1"),    # árvore oca (carta 3)
    ("templo", 19, 8, "left", "templo:1"),        # câmara selada (amuleto)
]


def test_all_secrets():
    for room, tx, row, side, key in SECRETS:
        s = game(("dash", "double_jump"), name="segredos_todos.json", flags=("atracado",))
        s.goto(room, tx, row)
        s.p.facing = 1 if side == "right" else -1
        for _ in range(3):
            s.step(set(), {"attack_quick"})
            s.run(0.4)
        broke = bool(s.play.room.broken)
        got = s.wait_until(lambda: key in s.pr.collected, 3.0, held={side})
        check(f"segredo de {room}: golpe abre a parede e o item atrás é pego", broke and got,
              f"quebrou={broke}, pegou={got}")


def _floor_under(rows, x, y):
    """Primeira linha de apoio (chão, plataforma ou tábua) abaixo da coluna x, a partir da linha y."""
    for yy in range(y + 1, len(rows)):
        if rows[yy][x] in "#-C":
            return yy
    return None


def test_every_item_pickable():
    """Todo baú/item do mapa é pego andando no pouso logo abaixo dele (o pouso tem teste de alcance)."""
    bad = []
    for d in chapter1.ROOM_DEFS:
        rows = d["rows"]
        spots = [(x, y) for y, row in enumerate(rows) for x, ch in enumerate(row) if ch == "*"]
        for i, (x, y) in enumerate(spots):
            key = f"{d['id']}:{i}"
            if key in {sec[4] for sec in SECRETS}:
                continue                      # atrás de parede rachada: test_all_secrets
            s = game(("dash", "double_jump"), name="itens_todos.json", flags=("atracado",))
            floor = _floor_under(rows, x, y)
            ok = False
            for dx, held in ((-2, "right"), (2, "left"), (-1, "right"), (1, "left")):
                sx = x + dx
                if floor is None or rows[floor][sx] not in "#-C" or rows[floor - 1][sx] in "#X":
                    continue
                s.goto(d["id"], sx, floor)
                if s.wait_until(lambda: key in s.pr.collected, 1.0, held={held}):
                    ok = True
                    break
            if not ok:
                bad.append(f"{key} ({x},{y})")
    check("todo item do mapa pode ser pego do pouso embaixo dele", not bad, ", ".join(bad))


def test_endings():
    for letters, true_end in ((("carta1", "carta2", "carta3"), True), (("carta1",), False)):
        s = game(("dash", "double_jump"), name=f"final{len(letters)}.json")
        s.pr.letters = set(letters)
        s.play.load_room(s.play.world.rooms["altar"])
        st = EndingState(s.app, s.play)
        s.app.push(st)
        check(f"final {'verdadeiro' if true_end else 'comum'} com {len(letters)} carta(s)",
              st.true_ending == true_end)
        for _ in range(40):
            if not isinstance(s.app.state, EndingState):
                break
            s.app.state.typed = 999
            s.inp.pressed.add("menu_confirm")
            s.app.state.frame(1 / 60, s.inp)
            s.app.state.draw(s.app.screen)
        check("desfecho termina na tela de resultado", isinstance(s.app.state, ResultsState))
        rs = s.app.state
        rs.draw(s.app.screen)
        check("resultado calcula nota", rs.grade in "SABC" and rs.score >= 0, f"nota {rs.grade}, {rs.score} pts")


def test_dialogs_and_npcs():
    s = game(protagonist="ela", name="falas.json")
    s.goto("conves", 30, 18)
    s.inp.pressed.add("interact")
    s.play.fixed_update(SIM_DT, s.inp)
    s.inp.consume()
    st = s.app.state
    check("W perto do amigo abre o diálogo", isinstance(st, DialogState) and st.character.char_id == "amigo")
    check("fala usa a forma feminina", any("feiticeira" in line for line in st.lines))
    st.draw(s.app.screen)
    s.app.resume(s.play)


def test_render_all():
    for prot in ("ela",):
        s = game(("dash", "double_jump"), protagonist=prot, name=f"desenho_{prot}.json")
        for rid, room in list(s.play.world.rooms.items()):
            if rid.startswith("L"):
                continue
            s.play.load_room(room)
            s.run(0.2)
            s.play.draw(s.app.screen)
    check("todas as salas desenham com a protagonista", True)


TESTS = [test_start_abilities, test_water_returns_to_checkpoint, test_structure, test_doors, test_crumble, test_movers, test_items_and_letters, test_secrets, test_all_secrets, test_every_item_pickable, test_fair_landings, test_enemies_not_in_walls,
         test_enemy_mix, test_enemy_variety, test_dialogs_and_npcs,
         test_endings, test_bosses, test_render_all, test_gates, test_reach_none, test_reach_dash, test_reach_double,
         test_reach_movers]
