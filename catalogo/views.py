from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Prefetch
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AvaliacaoForm, DiretorForm, FilmeForm, GeneroForm
from .models import Avaliacao, Diretor, Filme, Genero


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
    filmes = Filme.objects.select_related('genero', 'diretor')

    destaque = (
        filmes.annotate(media=Avg('avaliacoes__nota'))
        .filter(media__isnull=False)
        .order_by('-media')
        .first()
    )

    contexto = {
        'total_filmes': Filme.objects.count(),
        'total_diretores': Diretor.objects.count(),
        'total_generos': Genero.objects.count(),
        'total_avaliacoes': Avaliacao.objects.count(),
        'ultimos_filmes': filmes.order_by('-id')[:5],
        'ultimas_avaliacoes': Avaliacao.objects.select_related('filme')[:5],
        'destaque': destaque,
    }
    return render(request, 'catalogo/dashboard.html', contexto)


# ------------------------------------------------------------------ detalhes
# Cada página abaixo é a prova visual de uma relação 1:N: o filme mostra suas
# avaliações, o diretor e o gênero mostram seus filmes.

@login_required(login_url='login')
def detalhe_filme(request, pk):
    filme = get_object_or_404(
        Filme.objects.select_related('genero', 'diretor'), pk=pk
    )
    avaliacoes = filme.avaliacoes.all()
    return render(request, 'catalogo/filme_detalhe.html', {
        'filme': filme,
        'avaliacoes': avaliacoes,
        'media': avaliacoes.aggregate(m=Avg('nota'))['m'],
        'do_mesmo_diretor': filme.diretor.filmes.exclude(pk=filme.pk).select_related('genero'),
    })


@login_required(login_url='login')
def detalhe_diretor(request, pk):
    diretor = get_object_or_404(Diretor, pk=pk)
    return render(request, 'catalogo/diretor_detalhe.html', {
        'diretor': diretor,
        'filmes': diretor.filmes.select_related('genero').annotate(media=Avg('avaliacoes__nota')),
    })


@login_required(login_url='login')
def detalhe_genero(request, pk):
    genero = get_object_or_404(Genero, pk=pk)
    return render(request, 'catalogo/genero_detalhe.html', {
        'genero': genero,
        'filmes': genero.filmes.select_related('diretor').annotate(media=Avg('avaliacoes__nota')),
    })


# -------------------------------------------------------------------- filmes

@login_required(login_url='login')
def lista_filmes(request):
    filmes = (
        Filme.objects.select_related('genero', 'diretor')
        .annotate(media=Avg('avaliacoes__nota'), total_avaliacoes=Count('avaliacoes'))
    )
    return render(request, 'catalogo/filme_lista.html', {'filmes': filmes})


@login_required(login_url='login')
def criar_filme(request):
    form = FilmeForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('lista_filmes')
    return render(request, 'catalogo/form.html', {
        'form': form,
        'titulo_pagina': 'Novo filme',
        'voltar_para': 'lista_filmes',
    })


@login_required(login_url='login')
def editar_filme(request, pk):
    filme = get_object_or_404(Filme, pk=pk)
    form = FilmeForm(request.POST or None, instance=filme)
    if form.is_valid():
        form.save()
        return redirect('lista_filmes')
    return render(request, 'catalogo/form.html', {
        'form': form,
        'titulo_pagina': f'Editar: {filme.titulo}',
        'voltar_para': 'lista_filmes',
    })


@login_required(login_url='login')
def excluir_filme(request, pk):
    filme = get_object_or_404(Filme, pk=pk)
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


# ----------------------------------------------------------------- diretores

@login_required(login_url='login')
def lista_diretores(request):
    diretores = Diretor.objects.annotate(total_filmes=Count('filmes')).prefetch_related(
        Prefetch('filmes', queryset=Filme.objects.select_related('genero', 'diretor'))
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
    filmes_vinculados = diretor.filmes.count()

    if request.method == 'POST' and filmes_vinculados == 0:
        diretor.delete()
        return redirect('lista_diretores')

    return render(request, 'catalogo/confirmar_exclusao.html', {
        'objeto': diretor,
        'tipo': 'diretor',
        'detalhe': diretor.nacionalidade,
        'bloqueio': (
            f'Este diretor tem {filmes_vinculados} filme(s) cadastrado(s) e não pode '
            f'ser excluído. Exclua ou altere os filmes primeiro.'
        ) if filmes_vinculados else '',
        'voltar_para': 'lista_diretores',
    })


# -------------------------------------------------------------------- gêneros

@login_required(login_url='login')
def lista_generos(request):
    generos = Genero.objects.annotate(total_filmes=Count('filmes')).prefetch_related(
        Prefetch('filmes', queryset=Filme.objects.select_related('genero', 'diretor'))
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
            f'Este gênero tem {filmes_vinculados} filme(s) cadastrado(s) e não pode '
            f'ser excluído. Exclua ou altere os filmes primeiro.'
        ) if filmes_vinculados else '',
        'voltar_para': 'lista_generos',
    })


# ---------------------------------------------------------------- avaliações

@login_required(login_url='login')
def lista_avaliacoes(request):
    avaliacoes = Avaliacao.objects.select_related('filme', 'filme__genero', 'filme__diretor')
    return render(request, 'catalogo/avaliacao_lista.html', {'avaliacoes': avaliacoes})


@login_required(login_url='login')
def criar_avaliacao(request):
    form = AvaliacaoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('lista_avaliacoes')
    return render(request, 'catalogo/form.html', {
        'form': form,
        'titulo_pagina': 'Nova avaliação',
        'voltar_para': 'lista_avaliacoes',
    })


@login_required(login_url='login')
def editar_avaliacao(request, pk):
    avaliacao = get_object_or_404(Avaliacao, pk=pk)
    form = AvaliacaoForm(request.POST or None, instance=avaliacao)
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
    avaliacao = get_object_or_404(Avaliacao, pk=pk)
    if request.method == 'POST':
        avaliacao.delete()
        return redirect('lista_avaliacoes')
    return render(request, 'catalogo/confirmar_exclusao.html', {
        'objeto': avaliacao,
        'tipo': 'avaliação',
        'detalhe': f'{avaliacao.nota}/5 em {avaliacao.filme.titulo}',
        'voltar_para': 'lista_avaliacoes',
    })
