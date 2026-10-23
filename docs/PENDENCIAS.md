# Pendências por área

## Interface

Feito (`src/ui.py`, `src/menus.py`, `tests/test_menus.py`):
- Kit visual: painéis com moldura dourada, ornamentos, teclas desenhadas nas dicas, adaga como cursor,
  títulos com degradê e contorno (vale para todos os `ui.text(..., title=True)` do jogo).
- Menu com animação de entrada, destaque deslizante e mouse que não briga com o teclado.
- HUD: orbe de foco com líquido, corações do `coracao.png` (perda pisca), moedas com contagem e "+N",
  ícones de `habilidades.png`, dica de teclas só nos 2 primeiros minutos.
- Barra de chefe com rastro de dano e pulso na fase 2; mapa e inventário em painéis.
- Menu principal, dificuldade, introdução, como jogar (abas clicáveis), recordes e créditos refeitos.
- Teste novo: mouse/teclado no menu e clique nas abas do "Como jogar".
- QA 6: "loja da Vila" virou "loja do convés" (mapa e inventário).
- QA 7 e 8: com a partida congelada (pausa, mapa, loja, ferreiro, amuletos, diálogo) o HUD esconde o nome
  da sala e a dica ESC/Tab/M; detecta pelo tempo de jogo parado há mais de 0,12 s.

Pendente (depende de `src/states.py`, que é da área de gameplay):
- Pausa: menu encosta no título "PAUSADO". Sugestão: título y=40 size=44; menu center_y=190, spacing=36;
  inventário em (40, 330); controles em (480, 318).
- MessageState e DialogState: trocar as caixas `pygame.draw.rect` por `ui.panel(...)` e a dica por
  `ui.hints(...)`. Retrato da caixa de diálogo sai quase vazio.
- QA 4 (morte: texto da bolsa 30 px abaixo), QA 5 (MessageState: quebrar o corpo com `ui.wrap_text`
  e alargar a caixa) e QA 11 (EndingState: "FINAL VERDADEIRO" com `title=True`, igual ao "FIM").
- Ideias de polimento ainda não feitas: nome da sala ao passar o mouse no mapa; tela de resultados
  com painel (ResultsState mora em `states.py`).
- Detalhes e capturas antes/depois: nota `interface.md` nas notas de trabalho da interface.

## Level design

Feito:
- As 13 salas redesenhadas em `src/chapter1.py` (já no commit aace19a). Mesmas portas e ligações; só o
  Porão 1 cresceu para baixo (24 -> 30 linhas). Parkour com rotas opcionais, 6 paredes rachadas (`X`) com
  segredos, 4 fragmentos no total (fecham +1 coração), moedas em baús, as 3 cartas escondidas (nicho sobre
  a entrada do Porão 2, cesto alto das Vergas, árvore oca da Floresta).
- Arenas: barris na Toca (a investida do Rei dos Ratos bate e ele fica tonto), barris-abrigo contra o vento
  na Gávea, arcos de pedra contra o canhonaço nas Ruínas, plataformas sob as 3 posições do Caelum e altar
  como refúgio da maré.
- `tests/test_ship.py`: listas de alcance novas, `test_crumble` na sentina, `test_secrets` novo, ajustes em
  `test_items_and_letters` e `test_bosses`.
- QA (`docs/QA.md`):
  - nº 2: bola de cristal nova no pé da Floresta (a Praia já tinha uma antes da vala);
  - nº 9: tronco caído (1 tile) na Floresta segura o lobo antes dos espinhos; meio-fio no Templo faz o
    mesmo com a múmia e o cavaleiro do chão leste;
  - nº 10 (Convés -> Cordame): resolvido pelo redesenho, há uma plataforma de pouso sobre a abertura.

Pendente:
- QA nº 10 (Porão 1 -> Convés): pular reto pela escotilha ainda faz cair de volta. Uma plataforma de mão
  única sobre a escotilha resolveria, mas aí descer ao porão exigiria apertar S, e isso não é ensinado.
  Sugestão para gameplay: empurrão lateral ao chegar por uma porta `N`.
- QA nº 2, parte de gameplay: voltar ao último chão seguro da mesma sala em vez da bola de outra sala.
- Jogar as salas de verdade para ajustar a dificuldade (posição de inimigos, largura das tábuas).
- `WALKERS` (`src/background.py`): nenhuma posição precisa mudar.

## Assets

Feito (23/10, sem commit):
- Protagonista nova (PixelLab do Gabriel) com animações de `tools/gerar_heroina.py` → `heroina.png`; antiga em `SKINS["feiticeira_antiga"]`.
- Rei dos Ratos novo (PixelLab, vista sudoeste 2x) no `draw` do chefe. Feiticeiro da Maré voltou ao desenho antigo.
- NPCs só de pacotes da internet (feiticeira "sample" + espadachim Metroidvania Forge recoloridos, chapéus que não cortam);
  múmia e cavaleiro negro = Skeletons Free Pack. Crash do `MODEL_OF` (Capitã no Convés) corrigido em `pixelart.corpse()`.
- Blocos com mais variação e paredes fundas escuras (`tiles.solid_tile`); céus Craftpix em camadas (noite, tempestade com raio, roxo, cinza).
- Respingo nas gotas do porão; sons do pacote (`heavy_charge`, `break_wood`, `explosion`, `ability`, `door`); `assets/CREDITOS.md` atualizado.
- `tools/capturar.py`: galeria de personagens e salas inteiras sem janela.

Pendente:
- Monstros ainda em `npcs.png` (lobo, goblin, diabrete, espírito, lich): trocar quando o Gabriel mandar os originais (pasta `Personagens gerados por mim`).
- Gameplay: tocar `heavy_charge` na carga do golpe forte; pôr `break_wood`, `explosion`, `ability`, `door` em `SFX_NAMES` e usar.
- Imagens sem uso: `efeitos/moedas`, `fantasma_roxo`, `veneno`, `corte_h/v`, `onda_roxa`; `objetos/poeira`, `porta`, `teclas`, `moldura_vida`; `itens/queijo, rosquinha, sanduiche, sushi`.
- `objects.draw_character` desenha o elenco 3 px acima do chão (falta `+ 3` no `midbottom`; arquivo de gameplay).
- Conferir `docs/ASSETS_ANALISE.md` (recomendações de pacotes) e licenças `[CONFIRMAR]` em `assets/CREDITOS.md`.
- **NPCs "bugados" (Gabriel, 23/10, prints do Convés):** a base do espadachim (Metroidvania Forge) recolorido ficou ruim
  (cores e chapéus soltos). Conserto mínimo feito: todos os papéis voltaram à base da feiticeira "sample" recolorida
  (`elenco.py`, sem `"base": "heroi"`) e a capitã caída agora deita de costas (`pixelart.corpse`, rotação -90).
  **Falta conferir em jogo** (parei por limite de uso: 5 h em 99%). Se ainda estiver feio: tirar os chapéus dos papéis
  ou usar o desenho provisório até chegarem os sprites do PixelLab.
