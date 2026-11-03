"""Imagens do jogo: carregamento com cache, recorte de spritesheets e animações.

Todas as imagens ficam em assets/img/. As funções guardam o resultado em
cache, então podem ser chamadas a cada quadro sem custo.
"""

import os

import pygame

from .paths import asset

_images = {}
_frames = {}
_variants = {}


def image(*parts):
    """Carrega assets/img/<parts>. Retorna None se o arquivo não existir."""
    key = parts
    if key not in _images:
        path = asset("img", *parts)
        if not os.path.isfile(path):
            _images[key] = None
        else:
            img = pygame.image.load(path)
            _images[key] = img.convert_alpha() if pygame.display.get_init() and pygame.display.get_surface() else img
    return _images[key]


def grid(rel_path, fw, fh):
    """Recorta uma spritesheet em quadros de fw x fh, linha por linha."""
    key = ("grid", rel_path, fw, fh)
    if key not in _frames:
        sheet = image(*rel_path.split("/"))
        out = []
        if sheet is not None:
            w, h = sheet.get_size()
            for y in range(0, h - fh + 1, fh):
                for x in range(0, w - fw + 1, fw):
                    out.append(sheet.subsurface((x, y, fw, fh)).copy())
        _frames[key] = out
    return _frames[key]


def effect(name):
    """Quadros de um efeito do Super Pixel Effects (png + txt com os recortes)."""
    key = ("fx", name)
    if key not in _frames:
        sheet = image("efeitos", name + ".png")
        out = []
        path = asset("img", "efeitos", name + ".txt")
        if sheet is not None and os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                for line in f:
                    if "=" not in line:
                        continue
                    x, y, w, h = (int(v) for v in line.split("=")[1].split())
                    out.append(sheet.subsurface((x, y, w, h)).copy())
        _frames[key] = out
    return _frames[key]


def strip(rel_path, fw, fh=None):
    """Quadros de uma tira horizontal (efeitos sem txt)."""
    sheet = image(*rel_path.split("/"))
    if sheet is None:
        return []
    return grid(rel_path, fw, fh or sheet.get_height())


def crop(rel_path, rect):
    key = ("crop", rel_path, tuple(rect))
    if key not in _frames:
        sheet = image(*rel_path.split("/"))
        _frames[key] = sheet.subsurface(rect).copy() if sheet is not None else None
    return _frames[key]


# ---------------------------------------------------------------------------
# variações (espelhado, silhueta branca, escala) com cache
# ---------------------------------------------------------------------------

def variant(surf, flip=False, white=False, scale=1, tint=None):
    key = (id(surf), flip, white, scale, tint)
    v = _variants.get(key)
    if v is None:
        v = surf
        if scale != 1:
            v = pygame.transform.scale(v, (int(v.get_width() * scale), int(v.get_height() * scale)))
        if flip:
            v = pygame.transform.flip(v, True, False)
        if white:
            v = v.copy()
            v.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_MAX)
        elif tint is not None:
            v = v.copy()
            v.fill(tint, special_flags=pygame.BLEND_RGBA_MULT)
        if len(_variants) > 4000:
            _variants.clear()
        _variants[key] = v
    return v


def blit_anchor(dest, surf, x, y, anchor, flip=False, white=False, scale=1, tint=None):
    """Desenha `surf` com o ponto `anchor` (do quadro original) em (x, y) na tela."""
    ax, ay = anchor
    if flip:
        ax = surf.get_width() - 1 - ax
    v = variant(surf, flip, white, scale, tint)
    dest.blit(v, (round(x - ax * scale), round(y - ay * scale)))


class Anim:
    """Sequência de quadros com velocidade (quadros por segundo)."""

    def __init__(self, frames, fps=10, loop=True):
        self.frames = frames
        self.fps = fps
        self.loop = loop

    def frame(self, t):
        if not self.frames:
            return None
        i = int(t * self.fps)
        if self.loop:
            i %= len(self.frames)
        else:
            i = min(i, len(self.frames) - 1)
        return self.frames[i]

    def duration(self):
        return len(self.frames) / self.fps if self.fps else 0


def pick(frames, indices):
    return [frames[i] for i in indices if 0 <= i < len(frames)]


_POSES_META = None


def pose_anim(name, pose, phase):
    """Quadro animado gerado por tools/animar_pose.py a partir de uma pose parada `east`.

    `pose` é "idle", "walk" ou "attack"; `phase` vai de 0 a 1 no ciclo. O quadro olha para a
    direita. Retorna (quadro, âncora do pé) ou (None, None) se o personagem não tiver folha."""
    global _POSES_META
    if _POSES_META is None:
        import json
        try:
            with open(asset("img", "personagens", "anim_poses.json"), encoding="utf-8") as f:
                _POSES_META = json.load(f)
        except OSError:
            _POSES_META = {}
    meta = _POSES_META.get(name)
    if meta is None:
        return None, None
    fw, fh = meta["frame"]
    frames = grid(f"personagens/anim_{name}.png", fw, fh)
    if not frames:
        return None, None
    order = ("idle", "walk", "attack")
    row = order.index(pose) if pose in order else 0
    cols = max(meta["frames"].values())
    n = meta["frames"][order[row]]
    i = min(n - 1, int((phase % 1.0) * n))
    return frames[row * cols + i], tuple(meta["anchor"])
