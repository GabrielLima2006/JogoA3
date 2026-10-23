"""Atravessa cada porta (nos dois sentidos, pois os links são listados dos dois lados) e captura a chegada."""
from qa_common import *

s = game(("dash", "double_jump"), flags=("atracado",), name="qa_portas.json")
for r in s.play.world.rooms.values():
    r.door_unlocked = r.key is not None
    r.boss_defeated = bool(r.boss)
for (rid, digit), (tid, tdig) in sorted(s.play.world.links.items()):
    if rid not in GAME_ROOMS:
        continue
    room = s.play.world.rooms[rid]
    door = room.doors[digit]
    s.play.load_room(room)
    s.play.enemies, s.play.items, s.play.boss = [], [], None
    p = s.p
    p.reset_state(); p.hp = p.max_hp
    held = set()
    if door.side == "W":
        p.x, p.y = 2.0, (door.hi + 1) * T - p.h; held = {"left"}
    elif door.side == "E":
        p.x, p.y = room.width - p.w - 2.0, (door.hi + 1) * T - p.h; held = {"right"}
    else:
        p.x = (door.lo + door.hi + 1) / 2 * T - p.w / 2
        if door.side == "N":
            p.y, p.vy = 4.0, -700.0
        else:
            p.y, p.vy = room.height - p.h - 4.0, 300.0
    arrived = s.wait_until(lambda: s.play.room.id == tid, 1.5, held=held)
    inside = overlaps_solid(s.play.room, p.x, p.y, p.w, p.h) if arrived else None
    landed = s.wait_until(lambda: s.p.on_ground, 2.0, held=held) if arrived else False
    s.run(0.4)
    hz = s.play.hazard_timer > 0 or p.hp < p.max_hp
    res = f"{rid}:{digit}({door.side}) -> {tid}:{tdig}  chegou={arrived} preso_na_parede={inside} pousou={landed} sala_final={s.play.room.id} dano={hz} pos=({p.x/T:.1f},{p.bottom/T:.1f})"
    print(res)
    p.invuln = 0
    shot(s, f"porta_{rid}{digit}_para_{tid}")
