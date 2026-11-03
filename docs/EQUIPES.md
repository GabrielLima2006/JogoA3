# Frentes de trabalho

Várias frentes trabalham ao mesmo tempo nesta pasta. Cada uma só edita os próprios arquivos.

| Frente | Arquivos |
|---|---|
| Gameplay | `src/player.py`, `src/combat.py`, `src/physics.py`, `src/states.py`, `src/config.py`, `src/amuletos.py`, `src/enemies.py`, `src/audio.py`, `src/input.py`, lógica de `src/bosses.py` e `src/creatures.py`, `tests/test_mechanics.py`, `tests/test_world.py` |
| Arte | `assets/`, `tools/`, `src/tiles.py`, `src/paisagem.py`, `src/background.py`, `src/elenco.py`, `src/pixelart.py`, `src/sprites.py`, `src/skins.py`, `src/objects.py`, métodos `draw` de `src/bosses.py` e `src/creatures.py`, `assets/CREDITOS.md`, `docs/PERSONAGENS.md` |
| Fases | `src/chapter1.py` (salas, itens, inimigos; não os textos), `tests/test_ship.py` |
| Interface | `src/ui.py`, `src/menus.py`, `src/fonte.py`, `tests/test_menus.py` |
| Integração e testes | `docs/QA.md`, `docs/qa/`, `docs/PENDENCIAS.md` (seção própria), commits e envio ao GitHub |

Regras para todas:
- Não mudar os valores aprovados de `Player`, `Physics`, `Dash` e `Combat` em `src/config.py`.
- Controles fixos (nunca J/K/L). Textos e comentários em pt-BR.
- A história está pausada: não mudar textos de história.
- Ler só os trechos de arquivo necessários; rodar os testes da própria área durante o trabalho e a suíte
  completa (`python tests/run_tests.py`) no fim; poucas capturas, pequenas.
- Só a frente de Integração faz commit e push. Mensagens de commit descrevem o jogo, sem falar de
  sessões, ferramentas ou uso do plano, e sem coautor.
- Limite de uso: ao fim de cada etapa, consultar `mcp__ccd_session_mgmt__get_usage`. Com 5 horas ou semana
  em 95% ou mais: parar, deixar os testes passando, registrar o que foi feito e o que falta na própria seção
  de `docs/PENDENCIAS.md` e encerrar.
- Pendências e problemas conhecidos: `docs/PENDENCIAS.md` e `docs/QA.md`. Personagens: `docs/PERSONAGENS.md`.
  Artes novas do Gabriel: `C:\Users\gabri\OneDrive\Documentos\Jogo A3\Personagens gerados por mim` (podem chegar mais).
