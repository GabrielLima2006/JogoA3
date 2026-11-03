# Inventário de personagens

Conferido em 3 de novembro de 2026. As artes novas foram salvas também na pasta
`Personagens gerados por mim`, em subpastas com o nome de cada personagem.

## Elenco

| Personagem | Situação |
|---|---|
| Nyra, protagonista | Completa para jogar; o jogo gera corrida, pulo, dash, dano e demais ações. |
| Tico, Rei dos Ratos | Completo; tem idle, caminhada, salto e ataque, e já é usado pelo chefe. |
| Aldric, Cavaleiro Rubro | Completo; seus arquivos ficam em `Personagens gerados por mim/Cavaleiro Rubro` e incluem idle, caminhada e ataque forte. |
| Selka, Canhoneira da Tempestade | Arte PixelLab integrada ao chefe. Faltam ciclos próprios de caminhada, espada e canhão. |
| Capitã Maren | Arte PixelLab integrada à cena da capitã caída; sem animação, adequada ao papel atual. |
| Caelum, Feiticeiro da Maré | Arte PixelLab integrada ao NPC, chefe e ilusões. Faltam ciclos próprios de caminhada e magia. |
| Comerciantes, ferreira, curandeira, pescador, estudioso, bardo, ancião, anciã, aldeã e grumete | Cada papel agora tem sprite próprio PixelLab, integrado ao desenho dos NPCs. Ainda usam pose estática com balanço simples; não têm ciclos próprios de caminhada. |
| Lobo e goblin | Sprites laterais próprios; ainda sem ciclo desenhado de caminhada. |
| Diabrete, ladino e cavaleiro do escudo | Modelos da folha da equipe com ciclo de caminhada de quatro quadros. Saltos usam o deslocamento vertical do jogo; o golpe usa o efeito de corte separado. |
| Espírito e lich | Modelos da folha da equipe; ainda sem ciclos próprios de ataque. |
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

As imagens foram conferidas na galeria. Os chefes Tico e Aldric já usam sequências de quadros;
Selka, Caelum e os inimigos restantes recebem poses de caminhada, salto e ataque pelo desenho
do jogo, sem alteração de física ou comportamento.
