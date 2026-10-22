"""Telas fora da partida: menu principal, novo jogo (protagonista e dificuldade),
introdução, como jogar, recordes e créditos."""

import math

import pygame

from . import ui
from .config import Audio as AudioCfg, Colors, Display, Game
from .progress import Progress
from .records import best_records, load_records

W, H = Display.WIDTH, Display.HEIGHT

SEA = (16, 30, 48)
SEA_LIGHT = (40, 70, 100)
SKY_TOP = (8, 10, 20)
SKY_BOTTOM = (28, 34, 58)


def draw_sea_background(surf, t):
    """Fundo provisório: céu de tempestade, lua, navio balançando e ondas."""
    for i in range(0, H, 6):
        k = i / H
        col = tuple(int(a + (b - a) * k) for a, b in zip(SKY_TOP, SKY_BOTTOM))
        pygame.draw.rect(surf, col, (0, i, W, 6))
    pygame.draw.circle(surf, (210, 215, 230), (880, 64), 30)
    pygame.draw.circle(surf, SKY_TOP, (867, 57), 26)
    # navio
    sea_y = 410
    bob = math.sin(t * 1.3) * 5
    tilt = math.sin(t * 1.3 + 0.6) * 0.04
    cx, cy = 690, sea_y - 6 + bob

    def rot(px, py):
        return (cx + px * math.cos(tilt) - py * math.sin(tilt), cy + px * math.sin(tilt) + py * math.cos(tilt))
    hull = [rot(-120, -26), rot(130, -26), rot(98, 14), rot(-92, 14)]
    pygame.draw.polygon(surf, (24, 20, 26), hull)
    pygame.draw.line(surf, (24, 20, 26), rot(0, -26), rot(0, -170), 5)
    pygame.draw.line(surf, (24, 20, 26), rot(-60, -26), rot(-60, -120), 4)
    pygame.draw.polygon(surf, (52, 48, 60), [rot(4, -160), rot(80, -70), rot(4, -60)])
    pygame.draw.polygon(surf, (52, 48, 60), [rot(-56, -112), rot(-8, -50), rot(-56, -44)])
    for i in range(3):
        wx = rot(-70 + i * 60, -36)
        pygame.draw.rect(surf, (250, 200, 110), (wx[0] - 3, wx[1] - 3, 6, 5))
    # ondas
    for layer in range(3):
        y0 = sea_y + layer * 34
        col = tuple(int(c * (0.7 + layer * 0.15)) for c in SEA_LIGHT)
        pts = [(0, H)]
        for x in range(0, W + 20, 20):
            pts.append((x, y0 + math.sin(x * 0.02 + t * (1.2 + layer * 0.4) + layer) * (6 + layer * 2)))
        pts.append((W, H))
        pygame.draw.polygon(surf, SEA if layer else col, pts)
        pygame.draw.lines(surf, col, False, pts[1:-1], 2)


def title(surf, msg, y=70, size=60):
    ui.text(surf, msg, size, (W // 2, y), Colors.UI_TEXT, "center", title=True)


def footer(surf, msg):
    ui.text(surf, msg, 20, (W // 2, H - 24), Colors.UI_DIM, "center")


def go_back(inp):
    return inp.was_pressed("pause")


# ---------------------------------------------------------------------------
class Screen:
    def __init__(self, app):
        self.app = app
        self.t = 0.0

    def frame(self, dt, inp):
        self.t += dt
        self.update(inp)
        inp.consume()

    def update(self, inp):
        pass


class MenuState(Screen):
    """Menu principal pedido no documento do A3."""

    def __init__(self, app):
        super().__init__(app)
        has_save = Progress.exists(app.save_path)
        app.audio.play_music(AudioCfg.MUSIC["menu"])
        self.menu = ui.Menu([
            ("Novo jogo", "new"),
            ("Continuar capítulo", "continue", has_save),
            ("Como jogar", "howto"),
            ("Recordes", "records"),
            ("Créditos", "credits"),
            ("Sair", "quit"),
        ], center_y=318, spacing=38, size=34)
        if has_save:
            self.menu.index = 1
        self.has_save = has_save

    def update(self, inp):
        choice = self.menu.handle(inp, self.app.audio)
        if choice == "new":
            self.app.push(NewGameState(self.app))
        elif choice == "continue":
            progress = Progress.load(self.app.save_path)
            if progress is not None:
                self.app.start_game(progress)
        elif choice == "howto":
            self.app.push(HowToPlayState(self.app, back=self))
        elif choice == "records":
            self.app.push(RecordsState(self.app, back=self))
        elif choice == "credits":
            self.app.push(CreditsState(self.app, back=self))
        elif choice == "quit":
            self.app.running = False

    def draw(self, surf):
        draw_sea_background(surf, self.t)
        ui.dim(surf, 70)
        title(surf, Game.TITLE.upper(), 96, 68)
        ui.text(surf, Game.SUBTITLE, 28, (W // 2, 146), Colors.UI_DIM, "center")
        ui.text(surf, "Prontos para o jogo?", 22, (W // 2, 178), (170, 180, 200), "center")
        self.menu.draw(surf)
        if self.has_save:
            pr = Progress.load(self.app.save_path)
            if pr is not None:
                ui.text(surf, f"Save: capítulo {pr.chapter} · {Game.DIFFICULTIES[pr.difficulty]['label']}", 18,
                        (W // 2, H - 22), Colors.UI_DIM, "center")


# ---------------------------------------------------------------------------
class NewGameState(Screen):
    """Escolha do protagonista e depois da dificuldade."""

    def __init__(self, app):
        super().__init__(app)
        self.step = "protagonist"
        self.protagonists = list(Game.PROTAGONISTS)
        self.difficulties = list(Game.DIFFICULTIES)
        self.pi = 0
        self.di = self.difficulties.index("normal")
        self.cards = []

    def _choices(self):
        return self.protagonists if self.step == "protagonist" else self.difficulties

    def update(self, inp):
        n = len(self._choices())
        idx = self.pi if self.step == "protagonist" else self.di
        if inp.was_pressed("left") or inp.was_pressed("menu_up"):
            idx = (idx - 1) % n
            self.app.audio.play("ui_move")
        if inp.was_pressed("right") or inp.was_pressed("menu_down"):
            idx = (idx + 1) % n
            self.app.audio.play("ui_move")
        clicked = False
        for i, r in enumerate(self.cards):
            if r.collidepoint(inp.mouse_pos):
                idx = i
                clicked = clicked or inp.mouse_clicked
        if self.step == "protagonist":
            self.pi = idx
        else:
            self.di = idx
        if go_back(inp):
            if self.step == "difficulty":
                self.step = "protagonist"
            else:
                self.app.to_menu()
            return
        if inp.was_pressed("menu_confirm") or clicked:
            self.app.audio.play("ui_select")
            if self.step == "protagonist":
                self.step = "difficulty"
            else:
                progress = Progress()
                progress.protagonist = self.protagonists[self.pi]
                progress.difficulty = self.difficulties[self.di]
                progress.chapter = 1
                self.app.push(IntroState(self.app, progress))

    def draw(self, surf):
        draw_sea_background(surf, self.t)
        ui.dim(surf, 150)
        self.cards = []
        if self.step == "protagonist":
            title(surf, "Escolha o protagonista", 70, 50)
            ui.text(surf, "Um enganador que se diz feiticeiro. Sabe blefar e ler reações.", 24,
                    (W // 2, 112), Colors.UI_DIM, "center")
            for i, key in enumerate(self.protagonists):
                p = Game.PROTAGONISTS[key]
                r = pygame.Rect(0, 0, 240, 270)
                r.center = (W // 2 + (i - 0.5) * 290, 300)
                self._card(surf, r, i == self.pi)
                draw_protagonist(surf, key, r.centerx, r.y + 190, scale=3.0, t=self.t)
                ui.text(surf, p["label"], 40, (r.centerx, r.bottom - 38), Colors.UI_TEXT, "center")
                self.cards.append(r)
            footer(surf, "A/D ou setas para escolher · Enter ou clique para confirmar · ESC volta")
        else:
            title(surf, "Dificuldade", 70, 50)
            for i, key in enumerate(self.difficulties):
                d = Game.DIFFICULTIES[key]
                r = pygame.Rect(0, 0, 250, 210)
                r.center = (W // 2 + (i - 1) * 280, 270)
                self._card(surf, r, i == self.di)
                ui.text(surf, d["label"], 40, (r.centerx, r.y + 40), Colors.UI_TEXT, "center")
                ui.text(surf, f"maré: {d['tide_minutes']} min", 24, (r.centerx, r.y + 80), Colors.UI_ACCENT, "center")
                self._wrap(surf, d["desc"], r.x + 18, r.y + 110, r.w - 36)
                self.cards.append(r)
            if Progress.exists(self.app.save_path):
                ui.text(surf, "Começar um novo jogo substitui o save atual.", 22, (W // 2, 410),
                        Colors.HP_FULL, "center")
            footer(surf, "A/D ou setas para escolher · Enter ou clique para começar · ESC volta")

    @staticmethod
    def _card(surf, r, selected):
        pygame.draw.rect(surf, (26, 32, 50) if selected else (18, 22, 34), r, border_radius=12)
        pygame.draw.rect(surf, Colors.UI_ACCENT if selected else (60, 66, 90), r, 3 if selected else 1,
                         border_radius=12)

    @staticmethod
    def _wrap(surf, msg, x, y, width, size=22):
        words, line = msg.split(), ""
        for w in words:
            test = (line + " " + w).strip()
            if ui.font(size).size(test)[0] > width:
                ui.text(surf, line, size, (x, y), Colors.UI_TEXT)
                y += size
                line = w
            else:
                line = test
        if line:
            ui.text(surf, line, size, (x, y), Colors.UI_TEXT)


def draw_protagonist(surf, key, x, foot_y, scale=1.0, t=0.0, facing=1):
    """Retrato provisório: corpo, capa e chapéu de 'feiticeiro'."""
    p = Game.PROTAGONISTS[key]
    w, h = 22 * scale, 40 * scale
    body = pygame.Rect(0, 0, round(w), round(h))
    body.midbottom = (round(x), round(foot_y))
    sway = math.sin(t * 2) * 2 * scale
    cloak = [(body.left - 3 * scale, body.top + 12 * scale), (body.right + 3 * scale, body.top + 12 * scale),
             (body.right + 6 * scale + sway, body.bottom), (body.left - 6 * scale + sway, body.bottom)]
    pygame.draw.polygon(surf, p["cloak"], cloak)
    pygame.draw.rect(surf, p["body"], body.inflate(-6 * scale, 0).move(0, 0), border_radius=round(4 * scale))
    if p["hair"]:
        # franja curta + mecha longa atrás (do lado oposto ao olhar)
        pygame.draw.rect(surf, p["hair"], (body.left + 2 * scale, body.top + 4 * scale, w - 4 * scale, 5 * scale))
        back_x = body.left + 2 * scale if facing > 0 else body.right - 8 * scale
        pygame.draw.rect(surf, p["hair"], (back_x, body.top + 4 * scale, 6 * scale, 22 * scale),
                         border_radius=round(2 * scale))
    # chapéu pontudo
    hat = [(body.left - 4 * scale, body.top + 6 * scale), (body.right + 4 * scale, body.top + 6 * scale),
           (body.centerx + 6 * scale * facing, body.top - 22 * scale)]
    pygame.draw.polygon(surf, p["cloak"], hat)
    pygame.draw.rect(surf, (230, 200, 90), (body.left - 2 * scale, body.top + 3 * scale, w + 4 * scale, 3 * scale))
    eye_x = body.centerx + facing * w * 0.2
    pygame.draw.rect(surf, (20, 24, 36), (round(eye_x - 2 * scale), round(body.top + 12 * scale),
                                          round(4 * scale), round(4 * scale)))


# ---------------------------------------------------------------------------
INTRO_SLIDES = [
    "Noite de tempestade. O navio da capitã corta o mar escuro rumo ao porto.",
    "Você viaja como {passageiro}. Diz ser {feiticeiro}... mas a verdade é que você é só "
    "muito {bom} em enganar. E em ler pessoas.",
    "No jantar, a capitã ergue a taça, leva a colher à boca... e desaba sobre a mesa.",
    "Veneno. Quatro pessoas estiveram perto daquele prato. Lá fora, a maré não para de subir.",
    "A tripulação inteira se vira para você. \"{Feiticeiro}... descubra quem fez isso. Antes que seja tarde.\"",
]


class IntroState(Screen):
    """Introdução em telas de texto com efeito de máquina de escrever."""
    CHARS_PER_SEC = 45

    def __init__(self, app, progress):
        super().__init__(app)
        self.progress = progress
        p = Game.PROTAGONISTS[progress.protagonist]
        forms = {k: p[k] for k in ("o", "feiticeiro", "passageiro", "bom")}
        forms["Feiticeiro"] = p["feiticeiro"].capitalize()
        self.slides = [s.format(**forms) for s in INTRO_SLIDES]
        self.slides.append(None)    # cartão do capítulo
        self.index = 0
        self.typed = 0.0

    @property
    def current(self):
        return self.slides[self.index]

    def _full(self):
        return self.current is None or self.typed >= len(self.current)

    def frame(self, dt, inp):
        self.typed += dt * self.CHARS_PER_SEC
        super().frame(dt, inp)

    def update(self, inp):
        if go_back(inp):
            self.finish()
            return
        if inp.was_pressed("menu_confirm") or inp.mouse_clicked or inp.was_pressed("attack_quick"):
            if not self._full():
                self.typed = len(self.current)
            else:
                self.index += 1
                self.typed = 0.0
                self.t = 0.0
                if self.index >= len(self.slides):
                    self.finish()

    def finish(self):
        self.app.start_game(self.progress)

    def draw(self, surf):
        draw_sea_background(surf, self.t + self.index * 3)
        ui.dim(surf, 175)
        if self.current is None:
            ui.text(surf, "Capítulo 1", 34, (W // 2, H // 2 - 50), Colors.UI_DIM, "center")
            title(surf, Game.CHAPTERS[1], H // 2, 54)
        else:
            shown = self.current[:int(self.typed)]
            NewGameState._wrap(surf, shown, 120, 200, W - 240, size=34)
        n = len(self.slides)
        for i in range(n):
            pos = (W // 2 + (i - (n - 1) / 2) * 20, H - 62)
            pygame.draw.circle(surf, Colors.UI_ACCENT if i == self.index else Colors.UI_DIM, pos, 5, 0 if i == self.index else 1)
        footer(surf, "Enter, Espaço ou clique para continuar · ESC pula a introdução")


# ---------------------------------------------------------------------------
HOWTO_PAGES = [
    ("Controles", None),
    ("Investigação", [
        "Explore o navio atrás das pistas físicas de cada capítulo.",
        "Converse com os suspeitos (W) para ouvir os depoimentos.",
        "Pistas e depoimentos vão para o caderno (Tab). Procure contradições.",
        "A maré sobe com o tempo: demore e pistas são destruídas,",
        "testemunhas somem e o criminoso ganha força.",
        "Sua credibilidade é sua vida. Se zerar, você perde o capítulo.",
        "Na cabine do protagonista você salva o jogo e se recompõe.",
    ]),
    ("Interrogatório", [
        "Quando estiver pronto, acuse um suspeito no salão. O duelo começa.",
        "Leia a reação dele a cada fala (desviar o olhar, apertar as mãos...).",
        "OUVIR — aceita a fala e segue. Sem risco.",
        "PRESSIONAR — pede detalhes. Suspeito irritado pode se calar.",
        "APRESENTAR PISTA — mostra a contradição. Pista errada custa credibilidade.",
        "BLEFAR — finge ter uma prova. Se ele estiver calmo, você perde credibilidade.",
        "Quebre a compostura do culpado antes de perder a sua credibilidade.",
    ]),
]


class HowToPlayState(Screen):
    def __init__(self, app, back):
        super().__init__(app)
        self.back = back
        self.page = 0

    def update(self, inp):
        if go_back(inp) or inp.was_pressed("menu_confirm") and self.page == len(HOWTO_PAGES) - 1:
            self.app.push(self.back)
            return
        if inp.was_pressed("right") or inp.was_pressed("menu_confirm") or inp.mouse_clicked:
            self.page = min(len(HOWTO_PAGES) - 1, self.page + 1)
        if inp.was_pressed("left"):
            self.page = max(0, self.page - 1)

    def draw(self, surf):
        draw_sea_background(surf, self.t)
        ui.dim(surf, 200)
        name, lines = HOWTO_PAGES[self.page]
        title(surf, "Como jogar", 50, 50)
        ui.text(surf, f"{name}  ({self.page + 1}/{len(HOWTO_PAGES)})", 30, (W // 2, 96), Colors.UI_ACCENT, "center")
        if lines is None:
            ui.draw_controls(surf, 300, 130, title=False)
        else:
            y = 150
            for line in lines:
                ui.text(surf, line, 26, (90, y), Colors.UI_TEXT)
                y += 40
        footer(surf, "A/D ou setas trocam de página · Enter avança · ESC volta")


class RecordsState(Screen):
    def __init__(self, app, back, path=None):
        super().__init__(app)
        self.back = back
        self.records = best_records(load_records(path or getattr(app, "records_path", None)))

    def update(self, inp):
        if go_back(inp) or inp.was_pressed("menu_confirm") or inp.mouse_clicked:
            self.app.push(self.back)

    def draw(self, surf):
        draw_sea_background(surf, self.t)
        ui.dim(surf, 200)
        title(surf, "Recordes", 60, 52)
        if not self.records:
            ui.text(surf, "Nenhum capítulo concluído ainda.", 30, (W // 2, H // 2 - 10), Colors.UI_TEXT, "center")
            ui.text(surf, "Termine um capítulo para registrar sua nota.", 24, (W // 2, H // 2 + 26),
                    Colors.UI_DIM, "center")
        else:
            cols = [("Nota", 120), ("Capítulo", 200), ("Tempo", 420), ("Credib.", 530), ("Pistas", 640),
                    ("Dificuldade", 740)]
            for label, x in cols:
                ui.text(surf, label, 22, (x, 120), Colors.UI_ACCENT)
            y = 156
            for r in self.records:
                tempo = int(r.get("tempo", 0))
                vals = [r.get("nota", "-"), f"{r.get('capitulo', 1)}", f"{tempo // 60}:{tempo % 60:02d}",
                        str(r.get("credibilidade", "-")), str(r.get("pistas", "-")),
                        Game.DIFFICULTIES.get(r.get("dificuldade"), {}).get("label", "-")]
                for (label, x), v in zip(cols, vals):
                    ui.text(surf, v, 24, (x, y), Colors.UI_TEXT)
                y += 34
        footer(surf, "ESC ou Enter volta")


CREDITS = [
    ("Universidade São Judas Tadeu — USJT", 30, Colors.UI_TEXT),
    ("Usabilidade Web e Jogos · Desenvolvimento de Jogo · 2026", 24, Colors.UI_DIM),
    ("", 20, None),
    ("Equipe", 28, Colors.UI_ACCENT),
    ("(nomes do grupo — editar em src/menus.py, lista CREDITS)", 22, Colors.UI_DIM),
    ("", 20, None),
    ("Feito em Python com pygame-ce", 22, Colors.UI_DIM),
    ("Gráficos e sons provisórios", 22, Colors.UI_DIM),
]


class CreditsState(Screen):
    def __init__(self, app, back):
        super().__init__(app)
        self.back = back

    def update(self, inp):
        if go_back(inp) or inp.was_pressed("menu_confirm") or inp.mouse_clicked:
            self.app.push(self.back)

    def draw(self, surf):
        draw_sea_background(surf, self.t)
        ui.dim(surf, 190)
        title(surf, "Créditos", 70, 52)
        y = 150
        for msg, size, col in CREDITS:
            if msg:
                ui.text(surf, msg, size, (W // 2, y), col, "center")
            y += size + 12
        footer(surf, "ESC ou Enter volta")
