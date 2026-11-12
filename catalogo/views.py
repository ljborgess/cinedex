import csv
from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Avg, Count, F, Prefetch, ProtectedError, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.urls import reverse

from .capas import ErroDeBusca, buscar_capa
from .forms import (
    AtorForm, AvaliacaoForm, ConsultaForm, DiretorForm, ElencoForm, FilmeForm, GeneroForm,
)
from .models import Ator, Avaliacao, Diretor, Elenco, Filme, Genero

# Regra de isolamento: Filme e Avaliacao têm dono. Toda consulta a eles parte
# de `filmes_do(request)` / `avaliacoes_do(request)`, inclusive as que buscam
# por pk. Assim um id digitado na URL que pertença a outra pessoa vira 404,
# em vez de abrir o registro dela.
#
# Gênero e Diretor são tabelas de referência compartilhadas (o mesmo
# "Drama" serve para todo mundo), mas os filmes exibidos dentro deles também
# passam pelo filtro do usuário.


def _filmes(n):
    """'1 filme' / '4 filmes': o texto de bloqueio não usa 'filme(s)'."""
    return f'{n} filme' if n == 1 else f'{n} filmes'


def _excluiu(registro):
    """Exclui gênero, diretor ou ator; False se o PROTECT do banco barrar.

    A view conta os vínculos antes, mas outra conta pode ligar um filme ao
    registro entre a contagem e o delete. Nesse caso a view volta para a
    confirmação, que recontou e mostra o bloqueio em vez de uma página 500.
    """
    try:
        registro.delete()
    except ProtectedError:
        return False
    return True


def filmes_do(request):
    return Filme.objects.filter(usuario=request.user)


def avaliacoes_do(request):
    return Avaliacao.objects.filter(usuario=request.user)


# --------------------------------------------------------------------- home
# Única tela aberta do catálogo. Todas as outras exigem login.

def home(request):
    return render(request, 'catalogo/home.html')


# A parede de cartazes da página inicial usa só as capas da conta de
# demonstração: o catálogo de cada usuário continua invisível para os outros.
CONTA_DA_VITRINE = 'demo'
WIKIMEDIA = 'https://upload.wikimedia.org/wikipedia/'


def _miniatura(url, largura=330):
    """Troca o arquivo original da Wikimedia pela miniatura, três vezes mais leve."""
    prefixo = WIKIMEDIA
    if not url.startswith(prefixo) or '/thumb/' in url:
        return url
    projeto, resto = url[len(prefixo):].split('/', 1)
    arquivo = resto.rsplit('/', 1)[-1]
    return f'{prefixo}{projeto}/thumb/{resto}/{largura}px-{arquivo}'


def _fileiras_da_vitrine(quantas=4, por_fileira=16):
    # Só capas da Wikimedia: a senha da `demo` é pública, então qualquer pessoa
    # pode colar um link no filme dela. Sem esse filtro, a imagem que ela
    # escolhesse apareceria no início do site para todos os visitantes.
    capas = list(
        Filme.objects.filter(usuario__username=CONTA_DA_VITRINE, capa_url__startswith=WIKIMEDIA)
        .order_by('pk')
        .values_list('capa_url', flat=True)
    )
    if len(capas) < 4:
        return []
    capas = [_miniatura(url) for url in capas]
    passo = max(1, len(capas) // quantas)
    fileiras = []
    for indice in range(quantas):
        girada = capas[indice * passo:] + capas[:indice * passo]
        fileiras.append((girada * por_fileira)[:por_fileira])
    return fileiras


# ---------------------------------------------------------------- dashboard

@login_required(login_url='login')
def dashboard(request):
    filmes = filmes_do(request).select_related('genero', 'diretor')
    avaliacoes = avaliacoes_do(request)

    destaque = (
        filmes.annotate(media=Avg('avaliacoes__nota'))
        .filter(media__isnull=False)
        .order_by('-media')
        .first()
    )

    contexto = {
        'total_filmes': filmes.count(),
        'total_diretores': Diretor.objects.filter(filmes__usuario=request.user).distinct().count(),
        'total_generos': Genero.objects.filter(filmes__usuario=request.user).distinct().count(),
        'total_avaliacoes': avaliacoes.count(),
        'media_geral': avaliacoes.aggregate(m=Avg('nota'))['m'],
        'por_genero': (
            Genero.objects.annotate(total=Count('filmes', filter=Q(filmes__usuario=request.user)))
            .filter(total__gt=0)
            .order_by('-total', 'nome')
        ),
        'ultimos_filmes': filmes.order_by('-id')[:5],
        'ultimas_avaliacoes': avaliacoes.select_related('filme', 'filme__genero', 'filme__diretor')[:5],
        'destaque': destaque,
        # Para a conta nova: gêneros e diretores são compartilhados, então já
        # existem opções prontas antes do primeiro filme.
        'generos_disponiveis': Genero.objects.count(),
        'diretores_disponiveis': Diretor.objects.count(),
    }
    return render(request, 'catalogo/dashboard.html', contexto)


# ----------------------------------------------------------------- consultas

def filtrar_filmes(request, dados):
    """Aplica os filtros validados do ConsultaForm aos filmes do usuário."""
    filmes = filmes_do(request)
    if dados.get('titulo'):
        filmes = filmes.filter(titulo__icontains=dados['titulo'])
    if dados.get('genero'):
        filmes = filmes.filter(genero=dados['genero'])
    if dados.get('diretor'):
        filmes = filmes.filter(diretor=dados['diretor'])
    if dados.get('ator'):
        filmes = filmes.filter(atores=dados['ator'])

    # Count com distinct: o filtro por ator acrescenta um JOIN e não pode
    # multiplicar a contagem de avaliações.
    filmes = filmes.select_related('genero', 'diretor').annotate(
        media=Avg('avaliacoes__nota'),
        total_avaliacoes=Count('avaliacoes', distinct=True),
    )
    if dados.get('nota_minima'):
        filmes = filmes.filter(media__gte=dados['nota_minima'])

    ordem = dados.get('ordenar') or 'titulo'
    if ordem == '-media':
        return filmes.order_by(F('media').desc(nulls_last=True), 'titulo')
    return filmes.order_by(ordem, 'titulo')


@login_required(login_url='login')
def consulta(request):
    form = ConsultaForm(request.GET or None, usuario=request.user)
    dados = form.cleaned_data if form.is_valid() else {}
    filmes = filtrar_filmes(request, dados).prefetch_related('atores')

    if request.GET.get('formato') == 'csv':
        return exportar_csv(filmes)

    return render(request, 'catalogo/consulta.html', {
        'form': form,
        'filmes': filmes,
        'resumo': avaliacoes_do(request).filter(filme__in=filmes.values('pk')).aggregate(
            media=Avg('nota'), avaliacoes=Count('id'),
        ),
        # Mesma busca, com o formato trocado: o relatório exporta o que está na tela.
        'link_csv': '?' + _query_com(request, formato='csv'),
    })


def _query_com(request, **extras):
    query = request.GET.copy()
    for chave, valor in extras.items():
        query[chave] = valor
    return query.urlencode()


def _celula(texto):
    """Texto digitado pelo usuário, seguro para abrir no Excel.

    Uma célula que começa com = + - @ é lida como fórmula: um título como
    `=HYPERLINK(...)` viraria link clicável no relatório. O apóstrofo na frente
    faz o Excel mostrar o conteúdo como texto.
    """
    return "'" + texto if texto[:1] in ('=', '+', '-', '@', '\t', '\r') else texto


def exportar_csv(filmes):
    resposta = HttpResponse(content_type='text/csv; charset=utf-8')
    resposta['Content-Disposition'] = 'attachment; filename="relatorio_filmes.csv"'
    # BOM + ponto e vírgula: o Excel em português abre acentos e colunas certo.
    resposta.write('\ufeff')
    escritor = csv.writer(resposta, delimiter=';')
    escritor.writerow(['Título', 'Gênero', 'Diretor', 'Elenco', 'Avaliações', 'Média'])
    for filme in filmes:
        escritor.writerow([
            _celula(filme.titulo),
            _celula(filme.genero.nome),
            _celula(filme.diretor.nome),
            _celula(', '.join(ator.nome for ator in filme.atores.all())),
            filme.total_avaliacoes,
            f'{filme.media:.1f}'.replace('.', ',') if filme.media is not None else '',
        ])
    return resposta


# ------------------------------------------------------------------ detalhes
# Cada página abaixo é a prova visual de uma relação 1:N: o filme mostra suas
# avaliações, o diretor e o gênero mostram seus filmes.

# Onde assistir: não existe API pública e gratuita que diga em qual serviço o
# filme está hoje (isso muda toda semana). Então a página não afirma
# disponibilidade: ela abre a busca do título em cada serviço, e o JustWatch,
# que mostra onde o filme está disponível no Brasil.
SERVICOS_DE_STREAMING = [
    ('Netflix', 'https://www.netflix.com/search?q={}'),
    ('Prime Video', 'https://www.primevideo.com/search/?phrase={}'),
    ('Max', 'https://play.max.com/search?q={}'),
    ('Globoplay', 'https://globoplay.globo.com/busca/?q={}'),
    ('Apple TV', 'https://tv.apple.com/br/search?term={}'),
]
JUSTWATCH = 'https://www.justwatch.com/br/busca?q={}'


def _onde_assistir(titulo):
    termo = quote(titulo)
    return {
        'disponibilidade': JUSTWATCH.format(termo),
        'servicos': [
            {'nome': nome, 'url': url.format(termo)} for nome, url in SERVICOS_DE_STREAMING
        ],
    }


@login_required(login_url='login')
def detalhe_filme(request, pk):
    filme = get_object_or_404(
        filmes_do(request).select_related('genero', 'diretor'), pk=pk
    )
    avaliacoes = list(filme.avaliacoes.all())
    total = len(avaliacoes)
    media = sum(a.nota for a in avaliacoes) / total if total else None

    # Quantas avaliações deram cada nota, de 5 a 1, para as barras do resumo.
    distribuicao = [
        {
            'nota': nota,
            'quantas': sum(1 for a in avaliacoes if a.nota == nota),
        }
        for nota in range(5, 0, -1)
    ]
    for linha in distribuicao:
        linha['porcento'] = round(100 * linha['quantas'] / total) if total else 0

    return render(request, 'catalogo/filme_detalhe.html', {
        'filme': filme,
        'elenco': filme.elenco.select_related('ator'),
        'avaliacoes': avaliacoes,
        'media': media,
        'distribuicao': distribuicao,
        'onde_assistir': _onde_assistir(filme.titulo),
        'do_mesmo_diretor': (
            filmes_do(request).filter(diretor=filme.diretor)
            .exclude(pk=filme.pk).select_related('genero', 'diretor')
        ),
    })


@login_required(login_url='login')
def detalhe_diretor(request, pk):
    diretor = get_object_or_404(Diretor, pk=pk)
    return render(request, 'catalogo/diretor_detalhe.html', {
        'diretor': diretor,
        'filmes': (
            filmes_do(request).filter(diretor=diretor)
            .select_related('genero', 'diretor').annotate(media=Avg('avaliacoes__nota'))
        ),
    })


@login_required(login_url='login')
def detalhe_genero(request, pk):
    genero = get_object_or_404(Genero, pk=pk)
    return render(request, 'catalogo/genero_detalhe.html', {
        'genero': genero,
        'filmes': (
            filmes_do(request).filter(genero=genero)
            .select_related('genero', 'diretor').annotate(media=Avg('avaliacoes__nota'))
        ),
    })


# -------------------------------------------------------------------- filmes

@login_required(login_url='login')
def lista_filmes(request):
    filmes = (
        filmes_do(request).select_related('genero', 'diretor')
        .annotate(media=Avg('avaliacoes__nota'), total_avaliacoes=Count('avaliacoes'))
    )
    return render(request, 'catalogo/filme_lista.html', {'filmes': filmes})


@login_required(login_url='login')
def criar_filme(request):
    form = FilmeForm(request.POST or None)
    if form.is_valid():
        filme = form.save(commit=False)
        filme.usuario = request.user  # o dono vem da sessão, nunca do formulário
        filme.save()
        return redirect('detalhe_filme', pk=filme.pk)
    return render(request, 'catalogo/form.html', {
        'form': form,
        'titulo_pagina': 'Novo filme',
        'voltar_para': 'lista_filmes',
    })


@login_required(login_url='login')
def editar_filme(request, pk):
    filme = get_object_or_404(filmes_do(request), pk=pk)
    form = FilmeForm(request.POST or None, instance=filme)
    if form.is_valid():
        form.save()
        return redirect('detalhe_filme', pk=filme.pk)
    return render(request, 'catalogo/form.html', {
        'form': form,
        'titulo_pagina': f'Editar: {filme.titulo}',
        'voltar_para': 'lista_filmes',
    })


@login_required(login_url='login')
def excluir_filme(request, pk):
    filme = get_object_or_404(filmes_do(request), pk=pk)
    if request.method == 'POST':
        filme.delete()
        return redirect('lista_filmes')
    return render(request, 'catalogo/confirmar_exclusao.html', {
        'objeto': filme,
        'tipo': 'filme',
        'detalhe': f'{filme.genero} · {filme.diretor}',
        'aviso': 'As avaliações deste filme também serão excluídas.',
        'voltar_para': 'lista_filmes',
    })


# -------------------------------------------------------------------- elenco
# Linhas da tabela through Filme <-> Ator. A posse é verificada pelo filme:
# só o dono do filme mexe no elenco dele.

def elenco_do(request):
    return Elenco.objects.filter(filme__usuario=request.user).select_related('filme', 'ator')


def _salvou_sem_repetir(form, participacao):
    """Grava a participação; se o ator já entrou no filme, vira erro do formulário.

    O `clean_ator` já recusa o repetido, mas dois envios simultâneos (duplo
    clique) passam juntos pela checagem. Quem decide no fim é a
    UniqueConstraint do banco, e o erro dela não pode virar página 500.
    """
    try:
        with transaction.atomic():
            participacao.save()
    except IntegrityError:
        form.add_error('ator', 'Este ator já está no elenco do filme.')
        return False
    return True


@login_required(login_url='login')
def criar_elenco(request, pk):
    filme = get_object_or_404(filmes_do(request), pk=pk)
    form = ElencoForm(request.POST or None, filme=filme, initial={'ordem': filme.elenco.count() + 1})
    if form.is_valid():
        participacao = form.save(commit=False)
        participacao.filme = filme
        if _salvou_sem_repetir(form, participacao):
            return redirect('detalhe_filme', pk=filme.pk)
    return render(request, 'catalogo/form.html', {
        'form': form,
        'titulo_pagina': f'Elenco de {filme.titulo}',
        'voltar_url': reverse('detalhe_filme', args=[filme.pk]),
    })


@login_required(login_url='login')
def editar_elenco(request, pk):
    participacao = get_object_or_404(elenco_do(request), pk=pk)
    form = ElencoForm(request.POST or None, instance=participacao, filme=participacao.filme)
    if form.is_valid() and _salvou_sem_repetir(form, form.instance):
        return redirect('detalhe_filme', pk=participacao.filme_id)
    return render(request, 'catalogo/form.html', {
        'form': form,
        'titulo_pagina': f'Editar: {participacao.ator} em {participacao.filme}',
        'voltar_url': reverse('detalhe_filme', args=[participacao.filme_id]),
    })


@login_required(login_url='login')
def excluir_elenco(request, pk):
    participacao = get_object_or_404(elenco_do(request), pk=pk)
    if request.method == 'POST':
        participacao.delete()
        return redirect('detalhe_filme', pk=participacao.filme_id)
    return render(request, 'catalogo/confirmar_exclusao.html', {
        'objeto': participacao,
        'tipo': 'vínculo',
        'detalhe': 'O ator sai do elenco deste filme, mas continua cadastrado.',
        'voltar_url': reverse('detalhe_filme', args=[participacao.filme_id]),
    })


# -------------------------------------------------------------------- atores

@login_required(login_url='login')
def lista_atores(request):
    meus = Q(filmes__usuario=request.user)
    # Atores são compartilhados, mas a lista mostra só quem está no seu
    # catálogo ou quem ainda não está em filme nenhum (recém-cadastrado).
    # Quem só aparece em filmes de outras contas fica de fora.
    atores = (
        Ator.objects.annotate(
            total_filmes=Count('filmes', filter=meus, distinct=True),
            total_geral=Count('filmes', distinct=True),
        )
        .filter(Q(total_filmes__gt=0) | Q(total_geral=0))
        .order_by('nome')
        .prefetch_related(
            Prefetch('filmes', queryset=filmes_do(request).select_related('genero', 'diretor'))
        )
    )
    return render(request, 'catalogo/ator_lista.html', {'atores': atores})


@login_required(login_url='login')
def detalhe_ator(request, pk):
    ator = get_object_or_404(Ator, pk=pk)
    participacoes = (
        elenco_do(request).filter(ator=ator)
        .select_related('filme__genero', 'filme__diretor')
        .order_by('filme__titulo')
    )
    return render(request, 'catalogo/ator_detalhe.html', {
        'ator': ator,
        'participacoes': participacoes,
    })


@login_required(login_url='login')
def criar_ator(request):
    form = AtorForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('lista_atores')
    return render(request, 'catalogo/form.html', {
        'form': form,
        'titulo_pagina': 'Novo ator',
        'voltar_para': 'lista_atores',
    })


@login_required(login_url='login')
def editar_ator(request, pk):
    ator = get_object_or_404(Ator, pk=pk)
    form = AtorForm(request.POST or None, instance=ator)
    if form.is_valid():
        form.save()
        return redirect('lista_atores')
    return render(request, 'catalogo/form.html', {
        'form': form,
        'titulo_pagina': f'Editar: {ator.nome}',
        'voltar_para': 'lista_atores',
    })


@login_required(login_url='login')
def excluir_ator(request, pk):
    ator = get_object_or_404(Ator, pk=pk)
    vinculos = ator.participacoes.count()

    if request.method == 'POST' and vinculos == 0:
        if _excluiu(ator):
            return redirect('lista_atores')
        return redirect('excluir_ator', pk=ator.pk)

    return render(request, 'catalogo/confirmar_exclusao.html', {
        'objeto': ator,
        'tipo': 'ator',
        'detalhe': ator.nacionalidade,
        'bloqueio': (
            f'{ator.nome} está no elenco de {_filmes(vinculos)}. Um ator não pode sair '
            f'do cadastro enquanto aparece nos créditos.'
        ) if vinculos else '',
        'como_liberar': 'Remova o ator do elenco desses filmes e a exclusão fica liberada.',
        'resolver_url': reverse('detalhe_ator', args=[ator.pk]),
        'resolver_rotulo': 'Ver filmografia',
        'voltar_para': 'lista_atores',
    })


# --------------------------------------------------------------------- capas

@login_required(login_url='login')
@require_POST
def buscar_capa_filme(request, pk):
    filme = get_object_or_404(filmes_do(request).select_related('diretor'), pk=pk)
    try:
        url = buscar_capa(filme.titulo, filme.diretor.nome)
    except ErroDeBusca as erro:
        messages.warning(request, f'Não foi possível buscar a capa agora: {erro}.')
        return redirect('detalhe_filme', pk=filme.pk)

    if url:
        filme.capa_url = url
        filme.save(update_fields=['capa_url'])
        messages.success(request, 'Capa encontrada na Wikipédia. Se não for a certa, troque o link em Editar.')
    else:
        messages.warning(request, 'Nenhuma capa confiável encontrada. Você pode colar um link em Editar.')
    return redirect('detalhe_filme', pk=filme.pk)


# ----------------------------------------------------------------- diretores

@login_required(login_url='login')
def lista_diretores(request):
    meus = Q(filmes__usuario=request.user)
    diretores = Diretor.objects.annotate(total_filmes=Count('filmes', filter=meus)).prefetch_related(
        Prefetch('filmes', queryset=filmes_do(request).select_related('genero', 'diretor'))
    )
    return render(request, 'catalogo/diretor_lista.html', {'diretores': diretores})


@login_required(login_url='login')
def criar_diretor(request):
    form = DiretorForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('lista_diretores')
    return render(request, 'catalogo/form.html', {
        'form': form,
        'titulo_pagina': 'Novo diretor',
        'voltar_para': 'lista_diretores',
    })


@login_required(login_url='login')
def editar_diretor(request, pk):
    diretor = get_object_or_404(Diretor, pk=pk)
    form = DiretorForm(request.POST or None, instance=diretor)
    if form.is_valid():
        form.save()
        return redirect('lista_diretores')
    return render(request, 'catalogo/form.html', {
        'form': form,
        'titulo_pagina': f'Editar: {diretor.nome}',
        'voltar_para': 'lista_diretores',
    })


@login_required(login_url='login')
def excluir_diretor(request, pk):
    diretor = get_object_or_404(Diretor, pk=pk)
    # Conta os filmes de todos os usuários: o PROTECT do banco vale para todos.
    filmes_vinculados = diretor.filmes.count()

    if request.method == 'POST' and filmes_vinculados == 0:
        if _excluiu(diretor):
            return redirect('lista_diretores')
        return redirect('excluir_diretor', pk=diretor.pk)

    return render(request, 'catalogo/confirmar_exclusao.html', {
        'objeto': diretor,
        'tipo': 'diretor',
        'detalhe': diretor.nacionalidade,
        'bloqueio': (
            f'{diretor.nome} assina a direção de {_filmes(filmes_vinculados)} no sistema. '
            f'Um filme não pode ficar sem diretor.'
        ) if filmes_vinculados else '',
        'como_liberar': 'Troque o diretor desses filmes ou exclua-os, e a exclusão fica liberada.',
        'resolver_url': reverse('detalhe_diretor', args=[diretor.pk]),
        'resolver_rotulo': 'Ver filmes do diretor',
        'voltar_para': 'lista_diretores',
    })


# -------------------------------------------------------------------- gêneros

@login_required(login_url='login')
def lista_generos(request):
    meus = Q(filmes__usuario=request.user)
    generos = Genero.objects.annotate(total_filmes=Count('filmes', filter=meus)).prefetch_related(
        Prefetch('filmes', queryset=filmes_do(request).select_related('genero', 'diretor'))
    )
    return render(request, 'catalogo/genero_lista.html', {'generos': generos})


@login_required(login_url='login')
def criar_genero(request):
    form = GeneroForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('lista_generos')
    return render(request, 'catalogo/form.html', {
        'form': form,
        'titulo_pagina': 'Novo gênero',
        'voltar_para': 'lista_generos',
    })


@login_required(login_url='login')
def editar_genero(request, pk):
    genero = get_object_or_404(Genero, pk=pk)
    form = GeneroForm(request.POST or None, instance=genero)
    if form.is_valid():
        form.save()
        return redirect('lista_generos')
    return render(request, 'catalogo/form.html', {
        'form': form,
        'titulo_pagina': f'Editar: {genero.nome}',
        'voltar_para': 'lista_generos',
    })


@login_required(login_url='login')
def excluir_genero(request, pk):
    genero = get_object_or_404(Genero, pk=pk)
    filmes_vinculados = genero.filmes.count()

    if request.method == 'POST' and filmes_vinculados == 0:
        if _excluiu(genero):
            return redirect('lista_generos')
        return redirect('excluir_genero', pk=genero.pk)

    return render(request, 'catalogo/confirmar_exclusao.html', {
        'objeto': genero,
        'tipo': 'gênero',
        'detalhe': '',
        'bloqueio': (
            f'{genero.nome} classifica {_filmes(filmes_vinculados)} no sistema. '
            f'Um filme não pode ficar sem gênero.'
        ) if filmes_vinculados else '',
        'como_liberar': 'Mude o gênero desses filmes ou exclua-os, e a exclusão fica liberada.',
        'resolver_url': reverse('detalhe_genero', args=[genero.pk]),
        'resolver_rotulo': 'Ver filmes do gênero',
        'voltar_para': 'lista_generos',
    })


# ---------------------------------------------------------------- avaliações

@login_required(login_url='login')
def lista_avaliacoes(request):
    avaliacoes = avaliacoes_do(request).select_related('filme', 'filme__genero', 'filme__diretor')
    return render(request, 'catalogo/avaliacao_lista.html', {'avaliacoes': avaliacoes})


@login_required(login_url='login')
def criar_avaliacao(request):
    perfil = getattr(request.user, 'perfil', None)
    inicial = {
        'autor': perfil.nome_exibicao if perfil else request.user.username,
        'filme': request.GET.get('filme'),
    }
    form = AvaliacaoForm(request.POST or None, usuario=request.user, initial=inicial)
    if form.is_valid():
        avaliacao = form.save(commit=False)
        avaliacao.usuario = request.user
        avaliacao.save()
        return redirect('detalhe_filme', pk=avaliacao.filme_id)
    return render(request, 'catalogo/form.html', {
        'form': form,
        'titulo_pagina': 'Nova avaliação',
        'voltar_para': 'lista_avaliacoes',
    })


@login_required(login_url='login')
def editar_avaliacao(request, pk):
    avaliacao = get_object_or_404(avaliacoes_do(request), pk=pk)
    form = AvaliacaoForm(request.POST or None, instance=avaliacao, usuario=request.user)
    if form.is_valid():
        form.save()
        return redirect('lista_avaliacoes')
    return render(request, 'catalogo/form.html', {
        'form': form,
        'titulo_pagina': f'Editar avaliação de {avaliacao.autor}',
        'voltar_para': 'lista_avaliacoes',
    })


@login_required(login_url='login')
def excluir_avaliacao(request, pk):
    avaliacao = get_object_or_404(avaliacoes_do(request), pk=pk)
    if request.method == 'POST':
        avaliacao.delete()
        return redirect('lista_avaliacoes')
    return render(request, 'catalogo/confirmar_exclusao.html', {
        'objeto': avaliacao,
        'tipo': 'avaliação',
        'detalhe': f'{avaliacao.nota}/5 em {avaliacao.filme.titulo}',
        'voltar_para': 'lista_avaliacoes',
    })
