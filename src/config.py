"""Parâmetros centrais do jogo.

Todos os valores de balanceamento e de "game feel" ficam aqui. Unidades:
distâncias em pixels, velocidades em px/s, acelerações em px/s², tempos em segundos.
"""


class Game:
    # nome ainda não definido pelo grupo: troque aqui quando decidirem
    TITLE = "Maré de Mentiras"
    SUBTITLE = "a maldição do Templo da Maré"
    CHAPTERS = {
        1: "Jantar no molhado em veneno",
        2: "O leme estranhamente destruído",
        3: "A carta de sumiço",
        4: "Desvio de rota premeditado",
        5: "O porto tempestuoso",
    }
    PROTAGONISTS = {
        # cores provisórias; os textos usam as formas de cada um
        "ele": {"label": "Ele", "body": (110, 210, 255), "cloak": (70, 64, 150), "hair": None,
                "o": "o", "feiticeiro": "feiticeiro", "passageiro": "passageiro", "bom": "bom"},
        "ela": {"label": "Ela", "body": (250, 170, 210), "cloak": (130, 56, 120), "hair": (90, 50, 40),
                "o": "a", "feiticeiro": "feiticeira", "passageiro": "passageira", "bom": "boa"},
    }
    DIFFICULTIES = {
        "facil": {"label": "Fácil", "hp_bonus": 2, "enemy_hp": 0.75,
                  "desc": "+2 corações. Inimigos e chefes com menos vida. Para curtir a história."},
        "normal": {"label": "Normal", "hp_bonus": 0, "enemy_hp": 1.0,
                   "desc": "O desafio pensado para o jogo."},
        "dificil": {"label": "Difícil", "hp_bonus": -1, "enemy_hp": 1.35,
                    "desc": "1 coração a menos. Inimigos e chefes bem mais resistentes."},
    }


class Audio:
    SFX_VOLUME = 0.55
    MUSIC_VOLUME = 0.32
    # ajuste fino por efeito (alguns arquivos vêm mais altos que outros)
    SFX_GAIN = {"checkpoint": 0.6, "buy": 0.6, "item": 0.7, "boss": 0.8, "ui_move": 0.6, "coin": 0.5}
    # música por tela/zona (arquivos em assets/music/)
    MUSIC = {
        "menu": "title_01.ogg",
        "boss": "dungeon_01.ogg",
        "ilha": "forest_01.ogg",
        "ruínas": "forest_01.ogg",
        "templo": "dungeon_01.ogg",
        "convés": "forest_01.ogg",
        "interior": "dungeon_01.ogg",
        "porão": "dungeon_01.ogg",
        "default": "dungeon_01.ogg",
    }


class Display:
    WIDTH = 960
    HEIGHT = 540
    TITLE = Game.TITLE
    FPS_CAP = 144           # limite de renderização; a física não depende disso
    SIM_HZ = 120            # passo fixo da simulação
    MAX_FRAME_DT = 0.1      # evita "espiral da morte" após travadas


class World:
    TILE = 32


class Physics:
    GRAVITY = 2600.0
    FALL_GRAVITY_MULT = 1.6     # queda mais rápida que a subida = salto menos "flutuante"
    APEX_GRAVITY_MULT = 0.6     # gravidade reduzida perto do ápice (segurando pulo)
    APEX_THRESHOLD = 70.0       # |vy| abaixo disto conta como ápice
    MAX_FALL_SPEED = 900.0
    MAX_STEP = 8.0              # deslocamento máximo por sub-passo (anti-túnel)
    CORNER_CORRECTION = 7       # px de tolerância ao bater a quina da cabeça no teto
    STEP_UP = 10                # px de tolerância ao bater de lado numa quina de chão


class Player:
    WIDTH = 22
    HEIGHT = 40
    MAX_HP = 5

    RUN_SPEED = 300.0
    GROUND_ACCEL = 3200.0
    GROUND_DECEL = 3600.0
    GROUND_TURN_ACCEL = 5200.0
    AIR_ACCEL = 2400.0
    AIR_DECEL = 1700.0
    AIR_TURN_ACCEL = 3600.0

    JUMP_VELOCITY = 820.0       # ~4 tiles segurando
    JUMP_CUT_MULT = 0.45        # soltar o pulo durante a subida multiplica vy por isto
    DROP_THROUGH_TIME = 0.2     # S numa plataforma de mão única: ignora plataformas por este tempo
    MIN_JUMP_HOLD = 0.05        # o corte só vale depois disto (toque rápido = pulinho útil)
    COYOTE_TIME = 0.10
    JUMP_BUFFER = 0.13

    MAX_JUMPS = 2               # 1 no chão + 1 no ar (pulo duplo)
    DOUBLE_JUMP_VELOCITY = 720.0  # ~3 tiles

    HURT_INVULN = 1.0
    HURT_LOCK = 0.20            # tempo sem controle após dano
    HURT_KNOCKBACK_X = 260.0
    HURT_KNOCKBACK_Y = 340.0

    HAZARD_DAMAGE = 1
    HAZARD_FREEZE = 0.35        # pausa curta antes de voltar ao último chão seguro


class Dash:
    SPEED = 950.0
    DURATION = 0.18
    COOLDOWN = 0.45
    END_SPEED_MULT = 0.55       # fração de RUN_SPEED mantida ao terminar o dash
    INVULNERABLE = True         # dash atravessa ataques
    AIR_DASHES = 1              # dashes por tempo no ar (recarrega ao tocar o chão)
    INPUT_BUFFER = 0.10
    GHOST_INTERVAL = 0.022


class AttackSpec:
    """Dados de um golpe. Hitbox relativa à frente do jogador."""

    def __init__(self, name, damage, windup, active, recovery, hit_w, hit_h,
                 hit_offset_x, hit_offset_y, knockback, knock_up, stun,
                 hitstop, shake, ground_move_mult, air_move_mult,
                 lunge=0.0, self_recoil=0.0):
        self.name = name
        self.damage = damage
        self.windup = windup
        self.active = active
        self.recovery = recovery
        self.hit_w = hit_w
        self.hit_h = hit_h
        self.hit_offset_x = hit_offset_x    # distância da borda frontal do corpo
        self.hit_offset_y = hit_offset_y    # deslocamento vertical a partir do centro
        self.knockback = knockback
        self.knock_up = knock_up
        self.stun = stun
        self.hitstop = hitstop
        self.shake = shake
        self.ground_move_mult = ground_move_mult
        self.air_move_mult = air_move_mult
        self.lunge = lunge
        self.self_recoil = self_recoil

    @property
    def total(self):
        return self.windup + self.active + self.recovery


class Combat:
    QUICK = AttackSpec(
        name="quick", damage=2,
        windup=0.04, active=0.09, recovery=0.13,
        hit_w=48, hit_h=36, hit_offset_x=-4, hit_offset_y=-2,
        knockback=200.0, knock_up=0.0, stun=0.12,
        hitstop=0.035, shake=0.0,
        ground_move_mult=0.85, air_move_mult=1.0,
        lunge=0.0, self_recoil=70.0,
    )
    HEAVY = AttackSpec(
        name="heavy", damage=5,
        windup=0.24, active=0.12, recovery=0.30,
        hit_w=72, hit_h=54, hit_offset_x=-6, hit_offset_y=-6,
        knockback=540.0, knock_up=220.0, stun=0.55,
        hitstop=0.085, shake=5.0,
        ground_move_mult=0.25, air_move_mult=0.6,
        lunge=260.0, self_recoil=0.0,
    )
    POGO_VELOCITY = 640.0       # quique ao acertar algo com golpe para baixo
    ATTACK_BUFFER = 0.16        # clique durante outro golpe fica guardado por este tempo
    PLAYER_PROJECTILE_PARRY = True  # golpes destroem projéteis inimigos


class Projectile:
    SPEED = 250.0
    DAMAGE = 1
    RADIUS = 6
    LIFETIME = 4.0
    MAX_ACTIVE = 16


class Enemies:
    CONTACT_KNOCKBACK_RESIST = 1.0

    PATROLLER_HP = 6
    PATROLLER_SPEED = 70.0
    PATROLLER_SIZE = (28, 26)
    PATROLLER_DAMAGE = 1

    CHASER_HP = 10
    CHASER_PATROL_SPEED = 55.0
    CHASER_SPEED = 165.0
    CHASER_ACCEL = 900.0
    CHASER_SIZE = (26, 34)
    CHASER_DAMAGE = 1
    CHASER_DETECT_RANGE = 300.0
    CHASER_LOSE_RANGE = 460.0
    CHASER_VERTICAL_RANGE = 110.0
    CHASER_ALERT_TIME = 0.40       # pausa com "!" antes de perseguir (telegrafia)
    CHASER_GIVE_UP_TIME = 1.2      # tempo fora das condições até desistir

    TURRET_HP = 6
    TURRET_SIZE = (26, 26)
    TURRET_RANGE = 440.0
    TURRET_COOLDOWN = 1.8
    TURRET_TELEGRAPH = 0.45

    FLIER_HP = 6
    FLIER_SIZE = (24, 20)
    FLIER_SPEED = 150.0
    FLIER_ACCEL = 420.0
    FLIER_DETECT_RANGE = 280.0
    FLIER_LOSE_RANGE = 460.0
    FLIER_ALERT_TIME = 0.35

    JUMPER_HP = 10
    JUMPER_SIZE = (28, 28)
    JUMPER_RANGE = 320.0
    JUMPER_COOLDOWN = 1.3
    JUMPER_TELEGRAPH = 0.35
    JUMPER_JUMP_VY = 720.0
    JUMPER_JUMP_VX = 230.0

    SHIELD_HP = 14
    SHIELD_SIZE = (30, 40)
    SHIELD_SPEED = 70.0
    SHIELD_RANGE = 300.0
    SHIELD_BASH_RANGE = 70.0
    SHIELD_BASH_WINDUP = 0.45
    SHIELD_BASH_SPEED = 330.0
    SHIELD_BASH_TIME = 0.25
    SHIELD_GUARD_BREAK = 1.2       # atordoamento quando o ataque pesado quebra a guarda
    SHIELD_BLOCK_RECOIL = 260.0    # empurrão no jogador quando o golpe é bloqueado

    KNOCKBACK_FRICTION = 1800.0

    # moedas que cada inimigo solta
    DROPS = {"crate": 3, "patroller": 4, "chaser": 8, "turret": 5, "flier": 5, "jumper": 7, "shield": 12, "guardian": 120}


class Boss:
    HP = 90
    SIZE = (56, 64)
    CONTACT_DAMAGE = 1
    TRIGGER_DISTANCE = 380.0       # distância do jogador que inicia a luta
    IDLE_TIME = (0.7, 1.0)
    CHARGE_TELEGRAPH = 0.55
    CHARGE_SPEED = 520.0
    WALL_STUN = 1.1                # janela de punição depois de bater na parede
    LEAP_TELEGRAPH = 0.38
    LEAP_VY = 900.0
    SPIT_TELEGRAPH = 0.42
    SHOCKWAVE_SPEED = 300.0
    PHASE2_HP = 0.5                # abaixo desta fração fica mais agressivo
    PHASE2_SPEED = 1.25


class Energy:
    MAX = 99
    PER_HIT_QUICK = 11
    PER_HIT_HEAVY = 16
    HEAL_COST = 33
    HEAL_TIME = 0.9                # segurar F por este tempo cura 1 de vida
    HEAL_AMOUNT = 1


class Economy:
    PICKUP_MAGNET = 46.0           # raio em que moedas próximas voam até o jogador
    CHARM_MAGNET = 190.0           # raio com o amuleto Ímã
    COIN_LIFETIME = 40.0


class Progression:
    BASE_HP = 5
    FRAGMENTS_PER_HP = 4
    BASE_NOTCHES = 3
    # nível da arma: (preço em moedas, minérios necessários)
    WEAPON_UPGRADES = [(100, 0), (250, 1), (450, 2)]
    QUICK_DAMAGE_PER_LEVEL = 1
    HEAVY_DAMAGE_PER_LEVEL = 2
    START_ABILITIES = ()           # dash e pulo duplo são encontrados no mapa


class Camera:
    FOLLOW_SHARPNESS_X = 9.0
    FOLLOW_SHARPNESS_Y = 6.0
    LOOKAHEAD_X = 70.0
    LOOKAHEAD_SHARPNESS = 3.0
    VERTICAL_OFFSET = -30.0     # mostra um pouco mais acima do jogador


class Effects:
    ENABLE_SHAKE = True
    ENABLE_HITSTOP = True
    SHAKE_DECAY = 28.0          # px/s de redução da intensidade
    MAX_PARTICLES = 700
    HURT_HITSTOP = 0.06
    HURT_SHAKE = 6.0
    ROOM_FADE = 0.22


class Colors:
    BG = (18, 20, 30)
    BG_FAR = (26, 29, 44)
    TILE = (58, 64, 92)
    TILE_EDGE = (98, 108, 150)
    ONEWAY = (140, 112, 78)
    SPIKE = (210, 70, 80)
    CHECKPOINT = (90, 200, 160)
    CHECKPOINT_OFF = (70, 90, 100)

    PLAYER = (110, 210, 255)
    PLAYER_DASH = (180, 240, 255)
    PLAYER_HEAVY_CHARGE = (255, 170, 60)
    PLAYER_HURT = (255, 255, 255)

    QUICK_SLASH = (240, 245, 255)
    HEAVY_SLASH = (255, 180, 70)

    PATROLLER = (220, 120, 90)
    CHASER = (200, 90, 200)
    CHASER_ALERT = (255, 230, 90)
    TURRET = (150, 170, 90)
    PROJECTILE = (255, 120, 60)

    COIN = (255, 210, 90)
    ENERGY = (200, 220, 255)
    BENCH = (150, 120, 90)
    NPC_SHOP = (240, 200, 120)
    NPC_SMITH = (200, 140, 110)
    ITEM = (255, 240, 160)
    CHEST = (180, 130, 60)
    BREAKABLE = (70, 74, 100)
    GATE = (150, 150, 170)
    FLIER = (120, 200, 140)
    JUMPER = (230, 170, 80)
    SHIELD = (150, 160, 200)
    GUARDIAN = (210, 80, 70)

    UI_TEXT = (230, 232, 240)
    UI_DIM = (120, 125, 145)
    UI_ACCENT = (110, 210, 255)
    HP_FULL = (240, 80, 100)
    HP_EMPTY = (70, 40, 55)


# Paleta provisória por zona: (fundo, fundo distante, tile, borda do tile)
ZONE_PALETTES = {
    "cavernas": ((18, 20, 30), (26, 29, 44), (58, 64, 92), (98, 108, 150)),
    "vila": ((24, 20, 26), (36, 30, 38), (78, 66, 70), (132, 112, 104)),
    "arena": ((28, 16, 18), (42, 24, 26), (84, 52, 56), (150, 90, 90)),
    "jardins": ((14, 24, 20), (22, 36, 30), (48, 78, 62), (96, 150, 110)),
    "alturas": ((22, 22, 36), (34, 34, 56), (80, 82, 120), (150, 150, 200)),
    # navio (capítulo 1)
    "convés": ((10, 14, 30), (20, 28, 50), (96, 66, 44), (156, 114, 72)),
    "interior": ((30, 22, 18), (44, 32, 26), (82, 58, 42), (142, 102, 66)),
    "porão": ((12, 14, 18), (22, 24, 30), (56, 48, 42), (98, 86, 72)),
    "ilha": ((10, 14, 26), (30, 44, 62), (70, 90, 60), (120, 170, 90)),
    "ruínas": ((12, 12, 24), (40, 40, 64), (90, 90, 100), (150, 150, 170)),
    "templo": ((10, 14, 16), (30, 40, 44), (60, 80, 84), (120, 150, 150)),
}
