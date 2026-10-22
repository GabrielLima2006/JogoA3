# Desenvolvimento — decisões, estado e histórico

Documento de referência do projeto: o que foi decidido, como o jogo está organizado e o que falta.
A história completa está em [HISTORIA.md](HISTORIA.md). As notas de planejamento (cofre do Obsidian) estão em [obsidian/](obsidian/LEIA-ME.md).

## Decisões de design

- **Gênero:** metroidvania 2D de ação curto e completo: 3 áreas, 13 salas, 4 chefes, introdução,
  dois finais e tela de resultado.
- **Protagonista única:** a feiticeira. Uma versão com protagonista masculino foi testada e retirada porque
  os dois sprites tinham estilos muito diferentes.
- **Controle:** movimento, pulo, dash e golpes foram ajustados e aprovados nos testes do grupo; os valores
  ficam em `src/config.py` (`Player`, `Physics`, `Dash`, `Combat`) e não devem mudar sem combinar.
- **Teclas fixas:** A/D ou setas, Espaço, Shift, mouse esquerdo/direito, W/S para mirar, F, W, Tab, M, ESC/P.
- **Progressão:** dash desde o começo; pulo duplo depois do primeiro chefe (abre o mastro e a ilha); o segundo
  chefe faz o navio atracar (abre a prancha para a ilha).
- **Visual único:** todos os humanos derivam do sprite da protagonista (mesmo traço e mesmas animações),
  com outras cores, cabelos e acessórios.
- **Dificuldade:** Fácil (7 corações, inimigos com 75% da vida), Normal (5), Difícil (4, inimigos com 135%).

## Organização do código

| Arquivo | Conteúdo |
|---|---|
| `main.py` | Aplicativo e troca de telas |
| `src/chapter1.py` | Salas, ligações, itens, chefes, falas, cartas e finais |
| `src/states.py` | Partida, pausa, morte, apresentação de chefe, finais, resultado |
| `src/player.py`, `src/physics.py`, `src/combat.py` | Jogador, colisão e golpes |
| `src/bosses.py`, `src/creatures.py`, `src/enemies.py` | Chefes e inimigos |
| `src/skins.py` | Animações da protagonista |
| `src/elenco.py` | Tripulação e capangas derivados do sprite da protagonista |
| `src/pixelart.py` | Ratos, gaivotas, chefe final, canhões e caixas desenhados no código |
| `src/background.py`, `src/tiles.py` | Cenários, parallax, decoração, chuva |
| `src/ui.py`, `src/menus.py`, `src/fonte.py` | HUD, menus e fonte com acentos |
| `tools/gerar_feiticeira.py` | Gera as animações de ação da protagonista |
| `tests/` | Testes automáticos (`python tests/run_tests.py`) |

## Animações da protagonista

O pacote gratuito da personagem traz só "parada", "andando" e a transição entre as duas. As outras
animações foram criadas pela equipe com `tools/gerar_feiticeira.py`, que separa cabeça, cabelo, tronco e
pernas do sprite original, tira a espada escura, gira o tronco na cintura, faz o cabelo arrastar e desenha
braço e lâmina em cada pose. Para refazer depois de mudar o script:

```bash
python tools/gerar_feiticeira.py
```

## Testes

`python tests/run_tests.py` roda tudo sem abrir janela (cerca de 3 minutos): física, menus, portas,
chefes, itens, finais e uma busca automática que prova que todo salto obrigatório é possível com as
habilidades daquele trecho, e impossível antes delas.

## Histórico

- **Base:** motor de plataforma com física em passo fixo de 120 Hz, dash, golpes rápido e pesado, mira
  para cima/baixo com quique, cura com F, bancos, loja, ferreiro, amuletos e mapa.
- **Primeira ideia:** investigação no navio (pistas, maré subindo, interrogatório). Trocada por ação.
- **Mundo de ação:** 13 salas, 4 chefes com 2 fases, plataformas móveis, tábuas que desabam, cartas e finais.
- **Visual:** fonte com acentos, cenários com parallax, decoração do navio, chuva, relâmpago e vinheta.
- **Entrega A3:** README completo, créditos, capturas de tela, executável e release no GitHub.
- **Protagonista única, dash inicial, animações novas e elenco no estilo dela.**

## Próximos passos

Direção geral: o jogo é **inspirado** em Hollow Knight (exploração, bancos, amuletos, golpe para baixo com
quique), mas **não pode ser uma cópia**. Cada sistema e cada chefe precisa ter identidade própria ligada ao
navio, à maré e à história da feiticeira que finge ser maga.

1. **Corrigir modelos no jogo:** revisar personagens que ficaram estranhos em cena (chapéus, cabelo curto,
   cores de pele, tamanhos, restos de pixels da espada original), o chefe final (ainda no estilo antigo) e a
   escala dos chefes em relação à protagonista.
2. **Fluidez da movimentação:** mais quadros de transição (virar, começar e parar de correr, subir/descer no
   ar, aterrissar), sem mudar os valores de física aprovados.
3. **Melhorar animações:** golpes com mais quadros e rastro, cura, dano e morte mais expressivos, idle com
   variações; inimigos e NPCs com reações próprias.
4. **Golpe na diagonal:** a mira diagonal (W + A/D + ataque) continua na lógica, mas usa a pose de golpe para
   cima. Criar quadros próprios da diagonal e conferir o alcance do golpe.
5. **Level design mais vivo:** NPCs andando e reagindo, animais, objetos que balançam com o navio, água com
   ondas, luz das lanternas, partículas (respingos, folhas, poeira), mais caminhos secretos e salas com
   identidade visual própria.
6. **Chefes com identidade própria:** rever os padrões de ataque para não lembrarem chefes de Hollow Knight.
   Ideias: o Rei dos Ratos usar o porão alagado (sobe e desce a água), o Cavaleiro Rubro lutar nas vergas
   balançando com o vento, a Irmã da Capitã usar canhões e cordas do navio, o Feiticeiro da Maré controlar
   a maré da arena e criar ilusões (tema da mentira).
7. **Menu de amuletos:** tela própria, com ícones desenhados, descrição, custo e espaços livres, equipar e
   desequipar com mouse e teclado, e prévia do efeito.

## Pendências

- Nomes e RA dos integrantes, divisão de tarefas e seção "Uso de IA" no README.
- Links e licenças marcados com [CONFIRMAR] em `assets/CREDITOS.md`.
- Cronometrar partidas reais para confirmar a duração estimada.
- Testes com jogadores: dificuldade dos chefes e preços da loja.
