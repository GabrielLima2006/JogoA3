"""Testes do mundo do jogo (navio, porão, cordame, ilha, templo): estrutura, portas,
alcance dos saltos por habilidade, mecânicas de parkour, chefes, itens e finais."""

import random

from helpers import SIM_DT, Sim, T, check, in_room, stands_on, try_reach
from src import chapter1
from src.bosses import PirateSister, RatKing, RedKnight, Sorcerer
from src.physics import tile_span
from src.progress import Progress
from src.states import BossIntroState, DialogState, EndingState, ResultsState


def game(abilities=(), protagonist="ele", name="jogo.json", flags=()):
    pr = Progress()
    pr.chapter = 1
    pr.abilities = set(abilities)
    pr.protagonist = protagonist
    pr.flags = set(flags)
    return Sim(progress=pr, save_name=name)


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
    ("Convés: cordame 1", "conves", 26, 18, stands_on("conves", 15, 24, 28)),
    ("Convés: cordame 2", "conves", 26, 15, stands_on("conves", 12, 19, 23)),
    ("Convés: cordame 3", "conves", 21, 12, stands_on("conves", 9, 24, 28)),
    ("Convés: cordame 4", "conves", 26, 9, stands_on("conves", 6, 19, 23)),
    ("Porão 1: volta 1", "porao1", 28, 20, stands_on("porao1", 17, 24, 27)),
    ("Porão 1: volta 2", "porao1", 25, 17, stands_on("porao1", 14, 17, 20)),
    ("Porão 1: volta 3", "porao1", 18, 14, stands_on("porao1", 11, 24, 27)),
    ("Porão 1: volta 4", "porao1", 25, 11, stands_on("porao1", 8, 17, 20)),
    ("Porão 1: volta 5", "porao1", 18, 8, stands_on("porao1", 5, 21, 22)),
    ("Porão 1: volta 6", "porao1", 21, 5, stands_on("porao1", 3, 20, 21)),
    ("Porão 1: sobe ao convés", "porao1", 20, 3, in_room("conves")),
    ("Porão 1: poça", "porao1", 32, 20, stands_on("porao1", 20, 38, 44)),
    ("Porão 2: ilha A", "porao2", 7, 20, stands_on("porao2", 18, 13, 15)),
    ("Porão 2: tábuas até a ilha B", "porao2", 33, 16, stands_on("porao2", 17, 38, 40)),
    ("Porão 2: chão leste", "porao2", 39, 17, stands_on("porao2", 20, 44, 62)),
    ("Porão 2: volta do chão leste", "porao2", 45, 20, stands_on("porao2", 17, 38, 40)),
    ("Toca: plataforma", "toca", 4, 15, stands_on("toca", 12, 7, 11)),
]

PATHS_DASH = [
    ("Convés: salto do mastro (dash)", "conves", 22, 6, stands_on("conves", 4, 31, 36)),
    ("Convés: sobe ao cordame", "conves", 34, 4, in_room("cordame1")),
    ("Cordame: 1", "cordame1", 15, 39, stands_on("cordame1", 36, 8, 13)),
    ("Cordame: 2 (dash)", "cordame1", 10, 36, stands_on("cordame1", 33, 21, 25)),
    ("Cordame: 3", "cordame1", 22, 33, stands_on("cordame1", 30, 30, 35)),
    ("Cordame: 4 (tábuas)", "cordame1", 31, 30, stands_on("cordame1", 27, 22, 26)),
    ("Cordame: 5", "cordame1", 23, 27, stands_on("cordame1", 24, 12, 17)),
    ("Cordame: 7", "cordame1", 33, 18, stands_on("cordame1", 15, 22, 26)),
    ("Cordame: 8", "cordame1", 23, 15, stands_on("cordame1", 12, 12, 16)),
    ("Cordame: 9", "cordame1", 13, 12, stands_on("cordame1", 9, 4, 8)),
    ("Cordame: 10", "cordame1", 5, 9, stands_on("cordame1", 6, 12, 15)),
    ("Cordame: 11", "cordame1", 13, 6, stands_on("cordame1", 4, 20, 24)),
    ("Cordame: ponta", "cordame1", 21, 4, stands_on("cordame1", 4, 31, 38)),
    ("Vergas: verga", "cordame2", 6, 15, stands_on("cordame2", 13, 13, 16)),
    ("Vergas: mastro (dash)", "cordame2", 14, 13, stands_on("cordame2", 14, 24, 26)),
    ("Vergas: tábuas", "cordame2", 25, 14, stands_on("cordame2", 14, 29, 34)),
    ("Gávea: plataforma", "gavea", 14, 17, stands_on("gavea", 14, 5, 9)),
]

PATHS_DJ = [
    ("Vergas: carta 2 (pulo duplo)", "cordame2", 25, 14, stands_on("cordame2", 8, 29, 32)),
    ("Praia: vala de espinhos", "praia", 12, 18, stands_on("praia", 18, 23, 35)),
    ("Praia: penhasco (pulo duplo)", "praia", 33, 18, stands_on("praia", 12, 36, 58)),
    ("Floresta: 1", "floresta", 4, 37, stands_on("floresta", 32, 6, 11)),
    ("Floresta: 2", "floresta", 9, 32, stands_on("floresta", 28, 16, 20)),
    ("Floresta: 3 (tábuas)", "floresta", 18, 28, stands_on("floresta", 25, 25, 30)),
    ("Floresta: 4", "floresta", 28, 25, stands_on("floresta", 21, 35, 40)),
    ("Floresta: 6", "floresta", 32, 10, stands_on("floresta", 8, 20, 24)),
    ("Floresta: carta 3", "floresta", 22, 8, stands_on("floresta", 5, 8, 13)),
    ("Floresta: saída", "floresta", 32, 10, stands_on("floresta", 6, 38, 46)),
    ("Ruínas: plataforma", "ruinas", 14, 17, stands_on("ruinas", 12, 6, 11)),
    ("Ruínas: plataforma alta", "ruinas", 9, 12, stands_on("ruinas", 8, 16, 23)),
    ("Templo: 1", "templo", 8, 18, stands_on("templo", 15, 11, 14)),
    ("Templo: 2 (tábuas)", "templo", 12, 15, stands_on("templo", 14, 19, 23)),
    ("Templo: saída", "templo", 40, 15, stands_on("templo", 18, 47, 58)),
    ("Altar: plataforma", "altar", 12, 19, stands_on("altar", 14, 6, 11)),
    ("Altar: plataforma alta", "altar", 9, 14, stands_on("altar", 10, 17, 26)),
]

GATES = [
    ("sem dash não chega ao cordame", (), "conves", 21, 6, stands_on("conves", 4, 31, 36)),
    ("sem dash não sobe do degrau 3 ao topo", (), "conves", 26, 9, stands_on("conves", 4, 31, 36)),
    ("sem pulo duplo não sobe o penhasco da praia", ("dash",), "praia", 33, 18, stands_on("praia", 12, 36, 58)),
    ("sem pulo duplo não pega a carta das vergas", ("dash",), "cordame2", 25, 14, stands_on("cordame2", 8, 29, 32)),
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


def test_crumble():
    s = game(name="tabua.json")
    s.goto("porao1", 43, 20)
    room = s.play.room
    s.p.place(46 * T + 16, 20 * T)
    s.step()
    s.run(0.2)
    check("tábua começa a ceder quando pisada", bool(s.play.crumble_timers) or bool(room.crumbled))
    s.run(0.5)
    check("tábua desaba depois de um instante", any(k[1] == 20 for k in room.crumbled))
    s.goto("porao1", 40, 20)
    s.run(3.5)
    check("tábua volta depois", not room.crumbled)
    s2 = game(name="tabua2.json")
    s2.goto("porao1", 42, 20)
    s2.play.enemies = []
    ok = s2.wait_until(lambda: s2.p.left >= 51 * T, 2.0, held={"right"})
    check("correndo dá para atravessar as tábuas antes de caírem", ok and s2.p.hp == s2.p.max_hp)


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
    specs = [("toca", RatKing, ["charge", "leap", "summon"]),
             ("gavea", RedKnight, ["slash", "leap"]),
             ("ruinas", PirateSister, ["pistol", "lunge", "bomb"]),
             ("altar", Sorcerer, ["skulls", "lightning", "tele_out"])]
    for room, cls, attacks in specs:
        s = game(("dash", "double_jump"), name=f"chefe_{room}.json")
        r = s.play.world.rooms[room]
        floor = {"toca": 15, "gavea": 17, "ruinas": 17, "altar": 19}[room]
        s.goto(room, 6, floor, enemies=True)
        boss = s.play.boss
        check(f"{cls.name}: chefe da sala certa", isinstance(boss, cls))
        s.p.invuln = 99
        woke = s.wait_until(lambda: boss.awake, 4.0, held={"right"})
        check(f"{cls.name}: acorda, fecha a arena e se apresenta", woke and r.fight_active)
        seen = set()
        for _ in range(int(25 / SIM_DT)):
            s.step()
            s.p.invuln = 99
            seen.add(boss.state.replace("_tele", ""))
            if all(a in seen for a in attacks):
                break
        check(f"{cls.name}: usa todos os ataques", all(a in seen for a in attacks), str(sorted(seen)))
        check(f"{cls.name}: fica dentro da arena", -2 <= boss.x and boss.right <= r.width + 2)
        # derrota
        boss.hp = 1
        boss.invulnerable = False
        if isinstance(boss, RedKnight):
            boss.powered = True
        for _ in range(6):
            boss.state = "idle"
            boss.timer = 5
            boss.vx = boss.vy = 0
            fx = boss.cx - 34
            s.p.place(fx, s.play._floor_below(fx, boss.top))
            s.p.facing = 1
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
                has = any(i.kind == kind and i.arg == arg for i in s.play.items) or arg in s.pr.abilities
                check(f"{cls.name}: recompensa aparece na arena", has)
            if info.get("flag"):
                check(f"{cls.name}: libera {info['flag']}", info["flag"] in s.pr.flags)


def test_items_and_letters():
    s = game(("dash", "double_jump"), name="itens.json")
    s.goto("porao2", 52, 10)
    got = s.wait_until(lambda: "carta1" in s.pr.letters, 1.5, held={"right"})
    check("pegar a carta registra o texto", got)
    s.goto("praia", 24, 18)
    s.p.hp = 2
    s.wait_until(lambda: "praia:0" in s.pr.collected, 1.0, held={"right"})
    check("comida recupera 2 corações", s.p.hp == 4)
    saved = Progress.load(s.save_path)
    check("cartas ficam salvas", saved is not None and "carta1" in saved.letters)


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
    for prot in ("ele", "ela"):
        s = game(("dash", "double_jump"), protagonist=prot, name=f"desenho_{prot}.json")
        for rid, room in list(s.play.world.rooms.items()):
            if rid.startswith("L"):
                continue
            s.play.load_room(room)
            s.run(0.2)
            s.play.draw(s.app.screen)
    check("todas as salas desenham com os dois protagonistas", True)


TESTS = [test_structure, test_doors, test_crumble, test_movers, test_items_and_letters, test_dialogs_and_npcs,
         test_endings, test_bosses, test_render_all, test_gates, test_reach_none, test_reach_dash, test_reach_double]
