---
tipo: guia
atualizado: 2026-10-22
---

# Guia para IAs colaboradoras

Leia isto antes de mexer no jogo. Histórico em [[Registro de alterações]]; decisões em [[Jogo A3]].

## Contexto
- Trabalho A3 da USJT (Usabilidade, desenvolvimento web, mobile e jogos; prof. Elzo Brito dos Santos Filho).
- Jogo: **Maré de Mentiras**, metroidvania 2D de **ação** em pixel art (Python 3.12 + pygame-ce).
- Em 2026-10-22 o Gabriel trocou a investigação (pistas, maré, interrogatório) por ação: parkour,
  chefes diferenciados e "jogo curto completo". A história do roteiro foi adaptada, não seguida 100%.
- Repositório **privado**: https://github.com/GabrielLima2006/JogoA3 . **Nunca** colocar IA como coautora
  nos commits (sem `Co-Authored-By`). `AGENTS.md`/`CLAUDE.md` ficam fora do repo (`.gitignore`).
- Declaração de uso de IA no README (seção 9) fica para o grupo decidir. Não preencher sozinho.

## Onde está tudo
- Código: `C:\Users\gabri\OneDrive\Documentos\Jogo A3\jogo\`
- Jogar: `python main.py` · Testar: `python tests/run_tests.py` (todos devem passar, ~3 min).
- Executável: `python -m PyInstaller --noconfirm --windowed --name MareDeMentiras --add-data "assets;assets" main.py`
  → `dist/MareDeMentiras/` (zip para o grupo: `dist/MareDeMentiras.zip`). Save fica em `saves/` ao lado do exe.
- Assets usados: `jogo/assets/` (créditos em `assets/CREDITOS.md`, campos `[CONFIRMAR]`). Pacotes originais:
  `Jogo A3\assets internet\` — ver [[Assets da internet]].

## Mundo (src/chapter1.py)
13 salas, ligadas por dígitos nas bordas (`ROOM_LINKS`), layout por BFS:
- Protagonista única: a feiticeira ("ela"). Dash desde o começo (`chapter1.START_ABILITIES`).
- **Navio:** cabine (início, bola de cristal) → convés (hub: capitã, amigo, loja `$`, ferreiro `R`)
  → escotilha → porão (tábuas que desabam, poça) → porão alagado (plataformas móveis, carta 1)
  → **Toca dos Ratos** (chefe O Grumete / Rei dos Ratos → pulo duplo).
- **Cordame** (último degrau do mastro exige pulo duplo): cordame → vergas (carta 2)
  → **Cesto da Gávea** (chefe O Imediato / Cavaleiro Rubro → fragmento + flag `atracado`, abre a prancha `D`).
- **Ilha:** praia (vala de espinhos, penhasco de pulo duplo) → floresta (vertical, carta 3)
  → **Ruínas** (chefe A Irmã da Capitã / Lâmina da Tempestade) → Templo da Maré (espinhos, tábuas)
  → **Altar** (chefe final O Melhor Amigo / Feiticeiro da Maré).
- Final verdadeiro com as 3 cartas; comum sem elas. Depois: tela de resultado (nota S/A/B/C, recorde).

## Arquitetura (src/)
- `states.py` PlayState (salas, inimigos, chefes, movers, tábuas `C`, perigos), Pause (continuar, bola de cristal,
  som, reiniciar com confirmação, menu, sair), Death, BossIntro, Ending, Results.
- `bosses.py` 4 chefes (fases, telegraph piscando, invulnerável na transformação do Cavaleiro).
- `creatures.py` inimigos do mundo; `movers.py` plataformas móveis; `tiles.py` tiles por tema;
  `background.py` parallax, decoração presa ao mundo (lanternas, escotilhas, barris/caixotes, vigas,
  mastro com velas, amurada, braseiros), chuva, relâmpago e vinheta.
- `skins.py` sprite da feiticeira (idle/walk do pacote + ações de `tools/gerar_feiticeira.py`, âncora por animação).
- `elenco.py` humanos derivados do sprite dela (paleta por região + acessórios); `pixelart.py` bichos, chefe final, objetos.
- História completa: `docs/HISTORIA.md` (cópia em [[História do jogo]]).
- `fonte.py` fonte pixel (alagard) com acentos compostos. Escala: tamanho ≤30 → 1x, ≤56 → 2x, maior → 3x;
  `title=True` soma 1 quando tamanho > 40.
- `ui.py` HUD (orbe, corações, moedas, cartas, habilidades, tempo), barra de chefe no topo, Menu.
- `menus.py` menu, novo jogo (retratos com sprites reais), intro, como jogar (3 páginas), recordes, créditos rolando.

## Regras
1. Não alterar `Player`, `Physics`, `Dash`, `Combat` em `src/config.py` sem pedir (aprovados pelo Gabriel).
2. Controles fixos (README). Nunca J/K/L.
3. Textos em pt-BR.
4. Todo salto obrigatório novo entra nos testes de alcance (`PATHS_*` e `GATES` em `tests/test_ship.py`).
   Altura confortável de pulo simples: 3 tiles. 4+ exige pulo duplo.
5. Ao terminar: atualizar este guia e o [[Registro de alterações]].

## Próximos passos (pedidos do Gabriel, 2026-10-22)
Detalhes em `jogo/docs/DESENVOLVIMENTO.md` → "Próximos passos". Regra geral: inspirado em Hollow Knight, **sem copiar**.
1. Corrigir modelos no jogo (chapéus, cabelo, peles, tamanhos, restos da espada, chefe final no estilo antigo).
2. Fluidez da movimentação: mais quadros de transição (virar, parar, subir/descer no ar), sem mexer na física aprovada.
3. Melhorar animações (golpes, cura, dano, morte, idle; inimigos e NPCs).
4. Golpe na diagonal: lógica existe, falta animação própria (hoje usa a pose "para cima").
5. Level design mais vivo: NPCs andando, animais, objetos balançando, água com ondas, partículas, segredos.
6. Chefes com identidade própria (não parecer cópia de chefes do Hollow): água no Rei dos Ratos, vergas e vento
   no Cavaleiro, canhões e cordas na Irmã, maré e ilusões no Feiticeiro.
7. Menu de amuletos novo: tela própria, ícones, custo, espaços, mouse e teclado, prévia do efeito.

## Pendências
- Grupo: nomes/RA, divisão de tarefas, seção de IA, links e licenças `[CONFIRMAR]` (README e `assets/CREDITOS.md`, lista `CREDITS` em `src/menus.py`).
- Testes com jogadores reais: dificuldade dos chefes, preços da loja, textos.
- Ideias: mais variedade de inimigos na ilha, música própria por área (hoje 3 faixas).

Voltar: [[Cérebro]]
