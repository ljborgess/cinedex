from django.contrib import admin

from .models import Ator, Avaliacao, Diretor, Elenco, Filme, Genero


@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)


@admin.register(Diretor)
class DiretorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nacionalidade')
    search_fields = ('nome',)


@admin.register(Ator)
class AtorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nacionalidade')
    search_fields = ('nome',)


class ElencoInline(admin.TabularInline):
    model = Elenco
    extra = 1
    autocomplete_fields = ('ator',)


@admin.register(Filme)
class FilmeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'genero', 'diretor', 'usuario')
    list_filter = ('genero', 'usuario')
    search_fields = ('titulo', 'diretor__nome')
    # Uma consulta por página, não uma por linha para buscar gênero, diretor e dono.
    list_select_related = ('genero', 'diretor', 'usuario')
    autocomplete_fields = ('genero', 'diretor')
    inlines = [ElencoInline]


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('filme', 'autor', 'nota', 'usuario', 'criado_em')
    list_filter = ('nota', 'usuario')
    search_fields = ('filme__titulo', 'autor')
    list_select_related = ('filme', 'usuario')
    autocomplete_fields = ('filme',)
