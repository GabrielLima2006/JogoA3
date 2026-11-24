# Como o jogo foi feito — Maré de Mentiras

Documento técnico do trabalho A3 (Usabilidade, desenvolvimento web, mobile e jogos — USJT, 2026).
Escrito para um colega de turma entender como o jogo funciona por dentro. Os trechos de código são
copiados do projeto; o caminho e a função aparecem antes de cada um.

---

## 1. Visão geral

**Maré de Mentiras** é um metroidvania 2D de ação em pixel art. A jogadora controla Nyra, uma feiticeira
de chifres, que atravessa um navio (Gaivota Rubra), uma ilha (Velmora) e um templo para descobrir quem
envenenou a Capitã Maren. São **13 salas em 3 regiões**, **4 chefes** com duas fases cada, habilidades
que abrem caminho (dash e pulo duplo), 8 amuletos, loja, 3 dificuldades e 2 finais.

- Rodar: `pip install -r requirements.txt` e `python main.py`.
- Testar: `python tests/run_tests.py` (roda sem abrir janela).

## 2. Tecnologia e por quê

| Escolha | Motivo |
|---|---|
| **Python 3.12** | Linguagem da disciplina; fácil de ler e de alterar ao vivo |
| **pygame-ce 2.5** | Biblioteca sugerida no enunciado; janela, desenho de imagens, teclado/mouse e som (`pygame.mixer`). A versão "ce" (community edition) é mantida e tem `pygame.SCALED` para a janela crescer sem borrar o pixel art |
| **JSON** (biblioteca padrão) | Save e recordes legíveis, sem dependência extra |
| **PyInstaller + Inno Setup** | Gerar `.exe` e instalador para quem não tem Python |

A biblioteca só fornece o básico (janela, imagens, sons). **Toda a lógica** — física, colisão, IA dos
inimigos, chefes, salas, save, menus — está escrita no projeto, em `src/`.

## 3. Estrutura de pastas

```
main.py            ponto de entrada: janela, laço principal e troca de estados (classe App)
requirements.txt   dependências (pygame-ce)
src/               código do jogo
  config.py        TODOS os números de balanceamento (física, pulo, dano, vida, cores, músicas)
  states.py        estados da partida: PlayState, pausa, mapa, diálogo, morte, final, resultado, loja
  menus.py         menu inicial, novo jogo, introdução, como jogar, recordes, créditos
  input.py         teclado/mouse -> ações ("jump", "dash", "pause"...)
  physics.py       corpo AABB e colisão com o mapa de tiles
  player.py        a protagonista (movimento, pulo, dash, ataques, cura, dano)
  combat.py        golpes, hitbox e projéteis
  enemies.py       IA base dos inimigos (patrulha, perseguidor, torreta, voador...)
  creatures.py     inimigos com visual próprio por região (rato, lobo, goblin, múmia...)
  bosses.py        os 4 chefes e seus ataques
  world.py         salas, portas, tiles especiais e mapa-múndi
  rooms.py         Grid: ferramenta para desenhar salas com caracteres
  chapter1.py      o mundo do jogo: as 13 salas, ligações, itens, falas e finais
  progress.py      progresso do jogador e save em JSON
  records.py       recordes (records.json)
  audio.py         efeitos (mixer.Sound) e música (mixer.music)
  ui.py            HUD, painéis, menus, mapa e inventário
  camera.py, effects.py, background.py, tiles.py, sprites.py, skins.py, elenco.py, pixelart.py ...  visual
assets/
  img/             sprites, fundos, tiles, efeitos, interface
  sons/efeitos/    efeitos .wav       sons/musicas/   músicas .ogg
  fonts/           fonte Alagard      CREDITOS.md     autor, link e licença de cada asset
tests/             testes automáticos (rodam sem janela)
tools/             scripts de arte (animar poses, importar PixelLab, gerar sons) e instalador
docs/              história, QA, capturas e estes documentos
```

## 4. Laço principal (entrada → atualização → desenho)

Fica em `main.py`, método `App.run`. A cada quadro: lê eventos (entrada), manda o estado atual se
atualizar (`frame`) e desenhar (`draw`), e mostra a tela (`flip`).

```python
# main.py — App.run
while self.running:
    dt = min(self.clock.tick(Display.FPS_CAP) / 1000.0, Display.MAX_FRAME_DT)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.WINDOWFOCUSLOST:
            # evita "tecla presa" ao trocar de janela
            self.input.reset()
            ...
        else:
            self.input.process_event(event)
    self.state.frame(dt, self.input)
    self.state.draw(self.screen)
    pygame.display.flip()
```

- **Entrada:** `src/input.py`, classe `Input`. Cada tecla vira uma **ação** (`DEFAULT_BINDINGS`):
  `"jump"` = Espaço, `"pause"` = ESC ou P, `"mute"` = M. O resto do código só pergunta
  `inp.was_pressed("jump")`, nunca a tecla.
- **Atualização em passo fixo:** `PlayState.frame` (`src/states.py`) junta o tempo do quadro num
  acumulador e roda a física em passos de 1/120 s (`Display.SIM_HZ = 120`). Assim o pulo tem a mesma
  altura em PC rápido ou lento.

```python
# src/states.py — PlayState.frame
self.accumulator += dt
while self.accumulator >= SIM_DT:
    self.accumulator -= SIM_DT
    if self.fixed_update(SIM_DT, inp):
        inp.consume()
```

- `PlayState.fixed_update` é "um passo do mundo": move plataformas, jogador (`Player.update`), inimigos
  (`e.update`), projéteis, moedas; resolve ataques (`resolve_player_attack`), contato com inimigos,
  coleta, perigos e troca de sala.
- **Desenho:** `PlayState.draw` desenha fundo em camadas, tiles, objetos, inimigos, jogador, efeitos e o HUD
  (`ui.draw_hud`).

## 5. Máquina de estados

O `App` guarda **um estado por vez** em `self.state`. Todo estado tem `frame(dt, inp)` e `draw(surf)`
(classe base `State` em `src/states.py`). Trocar de tela é só trocar o objeto:

```python
# main.py
def start_game(self, progress=None):
    self.input.reset()
    self.state = PlayState(self, progress)

def push(self, state):
    """Abre uma tela por cima da partida (pausa, mapa, loja...)."""
    self.state = state
```

| Estado | Arquivo / classe | Como entra | Como sai |
|---|---|---|---|
| Menu inicial | `menus.MenuState` | início do jogo, "Menu inicial" | Novo jogo / Continuar / Como jogar / Recordes / Créditos / Sair |
| Novo jogo | `menus.NewGameState` | "Novo jogo" | escolhe dificuldade → introdução |
| Introdução | `menus.IntroState` | depois da dificuldade | Enter avança, ESC pula → partida |
| Partida | `states.PlayState` | `App.start_game` | pausa, mapa, diálogo, morte, final |
| Pausa | `states.PauseState` | ESC ou P | Continuar, Voltar à bola, Som, Reiniciar, Menu, Sair |
| Mapa | `states.MapState` | Tab | Tab/ESC |
| Diálogo | `states.DialogState` | W perto de personagem, fim de luta | Enter avança |
| Apresentação do chefe | `states.BossIntroState` | chefe acorda | some sozinho |
| Morte | `states.DeathState` | corações chegam a 0 | "Tentar de novo" (último ponto salvo) ou menu |
| Final | `states.EndingState` | derrotar Caelum | textos → resultado |
| Resultado | `states.ResultsState` | fim do final | "Jogar de novo" ou "Menu inicial" |
| Loja, banco (bola de cristal), mensagem | `ShopState`, `BenchState`, `MessageState` | interagir / pegar item | fechar |

Pausa, mapa, diálogo etc. são **overlays** (classe `Overlay`): guardam a partida em `self.play`, desenham
a partida congelada por baixo e voltam com `App.resume(play)`. A partida não é atualizada enquanto
o overlay está na frente — por isso o jogo "congela".

## 6. Física e colisão com tiles

Cada sala é uma **grade de caracteres** (tile de 32×32 px). `#` é bloco sólido, `-` plataforma de mão
única, `^` espinho, `~` água, dígitos são portas (legenda completa no topo de `src/world.py`).

Tudo que se move é um retângulo **AABB** (`Body` em `src/physics.py`: x, y, largura, altura). A função
`move_and_collide` move o corpo **em pedacinhos de no máximo 8 px** (`Physics.MAX_STEP`) para não
atravessar paredes em alta velocidade (anti-túnel), primeiro no eixo X e depois no Y:

```python
# src/physics.py — move_and_collide
steps = max(1, int(math.ceil(max(abs(dx), abs(dy)) / Physics.MAX_STEP)))
sx = dx / steps
sy = dy / steps
for _ in range(steps):
    if sx:
        if _step_x(body, sx, tilemap, oob_solid, step_up):
            sx = 0.0
    if sy:
        res = _step_y(body, sy, tilemap, oob_solid, corner_correction, ignore_oneway)
        ...
```

`_step_x` descobre em qual coluna de tile a frente do corpo entrou e se algum tile dessa coluna é sólido;
se for, encosta o corpo na parede. `_step_y` faz o mesmo para chão e teto. Plataforma de mão única só
segura se os pés estavam **acima** dela no passo anterior. Dois "perdões" deixam o controle justo:
`CORNER_CORRECTION` (raspou a quina da cabeça no teto → desliza de lado) e `STEP_UP` (bateu numa quina
baixa → sobe nela).

Colisão entre personagens (golpe acerta inimigo, inimigo encosta no jogador) é sobreposição de
retângulos: `rects_overlap` em `src/physics.py`.

Gravidade (`Player._gravity`): mais forte na queda (`FALL_GRAVITY_MULT = 1.6`) e mais fraca no topo do pulo
quando se segura Espaço (`APEX_GRAVITY_MULT`), para o salto não parecer "flutuante".

## 7. Jogador

`src/player.py`, classe `Player(Body)`. Valores em `src/config.py` (classes `Player`, `Physics`, `Dash`,
`Combat` — **valores aprovados, não mudar sem o dono do projeto**).

- **Andar:** `_horizontal` acelera até `RUN_SPEED = 300` px/s com aceleração diferente no chão e no ar.
- **Pulo** (`_try_jump`): velocidade inicial `JUMP_VELOCITY = 820`. Soltar Espaço na subida corta o pulo
  (`JUMP_CUT_MULT`). Tem *coyote time* (ainda dá para pular 0,1 s depois de sair da borda) e *buffer*
  (apertar pouco antes de pousar também vale). Pulo duplo só depois do primeiro chefe.
- **Dash** (`_start_dash`): 950 px/s por 0,18 s, invulnerável, 1 no ar, recarga 0,45 s.
- **Ataques** (`_start_attack`, `src/combat.py`): rápido (botão esquerdo, dano 2) e pesado (botão direito,
  dano 5, quebra escudo). Cada golpe tem preparo → ativo → recuperação (`AttackSpec`). W/S + ataque mira
  para cima/baixo; golpe para baixo no ar quica no inimigo (`pogo`).
- **Cura** (`_heal_step`): segurar F gasta energia do orbe (ganha ao acertar inimigos) e devolve 1 coração.
- **Dano** (`take_hit`): perde vida, fica invulnerável 1 s, é empurrado, a tela treme e pisca. Com 0 de vida
  chama `die`, que toca `death` e avisa a partida (`PlayState.on_player_death`: soma uma queda, deixa as
  moedas numa bolsa no último chão seguro e salva).

```python
# src/player.py — Player.take_hit (resumo)
self.hp -= damage
self.invuln = P.HURT_INVULN
...
ctx.audio.play("hurt")
if self.hp <= 0:
    self.die(ctx)
```

## 8. Inimigos e IA

Base em `src/enemies.py`, classe `Enemy(Body)`: vida, dano de contato, `take_hit` (pisca, recua, explode e
solta moedas ao morrer) e `think` (a IA de cada tipo). As salas marcam inimigos com letras; `creatures.py`
troca o visual conforme a região (`TYPES` no navio, `ZONE_TYPES` na ilha, ruínas e templo).

| Letra | IA (`enemies.py`) | Como pensa | Visual por região (`creatures.py`) |
|---|---|---|---|
| `g` | `Patroller` | anda e vira ao achar parede ou borda (`wall_ahead`, `ground_ahead`) | rato (navio), lobo (ilha/ruínas) |
| `c` | `Chaser` | patrulha; ao ver o jogador (distância + linha de visão) mostra "!" e persegue; desiste se perder de vista; nunca pula de borda | capanga, goblin, múmia |
| `t` | `Turret` | fixa; brilha antes de atirar (aviso) | canhão, lich |
| `f` | `Flier` | flutua; ao ver o jogador avisa e persegue pelo ar | gaivota, diabrete, espírito |
| `j` | `Jumper` | agacha (aviso) e salta na direção do jogador | gosma da maré |
| `s` | `Shield` | escudo na frente bloqueia o golpe rápido; o pesado quebra a guarda | pirata do escudo, cavaleiro negro |
| `a` | `Gunner` | mantém distância, recua de quem chega perto, mira com aviso, atira e fica recarregando | pistoleiro, atirador de pedras |
| `k` | `Crate` | caixa quebrável que solta moedas | caixote |

A regra de design é **"avisar antes de bater"**: todo ataque perigoso tem uma pausa de aviso
(`CHASER_ALERT_TIME`, `TURRET_TELEGRAPH`...) para o jogador reagir. A dificuldade muda vida
(`enemy_hp`), agressividade e recargas (`config.Game.DIFFICULTIES`).

## 9. Chefes e padrões

`src/bosses.py`. Cada chefe herda de `Boss(Enemy)` e é uma **máquina de estados** dentro de `think`
(`self.state` = `"sleep"`, `"idle"`, `"charge"`, `"leap_tele"`...). Estados terminados em `_tele` são o
aviso antes do golpe. Com metade da vida entram na **fase 2** (mais rápidos, ataques novos).

| Chefe | Sala | Classe | Padrões |
|---|---|---|---|
| Tico, o Rei dos Ratos | Toca | `RatKing` | investida (bate na parede e fica tonto), salto, chama ratos |
| Aldric, o Cavaleiro Rubro | Gávea | `RedKnight` | transformação, cortes com aviso, salto, rajadas de vento (`Gust`) |
| Selka, a Canhoneira | Ruínas | `PirateSister` | pistola, bote (investida), canhonaço (`CannonShot`); recua se você chega perto, mas depois de alguns pulos ou encurralada parte para cima |
| Caelum, o Feiticeiro da Maré | Altar | `Sorcerer` | teleporte, ilusões que atiram (`Illusion`, sem sombra no chão), raios (`Lightning`), onda e maré que sobe (`Wave`, `Flood`) |

A luta começa em `PlayState._update_boss_fight`: com o jogador perto, o chefe acorda, o portão da arena
fecha, toca `boss_01.ogg` e aparece o cartão do chefe (`BossIntroState`). Ao morrer,
`PlayState.on_enemy_killed` marca a sala como vencida, dá a recompensa (pulo duplo, fragmento), salva e
mostra as falas de depois da luta.

## 10. Salas, portas e mapa

- As salas são desenhadas com a classe `Grid` (`src/rooms.py`) em funções de `src/chapter1.py`:

```python
# src/chapter1.py — room_cabine
g = Grid(30, 17)
g.rect(1, 1, 28, 3)          # teto
g.rect(1, 14, 28, 15)        # chão
g.door("E", 10, 13, "1")     # porta 1 na parede leste
g.hline(3, 8, 11, "-")       # cama (plataforma de mão única)
g.put(12, 13, "B").put(17, 13, "P").put(26, 13, "k")   # banco, início, caixote
```

- `ROOM_DEFS` dá nome, região, itens e chefe de cada sala; `ROOM_LINKS` liga (sala, dígito da porta) a
  (outra sala, dígito). `WorldMap` (`src/world.py`) monta tudo e confere se as portas estão em lados
  opostos.
- **Troca de sala:** `PlayState._check_transition` — quando o centro do jogador sai da sala, acha a porta,
  calcula a posição equivalente na sala vizinha e chama `load_room`. Cair pelo fundo sem porta conta como
  perigo.
- **Mapa** (Tab): `ui.draw_map`, com as salas visitadas (`progress.visited`).
- **Portas trancadas:** `D` abre com uma "chave" (bandeira da história, ex.: `atracado` depois do chefe 2);
  `=` abre quando o chefe da sala morre.

## 11. Save

`src/progress.py`, classe `Progress`: habilidades, moedas, vida extra, amuletos, salas visitadas, itens
pegos, paredes quebradas, chefes vencidos, cartas, bandeiras, quedas e tempo. Salva em JSON ao descansar na
bola de cristal, ao vencer um chefe e ao cair. A gravação é **atômica**: escreve num arquivo temporário e
troca de nome no fim, para um save não ficar corrompido se o jogo fechar no meio.

```python
# src/progress.py — Progress.save (resumo)
os.makedirs(os.path.dirname(path), exist_ok=True)
...
    json.dump(self.to_dict(), f, ensure_ascii=False, indent=1)
os.replace(tmp, path)
```

`Progress.load` devolve `None` se o arquivo não existe ou está estragado (o menu então esconde
"Continuar"). Local: `saves/save.json` pelo código-fonte; `%APPDATA%\MareDeMentiras` no jogo instalado
(`src/paths.py`). Recordes: `src/records.py` → `records.json`.

## 12. Som

`src/audio.py`, classe `Audio`:

- **Efeitos:** no início carrega cada arquivo de `assets/sons/efeitos/` como `pygame.mixer.Sound`
  (lista `SFX_NAMES`). Tocar é `audio.play("jump")`. Cada efeito tem um ganho próprio
  (`config.Audio.SFX_GAIN`) para equilibrar o volume.
- **Música:** `play_music` usa `pygame.mixer.music` com `loops=-1` (loop infinito) e fade de entrada.
  Não reinicia se a mesma música já está tocando. Menu: `title_01.ogg`; partida: `forest_01`/`dungeon_01`
  conforme a região (`config.Audio.MUSIC`); chefe: `boss_01.ogg`.
- **Silenciar:** M chama `toggle_mute`, que zera o volume da música e bloqueia os efeitos; aparece um
  ícone no HUD. Também dá para ligar/desligar na pausa.
- Se o PC não tiver placa de som, `pygame.mixer.init()` falha e o jogo segue mudo (`self.enabled = False`).

```python
# src/audio.py — Audio.play
def play(self, name):
    snd = self.sounds.get(name)
    if snd is not None and not self.muted:
        snd.set_volume(self.sfx_volume * AC.SFX_GAIN.get(name, 1.0))
        snd.play()
```

## 13. Interface e HUD

- `src/ui.py`: `draw_hud` (orbe de foco, corações que pulsam quando falta vida, moedas, páginas x/3,
  habilidades com recarga, tempo, ícone de som desligado, dica de teclas nos 2 primeiros minutos),
  `draw_boss_bar`, `draw_map`, `draw_inventory`, `draw_controls`, `Menu` (navegação por teclado e mouse),
  `panel` (moldura medieval) e `text` (fonte Alagard).
- `src/fonte.py`: a Alagard não tem acentos; o jogo compõe á, ã, ç, é... pixel a pixel.
- Janela 960×540 com `pygame.SCALED | pygame.RESIZABLE`: cresce mantendo o pixel art nítido.

## 14. Assets e licenças

Imagens, sons, músicas e fonte de terceiros vêm de pacotes gratuitos do itch.io, Craftpix e DaFont, com
licença conferida. A lista completa (pacote, autor, link, licença e arquivos) está em
[`assets/CREDITOS.md`](../assets/CREDITOS.md). Resumo:

- Efeitos visuais: Super Pixel Effects Gigapack (unTied Games), Dark VFX / Smear VFX (pimen).
- Tiles, objetos, cavaleiro, slime, efeitos sonoros e músicas: Metroidvania Forge (Michael Games, CC BY 4.0).
- Esqueletos: Skeletons Free Pack (MonoPixelArt). Fundos: Craftpix. Interface: ToffeeCraft. Comidas:
  Ghostpixxells (CC0). Textura: Screaming Brain Studios (CC0). Fonte: Alagard (Hewett Tsoi).
- Feito pelo grupo: protagonista e Rei dos Ratos (desenhos do Gabriel, refinados e animados no PixelLab),
  NPCs e chefes no PixelLab, elenco recolorido por código (`src/elenco.py`), desenhos por código
  (`src/pixelart.py`, `src/tiles.py`, `src/background.py`), poses de ataque (`tools/animar_pose.py`),
  sons de passo (`tools/gerar_sons.py`).
- Um asset sem licença confirmável (feiticeira "sample") foi retirado do jogo.

## 15. Testes automatizados e bot de QA

- `python tests/run_tests.py` roda tudo **sem abrir janela** (`App(headless=True)`). São mais de 500
  verificações em `test_mechanics.py` (pulo, dash, ataques, cura, dano), `test_world.py` (salas, portas,
  save, chefes), `test_menus.py` (telas) e `test_ship.py` (as 13 salas do jogo).
- `tests/helpers.py`, classe `Sim`: uma partida simulada em que o teste "aperta teclas"
  (`inp.simulate`) e avança o tempo.
- `try_reach` busca por força bruta uma sequência de comandos (andar, pular, dash, pulo duplo) que leve de
  um ponto a outro. Todo salto obrigatório do jogo tem um teste que prova que é possível.
- **Bot de QA** (`docs/qa/scripts/`): scripts que percorrem as 24 passagens de porta, caem em perigos,
  lutam com os chefes (um bot simples que anda, bate e desvia, nas 3 dificuldades) e salvam capturas
  em `docs/qa/`. Os resultados de cada rodada estão em `docs/QA.md`.

## 16. Instalador

1. `python -m PyInstaller ... main.py` (ou `MareDeMentiras.spec`) gera um `.exe` único com Python,
   pygame e `assets/` dentro.
2. `tools/instalador.iss` (Inno Setup 6) empacota o `.exe` num instalador em pt-BR que não pede
   administrador e cria atalho no Menu Iniciar.
3. As versões saem na página de releases do GitHub. `Jogar.bat` é a alternativa para rodar pelo código:
   instala o pygame-ce na primeira vez e abre o jogo.

## 17. Três dificuldades técnicas reais e como foram resolvidas

### 1) Cair em espinho ou água mandava o jogador para muito longe

**Problema** (QA, problema 2, rodadas 2 e 3): ao cair num perigo, o jogo devolvia o jogador à última bola
de cristal usada — às vezes do outro lado do navio. Errar o primeiro salto da ilha levava de volta à
Cabine.

**Solução:** a partida guarda o **primeiro chão firme** pisado em cada sala (`room_entry`) e o último chão
seguro (`last_safe`), atualizados em `PlayState._update_safe_spot`. Esse ponto nunca é tábua que desaba,
espinho ou plataforma móvel, e exige chão dos dois lados dos pés. `_respawn_at_safe` devolve o jogador
para lá, na mesma sala. Commit `afb7e78` e correção final na rodada 4.

```python
# src/states.py — PlayState._respawn_at_safe
room, x, y = self._spawn_point()
if room is not self.room and self.room_entry is not None:
    room = self.room
    x, y = self.room_entry
```

### 2) A chefe Selka nunca atacava se o jogador ficasse colado nela

**Problema** (QA, problema 1): a IA da Selka mandava ela recuar com um pulinho sempre que o jogador
chegava a menos de 110 px. Encostada no portão, ela pulava sem parar e nunca usava pistola, investida ou
canhão — o bot venceu 9 lutas sem levar dano.

**Solução:** contar os recuos seguidos e checar se ela está encurralada. Depois de `SISTER_MAX_HOPS`
pulos, ou sem espaço atrás, ela parte para a investida (com aviso). Coberto pelo teste
`test_selka_fights_up_close`.

```python
# src/bosses.py — PirateSister.think
if abs(dx) < 110 and self.on_ground:
    if self.hops >= BC.SISTER_MAX_HOPS or self._cornered(room, -self.direction):
        self.hops = 0
        self.state = "lunge_tele"
        ...
```

### 3) O jogo fechava ao entrar no Convés depois de uma mudança na arte

**Problema** (QA, problema 0): uma mudança em `src/elenco.py` removeu o dicionário `MODEL_OF`, mas
`src/pixelart.py` ainda o usava para desenhar a capitã caída. Qualquer partida que chegasse ao Convés
travava com `AttributeError`.

**Solução:** trocar a busca pela estrutura nova do elenco e, principalmente, criar o hábito de **rodar a
suíte completa sem janela antes de cada versão** (os testes desenham todas as 13 salas). Além disso,
`main.main` grava qualquer erro em `erro.txt` ao lado do jogo, para quem testou mandar o arquivo.

Outras que valem citar: "tecla presa" ao trocar de janela (resolvido limpando a entrada no evento
`WINDOWFOCUSLOST` em `App.run`) e o jogador atravessando paredes em queda rápida (resolvido com os
sub-passos de 8 px em `move_and_collide`).

## 18. Uso de IA

O enunciado (seção 6) pede: qual ferramenta, para quê e em quais arquivos. O mesmo texto vai no README
(seção "Uso de IA"); o bloco pronto para copiar está logo abaixo.

<!-- INÍCIO DO BLOCO PARA O README -->
### Uso de IA

| Ferramenta | Para quê | Arquivos |
|---|---|---|
| **Claude Code** (Anthropic), assistente de programação | As mecânicas mais simples foram feitas pelo grupo à mão: **movimento, pulo e tamanho da tela/janela**. O restante do código foi desenvolvido com auxílio da IA e **revisado e testado pelo grupo** | ver lista abaixo |
| **PixelLab** (pixellab.ai) | Todos os personagens foram **desenhados à mão pelo grupo** e depois aprimorados e animados com IA no PixelLab | ver lista abaixo |
| — | **História:** escrita pelo grupo (textos em `src/chapter1.py` e `src/menus.py`, `docs/HISTORIA.md`) | — |
| — | **Assets de terceiros** (itch.io, Craftpix, DaFont): não são de IA; autor, link e licença em [`assets/CREDITOS.md`](assets/CREDITOS.md) | — |

**Feito à mão pelo grupo (sem IA):** movimento e pulo da personagem (`Player._horizontal`,
`Player._gravity`, `Player._try_jump` em `src/player.py`; valores em `Player` e `Physics` de
`src/config.py`) e tela/janela (`App.__init__` em `main.py`; `Display` em `src/config.py`).

**Código desenvolvido com auxílio do Claude Code (revisado e testado pelo grupo):**

| Parte | Arquivos |
|---|---|
| Laço, estados, pausa, morte, final | `main.py` (`App.run`), `src/states.py` |
| Física e colisão com tiles | `src/physics.py`, `src/camera.py`, `src/movers.py` |
| Jogador (dash, ataques, cura, dano) e combate | `src/player.py` (exceto as funções acima), `src/combat.py`, `src/amuletos.py` |
| Inimigos | `src/enemies.py`, `src/creatures.py` |
| Chefes | `src/bosses.py` |
| Salas, portas e mapa | `src/chapter1.py` (estrutura das salas), `src/rooms.py`, `src/world.py` |
| Save e recordes | `src/progress.py`, `src/records.py`, `src/paths.py` |
| Som | `src/audio.py` |
| Interface, menus, HUD, fonte | `src/ui.py`, `src/menus.py`, `src/fonte.py`, `src/input.py` |
| Visual por código e efeitos | `src/effects.py`, `src/background.py`, `src/paisagem.py`, `src/tiles.py`, `src/pixelart.py`, `src/elenco.py`, `src/sprites.py`, `src/skins.py`, `src/objects.py` |
| Testes e bot de QA | `tests/` (`run_tests.py`, `helpers.py`, `test_*.py`), `docs/qa/scripts/` |
| Ferramentas de arte e instalador | `tools/` (`animar_pose.py`, `importar_*.py`, `gerar_*.py`, `montar_banca.py`, `desenhar_maren_caida.py`, `capturar.py`, `instalador.iss`), `MareDeMentiras.spec`, `Jogar.bat` |

**Personagens desenhados pelo grupo e aprimorados/animados no PixelLab:**
- Protagonista Nyra: `assets/img/personagens/heroina.png` (originais em `assets/fontes/heroina/`).
- Chefes: Tico, o Rei dos Ratos — `assets/img/chefes/rei_rato_{parado,andando,ataque}.png`
  (originais em `assets/fontes/rei_rato/`); Aldric — `assets/img/chefes/aldric_{parado,andando,ataque}.png`;
  Selka e Caelum — `assets/img/personagens/selka.png`, `caelum.png`, `anim_selka.png`, `anim_caelum.png`.
- Capitã Maren: `assets/img/personagens/maren.png` (`maren_caida.png` desenhada à mão com a paleta dela).
- NPCs: `assets/img/personagens/npc_*.png` e `anim_*.png` (aldeã, anciã, ancião, bardo, comerciante,
  curandeira, estudioso, ferreira, grumete, pescador).
- Inimigos: `assets/img/personagens/inimigo_lobo.png`, `inimigo_goblin.png` e as folhas `anim_*.png`
  (diabrete, espírito, lich, ladino, cavaleiro do escudo); folhas de modelos `npcs.png` e
  `feiticeira_modelos.png`.
- Originais exportados do PixelLab: `assets/fontes/pixellab/`.
<!-- FIM DO BLOCO PARA O README -->
