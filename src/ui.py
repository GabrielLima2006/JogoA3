"""Interface provisória: HUD, menus, inventário, mapa e textos."""

import os

import pygame

from .config import Colors, Dash, Display, Energy, Progression, World
from .fonte import PixelFont, scale_for
from .input import CONTROLS_TEXT
from .paths import asset

_fonts = {}


TITLE_FONT = asset("fonts", "alagard.ttf")


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


def text(surf, msg, size, pos, color=Colors.UI_TEXT, anchor="topleft", title=False, shadow=True):
    """Escreve texto; por padrão com sombra de 1 pixel para contraste em qualquer fundo."""
    f = font(size, title)
    img = f.render(msg, False, color)
    rect = img.get_rect(**{anchor: pos})
    if shadow:
        dark = f.render(msg, False, (12, 10, 16))
        k = getattr(f, "scale", 1)
        surf.blit(dark, rect.move(k, k))
    surf.blit(img, rect)
    return rect


def wrap_text(surf, msg, size, x, y, width, color=Colors.UI_TEXT, line_gap=4):
    """Escreve texto quebrando linhas pela largura. Retorna o y final."""
    words, line = msg.split(), ""
    for w in words:
        test = (line + " " + w).strip()
        if font(size).size(test)[0] > width and line:
            text(surf, line, size, (x, y), color)
            y += size + line_gap
            line = w
        else:
            line = test
    if line:
        text(surf, line, size, (x, y), color)
        y += size + line_gap
    return y


def dim(surf, alpha=160):
    s = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    s.fill((8, 9, 14, alpha))
    surf.blit(s, (0, 0))


class Menu:
    """Lista vertical de opções; teclado (W/S, setas, Enter/Espaço) ou mouse."""

    def __init__(self, options, center_y, spacing=46, size=40):
        # [(rótulo, chave)] ou [(rótulo, chave, habilitado)]
        self.options = [o if len(o) == 3 else (o[0], o[1], True) for o in options]
        self.index = next((i for i, o in enumerate(self.options) if o[2]), 0)
        self.center_y = center_y
        self.spacing = spacing
        self.size = size
        self.rects = []

    def handle(self, inp, audio):
        """Retorna a chave escolhida ou None."""
        if inp.was_pressed("menu_up"):
            self._move(-1)
            audio.play("ui_move")
        if inp.was_pressed("menu_down"):
            self._move(1)
            audio.play("ui_move")
        for i, r in enumerate(self.rects):
            if r.collidepoint(inp.mouse_pos) and self.options[i][2]:
                if self.index != i:
                    self.index = i
                if inp.mouse_clicked:
                    audio.play("ui_select")
                    return self.options[i][1]
        if inp.was_pressed("menu_confirm"):
            audio.play("ui_select")
            return self.options[self.index][1]
        return None

    def _move(self, step):
        for _ in range(len(self.options)):
            self.index = (self.index + step) % len(self.options)
            if self.options[self.index][2]:
                return

    def draw(self, surf):
        self.rects = []
        top = self.center_y - (len(self.options) - 1) * self.spacing / 2
        for i, (label, _, enabled) in enumerate(self.options):
            sel = i == self.index
            col = Colors.UI_ACCENT if sel else (Colors.UI_DIM if enabled else (60, 63, 78))
            msg = f"> {label} <" if sel else label
            r = text(surf, msg, self.size, (Display.WIDTH // 2, int(top + i * self.spacing)), col, "center")
            self.rects.append(r.inflate(40, 10))


def draw_controls(surf, x, y, title=True, compact=False):
    rows = CONTROLS_TEXT
    size, step = (20, 18) if compact else (21, 20)
    if title:
        text(surf, "CONTROLES", 24, (x, y), Colors.UI_ACCENT)
        y += 24
    for key, action in rows:
        text(surf, key, size, (x, y), Colors.UI_TEXT)
        text(surf, action, size, (x + 150, y), Colors.UI_DIM)
        y += step
    return y


# ---------------------------------------------------------------------------
# HUD
# ---------------------------------------------------------------------------

def draw_hud(surf, player, progress, room_name, room_name_timer, fps=None, muted=False, story=False):
    """HUD: orbe de foco (cura), corações, moedas, tempo, cartas e habilidades.

    Fica nos cantos superiores para não cobrir a ação.
    """
    from . import sprites
    t = pygame.time.get_ticks() / 1000.0
    # orbe de foco
    cx, cy, r = 38, 40, 24
    pygame.draw.circle(surf, (20, 18, 34), (cx, cy), r + 3)
    pygame.draw.circle(surf, (36, 30, 58), (cx, cy), r)
    k = player.energy / Energy.MAX
    if k > 0:
        fill = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(fill, (150, 210, 255, 255), (r, r), r - 3)
        pygame.draw.circle(fill, (220, 245, 255, 255), (r - 7, r - 7), 5)
        cut = int((r * 2) * (1 - k))
        fill.fill((0, 0, 0, 0), (0, 0, r * 2, cut))
        surf.blit(fill, (cx - r, cy - r))
    ready = player.energy >= Energy.HEAL_COST
    pygame.draw.circle(surf, (200, 170, 100) if ready else (90, 80, 70), (cx, cy), r + 1, 3)
    if ready:
        text(surf, "F", 20, (cx, cy + 1), (30, 26, 50), "center", shadow=False)

    # corações (sprite que pulsa; vazios ficam escuros)
    hearts = sprites.grid("objetos/coracao.png", 32, 32)
    x, y = 70, 10
    for i in range(player.max_hp):
        if hearts:
            img = hearts[int(t * 8) % len(hearts)] if i == player.hp - 1 and player.hp <= 2 else hearts[0]
            if i >= player.hp:
                img = sprites.variant(hearts[0], tint=(60, 50, 70, 255))
            surf.blit(img, (x + i * 26 - 4, y - 2))
        else:
            col = Colors.HP_FULL if i < player.hp else Colors.HP_EMPTY
            pygame.draw.rect(surf, col, (x + i * 24, y + 6, 18, 18), border_radius=4)
    # moedas e cartas
    coin_y = 46
    pygame.draw.circle(surf, (120, 80, 20), (x + 7, coin_y + 8), 7)
    pygame.draw.circle(surf, Colors.COIN, (x + 7, coin_y + 8), 6)
    pygame.draw.circle(surf, (255, 240, 170), (x + 5, coin_y + 6), 2)
    text(surf, str(progress.coins), 20, (x + 19, coin_y - 1), Colors.COIN)
    if story:
        lx = x + 76
        pygame.draw.rect(surf, (238, 226, 190), (lx, coin_y + 1, 14, 14), border_radius=2)
        pygame.draw.circle(surf, (180, 40, 50), (lx + 11, coin_y + 12), 3)
        text(surf, f"{len(progress.letters)}/3", 20, (lx + 19, coin_y - 1), (238, 226, 190))

    # habilidades
    y2 = 72
    ax = 14
    if "dash" in player.abilities:
        _ability_dash(surf, ax, y2, player)
        ax += 62
    if "double_jump" in player.abilities:
        _ability_icon(surf, ax, y2, "2x", "PULO", player.can_air_jump)

    # tempo de jogo e dicas (canto direito)
    m, sec = divmod(int(progress.play_time), 60)
    text(surf, f"{m:02d}:{sec:02d}", 30, (Display.WIDTH - 16, 10), Colors.UI_TEXT, "topright")
    hint = "ESC pausa - Tab mapa - M som"
    text(surf, hint, 20, (Display.WIDTH - 14, Display.HEIGHT - 22), Colors.UI_DIM, "topright")
    if muted:
        mx, my = Display.WIDTH - 40, 50
        pygame.draw.polygon(surf, (200, 200, 210), [(mx, my + 5), (mx + 6, my + 5), (mx + 12, my), (mx + 12, my + 16),
                                                    (mx + 6, my + 11), (mx, my + 11)])
        pygame.draw.line(surf, (240, 80, 90), (mx + 15, my + 3), (mx + 24, my + 13), 3)
        pygame.draw.line(surf, (240, 80, 90), (mx + 24, my + 3), (mx + 15, my + 13), 3)

    if room_name_timer > 0:
        alpha = min(1.0, room_name_timer / 0.4)
        col = tuple(int(c * alpha) for c in Colors.UI_TEXT)
        text(surf, room_name, 34, (Display.WIDTH // 2, 16), col, "midtop", title=True)
    if fps is not None:
        text(surf, f"FPS {fps:.0f}", 20, (Display.WIDTH - 14, 44), Colors.UI_DIM, "topright")


def draw_boss_bar(surf, name, hp, max_hp):
    """Barra do chefe no topo central (não cobre o chão da arena)."""
    w = 420
    x = (Display.WIDTH - w) // 2
    y = 46
    text(surf, name, 24, (Display.WIDTH // 2, y - 4), Colors.UI_TEXT, "midbottom")
    k = max(0.0, hp) / max_hp
    pygame.draw.rect(surf, (12, 8, 14), (x - 3, y - 3, w + 6, 18), border_radius=5)
    pygame.draw.rect(surf, (52, 22, 30), (x, y, w, 12), border_radius=3)
    if k > 0:
        fill = int(w * k)
        pygame.draw.rect(surf, Colors.GUARDIAN, (x, y, fill, 12), border_radius=3)
        pygame.draw.rect(surf, tuple(min(255, c + 70) for c in Colors.GUARDIAN), (x + 2, y + 2, max(0, fill - 4), 3))
    # marca da metade (fase 2)
    pygame.draw.line(surf, (230, 210, 170), (x + w // 2, y - 2), (x + w // 2, y + 13), 2)
    pygame.draw.rect(surf, (200, 170, 100), (x - 3, y - 3, w + 6, 18), 2, border_radius=5)


def _ability_icon(surf, x, y, big, small, ready):
    rect = pygame.Rect(x, y, 56, 44)
    pygame.draw.rect(surf, (30, 34, 50), rect, border_radius=6)
    pygame.draw.rect(surf, Colors.UI_ACCENT if ready else Colors.UI_DIM, rect, 2, border_radius=6)
    text(surf, big, 20, (rect.centerx, rect.y + 3), Colors.UI_TEXT if ready else Colors.UI_DIM, "midtop")
    text(surf, small, 15, (rect.centerx, rect.y + 22), Colors.UI_DIM, "midtop")


def _ability_dash(surf, x, y, player):
    rect = pygame.Rect(x, y, 56, 44)
    pygame.draw.rect(surf, (30, 34, 50), rect, border_radius=6)
    total = Dash.DURATION + player.dash_cooldown_time
    k = player.dash_cooldown / total if total else 0
    if k > 0:
        h = int(rect.h * k)
        pygame.draw.rect(surf, (45, 60, 80), (rect.x, rect.bottom - h, rect.w, h), border_radius=6)
    ready = player.dash_ready
    pygame.draw.rect(surf, Colors.UI_ACCENT if ready else Colors.UI_DIM, rect, 2, border_radius=6)
    text(surf, "SHIFT", 18, (rect.centerx, rect.y + 3), Colors.UI_TEXT if ready else Colors.UI_DIM, "midtop")
    text(surf, "DASH", 15, (rect.centerx, rect.y + 22), Colors.UI_DIM, "midtop")


# ---------------------------------------------------------------------------
# Inventário (tela de pausa)
# ---------------------------------------------------------------------------

def draw_inventory(surf, progress, player, x, y):
    from .progress import ABILITIES, CHARMS
    text(surf, "INVENTÁRIO", 24, (x, y), Colors.UI_ACCENT)
    y += 28
    lines = [
        (f"Vida máxima: {player.max_hp}", Colors.HP_FULL),
        (f"Fragmentos de vida: {progress.fragments % Progression.FRAGMENTS_PER_HP}/{Progression.FRAGMENTS_PER_HP}",
         Colors.UI_TEXT),
        (f"Moedas: {progress.coins}    Minérios: {progress.ore}", Colors.COIN),
        (f"Arma: nível {progress.weapon_level}  (rápido {player.quick_spec.damage} / pesado {player.heavy_spec.damage})",
         Colors.UI_TEXT),
        ("Habilidades: " + (", ".join(ABILITIES[a][0] for a in sorted(progress.abilities)) or "nenhuma ainda"),
         Colors.UI_TEXT),
        (f"Mapa: {'sim' if progress.has_map else 'não'}", Colors.UI_TEXT),
        (f"Amuletos ({progress.notches_used}/{progress.notches} espaços):", Colors.UI_TEXT),
    ]
    for msg, col in lines:
        text(surf, msg, 22, (x, y), col)
        y += 22
    if not progress.charms_owned:
        text(surf, "  nenhum", 22, (x, y), Colors.UI_DIM)
    for cid in progress.charms_owned:
        eq = cid in progress.charms_equipped
        text(surf, ("  [x] " if eq else "  [  ] ") + CHARMS[cid]["name"], 22, (x, y),
             Colors.UI_ACCENT if eq else Colors.UI_DIM)
        y += 21


# ---------------------------------------------------------------------------
# Mapa
# ---------------------------------------------------------------------------

def draw_map(surf, play):
    progress = play.progress
    text(surf, "MAPA", 44, (Display.WIDTH // 2, 36), Colors.UI_TEXT, "center", title=True)
    text(surf, "M / Tab / ESC para fechar", 20, (Display.WIDTH // 2, Display.HEIGHT - 24), Colors.UI_DIM, "center")
    if not progress.has_map:
        text(surf, "Você ainda não tem um mapa.", 30, (Display.WIDTH // 2, Display.HEIGHT // 2 - 10),
             Colors.UI_TEXT, "center")
        text(surf, "Compre um na loja da Vila.", 24, (Display.WIDTH // 2, Display.HEIGHT // 2 + 24),
             Colors.UI_DIM, "center")
        return
    rooms = [r for r in play.world.rooms.values() if r.id in progress.visited]
    if not rooms:
        return
    x0 = min(r.origin_tx for r in play.world.rooms.values())
    y0 = min(r.origin_ty for r in play.world.rooms.values())
    x1 = max(r.origin_tx + r.cols for r in play.world.rooms.values())
    y1 = max(r.origin_ty + r.rows_count for r in play.world.rooms.values())
    area = pygame.Rect(40, 70, Display.WIDTH - 80, Display.HEIGHT - 120)
    scale = min(area.w / (x1 - x0), area.h / (y1 - y0))
    ox = area.x + (area.w - (x1 - x0) * scale) / 2
    oy = area.y + (area.h - (y1 - y0) * scale) / 2

    def to_screen(tx, ty):
        return ox + (tx - x0) * scale, oy + (ty - y0) * scale

    for room in rooms:
        rx, ry = to_screen(room.origin_tx, room.origin_ty)
        rect = pygame.Rect(round(rx), round(ry), round(room.cols * scale), round(room.rows_count * scale))
        current = room is play.room
        pygame.draw.rect(surf, (40, 46, 66) if current else (28, 32, 46), rect)
        edge = room.palette[3]
        for ty in range(room.rows_count):
            for tx in range(room.cols):
                if room.tile(tx, ty) == "#":
                    px, py = to_screen(room.origin_tx + tx, room.origin_ty + ty)
                    pygame.draw.rect(surf, edge, (int(px), int(py), max(1, int(scale + 0.6)), max(1, int(scale + 0.6))))
        pygame.draw.rect(surf, Colors.UI_ACCENT if current else Colors.UI_DIM, rect, 1)
        for s in room.spawns:
            icon = {"B": (Colors.ENERGY, "banco"), "$": (Colors.NPC_SHOP, "loja"),
                    "R": (Colors.NPC_SMITH, "ferreiro")}.get(s[0])
            if icon:
                px, py = to_screen(room.origin_tx + s[1] / World.TILE, room.origin_ty + s[2] / World.TILE)
                pygame.draw.circle(surf, icon[0], (int(px), int(py - 3)), 4)
    if progress.equipped("bussola"):
        r = play.room
        p = play.player
        px, py = to_screen(r.origin_tx + p.cx / World.TILE, r.origin_ty + p.cy / World.TILE)
        pygame.draw.circle(surf, (255, 255, 255), (int(px), int(py)), 5)
        pygame.draw.circle(surf, Colors.PLAYER, (int(px), int(py)), 3)
    else:
        text(surf, "Equipe a Bússola para ver onde você está.", 20, (40, Display.HEIGHT - 50), Colors.UI_DIM)
    # legenda
    lx = Display.WIDTH - 200
    for i, (col, name) in enumerate([(Colors.ENERGY, "banco"), (Colors.NPC_SHOP, "loja"),
                                     (Colors.NPC_SMITH, "ferreiro")]):
        pygame.draw.circle(surf, col, (lx, Display.HEIGHT - 72 + i * 18), 4)
        text(surf, name, 18, (lx + 10, Display.HEIGHT - 79 + i * 18), Colors.UI_DIM)
