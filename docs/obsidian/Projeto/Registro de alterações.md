---
tipo: registro
---

# Registro de alterações

Mais recente primeiro. Cada entrada traz o que mudou, os arquivos e o resultado dos testes. Guia: [[Guia para IAs colaboradoras]].

## 2026-10-22 — Só a feiticeira, dash inicial, animações e elenco no estilo dela
- Gabriel achou Ele e Ela discrepantes: só a feiticeira é jogável (tela vai direto à dificuldade).
- Dash desde o começo; chefe 1 dá o pulo duplo; mastro do convés exige pulo duplo; chefe 2 dá fragmento.
- `tools/gerar_feiticeira.py` cria golpes (rápido 4, pesado 5, cima 3, baixo 2), pulo, queda, dash, dano,
  morte e aterrissagem a partir do sprite original → `feiticeira_acoes.png`. Transição parado→correndo
  (`feiticeira_partida.png`, do pacote) e inclinação na corrida.
- `src/elenco.py`: todos os humanos derivados do sprite dela (troca de paleta por região, cabelo curto,
  chapéus, porte). Capangas e piratas de escudo usam isso no lugar do herói do Metroidvania Forge.
- O pacote grátis da feiticeira só tem idle, walk e "from idle"; o resto do preview do itch é da versão paga.
- `docs/HISTORIA.md` com sinopse, atos, falas, finais e duração estimada (40–60 min).
- Release v1.0 no GitHub com exe único + zip.

## 2026-10-22 — Virada para metroidvania de ação + entrega A3
- Pedido do Gabriel: level design melhor, parkour, chefes diferenciados, gráficos bonitos, executável e repo privado.
- Mundo novo com 13 salas em 3 áreas (navio, ilha, templo) e 4 chefes com 2 fases; 3 cartas e 2 finais.
- Parkour: plataformas móveis, tábuas que desabam, espinhos, água, saltos que exigem dash/pulo duplo.
- Visual: tiles da ilha/ruínas/templo, madeira procedural, parallax, barris/caixotes, vigas, mastro com velas,
  amurada, chuva, relâmpago, vinheta, personagens em pixel art por código, efeitos Super Pixel.
- Fonte com acentos; escala da fonte revista (sem textos sobrepostos). Barra do chefe no topo.
- Menus: intro nova, como jogar (controles/objetivo/regras), recordes (pontos, quedas, cartas), créditos rolando,
  retratos com sprites reais, pausa com som e reiniciar.
- README nas 10 seções do A3 + `assets/CREDITOS.md` + screenshots em `docs/screenshots/`.
- Executável PyInstaller em `dist/MareDeMentiras/`. Repo privado GabrielLima2006/JogoA3 (sem coautor IA).

## 2026-10-22 — Assets integrados (parcial)
- Copiados para `jogo/assets/`:
  - 22 efeitos sonoros (`audio/`);
  - 3 músicas (`music/`: título no menu, forest_01 no convés, dungeon_01 no interior e no porão);
  - a fonte `alagard.ttf` (`fonts/`, usada nos títulos, menus e nomes dos personagens).
- Origem: pacotes `ch_03`, `ch_04`, `ch_05` e `ch_06` da pasta "assets internet". **A licença ainda precisa ser confirmada.**
- Código:
  - `game/paths.py`: caminhos que funcionam também num `.exe`;
  - `config.Audio` com volumes e música por zona;
  - `Audio.play_music` sem reiniciar a mesma faixa;
  - `ui.font(title=True)`;
  - `erro.txt` gravado quando o jogo quebra.
- **322/322.**
- **Falta:** gerar o `.exe` com PyInstaller para o grupo (`pip install pyinstaller`, depois `python -m PyInstaller --noconfirm --windowed --name MareDeMentiras --add-data "assets;assets" main.py`) e testá-lo; créditos dos assets na tela de Créditos; pacote Super Pixel Effects ainda não usado.

## 2026-10-22 — Etapa 2: navio do capítulo 1
- 9 salas em `game/chapter1.py`: Proa (cama para salvar + baú com Passo ilusório), Convés (cordame até a Gávea, escotilha), Tombadilho, Gávea, Salão (corpo da capitã), Cabine da capitã (porta `D` trancada), Cozinha (alçapão), Alojamento e Porão (trecho alagado `~` que exige dash, ratos).
- Personagens com diálogo (`CHARACTERS`, `DIALOGS`): imediato, amigo, irmã, cozinheira, grumete, capitã (examinar → chave).
- Motor:
  - `WorldMap(chapter=N)`;
  - tiles `D` e `~`;
  - `N` + lista `npcs` nas salas;
  - `progress.flags` / `progress.talked`;
  - `PlayState.talk_to` / `give_flag`;
  - `DialogState` (retrato, digitação);
  - fundos por zona (convés com céu e mar, interior com lanternas, porão).
- Ajustes de design após os testes de alcance: no mastro, o vão entre plataformas caiu de 4 para 3 tiles, e o cesto virou plataforma de mão única.
- Testes novos `tests/test_ship.py`: portas, alcance, porta trancada, diálogos, baú, desenho. **322/322.**

## 2026-10-22 — Etapa 1: telas do documento A3
- `game/menus.py`: menu (Novo jogo, Continuar capítulo, Como jogar, Recordes, Créditos, Sair), protagonista ele/ela, dificuldade (minutos de maré), introdução com formas de gênero, como jogar (3 páginas), recordes e créditos. `game/records.py`.
- Título provisório "Maré de Mentiras" em `config.Game`.
- `tests/test_menus.py`. **264/264.**

## 2026-10-22 — Pedidos do Gabriel após jogar
- S desce de plataforma de mão única.
- Mira por teclado: W + ataque, W + A/D na diagonal, S + ataque no ar para baixo com quique (devolve pulo duplo e dash).
- **235/235.**

## 2026-10-22 — Expansão estilo Hollow Knight (mundo de testes)
- 13 salas em cavernas: habilidades achadas no mapa, bancos, loja, ferreiro, 8 amuletos, fragmentos de vida, moedas e bolsa na morte, energia + cura (F), mapa/bússola, paredes secretas, chefe Guardião, save JSON.
- Inimigos: voador, saltador, escudeiro.
- **223/223.**

## 2026-10-22 — Protótipo inicial
- Movimento (coyote, buffer, pulo variável, pulo duplo), dash, ataques rápido e pesado, 3 inimigos, 5 salas, HUD, pausa, morte. Física em passo fixo de 120 Hz.
- Controle **aprovado pelo Gabriel**.
- **114/114.**

Voltar: [[Cérebro]]
