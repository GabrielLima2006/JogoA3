"""Capturas da versão atual para o README (docs/screenshots/)."""
import time
from qa_common import *
from src import states as S, menus as M

OUT = os.path.join(ROOT, "docs", "screenshots")


def save(s, name, st=None):
    st = st or s.app.state
    st.draw(s.app.screen)
    pygame.image.save(s.app.screen, os.path.join(OUT, name + ".png"))
    print("ok", name)


def menu_shot(s, st, name):
    s.app.state = st
    st.draw(s.app.screen); time.sleep(0.8)
    for _ in range(5):
        st.frame(1 / 60, s.inp); s.inp.consume()
    save(s, name, st)


s = game(("dash", "double_jump"), flags=("atracado",), name="qa_readme.json")
s.pr.coins = 120
menu_shot(s, M.MenuState(s.app), "menu")
for room, x, row, name in [("conves", 12, 18, "conves"), ("porao2", 4, 20, "porao"),
                           ("floresta", 3, 37, "floresta"), ("templo", 3, 18, "templo"),
                           ("ruinas", 3, 17, "ruinas")]:
    s.goto(room, x, row, enemies=True)
    s.run(2.2)
    s.app.state = s.play
    save(s, name)
# mapa e pausa (inventário)
s.pr.has_map = True
menu_shot(s, S.MapState(s.app, s.play), "mapa")
menu_shot(s, S.PauseState(s.app, s.play), "pausa")
# chefe: Aldric na Gávea, acordado
s.goto("gavea", 4, 17, enemies=True)
boss = s.play.boss
s.p.place(boss.cx - 220, s.p.bottom)
boss.wake()
for _ in range(150):
    s.app.state = s.play
    s.step()
s.app.state = s.play
save(s, "chefe_aldric")
