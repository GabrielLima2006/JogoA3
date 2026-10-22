"""Caminhos de arquivos, iguais rodando pelo Python ou pelo executável (PyInstaller)."""

import os
import sys

FROZEN = getattr(sys, "frozen", False)

# arquivos que vêm com o jogo (sons, músicas, fontes)
RESOURCE_DIR = getattr(sys, "_MEIPASS", None) if FROZEN else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# arquivos que o jogo grava (save, recordes, log de erro): ao lado do .exe ou do main.py
DATA_DIR = os.path.dirname(os.path.abspath(sys.executable)) if FROZEN else RESOURCE_DIR


def asset(*parts):
    return os.path.join(RESOURCE_DIR, "assets", *parts)
