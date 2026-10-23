"""Visual do protagonista: escolhe a animação certa para o estado do jogador.

"Ele": espadachim (heroi.png, quadros 80x80, 16 por linha).
"Ela": feiticeira de chifres nova (heroina.png, de tools/gerar_heroina.py). A feiticeira antiga
(feiticeira_parada/andando + ações de tools/gerar_feiticeira.py) fica como "feiticeira_antiga".
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
    """Feiticeira: parada/andando/partida do pacote + ações de tools/gerar_feiticeira.py
    (feiticeira_acoes.png, quadros 96x72). Os modelos importados de feiticeira_modelos.png
    ficaram de fora a pedido do Gabriel."""
    anchor = (21, 54)
    faces_right = False
    procedural_attacks = False
    motion_lean = True
    drawn_slashes = ()
    ACTION_ANCHOR_X = 48
    ACTIONS = {"quick": (0, 4), "heavy": (1, 5), "up": (2, 3), "down": (3, 2), "jump": (4, 2),
               "fall": (5, 2), "dash": (6, 2), "hurt": (7, 1), "death": (8, 5), "land": (9, 1), "diag": (10, 4)}

    def anims(self):
        idle = sprites.grid("personagens/feiticeira_parada.png", 46, 55)
        walk = sprites.grid("personagens/feiticeira_andando.png", 45, 58)
        acts = sprites.grid("personagens/feiticeira_acoes.png", 96, 72)
        anims = {
            "idle": Anim(idle, 10),
            "run_start": Anim(sprites.grid("personagens/feiticeira_partida.png", 45, 58), 24, loop=False),
            "run": Anim(walk, 26),
            "heal": Anim(idle, 4),
        }
        fps = {"jump": 8, "fall": 8, "dash": 20, "death": 7, "down": 10}
        for name, (row, n) in self.ACTIONS.items():
            frames = acts[row * 5:row * 5 + n] if acts else []
            anims[name] = Anim(frames, fps.get(name, 1), loop=name in ("jump", "fall", "dash", "down"))
        return anims

    def anchor_x(self, name):
        return self.ACTION_ANCHOR_X if name in self.ACTIONS else self.anchor[0]


class HeroineSkin(Skin):
    """Protagonista nova (modelo 32x32 do PixelLab feito pelo Gabriel, vista "west" em 2x).
    Todos os quadros vêm de tools/gerar_heroina.py (heroina.png, 96x80, pé em x = 48)."""
    anchor = (48, 79)
    faces_right = False
    procedural_attacks = False
    motion_lean = False          # os quadros já inclinam; girar pixel art 2x deixaria serrilhado
    drawn_slashes = ("quick", "heavy")
    ROWS = ["idle", "run_start", "run", "jump", "fall", "land", "quick", "heavy", "up", "diag", "down",
            "dash", "hurt", "death", "heal"]
    FPS = {"idle": 6, "run_start": 20, "run": 14, "jump": 8, "fall": 8, "dash": 20, "death": 7, "down": 10,
           "heal": 4}
    LOOP = ("idle", "run", "jump", "fall", "dash", "down", "heal")

    def anims(self):
        f = sprites.grid("personagens/heroina.png", 96, 80)
        cols = 8
        anims = {}
        for r, name in enumerate(self.ROWS):
            frames = [fr for fr in f[r * cols:(r + 1) * cols] if fr.get_bounding_rect().w]
            anims[name] = Anim(frames, self.FPS.get(name, 1), loop=name in self.LOOP)
        return anims


SKINS = {"ele": HeroSkin(), "ela": HeroineSkin(), "feiticeira_antiga": SorceressSkin()}


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
