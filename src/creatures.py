"""Inimigos do navio e da ilha: mesmo comportamento dos inimigos-base, com visual próprio.

rato (patrulheiro) · gaivota (voador) · capanga encapuzado (perseguidor)
slime da maré (saltador) · canhão (torreta) · pirata de escudo (escudeiro) · caixa quebrável
"""

import pygame

from . import pixelart, sprites
from .enemies import Chaser, Enemy, Flier, Jumper, Patroller, Shield, Turret
from .skins import SKINS, frame_for

HENCH_TINT = (120, 80, 150, 255)     # capangas: roupa roxa do feiticeiro
PIRATE_TINT = (200, 110, 100, 255)


def _blit_bottom(surf, img, enemy, cam_x, cam_y, white=False, flip=False, scale=1):
    v = sprites.variant(img, flip, white, scale)
    surf.blit(v, v.get_rect(midbottom=(round(enemy.cx - cam_x), round(enemy.bottom - cam_y))))


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


class Hench(Chaser):
    """Capanga encapuzado: o herói com roupa roxa (mesmas animações)."""
    color = (150, 100, 180)

    def draw(self, surf, cam_x, cam_y):
        skin = SKINS["ele"]
        moving = abs(self.vx) > 20
        t = pygame.time.get_ticks() / 1000.0
        frame = frame_for(skin, "run" if moving else "idle", t)
        if frame is None:
            return super().draw(surf, cam_x, cam_y)
        flip = self.direction < 0
        sprites.blit_anchor(surf, frame, self.cx - cam_x, self.bottom - cam_y, (skin.anchor[0], 79),
                            flip=flip, white=self.flash > 0, tint=None if self.flash > 0 else HENCH_TINT)
        if self.state == "alert":
            fr = sprites.effect("alerta")
            if fr:
                a = fr[int(self.timer * 20) % len(fr)]
                surf.blit(a, a.get_rect(midbottom=(round(self.cx - cam_x), round(self.top - 18 - cam_y))))
        self.draw_hp(surf, cam_x, cam_y)


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


class ShieldPirate(Shield):
    color = (200, 110, 100)

    def draw(self, surf, cam_x, cam_y):
        skin = SKINS["ele"]
        t = pygame.time.get_ticks() / 1000.0
        name = "quick" if self.state == "bash" else ("run" if abs(self.vx) > 20 else "idle")
        frame = frame_for(skin, name, 0.5 if name == "quick" else t)
        flip = self.direction < 0
        sprites.blit_anchor(surf, frame, self.cx - cam_x, self.bottom - cam_y, (skin.anchor[0], 79),
                            flip=flip, white=self.flash > 0,
                            tint=None if self.flash > 0 else (PIRATE_TINT if self.state != "windup" else (255, 230, 200, 255)))
        if not self.guard_broken and self.stun <= 0:
            sx = self.cx + self.direction * (self.w / 2 + 3) - cam_x
            r = pygame.Rect(0, 0, 10, self.h - 4)
            r.midbottom = (round(sx), round(self.bottom - 2 - cam_y))
            pygame.draw.rect(surf, (120, 86, 52), r, border_radius=4)
            pygame.draw.rect(surf, (200, 180, 120), r, 2, border_radius=4)
            pygame.draw.circle(surf, (220, 200, 140), r.center, 2)
        self.draw_hp(surf, cam_x, cam_y)


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


TYPES = {"g": Rat, "f": Gull, "c": Hench, "j": TideSlime, "t": Cannon, "s": ShieldPirate, "k": Crate}
