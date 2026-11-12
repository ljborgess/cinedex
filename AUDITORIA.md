# Auditoria pelo padrão ProLobby

Revisão do Catálogo de Filmes contra o padrão de código do ProLobby: o [checklist de segurança de 18 itens](#checklist-de-segurança-item-a-item), as [regras que já pegaram bug](#regras-que-já-pegaram-bug) e o [fluxo de código](#fluxo-de-código-ci-e-pr). Feita em 2026-11-12, na branch `chore/padrao-prolobby`.

Cada achado tem o que foi visto, por que importa e o que foi feito. O que ficou de fora diz o motivo, em [Não corrigido de propósito](#não-corrigido-de-propósito).

## Resumo

| # | Achado | Gravidade | Situação |
|---|---|---|---|
| 1 | `SECRET_KEY` commitada no `settings.py` | alta | corrigido |
| 2 | `DEBUG = True` fixo: stack trace aparece para qualquer visitante | alta | corrigido |
| 3 | `sqlparse 0.5.5` com 5 vulnerabilidades conhecidas | alta | corrigido (0.6.0) |
| 4 | Login sem limite de tentativas: senha da `demo` testável por script | alta | corrigido |
| 5 | Cadastro sem limite: contas criadas em lote | média | corrigido |
| 6 | Sem HTTPS obrigatório, cookie seguro e HSTS em produção (7 alertas do `check --deploy`) | média | corrigido |
| 7 | Sem `Content-Security-Policy` | média | corrigido |
| 8 | Injeção de fórmula no CSV exportado | média | corrigido |
| 9 | Corrida entre contagem e `delete` gera página 500 (`ProtectedError`) | baixa | corrigido |
| 10 | Corrida no elenco duplicado gera página 500 (`IntegrityError`) | baixa | corrigido |
| 11 | `Filme.media_nota` sem uso e com N+1 embutido | baixa | removido |
| 12 | Sem CI: teste, migration e dependência só eram conferidos à mão | média | corrigido |
| 13 | Qualquer conta edita Gênero, Diretor e Ator compartilhados | média | aceito, ver abaixo |
| 14 | Migrations criam `admin` / `filmes123` em qualquer ambiente | alta fora da apresentação | aceito, ver abaixo |
| 15 | Código em português (o ProLobby pede inglês) | — | desvio consciente |

### Segunda rodada: telas, admin e o que sobrou

| # | Achado | Gravidade | Situação |
|---|---|---|---|
| 16 | Login do `/admin/` tem formulário próprio e escapava do limite de tentativas | alta | corrigido |
| 17 | Filtros da Consulta listavam atores, diretores e gêneros que só existem no catálogo de outra conta | média | corrigido |
| 18 | Vitrine pública mostrava qualquer link de capa da `demo`, cuja senha é pública | média | corrigido |
| 19 | Admin sem o visual do site, com rótulos sem acento ("Genero", "Titulo") | baixa | corrigido |
| 20 | Hash das senhas | — | conferido: `pbkdf2_sha256`, salt e 1.000.000 de iterações |
| 21 | IDs dos filmes na URL são sequenciais (`/filmes/1/`) | — | aceito, ver abaixo |

Testes: de 23 para 33, todos passando. `manage.py check --deploy` em modo produção: de 7 alertas para nenhum.

## Checklist de segurança, item a item

O checklist do ProLobby foi escrito para NestJS + Postgres. Aqui está traduzido para Django + SQLite.

| Item | O que pede | Como estava | Agora |
|---|---|---|---|
| 1 · Esconder API keys | chave só no servidor ou no ambiente | não há API paga; a Wikipédia não pede chave | OK |
| 2 · Secrets fora do git | nada de chave no repositório | `SECRET_KEY` no `settings.py` | vem de `DJANGO_SECRET_KEY`; sem ela e com `DJANGO_DEBUG=0` o servidor não sobe |
| 3 · Sem acesso direto ao banco | o navegador só fala com o servidor | SQLite local, só o Django acessa | OK |
| 4 · RLS | política por linha | N/A no SQLite; o isolamento é feito nas views (`filmes_do`, `avaliacoes_do`, `elenco_do`) | OK, já coberto por teste |
| 5 · Criptografia em repouso | dado sensível cifrado | o projeto não guarda dado sensível além da senha (hash) | N/A |
| 6 · Auth no servidor | permissão nunca vem do cliente | `@login_required` em toda view interna | OK |
| 7 · Restringir acessos | dono vs. terceiro | filme, avaliação e elenco isolados por dono | OK, menos o achado 13 |
| 8 · Mass assignment | só os campos do formulário | todo `ModelForm` lista `fields`; o dono vem da sessão | OK, já coberto por teste |
| 9 · Cookies | `HttpOnly`, `Secure`, `SameSite` | `HttpOnly` e `SameSite=Lax` são padrão do Django; faltava `Secure` | `Secure` em produção |
| 9b · GET sem efeito colateral | ação que muda estado é POST | excluir, buscar capa e sair já eram POST, e o Django tem token CSRF | OK |
| 10 · Hash de senha | bcrypt/argon2/PBKDF2 com salt | PBKDF2 do Django + 4 validadores de senha | OK |
| 11 · Rate limit | login por IP | nenhum | 5 erros por IP a cada 15 min ([`usuarios/limite.py`](usuarios/limite.py)) |
| 12 · Bot protection | cadastro protegido de automação | nenhum | 5 contas por IP a cada 15 min |
| 13 · Queries parametrizadas | nada de SQL concatenado | só ORM; a ordenação da consulta é lista fechada (`ChoiceField`) | OK |
| 14 · Validação de input | no servidor | `ModelForm` e `URLField` (aceita só http/https/ftp, nunca `javascript:`) | OK |
| 15 · Não vazar conteúdo | sem stack trace | `DEBUG=True` mostrava código e configuração | `DEBUG` desligável; mensagem de login bloqueado é igual exista a conta ou não |
| 16 · Uploads | tipo real e tamanho | não há upload: a capa é só um link | N/A |
| 17 · Trim de resposta | só os campos da tela | páginas renderizadas no servidor, sem API JSON | N/A |
| 18 · Security headers | CSP, nosniff, frame-ancestors, HSTS | `nosniff` e `X-Frame-Options` vinham do Django; faltavam CSP e HSTS | CSP em [`core/middleware.py`](core/middleware.py); HSTS em produção |

### Detalhes dos achados corrigidos

**1 e 2 · Chave e DEBUG.** A chave antiga continua no histórico do git e por isso não vale mais como segredo: agora serve só para desenvolvimento. Sem variável nenhuma o projeto roda exatamente como antes (`rodar.bat` não muda). Para produção:

```bash
DJANGO_DEBUG=0
DJANGO_SECRET_KEY=<gerar com: python -c "import secrets; print(secrets.token_urlsafe(50))">
DJANGO_ALLOWED_HOSTS=meudominio.com
```

**3 · Dependência vulnerável.** `pip-audit` achou PYSEC-2026-3696 a 3699 e 3923 no `sqlparse 0.5.5`. Atualizado para 0.6.0; o CI roda `pip-audit` em todo PR.

**4 e 5 · Limite de tentativas.** O contador é por IP (`REMOTE_ADDR`), nunca por `X-Forwarded-For`, que quem ataca escreve como quiser. É por IP e não por conta de propósito: limite por conta deixaria qualquer um trancar a conta `demo` de outra pessoa errando a senha dela. O bloqueio é checado antes da senha, então quem está bloqueado não consegue nem saber se acertou. Limite conhecido: o cache padrão do Django vale por processo; com vários workers, trocar `CACHES` para Redis.

**7 · CSP.** Fecha script de outro domínio, `<object>`, `<base>` trocado, formulário postando para fora e o site dentro de iframe alheio. Mantém `'unsafe-inline'` em script e estilo porque as capas usam `onerror` e `style="--matiz"`. Tirar isso exige mover o `onerror` para um `.js` e trocar o estilo inline por classes; vale quando o projeto for para o ar de verdade.

**8 · CSV.** Um filme com título `=HYPERLINK("http://site")` virava link clicável no Excel de quem abrisse o relatório. Agora célula que começa com `=`, `+`, `-`, `@`, tab ou quebra de linha ganha um apóstrofo na frente e é mostrada como texto.

**9 e 10 · Corridas.** A tela de exclusão conta os vínculos e só então apaga. Se outra conta ligar um filme ao diretor nesse intervalo, o `PROTECT` do banco barra, e antes isso virava página 500; agora volta para a confirmação, que reconta e explica o bloqueio. No elenco, dois envios simultâneos (duplo clique) passavam juntos pelo `clean_ator`; quem barra é a `UniqueConstraint`, e o erro dela agora vira mensagem no campo. É a regra do ProLobby: idempotência pelo banco, não por "checa e insere".

**16 · Porta lateral do admin.** O `/admin/` usa o `AdminAuthenticationForm`, não o login do site, então o limite novo não valia lá, justamente na conta mais poderosa. Agora `admin.site.login_form` usa o mesmo limite, e o contador é compartilhado: errar no site conta no admin, e vice-versa.

**17 · Filtros da Consulta.** As opções vinham de `Ator.objects.all()`. A `demo` via no filtro "Cillian Murphy", que só existe no catálogo da `ana`. Isso vaza um pedaço do catálogo de outra conta, e filtrar por esse nome nunca traz resultado. Agora gênero, diretor e ator saem só dos filmes de quem consulta.

**18 · Vitrine.** A parede de cartazes do início usa as capas da `demo`, e a senha dela está no README. Qualquer pessoa podia entrar, colar um link de imagem num filme e fazer essa imagem aparecer para todo visitante do site. Agora a vitrine só aceita capas de `upload.wikimedia.org`.

**19 · Admin.** O Django admin é montado sobre variáveis CSS. `templates/admin/base_site.html` carrega `catalogo/static/catalogo/admin.css`, que troca as variáveis pelas cores e fontes do site, sem copiar nenhum template do admin. O seletor de tema claro sai, porque o site só tem tema escuro. Os rótulos ganharam acento pelo `verbose_name` dos models (migrations 0012 e `usuarios` 0002, que só mudam rótulo e não tocam no banco).

**21 · IDs sequenciais.** Trocar `/filmes/1/` por um código aleatório esconderia quantos filmes existem, mas não protege nada: um id de outra conta já devolve 404 (`test_id_de_outro_usuario_na_url_retorna_404`). A troca exige uma coluna nova em todas as tabelas com dono e mudar todas as rotas. Vale só se o número de registros virar informação sensível.

## Regras que já pegaram bug

| Regra do ProLobby | Aqui |
|---|---|
| Guard fechado por padrão | Django não tem guard global; cada view interna tem `@login_required`. O teste `test_areas_internas_redirecionam_para_login` confere as principais. |
| Segurança no módulo, não no bootstrap | Middleware e validadores estão no `settings.py`, que os testes carregam. OK. |
| GET nunca muda estado | OK, ver item 9b. |
| Resposta não revela se a conta existe | O login do Django já devolve a mesma mensagem nos dois casos; o bloqueio também. O cadastro diz "usuário já existe", o que é aceitável num catálogo pessoal sem e-mail. |
| I/O de terceiro fora da resposta | A busca de capa espera a Wikipédia (até 15 s) dentro da requisição. Aceito: é ação manual do próprio dono, com botão, e a falha vira aviso. |
| Idempotência pelo banco | Corrigido no elenco (achado 10). |
| Migration sempre de banco limpo | O CI roda `makemigrations --check` e os testes criam o banco do zero a cada execução. |
| Sem N+1 | Revisadas todas as listas: `select_related` e `Prefetch` estão onde precisam. O único N+1 latente (`media_nota`) estava sem uso e foi removido. |

## Fluxo de código, CI e PR

- **CI** em [`.github/workflows/ci.yml`](.github/workflows/ci.yml): `pip-audit`, `makemigrations --check`, os 30 testes e `check --deploy` em modo produção. Permissão só de leitura e action presa por hash, como no ProLobby.
- **Template de PR** em [`.github/pull_request_template.md`](.github/pull_request_template.md), com o checklist traduzido para este projeto.
- **Commits** em português, no padrão Conventional Commits (`feat:`, `fix:`, `chore:`).

## Não corrigido de propósito

**13 · Gênero, Diretor e Ator podem ser editados por qualquer conta.** São tabelas compartilhadas ([DECISOES.md, item 26](DECISOES.md)): se a conta `ana` renomeia "Drama" para "Comédia", o catálogo da `demo` muda junto. Pelo item 7 do checklist isso é furo. A correção é um campo `criado_por` nessas tabelas, deixando editar e excluir só quem criou ou o staff. Ficou de fora porque os registros do seed não têm criador, então a `demo` deixaria de editar os gêneros prontos, e isso quebra o passo 4 do roteiro de apresentação. Vale fazer se o projeto sair do ambiente de sala.

**14 · Contas com senha conhecida.** As migrations 0004, 0009 e 0010 criam `demo`, `ana` e `admin` com a senha `filmes123` em qualquer banco onde rodarem, inclusive um de produção. Aqui é o que faz o projeto abrir pronto para apresentar. Antes de qualquer deploy público: trocar as senhas (`manage.py changepassword admin`) ou tirar essas migrations.

**15 · Idioma do código.** O ProLobby exige código em inglês e projeto em português, nunca misturados no mesmo arquivo. Aqui todo o código é em português (`Filme`, `filmes_do`, `criar_avaliacao`), e o enunciado do trabalho e a apresentação usam esses nomes. Renomear exige migration de todas as tabelas e reescrever as 11 migrations de seed, sem ganho para o avaliador. A regra que vale e foi seguida é a da fronteira: o código novo desta revisão também é em português, para nenhum arquivo ficar com meia frase em cada idioma.
