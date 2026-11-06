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
- Vida nova dos chefes medida com o bot em 06/11 (ver abaixo); falta só jogar com gente.
- Decisão do Gabriel (03/11): manter vida dos chefes, Selka, descanso do Caelum, ritmo por dificuldade,
  volta ao chão firme da sala e empurrão da porta do teto.

Desafio maior (04/11, sem mexer em Player/Physics/Dash/Combat):
- Dificuldade dos inimigos em `Game.DIFFICULTIES`: `enemy_aggro` (0/1/2), `strong_damage` (1/2/2) e
  `enemy_cooldown` (1,0/0,85/0,7). Fácil ficou igual ao de antes.
- Perseguidores (`c`) dão bote no Normal/Difícil: recuam e piscam (0,42 s; 0,34 no Difícil), avançam e
  ficam parados 0,65 s. O bote e o empurrão do escudo tiram 2 corações no Normal/Difícil; encostar segue 1.
- Inimigo novo, atirador (letra `a`): mira piscando, atira, recarrega parado e recua de quem chega perto
  (mais lento que a corrida; encurralado, não foge). Navio = pistoleiro, ilha/ruínas/templo = goblin
  com pedras. Escudo já defende só de frente (golpe por trás ou reto para cima/baixo passa).
- Fase 2 dos chefes: Tico emenda dois saltos; Aldric com poder salta logo depois do vento; Selka investe
  logo depois do sinal do canhonaço; Caelum ganha a caçada de três raios seguidos.
- Combinado com a Fases: ela posiciona os `a` e mais `c`/`s` nas salas (ainda não há `a` no mapa).
- Desenho: em `creatures._ModelMixin.draw` o corpo pisca branco no aviso (`windup`/`aim`); a Arte pode trocar.
- Testes novos em `tests/test_world.py`. Falta jogar de verdade para afinar os números.

Medição e sons (06/11, sem commit):
- `qa_chefes.py` com 3 sementes nas 3 dificuldades (vida 48/76/84/100 e fase 2 nova). Tempo da luta acordada
  pelo bot: Tico 8–21 s, Aldric 16–34 s, Selka 32–78 s, Caelum 30–90 s (Fácil), 45–64 s (Normal), 33–169 s
  (Difícil; 169 s numa semente com 30 "mortes"). Nenhuma luta passa de 90 s no Normal: **nenhum número mudou**.
  Caelum intocado na mecânica (só ganhou o efeito `impacto_roxo` no acerto).
- Sons ligados: música `boss_01.ogg` nas lutas (`Audio.MUSIC["boss"]`) e volta à música da zona quando o chefe
  cai; `door_crash` no portão da arena; `ground_slam` nas quedas do Tico e do Aldric; `health_up` ao ganhar
  coração; `slime_hit`/`slime_death` no slime (`Enemy.hit_sound`/`death_sound`); `ui_woosh` ao abrir a pausa.
- Efeitos ligados: `morte_chefe` na morte do chefe, `impacto_critico` no golpe forte, `defesa` no golpe
  defendido pelo escudo, `absorver` ao pegar habilidade, `coracoes` ao ganhar coração, `impacto_roxo` em
  Caelum, espírito e lich (`Enemy.hit_fx`). `pressa` ainda sem uso (sugestão: amuleto de velocidade).
- Teste novo `test_sounds_wired` (arquivos de todo som/música e os ligados).
- QA da rota inteira numa só partida (script `qa_rota.py` na pasta de notas da coordenação; a Integração pode
  copiar para `docs/qa/scripts/`): Cabine -> Toca -> Gávea -> ilha -> Altar -> final verdadeiro nas 3
  dificuldades, **0 problemas**: portas levam à sala certa, prancha do Convés trancada antes do Aldric e aberta
  depois, recompensas (Levitação, fragmento) aparecem, arenas reabrem, 3 páginas e final verdadeiro.
  O bot se teleporta dentro da sala (alcance fica com `try_reach`). Rodado sobre o mapa de 06/11 cedo:
  **rodar de novo depois que a Fases terminar** os atiradores `a` e os inimigos novos.

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
- Nome da sala ao passar o mouse no mapa: pronto do lado da interface (`ui.draw_map` guarda as salas em
  `ui.map_rooms`; `ui.draw_map_hover(surf, mouse_pos)` desenha contorno e etiqueta; teste `test_map_hover`).
  Falta só a Gameplay chamar em `MapState.draw`, depois do `blit` do cache e também logo após criar o
  cache: `ui.draw_map_hover(surf, self.app.input.mouse_pos)` (o cache continua valendo; o hover é por cima).
- Ideia de polimento ainda não feita: tela de resultados com painel (ResultsState mora em `states.py`).
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

Feito (04/11, dificuldade, sem commit): medidos os inimigos perto de cada pouso dos testes de alcance.
- Porão 1: rato do chão entre o buraco e os caixotes (7 tiles) foi para 26 (longe também do alçapão).
- Porão 2: rato do teto saiu da viga logo depois das tábuas (25 -> 16, viga firme); gosma 48 -> 54.
- Cordame: gaivota saiu de cima do pouso leste 2 (34,28 -> 36,21).
- Vergas: canhão 54 -> 56: com alcance de 440 px, agora pega só o fim da plataforma móvel, não ela toda.
- Floresta: gosma saiu do galho 2 (6 tiles, chegada por pulo) para o caminho longo (27, 21).
- Tábuas: larguras conferidas (3 a 6 tiles; correndo cada tile leva ~0,1 s e cede em 0,45 s): sem mudança.
- `test_fair_landings`: nenhum inimigo começa em pouso estreito logo depois de buraco, água ou tábuas.

Feito (04/11, mais desafio, sem commit):
- Cordame: enfrechate oeste 6 (10-15, linha 19) virou tábua podre (não dá para parar); rato novo no
  enfrechate oeste 5, junto com a gaivota.
- Praia: diabrete sobre a vala de espinhos (19, 13). Ninho virou desafio: galho podre + diabrete,
  recompensa 60 moedas (item novo no índice 0 da sala; a torta passou a `praia:1`).
- Floresta: diabrete sobre as tábuas do caminho rápido (espinhos embaixo).
- Templo: espírito sobre a plataforma móvel; desafio da torre (opcional): da galeria, pedras soltas
  (48-52, linha 6) até o cofre (54-57, linha 3) com 80 moedas e um espírito de guarda.
- Testes de alcance novos para a torre do templo; fragmentos continuam 4 (o teste exige 1 coração).
- Atirador novo da Gameplay (`a`): ponta da verga grande do Cordame (29, 12), fundo do penhasco da Praia
  (57, 11, atrás do goblin e do lobo) e saída da Floresta (45, 5, mira quem sobe pelo elevador).
  Porão 2: rato do chão leste virou pirata de escudo (`s`), junto com a gosma.

Feito (06/11, combinações e desafios, sem commit):
- Atirador (`a`) agora em 7 salas, sempre junto de outro inimigo, crescendo do navio ao templo:
  Porão 1 (pistoleiro na prateleira alta, atira em quem sobe a escada; rato do chão leste virou capanga `c`),
  Porão 2 (pistoleiro na prateleira do elevador + escudo e gosma no chão), Vergas (pistoleiro no lado
  leste, com o canhão e a gaivota), Templo (saída com múmia, atirador e cavaleiro: `c` 50, `a` 55, `s` 57).
  Cordame, Praia e Floresta continuam com os da rodada anterior.
- Praia: vala de espinhos de 8 para 9 tiles (chão leste começa na coluna 24): pede pulo duplo ou dash,
  com o diabrete por cima.
- Terceiro desafio opcional (Porão 2, "vigas podres"): da prateleira alta, tábua podre (58-61, linha 7) e
  jirau sob o teto (50-55, linha 5) com o fragmento que ficava na prateleira (realocado, total continua 4).
  Sinal: caixotes de carga na prateleira e no jirau. Os outros dois: ninho da Praia e torre do Templo.
  Atenção: a ordem dos itens do Porão 2 mudou (fragmento é `porao2:0`, carta 1 `porao2:1`); saves antigos
  podem mostrar a carta/fragmento trocados.
- Testes (`tests/test_ship.py`): alcance da tábua podre e do jirau (só dash), vala nova, `a` entra no
  `test_fair_landings`, `test_enemies_not_in_walls` (inimigo de chão com chão embaixo e espaço em cima;
  voador fora de parede) e `test_enemy_mix` (atirador em combinação nas salas das 4 áreas). Simulação de 8 s
  em Porão 1/2, Vergas, Praia e Templo: todos ficam no próprio andar, ninguém cai em perigo.
- Sugestão para a Arte: uma placa/marca visual no início dos 3 desafios (hoje o sinal são caixotes e baús).

Pendente:
- Falta jogar as salas de verdade (dificuldade humana) e conferir as capturas. Templo (saída com múmia e
  cavaleiro) ficou como está: área final, chão largo depois do meio-fio.
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
- Animações de combate: completar as folhas usando as artes de referência em `Personagens gerados por mim`;
  os ciclos provisórios do diabrete, ladino e cavaleiro do escudo foram rejeitados e removidos do jogo.
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

Feito (retomada 3/11):
- Convés conferido (captura `arte_capturas/conves_npcs_corrigido.png` na pasta de notas): NPCs PixelLab no chão e na escala certa.
  Corrigido: personagens de conversa flutuavam 3 px (`objects.draw_character` agora desconta a folga do quadro do elenco)
  e Caelum no Convés estava parado e virado para o lado errado (agora usa `anim_caelum`, respira e olha para a esquerda).
- Espírito e lich: conjuração própria (`anim_espirito.png`, `anim_lich.png`, ligada em `creatures.draw_model`).
- Capitã Maren caída: pose própria de deitada de costas desenhada pixel a pixel com a paleta dela
  (`tools/desenhar_maren_caida.py` -> `maren_caida.png`, 63x16), usada por `pixelart.corpse()` no lugar do sprite em pé
  girado. Chapéu caído ao lado, gola branca, braço no peito, botas para cima; apoiada no chão do Convés
  (captura `arte_capturas/conves_maren_caida.png`). PixelLab segue recusando o token (401).
- Banca do comerciante do Convés: barril e caixote-balcão do Forge com mercadoria pequena apoiada (frasco de geleia do
  Pixel Food, pão reduzido, mapa enrolado, peixe seco e rolo de corda desenhados à mão), à esquerda do comerciante, que
  olha para ela (`tools/montar_banca.py` -> `objetos/banca_comerciante.png`, `objects.NPC.draw`). Captura
  `arte_capturas/conves_banca_comerciante.png`.
- Figurantes de fundo (`background.WALKERS`): no máximo 2 por sala, com atividade. Convés: pescador na amurada
  e aldeã carregando caixote devagar; Cabine e Ruínas: um parado; Praia: um parado e um passeando; Floresta: uma
  passeando. Caminhada a ~12 px/s com pausa de 3 s nas pontas e passada mais lenta (`_draw_walker`). Captura
  `arte_capturas/conves_figurantes.png`.
- Testes: suíte completa 476/476 (antes da capitã e da banca); depois delas, `test_render_all` e
  `test_dialogs_and_npcs` passam de novo. Sem commit.

Pendente:
- Gameplay: ligar os sons novos em `SFX_NAMES`/`audio.play`, `boss_01` nas lutas e os efeitos novos nos eventos.
- Ações por personagem para completar e integrar:
  - Inimigos terrestres: lobo (corrida, salto/queda e mordida), goblin (caminhada, salto/queda e porretada),
    ladino (caminhada, salto/queda e golpe de adaga) e cavaleiro do escudo (caminhada, guarda, investida,
    golpe e quebra da guarda).
  - Inimigos voadores/mágicos: diabrete (voo, mergulho e ataque), espírito (flutuação, conjuração e ataque),
    lich (preparo, lançamento de magia e recuperação). Múmia e cavaleiro negro já têm folhas do pacote;
    só substituir se a conferência mostrar defeitos.
  - Chefes: preservar as animações de caminhada e pulo já existentes para Tico e Aldric; conferir os ataques
    e só preencher uma ação se estiver realmente faltando. Selka: caminhada, pulinho/pouso, bote, pistola e
    canhão. Caelum: flutuação, teleporte, conjuração e recuperação.
  - Fazer o inventário de todo inimigo sem sequência própria além dos nomes acima; verificar se o golpe muda
    de pose, e não só mostra um efeito sobre o corpo parado. Reaproveitar a ação de Caelum nas ilusões.
    NPCs como Maren ficam fora desta tarefa.
  - Preservar a aparência e a escala das artes de referência, fundo transparente, âncora estável no pé e quadros
    próprios para cada ação. Conferir os dois sentidos, atualizar `CREDITOS.md` e salvar os novos arquivos nas
    subpastas correspondentes de `Personagens gerados por mim`. NPCs não são prioridade.
  - Revisar as folhas provisórias de lobo e goblin; não reutilizar os ciclos recusados de diabrete, ladino e
    cavaleiro do escudo.
  - Rat, gaivota e slime já têm movimento/quadros no jogo; canhão e caixa são estáticos por função. Múmia e
    cavaleiro negro já têm folhas animadas do pacote. Conferir essas artes, mas não gerar substituições sem defeito.
- Suíte (3/11): 433/436. `test_render_all` caía em `PirateSister.alpha`; já corrigido no `draw` (render passa).
  As outras duas falhas são de volta ao checkpoint (`volta ao último checkpoint`, água do porao2): área de gameplay.

## Integração e testes

Feito (06/11):
- Suíte completa: 494/494 (inimigos mais desafiadores, figurantes reduzidos, capitã caída, cenários).
- Commit em `main`, executável novo em `dist\onefile\MareDeMentiras.exe` e release `v1.2` no GitHub.

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
