# Pendências por área

## Gameplay

Estado (12/11): tudo da Gameplay fechado; histórico no registro de alterações do Obsidian.
- QA antigos conferidos de novo sem janela: 1 (Selka ataca de perto, `test_selka_fights_up_close`),
  2 (canal do Porão 2 e vala da Praia voltam na própria sala, `qa_perigos.py`), 3 (lutas no Normal 11–64 s),
  4 (bolsa abaixo de "VOCÊ CAIU"), 5 (diário com painel e texto quebrado), 10 (porta do teto,
  `test_ceiling_door_nudge`), 12 (pausa: menu afastado do título e painéis dentro da tela). Todos **feitos**.
- Loja/ferreiro com `ui.panel` atrás da lista e `ui.hints` no rodapé; mapa diz "(Tab)"; "[W] Loja" só
  aparece com o jogo na frente (some atrás de loja, banco, diálogo e pausa). Mapa mostra o nome da sala
  sob o mouse (`ui.draw_map_hover`).
- Varredura: os dois finais chegam ao resultado e ao menu; créditos rolam até o fim (618 px, ~20 s) e voltam;
  salvar no banco e carregar volta ao banco certo em todas as salas com banco (sem banco: último banco).
- Rota inteira com o bot (`qa_rota.py`, pasta de notas da coordenação): 0 problemas nas 3 dificuldades.

Pendente / para outras frentes:
- Arte: retrato da Capitã na caixa de diálogo pequeno (`objects.draw_portrait` sem arte para ela).
- Arte: efeito `pressa` sem uso (sugestão: amuleto de velocidade).
- Jogar as lutas com gente (bot só mede tempo).

## Interface

Feito: kit visual, menus, HUD, barra de chefe, mapa e inventário, revisão de legibilidade (03/11), QA 6/7/8,
e (pela Gameplay em `states.py`) pausa, caixas de mensagem/diálogo, morte, final, loja e hover do mapa.

Pendente:
- Créditos ainda com "[Nome do integrante - RA]": falta o Gabriel mandar nomes e RAs (`CREDITS` em `src/menus.py`).
- Ideia opcional: tela de resultados com painel (`ResultsState` em `states.py`).

## Level design

Pronto (`src/chapter1.py`, `tests/test_ship.py`; auditoria final em 12/11):
- 13 salas com as mesmas portas e ligações. Parkour com rotas opcionais, 6 paredes rachadas com segredo,
  4 fragmentos (+1 coração), 3 cartas, baús de moedas, arenas com abrigos para cada chefe.
- Inimigos em combinação, crescendo do navio ao templo (porão 5 e 5, cordame 6 e 5, ilha 8 e 7, templo 7 com
  múmia, cavaleiro e lich). Atirador (`a`) em 7 salas, sempre junto de outro inimigo.
- Perigos em ritmo: diabrete sobre a vala da Praia (9 tiles) e sobre as tábuas da Floresta, espírito sobre a
  plataforma dos espinhos do Templo, canhão e pistoleiro no fim da plataforma das Vergas.
- 3 desafios opcionais com recompensa, sinalizados por caixotes e baú à vista: vigas podres do Porão 2
  (fragmento), ninho da Praia (60 moedas) e torre do Templo (80 moedas).
- Auditoria: todo baú é pego do pouso embaixo dele (`test_every_item_pickable`), toda parede rachada abre e
  dá o item de trás (`test_all_secrets`), todo pouso testado com o `Sim` (`test_reach_*`), nenhum inimigo
  começa em parede (`test_enemies_not_in_walls`) ou em pouso estreito depois de perigo (`test_fair_landings`).
  Pousos sem volta: nenhum (bolsões fechados por parede rachada têm saída pela própria parede; quedas caem
  em perigo, que devolve ao chão firme da sala).
- Menos repetição (pedido do Gabriel na v1.4): ladino (capuz roxo; modelo do capanga `c` e do pistoleiro `a`
  no navio) de 6 para 4 no navio, 1 por sala (só o pistoleiro). O capanga do Porão 1 virou gaivota e o das
  Vergas virou rato. Escudo continua 1 pirata (Porão 2) e 1 cavaleiro negro (Templo), nunca 2 na mesma sala.
  Teste `test_enemy_variety`: até 2 ladinos por sala no navio, até 1 escudo por sala, 3+ tipos por sala.
  Para a Arte, se quiser: pistoleiro com visual próprio (hoje usa o mesmo `ladino` do capanga).
- Saves antigos: a ordem dos itens do Porão 2 mudou (fragmento `porao2:0`, carta 1 `porao2:1`).

Pendente:
- Jogar as salas de verdade (dificuldade humana) e afinar posições se algo ficar injusto.
- Sugestão para a Arte: placa ou marca no início dos 3 desafios (hoje o sinal são caixotes e baús).

## Assets

Estado (12/11/2026, sem commit; capturas `r2_*` e `r3_*` em `arte_capturas` na pasta de notas):
- Personagens: protagonista e Rei dos Ratos (PixelLab do Gabriel); NPCs, lobo, goblin, Selka, Caelum e Maren em
  PixelLab com folhas `anim_*.png` de `tools/animar_pose.py` (parado, andando, ataque). A ferramenta aceita nomes
  (`python tools/animar_pose.py lobo goblin`) e só refaz esses.
- Ataques com pose própria (não só efeito sobre o corpo parado), ligados por estado em `creatures.draw_model`
  (preparo -> golpe -> recuperação): goblin, ladino (capanga e pistoleiro), cavaleiro do escudo (investida com o
  escudo), lobo (bote: agacha, salta, pousa; o lobo de hoje só patrulha, então a folha fica pronta para quando
  ganhar mordida), diabrete (recolhe e mergulha), espírito e lich (conjuração). Selka golpeia com o tronco no bote;
  Caelum recolhe, brilha e lança ao conjurar; as ilusões agora usam a mesma folha em 2x e conjuram antes de atirar.
  Corrigido: a pose de conjuração do Caelum podia não aparecer (`sprites.variant` guarda por `id()` e o quadro era
  recriado a cada desenho); agora o quadro acolchoado fica guardado (`bosses._quadro_caelum`).
- Atirador `a`: pistola ou pedra na mão e aviso de mira (linha pontilhada que fica vermelha ao travar, anel que
  fecha na boca da arma, brilho antes do tiro).
- Cenários: luz de lanternas (cone e poça), luar das escotilhas, redes, cordas, baldes, teias e bolhas no navio;
  plantas, pedras e colunas quebradas na ilha, ruínas e templo; poça de luz dos braseiros; variação rara nos blocos.
- Capitã caída com pose própria (`maren_caida.png`) e retrato em busto apagado; banca do comerciante; figurantes
  (no máximo 2 por sala); `objects.draw_character` já desconta a folga de 3 px do quadro do elenco.
- Licenças: `assets/CREDITOS.md` conferido nas páginas dos pacotes, sem nenhum `[CONFIRMAR]`. A feiticeira "sample"
  (sem autor identificável) saiu do jogo: arquivos movidos para `assets internet/fora_do_jogo_licenca/` e skin
  `feiticeira_antiga` retirada de `skins.SKINS` (os saves antigos já carregam como "ela").

Falta:
- Conferir em jogo, com janela e quando o Gabriel puder, a força das luzes e a clareza do aviso de mira.
- Gameplay: a música `boss_01` e o efeito `pressa` ainda não são usados.
- Grupo: dizer a origem da folha de modelos da equipe (`npcs.png`) e escrever a seção "Uso de IA" do relatório.
- Imagens sem uso (podem sair do pacote final): `efeitos/fantasma_roxo`, `corte_v`, `onda_roxa`; `objetos/porta`,
  `moldura_vida`; `itens/queijo`, `rosquinha`, `sanduiche`, `sushi`.

## Integração e testes

Versões publicadas (instalador `MareDeMentiras-Setup.exe` + `.exe` portátil):
- `v1.5` (12/11): menos inimigos repetidos no navio; versão para teste com amigos. Suíte 512/512.
- `v1.4` (12/11): **versão final.** Rodada 4 de QA sem janela sem problemas abertos; suíte 510/510.
- `v1.3` (06/11, commit `30086ea`): suíte 503/503 sem janela; instalador testado em modo silencioso.
- `v1.2` (06/11): inimigos mais desafiadores; instalador novo (`tools/instalador.iss`, pt-BR, sem pedir
  administrador; instalado, o save vai para `%APPDATA%\MareDeMentiras`); `Jogar.bat` instala o pygame-ce.

Como gerar uma versão: suíte sem janela (`SDL_VIDEODRIVER=dummy`, `SDL_AUDIODRIVER=dummy`); PyInstaller com
`MareDeMentiras.spec` (ícone `tools/icone.ico`) a partir do commit; `ISCC.exe tools\instalador.iss` (atualizar
`Versao`); testar o Setup com `/VERYSILENT /SUPPRESSMSGBOXES`; `gh release create` com a tag no commit.

Pendente: nada.
