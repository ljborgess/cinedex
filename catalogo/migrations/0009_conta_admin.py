"""Cria o superusuário `admin` para a demonstração do /admin/.

Assim um banco novo, criado só com `migrate`, já tem o admin pronto, do mesmo
jeito que já tem a conta `demo`. A senha está documentada no README.
"""
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations

USUARIO_ADMIN = 'admin'
SENHA_ADMIN = 'filmes123'


def criar_admin(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    Perfil = apps.get_model('usuarios', 'Perfil')
    admin, criado = User.objects.get_or_create(
        username=USUARIO_ADMIN,
        defaults={
            'password': make_password(SENHA_ADMIN),
            'is_staff': True,
            'is_superuser': True,
        },
    )
    Perfil.objects.get_or_create(usuario=admin, defaults={'apelido': 'Admin'})


def remover_admin(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    User.objects.filter(username=USUARIO_ADMIN, is_superuser=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0008_seed_capas'),
        ('usuarios', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(criar_admin, remover_admin),
    ]
