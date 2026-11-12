from django.contrib import admin

from .forms import AdminLoginForm
from .models import Perfil

# O login do /admin/ passa pelo mesmo limite de tentativas do site.
admin.site.login_form = AdminLoginForm
admin.site.site_header = 'Catálogo de Filmes'
admin.site.site_title = 'Catálogo de Filmes'
admin.site.index_title = 'Administração'


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'apelido', 'genero_favorito', 'criado_em')
