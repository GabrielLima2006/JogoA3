import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
from helpers import Sim, T, SIM_DT, try_reach, stands_on, in_room  # noqa
import pygame  # noqa
from src.progress import Progress  # noqa
from src.physics import tile_span  # noqa

SHOTS = os.path.join(ROOT, "docs", "qa")
GAME_ROOMS = ["cabine", "conves", "porao1", "porao2", "toca", "cordame1", "cordame2", "gavea",
              "praia", "floresta", "ruinas", "templo", "altar"]


def game(abilities=("dash",), flags=(), name="qa.json", difficulty="normal", protagonist="ela"):
    pr = Progress()
    pr.chapter = 1
    pr.abilities = set(abilities)
    pr.flags = set(flags)
    pr.difficulty = difficulty
    pr.protagonist = protagonist
    return Sim(progress=pr, save_name=name)


def shot(s, name, state=None):
    st = state or s.app.state
    st.draw(s.app.screen)
    path = os.path.join(SHOTS, name + ".png")
    pygame.image.save(s.app.screen, path)
    return path


def overlaps_solid(room, x, y, w, h):
    x0, x1 = tile_span(x, w)
    y0, y1 = tile_span(y, h)
    return [(tx, ty) for ty in range(y0, y1 + 1) for tx in range(x0, x1 + 1) if room.is_solid(tx, ty)]
