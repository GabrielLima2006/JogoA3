"""Ponto de entrada: janela, loop principal e troca de estados."""

import os
import sys

import pygame

from src.audio import Audio
from src.config import Display
from src.input import Input
from src.progress import SAVE_PATH
from src.menus import MenuState
from src.states import PauseState, PlayState


class App:
    def __init__(self, headless=False, save_path=SAVE_PATH):
        pygame.init()
        flags = 0 if headless else pygame.SCALED | pygame.RESIZABLE
        self.screen = pygame.display.set_mode((Display.WIDTH, Display.HEIGHT), flags)
        pygame.display.set_caption(Display.TITLE)
        self.clock = pygame.time.Clock()
        self.input = Input()
        self.audio = Audio()
        self.save_path = save_path
        self.records_path = os.path.join(os.path.dirname(save_path), "records.json")
        self.running = True
        self.state = MenuState(self)

    # --- transições de estado ---
    def start_game(self, progress=None):
        self.input.reset()
        self.state = PlayState(self, progress)

    def to_menu(self):
        self.input.reset()
        self.state = MenuState(self)

    def push(self, state):
        """Abre uma tela por cima da partida (pausa, mapa, loja...)."""
        self.state = state

    def resume(self, play):
        play.accumulator = 0.0
        # mantém o que está segurado agora, descarta cliques do menu
        self.input.consume()
        self.state = play

    # --- loop ---
    def run(self):
        while self.running:
            dt = min(self.clock.tick(Display.FPS_CAP) / 1000.0, Display.MAX_FRAME_DT)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.WINDOWFOCUSLOST:
                    # evita "tecla presa" ao trocar de janela
                    self.input.reset()
                    if isinstance(self.state, PlayState) and self.state.player.alive:
                        self.push(PauseState(self, self.state))
                else:
                    self.input.process_event(event)
            self.state.frame(dt, self.input)
            self.state.draw(self.screen)
            pygame.display.flip()
        pygame.quit()


def main():
    try:
        App().run()
    except Exception:
        # registra o erro num arquivo ao lado do jogo, para os testadores mandarem
        import traceback
        from src.paths import DATA_DIR
        with open(os.path.join(DATA_DIR, "erro.txt"), "w", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        raise
    return 0


if __name__ == "__main__":
    sys.exit(main())
