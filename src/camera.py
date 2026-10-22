"""Câmera lateral suave, limitada aos limites da sala."""

import math

from .config import Camera as C, Display


class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.lookahead = 0.0
        self.view_w = Display.WIDTH
        self.view_h = Display.HEIGHT

    def _target(self, player, room):
        tx = player.cx + self.lookahead - self.view_w / 2
        ty = player.cy + C.VERTICAL_OFFSET - self.view_h / 2
        return self._clamp(tx, ty, room)

    def _clamp(self, x, y, room):
        if room.width <= self.view_w:
            x = (room.width - self.view_w) / 2
        else:
            x = min(max(x, 0.0), room.width - self.view_w)
        if room.height <= self.view_h:
            y = (room.height - self.view_h) / 2
        else:
            y = min(max(y, 0.0), room.height - self.view_h)
        return x, y

    def snap(self, player, room):
        self.lookahead = player.facing * C.LOOKAHEAD_X
        self.x, self.y = self._target(player, room)

    def update(self, dt, player, room):
        # lookahead acompanha a direção do olhar, sem trancos
        goal = player.facing * C.LOOKAHEAD_X
        self.lookahead += (goal - self.lookahead) * (1 - math.exp(-C.LOOKAHEAD_SHARPNESS * dt))
        tx, ty = self._target(player, room)
        self.x += (tx - self.x) * (1 - math.exp(-C.FOLLOW_SHARPNESS_X * dt))
        self.y += (ty - self.y) * (1 - math.exp(-C.FOLLOW_SHARPNESS_Y * dt))
        # nunca deixa o jogador sair da tela em quedas/dashes rápidos
        margin = 60
        self.x = min(max(self.x, player.right + margin - self.view_w), player.left - margin)
        self.y = min(max(self.y, player.bottom + margin - self.view_h), player.top - margin)
        self.x, self.y = self._clamp(self.x, self.y, room)

    def render_offset(self, shake=(0, 0)):
        return int(round(self.x + shake[0])), int(round(self.y + shake[1]))
