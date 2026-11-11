---
name: Catálogo de Filmes
description: Catálogo pessoal de filmes em azul-tinta, com um único laranja de cátodo como luz.
colors:
  fundo: "#070a12"
  fundo-fundo: "#04060c"
  malha: "rgba(200, 160, 106, 0.3)"
  fantasma: "rgba(226, 214, 196, 0.42)"
  fantasma-fraco: "rgba(226, 214, 196, 0.3)"
  golpe: "#ff7a1c"
  golpe-claro: "#ffa257"
  osso: "#efe7da"
  osso-fraco: "rgba(239, 231, 218, 0.62)"
  recusa: "rgba(239, 231, 218, 0.22)"
  sinal: "#ff5a3c"
typography:
  display:
    fontFamily: "'Saira Condensed', 'Barlow Condensed', sans-serif"
    fontSize: "clamp(2rem, 6.4vw, 5.4rem)"
    fontWeight: 900
    lineHeight: 1.02
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "'Saira Condensed', sans-serif"
    fontSize: "clamp(1.5rem, 2.4vw, 2.05rem)"
    fontWeight: 900
    lineHeight: 1.02
    letterSpacing: "-0.02em"
  title:
    fontFamily: "'Saira Condensed', sans-serif"
    fontSize: "1.35rem"
    fontWeight: 700
    lineHeight: 1.02
    letterSpacing: "-0.015em"
  body:
    fontFamily: "'Barlow', system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "'Barlow Condensed', sans-serif"
    fontSize: "0.78rem"
    fontWeight: 600
    letterSpacing: "0.22em"
rounded:
  none: "0"
spacing:
  gutter: "clamp(20px, 5vw, 72px)"
  secao: "clamp(48px, 6vw, 76px)"
  grupo: "clamp(28px, 4vw, 56px)"
  campo: "30px"
  acoes: "22px"
components:
  acao:
    textColor: "{colors.osso-fraco}"
    typography: "{typography.label}"
    padding: "6px 0"
  acao-hover:
    textColor: "{colors.golpe}"
  acao-forte:
    textColor: "{colors.golpe}"
    typography: "{typography.label}"
    padding: "6px 0"
  acao-recusa-hover:
    textColor: "{colors.sinal}"
  campo:
    textColor: "{colors.osso}"
    typography: "{typography.body}"
    rounded: "{rounded.none}"
    padding: "10px 0"
  nav-secao-ativa:
    textColor: "{colors.golpe}"
    typography: "{typography.label}"
  capa:
    backgroundColor: "{colors.fundo-fundo}"
    textColor: "{colors.osso}"
    rounded: "{rounded.none}"
---

# Design System: Catálogo de Filmes

## Overview

**Creative North Star: "Cátodo Velado"**

Todo valor possível está na tela ao mesmo tempo, apagado, como um fantasma atrás de uma tela de bronze. O valor em vigor é **golpeado à frente**, aceso em laranja. Nada aparece por transição suave: o novo golpeia e o antigo decai. A página é um painel de instrumentos às escuras com uma única fonte de luz.

A densidade é de produto operacional: o painel mostra as quatro contagens, o filme de maior média e duas faixas de programação. As listagens são grades sem moldura. Toda a ousadia mora na tipografia condensada monumental, na luz de cátodo e no movimento. O código de layout fica simples.

O mundo recusa a grade de cards em caixa que todo catálogo de filmes entrega. Não há borda de contorno, card nem divisória horizontal. O agrupamento vem de espaço, profundidade e luz.

**Key Characteristics:**
- Duas cores, quatro papéis: azul-tinta de fundo, laranja de cátodo como única luz, osso para prosa e fantasma para o que está apagado.
- Sem caixa, régua ou divisória: o agrupamento vem de densidade, profundidade e espaço.
- Saira Condensed 900 em caixa alta, golpeada contra Barlow em osso.
- Um relógio só: `--beat` 220ms e uma curva de saída.
- Os estados são lidos pela luz: em vigor, disponível, apagado, recusado e condenado.

## Colors

Um chão azul-tinta quase preto e uma única luz laranja. O resto é osso em opacidades diferentes.

### Primary
- **Cátodo Aceso** (`golpe`): o valor em vigor. Item ativo da navegação, numerais do painel, médias, ação primária, foco, seleção de texto, cursor e barra de rolagem. Quase sempre vem com halo.
- **Cátodo Morno** (`golpe-claro`): atributos e vínculos (nacionalidade, "Gênero → Drama"). É a luz antes de ser golpeada.

### Neutral
- **Azul-Tinta** (`fundo`): o chão de toda página.
- **Trilho de Rolagem** (`fundo-fundo`): trilho das barras de rolagem, fundo das capas e opções de `select`.
- **Tecido de Bronze** (`malha`): a trama das capas e o véu das linhas pares do relatório.
- **Valor Apagado** (`fantasma`): linha de base dos campos e contorno dos numerais fantasmas.
- **Contorno das Irmãs** (`fantasma-fraco`): trilhos vazios dos instrumentos.
- **Osso** (`osso`): títulos e valores de campo.
- **Osso Velado** (`osso-fraco`): prosa secundária, rótulos e ações em repouso.
- **Recusado** (`recusa`): o que está desligado. Placeholder, "Sair", estrela vazia e separadores "·".

### Named Rules
**A Regra da Terceira Cor.** Duas cores, quatro papéis, sem terceira cor. `sinal` (#ff5a3c) aparece só em erro de formulário e em exclusão: não é cor do sistema, é sinal.

**A Regra do Bloqueio Escuro.** O bloqueio do PROTECT fica escuro e explica o motivo, sem nunca ficar vermelho, porque não é falha de quem tentou.

As matizes das capas variam por gênero, mas ficam presas à faixa quente do cátodo (do âmbar ao vermelho). Dois gêneros se distinguem sem que a capa saia das duas cores do sistema.

## Typography

**Display Font:** Saira Condensed (com fallback Barlow Condensed)
**Body Font:** Barlow (com fallback system-ui)
**Label Font:** Barlow Condensed

**Character:** a letra condensada e pesada faz o papel de luz de marquise. A Barlow em osso faz a leitura calma por baixo dela.

### Hierarchy
- **Display** (900, `clamp(2rem, 6.4vw, 5.4rem)`, 1.02): título de página, título do filme e herói do painel. Sempre em caixa alta.
- **Headline** (900, `clamp(1.5rem, 2.4vw, 2.05rem)`, 1.02): nome do registro nas listagens.
- **Title** (700, 1–1.35rem, 1.02): nome do filme nas faixas e na grade, autor da avaliação.
- **Body** (400, 16px, 1.6): sinopses e comentários, limitados a 68ch.
- **Label** (600, 0.78rem, `letter-spacing: 0.22em`, caixa alta): rótulos, navegação, ações e cabeçalhos de tabela. O texto é o controle.

### Named Rules
**A Regra do Til.** Todo título monumental com acento usa `line-height` ≥ 1.02 e `padding-top: .06em`. Sem isso o til do "Ã" encosta no limite da linha.

**A Regra Sem Sobretítulo.** Nenhum rótulo pequeno fica acima de um título. O título fala sozinho. O contexto vem depois dele, nos vínculos ("Gênero · Drama") ou na linha da nota ("de 5 · maior média do catálogo").

Os numerais usam `font-variant-numeric: tabular-nums`.

## Layout

O gutter lateral é `clamp(20px, 5vw, 72px)`. Telas de formulário, login e exclusão usam a coluna estreita (`main.estreito`, máximo de 660px), e o resto ocupa a largura toda.

- **Listagens de registro:** grade `auto-fill` com mínimo `min(100%, 290px)`.
- **Grade de capas:** `auto-fill` com mínimo de 190px (140px no celular).
- **Faixas:** rolagem horizontal com `scroll-snap`. A largura mora no `li` (`clamp(210px, 22vw, 268px)`, ou `.compacta` com `clamp(150px, 16vw, 190px)`), então toda capa da faixa tem o mesmo tamanho. A `mask-image` desvanece o último item em vez de cortá-lo.
- **Seções:** `clamp(48px, 6vw, 76px)` acima do título de seção e 20px abaixo. Uma seção com ação usa `.cabeca-secao`, com título e ação na mesma linha de base.
- **Respiros nomeados:** `.acoes-final` (38px antes do envio do formulário), `.acoes-pos` (28px depois de um bloco de conteúdo) e `.meta-fraca`. Não há `style=""` para espaçamento nos templates.

Abaixo de 720px: a navegação quebra em duas linhas, o herói e o detalhe empilham, os instrumentos ficam em 2×2 e a tabela de consultas vira um bloco por filme, com o título em cima e pares rótulo/valor em duas colunas.

## Elevation & Depth

Não existe sombra estrutural. A profundidade vem de **luz**: halos laranja (`text-shadow` e `drop-shadow` com deslocamento zero) marcam o que está em vigor, e o campo de luz do herói se dissolve no fundo sem desenhar borda.

O fundo (`.gauze`) é `position: fixed`, um chão limpo sem trama, com duas manchas radiais: o cátodo no alto à direita e um eco de bronze embaixo à esquerda. A trama de bronze fica só nas capas.

### Shadow Vocabulary
- **Halo de vigor** (`0 0 16px rgba(255,122,28,.55)`): navegação ativa, ação em hover e marca.
- **Halo de numeral** (`drop-shadow(0 0 16px rgba(255,122,28,.55))`, ou 30px/.95 em hover): números do painel e médias.
- **Brilho de base** (`0 1px 18px -6px rgba(255,122,28,.8)`): linha do campo em foco.

### Named Rules
**A Regra Sem Caixa.** Não existe `border` de contorno, card nem separador horizontal. Se uma luz ou um fundo ficar cortado em retângulo visível, isso é defeito: o herói não usa `overflow: hidden`, e quem corta o excesso lateral é o `main` (`overflow-x: clip`).

## Shapes

Ângulo reto em tudo (`border-radius: 0`). A única silhueta recorrente é a **capa 2:3**: um campo de cor diagonal na matiz do gênero, a trama de bronze por cima e o título condensado na base. Quando há `capa_url`, a foto cobre a capa desenhada. O contorno só existe como **traço de 1px**: base de campo, fio vertical do bloco recusado, trilho dos instrumentos e sublinhado de ação.

## Components

### Ações (botões)
- **Forma:** sem caixa. O texto em rótulo condensado é o controle, com `padding: 6px 0`.
- **Padrão:** osso velado. Em hover e foco, golpeia em laranja com halo e o sublinhado de 1px abre de `scaleX(0)`.
- **Forte:** já aceso em repouso, com sublinhado a 45%. Uma por tela: a ação primária (Novo, Salvar, Avaliar).
- **Recusa:** apagada em repouso, acende em `sinal` só sob o ponteiro (Excluir, Remover).

### Campos
- **Estilo:** sem caixa, só a linha de base em `fantasma`, com fundo transparente e ângulo reto.
- **Foco:** a base golpeia em laranja com brilho por baixo. O cursor de texto também é laranja.
- **Erro:** a base fica em `sinal` e a mensagem aparece em rótulo condensado logo abaixo, dentro de `#<id>_error`, o mesmo id que o Django coloca no `aria-describedby`.
- **Select:** seta desenhada com dois gradientes em laranja, sem ícone.

### Navegação
- Rótulos condensados em osso a 72%. A seção em vigor golpeia em laranja com halo. "Sair" é um `<button>` POST vestido de link, recusado em repouso e `sinal` em hover.

### Registro (item de listagem)
- Mosaico de até três capas em leque, que se abre em hover só com `transform`. Abaixo vêm o nome em headline, os atributos em cátodo morno, a contagem e as ações. Não tem borda nem fundo.

### Bloqueio explicado
- Fio vertical de 1px em gradiente laranja→transparente à esquerda, com rótulo "Por que está bloqueado", o motivo em prosa, como liberar e a ação forte que leva até os registros que bloqueiam. A ordem da tela é: título → registro → motivo → saída.

### Estados vazios
- `_vazio.html`: frase em rótulo recusado seguida de uma ação secundária que tira a tela do vazio ("Cadastrar o primeiro filme", "Limpar filtros"). Ocupa a linha inteira da grade. A ação nunca é forte, porque a ação primária da tela já está no cabeçalho.

### Painel (assinatura)
- Um herói com o filme de maior média e um campo de luz na matiz do gênero que respira (9s) e é varrido uma vez na chegada. Em seguida, quatro **instrumentos**: numeral que conta de 0 até o valor em CSS puro (`@property --contagem`), com um trilho que preenche junto.
- **Contagem zero fica apagada:** o numeral vira contorno `fantasma`, sem luz, e o trilho fica vazio. É o estado "apagado" do sistema aplicado a dados.
- **Estreia (conta sem filmes):** no lugar do herói, um título display "Seu catálogo começa aqui", o que já está disponível (gêneros e diretores compartilhados, em cátodo morno) e a ação forte "Cadastrar o primeiro filme". As faixas e os indicadores só aparecem quando há filmes.
- **Últimas avaliações:** capa de 76px ao lado de nome, estrelas, trecho do comentário em itálico e autor em rótulo recusado.

### Capa com foto
- A `<img class="capa-foto">` cobre a capa autoral e não tem fundo próprio: enquanto carrega, ou se falhar, a capa desenhada aparece por baixo.

### Início (vitrine)
Página de entrada no padrão de streaming: uma parede de cartazes inclinada em quatro fileiras que correm em sentidos alternados, coberta por um véu escuro com a luz de cátodo subindo de baixo. Na frente, só três coisas: a frase "Seus filmes. Suas notas.", uma linha de apoio e a ação. Os cartazes vêm apenas da conta de demonstração, em miniatura de 330px. É a única tela com botão cheio (`.botao-cheio`, fundo golpe); o resto do sistema segue a regra das ações sem caixa.

### Entrar e Criar conta
A mesma parede de cartazes, mais apagada (opacidade 0.32), sem a barra de carregamento. Na frente, um painel escuro translúcido de até 440px com título, campos, `.botao-cheio.botao-largo` e uma linha para trocar de tela. É a única caixa do sistema, aceita porque a tela de acesso segue o padrão de streaming.

## Motion

Um relógio só: `--beat: 220ms` e `--saida: cubic-bezier(.16,1,.3,1)`.

- **golpear:** desfoque → nítido em 2 beats. Média do filme.
- **erguer:** 14px + opacidade, 420ms, escalonado em ~55ms com teto de 330ms. Listas, faixas e grade.
- **contar / preencher:** 1100ms. Instrumentos do painel.
- **Transição entre páginas:** a capa viaja da grade até o detalhe (420ms) e a página cede em 90ms. A transição é pulada no envio de formulário.
- `prefers-reduced-motion` zera durações, desliga a transição entre páginas, a respiração, a varredura e a rolagem suave.

## Do's and Don'ts

### Do:
- **Do** golpeie o valor em vigor em `golpe` com halo e deixe os demais em `osso-fraco` ou contorno `fantasma`.
- **Do** use o texto como controle: ações em Barlow Condensed 600 caixa alta, com sublinhado abrindo de `scaleX(0)`.
- **Do** ponha a largura das faixas no `li`, para que toda capa da faixa tenha o mesmo tamanho.
- **Do** tematize seleção, cursor, barras de rolagem e anel de foco em `golpe`.
- **Do** escreva bloqueios com o motivo, como liberar e um link para resolver. Use plural de verdade ("1 filme" / "4 filmes"), nunca "filme(s)".

### Don't:
- **Don't** introduza uma terceira cor de sistema.
- **Don't** desenhe caixas, cards com borda ou divisórias horizontais, nem deixe uma luz ser cortada em retângulo.
- **Don't** trate o bloqueio do PROTECT como erro vermelho.
- **Don't** ponha rótulo pequeno acima de título.
- **Don't** anime `margin`, `width` ou `height`: o movimento é só `transform`, `opacity`, `filter` e máscara.
- **Don't** deixe o azul padrão de link vazar: `a { color: inherit }`.
- **Don't** escreva espaçamento em `style=""` no template. Use as classes de respiro.
