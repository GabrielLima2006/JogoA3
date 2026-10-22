"""Ferramentas comuns dos testes: simulação sem janela, salas-laboratório e busca de saltos."""

import itertools
import os
import sys
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import App  # noqa: E402
from src.config import Player as PC  # noqa: E402
from src.progress import Progress  # noqa: E402
from src.states import SIM_DT  # noqa: E402
from src.world import Room  # noqa: E402

T = 32
TMP_DIR = tempfile.mkdtemp(prefix="metroidvania_testes_")


# ---------------------------------------------------------------------------
# Salas-laboratório: geometria fixa usada nos testes de mecânica
# (não fazem parte do jogo; as do jogo mudam conforme o mapa evolui)
# ---------------------------------------------------------------------------

def _lab_a():
    r = ["#" * 40]
    r += ["#" + "." * 38 + "#"] * 3
    r.append("#" + "." * 25 + "####" + "." * 9 + "#")
    r += ["#" + "." * 38 + "#"] * 2
    r.append("#" + "." * 18 + "------" + "." * 14 + "#")
    r.append("#" + "." * 38 + "#")
    r.append("#" + "." * 10 + "#####" + "." * 23 + "#")
    r.append("#" + "." * 38 + "#")
    r.append("#" + "...." + "----" + "." * 30 + "#")
    r.append("#" + "." * 38 + "#")
    r.append("#" + "...." + "." * 13 + "g" + "." * 20 + "#")
    r.append("#" * 28 + "." * 6 + "#" * 6)
    r.append("#" * 28 + "." * 6 + "#" * 6)
    r.append("#" * 30 + "." * 4 + "#" * 6)
    return r


def _lab_b():
    r = ["#" * 50]
    r += ["#" + "." * 9 + "#" * 19 + "." * 20 + "#"] * 9
    r.append("#" + "." * 9 + "#" * 19 + "...." + "-----" + "." * 11 + "#")
    r.append("#" + "." * 9 + "#" * 19 + "." * 20 + "#")
    r.append("#" + "." * 48 + "#")
    r.append("#" + "." * 39 + "c" + "." * 8 + "#")
    r.append("#" * 18 + "." * 5 + "#" * 27)
    r.append("#" * 18 + "." * 5 + "#" * 27)
    r.append("#" * 18 + "^" * 5 + "#" * 27)
    return r


def _lab_c():
    w = 30
    r = ["#" * w]
    r += ["#" + "." * 28 + "#"] * 13
    r.append("#" * 10 + "." * 19 + "#")
    r += ["#" + "." * 28 + "#"] * 5
    r.append("#" + "." * 13 + "------" + "." * 9 + "#")
    r.append("#" + "." * 28 + "#")
    r.append("#" + "." * 27 + "t" + "#")
    r += ["#" + "." * 28 + "#"] * 2
    r.append("#" + "." * 7 + "------" + "." * 15 + "#")
    r += ["#" + "." * 28 + "#"] * 5
    r.append("#" + "." * 15 + "------" + "." * 7 + "#")
    r += ["#" + "." * 28 + "#"] * 4
    r.append("#" + "." * 7 + "g" + "." * 13 + "^" * 7 + "#")
    r += ["#" * w] * 3
    return r


LAB_ROOMS = {"LA": _lab_a, "LB": _lab_b, "LC": _lab_c}


class Sim:
    """Partida sem janela. `abilities`: conjunto inicial de habilidades."""

    def __init__(self, abilities=("dash", "double_jump"), progress=None, save_name="save.json", chapter=0):
        self.save_path = os.path.join(TMP_DIR, save_name)
        self.app = App(headless=True, save_path=self.save_path)
        pr = progress if progress is not None else Progress()
        if progress is None:
            pr.abilities = set(abilities)
            pr.chapter = chapter      # 0 = mundo de testes (cavernas), 1 = navio
        self.app.start_game(pr)
        self.play = self.app.state
        for rid, gen in LAB_ROOMS.items():
            self.play.world.add_room(Room(rid, "Laboratório " + rid, "cavernas", gen()))
        self.inp = self.app.input
        self.t = 0.0

    @property
    def p(self):
        return self.play.player

    @property
    def pr(self):
        return self.play.progress

    def step(self, held=(), pressed=(), released=()):
        self.inp.held = set(held)
        self.inp.pressed |= set(pressed)
        self.inp.released |= set(released)
        if self.play.fixed_update(SIM_DT, self.inp):
            self.inp.consume()
        self.t += SIM_DT
        # telas por cima (mensagem de item, chefe derrotado) são fechadas na hora
        if self.app.state is not self.play:
            self.app.resume(self.play)

    def run(self, seconds, held=(), first_pressed=()):
        n = max(1, int(round(seconds / SIM_DT)))
        for i in range(n):
            self.step(held, first_pressed if i == 0 else ())

    def goto(self, room_id, tile_x, floor_row, enemies=False, items=True):
        """Põe o jogador em pé sobre a linha `floor_row` (topo do tile), coluna `tile_x`."""
        room = self.play.world.rooms[room_id]
        if self.play.room is not room:
            self.play.load_room(room)
        if not enemies:
            self.play.enemies = []
            self.play.boss = None
        if not items:
            self.play.items = []
        self.play.projectiles.clear()
        self.play.coins = []
        room.crumbled.clear()
        self.play.crumble_timers.clear()
        self.play.riding = None
        self.play.mover_ignore = 0.0
        p = self.p
        hp = p.hp
        energy = p.energy
        p.reset_state()
        p.hp = hp
        p.energy = energy
        p.place(tile_x * T + T / 2, floor_row * T)
        self.play.effects.clear()
        self.play.hazard_timer = 0.0
        self.step()   # assenta no chão
        assert p.on_ground, f"goto: jogador não ficou no chão em {room_id} ({tile_x},{floor_row})"

    def wait_until(self, cond, max_time, held=()):
        n = int(max_time / SIM_DT)
        for _ in range(n):
            if cond():
                return True
            self.step(held)
        return cond()


RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    mark = "OK  " if cond else "FALHA"
    print(f"  [{mark}] {name}" + (f"  ({detail})" if detail else ""))
    return cond


def stands_on(room_id, row, c0, c1):
    def f(s):
        p = s.p
        return (s.play.room.id == room_id and p.on_ground and abs(p.bottom - row * T) < 1e-6
                and c0 * T <= p.cx <= (c1 + 1) * T)
    return f


def in_room(room_id):
    return lambda s: s.play.room.id == room_id


def try_reach(s, room_id, start_tile, start_floor, target, max_time=2.4):
    """Busca por força bruta uma sequência simples de comandos que leve ao alvo.

    Usa as habilidades que o jogador tem no momento. Retorna a descrição da
    sequência que funcionou ou None.
    """
    has_dj = "double_jump" in s.p.abilities
    has_dash = "dash" in s.p.abilities
    holds = (None, 0.15, 0.3, 0.45)
    dj_times = (None, 0.18, 0.26, 0.34, 0.42, 0.5) if has_dj else (None,)
    dash_times = (None, 0.05, 0.15, 0.25, 0.35, 0.5, 0.65) if has_dash else (None,)
    jump_holds = (None, 0.12)
    for run, direction, dir_delay, dir_release, jh, dj, dash_t in itertools.product(
            (0.0, 0.2, 0.4), ("left", "right"), (0.0, 0.1, 0.2), holds, jump_holds, dj_times, dash_times):
        if run and dir_delay:
            continue
        s.p.hp = s.p.max_hp
        s.goto(room_id, start_tile, start_floor, items=False)
        # corrida antes do salto
        for _ in range(int(run / SIM_DT)):
            s.step({direction})
        if not s.p.on_ground:
            continue
        n = int(max_time / SIM_DT)
        start_room = s.play.room.id
        for i in range(n):
            t = i * SIM_DT
            held = set()
            pressed = set()
            if jh is None or t < jh or (dj is not None and t >= dj):
                held.add("jump")
            if i == 0:
                pressed.add("jump")
            if t >= dir_delay and (dir_release is None or t < dir_delay + dir_release):
                held.add(direction)
            if dj is not None and abs(t - dj) < SIM_DT / 2:
                pressed.add("jump")
            if dash_t is not None and abs(t - dash_t) < SIM_DT / 2:
                pressed.add("dash")
            s.step(held, pressed)
            if s.p.hp < s.p.max_hp or s.play.hazard_timer > 0:
                break
            if i > 5 and target(s):
                return (f"corre {run}s, {direction}, atraso {dir_delay}s, solta {dir_release}, pulo {jh or 'cheio'}, "
                        f"duplo {dj}, dash {dash_t}")
            if s.p.on_ground and i > 20 and s.play.room.id == start_room:
                break
    return None


def full_hp(s):
    s.p.hp = s.p.max_hp
