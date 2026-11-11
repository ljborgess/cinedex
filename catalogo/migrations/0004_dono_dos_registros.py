"""Dá dono a Filme e Avaliacao.

Os registros do seed (0002 e 0003) já existem sem dono, então a migration
cria a conta de demonstração `demo` e atribui tudo a ela antes de tornar o
campo obrigatório.
"""
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations, models
import django.db.models.deletion

USUARIO_DEMO = 'demo'
SENHA_DEMO = 'filmes123'


def atribuir_ao_demo(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    Perfil = apps.get_model('usuarios', 'Perfil')
    Filme = apps.get_model('catalogo', 'Filme')
    Avaliacao = apps.get_model('catalogo', 'Avaliacao')

    demo, criado = User.objects.get_or_create(
        username=USUARIO_DEMO,
        defaults={'password': make_password(SENHA_DEMO)},
    )
    Perfil.objects.get_or_create(usuario=demo, defaults={'apelido': 'Demo'})
    Filme.objects.filter(usuario__isnull=True).update(usuario=demo)
    Avaliacao.objects.filter(usuario__isnull=True).update(usuario=demo)


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0003_mais_filmes'),
        ('usuarios', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='filme',
            name='usuario',
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name='filmes', to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='avaliacao',
            name='usuario',
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name='avaliacoes', to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(atribuir_ao_demo, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='filme',
            name='usuario',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='filmes', to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='avaliacao',
            name='usuario',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='avaliacoes', to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
