from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('filmes/', views.lista_filmes, name='lista_filmes'),
    path('filmes/<int:pk>/', views.detalhe_filme, name='detalhe_filme'),
    path('filmes/novo/', views.criar_filme, name='criar_filme'),
    path('filmes/<int:pk>/editar/', views.editar_filme, name='editar_filme'),
    path('filmes/<int:pk>/excluir/', views.excluir_filme, name='excluir_filme'),

    path('filmes/<int:pk>/elenco/novo/', views.criar_elenco, name='criar_elenco'),
    path('elenco/<int:pk>/editar/', views.editar_elenco, name='editar_elenco'),
    path('elenco/<int:pk>/excluir/', views.excluir_elenco, name='excluir_elenco'),

    path('atores/', views.lista_atores, name='lista_atores'),
    path('atores/<int:pk>/', views.detalhe_ator, name='detalhe_ator'),
    path('atores/novo/', views.criar_ator, name='criar_ator'),
    path('atores/<int:pk>/editar/', views.editar_ator, name='editar_ator'),
    path('atores/<int:pk>/excluir/', views.excluir_ator, name='excluir_ator'),

    path('diretores/', views.lista_diretores, name='lista_diretores'),
    path('diretores/<int:pk>/', views.detalhe_diretor, name='detalhe_diretor'),
    path('diretores/novo/', views.criar_diretor, name='criar_diretor'),
    path('diretores/<int:pk>/editar/', views.editar_diretor, name='editar_diretor'),
    path('diretores/<int:pk>/excluir/', views.excluir_diretor, name='excluir_diretor'),

    path('generos/', views.lista_generos, name='lista_generos'),
    path('generos/<int:pk>/', views.detalhe_genero, name='detalhe_genero'),
    path('generos/novo/', views.criar_genero, name='criar_genero'),
    path('generos/<int:pk>/editar/', views.editar_genero, name='editar_genero'),
    path('generos/<int:pk>/excluir/', views.excluir_genero, name='excluir_genero'),

    path('avaliacoes/', views.lista_avaliacoes, name='lista_avaliacoes'),
    path('avaliacoes/nova/', views.criar_avaliacao, name='criar_avaliacao'),
    path('avaliacoes/<int:pk>/editar/', views.editar_avaliacao, name='editar_avaliacao'),
    path('avaliacoes/<int:pk>/excluir/', views.excluir_avaliacao, name='excluir_avaliacao'),
]
