"""Interface: textos, painéis, menus, HUD, barra de chefe, inventário e mapa.

Tudo é desenhado em "pixels de 2": molduras, ícones e o orbe seguem a mesma
escala da arte do jogo, e o texto usa a fonte pixel (ver fonte.py).
"""

import math
import os

import pygame

from .config import Colors, Dash, Display, Energy, Progression, World
from .fonte import PixelFont, scale_for
from .input import CONTROLS_TEXT
from .paths import asset

_fonts = {}

TITLE_FONT = asset("fonts", "alagard.ttf")

W, H = Display.WIDTH, Display.HEIGHT
P = 2                       # tamanho do "pixel" das molduras e ícones

# paleta da interface (molduras douradas sobre azul-noite, como as placas do navio)
INK = (12, 10, 16)
PANEL = (18, 20, 34)
PANEL_HI = (30, 34, 54)
GOLD = (214, 178, 106)
GOLD_DARK = (112, 82, 46)
GOLD_LIGHT = (255, 230, 168)
SELECTED = (255, 226, 160)
MUTED = (88, 92, 112)
PARCHMENT = (238, 226, 190)


def _now():
    return pygame.time.get_ticks() / 1000.0


def _mix(a, b, k):
    return tuple(int(x + (y - x) * k) for x, y in zip(a, b))


def ease_out(k):
    k = max(0.0, min(1.0, k))
    return 1 - (1 - k) ** 3


# ---------------------------------------------------------------------------
# Texto
# ---------------------------------------------------------------------------

def font(size, title=False):
    """Fonte em pixel art (alagard + acentos desenhados). `title` usa um fator maior."""
    key = (size, title)
    if key not in _fonts:
        if os.path.isfile(TITLE_FONT):
            k = scale_for(size) + (1 if title and size > 40 else 0)
            _fonts[key] = PixelFont(TITLE_FONT, k)
        else:
            _fonts[key] = pygame.font.Font(None, size)
    return _fonts[key]


_title_cache = {}


def _title_image(msg, size, color):
    """Título com degradê vertical (claro em cima, escuro embaixo), contorno e sombra."""
    key = (msg, size, tuple(color))
    img = _title_cache.get(key)
    if img is not None:
        return img
    f = font(size, True)
    k = getattr(f, "scale", 1)
    white = f.render(msg, False, (255, 255, 255))
    dark = f.render(msg, False, INK)
    w, h = white.get_size()
    grad = pygame.Surface((w, h), pygame.SRCALPHA)
    top, bottom = _mix(color, (255, 255, 255), 0.45), _mix(color, INK, 0.38)
    for y in range(0, h, k):
        t = y / max(1, h - 1)
        col = _mix(top, color, t * 2) if t < 0.5 else _mix(color, bottom, (t - 0.5) * 2)
        grad.fill((*col, 255), (0, y, w, k))
    fill = white.copy()
    fill.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    img = pygame.Surface((w + 2 * k, h + 3 * k), pygame.SRCALPHA)
    img.blit(dark, (k, 3 * k))          # sombra
    for dx, dy in ((0, k), (2 * k, k), (k, 0), (k, 2 * k)):
        img.blit(dark, (dx, dy))        # contorno
    img.blit(fill, (k, k))
    if len(_title_cache) > 200:
        _title_cache.clear()
    _title_cache[key] = img
    return img


def text(surf, msg, size, pos, color=Colors.UI_TEXT, anchor="topleft", title=False, shadow=True,
         outline=False, alpha=None):
    """Escreve texto; por padrão com sombra de 1 pixel para contraste em qualquer fundo.

    `title` usa a fonte maior com degradê e contorno. `outline` contorna o texto
    inteiro (bom sobre o cenário). `alpha` (0-255) desenha transparente.
    """
    if title:
        img = _title_image(msg, size, color)
        if alpha is not None and alpha < 255:
            img = img.copy()
            img.set_alpha(max(0, int(alpha)))
        k = getattr(font(size, True), "scale", 1)
        rect = img.get_rect(**{anchor: pos})
        surf.blit(img, rect)
        return pygame.Rect(rect.x + k, rect.y + k, rect.w - 2 * k, rect.h - 3 * k)
    f = font(size)
    k = getattr(f, "scale", 1)
    img = f.render(msg, False, color)
    rect = img.get_rect(**{anchor: pos})
    if alpha is not None and alpha < 255:
        img = img.copy()
        img.set_alpha(max(0, int(alpha)))
    if outline or shadow:
        dark = f.render(msg, False, INK)
        if alpha is not None and alpha < 255:
            dark = dark.copy()
            dark.set_alpha(max(0, int(alpha)))
        if outline:
            for dx, dy in ((-k, 0), (k, 0), (0, -k), (0, k), (k, k)):
                surf.blit(dark, rect.move(dx, dy))
        else:
            surf.blit(dark, rect.move(k, k))
    surf.blit(img, rect)
    return rect


def wrap_lines(msg, size, width):
    """Quebra o texto em linhas que cabem em `width` pixels."""
    words, line, out = msg.split(), "", []
    for w in words:
        test = (line + " " + w).strip()
        if font(size).size(test)[0] > width and line:
            out.append(line)
            line = w
        else:
            line = test
    if line:
        out.append(line)
    return out


def line_height(size):
    return font(size).size("Ág")[1]


def wrap_text(surf, msg, size, x, y, width, color=Colors.UI_TEXT, line_gap=4):
    """Escreve texto quebrando linhas pela largura. Retorna o y final."""
    step = max(size, line_height(size) - 2) + line_gap
    for line in wrap_lines(msg, size, width):
        text(surf, line, size, (x, y), color)
        y += step
    return y


def dim(surf, alpha=160):
    s = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    s.fill((8, 9, 14, alpha))
    surf.blit(s, (0, 0))


_vignettes = {}


def vignette(surf, strength=170):
    """Escurece as bordas da tela (foco no centro)."""
    key = (surf.get_size(), strength)
    v = _vignettes.get(key)
    if v is None:
        w, h = surf.get_size()
        small = pygame.Surface((w // 8, h // 8), pygame.SRCALPHA)
        sw, sh = small.get_size()
        for y in range(sh):
            for x in range(sw):
                dx, dy = (x - sw / 2) / (sw / 2), (y - sh / 2) / (sh / 2)
                d = min(1.0, max(0.0, (dx * dx * 0.7 + dy * dy) ** 0.5 - 0.45) / 0.75)
                small.set_at((x, y), (4, 4, 10, int(strength * d * d)))
        v = pygame.transform.smoothscale(small, (w, h))
        _vignettes[key] = v
    surf.blit(v, (0, 0))


# ---------------------------------------------------------------------------
# Molduras, ornamentos e teclas
# ---------------------------------------------------------------------------

def _edges(surf, r, col, t=P):
    """Contorno de espessura `t` sem os cantos (cantos chanfrados)."""
    pygame.draw.rect(surf, col, (r.x + t, r.y, r.w - 2 * t, t))
    pygame.draw.rect(surf, col, (r.x + t, r.bottom - t, r.w - 2 * t, t))
    pygame.draw.rect(surf, col, (r.x, r.y + t, t, r.h - 2 * t))
    pygame.draw.rect(surf, col, (r.right - t, r.y + t, t, r.h - 2 * t))


def panel(surf, rect, fill=PANEL, alpha=232, trim=GOLD, studs=True, glow=0.0):
    """Painel em pixel art: fundo escuro, contorno preto, filete dourado e rebites nos cantos."""
    r = pygame.Rect(rect)
    if r.w < 8 * P or r.h < 8 * P:
        return r
    if glow > 0:
        g = pygame.Surface((r.w + 16, r.h + 16), pygame.SRCALPHA)
        for i in range(4):
            a = int(34 * glow * (4 - i) / 4)
            pygame.draw.rect(g, (*trim, a), (i * 2, i * 2, r.w + 16 - i * 4, r.h + 16 - i * 4), border_radius=10)
        surf.blit(g, (r.x - 8, r.y - 8))
    body = pygame.Surface(r.size, pygame.SRCALPHA)
    body.fill((*fill, alpha))
    # faixas mais escuras para baixo (degradê em degraus, estilo pixel)
    bands = 4
    for i in range(1, bands):
        y = r.h * i // bands
        body.fill((*_mix(fill, INK, 0.12 * i), alpha), (0, y, r.w, r.h - y))
    body.fill((*_mix(fill, (255, 255, 255), 0.06), alpha), (0, P * 2, r.w, P))
    for cx, cy in ((0, 0), (r.w - P, 0), (0, r.h - P), (r.w - P, r.h - P)):
        body.fill((0, 0, 0, 0), (cx, cy, P, P))
    surf.blit(body, r)
    _edges(surf, r, INK)
    inner = r.inflate(-2 * P, -2 * P)
    shade = _mix(trim, INK, 0.45)
    pygame.draw.rect(surf, trim, (inner.x + P, inner.y, inner.w - 2 * P, P // 2 + 1))
    pygame.draw.rect(surf, trim, (inner.x, inner.y + P, P // 2 + 1, inner.h - 2 * P))
    pygame.draw.rect(surf, shade, (inner.x + P, inner.bottom - P // 2 - 1, inner.w - 2 * P, P // 2 + 1))
    pygame.draw.rect(surf, shade, (inner.right - P // 2 - 1, inner.y + P, P // 2 + 1, inner.h - 2 * P))
    if studs:
        for sx, sy in ((inner.x, inner.y), (inner.right - 3 * P, inner.y),
                       (inner.x, inner.bottom - 3 * P), (inner.right - 3 * P, inner.bottom - 3 * P)):
            pygame.draw.rect(surf, INK, (sx, sy, 3 * P, 3 * P))
            pygame.draw.rect(surf, trim, (sx + P // 2, sy + P // 2, 2 * P, 2 * P))
            pygame.draw.rect(surf, GOLD_LIGHT, (sx + P // 2, sy + P // 2, P, P))
    return r


def diamond(surf, center, size, color, outline=True):
    """Losango em pixels (marcadores e ornamentos)."""
    cx, cy = int(center[0]), int(center[1])
    pts = [(cx, cy - size), (cx + size, cy), (cx, cy + size), (cx - size, cy)]
    if outline:
        pygame.draw.polygon(surf, INK, [(cx, cy - size - P), (cx + size + P, cy), (cx, cy + size + P),
                                        (cx - size - P, cy)])
    pygame.draw.polygon(surf, color, pts)


def ornament(surf, center, half_width, color=GOLD, alpha=255):
    """Linha decorativa com losango no meio: ——◆——"""
    cx, cy = int(center[0]), int(center[1])
    if half_width <= 10:
        return
    layer = pygame.Surface((half_width * 2 + 8, 14), pygame.SRCALPHA)
    lx = half_width + 4
    for side in (-1, 1):
        x0 = lx + side * 10
        x1 = lx + side * half_width
        pygame.draw.line(layer, (*_mix(color, INK, 0.3), 255), (min(x0, x1), 8), (max(x0, x1), 8), P)
        pygame.draw.line(layer, (*color, 255), (min(x0, x1), 6), (max(x0, x1), 6), P)
        diamond(layer, (x1, 7), 2, color, outline=False)
    diamond(layer, (lx, 7), 5, color)
    pygame.draw.rect(layer, GOLD_LIGHT, (lx - 1, 3, 2, 2))
    if alpha < 255:
        layer.set_alpha(int(alpha))
    surf.blit(layer, (cx - lx, cy - 7))


def keycap(surf, label, pos, anchor="midleft", active=True):
    """Tecla desenhada (para dicas de controle). Retorna o retângulo."""
    f = font(20)
    tw, th = f.size(label)
    r = pygame.Rect(0, 0, max(22, tw + 12), 22)
    setattr(r, anchor, pos)
    face = (58, 62, 84) if active else (36, 38, 52)
    pygame.draw.rect(surf, INK, r.inflate(2, 2), border_radius=4)
    pygame.draw.rect(surf, _mix(face, INK, 0.5), r, border_radius=3)
    pygame.draw.rect(surf, face, (r.x, r.y, r.w, r.h - 4), border_radius=3)
    pygame.draw.line(surf, _mix(face, (255, 255, 255), 0.25), (r.x + 3, r.y + 1), (r.right - 4, r.y + 1))
    text(surf, label, 20, (r.centerx, r.y + (r.h - 4) // 2 + 1), Colors.UI_TEXT if active else MUTED, "center",
         shadow=False)
    return r


def hints(surf, items, center, color=Colors.UI_DIM, align="center"):
    """Linha de dicas: [(tecla, ação), ...] centralizada em `center` (ou terminando nele, com align="right")."""
    f = font(20)
    widths = []
    for keys, action in items:
        kw = sum(max(22, f.size(k)[0] + 12) + 4 for k in keys.split("|"))
        widths.append(kw + 4 + f.size(action)[0])
    total = sum(widths) + 22 * (len(items) - 1)
    x = center[0] - (total if align == "right" else total // 2)
    y = center[1]
    for (keys, action), wdt in zip(items, widths):
        cx = x
        for k in keys.split("|"):
            cx = keycap(surf, k, (cx, y), "midleft").right + 4
        text(surf, action, 20, (cx + 2, y), color, "midleft")
        x += wdt + 22


_cursor = None


def _dagger():
    """Adaga da folha medieval.png, deitada, usada como cursor de seleção."""
    global _cursor
    if _cursor is None:
        from . import sprites
        sheet = sprites.image("ui", "medieval.png")
        img = None
        if sheet is not None:
            sub = sheet.subsurface((238, 0, 18, 32))
            sub = sub.subsurface(sub.get_bounding_rect()).copy()
            img = pygame.transform.rotate(sub, -90)
        _cursor = img or False
    return _cursor or None


def cursor(surf, pos, direction=1, scale=1):
    """Cursor de seleção: adaga apontando para o item (`direction` 1 = aponta para a direita)."""
    img = _dagger()
    x, y = pos
    if img is None:
        diamond(surf, pos, 5, GOLD)
        return
    if direction > 0:
        img = pygame.transform.flip(img, True, False)
    if scale != 1:
        img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
    surf.blit(img, img.get_rect(midright=(x, y)) if direction > 0 else img.get_rect(midleft=(x, y)))


_bands = {}


def highlight_band(surf, rect, color=GOLD, alpha=70):
    """Faixa de destaque que some nas pontas (item selecionado)."""
    r = pygame.Rect(rect)
    key = (r.size, tuple(color), alpha)
    band = _bands.get(key)
    if band is None:
        band = pygame.Surface(r.size, pygame.SRCALPHA)
        half = r.w / 2
        for x in range(0, r.w, P):
            k = 1 - abs(x + 1 - half) / half
            a = int(alpha * min(1.0, k * 1.8) ** 1.4)
            band.fill((*color, a), (x, P, P, r.h - 2 * P))
            band.fill((*_mix(color, (255, 255, 255), 0.4), min(255, a * 2)), (x, 0, P, P))
            band.fill((*_mix(color, (255, 255, 255), 0.4), min(255, a * 2)), (x, r.h - P, P, P))
        if len(_bands) > 60:
            _bands.clear()
        _bands[key] = band
    surf.blit(band, r)


# ---------------------------------------------------------------------------
# Menu vertical
# ---------------------------------------------------------------------------

class Menu:
    """Lista vertical de opções; teclado (W/S, setas, Enter/Espaço) ou mouse.

    Entra com animação (itens sobem um a um) e o destaque desliza até o item
    escolhido.
    """

    def __init__(self, options, center_y, spacing=46, size=40):
        # [(rótulo, chave)] ou [(rótulo, chave, habilitado)]
        self.options = [o if len(o) == 3 else (o[0], o[1], True) for o in options]
        self.index = next((i for i, o in enumerate(self.options) if o[2]), 0)
        self.center_y = center_y
        self.spacing = spacing
        self.size = size
        self.rects = []
        self.born = None
        self._bar = None
        self._last = None
        self._mouse = None
        self.pulse = 0.0

    def handle(self, inp, audio):
        """Retorna a chave escolhida ou None."""
        if inp.was_pressed("menu_up"):
            self._move(-1)
            audio.play("ui_move")
        if inp.was_pressed("menu_down"):
            self._move(1)
            audio.play("ui_move")
        # o mouse só muda a seleção quando se mexe (não briga com o teclado)
        moved = self._mouse is not None and inp.mouse_pos != self._mouse
        self._mouse = inp.mouse_pos
        for i, r in enumerate(self.rects):
            if r.collidepoint(inp.mouse_pos) and self.options[i][2]:
                if self.index != i and moved:
                    self.index = i
                    audio.play("ui_move")
                if inp.mouse_clicked:
                    self.index = i
                    self.pulse = 1.0
                    audio.play("ui_select")
                    return self.options[i][1]
        if inp.was_pressed("menu_confirm"):
            self.pulse = 1.0
            audio.play("ui_select")
            return self.options[self.index][1]
        return None

    def _move(self, step):
        for _ in range(len(self.options)):
            self.index = (self.index + step) % len(self.options)
            if self.options[self.index][2]:
                return

    def row_y(self, i):
        top = self.center_y - (len(self.options) - 1) * self.spacing / 2
        return int(top + i * self.spacing)

    def draw(self, surf):
        now = _now()
        if self.born is None:
            self.born = now
        dt = 0.0 if self._last is None else min(0.1, now - self._last)
        self._last = now
        age = now - self.born
        self.pulse = max(0.0, self.pulse - dt * 4)
        target = self.row_y(self.index)
        self._bar = target if self._bar is None else self._bar + (target - self._bar) * min(1.0, dt * 16)
        f = font(self.size)
        row_h = min(self.spacing - 4, f.size("Ág")[1] + 4)
        widest = max(f.size(o[0])[0] for o in self.options)
        band_w = min(Display.WIDTH - 40, widest + 200)
        if self.options[self.index][2]:
            highlight_band(surf, (Display.WIDTH // 2 - band_w // 2, int(self._bar) - row_h // 2, band_w, row_h))
        self.rects = []
        for i, (label, _, enabled) in enumerate(self.options):
            appear = ease_out((age - 0.05 * i) / 0.35)
            sel = i == self.index
            if not enabled:
                col = (64, 66, 82)
            elif sel:
                col = _mix(SELECTED, (255, 255, 255), self.pulse * 0.6)
            else:
                col = Colors.UI_DIM
            y = self.row_y(i) + int((1 - appear) * 18)
            r = text(surf, label, self.size, (Display.WIDTH // 2, y), col, "center", alpha=255 * appear)
            if sel and enabled and appear > 0.6:
                wob = int(math.sin(now * 6) * 2 + 0.5)
                k = 2 if f.size("A")[1] > 30 else 1
                cursor(surf, (r.left - 10 - wob, y + k), 1, k)
                cursor(surf, (r.right + 10 + wob, y + k), -1, k)
            hit = pygame.Rect(0, 0, max(r.w + 80, 240), self.spacing)
            hit.center = (Display.WIDTH // 2, self.row_y(i))
            self.rects.append(hit)


def draw_controls(surf, x, y, title=True, compact=False, boxed=None):
    """Lista de controles (tecla em dourado, ação em branco). `boxed` põe um painel atrás."""
    rows = CONTROLS_TEXT
    step = 17 if compact else 22
    if boxed is None:
        boxed = compact
    if boxed:
        h = len(rows) * step + 18 + (24 if title else 0)
        panel(surf, (x - 14, y - 9, min(Display.WIDTH - 16, x + 470) - (x - 14), h), alpha=215)
    if title:
        text(surf, "CONTROLES", 20, (x, y), GOLD)
        y += 24
    for key, action in rows:
        text(surf, key, 20, (x, y), GOLD_LIGHT)
        text(surf, action, 20, (x + 140, y), Colors.UI_TEXT)
        y += step
    return y


# ---------------------------------------------------------------------------
# Ícones
# ---------------------------------------------------------------------------

def _sheet_frame(rel, fw, fh, i):
    from . import sprites
    frames = sprites.grid(rel, fw, fh)
    return frames[i] if 0 <= i < len(frames) else None


_icon_cache = {}


def heart_icon(frame=0, scale=2, empty=False):
    """Coração de objetos/coracao.png recortado e ampliado (vazio = silhueta escura)."""
    key = ("heart", frame, scale, empty)
    if key in _icon_cache:
        return _icon_cache[key]
    img = _sheet_frame("objetos/coracao.png", 32, 32, frame)
    if img is not None:
        img = img.subsurface((4, 4, 24, 24)).copy()
        if empty:
            dark = img.copy()
            dark.fill((46, 34, 54, 255), special_flags=pygame.BLEND_RGBA_MULT)
            img = dark
        img = pygame.transform.scale(img, (24 * scale, 24 * scale))
    _icon_cache[key] = img
    return img


def ability_icon(row, col=2, scale=1, dim_it=False):
    """Ícone de objetos/habilidades.png (5x5 quadros de 32 px)."""
    key = ("abil", row, col, scale, dim_it)
    if key in _icon_cache:
        return _icon_cache[key]
    img = _sheet_frame("objetos/habilidades.png", 32, 32, row * 5 + col)
    if img is not None:
        if dim_it:
            img = img.copy()
            img.fill((90, 100, 110, 255), special_flags=pygame.BLEND_RGBA_MULT)
        if scale != 1:
            img = pygame.transform.scale(img, (32 * scale, 32 * scale))
    _icon_cache[key] = img
    return img


def coin_icon(surf, x, y, t=0.0):
    """Moeda em pixel art (12x14) girando devagar."""
    phase = (math.sin(t * 3) + 1) / 2
    w = 4 + int(8 * (0.35 + 0.65 * abs(math.cos(t * 1.6))))
    cx = x + 7
    r = pygame.Rect(0, 0, w + 2, 16)
    r.center = (cx, y + 8)
    pygame.draw.rect(surf, INK, r.inflate(2, 0), border_radius=4)
    pygame.draw.rect(surf, (150, 96, 26), r, border_radius=4)
    pygame.draw.rect(surf, Colors.COIN, r.inflate(-2, -4), border_radius=3)
    if r.w > 7:
        pygame.draw.rect(surf, (255, 244, 190), (r.x + 2, r.y + 3, 2, 4))
        pygame.draw.rect(surf, (190, 130, 40), (r.centerx - 1 + int(phase), r.y + 5, 2, 6))


def page_icon(surf, x, y):
    """Página do diário (pergaminho com lacre)."""
    pygame.draw.rect(surf, INK, (x - 1, y - 1, 16, 18))
    pygame.draw.rect(surf, PARCHMENT, (x, y, 14, 16))
    pygame.draw.rect(surf, (200, 184, 140), (x, y + 12, 14, 4))
    for i in range(3):
        pygame.draw.rect(surf, (150, 130, 100), (x + 3, y + 3 + i * 3, 8, 1))
    pygame.draw.rect(surf, INK, (x + 8, y + 10, 7, 7))
    pygame.draw.rect(surf, (180, 40, 50), (x + 9, y + 11, 5, 5))
    pygame.draw.rect(surf, (230, 90, 90), (x + 9, y + 11, 2, 2))


# ---------------------------------------------------------------------------
# HUD
# ---------------------------------------------------------------------------

class _HudMemory:
    """Lembra valores do quadro anterior para animar perdas e ganhos."""

    def __init__(self):
        self.hp = None
        self.lost = {}            # índice do coração -> instante em que foi perdido
        self.gained = {}
        self.coins = None
        self.coins_shown = 0.0
        self.coin_gain = 0
        self.coin_gain_t = -9.0
        self.last = None
        self.boss = {}
        self.play_time = None
        self.play_moved = 0.0


_hud = _HudMemory()
_hud_backdrop = None


def _backdrop():
    """Sombra suave atrás do HUD (lê bem sobre cenário claro ou escuro)."""
    global _hud_backdrop
    if _hud_backdrop is None:
        w, h = 46, 16
        small = pygame.Surface((w, h), pygame.SRCALPHA)
        for y in range(h):
            for x in range(w):
                d = ((x / w) ** 2 * 1.0 + (y / h) ** 2 * 1.2) ** 0.5
                small.set_at((x, y), (6, 6, 12, int(150 * max(0.0, 1 - d) ** 1.3)))
        _hud_backdrop = pygame.transform.smoothscale(small, (w * 8, h * 8))
    return _hud_backdrop


def _orb(surf, cx, cy, player, t):
    """Orbe de foco: líquido azul com onda; brilha quando dá para curar."""
    r = 15                           # raio em "pixels de 2"
    size = r * 2 + 6
    o = pygame.Surface((size, size), pygame.SRCALPHA)
    c = size // 2
    k = max(0.0, min(1.0, player.energy / Energy.MAX))
    ready = player.energy >= Energy.HEAL_COST
    pygame.draw.circle(o, INK, (c, c), r + 3)
    pygame.draw.circle(o, GOLD_DARK, (c, c), r + 2)
    pygame.draw.circle(o, GOLD if ready else (150, 124, 84), (c, c), r + 1)
    pygame.draw.circle(o, INK, (c, c), r)
    pygame.draw.circle(o, (22, 18, 40), (c, c), r - 1)
    if k > 0:
        liquid = pygame.Surface((size, size), pygame.SRCALPHA)
        level = c + r - 1 - (2 * r - 2) * k
        for x in range(size):
            wave = math.sin(x * 0.55 + t * 4.0) * (1.0 if k < 0.98 else 0)
            top = int(level + wave)
            if top < size:
                liquid.fill((70, 140, 220, 255), (x, top, 1, size - top))
                liquid.fill((150, 210, 255, 255), (x, top, 1, 2))
                liquid.fill((110, 180, 245, 255), (x, top + 2, 1, max(0, min(4, size - top - 2))))
        mask = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255, 255), (c, c), r - 1)
        liquid.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        o.blit(liquid, (0, 0))
    # reflexo do vidro
    pygame.draw.rect(o, (230, 245, 255), (c - r // 2 - 1, c - r // 2 - 2, 3, 2))
    pygame.draw.rect(o, (200, 225, 255), (c - r // 2 - 2, c - r // 2, 2, 2))
    big = pygame.transform.scale(o, (size * P, size * P))
    if ready:
        glow = pygame.Surface((size * P + 24, size * P + 24), pygame.SRCALPHA)
        a = int(50 + 40 * math.sin(t * 4))
        pygame.draw.circle(glow, (150, 210, 255, a // 2), (glow.get_width() // 2,) * 2, r * P + 12)
        pygame.draw.circle(glow, (150, 210, 255, a), (glow.get_width() // 2,) * 2, r * P + 7)
        surf.blit(glow, glow.get_rect(center=(cx, cy)))
    surf.blit(big, big.get_rect(center=(cx, cy)))
    # carregando a cura (segurando F): arco dourado em volta
    heal_t = getattr(player, "heal_timer", 0.0)
    heal_total = getattr(player, "heal_time", 0.0)
    if heal_t > 0 and heal_total:
        frac = min(1.0, heal_t / heal_total)
        rect = pygame.Rect(0, 0, (r + 5) * P * 2, (r + 5) * P * 2)
        rect.center = (cx, cy)
        pygame.draw.arc(surf, GOLD_LIGHT, rect, math.pi / 2, math.pi / 2 + frac * 2 * math.pi, 4)
    if ready:
        keycap(surf, "F", (cx + r * P - 2, cy + r * P - 2), "center")


def _ability_slot(surf, x, y, icon_row, key, ready, cooldown=0.0, t=0.0):
    """Ícone de habilidade com tecla embaixo. `cooldown` (0-1) escurece de cima para baixo."""
    rect = pygame.Rect(x, y, 34, 34)
    pygame.draw.rect(surf, INK, rect.inflate(4, 4))
    pygame.draw.rect(surf, (24, 28, 44), rect)
    pygame.draw.rect(surf, GOLD if ready else GOLD_DARK, rect, P)
    icon = ability_icon(icon_row, 2, dim_it=not ready)
    if icon is not None:
        bob = int(math.sin(t * 3 + icon_row) * 1.5) if ready else 0
        surf.blit(icon, icon.get_rect(center=(rect.centerx, rect.centery + bob)))
    if cooldown > 0:
        h = int((rect.h - 4) * cooldown)
        shade = pygame.Surface((rect.w - 4, h), pygame.SRCALPHA)
        shade.fill((8, 10, 18, 170))
        surf.blit(shade, (rect.x + 2, rect.y + 2))
    text(surf, key, 20, (rect.centerx, rect.bottom + 2), Colors.UI_TEXT if ready else MUTED, "midtop",
         outline=True)


def draw_hud(surf, player, progress, room_name, room_name_timer, fps=None, muted=False, story=False):
    """HUD: orbe de foco (cura), corações, moedas, páginas, habilidades e tempo.

    Fica nos cantos superiores para não cobrir a ação.
    """
    t = _now()
    mem = _hud
    dt = 0.0 if mem.last is None else min(0.1, max(0.0, t - mem.last))
    mem.last = t
    # partida congelada (pausa, mapa, loja, diálogo por cima): o tempo de jogo para de andar.
    # Nesses casos o nome da sala e a dica de teclas somem para não ficar sob o título da tela.
    if progress.play_time != mem.play_time:
        mem.play_time = progress.play_time
        mem.play_moved = t
    frozen = t - mem.play_moved > 0.12
    surf.blit(_backdrop(), (0, 0))

    # --- orbe de foco ---
    _orb(surf, 44, 42, player, t)

    # --- corações ---
    if mem.hp is not None and player.hp != mem.hp:
        if player.hp < mem.hp:
            for i in range(player.hp, mem.hp):
                mem.lost[i] = t
        else:
            for i in range(mem.hp, player.hp):
                mem.gained[i] = t
    mem.hp = player.hp
    hx, hy, step = 86, 6, 28
    for i in range(player.max_hp):
        full = i < player.hp
        x = hx + i * step
        y = hy
        frame = 0
        lost_t = t - mem.lost.get(i, -9)
        gain_t = t - mem.gained.get(i, -9)
        if full and gain_t < 0.5:
            frame = min(9, int(gain_t * 20))
        elif full and player.hp <= 2 and i == player.hp - 1:
            frame = int(t * 10) % 10           # último coração pulsando
        img = heart_icon(frame, 2, empty=not full)
        if img is None:
            pygame.draw.rect(surf, Colors.HP_FULL if full else Colors.HP_EMPTY, (x + 6, y + 10, 18, 18))
            continue
        if not full and lost_t < 0.45:
            shake = int(math.sin(lost_t * 70) * 3 * (1 - lost_t / 0.45))
            flash = heart_icon(0, 2)
            surf.blit(img, (x - 10 + shake, y - 8))
            if int(lost_t * 20) % 2 == 0 and flash is not None:
                white = flash.copy()
                white.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_MAX)
                white.set_alpha(int(220 * (1 - lost_t / 0.45)))
                surf.blit(white, (x - 10 + shake, y - 8))
        else:
            surf.blit(img, (x - 10, y - 8))

    # --- moedas (o número conta até o valor novo) e páginas ---
    if mem.coins is None:
        mem.coins = progress.coins
        mem.coins_shown = float(progress.coins)
    if progress.coins > mem.coins:
        mem.coin_gain = (mem.coin_gain if t - mem.coin_gain_t < 1.2 else 0) + progress.coins - mem.coins
        mem.coin_gain_t = t
    mem.coins = progress.coins
    diff = progress.coins - mem.coins_shown
    if abs(diff) < 0.5:
        mem.coins_shown = float(progress.coins)
    else:
        mem.coins_shown += diff * min(1.0, dt * 10) + (0.5 if diff > 0 else -0.5)
    cy = 46
    coin_icon(surf, hx - 2, cy, t)
    r = text(surf, str(int(round(mem.coins_shown))), 20, (hx + 16, cy - 1), Colors.COIN, outline=True)
    since = t - mem.coin_gain_t
    if since < 1.2 and mem.coin_gain > 0:
        a = 255 * min(1.0, (1.2 - since) / 0.4)
        text(surf, f"+{mem.coin_gain}", 20, (r.right + 6, cy - 1 - int(since * 8)), GOLD_LIGHT, outline=True,
             alpha=a)
    if story:
        lx = hx + 86
        page_icon(surf, lx, cy)
        text(surf, f"{len(progress.letters)}/3", 20, (lx + 20, cy - 1), PARCHMENT, outline=True)

    # --- habilidades ---
    ax, ay = 12, 82
    if "dash" in player.abilities:
        total = Dash.DURATION + player.dash_cooldown_time
        cd = player.dash_cooldown / total if total else 0
        _ability_slot(surf, ax, ay, 0, "Shift", player.dash_ready, max(0.0, min(1.0, cd)), t)
        ax += 62
    if "double_jump" in player.abilities:
        _ability_slot(surf, ax, ay, 1, "Espaço", player.can_air_jump or player.on_ground, 0.0, t)

    # --- tempo de jogo (canto direito) ---
    m, sec = divmod(int(progress.play_time), 60)
    text(surf, f"{m:02d}:{sec:02d}", 20, (Display.WIDTH - 14, 10), Colors.UI_TEXT, "topright", outline=True)
    if muted:
        mx, my = Display.WIDTH - 40, 34
        pygame.draw.polygon(surf, INK, [(mx - 1, my + 4), (mx + 6, my + 4), (mx + 13, my - 1), (mx + 13, my + 17),
                                        (mx + 6, my + 12), (mx - 1, my + 12)])
        pygame.draw.polygon(surf, (200, 200, 210), [(mx, my + 5), (mx + 6, my + 5), (mx + 12, my), (mx + 12, my + 16),
                                                    (mx + 6, my + 11), (mx, my + 11)])
        pygame.draw.line(surf, (240, 80, 90), (mx + 15, my + 3), (mx + 24, my + 13), 3)
        pygame.draw.line(surf, (240, 80, 90), (mx + 24, my + 3), (mx + 15, my + 13), 3)
    # dica de teclas: só nos primeiros minutos (depois fica na pausa)
    if progress.play_time < 120 and not frozen:
        a = 255 * min(1.0, (120 - progress.play_time) / 4)
        layer = pygame.Surface((Display.WIDTH, 30), pygame.SRCALPHA)
        hints(layer, [("ESC", "pausa"), ("Tab", "mapa"), ("M", "som")], (Display.WIDTH - 16, 15), align="right")
        layer.set_alpha(int(a * 0.85))
        surf.blit(layer, (0, Display.HEIGHT - 32))

    # --- nome da sala ao entrar ---
    if room_name_timer > 0 and not frozen:
        a = 255 * min(1.0, room_name_timer / 0.4)
        rr = text(surf, room_name, 34, (Display.WIDTH // 2, 14), Colors.UI_TEXT, "midtop", title=True, alpha=a)
        ornament(surf, (Display.WIDTH // 2, rr.bottom + 10), max(60, rr.w // 2 + 20), GOLD, alpha=a)
    if fps is not None:
        text(surf, f"FPS {fps:.0f}", 20, (Display.WIDTH - 14, 58), Colors.UI_DIM, "topright", outline=True)


def draw_boss_bar(surf, name, hp, max_hp):
    """Barra do chefe no topo central (não cobre o chão da arena).

    A parte perdida fica clara por um instante e escorre depois (dá para ler o
    tamanho do golpe). Da metade para baixo (fase 2) a barra pulsa.
    """
    t = _now()
    mem = _hud.boss.setdefault(name, {"shown": float(hp), "hit": -9.0, "last_hp": hp, "born": t, "last": t})
    dt = min(0.1, max(0.0, t - mem["last"]))
    mem["last"] = t
    if hp < mem["last_hp"]:
        mem["hit"] = t
    mem["last_hp"] = hp
    if t - mem["hit"] > 0.45:
        mem["shown"] = max(float(hp), mem["shown"] - max_hp * 0.5 * dt)
    mem["shown"] = max(mem["shown"], float(hp))
    appear = ease_out((t - mem["born"]) / 0.6)

    w = 400
    x = (Display.WIDTH - w) // 2
    y = 58
    parts = name.split(" - ", 1)
    text(surf, parts[0], 34, (Display.WIDTH // 2, y - 3), (255, 214, 140), "midbottom", title=True,
              alpha=255 * appear)
    if len(parts) > 1:
        text(surf, parts[1], 20, (Display.WIDTH // 2, y + 20), (230, 150, 160), "midtop", outline=True,
             alpha=255 * appear)
    frame = pygame.Rect(x - 8, y - 4, w + 16, 20)
    pygame.draw.rect(surf, INK, frame.inflate(2, 2))
    pygame.draw.rect(surf, GOLD_DARK, frame)
    pygame.draw.rect(surf, GOLD, frame.inflate(-2, -2), P // 2 + 1)
    for ex in (frame.x - 6, frame.right + 6):
        diamond(surf, (ex, frame.centery), 7, GOLD)
        pygame.draw.rect(surf, GOLD_LIGHT, (ex - 1, frame.centery - 4, 2, 2))
    inner = pygame.Rect(x, y, w, 12)
    pygame.draw.rect(surf, (40, 14, 22), inner)
    k = max(0.0, hp) / max_hp * appear
    ks = max(0.0, mem["shown"]) / max_hp * appear
    if ks > k:
        pygame.draw.rect(surf, (250, 220, 170), (x + int(w * k), y, int(w * (ks - k)) + 1, 12))
    if k > 0:
        fill = int(w * k)
        phase2 = hp <= max_hp * 0.5
        base = (190, 40, 70) if phase2 else Colors.GUARDIAN
        if phase2:
            base = _mix(base, (255, 90, 110), (math.sin(t * 6) + 1) * 0.18)
        pygame.draw.rect(surf, _mix(base, INK, 0.3), (x, y, fill, 12))
        pygame.draw.rect(surf, base, (x, y, fill, 8))
        pygame.draw.rect(surf, _mix(base, (255, 255, 255), 0.35), (x, y + 2, fill, 2))
        if t - mem["hit"] < 0.12:
            pygame.draw.rect(surf, (255, 255, 255), (x, y, fill, 12))
    # marca da metade (fase 2)
    mx = x + w // 2
    pygame.draw.rect(surf, INK, (mx - 2, y - 3, 4, 18))
    pygame.draw.rect(surf, (230, 210, 170), (mx - 1, y - 2, 2, 16))


# ---------------------------------------------------------------------------
# Inventário (tela de pausa)
# ---------------------------------------------------------------------------

def _pips(surf, x, y, filled, total, color, size=4):
    for i in range(total):
        c = (x + i * (size * 2 + 6) + size, y + size)
        diamond(surf, c, size, color if i < filled else (52, 54, 70))
    return x + total * (size * 2 + 6)


def draw_inventory(surf, progress, player, x, y):
    """Resumo do inventário num painel (usado na pausa)."""
    from .progress import ABILITIES, CHARMS
    pw = min(410, Display.WIDTH - x - 20)
    ph = min(Display.HEIGHT - y + 6, 222)
    panel(surf, (x - 14, y - 10, pw, ph), alpha=215)
    text(surf, "INVENTÁRIO", 20, (x, y), GOLD)
    row = y + 26
    step = 24
    # vida e fragmentos
    icon = heart_icon(0, 1)
    if icon is not None:
        surf.blit(icon, (x - 4, row - 3))
    text(surf, f"Vida máxima {player.max_hp}", 20, (x + 22, row), Colors.UI_TEXT)
    frag = progress.fragments % Progression.FRAGMENTS_PER_HP
    fx = _pips(surf, x + 190, row + 4, frag, Progression.FRAGMENTS_PER_HP, Colors.HP_FULL)
    text(surf, "fragmentos", 20, (fx + 4, row), Colors.UI_DIM)
    row += step
    # moedas e minérios
    coin_icon(surf, x - 2, row, 0.0)
    text(surf, f"{progress.coins} moedas", 20, (x + 22, row), Colors.COIN)
    pygame.draw.polygon(surf, INK, [(x + 189, row + 9), (x + 196, row), (x + 205, row + 4), (x + 203, row + 15),
                                    (x + 193, row + 16)])
    pygame.draw.polygon(surf, (150, 160, 190), [(x + 191, row + 9), (x + 196, row + 2), (x + 203, row + 5),
                                                (x + 201, row + 13), (x + 194, row + 14)])
    text(surf, f"{progress.ore} minérios", 20, (x + 212, row), (170, 180, 210))
    row += step
    # arma
    text(surf, "Arma", 20, (x, row), Colors.UI_DIM)
    lx = _pips(surf, x + 46, row + 4, progress.weapon_level + 1, 4, GOLD)
    text(surf, f"rápido {player.quick_spec.damage}  pesado {player.heavy_spec.damage}", 20, (lx + 6, row),
         Colors.UI_TEXT)
    row += step
    # habilidades
    names = [ABILITIES[a][0] for a in sorted(progress.abilities) if a in ABILITIES]
    text(surf, "Habilidades", 20, (x, row), Colors.UI_DIM)
    text(surf, ", ".join(names) or "nenhuma ainda", 20, (x + 92, row), Colors.UI_TEXT)
    row += step
    text(surf, "Mapa", 20, (x, row), Colors.UI_DIM)
    text(surf, "sim" if progress.has_map else "não (loja do convés)", 20, (x + 92, row),
         Colors.UI_TEXT if progress.has_map else MUTED)
    row += step
    # amuletos: espaços como losangos e nomes dos equipados
    text(surf, "Amuletos", 20, (x, row), Colors.UI_DIM)
    _pips(surf, x + 92, row + 4, progress.notches_used, progress.notches, (150, 210, 255))
    row += step - 2
    equipped = [CHARMS[c]["name"] for c in progress.charms_owned if c in progress.charms_equipped]
    others = len(progress.charms_owned) - len(equipped)
    if not progress.charms_owned:
        msg = "nenhum encontrado"
    else:
        msg = ", ".join(equipped) if equipped else "nenhum equipado"
        if others:
            msg += f"  (+{others} na bolsa)"
    for line in wrap_lines(msg, 20, pw - 40)[:2]:
        text(surf, line, 20, (x + 12, row), SELECTED if equipped else MUTED)
        row += 19


# ---------------------------------------------------------------------------
# Mapa
# ---------------------------------------------------------------------------

# salas desenhadas no último draw_map: [(retângulo na tela, nome)] (usado pelo hover do mouse)
map_rooms = []


def draw_map(surf, play):
    progress = play.progress
    map_rooms.clear()
    t = _now()
    frame = pygame.Rect(24, 64, Display.WIDTH - 48, Display.HEIGHT - 112)
    text(surf, "Mapa", 44, (Display.WIDTH // 2, 34), Colors.UI_TEXT, "center", title=True)
    hints(surf, [("Tab|ESC", "fechar")], (Display.WIDTH // 2, Display.HEIGHT - 24))
    panel(surf, frame, fill=(16, 20, 32), alpha=236)
    if not progress.has_map:
        text(surf, "Você ainda não tem um mapa.", 34, (Display.WIDTH // 2, Display.HEIGHT // 2 - 14),
             Colors.UI_TEXT, "center")
        text(surf, "Compre um na loja do convés.", 20, (Display.WIDTH // 2, Display.HEIGHT // 2 + 22),
             Colors.UI_DIM, "center")
        return
    rooms = [r for r in play.world.rooms.values() if r.id in progress.visited]
    if not rooms:
        return
    allr = play.world.rooms.values()
    x0 = min(r.origin_tx for r in allr)
    y0 = min(r.origin_ty for r in allr)
    x1 = max(r.origin_tx + r.cols for r in allr)
    y1 = max(r.origin_ty + r.rows_count for r in allr)
    area = frame.inflate(-48, -56)
    area.y -= 8
    # grade leve de fundo
    grid = pygame.Surface(frame.inflate(-12, -12).size, pygame.SRCALPHA)
    for gx in range(0, grid.get_width(), 24):
        grid.fill((90, 110, 150, 18), (gx, 0, 1, grid.get_height()))
    for gy in range(0, grid.get_height(), 24):
        grid.fill((90, 110, 150, 18), (0, gy, grid.get_width(), 1))
    surf.blit(grid, frame.inflate(-12, -12))
    scale = min(area.w / (x1 - x0), area.h / (y1 - y0))
    ox = area.x + (area.w - (x1 - x0) * scale) / 2
    oy = area.y + (area.h - (y1 - y0) * scale) / 2

    def to_screen(tx, ty):
        return ox + (tx - x0) * scale, oy + (ty - y0) * scale

    cell = max(1, int(scale + 0.6))
    for room in rooms:
        rx, ry = to_screen(room.origin_tx, room.origin_ty)
        rect = pygame.Rect(round(rx), round(ry), round(room.cols * scale), round(room.rows_count * scale))
        current = room is play.room
        map_rooms.append((rect.copy(), room.name))
        pygame.draw.rect(surf, INK, rect.inflate(4, 4))
        pygame.draw.rect(surf, (44, 52, 78) if current else (30, 35, 52), rect)
        edge = room.palette[3]
        for ty in range(room.rows_count):
            for tx in range(room.cols):
                if room.tile(tx, ty) == "#":
                    px, py = to_screen(room.origin_tx + tx, room.origin_ty + ty)
                    pygame.draw.rect(surf, edge, (int(px), int(py), cell, cell))
        if current:
            a = (math.sin(t * 5) + 1) / 2
            pygame.draw.rect(surf, _mix(Colors.UI_ACCENT, (255, 255, 255), a * 0.5), rect.inflate(2, 2), 2)
        else:
            pygame.draw.rect(surf, (82, 88, 112), rect.inflate(2, 2), 1)
        for s in room.spawns:
            icon = {"B": (Colors.ENERGY, "banco"), "$": (Colors.NPC_SHOP, "loja"),
                    "R": (Colors.NPC_SMITH, "ferreiro")}.get(s[0])
            if icon:
                px, py = to_screen(room.origin_tx + s[1] / World.TILE, room.origin_ty + s[2] / World.TILE)
                diamond(surf, (int(px), int(py - 4)), 4, icon[0])
    text(surf, play.room.name, 20, (frame.x + 18, frame.y + 14), SELECTED)
    if progress.equipped("bussola"):
        r = play.room
        p = play.player
        px, py = to_screen(r.origin_tx + p.cx / World.TILE, r.origin_ty + p.cy / World.TILE)
        pygame.draw.circle(surf, INK, (int(px), int(py)), 7)
        pygame.draw.circle(surf, (255, 255, 255), (int(px), int(py)), 5)
        pygame.draw.circle(surf, Colors.PLAYER, (int(px), int(py)), 3)
    else:
        text(surf, "Equipe a Bússola para ver onde você está.", 20, (frame.x + 18, frame.bottom - 30), Colors.UI_DIM)
    # legenda
    legend = [(Colors.ENERGY, "bola de cristal"), (Colors.NPC_SHOP, "loja"), (Colors.NPC_SMITH, "ferreiro")]
    widest = max(font(20).size(name)[0] for _, name in legend)
    lx, ly = frame.right - 26 - widest - 12, frame.bottom - 80
    for i, (col, name) in enumerate(legend):
        diamond(surf, (lx, ly + 8 + i * 20), 4, col)
        text(surf, name, 20, (lx + 12, ly + i * 20), Colors.UI_DIM)


def map_room_at(pos):
    """Nome da sala do mapa sob `pos` (ou None)."""
    for rect, name in reversed(map_rooms):
        if rect.collidepoint(pos):
            return name
    return None


def draw_map_hover(surf, mouse_pos):
    """Contorno e etiqueta com o nome da sala sob o mouse. Chamar depois de `draw_map` (ou do cache dele)."""
    name = map_room_at(mouse_pos)
    if name is None:
        return None
    rect = next(r for r, n in reversed(map_rooms) if n == name)
    pygame.draw.rect(surf, SELECTED, rect.inflate(2, 2), 1)
    f = font(20)
    tw, th = f.size(name)
    tip = pygame.Rect(0, 0, tw + 20, th + 12)
    tip.midbottom = (mouse_pos[0], mouse_pos[1] - 10)
    tip.clamp_ip(pygame.Rect(28, 68, Display.WIDTH - 56, Display.HEIGHT - 120))
    panel(surf, tip, alpha=240, studs=False)
    text(surf, name, 20, tip.center, SELECTED, "center")
    return tip
