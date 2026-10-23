"""Visual do protagonista: escolhe a animação certa para o estado do jogador.

"Ele": espadachim (heroi.png, quadros 80x80, 16 por linha).
"Ela": feiticeira (feiticeira_parada.png e feiticeira_andando.png).
"""

import math

from . import sprites
from .sprites import Anim, pick

HERO = "personagens/heroi.png"


def _row(r, a, b):
    return list(range(r * 16 + a, r * 16 + b + 1))


class Skin:
    anchor = (0, 0)
    faces_right = True
    procedural_attacks = False   # True: pose de golpe gerada por código (sem quadros de ataque)
    motion_lean = False
    drawn_slashes = ()           # animações cujos quadros já têm o corte desenhado

    def anchor_x(self, name):
        return self.anchor[0]
    scale = 1

    def anims(self):
        raise NotImplementedError

    def get(self, name):
        if not hasattr(self, "_anims"):
            self._anims = self.anims()
        return self._anims.get(name) or self._anims["idle"]

    def has(self, name):
        self.get("idle")
        return name in self._anims


class HeroSkin(Skin):
    anchor = (38, 79)  # x do centro do corpo no quadro; y = pé (última linha)
    faces_right = True

    def anims(self):
        f = sprites.grid(HERO, 80, 80)
        return {
            "idle": Anim(pick(f, _row(0, 0, 11)), 9),
            "run": Anim(pick(f, _row(0, 12, 15) + _row(1, 0, 3)), 15),
            "jump": Anim(pick(f, _row(1, 8, 9)), 10, loop=False),
            "fall": Anim(pick(f, _row(1, 10, 12)), 10, loop=False),
            "land": Anim(pick(f, _row(1, 4, 6)), 18, loop=False),
            "quick": Anim(pick(f, _row(2, 0, 4)), 1, loop=False),
            "heavy": Anim(pick(f, _row(2, 5, 10)), 1, loop=False),
            "down": Anim(pick(f, [2 * 16 + 11]), 1),
            "up": Anim(pick(f, _row(2, 0, 2)), 1, loop=False),
            "dash": Anim(pick(f, _row(2, 12, 14)), 24),
            "hurt": Anim(pick(f, [1 * 16 + 14]), 1),
            "heal": Anim(pick(f, _row(1, 5, 7)), 6),
            "death": Anim(pick(f, _row(3, 0, 11)), 12, loop=False),
        }


class SorceressSkin(Skin):
    """Feiticeira.

    - parada/andando/partida: pacote original;
    - golpe rápido, golpe forte, dash, pulo, queda e aterrissagem: modelos da equipe
      (tools/importar_modelos.py -> feiticeira_modelos.png, quadros 112x72);
    - golpe para cima, diagonal, para baixo, dano e morte: tools/gerar_feiticeira.py
      (feiticeira_acoes.png, quadros 80x64).
    """
    anchor = (21, 54)
    faces_right = False
    procedural_attacks = False
    motion_lean = True
    drawn_slashes = ("quick", "heavy")      # quadros já trazem o corte desenhado
    MODELS = {"quick": (0, 0, 5), "heavy": (1, 0, 4), "dash": (2, 0, 6), "jump": (3, 1, 2), "fall": (3, 3, 1),
              "land": (3, 4, 2), "roll": (4, 0, 7)}
    ACTIONS = {"up": (2, 3), "down": (3, 2), "hurt": (7, 1), "death": (8, 5), "diag": (10, 4)}

    def anims(self):
        idle = sprites.grid("personagens/feiticeira_parada.png", 46, 55)
        walk = sprites.grid("personagens/feiticeira_andando.png", 45, 58)
        acts = sprites.grid("personagens/feiticeira_acoes.png", 80, 64)
        models = sprites.grid("personagens/feiticeira_modelos.png", 112, 72)
        anims = {
            "idle": Anim(idle, 10),
            "run_start": Anim(sprites.grid("personagens/feiticeira_partida.png", 45, 58), 24, loop=False),
            "run": Anim(walk, 26),
            "heal": Anim(idle, 4),
        }
        fps = {"jump": 9, "fall": 8, "dash": 40, "death": 7, "down": 10, "land": 16, "roll": 18}
        loop = ("fall", "dash", "down")
        cols = 7
        for name, (row, start, n) in self.MODELS.items():
            frames = models[row * cols + start:row * cols + start + n] if models else []
            anims[name] = Anim(frames, fps.get(name, 1), loop=name in loop)
        for name, (row, n) in self.ACTIONS.items():
            frames = acts[row * 5:row * 5 + n] if acts else []
            anims[name] = Anim(frames, fps.get(name, 1), loop=name in loop)
        return anims

    def anchor_x(self, name):
        if name in self.MODELS:
            return 56
        if name in self.ACTIONS:
            return 40
        return self.anchor[0]


SKINS = {"ele": HeroSkin(), "ela": SorceressSkin()}


def state_of(player):
    """Nome da animação e tempo dentro dela, a partir do estado do jogador."""
    if not player.alive:
        return "death", player.anim_time
    atk = player.attack
    if player.dashing:
        return "dash", player.anim_time
    if atk is not None:
        dy = atk.aim[1]
        if dy > 0:
            return "down", 0
        if dy < 0:
            return ("diag" if atk.aim[0] else "up"), atk.t / atk.spec.total
        name = atk.spec.name
        return ("heavy" if name == "heavy" else "quick"), atk.t / atk.spec.total
    if player.hurt_lock > 0:
        return "hurt", 0
    if player.healing:
        return "heal", player.anim_time
    if not player.on_ground:
        return ("jump" if player.vy < 0 else "fall"), player.anim_time
    if player.land_timer > 0:
        return "land", 0.12 - player.land_timer
    if abs(player.vx) > 20:
        return "run", player.anim_time
    return "idle", player.anim_time


def frame_for(skin, name, t):
    if name == "run":
        start = skin.get("run_start") if skin.has("run_start") else None
        if start is not None and start.frames:
            dur = len(start.frames) / start.fps
            if t < dur:
                return start.frame(t)        # transição parado -> correndo
            t -= dur
    anim = skin.get(name)
    if name in ("quick", "heavy", "up", "diag") and anim.frames:
        # golpes: o tempo vem normalizado (0..1) pela duração do ataque
        i = min(len(anim.frames) - 1, int(t * len(anim.frames)))
        return anim.frames[i]
    return anim.frame(t)


def bob(t):
    return math.sin(t * 6) * 1.5
