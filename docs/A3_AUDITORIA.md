# Auditoria do A3 — Maré de Mentiras

Conferência do jogo e do repositório contra as seções 3, 4, 5, 6 e 9 do enunciado da A3 (prof. Elzo).
Feita em 24/11/2026 só com leitura do código e testes sem janela (`SDL_VIDEODRIVER=dummy`,
`SDL_AUDIODRIVER=dummy`). Nenhum código do jogo foi alterado.

**Legenda:** ok = atende · parcial = existe, mas incompleto ou com risco · falta = não existe.
**Frentes:** Arte, Gameplay, Fases, Interface, Integração (ver `docs/EQUIPES.md`).

Suíte automática: 512/512 (detalhes no fim deste arquivo).

## Resumo do que precisa de ação

| Prioridade | Item | Frente |
|---|---|---|
| Alta | README sem integrantes com RA, sem regras, sem divisão de tarefas e sem declaração de IA | Integração (com o grupo) |
| Alta | Declaração de IA completa (ferramenta, finalidade, arquivos) no README — texto pronto em `docs/COMO_O_JOGO_FOI_FEITO.md`, seção 18 | Integração |
| Alta | Créditos dentro do jogo: "[Nome do integrante - RA]" e crédito de asset que já saiu do jogo | Interface |
| Média | Final de derrota: hoje é só "VOCÊ CAIU" + uma frase | Gameplay (texto: grupo, história pausada) |
| Média | Som de vitória: o final não toca efeito próprio | Gameplay |
| Baixa | Comentários desatualizados em `src/config.py` | Gameplay |
| Baixa | Ouvir o som com caixa de som de verdade (volume equilibrado nunca foi testado com áudio) | Integração |
| Baixa | Dar acesso ao repositório para o professor | Integração (Gabriel) |

---

## Seção 3 — O que entregar

| Item | Situação | Onde no código | O que fazer | Frente |
|---|---|---|---|---|
| Instruções para instalar e rodar pelo código-fonte | ok | `README.md` ("Como jogar": `pip install -r requirements.txt` e `python main.py`; `Jogar.bat`) | Deixar os pré-requisitos numa lista própria ("Python 3.10+, pip") ao reescrever o README | Integração |
| Tela inicial | ok | `src/menus.py` `MenuState` (Novo jogo, Continuar, Como jogar, Recordes, Créditos, Sair) | — | — |
| Partida | ok | `src/states.py` `PlayState` | — | — |
| Tela de fim com jogar de novo / voltar ao menu | ok | `src/states.py` `ResultsState` ("Jogar de novo", "Menu inicial"); derrota: `DeathState` ("Tentar de novo", "Menu inicial") | — | — |
| Mecânica principal clara | ok | `src/player.py` (pulo, dash, ataques, cura), `src/combat.py` | — | — |
| Condição de vitória | ok | Derrotar Caelum no Altar → `PlayState._after_boss` → `EndingState` → `ResultsState` | — | — |
| Condição de derrota | parcial | `Player.die` → `DeathState`. Perder todos os corações não encerra a partida: volta à última bola de cristal (estilo metroidvania) | Explicar isso nas regras do README ("cair não é fim de jogo; volta ao último ponto salvo") | Integração |
| Indicador na tela (pontos, vidas, tempo, progresso) | ok | `src/ui.py` `draw_hud`: corações, orbe de foco, moedas, páginas do diário (x/3), habilidades, tempo de jogo, ícone de som desligado; barra de chefe (`draw_boss_bar`); pontuação e nota na `ResultsState` | — | — |
| Lógica escrita pelo grupo / original | ok | Todo `src/` é código próprio; só assets de terceiros | Declarar a ajuda de IA (ver seção 6) | Integração |

## Seção 4 — Critérios

### Gráfico

| Item | Situação | Onde no código | O que fazer | Frente |
|---|---|---|---|---|
| Visual coerente e legível, paleta | ok | Paleta por zona em `src/config.py` (`ZONE_PALETTES`, `Colors`), fundos em `src/background.py` | — | — |
| Sprites próprios | ok | Protagonista e Rei dos Ratos (desenhos do Gabriel refinados no PixelLab), elenco em `src/elenco.py`, desenho por código em `src/pixelart.py` | — | — |
| HUD legível | ok | `src/ui.py` `draw_hud` | — | — |
| Animação | ok | `src/skins.py`, `src/sprites.py`, folhas `anim_*.png`; squash/stretch em `Player._update_visuals` | — | — |
| Feedback visual | ok | `src/effects.py` (hitstop, tremor, flash, partículas, sprites de efeito) | — | — |
| Menu, pausa e fim no mesmo estilo | ok | `ui.panel`, `ui.Menu`, fonte Alagard em todas as telas | — | — |

### Jogabilidade

| Item | Situação | Onde no código | O que fazer | Frente |
|---|---|---|---|---|
| Controles responsivos | ok | Passo fixo de 120 Hz (`PlayState.frame`), coyote time e buffer de pulo (`config.Player`) | — | — |
| Controles explicados no jogo | ok | "Como jogar" (`menus.HOWTO_PAGES`), painel de controles na pausa (`ui.draw_controls`), dica no HUD nos 2 primeiros minutos | — | — |
| Regras claras | parcial | No jogo, sim (como jogar). No README não há seção "Regras" | Escrever no README | Integração |
| Dificuldade crescente | ok | Inimigos mais variados do navio ao templo (`chapter1.py`, `creatures.ZONE_TYPES`); chefes com mais vida (`config.Boss`: 48 → 76 → 84 → 100) e 2ª fase; 3 dificuldades (`config.Game.DIFFICULTIES`) | — | — |
| Colisões | ok | `src/physics.py` `move_and_collide` (AABB contra tiles, sub-passos anti-túnel) | — | — |
| Pausa com P ou ESC | ok | `src/input.py` linha 19 (`"pause": K_ESCAPE, K_p`); `PlayState.frame` abre `PauseState` | — | — |
| Reinício sem fechar | ok | Pausa → "Reiniciar jogo" (pede confirmação; apaga o save); resultado → "Jogar de novo"; morte → "Tentar de novo" | — | — |
| Sem travamentos | ok | QA rodada 4 sem problemas abertos (`docs/QA.md`); erro grava `erro.txt` (`main.main`) | Jogar a rota inteira com gente antes da apresentação | Integração |
| Extras | ok | IA de inimigos e chefes, amuletos (power-ups), recordes salvos (`src/records.py`, `records.json`), 3 dificuldades | — | — |
| Ajuste de volume | parcial | Existe `Audio.change_volume`, mas nenhuma tela chama. Só o M (silenciar) funciona, o que já atende o enunciado | Opcional | Interface |

### Som

| Item | Situação | Onde no código | O que fazer | Frente |
|---|---|---|---|---|
| Efeito de pulo | ok | `Player._try_jump`: `jump`, `double_jump`; pouso `land` | — | — |
| Efeito de tiro | ok | `shoot` (atiradores, canhões, chefes) | — | — |
| Efeito de colisão / golpe | ok | `combat.resolve_player_attack`: `hit`, `heavy_hit`, `block`, `impact` | — | — |
| Efeito de coleta | ok | `coin`, `item`, `health_up`, `buy` | — | — |
| Efeito de dano | ok | `Player.take_hit` e `PlayState._hazard_hit`: `hurt` | — | — |
| Efeito de derrota | ok | `Player.die`: `death` | — | — |
| Efeito de vitória | parcial | Ao vencer o chefe final toca só o som de morte do inimigo; `EndingState` só troca para a música do menu | Tocar um efeito (ex.: `ability` ou `health_up`) ao abrir `EndingState` e/ou `ResultsState` | Gameplay |
| Música em loop | ok | `Audio.play_music` com `loops=-1` | — | — |
| Música diferente no menu e na partida | ok | `config.Audio.MUSIC`: menu `title_01.ogg`; partida `forest_01`/`dungeon_01` por zona; chefe `boss_01.ogg` | — | — |
| Volume equilibrado | parcial | `config.Audio.SFX_GAIN` ajusta efeito por efeito, mas o QA nunca testou com áudio (`docs/QA.md`, "O que não deu para testar") | Ouvir uma partida com som antes da apresentação | Integração |
| Silenciar com M | ok | `input.py` (`"mute": K_m`), `PlayState.frame` → `Audio.toggle_mute`; ícone no HUD; opção "Som" na pausa | — | — |
| Créditos com fonte/licença | ok | `assets/CREDITOS.md` (efeitos e músicas do Metroidvania Forge, CC BY 4.0) | — | — |
| `pygame.mixer.Sound` e `pygame.mixer.music` | ok | `src/audio.py` (`Audio.__init__` carrega `Sound`; `play_music` usa `mixer.music`) | — | — |

### Documentação

| Item | Situação | Onde no código | O que fazer | Frente |
|---|---|---|---|---|
| README com os itens da seção 5 | parcial | Ver tabela da seção 5 abaixo | Ver abaixo | Integração |
| Nomes claros e comentários | ok | Docstring em todo módulo e nas classes principais, comentários em pt-BR | Corrigir 2 comentários velhos: `config.py` linha 9 ("nome ainda não definido pelo grupo") e linha 45 ("assets/music/", a pasta é `assets/sons/musicas/`) | Gameplay |
| Pastas `src/`, `assets/img/`, `assets/sons/` | ok | Existem exatamente assim | — | — |
| `requirements.txt` | ok | `pygame-ce>=2.4` | — | — |
| Capturas ou GIF | ok | `docs/screenshots/` (9 capturas + `gameplay.gif`) no README | — | — |

### História dentro do jogo

O que existe hoje (cerca de 40 falas/textos):

| Momento | Onde | Conteúdo |
|---|---|---|
| Introdução | `src/menus.py` `INTRO_SLIDES` / `IntroState` (depois de escolher a dificuldade; ESC pula) | 5 telas: academia, Nyra escondida, viagem na Gaivota Rubra, capitã envenenada, a Maré acordando |
| Falas no Convés | `src/chapter1.py` `DIALOGS` | Capitã Maren caída (2 + 1 repetida); Caelum (4 + 1 repetida) |
| Apresentação dos chefes | `chapter1.BOSSES[...]["intro"]` / `BossIntroState` | 1 fala de cada um dos 4 chefes |
| Textos entre áreas | `chapter1.BOSSES[...]["after"]` / `DialogState`; `FLAG_MESSAGES` | 2 falas depois de Tico, Aldric e Selka; aviso "A Gaivota Rubra atracou" |
| Segredos | `chapter1.LETTERS` | 3 páginas do diário da capitã |
| Final de vitória | `chapter1.ENDING_TRUE` (6 telas) e `ENDING_NORMAL` (5 telas) / `EndingState` | Final verdadeiro (com as 3 páginas) e final comum |
| Derrota | `states.DeathState` | "VOCÊ CAIU" + "A maré quase levou você... mas a história ainda não acabou." |
| Nome da sala | HUD ao entrar em cada sala | 13 nomes |

| Item | Situação | Onde no código | O que fazer | Frente |
|---|---|---|---|---|
| Premissa | ok | `INTRO_SLIDES`, README "Sobre" | — | — |
| Conflito | ok | Capitã envenenada, tripulação enfeitiçada, Caelum e a Maré | — | — |
| Introdução | ok | `IntroState` | — | — |
| Textos entre fases | ok | Falas depois de cada chefe, aviso do navio atracado, páginas do diário | — | — |
| Falas | ok | `DIALOGS`, `BOSSES` | — | — |
| Final de vitória | ok | Dois finais (`ENDING_TRUE`, `ENDING_NORMAL`) | — | — |
| Final de derrota | parcial | Só a tela "VOCÊ CAIU" com uma frase; não há desfecho de derrota | Decidir com o grupo (história pausada). Opção simples: 2 ou 3 frases de narração na `DeathState` ou uma fala da Maren/Caelum na primeira queda. Ou assumir no README que "cair" volta ao último ponto salvo | Gameplay (texto: grupo) |
| Coerência | ok | Pistas batem (tônico → Tico → cachecol roxo → Caelum); README e jogo contam a mesma história | Observação: `config.Game.CHAPTERS` lista capítulos 2 a 5 que não existem no jogo (não aparecem na tela) | — |

## Seção 5 — Itens obrigatórios do README

| # | Item | Situação | Onde | O que fazer | Frente |
|---|---|---|---|---|---|
| 1 | Identificação (jogo, grupo, disciplina, professor, integrantes com nome e RA) | falta | `README.md` "Autor": só Gabriel, sem RA e sem nome do grupo | Seção "Identificação" com nome do grupo e tabela integrante / RA | Integração (dados: Gabriel) |
| 2 | Descrição (3–5 linhas + premissa) | ok | "Sobre" | — | — |
| 3 | Como rodar | ok | "Como jogar" | Pôr os comandos em bloco de código e citar que foi testado em outro PC | Integração |
| 4 | Controles (tabela) | ok | "Controles" | — | — |
| 5 | Regras (ganhar, perder, pontuar) | falta | Só há pistas em "Recursos" (nota S/A/B/C) | Seção "Regras": vence ao derrotar Caelum; cair volta à bola de cristal e deixa as moedas numa bolsa; pontuação = 10000 − 2×segundos − 300×quedas + 5×moedas + 1000×páginas (`ResultsState`) | Integração |
| 6 | Divisão de tarefas | falta | — | Tabela integrante / área (usar as 6 áreas de `docs/GUIA_APRESENTACAO.md`) | Integração (com o grupo) |
| 7 | Créditos (arquivo, autor, link, licença; o que o grupo criou) | ok | README aponta para `assets/CREDITOS.md`, que tem tudo isso e a lista "Feito pela equipe" | Opcional: tabela curta no próprio README | — |
| 8 | Tecnologia | ok | "Feito com" | — | — |
| 9 | Uso de IA (ferramenta, para quê, quais arquivos) | falta | Não há no README; `assets/CREDITOS.md` tem uma frase genérica | Texto definido pelo Gabriel (24/11): bloco pronto entre `<!-- INÍCIO/FIM DO BLOCO PARA O README -->` em `docs/COMO_O_JOGO_FOI_FEITO.md`, seção 18. Copiar para o README e alinhar a frase de `assets/CREDITOS.md` | Integração |
| 10 | Capturas (2+) | ok | "Capturas" (9) + GIF | — | — |

## Seção 6 — Autoria

| Item | Situação | Onde | O que fazer | Frente |
|---|---|---|---|---|
| Lógica escrita pelo grupo | ok | `src/` | Todos precisam saber explicar (ver `docs/GUIA_APRESENTACAO.md`) | Todos |
| Assets de terceiros com licença e crédito | ok | `assets/CREDITOS.md`; a feiticeira "sample" sem licença já saiu | — | — |
| Créditos dentro do jogo batem com os arquivos | falta | `src/menus.py` `CREDITS`: tem "[Nome do integrante - RA]" e "(editar em src/menus.py...)"; cita "Feiticeira (idle & walk) - protagonista", que **foi removida** do jogo; não cita Skeletons Pack (MonoPixelArt), fundos Craftpix, ToffeeCraft pelo nome, nem PixelLab | Atualizar `CREDITS` com os nomes e RAs e com a mesma lista de `assets/CREDITOS.md` (incluir PixelLab) | Interface |
| IA declarada | falta | README sem a seção; `CREDITOS.md` só com uma frase | Ver item 9 da seção 5. IA não declarada conta como violação de autoria | Integração (com o grupo) |
| Grupo sabe explicar e alterar o código ao vivo | parcial | `docs/GUIA_APRESENTACAO.md` (novo) | Cada integrante estudar a própria área e a seção geral; ensaiar as alterações ao vivo | Todos |
| Aldric (PixelLab) nos créditos | falta | `assets/img/chefes/aldric_*.png` e `assets/fontes/pixellab/aldric/` existem, mas `assets/CREDITOS.md` não cita o Aldric (só o `cavaleiro_rubro*.png` do Metroidvania Forge) | Acrescentar Aldric na linha "Personagens PixelLab" | Arte |
| Nome do autor consistente | parcial | `assets/CREDITOS.md` usa "Gabriel Lima" (PixelLab) e "Gabriel Costa" (folha de NPCs) | Usar um nome só | Arte |

## Seção 9 — Checklist final

| Item | Situação | Observação |
|---|---|---|
| Integrantes com nome e RA no README | falta | Ver seção 5, item 1 |
| Jogo original | ok | — |
| Roda do início ao fim sem travar | ok | Bot de rota inteira sem problemas nas 3 dificuldades (`docs/PENDENCIAS.md`); falta uma partida humana completa |
| Tela inicial, partida, fim com jogar de novo | ok | — |
| Vitória/derrota e indicador | ok | Derrota volta ao último ponto salvo (explicar no README) |
| Controles no jogo e no README | ok | — |
| Pausa e reinício | ok | — |
| Gráficos, HUD, animação | ok | — |
| Música e efeitos | parcial | Falta efeito de vitória; volume nunca ouvido de verdade no QA |
| História dentro do jogo (intro e final) | ok | Final de derrota só com uma frase (parcial na rubrica "excelente") |
| README completo com declaração de IA | falta | Itens 1, 5, 6 e 9 |
| Assets com autor/link/licença | ok | `assets/CREDITOS.md`; créditos do jogo desatualizados |
| Instruções testadas em outro PC | parcial | Instalador testado; rodar pelo código-fonte num PC limpo (`pip install -r requirements.txt`, `python main.py`) antes da entrega |
| Link com acesso ao professor | falta | Repositório privado: adicionar o professor como colaborador, ou entregar o .zip `A3_Jogo_NomeDoGrupo.zip` sem `build/`, `dist/`, `saves/`, `__pycache__/` |
| Apresentação ensaiada | parcial | `docs/apresentacao/MareDeMentiras-apresentacao.pptx` existe (fora do git); guia de estudo novo |

## Resultado da suíte automática

`python tests/run_tests.py` com `SDL_VIDEODRIVER=dummy` e `SDL_AUDIODRIVER=dummy` em 24/11/2026:
**512/512 verificações passaram** (578,8 s). Nada de som foi ouvido (driver de áudio falso).

Integrantes (definidos pelo Gabriel em 24/11): Gabriel Lima Costa (825251531), Arthur Santana dos Santos
(825169114), Gabriel Araujo Francisquete (826188750), Glória Fattorelli Carrion (8261106681) e o 5º
integrante (nome e RA a preencher). Divisão de áreas em `docs/GUIA_APRESENTACAO.md`.
