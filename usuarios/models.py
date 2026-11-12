from django.conf import settings
from django.db import models


class Perfil(models.Model):
    """Dados extras do usuário. Relação 1:1: cada usuário tem exatamente um perfil."""

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil'
    )
    apelido = models.CharField(max_length=60, blank=True)
    bio = models.TextField(max_length=280, blank=True)
    # SET_NULL: apagar um gênero não deve apagar o perfil de ninguém.
    genero_favorito = models.ForeignKey(
        'catalogo.Genero', verbose_name='gênero favorito', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='fas',
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'perfil'
        verbose_name_plural = 'perfis'

    def __str__(self):
        return f'Perfil de {self.usuario.username}'

    @property
    def nome_exibicao(self):
        return self.apelido or self.usuario.username
