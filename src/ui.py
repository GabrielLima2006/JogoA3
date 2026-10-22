"""Interface provisória: HUD, menus, inventário, mapa e textos."""

import os

import pygame

from .config import Colors, Dash, Display, Energy, Progression, World
from .input import CONTROLS_TEXT
from .paths import asset

_fonts = {}


TITLE_FONT = asset("fonts", "alagard.ttf")


def font(size, title=False):
    """Fonte padrão; `title=True` usa a fonte de títulos (alagard), se existir."""
    key = (size, title)
    if key not in _fonts:
        if title and os.path.isfile(TITLE_FONT):
            _fonts[key] = pygame.font.Font(TITLE_FONT, int(size * 0.62))
        else:
            _fonts[key] = pygame.font.Font(None, size)
    return _fonts[key]


def text(surf, msg, size, pos, color=Colors.UI_TEXT, anchor="topleft", title=False):
    img = font(size, title).render(msg, True, color)
    rect = img.get_rect(**{anchor: pos})
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
            r = text(surf, msg, self.size, (Display.WIDTH // 2, int(top + i * self.spacing)), col, "center",
                     title=True)
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

def draw_hud(surf, player, progress, room_name, room_name_timer, fps=None):
    # orbe de energia
    cx, cy, r = 38, 40, 24
    pygame.draw.circle(surf, (24, 26, 40), (cx, cy), r)
    k = player.energy / Energy.MAX
    if k > 0:
        fill = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(fill, (*Colors.ENERGY, 255), (r, r), r - 3)
        cut = int((r * 2) * (1 - k))
        fill.fill((0, 0, 0, 0), (0, 0, r * 2, cut))
        surf.blit(fill, (cx - r, cy - r))
    ready = player.energy >= Energy.HEAL_COST
    pygame.draw.circle(surf, Colors.UI_ACCENT if ready else Colors.UI_DIM, (cx, cy), r, 2)
    if ready:
        text(surf, "F", 20, (cx, cy), (20, 24, 40), "center")

    # vida
    x, y = 72, 18
    for i in range(player.max_hp):
        col = Colors.HP_FULL if i < player.hp else Colors.HP_EMPTY
        pygame.draw.rect(surf, col, (x + i * 24, y, 18, 18), border_radius=4)
        pygame.draw.rect(surf, (20, 14, 22), (x + i * 24, y, 18, 18), 2, border_radius=4)
    # moedas
    pygame.draw.rect(surf, Colors.COIN, (x + 1, 46, 10, 10), border_radius=2)
    text(surf, str(progress.coins), 24, (x + 18, 43), Colors.COIN)

    # habilidades
    y2 = 70
    ax = 14
    if "dash" in player.abilities:
        _ability_dash(surf, ax, y2, player)
        ax += 58
    if "double_jump" in player.abilities:
        _ability_icon(surf, ax, y2, "2x", "PULO", player.can_air_jump)

    text(surf, "ESC: pausa · M: mapa", 20, (Display.WIDTH - 14, Display.HEIGHT - 22), Colors.UI_DIM, "topright")

    if room_name_timer > 0:
        alpha = min(1.0, room_name_timer / 0.4)
        col = tuple(int(c * alpha) for c in Colors.UI_TEXT)
        text(surf, room_name, 30, (Display.WIDTH // 2, 22), col, "midtop", title=True)
    if fps is not None:
        text(surf, f"FPS {fps:.0f}", 20, (Display.WIDTH - 14, 14), Colors.UI_DIM, "topright")


def draw_boss_bar(surf, name, hp, max_hp):
    w = 520
    x = (Display.WIDTH - w) // 2
    y = Display.HEIGHT - 46
    text(surf, name, 24, (Display.WIDTH // 2, y - 6), Colors.UI_TEXT, "midbottom")
    pygame.draw.rect(surf, (40, 20, 24), (x, y, w, 12), border_radius=4)
    pygame.draw.rect(surf, Colors.GUARDIAN, (x, y, int(w * max(0, hp) / max_hp), 12), border_radius=4)
    pygame.draw.rect(surf, (20, 10, 12), (x, y, w, 12), 2, border_radius=4)


def _ability_icon(surf, x, y, big, small, ready):
    rect = pygame.Rect(x, y, 52, 38)
    pygame.draw.rect(surf, (30, 34, 50), rect, border_radius=6)
    pygame.draw.rect(surf, Colors.UI_ACCENT if ready else Colors.UI_DIM, rect, 2, border_radius=6)
    text(surf, big, 21, (rect.centerx, rect.y + 5), Colors.UI_TEXT if ready else Colors.UI_DIM, "midtop")
    text(surf, small, 15, (rect.centerx, rect.bottom - 13), Colors.UI_DIM, "midtop")


def _ability_dash(surf, x, y, player):
    rect = pygame.Rect(x, y, 52, 38)
    pygame.draw.rect(surf, (30, 34, 50), rect, border_radius=6)
    total = Dash.DURATION + player.dash_cooldown_time
    k = player.dash_cooldown / total if total else 0
    if k > 0:
        h = int(rect.h * k)
        pygame.draw.rect(surf, (45, 60, 80), (rect.x, rect.bottom - h, rect.w, h), border_radius=6)
    ready = player.dash_ready
    pygame.draw.rect(surf, Colors.UI_ACCENT if ready else Colors.UI_DIM, rect, 2, border_radius=6)
    text(surf, "SHIFT", 18, (rect.centerx, rect.y + 6), Colors.UI_TEXT if ready else Colors.UI_DIM, "midtop")
    text(surf, "DASH", 15, (rect.centerx, rect.bottom - 13), Colors.UI_DIM, "midtop")


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
