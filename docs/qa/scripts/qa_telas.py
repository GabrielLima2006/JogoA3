"""Capturas das telas: menu, novo jogo, intro, como jogar, recordes, créditos, pausa, mapa, loja, ferreiro,
amuletos, morte (com bolsa), diálogo, apresentação de chefe, carta, final e resultado."""
from qa_common import *
from src import states as S, menus as M
from src.progress import CHARMS

def drive(s, st, name, frames=30, keys=()):
    s.app.state = st
    for i in range(frames):
        if keys and i == 1:
            s.inp.pressed |= set(keys)
        s.app.state.frame(1 / 60, s.inp)
        s.inp.consume()
    p = shot(s, name, s.app.state)
    return s.app.state

s = game(("dash",), name="qa_telas.json")
# menus
drive(s, M.MenuState(s.app), "tela_menu")
st = drive(s, M.NewGameState(s.app), "tela_novo_jogo")
for k in range(3):
    drive(s, st, f"tela_novo_jogo_{k}", frames=4, keys=("menu_down",))
drive(s, M.HowToPlayState(s.app, M.MenuState(s.app)), "tela_como_jogar")
drive(s, M.RecordsState(s.app, M.MenuState(s.app)), "tela_recordes")
drive(s, M.CreditsState(s.app, M.MenuState(s.app)), "tela_creditos", frames=120)
pr = Progress(); pr.chapter = 1
it = M.IntroState(s.app, pr)
drive(s, it, "tela_intro", frames=200)

# partida
s = game(("dash", "double_jump"), name="qa_telas2.json")
s.pr.coins = 999; s.pr.ore = 5
s.pr.visited |= set(GAME_ROOMS[:8]); s.pr.shop_bought.add("map")
s.goto("conves", 12, 18)
drive(s, S.PauseState(s.app, s.play), "tela_pausa", frames=5)
st = S.PauseState(s.app, s.play); st.confirm_restart = True; st._build_menu(3)
drive(s, st, "tela_pausa_confirmar_reiniciar", frames=2)
drive(s, S.MapState(s.app, s.play), "tela_mapa", frames=2)
st = drive(s, S.ShopState(s.app, s.play, "shop"), "tela_loja", frames=3)
drive(s, st, "tela_loja_comprou", frames=3, keys=("menu_confirm",))
for i in range(5):
    drive(s, st, f"tela_loja_item{i}", frames=3, keys=("menu_down",))
drive(s, S.ShopState(s.app, s.play, "smith"), "tela_ferreiro", frames=3)
st = S.ShopState(s.app, s.play, "smith"); drive(s, st, "tela_ferreiro_melhorou", frames=3, keys=("menu_confirm",))
# amuletos
s.pr.charms_owned = set(CHARMS)
st = drive(s, S.BenchState(s.app, s.play), "tela_amuletos", frames=3)
drive(s, st, "tela_amuletos_equipa", frames=3, keys=("menu_confirm",))
for i in range(4):
    drive(s, st, f"tela_amuletos_mov{i}", frames=3, keys=("right",))
    drive(s, st, f"tela_amuletos_eq{i}", frames=3, keys=("menu_confirm",))
# diálogo e carta
s.app.state = s.play
cap = [o for o in s.play.interactables if getattr(o, "char_id", None) == "amigo"]
s.play.talk_to(cap[0])
st = s.app.state; st.typed = 999 if hasattr(st, "typed") else None
drive(s, st, "tela_dialogo", frames=60)
from src import chapter1
for cid, (t_, b_) in chapter1.LETTERS.items():
    drive(s, S.MessageState(s.app, s.play, t_, b_), f"tela_carta_{cid}", frames=40)
drive(s, S.MessageState(s.app, s.play, *chapter1.FLAG_MESSAGES["atracado"]), "tela_aviso_atracado", frames=40)
# apresentação de cada chefe
for rid in ("toca", "gavea", "ruinas", "altar"):
    s.app.state = s.play
    s.goto(rid, 4, {"toca": 15, "gavea": 17, "ruinas": 17, "altar": 19}[rid], enemies=True)
    boss = s.play.boss
    info = chapter1.BOSSES[rid if False else s.play.room.boss]
    drive(s, S.BossIntroState(s.app, s.play, boss, info), f"tela_intro_chefe_{rid}", frames=90)
    # falas depois
    if info["after"]:
        from src.objects import Speaker
        sp = Speaker(info["speaker"], s.play._speaker_name(info["speaker"]))
        drive(s, S.DialogState(s.app, s.play, sp, info["after"]), f"tela_falas_depois_{rid}", frames=240)
# morte com bolsa
s.app.state = s.play
s.goto("porao1", 10, 20)
s.pr.coins = 57
s.p.hp = 1
s.p.take_hit(1, s.p.cx + 10, s.play)
for _ in range(200):
    s.app.state.frame(1/60, s.inp)
    if isinstance(s.app.state, S.DeathState):
        break
drive(s, s.app.state, "tela_morte_com_bolsa", frames=30)
# final e resultado
for letters in (("carta1", "carta2", "carta3"), ("carta1",)):
    s.app.state = s.play
    s.pr.letters = set(letters)
    s.play.load_room(s.play.world.rooms["altar"])
    st = S.EndingState(s.app, s.play)
    s.app.push(st)
    k = 0
    while isinstance(s.app.state, S.EndingState) and k < 20:
        for _ in range(240):
            s.app.state.frame(1/60, s.inp)
        shot(s, f"tela_final_{len(letters)}cartas_{k}", s.app.state)
        s.inp.pressed.add("menu_confirm"); s.app.state.frame(1/60, s.inp); s.inp.consume()
        k += 1
    for _ in range(120):
        s.app.state.frame(1/60, s.inp)
    shot(s, f"tela_resultado_{len(letters)}cartas", s.app.state)
print("ok")
