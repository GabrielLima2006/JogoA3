from qa_common import *
from src import states as S
from src.progress import CHARMS, Progress as P2
s = game(("dash", "double_jump"), flags=("atracado",), name="qa_sis.json")
p = s.p
base = dict(q=p.quick_spec.damage, qw=p.quick_spec.hit_w, hp=p.max_hp, dash=p.dash_speed, cd=p.dash_cooldown_time,
            heal=p.heal_time, en=p.energy_mult, mag=p.magnet)
print("base", base, "espaços", getattr(s.pr, "notches", None))
for cid in CHARMS:
    if cid not in s.pr.charms_owned: s.pr.charms_owned.append(cid)
for cid in CHARMS:
    pr = s.pr
    # desequipa tudo
    for c in list(CHARMS):
        if pr.equipped(c):
            pr.toggle_charm(c)
    ok = pr.toggle_charm(cid)
    p.recompute_stats()
    now = dict(q=p.quick_spec.damage, qw=p.quick_spec.hit_w, hp=p.max_hp, dash=p.dash_speed, cd=p.dash_cooldown_time,
               heal=p.heal_time, en=p.energy_mult, mag=p.magnet)
    diff = {k: (base[k], v) for k, v in now.items() if v != base[k]}
    print(f"  {cid:8s} custo={CHARMS[cid]['cost']} equipou={ok} muda={diff}")
# navegação da grade
from src.amuletos import CharmScreen
cs = CharmScreen(s.pr)
seen = set()
for mv in [(1,0)]*10 + [(0,1)] + [(1,0)]*10 + [(0,-1)]:
    cs.move(*mv); seen.add(cs.selected())
print("grade alcança:", len(seen), "de", len(CHARMS), sorted(set(CHARMS) - seen))
# mapa com mapa comprado
s.pr.has_map = True
s.pr.visited |= {"cabine", "conves", "porao1", "porao2", "toca", "cordame1", "praia"}
s.goto("porao2", 4, 20)
st = S.MapState(s.app, s.play); s.app.state = st; shot(s, "sis_mapa_com_mapa", st)
for c in list(CHARMS):
    if s.pr.equipped(c): s.pr.toggle_charm(c)
s.pr.toggle_charm("bussola")
st = S.MapState(s.app, s.play); s.app.state = st; shot(s, "sis_mapa_com_bussola", st)
s.app.state = s.play
# pausa -> voltar à bola de cristal
s.play.rest_at_bench([o for o in s.play.interactables if o.kind == "bench"][0])
s.goto("toca", 5, 15)
st = S.PauseState(s.app, s.play); s.app.state = st
st.menu.index = 1; s.inp.pressed.add("menu_confirm"); st.frame(1/60, s.inp); s.inp.consume()
print("pausa > voltar à bola:", type(s.app.state).__name__, s.play.room.id)
# salvar e continuar
s.play.save()
pr2 = P2.load(s.save_path)
print("save carrega:", pr2 is not None, pr2.bench if pr2 else None, sorted(pr2.abilities) if pr2 else None)
# cura com F
s.p.hp = 2; s.p.energy = 999
for _ in range(int(2.5 / SIM_DT)):
    s.step({"heal"} if "heal" in s.inp.__dict__.get("bindings", {}) else {"heal"})
print("cura segurando F:", s.p.hp)
