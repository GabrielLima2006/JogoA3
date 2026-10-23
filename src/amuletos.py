"""Ícones dos amuletos (um desenho para cada) e a tela de equipar no banco."""

import math

import pygame

from . import pixelart, ui
from .config import Colors, Display
from .progress import CHARMS

W, H = Display.WIDTH, Display.HEIGHT
ORDER = ["lamina", "forca", "vigor", "foco", "vento", "coletor", "ima", "bussola"]
_icons = {}

GOLD = (230, 196, 100)
GOLD_DK = (150, 110, 50)


def _gem(s, c, r, color):
    pygame.draw.circle(s, color, c, r)
    pygame.draw.circle(s, pixelart.shade(color, 60), (c[0] - r // 3, c[1] - r // 3), max(1, r // 3))


def charm_icon(cid, size=40, locked=False):
    key = (cid, size, locked)
    if key in _icons:
        return _icons[key]
    s = pygame.Surface((32, 32), pygame.SRCALPHA)
    # moldura redonda dourada (todos os amuletos)
    pygame.draw.circle(s, GOLD_DK, (16, 16), 15)
    pygame.draw.circle(s, (36, 30, 54), (16, 16), 13)
    if cid == "lamina":                     # Lâmina Longa: espada comprida
        pygame.draw.line(s, (220, 230, 245), (9, 23), (23, 7), 3)
        pygame.draw.line(s, (255, 255, 255), (10, 22), (22, 8), 1)
        pygame.draw.line(s, GOLD, (8, 18), (14, 24), 2)
    elif cid == "forca":                    # Força Bruta: punho/martelo
        pygame.draw.rect(s, (200, 90, 70), (9, 9, 14, 9), border_radius=2)
        pygame.draw.rect(s, (130, 80, 50), (15, 17, 3, 9))
        pygame.draw.line(s, (255, 160, 140), (10, 10), (21, 10), 1)
    elif cid == "vigor":                    # Vigor: coração
        pygame.draw.circle(s, (230, 60, 80), (12, 13), 5)
        pygame.draw.circle(s, (230, 60, 80), (20, 13), 5)
        pygame.draw.polygon(s, (230, 60, 80), [(7, 15), (25, 15), (16, 25)])
        pygame.draw.circle(s, (255, 170, 180), (11, 11), 2)
    elif cid == "foco":                     # Foco Rápido: gota de energia
        pygame.draw.polygon(s, (120, 200, 255), [(16, 6), (23, 18), (9, 18)])
        pygame.draw.circle(s, (120, 200, 255), (16, 19), 7)
        pygame.draw.circle(s, (230, 250, 255), (13, 17), 2)
    elif cid == "vento":                    # Passo de Vento: redemoinho
        for i, r in enumerate((10, 7, 4)):
            pygame.draw.arc(s, (170, 230, 220), (16 - r, 16 - r, r * 2, r * 2), i * 1.2, i * 1.2 + 4.2, 2)
    elif cid == "coletor":                  # Coletor: orbe de alma
        _gem(s, (16, 16), 8, (190, 120, 255))
        for a in range(0, 360, 90):
            x = 16 + math.cos(math.radians(a)) * 11
            y = 16 + math.sin(math.radians(a)) * 11
            pygame.draw.circle(s, (230, 200, 255), (round(x), round(y)), 1)
    elif cid == "ima":                      # Ímã
        pygame.draw.arc(s, (220, 60, 60), (8, 8, 16, 18), math.pi, 2 * math.pi, 5)
        pygame.draw.rect(s, (220, 60, 60), (8, 15, 5, 6))
        pygame.draw.rect(s, (220, 60, 60), (19, 15, 5, 6))
        pygame.draw.rect(s, (230, 230, 240), (8, 9, 5, 4))
        pygame.draw.rect(s, (230, 230, 240), (19, 9, 5, 4))
    elif cid == "bussola":                  # Bússola
        pygame.draw.circle(s, (230, 220, 190), (16, 16), 9)
        pygame.draw.polygon(s, (220, 60, 60), [(16, 8), (19, 16), (13, 16)])
        pygame.draw.polygon(s, (60, 60, 80), [(16, 24), (19, 16), (13, 16)])
    pygame.draw.circle(s, GOLD, (16, 16), 15, 2)
    if locked:
        s.fill((30, 26, 40, 255), special_flags=pygame.BLEND_RGBA_MIN)
        pygame.draw.circle(s, (70, 64, 90), (16, 16), 15, 2)
    s = pixelart.outline(s)
    s = pygame.transform.scale(s, (size, size))
    _icons[key] = s
    return s


def draw_notches(surf, x, y, used, total):
    """Espaços de amuleto como gemas: cheias = usadas."""
    for i in range(total):
        c = (x + i * 22, y)
        pygame.draw.circle(surf, (20, 16, 30), c, 9)
        if i < used:
            _gem(surf, c, 7, (210, 170, 255))
        else:
            pygame.draw.circle(surf, (90, 80, 120), c, 7, 2)


class CharmScreen:
    """Lógica e desenho da tela de amuletos (usada pelo estado do banco)."""
    COLS = 4

    def __init__(self, progress):
        self.pr = progress
        self.index = 0
        self.rects = []
        self.close_rect = pygame.Rect(0, 0, 0, 0)

    def owned(self, cid):
        return cid in self.pr.charms_owned

    def selected(self):
        return ORDER[self.index] if self.index < len(ORDER) else None

    def move(self, dx, dy):
        n = len(ORDER)
        col, row = self.index % self.COLS, self.index // self.COLS
        col = (col + dx) % self.COLS
        row = (row + dy) % (n // self.COLS)
        self.index = row * self.COLS + col

    def draw(self, surf, t, notice=""):
        pr = self.pr
        panel = pygame.Rect(60, 70, W - 120, H - 140)
        pygame.draw.rect(surf, (22, 18, 34), panel, border_radius=12)
        pygame.draw.rect(surf, GOLD_DK, panel, 2, border_radius=12)
        ui.text(surf, "Amuletos", 48, (W // 2, 40), Colors.UI_TEXT, "center", title=True)
        # espaços
        ui.text(surf, "Espaços", 22, (90, 92), Colors.UI_DIM)
        draw_notches(surf, 190, 104, pr.notches_used, pr.notches)
        # equipados
        ui.text(surf, "Equipados", 22, (90, 128), Colors.UI_DIM)
        ex = 190
        for cid in pr.charms_equipped:
            surf.blit(charm_icon(cid, 30), (ex - 15, 124))
            ex += 36
        if not pr.charms_equipped:
            ui.text(surf, "nenhum", 20, (190, 130), Colors.UI_DIM)
        # grade
        self.rects = []
        gx, gy, cell = 96, 190, 92
        for i, cid in enumerate(ORDER):
            r = pygame.Rect(gx + (i % self.COLS) * cell, gy + (i // self.COLS) * cell, 76, 76)
            self.rects.append(r)
            sel = i == self.index
            eq = cid in pr.charms_equipped
            pygame.draw.rect(surf, (40, 34, 60) if sel else (30, 26, 44), r, border_radius=10)
            pygame.draw.rect(surf, Colors.UI_ACCENT if sel else ((210, 170, 255) if eq else (70, 64, 90)), r,
                             3 if sel or eq else 1, border_radius=10)
            bob = math.sin(t * 4) * 2 if sel else 0
            icon = charm_icon(cid, 52, locked=not self.owned(cid))
            surf.blit(icon, icon.get_rect(center=(r.centerx, r.centery + bob)))
            if eq:
                pygame.draw.circle(surf, (210, 170, 255), (r.right - 10, r.top + 10), 6)
        # detalhes
        cid = self.selected()
        dx0 = 500
        box = pygame.Rect(dx0, 180, W - 60 - dx0 - 24, 230)
        pygame.draw.rect(surf, (30, 26, 44), box, border_radius=10)
        if cid and self.owned(cid):
            c = CHARMS[cid]
            surf.blit(charm_icon(cid, 64), (box.x + 16, box.y + 16))
            ui.text(surf, c["name"], 34, (box.x + 96, box.y + 20), Colors.UI_TEXT)
            ui.text(surf, "custo", 20, (box.x + 96, box.y + 62), Colors.UI_DIM)
            draw_notches(surf, box.x + 160, box.y + 72, c["cost"], c["cost"])
            ui.wrap_text(surf, c["desc"], 22, box.x + 16, box.y + 110, box.w - 32)
            eq = cid in pr.charms_equipped
            if eq:
                status, col = "Equipado - Enter para tirar", (210, 170, 255)
            elif pr.can_equip(cid):
                status, col = "Enter para equipar", Colors.UI_ACCENT
            else:
                status, col = "Sem espaço livre", Colors.HP_FULL
            ui.text(surf, status, 22, (box.x + 16, box.bottom - 34), col)
        else:
            ui.text(surf, "???", 40, (box.centerx, box.y + 70), Colors.UI_DIM, "center")
            ui.text(surf, "Amuleto ainda não encontrado.", 22, (box.centerx, box.y + 130), Colors.UI_DIM, "center")
        # rodapé
        self.close_rect = pygame.Rect(0, 0, 200, 36)
        self.close_rect.center = (box.centerx, box.bottom + 40)
        pygame.draw.rect(surf, (40, 34, 60), self.close_rect, border_radius=8)
        pygame.draw.rect(surf, GOLD_DK, self.close_rect, 2, border_radius=8)
        ui.text(surf, "Levantar (ESC)", 22, self.close_rect.center, Colors.UI_TEXT, "center")
        msg = notice or "Setas/WASD escolhem - Enter ou clique equipam - ESC levanta"
        ui.text(surf, msg, 20, (W // 2, H - 52), Colors.ITEM if notice else Colors.UI_DIM, "center")
