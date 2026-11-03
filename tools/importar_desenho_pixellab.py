"""Exporta um desenho do PixelLab pixel workbench para elenco e jogo."""

import argparse
from pathlib import Path
import shutil
from urllib.request import urlopen


RAIZ = Path(__file__).resolve().parents[1]
PASTA_ELENCO = Path(r"C:\Users\gabri\OneDrive\Documentos\Jogo A3\Personagens gerados por mim")


def importar(id_desenho, slug, nome, inimigo=False):
    pasta = PASTA_ELENCO / nome
    fontes = RAIZ / "assets" / "fontes" / "pixellab" / slug
    pasta.mkdir(parents=True, exist_ok=True)
    fontes.mkdir(parents=True, exist_ok=True)
    base = f"https://api.pixellab.ai/mcp/pixel-tools/{id_desenho}"
    for url, destino in (
        (f"{base}/assets/east/full.png", fontes / "east.png"),
        (f"{base}/recipe.json", pasta / "recipe.json"),
    ):
        with urlopen(url, timeout=45) as resposta:
            destino.write_bytes(resposta.read())
    destino_jogo = RAIZ / "assets" / "img" / "personagens"
    prefixo = "inimigo_" if inimigo else "npc_"
    shutil.copy2(fontes / "east.png", destino_jogo / f"{prefixo}{slug}.png")
    # Mantém também uma cópia independente, fácil de localizar e abrir.
    with urlopen(f"{base}/assets/east/full.png", timeout=45) as resposta:
        (pasta / "east.png").write_bytes(resposta.read())
    (pasta / "informacoes.txt").write_text(
        f"PixelLab drawing ID: {id_desenho}\nPersonagem: {nome}\nVista: east\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("id")
    parser.add_argument("slug")
    parser.add_argument("nome")
    parser.add_argument("--inimigo", action="store_true")
    args = parser.parse_args()
    importar(args.id, args.slug, args.nome, args.inimigo)
    print(f"Desenho de {args.nome} exportado para a pasta do elenco e o jogo.")
