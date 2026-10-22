"""Testes do navio (capítulo 1): salas, portas, alcance, porta trancada, personagens e diálogos."""

from helpers import SIM_DT, Sim, T, check, in_room, stands_on, try_reach
from src import chapter1
from src.physics import tile_span
from src.progress import Progress
from src.states import DialogState, MessageState


def ship(abilities=(), protagonist="ele", name="navio.json"):
    pr = Progress()
    pr.chapter = 1
    pr.abilities = set(abilities)
    pr.protagonist = protagonist
    return Sim(progress=pr, save_name=name)


def test_ship_structure():
    s = ship()
    w = s.play.world
    ship_rooms = [r for r in w.rooms.values() if not r.id.startswith("L")]
    overlaps = [o for o in w.overlaps() if not (o[0].startswith("L") or o[1].startswith("L"))]
    check("navio tem 9 salas sem sobreposição no mapa", len(ship_rooms) == 9 and not overlaps, str(overlaps))
    unlinked = [(r.id, d) for r in ship_rooms for d in r.doors if (r.id, d) not in w.links]
    check("toda porta do navio tem destino", not unlinked, str(unlinked))
    check("novo jogo começa na proa", s.play.room.id == "proa")
    npcs = {cid for r in ship_rooms for cid in r.npcs}
    check("os 6 personagens do capítulo estão no navio", npcs == set(chapter1.CHARACTERS), str(sorted(npcs)))


def _overlaps_solid(s):
    p = s.p
    room = s.play.room
    x0, x1 = tile_span(p.x, p.w)
    y0, y1 = tile_span(p.y, p.h)
    return any(room.is_solid(tx, ty) for ty in range(y0, y1 + 1) for tx in range(x0, x1 + 1))


def test_ship_doors():
    s = ship(("dash",))
    s.pr.flags.add("chave_cabine")
    s.play.world.rooms["salao"].door_unlocked = True
    bad = []
    for (rid, digit), (tid, _) in sorted(s.play.world.links.items()):
        room = s.play.world.rooms[rid]
        door = room.doors[digit]
        ok = False
        for settle in ("left", "right"):
            s.play.load_room(room)
            s.play.enemies, s.play.items = [], []
            p = s.p
            p.reset_state()
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
    check("todas as passagens do navio funcionam nos dois sentidos", not bad, ", ".join(bad))


PATHS = [
    ("Convés: cordame 1", "conves", 18, 15, stands_on("conves", 12, 20, 23)),
    ("Convés: cordame 2", "conves", 21, 12, stands_on("conves", 9, 25, 28)),
    ("Convés: cordame 3", "conves", 26, 9, stands_on("conves", 6, 20, 23)),
    ("Convés: cordame 4", "conves", 21, 6, stands_on("conves", 3, 24, 27)),
    ("Convés: sobe para a gávea", "conves", 25, 3, in_room("gavea")),
    ("Gávea: 1", "gavea", 6, 29, stands_on("gavea", 26, 5, 9)),
    ("Gávea: 2", "gavea", 7, 26, stands_on("gavea", 23, 13, 17)),
    ("Gávea: 3", "gavea", 15, 23, stands_on("gavea", 20, 5, 9)),
    ("Gávea: 4", "gavea", 7, 20, stands_on("gavea", 17, 13, 17)),
    ("Gávea: 5", "gavea", 15, 17, stands_on("gavea", 14, 5, 9)),
    ("Gávea: 6", "gavea", 7, 14, stands_on("gavea", 11, 13, 17)),
    ("Gávea: 7", "gavea", 15, 11, stands_on("gavea", 8, 5, 9)),
    ("Gávea: cesto", "gavea", 7, 8, stands_on("gavea", 5, 8, 16)),
    ("Tombadilho: leme", "tombadilho", 14, 15, stands_on("tombadilho", 12, 1, 10)),
    ("Salão: escada 1", "salao", 25, 15, stands_on("salao", 12, 19, 22)),
    ("Salão: escada 2", "salao", 20, 12, stands_on("salao", 9, 13, 16)),
    ("Salão: escada 3", "salao", 14, 9, stands_on("salao", 6, 19, 22)),
    ("Salão: escada 4", "salao", 20, 6, stands_on("salao", 4, 16, 17)),
    ("Salão: sobe para o convés", "salao", 16, 4, in_room("conves")),
    ("Porão: 1", "porao", 14, 16, stands_on("porao", 13, 9, 12)),
    ("Porão: 2", "porao", 10, 13, stands_on("porao", 10, 3, 6)),
    ("Porão: 3", "porao", 4, 10, stands_on("porao", 7, 9, 12)),
    ("Porão: 4", "porao", 10, 7, stands_on("porao", 4, 6, 7)),
    ("Porão: sobe para a cozinha", "porao", 6, 4, in_room("cozinha")),
]


def test_ship_reach():
    s = ship(())
    for name, room, tx, row, target in PATHS:
        res = try_reach(s, room, tx, row, target)
        check(f"alcançável no navio: {name}", res is not None, res or "nenhuma sequência funcionou")
    res = try_reach(s, "porao", 18, 16, stands_on("porao", 16, 29, 48))
    check("sem Passo ilusório não cruza o trecho alagado do porão", res is None, res or "")
    s2 = ship(("dash",))
    res = try_reach(s2, "porao", 18, 16, stands_on("porao", 16, 29, 48))
    check("com Passo ilusório cruza o trecho alagado (ida)", res is not None, res or "")
    res = try_reach(s2, "porao", 30, 16, stands_on("porao", 16, 1, 19))
    check("com Passo ilusório cruza o trecho alagado (volta)", res is not None, res or "")


def _talk(s, room_id, tile_x, floor_row):
    s.goto(room_id, tile_x, floor_row)
    s.inp.pressed.add("interact")
    s.play.fixed_update(SIM_DT, s.inp)
    s.inp.consume()
    return s.app.state


def _finish_dialog(s):
    lines = list(s.app.state.lines)
    for _ in range(50):
        if not isinstance(s.app.state, DialogState):
            break
        s.app.state.typed = 9999
        s.app.state.t = 1
        s.inp.pressed.add("menu_confirm")
        s.app.state.frame(1 / 60, s.inp)
    return lines


def test_dialogs():
    s = ship(protagonist="ela", name="dialogos.json")
    spots = {"imediato": ("tombadilho", 7, 12), "amigo": ("proa", 13, 15), "cozinheira": ("cozinha", 16, 15),
             "grumete": ("alojamento", 26, 15), "irma": ("gavea", 12, 5)}
    for cid, (room, tx, row) in spots.items():
        st = _talk(s, room, tx, row)
        ok = isinstance(st, DialogState) and st.character.char_id == cid
        lines = _finish_dialog(s) if ok else []
        expected = [line.format(**s.play.forms()) for line in chapter1.DIALOGS[cid]["first"]]
        check(f"W perto de {cid} abre o diálogo completo", ok and lines == expected)
        check(f"conversa com {cid} fica registrada", cid in s.pr.talked)
        st = _talk(s, room, tx, row)
        again = _finish_dialog(s) if isinstance(st, DialogState) else []
        check(f"segunda conversa com {cid} usa a fala curta", len(again) == len(chapter1.DIALOGS[cid]["repeat"]))
    forms = s.play.forms()
    check("falas usam a forma do protagonista escolhido (feiticeira)",
          any("feiticeira" in line.format(**forms) for line in chapter1.DIALOGS["imediato"]["first"]))
    s.goto("proa", 13, 15)
    friend = next(o for o in s.play.interactables if o.kind == "talk")
    s.app.push(DialogState(s.app, s.play, friend, ["teste de desenho"]))
    s.app.state.draw(s.app.screen)
    s.app.resume(s.play)


def test_locked_cabin():
    s = ship(name="chave.json")
    salao = s.play.world.rooms["salao"]
    check("porta da cabine começa trancada", salao.is_solid(1, 12))
    s.goto("salao", 4, 15)
    s.wait_until(lambda: s.play.room.id == "cabine", 1.0, held={"left"})
    check("trancada: não dá para entrar na cabine", s.play.room.id == "salao")
    st = _talk(s, "salao", 13, 15)
    check("examinar a capitã abre o texto da cena", isinstance(st, DialogState) and st.character.char_id == "capita")
    _finish_dialog(s)
    check("chave entregue ao terminar de examinar",
          "chave_cabine" in s.pr.flags and isinstance(s.app.state, MessageState))
    s.app.resume(s.play)
    check("porta da cabine destrancada", not salao.is_solid(1, 12))
    s.goto("salao", 4, 15)
    ok = s.wait_until(lambda: s.play.room.id == "cabine", 1.5, held={"left"})
    check("com a chave, entra na cabine da capitã", ok)
    saved = Progress.load(s.save_path)
    check("chave fica salva", saved is not None and "chave_cabine" in saved.flags)
    s2 = Sim(progress=saved, save_name="chave2.json")
    check("ao continuar, a porta continua aberta", not s2.play.world.rooms["salao"].is_solid(1, 12))


def test_trunk_and_render():
    s = ship(name="bau.json")
    s.goto("proa", 34, 15)
    got = s.wait_until(lambda: "dash" in s.pr.abilities, 1.0, held={"right"})
    check("baú de truques na cabine dá o Passo ilusório", got)
    for room in list(s.play.world.rooms.values()):
        s.play.load_room(room)
        s.play.fade = 0
        s.play.draw(s.app.screen)
    check("todas as salas do navio desenham sem erro", True)


TESTS = [test_ship_structure, test_ship_doors, test_locked_cabin, test_dialogs, test_trunk_and_render,
         test_ship_reach]
