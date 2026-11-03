"""Estados do jogo: menu, partida, pausa/inventário, mapa, banco, loja, mensagem e morte."""

import math
import random

import pygame

from . import ui
from . import tiles as tiles_mod
from .background import Background
from .bosses import BOSS_CLASSES
from .creatures import TYPES as CREATURE_TYPES, ZONE_TYPES
from .movers import Mover
from .physics import move_and_collide, tile_span
from .camera import Camera
from .combat import ProjectileSystem, resolve_player_attack
from .config import Audio as AudioCfg, Boss as BossCfg, Colors, Display, Effects as FX, Enemies as EN, Game, Player as PCfg, World
from .effects import EffectSystem
from .enemies import spawn_enemies
from .objects import Bench, Character, CoinBag, ItemPickup, NPC, Speaker, draw_character, draw_portrait, spawn_coins
from .physics import is_supported, rects_overlap
from .player import Player
from .progress import CHARMS, SHOP_STOCK, Progress
from .world import BOSS_LOCK, BREAKABLE, CRUMBLE, FIGHT_GATE, LOCKED, WorldMap

T = World.TILE
SIM_DT = 1.0 / Display.SIM_HZ


class State:
    def __init__(self, app):
        self.app = app

    def frame(self, dt, inp):
        pass

    def draw(self, surf):
        pass


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
class PlayState(State):
    """Partida em andamento. Física em passo fixo (SIM_HZ)."""

    def __init__(self, app, progress=None):
        super().__init__(app)
        self.audio = app.audio
        self.progress = progress if progress is not None else Progress()
        self.world = WorldMap(chapter=self.progress.chapter)
        self.story = None
        if self.progress.chapter == 1:
            from . import chapter1
            self.story = chapter1
            self.progress.abilities |= set(chapter1.START_ABILITIES)   # o dash já vem desde o começo
        self._apply_progress_to_world()
        self.effects = EffectSystem()
        self.projectiles = ProjectileSystem()
        self.camera = Camera()
        room, x, y = self._spawn_point()
        self.player = Player(x, y, self.progress)
        self.last_safe = (room.id, x, y)
        self.accumulator = 0.0
        self.hazard_timer = 0.0
        self.fade = 0.0
        self.room_name_timer = 0.0
        self.death_timer = 0.0
        self.debug = False
        self.time = 0.0
        self.room = None
        self.riding = None              # plataforma móvel em que o jogador está
        self.mover_ignore = 0.0
        self.pending_after_boss = None  # (segundos, dados do chefe) para as falas pós-luta
        self.load_room(room)
        self.camera.snap(self.player, self.room)

    # --- progresso <-> mundo ---
    def _apply_progress_to_world(self):
        for key in self.progress.broken:
            rid, tx, ty = key.split(":")
            if rid in self.world.rooms:
                self.world.rooms[rid].broken.add((int(tx), int(ty)))
        for rid in self.progress.bosses:
            if rid in self.world.rooms:
                self.world.rooms[rid].boss_defeated = True
        for room in self.world.rooms.values():
            room.door_unlocked = room.key is not None and room.key in self.progress.flags

    def _spawn_point(self):
        bench = self.progress.bench
        if bench and bench[0] in self.world.rooms:
            return self.world.rooms[bench[0]], bench[1], bench[2]
        return self.world.player_start()

    def save(self):
        self.progress.save(self.app.save_path)

    # --- salas ---
    def load_room(self, room):
        self.room = room
        room.fight_active = False
        self.progress.visited.add(room.id)
        self.enemies = self._spawn_enemies(room)
        self.boss = next((e for e in self.enemies if e.is_boss), None)
        if self.boss is not None and hasattr(self.boss, "setup"):
            self.boss.setup(room)
        self.spawn_queue = []
        self.hazards = []
        self.movers = [Mover(m) for m in room.movers]
        self.riding = None
        self.crumble_timers = {}
        self.items = []
        self.interactables = []
        for spawn in room.spawns:
            kind, x, y = spawn[0], spawn[1], spawn[2]
            if kind == "*":
                idx = spawn[3]
                item_kind, arg = room.items[idx]
                if f"{room.id}:{idx}" not in self.progress.collected:
                    self.items.append(ItemPickup(room.id, idx, item_kind, arg, x, y))
            elif kind == "B":
                bench = Bench(x, y)
                if self.story is not None:
                    bench.prompt = "Descansar (salvar)"
                self.interactables.append(bench)
            elif kind == "N" and self.story is not None:
                cid = room.npcs[spawn[3]]
                self.interactables.append(Character(x, y, cid, self.story.CHARACTERS[cid]))
            elif kind == "$":
                self.interactables.append(NPC(x, y, "shop"))
            elif kind == "R":
                self.interactables.append(NPC(x, y, "smith"))
        self._spawn_boss_reward(room)
        bag = self.progress.bag
        self.bag = CoinBag(bag[1], bag[2], bag[3]) if bag and bag[0] == room.id else None
        self.coins = []
        self.projectiles.clear()
        self.effects.clear()
        self.room_surface = self._render_room(room)
        self.background = Background(room)
        self.water_tiles = room.tiles_of({"~"})
        self.room_name_timer = 1.8
        self.fade = FX.ROOM_FADE
        self.audio.play_music(AudioCfg.MUSIC.get(room.zone, AudioCfg.MUSIC["default"]))

    def _spawn_enemies(self, room):
        if self.story is None:
            return spawn_enemies(room, room.boss_defeated)
        mult = Game.DIFFICULTIES.get(self.progress.difficulty, {}).get("enemy_hp", 1.0)
        out = []
        for spawn in room.spawns:
            kind, x, y = spawn[0], spawn[1], spawn[2]
            if kind == "G":
                if room.boss and not room.boss_defeated:
                    out.append(BOSS_CLASSES[room.boss](x, y))
            elif kind in CREATURE_TYPES:
                cls = ZONE_TYPES.get(room.zone, {}).get(kind, CREATURE_TYPES[kind])
                out.append(cls(x, y))
        for e in out:
            if e.max_hp > 1:
                e.max_hp = e.hp = max(1, round(e.max_hp * mult))
        return out

    def spawn_enemy(self, enemy):
        """Inimigos criados durante a luta (ex.: ratos do Rei dos Ratos)."""
        self.spawn_queue.append(enemy)

    def _boss_info(self, room):
        if self.story is None or not room.boss:
            return None
        return self.story.BOSSES.get(room.boss)

    def _spawn_boss_reward(self, room):
        info = self._boss_info(room)
        if not info or not room.boss_defeated or not info.get("reward"):
            return
        key = f"{room.id}:boss"
        if key in self.progress.collected:
            return
        kind, arg = info["reward"]
        floor_y = self._floor_below(room.width / 2, room.height / 2)
        item = ItemPickup(room.id, "boss", kind, arg, room.width / 2, floor_y)
        self.items.append(item)

    def _floor_below(self, x, y):
        tx = int(x // T)
        for ty in range(int(y // T), self.room.rows_count):
            if self.room.is_solid(tx, ty):
                return ty * T
        return self.room.height - T

    def _check_transition(self):
        p = self.player
        room = self.room
        if 0 <= p.cx < room.width and 0 <= p.cy < room.height:
            return
        if p.cx < 0:
            side, coord = "W", int(p.cy // T)
        elif p.cx >= room.width:
            side, coord = "E", int(p.cy // T)
        elif p.cy < 0:
            side, coord = "N", int(p.cx // T)
        else:
            side, coord = "S", int(p.cx // T)
        door = room.door_at_exit(side, coord)
        target = self.world.target_of(room.id, door.digit) if door else None
        if target is None:
            if side == "S":
                self._hazard_hit()
            else:
                p.x = min(max(p.x, 0.0), room.width - p.w)
                p.y = max(p.y, 0.0)
            return
        new_room = self.world.rooms[target[0]]
        nd = new_room.doors[target[1]]
        if side in ("W", "E"):
            from_bottom = (door.hi + 1) * T - p.bottom
            p.y = (nd.hi + 1) * T - from_bottom - p.h
            p.x = new_room.width - p.w - 1 if side == "W" else 1.0
        else:
            p.x = nd.lo * T + (p.x - door.lo * T)
            if side == "N":
                p.y = new_room.height - p.h - 1
                p.vy = min(p.vy, -PCfg.JUMP_VELOCITY)   # empurrão para alcançar o chão de cima
            else:
                p.y = 1.0
        self.load_room(new_room)
        self.camera.snap(p, self.room)

    # --- loop ---
    def frame(self, dt, inp):
        if inp.was_pressed("debug"):
            self.debug = not self.debug
            inp.pressed.discard("debug")
        if inp.was_pressed("mute"):
            self.app.audio.toggle_mute()
            inp.pressed.discard("mute")
        if self.player.alive and self.hazard_timer <= 0:
            if inp.was_pressed("pause"):
                inp.consume()
                self.app.push(PauseState(self.app, self))
                return
            if inp.was_pressed("map"):
                inp.consume()
                self.app.push(MapState(self.app, self))
                return
        self.accumulator += dt
        while self.accumulator >= SIM_DT:
            self.accumulator -= SIM_DT
            if self.fixed_update(SIM_DT, inp):
                inp.consume()
            if self.app.state is not self:
                self.accumulator = 0.0
                return
        if not self.player.alive:
            self.death_timer += dt
            if self.death_timer > 1.4:
                self.app.push(DeathState(self.app, self))

    def fixed_update(self, dt, inp):
        """Um passo de simulação. Retorna True se a entrada foi lida."""
        self.time += dt
        fx = self.effects
        fx.update_timers(dt)
        self.fade = max(0.0, self.fade - dt)
        self.room_name_timer = max(0.0, self.room_name_timer - dt)
        if fx.hitstop > 0:
            fx.hitstop -= dt
            return False
        if self.hazard_timer > 0:
            self.hazard_timer -= dt
            fx.update(dt)
            if self.hazard_timer <= 0:
                self._respawn_at_safe()
            return True   # descarta comandos dados durante a pausa do espinho

        p = self.player
        if p.alive:
            self.progress.play_time += dt
        if p.alive and inp.was_pressed("interact") and p.on_ground and not p.dashing:
            if self._interact():
                return True
        # plataformas móveis: andam primeiro e carregam quem está em cima
        for m in self.movers:
            m.update(dt)
        if self.riding is not None:
            move_and_collide(p, self.riding.dx, self.riding.dy if self.riding.dy > 0 else 0, self.room)
            if self.riding.dy < 0:
                p.y += self.riding.dy
            if inp.was_pressed("down"):
                self.riding = None
                self.mover_ignore = 0.25
        self.mover_ignore = max(0.0, self.mover_ignore - dt)
        prev_bottom = p.bottom
        p.update(dt, inp, self.room, self)
        self._land_on_movers(prev_bottom)
        self._update_crumble(dt)
        self._update_boss_fight()
        for e in self.enemies:
            e.update(dt, self.room, p, self)
        if self.spawn_queue:
            self.enemies.extend(self.spawn_queue)
            self.spawn_queue = []
        self.hazards = [h for h in self.hazards if h.update(dt, self.room, p, self)]
        if self.pending_after_boss is not None:
            t, info = self.pending_after_boss
            t -= dt
            if t <= 0:
                self.pending_after_boss = None
                self._after_boss(info)
            else:
                self.pending_after_boss = (t, info)
        self.projectiles.update(dt, self.room, p, self)
        for c in self.coins:
            c.update(dt, self.room, p, p.magnet)

        if p.alive:
            resolve_player_attack(p, self.enemies, self.projectiles, self)
            for e in self.enemies:
                if not e.alive or not e.contact_damage or (e.is_boss and not e.awake):
                    continue
                if p.overlaps(e):
                    p.take_hit(e.contact_damage, e.cx, self)
            self._collect()
            self._check_hazards()
            self._check_transition()
            self._update_safe_spot()
        self.enemies = [e for e in self.enemies if e.alive]
        self.coins = [c for c in self.coins if c.alive]
        fx.update(dt)
        self.background.update(dt, self.camera.render_offset((0, 0)))
        self.camera.update(dt, p, self.room)
        return True

    # --- plataformas móveis e tábuas que desabam ---
    def _land_on_movers(self, prev_bottom):
        p = self.player
        if not p.alive or not self.movers:
            return
        if self.riding is not None:
            m = self.riding
            on_top = p.right > m.x + 2 and p.left < m.x + m.w - 2 and abs(p.bottom - m.y) <= 6
            if p.vy < 0 or not on_top:
                self.riding = None
            else:
                p.y = m.y - p.h
                p.land_on_platform(self)
                return
        if p.vy < 0 or self.mover_ignore > 0:
            return
        for m in self.movers:
            if p.right > m.x + 2 and p.left < m.x + m.w - 2 and prev_bottom <= m.y + 4 + max(0.0, -m.dy) \
                    and p.bottom >= m.y:
                p.y = m.y - p.h
                p.land_on_platform(self)
                self.riding = m
                return

    def _update_crumble(self, dt):
        room = self.room
        p = self.player
        if p.alive and p.on_ground and self.riding is None:
            ty = int((p.bottom + 1) // T)
            x0, x1 = tile_span(p.x, p.w)
            for tx in range(x0, x1 + 1):
                if room.tile(tx, ty) == CRUMBLE and (tx, ty) not in room.crumbled \
                        and (tx, ty) not in self.crumble_timers:
                    self.crumble_timers[(tx, ty)] = 0.45
                    self.audio.play("impact")
        for key in list(self.crumble_timers):
            self.crumble_timers[key] -= dt
            if self.crumble_timers[key] <= 0:
                del self.crumble_timers[key]
                room.crumbled[key] = 2.8
                tx, ty = key
                self.effects.burst(tx * T + 16, ty * T + 6, 10, (150, 104, 60), speed=(40, 160), gravity=700)
        for key in list(room.crumbled):
            room.crumbled[key] -= dt
            if room.crumbled[key] <= 0:
                tx, ty = key
                if not rects_overlap((tx * T, ty * T, T, T), p.rect_tuple()):
                    del room.crumbled[key]

    # --- chefe ---
    def _update_boss_fight(self):
        boss = self.boss
        room = self.room
        if boss is None or room.boss_defeated:
            return
        p = self.player
        if not boss.awake and p.alive and abs(p.cx - boss.cx) < BossCfg.TRIGGER_DISTANCE:
            boss.wake()
            room.fight_active = True
            self.effects.add_shake(6)
            self.audio.play("boss")
            self.audio.play_music(AudioCfg.MUSIC["boss"])
            info = self._boss_info(room)
            if info is not None:
                self.app.push(BossIntroState(self.app, self, boss, info))
            # empurra o jogador para fora do portão que fechou
            for tx, ty in room.tiles_of(FIGHT_GATE):
                gx = tx * T
                if p.right > gx and p.left < gx + T:
                    p.x = gx - p.w - 1 if p.cx < gx + T / 2 else gx + T + 1

    def on_enemy_killed(self, enemy):
        value = EN.DROPS.get(enemy.drop, 0)
        spawn_coins(self.coins, enemy.cx, enemy.cy, value)
        if enemy.is_boss:
            room = self.room
            room.boss_defeated = True
            room.fight_active = False
            self.progress.bosses.add(room.id)
            self.effects.add_shake(12)
            self.effects.flash(0.3, (255, 240, 200))
            self.hazards = []
            self.projectiles.clear()
            for e in self.enemies:
                if e is not enemy:
                    e.hp = 0
                    e.alive = False
            info = self._boss_info(room)
            if info is None:
                self.save()
                self.app.push(MessageState(self.app, self, "Guardião derrotado", "O caminho a oeste está aberto."))
                return
            self._spawn_boss_reward(room)
            flag = info.get("flag")
            if flag:
                self.progress.flags.add(flag)
                for r in self.world.rooms.values():
                    if r.key == flag:
                        r.door_unlocked = True
            self.save()
            self.pending_after_boss = (1.3, info)

    def _after_boss(self, info):
        """Falas do chefe derrotado; no chefe final, vai para o desfecho."""
        if self.room.boss == "feiticeiro":
            self.app.push(EndingState(self.app, self))
            return
        speaker = Speaker(info["speaker"], self._speaker_name(info["speaker"]))
        lines = [line.format(**self.forms()) for line in info.get("after", [])]
        flag = info.get("flag")

        def done():
            msg = getattr(self.story, "FLAG_MESSAGES", {}).get(flag) if flag else None
            if msg:
                self.app.push(MessageState(self.app, self, *msg))

        if lines:
            self.app.push(DialogState(self.app, self, speaker, lines, done))
        else:
            done()

    def _speaker_name(self, style):
        return {"grumete": "Tico, o grumete", "imediato": "Aldric, o imediato", "irma": "Selka, irmã da capitã",
                "amigo": "Caelum"}.get(style, style)

    def break_tile(self, tx, ty):
        self.room.broken.add((tx, ty))
        self.progress.broken.add(f"{self.room.id}:{tx}:{ty}")
        self.effects.burst(tx * T + T / 2, ty * T + T / 2, 16, self.room.palette[3], speed=(80, 280), gravity=700)
        self.effects.add_shake(4)
        self.audio.play("impact")
        self.save()

    # --- coleta / interação ---
    def _collect(self):
        p = self.player
        prect = p.rect_tuple()
        for c in self.coins:
            if c.alive and rects_overlap(prect, c.rect_tuple()):
                c.alive = False
                self.progress.coins += c.value
                self.audio.play("coin")
        for item in self.items:
            if item.alive and rects_overlap(prect, item.rect()):
                item.alive = False
                self._give_item(item)
        self.items = [i for i in self.items if i.alive]
        if self.bag and rects_overlap(prect, self.bag.rect()):
            self.progress.coins += self.bag.amount
            self.effects.burst(self.bag.x, self.bag.y - 14, 20, Colors.COIN, speed=(60, 220))
            self.audio.play("coin")
            self.bag = None
            self.progress.bag = None
            self.save()

    def _give_item(self, item):
        pr = self.progress
        pr.collected.add(item.key)
        if item.kind == "food":
            p = self.player
            p.hp = min(p.max_hp, p.hp + 2)
            self.effects.sprite("coracoes", p.cx, p.cy - 10, fps=20)
            self.audio.play("heal")
            self.save()
            return
        if item.kind == "letter":
            pr.letters.add(item.arg)
            self.effects.sprite("brilho", item.x, item.y - 20, fps=18, scale=2)
            self.audio.play("item")
            self.save()
            title, body = self.story.LETTERS[item.arg]
            self.app.push(MessageState(self.app, self, title, body))
            return
        old_max = self.player.max_hp
        msg = pr.give(item.kind, item.arg)
        self.player.recompute_stats()
        if self.player.max_hp > old_max:
            self.player.hp = self.player.max_hp
        self.effects.burst(item.x, item.y - 20, 24, Colors.ITEM, speed=(60, 260), gravity=-50)
        self.audio.play("item")
        self.save()
        if msg:
            self.app.push(MessageState(self.app, self, *msg))

    def nearby_interactable(self):
        for obj in self.interactables:
            if obj.near(self.player):
                return obj
        return None

    def _interact(self):
        obj = self.nearby_interactable()
        if obj is None:
            return False
        if obj.kind == "bench":
            self.rest_at_bench(obj)
            self.app.push(BenchState(self.app, self))
        elif obj.kind == "shop":
            self.app.push(ShopState(self.app, self, "shop"))
        elif obj.kind == "smith":
            self.app.push(ShopState(self.app, self, "smith"))
        elif obj.kind == "talk":
            self.talk_to(obj)
        return True

    # --- história ---
    def forms(self):
        p = Game.PROTAGONISTS[self.progress.protagonist]
        f = {k: p[k] for k in ("o", "feiticeiro", "passageiro", "bom")}
        f["Feiticeiro"] = p["feiticeiro"].capitalize()
        return f

    def talk_to(self, character):
        cid = character.char_id
        dialog = self.story.DIALOGS[cid]
        first = cid not in self.progress.talked
        lines = [line.format(**self.forms()) for line in (dialog["first"] if first else dialog["repeat"])]

        def done():
            self.progress.talked.add(cid)
            flag = dialog.get("on_first")
            if first and flag:
                self.give_flag(flag)
            else:
                self.save()

        self.app.push(DialogState(self.app, self, character, lines, done))

    def give_flag(self, flag):
        if flag in self.progress.flags:
            return
        self.progress.flags.add(flag)
        for room in self.world.rooms.values():
            if room.key == flag:
                room.door_unlocked = True
        self.audio.play("item")
        self.save()
        msg = getattr(self.story, "FLAG_MESSAGES", {}).get(flag)
        if msg:
            self.app.push(MessageState(self.app, self, *msg))

    def rest_at_bench(self, bench):
        p = self.player
        p.place(bench.x, bench.y)
        p.recompute_stats()
        p.hp = p.max_hp
        p.attack = None
        p.attack_buffer = None
        self.progress.bench = (self.room.id, bench.x, bench.y)
        self.last_safe = self.progress.bench
        # descansar traz os inimigos da sala de volta
        self.enemies = self._spawn_enemies(self.room)   # mesmas criaturas da sala (não os blocos genéricos)
        self.boss = next((e for e in self.enemies if e.is_boss), None)
        self.projectiles.clear()
        self.effects.ring(bench.x, bench.y - 16, 60, 0.5, Colors.ENERGY, 3)
        self.audio.play("checkpoint")
        self.save()

    # --- perigos / segurança ---
    def _check_hazards(self):
        p = self.player
        for r in self.room.spike_rects(p.left, p.top, p.right, p.bottom):
            if rects_overlap(p.rect_tuple(), r):
                self._hazard_hit()
                return

    def _hazard_hit(self):
        p = self.player
        if self.hazard_timer > 0 or not p.alive:
            return
        p.hp -= PCfg.HAZARD_DAMAGE
        p.heal_timer = 0.0
        self.effects.burst(p.cx, p.cy, 18, (255, 90, 110), speed=(80, 280))
        self.effects.flash(0.15, (255, 60, 80))
        self.effects.add_shake(FX.HURT_SHAKE)
        self.audio.play("hurt")
        if p.hp <= 0:
            p.die(self)
            return
        self.hazard_timer = PCfg.HAZARD_FREEZE

    def _respawn_at_safe(self):
        """Depois de cair em água ou espinhos, volta sempre ao último checkpoint (bola de cristal).
        Voltar ao "último chão firme" podia cair numa tábua ou plataforma que já não estava lá e
        prender a jogadora num loop de quedas."""
        room, x, y = self._spawn_point()
        p = self.player
        if room is not self.room:
            p.place(x, y)
            self.load_room(room)
        p.place(x, y)
        p.vx = p.vy = 0.0
        p.dash_time = 0.0
        p.attack = None
        p.attack_buffer = None
        p.invuln = PCfg.HURT_INVULN
        self.fade = FX.ROOM_FADE
        self.camera.snap(p, self.room)

    def _update_safe_spot(self):
        p = self.player
        if not p.on_ground or p.hurt_lock > 0 or p.dashing or not is_supported(p, self.room):
            return
        if self.room.fight_active:
            return
        ty = int((p.bottom - 1) // T)
        for tx in range(int(p.left // T) - 1, int(p.right // T) + 2):
            if self.room.is_spike(tx, ty) or self.room.is_spike(tx, ty + 1):
                return
        # exige um pouco de chão além dos pés, para não reaparecer na beirada
        ty_floor = int(p.bottom // T)
        for fx in (p.left - 8, p.right + 8):
            tx = int(fx // T)
            if not (self.room.is_solid(tx, ty_floor) or self.room.is_oneway(tx, ty_floor)):
                return
        self.last_safe = (self.room.id, p.cx, p.bottom)

    # --- morte ---
    def on_player_death(self):
        """Chamado pelo jogador ao morrer: moedas ficam numa bolsa no último chão seguro."""
        pr = self.progress
        pr.deaths += 1
        if pr.coins > 0:
            room_id, x, y = self.last_safe
            pr.bag = (room_id, x, y, pr.coins)
            pr.coins = 0
        self.save()

    def respawn_at_bench(self):
        room, x, y = self._spawn_point()
        p = self.player
        p.recompute_stats()
        p.reset_state()
        p.place(x, y)
        self.last_safe = (room.id, x, y)
        self.hazard_timer = 0.0
        self.death_timer = 0.0
        self.accumulator = 0.0
        self.load_room(room)
        self.camera.snap(p, self.room)

    # --- desenho ---
    def _render_room(self, room):
        """Pré-desenha os blocos fixos da sala numa imagem (com o tema da zona)."""
        surf = pygame.Surface((room.width, room.height), pygame.SRCALPHA)
        ts = tiles_mod.tileset(tiles_mod.theme_of(room.zone))
        shadow = (0, 0, 0, 90)
        for ty in range(room.rows_count):
            for tx in range(room.cols):
                ch = room.tile(tx, ty)
                x, y = tx * T, ty * T
                if ch == "#":
                    open_above = room.tile(tx, ty - 1) not in ("#", None, "X")
                    surf.blit(tiles_mod.solid_tile(ts, room, tx, ty), (x, y))
                    # sombra nas bordas laterais e de baixo expostas (dá volume)
                    if room.tile(tx - 1, ty) not in ("#", None, "X"):
                        pygame.draw.rect(surf, (0, 0, 0, 70), (x, y, 3, T))
                    if room.tile(tx + 1, ty) not in ("#", None, "X"):
                        pygame.draw.rect(surf, (0, 0, 0, 70), (x + T - 3, y, 3, T))
                    if room.tile(tx, ty + 1) not in ("#", None, "X"):
                        pygame.draw.rect(surf, shadow, (x, y + T - 4, T, 4))
                    self._tile_detail(surf, room, tx, ty, x, y, open_above)
                elif ch == "-":
                    surf.blit(ts["oneway"], (x, y))
                elif ch == "^":
                    surf.blit(ts["spike"], (x, y))
        return surf

    def _tile_detail(self, surf, room, tx, ty, x, y, open_above):
        """Acabamento dos blocos: luz no topo, cantos gastos, pedras, rachaduras e raízes."""
        theme = tiles_mod.theme_of(room.zone)
        h = (tx * 73856093 ^ ty * 19349663) & 0xFFFF          # aleatório fixo por bloco
        solid = lambda a, b: room.tile(a, b) in ("#", None, "X")
        left_open, right_open = not solid(tx - 1, ty), not solid(tx + 1, ty)
        if open_above:
            pygame.draw.line(surf, (255, 255, 255, 40), (x, y), (x + T - 1, y))
            for corner_x, is_open in ((x, left_open), (x + T - 2, right_open)):
                if is_open:                                    # canto gasto
                    surf.fill((0, 0, 0, 0), (corner_x, y, 2, 2))
        if not open_above and theme in ("island", "ruins", "temple", "hull", "bilge"):
            if h % 7 == 0:                                     # pedra encravada
                cx, cy = x + 6 + h % 18, y + 8 + (h >> 4) % 14
                pygame.draw.ellipse(surf, (0, 0, 0, 60), (cx - 4, cy - 2, 9, 6))
                pygame.draw.ellipse(surf, (255, 255, 255, 34), (cx - 3, cy - 3, 6, 3))
            elif h % 11 == 0:                                  # rachadura
                cx, cy = x + 4 + h % 20, y + 4 + (h >> 3) % 16
                pygame.draw.lines(surf, (0, 0, 0, 80), False,
                                  [(cx, cy), (cx + 4, cy + 3), (cx + 3, cy + 7), (cx + 7, cy + 10)], 1)
        if theme == "island" and not solid(tx, ty + 1) and h % 3 == 0:
            for k in range(2):                                 # raízes penduradas embaixo
                rx = x + 6 + k * 12 + h % 5
                ln = 4 + (h >> (k + 2)) % 9
                pygame.draw.line(surf, (70, 50, 34, 220), (rx, y + T), (rx + (k * 2 - 1), y + T + ln), 1)

    def _draw_water(self, surf, cam_x, cam_y):
        """Água animada (tiles ~): superfície com ondas e brilho."""
        t = self.time
        for tx, ty in self.water_tiles:
            x, y = tx * T - cam_x, ty * T - cam_y
            if x < -T or x > Display.WIDTH or y < -T or y > Display.HEIGHT:
                continue
            top_open = self.room.tile(tx, ty - 1) != "~"
            body = pygame.Surface((T, T), pygame.SRCALPHA)
            body.fill((28, 76, 120, 200))
            if top_open:
                off = int(3 + 2 * math.sin(t * 3 + tx * 0.9))
                body.fill((0, 0, 0, 0), (0, 0, T, off))
                pygame.draw.line(body, (150, 210, 240, 255), (0, off), (T, off), 2)
                if int(t * 4 + tx) % 5 == 0:
                    body.set_at(((tx * 11 + int(t * 20)) % T, off + 3), (220, 240, 255, 255))
            surf.blit(body, (x, y))

    def _draw_dynamic_tiles(self, surf, cam_x, cam_y):
        room = self.room
        tile_col = room.palette[2]
        ts = tiles_mod.tileset(tiles_mod.theme_of(room.zone))
        for tx, ty in room.tiles_of({BREAKABLE, FIGHT_GATE, BOSS_LOCK, LOCKED, CRUMBLE}):
            if not room.is_solid(tx, ty):
                continue
            x, y = tx * T - cam_x, ty * T - cam_y
            ch = room.tile(tx, ty)
            if ch == CRUMBLE:
                shake = 0
                if (tx, ty) in self.crumble_timers:
                    shake = int(math.sin(self.time * 60 + tx) * 2)
                surf.blit(ts["crumble"], (x + shake, y))
                continue
            if ch == BREAKABLE:
                # quase igual à rocha: só uma rachadura sutil denuncia o segredo
                pygame.draw.rect(surf, tile_col, (x, y, T, T))
                c = tuple(max(0, v - 14) for v in tile_col)
                pygame.draw.line(surf, c, (x + 8, y + 6), (x + 16, y + 18), 2)
                pygame.draw.line(surf, c, (x + 16, y + 18), (x + 12, y + 28), 2)
            elif ch == LOCKED:
                # porta de madeira com fechadura
                pygame.draw.rect(surf, (110, 72, 44), (x, y, T, T))
                pygame.draw.rect(surf, (70, 44, 28), (x, y, T, T), 2)
                pygame.draw.circle(surf, (220, 190, 90), (x + T - 9, y + 16), 3)
            else:
                pygame.draw.rect(surf, (40, 40, 50), (x, y, T, T))
                for i in range(3):
                    pygame.draw.rect(surf, Colors.GATE, (x + 4 + i * 10, y, 5, T))

    def draw(self, surf):
        shake = self.effects.shake_offset()
        cam_x, cam_y = self.camera.render_offset(shake)
        self.background.draw(surf, cam_x, cam_y, self.time)
        surf.blit(self.room_surface, (-cam_x, -cam_y))
        self._draw_dynamic_tiles(surf, cam_x, cam_y)

        for obj in self.interactables:
            obj.draw(surf, cam_x, cam_y, self.time)
        for item in self.items:
            item.draw(surf, cam_x, cam_y, self.time)
        if self.bag:
            self.bag.draw(surf, cam_x, cam_y, self.time)
        island = tiles_mod.theme_of(self.room.zone) in ("island", "ruins", "temple")
        for m in self.movers:
            m.draw(surf, cam_x, cam_y, island)
        for e in self.enemies:
            e.draw(surf, cam_x, cam_y)
        for h in self.hazards:
            if not getattr(h, "front", False):
                h.draw(surf, cam_x, cam_y, self.time)
        for c in self.coins:
            c.draw(surf, cam_x, cam_y)
        self.projectiles.draw(surf, cam_x, cam_y)
        self.player.draw(surf, cam_x, cam_y)
        for h in self.hazards:
            if getattr(h, "front", False):
                h.draw(surf, cam_x, cam_y, self.time)
        self.effects.draw_world(surf, cam_x, cam_y)
        self._draw_water(surf, cam_x, cam_y)
        self.background.draw_front(surf, cam_x, cam_y, self.time)
        near = self.nearby_interactable() if self.player.alive else None
        if near is not None:
            near.draw_prompt(surf, cam_x, cam_y)

        if self.debug:
            self._draw_debug(surf, cam_x, cam_y)

        self.effects.draw_overlay(surf)
        fade = self.fade / FX.ROOM_FADE if FX.ROOM_FADE else 0
        if self.hazard_timer > 0:
            fade = max(fade, 1.0 - self.hazard_timer / PCfg.HAZARD_FREEZE)
        if fade > 0:
            ui.dim(surf, int(255 * min(1.0, fade)))
        boss_bar = self.boss is not None and self.boss.alive and self.boss.awake
        ui.draw_hud(surf, self.player, self.progress, self.room.name, 0.0 if boss_bar else self.room_name_timer,
                    self.app.clock.get_fps() if self.debug else None, muted=self.app.audio.muted,
                    story=self.story is not None)
        if boss_bar:
            name = getattr(self.boss, "name", "Guardião")
            title = getattr(self.boss, "title", "")
            ui.draw_boss_bar(surf, f"{name} - {title}" if title else name, self.boss.hp, self.boss.max_hp)

    def _draw_debug(self, surf, cam_x, cam_y):
        p = self.player
        pygame.draw.rect(surf, (0, 255, 0), (p.x - cam_x, p.y - cam_y, p.w, p.h), 1)
        if p.attack is not None:
            bx, by, bw, bh = p.attack.hitbox(p)
            col = (255, 0, 0) if p.attack.phase == "active" else (120, 60, 60)
            pygame.draw.rect(surf, col, (bx - cam_x, by - cam_y, bw, bh), 1)
        for e in self.enemies:
            pygame.draw.rect(surf, (255, 255, 0), (e.x - cam_x, e.y - cam_y, e.w, e.h), 1)
        state = "chão" if p.on_ground else "ar"
        info = (f"{self.room.id} {state} vx={p.vx:6.0f} vy={p.vy:6.0f} pulos={p.jumps_used} "
                f"dash_cd={p.dash_cooldown:.2f} energia={p.energy:.0f} "
                f"atk={p.attack.spec.name + ':' + p.attack.phase if p.attack else '-'}")
        ui.text(surf, info, 20, (20, 96), (180, 255, 180))



# ---------------------------------------------------------------------------
class Overlay(State):
    """Estado sobre a partida (partida congelada por baixo)."""

    def __init__(self, app, play):
        super().__init__(app)
        self.play = play

    def close(self):
        self.app.resume(self.play)


class PauseState(Overlay):
    def __init__(self, app, play):
        super().__init__(app, play)
        self.confirm_restart = False
        self._build_menu(0)

    def _build_menu(self, index):
        som = "Som: desligado" if self.app.audio.muted else "Som: ligado"
        restart = "Confirmar? (apaga o save)" if self.confirm_restart else "Reiniciar jogo"
        self.menu = ui.Menu([("Continuar", "resume"), ("Voltar à bola de cristal", "bench"), (som, "sound"),
                             (restart, "restart"), ("Menu inicial", "menu"), ("Sair do jogo", "quit")],
                            center_y=172, spacing=40, size=34)
        self.menu.index = index

    def frame(self, dt, inp):
        if inp.was_pressed("pause"):
            inp.consume()
            self.close()
            return
        choice = self.menu.handle(inp, self.app.audio)
        inp.consume()
        if choice == "resume":
            self.close()
        elif choice == "bench":
            self.play.respawn_at_bench()
            self.close()
        elif choice == "sound":
            self.app.audio.toggle_mute()
            self._build_menu(self.menu.index)
        elif choice == "restart":
            if not self.confirm_restart:
                self.confirm_restart = True
                self._build_menu(self.menu.index)
            else:
                self.app.start_game(self.play.progress.fresh_copy())
        elif choice == "menu":
            self.app.to_menu()
        elif choice == "quit":
            self.app.running = False

    def draw(self, surf):
        self.play.draw(surf)
        ui.dim(surf, 190)
        ui.text(surf, "PAUSADO", 48, (Display.WIDTH // 2, 34), Colors.UI_TEXT, "center", title=True)
        self.menu.draw(surf)
        ui.draw_inventory(surf, self.play.progress, self.play.player, 40, 318)
        ui.draw_controls(surf, 470, 300, title=False, compact=True)


class MapState(Overlay):
    def frame(self, dt, inp):
        if inp.was_pressed("map") or inp.was_pressed("pause") or inp.was_pressed("menu_confirm"):
            inp.consume()
            self.close()
            return
        inp.consume()

    def draw(self, surf):
        # o jogo fica parado enquanto o mapa está aberto: desenha uma vez e reaproveita
        if getattr(self, "cache", None) is None:
            self.play.draw(surf)
            ui.dim(surf, 220)
            ui.draw_map(surf, self.play)
            self.cache = surf.copy()
        else:
            surf.blit(self.cache, (0, 0))


class MessageState(Overlay):
    """Aviso de item novo. Fecha com Enter/Espaço/clique depois de um instante."""

    def __init__(self, app, play, title, body):
        super().__init__(app, play)
        self.title = title
        self.body = body
        self.t = 0.0

    def frame(self, dt, inp):
        self.t += dt
        if self.t > 0.45 and (inp.was_pressed("menu_confirm") or inp.was_pressed("attack_quick")
                              or inp.was_pressed("pause") or inp.was_pressed("interact")):
            inp.consume()
            self.close()
            return
        inp.consume()

    def draw(self, surf):
        self.play.draw(surf)
        ui.dim(surf, 150)
        box = pygame.Rect(0, 0, 640, 170)
        box.center = (Display.WIDTH // 2, Display.HEIGHT // 2)
        pygame.draw.rect(surf, (20, 22, 34), box, border_radius=10)
        pygame.draw.rect(surf, Colors.ITEM, box, 2, border_radius=10)
        ui.text(surf, self.title, 42, (box.centerx, box.y + 46), Colors.ITEM, "center", title=True)
        ui.text(surf, self.body, 26, (box.centerx, box.y + 96), Colors.UI_TEXT, "center")
        if self.t > 0.45:
            ui.text(surf, "Enter / Espaço / clique para continuar", 20, (box.centerx, box.bottom - 22),
                    Colors.UI_DIM, "center")


class ListState(Overlay):
    """Base para listas de opções com descrição (banco e lojas)."""
    title = ""

    def __init__(self, app, play):
        super().__init__(app, play)
        self.index = 0
        self.notice = ""
        self.notice_t = 0.0

    def entries(self):
        """[(rótulo, info à direita, descrição, habilitado, ação)]"""
        return []

    def frame(self, dt, inp):
        self.notice_t = max(0.0, self.notice_t - dt)
        entries = self.entries()
        if inp.was_pressed("pause"):
            inp.consume()
            self.on_close()
            return
        if inp.was_pressed("menu_up"):
            self.index = (self.index - 1) % len(entries)
            self.app.audio.play("ui_move")
        if inp.was_pressed("menu_down"):
            self.index = (self.index + 1) % len(entries)
            self.app.audio.play("ui_move")
        for i, r in enumerate(getattr(self, "rects", [])):
            if r.collidepoint(inp.mouse_pos):
                self.index = i
        clicked = inp.mouse_clicked and any(r.collidepoint(inp.mouse_pos) for r in getattr(self, "rects", []))
        if inp.was_pressed("menu_confirm") or clicked:
            action = entries[self.index][4]
            inp.consume()
            action()
            return
        inp.consume()

    def say(self, msg):
        self.notice = msg
        self.notice_t = 2.0

    def on_close(self):
        self.close()

    def draw(self, surf):
        self.play.draw(surf)
        ui.dim(surf, 200)
        ui.text(surf, self.title, 44, (Display.WIDTH // 2, 44), Colors.UI_TEXT, "center", title=True)
        ui.text(surf, f"Moedas: {self.play.progress.coins}", 26, (Display.WIDTH - 40, 34), Colors.COIN, "topright")
        self.rects = []
        entries = self.entries()
        y = 96
        for i, (label, info, _desc, enabled, _a) in enumerate(entries):
            sel = i == self.index
            col = Colors.UI_ACCENT if sel else (Colors.UI_TEXT if enabled else Colors.UI_DIM)
            r = pygame.Rect(150, y - 4, 660, 34)
            if sel:
                pygame.draw.rect(surf, (34, 40, 60), r, border_radius=6)
            ui.text(surf, label, 28, (170, y + 2), col)
            ui.text(surf, info, 26, (790, y + 4), Colors.COIN if enabled else Colors.UI_DIM, "topright")
            self.rects.append(r)
            y += 38
        desc = entries[self.index][2] if entries else ""
        ui.text(surf, desc, 24, (Display.WIDTH // 2, Display.HEIGHT - 74), Colors.UI_TEXT, "center")
        if self.notice_t > 0:
            ui.text(surf, self.notice, 26, (Display.WIDTH // 2, Display.HEIGHT - 44), Colors.ITEM, "center")
        else:
            ui.text(surf, "W/S navegar · Enter escolher · ESC sair", 20, (Display.WIDTH // 2, Display.HEIGHT - 40),
                    Colors.UI_DIM, "center")


class BenchState(Overlay):
    """Bola de cristal: salva, cura e abre a tela de amuletos (grade com ícones)."""

    def __init__(self, app, play):
        super().__init__(app, play)
        from .amuletos import CharmScreen
        self.screen = CharmScreen(play.progress)
        self.notice = ""
        self.notice_t = 0.0
        self.t = 0.0

    def frame(self, dt, inp):
        self.t += dt
        self.notice_t = max(0.0, self.notice_t - dt)
        if inp.was_pressed("pause"):
            inp.consume()
            self.on_close()
            return
        moves = {"left": (-1, 0), "right": (1, 0), "menu_up": (0, -1), "menu_down": (0, 1)}
        for action, (dx, dy) in moves.items():
            if inp.was_pressed(action):
                self.screen.move(dx, dy)
                self.app.audio.play("ui_move")
        for i, r in enumerate(self.screen.rects):
            if r.collidepoint(inp.mouse_pos):
                self.screen.index = i
        clicked = inp.mouse_clicked
        if clicked and self.screen.close_rect.collidepoint(inp.mouse_pos):
            inp.consume()
            self.on_close()
            return
        on_cell = any(r.collidepoint(inp.mouse_pos) for r in self.screen.rects)
        if inp.was_pressed("menu_confirm") or (clicked and on_cell):
            self._toggle(self.screen.selected())
        inp.consume()

    def _toggle(self, cid):
        pr = self.play.progress
        if cid not in pr.charms_owned:
            self.say("Você ainda não encontrou este amuleto.")
            return
        if pr.toggle_charm(cid):
            self.play.player.recompute_stats()
            self.play.player.hp = self.play.player.max_hp
            self.app.audio.play("ui_select")
            self.play.save()
        else:
            self.say("Espaços de amuleto insuficientes.")

    def say(self, msg):
        self.notice = msg
        self.notice_t = 2.0

    def on_close(self):
        self.play.save()
        self.close()

    def draw(self, surf):
        self.play.draw(surf)
        ui.dim(surf, 200)
        self.screen.draw(surf, self.t, self.notice if self.notice_t > 0 else "")


class ShopState(ListState):
    def __init__(self, app, play, kind):
        super().__init__(app, play)
        self.kind = kind
        self.title = "Loja" if kind == "shop" else "Ferreiro"

    def entries(self):
        pr = self.play.progress
        out = []
        if self.kind == "shop":
            for sid, label, price in SHOP_STOCK:
                sold = sid in pr.shop_bought
                if sid.startswith("charm:"):
                    desc = CHARMS[sid[6:]]["desc"]
                else:
                    desc = {"map": "Mostra as salas que você já visitou (M ou Tab).",
                            "fragment": "Junte 4 fragmentos para ganhar +1 de vida máxima.",
                            "notch": "Mais espaço para equipar amuletos."}[sid]
                info = "vendido" if sold else f"{price} moedas"
                out.append((label, info, desc, not sold and pr.coins >= price,
                            lambda sid=sid, price=price: self._buy(sid, price)))
        else:
            up = pr.next_weapon_upgrade()
            if up is None:
                out.append(("Arma no nível máximo", "", "Não há mais o que melhorar.", False, lambda: None))
            else:
                cost, ore = up
                ok = pr.coins >= cost and pr.ore >= ore
                info = f"{cost} moedas" + (f" + {ore} minério" if ore else "")
                out.append((f"Melhorar arma (nível {pr.weapon_level} -> {pr.weapon_level + 1})", info,
                            f"Ataque rápido +1 de dano, pesado +2. Você tem {pr.ore} minério(s).", ok,
                            lambda: self._upgrade(cost, ore)))
        out.append(("Sair", "", "", True, self.on_close))
        return out

    def _buy(self, sid, price):
        pr = self.play.progress
        if sid in pr.shop_bought:
            self.say("Já vendido.")
            return
        if pr.coins < price:
            self.say("Moedas insuficientes.")
            return
        pr.coins -= price
        pr.shop_bought.add(sid)
        if sid.startswith("charm:"):
            msg = pr.give("charm", sid[6:])
        else:
            msg = pr.give(sid)
        old_max = self.play.player.max_hp
        self.play.player.recompute_stats()
        if self.play.player.max_hp > old_max:
            self.play.player.hp = self.play.player.max_hp
        self.app.audio.play("buy")
        self.play.save()
        self.say(msg[0] + " comprado!" if msg else "Comprado!")

    def _upgrade(self, cost, ore):
        pr = self.play.progress
        if pr.coins < cost or pr.ore < ore:
            self.say("Faltam moedas ou minério.")
            return
        pr.coins -= cost
        pr.ore -= ore
        pr.weapon_level += 1
        self.play.player.recompute_stats()
        self.app.audio.play("buy")
        self.play.save()
        self.say(f"Arma melhorada para o nível {pr.weapon_level}!")


class DeathState(Overlay):
    def __init__(self, app, play):
        super().__init__(app, play)
        self.t = 0.0
        label = "Tentar de novo (último ponto salvo)" if play.story is not None else "Voltar ao último banco"
        self.menu = ui.Menu([(label, "respawn"), ("Menu inicial", "menu")], center_y=320, size=34)

    def frame(self, dt, inp):
        self.play.effects.update(dt)
        choice = self.menu.handle(inp, self.app.audio)
        inp.consume()
        if choice == "respawn":
            self.play.respawn_at_bench()
            self.close()
        elif choice == "menu":
            self.app.to_menu()

    def draw(self, surf):
        self.play.draw(surf)
        ui.dim(surf, 200)
        title = "VOCÊ CAIU" if self.play.story is not None else "VOCÊ MORREU"
        ui.text(surf, title, 64, (Display.WIDTH // 2, 150), Colors.HP_FULL, "center", title=True)
        if self.play.story is not None:
            ui.text(surf, "A maré quase levou você... mas a história ainda não acabou.", 26,
                    (Display.WIDTH // 2, 210), Colors.UI_DIM, "center")
        bag = self.play.progress.bag
        if bag:
            ui.text(surf, f"{bag[3]} moedas ficaram para trás. Volte para buscá-las.", 26,
                    (Display.WIDTH // 2, 222), Colors.COIN, "center")
        self.menu.draw(surf)


class DialogState(Overlay):
    """Caixa de diálogo com retrato, nome e texto digitado. Enter/Espaço/W/clique avançam."""
    CHARS_PER_SEC = 55

    def __init__(self, app, play, character, lines, on_done=None):
        super().__init__(app, play)
        self.character = character
        self.lines = lines
        self.on_done = on_done
        self.index = 0
        self.typed = 0.0
        self.t = 0.0

    def _full(self):
        return self.typed >= len(self.lines[self.index])

    def frame(self, dt, inp):
        self.t += dt
        self.typed += dt * self.CHARS_PER_SEC
        advance = (inp.was_pressed("menu_confirm") or inp.was_pressed("interact")
                   or inp.was_pressed("attack_quick") or inp.mouse_clicked)
        if inp.was_pressed("pause"):
            inp.consume()
            self.finish()
            return
        if advance and self.t > 0.12:
            if not self._full():
                self.typed = len(self.lines[self.index])
            else:
                self.index += 1
                self.typed = 0.0
                if self.index >= len(self.lines):
                    inp.consume()
                    self.finish()
                    return
        inp.consume()

    def finish(self):
        self.close()
        if self.on_done:
            self.on_done()

    def draw(self, surf):
        self.play.draw(surf)
        W, H = Display.WIDTH, Display.HEIGHT
        box = pygame.Rect(30, H - 176, W - 60, 156)
        shade = pygame.Surface(box.size, pygame.SRCALPHA)
        shade.fill((12, 12, 20, 235))
        surf.blit(shade, box)
        pygame.draw.rect(surf, (150, 120, 80), box, 2, border_radius=8)
        portrait = pygame.Rect(box.x + 14, box.y + 14, 120, box.h - 28)
        pygame.draw.rect(surf, (28, 26, 36), portrait, border_radius=6)
        ch = self.character
        if not draw_portrait(surf, ch.style, portrait, self.t):
            draw_character(surf, ch.style, ch.color, ch.h, portrait.centerx, portrait.bottom - 8, self.t,
                           scale=1.4 if ch.style == "corpo" else 2.1)
        ui.text(surf, ch.data["name"], 28, (portrait.right + 18, box.y + 14), (240, 200, 130), title=True)
        shown = self.lines[self.index][:int(self.typed)]
        ui.wrap_text(surf, shown, 26, portrait.right + 18, box.y + 50, box.right - portrait.right - 40)
        if self._full():
            ui.text(surf, "Enter / W / clique", 18, (box.right - 14, box.bottom - 22), Colors.UI_DIM, "topright")
        ui.text(surf, f"{self.index + 1}/{len(self.lines)}", 18, (box.right - 14, box.y + 12), Colors.UI_DIM,
                "topright")



class BossIntroState(Overlay):
    """Cartão de apresentação do chefe (nome, título e uma fala)."""

    def __init__(self, app, play, boss, info):
        super().__init__(app, play)
        self.boss = boss
        self.line = info.get("intro", "").format(**play.forms())
        self.t = 0.0

    def frame(self, dt, inp):
        self.t += dt
        if self.t > 0.8 and (inp.was_pressed("menu_confirm") or inp.was_pressed("attack_quick")
                             or inp.was_pressed("pause") or self.t > 4.5):
            inp.consume()
            self.close()
            return
        inp.consume()

    def draw(self, surf):
        self.play.draw(surf)
        W, H = Display.WIDTH, Display.HEIGHT
        k = min(1.0, self.t / 0.35)
        band = pygame.Surface((W, 150), pygame.SRCALPHA)
        band.fill((8, 6, 12, int(220 * k)))
        surf.blit(band, (0, H // 2 - 110))
        x = int(-400 + 400 * k)
        ui.text(surf, self.boss.name.upper(), 56, (W // 2 + x, H // 2 - 70), (255, 214, 140), "center", title=True)
        ui.text(surf, self.boss.title, 34, (W // 2 - x, H // 2 - 22), (230, 120, 140), "center", title=True)
        if self.t > 0.5:
            ui.wrap_text(surf, f"\"{self.line}\"", 24, 90, H // 2 + 8, W - 180, Colors.UI_TEXT)


class EndingState(Overlay):
    """Desfecho: textos finais (verdadeiro com as 3 cartas, comum sem elas)."""
    CHARS_PER_SEC = 40

    def __init__(self, app, play):
        super().__init__(app, play)
        story = play.story
        self.true_ending = len(play.progress.letters) >= 3
        self.lines = list(story.ENDING_TRUE if self.true_ending else story.ENDING_NORMAL)
        self.index = 0
        self.typed = 0.0
        self.t = 0.0
        play.progress.flags.add("zerado")
        play.save()
        app.audio.play_music(AudioCfg.MUSIC["menu"])

    def frame(self, dt, inp):
        self.t += dt
        self.typed += dt * self.CHARS_PER_SEC
        if inp.was_pressed("menu_confirm") or inp.was_pressed("attack_quick") or inp.mouse_clicked:
            line = self.lines[self.index]
            if self.typed < len(line):
                self.typed = len(line)
            else:
                self.index += 1
                self.typed = 0.0
                if self.index >= len(self.lines):
                    inp.consume()
                    self.app.push(ResultsState(self.app, self.play, self.true_ending))
                    return
        inp.consume()

    def draw(self, surf):
        W, H = Display.WIDTH, Display.HEIGHT
        surf.fill((6, 8, 16))
        for i in range(60):
            x = (i * 97 + self.t * (10 + i % 5)) % W
            y = (i * 53) % H
            surf.set_at((int(x), int(y)), (120, 130, 170))
        line = self.lines[self.index]
        final = self.index == len(self.lines) - 1
        if final:
            ui.text(surf, line, 64, (W // 2, H // 2 - 20), (255, 214, 140), "center", title=True)
        else:
            ui.wrap_text(surf, line[:int(self.typed)], 28, 110, H // 2 - 40, W - 220)
        ui.text(surf, "Enter / clique para continuar", 20, (W // 2, H - 30), Colors.UI_DIM, "center")


class ResultsState(State):
    """Placar final: tempo, mortes, moedas, cartas -> nota e recorde."""

    def __init__(self, app, play, true_ending):
        super().__init__(app)
        self.play = play
        pr = play.progress
        self.time = pr.play_time
        self.deaths = pr.deaths
        self.coins = pr.coins
        self.letters = len(pr.letters)
        self.true_ending = true_ending
        score = 10000 - int(self.time) * 2 - self.deaths * 300 + self.coins * 5 + self.letters * 1000
        self.score = max(0, score)
        if self.letters >= 3 and self.deaths <= 3:
            self.grade = "S"
        elif self.deaths <= 6:
            self.grade = "A"
        elif self.deaths <= 12:
            self.grade = "B"
        else:
            self.grade = "C"
        from .records import add_record
        import datetime
        add_record({"capitulo": 1, "protagonista": pr.protagonist, "dificuldade": pr.difficulty,
                    "tempo": round(self.time), "quedas": self.deaths, "cartas": self.letters,
                    "nota": self.grade, "pontos": self.score, "data": datetime.date.today().isoformat()},
                   getattr(app, "records_path", None))
        self.menu = ui.Menu([("Jogar de novo", "again"), ("Menu inicial", "menu")], center_y=430, size=34)
        self.t = 0.0

    def frame(self, dt, inp):
        self.t += dt
        choice = self.menu.handle(inp, self.app.audio)
        inp.consume()
        if choice == "again":
            self.app.start_game(self.play.progress.fresh_copy())
        elif choice == "menu":
            self.app.to_menu()

    def draw(self, surf):
        W, H = Display.WIDTH, Display.HEIGHT
        surf.fill((10, 10, 20))
        ui.text(surf, "RESULTADO", 56, (W // 2, 60), (255, 214, 140), "center", title=True)
        ui.text(surf, "Final verdadeiro" if self.true_ending else "Final comum", 30, (W // 2, 112),
                Colors.UI_ACCENT, "center")
        m, sec = divmod(int(self.time), 60)
        rows = [("Tempo", f"{m}:{sec:02d}"), ("Quedas", str(self.deaths)), ("Moedas", str(self.coins)),
                ("Páginas do diário", f"{self.letters}/3"), ("Pontuação", str(self.score))]
        y = 160
        for label, value in rows:
            ui.text(surf, label, 28, (W // 2 - 200, y), Colors.UI_DIM)
            ui.text(surf, value, 28, (W // 2 + 200, y), Colors.UI_TEXT, "topright")
            y += 40
        ui.text(surf, self.grade, 120, (W // 2 + 330, 250), (255, 214, 140), "center", title=True)
        ui.text(surf, "nota", 24, (W // 2 + 330, 320), Colors.UI_DIM, "center")
        self.menu.draw(surf)
