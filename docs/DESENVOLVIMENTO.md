# Desenvolvimento — decisões, estado e histórico

Documento de referência do projeto: o que foi decidido, como o jogo está organizado e o que falta.
A história completa está em [HISTORIA.md](HISTORIA.md).

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

## Pendências

- Nomes e RA dos integrantes, divisão de tarefas e seção "Uso de IA" no README.
- Links e licenças marcados com [CONFIRMAR] em `assets/CREDITOS.md`.
- Cronometrar partidas reais para confirmar a duração estimada.
- Testes com jogadores: dificuldade dos chefes e preços da loja.
