"""Estados do jogo: menu, partida, pausa/inventário, mapa, banco, loja, mensagem e morte."""

import math
import random

import pygame

from . import ui
from .camera import Camera
from .combat import ProjectileSystem, resolve_player_attack
from .config import Audio as AudioCfg, Boss as BossCfg, Colors, Display, Effects as FX, Enemies as EN, Game, Player as PCfg, World
from .effects import EffectSystem
from .enemies import spawn_enemies
from .objects import Bench, Character, CoinBag, ItemPickup, NPC, draw_character, spawn_coins
from .physics import is_supported, rects_overlap
from .player import Player
from .progress import CHARMS, SHOP_STOCK, Progress
from .world import BOSS_LOCK, BREAKABLE, FIGHT_GATE, LOCKED, WorldMap

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
        self.enemies = spawn_enemies(room, room.boss_defeated)
        self.boss = next((e for e in self.enemies if e.is_boss), None)
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
        bag = self.progress.bag
        self.bag = CoinBag(bag[1], bag[2], bag[3]) if bag and bag[0] == room.id else None
        self.coins = []
        self.projectiles.clear()
        self.effects.clear()
        self.room_surface = self._render_room(room)
        self.room_name_timer = 1.8
        self.fade = FX.ROOM_FADE
        self.audio.play_music(AudioCfg.MUSIC.get(room.zone, AudioCfg.MUSIC["default"]))

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
            if self.death_timer > 1.1:
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
        if p.alive and inp.was_pressed("interact") and p.on_ground and not p.dashing:
            if self._interact():
                return True
        p.update(dt, inp, self.room, self)
        self._update_boss_fight()
        for e in self.enemies:
            e.update(dt, self.room, p, self)
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
        self.camera.update(dt, p, self.room)
        return True

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
            self.save()
            self.app.push(MessageState(self.app, self, "Guardião derrotado", "O caminho a oeste está aberto."))

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
        self.enemies = spawn_enemies(self.room, self.room.boss_defeated)
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
        room_id, x, y = self.last_safe
        p = self.player
        if room_id != self.room.id:
            p.place(x, y)
            self.load_room(self.world.rooms[room_id])
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
        surf = pygame.Surface((room.width, room.height), pygame.SRCALPHA)
        tile_col, edge_col = room.palette[2], room.palette[3]
        for ty in range(room.rows_count):
            for tx in range(room.cols):
                ch = room.tile(tx, ty)
                x, y = tx * T, ty * T
                if ch == "#":
                    pygame.draw.rect(surf, tile_col, (x, y, T, T))
                    if room.tile(tx, ty - 1) not in ("#", None):
                        pygame.draw.rect(surf, edge_col, (x, y, T, 4))
                    if room.tile(tx - 1, ty) not in ("#", None):
                        pygame.draw.rect(surf, edge_col, (x, y, 2, T))
                    if room.tile(tx + 1, ty) not in ("#", None):
                        pygame.draw.rect(surf, edge_col, (x + T - 2, y, 2, T))
                elif ch == "-":
                    pygame.draw.rect(surf, Colors.ONEWAY, (x, y, T, 7))
                    pygame.draw.rect(surf, (90, 70, 50), (x, y + 7, T, 3))
                elif ch == "~":
                    pygame.draw.rect(surf, (30, 70, 110, 220), (x, y + 6, T, T - 6))
                    pygame.draw.rect(surf, (90, 150, 200), (x, y + 6, T, 3))
                elif ch == "^":
                    for i in range(3):
                        bx = x + 2 + i * 10
                        pygame.draw.polygon(surf, Colors.SPIKE, [(bx, y + T), (bx + 5, y + 10), (bx + 10, y + T)])
        return surf

    def _draw_background(self, surf, cam_x, cam_y):
        """Fundo provisório por zona, com parallax para dar noção de velocidade."""
        zone = self.room.zone
        bg, bg_far = self.room.palette[0], self.room.palette[1]
        W, H = Display.WIDTH, Display.HEIGHT
        surf.fill(bg)
        if zone == "convés":
            for i in range(0, H, 8):
                k = i / H
                col = tuple(int(a + (b - a) * k) for a, b in zip((6, 8, 18), bg_far))
                pygame.draw.rect(surf, col, (0, i, W, 8))
            rnd = random.Random(7)
            for _ in range(40):
                sx = (rnd.uniform(0, W * 2) - cam_x * 0.05) % W
                sy = rnd.uniform(0, H * 0.6)
                pygame.draw.circle(surf, (150, 160, 190), (int(sx), int(sy)), 1)
            # mar ao longe
            sea_y = H - 60 - cam_y * 0.15 + (self.room.height - H) * 0.15
            pts = [(0, H)]
            for x in range(0, W + 24, 24):
                pts.append((x, sea_y + math.sin((x + cam_x * 0.3) * 0.02 + self.time * 1.5) * 6))
            pts.append((W, H))
            pygame.draw.polygon(surf, (18, 34, 56), pts)
        elif zone in ("interior", "porão"):
            for i in range(16):
                x = (i * 70 - cam_x * 0.5) % (W + 70) - 35
                pygame.draw.rect(surf, bg_far, (x, 0, 66, H))
            for i in range(4):
                lx = (i * 300 + 120 - cam_x * 0.5) % (W + 300) - 150
                glow = 40 + 4 * math.sin(self.time * 3 + i)
                pygame.draw.circle(surf, tuple(min(255, c + 18) for c in bg_far), (int(lx), 120), int(glow))
                pygame.draw.rect(surf, (230, 180, 90), (lx - 4, 112, 8, 12))
        else:
            for i in range(14):
                x = (i * 131 - cam_x * 0.35) % (W + 160) - 80
                h = 120 + (i * 53) % 200
                pygame.draw.rect(surf, bg_far, (x, H - h - (cam_y * 0.2) % 40, 46, h + 60))

    def _draw_dynamic_tiles(self, surf, cam_x, cam_y):
        room = self.room
        tile_col = room.palette[2]
        for tx, ty in room.tiles_of({BREAKABLE, FIGHT_GATE, BOSS_LOCK, LOCKED}):
            if not room.is_solid(tx, ty):
                continue
            x, y = tx * T - cam_x, ty * T - cam_y
            ch = room.tile(tx, ty)
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
        self._draw_background(surf, cam_x, cam_y)
        surf.blit(self.room_surface, (-cam_x, -cam_y))
        self._draw_dynamic_tiles(surf, cam_x, cam_y)

        for obj in self.interactables:
            obj.draw(surf, cam_x, cam_y, self.time)
        for item in self.items:
            item.draw(surf, cam_x, cam_y, self.time)
        if self.bag:
            self.bag.draw(surf, cam_x, cam_y, self.time)
        for e in self.enemies:
            e.draw(surf, cam_x, cam_y)
        for c in self.coins:
            c.draw(surf, cam_x, cam_y)
        self.projectiles.draw(surf, cam_x, cam_y)
        self.player.draw(surf, cam_x, cam_y)
        self.effects.draw_world(surf, cam_x, cam_y)
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
        ui.draw_hud(surf, self.player, self.progress, self.room.name, self.room_name_timer,
                    self.app.clock.get_fps() if self.debug else None)
        if self.boss is not None and self.boss.alive and self.boss.awake:
            ui.draw_boss_bar(surf, "Guardião", self.boss.hp, self.boss.max_hp)

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
        self.menu = ui.Menu([("Continuar", "resume"), ("Voltar ao último banco", "bench"),
                             ("Menu inicial", "menu"), ("Sair do jogo", "quit")],
                            center_y=150, spacing=40, size=34)

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
        elif choice == "menu":
            self.app.to_menu()
        elif choice == "quit":
            self.app.running = False

    def draw(self, surf):
        self.play.draw(surf)
        ui.dim(surf, 190)
        ui.text(surf, "PAUSADO", 48, (Display.WIDTH // 2, 54), Colors.UI_TEXT, "center", title=True)
        self.menu.draw(surf)
        ui.draw_inventory(surf, self.play.progress, self.play.player, 40, 260)
        ui.draw_controls(surf, 560, 260)


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


class BenchState(ListState):
    title = "Banco — amuletos"

    def entries(self):
        pr = self.play.progress
        out = []
        for cid in pr.charms_owned:
            c = CHARMS[cid]
            eq = cid in pr.charms_equipped
            mark = "[x] " if eq else "[  ] "
            out.append((mark + c["name"], f"custo {c['cost']}", c["desc"], eq or pr.can_equip(cid),
                        lambda cid=cid: self._toggle(cid)))
        out.append(("Levantar", f"espaços {pr.notches_used}/{pr.notches}",
                    "Vida restaurada e jogo salvo. Equipe amuletos aqui.", True, self.on_close))
        return out

    def _toggle(self, cid):
        pr = self.play.progress
        if pr.toggle_charm(cid):
            self.play.player.recompute_stats()
            self.play.player.hp = self.play.player.max_hp
            self.app.audio.play("ui_select")
            self.play.save()
        else:
            self.say("Espaços de amuleto insuficientes.")

    def on_close(self):
        self.play.save()
        self.close()


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
        self.menu = ui.Menu([("Voltar ao último banco", "respawn"), ("Menu inicial", "menu")],
                            center_y=300, size=36)

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
        ui.dim(surf, 190)
        ui.text(surf, "VOCÊ MORREU", 64, (Display.WIDTH // 2, 170), Colors.HP_FULL, "center", title=True)
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
        draw_character(surf, ch.style, ch.color, ch.h, portrait.centerx, portrait.bottom - 8, self.t,
                       scale=1.4 if ch.style == "corpo" else 2.1)
        ui.text(surf, ch.data["name"], 28, (portrait.right + 18, box.y + 14), (240, 200, 130), title=True)
        shown = self.lines[self.index][:int(self.typed)]
        ui.wrap_text(surf, shown, 26, portrait.right + 18, box.y + 50, box.right - portrait.right - 40)
        if self._full():
            ui.text(surf, "Enter / W / clique", 18, (box.right - 14, box.bottom - 22), Colors.UI_DIM, "topright")
        ui.text(surf, f"{self.index + 1}/{len(self.lines)}", 18, (box.right - 14, box.y + 12), Colors.UI_DIM,
                "topright")
