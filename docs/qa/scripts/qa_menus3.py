import time
from qa_common import *
from src import states as S, menus as M
s = game(("dash",), name="qa_m3.json")
def cap(st, name):
    s.app.state = st
    st.draw(s.app.screen); time.sleep(0.8)
    for _ in range(5):
        st.frame(1/60, s.inp); s.inp.consume()
    shot(s, name, st)
cap(M.MenuState(s.app), "tela_menu")
s.goto("conves", 12, 18); s.run(2.5)
cap(S.PauseState(s.app, s.play), "tela_pausa")
st = S.PauseState(s.app, s.play); st.confirm_restart = True; st._build_menu(3); cap(st, "tela_pausa_confirmar_reiniciar")
s.app.state = s.play
s.pr.coins = 57
s.p.hp = 1; s.p.take_hit(1, s.p.cx + 10, s.play)
for _ in range(400):
    s.app.state.frame(1/60, s.inp)
    if isinstance(s.app.state, S.DeathState): break
cap(s.app.state, "tela_morte_com_bolsa")
