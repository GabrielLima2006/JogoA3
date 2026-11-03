"""Para onde a jogadora volta ao cair em água/espinhos, com e sem bola de cristal usada; morte e bolsa."""
from qa_common import *
from src import states as S

def fall_into(s, rid, tx, row_floor, label, direction=None):
    s.app.state = s.play
    s.goto(rid, tx, row_floor)
    hp0 = s.p.hp
    held = {direction} if direction else set()
    hit = s.wait_until(lambda: s.play.hazard_timer > 0 or s.play.room.id != rid, 3.0, held=held)
    s.wait_until(lambda: s.play.hazard_timer <= 0 and s.p.on_ground, 3.0)
    s.run(0.3)
    print(f"  {label}: tocou={hit} voltou para {s.play.room.id} ({s.p.cx/T:.1f},{s.p.bottom/T:.1f}) vida {hp0}->{s.p.hp}")
    return s.play.room.id

print("Novo jogo, nunca usou bola de cristal:")
s = game(("dash", "double_jump"), flags=("atracado",), name="qa_per1.json")
s.pr.bench = None
fall_into(s, "porao2", 7, 20, "canal do porão 2 (anda para a direita)", "right")
shot(s, "perigo_porao2_volta_cabine")
fall_into(s, "praia", 13, 18, "vala de espinhos da praia (anda para a direita)", "right")
print("Usou a bola de cristal da praia e foi para a floresta:")
s.goto("praia", 4, 18)
s.play.rest_at_bench([o for o in s.play.interactables if o.kind == "bench"][0])
fall_into(s, "floresta", 18, 37, "espinhos do chão da floresta", "right")
shot(s, "perigo_floresta_volta_praia")
print("Usou a bola do templo:")
s.goto("templo", 3, 18)
s.play.rest_at_bench([o for o in s.play.interactables if o.kind == "bench"][0])
fall_into(s, "templo", 8, 18, "espinhos do templo", "right")
print("Vergas (cordame2), banco usado ali:")
s.goto("cordame2", 3, 15)
s.play.rest_at_bench([o for o in s.play.interactables if o.kind == "bench"][0])
fall_into(s, "cordame2", 9, 15, "mar das vergas", "right")
print("Cordame 1 sem banco (último banco = vergas): cair pelo fundo")
try:
    s.goto("cordame1", 10, 36)
    s.p.x = 25 * T; s.p.y = 38 * T; s.p.vy = 300
    s.run(1.5)
    print(f"  ficou em {s.play.room.id} ({s.p.cx/T:.1f},{s.p.bottom/T:.1f})")
except AssertionError as e:
    print("  não testado (sala redesenhada):", e)

print("Morte e bolsa:")
s = game(("dash", "double_jump"), name="qa_morte.json")
s.goto("porao2", 4, 20)
s.play.rest_at_bench([o for o in s.play.interactables if o.kind == "bench"][0])
s.goto("porao2", 46, 20)
s.pr.coins = 33
s.p.hp = 1
s.p.take_hit(1, s.p.cx + 10, s.play)
for _ in range(400):
    s.app.state.frame(1 / 60, s.inp)
    if isinstance(s.app.state, S.DeathState):
        break
print("  tela de morte:", type(s.app.state).__name__, "bolsa:", s.pr.bag, "mortes:", s.pr.deaths)
st = s.app.state
s.inp.pressed.add("menu_confirm"); st.frame(1 / 60, s.inp); s.inp.consume()
print("  depois de 'tentar de novo':", type(s.app.state).__name__, s.play.room.id, f"({s.p.cx/T:.1f},{s.p.bottom/T:.1f})", "vida", s.p.hp, "/", s.p.max_hp)
bag = s.pr.bag
s.app.state = s.play
if bag:
    s.p.place(bag[1], bag[2]); s.run(0.3)
    print("  bolsa recuperada:", s.pr.bag is None, "moedas", s.pr.coins)
