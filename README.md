# Maré de Mentiras (título provisório)

Trabalho A3 de Usabilidade Web e Jogos (USJT, 2026). É um híbrido de **metroidvania com
investigação** a bordo de um navio, baseado no roteiro do grupo: pistas, maré subindo,
credibilidade como vida e interrogatório como duelo.

**Andamento** (o plano completo está no cofre do Obsidian, em `Planos/Capítulo 1`; o guia para IAs
colaboradoras está em `Projeto/Guia para IAs colaboradoras`, e o resumo em `AGENTS.md`):
- [x] Etapa 1: menu principal, escolha de protagonista (ele ou ela), dificuldade, introdução, como jogar,
  recordes e créditos.
- [x] Etapa 2: o navio com 9 salas, personagens com diálogo, chave da cabine e porão alagado.
- [ ] Etapas 3 a 8: pistas e caderno, maré, interrogatório, credibilidade e fechamento do capítulo.

## O navio (capítulo 1)

```
                       [Gávea]          <- meia-irmã, gaivotas
                          | mastro (cordame)
    [Tombadilho]------[Convés]------[Proa + cabine]   <- amigo; cama (salvar); baú = Passo ilusório
     imediato             | escotilha
    [Cabine capitã]=D=[Salão]--[Cozinha]--[Alojamento]
     (trancada)        capitã    cozinheira   grumete
                                   | alçapão
                                [Porão]          <- ratos; trecho alagado exige Passo ilusório
```

- **W** perto de um personagem conversa com ele. Na primeira vez você ouve o depoimento completo;
  depois, só uma fala curta.
- **Examinar** a capitã no salão dá a **chave** da cabine dela.
- **Cama na cabine do protagonista:** restaura a vida e salva o jogo.
- **Personagens e falas:** ficam em `src/chapter1.py` (`CHARACTERS`, `DIALOGS`). As falas usam
  `{feiticeiro}` e outros marcadores para o protagonista ele/ela.
- **Mundo de cavernas:** o antigo continua só para os testes do motor (`progress.chapter = 0`).

## Fluxo de telas

- **Menu:** Novo jogo, Continuar capítulo, Como jogar, Recordes, Créditos, Sair.
  Continuar fica desabilitado sem save.
- **Novo jogo:**
  1. Escolha o protagonista (Ele ou Ela). Muda o visual e as palavras da história
     (feiticeiro/feiticeira, passageiro/passageira).
  2. Escolha a dificuldade. Ela define a duração da maré: Fácil 20 min, Normal 14 min,
     Difícil 10 min.
  3. Veja a introdução: 5 telas com texto digitado e o cartão do capítulo. Enter avança e
     ESC pula.
- **Recordes:** ficam em `saves/records.json`, com nota, tempo, credibilidade, pistas e
  dificuldade.
- **Créditos:** a lista `CREDITS` em `src/menus.py` tem um espaço para os nomes do grupo.
- **Nome do jogo:** troque em `src/config.py`, na classe `Game`.

## Instalação e execução

```
pip install -r requirements.txt
python main.py
```

No Windows, também dá para abrir com dois cliques em `Jogar.bat`.

Testes automatizados (sem abrir janela, cerca de 2 minutos):

```
python tests/run_tests.py
```

## Controles

| Tecla | Ação |
|---|---|
| A / D ou setas ← → | mover |
| Espaço | pular (segure para ir mais alto) |
| Espaço no ar | pulo duplo, depois de encontrá-lo |
| Shift esquerdo | dash, depois de encontrá-lo |
| Botão esquerdo do mouse | ataque rápido |
| Botão direito do mouse | ataque pesado |
| W + ataque | golpe para cima (W + A/D = diagonal para cima) |
| S + ataque no ar | golpe para baixo (S + A/D = diagonal para baixo); ao acertar inimigo, projétil ou espinho, **quica** e recupera pulo duplo e dash |
| S (tocar) | descer de plataforma de mão única (as de madeira) |
| F (segurar) | curar 1 de vida gastando energia (parado no chão) |
| W ou seta ↑ | interagir: sentar no banco, falar com a loja ou o ferreiro |
| M ou Tab | mapa |
| ESC | pausa e inventário |
| F3 | (desenvolvimento) hitboxes, FPS e estado do jogador |

Nos menus: W/S ou setas para navegar, Enter/Espaço ou clique para escolher, ESC para sair.
Sem W/S o golpe sai para a frente, como antes. No chão, S + ataque também sai para a frente.
O mapeamento fica em `src/input.py` (`DEFAULT_BINDINGS`) e pode ser trocado.

## Como o jogo funciona

**Progressão.** O jogo começa só com pulo e ataques.
- O **Guardião** (chefe da Arena) protege o **Dash**.
- Com o dash você atravessa o fosso de 9 tiles da Vila e chega aos Jardins. No fim deles
  está o **Pulo duplo**.
- Com o pulo duplo você alcança a plataforma alta da Vila, que leva às Alturas. Lá estão
  segredos, minérios e amuletos.

Os testes automáticos confirmam que cada trecho é alcançável com as habilidades certas e
impossível sem elas.

**Energia e cura.** Cada golpe que acerta enche o orbe de energia (rápido +11, pesado +16).
Segurar F parado no chão por 0,9 s gasta 33 de energia e cura 1 de vida. Durante a cura o
personagem fica parado, e levar dano interrompe.

**Bancos.** Aperte W perto de um banco para sentar.
- A vida é restaurada, o banco vira o ponto de reaparecimento e o jogo é salvo.
- Os inimigos da sala voltam.
- No banco você equipa e desequipa amuletos.

**Moedas.** Os inimigos soltam moedas. Ao morrer, todas as moedas ficam numa bolsa no último
lugar seguro. Encoste nela para recuperar. Se morrer de novo antes disso, perde a bolsa.

**Loja (Vila).** Vende mapa, amuletos (Bússola, Ímã, Foco Rápido), um fragmento de vida e um
entalhe (+1 espaço de amuleto).

**Ferreiro (Vila).** Melhora a arma em 3 níveis. Cada nível dá +1 de dano no ataque rápido e
+2 no pesado. Os níveis 2 e 3 também exigem minério.

**Amuletos** (equipados no banco, cada um custa espaços; você começa com 3):

| Amuleto | Custo | Efeito | Onde |
|---|---|---|---|
| Lâmina Longa | 2 | golpes alcançam 30% mais longe | segredo nos Túneis |
| Força Bruta | 3 | +50% de dano | Câmara (Alturas) |
| Ímã | 1 | atrai moedas de longe | loja |
| Foco Rápido | 2 | cura 40% mais rápida | loja |
| Vigor | 2 | +1 de vida máxima | segredo no Ninho |
| Passo de Vento | 2 | dash mais longo e recarga menor | Mirante |
| Coletor | 1 | +50% de energia por acerto | Galeria |
| Bússola | 1 | mostra sua posição no mapa | loja |

**Fragmentos de vida.** Quatro fragmentos dão +1 de vida máxima. Há três no mapa e um na loja.

**Segredos.** Algumas paredes têm uma rachadura sutil. Ataque para quebrá-las.

**Mapa.** Com o mapa comprado, M ou Tab mostra as salas já visitadas, com bancos, loja e
ferreiro. A Bússola equipada mostra onde você está.

**Save.** O jogo salva em `saves/save.json` ao sentar no banco, pegar itens, comprar,
quebrar paredes, vencer o chefe e morrer. No menu, "Continuar" volta ao último banco.

## Inimigos

| Inimigo | Comportamento | Dica |
|---|---|---|
| Patrulheiro (laranja) | anda e vira em paredes e bordas | — |
| Perseguidor (roxo) | dá um pulinho com "!" e corre atrás de você no mesmo andar | — |
| Torreta (verde-oliva) | pisca e atira | golpes destroem os projéteis |
| Voador (verde) | flutua; ao ver você, avisa e persegue pelo ar | — |
| Saltador (amarelo) | agacha (aviso) e salta na sua direção | — |
| Escudeiro (azul) | o escudo frontal bloqueia o ataque rápido e empurra você | o **pesado** quebra a guarda; pelas costas o rápido funciona |
| **Guardião** (chefe) | investida, salto com ondas de choque e cuspe em leque | — |

O Guardião acorda quando você se aproxima, e o portão fecha atrás de você.
- Na **investida**, ele corre até bater na parede e fica tonto: é a hora de punir.
- No **salto**, cai soltando ondas de choque no chão.
- No **cuspe**, solta projéteis em leque.

Abaixo de 50% de vida ele fica mais rápido e agressivo.

## Mapa (13 salas)

```
                [Câmara]──[Picos]──[Mirante]               [Santuário 2]
                             │ (pulo duplo)                  (Pulo duplo)
[Santuário]─[Arena]─[Galeria]─[Túneis]   │                       │
  (Dash)   (Guardião) (banco)     │       │                       │
                      [Entrada]──[  Vila  ]──(dash)──[Descida]─[Jardim]─[Ninho]
                                 banco/loja/ferreiro            (banco)
```
Túneis e Picos ficam acima da Vila (poços à esquerda e à direita); o Santuário 2 fica acima do Ninho.

As salas ficam em `src/rooms.py`, desenhadas com um pequeno construtor (`Grid`). As portas
são dígitos na borda da sala, e `ROOM_LINKS` liga as portas entre si. A posição de cada sala
no mapa-múndi é calculada automaticamente a partir das ligações.

## Estrutura do código

```
main.py            janela, loop principal, troca de estados
src/config.py     TODOS os parâmetros de balanceamento
src/input.py      ações remapeáveis
src/physics.py    colisão por eixos com sub-passos (anti-túnel)
src/player.py     movimento, pulo, dash, golpes, energia, cura, atributos por amuleto
src/combat.py     golpes, acertos, defesa do escudo, paredes quebráveis, projéteis
src/enemies.py    patrulheiro, perseguidor, torreta, voador, saltador, escudeiro, Guardião
src/world.py      salas, tiles, portas, layout do mapa-múndi
src/rooms.py      dados das 13 salas e ligações
src/objects.py    moedas, itens, banco, loja/ferreiro, bolsa perdida
src/progress.py   inventário, amuletos, loja, save/load em JSON
src/camera.py     câmera suave
src/effects.py    partículas, tremor, hitstop
src/ui.py         HUD, inventário, mapa
src/menus.py      menu, novo jogo, introdução, como jogar, recordes, créditos
src/records.py    recordes em JSON
src/states.py     partida, pausa, mapa, banco, loja, mensagem, morte
tests/             testes automatizados
```

## Movimento e combate (inalterados — aprovados)

- Física em passo fixo de 120 Hz, igual em qualquer FPS.
- Pulo variável (cerca de 4 tiles), coyote time de 100 ms, jump buffer de 130 ms e pulo duplo
  de cerca de 3 tiles.
- Dash: cerca de 175 px, recarga de 0,45 s, um por pulo no ar, invulnerável durante o dash.
- Ataque rápido: 40/90/130 ms. Ataque pesado: 240/120/300 ms, com mais alcance, empurrão e
  atordoamento.
- Regras: um golpe por vez, cliques ficam guardados por 160 ms e o dash cancela a preparação
  ou a recuperação de um golpe.

O dano base foi dobrado (rápido 2, pesado 5) para abrir espaço para os upgrades do ferreiro.
A vida dos inimigos subiu na mesma proporção, então o número de golpes para derrotar cada um
continua o mesmo.

## O que os testes cobrem

`tests/run_tests.py` roda mais de 200 verificações:
- **Mecânica**: movimento, pulo, coyote, buffer, colisões, dash, pulo duplo, combate, dano,
  inimigos e FPS. Roda em salas-laboratório fixas.
- **Mundo**: cada porta leva à sala certa e o jogador se firma do outro lado. Uma busca
  automática prova que todo salto obrigatório é alcançável com as habilidades daquele ponto
  do jogo e que os bloqueios funcionam sem elas.
- **Progressão**: itens, habilidades, moedas, bolsa na morte, energia e cura, banco, amuletos,
  loja, ferreiro, parede secreta, escudeiro, voador, saltador e cada ataque do chefe. Também
  vitória sobre o chefe, save corrompido, Continuar, mapa, pausa e desenho de todas as telas.

A sensação de controle e a dificuldade do chefe precisam de teste com as mãos.
