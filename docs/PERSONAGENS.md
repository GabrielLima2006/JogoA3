# Inventário de personagens

Conferido em 3 de novembro de 2026. As artes novas foram salvas também na pasta
`Personagens gerados por mim`, em subpastas com o nome de cada personagem.

## Elenco

| Personagem | Situação |
|---|---|
| Nyra, protagonista | Completa para jogar; o jogo gera corrida, pulo, dash, dano e demais ações. |
| Tico, Rei dos Ratos | Já tem caminhada e pulo; preservar essas animações e só preencher alguma ação que a revisão confirmar ausente. |
| Aldric, Cavaleiro Rubro | Já tem caminhada e pulo nos arquivos em `Personagens gerados por mim/Cavaleiro Rubro`; preservar essas animações e só preencher alguma ação que a revisão confirmar ausente. |
| Selka, Canhoneira da Tempestade | `anim_selka.png` tem repouso, caminhada e ataque; faltam salto/pouso e ações separadas para bote, pistola e canhão. |
| Capitã Maren | Arte PixelLab em pé (`maren.png`, retrato do diálogo). Caída no Convés: pose própria deitada de costas, desenhada à mão sobre a paleta dela (`maren_caida.png`, `tools/desenhar_maren_caida.py`). |
| Caelum, Feiticeiro da Maré | `anim_caelum.png` tem repouso e conjuração. Como chefe flutuante, faltam ciclos próprios de voo, teleporte e ataque mágico. |
| Comerciantes, ferreira, curandeira, pescador, estudioso, bardo, ancião, anciã, aldeã e grumete | Sprite próprio PixelLab com folha `anim_<nome>.png`: respiração parada (4 quadros), caminhada (6) e ataque (3). Alturas acertadas pela protagonista (60 px): adultos 55–57, idosos 52–53, grumete 47. |
| Lobo e goblin | Sprites laterais próprios com folhas provisórias de passada, respiração e ataque; conferir a qualidade e refazer se necessário. Lobo reduzido para 44 px de altura, goblin 52 px. |
| Diabrete, ladino e cavaleiro do escudo | Modelos da folha da equipe. Os ciclos provisórios de caminhada foram rejeitados e retirados do jogo; faltam animações próprias de caminhada, salto/queda e ataque. |
| Espírito e lich | Modelos da folha da equipe com conjuração própria (`anim_espirito.png`, `anim_lich.png`): recolhem, carregam com brilho roxo e lançam para a frente. Lich conjura no aviso do tiro; espírito carrega no alerta e lança ao perseguir. Flutuação continua pelo balanço do jogo. |
| Múmia e cavaleiro negro | Continuam usando as animações próprias do pacote Skeletons Free Pack. |

## Artes novas

As vistas laterais usadas no jogo são `east`; a direção é invertida quando o personagem
precisa olhar para a esquerda. Arquivos de origem, rotações e receitas estão em
`assets/fontes/pixellab/` e na pasta externa indicada acima.

Diabrete, espírito, lich, ladino e cavaleiro do escudo usam os modelos sombreados da folha
`assets/img/personagens/npcs.png`, que combina melhor com a arte dos demais inimigos.

| Personagem | Arquivo do jogo | PixelLab ID |
|---|---|---|
| Ferreira da Ilha | `assets/img/personagens/npc_ferreira.png` | `c4269172-c32f-4253-a411-84066cc4d000` |
| Comerciante da Ilha | `assets/img/personagens/npc_comerciante.png` | `ff1d9de7-9de4-46a2-83e3-80d8d95f6261` |
| Curandeira da Ilha | `assets/img/personagens/npc_curandeira.png` | `e8e0e7c0-6f9d-4861-ae26-a7fcd14147e7` |
| Pescador da Ilha | `assets/img/personagens/npc_pescador.png` | `d9e5fe12-2ef2-4d1e-81d8-cd1c6d50c322` |
| Estudioso da Ilha | `assets/img/personagens/npc_estudioso.png` | `2f3ecae9-672d-4cc7-9803-cb5b71a49c51` |
| Bardo da Ilha | `assets/img/personagens/npc_bardo.png` | `2a5ce15e-e044-4fcc-96ab-042cf4be36e1` |
| Ancião da Ilha | `assets/img/personagens/npc_anciao.png` | `bf8088cf-2227-4099-8672-c25b0404600d` |
| Anciã da Ilha | `assets/img/personagens/npc_ancia.png` | `8390887b-0101-41f9-82a9-9524bb2b8060` |
| Aldeã da Ilha | `assets/img/personagens/npc_aldea.png` | `f7c26130-326f-4b01-8c02-1559e6e1e138` |
| Grumete | `assets/img/personagens/npc_grumete.png` | `656bd253-5bfb-4f56-9196-4b95d84d2255` |
| Lobo da Ilha | `assets/img/personagens/inimigo_lobo.png` | `783d2f66-0797-4f24-a734-d62a09334809` |
| Goblin da Ilha | `assets/img/personagens/inimigo_goblin.png` | `581b02e2-e107-4086-bd4c-09114624dda6` |

As imagens foram conferidas na galeria. A tabela acima marca quais ações ainda precisam de quadros
próprios. As animações não devem alterar física nem comportamento dos inimigos e chefes.

## Estado das folhas provisórias

`tools/animar_pose.py` criou folhas provisórias para lobo, goblin, NPCs, Selka e Caelum. Elas não
substituem as ações específicas listadas na tabela. Os NPCs não são prioridade nesta revisão.

Os ciclos de caminhada do diabrete, ladino e cavaleiro do escudo foram rejeitados pelo Gabriel e
removidos do jogo. Os arquivos de rascunho ainda estão nas pastas externas desses personagens;
não devem ser usados como versão final. Criar folhas novas a partir das artes de referência guardadas
em `Personagens gerados por mim`, com caminhada, salto/queda e ataque legíveis em quadros separados.
