from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import AtorForm, AvaliacaoForm, DiretorForm, ElencoForm, FilmeForm, GeneroForm
from .models import Ator, Avaliacao, Diretor, Elenco, Filme, Genero

# Regra de isolamento: Filme e Avaliacao têm dono. Toda consulta a eles parte
# de `filmes_do(request)` / `avaliacoes_do(request)`, inclusive as que buscam
# por pk. Assim um id digitado na URL que pertença a outra pessoa vira 404,
# em vez de abrir o registro dela.
#
# Gênero e Diretor são tabelas de referência compartilhadas (o mesmo
# "Drama" serve para todo mundo), mas os filmes exibidos dentro deles também
# passam pelo filtro do usuário.


def filmes_do(request):
    return Filme.objects.filter(usuario=request.user)


def avaliacoes_do(request):
    return Avaliacao.objects.filter(usuario=request.user)


# --------------------------------------------------------------------- home
# Única tela aberta do catálogo. Todas as outras exigem login.

def home(request):
    return render(request, 'catalogo/home.html', {
        'total_generos': Genero.objects.count(),
        'total_diretores': Diretor.objects.count(),
    })


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
    }
    return render(request, 'catalogo/dashboard.html', contexto)


# ------------------------------------------------------------------ detalhes
# Cada página abaixo é a prova visual de uma relação 1:N: o filme mostra suas
# avaliações, o diretor e o gênero mostram seus filmes.

@login_required(login_url='login')
def detalhe_filme(request, pk):
    filme = get_object_or_404(
        filmes_do(request).select_related('genero', 'diretor'), pk=pk
    )
    avaliacoes = filme.avaliacoes.all()
    return render(request, 'catalogo/filme_detalhe.html', {
        'filme': filme,
        'elenco': filme.elenco.select_related('ator'),
        'avaliacoes': avaliacoes,
        'media': avaliacoes.aggregate(m=Avg('nota'))['m'],
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


@login_required(login_url='login')
def criar_elenco(request, pk):
    filme = get_object_or_404(filmes_do(request), pk=pk)
    form = ElencoForm(request.POST or None, filme=filme, initial={'ordem': filme.elenco.count() + 1})
    if form.is_valid():
        participacao = form.save(commit=False)
        participacao.filme = filme
        participacao.save()
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
    if form.is_valid():
        form.save()
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
    atores = Ator.objects.annotate(total_filmes=Count('filmes', filter=meus)).prefetch_related(
        Prefetch('filmes', queryset=filmes_do(request).select_related('genero', 'diretor'))
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
        ator.delete()
        return redirect('lista_atores')

    return render(request, 'catalogo/confirmar_exclusao.html', {
        'objeto': ator,
        'tipo': 'ator',
        'detalhe': ator.nacionalidade,
        'bloqueio': (
            f'Este ator está no elenco de {vinculos} filme(s) no sistema e não pode '
            f'ser excluído enquanto fizer parte deles.'
        ) if vinculos else '',
        'voltar_para': 'lista_atores',
    })


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
        diretor.delete()
        return redirect('lista_diretores')

    return render(request, 'catalogo/confirmar_exclusao.html', {
        'objeto': diretor,
        'tipo': 'diretor',
        'detalhe': diretor.nacionalidade,
        'bloqueio': (
            f'Este diretor está vinculado a {filmes_vinculados} filme(s) no sistema e não '
            f'pode ser excluído enquanto eles existirem.'
        ) if filmes_vinculados else '',
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
        genero.delete()
        return redirect('lista_generos')

    return render(request, 'catalogo/confirmar_exclusao.html', {
        'objeto': genero,
        'tipo': 'gênero',
        'detalhe': '',
        'bloqueio': (
            f'Este gênero está vinculado a {filmes_vinculados} filme(s) no sistema e não '
            f'pode ser excluído enquanto eles existirem.'
        ) if filmes_vinculados else '',
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
