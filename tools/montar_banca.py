"""Banca do comerciante do Convés: caixote como balcão, barril ao lado e mercadoria pequena.

Uso: python tools/montar_banca.py "<pasta assets internet>"
Saída: assets/img/objetos/banca_comerciante.png (base na última linha; o comerciante fica à direita).

- Caixote e barril: folha de objetos do Metroidvania Forge (assets/img/objetos/caixas.png).
- Pão (assets/img/itens) e frasco de geleia: pacote Pixel Food (Ghostpixxells), reduzidos pela cor
  dominante de cada bloco, para ficarem menores que a cabeça do comerciante.
- Mapa enrolado, rolo de corda e peixe seco: desenhados à mão, poucos pixels.
"""

import io
import os
import sys
import zipfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from animar_pose import reduzir  # noqa: E402

OUT = os.path.join(ROOT, "assets", "img", "objetos", "banca_comerciante.png")
O = (5, 2, 21)


def comida(z, nome, altura):
    img = pygame.image.load(io.BytesIO(z.read(nome))).convert_alpha()
    img = img.subsurface(img.get_bounding_rect()).copy()
    return reduzir(img, altura)


def mapa():
    """Pergaminho enrolado deitado (12x5) com fita vermelha."""
    s = pygame.Surface((12, 5), pygame.SRCALPHA)
    papel, sombra, fita = (226, 204, 150), (176, 146, 96), (170, 50, 50)
    pygame.draw.rect(s, O, (0, 0, 12, 5))
    pygame.draw.rect(s, papel, (1, 1, 10, 2))
    pygame.draw.rect(s, sombra, (1, 3, 10, 1))
    s.set_at((0, 0), (0, 0, 0, 0)); s.set_at((11, 0), (0, 0, 0, 0))
    s.set_at((0, 4), (0, 0, 0, 0)); s.set_at((11, 4), (0, 0, 0, 0))
    for y in (1, 2, 3):
        s.set_at((6, y), fita)
    s.set_at((1, 1), (200, 176, 120))
    return s


def corda():
    """Rolo de corda (13x7) visto de lado, apoiado no chão."""
    s = pygame.Surface((13, 7), pygame.SRCALPHA)
    clara, escura = (196, 160, 96), (130, 96, 56)
    pygame.draw.ellipse(s, O, (0, 0, 13, 7))
    pygame.draw.ellipse(s, clara, (1, 1, 11, 5))
    pygame.draw.ellipse(s, escura, (4, 2, 5, 3))
    for x in (2, 5, 8, 10):
        s.set_at((x, 1), escura)
    s.set_at((6, 3), O)
    return s


def peixe():
    """Peixe seco deitado (13x6): corpo prateado-azulado, rabo à esquerda, olho à direita."""
    linhas = [
        "..O.....OOO..",
        ".OkO..OOllllO.",
        ".OkkOOllllllEO",
        ".OkkOkkkkkkkkO",
        ".OkO.OOkkkkOO.",
        "..O....OOOO...",
    ]
    cores = {"O": O, "l": (168, 186, 196), "k": (104, 122, 140), "E": (20, 16, 30)}
    s = pygame.Surface((14, 6), pygame.SRCALPHA)
    for y, linha in enumerate(linhas):
        for x, ch in enumerate(linha):
            if ch in cores:
                s.set_at((x, y), cores[ch])
    return s


def main(pasta_pacotes):
    pygame.init()
    pygame.display.set_mode((8, 8))
    folha = pygame.image.load(os.path.join(ROOT, "assets", "img", "objetos", "caixas.png")).convert_alpha()
    caixote = folha.subsurface((53, 28, 39, 35)).copy()
    barril = folha.subsurface((109, 38, 22, 25)).copy()
    z = zipfile.ZipFile(os.path.join(pasta_pacotes, "Ghostpixxells_pixelfood.zip"))
    geleia = comida(z, "61_jam.png", 10)
    itens = os.path.join(ROOT, "assets", "img", "itens")

    def item(nome, altura):
        img = pygame.image.load(os.path.join(itens, nome)).convert_alpha()
        return reduzir(img.subsurface(img.get_bounding_rect()).copy(), altura)
    pao = item("pao.png", 9)
    salmao = peixe()                              # peixe seco em cima do barril

    W, H = 70, 48
    banca = pygame.Surface((W, H), pygame.SRCALPHA)
    chao = H                                      # base de tudo na última linha
    # barril à esquerda, corda encostada nele, salmão em cima
    bx = 2
    banca.blit(barril, (bx, chao - barril.get_height()))
    banca.blit(salmao, (bx + 11 - salmao.get_width() // 2, chao - barril.get_height() - salmao.get_height()))
    banca.blit(corda(), (bx + 14, chao - 7))
    # caixote-balcão à direita, mercadoria apoiada na tampa
    cx = W - caixote.get_width() - 1
    topo = chao - caixote.get_height()
    banca.blit(caixote, (cx, topo))
    banca.blit(mapa(), (cx + 3, topo - 5))
    banca.blit(geleia, (cx + 17, topo - geleia.get_height()))
    banca.blit(pao, (cx + 39 - pao.get_width() - 1, topo - pao.get_height()))
    r = banca.get_bounding_rect()
    banca = banca.subsurface((r.x, r.y, r.w, H - r.y)).copy()
    pygame.image.save(banca, OUT)
    print("salvo", OUT, banca.get_size())


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "assets internet"))
