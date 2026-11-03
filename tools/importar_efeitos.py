"""Copia efeitos do Super Pixel Effects Gigapack (Free) para assets/img/efeitos.

Uso: python tools/importar_efeitos.py <caminho do zip do Gigapack>

Cada efeito vira uma tira <nome>.png com os quadros lado a lado e um <nome>.txt com o
recorte de cada quadro (mesmo formato lido por sprites.effect).
"""

import io
import os
import sys
import zipfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, "assets", "img", "efeitos")

# nome no jogo: pasta da variante no pacote
EFEITOS = {
    "morte_chefe": "epic_explosion_002_small_yellow",      # morte de chefe
    "absorver": "spell_absorb_001_small_violet",            # ganhar habilidade
    "impacto_roxo": "directional_impact_003_small_violet",  # golpe forte acertando
    "impacto_critico": "symmetrical_impact_006_small_yellow",
    "defesa": "spell_defense_up_001_small_blue",            # bloqueio / escudo
    "pressa": "spell_haste_001_small_green",                # bônus de velocidade
    "carga": "scifi_charge_up_001_small_violet",            # carregar ataque de chefe
    "aviso_duplo": "symbol_alert_002_small_red",            # aviso de ataque (!!)
}


def main(zip_path):
    pygame.init()
    z = zipfile.ZipFile(zip_path)
    nomes = z.namelist()
    for nome, pasta in EFEITOS.items():
        quadros = sorted(n for n in nomes if f"/{pasta}/" in n and n.endswith(".png"))
        if not quadros:
            # algumas variantes só existem em outra cor: pega a primeira small disponível
            base = pasta.rsplit("_small_", 1)[0]
            pastas = sorted({n.split("/")[-2] for n in nomes if f"/{base}_small_" in n and n.endswith(".png")})
            if not pastas:
                print("faltou", nome, pasta)
                continue
            quadros = sorted(n for n in nomes if f"/{pastas[0]}/" in n and n.endswith(".png"))
            pasta = pastas[0]
        imgs = [pygame.image.load(io.BytesIO(z.read(q))) for q in quadros]
        w, h = imgs[0].get_size()
        tira = pygame.Surface((w * len(imgs), h), pygame.SRCALPHA)
        linhas = []
        for i, (q, img) in enumerate(zip(quadros, imgs)):
            tira.blit(img, (i * w, 0))
            linhas.append(f"{q.split('PNG/', 1)[-1]} = {i * w} 0 {w} {h}")
        pygame.image.save(tira, os.path.join(DEST, nome + ".png"))
        with open(os.path.join(DEST, nome + ".txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(linhas) + "\n")
        print(nome, pasta, len(imgs), (w, h))


if __name__ == "__main__":
    main(sys.argv[1])
