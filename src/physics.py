"""Corpo físico AABB e resolução de colisões contra o tilemap.

Estratégia: movimento separado por eixo (X depois Y), dividido em sub-passos de
no máximo Physics.MAX_STEP px. Assim nada atravessa tiles mesmo em velocidades
altas (dash, queda máxima, recuo forte).
"""

import math

from .config import Physics, World

T = World.TILE
EPS = 1e-4


class Body:
    def __init__(self, x, y, w, h):
        self.x = float(x)   # canto superior esquerdo, coordenadas da sala
        self.y = float(y)
        self.w = w
        self.h = h
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.hit_left = False
        self.hit_right = False
        self.hit_ceiling = False

    # --- geometria ---
    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.w

    @property
    def top(self):
        return self.y

    @property
    def bottom(self):
        return self.y + self.h

    @property
    def cx(self):
        return self.x + self.w * 0.5

    @property
    def cy(self):
        return self.y + self.h * 0.5

    def rect_tuple(self):
        return (self.x, self.y, self.w, self.h)

    def overlaps(self, other):
        return rects_overlap(self.rect_tuple(), other.rect_tuple())


def rects_overlap(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def tile_span(a, size):
    """Índices de tile cobertos pelo intervalo [a, a+size)."""
    return int(math.floor(a / T)), int(math.floor((a + size - EPS) / T))


def move_and_collide(body, dx, dy, tilemap, oob_solid=False, corner_correction=0, step_up=0,
                     ignore_oneway=False):
    """Move o corpo resolvendo colisões. Atualiza flags de contato.

    step_up: se o corpo bater de lado numa quina que está até N px acima dos
    pés, ele sobe na quina em vez de parar (perdão de borda).
    """
    body.hit_left = body.hit_right = body.hit_ceiling = False
    landed = False
    steps = max(1, int(math.ceil(max(abs(dx), abs(dy)) / Physics.MAX_STEP)))
    sx = dx / steps
    sy = dy / steps
    for _ in range(steps):
        if sx:
            if _step_x(body, sx, tilemap, oob_solid, step_up):
                sx = 0.0
        if sy:
            res = _step_y(body, sy, tilemap, oob_solid, corner_correction, ignore_oneway)
            if res == "floor":
                landed = True
                sy = 0.0
            elif res == "ceiling":
                sy = 0.0
    body.on_ground = landed
    return landed


def _step_x(body, sx, tilemap, oob_solid, step_up=0):
    body.x += sx
    y0, y1 = tile_span(body.y, body.h)
    if sx > 0:
        tx = int(math.floor((body.x + body.w - EPS) / T))
    else:
        tx = int(math.floor(body.x / T))
    blocked = [ty for ty in range(y0, y1 + 1) if tilemap.is_solid(tx, ty, oob_solid)]
    if not blocked:
        return False
    if step_up:
        top = min(blocked) * T
        rise = body.bottom - top
        if 0 < rise <= step_up and not _overlaps_solid(body.x, top - body.h, body.w, body.h, tilemap, oob_solid):
            body.y = top - body.h
            return False
    if sx > 0:
        body.x = tx * T - body.w
        body.hit_right = True
    else:
        body.x = (tx + 1) * T
        body.hit_left = True
    return True


def _overlaps_solid(x, y, w, h, tilemap, oob_solid):
    x0, x1 = tile_span(x, w)
    y0, y1 = tile_span(y, h)
    return any(tilemap.is_solid(tx, ty, oob_solid) for ty in range(y0, y1 + 1) for tx in range(x0, x1 + 1))


def _step_y(body, sy, tilemap, oob_solid, corner_correction, ignore_oneway=False):
    prev_bottom = body.bottom
    body.y += sy
    x0, x1 = tile_span(body.x, body.w)
    if sy > 0:
        ty = int(math.floor((body.y + body.h - EPS) / T))
        for tx in range(x0, x1 + 1):
            if tilemap.is_solid(tx, ty, oob_solid) or (
                not ignore_oneway and tilemap.is_oneway(tx, ty) and prev_bottom <= ty * T + EPS
            ):
                body.y = ty * T - body.h
                return "floor"
    else:
        ty = int(math.floor(body.y / T))
        hit = [tx for tx in range(x0, x1 + 1) if tilemap.is_solid(tx, ty, oob_solid)]
        if hit:
            if corner_correction and _try_corner_correct(body, ty, tilemap, oob_solid, corner_correction):
                return None
            body.y = (ty + 1) * T
            body.hit_ceiling = True
            return "ceiling"
    return None


def _try_corner_correct(body, ty, tilemap, oob_solid, max_shift):
    """Se só a quina da cabeça raspou no teto, empurra o corpo de lado."""
    for shift in range(1, max_shift + 1):
        for direction in (-1, 1):
            nx = body.x + direction * shift
            if not _overlaps_solid(nx, body.y, body.w, body.h, tilemap, oob_solid):
                body.x = nx
                return True
    return False


def is_supported(body, tilemap):
    """Há chão sólido/plataforma logo abaixo dos dois pés?"""
    ty = int(math.floor((body.bottom + 1) / T))
    lx = int(math.floor((body.x + 1) / T))
    rx = int(math.floor((body.right - 1) / T))
    return all(tilemap.is_solid(tx, ty) or tilemap.is_oneway(tx, ty) for tx in (lx, rx))


def standing_only_on_oneway(body, tilemap):
    """Os pés estão apoiados apenas em plataformas de mão única (dá para descer)."""
    ty = int(math.floor((body.bottom + 1) / T))
    x0, x1 = tile_span(body.x, body.w)
    tiles = range(x0, x1 + 1)
    return (any(tilemap.is_oneway(tx, ty) for tx in tiles)
            and not any(tilemap.is_solid(tx, ty) for tx in tiles))


def ground_ahead(body, tilemap, direction):
    """Existe chão um pouco à frente (para inimigos não caírem de bordas)."""
    probe_x = body.right + 2 if direction > 0 else body.left - 2
    tx = int(math.floor(probe_x / T))
    ty = int(math.floor((body.bottom + 2) / T))
    return tilemap.is_solid(tx, ty, True) or tilemap.is_oneway(tx, ty)


def wall_ahead(body, tilemap, direction):
    probe_x = body.right + 1 if direction > 0 else body.left - 1
    tx = int(math.floor(probe_x / T))
    y0, y1 = tile_span(body.y, body.h)
    return any(tilemap.is_solid(tx, ty, True) for ty in range(y0, y1 + 1))


def line_of_sight(tilemap, x0, y0, x1, y1):
    dist = math.hypot(x1 - x0, y1 - y0)
    steps = max(1, int(dist / (T * 0.4)))
    for i in range(1, steps):
        t = i / steps
        tx = int(math.floor((x0 + (x1 - x0) * t) / T))
        ty = int(math.floor((y0 + (y1 - y0) * t) / T))
        if tilemap.is_solid(tx, ty, True):
            return False
    return True
