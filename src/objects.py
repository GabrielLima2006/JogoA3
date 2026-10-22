"""Objetos do cenário: moedas, itens, banco, loja, ferreiro e bolsa perdida."""

import math
import random

import pygame

from .config import Colors, Economy as EC, Physics as PH, World
from .physics import Body, move_and_collide, rects_overlap
from .ui import text

T = World.TILE


class Coin(Body):
    def __init__(self, x, y, value):
        size = 8 if value < 5 else 11
        super().__init__(x - size / 2, y - size / 2, size, size)
        self.value = value
        self.vx = random.uniform(-160, 160)
        self.vy = random.uniform(-420, -220)
        self.life = EC.COIN_LIFETIME
        self.alive = True
        self.homing = False
        self.spin = random.uniform(0, math.tau)

    def update(self, dt, room, player, magnet):
        self.life -= dt
        self.spin += dt * 8
        if self.life <= 0:
            self.alive = False
            return
        dx = player.cx - self.cx
        dy = player.cy - self.cy
        dist = math.hypot(dx, dy)
        if player.alive and (dist < magnet or self.homing):
            # voa até o jogador ignorando o cenário (evita moeda presa em parede)
            self.homing = True
            speed = 520.0
            self.x += dx / (dist or 1) * speed * dt
            self.y += dy / (dist or 1) * speed * dt
            return
        self.vy = min(self.vy + PH.GRAVITY * dt, PH.MAX_FALL_SPEED)
        move_and_collide(self, self.vx * dt, self.vy * dt, room, oob_solid=True)
        if self.on_ground:
            self.vy = -self.vy * 0.35 if abs(self.vy) > 120 else 0.0
            self.vx *= 0.6
        if self.hit_left or self.hit_right:
            self.vx = -self.vx * 0.5
        if self.hit_ceiling:
            self.vy = 0.0

    def draw(self, surf, cam_x, cam_y):
        w = max(2, int(self.w * abs(math.cos(self.spin))))
        r = pygame.Rect(0, 0, w, self.h)
        r.center = (int(self.cx - cam_x), int(self.cy - cam_y))
        pygame.draw.rect(surf, Colors.COIN, r, border_radius=2)


def spawn_coins(target_list, x, y, amount):
    """Divide o valor em moedas grandes (5) e pequenas (1)."""
    big, small = divmod(amount, 5)
    for _ in range(big):
        target_list.append(Coin(x, y, 5))
    for _ in range(small):
        target_list.append(Coin(x, y, 1))


class ItemPickup:
    """Item no chão (pedestal brilhante) ou baú de moedas."""

    def __init__(self, room_id, index, kind, arg, foot_x, foot_y):
        self.key = f"{room_id}:{index}"
        self.kind = kind
        self.arg = arg
        self.x = foot_x
        self.y = foot_y
        self.t = random.uniform(0, 5)
        self.alive = True

    def rect(self):
        if self.kind == "coins":
            return (self.x - 14, self.y - 22, 28, 22)
        return (self.x - 10, self.y - 34, 20, 26)

    def draw(self, surf, cam_x, cam_y, time):
        x, y = self.x - cam_x, self.y - cam_y
        if self.kind == "coins":
            pygame.draw.rect(surf, Colors.CHEST, (x - 14, y - 20, 28, 20), border_radius=3)
            pygame.draw.rect(surf, Colors.COIN, (x - 14, y - 14, 28, 3))
            pygame.draw.rect(surf, Colors.COIN, (x - 3, y - 16, 6, 6))
            return
        bob = math.sin(time * 3 + self.t) * 3
        glow = 10 + 3 * math.sin(time * 5 + self.t)
        color = {"ability": (130, 230, 255), "charm": (240, 160, 255), "fragment": Colors.HP_FULL,
                 "ore": (180, 200, 220)}.get(self.kind, Colors.ITEM)
        pygame.draw.circle(surf, tuple(c // 3 for c in color), (int(x), int(y - 20 + bob)), int(glow))
        if self.kind == "fragment":
            pts = [(x, y - 30 + bob), (x + 7, y - 20 + bob), (x, y - 10 + bob), (x - 7, y - 20 + bob)]
            pygame.draw.polygon(surf, color, pts)
        elif self.kind == "ore":
            pygame.draw.polygon(surf, color, [(x - 8, y - 12 + bob), (x - 3, y - 27 + bob),
                                              (x + 6, y - 24 + bob), (x + 8, y - 13 + bob)])
        else:
            pygame.draw.circle(surf, color, (int(x), int(y - 20 + bob)), 7)
            pygame.draw.circle(surf, (255, 255, 255), (int(x), int(y - 20 + bob)), 3)


class Interactable:
    """Base de banco/loja/ferreiro: mostra um aviso e reage ao botão de interagir."""
    kind = ""
    prompt = ""
    w, h = 40, 40

    def __init__(self, foot_x, foot_y):
        self.x = foot_x
        self.y = foot_y

    def rect(self):
        return (self.x - self.w / 2, self.y - self.h, self.w, self.h)

    def near(self, player):
        r = self.rect()
        zone = (r[0] - 10, r[1] - 10, r[2] + 20, r[3] + 20)
        return rects_overlap(zone, player.rect_tuple())

    def draw_prompt(self, surf, cam_x, cam_y):
        text(surf, f"[W] {self.prompt}", 22, (int(self.x - cam_x), int(self.y - self.h - 22 - cam_y)),
             Colors.UI_TEXT, "midbottom")


class Bench(Interactable):
    kind = "bench"
    prompt = "Sentar"
    w, h = 56, 22

    def draw(self, surf, cam_x, cam_y, time):
        x, y = self.x - cam_x, self.y - cam_y
        pygame.draw.rect(surf, Colors.BENCH, (x - 28, y - 16, 56, 6), border_radius=2)
        pygame.draw.rect(surf, Colors.BENCH, (x - 24, y - 10, 5, 10))
        pygame.draw.rect(surf, Colors.BENCH, (x + 19, y - 10, 5, 10))
        pygame.draw.rect(surf, Colors.BENCH, (x - 28, y - 30, 4, 16))
        pygame.draw.rect(surf, Colors.BENCH, (x - 28, y - 30, 56, 4), border_radius=2)


class NPC(Interactable):
    w, h = 28, 46

    def __init__(self, foot_x, foot_y, kind):
        super().__init__(foot_x, foot_y)
        self.kind = kind
        self.prompt = "Loja" if kind == "shop" else "Ferreiro"
        self.color = Colors.NPC_SHOP if kind == "shop" else Colors.NPC_SMITH

    def draw(self, surf, cam_x, cam_y, time):
        x, y = self.x - cam_x, self.y - cam_y
        breath = math.sin(time * 2) * 1.5
        body = pygame.Rect(0, 0, 28, int(40 + breath))
        body.midbottom = (int(x), int(y))
        pygame.draw.rect(surf, self.color, body, border_radius=6)
        pygame.draw.rect(surf, (30, 24, 30), (body.centerx - 8, body.y + 9, 4, 4))
        pygame.draw.rect(surf, (30, 24, 30), (body.centerx + 4, body.y + 9, 4, 4))
        if self.kind == "smith":
            pygame.draw.rect(surf, (90, 90, 100), (x - 34, y - 14, 20, 14))     # bigorna
            pygame.draw.rect(surf, (90, 90, 100), (x - 38, y - 18, 28, 5))
        else:
            pygame.draw.rect(surf, (120, 90, 60), (x + 18, y - 22, 26, 22))    # balcão
            pygame.draw.circle(surf, Colors.COIN, (int(x + 31), int(y - 26)), 4)


class CoinBag:
    """Moedas perdidas na morte. Encoste para recuperar."""

    def __init__(self, x, y, amount):
        self.x, self.y = x, y
        self.amount = amount

    def rect(self):
        return (self.x - 14, self.y - 28, 28, 28)

    def draw(self, surf, cam_x, cam_y, time):
        x = self.x - cam_x
        y = self.y - cam_y + math.sin(time * 2.5) * 3
        pygame.draw.circle(surf, (60, 50, 80), (int(x), int(y - 14)), 16)
        pygame.draw.circle(surf, (150, 120, 200), (int(x), int(y - 14)), 11)
        pygame.draw.circle(surf, Colors.COIN, (int(x), int(y - 14)), 4)


class Character(Interactable):
    """Personagem da história: conversa com W. Visual provisório por estilo."""
    kind = "talk"

    def __init__(self, foot_x, foot_y, char_id, data):
        super().__init__(foot_x, foot_y)
        self.char_id = char_id
        self.data = data
        self.style = data.get("style", "")
        self.color = data["color"]
        self.h = data.get("height", 42)
        self.w = 28
        self.prompt = data.get("prompt", "Conversar")
        if self.style == "corpo":
            # deitada sobre a mesa: área de interação larga para examinar do chão
            self.w, self.h = 170, 18

    def draw(self, surf, cam_x, cam_y, time):
        draw_character(surf, self.style, self.color, self.h, self.x - cam_x, self.y - cam_y, time)


def draw_character(surf, style, color, height, x, foot_y, time=0.0, scale=1.0):
    """Desenho provisório dos personagens (também usado no retrato do diálogo)."""
    s = scale
    if style == "corpo":
        # caída sobre a mesa: corpo deitado + chapéu de capitã
        pygame.draw.rect(surf, color, (x - 22 * s, foot_y - 14 * s, 44 * s, 14 * s), border_radius=round(4 * s))
        pygame.draw.circle(surf, (225, 190, 170), (int(x - 24 * s), int(foot_y - 9 * s)), int(7 * s))
        pygame.draw.polygon(surf, (40, 34, 50), [(x - 34 * s, foot_y - 14 * s), (x - 16 * s, foot_y - 14 * s),
                                                 (x - 26 * s, foot_y - 24 * s)])
        return
    breath = math.sin(time * 2 + x * 0.01) * 1.2 * s
    w, h = 26 * s, height * s + breath
    body = pygame.Rect(0, 0, round(w), round(h))
    body.midbottom = (int(x), int(foot_y))
    pygame.draw.rect(surf, color, body, border_radius=round(6 * s))
    face_y = body.y + round(9 * s)
    pygame.draw.rect(surf, (30, 24, 30), (body.centerx - round(7 * s), face_y, round(4 * s), round(4 * s)))
    pygame.draw.rect(surf, (30, 24, 30), (body.centerx + round(3 * s), face_y, round(4 * s), round(4 * s)))
    if style == "chef":
        pygame.draw.rect(surf, (245, 245, 245), (body.x + 3 * s, body.y - 12 * s, w - 6 * s, 13 * s),
                         border_radius=round(5 * s))
        pygame.draw.rect(surf, (245, 245, 245), (body.x, body.y + h * 0.45, w, 6 * s))      # avental
    elif style == "boné":
        pygame.draw.rect(surf, (70, 90, 140), (body.x, body.y - 4 * s, w, 7 * s), border_radius=round(3 * s))
        pygame.draw.rect(surf, (70, 90, 140), (body.right - 2 * s, body.y, 8 * s, 3 * s))
    elif style == "casaco":
        pygame.draw.rect(surf, (50, 56, 90), (body.x - 2 * s, body.y + h * 0.35, w + 4 * s, h * 0.65),
                         border_radius=round(4 * s))
        pygame.draw.rect(surf, (220, 190, 90), (body.centerx - 2 * s, body.y + h * 0.4, 4 * s, 4 * s))
        pygame.draw.polygon(surf, (40, 40, 60), [(body.x - 6 * s, body.y + 1 * s), (body.right + 6 * s, body.y + 1 * s),
                                                (body.centerx, body.y - 9 * s)])
    elif style == "bandana":
        pygame.draw.rect(surf, (160, 30, 40), (body.x, body.y, w, 6 * s))
        pygame.draw.polygon(surf, (160, 30, 40), [(body.x, body.y + 2 * s), (body.x - 8 * s, body.y + 8 * s),
                                                  (body.x - 2 * s, body.y + 10 * s)])
        pygame.draw.circle(surf, (230, 200, 90), (int(body.right - 3 * s), int(face_y + 10 * s)), max(1, int(2 * s)))
    elif style == "cachecol":
        pygame.draw.rect(surf, (90, 60, 110), (body.x - 2 * s, body.y + 15 * s, w + 4 * s, 6 * s))
        pygame.draw.rect(surf, (90, 60, 110), (body.x + 3 * s, body.y + 18 * s, 6 * s, 14 * s))
