"""Efeitos sonoros e música.

Efeitos: arquivos em assets/sons/efeitos/ com o nome do efeito (ex.: jump.wav ou
jump.ogg). Músicas: assets/sons/musicas/. Arquivos ausentes são ignorados; se o
mixer não iniciar (sem placa de som), o jogo segue normalmente.
"""

import os

import pygame

from .config import Audio as AC
from .paths import asset

SFX_NAMES = (
    "jump", "double_jump", "land", "dash", "attack_quick", "attack_heavy",
    "heavy_charge", "hit", "heavy_hit", "hurt", "death", "enemy_death",
    "shoot", "impact", "checkpoint", "ui_move", "ui_select",
    "heal", "block", "coin", "item", "buy", "boss",
)

AUDIO_DIR = asset("sons", "efeitos")
MUSIC_DIR = asset("sons", "musicas")


class Audio:
    def __init__(self, volume=AC.SFX_VOLUME):
        self.enabled = False
        self.volume = volume
        self.sounds = {}
        self.current_music = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.enabled = True
        except pygame.error:
            return
        for name in SFX_NAMES:
            for ext in (".wav", ".ogg", ".mp3"):
                path = os.path.join(AUDIO_DIR, name + ext)
                if os.path.isfile(path):
                    try:
                        snd = pygame.mixer.Sound(path)
                        snd.set_volume(volume * AC.SFX_GAIN.get(name, 1.0))
                        self.sounds[name] = snd
                    except pygame.error:
                        pass
                    break

    def play(self, name):
        snd = self.sounds.get(name)
        if snd is not None:
            snd.play()

    def play_music(self, filename, loops=-1):
        """Troca a música; não reinicia se a mesma já estiver tocando. None = silêncio."""
        if not self.enabled or filename == self.current_music:
            return
        self.current_music = filename
        try:
            if filename is None:
                pygame.mixer.music.fadeout(600)
                return
            path = os.path.join(MUSIC_DIR, filename)
            if not os.path.isfile(path):
                return
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(AC.MUSIC_VOLUME)
            pygame.mixer.music.play(loops, fade_ms=800)
        except pygame.error:
            pass
