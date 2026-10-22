"""Fonte em pixel art com acentos do português.

A fonte alagard (pixel, 16 px) não tem letras acentuadas. Aqui o texto é
desenhado com a letra base e os acentos (til, agudo, crase, circunflexo,
trema, cedilha) são pintados pixel a pixel por cima, no tamanho nativo.
Depois a imagem é ampliada por um fator inteiro, mantendo os pixels nítidos.
A classe imita a interface de pygame.font.Font (size/render), então o resto
do código não precisa saber dessa diferença.
"""

import unicodedata

import pygame

NATIVE_SIZE = 16          # tamanho em que a alagard foi desenhada
PAD_TOP = 4               # espaço para acentos de maiúsculas

# acento combinante -> pixels relativos (dx, dy) a partir do topo da letra
MARKS = {
    "̃": [(-2, 1), (-1, 0), (0, 1), (1, 1), (2, 0)],   # til
    "́": [(0, 1), (1, 0)],                              # agudo
    "̀": [(-1, 0), (0, 1)],                             # crase
    "̂": [(-1, 1), (0, 0), (1, 1)],                     # circunflexo
    "̈": [(-1, 0), (1, 0)],                             # trema
}
CEDILLA = "̧"
REPLACE = {"—": "-", "–": "-", "…": "...", "“": '"', "”": '"', "‘": "'", "’": "'"}


class PixelFont:
    def __init__(self, path, scale):
        self.base = pygame.font.Font(path, NATIVE_SIZE)
        self.scale = max(1, int(scale))
        self.ascent = self.base.get_ascent()
        self._cache = {}

    @staticmethod
    def _split(msg):
        """Separa cada caractere em (letra base, [acentos])."""
        out = []
        for ch in msg:
            ch = REPLACE.get(ch, ch)
            for c in ch:
                d = unicodedata.normalize("NFD", c)
                base, marks = d[0], [m for m in d[1:] if unicodedata.combining(m)]
                out.append((base, marks))
        return out

    def size(self, msg):
        parts = self._split(msg)
        plain = "".join(b for b, _ in parts)
        w, h = self.base.size(plain)
        return w * self.scale, (h + PAD_TOP) * self.scale

    def get_height(self):
        return self.size("Ág")[1]

    def render(self, msg, antialias, color, background=None):
        key = (msg, tuple(color))
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        parts = self._split(msg)
        plain = "".join(b for b, _ in parts)
        glyphs = self.base.render(plain, False, color)
        w, h = glyphs.get_size()
        surf = pygame.Surface((max(1, w), h + PAD_TOP + 2), pygame.SRCALPHA)
        surf.blit(glyphs, (0, PAD_TOP))
        x = 0
        for i, (base, marks) in enumerate(parts):
            adv = self.base.size(base)[0]
            if marks:
                metrics = self.base.metrics(base)[0]
                top = PAD_TOP + self.ascent - (metrics[3] if metrics else self.ascent)
                cx = x + ((metrics[0] + metrics[1]) // 2 if metrics else adv // 2)
                for m in marks:
                    if m == CEDILLA:
                        by = PAD_TOP + self.ascent
                        for dx, dy in ((0, 0), (1, 1), (0, 2)):
                            surf.set_at((min(w - 1, cx + dx), min(surf.get_height() - 1, by + dy)), color)
                    elif m in MARKS:
                        for dx, dy in MARKS[m]:
                            px, py = cx + dx, top - 3 + dy
                            if 0 <= px < w and 0 <= py < surf.get_height():
                                surf.set_at((px, py), color)
            x += adv
        if self.scale > 1:
            surf = pygame.transform.scale(surf, (surf.get_width() * self.scale, surf.get_height() * self.scale))
        if len(self._cache) > 600:
            self._cache.clear()
        self._cache[key] = surf
        return surf


def scale_for(size):
    """Converte o "tamanho em pontos" usado no código para um fator inteiro."""
    if size <= 20:
        return 1
    if size <= 46:
        return 2
    return 3
