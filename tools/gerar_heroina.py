"""Gera as animações da protagonista nova (feiticeira de chifres, 32x32, gerada pelo Gabriel no PixelLab).

O modelo veio só com poses paradas em 8 direções (parada e golpe de espada). O jogo é de lado,
então usamos a vista "west" (rosto à mostra, olhando para a esquerda) e criamos os outros quadros
mexendo nas partes do desenho, sempre em pixels inteiros (nada de borrão):

- respiração: tronco desce 1 px;
- corrida: pernas separadas em frente/trás e deslocadas em ciclo, tronco sobe e desce;
- golpes: inclinação para trás no preparo (cisalhamento por linha), quadro do golpe com o arco
  desenhado, e o arco sumindo na volta;
- pulo, queda, dash, dano e morte: inclinações, pernas encolhidas/esticadas e rotação final.

Trabalha em 48x40 e no fim dobra o tamanho (2x, vizinho mais próximo).

Uso:  python tools/gerar_heroina.py
Entrada: assets/fontes/heroina/parada_west.png, ataque_west.png
Saída:   assets/img/personagens/heroina.png (quadros de 96x80, pé na última linha, x = 48)
"""

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "fontes", "heroina")
OUT = os.path.join(ROOT, "assets", "img", "personagens", "heroina.png")

CW, CH = 48, 40           # quadro de trabalho
OFF = (8, 9)              # onde o canto do desenho 32x32 entra no quadro (pé em (24, 39))
SCALE = 2
WAIST = 21                # primeira linha das pernas/saia no desenho original
LEGS = 25                 # onde as pernas ficam separadas
SPLIT_X = 16              # coluna que divide perna da frente (x menor) e de trás

# linhas da folha (a ordem vale para src/skins.py)
ANIMS = ["idle", "run_start", "run", "jump", "fall", "land", "quick", "heavy", "up", "diag", "down",
         "dash", "hurt", "death", "heal"]

# cores do arco do golpe (azul-claro); a lâmina usa outros tons e fica
ARC = {(239, 253, 254), (200, 220, 240), (206, 227, 243), (153, 192, 229), (96, 116, 168), (147, 157, 196),
       (226, 225, 244)}


def load(name):
    return pygame.image.load(os.path.join(SRC, name)).convert_alpha()


def blank():
    return pygame.Surface((CW, CH), pygame.SRCALPHA)


def region(src, y0, y1, x0=0, x1=32):
    """Pedaço do desenho (linhas y0..y1-1, colunas x0..x1-1), no mesmo lugar."""
    s = pygame.Surface(src.get_size(), pygame.SRCALPHA)
    s.blit(src, (x0, y0), (x0, y0, x1 - x0, y1 - y0))
    return s


def shear(img, amount, base_y):
    """Inclina as linhas acima de `base_y`: a de cima anda `amount` px, a de baixo não anda.
    amount > 0 = para a direita (para trás, já que ela olha para a esquerda)."""
    w, h = img.get_size()
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        dx = round(amount * (base_y - y) / base_y) if y < base_y else 0
        out.blit(img, (dx, y), (0, y, w, 1))
    return out


def compose(parts):
    """parts: lista de (imagem 32x32, dx, dy). Monta no quadro de trabalho."""
    f = blank()
    for img, dx, dy in parts:
        f.blit(img, (OFF[0] + dx, OFF[1] + dy))
    return f


def body(src, lean=0, bob=0, front=(0, 0), back=(0, 0), lower=(0, 0)):
    """Tronco (com inclinação e sobe/desce) + quadril + pernas separadas."""
    upper = shear(region(src, 0, WAIST), lean, WAIST)
    hips = region(src, WAIST, LEGS)
    leg_f = region(src, LEGS, 32, 0, SPLIT_X)
    leg_b = region(src, LEGS, 32, SPLIT_X, 32)
    lx, ly = lower
    return compose([(leg_b, back[0] + lx, back[1] + ly), (leg_f, front[0] + lx, front[1] + ly),
                    (hips, lx, ly + min(0, bob)), (upper, 0, bob)])


def rotate_frame(frame, angle, pivot, shift=0):
    """Gira o quadro inteiro em volta de `pivot` e anda `shift` px de lado (queda da morte)."""
    w, h = frame.get_size()
    off = pygame.math.Vector2(w / 2 - pivot[0], h / 2 - pivot[1]).rotate(-angle)
    rot = pygame.transform.rotate(frame, angle)
    out = blank()
    out.blit(rot, rot.get_rect(center=(pivot[0] + off.x + shift, pivot[1] + off.y)))
    return out


def arc_alpha(src, alpha):
    """Golpe com o arco mais fraco (alpha 0 apaga). O arco fica nas bordas esquerda e direita."""
    s = src.copy()
    for y in range(32):
        for x in range(32):
            c = s.get_at((x, y))
            if c.a and tuple(c)[:3] in ARC and (x <= 10 or x >= 26):
                s.set_at((x, y), (c.r, c.g, c.b, alpha))
    return s


def build():
    pygame.init()
    pygame.display.set_mode((1, 1))
    idle = load("parada_west.png")
    atk = load("ataque_west.png")
    feet = (OFF[0] + 16, OFF[1] + 30)          # pé no quadro de trabalho

    run = []
    for i in range(8):
        a = i / 8 * 2 * math.pi
        step = round(2 * math.sin(a))
        run.append(body(idle, lean=-2, bob=-1 if i % 4 in (1, 2) else 0,
                        front=(-step, -1 if step < 0 else 0), back=(step, -1 if step > 0 else 0)))
    rows = {
        "idle": [body(idle), body(idle), body(idle, bob=1), body(idle, bob=1), body(idle, bob=1), body(idle)],
        "run_start": [body(idle, lean=-1, front=(-1, 0)), body(idle, lean=-2, front=(-2, -1), back=(1, 0))],
        "run": run,
        "jump": [body(idle, lean=-1, front=(-1, -2), back=(1, -1), lower=(0, -1)),
                 body(idle, lean=-1, front=(-2, -3), back=(1, -2), lower=(0, -1))],
        "fall": [body(idle, lean=1, front=(-1, 1), back=(1, 0), bob=-1),
                 body(idle, lean=2, front=(-1, 1), back=(2, 1), bob=-1)],
        "land": [body(idle, bob=2, front=(-1, 0), back=(1, 0))],
        # golpe: preparo inclinado para trás, golpe com o arco, arco sumindo
        "quick": [body(idle, lean=3), compose([(atk, 0, 0)]), compose([(arc_alpha(atk, 120), 0, 0)]),
                  compose([(arc_alpha(atk, 0), 0, 0)])],
        "heavy": [body(idle, lean=3), body(idle, lean=5, bob=1), compose([(atk, -1, 0)]), compose([(atk, -1, 0)]),
                  compose([(arc_alpha(atk, 110), -1, 0)]), compose([(arc_alpha(atk, 0), 0, 0)])],
        # para cima e diagonal: corpo estica para trás (o corte vem do efeito do jogo)
        "up": [body(idle, lean=2), body(idle, lean=3, bob=-1), body(idle, lean=1)],
        "diag": [body(idle, lean=3), body(idle, lean=1, bob=-1), body(idle, lean=-1, bob=-1), body(idle)],
        "down": [body(idle, lean=-3, front=(-1, -3), back=(1, -2), lower=(0, -2)),
                 body(idle, lean=-4, front=(-2, -3), back=(1, -3), lower=(0, -2))],
        "dash": [body(idle, lean=-5, front=(-2, -1), back=(3, 0)), body(idle, lean=-6, front=(-3, -1), back=(4, 0))],
        "hurt": [body(idle, lean=4, bob=1, front=(1, 0), back=(1, 0))],
        "death": [body(idle, lean=4, bob=1),
                  rotate_frame(body(idle, lean=4, bob=2), -15, feet, -2),
                  rotate_frame(body(idle, lean=4, bob=2), -40, feet, -6),
                  rotate_frame(body(idle, lean=2, bob=2), -70, feet, -10),
                  rotate_frame(body(idle, bob=2), -90, feet, -12)],
        "heal": [body(idle, bob=1), body(idle, bob=1)],
    }
    cols = max(len(v) for v in rows.values())
    sheet = pygame.Surface((CW * cols, CH * len(ANIMS)), pygame.SRCALPHA)
    for r, name in enumerate(ANIMS):
        for c, fr in enumerate(rows[name]):
            sheet.blit(fr, (c * CW, r * CH))
    sheet = pygame.transform.scale(sheet, (sheet.get_width() * SCALE, sheet.get_height() * SCALE))
    pygame.image.save(sheet, OUT)
    print(OUT, {k: len(v) for k, v in rows.items()})


if __name__ == "__main__":
    build()
    sys.exit(0)
