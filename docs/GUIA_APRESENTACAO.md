# Guia de estudo para a apresentação — Maré de Mentiras

O professor pode perguntar a **qualquer integrante** sobre **qualquer parte** do código e pedir para
**alterar um trecho ao vivo**. Este guia divide o trabalho em 5 áreas, uma por integrante: 3 de código
(Áreas 1 a 3, com alterações ao vivo) e 2 sem código (Áreas 4 e 5, em linguagem simples, com um kit
mínimo de perguntas técnicas). **Todos** precisam saber a seção "Perguntas que qualquer um deve saber".

Explicação mais longa de cada parte: [`docs/COMO_O_JOGO_FOI_FEITO.md`](COMO_O_JOGO_FOI_FEITO.md).
Apresentação: **01/12 às 21h**. Roteiro e checklist de ensaio no fim deste arquivo.

## Quem estuda o quê

| Área | Tipo | Integrante | RA |
|---|---|---|---|
| 1. Visão geral, laço principal e estados, jogador (movimento, pulo) e tela — parte feita à mão; salas, portas, mapa e save; demonstração jogando. Representante e condutor | código | Gabriel Lima Costa | 825251531 |
| 2. Combate, inimigos (IA de cada tipo), chefes e dificuldades | código | Arthur Santana dos Santos | 825169114 |
| 3. Interface (HUD, menus, pausa, telas de morte/final), som (`mixer.Sound`/`music`, silenciar com M) e configurações em `config.py` | código | Glória Fattorelli Carrion | 8261106681 |
| 4. História (premissa, conflito, apresentação, finais) e usabilidade; teste de instalação em outro PC; abre a apresentação | sem código | Gabriel Araujo Francisquete | 826188750 |
| 5. Arte e assets (personagens à mão + PixelLab, pacotes itch.io), créditos e licenças, declaração de uso de IA, slides | sem código | [5º INTEGRANTE] | [RA] |

Testes automatizados e instalador: quem responde é o Gabriel Lima Costa (resumo em
`COMO_O_JOGO_FOI_FEITO.md`, seções 15 e 16).

## Antes de qualquer alteração ao vivo (só para as Áreas 1 a 3)

1. Abra o projeto no VS Code e rode uma vez: `python main.py` (confirme que abre).
2. Faça a alteração, salve e rode `python main.py` de novo (o jogo não recarrega sozinho).
3. Para desfazer: **Ctrl+Z** no editor até voltar ao valor original, ou no terminal
   `git checkout -- src/config.py` (troque pelo arquivo alterado; apaga só as mudanças não salvas no git).
4. Os valores de `Player`, `Physics`, `Dash` e `Combat` em `src/config.py` foram aprovados pelo grupo:
   mude só para demonstrar e **desfaça logo depois**.

---

## Perguntas que qualquer um deve saber

**Como rodar o jogo?**
Python 3.10+ instalado. Na pasta do projeto: `pip install -r requirements.txt` e depois `python main.py`.
Ou dois cliques em `Jogar.bat`. Testes: `python tests/run_tests.py`.

**Em que linguagem e biblioteca foi feito?**
Python 3.12 com pygame-ce (versão mantida pela comunidade do pygame). A biblioteca só abre a janela,
desenha imagens, lê teclado/mouse e toca som; toda a lógica do jogo é nossa, em `src/`.

**Onde está o laço principal?**
`main.py`, método `App.run`. A cada quadro: lê os eventos (entrada), chama `self.state.frame(dt, input)`
(atualização) e `self.state.draw(screen)` (desenho), e `pygame.display.flip()` mostra a tela.

**Como o jogo troca de tela?**
Máquina de estados: `App.state` guarda a tela atual (menu, partida, pausa, morte, final). Cada uma tem
`frame` e `draw`. Trocar de tela é trocar o objeto (`App.start_game`, `App.to_menu`, `App.push`).

**Como o jogo detecta colisão?**
Duas formas. Com o cenário: a sala é uma grade de tiles de 32 px; `move_and_collide` (`src/physics.py`)
move o personagem em passos de até 8 px e, a cada passo, vê se entrou num tile sólido; se entrou, encosta
na parede/chão. Entre personagens: sobreposição de retângulos (`rects_overlap`) — hitbox do golpe contra
o retângulo do inimigo, retângulo do inimigo contra o do jogador.

**Por que a física roda a 120 Hz?**
Passo fixo (`PlayState.frame`): o pulo tem a mesma altura em qualquer PC, independentemente do FPS.

**Como funciona o save?**
`src/progress.py`, classe `Progress`, salva em JSON (`saves/save.json`) ao descansar na bola de cristal,
vencer chefe ou cair. Escreve num `.tmp` e troca de nome no fim (`os.replace`) para não corromper.
"Continuar" no menu usa `Progress.load`.

**Como o som toca?**
`src/audio.py`. Efeitos são `pygame.mixer.Sound` carregados no início e tocados com
`audio.play("jump")`. Música é `pygame.mixer.music` em loop (`play_music`, `loops=-1`), uma no menu e
outra por região na partida. M silencia (`toggle_mute`).

**Onde ficam os números do jogo (vida, velocidade, dano)?**
Todos em `src/config.py`.

**Como se vence e como se perde?**
Vence ao derrotar Caelum no Altar (dois finais: verdadeiro com as 3 páginas do diário, comum sem elas).
Com 0 corações a jogadora "cai": volta à última bola de cristal e as moedas ficam numa bolsa no lugar.
A pontuação final é calculada em `ResultsState` (tempo, quedas, moedas, páginas) e vira nota S/A/B/C.

**Qual foi uma dificuldade técnica?**
Ver a seção 17 de `COMO_O_JOGO_FOI_FEITO.md` (respawn longe demais nos espinhos; chefe Selka que não
atacava; jogo fechando no Convés).

**Usaram IA?**
Sim, declarado no README (seção "Uso de IA"). Duas ferramentas: o **Claude Code** (Anthropic) como
assistente de programação e o **PixelLab** para aprimorar e animar os personagens.

**O que foi feito com IA e o que foi feito à mão?**
- **À mão, pelo grupo:** as mecânicas mais simples — **movimento, pulo e tamanho da tela/janela** — e a
  **história**. Também todos os **desenhos dos personagens** (depois aprimorados e animados no PixelLab).
- **Com auxílio do Claude Code:** o restante do código (combate, inimigos, chefes, salas, interface, save,
  som, testes, instalador). Tudo foi **revisado e testado pelo grupo** (a suíte `tests/run_tests.py`
  precisa passar antes de cada versão).
- **Não é IA:** cenários, sons, músicas, fonte e parte dos inimigos vêm de pacotes gratuitos (itch.io,
  Craftpix, DaFont), com autor e licença em `assets/CREDITOS.md`.
- Lista de arquivos: `docs/COMO_O_JOGO_FOI_FEITO.md`, seção 18.

> **Atenção:** como movimento, pulo e tela foram feitos à mão, o professor tende a perguntar sobre eles.
> Quem apresenta a Área 1 (Gabriel Lima Costa) precisa saber explicar essas funções **linha por
> linha** — ver o destaque "Funções feitas à mão" nas partes A e B da Área 1.

---

## Área 1 — Visão geral, laço, estados, jogador, tela, salas e save (Gabriel Lima Costa)

### Parte A — Laço principal, estados e tela

**O que é:** o "esqueleto" do jogo: janela, laço que roda ~144 vezes por segundo, troca de telas, pausa e
entrada do teclado/mouse.

**Arquivos e funções**
- `main.py`: `App.__init__` (janela 960×540, relógio, `Input`, `Audio`), `App.run` (laço),
  `start_game`, `to_menu`, `push`, `resume`.
- `src/states.py`: `State` (base), `PlayState.frame` (acumulador e passo fixo), `PlayState.fixed_update`
  (um passo do mundo), `Overlay`, `PauseState`, `MapState`, `DeathState`, `DialogState`, `EndingState`,
  `ResultsState`.
- `src/input.py`: `DEFAULT_BINDINGS` (tecla → ação), `Input.was_pressed`, `is_held`, `consume`.
- `src/menus.py`: `MenuState`, `NewGameState`, `IntroState`, `HowToPlayState`, `CreditsState`.

**Em 1 minuto:** "O `main.py` cria a janela e roda o laço: lê eventos, atualiza o estado atual e desenha.
O estado pode ser o menu, a partida, a pausa, a morte ou o final; cada um é uma classe com `frame` e
`draw`. A partida roda a física em passo fixo de 1/120 s, juntando o tempo num acumulador, para o jogo
ser igual em qualquer PC. A pausa é um estado 'por cima' que desenha a partida congelada e volta para
ela com `resume`. O teclado não é lido direto: cada tecla vira uma ação ('jump', 'pause'), definida em
`input.py`."

**Perguntas prováveis**
1. *O que acontece quando aperto ESC?* `PlayState.frame` vê `inp.was_pressed("pause")` e faz
   `app.push(PauseState(...))`. Na pausa, ESC de novo chama `close()` → `app.resume(play)`.
2. *Por que o jogo para durante a pausa?* Porque o `App` só chama `frame` do estado atual; a partida não
   é atualizada, só desenhada por baixo.
3. *Como reinicia sem fechar?* Pausa → "Reiniciar jogo" → `app.start_game(progress.fresh_copy())`; ou
   "Jogar de novo" no resultado.
4. *O que é `dt`?* Tempo do quadro em segundos (`clock.tick`), limitado a 0,1 s para não "pular" a física
   depois de uma travada.
5. *Por que ação em vez de tecla?* Para trocar tecla num lugar só (`DEFAULT_BINDINGS`) e ter duas teclas
   para a mesma ação (ESC e P pausam).

**Funções feitas à mão (saber em detalhe): tela/janela**

```python
# main.py — App.__init__
pygame.init()
flags = 0 if headless else pygame.SCALED | pygame.RESIZABLE
self.screen = pygame.display.set_mode((Display.WIDTH, Display.HEIGHT), flags)
pygame.display.set_caption(Display.TITLE)
self.clock = pygame.time.Clock()
```

- `Display.WIDTH = 960`, `Display.HEIGHT = 540` (`src/config.py`): resolução interna; tudo é desenhado
  nesse tamanho.
- `pygame.SCALED`: o pygame amplia a imagem para a janela/tela sem borrar o pixel art.
  `pygame.RESIZABLE`: dá para arrastar a borda da janela. `headless` (testes) cria a tela sem esses flags.
- `set_caption`: título da janela. `Clock`: mede o tempo de cada quadro; `clock.tick(Display.FPS_CAP)` no
  laço limita a 144 FPS e devolve os milissegundos passados (vira o `dt`).
- Pergunta provável: *"Mude a janela para 1280×720."* → `src/config.py`, `Display`: `WIDTH = 1280`,
  `HEIGHT = 720`. Funciona, mas os menus foram posicionados para 960×540 e ficam deslocados; desfazer
  logo depois.

**Alterações ao vivo**
- **Trocar a tecla de pausa P por O.** `src/input.py`, linha 19: troque `pygame.K_p` por `pygame.K_o`.
  Rode e aperte O na partida. Desfazer: voltar para `pygame.K_p`.

---

### Parte B — Jogador (movimento, pulo, dash, ataques) e física

**O que é:** como a Nyra anda, pula, dá dash, ataca, cura e toma dano, e como qualquer corpo colide com o
cenário.

**Arquivos e funções**
- `src/physics.py`: `Body` (retângulo AABB), `move_and_collide`, `_step_x`, `_step_y`,
  `_try_corner_correct`, `rects_overlap`, `is_supported`, `line_of_sight`.
- `src/player.py`: `Player.update`, `_horizontal`, `_gravity`, `_try_jump`, `_start_dash`,
  `_start_attack`, `pogo`, `_heal_step`, `take_hit`, `die`.
- `src/combat.py`: `Attack` (fases preparo/ativo/recuperação, hitbox), `resolve_player_attack`.
- `src/config.py`: classes `Physics`, `Player`, `Dash`, `Combat`.

**Em 1 minuto:** "O jogador é um retângulo com velocidade. A cada passo de física a gente aplica
gravidade, a aceleração do teclado e chama `move_and_collide`, que move em pedaços de 8 px e encosta nos
tiles sólidos. O pulo tem coyote time e buffer, e soltar o Espaço corta a subida, então dá para controlar a
altura. O dash é rápido, curto e invulnerável. Os ataques têm preparo, parte ativa e recuperação; na
parte ativa a hitbox é testada contra os inimigos. Tomar dano tira vida, empurra, deixa invulnerável 1 s
e faz a tela tremer."

**Perguntas prováveis**
1. *Por que mover em pedaços de 8 px?* Para não atravessar parede quando está rápido (anti-túnel):
   `Physics.MAX_STEP`.
2. *O que é coyote time?* 0,1 s em que ainda dá para pular depois de sair da borda (`COYOTE_TIME`).
3. *Como funciona a plataforma que dá para atravessar por baixo?* Tile `-`: só segura se os pés estavam
   acima dela no passo anterior (`_step_y`); S faz descer (`DROP_THROUGH_TIME`).
4. *Como o golpe acerta?* `resolve_player_attack`: se o ataque está na fase ativa e a hitbox sobrepõe o
   retângulo do inimigo, chama `enemy.take_hit`; cada inimigo só leva um acerto por golpe (`hit_ids`).
5. *Como funciona a cura?* Segurar F com energia (ganha ao acertar) e no chão; depois de um tempo gasta
   `HEAL_COST` e devolve `HEAL_AMOUNT` corações (`_heal_step`).

**Funções feitas à mão (saber em detalhe): movimento e pulo** — `src/player.py`

*Movimento — `Player._horizontal(dt, move_x)`.* `move_x` vem de `inp.axis_x()` (−1 esquerda, 0 parado,
+1 direita). A velocidade não vira o alvo de uma vez: `approach` aproxima `vx` do alvo a uma taxa por
segundo, e essa taxa muda conforme a situação.

```python
target = move_x * P.RUN_SPEED * mult          # 300 px/s (mult < 1 durante ataque)
if move_x == 0:
    rate = P.GROUND_DECEL if grounded else P.AIR_DECEL          # soltou: freia
elif self.vx * move_x < 0:
    rate = P.GROUND_TURN_ACCEL if grounded else P.AIR_TURN_ACCEL  # virou: freia mais forte
else:
    rate = P.GROUND_ACCEL if grounded else P.AIR_ACCEL          # acelerando
self.vx = approach(self.vx, target, rate * dt)
```

- No ar a aceleração é menor (`AIR_ACCEL`), então dá para corrigir o salto, mas com menos controle.
- `hurt_lock > 0` (acabou de levar dano): ignora o teclado e só freia.
- Quem move de fato é `move_and_collide(self, self.vx * dt, dy, room, ...)` no fim de `Player.update`
  (`src/player.py`, linha 202), onde `dy` é o deslocamento vertical do passo.

*Gravidade — `Player._gravity(dt, inp)`.*

```python
g = PH.GRAVITY                                   # 2600 px/s²
if self.jumping and inp.is_held("jump") and abs(self.vy) < PH.APEX_THRESHOLD:
    g *= PH.APEX_GRAVITY_MULT                    # perto do topo, segurando: "flutua" um pouco
elif self.vy > 0:
    g *= PH.FALL_GRAVITY_MULT                    # caindo: gravidade 1,6x, queda mais firme
self.vy = min(self.vy + g * dt, PH.MAX_FALL_SPEED)
```

Lembrete: no pygame o **y cresce para baixo**, então pular é `vy` negativo e cair é `vy` positivo.

*Pulo — `Player._try_jump(ctx)`.*
- Pode pular se está no chão **ou** dentro do *coyote time* (`COYOTE_TIME = 0.10` s depois de sair da
  borda). Aí `self.vy = -P.JUMP_VELOCITY` (820 px/s para cima), marca `jumps_used = 1`, toca `jump`,
  solta poeira e estica o sprite (`scale_x, scale_y = 0.78, 1.25`).
- Senão, se `can_air_jump` (tem `double_jump` e ainda não usou), faz o pulo duplo com
  `DOUBLE_JUMP_VELOCITY = 720` e som `double_jump`.
- Senão, o aperto fica guardado no **buffer** (`JUMP_BUFFER = 0.13` s): se encostar no chão nesse tempo,
  pula sozinho. `update` chama `_try_jump` enquanto `jump_buffer > 0`.
- **Altura variável:** soltar Espaço na subida multiplica `vy` por `JUMP_CUT_MULT = 0.45` (pulinho);
  segurar dá o pulo inteiro (~4 tiles).

**Alterações ao vivo** (valores aprovados: desfazer depois)
- **Pulo mais alto.** `src/config.py`, linha 96: `JUMP_VELOCITY = 820.0` → `1100.0`. Rode e pule.
  Desfazer: voltar para `820.0`.
- **Correr mais rápido.** `src/config.py`, linha 88: `RUN_SPEED = 300.0` → `450.0`. Desfazer: `300.0`.

---

### Parte C — Salas, portas, mapa e save

**O que é:** como as 13 salas são desenhadas e ligadas, itens, portas trancadas, mapa e save.

**Arquivos e funções**
- `src/chapter1.py`: `room_cabine()`... `room_altar()` (salas), `ROOM_DEFS`, `ROOM_LINKS`, `START_ROOM`,
  `DIALOGS`, `LETTERS`, `BOSSES`, `ENDING_TRUE`, `ENDING_NORMAL`.
- `src/rooms.py`: `Grid` (`rect`, `hline`, `door`, `put`).
- `src/world.py`: legenda dos caracteres, `Room`, `WorldMap` (`_link`, `_layout`).
- `src/states.py`: `load_room`, `_check_transition`, `_respawn_at_safe`, `_update_safe_spot`, `save`.
- `src/progress.py`: `Progress`, `save`, `load`, `fresh_copy`. `src/records.py`.

**Em 1 minuto:** "Cada sala é uma grade de caracteres: `#` é bloco, `-` plataforma, `^` espinho, dígitos
são portas. A gente desenha as salas com a classe `Grid` em `chapter1.py` e liga as portas em
`ROOM_LINKS`. Quando o jogador sai da sala por uma porta, `_check_transition` acha a porta do outro lado e
carrega a sala vizinha. O progresso — habilidades, itens pegos, chefes vencidos — fica em `Progress` e é
salvo em JSON na bola de cristal. Os testes provam que todo salto obrigatório é possível."

**Perguntas prováveis**
1. *Como uma porta sabe para onde leva?* `ROOM_LINKS` liga (sala, dígito) a (sala, dígito);
   `WorldMap._link` confere que as portas estão em lados opostos.
2. *Como o item não volta depois de pego?* `progress.collected` guarda `"sala:índice"`; `load_room` não
   cria o item de novo.
3. *O que acontece ao cair num espinho?* Perde 1 coração e volta ao primeiro chão firme da sala
   (`_respawn_at_safe`).
4. *Como a porta para a ilha abre?* O chefe 2 dá a bandeira `atracado`; a sala com `key: "atracado"`
   destranca o `D`.
5. *Como sabem que dá para passar em todo salto?* `try_reach` (`tests/helpers.py`) testa por força bruta
   combinações de comandos; cada sala nova precisa desse teste.

**Checkpoint**
- Checkpoint = bola de cristal (`B` na sala, classe `Bench`): descansar salva (`PlayState.rest_at_bench`) e
  vira o ponto de volta ao cair (`_spawn_point`, `respawn_at_bench`).
6. *O que o save guarda?* Ver `Progress.__init__`: habilidades, moedas, amuletos, salas visitadas, itens
   pegos, paredes quebradas, chefes vencidos, cartas, quedas, tempo e a bola de cristal usada.

**Alterações ao vivo**
- **Mais moedas na Cabine.** `src/chapter1.py`, em `ROOM_DEFS`, a linha da `"cabine"`: troque
  `("coins", 15)` por `("coins", 500)`. Comece um **novo jogo** e pegue o baú da prateleira.
  Desfazer: voltar para `15`.
- **Começar com pulo duplo.** `src/chapter1.py`, linha 330: `START_ABILITIES = ("dash",)` →
  `("dash", "double_jump")`. Novo jogo: o pulo duplo já funciona na Cabine. Desfazer: voltar a
  `("dash",)`.

---

## Área 2 — Combate, inimigos, chefes e dificuldades (Arthur Santana dos Santos)

**O que é:** como os golpes acertam (combate), a IA dos inimigos comuns, os 4 chefes e as 3 dificuldades.

**Arquivos e funções**
- `src/combat.py`: `Attack` (fases preparo → ativo → recuperação, `hitbox`), `resolve_player_attack`
  (golpe contra inimigos, defesa do escudo, quique para baixo), `ProjectileSystem` (tiros).
- `src/config.py`: `Combat.QUICK` (dano 2) e `Combat.HEAVY` (dano 5, quebra escudo) — valores aprovados.
- `src/enemies.py`: `Enemy` (`take_hit`, `update`, `think`), `Patroller`, `Chaser`, `Turret`, `Flier`,
  `Jumper`, `Shield` (`blocks`), `Gunner`, `spawn_enemies`.
- `src/creatures.py`: visual por região (`Rat`, `Wolf`, `Goblin`, `Mummy`...), `TYPES`, `ZONE_TYPES`.
- `src/bosses.py`: `Boss` (`wake`, fase 2 com metade da vida), `RatKing`, `RedKnight`, `PirateSister`,
  `Sorcerer`, `Illusion`, projéteis (`Bomb`, `Lightning`, `Wave`, `Flood`, `Gust`, `CannonShot`).
- `src/states.py`: `_update_boss_fight` (acorda o chefe), `on_enemy_killed` (moedas, recompensa).
- `src/config.py`: `Enemies`, `Boss`, `Game.DIFFICULTIES`.

**Em 1 minuto:** "Todo inimigo herda de `Enemy` e tem um método `think` com a IA. O patrulheiro anda e
vira na parede ou na borda; o perseguidor vê o jogador por distância e linha de visão, mostra um '!' e
corre atrás; a torreta brilha antes de atirar; o escudo bloqueia o golpe rápido. Todo ataque tem um aviso
antes. Os chefes são máquinas de estado: `sleep`, `idle`, estados de aviso terminados em `_tele` e o
golpe. Com metade da vida entram na fase 2, mais rápidos. A dificuldade muda vida e agressividade."

**Perguntas prováveis**
1. *Como o inimigo sabe que viu o jogador?* Distância (`CHASER_DETECT_RANGE`) + mesma altura aproximada
   + `line_of_sight` (nenhum tile sólido no meio).
2. *Por que o inimigo não cai da plataforma?* `ground_ahead` testa se há chão à frente; se não, ele vira.
3. *Como é a IA de um chefe?* Um `if` por estado em `think`; um sorteio com peso (`choose`) escolhe o
   próximo ataque; cada ataque tem um estado de aviso antes.
4. *O que é a fase 2?* Propriedade em `Boss` que fica verdadeira com vida ≤ 50%; o chefe acelera e ganha
   ataques.
5. *Onde muda a vida dos chefes?* `src/config.py`, classe `Boss`: `HP_RAT_KING`, `HP_RED_KNIGHT`,
   `HP_PIRATE_SISTER`, `HP_SORCERER`, multiplicada pela dificuldade.

**Dificuldades**
- `src/config.py`, `Game.DIFFICULTIES`: Fácil (+2 corações, inimigos com 75% da vida), Normal, Difícil
  (−1 coração, 135% da vida, recargas menores). Escolhida em `NewGameState` e guardada em
  `progress.difficulty`; `PlayState` aplica nos inimigos e chefes ao criá-los.
6. *Onde muda a dificuldade?* `Game.DIFFICULTIES` em `src/config.py` (ex.: `"hp_bonus"`, `"enemy_hp"`).
7. *Como o golpe acerta o inimigo?* `resolve_player_attack`: na fase ativa, se a hitbox do golpe sobrepõe o
   retângulo do inimigo (`rects_overlap`), chama `enemy.take_hit` (tira vida, pisca, empurra, atordoa);
   cada inimigo só leva um acerto por golpe (`hit_ids`). Se o escudo defende (`blocks`), sai faísca e quem
   é empurrado é o jogador.
8. *O que é hitstop?* Uma pausa de centésimos de segundo no acerto (`effects.add_hitstop`) para o golpe
   "pesar"; o pesado tem mais (`hitstop=0.085`).

**Alterações ao vivo**
- **Rei dos Ratos com menos vida.** `src/config.py`, linha 289: `HP_RAT_KING = 48` → `10`. Rode,
  vá à Toca (Porão → Porão Alagado → Toca) e veja a barra cair rápido. Desfazer: `48`.
- **Perseguidor mais rápido.** `src/config.py`, linha 199: `CHASER_SPEED = 165.0` → `300.0`. Os capangas
  do Porão correm bem mais. Desfazer: `165.0`.

---

## Área 3 — Interface, som e configurações (Glória Fattorelli Carrion)

**O que é:** HUD, menus, pausa, telas de morte, final e resultado; efeitos sonoros, músicas e silenciar;
e o arquivo de configurações `src/config.py`.

**Arquivos e funções**
- `src/audio.py`: `SFX_NAMES`, `Audio.__init__` (carrega `mixer.Sound`), `play`, `toggle_mute`,
  `play_music` (`mixer.music`).
- `src/config.py`: `Audio` (`SFX_VOLUME`, `MUSIC_VOLUME`, `SFX_GAIN`, `MUSIC`), `Colors`.
- `src/ui.py`: `draw_hud`, `draw_boss_bar`, `draw_map`, `draw_inventory`, `draw_controls`, `Menu`,
  `panel`, `text`.
- `src/menus.py`: telas do menu, `INTRO_SLIDES`, `HOWTO_PAGES`, `CREDITS`. `src/fonte.py` (acentos).

**Em 1 minuto:** "O `Audio` carrega todos os efeitos como `pygame.mixer.Sound` quando o jogo abre; quem
quer um som chama `audio.play('jump')`. A música usa `pygame.mixer.music` em loop e troca por região: uma
no menu, outra no navio, outra no templo e uma de chefe. M silencia e aparece um ícone no HUD. O HUD fica
nos cantos: orbe de cura, corações, moedas, páginas do diário, habilidades e tempo. Os menus são a mesma
classe `Menu`, que funciona com teclado e mouse."

**Perguntas prováveis**
1. *Diferença entre `Sound` e `music`?* `Sound` fica todo na memória e pode tocar vários ao mesmo tempo
   (efeitos curtos). `music` toca um arquivo longo por vez, lido aos poucos (trilha).
2. *Como a música do menu é diferente da partida?* `MenuState` chama `play_music(MUSIC["menu"])`;
   `load_room` chama `play_music` da região; a luta chama `MUSIC["boss"]`.
3. *E se o PC não tiver som?* `pygame.mixer.init()` dá erro, `enabled` fica falso e o jogo segue mudo.
4. *Como o volume fica equilibrado?* `SFX_GAIN` diminui efeitos que vêm altos (moeda, passo...).
5. *Como o HUD mostra o último coração piscando?* `draw_hud`: com 2 corações ou menos, o último usa um
   quadro animado conforme o tempo.

**Telas de pausa, morte e final** (`src/states.py`)
- `PauseState`: menu Continuar / Voltar à bola de cristal / Som / Reiniciar (pede confirmação) / Menu /
  Sair; desenha a partida escurecida (`ui.dim`), o inventário e os controles.
- `DeathState`: "VOCÊ CAIU", aviso das moedas perdidas, "Tentar de novo" ou "Menu inicial".
- `EndingState`: textos do final, letra por letra; `ResultsState`: tempo, quedas, moedas, páginas,
  pontuação, nota S/A/B/C, grava recorde, "Jogar de novo" ou "Menu inicial".
6. *Como a pausa congela o jogo?* É um estado por cima: o `App` só atualiza o estado da frente; a pausa
   desenha a partida parada por baixo e volta com `close()` → `app.resume(play)`.
7. *Como funciona o M?* `PlayState.frame` vê `was_pressed("mute")` e chama `audio.toggle_mute()`, que zera
   o volume da música e bloqueia os efeitos; `draw_hud` mostra um alto-falante riscado.

**Configurações — `src/config.py`**
- Um arquivo só com todos os números do jogo, separados em classes: `Game` (título, dificuldades),
  `Audio` (volumes, músicas), `Display` (tamanho da tela, FPS), `Physics`/`Player`/`Dash`/`Combat`
  (valores aprovados, não mexer sem o grupo), `Enemies`, `Boss`, `Colors`...
- Unidades: distâncias em pixels, velocidades em px/s, tempos em segundos (docstring do arquivo).
8. *Por que tudo num arquivo só?* Para ajustar o jogo sem caçar números no código; qualquer mudança de
   balanceamento é uma linha.

**Alterações ao vivo**
- **Mudar o texto da tela de morte.** `src/states.py`, linha 1258: troque `"VOCÊ CAIU"` por
  `"TENTE DE NOVO"`. Caia num espinho até zerar os corações para ver. Desfazer: voltar o texto.
- **Música mais alta.** `src/config.py`, linha 41: `MUSIC_VOLUME = 0.32` → `0.8`. Desfazer: `0.32`.
- **Cor do relógio do HUD.** `src/ui.py`, linha 754: troque `Colors.UI_TEXT` por `(255, 214, 140)`
  (dourado). O tempo no canto superior direito muda de cor. Desfazer: voltar `Colors.UI_TEXT`.

---

## Partes sem código (Gabriel Araujo Francisquete e [5º INTEGRANTE])

Esta seção é em linguagem simples e não exige ler código. Alterações ao vivo ficam com os três
integrantes de código; se o professor pedir uma alteração a vocês, digam que vão mostrar com o
integrante responsável e chamem quem cuida daquela área.

### Kit mínimo de perguntas técnicas (para os dois)

O professor pode perguntar a qualquer um. Respostas curtas, com as palavras certas:

1. **Como roda o jogo?** "Precisa do Python instalado. Na pasta do jogo, roda `pip install -r
   requirements.txt` (instala o pygame-ce) e depois `python main.py`. Ou dois cliques no `Jogar.bat`. Para
   quem não tem Python, tem o instalador do Windows."
2. **Que linguagem e biblioteca?** "Python, com a biblioteca pygame-ce, que é a que a disciplina usa.
   Ela abre a janela, desenha as imagens, lê teclado e mouse e toca o som. As regras do jogo foram
   programadas por nós."
3. **O que é o laço principal?** "É uma repetição que roda o tempo todo enquanto o jogo está aberto, umas
   144 vezes por segundo. Cada volta faz três coisas: lê o que o jogador apertou, atualiza o mundo (move
   personagens, confere golpes) e desenha a tela. Fica no `main.py`."
4. **Como o jogo sabe que bateu na parede?** "O cenário é uma grade de quadradinhos de 32 pixels; cada
   quadradinho é parede, chão, espinho ou vazio. A personagem é um retângulo. A cada passo o jogo move o
   retângulo um pouquinho e vê se ele entrou num quadradinho de parede; se entrou, encosta ele na parede e
   para. Isso fica em `physics.py`."
5. **Como salva?** "Quando a jogadora descansa na bola de cristal (ou vence um chefe), o jogo grava num
   arquivo de texto JSON o que ela já conquistou: habilidades, moedas, itens pegos, chefes vencidos. No
   menu, 'Continuar' lê esse arquivo."
6. **Como toca o som?** "Os efeitos (pulo, golpe, moeda) são carregados quando o jogo abre e tocados na
   hora da ação. A música toca em repetição e muda: uma no menu, outra em cada região e outra nos chefes.
   A tecla M silencia."
7. **Como os inimigos pensam?** "Cada tipo tem uma regra simples: o patrulheiro anda e vira na parede; o
   perseguidor, quando vê a jogadora, mostra um '!' e corre atrás; o atirador avisa antes de atirar. Os
   chefes alternam ataques e sempre dão um aviso antes do golpe."
8. **Usaram IA?** Ver a resposta "O que foi feito com IA e o que foi feito à mão?" na seção geral —
   falar igual a todo o grupo.

### Área 4 — História e usabilidade; teste de instalação (Gabriel Araujo Francisquete)

**O que é:** a história contada dentro do jogo, se o jogo é fácil de entender e controlar, e a prova de
que ele instala em outro computador. Também abre a apresentação (história e objetivo).

**A história em 1 minuto** (escrita pelo grupo)
"No reino de Aurel, há dez anos, uma ilusão saiu de controle na academia de magia e um aprendiz,
Caelum, foi expulso. Nyra, uma aprendiz com chifres, ficou calada. Hoje ela viaja escondida sob o capuz
no navio da Capitã Maren rumo à ilha de Velmora, onde gente some toda lua cheia. Numa noite de
tempestade a capitã cai envenenada e a tripulação parece enfeitiçada. Nyra atravessa o navio, enfrenta
três pessoas que foram enganadas — Tico, o grumete; Aldric, o imediato; e Selka, a canhoneira — chega à
ilha e descobre que o culpado é Caelum, que quer acordar a Maré sob o templo para se vingar. O objetivo é
derrotá-lo. Se a jogadora achar as 3 páginas escondidas do diário da capitã, vê o final verdadeiro, em
que Nyra finalmente conta a verdade."

**Onde a história aparece no jogo** (para mostrar, não precisa abrir código)
| Parte (enunciado) | No jogo |
|---|---|
| Premissa e conflito | Introdução de 5 telas depois de escolher a dificuldade |
| Apresentação | Falas da capitã e de Caelum no Convés; cartão com uma fala de cada chefe |
| Textos entre fases | Falas de cada chefe derrotado; aviso "A Gaivota Rubra atracou"; páginas do diário |
| Desfecho | Final verdadeiro (com as 3 páginas) e final comum; tela "VOCÊ CAIU" ao perder todos os corações |

(Os textos ficam em `src/chapter1.py` e `src/menus.py`, se alguém perguntar onde.)

**Usabilidade — o que falar**
- Controles explicados no próprio jogo: tela "Como jogar" no menu, quadro de controles na pausa e dicas
  na tela nos primeiros 2 minutos (ESC pausa, Tab mapa, M som).
- Feedback: tudo que acontece tem resposta visual e sonora — a tela treme e pisca ao levar dano, o
  inimigo pisca branco ao ser atingido, partículas no pulo e no golpe, som em cada ação.
- Avisos antes do perigo: todo ataque de inimigo ou chefe tem uma "preparação" visível.
- Justiça: cair no espinho volta ao começo da mesma sala (não para longe); ao perder, as moedas ficam
  numa bolsa para buscar de volta; 3 dificuldades.
- HUD nos cantos para não cobrir a ação: corações, moedas, páginas e tempo.

**Teste de instalação em outro PC** (fazer antes de 29/11 e contar na apresentação)
1. Num computador que nunca rodou o jogo, instalar o Python 3.10 ou mais novo (marcar "Add to PATH").
2. Baixar o projeto, abrir o terminal na pasta e rodar `pip install -r requirements.txt`.
3. Rodar `python main.py` e jogar até a primeira sala.
4. Testar também o instalador `MareDeMentiras-Setup.exe` (página de versões do GitHub).
5. Anotar o que deu errado (se deu) e como resolveu.

**Perguntas prováveis**
1. *Qual é a premissa e o conflito?* A capitã foi envenenada e a tripulação enfeitiçada; Nyra precisa
   descobrir quem foi. O culpado é Caelum.
2. *Quantos finais?* Dois: verdadeiro (com as 3 páginas do diário) e comum. Perder todos os corações não
   encerra o jogo: volta ao último ponto salvo.
3. *Como o jogador aprende os controles?* "Como jogar" no menu, controles na pausa, dicas na tela.
4. *Testaram em outro PC?* Sim: [contar o teste feito].
5. *Por que essa história?* [Resposta do grupo.]

### Área 5 — Arte, assets, créditos, uso de IA e slides ([5º INTEGRANTE])

**O que é:** de onde vêm as imagens, sons e músicas, as licenças, como os personagens foram feitos, a
declaração de IA e os slides da apresentação.

**Em 1 minuto**
"Todos os personagens foram desenhados à mão pelo grupo e depois aprimorados e animados com IA no
PixelLab. Cenários, efeitos visuais, sons, músicas e a fonte vêm de pacotes gratuitos do itch.io,
Craftpix e DaFont; para cada um anotamos autor, link e licença no arquivo `assets/CREDITOS.md`, e os
créditos também aparecem no jogo. Tiramos do jogo um desenho cuja licença não dava para confirmar.
Algumas coisas são desenhadas pelo próprio código, como os ratos, as gaivotas e a decoração do navio."

**Pacotes de terceiros** (detalhes em `assets/CREDITOS.md`)
- Efeitos visuais: Super Pixel Effects Gigapack (unTied Games) e efeitos do pimen.
- Cenário, objetos, slime, cavaleiro, **efeitos sonoros e músicas**: Metroidvania Forge (Michael Games),
  licença CC BY 4.0 (pode usar e alterar dando crédito).
- Esqueletos (MonoPixelArt), fundos de céu (Craftpix), molduras da interface (ToffeeCraft), comidas
  (Ghostpixxells, domínio público), textura (Screaming Brain Studios, domínio público).
- Fonte Alagard (Hewett Tsoi, DaFont); os acentos foram montados pelo jogo.

**Uso de IA** — saber de cor (mesmo texto do README):
- **Claude Code** (Anthropic), assistente de programação: movimento, pulo e tamanho da tela feitos à mão
  pelo grupo; o resto do código com auxílio da IA, revisado e testado pelo grupo.
- **PixelLab**: personagens desenhados à mão pelo grupo e aprimorados/animados com IA.
- **História:** escrita pelo grupo. **Assets de terceiros:** não são IA, estão nos créditos.
- Lista de arquivos: `docs/COMO_O_JOGO_FOI_FEITO.md`, seção 18.

**Slides** (4 a 5, como o professor sugeriu): `docs/apresentacao/MareDeMentiras-apresentacao.pptx`.
Sugestão: 1) título, grupo e RAs; 2) história e objetivo; 3) como construímos (Python + pygame-ce,
laço principal, estrutura de pastas); 4) quem fez o quê + dificuldade técnica; 5) uso de IA e créditos.

**Perguntas prováveis**
1. *Os assets podem ser usados?* Sim, todos gratuitos e com licença conferida; os que pedem crédito estão
   creditados no arquivo de créditos e na tela de créditos.
2. *O que o grupo criou?* Os desenhos dos personagens, a história, o código e as fases; a lista está em
   "Feito pela equipe" no arquivo de créditos.
3. *Como a IA foi usada na arte?* Os desenhos do grupo foram levados ao PixelLab para melhorar o traço e
   gerar as animações (parado, andando, atacando).
4. *Como a animação aparece no jogo?* Cada personagem tem uma "folha" com vários quadros lado a lado; o
   jogo troca o quadro várias vezes por segundo, como um desenho animado.
5. *Por que tiraram um sprite?* Não achamos autor nem licença confirmáveis; preferimos não usar.

---

## Roteiro da apresentação (~10 min) — 01/12 às 21h

Segue o roteiro do professor: história e objetivo → demonstração → o que cada um fez → dificuldade
técnica → uso de IA. O Gabriel Lima Costa conduz e fica no teclado o tempo todo.

| Tempo | Parte | Quem fala | O que mostrar / dizer |
|---|---|---|---|
| 0:00–1:15 | História e objetivo | Gabriel Araujo Francisquete | Apresenta o grupo e o jogo; com o Gabriel Lima no teclado: Novo jogo → introdução (5 telas). Premissa, conflito, objetivo (derrotar Caelum), 2 finais e as 3 páginas do diário |
| 1:15–4:15 | Demonstração jogando | Gabriel Lima Costa (joga e narra) | Cabine (andar, pular, dash) → Convés (fala com Caelum e a capitã) → Porão (inimigos) → luta com Tico. No caminho: P (pausa), M (som), Tab (mapa), bola de cristal (salvar). Diz que é Python + pygame-ce e mostra o laço em `main.py` |
| 4:15–7:15 | O que cada um fez (≈35 s cada) | cada integrante, na ordem da tabela | Gabriel Lima: laço, estados, movimento, pulo e tela (à mão), salas e save. Arthur: combate, IA dos inimigos, chefes e dificuldades. Glória: interface, som e `config.py`. Gabriel Araujo: história, usabilidade e teste de instalação. [5º INTEGRANTE]: arte, assets, créditos e slides |
| 7:15–8:30 | Uma dificuldade técnica | Arthur Santana dos Santos | A chefe Selka que não atacava de perto e a correção com contador de recuos (`COMO_O_JOGO_FOI_FEITO.md`, seção 17.2). Alternativa: Gabriel Lima com o respawn longe demais nos espinhos (17.1) |
| 8:30–9:30 | Uso de IA | [5º INTEGRANTE] | Claude Code como assistente de programação (revisado e testado pelo grupo); movimento, pulo, tela e história feitos à mão; personagens desenhados pelo grupo e animados no PixelLab; assets de terceiros com licença |
| 9:30–10:00 | Encerramento | Gabriel Lima Costa | Agradece e abre para perguntas (perguntas de código vão para Gabriel Lima, Arthur ou Glória conforme a área) |

Plano B: se o jogo travar ou o PC falhar, mostrar `docs/screenshots/gameplay.gif` e as capturas do README,
e reabrir pelo `.exe` portátil.

## Checklist de ensaio (29–30/11)

- [ ] PC da apresentação: rodar `pip install -r requirements.txt` e `python main.py` pelo código-fonte;
      deixar também o `.exe` portátil à mão.
- [ ] Testar som com caixa/fone de verdade (música do menu, da partida, efeitos, M para silenciar).
- [ ] Save limpo para a demonstração (Novo jogo, dificuldade Fácil ou Normal) e um save já perto da Toca,
      caso falte tempo.
- [ ] Cronometrar o roteiro inteiro duas vezes; ficar em 10 min.
- [ ] Cada integrante explica a própria área em 1 minuto sem ler.
- [ ] Gabriel Lima, Arthur e Glória fazem **uma alteração ao vivo** da própria área e desfazem (Ctrl+Z ou
      `git checkout`).
- [ ] Gabriel Araujo e [5º INTEGRANTE] respondem o "Kit mínimo de perguntas técnicas" sem ler.
- [ ] Gabriel Araujo conta o teste de instalação em outro PC; [5º INTEGRANTE] revisa os slides.
- [ ] Rodada de perguntas cruzadas: os 3 de código respondem 3 perguntas da área de **outro** integrante;
      todos respondem a seção "Perguntas que qualquer um deve saber".
- [ ] Gabriel Lima Costa explica `_horizontal`, `_gravity`, `_try_jump` e `App.__init__` linha por linha.
- [ ] Todos sabem responder "o que foi feito com IA e o que foi feito à mão?" com as mesmas palavras.
- [ ] README atualizado (integrantes e RA, regras, divisão de tarefas, uso de IA) e créditos do jogo
      corrigidos (ver `docs/A3_AUDITORIA.md`).
- [ ] Professor com acesso ao repositório (ou .zip entregue).
- [ ] Preencher nome e RA do 5º integrante.
