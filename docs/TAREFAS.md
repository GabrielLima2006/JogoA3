# Tarefas para o grupo

Cada tarefa é independente e pode ser feita por uma pessoa (com a IA dela) sem mexer no trabalho das outras.
Antes de começar: leia `README.md` e `docs/DESENVOLVIMENTO.md`, rode o jogo (`python main.py`) e os testes
(`python tests/run_tests.py`, todos precisam passar no fim).

## Regras para todo mundo

1. **Uma branch por tarefa:** `git checkout -b tarefa-<numero>-<nome>`. Nada direto na `main`.
2. **Só mexa nos arquivos da sua tarefa** (listados em cada uma). Precisou mexer em outro? Avise no grupo.
3. **Não altere os valores de movimento e combate** (`Player`, `Physics`, `Dash`, `Combat` em `src/config.py`).
4. **Controles fixos** (README, seção 4). Nunca use J/K/L.
5. Textos do jogo em português; parâmetros novos ficam em `src/config.py`.
6. Sala nova ou salto novo: adicione o caminho nos testes de alcance (`PATHS_*` em `tests/test_ship.py`).
7. Ao terminar: testes passando, um print da tela, e abra um Pull Request descrevendo o que mudou.
8. Para a IA de vocês: peçam que ela leia este arquivo e o `docs/DESENVOLVIMENTO.md` antes de tudo.

---

## Tarefa 1 — Modelos dos personagens (arte)
**Arquivos:** `assets/img/personagens/`, `assets/fontes/`, `tools/importar_modelos.py`, `src/creatures.py`
- Gerar os sprites com as descrições de `docs/HISTORIA.md` (seção "Descrições para gerar modelos").
- Padrão: vista lateral, ~64 px de altura, fundo transparente, olhando para a direita.
- Colocar as folhas em `assets/fontes/` e ajustar o importador; trocar inimigos/NPCs que ficarem melhores.
- **Pronto quando:** cada personagem novo aparece no jogo com parado e andando, sem cortes.

## Tarefa 2 — Arma de fogo com mira no cursor
**Arquivos:** `src/player.py` (só um método novo), `src/combat.py`, `src/input.py`, `src/ui.py`, `tests/test_mechanics.py`
- Item novo (comprável na loja). Segurar **Q** mostra uma mira no cursor; clique esquerdo atira na direção dele.
- Munição limitada que recarrega no banco (bola de cristal); contador no HUD.
- **Pronto quando:** dá para atirar nos inimigos mirando com o mouse, com teste cobrindo tiro e munição.

## Tarefa 3 — Sons e música
**Arquivos:** `assets/sons/`, `src/audio.py`, `src/config.py` (classe `Audio`), `assets/CREDITOS.md`
- Música própria por área (navio, ilha, templo, chefe) e sons que faltam (porta, plataforma que desaba, água).
- Volume de música/efeitos na tela de pausa.
- **Pronto quando:** cada área tem música e todo som novo está nos créditos com autor e licença.

## Tarefa 4 — Level design: salas novas e segredos
**Arquivos:** `src/chapter1.py` (salas), `tests/test_ship.py` (caminhos)
- Mais 2 ou 3 salas opcionais com desafio de plataforma e recompensa (amuleto, fragmento de vida).
- Paredes falsas com segredos; inimigos posicionados para criar desafio.
- **Pronto quando:** salas novas ligadas ao mapa, com testes de alcance passando.

## Tarefa 5 — Chefes: equilíbrio e polimento
**Arquivos:** `src/bosses.py`, `tests/test_ship.py` (teste dos chefes)
- Jogar cada chefe e ajustar vida, tempos de aviso e janelas de punição; sons e efeitos de cada ataque.
- **Pronto quando:** cada chefe vence em 1 a 3 minutos sem ser injusto (anotar tempos e mortes).

## Tarefa 6 — Interface e menus
**Arquivos:** `src/menus.py`, `src/ui.py`, `src/amuletos.py`
- Mapa (Tab) mais bonito, tela de pausa com volume, ícones de teclas nos "Como jogar".
- **Pronto quando:** todas as telas sem texto sobreposto em 960x540.

## Tarefa 7 — Documentação da entrega (A3)
**Arquivos:** `README.md`, `assets/CREDITOS.md`, `docs/`
- Preencher integrantes/RA, divisão de tarefas, seção "Uso de IA" (decisão do grupo), links e licenças
  `[CONFIRMAR]`, screenshots atualizados.
- **Pronto quando:** nenhum `[CONFIRMAR]` e nenhum `[nome]` no README.

## Tarefa 8 — Testes com jogadores
**Arquivos:** `docs/TESTES_JOGADORES.md` (novo)
- 3 a 5 pessoas jogando o executável; anotar tempo, mortes, onde travaram, o que acharam difícil.
- **Pronto quando:** relatório com problemas priorizados para o grupo corrigir.

## Depois (história)
A história está pausada até a versão jogável ficar polida. Rascunho atual em `docs/HISTORIA.md`.
