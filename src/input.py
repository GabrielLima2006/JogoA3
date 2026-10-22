"""Entrada com mapeamento de ações (remapeável).

Cada ação aponta para uma lista de "binds": ("key", código) ou ("mouse", botão).
Eventos de pressionar/soltar ficam "travados" até a simulação consumi-los,
para que nenhum toque se perca quando um quadro roda zero ou vários passos
de física (ou durante o hitstop).
"""

import pygame


DEFAULT_BINDINGS = {
    "left": [("key", pygame.K_a), ("key", pygame.K_LEFT)],
    "right": [("key", pygame.K_d), ("key", pygame.K_RIGHT)],
    "jump": [("key", pygame.K_SPACE)],
    "dash": [("key", pygame.K_LSHIFT)],
    "attack_quick": [("mouse", 1)],
    "attack_heavy": [("mouse", 3)],
    "pause": [("key", pygame.K_ESCAPE), ("key", pygame.K_p)],
    "mute": [("key", pygame.K_m)],
    "up": [("key", pygame.K_w), ("key", pygame.K_UP)],
    "down": [("key", pygame.K_s), ("key", pygame.K_DOWN)],
    "heal": [("key", pygame.K_f)],
    "interact": [("key", pygame.K_w), ("key", pygame.K_UP)],
    "map": [("key", pygame.K_TAB)],
    # navegação de menus
    "menu_up": [("key", pygame.K_w), ("key", pygame.K_UP)],
    "menu_down": [("key", pygame.K_s), ("key", pygame.K_DOWN)],
    "menu_confirm": [("key", pygame.K_RETURN), ("key", pygame.K_KP_ENTER), ("key", pygame.K_SPACE)],
    # ferramenta de desenvolvimento (hitboxes / FPS)
    "debug": [("key", pygame.K_F3)],
}

# Texto exibido no menu, na pausa e no README.
CONTROLS_TEXT = [
    ("A / D ou setas", "mover"),
    ("Espaço", "pular (segure = mais alto)"),
    ("Espaço no ar", "pulo duplo (depois do chefe 1)"),
    ("Shift esquerdo", "dash"),
    ("Botão esquerdo", "ataque rápido"),
    ("Botão direito", "ataque pesado"),
    ("W / S + ataque", "golpe p/ cima, diagonal ou baixo (no ar)"),
    ("S", "descer da plataforma"),
    ("F (segurar)", "curar (gasta energia)"),
    ("W ou seta cima", "interagir (banco, loja)"),
    ("Tab", "mapa"),
    ("M", "silenciar / ligar o som"),
    ("ESC ou P", "pausar / inventário"),
]


class Input:
    def __init__(self, bindings=None):
        self.bindings = {k: list(v) for k, v in (bindings or DEFAULT_BINDINGS).items()}
        self._reverse = {}
        self._rebuild()
        self.held = set()
        self.pressed = set()
        self.released = set()
        self.mouse_pos = (0, 0)
        self.mouse_clicked = False

    def _rebuild(self):
        self._reverse = {}
        for action, binds in self.bindings.items():
            for b in binds:
                self._reverse.setdefault(b, []).append(action)

    def rebind(self, action, binds):
        self.bindings[action] = list(binds)
        self._rebuild()

    def process_event(self, event):
        bind = None
        down = None
        if event.type == pygame.KEYDOWN:
            bind, down = ("key", event.key), True
        elif event.type == pygame.KEYUP:
            bind, down = ("key", event.key), False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            bind, down = ("mouse", event.button), True
            self.mouse_pos = event.pos
            if event.button == 1:
                self.mouse_clicked = True
        elif event.type == pygame.MOUSEBUTTONUP:
            bind, down = ("mouse", event.button), False
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
        if bind is None:
            return
        for action in self._reverse.get(bind, ()):
            if down:
                # repetição de tecla do SO não gera novo "pressed"
                if action not in self.held:
                    self.pressed.add(action)
                self.held.add(action)
            else:
                # só solta se nenhum outro bind da ação continua segurado
                if not self._any_other_bind_held(action, bind):
                    self.held.discard(action)
                    self.released.add(action)

    def _any_other_bind_held(self, action, released_bind):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed(5)
        for kind, code in self.bindings[action]:
            if (kind, code) == released_bind:
                continue
            if kind == "key":
                try:
                    if keys[code]:
                        return True
                except IndexError:
                    pass
            elif kind == "mouse" and 1 <= code <= 5 and mouse[code - 1]:
                return True
        return False

    # --- consultas ---
    def is_held(self, action):
        return action in self.held

    def was_pressed(self, action):
        return action in self.pressed

    def was_released(self, action):
        return action in self.released

    def axis_x(self):
        return (1 if "right" in self.held else 0) - (1 if "left" in self.held else 0)

    def consume(self):
        """Chamado depois que um passo de simulação leu a entrada."""
        self.pressed.clear()
        self.released.clear()
        self.mouse_clicked = False

    def reset(self):
        self.held.clear()
        self.consume()

    # usado pelos testes automatizados
    def simulate(self, held=(), pressed=(), released=()):
        self.held = set(held)
        self.pressed |= set(pressed)
        self.released |= set(released)
