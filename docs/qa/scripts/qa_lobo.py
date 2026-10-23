from qa_common import *
s = game(("dash", "double_jump"), flags=("atracado",), name="qa_lobo.json")
s.play.load_room(s.play.world.rooms["floresta"])
s.p.place(4*T, 37*T); s.step()
w = [e for e in s.play.enemies if type(e).__name__ == "Wolf"][0]
for k in range(int(10/SIM_DT)):
    s.step(); s.p.invuln = 99
    if w.x > 18.6*T and w.alive:
        s.p.invuln = 0; shot(s, "inimigo_lobo_floresta_espinhos"); break
s.run(1.0); print("lobo vivo:", w.alive, "moedas soltas:", len(s.play.coins))
