"""Testes das telas fora da partida: menu, novo jogo, introdução, como jogar,
recordes e créditos."""

import os

from helpers import TMP_DIR, check
from main import App
from src.menus import (CreditsState, HowToPlayState, IntroState, MenuState, NewGameState,
                        RecordsState)
from src.progress import Progress
from src.records import add_record
from src.states import PlayState


def _app(name):
    path = os.path.join(TMP_DIR, name)
    if os.path.exists(path):
        os.remove(path)
    app = App(headless=True, save_path=path)
    return app


def _press(app, *actions, frames=1):
    for a in actions:
        app.input.pressed.add(a)
    for _ in range(frames):
        app.state.frame(1 / 60, app.input)
        app.state.draw(app.screen)


def test_main_menu():
    app = _app("menu1.json")
    st = app.state
    keys = [o[1] for o in st.menu.options]
    check("menu tem as 6 opções do documento",
          keys == ["new", "continue", "howto", "records", "credits", "quit"], str(keys))
    opts = {o[1]: o[2] for o in st.menu.options}
    check("sem save, Continuar capítulo fica desabilitado", opts["continue"] is False)
    check("seleção inicial pula opção desabilitada", st.menu.options[st.menu.index][1] == "new")
    _press(app, "menu_down")
    check("navegação pula Continuar desabilitado", st.menu.options[st.menu.index][1] == "howto")
    st.draw(app.screen)


def test_new_game_flow():
    app = _app("novo.json")
    _press(app, "menu_confirm")
    check("Novo jogo abre a escolha de dificuldade", isinstance(app.state, NewGameState))
    check("dificuldade padrão é Normal", app.state.difficulties[app.state.di] == "normal")
    app.state.draw(app.screen)
    _press(app, "right")
    _press(app, "menu_confirm")
    st = app.state
    check("depois da dificuldade vem a introdução", isinstance(st, IntroState))
    check("escolhas guardadas no progresso", st.progress.protagonist == "ela"
          and st.progress.difficulty == "dificil" and st.progress.chapter == 1)
    check("introdução apresenta Nyra e a ilha de Velmora", any("Nyra" in x for x in st.slides if x)
          and any("Velmora" in x for x in st.slides if x), st.slides[1][:60])
    _press(app, "menu_confirm")
    check("Enter durante a digitação completa o texto", st.index == 0 and st._full())
    _press(app, "menu_confirm")
    check("Enter com o texto completo avança", st.index == 1)
    for _ in range(20):
        if not isinstance(app.state, IntroState):
            break
        st.typed = 9999
        _press(app, "menu_confirm")
    check("fim da introdução começa a partida no navio", isinstance(app.state, PlayState)
          and app.state.room.id == "cabine")
    play = app.state
    check("partida começa com protagonista e dificuldade escolhidos",
          play.progress.protagonist == "ela" and play.progress.difficulty == "dificil")
    play.draw(app.screen)
    play.save()
    loaded = Progress.load(app.save_path)
    check("protagonista e dificuldade ficam no save", loaded.protagonist == "ela" and loaded.difficulty == "dificil")
    old = Progress()
    old.protagonist = "ele"
    old.save(app.save_path)
    check("save antigo com Ele carrega como a feiticeira", Progress.load(app.save_path).protagonist == "ela")


def test_intro_skip():
    app = _app("intro.json")
    app.push(IntroState(app, Progress()))
    _press(app, "pause")
    check("ESC pula a introdução", isinstance(app.state, PlayState))


def test_continue():
    app = _app("cont.json")
    pr = Progress()
    pr.difficulty = "facil"
    pr.save(app.save_path)
    app.to_menu()
    st = app.state
    check("com save, Continuar capítulo vem selecionado", st.menu.options[st.menu.index][1] == "continue")
    _press(app, "menu_confirm")
    check("Continuar capítulo carrega o save", isinstance(app.state, PlayState)
          and app.state.progress.difficulty == "facil")


def test_other_screens():
    app = _app("telas.json")
    menu = app.state
    menu.menu.index = 2
    _press(app, "menu_confirm")
    check("Como jogar abre", isinstance(app.state, HowToPlayState))
    _press(app, "right")
    _press(app, "right")
    check("Como jogar tem 3 páginas", app.state.page == 2)
    _press(app, "pause")
    check("ESC volta ao menu", app.state is menu)
    menu.menu.index = 3
    _press(app, "menu_confirm")
    check("Recordes abre (vazio)", isinstance(app.state, RecordsState) and not app.state.records)
    _press(app, "pause")
    add_record({"capitulo": 1, "dificuldade": "normal", "tempo": 543, "quedas": 4, "cartas": 4,
                "nota": "A"}, app.records_path)
    add_record({"capitulo": 1, "dificuldade": "facil", "tempo": 400, "quedas": 5, "cartas": 4,
                "nota": "S"}, app.records_path)
    app.push(RecordsState(app, back=menu))
    check("Recordes ordena pela nota", [r["nota"] for r in app.state.records] == ["S", "A"])
    app.state.draw(app.screen)
    _press(app, "pause")
    menu.menu.index = 4
    _press(app, "menu_confirm")
    check("Créditos abre", isinstance(app.state, CreditsState))
    _press(app, "menu_confirm")
    check("Enter volta dos créditos", isinstance(app.state, MenuState))
    menu.menu.index = 5
    _press(app, "menu_confirm")
    check("Sair encerra o jogo", app.running is False)


def test_mouse_and_tabs():
    app = _app("mouse.json")
    st = app.state
    st.draw(app.screen)
    hit = st.menu.rects[2]
    app.input.mouse_pos = (0, 0)
    _press(app)
    app.input.mouse_pos = hit.center
    _press(app)
    check("mouse em cima seleciona a opção", st.menu.options[st.menu.index][1] == "howto")
    _press(app, "menu_down")
    check("mouse parado não desfaz a escolha do teclado", st.menu.options[st.menu.index][1] == "records")
    st.menu.index = 2
    _press(app, "menu_confirm")
    howto = app.state
    app.input.mouse_pos = howto.tabs[2].center
    app.input.mouse_clicked = True
    _press(app)
    check("clique na aba vai direto para a página", howto.page == 2)


TESTS = [test_main_menu, test_new_game_flow, test_intro_skip, test_continue, test_other_screens,
         test_mouse_and_tabs]
