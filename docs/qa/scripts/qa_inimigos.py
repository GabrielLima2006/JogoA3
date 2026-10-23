from qa_common import *
s = game(("dash", "double_jump"), flags=("atracado",), name="qa_ini.json")
for rid in ("floresta", "praia", "templo", "porao1", "porao2"):
    room = s.play.world.rooms[rid]
    s.play.load_room(room)
    s.p.place(room.width - 3*T, 2*T)   # longe
    ens = list(s.play.enemies)
    for k in range(int(10 / SIM_DT)):
        s.step(); s.p.invuln = 99
        for e in ens:
            if not e.alive and not getattr(e, "_rep", False):
                e._rep = True
                print(f"{rid}: {type(e).__name__} sumiu em t={k*SIM_DT:.1f}s em ({e.x/T:.1f},{e.y/T:.1f}) hp={e.hp}")
    for e in ens:
        if e.alive and (e.y > room.height or e.x < 0 or e.x > room.width):
            print(f"{rid}: {type(e).__name__} fora da sala ({e.x/T:.1f},{e.y/T:.1f})")
# slime perto da jogadora
s.play.load_room(s.play.world.rooms["floresta"])
sl = [e for e in s.play.enemies if type(e).__name__ == "TideSlime"]
print("slimes", [(round(e.x/T,1), round(e.y/T,1)) for e in sl])
e = sl[-1]
s.goto("floresta", int(e.x // T) - 4, 37, enemies=True)
x0 = e.x
s.run(3.0)
print("slime do chão andou", round(e.x - x0), "px com a jogadora a 4 tiles")
