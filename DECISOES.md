# Decisões de projeto

Registro das decisões tomadas antes da implementação da 2ª etapa do trabalho.

**Contexto:** dar continuidade ao CRUD apresentado no bimestre passado, passando de 1 model para 4 tabelas no banco, com pelo menos uma cardinalidade 1:N.

---

## 1. Escopo: CRUD completo nos 4 models

Cada um dos 4 models tem suas quatro telas — criar, listar, editar e excluir.

**Por quê:** o enunciado pede "CRUD com 4 models". Ter 4 tabelas mas telas para apenas uma pode ser lido como requisito não cumprido. Como a nota do trabalho pode substituir a da prova, o custo de interpretar para menos é alto.

**Descartado:** CRUD apenas em Filme, com os outros 3 vivendo só no admin.

## 2. Schema: Genero, Filme, Diretor, Avaliação

O bimestre passado já tinha **dois** models (`Genero` e `Filme`), não um. Faltavam dois, não três.

**Por quê:** `Diretor` e `Avaliação` cabem no domínio sem inventar entidade artificial, e dão 1:N em sentidos opostos.

**Descartado:** `Ator` com ManyToMany — o Django cria uma 5ª tabela de junção por baixo, o que bagunçaria a contagem de "4 tabelas". `Estúdio` — ficaria quase idêntico a `Diretor`, com duas telas repetitivas.

## 3. Cardinalidades

| Relação | Tipo |
|---|---|
| Genero → Filme | 1:N (já existia) |
| Diretor → Filme | 1:N (nova) |
| Filme → Avaliação | 1:N (nova) |

**Por quê:** três relações 1:N em vez do mínimo de uma. `Diretor → Filme` coloca o model novo do lado "1"; `Filme → Avaliação` coloca o Filme do lado "1". Os dois sentidos ficam demonstrados.

## 4. on_delete: PROTECT no Diretor, CASCADE na Avaliação

- Excluir um **Diretor** com filmes é **bloqueado** (`PROTECT`), igual ao `Genero` que já era assim.
- Excluir um **Filme** apaga junto as **avaliações** dele (`CASCADE`).

**Por quê:** a diferença é proposital. Um diretor existe independentemente dos filmes, então não pode sumir e deixar registros órfãos. Uma avaliação só existe em função do filme — sem o filme, ela não significa nada. É a resposta pronta caso o professor pergunte por que o comportamento difere.

**Descartado:** CASCADE nos dois — um clique errado na demo apagaria meio banco. PROTECT nos dois — obrigaria apagar avaliação por avaliação antes de excluir um filme.

## 5. Model Diretor: nome + nacionalidade

**Por quê:** dois campos dão conteúdo ao card sem inventar complexidade, e `nacionalidade` rende um badge visual como o do gênero.

**Descartado:** incluir data de nascimento — mais um campo para preencher em toda demonstração.

## 6. Model Avaliação: nota 1–5, comentário, autor, criado_em

`nota` é `IntegerField` com validators de 1 a 5, renderizada como estrelas. `autor` é texto livre, sem login nem `User` do Django.

**Por quê:** escala de 1 a 5 é a mais visual e permite exibir média por filme. Autor como texto livre mantém o projeto simples e permite avatar com a inicial, como já fazem os cards de filme.

## 7. App renomeado de `filme` para `catalogo`

**Por quê:** o app passa a conter quatro models, então `filme` ficou mais estreito que o conteúdo.

**Por que é seguro:** renomear app Django normalmente dá problema com migrations, mas aqui `db.sqlite3` está no `.gitignore` e o seed recria os dados. As migrations podem ser apagadas e geradas de novo.

## 8. Views como função

As 16 views (4 models × 4 operações) continuam sendo funções.

**Por quê:** mantém o estilo já apresentado no bimestre passado e permite explicar cada view na arguição. Class-based views reduziriam para ~40 linhas, mas a lógica ficaria implícita no framework — arriscado se a turma não viu CBV em aula.

## 9. Django Forms (ModelForm)

Substitui o `request.POST['campo']` direto usado antes.

**Por quê:** o código atual quebra com `MultiValueDictKeyError` se um campo faltar, e não valida nada. Com 4 models isso seria 4× a chance de erro na apresentação. `ModelForm` valida, repopula o formulário com erro e corta boilerplate.

**Nota:** não usar Django Forms foi escolha do grupo no bimestre passado, não exigência do professor.

## 10. Templates: base.html + CSS em arquivo estático

Um `base.html` com layout e navegação; o CSS em `catalogo/static/catalogo/style.css`.

**Por quê:** o CSS estava duplicado inline nos 3 templates (~6 KB cada). Com 4 models seriam ~13 templates, ou seja, 13 cópias do mesmo CSS para manter em sincronia. `django.contrib.staticfiles` e `STATIC_URL` já estavam configurados.

## 11. Design pela skill `impeccable`

Direção criativa e futurista, aplicada depois que as telas existirem.

**Por quê:** desenhar antes dos models existirem seria desenhar tela vazia. O `base.html` + CSS único é a base sobre a qual o design atua de forma coerente nas 13 telas.

## 12. Dashboard na raiz

A rota `/` passa a ser uma dashboard com:

- contagem das 4 tabelas
- últimos filmes cadastrados
- últimas avaliações
- filme mais bem avaliado (média de estrelas)

**Por quê:** hoje `/` devolve **404** — só existem `admin/` e `filme/`. Além de corrigir isso, a dashboard comunica os 4 models de imediato e mostra as relações 1:N funcionando sem precisar navegar.

**Descartado:** gráficos. O pedido foi explicitamente "simples".

## 13. Seed com diretores e avaliações

O seed passa a criar diretores para os 5 filmes existentes e 2–3 avaliações por filme.

**Por quê:** `Diretor` é obrigatório, então os filmes existentes precisam de um. E a demonstração é ao vivo — nenhuma tela pode abrir vazia, ou a média de estrelas não aparece.

## 14. Artefato de apresentação: slides

Construído **depois** do código, não durante.

**Por quê:** é o formato esperado numa apresentação de sala e projeta bem. Cobre contexto, diagrama dos models, relações, decisões e demonstração.

## 15. Material a coletar durante a implementação

- diagrama do banco com as 4 tabelas e as setas 1:N
- comparativo antes/depois (1 CRUD com 2 models → 4 CRUDs com 4 models)

**Fora de escopo:** capturas de tela. A demonstração será ao vivo, e é por isso que o seed populado da decisão 13 importa.

---

## Ajustes menores decididos por padrão

- URLs no plural: `/filmes/`, `/diretores/`, `/generos/`, `/avaliacoes/`
- `TIME_ZONE` de `UTC` para `America/Sao_Paulo` — necessário para o `criado_em` das avaliações não aparecer 3 horas adiantado
- `Genero` ganha telas próprias de CRUD, que não tinha
- `admin.py` registra os 4 models
- README reescrito com o novo modelo de dados

---

## Pendência

O **enunciado oficial no Teams ainda não foi conferido**. Estas decisões partiram do recado repassado pelo grupo. Requisitos como autenticação, upload de imagem ou deploy mudariam parte do plano.

---

# Segunda rodada — telas de detalhe e capas

## 16. Sem réplica da Netflix

O pedido inicial era replicar o front-end da Netflix por completo. **Recusado**, por dois motivos: entregar como trabalho próprio a identidade visual de uma empresa é problema de integridade acadêmica, ainda mais quando a nota pode substituir a da prova; e o visual da Netflix é ativo protegido dela.

**O que foi adotado no lugar:** as *convenções* de catálogo de streaming, que são vocabulário de categoria e não propriedade de ninguém — fileiras por categoria, grade de capas, página de detalhe ao clicar.

## 17. Claude for Chrome indisponível

A skill aparece listada, mas as ferramentas `mcp__claude-in-chrome__*` não existem nesta sessão. Não houve análise do site da Netflix por navegação automatizada.

## 18. Telas de detalhe para Filme, Diretor e Gênero

As três entidades do lado "1" de alguma relação ganham página própria.

**Por quê:** cada página vira prova visual de um 1:N — o filme mostra suas avaliações, o diretor mostra seus filmes, o gênero mostra os dele. O código é quase idêntico nas três, então a simetria custa pouco e evita a impressão de trabalho pela metade.

**Descartado:** detalhe só para filme — clicar no nome do diretor cairia em beco sem saída.

## 19. Clicar abre o detalhe

Antes, clicar num filme levava ao formulário de edição. Agora abre a página dele; **editar e excluir viram ações** dentro da página e da listagem.

**Por quê:** é o que o avaliador espera ao explorar sozinho. Clicar num card de catálogo e cair num formulário surpreende.

## 20. A malha sai do fundo e permanece nas letras

O fundo volta a ser chão limpo. A malha continua **recortada dentro** dos títulos e numerais, que é a assinatura do mundo.

**Por quê:** o usuário achou o fundo pixelado demais. Remover a malha por completo abandonaria o Cátodo Velado e sobraria escuro com laranja, sem direção — exatamente o padrão que o piso de qualidade manda evitar.

## 21. Pôsteres tipográficos autorais

Cada filme ganha uma capa desenhada em SVG/CSS: o título na fonte condensada sobre campo de cor derivado do gênero, com a malha.

**Por quê:** não há geração de imagem nesta máquina, e usar os pôsteres reais desses filmes repetiria o problema de propriedade. As capas autorais não dependem de nada externo, combinam com o mundo e funcionam offline.

**Descartado:** fotos de banco gratuito — exigem internet na demonstração, e uma foto genérica colada num filme real confunde.

## 22. Listagem de filmes vira grade de capas

**Por quê:** é a convenção de streaming que o usuário pediu, e dá às capas a escala necessária para serem lidas.

## 23. Avaliação não fica embutida na página do filme

A página lista as avaliações e leva ao formulário por link.

**Por quê:** decisão do usuário. O formulário embutido tornaria a demonstração mais fluida (avaliar e ver a média mudar na hora), mas foi recusado em favor de menos código.

---

# Versão final — requisitos mínimos do projeto

Contexto: o comunicado da disciplina fixou os requisitos mínimos (apps separados, área pública e restrita, isolamento por usuário, CSRF, 5 models com 1:N, 1:1 e N:N through, 2 CRUDs, dashboard, consultas com relatório e 3 testes).

## 24. App `usuarios` separado do `catalogo`

Login, cadastro e perfil ficam num app próprio; o `catalogo` fica só com as entidades de negócio.

**Por quê:** é a separação por domínio pedida no comunicado. O nome `core` já é o pacote de configuração do projeto, então o app de autenticação se chama `usuarios`.

**Descartado:** colocar o login dentro do `catalogo`.

## 25. Perfil como a relação 1:1

`Perfil` tem `OneToOneField` para o `User` do Django, com apelido, bio e gênero favorito. Um signal cria o perfil de todo usuário novo.

**Por quê:** é o uso clássico do 1:1 — estender o usuário sem trocar o model de autenticação. O signal garante o perfil também para quem é criado pelo `createsuperuser`.

**Descartado:** `AbstractUser` customizado; exigiria recomeçar as migrations de auth no meio do projeto.

## 26. Dono em Filme e Avaliação; Gênero, Diretor e Ator compartilhados

Filme e Avaliação têm o campo `usuario`. Elenco herda a posse do filme. Gênero, Diretor e Ator não têm dono.

**Por quê:** o catálogo pessoal é o que pertence ao usuário. "Drama" ou "Christopher Nolan" são dados de referência; duplicá-los por usuário criaria dez "Drama" diferentes no banco. Mesmo nessas telas, os filmes listados passam pelo filtro do usuário.

**Descartado:** dono em todas as tabelas — mais isolamento, mas a mesma pessoa teria de recadastrar diretores e atores que já existem.

## 27. Seed atribuído a uma conta `demo`

A migration 0004 cria o usuário `demo` (senha `filmes123`) e passa para ele os filmes e avaliações das migrations 0002 e 0003, antes de o campo `usuario` ficar obrigatório.

**Por quê:** o seed já existia sem dono. Sem essa conta, quem roda `migrate` teria um banco com dados que ninguém consegue ver.

## 28. N:N Filme ↔ Ator através de `Elenco`

`Elenco` guarda o personagem e a ordem nos créditos, com `UniqueConstraint` em (filme, ator). O elenco é editado a partir da página do filme.

**Por quê:** o personagem é um dado da ligação, não do filme nem do ator — exatamente o caso que justifica um `through`. Como o filme não é campo do formulário, o `ElencoForm` confere a unicidade no `clean_ator`.

## 29. Home pública em `/`, painel em `/dashboard/`

**Por quê:** o comunicado exige uma Home navegável sem login, e o painel mostra dados do usuário, então precisa ser restrito.

## 30. Consultas por GET e relatório em CSV

Os filtros vão na query string; **Exportar CSV** reaproveita a mesma query com `formato=csv`.

**Por quê:** GET deixa a busca compartilhável e garante que o relatório exportado seja exatamente o que está na tela. O CSV sai com BOM e ponto e vírgula para abrir certo no Excel em português.

**Descartado:** PDF — exigiria uma biblioteca a mais (reportlab ou weasyprint) sem ganho para o requisito.

## 31. Capas reais por link, com a capa autoral como reserva (revê o item 21)

`Filme.capa_url` guarda só o endereço de uma imagem. Com link, a foto cobre a capa desenhada; sem link, ou se o link quebrar (`onerror`), a capa autoral continua aparecendo.

Para não ter de procurar imagem por imagem:
- o botão **Buscar capa automaticamente**, na página do filme, e o comando `python manage.py buscar_capas` consultam a Wikipédia (pt → artigo equivalente em inglês, onde os pôsteres ficam). Não precisa de chave nem de biblioteca extra;
- a busca só aceita a página se ela for de um filme e citar o diretor cadastrado, para não trazer o livro de mesmo nome;
- a migration 0008 já traz os links dos 20 filmes do seed, conferidos à mão (a busca errou Kill Bill e O Senhor dos Anéis, que pegaram a continuação).

**Por quê:** o usuário pediu fotos reais sem ter de baixar cada arquivo. O item 21 recusava pôsteres por depender de internet e por propriedade; a capa autoral como reserva resolve a demonstração offline, e o uso aqui é acadêmico, com as imagens servidas pela própria Wikimedia.

**Descartado:** upload de arquivo (`ImageField`) — exigiria baixar cada imagem e instalar o Pillow; API do TMDB — exige cadastro e chave.

**Limite conhecido:** a busca é por título, então em sequências pode trazer outro filme da série. O link pode ser corrigido em Editar.

## 32. Início no padrão de streaming

A página pública virou uma vitrine: uma parede de cartazes inclinada, em quatro fileiras que correm em sentidos opostos, e na frente só a frase "Seus filmes. Suas notas.", uma linha de apoio e o botão de começar. Na chegada, uma barra de carregamento corre no topo, as fileiras aparecem uma a uma e o título entra em foco. Entrar e Criar conta usam a mesma parede, mais apagada, com o formulário num painel central.

**Por quê:** o usuário pediu uma landing "tipo Netflix ou Prime Video" e menos informação na tela. A versão anterior tinha leque de gêneros, letreiro de diretores, passo a passo e fecho, o que era excesso para a primeira impressão.

**Cuidado com o isolamento:** os cartazes vêm só da conta `demo` (constante `CONTA_DA_VITRINE` em `views.py`), em miniatura de 330px da Wikimedia, três vezes mais leve que o original. Filmes de outras contas nunca aparecem para quem não entrou.

**Exceção visual:** o botão laranja cheio (`.botao-cheio`) e o painel das telas de acesso são as únicas caixas do sistema; o resto mantém as ações sem caixa (ver DESIGN.md).

## 33. Página do filme reorganizada

O topo usa a própria capa, ampliada e desfocada, como fundo. Na frente: gênero e direção, título, nota com estrela, sinopse, os botões Avaliar e Editar, e as ações menores (buscar capa, excluir) logo abaixo. Depois, avaliações e elenco lado a lado: a média grande com a distribuição das notas de 5 a 1, cada opinião com a inicial do autor, e o elenco numa coluna com nome e personagem. No fim, "Mais de [diretor]".

**Por quê:** antes as seções vinham empilhadas sem hierarquia, e as ações de editar e excluir tinham o mesmo peso de avaliar.

## 34. Onde assistir por busca, sem afirmar disponibilidade

Cada filme tem atalhos que abrem a busca do título no Netflix, Prime Video, Max, Globoplay e Apple TV, e o JustWatch, que mostra em qual serviço o filme está no Brasil.

**Por quê:** não existe API pública e gratuita de disponibilidade, e o catálogo dos serviços muda toda semana. Gravar "está na Netflix" no banco seria inventar um dado que envelhece.

**Descartado:** Disney+ — a busca não abre sem login (responde 404); o JustWatch cobre esse caso. API do TMDB (*watch providers*) — exige cadastro e chave.

## 35. Transição animada entre páginas desligada

O `@view-transition` (a capa "viajando" da lista para o detalhe) foi desligado.

**Por quê:** no Chromium a aba às vezes parava de renderizar depois de alguns cliques ou de enviar um formulário. Numa demonstração ao vivo, uma tela travada custa mais do que o efeito vale.

## 36. Pronto para apresentar com um comando

- `rodar.bat` cria o ambiente virtual, instala as dependências, aplica as migrations, roda os testes, abre o navegador e sobe o servidor.
- A migration 0009 cria o superusuário `admin` e a 0010 completa o seed: pelo menos 3 atores reais em cada filme da `demo`, perfil preenchido e a conta `ana` com 3 filmes próprios.
- A 0011 acrescenta 24 filmes à `demo` (de 20 para 44), com 17 diretores novos, o gênero Comédia, elenco de 3 atores e 2 ou 3 avaliações em cada. As capas vieram da API da Wikipédia, conferindo a página do filme certo: a busca automática tinha trazido a continuação em Gladiador, Alien e Jurassic Park.
- Todo seed usa `get_or_create`: rodar de novo, ou sobre um banco com dados, não duplica nem apaga nada. A 0010 não tem volta (`noop`), porque desfazê-la poderia apagar registros criados depois em cima dela.
- `ProntoParaApresentarTeste` confere que um banco criado só com `migrate` já tem as contas, o elenco e as páginas principais abrindo.

**Por quê:** a demonstração é ao vivo e o avaliador pode pedir qualquer tela. Nada pode abrir vazio, e preparar o ambiente não pode depender de lembrar comandos.

**Consequência:** com a conta `ana`, a lista de atores passou a filtrar quem só aparece em filmes de outras contas, para a `demo` não ver atores com "0 filmes".
