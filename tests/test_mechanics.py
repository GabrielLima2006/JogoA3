"""Testes de mecânica (movimento, dash, pulo duplo, combate, inimigos básicos).

Rodam nas salas-laboratório de tests/helpers.py, com todas as habilidades liberadas.
Executar todos os testes: python tests/run_tests.py
"""

from helpers import PC, SIM_DT, Sim, T, check
from src import physics
from src.config import Combat, Enemies
from src.enemies import Chaser, Patroller
from src.states import DeathState


def test_walk():
    s = Sim()
    s.goto("LA", 6, 14)
    t0 = s.t
    s.wait_until(lambda: s.p.vx >= PC.RUN_SPEED - 0.01, 1.0, held={"right"})
    accel_time = s.t - t0
    check("caminhar à direita atinge velocidade máxima", abs(s.p.vx - PC.RUN_SPEED) < 0.01,
          f"{accel_time * 1000:.0f} ms até {PC.RUN_SPEED:.0f} px/s")
    s.run(0.2, held={"right"})
    check("não passa da velocidade máxima", s.p.vx <= PC.RUN_SPEED + 1e-6)
    t0 = s.t
    s.wait_until(lambda: s.p.vx == 0, 1.0)
    check("para ao soltar (desaceleração curta)", s.p.vx == 0, f"{(s.t - t0) * 1000:.0f} ms")
    s.wait_until(lambda: s.p.vx <= -PC.RUN_SPEED + 0.01, 1.0, held={"left"})
    check("caminhar à esquerda", s.p.vx == -PC.RUN_SPEED and s.p.facing == -1)
    # virar no meio da corrida é rápido
    t0 = s.t
    s.wait_until(lambda: s.p.vx >= PC.RUN_SPEED - 0.01, 1.0, held={"right"})
    check("inversão de direção rápida", s.t - t0 < 0.25, f"{(s.t - t0) * 1000:.0f} ms de -300 a +300")


def _peak_height(s, hold_time, held_dir=()):
    y0 = s.p.bottom
    best = 0
    s.step(set(held_dir) | {"jump"}, {"jump"})
    hold_steps = int(hold_time / SIM_DT)
    for i in range(int(1.5 / SIM_DT)):
        held = set(held_dir)
        if i < hold_steps:
            held.add("jump")
        s.step(held, released={"jump"} if i == hold_steps else ())
        best = max(best, y0 - s.p.bottom)
        if s.p.on_ground and i > 3:
            break
    return best


def test_jump_variable():
    s = Sim()
    s.goto("LA", 6, 14)
    full = _peak_height(s, 2.0)
    s.goto("LA", 6, 14)
    tap = _peak_height(s, 0.0)
    s.goto("LA", 6, 14)
    mid = _peak_height(s, 0.12)
    check("pulo segurado ~4 tiles", 115 <= full <= 150, f"{full:.0f} px = {full / T:.1f} tiles")
    check("toque rápido gera pulo curto mas útil", 35 <= tap <= 75, f"{tap:.0f} px")
    check("altura proporcional ao tempo segurado", tap < mid < full, f"toque {tap:.0f} < médio {mid:.0f} < cheio {full:.0f}")


def test_jump_moving():
    s = Sim()
    s.goto("LA", 2, 14)
    s.run(0.3, held={"right"})
    x0 = s.p.cx
    _peak_height(s, 2.0, held_dir={"right"})
    dist = s.p.cx - x0
    check("pulo em movimento percorre distância horizontal", dist > 140, f"{dist:.0f} px no ar")
    check("aterrissa corretamente após pulo em movimento", s.p.on_ground)


def test_coyote():
    def trial(delay):
        # beirada de entrada da sala C: abaixo dela há um poço fundo
        s = Sim()
        s.goto("LC", 6, 14)
        s.wait_until(lambda: not s.p.on_ground, 2.0, held={"right"})
        s.run(delay, held={"right"})
        s.step({"right", "jump"}, {"jump"})
        return s.p.vy, s.p.jumps_used
    vy, used = trial(0.06)
    check("coyote time: pulo do chão 60 ms após sair da borda", abs(vy + PC.JUMP_VELOCITY) < 30 and used == 1,
          f"vy={vy:.0f}")
    vy, used = trial(0.20)
    check("depois do coyote vira pulo duplo (não ganha pulo extra)",
          abs(vy + PC.DOUBLE_JUMP_VELOCITY) < 30 and used == 2, f"vy={vy:.0f} pulos={used}")


def test_jump_buffer():
    def dropped():
        s = Sim()
        s.goto("LA", 3, 14)
        s.p.y -= 4 * T
        s.p.jumps_used = PC.MAX_JUMPS     # sem pulo no ar: só o buffer pode pular
        s.p.coyote = 0
        s.step()
        return s

    # 1ª passada descobre em que passo aterrissa (simulação é determinística)
    probe = dropped()
    n = 0
    while not probe.p.on_ground and n < 400:
        probe.step()
        n += 1

    def drop_trial(press_before):
        s = dropped()
        press_step = n - int(round(press_before / SIM_DT))
        for i in range(n + 3):
            pressed = {"jump"} if i == press_step else ()
            s.step({"jump"} if i >= press_step else (), pressed)
            if s.p.vy < -100:
                return True, i - n
        return False, None
    ok, lag = drop_trial(0.10)
    check("jump buffer: apertar 100 ms antes de aterrissar pula ao tocar o chão", ok,
          f"pulou {lag} passo(s) após o contato" if ok else "")
    ok2, _ = drop_trial(0.30)
    check("apertar 300 ms antes (fora do buffer) não pula", not ok2)


def test_walls_ceiling():
    s = Sim()
    s.goto("LA", 3, 14)
    min_left = 1e9
    for _ in range(int(1.0 / SIM_DT)):
        s.step({"left"})
        min_left = min(min_left, s.p.left)
    check("parede esquerda não é atravessada", min_left >= T - 1e-6, f"menor x = {min_left:.3f}")
    check("encostado na parede: vx zerado", s.p.vx == 0)
    # teto baixo do corredor da sala B (teto na linha 11, chão na 14)
    s.goto("LB", 12, 14)
    top_min = 1e9
    s.step({"jump"}, {"jump"})
    for _ in range(60):
        s.step({"jump"})
        top_min = min(top_min, s.p.top)
    check("teto do corredor não é atravessado", top_min >= 12 * T - 1e-6, f"topo mínimo {top_min:.2f}")
    check("volta ao chão após bater a cabeça", s.wait_until(lambda: s.p.on_ground, 1.0))


def test_no_tunneling():
    s = Sim()
    s.goto("LA", 3, 14)
    p = s.p
    p.y = 2 * T
    physics.move_and_collide(p, 0, 2000, s.play.room)
    check("deslocamento enorme para baixo para no chão", abs(p.bottom - 14 * T) < 1e-6 and p.on_ground)
    p.place(6 * T, 14 * T)
    physics.move_and_collide(p, -3000, 0, s.play.room)
    check("deslocamento enorme lateral para na parede", abs(p.left - T) < 1e-6)
    # dash contra parede a partir de várias posições sub-pixel
    bad = 0
    for k in range(40):
        s.goto("LA", 2, 14)
        s.p.x = T + 3 + k * 0.37
        s.p.facing = -1
        s.step({"left", "dash"}, {"dash"})
        for _ in range(40):
            s.step({"left"})
            if s.p.left < T - 1e-6:
                bad += 1
                break
    check("dash contra parede nunca atravessa (40 posições)", bad == 0)
    # queda máxima respeitada
    s.goto("LC", 5, 14)
    s.p.x = 12 * T
    vmax = 0
    for _ in range(200):
        s.step()
        vmax = max(vmax, s.p.vy)
    check("velocidade de queda limitada", vmax <= 900 + 1e-6, f"{vmax:.0f} px/s")


def test_double_jump():
    s = Sim()
    s.goto("LA", 6, 14)
    s.step({"jump"}, {"jump"})
    s.wait_until(lambda: s.p.vy >= 0, 1.0, held={"jump"})
    s.step({"jump"}, {"jump"})
    check("pulo duplo no ar", abs(s.p.vy + PC.DOUBLE_JUMP_VELOCITY) < 30 and s.p.jumps_used == 2,
          f"vy={s.p.vy:.0f}")
    s.run(0.1, held={"jump"})
    vy_before = s.p.vy
    s.step({"jump"}, {"jump"})
    check("terceiro pulo não acontece", s.p.vy >= vy_before - 1e-6 and s.p.jumps_used == 2)
    s.wait_until(lambda: s.p.on_ground, 2.0)
    check("pulos reiniciados ao aterrissar", s.p.on_ground and s.p.jumps_used == 0)
    s.step({"jump"}, {"jump"})
    s.wait_until(lambda: s.p.vy >= 0, 1.0, held={"jump"})
    s.step({"jump"}, {"jump"})
    check("pulo duplo disponível de novo após aterrissar", s.p.jumps_used == 2)
    # teto não corrompe contagem
    s.goto("LB", 12, 14)
    s.step({"jump"}, {"jump"})
    s.run(0.05, held={"jump"})
    s.step({"jump"}, {"jump"})
    s.wait_until(lambda: s.p.on_ground, 1.0)
    check("batidas no teto não corrompem os pulos", s.p.jumps_used == 0)


def test_dash():
    s = Sim()
    s.goto("LA", 6, 14)
    s.p.facing = 1
    x0 = s.p.x
    s.step({"dash"}, {"dash"})
    check("dash começa no mesmo passo do comando", s.p.dashing)
    s.wait_until(lambda: not s.p.dashing, 1.0, held={"dash"})
    dist = s.p.x - x0
    check("dash sem direção usa o lado que o personagem olha", dist > 140, f"{dist:.0f} px")
    # segurar shift não reativa
    count = 1
    was = False
    for _ in range(int(1.5 / SIM_DT)):
        s.step({"dash"})
        if s.p.dashing and not was:
            count += 1
        was = s.p.dashing
    check("segurar Shift não gera dashes repetidos", count == 1)
    # recarga
    s.goto("LA", 10, 14)
    s.step({"dash"}, {"dash"})
    s.wait_until(lambda: not s.p.dashing, 1.0)
    s.step({"dash"}, {"dash"})
    blocked = not s.p.dashing
    s.wait_until(lambda: s.p.dash_cooldown <= 0, 2.0)
    s.step({"dash"}, {"dash"})
    check("recarga impede dash imediato e libera depois", blocked and s.p.dashing)
    # direção escolhida
    s.goto("LA", 20, 14)
    x0 = s.p.x
    s.step({"left", "dash"}, {"dash"})
    s.wait_until(lambda: not s.p.dashing, 1.0, held={"left"})
    check("dash na direção pressionada (esquerda)", s.p.x < x0 - 120)
    # dash aéreo: um por pulo
    s.goto("LA", 6, 14)
    s.step({"jump"}, {"jump"})
    s.run(0.1, held={"jump"})
    s.step({"right", "dash"}, {"dash"})
    first = s.p.dashing
    y_dash = s.p.y
    s.run(0.05, held={"right"})
    check("dash aéreo mantém altura (sem gravidade)", abs(s.p.y - y_dash) < 1e-6)
    s.wait_until(lambda: not s.p.dashing and s.p.dash_cooldown <= 0, 2.0)
    if not s.p.on_ground:
        s.step({"dash"}, {"dash"})
        second = s.p.dashing
    else:
        second = False
    check("só um dash por tempo no ar", first and not second)


def test_dash_attack_rules():
    s = Sim()
    s.goto("LA", 6, 14)
    s.step(pressed={"attack_heavy"})
    s.run(0.05)
    check("ataque pesado em preparação", s.p.attack is not None and s.p.attack.phase == "windup")
    s.step({"dash"}, {"dash"})
    check("dash cancela a preparação do golpe", s.p.dashing and s.p.attack is None)
    s.goto("LA", 6, 14)
    s.step(pressed={"attack_quick"})
    s.run(Combat.QUICK.windup + 0.01)
    s.step(pressed={"dash"})
    s.step()
    active_blocked = s.p.attack is not None and not s.p.dashing
    s.wait_until(lambda: s.p.dashing, 0.2)
    check("durante a fase ativa o dash espera (buffer) e sai em seguida", active_blocked and s.p.dashing)
    s.goto("LA", 6, 14)
    s.step({"dash"}, {"dash"})
    s.step(pressed={"attack_quick"})
    during = s.p.attack is None
    s.wait_until(lambda: s.p.attack is not None, 0.3)
    check("clique durante o dash vira golpe logo após o dash", during and s.p.attack is not None)


# ---------------------------------------------------------------------------
# Combate
# ---------------------------------------------------------------------------

def _dummy(s, kind=Patroller, dx=40):
    e = kind(s.p.cx + dx, s.p.bottom)
    e.think = lambda *a: None
    s.play.enemies = [e]
    return e


def test_attacks():
    s = Sim()
    s.goto("LA", 8, 14)
    e = _dummy(s)
    e.max_hp = e.hp = 99
    s.step(pressed={"attack_quick"})
    t_hit = None
    for i in range(int(0.6 / SIM_DT)):
        s.step()
        if e.hp < 99 and t_hit is None:
            t_hit = (i + 1) * SIM_DT
    check("ataque rápido causa seu dano uma única vez por golpe", e.hp == 99 - Combat.QUICK.damage,
          f"hp {e.hp}, acerto em {t_hit * 1000:.0f} ms" if t_hit else f"hp {e.hp}")
    # pesado
    s.goto("LA", 8, 14)
    e = _dummy(s)
    e.max_hp = e.hp = 99
    s.step(pressed={"attack_heavy"})
    t_hit = None
    for i in range(int(0.9 / SIM_DT)):
        s.step()
        if e.hp < 99 and t_hit is None:
            t_hit = (i + 1) * SIM_DT
    check("ataque pesado causa dano maior, uma vez", e.hp == 99 - Combat.HEAVY.damage, f"hp {e.hp}")
    check("pesado acerta depois (preparação maior)", t_hit and t_hit >= Combat.HEAVY.windup - 1e-6,
          f"{t_hit * 1000:.0f} ms" if t_hit else "")
    q, h = Combat.QUICK, Combat.HEAVY
    check("rápido: preparação e recuperação menores", q.windup < h.windup and q.recovery < h.recovery,
          f"rápido {q.total * 1000:.0f} ms total, pesado {h.total * 1000:.0f} ms")
    check("pesado: maior alcance e recuo", h.hit_w > q.hit_w and h.knockback > q.knockback)
    # alcance: inimigo a 60 px só o pesado alcança
    s.goto("LA", 8, 14)
    # borda do inimigo 55 px à frente do corpo: fora do rápido (44), dentro do pesado (66)
    e = _dummy(s, dx=s.p.w / 2 + 55 + Enemies.PATROLLER_SIZE[0] / 2)
    e.max_hp = e.hp = 99
    s.step(pressed={"attack_quick"})
    s.run(0.4)
    quick_far = e.hp
    s.step(pressed={"attack_heavy"})
    s.run(0.8)
    check("alvo distante: rápido erra, pesado acerta", quick_far == 99 and e.hp == 99 - h.damage,
          f"hp após rápido {quick_far}, após pesado {e.hp}")
    # repetição
    s.goto("LA", 8, 14)
    e = _dummy(s)
    e.max_hp = e.hp = 99
    e.knockback_resist = 0.0
    for _ in range(4):
        s.step(pressed={"attack_quick"})
        s.run(q.total + 0.01)
    check("ataques rápidos repetidos acertam um por clique", e.hp == 99 - 4 * Combat.QUICK.damage, f"hp {e.hp}")
    # segurar botão não repete
    s.goto("LA", 8, 14)
    e = _dummy(s)
    e.max_hp = e.hp = 99
    e.knockback_resist = 0.0
    s.step({"attack_quick"}, {"attack_quick"})
    s.run(1.0, held={"attack_quick"})
    check("segurar o botão não repete o golpe", e.hp == 99 - Combat.QUICK.damage)


def test_attack_exclusivity():
    s = Sim()
    s.goto("LA", 8, 14)
    s.step(pressed={"attack_quick"})
    s.run(Combat.QUICK.windup + Combat.QUICK.active + 0.02)   # já na recuperação
    s.step(pressed={"attack_heavy"})
    check("pesado durante rápido não sobrepõe", s.p.attack.spec.name == "quick")
    s.wait_until(lambda: s.p.attack is not None and s.p.attack.spec.name == "heavy", 0.5)
    check("pesado guardado no buffer sai ao fim do rápido", s.p.attack and s.p.attack.spec.name == "heavy")
    s.goto("LA", 8, 14)
    s.step(pressed={"attack_quick", "attack_heavy"})
    check("dois cliques no mesmo instante geram um só golpe", s.p.attack is not None)


def test_air_attack_and_walls():
    s = Sim()
    s.goto("LA", 8, 14)
    s.step({"jump"}, {"jump"})
    s.run(0.1, held={"jump"})
    s.step({"jump"}, {"attack_quick"})
    check("ataque rápido no ar", s.p.attack is not None and not s.p.on_ground)
    s.wait_until(lambda: s.p.on_ground, 2.0)
    check("aterrissa normalmente após atacar no ar", s.p.on_ground)
    # pesado colado na parede
    s.goto("LA", 1, 14)
    s.p.facing = -1
    s.step({"left"})
    s.step(pressed={"attack_heavy"})
    s.run(0.7, held={"left"})
    check("ataque pesado encostado na parede não empurra para dentro", s.p.left >= T - 1e-6)


def test_hurt():
    s = Sim()
    s.goto("LA", 8, 14)
    e = _dummy(s, dx=0)
    hp0 = s.p.hp
    s.step()
    check("contato com inimigo causa dano", s.p.hp == hp0 - 1)
    check("recuo ao receber dano", abs(s.p.vx) > 100 and s.p.vy < 0)
    e.x = s.p.x
    e.y = s.p.y
    s.run(0.5)
    check("invulnerabilidade temporária", s.p.hp == hp0 - 1)
    s.run(0.8)
    e.x, e.y = s.p.x, s.p.y
    e.vx = e.vy = 0
    s.step()
    check("invulnerabilidade acaba", s.p.hp == hp0 - 2)


def test_kill_enemy():
    s = Sim()
    s.goto("LA", 8, 14)
    e = Patroller(s.p.cx + 40, s.p.bottom)
    s.play.enemies = [e]
    for _ in range(6):
        s.p.facing = 1 if e.cx > s.p.cx else -1
        s.step(pressed={"attack_quick"})
        s.run(Combat.QUICK.total + 0.02)
        if not s.play.enemies:
            break
    check("inimigo pode ser derrotado", not s.play.enemies, f"hp do patrulheiro: {e.hp}")
    s.goto("LA", 8, 14)
    e = Patroller(s.p.cx + 40, s.p.bottom)
    e.think = lambda *a: None
    e.max_hp = e.hp = 99
    s.play.enemies = [e]
    x0 = e.x
    s.step(pressed={"attack_heavy"})
    s.run(0.5)
    check("pesado empurra e atordoa", e.x - x0 > 40 and e.stun > 0, f"recuo {e.x - x0:.0f} px")


# ---------------------------------------------------------------------------
# Inimigos
# ---------------------------------------------------------------------------

def test_patroller():
    s = Sim()
    s.goto("LA", 3, 14, enemies=True)
    s.play.enemies = [e for e in s.play.enemies if isinstance(e, Patroller)]
    e = s.play.enemies[0]
    s.p.place(3 * T, 14 * T)
    min_x, max_x, y0 = e.x, e.x, e.y
    turns = 0
    last = e.direction
    for _ in range(int(25 / SIM_DT)):
        s.step()
        s.p.place(2 * T, 14 * T)    # jogador parado longe
        s.p.invuln = 1
        min_x, max_x = min(min_x, e.x), max(max_x, e.x)
        if e.direction != last:
            turns += 1
            last = e.direction
    check("patrulheiro vira em parede/borda e não cai no buraco", e.alive and abs(e.y - y0) < 1 and turns >= 2,
          f"faixa x {min_x:.0f}..{max_x:.0f}, {turns} viradas")
    check("patrulheiro para na borda do buraco (col 28)", max_x + e.w <= 28 * T + 1)


def test_chaser():
    s = Sim()
    s.goto("LB", 30, 14, enemies=True)
    ch = next(e for e in s.play.enemies if isinstance(e, Chaser))
    s.p.place(ch.cx - 250, 14 * T)
    s.p.invuln = 99
    s.run(0.05)
    check("perseguidor detecta o jogador", ch.state in ("alert", "chase"))
    s.run(0.6)
    d0 = abs(ch.cx - s.p.cx)
    s.run(0.6)
    d1 = abs(ch.cx - s.p.cx)
    check("perseguidor se aproxima", ch.state == "chase" and d1 < d0, f"{d0:.0f} -> {d1:.0f} px")
    # jogador some do alcance (vai para o alto da sala) -> desiste
    s.p.place(ch.cx, 4 * T)
    s.p.vy = 0
    gave_up = s.wait_until(lambda: ch.state == "patrol", 3.0)
    check("perseguidor desiste quando perde o jogador", gave_up)
    # dano no jogador
    s2 = Sim()
    s2.goto("LB", 36, 14, enemies=True)
    ch = next(e for e in s2.play.enemies if isinstance(e, Chaser))
    hp0 = s2.p.hp
    hurt = s2.wait_until(lambda: s2.p.hp < hp0, 4.0)
    check("perseguidor causa dano ao alcançar", hurt)
    # respeita colisões: não cai no fosso
    s3 = Sim()
    s3.goto("LB", 30, 14, enemies=True)
    ch = next(e for e in s3.play.enemies if isinstance(e, Chaser))
    s3.p.place(20 * T, 14 * T)     # atrás do fosso
    s3.p.invuln = 99
    ok = True
    for _ in range(int(5 / SIM_DT)):
        s3.step()
        s3.p.invuln = 99
        if not ch.alive or ch.left < 23 * T - 1:
            ok = False
    check("perseguidor não se joga no fosso", ok)


def test_turret():
    s = Sim()
    s.goto("LC", 16, 20, enemies=True)
    s.play.enemies = [e for e in s.play.enemies if e.__class__.__name__ == "Turret"]
    s.p.invuln = 99
    fired = s.wait_until(lambda: len(s.play.projectiles.items) > 0, 3.0)
    check("torreta dispara quando o jogador está no alcance", fired)
    # projétil some ao bater no cenário/jogador
    s.p.place(3 * T, 14 * T)
    s.p.invuln = 99
    cleared = s.wait_until(lambda: len(s.play.projectiles.items) == 0, 5.0)
    check("projéteis são removidos após impacto", cleared)
    # limite de projéteis ativos
    for _ in range(40):
        s.play.projectiles.spawn(100, 100, 1, 0)
    check("limite de projéteis ativos", len(s.play.projectiles.items) <= 16)
    s.play.projectiles.clear()
    s.goto("LC", 16, 20)
    s.p.invuln = 0
    hp0 = s.p.hp
    s.play.projectiles.spawn(s.p.cx + 60, s.p.cy, -1, 0)
    s.run(0.5)
    check("projétil causa dano ao jogador", s.p.hp == hp0 - 1)
    s.goto("LC", 16, 20)
    s.p.invuln = 0
    hp0 = s.p.hp
    s.p.facing = 1
    s.play.projectiles.spawn(s.p.cx + 120, s.p.cy, -1, 0)
    s.run(0.25)
    s.step(pressed={"attack_quick"})
    s.run(0.4)
    check("ataque destrói projétil (defesa)", s.p.hp == hp0)


# ---------------------------------------------------------------------------
# Mapa: transições e alcance dos saltos
# ---------------------------------------------------------------------------

def test_dash_pit():
    def cross(start_tile, direction, use_dash):
        s = Sim()
        s.goto("LB", start_tile, 14)
        for i in range(int(2.0 / SIM_DT)):
            pressed = set()
            held = {direction}
            # dash quando o pé sai da borda (com coyote)
            if use_dash and not s.p.on_ground and not s.p.dashing and s.p.dash_ready:
                pressed.add("dash")
            if not use_dash and not s.p.on_ground and s.p.jumps_used == 0:
                pressed.add("jump")
                held.add("jump")
            s.step(held, pressed)
            if s.play.hazard_timer > 0 or s.p.hp < s.p.max_hp:
                return False
            if s.p.on_ground and (s.p.left >= 23 * T if direction == "right" else s.p.right <= 18 * T):
                return True
        return False
    check("fosso sob teto baixo: atravessa com dash (ida)", cross(14, "right", True))
    check("fosso sob teto baixo: atravessa com dash (volta)", cross(27, "left", True))
    check("fosso sob teto baixo: pulo comum não basta", not cross(14, "right", False))


# ---------------------------------------------------------------------------
# Estados
# ---------------------------------------------------------------------------

def test_hazard_and_death():
    s = Sim()
    s.goto("LB", 15, 14)
    safe = s.play.last_safe
    hp0 = s.p.hp
    s.wait_until(lambda: s.play.hazard_timer > 0, 3.0, held={"right"})
    check("espinhos causam dano", s.p.hp == hp0 - 1)
    s.wait_until(lambda: s.play.hazard_timer <= 0, 2.0)
    s.step()
    check("volta ao último chão seguro", s.p.on_ground and s.p.bottom == 14 * T and s.p.right <= 18 * T,
          f"seguro registrado em x={safe[1]:.0f}")
    check("velocidades zeradas ao voltar", abs(s.p.vx) < 1 and s.p.vy == 0)

    # morte e reaparecimento pelo fluxo do App
    s = Sim()
    s.goto("LB", 15, 14)
    s.p.hp = 1
    s.wait_until(lambda: not s.p.alive, 3.0, held={"right"})
    check("morte quando a vida chega a zero", not s.p.alive)
    app = s.app
    for _ in range(200):
        app.state.frame(1 / 60, app.input)
    check("tela de morte aparece", isinstance(app.state, DeathState))
    death = app.state
    death.play.respawn_at_bench()
    app.resume(death.play)
    p = app.state.player
    check("sem banco ainda: reaparece vivo, vida cheia, no início",
          p.alive and p.hp == p.max_hp and app.state.room.id == app.state.world.start_room)
    check("reaparece sem velocidade nem estados antigos",
          p.vx == 0 and p.vy == 0 and p.attack is None and not p.dashing and p.jumps_used == 0)


def test_framerate_independence():
    peaks = []
    for fps in (30, 60, 144, 240):
        s = Sim()
        s.goto("LA", 6, 14)
        app = s.app
        play = app.state
        y0 = play.player.bottom
        best = 0
        app.input.held = {"jump"}
        app.input.pressed = {"jump"}
        for _ in range(int(1.2 * fps)):
            play.frame(1 / fps, app.input)
            best = max(best, y0 - play.player.bottom)
        peaks.append(best)
    spread = max(peaks) - min(peaks)
    check("altura do pulo igual em 30/60/144/240 FPS", spread < 1.0,
          ", ".join(f"{p:.1f}" for p in peaks))



def test_drop_through():
    s = Sim()
    # plataforma de mão única baixa do laboratório: linha 11, colunas 5..8
    s.goto("LA", 6, 11)
    y0 = s.p.bottom
    s.step({"down"}, {"down"})
    s.run(0.4)
    check("S em cima da plataforma de mão única desce por ela", s.p.on_ground and s.p.bottom > y0 + T,
          f"de {y0:.0f} para {s.p.bottom:.0f}")
    s.goto("LA", 3, 14)
    y0 = s.p.bottom
    s.step({"down"}, {"down"})
    s.run(0.3)
    check("S em chão sólido não faz nada", s.p.on_ground and s.p.bottom == y0)
    s.goto("LA", 6, 11)
    s.run(0.5, held={"down"})
    check("segurar S não derruba de novo sem um novo toque (só o toque desce)", s.p.on_ground)
    # subir pela plataforma continua funcionando depois de descer
    s.goto("LA", 6, 14)
    s.step({"jump"}, {"jump"})
    s.wait_until(lambda: s.p.on_ground, 1.5, held={"jump"})
    check("plataforma volta a segurar depois", s.p.bottom == 11 * T)


def _target(s, kind, dx, dy):
    e = kind(s.p.cx + dx, s.p.bottom + dy)
    e.think = lambda *a: None
    e.max_hp = e.hp = 99
    s.play.enemies = [e]
    return e


def test_aimed_attacks():
    from src.enemies import Flier
    s = Sim()
    # voador logo acima da cabeça
    s.goto("LA", 6, 14)
    f = _target(s, Flier, 0, -70)
    s.step({"up"}, {"attack_quick"})
    s.run(0.3)
    check("W + ataque acerta inimigo acima", f.hp < 99)
    s.goto("LA", 6, 14)
    f = _target(s, Flier, 0, -70)
    s.step(pressed={"attack_quick"})
    s.run(0.3)
    check("sem W o ataque para a frente não acerta o de cima", f.hp == 99)
    # diagonal para cima à direita
    s.goto("LA", 6, 14)
    f = _target(s, Flier, 48, -60)
    s.step({"up", "right"}, {"attack_quick"})
    s.run(0.3)
    check("W + D + ataque acerta na diagonal", f.hp < 99)
    s.goto("LA", 6, 14)
    f = _target(s, Flier, -48, -60)
    s.step({"up", "left"}, {"attack_heavy"})
    s.run(0.5, held={"up"})
    check("diagonal para a esquerda com o pesado", f.hp < 99 and s.p.facing == -1)
    # golpe para baixo no ar com quique
    s.goto("LA", 3, 14)
    s.p.y -= 4 * T
    s.p.jumps_used = 2
    s.p.air_dashes_used = 1
    s.step()
    e = _target(s, Patroller, 0, 4 * T)
    e.y = s.p.bottom + 10
    s.step({"down"}, {"attack_quick"})
    s.wait_until(lambda: s.p.vy < 0, 0.3, held={"down"})
    check("S + ataque no ar acerta embaixo e quica", e.hp < 99 and s.p.vy < -300, f"vy {s.p.vy:.0f}")
    check("quique devolve pulo duplo e dash aéreo", s.p.jumps_used <= 1 and s.p.air_dashes_used == 0)
    # S + ataque no chão = ataque normal para a frente
    s.goto("LA", 6, 14)
    s.step({"down"}, {"attack_quick"})
    check("S + ataque no chão ataca para a frente", s.p.attack is not None and s.p.attack.aim[1] == 0)
    # quique em espinhos
    s.goto("LB", 15, 14)
    s.p.x = 19 * T
    s.p.y = 13 * T
    s.p.vy = 200
    s.step({"down"})
    s.step({"down"}, {"attack_quick"})
    bounced = s.wait_until(lambda: s.p.vy < -300, 0.4, held={"down"})
    check("golpe para baixo quica nos espinhos sem tomar dano", bounced and s.p.hp == s.p.max_hp)


TESTS = [
    test_walk, test_jump_variable, test_jump_moving, test_coyote, test_jump_buffer,
    test_walls_ceiling, test_no_tunneling, test_double_jump, test_dash, test_dash_attack_rules,
    test_attacks, test_attack_exclusivity, test_air_attack_and_walls, test_hurt, test_kill_enemy,
    test_patroller, test_chaser, test_turret, test_dash_pit, test_hazard_and_death,
    test_framerate_independence, test_drop_through, test_aimed_attacks,
]
