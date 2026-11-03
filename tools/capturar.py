"""Capturas do jogo sem janela, para revisar sprites e cenários.

Uso: python tools/capturar.py [pasta_saida] [salas|galeria|tudo]

- galeria.png: todos os personagens, inimigos, chefes e itens lado a lado com a
  protagonista (escala 2x, linha do chão marcada), para conferir tamanho e direção.
- salas/<id>.png: cada sala inteira montada a partir de várias telas da câmera.
"""

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

import pygame  # noqa: E402

from helpers import Sim  # noqa: E402
from src import bosses, creatures, elenco, pixelart, skins, sprites  # noqa: E402
from src.config import Display  # noqa: E402
from src import ui  # noqa: E402


def _label(surf, text, x, y):
    surf.blit(ui.font(14).render(text, True, (230, 230, 230)), (x, y))


def galeria(out_dir):
    pygame.init()
    pygame.display.set_mode((Display.WIDTH, Display.HEIGHT))
    cell_w, floor = 120, 150
    entries = []

    skin = skins.SKINS["ela"]

    def protag(name):
        def draw(s, x, y, facing):
            fr = skins.frame_for(skin, name, 0.3)
            ax = skin.anchor_x(name)
            sprites.blit_anchor(s, fr, x, y, (ax, fr.get_height() - 1), flip=(facing > 0) != skin.faces_right)
        return draw

    for n in ("idle", "run", "jump", "fall", "quick", "heavy", "up", "diag", "down", "dash", "hurt", "land"):
        entries.append(("ela:" + n, protag(n)))

    for style in elenco.CAST:
        def draw(s, x, y, facing, style=style):
            img = elenco.character(style, "idle", 0.0, facing)
            s.blit(img, img.get_rect(midbottom=(x, y + 3)))
        entries.append((style, draw))
        def draw_w(s, x, y, facing, style=style):
            img = elenco.character(style, "walk", 0.3, facing)
            s.blit(img, img.get_rect(midbottom=(x, y + 3)))
        entries.append((style + ":anda", draw_w))

    creatures.npc_frame("lobo")
    names = list(creatures._NPC_META["rows"].keys())
    for n in names:
        def draw(s, x, y, facing, n=n):
            creatures.draw_model(s, n, x, y, 0.0, facing)
        entries.append((n, draw))

    def rat(s, x, y, facing):
        img = pixelart.rat(0.2, facing)
        s.blit(img, img.get_rect(midbottom=(x, y)))
    def gull(s, x, y, facing):
        img = pixelart.gull(0.2, facing)
        s.blit(img, img.get_rect(center=(x, y - 40)))
    def slime(s, x, y, facing):
        fr = sprites.grid("inimigos/slime.png", 48, 32)
        if fr:
            v = sprites.variant(fr[0], facing > 0)
            s.blit(v, v.get_rect(midbottom=(x, y)))
    def cannon(s, x, y, facing):
        img = pixelart.cannon(facing)
        s.blit(img, img.get_rect(midbottom=(x, y)))
    def crate(s, x, y, facing):
        img = pixelart.crate()
        s.blit(img, img.get_rect(midbottom=(x, y)))
    def rei(s, x, y, facing):
        img = sprites.variant(sprites.image("chefes", "rei_rato_parado.png"), facing > 0, False, 2)
        s.blit(img, img.get_rect(midbottom=(x, y + 2)))
    def knight(s, x, y, facing):
        fr = sprites.grid(bosses.KNIGHT, 80, 80)
        if fr:
            sprites.blit_anchor(s, fr[0], x, y, (38, 79), flip=facing < 0, scale=2)
    def irma(s, x, y, facing):
        img = sprites.image("personagens", "selka.png")
        if img is None:
            img = pixelart.human("irma", "idle", 0.0, facing)
            v = sprites.variant(img, False, False, 2)
        else:
            v = sprites.variant(img, facing > 0)
        s.blit(v, v.get_rect(midbottom=(x, y + 2)))
    def mago(s, x, y, facing):
        img = sprites.image("personagens", "caelum.png")
        if img is None:
            img = pixelart.sorcerer("idle", 0.0, facing)
        else:
            img = sprites.variant(img, facing > 0)
        s.blit(img, img.get_rect(midbottom=(x, y + 4)))
    def capita(s, x, y, facing):
        img = pixelart.corpse()
        s.blit(img, img.get_rect(midbottom=(x, y)))
    def amigo(s, x, y, facing):
        img = pixelart.human("amigo", "idle", 0.0, facing)
        s.blit(img, img.get_rect(midbottom=(x, y + 2)))
    for n, f in (("rato", rat), ("gaivota", gull), ("slime", slime), ("canhao", cannon), ("caixa", crate),
                 ("CHEFE rei_rato", rei), ("CHEFE cavaleiro", knight), ("CHEFE irma", irma),
                 ("CHEFE feiticeiro", mago), ("NPC Maren", capita), ("NPC Caelum", amigo)):
        entries.append((n, f))

    cols = 8
    rows = (len(entries) + cols - 1) // cols
    big = pygame.Surface((cols * cell_w, rows * (floor + 40)))
    big.fill((70, 74, 84))
    for i, (name, f) in enumerate(entries):
        cx = (i % cols) * cell_w + cell_w // 2
        y = (i // cols) * (floor + 40) + floor
        pygame.draw.line(big, (120, 200, 120), (cx - cell_w // 2 + 4, y), (cx + cell_w // 2 - 4, y))
        pygame.draw.line(big, (200, 120, 120), (cx - 6, y - 55), (cx + 6, y - 55))   # altura da protagonista
        try:
            f(big, cx, y, 1)        # todos olhando para a direita
        except Exception as e:      # mostra o erro no lugar
            _label(big, "ERRO " + type(e).__name__, cx - 50, y - 30)
        _label(big, name, cx - cell_w // 2 + 4, y + 6)
    big = pygame.transform.scale(big, (big.get_width() * 2, big.get_height() * 2))
    path = os.path.join(out_dir, "galeria.png")
    pygame.image.save(big, path)
    print("salvo", path)


def salas(out_dir, only=None):
    s = Sim(chapter=1)
    play = s.play
    hud = ui.draw_hud
    ui.draw_hud = lambda *a, **k: None          # sem HUD: a imagem é montada com várias telas
    os.makedirs(os.path.join(out_dir, "salas"), exist_ok=True)
    screen = pygame.display.get_surface()
    W, H = Display.WIDTH, Display.HEIGHT
    for rid, room in list(play.world.rooms.items()):
        if rid.startswith("L") or (only and rid not in only):
            continue
        play.load_room(room)
        for _ in range(30):
            play.fixed_update(1 / 120, s.inp)
            if s.app.state is not play:
                s.app.resume(play)
        full = pygame.Surface((max(W, room.width), max(H, room.height)))
        xs = list(range(0, max(1, room.width - W), W)) + [max(0, room.width - W)]
        ys = list(range(0, max(1, room.height - H), H)) + [max(0, room.height - H)]
        p = play.player
        for cy in ys:
            for cx in xs:
                play.camera.x, play.camera.y = cx, cy
                p.place(-500, -500)                 # protagonista fora da foto
                p.vx = p.vy = 0
                play.draw(screen)
                full.blit(screen, (cx, cy))
        full = pygame.transform.smoothscale(full, (full.get_width() // 2, full.get_height() // 2))
        path = os.path.join(out_dir, "salas", rid + ".png")
        pygame.image.save(full, path)
        print("salvo", path)
    ui.draw_hud = hud


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "capturas")
    what = sys.argv[2] if len(sys.argv) > 2 else "tudo"
    os.makedirs(out, exist_ok=True)
    if what in ("galeria", "tudo"):
        galeria(out)
    if what in ("salas", "tudo"):
        salas(out, sys.argv[3:] or None)
