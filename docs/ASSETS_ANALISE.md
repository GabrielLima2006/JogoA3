# Análise dos assets da internet — o que ainda não foi aproveitado

Data: 2026-10-23. Só leitura: nada do jogo foi alterado. Pacotes extraídos para uma pasta temporária; prévias conferidas
em montagens. Protagonista ≈ 55 px de altura.

> **STATUS: ANÁLISE COMPLETA** (todos os pacotes abertos e conferidos em montagens).

## Licenças (o que o arquivo do pacote diz)

| Pacote | Licença no pacote |
|---|---|
| Super Pixel Effects Gigapack (Free) v3.1.0 | `license.txt` (resumo; texto completo em untiedgames.com/files/license.txt): uso em jogo comercial ou não, **crédito obrigatório** ("Super Pixel Effects Gigapack – Will Tice / unTied Games"); proibido revender/redistribuir o pacote e **treinar IA** |
| New free backgrounds 1–5 e free-sky-with-clouds | `license.txt` só traz o link `craftpix.net/file-licenses/` (Craftpix). Termos exatos **[CONFIRMAR]** lendo a página; autor Craftpix |
| Skeletons Free Pack | sem arquivo de licença **[CONFIRMAR]** (página do itch.io) |
| Metroidvania Forge ch_01–ch_06 | sem licença **[CONFIRMAR]**; não usar o logo |
| Coin_Gems | sem licença **[CONFIRMAR]** |
| Dark VFX 01–02, Smear VFX 01, sample idle&walk, FreeButtons | sem licença **[CONFIRMAR]** |
| FREE (SunGraphica) | só nota do autor (gamedevmarket.net/member/sgasset), sem termos **[CONFIRMAR]** |
| UIBundleFree | sem licença no pacote **[CONFIRMAR]** |
| Input Prompts Pack V7 (+ Source) | sem licença **[CONFIRMAR]**; é projeto Unreal, só os PNGs interessam |
| DEMO Cozy UI (dobo_ui) | só nota "versão demo" **[CONFIRMAR]**; não usar |
| SBS Tiny Texture 1 e 2 | `License.txt` confirma **CC0**/domínio público, uso comercial livre, crédito opcional |

Todos precisam entrar em `assets/CREDITOS.md` com autor, link e licença antes da entrega.

---

## PRIORIDADE ALTA

### A1. Skeletons Free Pack — inimigo novo para o templo (área: assets; gameplay liga a IA)
- Conteúdo: esqueleto com espada, 2 cores (**White** e **Yellow/osso dourado**), versões com e sem VFX.
  Quadro **96×64**, esqueleto ≈ 45–48 px de altura (cabe ao lado da protagonista de 55 px), olhando para a direita (espelhar).
  Animações: Idle 8, Walk 10, Attack1 10, Attack2 9 (a versão Yellow-VFX traz o arco de corte), Hurt 5, Die 13.
- Onde entra: salas do templo (inimigo comum de patrulha) e escolta do chefe final; o amarelo como variante forte/elite.
- Por quê: o jogo só tem slime, ratos e piratas; esqueleto tem 6 animações prontas (morte longa com ossos no chão) e pixel art
  no mesmo nível de detalhe do herói do Forge. Combina com o tom sombrio/mágico.
- Obs.: pasta `Skeleton_With_VFX` já inclui o corte na animação (não precisa de efeito separado).

### A2. Super Pixel Effects — 60 animações ainda não usadas (área: assets; gameplay chama)
Já em uso: golpe, golpe forte, explosões, fumaça, fogo, raio, cura, brilho, alerta, moedas, corações, respingo, veneno.
Sugestões novas (tamanho = variante *small*, a *large* é o dobro):
- **Falar/estado do jogador:** `spell_defense_up_001` (escudo azul 64×64) para o bloqueio/defesa; `spell_attack_up_001` (espada) ao pegar upgrade de ataque; `spell_haste_001` (relógio, 64×64) para o dash/bônus de velocidade; `status_sparkling_001` para item brilhando/checkpoint; `status_poison_001` (bolhas verdes 48×48) para estar envenenado (tema do jantar envenenado).
- **Magia da protagonista (roxo):** `spell_absorb_001_small_violet` (64×64, 31 quadros) para absorver/ganhar habilidade; `stylized_explosion_002_small_violet` (48×48, esfera roxa) como explosão da onda roxa; `lightning_burst_001/003 violet` para hit forte; `scifi_warp_*` (verde/vermelho/azul) como portal/teleporte entre salas e entrada de chefe.
- **Impactos de golpe em tipos diferentes:** `directional_impact_001 blue` (32×32), `003 violet` (40×40), `004 yellow` (40×40, anel no chão), `symmetrical_impact_002/003/004` (48×48) e `006` (80×80) para acerto crítico/parry/golpe final.
- **Fogo/tochas:** `fire_looping_003B`, `004A`, `004B` (40–48×64) — variar as tochas; fogo parecido com o atual mas com 15 quadros.
- **Chefes:** `epic_explosion_002` (96×96/192×192) para a morte de chefe; `scifi_charge_up_001` (48×48) para carregar ataque; `symbol_alert_002` (!!) como aviso de ataque; `round_light_burst_001` (128×72) flash de transição.
- **HUD/mensagens:** `symbol_complete_text_001`, `bonus_text_001/002`, `cool_text`, `game_over_text_001` (208×64), `symbol_crown_001`, `symbol_failure_001` — texto estilizado em inglês: usar só se combinar com a interface (o jogo é pt-BR; **evitar** textos em inglês).
- Escala: efeitos small têm 32–64 px, bons para a protagonista de 55 px; large (96–192) só para chefes.
- Estilo: mesma família já em uso no jogo, combina.

### A3. Novos fundos de céu (Craftpix) — 16 dos 20 ainda não usados (área: assets)
- 20 fundos de nuvens em pixel art, **576×324**, cada um com 5–8 camadas separadas (parallax). O jogo já usa 4 temas
  (`ceu_noite`, `ceu_roxo`, `ceu_cinza`, `ceu_tempestade`, 4 camadas cada).
- Ainda livres (montagem conferida): rosa/vermelho (p1 b2), céu com sol amarelo (p1 b4), azul claro (p2 b1), **pôr do sol laranja** (p2 b2),
  menta (p2 b3), azul vivo (p3 b3), magenta (p3 b2), azul com nuvens claras (p3 b1), **crepúsculo roxo** (p4 b2), cinza-azulado (p4 b3),
  amarelo-névoa (p4 b1), **noite com lua cheia e estrelas** (p5 b4), manhã com sol (p5 b1), rosa com sol (p5 b2), azul claro (p5 b3).
- Onde: ilha = pôr do sol laranja (p2b2) ou céu azul claro; templo = crepúsculo roxo (p4b2) e noite com lua (p5b4); sala do chefe final = tempestade (já usado) ou magenta (p3b2); título/menu = manhã/pôr do sol; fim feliz = amanhecer rosa (p5b2).
- Por quê: fundo é o que mais muda a "beleza" por sala; 20 opções cobrem as 13 salas sem repetir.
- Estilo: 576×324 escalado para 960×540 (×1,667) — não é inteiro; usar `scale` suave só no fundo ou reduzir camada (já feito nos `ceu_*`).
- Licença Craftpix **[CONFIRMAR]**.

### A4. Sons do Metroidvania Forge ainda sem uso (área: assets / gameplay)
Do ch_03–ch_06 (conferir quais já estão em `assets/sons/efeitos`; vários nomes ainda não aparecem lá — **[CONFIRMAR]**):
`ability_acquire` (pegar habilidade), `ability_crack`, `break_wood` (caixa quebrando), `boom`, `morph`/`morph_out`, `aargh`, `door_crash`, `door_switch`, `health_up`,
`slime_hit`/`slime_death`, `ui_bloop`, `ui_woosh` (menu), `ui_success`/`ui_error`/`ui_select`, ch_06: `charge`, `dash`, `explosion`, `ground slam`, `whoa`.
Música de chefe: `nega_pink_box_boss.wav` (10 MB, converter para .ogg) — usar na luta de chefe (hoje só dungeon/forest/title).

---

### A5. Tileset do Forge: pedras de masmorra para o TEMPLO (assets + level design)
Prévia de `ch_02/forgotten_forest_example_tileset.png` (1024×512): além da grama/terra da floresta (já em `ilha.png`), traz
**blocos de masmorra em pedra azul-esverdeada** (teto, parede lisa, parede quebrada, pilar escuro com capitel), **parede de pedra cinza arredondada**,
**4–5 braseiros com fogo animado**, plantas, **tábuas de madeira** (plataformas), pedras soltas, **silhuetas de árvores** (máscaras brancas, para tingir) e
**cachoeira/névoa** em degradê. Tiles de 16 px; o jogo escala ×3 (48 px por bloco) — confirmar com `src/tiles.py`.
Onde: templo (blocos, pilar, braseiros), plataformas de madeira, decoração da ilha. Por quê: hoje o templo usa tiles desenhados por código; estes dão
visual consistente com o herói/chefe do Forge. Combina com o estilo.

### A6. UIBundleFree — mais folhas utilizáveis (interface)
Folhas 256 px, 8 estilos. Já em uso: **Mediavel**. Ainda livres e que combinam:
- **FreeHorrorUi**: painel preto com bordas vermelho-escuro, botões PLAY/SETTINGS/EXIT (em inglês; recortar sem texto), caveira, ursinho, **coração em 3 estados (cheio/meio/vazio)**, barra de vida em dragão, **orbes laranja e azul** (ícones de habilidade/poder), botões pílula. Ideal para a tela de chefe/game over e HUD de vida.
- **freefantasy**: placas de madeira com cordas (PLAY/LOAD/EXIT), botões quadrados de ícones (play, pause, + , ✓, ✗, −, ?, $), **setas/flechas**, **velas coloridas** (azul/laranja/ciano/verde), seta de cantos. Dá menu inicial/pausa e loja.
- Mediavel (já usado) tem ainda placa pequena, espada, velas, ícones de som — conferir o que falta no `ui.py` **[CONFIRMAR]**.
- Texto "PLAY/EXIT" está em inglês: recortar a placa sem rótulo e escrever os textos em pt-BR com a fonte Alagard.
- Os demais (Casino, Pastel, Cozy, Demo, FreeUI) não combinam.

## PRIORIDADE MÉDIA

### M1. Props do Forge ainda sem uso (assets)
- `ch_04/props_destructible.png` (144×64): barril, caixa grande, tochas/tocheiros, coração solto — caixas já usadas; **barril e tocheiros** faltam (quebráveis com som `break_wood`).
- `ch_04/dust_effects.png`: poeira de pouso/derrapagem (usar no som de passo/skid).
- `ch_04/weapon_smears.png` (1024×128, 8 quadros por linha): cortes de espada brancos grandes — usar para o golpe da feiticeira (hoje usa `corte_h/v` do Smear VFX).
- `ch_04/abilities.png` (160×160, setas/ícones ciano): ícones das habilidades (já em `habilidades.png`).
- `ch_03/save_point.png` (96×80) e `door_and_switch.png` (32×96): checkpoint e alavanca/porta — checar se já em `objetos/porta.png`.
- `ch_02/forgotten_forest_example_tileset.png` (1024×512) e `autotile_template.png`: tileset de floresta — a ilha já usa `ilha.png` desta fonte; o exemplo inteiro traz mais peças (árvores, pedras) para variar a ilha **[CONFIRMAR peças não usadas]**.
- `ch_05/slime.png` (288×96): slime já usado.

### M2. Coin_Gems (assets/interface)
Moedas animadas em 4–5 cores (spr_coin_*: 16×16, 4 quadros; Moneda D/P/R: 16×16, 5 quadros) e gema verde. Úteis para contador de moedas no HUD e loja (cor por valor). Escala 16 px = pequeno; usar ×2.

### M3. Dark VFX 01 e 02 (assets)
Caveira roxa projétil (40×32, 10 quadros) e fantasma roxo (48×64, 16 quadros). Já em uso; as pastas "Separeted frames" permitem reutilizar quadros soltos. Usar nas magias do Feiticeiro da Maré.

### M4. Efeitos extras do Smear VFX (assets)
`Smear 01 Horizontal 1–3` (240×48, 5 quadros) e `Vertical 01–03` (288×48, 6 quadros): há 3 variantes de cada, e o jogo usa 1. Alternar entre elas no combo.

---

### M5. Texturas SBS (assets) — CC0, mas não são pixel art
Prévia dos 13 conjuntos de 128 px (Bricks, Grass, Roofs, Tile, Wood; Brick, Dirt, Elements, Metal, Plaster, Stone, Tile, Wood): texturas realistas/pintadas
(tijolo, telhado, madeira, metal, **lava** e **água/gelo** em Elements). Só servem como fundo de parede **escurecido e com paleta reduzida** (já se usa `madeira_escura`).
Ideias: **Stone/Brick escurecidos** atrás dos blocos do templo; **Elements lava** como brilho no chão da sala do chefe (com paleta reduzida). Não colocar texturas cruas: destoam do pixel art.

## PRIORIDADE BAIXA

- **Skeletons Free Pack variante Yellow com VFX**: só se ficar poucos tipos de inimigo.
- **FREE (SunGraphica)**: 89 ícones (maçã, alarme, voltar etc.) em 0.5x/1x/2x, claro e escuro, brancos lisos e vetoriais (maçã, seta, bateria, aviso, teclado, mouse, gamepad, nota musical, mapa, chave, cadeado…), 512 px, no estilo "flat". **Não é pixel art**; só serviria como ícone de configurações (gamepad, nota musical, mapa, cadeado) se reduzido com cor da paleta — **melhor não usar**. Licença [CONFIRMAR].
- **Input Prompts Pack / Source**: PNG 128×128 de teclas/mouse e botões (Xbox, PS4, PS5, Switch) em temas Default, Alt, Light, Dark, **Retro** (teclas em creme com letra serifada), Vintage, Stylized. O estilo vetorial/arte limpa não é pixel art; só vale o tema **Retro/Vintage** para a tela de controles se o `teclas.png` do Forge não cobrir (setas, Esc, Shift, Espaço). `Source` repete os mesmos PNGs e o `.uproject` é do Unreal (ignorar).
- **DEMO Cozy UI**: botões verdes/vermelhos "BUY/CLAIM/EXIT GAME" estilo cartoon liso e painéis creme/marrom; vetor, **não pixel art**. Não usar. **FreeButtons**: botões cinza sem graça. Não usar.

---

## Para quem aplicar

| Área | O que fazer |
|---|---|
| **assets** | A5 (recortar peças do tileset), M5, A1 (copiar esqueleto, recortar 96×64, espelhar), A2 (importar efeitos da lista; guardar `.txt` de recorte), A3 (fundos de céu por área), A4 (converter sons), M1, M4, M3 |
| **interface** | A6 (folhas Horror e Fantasy: coração 3 estados, painéis, orbes), M2 (moedas no HUD), efeitos de estado (defesa, haste) como ícones de buff, textos de recompensa **em pt-BR** (não usar PNGs em inglês) |
| **gameplay** | IA do esqueleto (patrulha, ataque 1/2, morte), chamar efeitos novos nos golpes/chefes, tocar `ability_acquire`/`break_wood`/música de chefe |
| **level design** | usar os novos céus por sala; colocar barris/tocheiros quebráveis; A5 (pedras de masmorra e braseiros do templo) |

## Créditos a acrescentar em `assets/CREDITOS.md`
Skeletons Free Pack, Coin_Gems, Craftpix (fundos e céu), Super Pixel Effects (já), todos com autor/link/licença **[CONFIRMAR]**.

Análise concluída. Uso semanal 95%, abaixo do corte de 98%.
