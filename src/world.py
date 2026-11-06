"""Salas, tiles, portas e mapa-múndi.

As salas são grades de caracteres (montadas em src/rooms.py). As bordas
abertas são marcadas com dígitos: cada dígito é uma porta, e ROOM_LINKS liga
(sala, dígito) a (outra sala, dígito). A posição das salas no mapa-múndi é
calculada a partir dessas ligações.

Legenda:
    #  bloco sólido              -  plataforma de mão única
    ^  espinhos                  X  parede quebrável (segredo)
    |  portão da luta (fecha enquanto o chefe luta)
    =  portão trancado até o chefe da sala ser derrotado
    D  porta trancada (abre com a chave da sala)   ~  água funda (perigo)
    N  personagem (lista `npcs` da sala, em ordem de leitura)
    C  tábua que desaba pouco depois de pisada (volta depois)
    k  caixa quebrável (solta moedas)
    0-9  porta (borda aberta)    *  item (lista `items` da sala, em ordem de leitura)
    P  início do jogo            B  banco      $  loja      R  ferreiro
    g c t f j s  inimigos        G  chefe
"""

from collections import deque

from .config import World, ZONE_PALETTES

T = World.TILE

SOLID = "#"
ONEWAY = "-"
SPIKE = "^"
BREAKABLE = "X"
FIGHT_GATE = "|"
BOSS_LOCK = "="
LOCKED = "D"
WATER = "~"
DOOR_CHARS = set("0123456789")
ENTITY_CHARS = set("PB$RgctfjsG*Nka")
CRUMBLE = "C"


class Door:
    def __init__(self, digit, side, cells):
        self.digit = digit
        self.side = side
        self.cells = cells
        if side in ("W", "E"):
            rows = [ty for _, ty in cells]
            self.lo, self.hi = min(rows), max(rows)
        else:
            cols = [tx for tx, _ in cells]
            self.lo, self.hi = min(cols), max(cols)


class Room:
    def __init__(self, room_id, name, zone, rows, items=(), npcs=(), key=None, movers=(), boss=None):
        widths = {len(row) for row in rows}
        if len(widths) != 1:
            raise ValueError(f"Sala {room_id}: linhas com larguras diferentes {sorted(widths)}")
        self.id = room_id
        self.name = name
        self.zone = zone
        self.palette = ZONE_PALETTES[zone]
        self.cols = len(rows[0])
        self.rows_count = len(rows)
        self.width = self.cols * T
        self.height = self.rows_count * T
        self.origin_tx = self.origin_ty = 0
        self.tiles = []
        self.spawns = []           # (tipo, x, y[, índice do item]) — base do tile
        self.doors = {}
        door_cells = {}
        item_index = 0
        npc_index = 0
        for ty, row in enumerate(rows):
            line = []
            for tx, ch in enumerate(row):
                if ch in ENTITY_CHARS:
                    if ch == "*":
                        self.spawns.append((ch, tx * T + T / 2, (ty + 1) * T, item_index))
                        item_index += 1
                    elif ch == "N":
                        self.spawns.append((ch, tx * T + T / 2, (ty + 1) * T, npc_index))
                        npc_index += 1
                    else:
                        self.spawns.append((ch, tx * T + T / 2, (ty + 1) * T))
                    ch = "."
                elif ch in DOOR_CHARS:
                    door_cells.setdefault(ch, []).append((tx, ty))
                    ch = "."
                line.append(ch)
            self.tiles.append(line)
        self.items = list(items)
        self.npcs = list(npcs)
        if len(self.npcs) != npc_index:
            raise ValueError(f"Sala {room_id}: {npc_index} 'N' no mapa, {len(self.npcs)} personagens definidos")
        self.key = key                 # flag do progresso que abre as portas 'D' desta sala
        self.door_unlocked = False
        self.movers = list(movers)     # plataformas móveis: dicts com x0, y0, x1, y1 (tiles), w, speed
        self.boss = boss               # id do chefe desta sala (ver chapter1.BOSSES)
        self.crumbled = {}             # (tx, ty) -> segundos até voltar
        if len(self.items) != item_index:
            raise ValueError(f"Sala {room_id}: {item_index} '*' no mapa, {len(self.items)} itens definidos")
        for digit, cells in door_cells.items():
            sides = {self._side_of(tx, ty) for tx, ty in cells}
            if len(sides) != 1 or None in sides:
                raise ValueError(f"Sala {room_id}: porta {digit} precisa ficar numa única borda")
            self.doors[digit] = Door(digit, sides.pop(), cells)
        # estado dinâmico (preenchido pelo PlayState a partir do progresso)
        self.broken = set()
        self.fight_active = False
        self.boss_defeated = False

    def _side_of(self, tx, ty):
        if tx == 0:
            return "W"
        if tx == self.cols - 1:
            return "E"
        if ty == 0:
            return "N"
        if ty == self.rows_count - 1:
            return "S"
        return None

    # --- tiles ---
    def tile(self, tx, ty):
        if 0 <= tx < self.cols and 0 <= ty < self.rows_count:
            return self.tiles[ty][tx]
        return None

    def is_solid(self, tx, ty, oob_solid=False):
        ch = self.tile(tx, ty)
        if ch is None:
            return oob_solid
        if ch == SOLID:
            return True
        if ch == BREAKABLE:
            return (tx, ty) not in self.broken
        if ch == FIGHT_GATE:
            return self.fight_active
        if ch == BOSS_LOCK:
            return not self.boss_defeated
        if ch == CRUMBLE:
            return (tx, ty) not in self.crumbled
        if ch == LOCKED:
            return not self.door_unlocked
        return False

    def is_oneway(self, tx, ty):
        return self.tile(tx, ty) == ONEWAY

    def is_spike(self, tx, ty):
        """Espinho ou água funda: os dois devolvem ao último chão seguro."""
        return self.tile(tx, ty) in (SPIKE, WATER)

    def spike_rects(self, x0, y0, x1, y1, water=True):
        """Hitboxes de perigo perto da área: espinho = metade de baixo do tile, água = tile quase todo."""
        out = []
        for ty in range(int(y0 // T) - 1, int(y1 // T) + 2):
            for tx in range(int(x0 // T) - 1, int(x1 // T) + 2):
                ch = self.tile(tx, ty)
                if ch == SPIKE:
                    out.append((tx * T + 4, ty * T + T * 0.45, T - 8, T * 0.55))
                elif ch == WATER and water:
                    out.append((tx * T, ty * T + 8, T, T - 8))
        return out

    def tiles_of(self, chars):
        return [(tx, ty) for ty, row in enumerate(self.tiles) for tx, ch in enumerate(row) if ch in chars]

    def door_at_exit(self, side, coord):
        """Porta na borda `side` mais próxima da coordenada (linha ou coluna) dada."""
        best = None
        for door in self.doors.values():
            if door.side != side:
                continue
            dist = 0 if door.lo <= coord <= door.hi else min(abs(coord - door.lo), abs(coord - door.hi))
            if best is None or dist < best[0]:
                best = (dist, door)
        return best[1] if best and best[0] <= 2 else None


OPPOSITE = {"W": "E", "E": "W", "N": "S", "S": "N"}


class WorldMap:
    def __init__(self, room_defs=None, links=None, start_room=None, chapter=0):
        """chapter 0 = mundo de testes (cavernas); 1 = navio do capítulo 1."""
        if chapter == 1:
            from . import chapter1 as R
        else:
            from . import rooms as R
        room_defs = R.ROOM_DEFS if room_defs is None else room_defs
        links = R.ROOM_LINKS if links is None else links
        self.start_room = start_room or R.START_ROOM
        self.rooms = {}
        for d in room_defs:
            self.add_room(Room(d["id"], d["name"], d["zone"], d["rows"], d.get("items", ()), d.get("npcs", ()),
                               d.get("key"), d.get("movers", ()), d.get("boss")))
        self.links = {}
        for a, b in links:
            self._link(a, b)
        self._layout()

    def add_room(self, room):
        self.rooms[room.id] = room

    def _link(self, a, b):
        for (ra, da), (rb, db) in ((a, b), (b, a)):
            door_a = self.rooms[ra].doors.get(da)
            door_b = self.rooms[rb].doors.get(db)
            if door_a is None or door_b is None:
                raise ValueError(f"Ligação inválida {a} <-> {b}")
            if OPPOSITE[door_a.side] != door_b.side:
                raise ValueError(f"Portas {a} e {b} não estão em lados opostos")
            self.links[(ra, da)] = (rb, db)

    def target_of(self, room_id, digit):
        return self.links.get((room_id, digit))

    def _layout(self):
        """Posiciona as salas no mapa-múndi seguindo as portas (busca em largura)."""
        if self.start_room not in self.rooms:
            return
        placed = {self.start_room}
        queue = deque([self.start_room])
        while queue:
            rid = queue.popleft()
            room = self.rooms[rid]
            for digit, door in room.doors.items():
                target = self.links.get((rid, digit))
                if target is None or target[0] in placed:
                    continue
                other = self.rooms[target[0]]
                od = other.doors[target[1]]
                if door.side == "E":
                    other.origin_tx = room.origin_tx + room.cols
                    other.origin_ty = room.origin_ty + door.lo - od.lo
                elif door.side == "W":
                    other.origin_tx = room.origin_tx - other.cols
                    other.origin_ty = room.origin_ty + door.lo - od.lo
                elif door.side == "N":
                    other.origin_ty = room.origin_ty - other.rows_count
                    other.origin_tx = room.origin_tx + door.lo - od.lo
                else:
                    other.origin_ty = room.origin_ty + room.rows_count
                    other.origin_tx = room.origin_tx + door.lo - od.lo
                placed.add(other.id)
                queue.append(other.id)

    def overlaps(self):
        out = []
        rooms = list(self.rooms.values())
        for i, a in enumerate(rooms):
            for b in rooms[i + 1:]:
                if (a.origin_tx < b.origin_tx + b.cols and b.origin_tx < a.origin_tx + a.cols
                        and a.origin_ty < b.origin_ty + b.rows_count
                        and b.origin_ty < a.origin_ty + a.rows_count):
                    out.append((a.id, b.id))
        return out

    def player_start(self):
        room = self.rooms[self.start_room]
        for s in room.spawns:
            if s[0] == "P":
                return room, s[1], s[2]
        return room, room.width / 2, room.height / 2

    def benches(self):
        return [(room.id, s[1], s[2]) for room in self.rooms.values() for s in room.spawns if s[0] == "B"]
