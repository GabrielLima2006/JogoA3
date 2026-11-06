"""Inimigos do navio e da ilha: mesmo comportamento dos inimigos-base, com visual próprio.

rato (patrulheiro) · gaivota (voador) · capanga encapuzado (perseguidor)
slime da maré (saltador) · canhão (torreta) · pirata de escudo (escudeiro) · caixa quebrável
"""

import pygame

from . import pixelart, sprites
import json
import math

from .enemies import (Chaser, Enemy, Flier, Gunner, Jumper, Patroller, Shield, Turret, approach, ground_ahead,
                      wall_ahead)
from .config import Enemies as E
from .paths import asset


def _blit_human(surf, img, enemy, cam_x, cam_y, white=False):
    """Humanos do pixelart têm 3 px vazios abaixo das botas."""
    v = sprites.variant(img, False, white, 1)
    surf.blit(v, v.get_rect(midbottom=(round(enemy.cx - cam_x), round(enemy.bottom - cam_y + 3))))


def _blit_bottom(surf, img, enemy, cam_x, cam_y, white=False, flip=False, scale=1):
    v = sprites.variant(img, flip, white, scale)
    surf.blit(v, v.get_rect(midbottom=(round(enemy.cx - cam_x), round(enemy.bottom - cam_y))))


# ---------------------------------------------------------------------------
# Criaturas da ilha e do templo (modelos da equipe: personagens/npcs.png)
# ---------------------------------------------------------------------------

_NPC_META = None


def npc_frame(name):
    """Quadro do modelo `name` (olhando para a esquerda) e a âncora do pé."""
    global _NPC_META
    if _NPC_META is None:
        try:
            with open(asset("img", "personagens", "npcs.json"), encoding="utf-8") as f:
                _NPC_META = json.load(f)
        except OSError:
            _NPC_META = {"rows": {}, "frame": [128, 96], "anchor": [64, 95]}
    row = _NPC_META["rows"].get(name)
    fw, fh = _NPC_META["frame"]
    frames = sprites.grid("personagens/npcs.png", fw, fh)
    if row is None or not frames:
        return None, (0, 0)
    return frames[row[0]], tuple(_NPC_META["anchor"])


# Modelos de npcs.png trocados por personagens de pacotes da internet (pedido do Gabriel, até
# chegarem as artes originais): humanos viram papéis do elenco; múmia e cavaleiro negro, esqueletos.
AS_CAST = {"comerciante": "mercador", "ferreiro": "ferreiro", "ladino": "capanga", "cavaleiro_escudo": "escudeiro",
           "aldea": "aldea", "curandeira": "curandeira", "fazendeiro": "pescador", "bardo": "marinheiro",
           "estudioso": "amigo", "velho": "pescador", "anciã": "aldea", "menino": "grumete"}
AS_SKELETON = {"mumia": "amarelo", "cavaleiro_negro": "branco"}
SKELETON_ANCHOR = (46, 63)          # pé no quadro 96x64 (o esqueleto olha para a direita)
def _skeleton_frame(color, t, moving, lean):
    """Quadro do esqueleto (Skeletons Free Pack): parado, andando ou atacando."""
    kind = "ataque" if lean else ("andando" if moving else "parado")
    frames = sprites.grid(f"inimigos/esqueleto_{color}_{kind}.png", 96, 64)
    if not frames:
        return None
    return frames[int(t * (14 if lean else 10)) % len(frames)]


def draw_model(surf, name, x, foot_y, t, facing, moving=False, white=False, lean=0.0, float_amp=0.0, scale=1.0,
               alpha=255, state="", vy=0.0, airborne=False):
    """Desenha os quadros sem deformar o pixel art; movimento vem do corpo e dos efeitos."""
    def pose_and_blit(frame, flip=False, frame_scale=1.0):
        # Ampliar ou girar a folha inteira deslocava partes finas e borrava contornos.
        # Mantemos a grade original e ancoramos pelo pé, inclusive ao espelhar.
        # O espelhamento fica para blit_anchor, que também corrige a âncora.
        v = sprites.variant(frame, False, white, frame_scale)
        if alpha < 255:
            v = v.copy()
            v.set_alpha(alpha)
        bob = (round(abs(math.sin(t * 12)) * 2) if moving else 0) if not airborne else 0
        lift = round(math.sin(t * 2.5) * float_amp)
        sprites.blit_anchor(surf, v, x, foot_y - bob + lift,
                            (v.get_width() // 2, v.get_height() - 1), flip=flip)

        # O ataque aparece como efeito separado; o corpo permanece pixel-perfect.
        if state in ("bash", "lunge", "charge", "slash", "pistol") or lean != 0:
            magia = name in ("diabrete", "espirito", "lich")
            frames = sprites.effect("brilho") if magia else sprites.grid("efeitos/corte_h.png", 48, 48)
            if frames:
                efeito = sprites.variant(frames[int(t * 18) % len(frames)], facing < 0)
                bounds = frame.get_bounding_rect()
                cy = foot_y - ((frame.get_height() - 1) - (bounds.top + bounds.bottom) / 2) * frame_scale
                surf.blit(efeito, efeito.get_rect(center=(round(x + facing * (bounds.width * frame_scale / 2 + 8)),
                                                          round(cy))))

    # Só estas duas criaturas ainda usam os retratos laterais recém-importados.
    # Os modelos sombreados da folha da equipe são melhores para os demais inimigos.
    if name in ("lobo", "goblin"):
        # Folha de tools/animar_pose.py: passada, respiração e bote a partir da vista east.
        pose = "attack" if lean else ("walk" if moving and not airborne else "idle")
        speed = {"attack": 5.0, "walk": 1.8 if name == "lobo" else 1.4, "idle": 0.8}[pose]
        quadro, pe = sprites.pose_anim(name, pose, t * speed)
        if quadro is not None:
            v = quadro
            if alpha < 255:
                v = quadro.copy()
                v.set_alpha(alpha)
            lift = round(math.sin(t * 2.5) * float_amp)
            sprites.blit_anchor(surf, v, x, foot_y + lift, pe, flip=facing < 0, white=white, scale=scale)
            if lean and name == "goblin":            # porretada: mesmo corte dos outros inimigos
                frames = sprites.grid("efeitos/corte_h.png", 48, 48)
                if frames:
                    slash = sprites.variant(frames[int(t * 18) % len(frames)], facing < 0)
                    surf.blit(slash, slash.get_rect(center=(round(x + facing * 22), round(foot_y - 30))))
            return
    if name == "diabrete":
        # Folha de tools/animar_pose.py: flutua batendo; no alerta recolhe; na perseguição mergulha.
        if state == "alert":
            pose, ph = "attack", 0.5 / 3
        elif state == "chase" or lean:
            pose, ph = "attack", (1.5 + int(t * 10) % 2) / 3
        else:
            pose, ph = "idle", t * 1.6
        quadro, pe = sprites.pose_anim(name, pose, ph)
        if quadro is not None:
            v = quadro
            if alpha < 255:
                v = quadro.copy()
                v.set_alpha(alpha)
            lift = round(math.sin(t * 2.5) * float_amp)
            sprites.blit_anchor(surf, v, x, foot_y + lift, pe, flip=facing < 0, white=white, scale=scale)
            return
    if name in ("espirito", "lich"):
        # Conjuração (tools/animar_pose.py): recolhe, carrega com brilho e lança para a frente.
        # Lich: alterna recolher/carregar no aviso do tiro. Espírito: carrega no alerta, lança ao perseguir.
        if state == "skulls_tele":
            pose, ph = "attack", (int(t * 8) % 2 + 0.5) / 3
        elif state == "alert":
            pose, ph = "attack", 1.5 / 3
        elif state == "chase" or lean:
            pose, ph = "attack", 2.5 / 3
        else:
            pose, ph = "idle", t * 0.8
        quadro, pe = sprites.pose_anim(name, pose, ph)
        if quadro is not None:
            v = quadro
            if alpha < 255:
                v = quadro.copy()
                v.set_alpha(alpha)
            lift = round(math.sin(t * 2.5) * float_amp)
            sprites.blit_anchor(surf, v, x, foot_y + lift, pe, flip=facing < 0, white=white, scale=scale)
            return
    art = sprites.image("personagens", f"inimigo_{name}.png") if name in ("lobo", "goblin") else None
    if art is not None:
        # As vistas east usadas nestes arquivos já olham para a direita.
        pose_and_blit(art, facing < 0, scale)
        return
    if name in AS_CAST and name not in ("ladino", "cavaleiro_escudo"):
        from . import elenco
        pose = "attack" if lean else ("walk" if moving else "idle")
        arte_propria = {
            "comerciante": "px_comerciante", "ferreiro": "px_ferreira", "aldea": "px_aldea",
            "curandeira": "px_curandeira", "fazendeiro": "px_pescador", "bardo": "px_bardo",
            "estudioso": "px_estudioso", "velho": "px_anciao", "anciã": "px_ancia", "menino": "px_grumete",
        }
        estilo = arte_propria.get(name, AS_CAST[name])
        img = elenco.character(estilo, pose, (t * (1.6 if moving else 0.5)) % 1.0, facing)
        v = sprites.variant(img, False, white, scale)
        if alpha < 255:
            v = v.copy()
            v.set_alpha(alpha)
        lift = math.sin(t * 2.5) * float_amp
        surf.blit(v, v.get_rect(midbottom=(round(x), round(foot_y + 3 * scale + lift))))
        return
    if name in AS_SKELETON:
        fr = _skeleton_frame(AS_SKELETON[name], t, moving, lean)
        if fr is not None:
            sprites.blit_anchor(surf, fr, x, foot_y, SKELETON_ANCHOR, flip=facing < 0, white=white, scale=scale)
            return
    img, (ax, ay) = npc_frame(name)
    if img is None:
        return
    flip = facing > 0                      # os modelos olham para a esquerda
    pose_and_blit(img, flip, scale)


class _ModelMixin:
    model = ""
    float_amp = 0.0

    def draw(self, surf, cam_x, cam_y):
        t = pygame.time.get_ticks() / 1000.0 + (self.x % 97) * 0.1
        state = getattr(self, "state", "")
        if getattr(self, "telegraph", 0) > 0:
            state = "skulls_tele"
        lean = 10 if state in ("windup", "bash", "lunge", "charge") else 0
        warn = state in ("windup", "aim") and int(t * 16) % 2 == 0
        draw_model(surf, self.model, self.cx - cam_x, self.bottom - cam_y, t, self.direction,
                   abs(self.vx) > 20, self.flash > 0 or warn, lean, self.float_amp,
                   state=state, vy=getattr(self, "vy", 0.0), airborne=not getattr(self, "on_ground", True))
        if state == "alert":
            fr = sprites.effect("alerta")
            if fr:
                a = fr[int(self.timer * 20) % len(fr)]
                surf.blit(a, a.get_rect(midbottom=(round(self.cx - cam_x), round(self.top - 22 - cam_y))))
        self.draw_hp(surf, cam_x, cam_y)


class Wolf(_ModelMixin, Patroller):
    """Lobo da floresta: patrulha rápido."""
    model = "lobo"
    max_hp = E.PATROLLER_HP + 4

    def think(self, dt, room, player, ctx):
        if self.on_ground:
            if wall_ahead(self, room, self.direction) or not ground_ahead(self, room, self.direction):
                self.direction *= -1
        self.vx = approach(self.vx, self.direction * E.PATROLLER_SPEED * 2.0, 1600 * dt)


class Goblin(_ModelMixin, Chaser):
    model = "goblin"


class Mummy(_ModelMixin, Chaser):
    """Múmia do templo: mais lenta e resistente."""
    model = "mumia"
    max_hp = E.CHASER_HP + 6


class Imp(_ModelMixin, Flier):
    model = "diabrete"
    float_amp = 3.0


class Spirit(_ModelMixin, Flier):
    model = "espirito"
    hit_fx = "impacto_roxo"
    float_amp = 4.0


class Lich(_ModelMixin, Turret):
    model = "lich"
    hit_fx = "impacto_roxo"
    float_amp = 2.0


class DarkKnight(_ModelMixin, Shield):
    model = "cavaleiro_negro"


class Rat(Patroller):
    color = (150, 140, 146)

    def draw(self, surf, cam_x, cam_y):
        phase = (self.x * 0.05) % 1.0
        img = pixelart.rat(phase, self.direction)
        _blit_bottom(surf, img, self, cam_x, cam_y, white=self.flash > 0)
        self.draw_hp(surf, cam_x, cam_y)


class Gull(Flier):
    color = (236, 236, 240)

    def draw(self, surf, cam_x, cam_y):
        img = pixelart.gull(self.t * 1.6 % 1.0, self.direction)
        v = sprites.variant(img, False, self.flash > 0)
        surf.blit(v, v.get_rect(center=(round(self.cx - cam_x), round(self.cy - cam_y))))
        if self.state == "alert":
            fr = sprites.effect("alerta")
            if fr:
                a = fr[int(self.timer * 20) % len(fr)]
                surf.blit(a, a.get_rect(midbottom=(round(self.cx - cam_x), round(self.top - 4 - cam_y))))
        self.draw_hp(surf, cam_x, cam_y)


class Hench(_ModelMixin, Chaser):
    """Capanga do navio: ladino encapuzado (modelos da equipe)."""
    model = "ladino"


class TideSlime(Jumper):
    """Slime da maré amaldiçoada (slime.png: linha 0 parado, linha 2 salto)."""
    color = (70, 140, 230)
    hit_sound = "slime_hit"
    death_sound = "slime_death"

    def draw(self, surf, cam_x, cam_y):
        frames = sprites.grid("inimigos/slime.png", 48, 32)
        if not frames:
            return super().draw(surf, cam_x, cam_y)
        t = pygame.time.get_ticks() / 1000.0
        if self.state == "air":
            img = frames[12 + min(3, int((0.4 - min(0.4, abs(self.vy) / 1800)) * 10))]
        elif self.state == "crouch":
            img = frames[12]
        else:
            img = frames[int(t * 8) % 6]
        _blit_bottom(surf, img, self, cam_x, cam_y, white=self.flash > 0, flip=self.direction > 0)
        self.draw_hp(surf, cam_x, cam_y)


class Cannon(Turret):
    color = (90, 90, 100)

    def draw(self, surf, cam_x, cam_y):
        flash = self.telegraph > 0 and int(self.telegraph * 16) % 2 == 0
        img = pixelart.cannon(self.direction, flash)
        _blit_bottom(surf, img, self, cam_x, cam_y, white=self.flash > 0)
        self.draw_hp(surf, cam_x, cam_y)


class ShieldPirate(_ModelMixin, Shield):
    """Guarda de escudo do navio. O escudo desenhado no modelo bloqueia golpes rápidos de frente."""
    model = "cavaleiro_escudo"


class _ArmaMixin:
    """Atirador com a arma na mão e aviso de mira bem visível: linha pontilhada até onde vai o
    tiro (fica cheia quando a mira trava) e um anel que fecha na boca da arma até o disparo."""
    arma = "pistola"

    def draw(self, surf, cam_x, cam_y):
        t = pygame.time.get_ticks() / 1000.0 + (self.x % 97) * 0.1
        st = getattr(self, "state", "")
        d = self.direction
        draw_model(surf, self.model, self.cx - cam_x, self.bottom - cam_y, t, d, abs(self.vx) > 20,
                   self.flash > 0, 0, 0.0, state="", vy=getattr(self, "vy", 0.0),
                   airborne=not getattr(self, "on_ground", True))
        boca = (self.cx + d * 16 - cam_x, self.top + 12 - cam_y)
        if st == "aim":
            ax, ay = self.aim
            n = math.hypot(ax, ay) or 1.0
            ux, uy = ax / n, ay / n
            if ux * d < 0.2:                         # aviso sempre para o lado em que olha
                ux, uy = d * 1.0, 0.0
        elif st == "reload":
            ux, uy = d * 0.5, -0.86                  # arma para cima, recarregando
        else:
            ux, uy = d * 0.7, 0.7                    # arma baixa
        self._draw_arma(surf, boca, ux, uy, st, t)
        if st == "aim":
            self._draw_mira(surf, boca, ux, uy, t)
        self.draw_hp(surf, cam_x, cam_y)

    def _draw_arma(self, surf, boca, ux, uy, st, t):
        d = self.direction
        mao = (round(boca[0] - d * 7), round(boca[1] + 2))
        if self.arma == "pistola":
            ponta = (round(mao[0] + ux * 9), round(mao[1] + uy * 9))
            pygame.draw.line(surf, (20, 18, 24), mao, ponta, 4)                 # contorno
            pygame.draw.line(surf, (96, 98, 110), mao, ponta, 2)                # cano
            pygame.draw.line(surf, (96, 62, 38), mao, (mao[0] - d * 2, mao[1] + 4), 3)   # cabo
            if st == "reload" and int(t * 6) % 2 == 0:                          # fumacinha do cano
                pygame.draw.circle(surf, (150, 150, 160), (ponta[0] + d, ponta[1] - 4), 2, 1)
        else:
            # pedra pontuda: erguida acima da cabeça enquanto mira, na mão no resto do tempo
            if st == "aim":
                c = (round(boca[0] - d * 30), round(boca[1] - 16 + math.sin(t * 20)))   # braço para trás
                ombro = (round(boca[0] - d * 19), round(boca[1] - 7))
                pygame.draw.line(surf, (24, 20, 26), ombro, (c[0], c[1] + 3), 4)
                pygame.draw.line(surf, (126, 176, 66), ombro, (c[0], c[1] + 3), 2)
            else:
                c = (mao[0] + d * 2, mao[1] - 2)
            pygame.draw.polygon(surf, (24, 20, 26), [(c[0] - 5, c[1] + 3), (c[0], c[1] - 6), (c[0] + 5, c[1] + 3)])
            pygame.draw.polygon(surf, (140, 136, 130), [(c[0] - 3, c[1] + 2), (c[0], c[1] - 4), (c[0] + 3, c[1] + 2)])
            surf.set_at((c[0] - 1, c[1] - 2), (200, 196, 186))

    def _draw_mira(self, surf, boca, ux, uy, t):
        k = max(0.0, min(1.0, self.timer / E.GUNNER_AIM))
        travou = self.timer <= E.GUNNER_AIM_LOCK
        cor = (255, 70, 50) if travou else (255, 150, 60)
        comp = 120
        x0, y0 = boca
        passo = 6 if travou else 10
        fase = (t * 60) % passo
        dist = 6 + fase
        while dist < comp:                                   # pontilhado que corre para a frente
            px, py = round(x0 + ux * dist), round(y0 + uy * dist)
            pygame.draw.rect(surf, (30, 8, 10), (px - 1, py - 1, 3, 3))
            surf.set_at((px, py), cor)
            if travou:
                surf.set_at((px + 1, py), cor)
            dist += passo
        r = 3 + round(7 * k)                                 # anel que fecha até o tiro
        pygame.draw.circle(surf, (30, 8, 10), (round(x0), round(y0)), r + 1, 1)
        pygame.draw.circle(surf, cor, (round(x0), round(y0)), r, 1)
        if travou and int(t * 20) % 2 == 0:                  # brilho na boca: vai disparar
            pygame.draw.line(surf, (255, 240, 200), (x0 - 3, y0), (x0 + 3, y0))
            pygame.draw.line(surf, (255, 240, 200), (x0, y0 - 3), (x0, y0 + 3))


class PirateGunner(_ArmaMixin, _ModelMixin, Gunner):
    """Pistoleiro do navio: recua, mira e atira; recarrega parado."""
    model = "ladino"


class StoneThrower(_ArmaMixin, _ModelMixin, Gunner):
    """Goblin da ilha que atira pedras pontudas do mesmo jeito."""
    model = "goblin"
    shot_look = "espinho"
    arma = "pedra"


class Crate(Enemy):
    """Caixa de carga: quebra com um golpe e solta moedas."""
    color = (150, 104, 60)
    max_hp = 1
    drop = "crate"
    contact_damage = 0
    knockback_resist = 0.0

    def __init__(self, foot_x, foot_y):
        super().__init__(foot_x, foot_y, 28, 26)

    def draw(self, surf, cam_x, cam_y):
        _blit_bottom(surf, pixelart.crate(), self, cam_x, cam_y, white=self.flash > 0)


# mesma letra do mapa, visual e comportamento de acordo com a zona da sala
ZONE_TYPES = {
    "ilha": {"g": Wolf, "c": Goblin, "f": Imp, "a": StoneThrower},
    "ruínas": {"g": Wolf, "c": Goblin, "f": Imp, "s": DarkKnight, "a": StoneThrower},
    "templo": {"c": Mummy, "f": Spirit, "t": Lich, "s": DarkKnight, "a": StoneThrower},
}


TYPES = {"g": Rat, "f": Gull, "c": Hench, "j": TideSlime, "t": Cannon, "s": ShieldPirate, "k": Crate,
         "a": PirateGunner}
