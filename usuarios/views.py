from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from . import limite
from .forms import CadastroForm, PerfilForm
from .models import Perfil


def cadastro(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = CadastroForm(request.POST or None)
    # Conta cada conta criada por IP: impede criar contas em lote por script.
    if request.method == 'POST' and limite.bloqueado(request, 'cadastro'):
        form.add_error(None, limite.MENSAGEM)
    elif form.is_valid():
        usuario = form.save()
        limite.contar(request, 'cadastro')
        login(request, usuario)
        return redirect('dashboard')
    return render(request, 'usuarios/cadastro.html', {'form': form})


@login_required(login_url='login')
def perfil(request):
    # get_or_create cobre usuários criados antes do app de perfis existir.
    perfil_usuario, _ = Perfil.objects.get_or_create(usuario=request.user)
    form = PerfilForm(request.POST or None, instance=perfil_usuario)
    if form.is_valid():
        form.save()
        return redirect('perfil')
    return render(request, 'catalogo/form.html', {
        'form': form,
        'titulo_pagina': 'Meu perfil',
        'voltar_para': 'dashboard',
    })
