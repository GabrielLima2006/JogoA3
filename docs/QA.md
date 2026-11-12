# QA — Maré de Mentiras

Rodada de teste exploratório de 22–23/10/2026, feita sobre a pasta de trabalho atual (com as mudanças das outras frentes de trabalho ainda sem commit). Tudo foi rodado de novo no fim, depois que as outras sessões mexeram nos arquivos; os resultados abaixo são dessa última rodada.

- **Como foi testado:** simulação sem janela (`Sim` de `tests/helpers.py`), com scripts em `docs/qa/scripts/`. As capturas ficam em `docs/qa/` e são desenhadas pelo próprio `draw()` do jogo, em 960×540.
- **Suíte oficial:** `python tests/run_tests.py` passou com 376/376 nas duas rodadas (a final levou 518 s).
- **Gravidade:** **bloqueia** (impede de terminar) · **atrapalha** (piora bastante a experiência) · **detalhe** (acabamento).

---

## Situação na rodada 4 (12/11, versão final)

Rodada sem janela (`SDL_VIDEODRIVER=dummy`) com todos os scripts de `docs/qa/scripts/` sobre a versão final.
Suíte oficial: 510/510. **Nenhum problema aberto.**

| Item | Situação |
|---|---|
| 0, 6, 7, 8, 9, 11 | **Corrigidos** (rodada 3). Lobo da Floresta segue vivo, 0 moedas soltas. |
| 1. Selka não ataca de perto | **Corrigido.** Agora usa investida, pistola e canhonaço; dano levado 14–37 por luta. |
| 2. Volta à bola de outra sala | **Corrigido.** Canal do Porão 2 volta ao Porão 2; vala da Praia volta à Praia. |
| 3. Chefes com muitos golpes | **Corrigido.** Normal: Tico 24, Aldric 38, Selka 42, Caelum 50 golpes; lutas de 11 a 64 s. Difícil até 68 golpes e 88 s (Caelum). |
| 4, 5, 10, 12 | **Corrigidos.** Telas de morte, diário e pausa sem sobreposição; portas do teto (`conves:3`, `porao1:1`) param na sala de cima. |

Também conferido:
- 24 passagens sem prender nem dano; nenhum inimigo começa em parede nas 13 salas; 8 amuletos mudam o
  atributo certo; voltar à bola, salvar/carregar, cura e bolsa (33 moedas) funcionam; 36 lutas de chefe
  vencidas sem o chefe sair da arena.
- Sprites depois da saída da feiticeira "sample": todo inimigo, NPC e chefe das 13 salas desenha com arte
  própria, e os retratos de diálogo (Caelum, capitã caída, Tico, Aldric, Selka) também. A base "feiticeira"
  de `src/elenco.py` ficou sem arquivo, mas nenhum personagem do jogo a usa.
- Capturas do README refeitas (`docs/screenshots/`).
- Não testado: "cair pelo fundo do Cordame 1" (posição antiga do script não tem chão desde o redesenho).

## Situação na rodada 3 (03/11)

Rodado sobre o commit `305a156` mais as mudanças ainda sem commit das frentes. Todos os scripts de `docs/qa/scripts/` de novo; `qa_chefes.py` com 1 semente.

| Item | Situação |
|---|---|
| 0. Crash do `MODEL_OF` | **Corrigido** (está nos commits). Convés desenha sem erro. |
| 1. Selka não ataca de perto | **Continua.** Nas 3 dificuldades os únicos estados foram `sleep`, `idle` e `hop`; dano levado 3 em cada luta, 0 "mortes". |
| 2. Volta à bola de cristal de outra sala | **Parcial.** Bola nova no pé da Floresta resolve lá. `_respawn_at_safe` agora volta sempre à bola de propósito (comentário no código). Sem bola usada, canal do Porão 2 e vala da Praia ainda mandam à **Cabine**. |
| 3. Chefes com muitos golpes | **Continua** (26–108 golpes). Caelum: 115–164 s e 12–16 "mortes" do bot; os outros 15–37 s. |
| 4. Textos sobrepostos na tela de morte | **Continua** (y=210 e y=222 em `DeathState.draw`). |
| 5. Página 2/3 do diário | **Parcial.** O título cabe, mas encosta nas bordas da caixa, e o corpo ainda é uma linha só (`ui.text`, sem quebra). |
| 6. "loja da Vila" | **Corrigido.** |
| 7. Títulos por cima do nome da sala | **Corrigido** (o HUD esconde o nome com o jogo parado). |
| 8. Caixa de controles da pausa sobre o rodapé | **Corrigido** (a dica do HUD some na pausa). |
| 9. Lobo da Floresta se mata nos espinhos | **Corrigido** (tronco segura o lobo: vivo após 8 s, 0 moedas soltas). |
| 10. Portas no teto sem direção | **Continua** nas duas: `conves:3 -> cordame1` e `porao1:1 -> conves` com pulo reto terminam na sala de origem. |
| 11. Fontes de "FIM" e "FINAL VERDADEIRO" | **Corrigido** (os dois na fonte de título). |

Problemas novos:
- **12. Pausa: menu encosta no título "PAUSADO"** — **detalhe.** "Continuar" fica colado embaixo do título e "Sair do jogo" quase toca os painéis de inventário e controles. Captura: `docs/qa/tela_pausa.png`. Quem corrige: gameplay (`PauseState.draw` em `src/states.py`; a interface já sugeriu valores em `docs/PENDENCIAS.md`).
- Script `qa_perigos.py`: o caso "cair pelo fundo do Cordame 1" não roda mais (a posição antiga não tem chão depois do redesenho). Agora aparece como "não testado"; não é defeito do jogo.
- Ao gravar capturas dentro do OneDrive, às vezes `pygame.image.save` falha com "Couldn't open" (arquivo preso pela sincronização). Rodar de novo resolve.

Funcionou: 24 passagens sem prender e sem dano; nenhum inimigo começa em parede nas 13 salas; 8 amuletos mudam o atributo certo; pausa → voltar à bola, salvar/carregar, cura com F, morte e bolsa (33 moedas recuperadas).

## Situação na rodada 2 (23/10, cerca de 12h)

Rodado de novo sobre o commit `75085bb` mais as mudanças ainda sem commit em `src/pixelart.py` e `src/ui.py`.

| Item | Situação |
|---|---|
| 0. Crash do `MODEL_OF` | **Corrigido**, mas só na pasta de trabalho: `pixelart.corpse()` agora usa `elenco.character("capita", ...)`. O commit `75085bb` ainda trava ao desenhar o Convés. |
| 1. Selka não ataca de perto | **Continua.** Nas 9 lutas os únicos estados foram `sleep`, `idle` e `hop`. O dano levado subiu para 4–11 (provavelmente encostando nela), mas ela ainda não usou pistola, investida nem canhonaço. |
| 2. Volta à bola de cristal de outra sala | **Continua.** Canal do Porão 2 e vala da Praia sem bola usada: volta para a Cabine. Espinhos da Floresta: volta para a Praia. Nova captura: `perigo_porao2_volta_cabine.png`. |
| 3. Chefes com muitos golpes | **Continua** (26–108 golpes). Caelum ficou mais curto: 82–175 s e 6–19 "mortes" do bot no Normal, antes 161–215 s e 17–23. Tico também: 16–22 s no Normal. |
| 4. Textos sobrepostos na tela de morte | **Continua.** |
| 5. Página 2/3 do diário sai da caixa | **Continua.** |
| 6. "loja da Vila" | **Corrigido**: agora diz "loja do convés". |
| 7. Títulos por cima do nome da sala | **Continua** na Loja e no Mapa. |
| 8. Caixa de controles da pausa sobre o rodapé | Não deu para confirmar: a captura nova foi tirada depois do nome da sala sumir e o rodapé não aparece. Conferir de novo. |
| 9. Lobo da Floresta se mata nos espinhos | **Continua** (morre em 7,7 s e solta 4 moedas). |
| 10. Portas no teto sem direção | **Continua** (comportamento igual). |
| 11. Fontes de "FIM" e "FINAL VERDADEIRO" | **Continua.** |

Outras observações desta rodada:
- As 24 passagens continuam funcionando. Nenhum inimigo começa preso em parede, inclusive os novos (a Cabine e o Convés agora têm caixotes, e o Porão 1 ganhou a sentina, com rato e gosma).
- A Gávea ganhou barris de 1 tile (tiles 11 e 24, linha 16). Não é defeito do jogo, mas um bot que não pula ficava preso atrás deles e Aldric nem acordava. O bot foi ajustado para pular obstáculos.
- Os números completos da rodada 2 estão nos arquivos de saída dos scripts. A tabela do item 3 abaixo ainda é a da rodada 1.

## Problemas

### 0. Jogo fecha ao desenhar o Convés (capitã caída) — **bloqueia**
- **Erro (relatado pelo Gabriel, 23/10):** `AttributeError: module 'src.elenco' has no attribute 'MODEL_OF'` em `src/pixelart.py:224` (`corpse()` → `npc_frame(elenco.MODEL_OF["capita"])`), chamado por `objects.py:249` ao desenhar a Capitã Maren.
- **Causa:** a mudança atual (sem commit) em `src/elenco.py` removeu o dicionário `MODEL_OF`, mas `pixelart.corpse()` ainda o usa. Qualquer partida que entre no Convés trava.
- **Quem corrige:** assets (`src/elenco.py` / `src/pixelart.py`): repor `MODEL_OF` ou trocar a busca do modelo da capitã pela nova estrutura (`CAST["capita"]`).

### 1. Selka (chefe 3) não ataca nunca se a jogadora ficar colada nela — **atrapalha**
- **Tela:** Ruínas de Velmora (`ruinas`), luta contra Selka.
- **Como reproduzir:** acorde a chefe, ande até ela e fique batendo de perto (golpe rápido sem parar). Quando a jogadora está a menos de 110 px, Selka só dá o pulinho para trás (`hop`). Encostada no portão da direita, ela não sai do lugar e volta a pular, sem nunca usar pistola, investida ou canhonaço.
- **Medido:** 9 lutas de 9 (3 dificuldades × 3 sementes) vencidas com **0 de dano levado**. Os únicos estados que apareceram foram `sleep`, `idle` e `hop`. A chefe passou a luta inteira entre os tiles 29,4 e 38.
- **Captura:** `docs/qa/chefe_ruinas_normal_meio.png` (Selka encurralada no portão, piscando branco ao levar golpe).
- **Sugestão:** limitar o recuo seguido (por exemplo, depois de 1 ou 2 pulos, ou se não ganhar distância, partir para a investida).
- **Quem corrige:** gameplay (`src/bosses.py`, `PirateSister.think`).

### 2. Espinhos e água mandam de volta à última bola de cristal, mesmo que ela fique em outra sala — **atrapalha**
- **Como reproduzir (saída do script `qa_perigos.py`):**
  - Começar um jogo novo sem usar nenhuma bola, ir ao Porão 1 e cair na poça: a jogadora volta para a **Cabine** (−1 coração).
  - Sem ter usado bola, cair na vala de espinhos da Praia: volta para a **Cabine**, do outro lado do navio.
  - Usar a bola da Praia e cair nos espinhos do chão da Floresta: volta para a **Praia**.
  - Com bola na própria sala (Templo, Vergas), volta para a bola da sala, sem problema.
- **Por que atrapalha:** a vala da Praia (8 tiles, precisa de pulo duplo) é a primeira coisa da ilha. Quem errar esse salto sem ter descansado antes volta muito longe; o caso mais comum é voltar às Vergas ou à Cabine. A Floresta (40 tiles de altura, cheia de espinhos) não tem bola.
- **Capturas:** `docs/qa/perigo_porao2_volta_cabine.png`, `docs/qa/perigo_floresta_volta_praia.png`. Na rodada 2 o Porão 1 virou sentina, e o teste da água passou para o canal do Porão 2.
- **Quem corrige:** gameplay (`src/states.py`, `_respawn_at_safe`: voltar a um ponto seguro **da mesma sala**, ou à porta por onde ela entrou) e/ou level design (`src/chapter1.py`: bola de cristal na Floresta e no começo da Praia, antes da vala).

### 3. Chefes aguentam golpes demais, e o chefe final destoa dos outros — **atrapalha**
Bot simples: anda até o chefe, bate com o golpe rápido (2 de dano, arma nível 0, sem amuletos), pula golpeando para cima quando o chefe está no alto e só desvia das investidas. Não cura e não usa ataque pesado. Quando "morre", a vida volta e a luta segue, para medir o dano total. Foram 3 sementes por combinação.

| Chefe | Dificuldade | Vida | Golpes para vencer | Dano levado (3 lutas) | "Mortes" do bot | Tempo da luta |
|---|---|---|---|---|---|---|
| Tico (Toca) | Fácil (7 ♥) | 52 | 26 | 17 / 17 / 10 | 2 / 2 / 1 | 21–30 s |
| | Normal (5 ♥) | 70 | 35 | 28 / 19 / 17 | 5 / 3 / 3 | 36–45 s |
| | Difícil (4 ♥) | 94 | 47 | 30 / 27 / 22 | 7 / 6 / 5 | 45–53 s |
| Aldric (Gávea) | Fácil | 82 | 41 | 17 / 14 / 13 | 2 / 2 / 1 | 23–27 s |
| | Normal | 110 | 55 | 21 / 23 / 21 | 4 / 4 / 4 | 30–36 s |
| | Difícil | 148 | 74 | 24 / 27 / 22 | 6 / 6 / 5 | 39–43 s |
| Selka (Ruínas) | Fácil | 90 | 45 | 0 / 0 / 0 | 0 | 20 s |
| | Normal | 120 | 60 | 0 / 0 / 0 | 0 | 26 s |
| | Difícil | 162 | 81 | 0 / 0 / 0 | 0 | 35 s |
| Caelum (Altar) | Fácil | 120 | 60 | 81 / 65 / 63 | 11 / 9 / 9 | 109–143 s |
| | Normal | 160 | 80 | 118 / 111 / 87 | 23 / 22 / 17 | 161–215 s |
| | Difícil | 216 | 101–108 | 134 / 125 / 135 | 33 / 31 / 33 | 230 s ou mais (2 de 3 lutas não terminaram em 4 min) |

- 35 a 80 golpes no Normal e até 108 no Difícil é muito para um golpe de 2 de dano. As lutas viram "bater muito" e cansam, mesmo com os padrões variados.
- Caelum leva de 4 a 6 vezes mais tempo que os outros e tira muito mais vida (ele flutua a uns 150 px do chão, então quase todo golpe exige pulo). O salto de dificuldade entre o chefe 3 e o chefe 4 é grande.
- Nenhum chefe saiu da arena (0 quadros fora dos limites em 36 lutas). Os números do bot não são de jogador humano: servem para comparar os chefes entre si.
- **Capturas:** `docs/qa/chefe_<sala>_<dificuldade>_meio.png` (cada luta com o chefe abaixo de 45% de vida).
- **Quem corrige:** gameplay (vida dos chefes em `src/bosses.py`; multiplicador `enemy_hp` em `Game.DIFFICULTIES`, `src/config.py`). Não mexi nos valores aprovados de `Combat`/`Player`.

### 4. Tela de morte: dois textos um em cima do outro — **detalhe**
- **Como reproduzir:** morrer com moedas no bolso.
- **O que se vê:** "A maré quase levou você... mas a história ainda não acabou." (y=210) e "57 moedas ficaram para trás. Volte para buscá-las." (y=222) ficam sobrepostos.
- **Captura:** `docs/qa/tela_morte_com_bolsa.png`.
- **Quem corrige:** gameplay (`src/states.py`, `DeathState.draw`; o texto da bolsa deve descer uns 30 px).

### 5. Página 2/3 do diário: título e texto saem da caixa — **detalhe**
- **Como reproduzir:** pegar a carta do Cordame 2 (Vergas), ou abrir `MessageState` com `LETTERS["carta2"]`.
- **O que se vê:** o título "Diário da Capitã Maren (2/3)" encosta nas bordas da caixa de 640 px, e a frase passa da borda dos dois lados. As páginas 1 e 3 também ficam no limite.
- **Capturas:** `docs/qa/tela_carta_carta2.png`, `tela_carta_carta1.png`, `tela_carta_carta3.png`.
- **Quem corrige:** gameplay/interface (`src/states.py`, `MessageState.draw`: quebrar o texto com `ui.wrap_text` e diminuir o título ou alargar a caixa).

### 6. Texto fala de "loja da Vila", mas não existe vila — **detalhe**
- **Onde:** mapa sem mapa comprado ("Compre um na loja da Vila.") e inventário da pausa ("Mapa: não (loja da Vila)"). A loja fica no Convés.
- **Capturas:** `docs/qa/tela_mapa.png`, `docs/qa/tela_pausa.png`.
- **Quem corrige:** interface (`src/ui.py`, `draw_map` e `draw_inventory`).

### 7. Títulos das telas por cima do nome da sala — **detalhe**
- **Como reproduzir:** entrar numa sala e abrir pausa, mapa, loja, ferreiro ou bola de cristal em menos de 1,8 s.
- **O que se vê:** "PAUSADO", "Mapa", "Loja", "Ferreiro" e "Amuletos" são desenhados por cima do nome da sala ("Convés da Gaivota Rubra"), que continua visível embaixo, escurecido.
- **Capturas:** `docs/qa/tela_loja.png`, `tela_ferreiro.png`, `tela_amuletos.png`, `sis_mapa_com_bussola.png`.
- **Quem corrige:** interface (esconder o nome da sala do HUD quando houver tela por cima; `ui.draw_hud` recebe `room_name_timer`).

### 8. Pausa: a caixa de controles cobre a dica do rodapé — **detalhe**
- **O que se vê:** a última linha ("ESC ou P — pausar / inventário") fica sobre a dica "ESC pausa · Tab mapa · M som" do HUD, que aparece cortada atrás da caixa, no canto inferior direito.
- **Captura:** `docs/qa/tela_pausa.png`.
- **Quem corrige:** interface (`src/ui.py`, esconder a dica do HUD nas telas por cima).

### 9. Lobo do chão da Floresta se mata nos espinhos sozinho — **detalhe**
- **Como reproduzir:** entrar na Floresta pela Praia e esperar uns 8 s. O lobo (tile 14, linha 36) anda para a direita, entra na faixa de espinhos (colunas 20 a 46) e morre, soltando 4 moedas de graça.
- **Captura:** `docs/qa/inimigo_lobo_floresta_espinhos.png` (o lobo na beira dos espinhos).
- **Quem corrige:** level design (`src/chapter1.py`: mudar o lobo de lugar ou pôr uma parede ou limite na patrulha). Outra opção, em gameplay: inimigos que andam no chão não entram em espinhos.

### 10. Portas no teto: pular sem direção faz cair de volta pelo buraco — **detalhe**
- **Onde:** escotilha Porão 1 → Convés e mastro Convés → Cordame.
- **Como reproduzir:** pular reto para cima pela abertura, sem segurar ←/→. A jogadora entra na sala de cima e cai de volta na de baixo (`qa_portas.py`: `conves:3 -> cordame1` e `porao1:1 -> conves` terminam na sala de origem). Segurando uma direção, ela sobe e fica de pé normalmente (confirmado com `try_reach`). Não prende, mas pode confundir.
- **Quem corrige:** level design (uma plataforma ou beirada ao lado da abertura de chegada) ou gameplay (empurrão lateral na transição pelo `N`).

### 11. "FIM" e "FINAL VERDADEIRO" com fontes diferentes — **detalhe**
- O final comum termina com "FIM" na fonte gótica de título, e o verdadeiro com "FINAL VERDADEIRO" na fonte pixelada.
- **Capturas:** `docs/qa/tela_final_1cartas_4.png`, `docs/qa/tela_final_3cartas_5.png`.
- **Quem corrige:** interface/gameplay (`EndingState.draw`, em `src/states.py`).

---

## O que foi testado e funcionou

- **13 salas:** todas desenham sem erro, com capturas em 3 pontos de cada uma (`sala_<id>_<0..2>.png`). Nenhum personagem cortado, enterrado ou flutuando nas posições testadas, e nenhum inimigo começa dentro de parede ou sai do mapa em 8 s de simulação. Alguns inimigos ficam parados de propósito: caixotes, canhão e lich são fixos, e as gosmas só se mexem com a jogadora perto (a do chão andou 133 px com ela a 4 tiles).
- **24 passagens (12 portas × 2 sentidos):** todas chegam ao destino sem prender na parede e sem dano (`porta_<origem><dígito>_para_<destino>.png`).
- **4 chefes:** acordam, fecham a arena, usam a mecânica própria e não saem da arena. A recompensa do chefe 1 (pulo duplo) e a bandeira "atracado" do chefe 2 são cobertas pela suíte oficial (`test_bosses`).
- **3 páginas do diário, finais comum e verdadeiro e tela de resultado** (nota A com 1 carta, S com 3): ver `tela_final_*` e `tela_resultado_*`.
- **Loja, ferreiro** (melhora para o nível 1 e depois pede minério), **bola de cristal / amuletos:** os 8 amuletos equipam e mudam o atributo certo (Lâmina: alcance 48→62; Força: dano 2→3; Ímã: 46→190; Foco: cura 0,9→0,54 s; Vigor: 5→6 ♥; Vento: dash 950→1140 e recarga 0,45→0,27; Coletor: energia ×1,5; Bússola: marca no mapa). A grade alcança os 8. Com espaço insuficiente aparece "Espaços de amuleto insuficientes."
- **Morte e volta:** tela "VOCÊ CAIU", "Tentar de novo" volta à última bola com vida cheia, e a bolsa de moedas fica onde caiu e é recuperada.
- **Pausa** (todas as opções; "Voltar à bola de cristal" funciona), **mapa** com e sem mapa, com bússola, **salvar e continuar** (o save guarda bola, habilidades e cartas), **cura segurando F** (2 → 4 ♥).
- **Dificuldades:** Fácil 7 ♥ / inimigos ×0,75, Normal 5 ♥, Difícil 4 ♥ / ×1,35, aplicadas a chefes e inimigos.
- **Menus:** menu inicial, escolha de dificuldade, introdução, como jogar, recordes e créditos (`tela_*.png`).

## Tempo para zerar (rota direta, estimativa)

A rota inteira não foi jogada de uma vez só. A estimativa junta trechos medidos e calculados:
- **Deslocamento:** cerca de 910 tiles de caminho horizontal na rota Cabine → Porão → Toca → volta → Cordame → Gávea → volta → Praia → Floresta → Ruínas → Templo → Altar, a 300 px/s, mais uns 50 pulos. Com folga de 50% para plataformas móveis, tábuas e inimigos, dá cerca de 3,5 min.
- **Chefes (bot, Normal):** 40 + 32 + 26 + 190 s, cerca de 4,8 min.
- **Falas, apresentações e final:** cerca de 1 min.
- **Total aproximado:** **9 a 10 min no Normal** para quem já conhece o caminho, sem coletáveis. Com as 3 cartas e os amuletos, dá mais alguns minutos. Um jogador humano de primeira viagem deve levar bem mais, porque Caelum sozinho rendeu de 17 a 23 "mortes" do bot no Normal.

## O que não deu para testar

- Som, música e volume (rodou com `SDL_AUDIODRIVER=dummy`).
- Janela real: mouse, redimensionar, perda de foco, FPS e travadas em máquina fraca.
- Controle humano de verdade (sensação dos saltos, tempo de reação contra os chefes). Os números são de bot.
- Protagonista "ele" (o jogo hoje só usa "ela").
- Rota contínua do início ao fim numa única partida. Os trechos foram testados separados: portas, saltos pela suíte (`try_reach`), chefes, itens e final.
- As capturas dos menus mostram o estado depois de 0,8 s de tempo real (`qa_menus3.py`), porque as opções aparecem com animação. Sem essa espera, saem em branco na captura.

## Como rodar de novo

```bash
cd docs/qa/scripts
python qa_salas.py; python qa_portas.py; python qa_perigos.py; python qa_inimigos.py
python qa_sistemas.py; python qa_telas.py; python qa_menus3.py; python qa_lobo.py
python qa_chefes.py 1 2 3
```
`qa_chefes.py` leva alguns minutos e aceita só uma sala (por exemplo, `python qa_chefes.py ruinas 1`). `sheet.py` monta folhas de contato das capturas.
