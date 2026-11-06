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
    "heal", "block", "coin", "item", "buy", "boss", "step", "skid",
    "break_wood", "explosion", "ability", "door",
    "health_up", "slime_hit", "slime_death", "ground_slam", "door_crash", "ui_woosh",
)

AUDIO_DIR = asset("sons", "efeitos")
MUSIC_DIR = asset("sons", "musicas")


class Audio:
    def __init__(self, volume=AC.SFX_VOLUME):
        self.enabled = False
        self.volume = volume
        self.sounds = {}
        self.current_music = None
        self.muted = False
        self.music_volume = AC.MUSIC_VOLUME
        self.sfx_volume = volume
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
        if snd is not None and not self.muted:
            snd.set_volume(self.sfx_volume * AC.SFX_GAIN.get(name, 1.0))
            snd.play()

    def toggle_mute(self):
        self.muted = not self.muted
        self._apply_music_volume()
        return self.muted

    def change_volume(self, which, delta):
        """Ajusta 'music' ou 'sfx' em passos (0.0 a 1.0)."""
        if which == "music":
            self.music_volume = min(1.0, max(0.0, self.music_volume + delta))
            self._apply_music_volume()
        else:
            self.sfx_volume = min(1.0, max(0.0, self.sfx_volume + delta))
            self.play("ui_move")

    def _apply_music_volume(self):
        if self.enabled:
            try:
                pygame.mixer.music.set_volume(0.0 if self.muted else self.music_volume)
            except pygame.error:
                pass

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
            pygame.mixer.music.set_volume(0.0 if self.muted else self.music_volume)
            pygame.mixer.music.play(loops, fade_ms=800)
        except pygame.error:
            pass
