"""Progresso do jogador (inventário, mundo) e save em arquivo JSON."""

import json
import os

from .config import Progression as PR
from .paths import DATA_DIR

SAVE_DIR = os.path.join(DATA_DIR, "saves")
SAVE_PATH = os.path.join(SAVE_DIR, "save.json")

CHARMS = {
    "lamina": {"name": "Lâmina Longa", "cost": 2, "desc": "Golpes alcançam 30% mais longe."},
    "forca": {"name": "Força Bruta", "cost": 3, "desc": "Golpes causam 50% mais dano."},
    "ima": {"name": "Ímã", "cost": 1, "desc": "Atrai moedas de longe."},
    "foco": {"name": "Foco Rápido", "cost": 2, "desc": "Cura 40% mais rápido."},
    "vigor": {"name": "Vigor", "cost": 2, "desc": "+1 de vida máxima."},
    "vento": {"name": "Passo de Vento", "cost": 2, "desc": "Dash mais longo e recarga menor."},
    "coletor": {"name": "Coletor", "cost": 1, "desc": "+50% de energia por acerto."},
    "bussola": {"name": "Bússola", "cost": 1, "desc": "Mostra sua posição no mapa."},
}

ABILITIES = {
    "dash": ("Passo ilusório", "Shift esquerdo: um passo de fumaça rápido, no chão ou no ar."),
    "double_jump": ("Levitação", "Aperte Espaço no ar para pular de novo (pulo duplo)."),
}

# (id, rótulo, preço) — "charm:x" vende um amuleto
SHOP_STOCK = [
    ("map", "Mapa", 30),
    ("charm:bussola", "Amuleto: Bússola", 40),
    ("charm:ima", "Amuleto: Ímã", 60),
    ("charm:foco", "Amuleto: Foco Rápido", 120),
    ("fragment", "Fragmento de vida", 150),
    ("notch", "Entalhe (+1 espaço de amuleto)", 200),
]


class Progress:
    VERSION = 1

    def __init__(self):
        self.abilities = set(PR.START_ABILITIES)
        self.coins = 0
        self.fragments = 0
        self.ore = 0
        self.weapon_level = 0
        self.notches = PR.BASE_NOTCHES
        self.charms_owned = []
        self.charms_equipped = []
        self.has_map = False
        self.visited = set()
        self.collected = set()       # "sala:índice" de itens já pegos
        self.broken = set()          # "sala:tx:ty" de paredes quebradas
        self.bosses = set()          # salas cujo chefe foi derrotado
        self.shop_bought = set()
        self.flags = set()           # marcos da história (ex.: "atracado")
        self.letters = set()         # cartas da capitã encontradas
        self.deaths = 0
        self.play_time = 0.0         # segundos de partida (para placar e recordes)
        self.talked = set()          # personagens com quem já conversou
        self.protagonist = "ela"     # só a feiticeira é jogável; "ele" ficou no código
        self.difficulty = "normal"
        self.chapter = 1
        self.bench = None            # (sala, x, y) do último banco
        self.bag = None              # (sala, x, y, moedas) perdidas na morte

    # --- atributos derivados ---
    def equipped(self, charm_id):
        return charm_id in self.charms_equipped

    @property
    def max_hp(self):
        from .config import Game
        bonus = Game.DIFFICULTIES.get(self.difficulty, {}).get("hp_bonus", 0)
        return PR.BASE_HP + bonus + self.fragments // PR.FRAGMENTS_PER_HP + (1 if self.equipped("vigor") else 0)

    @property
    def notches_used(self):
        return sum(CHARMS[c]["cost"] for c in self.charms_equipped)

    def can_equip(self, charm_id):
        return (charm_id in self.charms_owned and charm_id not in self.charms_equipped
                and self.notches_used + CHARMS[charm_id]["cost"] <= self.notches)

    def toggle_charm(self, charm_id):
        if charm_id in self.charms_equipped:
            self.charms_equipped.remove(charm_id)
            return True
        if self.can_equip(charm_id):
            self.charms_equipped.append(charm_id)
            return True
        return False

    def next_weapon_upgrade(self):
        if self.weapon_level >= len(PR.WEAPON_UPGRADES):
            return None
        return PR.WEAPON_UPGRADES[self.weapon_level]

    # --- aquisição ---
    def give(self, kind, arg=None):
        """Aplica um item. Retorna (título, descrição) para a mensagem na tela."""
        if kind == "coins":
            self.coins += arg
            return None
        if kind == "ability":
            self.abilities.add(arg)
            return ABILITIES[arg]
        if kind == "charm":
            if arg not in self.charms_owned:
                self.charms_owned.append(arg)
            c = CHARMS[arg]
            return (f"Amuleto: {c['name']}", c["desc"] + " Equipe sentando num banco.")
        if kind == "fragment":
            self.fragments += 1
            n = self.fragments % PR.FRAGMENTS_PER_HP
            if n == 0:
                return ("Fragmento de vida", "Fragmentos completos: +1 de vida máxima!")
            return ("Fragmento de vida", f"{n}/{PR.FRAGMENTS_PER_HP} — junte {PR.FRAGMENTS_PER_HP} para ganhar +1 de vida.")
        if kind == "food":
            return None                  # cura aplicada pela partida (precisa do jogador)
        if kind == "letter":
            self.letters.add(arg)
            return None                  # o texto da carta vem da história (chapter1.LETTERS)
        if kind == "ore":
            self.ore += 1
            return ("Minério", "Leve ao ferreiro para melhorar sua arma.")
        if kind == "map":
            self.has_map = True
            return ("Mapa", "Aperte M ou Tab para ver as salas visitadas.")
        if kind == "notch":
            self.notches += 1
            return ("Entalhe", f"Agora você tem {self.notches} espaços de amuleto.")
        raise ValueError(f"item desconhecido: {kind}")

    # --- save ---
    def to_dict(self):
        return {
            "version": self.VERSION,
            "abilities": sorted(self.abilities),
            "coins": self.coins,
            "fragments": self.fragments,
            "ore": self.ore,
            "weapon_level": self.weapon_level,
            "notches": self.notches,
            "charms_owned": list(self.charms_owned),
            "charms_equipped": list(self.charms_equipped),
            "has_map": self.has_map,
            "visited": sorted(self.visited),
            "collected": sorted(self.collected),
            "broken": sorted(self.broken),
            "bosses": sorted(self.bosses),
            "shop_bought": sorted(self.shop_bought),
            "flags": sorted(self.flags),
            "letters": sorted(self.letters),
            "deaths": self.deaths,
            "play_time": round(self.play_time, 2),
            "talked": sorted(self.talked),
            "protagonist": self.protagonist,
            "difficulty": self.difficulty,
            "chapter": self.chapter,
            "bench": list(self.bench) if self.bench else None,
            "bag": list(self.bag) if self.bag else None,
        }

    @classmethod
    def from_dict(cls, d):
        p = cls()
        p.abilities = set(d.get("abilities", []))
        p.coins = int(d.get("coins", 0))
        p.fragments = int(d.get("fragments", 0))
        p.ore = int(d.get("ore", 0))
        p.weapon_level = int(d.get("weapon_level", 0))
        p.notches = int(d.get("notches", PR.BASE_NOTCHES))
        p.charms_owned = [c for c in d.get("charms_owned", []) if c in CHARMS]
        p.charms_equipped = [c for c in d.get("charms_equipped", []) if c in p.charms_owned]
        p.has_map = bool(d.get("has_map", False))
        p.visited = set(d.get("visited", []))
        p.collected = set(d.get("collected", []))
        p.broken = set(d.get("broken", []))
        p.bosses = set(d.get("bosses", []))
        p.shop_bought = set(d.get("shop_bought", []))
        p.protagonist = "ela"   # saves antigos com "ele" passam a usar a feiticeira
        p.difficulty = d.get("difficulty", "normal") if d.get("difficulty") in ("facil", "normal", "dificil") else "normal"
        p.chapter = int(d.get("chapter", 1))
        p.flags = set(d.get("flags", []))
        p.letters = set(d.get("letters", []))
        p.deaths = int(d.get("deaths", 0))
        p.play_time = float(d.get("play_time", 0.0))
        p.talked = set(d.get("talked", []))
        p.bench = tuple(d["bench"]) if d.get("bench") else None
        p.bag = tuple(d["bag"]) if d.get("bag") else None
        return p

    def fresh_copy(self):
        """Novo jogo com o mesmo protagonista, dificuldade e capítulo."""
        p = Progress()
        p.chapter = self.chapter
        p.protagonist = self.protagonist
        p.difficulty = self.difficulty
        return p

    def save(self, path=None):
        path = path or SAVE_PATH
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=1)
            os.replace(tmp, path)
            return True
        except OSError:
            return False

    @classmethod
    def load(cls, path=None):
        path = path or SAVE_PATH
        try:
            with open(path, encoding="utf-8") as f:
                return cls.from_dict(json.load(f))
        except (OSError, ValueError, KeyError, TypeError):
            return None

    @staticmethod
    def exists(path=None):
        return os.path.isfile(path or SAVE_PATH)
