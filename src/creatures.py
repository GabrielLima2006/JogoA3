"""Inimigos do navio e da ilha: mesmo comportamento dos inimigos-base, com visual próprio.

rato (patrulheiro) · gaivota (voador) · capanga encapuzado (perseguidor)
slime da maré (saltador) · canhão (torreta) · pirata de escudo (escudeiro) · caixa quebrável
"""

import pygame

from . import pixelart, sprites
import json
import math

from .enemies import Chaser, Enemy, Flier, Jumper, Patroller, Shield, Turret, approach, ground_ahead, wall_ahead
from .config import Enemies as E
from .paths import asset


def _blit_human(surf, img, enemy, cam_x, cam_y, white=False):
    """Humanos do pixelart têm 3 px vazios abaixo das botas."""
    v = sprites.variant(img, False, white, 1)
    surf.blit(v, v.get_rect(midbottom=(round(enemy.cx - cam_x), round(enemy.bottom - cam_y + 3))))


def _blit_bottom(surf, img, enemy, cam_x, cam_y, white=False, flip=False, scale=1):
    v = sprites.variant(img, flip, white, scale)
    surf.blit(v, v.get_rect(midbottom=(round(enemy.cx - cam_x), round(enemy.bottom - cam_y))))


# ---------------------------------------------------------------------------
# Criaturas da ilha e do templo (modelos da equipe: personagens/npcs.png)
# ---------------------------------------------------------------------------

_NPC_META = None


def npc_frame(name):
    """Quadro do modelo `name` (olhando para a esquerda) e a âncora do pé."""
    global _NPC_META
    if _NPC_META is None:
        try:
            with open(asset("img", "personagens", "npcs.json"), encoding="utf-8") as f:
                _NPC_META = json.load(f)
        except OSError:
            _NPC_META = {"rows": {}, "frame": [128, 96], "anchor": [64, 95]}
    row = _NPC_META["rows"].get(name)
    fw, fh = _NPC_META["frame"]
    frames = sprites.grid("personagens/npcs.png", fw, fh)
    if row is None or not frames:
        return None, (0, 0)
    return frames[row[0]], tuple(_NPC_META["anchor"])


def draw_model(surf, name, x, foot_y, t, facing, moving=False, white=False, lean=0.0, float_amp=0.0):
    """Desenha um modelo parado com vida: respira, balança ao andar, inclina ao atacar, flutua."""
    img, (ax, ay) = npc_frame(name)
    if img is None:
        return
    flip = facing > 0                      # os modelos olham para a esquerda
    v = sprites.variant(img, flip, white)
    if moving:
        sy = 1.0 + 0.05 * math.sin(t * 16)
        bob = abs(math.sin(t * 8)) * 2
    else:
        sy = 1.0 + 0.025 * math.sin(t * 3)
        bob = 0
    lift = math.sin(t * 2.5) * float_amp
    w, h = v.get_size()
    if abs(sy - 1) > 0.01:
        v = pygame.transform.scale(v, (w, max(1, round(h * sy))))
    if lean:
        v = pygame.transform.rotate(v, -lean * facing)
    r = v.get_rect(midbottom=(round(x), round(foot_y - bob + lift + (h - ay - 1) * sy)))
    surf.blit(v, r)


class _ModelMixin:
    model = ""
    float_amp = 0.0

    def draw(self, surf, cam_x, cam_y):
        t = pygame.time.get_ticks() / 1000.0 + (self.x % 97) * 0.1
        lean = 10 if getattr(self, "state", "") in ("windup", "bash", "chase", "lunge") else 0
        draw_model(surf, self.model, self.cx - cam_x, self.bottom - cam_y, t, self.direction,
                   abs(self.vx) > 20, self.flash > 0, lean, self.float_amp)
        if getattr(self, "state", "") == "alert":
            fr = sprites.effect("alerta")
            if fr:
                a = fr[int(self.timer * 20) % len(fr)]
                surf.blit(a, a.get_rect(midbottom=(round(self.cx - cam_x), round(self.top - 22 - cam_y))))
        self.draw_hp(surf, cam_x, cam_y)


class Wolf(_ModelMixin, Patroller):
    """Lobo da floresta: patrulha rápido."""
    model = "lobo"
    max_hp = E.PATROLLER_HP + 4

    def think(self, dt, room, player, ctx):
        if self.on_ground:
            if wall_ahead(self, room, self.direction) or not ground_ahead(self, room, self.direction):
                self.direction *= -1
        self.vx = approach(self.vx, self.direction * E.PATROLLER_SPEED * 2.0, 1600 * dt)


class Goblin(_ModelMixin, Chaser):
    model = "goblin"


class Mummy(_ModelMixin, Chaser):
    """Múmia do templo: mais lenta e resistente."""
    model = "mumia"
    max_hp = E.CHASER_HP + 6


class Imp(_ModelMixin, Flier):
    model = "diabrete"
    float_amp = 3.0


class Spirit(_ModelMixin, Flier):
    model = "espirito"
    float_amp = 4.0


class Lich(_ModelMixin, Turret):
    model = "lich"
    float_amp = 2.0


class DarkKnight(_ModelMixin, Shield):
    model = "cavaleiro_negro"


class Rat(Patroller):
    color = (150, 140, 146)

    def draw(self, surf, cam_x, cam_y):
        phase = (self.x * 0.05) % 1.0
        img = pixelart.rat(phase, self.direction)
        _blit_bottom(surf, img, self, cam_x, cam_y, white=self.flash > 0)
        self.draw_hp(surf, cam_x, cam_y)


class Gull(Flier):
    color = (236, 236, 240)

    def draw(self, surf, cam_x, cam_y):
        img = pixelart.gull(self.t * 1.6 % 1.0, self.direction)
        v = sprites.variant(img, False, self.flash > 0)
        surf.blit(v, v.get_rect(center=(round(self.cx - cam_x), round(self.cy - cam_y))))
        if self.state == "alert":
            fr = sprites.effect("alerta")
            if fr:
                a = fr[int(self.timer * 20) % len(fr)]
                surf.blit(a, a.get_rect(midbottom=(round(self.cx - cam_x), round(self.top - 4 - cam_y))))
        self.draw_hp(surf, cam_x, cam_y)


class Hench(_ModelMixin, Chaser):
    """Capanga do navio: ladino encapuzado (modelos da equipe)."""
    model = "ladino"


class TideSlime(Jumper):
    """Slime da maré amaldiçoada (slime.png: linha 0 parado, linha 2 salto)."""
    color = (70, 140, 230)

    def draw(self, surf, cam_x, cam_y):
        frames = sprites.grid("inimigos/slime.png", 48, 32)
        if not frames:
            return super().draw(surf, cam_x, cam_y)
        t = pygame.time.get_ticks() / 1000.0
        if self.state == "air":
            img = frames[12 + min(3, int((0.4 - min(0.4, abs(self.vy) / 1800)) * 10))]
        elif self.state == "crouch":
            img = frames[12]
        else:
            img = frames[int(t * 8) % 6]
        _blit_bottom(surf, img, self, cam_x, cam_y, white=self.flash > 0, flip=self.direction > 0)
        self.draw_hp(surf, cam_x, cam_y)


class Cannon(Turret):
    color = (90, 90, 100)

    def draw(self, surf, cam_x, cam_y):
        flash = self.telegraph > 0 and int(self.telegraph * 16) % 2 == 0
        img = pixelart.cannon(self.direction, flash)
        _blit_bottom(surf, img, self, cam_x, cam_y, white=self.flash > 0)
        self.draw_hp(surf, cam_x, cam_y)


class ShieldPirate(_ModelMixin, Shield):
    """Guarda de escudo do navio. O escudo desenhado no modelo bloqueia golpes rápidos de frente."""
    model = "cavaleiro_escudo"


class Crate(Enemy):
    """Caixa de carga: quebra com um golpe e solta moedas."""
    color = (150, 104, 60)
    max_hp = 1
    drop = "crate"
    contact_damage = 0
    knockback_resist = 0.0

    def __init__(self, foot_x, foot_y):
        super().__init__(foot_x, foot_y, 28, 26)

    def draw(self, surf, cam_x, cam_y):
        _blit_bottom(surf, pixelart.crate(), self, cam_x, cam_y, white=self.flash > 0)


# mesma letra do mapa, visual e comportamento de acordo com a zona da sala
ZONE_TYPES = {
    "ilha": {"g": Wolf, "c": Goblin, "f": Imp},
    "ruínas": {"g": Wolf, "c": Goblin, "f": Imp, "s": DarkKnight},
    "templo": {"c": Mummy, "f": Spirit, "t": Lich, "s": DarkKnight},
}


TYPES = {"g": Rat, "f": Gull, "c": Hench, "j": TideSlime, "t": Cannon, "s": ShieldPirate, "k": Crate}
