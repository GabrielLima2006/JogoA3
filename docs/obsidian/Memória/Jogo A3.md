---
tipo: projeto
criado: 2026-10-22
atualizado: 2026-10-22
---

# Jogo A3

Metroidvania 2D em **Python 3 + pygame-ce**. Código em `C:\Users\gabri\OneDrive\Documentos\Jogo A3\jogo` (ZIP: `Jogo A3\metroidvania-prototipo.zip`).

## Fase atual: base de gameplay (protótipo)
Nome, história, lore, personagens e arte final **ainda não definidos — de propósito**. Prioridade = qualidade de movimento e combate antes de conteúdo.

## Controles fixados pelo Gabriel
A/D ou setas mover · Espaço pular (altura variável) · Shift esq. dash · Mouse esq. ataque rápido · Mouse dir. ataque pesado · ESC pausa. **Nunca usar J/K/L.**

## Estado (2026-10-22)
- Protótipo completo: movimento (coyote, buffer, pulo variável, pulo duplo), dash, 2 ataques, 3 inimigos (patrulheiro, perseguidor, torreta), 5 salas em circuito, HUD, pausa, morte/checkpoint.
- Física em passo fixo 120 Hz; todos os parâmetros em `game/config.py`.
- `python tests/test_gameplay.py` → 114/114 passando (inclui busca automática provando que cada salto do mapa é alcançável).
- Falta: teste de "feel" com as mãos do Gabriel e ajuste fino dos números.

## Feedback do Gabriel (2026-10-22)
- **Aprovado — não mexer sem pedir:** pulo, corrida, ataques e dash (valores atuais do `config.py`).
- Achou inimigos e mapa simples demais → expansão estilo Hollow Knight.

## Expansão 2 (decidida em 2026-10-22)
- Dash e pulo duplo viram itens achados no mapa, abrindo caminhos (progressão metroidvania).
- Energia por acerto + tecla F (segurar) para curar.
- Amuletos com slots (equipa no banco), fragmentos de vida (4 = +1 vida), ferreiro (upgrade de arma com moedas + minério), mapa comprado na loja + amuleto bússola.
- Bancos salvam em arquivo; menu ganha "Continuar".
- Moedas caem dos inimigos; ao morrer ficam numa bolsa recuperável.

### Estado da expansão 2 (2026-10-22) — implementada
- 13 salas em 4 zonas (Cavernas, Vila, Jardins, Alturas). Portas = dígitos na borda; `ROOM_LINKS` em `game/rooms.py`; layout do mapa calculado sozinho.
- Ordem: Guardião (chefe) → Dash → Jardins → Pulo duplo → Alturas.
- Novos inimigos: voador, saltador, escudeiro (bloqueia rápido, pesado quebra guarda), Guardião.
- Dano base dobrado (rápido 2, pesado 5) e HP dos inimigos também → mesma quantidade de golpes.
- Save: `saves/save.json`. Testes: `python tests/run_tests.py` → 223/223 (busca automática prova alcance e bloqueios por habilidade).
- Falta: Gabriel testar exploração, chefe e economia (preços).

### Ajustes pedidos depois do teste (2026-10-22) — feitos
- S desce de plataforma de mão única.
- Mira por teclado (escolha do Gabriel): W + ataque = cima, W+A/D = diagonal, S + ataque no ar = baixo com quique (pogo) que devolve pulo duplo e dash. Testes: 235/235.

### Direção nova (2026-10-22)
Gabriel escolheu o **híbrido**: metroidvania no navio do roteiro A3 (pistas, maré subindo, credibilidade = vida, interrogatório = duelo). Plano do capítulo 1 em [[Capítulo 1 - Jantar no molhado em veneno]] — **aprovado**.
- Etapa 1 feita (2026-10-22): `game/menus.py` (menu com 6 opções, protagonista ele/ela, dificuldade = minutos de maré, introdução com formas de gênero, como jogar, recordes, créditos), `game/records.py`. Título provisório "Maré de Mentiras" em `config.Game`. Testes 264/264.
- Etapa 2 feita (2026-10-22): navio com 9 salas em `game/chapter1.py`, personagens com diálogo, chave da cabine, porão alagado que exige dash. Testes 322/322.
- Próxima: etapa 3 — pistas, depoimentos e caderno. Detalhes em [[Guia para IAs colaboradoras]].
- Gabriel pediu (2026-10-22) que tudo fique registrado no Obsidian para outras IAs colaborarem → guia + [[Registro de alterações]] + `AGENTS.md` no código.

## Decisões de design
- Dash cancela preparação/recuperação de golpe; na fase ativa fica em buffer.
- Clique durante golpe/dash vira buffer (160 ms).
- Espinhos/buracos: -1 vida e volta ao último chão seguro.
- Golpes destroem projéteis.

### Direção atual (2026-10-22, mais recente)
Investigação abandonada: agora é **metroidvania de ação** curto e completo (3 áreas, 4 chefes, intro, finais
verdadeiro/comum, resultado). Arte: mistura de assets do itch.io + pixel art por código. Repo privado
GabrielLima2006/JogoA3, commits só em nome do Gabriel. Seção "Uso de IA" do README: o grupo decide depois.
Detalhes e pendências em [[Guia para IAs colaboradoras]].

### Correção pendente (2026-10-22)
Cair em água/espinhos deve voltar ao último checkpoint (hoje volta ao último chão firme e pode entrar em loop).

### Próximos passos pedidos (2026-10-22)
Modelos no jogo, fluidez, animações, golpe diagonal com animação, level design vivo, chefes sem cópia do
Hollow, menu de amuletos, nomes dos personagens, arma de fogo com mira no cursor. Lista completa em [[Guia para IAs colaboradoras]].

Ver também: [[Gabriel]] · Voltar: [[Cérebro]]
