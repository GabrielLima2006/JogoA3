"""Telas fora da partida: menu principal, novo jogo (dificuldade),
introdução, como jogar, recordes e créditos."""

import math
import random

import pygame

from . import ui
from .config import Audio as AudioCfg, Colors, Display, Game
from .input import CONTROLS_TEXT
from .progress import Progress
from .records import best_records, load_records

W, H = Display.WIDTH, Display.HEIGHT

SEA = (16, 30, 48)
SEA_LIGHT = (40, 70, 100)
SKY_TOP = (8, 10, 20)
SKY_BOTTOM = (28, 34, 58)

# o fundo é desenhado em meia resolução e ampliado 2x: pixels grandes como os do jogo
BW, BH = W // 2, H // 2
_bg = {}


def _sky():
    """Céu em faixas com pontilhado entre elas, estrelas fixas e lua com halo."""
    if "sky" not in _bg:
        s = pygame.Surface((BW, BH))
        bands = 10
        for i in range(bands):
            k = i / (bands - 1)
            col = tuple(int(a + (b - a) * k) for a, b in zip(SKY_TOP, SKY_BOTTOM))
            y0 = int(BH * 0.78 * i / bands)
            s.fill(col, (0, y0, BW, BH - y0))
            if i:
                prev = tuple(int(a + (b - a) * (i - 1) / (bands - 1)) for a, b in zip(SKY_TOP, SKY_BOTTOM))
                for x in range(0, BW, 2):
                    s.set_at((x + (y0 // 1) % 2, y0), prev)
        rnd = random.Random(7)
        _bg["stars"] = [(rnd.randrange(BW), rnd.randrange(int(BH * 0.6)), rnd.random() * 6.28, rnd.random())
                        for _ in range(70)]
        # lua com halo
        mx, my = 440, 34
        halo = pygame.Surface((80, 80), pygame.SRCALPHA)
        for r, a in ((36, 14), (28, 22), (21, 34)):
            pygame.draw.circle(halo, (170, 180, 220, a), (40, 40), r)
        s.blit(halo, (mx - 40, my - 40))
        pygame.draw.circle(s, (210, 215, 232), (mx, my), 15)
        pygame.draw.circle(s, (238, 240, 250), (mx - 3, my - 3), 11)
        for cx, cy, r in ((mx + 4, my + 4, 3), (mx - 5, my + 5, 2), (mx + 6, my - 6, 2)):
            pygame.draw.circle(s, (186, 190, 212), (cx, cy), r)
        _bg["sky"] = s
    return _bg["sky"]


def _ship(s, t, sea_y):
    bob = math.sin(t * 1.3) * 2.5
    tilt = math.sin(t * 1.3 + 0.6) * 0.04
    cx, cy = 345, sea_y - 3 + bob

    def rot(px, py):
        return (cx + px * math.cos(tilt) - py * math.sin(tilt), cy + px * math.sin(tilt) + py * math.cos(tilt))
    dark = (20, 17, 24)
    sail = (46, 44, 58)
    pygame.draw.polygon(s, dark, [rot(-60, -13), rot(65, -13), rot(49, 7), rot(-46, 7)])
    pygame.draw.polygon(s, dark, [rot(65, -13), rot(84, -20), rot(66, -10)])
    pygame.draw.line(s, dark, rot(0, -13), rot(0, -86), 2)
    pygame.draw.line(s, dark, rot(-30, -13), rot(-30, -60), 2)
    pygame.draw.line(s, dark, rot(0, -84), rot(76, -18), 1)
    pygame.draw.polygon(s, sail, [rot(2, -80), rot(40, -36), rot(2, -30)])
    pygame.draw.polygon(s, sail, [rot(-2, -76), rot(-26, -40), rot(-2, -34)])
    pygame.draw.polygon(s, sail, [rot(-28, -56), rot(-4, -26), rot(-28, -22)])
    pygame.draw.polygon(s, (120, 30, 40), [rot(0, -86), rot(10, -83), rot(0, -80)])
    for i in range(4):
        wx = rot(-40 + i * 24, -18)
        flick = 0.8 + 0.2 * math.sin(t * 7 + i * 2)
        s.fill(tuple(int(c * flick) for c in (250, 196, 110)), (int(wx[0]) - 1, int(wx[1]) - 1, 3, 2))


def draw_sea_background(surf, t, lightning=True):
    """Céu de tempestade, lua, chuva, navio balançando e ondas (pixel art 2x)."""
    s = _bg.get("frame")
    if s is None:
        s = _bg["frame"] = pygame.Surface((BW, BH))
    s.blit(_sky(), (0, 0))
    for x, y, ph, k in _bg["stars"]:
        a = 0.5 + 0.5 * math.sin(t * (1 + k * 2) + ph)
        if a > 0.35:
            c = int(110 + 120 * a * k)
            s.set_at((x, y), (c, c, min(255, c + 30)))
    # nuvens escuras atravessando
    for i, (y, speed, w) in enumerate(((22, 4, 120), (48, 7, 90), (70, 3, 150))):
        x = (i * 170 + t * speed) % (BW + w) - w
        col = (18 + i * 4, 20 + i * 4, 34 + i * 5)
        pygame.draw.ellipse(s, col, (x, y, w, 14))
        pygame.draw.ellipse(s, col, (x + w * 0.2, y - 6, w * 0.5, 14))
    # relâmpago de vez em quando
    flash = 0.0
    if lightning:
        cycle = t % 9.0
        if 6.0 < cycle < 6.35:
            flash = 1.0 - (cycle - 6.0) / 0.35
            if int(cycle * 30) % 3 != 1:
                bx = 90 + int(t // 9) * 73 % 220
                pts = [(bx, 0)]
                rnd = random.Random(int(t // 9))
                for _ in range(6):
                    pts.append((pts[-1][0] + rnd.randint(-8, 8), pts[-1][1] + rnd.randint(10, 18)))
                pygame.draw.lines(s, (220, 225, 255), False, pts, 1)
    sea_y = 205
    _ship(s, t, sea_y)
    # mar em 3 camadas com espuma
    for layer in range(3):
        y0 = sea_y + layer * 17
        col = tuple(int(c * (0.7 + layer * 0.15)) for c in SEA_LIGHT)
        pts = [(0, BH)]
        for x in range(0, BW + 8, 8):
            pts.append((x, y0 + math.sin(x * 0.04 + t * (1.2 + layer * 0.4) + layer) * (3 + layer)))
        pts.append((BW, BH))
        pygame.draw.polygon(s, SEA if layer else _mix_col(SEA, SKY_BOTTOM, 0.3), pts)
        pygame.draw.lines(s, col, False, pts[1:-1], 1)
        for x in range(layer * 13, BW, 37 + layer * 11):
            y = y0 + math.sin(x * 0.04 + t * (1.2 + layer * 0.4) + layer) * (3 + layer)
            s.fill(_mix_col(col, (255, 255, 255), 0.35), (x, int(y) - 1, 3, 1))
    # reflexo da lua tremendo na água
    for i in range(10):
        y = sea_y + 5 + i * 5 + (i % 2)
        w = 9 - i // 2 + int(math.sin(t * 3 + i * 2.3) * 3)
        if w > 1 and (int(t * 4) + i) % 3:
            s.fill((120, 136, 176), (440 - w // 2 + int(math.sin(t * 2 + i * 1.7) * 4), y, w, 1))
    # chuva fina
    for i in range(60):
        x = (i * 53 + t * 60) % BW
        y = (i * 97 + t * 240) % BH
        s.fill((70, 86, 120), (int(x), int(y), 1, 3))
    if flash > 0:
        fl = pygame.Surface((BW, BH))
        fl.fill((110, 120, 160))
        s.blit(fl, (0, 0), special_flags=pygame.BLEND_RGB_ADD if flash > 0.6 else pygame.BLEND_RGB_MAX)
    pygame.transform.scale(s, (W, H), surf)
    ui.vignette(surf)


def _mix_col(a, b, k):
    return tuple(int(x + (y - x) * k) for x, y in zip(a, b))


def title(surf, msg, y=70, size=60, alpha=None):
    return ui.text(surf, msg, size, (W // 2, y), Colors.UI_TEXT, "center", title=True, alpha=alpha)


def screen_title(surf, msg, t, y=48):
    """Título de tela com ornamento embaixo e entrada suave."""
    a = ui.ease_out(t / 0.4)
    r = ui.text(surf, msg, 50, (W // 2, y - int((1 - a) * 10)), (255, 214, 140), "center", title=True,
                alpha=255 * a)
    ui.ornament(surf, (W // 2, r.bottom + 12), int((r.w // 2 + 40) * a), ui.GOLD, alpha=255 * a)
    return r


def footer(surf, items):
    """Rodapé com teclas desenhadas: [(tecla, ação)]."""
    ui.hints(surf, items, (W // 2, H - 24))


def go_back(inp):
    return inp.was_pressed("pause")


def _hover_moved(screen, inp):
    """True se o mouse se mexeu desde o último quadro (hover não briga com o teclado)."""
    last = getattr(screen, "_mouse", None)
    screen._mouse = inp.mouse_pos
    return last is not None and last != inp.mouse_pos


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
            ("Continuar", "continue", has_save),
            ("Como jogar", "howto"),
            ("Recordes", "records"),
            ("Créditos", "credits"),
            ("Sair", "quit"),
        ], center_y=344, spacing=42, size=34)
        if has_save:
            self.menu.index = 1
        self.has_save = has_save
        self.save_info = None
        if has_save:
            pr = Progress.load(app.save_path)
            if pr is not None:
                m, s = divmod(int(pr.play_time), 60)
                label = Game.DIFFICULTIES.get(pr.difficulty, {}).get("label", "")
                self.save_info = f"Jogo salvo: {label} - {m:02d}:{s:02d} de jogo"

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
        ui.dim(surf, 40)
        a = ui.ease_out(self.t / 0.9)
        bob = int(math.sin(self.t * 1.2) * 3)
        r = ui.text(surf, Game.TITLE.upper(), 68, (W // 2, 92 + bob - int((1 - a) * 24)), (255, 206, 120), "center",
                    title=True, alpha=255 * a)
        sub_a = ui.ease_out((self.t - 0.35) / 0.6)
        ui.ornament(surf, (W // 2, r.bottom + 14), int((r.w // 2) * sub_a), ui.GOLD, alpha=255 * sub_a)
        ui.text(surf, Game.SUBTITLE, 20, (W // 2, r.bottom + 32), (190, 196, 220), "midtop", alpha=255 * sub_a)
        self.menu.draw(surf)
        footer(surf, [("W|S", "escolher"), ("Enter", "confirmar")])
        if self.save_info:
            ui.text(surf, self.save_info, 20, (16, H - 34), Colors.UI_DIM, outline=True)


# ---------------------------------------------------------------------------
class NewGameState(Screen):
    """Escolha da dificuldade (a protagonista é sempre a feiticeira)."""
    PROTAGONIST = "ela"
    CARD_W, CARD_H = 212, 250

    def __init__(self, app):
        super().__init__(app)
        self.difficulties = list(Game.DIFFICULTIES)
        self.di = self.difficulties.index("normal")
        self.cards = []
        self.lift = [0.0] * len(self.difficulties)

    def _layout(self):
        n = len(self.difficulties)
        gap = 16
        total = n * self.CARD_W + (n - 1) * gap
        x0 = 252 + (W - 252 - 20 - total) // 2
        return [pygame.Rect(x0 + i * (self.CARD_W + gap), 132, self.CARD_W, self.CARD_H) for i in range(n)]

    def update(self, inp):
        n = len(self.difficulties)
        if inp.was_pressed("left") or inp.was_pressed("menu_up"):
            self.di = (self.di - 1) % n
            self.app.audio.play("ui_move")
        if inp.was_pressed("right") or inp.was_pressed("menu_down"):
            self.di = (self.di + 1) % n
            self.app.audio.play("ui_move")
        moved = _hover_moved(self, inp)
        clicked = False
        for i, r in enumerate(self.cards or self._layout()):
            if r.collidepoint(inp.mouse_pos):
                if (moved or inp.mouse_clicked) and self.di != i:
                    self.di = i
                    self.app.audio.play("ui_move")
                clicked = clicked or inp.mouse_clicked
        if go_back(inp):
            self.app.to_menu()
            return
        if inp.was_pressed("menu_confirm") or clicked:
            self.app.audio.play("ui_select")
            progress = Progress()
            progress.protagonist = self.PROTAGONIST
            progress.difficulty = self.difficulties[self.di]
            progress.chapter = 1
            self.app.push(IntroState(self.app, progress))

    def draw(self, surf):
        draw_sea_background(surf, self.t)
        ui.dim(surf, 120)
        screen_title(surf, "Novo jogo", self.t, 44)
        ui.text(surf, "Escolha a dificuldade", 20, (W // 2, 92), Colors.UI_DIM, "midtop", outline=True)
        # protagonista à esquerda, num pedestal
        base = pygame.Rect(30, 132, 206, self.CARD_H)
        ui.panel(surf, base, alpha=200, studs=False)
        glow = pygame.Surface((160, 40), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (130, 56, 120, 70), (0, 0, 160, 40))
        pygame.draw.ellipse(glow, (8, 8, 14, 150), (40, 14, 80, 14))
        surf.blit(glow, (base.centerx - 80, base.y + 136))
        draw_protagonist(surf, self.PROTAGONIST, base.centerx, base.y + 158, scale=2, t=self.t, facing=1)
        ui.text(surf, "Nyra", 34, (base.centerx, base.y + 172), (255, 214, 140), "midtop", title=True)
        ui.text(surf, "a feiticeira de chifres", 20, (base.centerx, base.y + 216), Colors.UI_DIM, "midtop")

        dt = 1 / 60
        self.cards = self._layout()
        for i, key in enumerate(self.difficulties):
            d = Game.DIFFICULTIES[key]
            sel = i == self.di
            self.lift[i] += ((1.0 if sel else 0.0) - self.lift[i]) * min(1.0, dt * 14)
            appear = ui.ease_out((self.t - 0.08 * i) / 0.4)
            r = self.cards[i].move(0, int(-8 * self.lift[i] + (1 - appear) * 30))
            ui.panel(surf, r, fill=(28, 32, 52) if sel else ui.PANEL, alpha=240 if sel else 210,
                     trim=ui.GOLD if sel else (92, 96, 120), glow=self.lift[i])
            col = (255, 214, 140) if sel else (170, 176, 200)
            ui.text(surf, d["label"], 40, (r.centerx, r.y + 32), col, "center", title=sel)
            # corações da dificuldade
            hearts = 5 + d["hp_bonus"]
            icon = ui.heart_icon(0, 1)
            hw = 18
            hx = r.centerx - (hearts * hw) // 2
            for h in range(hearts):
                if icon is not None:
                    surf.blit(icon, (hx + h * hw - 3, r.y + 58))
            ui.text(surf, f"{hearts} corações", 20, (r.centerx, r.y + 84), Colors.HP_FULL, "midtop")
            pct = int(round(d["enemy_hp"] * 100))
            ui.text(surf, f"Vida dos inimigos {pct}%", 20, (r.centerx, r.y + 104), Colors.UI_DIM, "midtop")
            pygame.draw.line(surf, (70, 74, 96), (r.x + 20, r.y + 130), (r.right - 20, r.y + 130), 2)
            ui.wrap_text(surf, d["desc"], 20, r.x + 18, r.y + 140, r.w - 36,
                         Colors.UI_TEXT if sel else Colors.UI_DIM, line_gap=2)
        if Progress.exists(self.app.save_path):
            warn = "Começar um novo jogo substitui o save atual."
            wr = ui.text(surf, warn, 20, (W // 2 + 4, 410), (255, 150, 140), "midtop", outline=True)
            ui.diamond(surf, (wr.x - 12, wr.centery), 5, (230, 90, 90))
        footer(surf, [("A|D", "escolher"), ("Enter", "começar"), ("ESC", "voltar")])


def draw_protagonist(surf, key, x, foot_y, scale=2, t=0.0, facing=1):
    """Retrato animado com o mesmo sprite usado no jogo."""
    from . import skins, sprites
    skin = skins.SKINS[key]
    frame = skins.frame_for(skin, "idle", t)
    if frame is None:
        return
    flip = (facing < 0) == skin.faces_right
    ax = skin.anchor_x("idle")
    sprites.blit_anchor(surf, frame, x, foot_y, (ax, frame.get_height() - 1), flip=flip, scale=scale)


# ---------------------------------------------------------------------------
INTRO_SLIDES = [
    "Reino de Aurel. Há dez anos, uma ilusão saiu de controle na academia de magia e um aprendiz foi banido.",
    "Nyra, a aprendiz de chifres, ficou calada. Desde então vive escondida sob o capuz, vendendo truques "
    "como se fosse uma feiticeira de verdade.",
    "Agora ela viaja na Gaivota Rubra, o navio da Capitã Maren, rumo à ilha de Velmora. No porto, gente some "
    "toda lua cheia.",
    "Noite de tempestade. Um grito no convés: a capitã caiu, envenenada. Os ratos do porão uivam e a "
    "tripulação parece enfeitiçada.",
    "Alguém está usando magia de verdade. E a Maré, que dorme sob Velmora, está acordando.",
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
        self.age = 0.0              # tempo desde o início (barras de cinema)

    @property
    def current(self):
        return self.slides[self.index]

    def _full(self):
        return self.current is None or self.typed >= len(self.current)

    def frame(self, dt, inp):
        self.typed += dt * self.CHARS_PER_SEC
        self.age += dt
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
        draw_sea_background(surf, self.age + self.index * 3)
        ui.dim(surf, 150)
        # barras de cinema
        bar = int(54 * ui.ease_out(self.age / 0.6))
        surf.fill((4, 4, 8), (0, 0, W, bar))
        surf.fill((4, 4, 8), (0, H - bar, W, bar))
        if self.current is None:
            a = ui.ease_out(self.t / 0.8)
            ui.text(surf, "Capítulo 1", 34, (W // 2, H // 2 - 64), (190, 196, 220), "center", alpha=255 * a)
            r = title(surf, Game.CHAPTERS[1], H // 2 - 6, 54, alpha=255 * a)
            ui.ornament(surf, (W // 2, r.bottom + 18), int((r.w // 2 + 30) * a), ui.GOLD, alpha=255 * a)
        else:
            size = 34
            lines = ui.wrap_lines(self.current, size, W - 260)
            step = ui.line_height(size) + 6
            y = H // 2 - (len(lines) * step) // 2 - 10
            left = int(self.typed)
            last = None
            for line in lines:
                shown = line[:max(0, left)]
                left -= len(line) + 1
                if shown:
                    last = ui.text(surf, shown, size, (130, y), Colors.UI_TEXT, outline=True)
                y += step
            if self._full() and last is not None and int(self.t * 2.5) % 2 == 0:
                tx, ty = last.right + 14, last.bottom - 14
                pygame.draw.polygon(surf, ui.INK, [(tx - 1, ty - 1), (tx + 11, ty - 1), (tx + 5, ty + 7)])
                pygame.draw.polygon(surf, ui.GOLD, [(tx, ty), (tx + 10, ty), (tx + 5, ty + 5)])
        n = len(self.slides)
        for i in range(n):
            pos = (W // 2 + int((i - (n - 1) / 2) * 22), H - 78)
            col = ui.GOLD if i == self.index else ((120, 110, 90) if i < self.index else (60, 62, 80))
            ui.diamond(surf, pos, 5 if i == self.index else 3, col)
        layer_y = H - 27
        ui.hints(surf, [("Enter|Espaço", "continuar"), ("ESC", "pular introdução")], (W // 2, layer_y))


# ---------------------------------------------------------------------------
HOWTO_PAGES = [
    ("Controles", None),
    ("Objetivo", [
        "Explore o navio e a ilha, vença os 4 chefes e liberte os desaparecidos.",
        "O dash você já tem; o pulo duplo vem do primeiro chefe e abre o mastro e a ilha.",
        "Ache as 3 páginas do diário da capitã para ver o final verdadeiro.",
        "Moedas compram melhorias na loja; amuletos dão bônus permanentes.",
        "Bola de cristal (W): salva o jogo e recupera os corações.",
        "Golpes acertados enchem o orbe de foco. Segure F para se curar.",
    ]),
    ("Regras", [
        "Corações chegam a zero: você volta à última bola de cristal com menos moedas.",
        "Espinhos e água ferem e te levam ao último chão firme.",
        "Tábuas rachadas desabam pouco depois de pisadas. Não pare em cima!",
        "Ataque para baixo no ar (S + clique) quica em inimigos e espinhos.",
        "Chefes têm 2 fases: na metade da vida ficam mais rápidos e perigosos.",
        "A nota final (S, A, B, C) depende de tempo, quedas e páginas do diário.",
    ]),
]


class HowToPlayState(Screen):
    def __init__(self, app, back):
        super().__init__(app)
        self.back = back
        self.page = 0
        self.page_t = 0.0
        self.tabs = []
        self.arrows = []

    def _goto(self, page):
        page = max(0, min(len(HOWTO_PAGES) - 1, page))
        if page != self.page:
            self.page = page
            self.page_t = self.t
            self.app.audio.play("ui_move")

    def update(self, inp):
        if go_back(inp) or inp.was_pressed("menu_confirm") and self.page == len(HOWTO_PAGES) - 1:
            self.app.push(self.back)
            return
        if inp.mouse_clicked:
            for i, r in enumerate(self.tabs):
                if r.collidepoint(inp.mouse_pos):
                    self._goto(i)
                    return
            for step, r in self.arrows:
                if r.collidepoint(inp.mouse_pos):
                    self._goto(self.page + step)
                    return
        if inp.was_pressed("right") or inp.was_pressed("menu_confirm") or inp.mouse_clicked:
            self._goto(self.page + 1)
        if inp.was_pressed("left"):
            self._goto(self.page - 1)

    def draw(self, surf):
        draw_sea_background(surf, self.t)
        ui.dim(surf, 150)
        screen_title(surf, "Como jogar", self.t, 40)
        # abas
        self.tabs = []
        tab_w, gap = 170, 10
        x0 = W // 2 - (len(HOWTO_PAGES) * tab_w + (len(HOWTO_PAGES) - 1) * gap) // 2
        body = pygame.Rect(60, 118, W - 120, 362)
        for i, (name, _) in enumerate(HOWTO_PAGES):
            r = pygame.Rect(x0 + i * (tab_w + gap), 86, tab_w, 36)
            sel = i == self.page
            ui.panel(surf, r.move(0, 0 if sel else 4), fill=(30, 34, 56) if sel else ui.PANEL,
                     alpha=245 if sel else 190, trim=ui.GOLD if sel else (86, 90, 112), studs=False)
            ui.text(surf, name, 20, (r.centerx, r.centery + (0 if sel else 4)),
                    ui.SELECTED if sel else Colors.UI_DIM, "center")
            self.tabs.append(r)
        ui.panel(surf, body, alpha=225)
        a = ui.ease_out((self.t - self.page_t) / 0.3)
        dx = int((1 - a) * 24)
        _, lines = HOWTO_PAGES[self.page]
        if lines is None:
            self._draw_controls(surf, body, dx, a)
        else:
            y = body.y + 30
            for i, line in enumerate(lines):
                ui.diamond(surf, (body.x + 40 + dx, y + 9), 4, ui.GOLD)
                y = ui.wrap_text(surf, line, 20, body.x + 58 + dx, y, body.w - 100, Colors.UI_TEXT) + 22
        # setas laterais
        self.arrows = []
        for step, cx in ((-1, body.x - 26), (1, body.right + 26)):
            target = self.page + step
            r = pygame.Rect(0, 0, 28, 48)
            r.center = (cx, body.centery)
            if 0 <= target < len(HOWTO_PAGES):
                wob = int(math.sin(self.t * 4) * 2) * step
                pts = [(r.centerx - 6 * step + wob, r.centery - 12), (r.centerx + 8 * step + wob, r.centery),
                       (r.centerx - 6 * step + wob, r.centery + 12)]
                pygame.draw.polygon(surf, ui.INK, [(p[0] + 1, p[1] + 2) for p in pts])
                pygame.draw.polygon(surf, ui.GOLD, pts)
                self.arrows.append((step, r))
        footer(surf, [("A|D", "trocar página"), ("Enter", "avançar"), ("ESC", "voltar")])

    @staticmethod
    def _draw_controls(surf, body, dx, a):
        half = (len(CONTROLS_TEXT) + 1) // 2
        col_w = (body.w - 60) // 2
        for i, (key, action) in enumerate(CONTROLS_TEXT):
            c, r = divmod(i, half)
            x = body.x + 30 + c * col_w + dx
            y = body.y + 34 + r * 44
            kr = ui.keycap(surf, key, (x, y), "midleft")
            ui.text(surf, action, 20, (max(kr.right + 12, x + 124), y), Colors.UI_TEXT, "midleft")


class RecordsState(Screen):
    def __init__(self, app, back, path=None):
        super().__init__(app)
        self.back = back
        self.records = best_records(load_records(path or getattr(app, "records_path", None)))

    def update(self, inp):
        if go_back(inp) or inp.was_pressed("menu_confirm") or inp.mouse_clicked:
            self.app.push(self.back)

    GRADE_COLORS = {"S": (255, 214, 120), "A": (210, 220, 240), "B": (220, 160, 110), "C": (150, 150, 170)}

    def draw(self, surf):
        draw_sea_background(surf, self.t)
        ui.dim(surf, 150)
        screen_title(surf, "Recordes", self.t, 48)
        if not self.records:
            box = pygame.Rect(0, 0, 640, 200)
            box.center = (W // 2, H // 2 + 20)
            ui.panel(surf, box, alpha=225)
            from . import sprites
            ball = sprites.image("objetos", "bola_de_cristal.png")
            if ball is not None:
                img = ball.subsurface(ball.get_bounding_rect())
                bob = int(math.sin(self.t * 2) * 3)
                surf.blit(img, img.get_rect(midtop=(box.centerx, box.y + 22 + bob)))
            ui.text(surf, "Nenhuma partida concluída ainda.", 34, (box.centerx, box.y + 116), Colors.UI_TEXT,
                    "midtop")
            ui.text(surf, "Vença o chefe final para registrar sua nota.", 20, (box.centerx, box.y + 158),
                    Colors.UI_DIM, "midtop")
        else:
            box = pygame.Rect(70, 104, W - 140, 64 + 40 * min(8, len(self.records)))
            ui.panel(surf, box, alpha=228)
            cols = [("Nota", 120, "center"), ("Pontos", 230, "center"), ("Tempo", 350, "center"),
                    ("Quedas", 460, "center"), ("Diário", 570, "center"), ("Dificuldade", 720, "center")]
            for label, x, anchor in cols:
                ui.text(surf, label, 20, (x, box.y + 22), ui.GOLD, anchor)
            pygame.draw.line(surf, ui.GOLD_DARK, (box.x + 20, box.y + 38), (box.right - 20, box.y + 38), 2)
            y = box.y + 62
            for n, r in enumerate(self.records[:8]):
                appear = ui.ease_out((self.t - 0.06 * n) / 0.35)
                row = pygame.Rect(box.x + 14, y - 18, box.w - 28, 36)
                if n % 2 == 0 or n == 0:
                    shade = pygame.Surface(row.size, pygame.SRCALPHA)
                    shade.fill((255, 226, 160, 26) if n == 0 else (255, 255, 255, 10))
                    surf.blit(shade, row)
                tempo = int(r.get("tempo", 0))
                grade = str(r.get("nota", "-"))
                vals = [str(r.get("pontos", "-")), f"{tempo // 60}:{tempo % 60:02d}",
                        str(r.get("quedas", "-")), f"{r.get('cartas', '-')}/3",
                        Game.DIFFICULTIES.get(r.get("dificuldade"), {}).get("label", "-")]
                ui.text(surf, grade, 34, (cols[0][1], y), self.GRADE_COLORS.get(grade, Colors.UI_TEXT), "center",
                        title=True, alpha=255 * appear)
                for (label, x, anchor), v in zip(cols[1:], vals):
                    ui.text(surf, v, 20, (x, y), Colors.UI_TEXT, anchor, alpha=255 * appear)
                if n == 0:
                    ui.diamond(surf, (row.x + 14, y), 5, ui.GOLD)
                y += 40
        footer(surf, [("ESC|Enter", "voltar")])


# (texto, tamanho, cor). Autor, link e licença de cada asset também estão em assets/CREDITOS.md.
CREDITS = [
    ("Universidade São Judas Tadeu - USJT", 30, Colors.UI_TEXT),
    ("Usabilidade, desenvolvimento web, mobile e jogos", 24, Colors.UI_DIM),
    ("Prof. Elzo Brito dos Santos Filho", 22, Colors.UI_DIM),
    ("", 10, None),
    ("Equipe", 30, Colors.UI_ACCENT),
    ("[Nome do integrante - RA]", 24, Colors.UI_TEXT),
    ("(editar em src/menus.py, lista CREDITS)", 20, Colors.UI_DIM),
    ("", 10, None),
    ("Programação, design de fases e roteiro", 30, Colors.UI_ACCENT),
    ("Equipe Maré de Mentiras", 24, Colors.UI_TEXT),
    ("", 10, None),
    ("Arte e animação", 30, Colors.UI_ACCENT),
    ("Super Pixel Effects Gigapack - Will Tice / unTied Games (efeitos)", 22, Colors.UI_TEXT),
    ("Metroidvania Forge - capangas, cavaleiro, slime, tiles, objetos", 22, Colors.UI_TEXT),
    ("Feiticeira (idle & walk) - protagonista", 22, Colors.UI_TEXT),
    ("Dark VFX 01-02 e Smear VFX 01 - magias e cortes", 22, Colors.UI_TEXT),
    ("UIBundleFree (Mediavel) - interface", 22, Colors.UI_TEXT),
    ("Ghostpixxells - pixelfood (comidas)", 22, Colors.UI_TEXT),
    ("Screaming Brain Studios - Tiny Texture Pack (CC0)", 22, Colors.UI_TEXT),
    ("Personagens do navio e itens desenhados pela equipe", 22, Colors.UI_TEXT),
    ("", 10, None),
    ("Música e sons", 30, Colors.UI_ACCENT),
    ("Metroidvania Forge - músicas e efeitos sonoros", 22, Colors.UI_TEXT),
    ("", 10, None),
    ("Fonte", 30, Colors.UI_ACCENT),
    ("Alagard - Hewett Tsoi (acentos compostos pelo jogo)", 22, Colors.UI_TEXT),
    ("", 10, None),
    ("Tecnologia", 30, Colors.UI_ACCENT),
    ("Python 3.12 e pygame-ce", 22, Colors.UI_TEXT),
    ("", 10, None),
    ("Links e licenças completas: assets/CREDITOS.md", 22, Colors.UI_DIM),
    ("Obrigado por jogar!", 34, Colors.UI_ACCENT),
]


def _credit_row(size, color):
    """Altura e estilo de cada linha dos créditos (cabeçalhos ganham ornamento)."""
    if color is None:
        return 14
    if color == Colors.UI_ACCENT:
        return 52
    return 26


class CreditsState(Screen):
    """Créditos que sobem sozinhos; W/S ou setas aceleram e voltam."""
    SPEED = 34

    def __init__(self, app, back):
        super().__init__(app)
        self.back = back
        self.scroll = 0.0
        self.total = sum(_credit_row(size, col) for _, size, col in CREDITS)

    def frame(self, dt, inp):
        speed = self.SPEED
        if inp.is_held("down"):
            speed = self.SPEED * 6
        elif inp.is_held("up"):
            speed = -self.SPEED * 6
        self.scroll = max(0.0, min(self.total, self.scroll + speed * dt))
        super().frame(dt, inp)

    def update(self, inp):
        if go_back(inp) or inp.was_pressed("menu_confirm") or inp.mouse_clicked:
            self.app.push(self.back)

    def draw(self, surf):
        draw_sea_background(surf, self.t)
        ui.dim(surf, 150)
        box = pygame.Rect(110, 104, W - 220, H - 160)
        ui.panel(surf, box, alpha=228)
        top, bottom = box.y + 10, box.bottom - 10
        clip = surf.get_clip()
        surf.set_clip(pygame.Rect(box.x + 8, top, box.w - 16, bottom - top))
        y = bottom - 30 - self.scroll
        for msg, size, col in CREDITS:
            h = _credit_row(size, col)
            if msg and top - 60 < y < bottom + 10:
                if col == Colors.UI_ACCENT:
                    big = size >= 34
                    r = ui.text(surf, msg, 34 if big else 20, (W // 2, y + 14), (255, 214, 140), "center",
                                title=big)
                    if not big:
                        ui.ornament(surf, (W // 2, r.bottom + 9), r.w // 2 + 30, ui.GOLD)
                else:
                    ui.text(surf, msg, 20, (W // 2, y + 6), col, "center")
            y += h
        # bordas que somem (texto entra e sai suave)
        for i in range(12):
            a = int(220 * (1 - i / 12))
            line = pygame.Surface((box.w - 16, 2), pygame.SRCALPHA)
            line.fill((*ui.PANEL, a))
            surf.blit(line, (box.x + 8, top + i * 2))
            surf.blit(line, (box.x + 8, bottom - 2 - i * 2))
        surf.set_clip(clip)
        # barra de rolagem
        k = self.scroll / self.total if self.total else 0
        track = pygame.Rect(box.right - 14, box.y + 20, 4, box.h - 40)
        pygame.draw.rect(surf, (40, 44, 62), track)
        pygame.draw.rect(surf, ui.GOLD, (track.x, track.y + int((track.h - 24) * k), 4, 24))
        screen_title(surf, "Créditos", self.t, 48)
        footer(surf, [("W|S", "rolar"), ("ESC|Enter", "voltar")])
