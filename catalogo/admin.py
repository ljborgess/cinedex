from django.contrib import admin

from .models import Ator, Avaliacao, Diretor, Elenco, Filme, Genero


@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('nome',)


@admin.register(Diretor)
class DiretorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nacionalidade')


@admin.register(Ator)
class AtorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nacionalidade')
    search_fields = ('nome',)


class ElencoInline(admin.TabularInline):
    model = Elenco
    extra = 1


@admin.register(Filme)
class FilmeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'genero', 'diretor', 'usuario')
    list_filter = ('genero', 'diretor', 'usuario')
    inlines = [ElencoInline]


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('filme', 'autor', 'nota', 'usuario', 'criado_em')
    list_filter = ('nota',)
