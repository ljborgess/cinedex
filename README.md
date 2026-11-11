# Catálogo de Filmes

Filmoteca pessoal em Django: cada usuário cadastra os próprios filmes, monta o elenco, dá notas e acompanha tudo num painel. São **7 models** em **2 apps**, com relações **1:N, 1:1 e N:N com tabela intermediária**, login obrigatório nas áreas internas e isolamento de dados por usuário.

Continuação dos trabalhos anteriores (2 models → 4 models → versão final).

## Stack

- Django 5.2
- SQLite (padrão do Django)
- HTML/CSS puro, sem frameworks front-end

## Instalação e execução

```bash
# 1. Criar e ativar o ambiente virtual
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

# 2. Instalar as dependências
pip install -r requirements.txt

# 3. Aplicar as migrations (o seed já popula todas as tabelas)
python manage.py migrate

# 4. Rodar o servidor
python manage.py runserver
```

A aplicação abre em `http://127.0.0.1:8000/`.

### Conta de demonstração

A migration de seed cria um usuário com os 20 filmes, 44 avaliações e o elenco de exemplo:

| Usuário | Senha |
|---|---|
| `demo` | `filmes123` |

Uma conta nova (em **Criar conta**) começa com o catálogo vazio, o que mostra o isolamento de dados na prática. Para usar o `/admin/`, crie um superusuário com `python manage.py createsuperuser`.

### Capas dos filmes

Os filmes do seed já vêm com o link do pôster (exibido direto da Wikimedia, então precisa de internet; sem ela, aparece a capa desenhada). Para filmes novos:

- na página do filme, clique em **Buscar capa automaticamente**; ou
- cole o endereço de uma imagem no campo **Link da capa** ao editar; ou
- preencha todos de uma vez: `python manage.py buscar_capas` (use `--usuario demo` para um usuário só e `--todos` para refazer quem já tem capa).

### Testes

```bash
python manage.py test
```

São 16 testes em `catalogo/tests.py`: acesso público e restrito, isolamento entre usuários, dashboard, CSV, relacionamentos e capas.

## Apps

| App | Responsabilidade |
|---|---|
| `usuarios` | login, logout, cadastro e perfil (model `Perfil`) |
| `catalogo` | entidades de negócio: filmes, elenco, diretores, gêneros, avaliações, painel e consultas |

`core/` é o pacote de configuração do projeto (`settings.py`, `urls.py`), não um app.

## Modelo de dados

```
                 User ──1:1── Perfil ──N:1── Genero (favorito)
                  │
                  │ 1:N (dono)
                  ▼
Genero ──1:N──┐
              ├──> Filme ──1:N──> Avaliacao <── 1:N ── User
Diretor ─1:N──┘      │
                     │ N:N through Elenco (personagem, ordem)
                     ▼
                    Ator
```

### Relacionamentos

| Tipo | Relação | Como está no código |
|---|---|---|
| **1:1** | `User` ↔ `Perfil` | `Perfil.usuario = OneToOneField(User)` |
| **1:N** | `Genero` → `Filme` | `Filme.genero = ForeignKey(Genero, PROTECT)` |
| **1:N** | `Diretor` → `Filme` | `Filme.diretor = ForeignKey(Diretor, PROTECT)` |
| **1:N** | `Filme` → `Avaliacao` | `Avaliacao.filme = ForeignKey(Filme, CASCADE)` |
| **1:N** | `User` → `Filme` / `Avaliacao` | campo `usuario` (dono do registro) |
| **N:N com through** | `Filme` ↔ `Ator` | `Filme.atores = ManyToManyField(Ator, through='Elenco')` |

### Os models

| Model | App | Campos principais |
|---|---|---|
| `Perfil` | usuarios | usuario (1:1), apelido, bio, genero_favorito, criado_em |
| `Genero` | catalogo | nome (único) |
| `Diretor` | catalogo | nome, nacionalidade |
| `Ator` | catalogo | nome, nacionalidade |
| `Filme` | catalogo | titulo, genero, diretor, sinopse, capa_url, atores, usuario |
| `Elenco` | catalogo | filme, ator, personagem, ordem — único por (filme, ator) |
| `Avaliacao` | catalogo | filme, autor, nota (1–5), comentario, criado_em, usuario |

### `on_delete`

- `PROTECT` em `Filme.genero`, `Filme.diretor` e `Elenco.ator`: tabelas de referência não podem sumir enquanto houver filme ligado a elas. A interface explica o bloqueio em vez de dar erro.
- `CASCADE` em `Avaliacao.filme` e `Elenco.filme`: avaliação e participação só existem em função do filme.
- `SET_NULL` em `Perfil.genero_favorito`: apagar um gênero não apaga o perfil de ninguém.

## Segurança

- **Área pública vs. restrita:** só a Home (`/`), `/login/` e `/cadastro/` abrem sem login. Todas as outras views têm `@login_required(login_url='login')`, e `LOGIN_URL = 'login'` está no `settings.py`. Quem tenta abrir uma tela interna é mandado para `/login/?next=...` e volta para ela depois de entrar.
- **Isolamento de dados:** toda consulta de `Filme`, `Avaliacao` e `Elenco` parte de `request.user` (funções `filmes_do`, `avaliacoes_do` e `elenco_do` em `catalogo/views.py`), inclusive as buscas por `pk`. Um id de outro usuário digitado na URL retorna 404. O dono é gravado a partir da sessão no `save`, nunca a partir do formulário, e o `AvaliacaoForm` só aceita filmes do próprio usuário.
- **CSRF:** todos os formulários POST têm `{% csrf_token %}`, inclusive o botão **Sair** (no Django 5 o logout é por POST).

Gênero, Diretor e Ator são tabelas de referência compartilhadas (o mesmo "Drama" serve para todos), mas os filmes exibidos dentro delas também passam pelo filtro do usuário. Ver [DECISOES.md](DECISOES.md), item 26.

## Telas

| URL | Acesso | Descrição |
|---|---|---|
| `/` | público | Home |
| `/login/`, `/cadastro/` | público | autenticação |
| `/perfil/` | restrito | edição do perfil (1:1) |
| `/dashboard/` | restrito | indicadores do usuário: totais, média geral, filmes por gênero, destaque, últimos filmes e avaliações |
| `/consultas/` | restrito | filtros (título, gênero, diretor, ator, média mínima, ordenação) e **exportação CSV** do resultado |
| `/filmes/` | restrito | CRUD de filmes + elenco na página de detalhe |
| `/atores/` | restrito | CRUD de atores |
| `/diretores/` | restrito | CRUD de diretores |
| `/generos/` | restrito | CRUD de gêneros |
| `/avaliacoes/` | restrito | CRUD de avaliações |
| `/admin/` | staff | painel administrativo do Django |

Os CRUDs seguem o mesmo padrão de rotas: `/`, `/novo/`, `/<pk>/`, `/<pk>/editar/` e `/<pk>/excluir/`. Todos os formulários são `ModelForm`, menos o de filtros da consulta, que é um `Form` comum porque não grava nada.

## Organização do código

```
core/                        configurações e rotas do projeto
usuarios/
  models.py                  Perfil (1:1 com User)
  signals.py                 cria o Perfil de todo usuário novo
  forms.py                   CadastroForm, PerfilForm
  views.py                   cadastro e perfil (login/logout são as views do Django)
  templates/usuarios/        login.html, cadastro.html
catalogo/
  models.py                  Genero, Diretor, Ator, Filme, Elenco, Avaliacao
  forms.py                   um ModelForm por model + ConsultaForm
  views.py                   home, painel, consultas/CSV e os CRUDs
  capas.py                   busca do pôster na Wikipédia
  management/commands/       buscar_capas (preenche as capas em lote)
  tests.py                   testes automatizados
  migrations/
    0002, 0003               seed de gêneros, diretores, filmes e avaliações
    0004_dono_dos_registros  cria a conta demo e dá dono ao seed
    0006_seed_elenco         atores e elenco de exemplo
    0008_seed_capas          links dos pôsteres dos filmes do seed
  templates/catalogo/
    base.html                layout e navegação (muda com o login)
    form.html                formulário compartilhado por todos os ModelForms
    confirmar_exclusao.html  confirmação compartilhada
```

## Decisões de projeto

As escolhas de modelagem e arquitetura, com as alternativas descartadas, estão em [DECISOES.md](DECISOES.md).
