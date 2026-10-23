# Créditos dos assets

Todos os pacotes abaixo foram baixados gratuitamente do itch.io (os do Craftpix, do site craftpix.net).
Só os arquivos usados foram copiados para esta pasta (renomeados em português). Campos marcados com
**[CONFIRMAR]** precisam ser conferidos na página do pacote antes da entrega: autor, link e licença exatos.

| Pacote | Autor | Link | Licença | Arquivos no jogo |
|---|---|---|---|---|
| Super Pixel Effects Gigapack (Free) | Will Tice / unTied Games | [CONFIRMAR link] | Licença do pacote (`license.txt`): uso em jogos comerciais ou não, **com crédito**; proibido revender o pacote ou usar para treinar IA | `img/efeitos/` (golpe, golpe_forte, explosao, explosao_grande, fumaca_*, fogo, raio, raio_explosao, cura, brilho, alerta, moedas, coracoes, respingo, veneno) |
| Metroidvania Forge (capítulos 1 a 6) | [CONFIRMAR autor] | [CONFIRMAR link] | [CONFIRMAR licença] | `img/personagens/heroi.png` (base dos papéis masculinos do elenco: grumete, imediato, amigo, mercador, ferreiro, capangas, marinheiro, pescador), `img/chefes/cavaleiro_rubro*.png`, `img/inimigos/slime.png`, `img/tiles/ilha.png`, `img/objetos/` (caixas, bola_de_cristal, coracao, moldura_vida, poeira, porta, teclas, habilidades), `img/efeitos/cortes.png`, `sons/efeitos/*.wav` (inclui `heavy_charge.wav` = `charge.wav`, `break_wood.wav`, `explosion.wav`, `ability.wav` = `ability_acquire.wav`, `door.wav` = `door_crash.wav`), `sons/musicas/*.ogg` |
| Sample – idle & walk (feiticeira) | [CONFIRMAR autor] | [CONFIRMAR link] | [CONFIRMAR licença] | `img/personagens/feiticeira_parada.png`, `feiticeira_andando.png`, `feiticeira_partida.png` (protagonista antiga e base dos papéis femininos do elenco: cozinheira, irmã da capitã, capitã, aldeã, curandeira) |
| Skeletons Free Pack | [CONFIRMAR autor] | [CONFIRMAR link] | [CONFIRMAR licença] (sem arquivo de licença no pacote) | `img/inimigos/esqueleto_{branco,amarelo}_{parado,andando,ataque,dano,morte}.png` (múmia do templo e cavaleiro negro) |
| New free backgrounds (partes 1 a 5) | Craftpix | https://craftpix.net/freebies/ | Licença Craftpix (`license.txt` aponta para https://craftpix.net/file-licenses/) [CONFIRMAR se a licença gratuita exige crédito] | `img/fundos/ceu_noite_*.png` (parte 1, fundo 1), `ceu_roxo_*.png` (parte 1, fundo 3), `ceu_tempestade_*.png` (parte 3, fundo 4), `ceu_cinza_*.png` (parte 4, fundo 3) |
| Dark VFX 01 e 02 | [CONFIRMAR autor] | [CONFIRMAR link] | [CONFIRMAR licença] | `img/efeitos/caveira_roxa.png`, `fantasma_roxo.png` |
| Smear VFX 01 | [CONFIRMAR autor] | [CONFIRMAR link] | [CONFIRMAR licença] | `img/efeitos/corte_h.png`, `corte_v.png` |
| UIBundleFree (folha Mediavel) | [CONFIRMAR autor] | [CONFIRMAR link] | [CONFIRMAR licença] | `img/ui/medieval.png` |
| pixelfood | Ghostpixxells | [CONFIRMAR link] | [CONFIRMAR licença] | `img/itens/*.png` |
| Tiny Texture Pack 1 e 2 | Screaming Brain Studios | [CONFIRMAR link] | CC0 (domínio público) | `img/fundos/madeira_escura.png` |
| Alagard (fonte) | Hewett Tsoi | [CONFIRMAR link] | [CONFIRMAR licença] | `fonts/alagard.ttf` |

## Feito pela equipe

- **Protagonista** (feiticeira de chifres) e **Rei dos Ratos** (garoto de boné montado no rato gigante):
  modelos feitos pelo Gabriel no PixelLab (32x32 e 48x48, 8 direções). Originais em
  `assets/fontes/heroina/` e `assets/fontes/rei_rato/`. No jogo: `img/personagens/heroina.png`
  (animações geradas por `tools/gerar_heroina.py` a partir da vista "west") e
  `img/chefes/rei_rato_{parado,andando,ataque}.png` (vista "south-west"). [CONFIRMAR com o grupo a
  descrição para a seção "Uso de IA" e os termos do PixelLab.]
- Modelos de NPCs/criaturas da folha da equipe (`assets/fontes/npcs_modelos.webp` → `img/personagens/npcs.png`,
  por `tools/importar_modelos.py`): a pedido do Gabriel, **só os monstros** ainda usam (lobo, goblin,
  diabrete, espírito, lich) até chegarem as artes originais. [CONFIRMAR com o grupo como foram feitos.]
- Elenco humano: recoloração por região das bases da feiticeira (pacote "sample") e do espadachim
  (Metroidvania Forge) com acessórios desenhados por código (`src/elenco.py`).
- Feiticeiro da Maré, ratos, gaivotas, canhões e caixotes: desenhados por código em `src/pixelart.py`.
- Ícones de itens, tábuas de madeira, espinhos, mastro, velas, vigas e decoração do navio:
  desenhados por código (`src/tiles.py`, `src/background.py`, `src/objects.py`).
- `sons/efeitos/step.wav` e `skid.wav`: gerados por `tools/gerar_sons.py`.
- Acentos da fonte (á, ã, ç, é, ê, í, ó, õ, ú…): compostos pixel a pixel em `src/fonte.py`.

## Observações

- O logo "Metroidvania Forge" não é usado no jogo.
- O pacote "Cozy UI Pack (demo)" e "FreeButtons" foram avaliados e **não** são usados.
- Avaliados e ainda não usados: "free sky with clouds" (licença em `License.txt` do pacote),
  "Coin Gems", "FREE" (ícones SunGraphica), "Input Prompts Pack".
