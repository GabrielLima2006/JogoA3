"""Dá vida a personagens que só têm uma pose parada (vista `east` do PixelLab).

Uso: python tools/animar_pose.py

Para cada personagem da tabela POSES, lê a pose `east` (olha para a direita), reduz para a
altura combinada com a protagonista (60 px) e monta uma folha com três linhas:

- linha 0, parado (4 quadros): respiração; o tronco desce 1 px nos quadros do meio.
- linha 1, andando (6 quadros): as pernas giram em torno do quadril por cisalhamento de
  pixels inteiros (sem borrar o contorno) e o corpo sobe 1 px quando as pernas se cruzam.
- linha 2, ataque (3 quadros): o tronco se inclina para a frente e volta.

Saída: assets/img/personagens/anim_<nome>.png e anim_poses.json (tamanho do quadro e pé).
A redução usa a cor mais frequente de cada bloco, o que preserva melhor o contorno do que
pegar um pixel só.
"""

import json
import math
import os
import sys
from collections import Counter

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, "assets", "img", "personagens")

# nome: (arquivo de origem em assets/img/personagens, altura final em px, quadril (fração da altura),
#        passada máxima do pé em px, quadrúpede?)
POSES = {
    "lobo": ("inimigo_lobo.png", 44, 0.55, 4, True, "bote"),
    "goblin": ("inimigo_goblin.png", 52, 0.76, 5, False, "golpe_curto"),
    "comerciante": ("npc_comerciante.png", 57, 0.62, 5, False),
    "ferreira": ("npc_ferreira.png", 57, 0.62, 5, False),
    "curandeira": ("npc_curandeira.png", 56, 0.64, 3, False),
    "pescador": ("npc_pescador.png", 57, 0.62, 5, False),
    "estudioso": ("npc_estudioso.png", 57, 0.62, 5, False),
    "bardo": ("npc_bardo.png", 56, 0.62, 5, False),
    "aldea": ("npc_aldea.png", 55, 0.64, 3, False),
    "anciao": ("npc_anciao.png", 53, 0.64, 3, False),
    "ancia": ("npc_ancia.png", 52, 0.66, 3, False),
    "grumete": ("npc_grumete.png", 47, 0.60, 4, False),
    # chefes: tamanho original (1x), só ganham o movimento
    "selka": ("selka.png", 62, 0.58, 5, False, "golpe"),
    "caelum": ("caelum.png", 59, 0.72, 0, False, True),
    # criaturas mágicas da folha da equipe: flutuam (sem passada) e conjuram no ataque
    "espirito": ("npcs.png#18", 50, 0.55, 0, False, True),
    "lich": ("npcs.png#22", 73, 0.55, 0, False, True),
    # capangas da folha da equipe: ladino (adaga) e cavaleiro do escudo (investida com o escudo)
    "ladino": ("npcs.png#15", 57, 0.62, 4, False, "golpe"),
    "cavaleiro_escudo": ("npcs.png#9", 59, 0.62, 4, False, "escudo"),
    # diabrete: voa (sem passada); no ataque recolhe as asas e mergulha de cabeça
    "diabrete": ("npcs.png#17", 47, 0.55, 0, False, "mergulho"),
}
FRAMES = {"idle": 4, "walk": 6, "attack": 3}
PAD = 8                                   # folga lateral para a passada e o ataque


def reduzir(src, altura):
    """Reduz `src` (já recortado) para `altura` px escolhendo a cor dominante de cada bloco."""
    w, h = src.get_size()
    f = altura / h
    nw, nh = max(1, round(w * f)), altura
    out = pygame.Surface((nw, nh), pygame.SRCALPHA)
    for ty in range(nh):
        y0, y1 = int(ty / f), max(int(ty / f) + 1, int((ty + 1) / f))
        for tx in range(nw):
            x0, x1 = int(tx / f), max(int(tx / f) + 1, int((tx + 1) / f))
            cores = Counter()
            total = 0
            for y in range(y0, min(y1, h)):
                for x in range(x0, min(x1, w)):
                    c = src.get_at((x, y))
                    total += 1
                    if c.a > 128:
                        cores[(c.r, c.g, c.b)] += 1
            opacos = sum(cores.values())
            if opacos * 2 >= total and cores:
                # contorno escuro tem prioridade quando empata, para não sumir
                cor = max(cores.items(), key=lambda kv: (kv[1], -sum(kv[0])))[0]
                out.set_at((tx, ty), cor + (255,))
    return out


def passada_bipede(body, hip, passo):
    """Bípede de perfil: as pernas aparecem juntas na pose parada. A perna de trás vira uma cópia
    um pouco mais escura que gira para trás, e a da frente gira para a frente por cima dela.
    Só entram as colunas dos pés, para não duplicar porrete, mão ou barra de roupa."""
    w, h = body.get_size()
    fundo = [x for y in range(h - 3, h) for x in range(w) if body.get_at((x, y)).a]
    if not fundo:
        return body.copy()
    x0, x1 = min(fundo) - 1, max(fundo) + 1
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    pernas = []
    for y in range(h):
        for x in range(w):
            c = body.get_at((x, y))
            if not c.a:
                continue
            if y >= hip and x0 <= x <= x1:
                pernas.append((x, y, c))
            else:
                out.set_at((x, y), c)
    altura = max(1, h - 1 - hip)
    for sinal, escuro in ((-1, True), (1, False)):
        for x, y, c in pernas:
            d = (y - hip) / altura
            dx = round(passo * sinal * d)
            lift = 1 if (passo * sinal > 1.5 and d > 0.85) else 0
            cor = (c.r * 3 // 4, c.g * 3 // 4, c.b * 3 // 4, 255) if escuro and abs(passo) >= 1 else c
            nx, ny = x + dx, y - lift
            if 0 <= nx < w and 0 <= ny < h and not (escuro and out.get_at((nx, ny)).a):
                out.set_at((nx, ny), cor)
    return out


def cisalhar(body, hip, passo, quadrupede, frente_sinal):
    """Pernas: metade de trás e da frente giram em sentidos opostos a partir do quadril."""
    if not quadrupede:
        return passada_bipede(body, hip, passo * frente_sinal)
    w, h = body.get_size()
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    out.blit(body, (0, 0), pygame.Rect(0, 0, w, hip))
    pernas = [(x, y) for y in range(hip, h) for x in range(w) if body.get_at((x, y)).a]
    if not pernas:
        return body.copy()
    xs = [p[0] for p in pernas]
    meio = (min(xs) + max(xs)) / 2
    tras, frente = [], []
    for x, y in pernas:
        (frente if x >= meio else tras).append((x, y))
    altura = max(1, h - 1 - hip)
    for grupo, sinal in ((tras, -1), (frente, 1)):
        s = sinal * frente_sinal
        for x, y in grupo:
            d = (y - hip) / altura
            dx = round(passo * s * d)
            # pé que vai à frente sobe um pouco no meio da passada
            lift = 1 if (passo * s > 0 and d > 0.8 and abs(passo) >= 2 and not quadrupede) else 0
            ny = y - lift
            if 0 <= x + dx < w and 0 <= ny < h:
                out.set_at((x + dx, ny), body.get_at((x, y)))
    return out


def inclinar(body, hip, avanco):
    """Tronco inclinado para a frente: cada linha acima do quadril avança proporcionalmente."""
    w, h = body.get_size()
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    out.blit(body, (0, hip), pygame.Rect(0, hip, w, h - hip))
    for y in range(hip):
        dx = round(avanco * (hip - y) / max(1, hip))
        out.blit(body, (dx, y), pygame.Rect(0, y, w, 1))
    return out


def respirar(body, hip):
    """Tronco desce 1 px (a linha do quadril se repete), pernas paradas."""
    w, h = body.get_size()
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    out.blit(body, (0, 1), pygame.Rect(0, 0, w, hip))
    out.blit(body, (0, hip), pygame.Rect(0, hip, w, h - hip))
    return out


def carregar(arquivo):
    """Arquivo em assets/img/personagens. "npcs.png#<linha>" recorta o modelo da folha da equipe
    (quadros de 128x96 olhando para a esquerda) e o vira para a direita, como as vistas east."""
    if "#" in arquivo:
        nome, linha = arquivo.split("#")
        folha = pygame.image.load(os.path.join(DEST, nome)).convert_alpha()
        quadro = folha.subsurface((0, int(linha) * 96, 128, 96)).copy()
        return pygame.transform.flip(quadro, True, False)
    return pygame.image.load(os.path.join(DEST, arquivo)).convert_alpha()


def conjurar(base, hip):
    """Ataque mágico (espírito, lich): recolhe, carrega com brilho roxo e lança para a frente."""
    w, h = base.get_size()
    recolhe = pygame.Surface((w, h), pygame.SRCALPHA)
    recolhe.blit(inclinar(base, hip, -3), (0, -1))
    carrega = pygame.Surface((w, h), pygame.SRCALPHA)
    carrega.blit(inclinar(base, hip, -5), (0, -2))
    brilho = carrega.copy()
    brilho.fill((48, 24, 72, 0), special_flags=pygame.BLEND_RGB_ADD)
    lanca = inclinar(base, hip, 6)
    return [recolhe, brilho, lanca]


def girar_tronco(base, hip, ang, dx=0, dy=0):
    """Gira só a parte de cima do corpo em volta do quadril (pernas paradas no chão).
    Giro sem suavizar: o pixel art continua nítido."""
    w, h = base.get_size()
    cima = pygame.Surface((w, hip), pygame.SRCALPHA)
    cima.blit(base, (0, 0), pygame.Rect(0, 0, w, hip))
    px = w // 2
    tela = pygame.Surface((w * 2, hip * 2), pygame.SRCALPHA)       # pivô no centro
    tela.blit(cima, (w - px, 0))
    g = pygame.transform.rotate(tela, ang)
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    out.blit(base, (0, hip), pygame.Rect(0, hip, w, h - hip))
    out.blit(g, g.get_rect(center=(px + dx, hip + dy)))
    return out


def golpear(base, hip, escudo=False):
    """Golpe de verdade (bípede olhando para a direita): arma para trás, tronco joga para a frente
    no golpe e acompanha o movimento. Escudo: investida com o corpo baixo e o escudo na frente."""
    if escudo:
        return [girar_tronco(base, hip, 8, -1), girar_tronco(base, hip, -16, 4, 2), girar_tronco(base, hip, -7, 2, 1)]
    return [girar_tronco(base, hip, 12, -1), girar_tronco(base, hip, -18, 3, 2), girar_tronco(base, hip, -8, 1, 1)]


def golpe_curto(base, hip):
    """Golpe de quem tem o quadril alto (goblin): giro menor para não parecer que cai."""
    return [girar_tronco(base, hip, 7, -1), girar_tronco(base, hip, -11, 3, 1), girar_tronco(base, hip, -5, 1)]


def bote(base, hip):
    """Bote do lobo: agacha, salta esticado de cabeça para a frente e aterrissa."""
    w, h = base.get_size()
    corpo = base.subsurface(base.get_bounding_rect()).copy()
    bw, bh = corpo.get_size()
    agacha = pygame.Surface((w, h), pygame.SRCALPHA)
    a = pygame.transform.scale(corpo, (bw + 2, bh - 4))
    agacha.blit(a, a.get_rect(midbottom=(w // 2 - 1, h - 1)))
    salto = pygame.Surface((w, h), pygame.SRCALPHA)
    e = pygame.transform.rotate(pygame.transform.scale(corpo, (bw + 6, bh - 2)), -8)
    salto.blit(e, e.get_rect(midbottom=(w // 2 + 4, h - 3)))
    pouso = pygame.Surface((w, h), pygame.SRCALPHA)
    p2 = pygame.transform.scale(corpo, (bw + 3, bh - 2))
    pouso.blit(p2, p2.get_rect(midbottom=(w // 2 + 3, h - 1)))
    return [agacha, salto, pouso]


def mergulhar(base, hip):
    """Ataque do diabrete: sobe recolhido, depois mergulha inclinado para a frente e para baixo."""
    w, h = base.get_size()
    recolhe = pygame.Surface((w, h), pygame.SRCALPHA)
    recolhe.blit(inclinar(base, hip, -4), (0, -1))
    quadros = [recolhe]
    for ang, dx, dy in ((-14, 1, 1), (-22, 2, 2)):
        # corpo todo inclinado de cabeça para a frente (giro sem suavizar, pixel art preservado)
        g = pygame.transform.rotate(inclinar(base, hip, 3), ang)
        q = pygame.Surface((w, h), pygame.SRCALPHA)
        q.blit(g, g.get_rect(center=(w // 2 + dx, h // 2 + dy)))
        quadros.append(q)
    return quadros


# modelos da folha da equipe que já olham para a direita (não viram ao recortar)
JA_OLHA_DIREITA = {"diabrete"}


def gerar(nome, arquivo, altura, quadril, passada, quadrupede, magico=False):
    src = carregar(arquivo)
    if nome in JA_OLHA_DIREITA:
        src = pygame.transform.flip(src, True, False)
    src = src.subsurface(src.get_bounding_rect()).copy()
    body = reduzir(src, altura)
    bw, bh = body.get_size()
    fw, fh = bw + PAD * 2, bh + 2                 # 1 px acima para o balanço, 1 abaixo de folga
    hip = round(bh * quadril)
    base = pygame.Surface((fw, fh), pygame.SRCALPHA)
    base.blit(body, (PAD, 1))
    hip += 1

    linhas = {"idle": [], "walk": [], "attack": []}
    for i in range(FRAMES["idle"]):
        linhas["idle"].append(respirar(base, hip) if i in (1, 2) else base.copy())
    for i in range(FRAMES["walk"]):
        a = math.sin(i / FRAMES["walk"] * math.tau)
        q = cisalhar(base, hip, passada * a, quadrupede, 1)
        if abs(a) < 0.6:                          # pernas cruzando: corpo um pouco mais alto
            up = pygame.Surface((fw, fh), pygame.SRCALPHA)
            up.blit(q, (0, -1))
            q = up
        linhas["walk"].append(q)
    for avanco in (() if magico else (2, 5, 3)):
        q = inclinar(base, hip, avanco)
        if quadrupede:                            # bote: o corpo todo avança e abaixa a cabeça
            q2 = pygame.Surface((fw, fh), pygame.SRCALPHA)
            q2.blit(cisalhar(base, hip, -2, True, 1), (avanco // 2, 0))
            q = inclinar(q2, hip, avanco // 2)
        linhas["attack"].append(q)
    if magico == "mergulho":
        linhas["attack"] = mergulhar(base, hip)
    elif magico == "golpe_curto":
        linhas["attack"] = golpe_curto(base, hip)
    elif magico in ("golpe", "escudo"):
        linhas["attack"] = golpear(base, hip, magico == "escudo")
    elif magico == "bote":
        linhas["attack"] = bote(base, hip)
    elif magico:
        linhas["attack"] = conjurar(base, hip)

    cols = max(FRAMES.values())
    sheet = pygame.Surface((fw * cols, fh * 3), pygame.SRCALPHA)
    for r, k in enumerate(("idle", "walk", "attack")):
        for c, q in enumerate(linhas[k]):
            sheet.blit(q, (c * fw, r * fh))
    pygame.image.save(sheet, os.path.join(DEST, f"anim_{nome}.png"))
    return {"frame": [fw, fh], "anchor": [PAD + bw // 2, fh - 1], "frames": FRAMES, "source": arquivo}


def main():
    pygame.init()
    pygame.display.set_mode((8, 8))
    # python tools/animar_pose.py [nomes...]: só refaz os nomes dados (os outros ficam como estão)
    so = sys.argv[1:]
    caminho = os.path.join(DEST, "anim_poses.json")
    meta = {}
    if so and os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as f:
            meta = json.load(f)
    for nome, args in POSES.items():
        if so and nome not in so:
            continue
        meta[nome] = gerar(nome, *args)
        print(nome, meta[nome]["frame"])
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    sys.exit(main())
