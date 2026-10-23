"""Percorre as 13 salas: capturas em 3 pontos e checagem dos inimigos (preso em parede, caiu do mapa, parado)."""
from qa_common import *

s = game(("dash", "double_jump"), flags=("atracado",), name="qa_salas.json")
for r in s.play.world.rooms.values():
    r.door_unlocked = r.key is not None
for rid in GAME_ROOMS:
    room = s.play.world.rooms[rid]
    s.play.load_room(room)
    s.play.player.invuln = 999
    # inimigos: estado inicial
    ens = list(s.play.enemies)
    start = {id(e): (e.x, e.y) for e in ens}
    stuck0 = [(type(e).__name__, overlaps_solid(room, e.x, e.y, e.w, e.h)) for e in ens if overlaps_solid(room, e.x, e.y, e.w, e.h)]
    # três pontos de vista: chão em 15%, 50%, 85% da largura
    for i, frac in enumerate((0.12, 0.5, 0.88)):
        x = room.width * frac
        y = 2 * T
        # procura primeira linha sólida/plataforma a partir do topo que tenha espaço livre acima
        tx = int(x // T)
        fy = None
        for ty in range(2, room.rows_count):
            if (room.is_solid(tx, ty) or room.is_oneway(tx, ty)) and not room.is_solid(tx, ty - 1) and not room.is_solid(tx, ty - 2) and not room.is_spike(tx, ty - 1):
                fy = ty * T
                break
        if fy is None:
            continue
        s.p.place(x, fy)
        s.p.vx = s.p.vy = 0
        s.play.camera.snap(s.p, room)
        for _ in range(int(0.6 / SIM_DT)):
            s.step()
            s.p.invuln = 999
        s.p.invuln = 0
        shot(s, f"sala_{rid}_{i}")
    # mais 8s de simulação para ver inimigos
    for _ in range(int(8 / SIM_DT)):
        s.step()
        s.p.invuln = 999
        s.p.hp = s.p.max_hp
    ens2 = s.play.enemies
    report = []
    for e in ens:
        n = type(e).__name__
        if not e.alive:
            continue
        sx, sy = start[id(e)]
        moved = abs(e.x - sx) + abs(e.y - sy)
        solid = overlaps_solid(room, e.x, e.y, e.w, e.h)
        out = not (-T <= e.x <= room.width + T and -T <= e.y <= room.height + T)
        flags = []
        if solid: flags.append(f"DENTRO-DE-PAREDE {solid[:3]}")
        if out: flags.append("FORA-DO-MAPA")
        if moved < 2: flags.append("PARADO")
        report.append(f"{n}@({e.x/T:.1f},{e.y/T:.1f}) movido={moved:.0f}px {' '.join(flags)}")
    print(f"== {rid} ({room.cols}x{room.rows_count}) inimigos={len(ens)} presos_no_inicio={stuck0}")
    for line in report:
        print("   ", line)
