---
tipo: plano
capitulo: 1
status: aprovado (2026-10-22) — etapas 1 e 2 concluídas; próxima: etapa 3 (pistas + caderno)
criado: 2026-10-22
---

# Capítulo 1 — Jantar no molhado em veneno

Plano do primeiro capítulo do híbrido **metroidvania + investigação** no navio, seguindo o [[Roteiro A3 - Investigação no navio]] e usando o motor do [[Jogo A3]] (movimento, combate, salas, save).

## 1. Resumo do capítulo

Noite de tempestade. No jantar, a **capitã** desaba envenenada e morre. O protagonista é um passageiro, um enganador que se diz feiticeiro. Ele sabe ler pessoas, então a tripulação o encarrega de achar o culpado antes que o navio afunde na desconfiança (e na água).

- **4 suspeitos:** Cozinheira, Grumete, Imediato e Pirata meia-irmã da capitã.
- **Culpado:** o **Grumete**. O vilão descobriu que o garoto roubava pequenas coisas e que a capitã ia expulsá-lo no próximo porto. Ofereceu um "tônico" para acalmá-la e fazê-la perdoar. O grumete serviu o veneno achando que salvava o próprio lugar no navio.
- **Fim do capítulo:** o grumete confessa, desaba e revela que *"um homem de capuz"* lhe deu o tônico. É o gancho para o vilão e para o capítulo 2.
- **Pista falsa (do roteiro):** a meia-irmã herda o navio. Ela tem motivo, mentiu sobre isso, mas é inocente.

## 2. Ciclo de jogo

1. **Explorar o navio** (plataforma + combate leve) para achar as 4 pistas físicas.
2. **Conversar** com os suspeitos (W) para coletar **depoimentos**, que vão para o caderno.
3. **Correr contra a maré:** a água sobe com o tempo. Cada estágio custa algo (ver seção 5).
4. Quando quiser (ou quando a maré encher), ir ao **Salão** e **acusar** um suspeito.
5. **Interrogatório = o duelo:** quebrar a compostura do suspeito com as ações certas antes de perder a credibilidade.

## 3. Mapa do navio (8 salas)

```
                    [Cesto da gávea]  ← meia-irmã pirata
                           │ (subida pelo mastro)
[Tombadilho / leme]──[Convés principal]──[Proa + Cabine do protagonista]
   imediato                │                 banco (salvar) + baú de truques
        │                  │ escotilha
[Cabine da capitã]──[Salão de jantar]──[Cozinha]──[Alojamento]
  (lacrada até achar      cena do crime   cozinheira   grumete
   a chave)                                  │ alçapão
                                       [Porão / despensa]  ← alaga primeiro
```

- **Cabine do protagonista:** funciona como o **banco**. Salva o jogo, recompõe a credibilidade com energia e permite trocar amuletos. Ali está o **baú de truques** com a primeira habilidade.
- **Habilidade do capítulo:** **Passo ilusório**, o dash atual com outro visual (fumaça). É necessária para cruzar o trecho alagado do porão e chegar à pista 1.
- **Cesto da gávea:** subida vertical pelo mastro, só com pulos. Testa plataforma.
- **Cabine da capitã:** trancada. A **chave** está com a capitã no salão. Lá dentro fica a pista 4 (bilhete).
- **Personagem extra:** o **melhor amigo de infância** aparece na proa como passageiro simpático (ele é o vilão do capítulo 5). Ele dá uma "dica" que empurra o jogador para a meia-irmã. É foreshadowing e armadilha ao mesmo tempo.

## 4. Pistas e depoimentos

### 4 pistas físicas

| # | Pista | Onde | O que prova | Risco da maré |
|---|---|---|---|---|
| P1 | **Frasco de "tônico"** vazio, cheiro amargo, com um símbolo desenhado (marca do vilão) | Porão, atrás do trecho alagado (exige Passo ilusório) | O veneno veio de fora da cozinha | **Destruído na maré 2** se não for pego |
| P2 | **Prato da capitã** (só ele tem resíduo; a panela está limpa) | Salão de jantar | O veneno foi posto **depois** de servir. Inocenta a cozinheira | — |
| P3 | **Escala de serviço** marcando quem serviu a mesa da capitã naquela noite | Alojamento da tripulação | Foi o **grumete** quem levou o prato | **Roubada por um capanga na maré 3** |
| P4 | **Bilhete da capitã**: "No próximo porto, o grumete desembarca. Chega de sumiços." + saquinho de bugigangas roubadas | Cabine da capitã (precisa da chave) | **Motivo** do grumete | — |

### Depoimentos (W para conversar; ficam no caderno)

| Suspeito | Diz | Verdade |
|---|---|---|
| Cozinheira | "Tudo saiu da mesma panela. Todo mundo comeu o mesmo ensopado." | Verdade (P2 confirma) |
| Grumete | "Eu nem entrei no salão, estava lavando o convés." | **Mentira** (P3 contradiz) |
| Imediato | "Eu estava no leme. E vou dizer: quem ganha com isso é a irmã. O navio fica pra ela." | Verdade, mas planta a pista falsa (ele é o culpado do capítulo 2) |
| Meia-irmã | "Não ganho nada com a morte dela." | **Mentira sobre o motivo** (herda o navio), mas é inocente |
| Melhor amigo | "Vi a irmã discutindo com a capitã mais cedo..." | Verdade irrelevante; empurra para a pista falsa |

## 5. Maré (relógio do capítulo)

A água sobe visivelmente nas salas de baixo. No HUD aparece um medidor de maré com o tempo restante.

| Estágio | Tempo (normal) | Consequência |
|---|---|---|
| 0 | 0–4 min | Navio seco |
| 1 | 4 min | Porão com água pela cintura: movimento lento e ratos na água |
| 2 | 8 min | **Porão alagado: P1 é destruída** se não foi pega. Aparecem os primeiros capangas mascarados |
| 3 | 11 min | **Capanga rouba P3** do alojamento (dá para persegui-lo e recuperar). Credibilidade máxima −1 ("as pessoas deixam de confiar") |
| Cheia | 14 min | Interrogatório forçado com o que você tiver |

- **Água funda:** ficar com a cabeça submersa por mais de 3 s custa 1 de credibilidade e devolve o jogador ao último chão seguro.
- **Dificuldade** (escolhida no início):
  - **Fácil:** 20 min de maré e pistas brilham.
  - **Normal:** 14 min.
  - **Difícil:** 10 min, blefe mais arriscado e mais capangas.

## 6. Credibilidade (= vida)

Substitui os corações (5 no início).

| Perde credibilidade quando… | Quanto |
|---|---|
| Leva golpe de capanga ou rato | 1 |
| Apresenta a pista errada no interrogatório | 1 |
| Blefa com o suspeito calmo | 1 |
| Acusa a pessoa errada | 2 |
| Afoga | 1 |

- **Zerou:** "fracasso visível a todos". Game over do capítulo, recomeçando da cabine.
- **Recompor-se:** segurar F gasta **foco** (a energia atual) e devolve 1 de credibilidade. O foco enche ao acertar inimigos **e ao descobrir pistas e depoimentos novos**.

## 7. Interrogatório (o duelo)

Tela própria. Retrato do suspeito com a barra de **Compostura** (no lugar da vida do chefe) e a sua **Credibilidade**. Cada rodada tem uma fala do suspeito e uma **reação visível** ("desvia o olhar", "aperta as mãos", "sorri tranquilo"). Ler essa reação é a habilidade do protagonista.

| Ação | Efeito | Risco |
|---|---|---|
| **Ouvir** | Aceita e passa para a próxima fala | Nenhum (mas não avança a compostura) |
| **Pressionar** | Pede detalhes. Se a fala for fraca, revela informação nova | Se o suspeito já está **irritado**, ele se fecha e a rodada se perde |
| **Apresentar pista** | Mostra uma pista do caderno que contradiz a fala. Se acertar, derruba muito a compostura | Pista errada = −1 de credibilidade |
| **Blefar** | Finge ter uma prova que não tem | Funciona se o suspeito estiver **nervoso** (compostura baixa); se estiver calmo = −1 de credibilidade |

### Roteiro do duelo com o Grumete (acusação correta)

1. *"Eu estava lavando o convés!"* (desvia o olhar) → **Apresentar P3** (escala de serviço).
2. *"Tá… eu levei o prato. Mas qualquer um podia ter mexido!"* → **Pressionar**: *"…o prato ficou comigo o tempo todo."*
3. *"Por que eu faria isso? Ela gostava de mim!"* → **Apresentar P4** (bilhete de expulsão).
4. *"Eu não sei nada de veneno!"* → **Apresentar P1** (frasco). Se a maré destruiu P1, **Blefar** ("eu achei o frasco no porão") funciona, porque ele já está nervoso.
5. **Confissão:** desaba e conta do "homem de capuz" e do "tônico".

- **Meia-irmã (acusação errada):** ela resiste. P4 não a afeta. Apresentar a herança faz ela admitir o motivo, mas mostrar o álibi dela custa a acusação errada (−2). Depois disso o jogador pode acusar de novo, se tiver credibilidade.
- **Cozinheira e Imediato** têm roteiros curtos que terminam em acusação errada.

## 8. Combate no capítulo

Leve, para não brigar com a investigação:
- **Ratos** no porão (patrulheiros).
- **Capangas mascarados** do vilão a partir da maré 2 (perseguidores e saltadores com outro visual).
- **Gaivotas** no mastro (voadores).
- Sem chefe de combate: o "chefe" é o interrogatório.
- O ataque rápido vira **"faísca"** (truque de mão) e o pesado vira **"estouro de fumaça"**. A mecânica é a mesma que você já aprovou; muda só o visual.

## 9. Telas pedidas no documento

- **Menu:** Novo jogo, Continuar capítulo, Como jogar, Recordes, Créditos, Sair.
- **Escolha de protagonista** (ele/ela) e **dificuldade**.
- **Introdução:** 4–5 telas de texto (jantar, a capitã desaba, pedem ajuda ao "feiticeiro").
- **Como jogar:** tutorial só no capítulo 1, com dicas contextuais na primeira vez em que se pula, ataca, conversa, pega pista e abre o caderno.
- **Caderno (Tab):** pistas, depoimentos e suspeitos, com indicação de contradições já descobertas.
- **Fim do capítulo:** resumo e **nota (S/A/B/C)** por tempo, credibilidade restante e pistas achadas. Vai para **Recordes**.

## 10. Plano de implementação (ordem)

| Etapa | O quê | Reaproveita |
|---|---|---|
| 1 ✅ | Menu novo, escolha de protagonista e dificuldade, introdução, créditos, recordes (vazio) | Menus e save atuais |
| 2 ✅ | Navio: 9 salas, NPCs com diálogo (caixa de texto), chave da cabine | Salas, portas, banco, NPC da loja |
| 3 | Pistas + depoimentos + caderno (Tab) | Itens e mensagens atuais |
| 4 | Maré: água visível, medidor, estágios e eventos, afogamento | Espinhos e "último chão seguro" |
| 5 | Interrogatório: tela de duelo, roteiro do grumete e acusações erradas | Barra do chefe, menus |
| 6 | Credibilidade no lugar da vida, foco ganho por pistas, inimigos reskin | Vida e energia atuais |
| 7 | Fim de capítulo, nota, recordes, save por capítulo | Save atual |
| 8 | Testes automáticos: pistas alcançáveis, eventos da maré, duelo (vitória, derrota, blefe) | Bateria de testes atual |

O mundo de cavernas atual sai do jogo. Fica só como sala de testes do motor.

## 11. Decisões em aberto (confirmar com o grupo)

- [ ] Duração do capítulo no Normal: **14 min** está bom?
- [ ] Acusar errado permite tentar de novo (gastando credibilidade), ou é uma chance só?
- [ ] O protagonista "ele ou ela" muda só o visual e os pronomes, ou também algum diálogo?
- [ ] Nome do jogo (o documento ainda não define).
- [ ] O professor aceita o híbrido com plataforma e combate leve?

Voltar: [[Cérebro]] · [[Jogo A3]]
