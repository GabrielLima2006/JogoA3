"""Testes do mundo e da progressão: portas, alcance dos saltos por habilidade,
itens, moedas, energia/cura, banco, loja, ferreiro, segredos, inimigos novos,
chefe, save, mapa e telas."""

import os
import random

from helpers import SIM_DT, Sim, T, check, in_room, stands_on, try_reach
from src.config import Combat, Energy, Progression
from src.enemies import Flier, Jumper, Patroller, Shield
from src.physics import tile_span
from src.progress import Progress
from src.states import BenchState, MapState, PauseState, PlayState, ShopState
from src.world import WorldMap


# ---------------------------------------------------------------------------
# Estrutura do mundo
# ---------------------------------------------------------------------------

def test_world_structure():
    w = WorldMap()
    check("salas não se sobrepõem no mapa-múndi", not w.overlaps(), str(w.overlaps()))
    unlinked = [(r.id, d) for r in w.rooms.values() for d in r.doors if (r.id, d) not in w.links]
    check("toda porta tem destino", not unlinked, str(unlinked))
    check(f"{len(w.rooms)} salas no mundo", len(w.rooms) >= 12)
    benches = w.benches()
    check("há bancos em zonas diferentes", len({w.rooms[b[0]].zone for b in benches}) >= 3, str(benches))


def _overlaps_solid(s):
    p = s.p
    room = s.play.room
    x0, x1 = tile_span(p.x, p.w)
    y0, y1 = tile_span(p.y, p.h)
    return any(room.is_solid(tx, ty) for ty in range(y0, y1 + 1) for tx in range(x0, x1 + 1))


def test_all_doors():
    s = Sim()
    bad = []
    for (rid, digit), (tid, _) in sorted(s.play.world.links.items()):
        room = s.play.world.rooms[rid]
        door = room.doors[digit]
        ok = False
        for settle in ("left", "right"):
            s.play.load_room(room)
            s.play.enemies, s.play.boss, s.play.items = [], None, []
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
            # depois de chegar, consegue se firmar na sala nova sem cair de volta
            hold = held or {settle}
            stable = s.wait_until(lambda: s.p.on_ground, 1.5, held=hold)
            if stable and s.play.room.id == tid and s.play.hazard_timer <= 0:
                ok = True
                break
        if not ok:
            bad.append(f"{rid}:{digit}->{tid}")
    check("todas as portas levam à sala certa e o jogador se firma do outro lado", not bad, ", ".join(bad))


# ---------------------------------------------------------------------------
# Alcance dos saltos conforme a progressão
# ---------------------------------------------------------------------------

PATHS_NONE = [
    ("Entrada: beirada alta", "A", 28, 17, stands_on("A", 14, 30, 34)),
    ("Entrada: fosso pequeno", "A", 20, 17, stands_on("A", 17, 26, 43)),
    ("Vila: escada 1", "B", 6, 24, stands_on("B", 21, 4, 8)),
    ("Vila: escada 2", "B", 6, 21, stands_on("B", 18, 10, 14)),
    ("Vila: escada 3", "B", 12, 18, stands_on("B", 15, 4, 8)),
    ("Vila: escada 4", "B", 6, 15, stands_on("B", 12, 6, 10)),
    ("Vila: poço 1", "B", 8, 12, stands_on("B", 9, 3, 6)),
    ("Vila: poço 2", "B", 4, 9, stands_on("B", 6, 6, 8)),
    ("Vila: poço 3", "B", 7, 6, stands_on("B", 3, 3, 5)),
    ("Vila: sobe para os Túneis", "B", 4, 3, in_room("C")),
    ("Túneis: plataforma 1", "C", 29, 21, stands_on("C", 18, 22, 27)),
    ("Túneis: plataforma 2", "C", 23, 18, stands_on("C", 15, 14, 19)),
    ("Túneis: beirada do segredo", "C", 15, 15, stands_on("C", 12, 10, 12)),
    ("Túneis: bloco", "C", 33, 21, stands_on("C", 18, 36, 39)),
    ("Galeria: subida 1", "D", 10, 27, stands_on("D", 24, 7, 13)),
    ("Galeria: subida 2", "D", 10, 24, stands_on("D", 21, 17, 23)),
    ("Galeria: subida 3", "D", 20, 21, stands_on("D", 18, 7, 13)),
    ("Galeria: subida 4", "D", 10, 18, stands_on("D", 15, 17, 23)),
    ("Galeria: subida 5", "D", 20, 15, stands_on("D", 12, 13, 17)),
    ("Galeria: volta à entrada", "D", 15, 12, stands_on("D", 10, 21, 32)),
    ("Galeria: nicho do amuleto", "D", 8, 18, stands_on("D", 15, 1, 5)),
    ("Arena: plataforma", "E", 4, 17, stands_on("E", 14, 8, 13)),
    ("Santuário: pedestal", "E2", 12, 15, stands_on("E2", 13, 6, 9)),
]

PATHS_DASH = [
    ("Vila: fosso de 9 (ida)", "B", 46, 24, stands_on("B", 24, 57, 62)),
    ("Vila: fosso de 9 (volta)", "B", 58, 24, stands_on("B", 24, 38, 47)),
    ("Descida: volta 1", "F", 42, 26, stands_on("F", 23, 38, 41)),
    ("Descida: volta 2", "F", 39, 23, stands_on("F", 20, 30, 33)),
    ("Descida: volta 3", "F", 31, 20, stands_on("F", 17, 21, 24)),
    ("Descida: volta 4", "F", 22, 17, stands_on("F", 14, 12, 15)),
    ("Descida: volta 5", "F", 13, 14, stands_on("F", 11, 1, 8)),
    ("Jardim: fosso 1 (ida)", "G", 18, 17, stands_on("G", 17, 25, 30)),
    ("Jardim: fosso 2 (ida)", "G", 29, 17, stands_on("G", 17, 36, 40)),
    ("Jardim: fosso 2 (volta)", "G", 37, 17, stands_on("G", 17, 25, 30)),
    ("Jardim: fosso 1 (volta)", "G", 26, 17, stands_on("G", 17, 10, 19)),
    ("Ninho: subida 1", "H", 3, 43, stands_on("H", 40, 6, 11)),
] + [
    (f"Ninho: subida {i + 2}", "H", 8 if i % 2 == 0 else 20, 40 - 3 * i,
     stands_on("H", 37 - 3 * i, 18, 23) if i % 2 == 0 else stands_on("H", 37 - 3 * i, 6, 11))
    for i in range(10)
] + [
    ("Ninho: topo 1", "H", 8, 10, stands_on("H", 7, 12, 17)),
    ("Ninho: topo 2", "H", 13, 7, stands_on("H", 4, 15, 17)),
    ("Ninho: sobe para o santuário", "H", 16, 4, in_room("I")),
]

PATHS_DOUBLE = [
    ("Vila: degrau 6 acima (Alturas)", "B", 37, 15, stands_on("B", 9, 43, 45)),
    ("Vila: poço direito 2", "B", 44, 9, stands_on("B", 6, 40, 42)),
    ("Vila: poço direito 3", "B", 41, 6, stands_on("B", 3, 43, 45)),
    ("Vila: sobe para os Picos", "B", 44, 3, in_room("K")),
    ("Picos: 1", "K", 12, 39, stands_on("K", 34, 4, 9)),
    ("Picos: 2", "K", 6, 34, stands_on("K", 29, 16, 21)),
    ("Picos: 3", "K", 18, 29, stands_on("K", 24, 28, 33)),
    ("Picos: 4", "K", 30, 24, stands_on("K", 19, 16, 21)),
    ("Picos: 5", "K", 18, 19, stands_on("K", 14, 4, 9)),
    ("Picos: 6", "K", 6, 14, stands_on("K", 9, 16, 21)),
    ("Picos: beirada oeste", "K", 18, 9, stands_on("K", 6, 1, 6)),
    ("Picos: beirada leste", "K", 18, 9, stands_on("K", 6, 33, 38)),
    ("Picos: fragmento", "K", 30, 24, stands_on("K", 19, 35, 38)),
    ("Mirante: 1", "M", 5, 13, stands_on("M", 11, 11, 13)),
    ("Mirante: 2", "M", 12, 11, stands_on("M", 9, 17, 19)),
    ("Mirante: 3", "M", 18, 9, stands_on("M", 11, 22, 23)),
    ("Mirante: 4", "M", 22, 11, stands_on("M", 13, 26, 34)),
    ("Jardim: fragmento alto", "G", 46, 17, stands_on("G", 11, 44, 48)),
]

GATES = [
    # (nome, habilidades, sala, coluna, linha, alvo) — deve ser IMPOSSÍVEL
    ("sem dash não cruza o fosso da Vila", set(), "B", 46, 24, stands_on("B", 24, 57, 62)),
    ("sem pulo duplo não sobe às Alturas", set(), "B", 37, 15, stands_on("B", 9, 43, 45)),
    ("só com dash também não sobe às Alturas", {"dash"}, "B", 37, 15, stands_on("B", 9, 43, 45)),
    ("sem pulo duplo não pega o fragmento alto do Jardim", {"dash"}, "G", 46, 17, stands_on("G", 11, 44, 48)),
]


def _run_paths(abilities, paths, label):
    s = Sim(abilities=abilities)
    for name, room, tx, row, target in paths:
        res = try_reach(s, room, tx, row, target)
        check(f"alcançável ({label}): {name}", res is not None, res or "nenhuma sequência funcionou")


def test_reach_without_abilities():
    _run_paths((), PATHS_NONE, "sem habilidades")


def test_reach_with_dash():
    _run_paths(("dash",), PATHS_DASH, "dash")


def test_reach_with_double_jump():
    _run_paths(("dash", "double_jump"), PATHS_DOUBLE, "dash + pulo duplo")


def test_gates():
    for name, abilities, room, tx, row, target in GATES:
        s = Sim(abilities=abilities)
        res = try_reach(s, room, tx, row, target)
        check(f"bloqueio: {name}", res is None, res or "")


# ---------------------------------------------------------------------------
# Itens, moedas, energia
# ---------------------------------------------------------------------------

def test_new_game_start():
    pr = Progress()
    pr.chapter = 0
    s = Sim(abilities=None, progress=pr, save_name="novo.json")
    check("novo jogo começa sem dash e sem pulo duplo", not s.p.abilities)
    s.step({"dash"}, {"dash"})
    check("sem a habilidade, Shift não faz dash", not s.p.dashing)
    s.step({"jump"}, {"jump"})
    s.wait_until(lambda: s.p.vy >= 0, 1.0, held={"jump"})
    s.step({"jump"}, {"jump"})
    check("sem a habilidade, não há pulo duplo", s.p.jumps_used <= 1)
    check("começa na Entrada", s.play.room.id == "A")


def test_ability_pickup():
    s = Sim(abilities=(), save_name="habilidade.json")
    s.goto("E2", 12, 15)
    s.p.place(7 * T + 16, 13 * T)
    s.wait_until(lambda: "dash" in s.p.abilities, 0.5)
    check("pegar o item do santuário libera o dash", "dash" in s.p.abilities)
    saved = Progress.load(s.save_path)
    check("habilidade fica salva no arquivo", saved is not None and "dash" in saved.abilities)
    s.play.load_room(s.play.world.rooms["E2"])
    check("item pego não reaparece", not s.play.items)


def test_coins_and_bag():
    s = Sim(save_name="moedas.json")
    s.goto("A", 6, 17)
    e = Patroller(s.p.cx + 40, s.p.bottom)
    e.think = lambda *a: None
    s.play.enemies = [e]
    for _ in range(8):
        if not e.alive:
            break
        s.p.facing = 1
        s.step(pressed={"attack_quick"})
        s.run(Combat.QUICK.total + 0.02)
    check("inimigo derrotado solta moedas", len(s.play.coins) > 0 or s.pr.coins > 0)
    # anda até as moedas
    for _ in range(int(3.0 / SIM_DT)):
        if not s.play.coins:
            break
        target = s.play.coins[0].cx
        s.step({"right"} if target > s.p.cx + 4 else {"left"} if target < s.p.cx - 4 else set())
    check("moedas são coletadas", s.pr.coins == 4, f"{s.pr.coins} moedas")
    # morte deixa bolsa
    s.pr.coins = 50
    s.goto("A", 8, 17)
    s.p.hp = 1
    s.p.take_hit(1, s.p.cx + 10, s.play)
    check("morrer guarda as moedas numa bolsa", s.pr.coins == 0 and s.pr.bag and s.pr.bag[3] == 50)
    s.play.respawn_at_bench()
    bag = s.pr.bag
    check("bolsa aparece na sala onde ficou", s.play.room.id != bag[0] or s.play.bag is not None)
    s.play.load_room(s.play.world.rooms[bag[0]])
    s.p.reset_state()
    s.p.place(bag[1], bag[2])
    s.step()
    check("encostar na bolsa recupera as moedas", s.pr.coins == 50 and s.pr.bag is None)


def test_energy_and_heal():
    s = Sim()
    s.goto("A", 6, 17)
    e = Patroller(s.p.cx + 40, s.p.bottom)
    e.think = lambda *a: None
    e.max_hp = e.hp = 999
    e.knockback_resist = 0
    s.play.enemies = [e]
    for _ in range(3):
        s.step(pressed={"attack_quick"})
        s.wait_until(lambda: s.p.attack is None, 1.0)
    check("acertos enchem a energia", s.p.energy == 3 * Energy.PER_HIT_QUICK, f"{s.p.energy:.0f}")
    s.play.enemies = []
    s.p.hp = 2
    s.run(Energy.HEAL_TIME + 0.05, held={"heal"})
    check("segurar F cura 1 de vida e gasta energia",
          s.p.hp == 3 and abs(s.p.energy - (3 * Energy.PER_HIT_QUICK - Energy.HEAL_COST)) < 1e-6)
    s.p.energy = 99
    x0 = s.p.x
    s.run(0.3, held={"heal", "right"})
    check("segurar F trava o movimento enquanto cura", abs(s.p.x - x0) < 1)
    s.run(0.1, held={"right"})
    check("soltar F interrompe a cura", s.p.heal_timer == 0 and s.p.x > x0)
    s.p.energy = 99
    s.p.hp = s.p.max_hp
    s.run(Energy.HEAL_TIME + 0.1, held={"heal"})
    check("vida cheia não gasta energia", s.p.energy == 99)
    s.p.hp = 2
    s.p.energy = 10
    s.run(Energy.HEAL_TIME + 0.1, held={"heal"})
    check("sem energia suficiente não cura", s.p.hp == 2)


# ---------------------------------------------------------------------------
# Banco, loja, ferreiro, amuletos
# ---------------------------------------------------------------------------

def _interact(s):
    s.inp.pressed.add("interact")
    s.play.fixed_update(SIM_DT, s.inp)
    s.inp.consume()
    return s.app.state


def test_bench():
    s = Sim(save_name="banco.json")
    s.goto("B", 26, 24)
    s.p.hp = 1
    st = _interact(s)
    check("W perto do banco abre o menu do banco", isinstance(st, BenchState))
    check("banco restaura a vida", s.p.hp == s.p.max_hp)
    check("banco vira ponto de reaparecimento", s.pr.bench and s.pr.bench[0] == "B")
    check("banco salva o jogo", Progress.exists(s.save_path))
    s.app.resume(s.play)
    # amuletos
    s.pr.give("charm", "lamina")
    s.pr.give("charm", "forca")
    base_w = s.p.quick_spec.hit_w
    ok1 = s.pr.toggle_charm("lamina")
    s.p.recompute_stats()
    check("equipar Lâmina Longa aumenta o alcance", ok1 and s.p.quick_spec.hit_w > base_w,
          f"{base_w} -> {s.p.quick_spec.hit_w}")
    ok2 = s.pr.toggle_charm("forca")
    check("espaços de amuleto limitam o que se equipa", not ok2, f"{s.pr.notches_used}/{s.pr.notches}")
    s.pr.toggle_charm("lamina")
    ok3 = s.pr.toggle_charm("forca")
    s.p.recompute_stats()
    check("Força Bruta aumenta o dano", ok3 and s.p.quick_spec.damage > Combat.QUICK.damage)
    s.pr.toggle_charm("forca")
    s.pr.give("charm", "vigor")
    s.pr.toggle_charm("vigor")
    s.p.recompute_stats()
    check("Vigor dá +1 de vida máxima", s.p.max_hp == Progression.BASE_HP + 1)
    s.pr.give("charm", "vento")
    s.pr.toggle_charm("vigor")
    s.pr.toggle_charm("vento")
    s.p.recompute_stats()
    check("Passo de Vento acelera o dash", s.p.dash_speed > 950 and s.p.dash_cooldown_time < 0.45)
    # morrer volta para o banco
    s.goto("A", 6, 17)
    s.p.hp = 1
    s.p.take_hit(1, s.p.cx + 10, s.play)
    s.play.respawn_at_bench()
    check("depois de morrer, reaparece no banco", s.play.room.id == "B"
          and abs(s.p.cx - s.pr.bench[1]) < 1 and s.p.hp == s.p.max_hp)


def test_shop():
    s = Sim(save_name="loja.json")
    s.goto("B", 18, 24)
    st = _interact(s)
    check("W perto do lojista abre a loja", isinstance(st, ShopState) and st.kind == "shop")
    s.pr.coins = 100
    st._buy("map", 30)
    check("comprar o mapa", s.pr.has_map and s.pr.coins == 70)
    st._buy("map", 30)
    check("item vendido não é comprado de novo", s.pr.coins == 70)
    st._buy("fragment", 150)
    check("sem moedas suficientes não compra", s.pr.fragments == 0 and s.pr.coins == 70)
    s.pr.coins = 1000
    for _ in range(4):
        s.pr.give("fragment")
    s.p.recompute_stats()
    check("4 fragmentos = +1 de vida máxima", s.p.max_hp == Progression.BASE_HP + 1)
    st._buy("notch", 200)
    check("entalhe aumenta espaços de amuleto", s.pr.notches == Progression.BASE_NOTCHES + 1)
    s.app.resume(s.play)
    # ferreiro
    s.goto("B", 44, 24)
    st = _interact(s)
    check("W perto do ferreiro abre a forja", isinstance(st, ShopState) and st.kind == "smith")
    s.pr.coins = 100
    s.pr.ore = 0
    dmg0 = s.p.quick_spec.damage
    cost, ore = s.pr.next_weapon_upgrade()
    st._upgrade(cost, ore)
    check("melhoria 1 da arma (só moedas)", s.pr.weapon_level == 1 and s.p.quick_spec.damage == dmg0 + 1)
    s.pr.coins = 1000
    cost, ore = s.pr.next_weapon_upgrade()
    st._upgrade(cost, ore)
    check("melhoria 2 exige minério", s.pr.weapon_level == 1)
    s.pr.ore = 1
    st._upgrade(cost, ore)
    check("com minério, melhora", s.pr.weapon_level == 2 and s.pr.ore == 0)


def test_breakable_secret():
    s = Sim(save_name="segredo.json")
    s.goto("C", 11, 12)
    s.p.facing = -1
    s.step({"left"})
    s.step(pressed={"attack_quick"})
    s.run(0.3)
    broken = s.play.world.rooms["C"].broken
    check("ataque quebra a parede secreta", len(broken) >= 1, str(sorted(broken)))
    got = s.wait_until(lambda: {"C:0", "C:1"} <= s.pr.collected, 3.0, held={"left"})
    check("dá para entrar no esconderijo e pegar os itens", got)
    saved = Progress.load(s.save_path)
    check("parede quebrada fica salva", saved and any(k.startswith("C:9:") for k in saved.broken))


# ---------------------------------------------------------------------------
# Inimigos novos e chefe
# ---------------------------------------------------------------------------

def test_shield():
    s = Sim()
    s.goto("A", 6, 17)
    e = Shield(s.p.cx + 44, s.p.bottom)
    e.think = lambda *a: None
    e.direction = -1           # escudo virado para o jogador
    s.play.enemies = [e]
    hp0 = e.hp
    s.p.facing = 1
    s.step(pressed={"attack_quick"})
    s.run(0.3)
    check("escudo bloqueia o ataque rápido de frente", e.hp == hp0 and s.p.vx <= 0)
    s.goto("A", 6, 17)
    s.play.enemies = [e]
    e.x = s.p.cx + 44 - e.w / 2
    e.vx = 0
    s.p.facing = 1
    s.step(pressed={"attack_heavy"})
    s.run(0.45)
    check("ataque pesado quebra a guarda e causa dano", e.hp < hp0 and e.stun > 0)
    e2 = Shield(s.p.cx + 44, s.p.bottom)
    e2.think = lambda *a: None
    e2.direction = 1           # de costas para o jogador
    s.goto("A", 6, 17)
    s.play.enemies = [e2]
    s.p.facing = 1
    s.step(pressed={"attack_quick"})
    s.run(0.3)
    check("pelas costas o rápido funciona", e2.hp < e2.max_hp)


def test_flier_and_jumper():
    s = Sim()
    s.goto("LA", 6, 14)
    f = Flier(s.p.cx + 200, s.p.bottom - 100)
    s.play.enemies = [f]
    s.p.invuln = 99
    d0 = abs(f.cx - s.p.cx) + abs(f.cy - s.p.cy)
    s.run(1.2)
    d1 = abs(f.cx - s.p.cx) + abs(f.cy - s.p.cy)
    check("voador detecta e se aproxima pelo ar", f.state == "chase" and d1 < d0, f"{d0:.0f} -> {d1:.0f}")
    s.goto("LA", 6, 14)
    j = Jumper(s.p.cx + 200, s.p.bottom)
    s.play.enemies = [j]
    s.p.invuln = 99
    x0 = j.cx
    jumped = s.wait_until(lambda: j.state == "air", 3.0)
    s.run(0.4)
    check("saltador avisa (agacha) e salta na direção do jogador", jumped and j.cx < x0)


def test_boss():
    s = Sim(save_name="chefe.json")
    s.goto("E", 30, 17, enemies=True)
    boss = s.play.boss
    room = s.play.room
    check("chefe começa dormindo", boss is not None and not boss.awake)
    check("saída oeste trancada antes da luta", room.is_solid(1, 15))
    s.p.invuln = 99
    s.run(1.0, held={"left"})
    check("chegar perto acorda o chefe e fecha o portão", boss.awake and room.fight_active and room.is_solid(38, 15))
    # cada ataque, forçado um de cada vez
    def force(state):
        boss.state = state
        boss.timer = 0.01
        s.play.projectiles.clear()
        seen = set()
        shots = 0
        for _ in range(int(3.0 / SIM_DT)):
            s.step()
            s.p.invuln = 99
            seen.add(boss.state)
            shots = max(shots, len(s.play.projectiles.items))
            if boss.state == "idle" and len(seen) > 1:
                break
        return seen, shots
    seen, _ = force("charge_tele")
    check("investida: corre até a parede e fica tonto (janela de punição)", "charge" in seen and "stunned" in seen)
    seen, shots = force("leap_tele")
    check("salto: cai e solta ondas de choque", "leap" in seen and shots >= 2, f"{shots} projéteis")
    seen, shots = force("spit_tele")
    check("cuspe: 3 projéteis em leque", shots >= 3, f"{shots} projéteis")
    random.seed(3)
    used = set()
    for _ in range(int(15 / SIM_DT)):
        s.step()
        s.p.invuln = 99
        used.add(boss.state)
    check("chefe alterna ataques sozinho", len({u for u in used if u.endswith("_tele")}) >= 2, str(sorted(used)))
    check("chefe fica dentro da arena", 0 <= boss.x and boss.right <= room.width)
    boss.hp = 1
    s.p.place(boss.cx - 40, 17 * T)
    s.p.facing = 1
    s.p.invuln = 99
    s.step(pressed={"attack_quick"})
    s.run(0.3)
    check("chefe derrotado", not boss.alive and "E" in s.pr.bosses)
    check("portões abrem após a vitória", not room.is_solid(1, 15) and not room.is_solid(38, 15))
    saved = Progress.load(s.save_path)
    s2 = Sim(progress=saved, save_name="chefe2.json")
    s2.play.load_room(s2.play.world.rooms["E"])
    check("chefe derrotado não volta", s2.play.boss is None and not s2.play.world.rooms["E"].is_solid(1, 15))


# ---------------------------------------------------------------------------
# Save, menu, mapa, telas
# ---------------------------------------------------------------------------

def test_save_and_continue():
    s = Sim(save_name="continuar.json")
    s.goto("B", 26, 24)
    s.pr.coins = 77
    s.pr.give("ability", "dash")
    _interact(s)
    s.app.resume(s.play)
    loaded = Progress.load(s.save_path)
    check("save guarda moedas, habilidades e banco",
          loaded.coins == 77 and "dash" in loaded.abilities and loaded.bench[0] == "B")
    s.app.to_menu()
    opts = {o[1]: o[2] for o in s.app.state.menu.options}
    check("menu habilita Continuar capítulo quando há save", opts.get("continue") is True, str(opts))
    s.app.start_game(Progress.load(s.save_path))
    st = s.app.state
    check("Continuar começa no banco salvo", isinstance(st, PlayState) and st.room.id == "B"
          and abs(st.player.cx - loaded.bench[1]) < 1)
    bad_path = os.path.join(os.path.dirname(s.save_path), "corrompido.json")
    with open(bad_path, "w", encoding="utf-8") as f:
        f.write("{isto não é json")
    check("save corrompido não quebra o jogo", Progress.load(bad_path) is None)


def test_map_and_screens():
    s = Sim(save_name="telas.json")
    app = s.app
    s.goto("A", 6, 17)
    app.input.pressed.add("map")
    app.state.frame(1 / 60, app.input)
    check("M abre o mapa", isinstance(app.state, MapState))
    app.state.draw(app.screen)
    app.input.pressed.add("map")
    app.state.frame(1 / 60, app.input)
    check("M fecha o mapa", app.state is s.play)
    s.pr.has_map = True
    s.pr.give("charm", "bussola")
    s.pr.toggle_charm("bussola")
    s.pr.visited |= set(s.play.world.rooms)
    app.push(MapState(app, s.play))
    app.state.draw(app.screen)
    app.resume(s.play)
    app.input.pressed.add("pause")
    app.state.frame(1 / 60, app.input)
    check("ESC abre pausa com inventário", isinstance(app.state, PauseState))
    x0 = s.p.x
    app.input.held = {"right"}
    for _ in range(30):
        app.state.frame(1 / 60, app.input)
    check("jogo congelado na pausa", s.p.x == x0)
    app.state.draw(app.screen)
    app.input.held = set()
    app.input.pressed.add("pause")
    app.state.frame(1 / 60, app.input)
    check("ESC retoma", app.state is s.play)
    for rid, room in s.play.world.rooms.items():
        s.play.load_room(room)
        s.play.draw(app.screen)
    app.push(BenchState(app, s.play))
    app.state.draw(app.screen)
    app.push(ShopState(app, s.play, "shop"))
    app.state.draw(app.screen)
    app.push(ShopState(app, s.play, "smith"))
    app.state.draw(app.screen)
    app.to_menu()
    app.state.draw(app.screen)
    check("todas as salas e telas desenham sem erro", True)


TESTS = [
    test_world_structure, test_all_doors, test_new_game_start, test_ability_pickup, test_coins_and_bag,
    test_energy_and_heal, test_bench, test_shop, test_breakable_secret, test_shield, test_flier_and_jumper,
    test_boss, test_save_and_continue, test_map_and_screens,
    test_gates, test_reach_without_abilities, test_reach_with_dash, test_reach_with_double_jump,
]
