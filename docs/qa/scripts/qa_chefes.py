"""Bot simples luta com cada chefe em cada dificuldade: golpes para vencer, dano levado, tempo, saída da arena."""
import random, sys
from qa_common import *

ARENAS = {"toca": 15, "gavea": 17, "ruinas": 17, "altar": 19}
SHOT_DONE = set()

def fight(room_id, diff, seed, dodge=True, max_t=240.0):
    random.seed(seed)
    s = game(("dash", "double_jump"), flags=("atracado",), name=f"qa_boss_{room_id}_{diff}.json", difficulty=diff)
    s.p.recompute_stats(); s.p.hp = s.p.max_hp
    s.goto(room_id, 4, ARENAS[room_id], enemies=True)
    room = s.play.room
    boss = s.play.boss
    max_hp = boss.max_hp
    hits = 0; taken = 0; deaths = 0; t = 0.0; outside = 0; min_x = 9e9; max_x = -9e9
    last_hp = boss.hp; php = s.p.hp; atk_cd = 0
    states = {}
    awake_t = None
    while t < max_t and boss.alive:
        p = s.p
        held = set(); pressed = set()
        if boss.awake and awake_t is None: awake_t = t
        dx = boss.cx - p.cx
        dy = boss.cy - p.cy
        d = 1 if dx > 0 else -1
        # aproxima
        if abs(dx) > 40:
            held.add("right" if d > 0 else "left")
        elif p.facing != d:
            held.add("right" if d > 0 else "left")
        # ataque
        near_x = abs(dx) < (boss.w / 2 + 50)
        if near_x and atk_cd <= 0 and boss.awake:
            if boss.bottom < p.top + 4:            # chefe acima: golpe para cima / pulo
                held.add("up")
                if boss.bottom < p.top - 20:
                    held.add("jump")
                    if p.on_ground:
                        pressed.add("jump")
                    elif p.vy > -150 and p.jumps_used < 2 and boss.top < p.top:
                        pressed.add("jump")
            pressed.add("attack_quick"); atk_cd = 0.16
        atk_cd -= SIM_DT
        # esquiva tosca: pula quando o chefe avança na direção e está perto
        if dodge and boss.awake and abs(boss.vx) > 300 and abs(dx) < 220 and (boss.vx > 0) == (dx < 0) and p.on_ground:
            pressed.add("jump"); held.add("jump")
        # pula obstáculo baixo (barris) quando empaca segurando a direção
        if p.on_ground and abs(p.vx) < 5 and abs(dx) > 60 and ("left" in held or "right" in held):
            pressed.add("jump"); held.add("jump")
        s.step(held, pressed)
        t += SIM_DT
        states[boss.state] = states.get(boss.state, 0) + 1
        if boss.hp < last_hp:
            hits += 1
        last_hp = boss.hp
        if s.p.hp < php:
            taken += php - s.p.hp
        if not s.p.alive or s.p.hp <= 0 or s.app.state.__class__.__name__ == "DeathState":
            deaths += 1
            s.p.alive = True
            s.p.hp = s.p.max_hp
        php = s.p.hp
        if s.play.room is not room:
            return dict(err=f"saiu da sala para {s.play.room.id}")
        min_x = min(min_x, boss.x); max_x = max(max_x, boss.right)
        if boss.x < -2 or boss.right > room.width + 2 or boss.bottom > room.height + 2 or boss.top < -64:
            outside += 1
        key = (room_id, diff)
        if key not in SHOT_DONE and boss.awake and boss.hp < boss.max_hp * 0.45 and seed == SEEDS[0]:
            SHOT_DONE.add(key); p.invuln = 0
            shot(s, f"chefe_{room_id}_{diff}_meio")
    return dict(max_hp=max_hp, hits=hits, taken=taken, deaths=deaths, time=t - (awake_t or 0), won=not boss.alive,
                outside=outside, x=(round(min_x / T, 1), round(max_x / T, 1)), w=room.width / T,
                player_max=s.p.max_hp, dmg=s.p.quick_spec.damage, states=sorted(states))

ONLY = [a for a in sys.argv[1:] if not a.isdigit()]
SEEDS = [int(a) for a in sys.argv[1:] if a.isdigit()] or [1, 2, 3]
for rid in (ONLY or ARENAS):
    for diff in ("facil", "normal", "dificil"):
        for seed in SEEDS:
            r = fight(rid, diff, seed)
            print(rid, diff, seed, r, flush=True)
