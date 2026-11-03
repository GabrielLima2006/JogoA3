"""Importa um personagem PixelLab para o projeto e a pasta de origem do elenco."""

import argparse
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

from PIL import Image


RAIZ = Path(__file__).resolve().parents[1]
PASTA_ELENCO = Path(r"C:\Users\gabri\OneDrive\Documentos\Jogo A3\Personagens gerados por mim")


def importar(id_personagem, slug, nome, pasta_elenco=None, inimigo=False):
    destino_elenco = Path(pasta_elenco) if pasta_elenco else PASTA_ELENCO / nome
    fontes = RAIZ / "assets" / "fontes" / "pixellab" / slug
    fontes.mkdir(parents=True, exist_ok=True)
    destino_elenco.mkdir(parents=True, exist_ok=True)

    url = f"https://api.pixellab.ai/mcp/characters/{id_personagem}/download"
    with urlopen(url, timeout=60) as resposta:
        pacote = resposta.read()
    (destino_elenco / f"{slug}_pixellab.zip").write_bytes(pacote)

    with ZipFile(BytesIO(pacote)) as arquivo:
        for caminho in arquivo.namelist():
            if caminho.lower().endswith(".png") and "/rotations/" in caminho.lower():
                direcao = Path(caminho).stem.lower()
                imagem = arquivo.read(caminho)
                (fontes / f"{direcao}.png").write_bytes(imagem)
                (destino_elenco / f"{direcao}.png").write_bytes(imagem)

    lateral = fontes / "east.png"
    if not lateral.exists():
        lateral = fontes / "west.png"
    if lateral.exists():
        with Image.open(lateral) as imagem:
            prefixo = "inimigo_" if inimigo else "npc_"
            imagem.convert("RGBA").save(RAIZ / "assets" / "img" / "personagens" / f"{prefixo}{slug}.png")

    (destino_elenco / "informacoes.txt").write_text(
        f"PixelLab ID: {id_personagem}\nPersonagem: {nome}\n"
        "Direção lateral para o jogo: east (espelhada para olhar à esquerda).\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("id")
    parser.add_argument("slug")
    parser.add_argument("nome")
    parser.add_argument("--pasta-elenco")
    parser.add_argument("--inimigo", action="store_true")
    args = parser.parse_args()
    importar(args.id, args.slug, args.nome, args.pasta_elenco, args.inimigo)
    print(f"Arte de {args.nome} salva no elenco e integrada ao projeto.")
