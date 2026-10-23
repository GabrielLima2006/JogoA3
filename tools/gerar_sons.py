"""Gera sons curtos que faltavam nos pacotes (passo e derrapagem), sem bibliotecas extras.

Uso:  python tools/gerar_sons.py   ->  assets/sons/efeitos/step.wav e skid.wav
"""

import math
import os
import random
import struct
import wave

RATE = 22050
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "sons", "efeitos")


def _write(name, samples):
    path = os.path.join(OUT, name + ".wav")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", max(-32767, min(32767, int(v * 32767)))) for v in samples))
    print(path)


def step(seed=3):
    """Passo: batida grave e curta com um chiado de terra."""
    rnd = random.Random(seed)
    n = int(RATE * 0.07)
    out, low = [], 0.0
    for i in range(n):
        t = i / RATE
        env = math.exp(-t * 70)
        noise = rnd.uniform(-1, 1)
        low += (noise - low) * 0.18                  # filtro passa-baixa simples
        thump = math.sin(2 * math.pi * 95 * t) * math.exp(-t * 90)
        out.append((low * 0.5 + thump * 0.7) * env * 0.55)
    return out


def skid(seed=5):
    """Derrapagem: chiado que vai abafando."""
    rnd = random.Random(seed)
    n = int(RATE * 0.2)
    out, low = [], 0.0
    for i in range(n):
        t = i / RATE
        k = i / n
        env = (1 - k) ** 1.6 * min(1.0, t * 80)
        noise = rnd.uniform(-1, 1)
        low += (noise - low) * (0.5 - 0.4 * k)
        out.append(low * env * 0.45)
    return out


if __name__ == "__main__":
    _write("step", step())
    _write("skid", skid())
