# Maré de Mentiras

Metroidvania 2D de ação em pixel art, feito em Python com pygame-ce.

![Convés do navio](docs/screenshots/conves.png)

## ▶ Baixar e jogar (Windows)

Baixe **MareDeMentiras.exe** em [Releases](https://github.com/GabrielLima2006/JogoA3/releases/latest)
e dê dois cliques. Não precisa instalar nada. Se o Windows avisar "O Windows protegeu o computador",
clique em **Mais informações** e depois em **Executar assim mesmo** (o executável não é assinado).

## 1. Identificação

| | |
|---|---|
| **Jogo** | Maré de Mentiras |
| **Grupo** | [nome do grupo] |
| **Disciplina** | Usabilidade, desenvolvimento web, mobile e jogos |
| **Professor** | Elzo Brito dos Santos Filho |
| **Instituição** | Universidade São Judas Tadeu (USJT), 2026 |

| Integrante | RA |
|---|---|
| [nome] | [RA] |
| [nome] | [RA] |
| [nome] | [RA] |

## 2. Descrição

Noite de tempestade. Você viaja no navio da capitã fingindo ser feiticeira, mas seu único truque de
verdade é enganar bem e saber lutar. Gente do porto vem desaparecendo, a capitã
cai envenenada e a tripulação começa a agir como se estivesse enfeitiçada.

Explore o navio e a ilha onde ele atraca, enfrente quatro chefes com estilos de luta diferentes e
descubra quem está por trás da maldição da maré. Três cartas escondidas da capitã revelam a história
inteira e liberam o final verdadeiro.

- **3 áreas:** navio (cabine, convés, porão, cordame), ilha (praia, floresta, ruínas) e Templo da Maré.
- **4 chefes:** O Grumete (Rei dos Ratos), O Imediato (Cavaleiro Rubro), A Irmã da Capitã (Lâmina
  da Tempestade) e o chefe final, O Melhor Amigo (Feiticeiro da Maré). Todos têm duas fases.
- **Habilidades** que abrem caminho: dash (Passo ilusório) e pulo duplo (Levitação).
- **Parkour:** plataformas móveis, tábuas que desabam, espinhos, água e saltos que exigem as habilidades.
- **Itens:** moedas, comida que cura, amuletos, fragmentos de vida, loja e ferreiro.
- **Três dificuldades** (7, 5 ou 4 corações).
- **Dois finais:** comum e verdadeiro (com as 3 cartas).

## 3. Como rodar

Requisitos: Python 3.10 ou mais novo.

```bash
pip install -r requirements.txt
```

```bash
python main.py
```

No Windows também dá para usar o executável da pasta `dist/MareDeMentiras/` (ver
[Gerar o executável](#gerar-o-executável)) ou dar dois cliques em `Jogar.bat`.

## 4. Controles

| Tecla | Ação |
|---|---|
| A / D ou setas | Mover |
| Espaço | Pular (segurar = pulo mais alto) |
| Espaço no ar | Pulo duplo (depois de encontrar) |
| Shift esquerdo | Dash (depois de encontrar) |
| Botão esquerdo do mouse | Ataque rápido |
| Botão direito do mouse | Ataque pesado |
| W / S + ataque | Golpe para cima, na diagonal ou para baixo (no ar, quica em inimigos e espinhos) |
| S | Descer de plataformas finas |
| F (segurar) | Curar (gasta o orbe de foco) |
| W ou seta para cima | Interagir (bola de cristal, loja, personagens) |
| Tab | Mapa |
| M | Ligar/desligar o som |
| ESC ou P | Pausar (continuar, som, reiniciar, menu) |

Os controles também aparecem no jogo, em **Como jogar** e na tela de pausa.

## 5. Regras

- **Objetivo:** vencer o chefe final no Templo da Maré. Vencer os chefes anteriores libera habilidades
  e caminhos novos.
- **Vida:** cada golpe recebido tira um coração. Com zero corações você **perde**: volta à última
  bola de cristal e deixa parte das moedas para trás.
- **Cura:** golpes acertados enchem o orbe de foco; segure **F** para trocar foco por um coração.
  Comida recupera 2 corações.
- **Salvar:** a bola de cristal (W) salva o jogo e recupera a vida.
- **Perigos:** espinhos e água ferem e devolvem você ao último chão firme. Tábuas rachadas desabam
  pouco depois de pisadas.
- **Vitória:** derrotar o chefe final. Com as 3 cartas da capitã você vê o **final verdadeiro**.
- **Pontuação:** na tela final aparecem tempo, quedas, cartas, pontos e uma nota (S, A, B ou C).
  O HUD mostra corações, moedas, cartas e o tempo de jogo o tempo todo.

## 6. Divisão de tarefas

| Integrante | Tarefas |
|---|---|
| [nome] | [ex.: programação da movimentação e combate] |
| [nome] | [ex.: level design e roteiro] |
| [nome] | [ex.: arte, sons e créditos] |

## 7. Créditos

Todos os assets de terceiros são gratuitos. Autor, link e licença de cada um estão em
[`assets/CREDITOS.md`](assets/CREDITOS.md) e também aparecem na tela **Créditos** do jogo.

| Asset | Autor | Uso |
|---|---|---|
| Super Pixel Effects Gigapack (Free) | Will Tice / unTied Games | Efeitos de golpe, explosões, fumaça, fogo, raios |
| Metroidvania Forge | [CONFIRMAR autor] | Capangas, Cavaleiro Rubro, slime, tiles da ilha, objetos, sons e músicas |
| Feiticeira (idle & walk) | [CONFIRMAR autor] | Protagonista |
| Dark VFX 01–02 / Smear VFX 01 | [CONFIRMAR autor] | Magias do vilão e rastro dos golpes |
| UIBundleFree (Mediavel) | [CONFIRMAR autor] | Interface |
| pixelfood | Ghostpixxells | Comidas (itens de cura) |
| Tiny Texture Pack 1 e 2 | Screaming Brain Studios (CC0) | Paredes de madeira do navio |
| Fonte Alagard | Hewett Tsoi | Todos os textos (os acentos são desenhados pelo jogo) |

Os personagens do navio (capitã, grumete, imediato, irmã, amigo, mercador), o Rei dos Ratos, o
Feiticeiro da Maré, os ratos, as gaivotas, os canhões e os ícones de itens foram desenhados no código
(`src/pixelart.py`).

## 8. Tecnologia

- **Linguagem:** Python 3.12
- **Biblioteca:** pygame-ce 2.5
- **Executável:** PyInstaller
- **Testes:** suíte própria sem dependências (`python tests/run_tests.py`), que simula o jogo sem
  janela e confere física, salas, portas, chefes, menus e se todos os saltos obrigatórios são possíveis
  com as habilidades de cada trecho.

Estrutura:

```
main.py              ponto de entrada (estados: menu, jogo, pausa, finais)
src/                 código do jogo (física, jogador, inimigos, chefes, salas, interface)
assets/img/          imagens (personagens, chefes, efeitos, tiles, objetos, interface)
assets/sons/         efeitos sonoros e músicas
assets/fonts/        fonte
tests/               testes automáticos
docs/screenshots/    capturas de tela do README
```

## 9. Uso de IA

[O grupo vai preencher esta seção: quais partes foram feitas com ajuda de IA, quais ferramentas
foram usadas e como o grupo revisou o resultado.]

## 10. Screenshots

| | |
|---|---|
| ![Menu](docs/screenshots/menu.png) | ![Porão](docs/screenshots/porao.png) |
| ![Chefe: Cavaleiro Rubro](docs/screenshots/chefe_cavaleiro.png) | ![Templo da Maré](docs/screenshots/templo.png) |

## Gerar o executável

```bash
pip install pyinstaller
```

```bash
python -m PyInstaller --noconfirm --windowed --name MareDeMentiras --add-data "assets;assets" main.py
```

O jogo fica em `dist/MareDeMentiras/MareDeMentiras.exe`. Para enviar ao grupo, compacte a pasta
`dist/MareDeMentiras` inteira em um .zip. O save e os recordes ficam na pasta `saves/` ao lado do
executável.
