# Pendências por área

## Gameplay

Feito (`src/states.py`, `src/bosses.py`, `src/config.py`, `src/player.py`, `src/audio.py`, testes):
- QA 2: espinhos e água voltam ao **primeiro chão firme da sala atual** (perto da porta de entrada), nunca
  tábua que desaba nem plataforma móvel. Bola de cristal só se ela estiver na própria sala ou se a sala
  ainda não teve chão firme. `tests/test_ship.py` (`test_water_returns_to_checkpoint`) ajustado para isso.
- QA 10: porta no teto (`N`) sem direção apertada leva a jogadora até a beirada do buraco
  (`Doors.CEILING_NUDGE_*` em `config.py`). Testado em Porão 1 -> Convés e Convés -> Cordame.
- QA 1: Selka recua no máximo 2 pulinhos seguidos (`Boss.SISTER_MAX_HOPS`); encurralada ou depois disso,
  investe com aviso e fica exposta na recuperação.
- QA 3: vida dos chefes no `config.py` (`Boss.HP_*`): 48 / 76 / 84 / 100 (24 / 38 / 42 / 50 golpes
  rápidos no Normal). Caelum desce cansado (estrelinhas) a cada 3 ataques por 2,2 s, num vão sem plataforma,
  ao alcance do golpe sem pular. Ritmo por dificuldade (`boss_pace`: 0,85 / 1,0 / 1,1): avisos mais longos
  no Fácil. Dano continua 1 coração por golpe em todos os chefes (a dificuldade muda vida e corações).
- Avisos: o canhonaço marca no chão a área real da explosão; aviso do raio usa a própria duração.
- Interface em `states.py`: pausa com as posições sugeridas; `MessageState` com `ui.panel`, texto quebrado,
  caixa larga e `ui.hints` (QA 5); `DialogState` com `ui.panel`; tela de morte com a bolsa 30 px abaixo
  (QA 4); "FINAL VERDADEIRO" em título que cabe na tela (QA 11).
- Sons: `heavy_charge` no preparo do golpe forte (o `attack_heavy` sai no golpe), `break_wood` na parede
  rachada, `explosion` nas bombas, `ability` ao pegar habilidade, `door` quando o portão da arena fecha.

Pendente / para outras frentes:
- Arte: retrato da Capitã na caixa de diálogo continua pequeno (`objects.draw_portrait` não tem arte para
  ela e cai no `draw_character`). `objects.draw_character` 3 px acima do chão continua (arquivo da arte).
- Arte: mexi só duas linhas de desenho em `bosses.py` (estrelinhas do Caelum no descanso e elipse da área no
  `CannonShot.draw`); podem trocar por arte própria.
- Jogar as lutas de verdade para afinar: a vida nova dos chefes ainda não foi medida com o bot do QA.

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
- Revisão de legibilidade em 960x540 (03/11): menu, dificuldade, intro, como jogar, recordes, créditos,
  HUD, mapa e barra de chefe conferidos. Corrigido: colunas do "Como jogar > Controles" alinhadas
  (antes cada ação começava num x diferente); dica ESC/Tab/M do HUD presa à margem direita
  (`ui.hints(..., align="right")`); legenda do mapa calculada pela largura do texto (encostava na
  moldura); créditos já abrem com o painel cheio e só sobem depois de 1,6 s (antes ficavam ~10 s vazios).
  Teste novo `test_credits_and_hints`.

Pendente (depende de `src/states.py`, que é da área de gameplay):
- Pausa: menu encosta no título "PAUSADO". Sugestão: título y=40 size=44; menu center_y=190, spacing=36;
  inventário em (40, 330); controles em (480, 318).
- MessageState e DialogState: trocar as caixas `pygame.draw.rect` por `ui.panel(...)` e a dica por
  `ui.hints(...)`. Retrato da caixa de diálogo sai quase vazio.
- QA 4 (morte: texto da bolsa 30 px abaixo), QA 5 (MessageState: quebrar o corpo com `ui.wrap_text`
  e alargar a caixa) e QA 11 (EndingState: "FINAL VERDADEIRO" com `title=True`, igual ao "FIM").
- Loja/ferreiro (`ShopState`/`ListState`): a descrição do mapa diz "(M ou Tab)", mas M é o som; trocar
  por "(Tab)". A tela não tem painel: o texto fica solto sobre o jogo e o "[W] Loja" aparece por trás.
  Sugestão: `ui.panel(surf, (140, 84, 680, 300))` atrás da lista e `ui.hints(...)` no rodapé no lugar de
  "W/S navegar - Enter escolher - ESC sair".
- Pausa: com o menu em `center_y=172` o "Continuar" (y=72) encosta no "PAUSADO" (y=34). Conferido de novo
  em 03/11; a sugestão acima continua valendo.
- Créditos mostram o texto provisório "[Nome do integrante - RA] (editar em src/menus.py, lista CREDITS)":
  falta o Gabriel mandar os nomes e RAs da equipe para pôr em `CREDITS` (`src/menus.py`).
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

Feito (03/11, rodada de ajuste, sem commit):
- QA nº 10 conferido: com o empurrão lateral do gameplay, pular reto pelas duas escotilhas chega em pé.
- Porão 1: rato do piso de cima saiu de 36 para 38 (não fica mais em cima do pouso do buraco).
- Porão 2: gaivota saiu de cima do canal (plataforma móvel + tábuas) para o chão leste (46, 13).
- Vergas: tábuas 27-31 que cedem + pedaço firme 32-33 para esperar a plataforma móvel sem cair no mar;
  gaivota saiu de cima das tábuas para a rota alta (guarda a carta 2).
- Praia: céu vazio ganhou um caminho opcional: do coqueiro, galho (16-20, linha 8) e ninho (7-11, linha 5)
  com duas caixas de moedas.
- Templo: pedras soltas 17-19 + pedra firme 20-21 para esperar a plataforma sobre os espinhos.
- `tests/test_ship.py`: alcances novos (ninho, pedaço firme, pedra firme, câmara) e `test_reach_movers`
  (12 saltos de/para plataformas móveis no Porão 2, Cordame, Vergas, Floresta e Templo, que antes não
  tinham teste).

Pendente:
- Parado por limite de uso. Falta jogar as salas de verdade (dificuldade humana) e conferir as capturas.
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

### Arte (3/11, sem commit)

Feito:
- `tools/animar_pose.py`: folhas `anim_<nome>.png` (parado, andando, ataque) para lobo, goblin, os 10 NPCs PixelLab,
  Selka e Caelum, ligadas em `creatures.py`, `elenco.py` e no `draw` de `bosses.py`. NPCs na altura da protagonista.
- Céus `porsol` (praia) e `crepusculo` (floresta); efeitos novos (`tools/importar_efeitos.py`): morte_chefe, absorver,
  impacto_roxo, impacto_critico, defesa, pressa, carga (Caelum), aviso_duplo (Selka).
- Sons health_up, slime_hit, slime_death, ground_slam, door_crash, ui_woosh e música `boss_01.ogg`.
- `docs/PERSONAGENS.md` e `assets/CREDITOS.md` atualizados.

Pendente:
- Gameplay: ligar os sons novos em `SFX_NAMES`/`audio.play`, `boss_01` nas lutas e os efeitos novos nos eventos.
- PixelLab recusou o token (401): ciclos desenhados à mão para Selka e Caelum ficariam melhores.
- Suíte completa rodada no fim da sessão de arte; conferir o resultado antes do commit.

## Integração e testes

Feito (03/11):
- Rodada 3 de QA com todos os scripts de `docs/qa/scripts/` (detalhes em `docs/QA.md`). Corrigidos desde a
  rodada 2: crash do `MODEL_OF`, "loja da Vila", nome da sala e dica do HUD por cima das telas, lobo nos
  espinhos, fontes dos finais.
- `qa_perigos.py`: caso do Cordame 1 marcado como "não testado" (sala redesenhada).
- Suíte completa: 436/436.

Pendente (por frente):
- Gameplay: Selka só pula para trás quando a jogadora fica colada (QA 1); chefes com 26–108 golpes e Caelum
  bem mais longo (QA 3); texto da bolsa sobre o da morte (QA 4); corpo do diário sem quebra de linha (QA 5);
  menu da pausa colado no título (QA 12); pulo reto pelas portas do teto volta à sala de baixo (QA 10).
- Fases: sem bola usada, cair no canal do Porão 2 ou na vala da Praia volta à Cabine (QA 2).
- QA: posição nova para o teste "cair pelo fundo do Cordame 1"; rota inteira numa só partida ainda não foi jogada.
